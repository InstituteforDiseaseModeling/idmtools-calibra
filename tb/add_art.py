def add_art(task, trigger_treatment_list, start_day=0,
                         duration= -1, property_restrictions_list= [], nodeIDs=[], black_period= 0, black_trigger= 'Blackout',event_name = 'ART'):

    event_coord    = { 'class' : 'StandardInterventionDistributionEventCoordinator',
                       'Number_Distributions': -1,
                       'Number_Repetitions': 1,
                       'Node_Property_Restrictions': [],
                        'Intervention_Config': {
                               'Actual_IndividualIntervention_Config': {
                                   'Days_To_Achieve_Viral_Suppression': 183,
                                   'Viral_Suppression': 1,
                                   'class': 'ARTBasic'
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