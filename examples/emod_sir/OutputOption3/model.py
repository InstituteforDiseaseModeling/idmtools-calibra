from emodpy.emod_task import EMODTask
import manifest 

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
    outbreak_event = OutbreakIndividual(campaign=camp, antigen=None)
    target_demographics_config = TargetDemographicsConfig(demographic_coverage=0.4)
    add_intervention_scheduled(camp,
                               intervention_list=[outbreak_event],
                               start_day=1,
                               target_demographics_config=target_demographics_config)
    return camp

