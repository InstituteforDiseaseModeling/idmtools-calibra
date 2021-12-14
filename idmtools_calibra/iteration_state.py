import json
import os
import time
import pandas as pd
from datetime import datetime
from logging import getLogger
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools_calibra.utilities.parameter_set import ParameterSet
from idmtools_calibra.process_state import StatusPoint
from idmtools_calibra.utilities.encoding import NumpyEncoder, json_numpy_obj_hook
from idmtools_calibra.utilities.display import verbose_timedelta


logger = getLogger("Calibration")


class IterationState:
    """
    Holds the settings, parameters, simulation state, analysis results, etc.
    for one calibtool iteration.

    Allows for the resumption or extension of existing CalibManager instances
    from an arbitrary point in the iterative process.
    """

    def __init__(self, **kwargs):
        self.iteration = 0
        self.calibration_name = None
        self.calibration_directory = None
        self.platform = None
        self.task = None
        self.sites = []
        self.suite_id = {}
        self.samples_for_this_iteration = {}
        self.next_point = {}
        self.simulations = {}
        self.analyzers = {}
        self.results = {}
        self.experiment_id = None
        self.next_point_algo = None
        self.analyzer_list = []
        self.site_analyzer_names = {}
        self.experiment_builder_function = None
        self.map_sample_to_model_input_fn = None
        self.sim_runs_per_param_set = None
        self.plotters = []
        self.all_results = None
        self.summary_table = None
        self.iteration_start = None
        self.calibration_start = None
        self.resume = False

        if 'calibration_start' in kwargs:
            cs = kwargs.pop('calibration_start') or datetime.now().replace(microsecond=0)
            if not isinstance(cs, datetime):
                self.calibration_start = datetime.strptime(cs, '%Y-%m-%d %H:%M:%S')
            else:
                self.calibration_start = cs

        if 'iteration_start' in kwargs:
            cs = kwargs.pop('iteration_start') or datetime.now().replace(microsecond=0)
            if not isinstance(cs, datetime):
                self.iteration_start = datetime.strptime(cs, '%Y-%m-%d %H:%M:%S')
            else:
                self.iteration_start = cs

        self._status = None
        self.update(**kwargs)
        if self._status is not None:
            self._status = StatusPoint[self._status]

        if not os.path.exists(self.iteration_directory):
            os.makedirs(self.iteration_directory)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status
        self.save()

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def restore_results(self, iteration):
        """
        Restore summary results from serialized state.
        Args:
            iteration: the # of iteration

        Returns:

        """
        # Depending on the type of results (lists or dicts), handle differently how we treat the results
        # This should be refactor to take care of both cases at once
        # if iteration == 0:
        #     self.all_results = None
        #     # self.all_results = pd.DataFrame()
        #     # self.all_results = self.all_results.head(0)     # keep columns and type
        # elif len(self.all_results) == 0:
        #     self.all_results = None
        # el
        if isinstance(self.all_results, pd.DataFrame):
            self.all_results.set_index('sample', inplace=True)
            self.all_results = self.all_results[self.all_results.iteration <= iteration]
        elif isinstance(self.all_results, list):
            self.all_results = self.all_results[iteration]

    def run(self):
        # START_STEP
        if not self.status:
            self.starting_step()

        # COMMISSION STEP
        if self.status == StatusPoint.iteration_start:
            self.commission_step()

        # RUNNING
        if self.status == StatusPoint.commission:
            self.status = StatusPoint.running
            self.wait_for_finished()

        # ANALYZE STEP
        if self.status == StatusPoint.running:
            self.analyze_step()

        # PLOTTING STEP
        if self.status == StatusPoint.analyze:
            self.plotting_step()

        # Done with calibration? exit the loop
        if self.finished():
            return

        # NEXT STEP
        if self.status == StatusPoint.plot:
            self.next_point_step()

        self.status = StatusPoint.done

    def starting_step(self):
        self.status = StatusPoint.iteration_start

        # Restart the time for each iteration
        self.iteration_start = datetime.now().replace(microsecond=0)
        logger.info('---- Starting Iteration %d ----' % self.iteration)

    def commission_step(self):
        # Get the params from the next_point
        next_params = self.next_point_algo.get_samples_for_iteration(self.iteration)
        self.set_samples_for_iteration(next_params, self.next_point_algo)

        # Then commission
        self.commission_iteration(next_params)

        # Ready for commissioning
        self.status = StatusPoint.commission

        # Call the plot for post commission plots
        self.plot_iteration()

    def analyze_step(self):
        # Analyze the iteration
        self.analyze_iteration()

        # Ready for analyzing
        self.status = StatusPoint.analyze

    def plotting_step(self):
        # Ready for plotting
        self.status = StatusPoint.plot

        # Plot the iteration
        self.plot_iteration()

    def next_point_step(self):
        # Ready for next point
        self.status = StatusPoint.next_point

        self.next_point_algo.update_iteration(self.iteration)

    def commission_iteration(self, next_params):
        """
        Commission an experiment of simulations constructed from a list of combinations of
        random seeds, calibration sites, and the next sample points.
        Cache the relevant experiment and simulation information to the IterationState.
        Args:
            next_params: the next sample
        Returns: None
        """

        from idmtools.entities.templated_simulation import TemplatedSimulations
        from idmtools.entities.experiment import Experiment

        ts = TemplatedSimulations(base_task=self.task)
        builder = self.experiment_builder_function(next_params)
        ts.add_builder(builder)

        exp_name = f'{self.calibration_name}_iter{self.iteration}'
        experiment = Experiment(name=exp_name)

        # create mixed experiment from two templates
        experiment.simulations = ts
        experiment.parent_id = self.suite_id

        # run experiment
        experiment.run()

        # store experiment id
        self.experiment_id = experiment.uid
        # save simulations' tags
        self.simulations = {sim.id: sim.tags for sim in experiment.simulations}
        logger.debug('Commissioned new simulations for experiment id: %s' % self.experiment_id)
        self.save()

    def plot_iteration(self):
        # Run all the plotters
        for plotter in self.plotters:
            plotter.visualize(self)

    def analyze_iteration(self):
        """
        Analyze the output of completed simulations by using the relevant analyzers by site.
        Cache the results that are returned by those analyzers.
        """
        if self.results:
            logger.info('Reloading results from cached iteration state.')
            return self.results['total']

        from idmtools.core import ItemType
        analyzerManager = AnalyzeManager(ids=[(self.experiment_id, ItemType.EXPERIMENT)],
                                         analyzers=self.analyzer_list,
                                         working_dir=self.iteration_directory,
                                         verbose=False,
                                         platform=self.platform,
                                         force_manager_working_directory=True)

        if not analyzerManager.analyze():
            print("Error encountered during analysis... Exiting")
            exit()

        # Ask the analyzers to cache themselves
        cached_analyses = {a.uid: a.cache() if callable(a.cache) else {} for a in analyzerManager.analyzers}
        logger.debug(cached_analyses)

        # Get the results from the analyzers and ask the next point how it wants to cache them
        results = pd.DataFrame({a.uid: a.results for a in analyzerManager.analyzers})
        cached_results = self.next_point_algo.get_results_to_cache(results)

        # Store the analyzers and results in the iteration state
        self.analyzers = cached_analyses
        self.results = cached_results

        # Set those results in the next point algorithm
        self.next_point_algo.set_results_for_iteration(self.iteration, results)

        # Update the summary table and all the results
        self.all_results, self.summary_table = self.next_point_algo.update_summary_table(self, self.all_results)

        # re-order columns
        top_columns = ['iteration', 'total']
        self.all_results = self.all_results.reindex(
            columns=(top_columns + list([a for a in self.all_results.columns if a not in top_columns])))

        logger.info(self.summary_table)
        print(self.summary_table)

    def wait_for_finished(self, init_sleep=1.0, sleep_time=30):
        from idmtools.core import ItemType
        logger.debug('Waiting for iteration %s simulations to complete' % self.iteration)

        experiment = self.platform.get_item(self.experiment_id, ItemType.EXPERIMENT)
        while True:
            time.sleep(init_sleep)
            self.platform.refresh_status(experiment)

            # Output time info
            current_time = datetime.now()
            iteration_time_elapsed = current_time - self.iteration_start
            calibration_time_elapsed = current_time - self.calibration_start

            logger.info('\n\nCalibration: %s' % self.calibration_name)
            logger.info('Calibration path: %s' % self.calibration_directory)
            logger.info('Calibration started: %s' % self.calibration_start)
            logger.info('Current iteration: Iteration %s' % self.iteration)
            logger.info('Current Iteration Started: %s' % self.iteration_start)
            logger.info('Time since iteration started: %s' % verbose_timedelta(iteration_time_elapsed))
            logger.info('Time since calibration started: %s\n' % verbose_timedelta(calibration_time_elapsed))

            # If Calibration has been canceled -> exit
            if experiment.any_failed and not experiment.done:
                # Kill the remaining simulations
                print("\nOne or more simulations failed. Calibration cannot continue. Exiting...")
                self.kill()
                exit()

            # Test if we are all done
            if experiment.done:
                break

            time.sleep(sleep_time)

        # exit if it is failed
        if experiment.done and not experiment.succeeded:
            print("\nexperiment failed")
            exit()

        # Print the status one more time
        iteration_time_elapsed = current_time - self.iteration_start
        logger.info("Iteration %s done (took %s)" % (self.iteration, verbose_timedelta(iteration_time_elapsed)))

    def kill(self):
        def experiment_is_running(e):
            from COMPS.Data.Simulation import SimulationState
            for sim in e.get_simulations():
                if sim.state not in (SimulationState.Succeeded, SimulationState.Failed,
                                     SimulationState.Canceled, SimulationState.Created,
                                     SimulationState.CancelRequested):
                    return True
            return False

        from idmtools.core import ItemType
        comps_experiment = self.platform.get_item(self.experiment_id, ItemType.EXPERIMENT, raw=True)
        if comps_experiment and experiment_is_running(comps_experiment):
            comps_experiment.cancel()

        logger.info("Waiting to complete cancellation...")
        self.wait_for_finished()

        # Print confirmation
        logger.info("Calibration %s successfully cancelled!" % self.calibration_name)
        print("Calibration %s successfully cancelled!" % self.calibration_name)

    @property
    def iteration_directory(self):
        return os.path.join(self.calibration_directory, 'iter%d' % self.iteration)

    @property
    def iteration_file(self):
        return os.path.join(self.iteration_directory, "IterationState.json")

    @property
    def param_names(self):
        return self.next_point_algo.get_param_names()

    def finished(self):
        """ The next-point algorithm has reached its termination condition. """
        return self.next_point_algo.end_condition()

    @classmethod
    def from_file(cls, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls(**json.load(f, object_hook=json_numpy_obj_hook))

    def to_file(self):
        state = dict(status=self.status.name,
                     location=self.platform._config_block,
                     samples_for_this_iteration=self.samples_for_this_iteration,
                     analyzers=self.analyzers,
                     iteration=self.iteration, iteration_start=self.iteration_start, results=self.results,
                     calibration_name=self.calibration_name, experiment_id=self.experiment_id,
                     calibration_directory=self.calibration_directory,
                     simulations=self.simulations,
                     next_point=self.next_point_algo.get_state(), suite_id=self.suite_id)

        with open(self.iteration_file, 'w') as f:
            json.dump(state, f, indent=4, cls=NumpyEncoder)

    @classmethod
    def restore_state(cls, iteration):
        """
        Restore IterationState
        """
        iter_directory = os.path.join(cls.calibration_directory, 'iter%d' % iteration)
        iter_file = os.path.join(iter_directory, 'IterationState.json')
        return cls.from_file(iter_file)

    def set_samples_for_iteration(self, samples, next_point):
        if isinstance(samples, pd.DataFrame):
            dtypes = {name: str(data.dtype) for name, data in samples.iteritems()}
            self.samples_for_this_iteration_dtypes = dtypes
            samples_NaN_to_Null = samples.where(~samples.isnull(), other=None)
            self.samples_for_this_iteration = samples_NaN_to_Null.to_dict(orient='list')
        else:
            self.samples_for_this_iteration = samples

    def save(self):
        """
        Cache information about the IterationState that is needed to resume after an interruption.
        If resuming from an existing iteration, also copy to backup the initial cached state.
        """
        logger.debug('Saving calibration iteration %s' % self.iteration)
        if not self.calibration_name:
            return
        self.to_file()

    def get_parameter_sets_with_likelihoods(self):
        likelihoods = self.results['total']  # an ordered list of likelihood floats
        param_dicts = self.samples_for_this_iteration  # an ordered list of input input parameters (user knobs)
        if len(likelihoods) != len(param_dicts):
            raise Exception('Inconsistent iteration data. \'total\' and \'samples_for_this_iteration\' '
                            'are not the same length')

        # find and attach the sim_id & run number for every parameter set replicate
        parameter_sets = []
        for sample_index in range(len(param_dicts)):
            param_dict = param_dicts[sample_index]
            likelihood = likelihoods[sample_index]

            replicates_dict = {sim_id: sim_dict for sim_id, sim_dict in self.simulations.items()
                               if sim_dict['__sample_index__'] == sample_index}
            if len(replicates_dict) == 0:
                raise Exception('There should be at least one simulation associated with sample_index: %s. '
                                'There are none. %s' % (sample_index, len(replicates_dict)))

            # Create a distinct ParameterSet object for each replicate
            for sim_id, replicate_dict in replicates_dict.items():
                run_number = replicate_dict['Run_Number']
                parameter_set = ParameterSet(param_dict=param_dict, likelihood=likelihood,
                                             iteration_number=self.iteration, sim_id=sim_id, run_number=run_number)
                parameter_sets.append(parameter_set)

        return parameter_sets
