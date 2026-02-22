import os
import sys


from emodpy.emod_task import EMODTask
sys.path.append(os.path.dirname(__file__))
import manifest
import settings

settings = settings.Settings()

# NOTE: Any campaign parameter you want to calibrate must be in the build_camp param list
def get_task( build_camp_fn=None, build_demog_fn=None ):
    def set_param_fn( config ):
        #config.parameters.Simulation_Duration = 730.0
        config.parameters.Enable_Demographics_Reporting = 0
        config.parameters.Enable_Property_Report = 1
        #config.parameters.Base_Individual_Sample_Rate = 0.1

        return config

    import emod_generic.bootstrap as dtk
    dtk.setup( manifest.model_dl_dir )
    import model
    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=settings.MODEL_DRIVER,
        campaign_builder=build_camp_fn,
        demog_builder=build_demog_fn,
        schema_path=manifest.schema_file,
        param_custom_cb=model.set_param_fn,
        ep4_path=manifest.ep4
    )
    task = EMODTask.from_defaults(eradication_path=settings.MODEL_DRIVER,
                                  campaign_builder=build_camp_fn,
                                  schema_path=manifest.schema_file,
                                  config_builder=model.set_param_fn,
                                  embedded_python_scripts_path=manifest.ep4,
                                  demographics_builder=build_demog_fn)

    task.config.parameters.Enable_Property_Output = 1
    task.set_sif( settings.SIF )
    return task