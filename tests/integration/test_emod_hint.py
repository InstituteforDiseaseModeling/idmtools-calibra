#!/usr/bin/env python
import csv
import os
import unittest
from functools import partial

import pandas as pd

from idmtools_calibra import calib_base_app as calib_app
from idmtools.core.platform_factory import Platform

import datetime
from sklearn.metrics import mean_squared_error
import math
from idmtools_calibra.rmse_site import RMSESite

from tests.integration.emod_hint import model, settings
from tests.integration.emod_hint.task import  get_task

from tests.integration.helper import download_experiment_files, delete_experiments, get_output_data

CURRENT_DIRECTORY = os.path.dirname(__file__)

mysettings = settings.Settings()


class TestEMODHint(unittest.TestCase):
    def demog_mapper(build_demog_actual, mapto_key, value):
        """
        This callback function maps paraemters names for the demogaign from calibra strings to
        the actual 'build_demog' function parameter names. We hook it up in the main function. See:

        calib_app.demogaign_mapper = demog_mapper

        """
        demog_fn_param = mapto_key.split(":")[1]
        # print( f"In demog_mapper: demog_fn_param = {demog_fn_param}." )
        if demog_fn_param == "group_a_baseinfectivity":  # this maps to a value in settings.py
            build_demog_actual = partial(build_demog_actual, hint_group_a_bi=value)
        elif demog_fn_param == "group_b_baseinfectivity":  # this maps to a value in settings.py
            build_demog_actual = partial(build_demog_actual, hint_group_b_bi=value)
        elif demog_fn_param == "group_c_baseinfectivity":  # this maps to a value in settings.py
            build_demog_actual = partial(build_demog_actual, hint_group_c_bi=value)
        elif demog_fn_param == "group_d_baseinfectivity":  # this maps to a value in settings.py
            build_demog_actual = partial(build_demog_actual, hint_group_d_bi=value)
        else:
            raise ValueError(f"{demog_fn_param} is not a valid calibration target.")
        return build_demog_actual

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

        cls.directory = os.path.join(CURRENT_DIRECTORY, "emod_hint_calibra_result", uniq_filename)
        calib_app.campaign_builder_fn = model.build_camp
        calib_app.demog_builder_fn = model.build_demog
        calib_app.demog_mapper = cls.demog_mapper
        calib_app.go(calib_man, directory=cls.directory)

        # following few lines for debug
        # uniq_filename = '2023-02-10_13_32_42.373032'
        # cls.directory = os.path.join(CURRENT_DIRECTORY, "emod_hint_calibra_result", uniq_filename)
        # calib_app.go(calib_man, directory=cls.directory, resume=True, iteration=3, iter_step='plot', loop=True)
        cls.experiments = download_experiment_files(cls.platform, cls.directory, cls.calibra_name, "output.csv")

    @classmethod
    def tearDownClass(cls) -> None:
        delete_experiments(cls.experiments)

    def test_emod_hint_regression_fitness(self):
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
            distance_list = []
            for i in range(1, len(data) - 2):
                # validate LL_all.csv is sorted by 'total' column
                self.assertTrue(float(data[i][index_total]) >= float(data[i + 1][index_total]))

                # validate ll_all.csv is sorted with RMSE - Root Mean Square Error which means the top one is the best
                # prediction against the real reference value
                # first get simulation by id
                sim_id = data[i][index_sim].replace("('", '').replace("',)", '')
                # Get value 'column' in simulation's output.csv from comps
                sim_output_value = get_output_data(self.experiments, sim_id, 'value')
                # Calculate RMSE for each simulation
                rmse = math.sqrt(mean_squared_error(sim_output_value, reference_dict['value_reference']))
                # save each rmse value to a list
                rmse_list.append(rmse)

            # validate rmse_list is sorted in ascend order(small to large)
            self.assertTrue(all(a <= b for a, b in zip(rmse_list, rmse_list[1:])))
            # verify distance_list is also sorted
            self.assertTrue(distance_list == sorted(distance_list))

