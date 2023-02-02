#!/usr/bin/env python
import csv
import os
import sys
import unittest

import pandas as pd

from idmtools.core import ItemType
from idmtools_calibra import calib_base_app as calib_app
from idmtools.core.platform_factory import Platform

import datetime
from sklearn.metrics import mean_squared_error
import math
from idmtools_calibra.rmse_site import RMSESite
# to make access from command line
CURRENT_DIRECTORY = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIRECTORY, "..", "..", "examples"))
from emod_sir.OutputOption1 import settings

mysettings = settings.Settings()

class TestEMODSir(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        mysettings.LOCALE = "SlurmStage"
        mysettings.N_ITERATIONS = 5
        # mysettings.MODEL_DRIVER = os.path.join('..', '..', 'examples', 'emod_sir', 'OutputOption1', mysettings.MODEL_DRIVER)
        # site we want to calibrate on - a core organization object for calibra
        cls.site = RMSESite(
            name='rmse_site',
            reference_sources={'production': os.path.join(mysettings.REFERENCE_DATA_DIR, 'output.csv')}
        )
        cls.platform = Platform(mysettings.LOCALE, node_group="idm_48cores", priority="Highest")
        import emod_sir.OutputOption1.test_and_plot as tap
        task = tap.get_task()
        calib_man = calib_app.init(mysettings, cls.site, task, platform=cls.platform)
        #calib_man = calib_app.init(mysettings, cls.site, platform=cls.platform)
        cls.settings = mysettings
        cls.calibra_name = mysettings.CALIBRATION_NAME
        uniq_filename = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':',
                                                                                                                '_')
        print(uniq_filename)
        cls.directory = os.path.join(CURRENT_DIRECTORY, "emod_sir_calibra_result", uniq_filename)
        calib_app.go(calib_man, directory=cls.directory)

        # following few lines for debug
        # uniq_filename = '2023-02-02_13_36_58.478958'
        # cls.directory = os.path.join(CURRENT_DIRECTORY, "calibra_result", uniq_filename)
        # calib_app.go(calib_man, directory=cls.directory, resume=True, iteration=2, iter_step='plot', loop=True)

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
        return df['value']

    def test_emod_sir_regression_fitness(self):
        """
        This test is to validate calibration output in LL_all.csv. If calibration works correctly, LL_all.csv should
        be sorted by best simulation output against the reference value. we are using metrix of Root Mean Square Error
        (RMSE) to evaluate linear regression model to see how close each simulation's output against real value(reference)
        Although automation can not tell which iteration to stop, but at least can validate top one is the best
        https://towardsdatascience.com/what-are-the-best-metrics-to-evaluate-your-regression-model-418ca481755b
        """
        reference_dict = self.site.reference_dict['production']
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
                rmse = math.sqrt(mean_squared_error(sim_output_production, reference_dict['value_reference']))
                # save each rmse value to a list
                rmse_list.append(rmse)
            # validate rmse_list is sorted in ascend order(small to large)
            is_sorted = all(a <= b for a, b in zip(rmse_list, rmse_list[1:]))
            self.assertTrue(is_sorted)

