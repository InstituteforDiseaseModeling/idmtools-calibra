import os
import pandas as pd

from itertool.resamplers.calibration_point import CalibrationPoint, CalibrationParameter
from itertool.resamplers.calibration_points import CalibrationPoints


class ResampleManager:
    def __init__(self, steps, calibration_manager, restart_at_step=None):
        for resampler in steps:
            resampler.set_calibration_manager(calibration_manager)
        self.steps = steps
        self.calibration_manager = calibration_manager

        # the place to store information needed to perform restarts between resampling steps in case things go wrong
        self.restart_state_directory = self.steps[0].output_location + '_restart_state'
        self.restart_filename_pattern = 'resample_restart_step_%d.json'
        self.restart_selection_filename_pattern = 'resample_restart_selection_value_step_%d.csv'
        os.makedirs(self.restart_state_directory, exist_ok=True)

        if restart_at_step is None:
            self.first_step = 0
        elif restart_at_step > 0:
            if restart_at_step < len(self.steps):
                self.first_step = restart_at_step
            else:
                raise Exception('Cannot restart resampling at step %d . Can restart at step %d or lower.' % (
                restart_at_step, len(self.steps) - 1))
        else:
            raise Exception(
                "Cannot restart from step 0. Run with no restart selected if resampling from the beginning is desired.")

    def resample_and_run(self):
        print('Resampling (re)starting at step: %s' % self.first_step)

        # set the initial parameter points to resample from
        initial_calibrated_points = self.get_calibrated_points()

        if self.first_step == 0:
            calibrated_points = initial_calibrated_points
            selection_values = None
        else:
            # ck4, load up the restart files for step first_step
            calibrated_points, selection_values = self.load_restart(step=self.first_step)

        for resample_step in range(self.first_step, len(self.steps)):
            # for resampler in self.steps:
            resampler = self.steps[resample_step]
            calibrated_points, selection_values = resampler.resample_and_run(calibrated_points=calibrated_points,
                                                                             resample_step=resample_step,
                                                                             selection_values=selection_values,
                                                                             initial_calibration_points=initial_calibrated_points)
            resample_step += 1
            self.results = calibrated_points
            self.write_restart(step=resample_step, selection_values=selection_values)

    def write_restart(self, step, selection_values):
        restart_filename = self._create_restart_filename(step=step)
        CalibrationPoints(points=self.results).write(filename=restart_filename)

        selection_filename = self._create_restart_selection_fiilename(step=step)
        selection_values.to_csv(selection_filename)

    def load_restart(self, step):
        restart_filename = self._create_restart_filename(step=step)
        calibrated_points = CalibrationPoints.read(
            restart_filename).points  # because the resamplers are using lists of them, not CalibrationPoints objects

        selection_filename = self._create_restart_selection_fiilename(step=step)
        selection_values = pd.read_csv(selection_filename)

        return calibrated_points, selection_values

    def _create_restart_filename(self, step):
        return os.path.join(self.restart_state_directory, self.restart_filename_pattern % step)

    def _create_restart_selection_fiilename(self, step):
        return os.path.join(self.restart_state_directory, self.restart_selection_filename_pattern % step)

    def get_calibrated_points(self):
        """
        Retrieve information about the most recent (final completed) iteration's calibrated point,
        merging from the final IterationState.json and CalibManager.json.
        
        Returns:
        """
        n_points = 1  # ck4, hardcoded for now for HIV purposes, need to determine how to get this from the CalibManager

        calib_data = self.calibration_manager.read_calib_data()

        iteration = self.calibration_manager.get_last_iteration()
        iteration_data = self.calibration_manager.read_iteration_data(iteration=iteration)

        final_samples = calib_data['final_samples']
        iteration_metadata = iteration_data.next_point['params']

        # Create the list of points and their associated parameters
        points = list()
        for i in range(0, n_points):
            parameters = list()
            for param_metadata in iteration_metadata:
                param_metadata["Value"] = final_samples[param_metadata["Name"]][0]
                param_metadata['MapTo'] = param_metadata.get('MapTo', None)  # assign None if not present
                parameters.append(CalibrationParameter.from_dict(param_metadata))
            points.append(CalibrationPoint(parameters))

        return points
