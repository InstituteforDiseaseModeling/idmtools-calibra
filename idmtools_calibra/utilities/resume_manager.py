import pandas as pd
from typing import Optional, Any, Dict, List
from idmtools.core.context import get_current_platform
from idmtools.entities.iplatform import IPlatform
from idmtools_calibra.cli.utils import read_calib_data
from idmtools_calibra.process_state import StatusPoint
from logging import getLogger

logger = getLogger(__name__)


class ResumeManager(object):
    """
    Manages the creation, execution, and resumption of multi-iteration a calibration suite.
    Each iteration spawns a new ExperimentManager to configure and commission either local
    or HPC simulations for a set of random seeds, sample points, and site configurations.
    """

    def __init__(self, calib_manager, iteration: int = None, iter_step: str = None, max_iterations: int = None,
                 loop=True, platform: Optional[IPlatform] = None):
        self.platform = platform if platform else get_current_platform()
        self.calib_manager = calib_manager
        self.iteration = iteration
        self.iter_step = iter_step
        self.max_iterations = max_iterations
        self.loop = loop
        # self.name = None
        self.calib_data = None

        self.initialize()

    def initialize(self):
        self.iter_step = None if self.iter_step is None else StatusPoint[self.iter_step]
        if self.iter_step:
            if self.iter_step.name not in ['commission', 'analyze', 'plot', 'next_point']:
                print(f"Invalid iter_step '{self.iter_step.name}', ignored.")
                exit()

        # self.calib_manager = get_calib_manager(self.config_name)
        # self.name = self.calib_manager.name

        self.calib_data = read_calib_data(self.calib_manager.calibration_path)
        self.calib_manager.suites = self.calib_data['suites']
        # self.calib_manager.latest_iteration = int(self.calib_data.get('iteration', 0))

        # step 4: load all_results
        results = self.calib_data.get('results')
        if isinstance(results, dict):
            self.calib_manager.all_results = pd.DataFrame.from_dict(results, orient='columns')
        elif isinstance(results, list):
            self.calib_manager.all_results = results

        self.adjust_iteration()
        self.adjust_iteration_step()

        # self.calib_manager.current_iteration = IterationState.restore_state(self.iteration_directory)
        # self.calib_manager.current_iteration = self.calib_manager.state_for_iteration(self.iteration)
        it = self.calib_manager.state_for_iteration(self.iteration)
        it.platform = self.calib_manager.platform
        self.calib_manager.current_iteration = it

        # step 5: update required objects for resume
        self.calib_manager.current_iteration.update(**self.calib_manager.required_components)

        # Resume the iteration
        self.calib_manager.current_iteration.resume(self.iter_step)

    def resume(self):
        self.calib_manager.resume = True  # [TODO]: may have done before already

        # print("Iteration: ", self.iteration)
        # print("iter_step: ", self.iter_step)
        # print("Status: ", self.calib_manager.current_iteration.status)
        # print("Loop: ", self.loop)

        # resume from a given iteration
        self.calib_manager.run_iterations(self.iteration, self.max_iterations, loop=self.loop)

    def adjust_iteration(self):
        """
        Validate iteration against latest_iteration
        return adjusted iteration
        """

        # Get latest iteration #
        latest_iteration = self.calib_data.get('iteration', None)

        # Handle special case
        if latest_iteration is None:
            self.iteration = 0

        # If no iteration passed in, take latest_iteration as instead
        if self.iteration is None:
            self.iteration = latest_iteration

        # Adjust input iteration
        if latest_iteration < self.iteration:
            self.iteration = latest_iteration

    def adjust_iteration_step(self):
        # validate input iter_step
        # it = IterationState.restore_state(self.iteration_directory)
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

        # finally check user input location and experiment location and provide options for resume
        # [TODO]: how in idmtools?
        # self.check_location(it)

    def check_location(self, iteration_state):
        """
        - Handle the case: process got interrupted but it still runs on remote
        - Handle location change case: may resume from commission instead
        """
        # Step 1: Checking possible location changes
        exp_id = iteration_state.experiment_id
        if not exp_id and iteration_state.status == StatusPoint.iteration_start:
            return

        exp = self.retrieve_experiment(exp_id)

        if not exp:
            var = input(
                "Cannot restore Experiment 'exp_id: %s'. Force to resume from commission... Continue ? [Y/N]" % exp_id if exp_id else 'None')
            # force to resume from commission
            if var.upper() == 'Y':
                iteration_state.resume_point = StatusPoint.commission
            else:
                logger.info(f"Answer is '{var.upper()}'. Exiting...")
                exit()

        # If location has been changed, will double check user for a special case before proceed...
        if self.location != exp.location:
            location = SetupParser.get('type')
            var = input(
                "Location has been changed from '%s' to '%s'. Resume will start from commission instead, do you want to continue? [Y/N]:  " % (
                    exp.location, location))
            if var.upper() == 'Y':
                self.current_iteration.resume_point = StatusPoint.commission
            else:
                logger.info(f"Answer is '{var.upper()}'. Exiting...")
                exit()
