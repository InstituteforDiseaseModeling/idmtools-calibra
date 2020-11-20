def add_simple_hiv_diagnostic(task, trigger_treatment_list, start_day=0, base_sensitivity= 1.0, base_specificity= 1.0, treatment_fraction= 1.0, daystodiag= 0,
                              pos_event= 'HIVTestedPositive', neg_event= 'HIVTestedNegative', duration= -1, property_restrictions_list = [], nodeIDs=[], black_period= 0, black_trigger= 'Blackout', event_name = 'HIV Simple Diagnostic'):

    event_coord    = { 'class' : 'StandardInterventionDistributionEventCoordinator',
                       'Number_Distributions': -1,
                       'Number_Repetitions': 1,
                        'Intervention_Config': {
                               'Actual_IndividualIntervention_Config': {
                                   'Base_Sensitivity': base_sensitivity,
                                   'Base_Specificity': base_specificity,
                                   'Treatment_Fraction': treatment_fraction,
                                   'Days_To_Diagnosis': daystodiag,
                                   'Event_Or_Config': 'Event',
                                   'Positive_Diagnosis_Event': pos_event,
                                   'Negative_Diagnosis_Event': neg_event,
                                   'class': 'HIVSimpleDiagnostic'
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