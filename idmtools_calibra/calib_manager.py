from typing import Optional, List
import os
import re
import json
import shutil
import pandas as pd
from datetime import datetime
from logging import getLogger

from idmtools.builders import SimulationBuilder
from idmtools.core.context import get_current_platform
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.itask import ITask
from idmtools.utils.json import IDMJSONEncoder
from idmtools_calibra.algorithms.next_point_algorithm import NextPointAlgorithm
from idmtools_calibra.calib_site import CalibSite
from idmtools_calibra.iteration_state import IterationState
from idmtools_calibra.plotters.base_plotter import BasePlotter
from idmtools_calibra.process_state import StatusPoint
from idmtools_calibra.utilities.mod_fn import ModFn
from idmtools_calibra.utilities.helper import validate_exp_name
from idmtools_calibra.utilities.display import verbose_timedelta

logger = getLogger(__name__)


def set_run_number(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {'Run_Number': value}


class SampleIndexWrapper(object):
    """
    Wrapper for a SimConfigBuilder-modifying function to add metadata
    on sample-point index when called in a iteration over sample points
    """
    __name__ = "SampleIndex"

    def __init__(self, map_sample_to_model_input_fn):
        self.map_sample_to_model_input_fn = map_sample_to_model_input_fn

    def __call__(self, simulation, idx, *args, **kwargs):
        params_dict = self.map_sample_to_model_input_fn(simulation, *args, **kwargs)
        simulation.task.config.parameters["__sample_index__"] = idx  # [TODO]: temp fix for not found __sample_index__
        params_dict.update({'__sample_index__': idx})
        return params_dict


class CalibManager(object):
    """
    Manages the creation, execution, and resumption of multi-iteration a calibration suite.
    Each iteration spawns a new ExperimentManager to configure and commission either local
    or HPC simulations for a set of random seeds, sample points, and site configurations.
    """

    def __init__(self, task: ITask, map_sample_to_model_input_fn, sites: List[CalibSite], next_point: NextPointAlgorithm,
                 platform: Optional[IPlatform] = None, name: str = 'calib_test',
                 sim_runs_per_param_set: int = 1, max_iterations: int = 5, plotters: List[BasePlotter] = None):

        self.name = name
        if platform is None:
            platform = get_current_platform()
        self.platform = platform
        self.task = task
        self.map_sample_to_model_input_fn = SampleIndexWrapper(map_sample_to_model_input_fn)
        self.sites = sites
        self.next_point = next_point
        self.sim_runs_per_param_set = sim_runs_per_param_set
        self.max_iterations = max_iterations
        self.plotters = plotters or []
        self.suites = []
        self.all_results = None
        self.summary_table = None
        self.calibration_start = None
        self.latest_iteration = 0
        self.current_iteration = None
        self.resume = False
        self.experiment_builder_function = self.default_experiment_builder_function  # if not overridden in the set method, use internally-generated func

    @classmethod
    def open_for_reading(cls, calibration_directory):
        return cls(task=None, map_sample_to_model_input_fn=None, sites=None, next_point=None, name=calibration_directory)

    @property
    def suite_id(self):
        # Generate the suite ID if not present
        if not self.suites:
            from idmtools.entities import Suite
            suite = Suite(name=self.name)
            suites = self.platform.create_items(suite)
            suite_id = suites[0][1]
            self.suites.append({'id': suite_id})
            self.cache_calibration()

        return self.suites[-1]['id']

    @property
    def iteration(self):
        return self.current_iteration.iteration if self.current_iteration else 0

    def run_calibration(self):
        """
        Create and run a complete multi-iteration calibration suite.
        """
        # Check experiment name as early as possible
        if not validate_exp_name(self.name):
            exit()

        self.create_calibration()

        self.run_iterations()

    def run_iterations(self, iteration=0):
        """
        Run iterations in a loop
        Args:
            iteration: the # of iteration

        Returns: None
        """
        self.calibration_start = datetime.now().replace(microsecond=0)

        # normal run
        for i in range(iteration, self.max_iterations):
            self.current_iteration = self.create_iteration_state(i)
            self.current_iteration.run()
            self.post_iteration()
        self.finalize_calibration()

        # Print the calibration finish time
        current_time = datetime.now()
        calibration_time_elapsed = current_time - self.calibration_start
        logger.info("Calibration done (took %s)" % verbose_timedelta(calibration_time_elapsed))
        print("Calibration done (took %s)" % verbose_timedelta(calibration_time_elapsed))

    def post_iteration(self):
        self.all_results = self.current_iteration.all_results
        self.summary_table = self.current_iteration.summary_table
        self.cache_calibration(iteration=self.iteration + 1)

    def set_experiment_builder_function(self, exp_builder_function):
        """
        Set the experiment builder to a predefined one, such that exp_builder_func will return it
        Args:
            exp_builder_function: an experiment builder object

        Returns: None
        """
        self.experiment_builder_function = exp_builder_function

    def set_map_replicates_callback(self, map_replicates_callback):
        """
        This sets the maps replicate callback. This callback should take a value parameter that is the value of the replicate.

        Normally you would want to map this to a value in the config
        Args:
            map_replicates_callback:

        Returns:

        """
        self.map_replicates_callback = map_replicates_callback

    def default_experiment_builder_function(self, next_params, n_replicates: Optional[int] = None) -> SimulationBuilder:
        """
        Defines the function that builds the experiment for each iteration of a calibration run

        Args:
            next_params: The next parameters to run
            n_replicates: Number of replicates

        Returns:
            Simulation Builder
        """
        if not n_replicates:
            n_replicates = self.sim_runs_per_param_set

        sweeps = [[ModFn(site.setup_fn) for site in self.sites]]
        sweep = [ModFn(set_run_number, value=i + 1) for i in range(n_replicates)]
        if n_replicates > 1 and len(sweep) == 1:
            sweep = sweep[0]
        sweeps.append(sweep)
        sweeps.append(
            [ModFn(self.map_sample_to_model_input_fn, index, samples.copy() if n_replicates > 1 else samples) for
             index, samples in enumerate(next_params)])

        builder = SimulationBuilder()
        count = None
        for sweep in sweeps:
            builder.sweeps.append(sweep)
            count = len(sweep) if count is None else count * len(sweep)
        builder.count = count

        return builder

    def create_iteration_state(self, iteration):
        """
        Create iteation state
        Args:
            iteration: the # of the iteration

        Returns: created IterationState
        """
        if self.resume:
            self.resume = False
            self.current_iteration.calibration_start = self.calibration_start
            return self.current_iteration

        return IterationState(iteration=iteration,
                              calibration_name=self.name,
                              platform=self.platform,
                              sites=self.sites,
                              suite_id=self.suite_id,
                              next_point_algo=self.next_point,
                              map_sample_to_model_input_fn=self.map_sample_to_model_input_fn,
                              experiment_builder_function=self.experiment_builder_function,
                              sim_runs_per_param_set=self.sim_runs_per_param_set,
                              site_analyzer_names=self.site_analyzer_names(),
                              analyzer_list=self.analyzer_list,
                              task=self.task,
                              plotters=self.plotters,
                              all_results=self.all_results,
                              calibration_start=self.calibration_start)

    def create_calibration(self):
        """
        Create the working directory for a new calibration.
        Cache the relevant suite-level information to allow re-initializing this instance.
        """
        if os.path.exists(self.name):
            logger.info("Calibration with name %s already exists in current directory" % self.name)
            var = ""
            # while var not in ('R', 'B', 'C', 'P', 'A'):
            #     var = input('Do you want to [R]esume, [B]ackup + run, [C]leanup + run, Re-[P]lot, [A]bort:  ')
            #     var = var.upper()
            while var not in ('B', 'C', 'A'):
                var = input('Do you want to [B]ackup + run, [C]leanup + run, [A]bort:  ')
                var = var.upper()

            # Abort
            if var == 'A':
                exit()
            elif var == 'B':
                tstamp = re.sub('[ :.-]', '_', str(datetime.now()))
                shutil.move(self.name, "%s_backup_%s" % (self.name, tstamp))
                self.create_calibration()
            elif var == "C":
                self.cleanup()
                self.create_calibration()
            elif var == "R":
                self.resume_calibration()
                exit()  # avoid calling self.run_iterations(**kwargs)
            elif var == "P":
                self.replot_calibration(iteration=None)
                exit()  # avoid calling self.run_iterations(**kwargs)
        else:
            os.mkdir(self.name)
            self.cache_calibration()

    def finalize_calibration(self):
        """
        Get the final samples from the next point algorithm.
        """
        final_samples = self.next_point.get_final_samples()
        print("\nFinal samples")
        for k, v in final_samples['final_samples'].items():
            print("{}: {}".format(k, v))

        self.cache_calibration(**final_samples)

    def cache_calibration(self, **kwargs):
        """
        Cache information about the CalibManager that is needed to resume after an interruption.
        N.B. This is not currently the complete state, some of which relies on nested and frozen functions.
        As such, the 'resume' logic relies on the existence of the original configuration script.
        Args:
            **kwargs: extra info

        Returns: None
        """
        state = {'name': self.name,
                 'suites': self.suites,
                 'iteration': self.iteration,
                 'param_names': self.param_names(),
                 'sites': self.site_analyzer_names(),
                 'results': self.serialize_results(),
                 'calibration_start': self.calibration_start}
        state.update(kwargs)
        json.dump(state, open(os.path.join(self.name, 'CalibManager.json'), 'w'), indent=4, cls=IDMJSONEncoder)

    def backup_calibration(self):
        """
        Backup CalibManager.json for resume action
        """
        calibration_path = os.path.join(self.name, 'CalibManager.json')
        if os.path.exists(calibration_path):
            backup_id = 'backup_' + re.sub('[ :.-]', '_', str(datetime.now().replace(microsecond=0)))
            shutil.copy(calibration_path, os.path.join(self.name, 'CalibManager_%s.json' % backup_id))

    def serialize_results(self):
        if self.all_results is None:
            return []

        if not isinstance(self.all_results, pd.DataFrame):
            return self.all_results

        self.all_results.index.name = 'sample'
        data = self.all_results.reset_index()

        data.iteration = data.iteration.astype(int)
        data['sample'] = data['sample'].astype(int)

        return data.to_dict(orient='list')

    def resume_calibration(self, iteration=None, iter_step=None):
        pass

    def kill(self):
        from idmtools.core import ItemType

        calib_data = self.read_calib_data(force=True)
        if not calib_data:
            return

        suites = calib_data.get('suites')
        for suite in suites:
            suite_id = suite['id']
            comps_suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)
            comps_exps = comps_suite.get_experiments()
            for comps_exp in comps_exps:
                try:
                    comps_exp.delete()
                except RuntimeError:
                    logger.info("Could not delete the associated experiment...")
                    return

            try:
                comps_suite.delete()
            except RuntimeError:
                logger.info(f"Could not delete suite ({suite_id})...")
                return

        # Print confirmation
        logger.info("Calibration %s successfully cancelled!" % self.name)

    def cleanup(self):
        """
        Cleanup the current calibration
        - Delete the result directory
        - If LOCAL -> also delete the simulations
        """
        # Kill
        self.kill()

        # Then delete the whole directory
        calib_dir = os.path.abspath(self.name)
        if os.path.exists(calib_dir):
            try:
                shutil.rmtree(calib_dir)
            except OSError:
                logger.error("Failed to delete %s" % calib_dir)
                logger.error("Try deleting the folder manually before retrying the calibration.")

    def read_calib_data(self, force=False):
        try:
            return json.load(open(os.path.join(self.name, 'CalibManager.json'), 'rb'))
        except IOError:
            if not force:
                raise Exception('Unable to find metadata in %s/CalibManager.json' % self.name)
            else:
                return None

    def read_iteration_data(self, iteration):
        iteration_cache = os.path.join(self.name, 'iter%d' % iteration, 'IterationState.json')
        return IterationState.from_file(iteration_cache)

    @property
    def calibration_path(self):
        return os.path.join(self.name, 'CalibManager.json')

    @property
    def analyzer_list(self):
        analyzer_list = []
        for site in self.sites:
            for analyzer in site.analyzers:
                analyzer.result = []
                analyzer_list.append(analyzer)

        return analyzer_list

    @property
    def required_components(self):
        # update required objects for resume, reanalyze and replot
        kwargs = {
            'experiment_builder_function': self.experiment_builder_function,
            'next_point_algo': self.next_point,
            'task': self.task,
            'analyzer_list': self.analyzer_list,
            'plotters': self.plotters,
            'all_results': self.all_results,
            'calibration_start': self.calibration_start,
            'site_analyzer_names': self.site_analyzer_names()
        }
        return kwargs

    def iteration_directory(self):
        return os.path.join(self.name, 'iter%d' % self.iteration)

    def state_for_iteration(self, iteration):
        iter_directory = os.path.join(self.name, 'iter%d' % iteration)
        return IterationState.from_file(os.path.join(iter_directory, 'IterationState.json'))

    def param_names(self):
        return self.next_point.get_param_names()

    def site_analyzer_names(self):
        return {site.name: [a.uid for a in site.analyzers] for site in self.sites}

    def get_last_iteration(self):
        """
        Determines the last (most recent) completed iteration number.
        Returns: the last completed iteration number as an int
        """
        calib_data = self.read_calib_data()
        last_iteration_number = int(calib_data.get('iteration', None))
        iteration = self.state_for_iteration(iteration=last_iteration_number)
        if last_iteration_number is None:
            raise KeyError('Could not determine what the most recent iteration is.')
        if iteration.status != StatusPoint.done:
            last_iteration_number -= 1
        return last_iteration_number

    def get_parameter_sets_with_likelihoods(self):
        """
        Returns: a list of ParameterSet objects.
        """
        last_iteration = self.get_last_iteration()
        parameter_sets = []
        for iteration_number in range(last_iteration + 1):
            iteration = self.state_for_iteration(iteration=iteration_number)
            iteration_param_sets = iteration.get_parameter_sets_with_likelihoods()
            parameter_sets += iteration_param_sets
        return parameter_sets
