import pytest
import os
import unittest

import pandas as pd
from idmtools.entities.experiment import Experiment

from idmtools_calibra import calib_base_app as calib_app
from idmtools.core.platform_factory import Platform

import datetime

from idmtools_calibra.rmse_site import RMSESiteSingleChannel as RMSESite
from tests.integration.emod_sir import settings
from tests.integration.emod_sir.task import get_task

from idmtools.registry.functions import FunctionPluginManager
from idmtools.registry.hook_specs import function_hook_impl
CURRENT_DIRECTORY = os.path.dirname(__file__)

mysettings = settings.Settings()
mysettings.N_ITERATIONS = 2
mysettings.N_SAMPLES = 10


def initialize_plugins(**kwargs):
    # register plugins
    fpm = FunctionPluginManager.instance()
    fpm.register(PluginForTest(**kwargs))


class PluginForTest:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @function_hook_impl
    def idmtools_runnable_on_succeeded(self, item, **kwargs):
        """
        This function will be triggered after each iteration's commission done and experiment status is succeeded
        We will download simulations tags for each experiment and save to a file
        Args:
            item:
            **kwargs:

        Returns:

        """
        if isinstance(item, Experiment):
            filename = 'hook_test_output.csv'
            tags_for_all_sims = []
            for simulation in item.simulations.items:
                a = simulation.tags
                tags_for_all_sims.append(a)
            df = pd.DataFrame(tags_for_all_sims)
            parts = item.name.split('_')
            df.to_csv(os.path.join(self.kwargs['directory'], self.kwargs['name'], parts[-1], filename), index=False)

    @function_hook_impl
    def idmtools_runnable_on_done(self, item, **kwargs):
        """
        This function will be triggered after comission done.
        Then make sure IterationState.json file exists for each iteration
        Args:
            item:
            **kwargs:

        Returns:

        """
        if isinstance(item, Experiment):
            parts = item.name.split('_')
            assert os.path.exists(os.path.join(self.kwargs['directory'], self.kwargs['name'], parts[-1], "IterationState.json"))


class TestHooks(unittest.TestCase):
    def setUp(self) -> None:
        self.platform = Platform('SlurmStage')
        self.id_file = None
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName

    def test_plugin_hooks(self):
        site = RMSESite(
            name='rmse_site',
            reference_sources={'production': os.path.join(mysettings.REFERENCE_DATA_DIR, 'output.csv')}
        )
        platform = Platform(mysettings.LOCALE, node_group="idm_48cores", priority="Highest")
        task = get_task()
        calib_man = calib_app.init(mysettings, site, task, platform=platform)

        date = datetime.datetime.now()
        uniq_filename = str(date.date()) + '_' + str(date.time()).replace(':', '_')
        print(uniq_filename)
        #uniq_filename = "2023-12-06_19_47_33.124852"
        directory = os.path.join(CURRENT_DIRECTORY, "emod_sir_calibra_result", uniq_filename)
        # add my plugin hook
        kwargs = {}
        kwargs['directory'] = directory
        kwargs['name'] = mysettings.CALIBRATION_NAME
        initialize_plugins(**kwargs)

        calib_app.go(calib_man, directory=directory)

        for n in range(mysettings.N_ITERATIONS):
            df = pd.read_csv(os.path.join(directory, mysettings.CALIBRATION_NAME, f"iter{n}", "hook_test_output.csv"))
            self.assertEqual(df.shape[0], mysettings.N_SAMPLES)  # make sure there are 10 lines








