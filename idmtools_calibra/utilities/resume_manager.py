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


def status_to_iter_step(status: StatusPoint):
    if status is None:
        return None
    elif status == StatusPoint.iteration_start:
        return StatusPoint.commission
    elif status == StatusPoint.commission:
        return StatusPoint.analyze
    elif status == StatusPoint.running:
        return StatusPoint.analyze
    elif status == StatusPoint.analyze:
        return StatusPoint.plot
    elif status == StatusPoint.plot:
        return StatusPoint.next_point
    elif status == StatusPoint.next_point:
        return StatusPoint.next_point


class ResumeManager(object):
    """
    Manages the creation, execution, and resumption of multi-iteration a calibration suite.
    Each iteration spawns a new ExperimentManager to configure and commission either local
    or HPC simulations for a set of random seeds, sample points, and site configurations.
    """

    def __init__(self, calib_manager: CalibManager, iteration: int = None, iter_step: str = None,
                 max_iterations: int = None, loop: bool = True, backup: bool = False, dry_run: bool = False):
        self.calib_manager = calib_manager
        self.iteration = iteration
        self.iter_step = iter_step
        self.max_iterations = max_iterations
        self.loop = loop
        self.backup = backup
        self.dry_run = dry_run
        self.calib_data = None
        self.location = None

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

        # restore calib_manager
        self.restore_calib_manager()

        # validate iteration
        self.adjust_iteration()

        # validate iter_step
        self.adjust_iteration_step()

        # restore iteration state
        self.restore_iteration_state()

        # restore LL_all.csv
        self.restore_ll_all()

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
        print(f' - iter_step = {status_to_iter_step(it.status).name}')
        print(f' - loop = {self.loop}')
        print(f' - max_iterations = {self.max_iterations}')

        # resume from a given iteration
        if not self.dry_run:
            self.calib_manager.run_iterations(self.iteration, self.max_iterations, loop=self.loop)

    def check_location(self):
        """
        - Handle the case: resume on different environments
        - Handle environment change case: may resume from commission instead
        """
        # restore iteration state
        it = self.calib_manager.state_for_iteration(iteration=self.iteration)

        # If location has been changed, will double check user for a special case before proceed...
        if self.calib_manager.platform._config_block != it.location:
            var = input(
                "\n/!\\ WARNING /!\\ Environment has been changed from '%s' to '%s'. Resume will start from 'commission' instead, do you want to continue? [Y/N]:  " % (
                    it.location, self.calib_manager.platform._config_block))
            if var.upper() == 'Y':
                logger.info(f"Answer is '{var.upper()}'. Continue...")
                self.calib_manager.suites = []  # will re-generate suite_id in commission_iteration step
                self.iter_step = StatusPoint.commission
            else:
                logger.info(f"Answer is '{var.upper()}'. Exiting...")
                exit()

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

        # check environment
        self.check_location()

    def adjust_iteration_step(self):
        """
        Validate iter_step
        """

        it = self.calib_manager.state_for_iteration(iteration=self.iteration)
        latest_step = it.status if isinstance(it.status, StatusPoint) else StatusPoint[it.status]

        if self.iter_step is None:
            self.iter_step = latest_step

        if self.iter_step == StatusPoint.running:
            self.iter_step = StatusPoint.commission
        elif self.iter_step == StatusPoint.analyze:
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

        # restore last time location
        self.location = self.calib_data['location']

        # load all_results
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

        # in case environment has been changed and new suite_id & suites are generated
        if not self.calib_manager.suites:
            it.suite_id = self.calib_manager.suite_id
            it.suites = self.calib_manager.suites

        # update required objects for resume
        it.update(**self.calib_manager.required_components)

        # set calibration_directory
        IterationState.calibration_directory = self.calib_manager.directory

        # step 1: restore next_point
        if self.iter_step not in (
                StatusPoint.plot, StatusPoint.next_point, StatusPoint.running) and self.iteration != 0:
            if self.iter_step == StatusPoint.commission or self.iter_step == StatusPoint.iteration_start:
                iteration_state = IterationState.restore_state(self.iteration - 1)
                it.next_point_algo.set_state(iteration_state.next_point, self.iteration - 1)
            elif self.iter_step == StatusPoint.analyze:
                iteration_state = IterationState.restore_state(self.iteration)
                it.next_point_algo.set_state(iteration_state.next_point, self.iteration)

                # For IMIS ONLY!
                it.next_point_algo.restore(IterationState.restore_state(self.iteration - 1))
        else:
            it.next_point_algo.set_state(it.next_point, self.iteration)

        # step 2: restore Calibration results
        if self.iteration > 0:
            if self.iter_step.value < StatusPoint.plot.value:
                # it will combine current results with previous results
                it.restore_results(self.iteration - 1)
            else:
                # it will use the current results and resume from next iteration
                it.restore_results(self.iteration)
        else:
            if self.iter_step.value >= StatusPoint.plot.value:
                # it will combine current results with previous results
                it.restore_results(self.iteration)

        # it.all_results.reset_index(inplace=True)
        if it.iteration == 0 and self.iter_step.value < StatusPoint.plot.value:
            it.all_results = None

        # step 3: prepare resume states
        if self.iter_step.value <= StatusPoint.commission.value:
            # need to run simulations
            it.simulations = {}

        if self.iter_step.value <= StatusPoint.analyze.value:
            # just need to calculate the results
            it.results = {}

        # finally update current status
        it._status = StatusPoint(self.iter_step.value - 1) if self.iter_step.value > 0 else StatusPoint.iteration_start

        it.resume = True
        self.calib_manager.current_iteration = it

    def restore_ll_all(self):
        from idmtools_calibra.utilities.ll_all_generator import generate_ll_all

        ll_all_name = 'LL_all.csv'
        ll_all_path = os.path.join(self.calib_manager.directory, '_plots', ll_all_name)
        if os.path.exists(ll_all_path):
            os.remove(ll_all_path)

        if self.iteration > 0:
            if self.iter_step.value <= StatusPoint.plot.value:
                generate_ll_all(self.calib_manager, iteration=self.iteration - 1, ll_all_name=ll_all_name)
            else:
                generate_ll_all(self.calib_manager, iteration=self.iteration, ll_all_name=ll_all_name)
        else:
            if self.iter_step.value > StatusPoint.plot.value:
                generate_ll_all(self.calib_manager, iteration=self.iteration, ll_all_name=ll_all_name)

    def backup_calibration(self):
        """
        Backup CalibManager.json for resume action
        """
        # calibration_path = os.path.join(self.calib_manager.name, 'CalibManager.json')
        calibration_path = self.calib_manager.calibration_path
        if os.path.exists(calibration_path):
            backup_id = 'backup_' + re.sub('[ :.-]', '_', str(datetime.now().replace(microsecond=0)))
            shutil.copy(calibration_path, os.path.join(self.calib_manager.name, 'CalibManager_%s.json' % backup_id))
