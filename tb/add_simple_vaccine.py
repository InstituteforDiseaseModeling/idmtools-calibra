def add_simple_vaccine(task, trigger_treatment_list, initial_efficacy, vaccine_take= 1, vtype ='AcquisitionBlocking', box_duration= 365, immune_decay= 3650, start_day=0, duration= -1, property_restrictions_list = [], nodeIDs=[],
                       black_period= 0, black_trigger= 'Blackout', event_name = 'Simple Vaccine'):

    if vtype not in ['AcquisitionBlocking','TransmissionBlocking','MortalityBlocking','Generic']:
         raise ValueError('invalid input for vaccine type')

    event_coord    = { 'class' : 'StandardInterventionDistributionEventCoordinator',
                       'Number_Distributions': -1,
                       'Number_Repetitions': 1,
                       'Node_Property_Restrictions': [],
                        'Intervention_Config': {
                               'Actual_IndividualIntervention_Config': {
                                   "class": "SimpleVaccine",
                                   "Vaccine_Take": vaccine_take,
                                   "Efficacy_Is_Multiplicative": 1,
                                   "Vaccine_Type": vtype,
                                   "Waning_Config": {
                                       "Initial_Effect": initial_efficacy,
                                       "Box_Duration": box_duration,
                                       "Decay_Rate_Factor": immune_decay,
                                       "class": "WaningEffectBoxExponential"
                                   }
                               },
                               'Distribute_On_Return_Home': 0,
                               'Duration': duration,
                               'Blackout_Period': black_period,
                               'Blackout_Event_Trigger':  black_trigger,
                               'Blackout_On_First_Occurrence': 0,
                               'Property_Restrictions': property_restrictions_list,
                               'Trigger_Condition_List': trigger_treatment_list,
                               'class': 'NodeLevelHealthTriggeredIV'
                           }
                       }

    node_cfg = {'class' : 'NodeSetAll'}
    if nodeIDs :
        node_cfg = { 'class': 'NodeSetNodeList',
                     'Node_List': nodeIDs}

    event = {"class": "CampaignEvent",
             "Start_Day": start_day,
             "Event_Coordinator_Config": event_coord,
             "Nodeset_Config": node_cfg,
             "Event_Name": event_name}

    task.campaign.add_event(event)