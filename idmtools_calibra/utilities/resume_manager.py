import os
import re
import shutil
from datetime import datetime
import pandas as pd
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.iteration_state import IterationState
from idmtools_calibra.process_state import StatusPoint
from idmtools_calibra.cli.utils import read_calib_data
from logging import getLogger

logger = getLogger(__name__)


class ResumeManager(object):
    """
    Manages the creation, execution, and resumption of multi-iteration a calibration suite.
    Each iteration spawns a new ExperimentManager to configure and commission either local
    or HPC simulations for a set of random seeds, sample points, and site configurations.
    """

    def __init__(self, calib_manager: CalibManager, iteration: int = None, iter_step: str = None,
                 max_iterations: int = None, loop: bool = True, backup: bool = False, dry: bool = False):
        self.calib_manager = calib_manager
        self.iteration = iteration
        self.iter_step = iter_step
        self.max_iterations = max_iterations
        self.loop = loop
        self.backup = backup
        self.dry = dry
        self.calib_data = None

        self.initialize()

    def initialize(self):
        """
        prepare calib_manager and iteration state for resume
         - restore calib_manager
         - restore iteration state
         - validate iteration
         - validate iter_step
        """
        self.iter_step = None if self.iter_step is None else StatusPoint[self.iter_step]
        if self.iter_step:
            if self.iter_step.name not in ['commission', 'analyze', 'plot', 'next_point']:
                print(f"Invalid iter_step '{self.iter_step.name}', ignored.")
                exit()

        # 1. restore calib_manager
        self.restore_calib_manager()

        # 2. validate iteration
        self.adjust_iteration()

        # 3. validate iter_step
        self.adjust_iteration_step()

        # 3. restore iteration state
        self.restore_iteration_state()

    def resume(self):
        """
        Call calib_manager.run_iterations to start resume action
        """
        self.calib_manager.resume = True
        if self.backup:
            self.backup_calibration()

        it = self.calib_manager.current_iteration
        print('\nResume will start with:')
        print(f' - iteration = {self.iteration}')
        print(f' - status = {it.status.name if it.status else None}')
        print(f' - loop = {self.loop}')
        print(f' - max_iterations = {self.max_iterations}')

        # resume from a given iteration
        if not self.dry:
            self.calib_manager.run_iterations(self.iteration, self.max_iterations, loop=self.loop)

    def adjust_iteration(self):
        """
        Validate iteration against latest_iteration
        return adjusted iteration
        """

        # Get latest iteration #
        latest_iteration = self.calib_data.get('iteration', None)

        # handle special case
        if latest_iteration is None:
            self.iteration = 0

        # if no iteration passed in, take latest_iteration as instead
        if self.iteration is None:
            self.iteration = latest_iteration

        # adjust input iteration
        if latest_iteration < self.iteration:
            self.iteration = latest_iteration

        # adjust max_iterations based on input max_iterations
        if not self.max_iterations:
            self.max_iterations = self.calib_manager.max_iterations

        if self.max_iterations <= self.iteration:
            self.max_iterations = self.iteration + 1

    def adjust_iteration_step(self):
        """
        Validate iter_step
        """

        it = self.calib_manager.state_for_iteration(iteration=self.iteration)
        latest_step = it.status if isinstance(it.status, StatusPoint) else StatusPoint[it.status]

        if self.iter_step is None:
            self.iter_step = latest_step

        if self.iter_step == StatusPoint.analyze:
            self.iter_step = StatusPoint.running

        if self.iter_step.value > latest_step.value:
            raise Exception(f"The iter_step '{self.iter_step.name}' is beyond the latest step '{latest_step.name}'")

        # move forward if status is done
        if self.iter_step == StatusPoint.done:
            self.iter_step = StatusPoint.next_point

    def restore_calib_manager(self):
        """
        Restore calib_manager
        """
        self.calib_data = read_calib_data(self.calib_manager.calibration_path)
        self.calib_manager.suites = self.calib_data['suites']

        # step 4: load all_results
        results = self.calib_data.get('results')
        if isinstance(results, dict):
            self.calib_manager.all_results = pd.DataFrame.from_dict(results, orient='columns')
        elif isinstance(results, list):
            self.calib_manager.all_results = results

    def restore_iteration_state(self):
        """
        Restore IterationState
        """
        # restore initial iteration state
        it = self.calib_manager.state_for_iteration(self.iteration)
        it.platform = self.calib_manager.platform

        # update required objects for resume
        it.update(**self.calib_manager.required_components)

        # step 1: restore next_point
        if self.iter_step not in (
                StatusPoint.plot, StatusPoint.next_point, StatusPoint.running) and self.iteration != 0:
            if self.iter_step == StatusPoint.commission or self.iter_step == StatusPoint.iteration_start:
                iteration_state = IterationState.restore_state(it.calibration_name, self.iteration - 1)
                it.next_point_algo.set_state(iteration_state.next_point, self.iteration - 1)
            elif self.iter_step == StatusPoint.analyze:
                iteration_state = IterationState.restore_state(it.calibration_name, self.iteration)
                it.next_point_algo.set_state(iteration_state.next_point, self.iteration)

                # For IMIS ONLY!
                it.next_point_algo.restore(IterationState.restore_state(it.calibration_name, self.iteration - 1))
        else:
            it.next_point_algo.set_state(it.next_point, self.iteration)

        # step 2: restore Calibration results
        if self.iteration > 0 and self.iter_step.value < StatusPoint.plot.value:
            # it will combine current results with previous results
            it.restore_results(self.iteration - 1)
        else:
            # it will use the current results and resume from next iteration
            it.restore_results(self.iteration)

        # step 3: prepare resume states
        if self.iter_step.value <= StatusPoint.commission.value:
            # need to run simulations
            it.simulations = {}

        if self.iter_step.value <= StatusPoint.analyze.value:
            # just need to calculate the results
            it.results = {}

        # finally update current status
        it._status = StatusPoint(self.iter_step.value - 1) if self.iter_step.value > 0 else None

        self.calib_manager.current_iteration = it

    def backup_calibration(self):
        """
        Backup CalibManager.json for resume action
        """
        # calibration_path = os.path.join(self.calib_manager.name, 'CalibManager.json')
        calibration_path = self.calib_manager.calibration_path
        if os.path.exists(calibration_path):
            backup_id = 'backup_' + re.sub('[ :.-]', '_', str(datetime.now().replace(microsecond=0)))
            shutil.copy(calibration_path, os.path.join(self.calib_manager.name, 'CalibManager_%s.json' % backup_id))
