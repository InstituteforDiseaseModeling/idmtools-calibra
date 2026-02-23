import os
import sys

from emodpy.emod_task import EMODTask

sys.path.append(os.path.dirname(__file__))
import manifest_sir as manifest
import settings

settings = settings.Settings()


def get_task():
    def set_param_fn(config):
        config.parameters.Simulation_Duration = 181.0
        config.parameters.Base_Infectivity_Constant = 3.5
        config.parameters.Enable_Demographics_Reporting = 0
        config.parameters.Incubation_Period_Constant = 0
        config.parameters.Infectious_Period_Exponential = 4.0
        config.parameters.Base_Individual_Sample_Rate = 0.1

        return config

    def build_camp(camp):
        from emodpy.campaign.individual_intervention import OutbreakIndividual as OutbreakIndividual
        from emodpy.campaign.common import TargetDemographicsConfig
        from emodpy.campaign.distributor import add_intervention_scheduled
        outbreak_event = OutbreakIndividual(campaign=camp, antigen=None)
        target_demographics_config = TargetDemographicsConfig(demographic_coverage=0.4)
        add_intervention_scheduled(camp,
                                   intervention_list=[outbreak_event],
                                   start_day=1,
                                   target_demographics_config=target_demographics_config)
        return camp

    import emod_generic.bootstrap as dtk
    dtk.setup(manifest.model_dl_dir)
    from idmtools.core.platform_factory import Platform
    platform = Platform(settings.LOCALE, node_group="idm_48cores", priority="AboveNormal")
    task = EMODTask.from_defaults(eradication_path=settings.MODEL_DRIVER,
                                  campaign_builder=build_camp,
                                  schema_path=manifest.schema_file,
                                  config_builder=set_param_fn,
                                  embedded_python_scripts_path=manifest.ep4,
                                  demographics_builder=None)
    task.set_sif( settings.SIF, platform )
    return task
