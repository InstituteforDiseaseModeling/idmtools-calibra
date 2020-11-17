from abc import ABCMeta, abstractmethod
from itertools import zip_longest
import os
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.resamplers.calibration_point import CalibrationPoint, CalibrationParameter


class BaseResampler(metaclass=ABCMeta):
    def __init__(self, calib_manager=None):
        self.calib_manager: CalibManager = calib_manager
        self.output_location = None  # must be set via setter below
        self.selection_columns = []  # items to strip off resampled points DataFrame and pass to next resampler
        self.selection_values = None  # a DataFrame, created using self.selection_columns, added to the resampled points for the next resampler to use

    # strictly required to be defined in subclasses
    @abstractmethod
    def resample(self, calibrated_points, selection_values, initial_calibration_points):
        pass

    # extend if desired in subclasses
    def post_analysis(self, resampled_points, analyzer_results, from_resample=None):
        os.makedirs(self.output_location, exist_ok=True)

    def set_calibration_manager(self, calib_manager: CalibManager):
        self.calib_manager = calib_manager
        self.output_location = os.path.join(calib_manager.name, 'resampling_output')

    def _run(self, points, resample_step) -> Experiment:
        """
        This run method is for running simulations, which is the in-common part of resampling.
        :param points: The points to run simulations at.
        :return: The Experiment object for these simulations
        """
        # create a sweep where each point is a separate sim
        if not self.calib_manager:
            raise Exception('calibration manager has not set for resampler. Cannot generate simulations.')

        point_dicts = [point.to_value_dict() for point in points]

        # ck4, the number of replicates must be 1 for HIV for now; the general solution should allow a user-selected
        # replicate count, so long as their likelihood analyzer can handle > 1 replicates.
        exp_builder = self.calib_manager.experiment_builder_function(point_dicts, n_replicates=1)

        # Create an experiment manager
        exp_name = self.calib_manager.name + '_resample_step_%d' % resample_step
        experiment = Experiment.from_template(TemplatedSimulations(builders={exp_builder}), name=exp_name)
        experiment.run(platform=self.calib_manager.platform)
        return experiment

    def _analyze(self, experiment: Experiment, analyzers, points_ran):
        """
        This method is the in-common route for Resamplers to analyze simulations for liklihood.

        Args:
            experiment: the experiment to analyze, should be from self._run()
            analyzers:
            points_ran: Points objects that were just _run()

        Returns:
            The supplied points_ran with their .likelihood attribute set, AND the direct results of the analyzer
                 as a list.
        """
        am = AnalyzeManager(analyzers=analyzers, ids=[(experiment.id, ItemType.EXPERIMENT)])
        am.analyze()

        # compute a single likelihood value from all of the analyzers on a per-simulation basis
        result_tuples = zip_longest(*[analyzer.results for analyzer in am.analyzers])
        try:
            results = [sum(tup) for tup in result_tuples]
        except TypeError as e:  # if 1+ None values snuck in...
            raise type(e)('All analyzers must contain one result per simulation. The result list lengths do not match.')

        for i in range(len(results)):
            # Add the likelihood
            points_ran[i].likelihood = results[i]

        # verify that the returned points all have a likelihood attribute set
        likelihoods_are_missing = True in {point.likelihood is None for point in points_ran}
        if likelihoods_are_missing:
            raise Exception('At least one Point object returned by the provided analyzer does not have '
                            'its .likelihood attribute set.')

        return points_ran, results

    def resample_and_run(self, calibrated_points, resample_step, selection_values, initial_calibration_points):
        """
        Canonical entry method for using the resampler.

        Args:
            calibrated_points: Calibrated Points
            resample_step:
            selection_values:
            initial_calibration_points:

        Returns:

        """
        # 1. resample
        # The user-provided _resample() method in Resampler subclasses must set the 'Value' in each Point object dict
        # for keying off of in the _run() method above.
        # Any _resample() methodology that depends on the likelihood of the provided points should reference
        #    the 'likelihood' attribute on the Point objects (e.g., use mypoint.likelihood, set it in the analyer
        #    return points.
        points_to_run, for_post_analysis = self.resample(calibrated_points=calibrated_points,
                                                         selection_values=selection_values,
                                                         initial_calibration_points=initial_calibration_points)

        # # 2. run simulations
        experiment = self._run(points=points_to_run, resample_step=resample_step)
        experiment.wait()

        # 3. analyze simulations for likelihood
        self.resampled_points, self.analyzer_results = self._analyze(experiment=experiment,
                                                                     analyzers=self.calib_manager.analyzer_list,
                                                                     points_ran=points_to_run)
        # 4. perform any post-analysis processing, if defined
        self.post_analysis(self.resampled_points, self.analyzer_results, from_resample=for_post_analysis)

        return self.resampled_points, self.selection_values

    def _transform_df_points_to_calibrated_points(self, calibrated_point, df_points):
        # build calibration points from dataframe, preserving CalibrationParameter metadata from calibrated_point
        calibrated_points = []
        for index, row in df_points.iterrows():
            parameters = []
            for name in calibrated_point.parameter_names:
                new_parameter = CalibrationParameter.from_calibration_parameter(calibrated_point.get_parameter(name),
                                                                                value=row[name])
                parameters.append(new_parameter)
            calibrated_points.append(CalibrationPoint(parameters))

        self.selection_values = df_points[self.selection_columns].copy()

        return calibrated_points
