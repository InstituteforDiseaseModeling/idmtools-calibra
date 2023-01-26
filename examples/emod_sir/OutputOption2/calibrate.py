import os
import sys

from idmtools_calibra.rmse_site import RMSESite 
from idmtools_calibra import calib_base_app as calib_app

import manifest 
from settings import Settings
mysettings = Settings()

if __name__ == "__main__":
    import matplotlib
    matplotlib.use( "TkAgg" )
    # site we want to calibrate on - a core organization object for calibra
    site = RMSESite(
        name='rmse_site',
        reference_sources={'production': os.path.join(mysettings.REFERENCE_DATA_DIR, 'output.csv')}
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

    def build_camp():
        """
        Build a campaign input file for the DTK using emod_api. 
        """
        import emod_api.campaign as camp
        import emod_api.interventions.outbreak as ob 

        camp.set_schema( manifest.schema_file )
        
        event = ob.new_intervention( camp, timestep=1, cases=1 )
        camp.add( event )
        return camp

    import emod_generic.bootstrap as dtk
    dtk.setup( manifest.model_dl_dir )
    from idmtools.core.platform_factory import Platform
    platform = Platform(mysettings.LOCALE, node_group="idm_48cores", priority="AboveNormal")
    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=mysettings.MODEL_DRIVER,
        campaign_builder=build_camp,
        demog_builder=None,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        ep4_path=manifest.ep4
    )
    task.set_sif( mysettings.SIF )
    calib_man = calib_app.init( mysettings, site, task )
    calib_man.platform = platform

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )

    import test_and_plot as tap
    tap.test_and_plot()
