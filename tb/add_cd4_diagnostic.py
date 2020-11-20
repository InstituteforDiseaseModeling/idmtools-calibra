def add_cd4_diagnostic(task, trigger_treatment_list, event_200='Below200', event_350='Below350', event_500='Below500', event_above_500='Above500', start_day=0,
                       duration= -1, property_restrictions_list = [], nodeIDs=[], black_period= 0, black_trigger= 'Blackout', event_name = 'CD4 Diagnostic'):

    event_coord    = { 'class' : 'StandardInterventionDistributionEventCoordinator',
                       'Number_Distributions': -1,
                       'Number_Repetitions': 1,
                        'Intervention_Config': {
                               'Actual_IndividualIntervention_Config': {
                                   'CD4_Thresholds': [{
                                       "Event": event_200,
                                       "High": 200,
                                       "Low": 0
                                   },

                                   {
                                         'Event': event_350,
                                         'High': 350,
                                         'Low': 200
                                   },

                                   {
                                         'Event': event_500,
                                         'High': 500,
                                         'Low': 350
                                   },

                                   {
                                         'Event': event_above_500,
                                         'High': 20000,
                                         'Low': 500
                                   }

                                ],
                                   "class": "CD4Diagnostic"
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

    # add to the listed events
    loc_event_list = [event_200, event_350, event_500, event_above_500]
    existing_event_list = task.get_parameter('Listed_Events')
    for event in loc_event_list:
        if event not in existing_event_list:
            existing_event_list.append(event)

    task.set_parameter('Listed_Events',existing_event_list)