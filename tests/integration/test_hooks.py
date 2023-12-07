import pytest
import os
import unittest

import pandas as pd

from idmtools_calibra import calib_base_app as calib_app
from idmtools.core.platform_factory import Platform

import datetime

from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.iteration_state import IterationState
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

    @function_hook_impl
    def idmtools_runnable_on_succeeded(self, item, **kwargs):
        if isinstance(item, IterationState):
            filename = 'hook_test_output.csv'
            df = pd.DataFrame(item.samples_for_this_iteration)
            df.to_csv(os.path.join(item.iteration_directory, filename))

    @function_hook_impl
    def idmtools_runnable_on_done(self, item, **kwargs):
        if isinstance(item, CalibManager):
            df = item.all_results.copy()
            df.to_csv(os.path.join(item.directory, "all_result.csv"))


@pytest.mark.comps
@pytest.mark.python
class TestHooks(unittest.TestCase):
    def setUp(self) -> None:
        self.platform = Platform('SlurmStage')
        self.id_file = None
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName

    def test_plugin_hooks(self):
        kwargs = {}
        initialize_plugins(**kwargs)

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
        #uniq_filename = "2023-12-06_18_45_41.593705"
        directory = os.path.join(CURRENT_DIRECTORY, "emod_sir_calibra_result", uniq_filename)
        calib_app.go(calib_man, directory=directory)
        df = pd.read_csv(os.path.join(directory, mysettings.CALIBRATION_NAME, "iter0", "hook_test_output.csv"))
        self.assertEqual(df.shape[0], mysettings.N_SAMPLES)  # make sure there are 10 lines
        df = pd.read_csv(os.path.join(directory, mysettings.CALIBRATION_NAME, "all_result.csv"))
        self.assertEqual(df.shape[0], mysettings.N_SAMPLES * mysettings.N_ITERATIONS * mysettings.N_REPLICATES)








