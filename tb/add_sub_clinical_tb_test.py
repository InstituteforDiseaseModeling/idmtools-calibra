def add_SubClinicalTBTest(task, trigger_treatment_list, base_sensitivity_active_no_HIV = 0, base_specificity = 0.95,cd4_strata=[100.0, 200.0, 1000.0],
                           strata_sensitivity = [0.56, 0.49, 0.15 ], subclinical_only= 1.0, pos_event= 'LAM_Positive', neg_event= 'LAM_Negative',
                           defaulters_event= 'LAM_Default', treatment_fraction= 1, start_day=0, duration= -1, property_restrictions_list = [], nodeIDs=[], black_period= 0, black_trigger= 'Blackout',event_name = 'TB SubClinical Diagnosis'):

    event_coord    = { 'class' : 'StandardInterventionDistributionEventCoordinator',
                       'Number_Distributions': -1,
                       'Number_Repetitions': 1,
                       'Node_Property_Restrictions': [],
                       'Intervention_Config': {
                               'Actual_IndividualIntervention_Config': {
                                   'Base_Sensitivity': base_sensitivity_active_no_HIV,
                                   'Base_Specificity': base_specificity,
                                   'Test_CD4_Strata': cd4_strata,
                                   'Strata_Sensitivity': strata_sensitivity,
                                   'Treatment_Fraction': treatment_fraction,
                                   'Days_To_Diagnosis': 0,
                                   'SubClinical_Only': subclinical_only,
                                   'Event_Or_Config': 'Event',
                                   'Positive_Diagnosis_Event': pos_event,
                                   'Negative_Diagnosis_Event': neg_event,
                                   'Defaulters_Event': defaulters_event,
                                   'class': 'DiagnosticSubClinical'
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