#!/usr/bin/env python
import csv
import os
import unittest

import pandas as pd

from idmtools.core import ItemType
from idmtools_calibra import calib_base_app as calib_app
from idmtools.core.platform_factory import Platform

import datetime
from sklearn.metrics import mean_squared_error
import math
from idmtools_calibra.rmse_site import RMSESiteSingleChannel as RMSESite
from tests.integration.emod_sir import settings
from tests.integration.emod_sir.task import get_task
from tests.integration.helper import download_experiment_files, delete_experiments, get_output_data

CURRENT_DIRECTORY = os.path.dirname(__file__)

mysettings = settings.Settings()
mysettings.N_ITERATIONS = 2
mysettings.N_SAMPLES = 10


class TestEMODSir(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # site we want to calibrate on - a core organization object for calibra
        cls.site = RMSESite(
            name='rmse_site',
            reference_sources={'production': os.path.join(mysettings.REFERENCE_DATA_DIR, 'output.csv')}
        )
        cls.platform = Platform(mysettings.LOCALE, node_group="idm_48cores", priority="Highest")
        task = get_task()
        calib_man = calib_app.init(mysettings, cls.site, task, platform=cls.platform)

        cls.calibra_name = mysettings.CALIBRATION_NAME

        date = datetime.datetime.now()
        uniq_filename = str(date.date()) + '_' + str(date.time()).replace(':', '_')
        print(uniq_filename)

        cls.directory = os.path.join(CURRENT_DIRECTORY, "emod_sir_calibra_result", uniq_filename)
        calib_app.go(calib_man, directory=cls.directory)

        # following few lines for debug
        # uniq_filename = '2023-02-02_20_08_13.484256'
        # cls.directory = os.path.join(CURRENT_DIRECTORY, "emod_sir_calibra_result", uniq_filename)
        # calib_app.go(calib_man, directory=cls.directory, resume=True, iteration=4, iter_step='plot', loop=True)
        cls.experiments = download_experiment_files(cls.platform, cls.directory, cls.calibra_name, "output.csv")

    @classmethod
    def tearDownClass(cls) -> None:
        delete_experiments(cls.experiments)

    def get_output_data(self, simulation):
        """
        Return simulation's output/output.csv 'production' column
        """
        files = self.platform.get_files(item=simulation, files=['output/output.csv'])
        output_content = files['output/output.csv'].decode('utf-8')
        l = list(output_content.split("\n"))  # convert output content to list
        df = pd.DataFrame([x.split(',') for x in l]).dropna() # convert list to dataframe
        df.columns = df.iloc[0]  # set df column names
        df = df[1:]  # set df content data
        return df['value'].astype('float32')  # convert string to float

    def test_emod_sir_regression_fitness(self):
        """
        This test is to validate calibration output in LL_all.csv. If calibration works correctly, LL_all.csv should
        be sorted by best simulation output against the reference value. we are using metrix of Root Mean Square Error
        (RMSE) to evaluate linear regression model to see how close each simulation's output against real value(reference)
        Although automation can not tell which iteration to stop, but at least can validate top one is the best
        https://towardsdatascience.com/what-are-the-best-metrics-to-evaluate-your-regression-model-418ca481755b
        """
        reference_dict = self.site.get_reference_data()
        ll_all_path = os.path.join(self.directory, self.calibra_name, "_plots", "LL_all.csv")
        with open(ll_all_path, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
            # validate "total" of likelihood column is sorted
            index_total = data[0].index('total')
            index_sim = data[0].index('simid')
            rmse_list = []
            distance_list = []
            for i in range(1, len(data) - 2):
                # validate LL_all.csv is sorted by 'total' column
                self.assertTrue(float(data[i][index_total]) >= float(data[i + 1][index_total]))

                # validate ll_all.csv is sorted with RMSE - Root Mean Square Error which means the top one is the best
                # prediction against the real reference value
                sim_id = data[i][index_sim].replace("('", '').replace("',)", '')
                # Get 'value' column in simulation's output.csv from comps
                sim_output_production = get_output_data(self.experiments, sim_id, 'value')
                # Calculate RMSE for each simulation
                rmse = math.sqrt(mean_squared_error(sim_output_production, reference_dict['value_reference']))
                # save each rmse value to a list
                rmse_list.append(rmse)

                # Or we can simply calculate distance between real value (i.e sim_output_production) and reference
                # value, top sim should have shortest distance
                distance = abs(sim_output_production.values[0]-reference_dict['value_reference'].values[0])
                distance_list.append(distance)

            # validate rmse_list is sorted in ascend order(small to large)
            self.assertTrue(all(a <= b for a, b in zip(rmse_list, rmse_list[1:])))
            # verify distance_list is also sorted
            self.assertTrue(distance_list == sorted(distance_list))

