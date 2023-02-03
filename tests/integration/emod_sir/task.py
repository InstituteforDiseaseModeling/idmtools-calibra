from emodpy.emod_task import EMODTask

from tests.integration.emod_sir import manifest


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    """
    import emod_api.campaign as camp
    import emod_api.interventions.outbreak as ob

    camp.set_schema( manifest.schema_file )

    # Seed the outbreak
    event = ob.new_intervention( camp, timestep=1, cases=1 )
    camp.add( event )

    return camp

def get_task( settings, build_camp_fn=None ):
    def set_param_fn( config ):
        config.parameters.Simulation_Duration = 365.0
        #config.parameters.Simulation_Duration = 730.0
        config.parameters.Base_Infectivity_Constant = 3.5
        config.parameters.Enable_Demographics_Reporting = 0
        config.parameters.Incubation_Period_Constant = 0
        config.parameters.Infectious_Period_Exponential = 4.0
        config.parameters.Base_Individual_Sample_Rate = 0.1
        #config.parameters.Minimum_End_Time = 90

        return config

    import emod_generic.bootstrap as dtk
    dtk.setup( manifest.model_dl_dir )
    from idmtools.core.platform_factory import Platform
    #platform = Platform(settings.LOCALE, node_group="idm_48cores", priority="AboveNormal")
    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=settings.MODEL_DRIVER,
        campaign_builder=build_camp,
        demog_builder=None,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        ep4_path=manifest.ep4
    )
    task.set_sif( settings.SIF )
    return task