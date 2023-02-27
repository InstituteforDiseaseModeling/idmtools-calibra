from tests.integration.emod_hint import manifest


def set_param_fn( config ):
    #config.parameters.Simulation_Duration = 365.0
    config.parameters.Simulation_Duration = 365.0
    #config.parameters.Base_Infectivity_Constant = 3.5 
    config.parameters.Enable_Demographics_Reporting = 0 
    #config.parameters.Incubation_Period_Constant = 0
    #config.parameters.Infectious_Period_Exponential = 4.0 
    #config.parameters.Acquisition_Blocking_Immunity_Decay_Rate = 1.0
    #config.parameters.Acquisition_Blocking_Immunity_Duration_Before_Decay = 0
    config.parameters.Base_Infectivity_Constant = 10.0
    config.parameters.Infectious_Period_Exponential = 6.1
    config.parameters.Incubation_Period_Constant = 3.9
    config.parameters.Acquisition_Blocking_Immunity_Decay_Rate = 1.000
    config.parameters.Acquisition_Blocking_Immunity_Duration_Before_Decay = 20.193
    #config.parameters.Minimum_End_Time = 90

    return config

def build_camp():
    """
    Build a campaign input file for the DTK using emod_api. 
    """
    import emod_api.campaign as camp
    import emod_api.interventions.outbreak as ob 

    camp.set_schema( manifest.schema_file ) # only need once with latest emodpy
    
    #event = ob.new_intervention( camp, timestep=1, cases=1 )
    event = ob.seed_by_coverage(camp, timestep=1, coverage=0.01, properties=None )

    camp.add( event )
    return camp

def build_demog( hint_group_a_bi=1.0, hint_group_b_bi=1.0, hint_group_c_bi=1.0, hint_group_d_bi=1.0 ):
    import emod_api.demographics.Demographics as Demographics

    demog = Demographics.from_template_node( lat=0, lon=0, pop=10000, name=1, forced_id=1 )
    demog.SetEquilibriumAgeDistFromBirthAndMortRates()
    demog.SetBirthRate(0.0001)

    demog.AddIndividualPropertyAndHINT(
        Property="Geographic",
        Values=["Province_A","Province_B","Province_C","Province_D"],
        InitialDistribution=[0.1,0.5,0.15,0.25],
        TransmissionMatrix = [
                [ hint_group_a_bi, 0, 0, 0 ],
                [ 0, hint_group_b_bi, 0, 0 ],
                [ 0, 0, hint_group_c_bi, 0 ],
                [ 0, 0, 0, hint_group_d_bi ],
            ]
        )
    return (demog)

