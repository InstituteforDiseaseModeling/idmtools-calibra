#!/usr/bin/env python
import csv
import json
import os
import unittest

import pandas as pd
from idmtools.core import ItemType

from examples.solar import settings
from idmtools_calibra import calib_base_app as calib_app
from idmtools.core.platform_factory import Platform
from examples.solar.solar_site import SolarSite
import datetime
from sklearn.metrics import mean_squared_error
import math

mysettings = settings.Settings()
CURRENT_DIRECTORY = os.path.dirname(__file__)


class TestSolarPanel(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        mysettings.LOCALE = "SlurmStage"
        mysettings.N_ITERATIONS = 5
        mysettings.MODEL_DRIVER = os.path.join('..', '..', 'examples', 'solar', 'bin', 'linear_model.py')
        # site we want to calibrate on - a core organization object for calibra
        cls.site = SolarSite(
            name='solar_site',
            reference_sources={'production': os.path.join(mysettings.REFERENCE_DATA_DIR, 'production.csv')}
        )
        cls.platform = Platform(mysettings.LOCALE, node_group="idm_48cores", priority="Highest")
        calib_man = calib_app.init(mysettings, cls.site, platform=cls.platform)
        cls.settings = mysettings
        cls.calibra_name = mysettings.CALIBRATION_NAME
        uniq_filename = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':',
                                                                                                                '_')
        print(uniq_filename)
        cls.directory = os.path.join(CURRENT_DIRECTORY, "calibra_result", uniq_filename)
        calib_app.go(calib_man, directory=cls.directory)

        # following few lines for debug
        # uniq_filename = '2023-02-02_09_03_40.161383'
        # cls.directory = os.path.join(CURRENT_DIRECTORY, "calibra_result", uniq_filename)
        # calib_app.go(calib_man, directory=cls.directory, resume=True, iteration=4, iter_step='plot', loop=True)

    def get_output_data(self, simulation):
        """
        Return simulation's output/output.csv 'production' column
        """
        files = self.platform.get_files(item=simulation, files=['output/output.csv'])
        output_content = files['output/output.csv'].decode('utf-8')
        l = list(output_content.split("\n"))  # convert output content to list
        df = pd.DataFrame([x.split(',') for x in l])  # convert list to dataframe
        df.columns = df.iloc[0]  # set df column names
        df = df[1:]  # set df content data
        return df['production']

    def test_regression_fitness(self):
        """
        This test is to validate calibration output in LL_all.csv. If calibration works correctly, LL_all.csv should
        be sorted by best simulation output against the reference value. we are using metrix of Root Mean Square Error
        (RMSE) to evaluate linear regression model to see how close each simulation's output against real value(reference)
        Although automation can not tell which iteration to stop, but at least can validate top one is the best
        https://towardsdatascience.com/what-are-the-best-metrics-to-evaluate-your-regression-model-418ca481755b
        """
        reference_dict = self.site.reference_dict['production']['production_reference']
        ll_all_path = os.path.join(self.directory, self.calibra_name, "_plots", "LL_all.csv")
        with open(ll_all_path, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
            # validate "total" of likelihood column is sorted
            index_total = data[0].index('total')
            index_sim = data[0].index('simid')
            rmse_list = []
            for i in range(1, len(data) - 2):
                # validate LL_all.csv is sorted by 'total' column
                self.assertTrue(float(data[i][index_total]) >= float(data[i + 1][index_total]))

                # validate ll_all.csv is sorted with RMSE - Root Mean Square Error which means the top one is the best
                # prediction against the real reference value
                # first get simulation by id
                sim_id = data[i][index_sim].replace("('", '').replace("',)", '')
                simulation = self.platform.get_item(item_id=sim_id, item_type=ItemType.SIMULATION)
                sim_output_production = self.get_output_data(simulation)
                # Calculate RMSE for each simulation
                rmse = math.sqrt(mean_squared_error(sim_output_production, reference_dict))
                # save each rmse value to a list
                rmse_list.append(rmse)
            # validate rmse_list is sorted in ascend order(small to large)
            is_sorted = all(a <= b for a, b in zip(rmse_list, rmse_list[1:]))
            self.assertTrue(is_sorted)

    def test_calibration_folder(self):
        # validate folders exists
        calibra_dir = os.path.join(self.directory, self.calibra_name)
        self.assertTrue(os.path.exists(os.path.join(calibra_dir, '_plots')))
        self.assertTrue(os.path.exists(os.path.join(calibra_dir, 'iter0')))
        self.assertTrue(os.path.exists(os.path.join(calibra_dir, f'iter{self.settings.N_ITERATIONS - 1}')))
        # Validate CalibraManager.json
        self.assertTrue(os.path.isfile(os.path.join(calibra_dir, 'CalibManager.json')))

    def test_calibration_manager(self):
        calibra_dir = os.path.join(self.directory, self.calibra_name)
        calib_manager_dict = json.load(open(os.path.join(calibra_dir, 'CalibManager.json'), 'rb'))
        self.assertEqual(calib_manager_dict['name'], self.calibra_name)
        self.assertEqual(calib_manager_dict['directory'], calibra_dir)
        self.assertEqual(calib_manager_dict['location'], self.settings.LOCALE)
        self.assertEqual(calib_manager_dict['iteration'], self.settings.N_ITERATIONS - 1)
        self.assertEqual(calib_manager_dict['sites'], {'solar_site': ['RMSEAnalyzer']})
        self.assertEqual(calib_manager_dict['param_names'], ['linear-coefficient', 'constant'])
        self.assertEqual(calib_manager_dict['final_samples_dtypes'],
                         {"linear-coefficient": "float64", "constant": "float64"})
        result_keys = ['sample', 'iteration', 'total', 'RMSEAnalyzer', 'linear-coefficient', 'constant']
        for key, value in calib_manager_dict['results'].items():
            self.assertEqual(len(value), self.settings.N_ITERATIONS * self.settings.N_SAMPLES)
            self.assertTrue(bool([x for x in result_keys if (x in key)]))

    def test_iteration_state(self):
        calibra_dir = os.path.join(self.directory, self.calibra_name)
        calib_manager_dict = json.load(open(os.path.join(calibra_dir, 'CalibManager.json'), 'rb'))
        # Validate IterationState.json file in last iteration
        iter_state_dict = json.load(
            open(os.path.join(calibra_dir, f'iter{self.settings.N_ITERATIONS - 1}', 'IterationState.json'), 'rb'))
        final_sample = calib_manager_dict['final_samples']
        for key, value in final_sample.items():
            self.assertTrue(True if key in ['linear-coefficient', 'constant'] else False)

            # check final_samples values. they should be last iteration's center values in last iterationState.json
            if key == 'linear-coefficient':
                self.assertEqual(value[0],
                                 iter_state_dict['next_point']['state']['Center'][(self.settings.N_ITERATIONS - 1) * 2])
            elif key == 'constant':
                self.assertEqual(value[0], iter_state_dict['next_point']['state']['Center'][
                    (self.settings.N_ITERATIONS - 1) * 2 + 1])
        self.assertEqual(iter_state_dict['status'], 'done')
        self.assertEqual(iter_state_dict['location'], self.settings.LOCALE)
        self.assertEqual(iter_state_dict['calibration_directory'], calibra_dir)
        self.assertEqual(iter_state_dict['calibration_name'], self.calibra_name)
        self.assertEqual(len(iter_state_dict['samples_for_this_iteration']), self.settings.N_SAMPLES)
        self.assertEqual(list(iter_state_dict['analyzers'].keys())[0], 'RMSEAnalyzer')
        self.assertEqual(iter_state_dict['iteration'], self.settings.N_ITERATIONS - 1)
        self.assertEqual(len(iter_state_dict['results']['RMSEAnalyzer']), self.settings.N_SAMPLES)
        self.assertEqual(len(iter_state_dict['results']['total']), self.settings.N_SAMPLES)
        self.assertIsNotNone(iter_state_dict['experiment_id'])
        self.assertIsNotNone(iter_state_dict['suite_id'])
        self.assertIsNotNone(iter_state_dict['iteration_start'])
        self.assertEqual(len(iter_state_dict['simulations']), self.settings.N_SAMPLES)
        self.assertEqual(list(iter_state_dict['next_point'].keys()),
                         ['mu_r', 'sigma_r', 'center_repeats', 'rsquared_thresh', 'n_dimensions', 'params',
                          'samples_per_iteration', 'data', 'data_dtypes', 'regression', 'regression_dtypes', 'state',
                          'state_dtypes'])
        self.assertEqual(list(iter_state_dict['next_point']['state'].keys()),
                         ['Iteration', 'Parameter', 'Center', 'Min', 'Max', 'Dynamic'])
