import os
import sys

from idmtools_calibra.rmse_site import RMSESiteSingleChannel as RMSESite
from idmtools_calibra import calib_base_app as calib_app

import manifest 
from settings import Settings
settings = Settings()

if __name__ == "__main__":
    import matplotlib
    matplotlib.use( "TkAgg" )
    # site we want to calibrate on - a core organization object for calibra
    site = RMSESite(
        name='rmse_site',
        reference_sources={'production': os.path.join(settings.REFERENCE_DATA_DIR, 'output.csv')}
    )
    from emodpy.emod_task import EMODTask
    def set_param_fn( config ):
        #config.parameters.Simulation_Duration = 365.0
        config.parameters.Simulation_Duration = 181.0
        config.parameters.Base_Infectivity_Constant = 3.5 
        config.parameters.Enable_Demographics_Reporting = 0 
        config.parameters.Incubation_Period_Constant = 0
        config.parameters.Infectious_Period_Exponential = 4.0 
        #config.parameters.Minimum_End_Time = 90

        return config

    def build_camp(camp):
        from emodpy.campaign.individual_intervention import OutbreakIndividual as OutbreakIndividual
        from emodpy.campaign.common import TargetDemographicsConfig
        from emodpy.campaign.distributor import add_intervention_scheduled
        outbreak_event = OutbreakIndividual(campaign=camp)
        target_demographics_config = TargetDemographicsConfig(demographic_coverage=0.4)
        add_intervention_scheduled(camp,
                                   intervention_list=[outbreak_event],
                                   start_day=1,
                                   target_demographics_config=target_demographics_config)
        return camp

    import emod_generic.bootstrap as dtk
    dtk.setup( manifest.model_dl_dir )
    from idmtools.core.platform_factory import Platform
    platform = Platform(settings.LOCALE, node_group="idm_48cores", priority="AboveNormal")
    task = EMODTask.from_defaults(eradication_path=settings.MODEL_DRIVER,
                                  campaign_builder=build_camp,
                                  schema_path=manifest.schema_file,
                                  config_builder=set_param_fn,
                                  embedded_python_scripts_path=manifest.ep4,
                                  demographics_builder=None)
    task.set_sif( settings.SIF, platform )
    calib_man = calib_app.init( settings, site, task )
    calib_man.platform = platform

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )
    # calib_app.go(calib_man, resume=True, iteration=0, iter_step='analyze', dry_run=False, loop=True)
    import test_and_plot as tap
    tap.test_and_plot()
