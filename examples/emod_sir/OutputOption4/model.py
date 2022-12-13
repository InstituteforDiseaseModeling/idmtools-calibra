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

def build_demog():
    """
    Build a demographics input file for the DTK using emod_api. 
    """
    import emodpy_generic.demographics.GenericDemographics as Demographics # OK to call into emod-api

    demog = Demographics.fromBasicNode( lat=0, lon=0, pop=1e5, name=1, forced_id=1 )
    return demog

