def add_Ramp_DiagnosticTreatNeg(task, trigger_treatment_list, ramp_time,  base_sensitivity_smearpos, base_sensitivity_smearneg,
                                base_sensitivity_smearpos2, base_sensitivity_smearneg2, treatment_fraction2,
                                pos_event2= 'TBTestPositive', neg_event2= 'TBTestNegative', defaulters_event2= 'TBTestDefault',
                                pos_event= 'TBTestPositive', neg_event= 'TBTestNegative',
                           defaulters_event= 'TBTestDefault', treatment_fraction= 1, start_day=0, duration= -1, property_restrictions_list = [], nodeIDs=[], black_period= 0, black_trigger= 'Blackout',event_name = 'TB Diagnosis Ramp'):

    event_coord    = { 'class' : 'StandardInterventionDistributionEventCoordinator',
                       'Number_Distributions': -1,
                       'Number_Repetitions': 1,
                        'Intervention_Config': {
                               'Actual_IndividualIntervention_Config': {
                                   'Base_Sensitivity': base_sensitivity_smearpos,
                                   'Base_Specificity': 1.0 - base_sensitivity_smearneg,
                                   'Treatment_Fraction': treatment_fraction,
                                   'Days_To_Diagnosis': 0,
                                   'Event_Or_Config': 'Event',
                                   'Positive_Diagnosis_Event': pos_event,
                                   'Negative_Diagnosis_Event': neg_event,
                                   'Defaulters_Event': defaulters_event,
                                   'class': 'DiagnosticTreatNeg'
                               },
                               'Not_Covered_IndividualIntervention_Configs': [ {
                                    'Base_Sensitivity': base_sensitivity_smearpos2,
                                    'Base_Specificity': 1.0 - base_sensitivity_smearneg2,
                                    'Treatment_Fraction': treatment_fraction2,
                                    'Days_To_Diagnosis': 0,
                                    'Event_Or_Config': 'Event',
                                    'Positive_Diagnosis_Event': pos_event2,
                                    'Negative_Diagnosis_Event': neg_event2,
                                    'Defaulters_Event': defaulters_event2,
                                    'class': 'DiagnosticTreatNeg'
                                    }
                              ] ,

                               'Distribute_On_Return_Home': 0,
                               'Duration': duration,
                               'Blackout_Period': black_period,
                               'Blackout_Event_Trigger':  black_trigger,
                               'Blackout_On_First_Occurrence': 0,
                               'Property_Restrictions': property_restrictions_list,
                               'Trigger_Condition_List': trigger_treatment_list,
                               'Demographic_Coverage_Time_Profile': 'Linear',
                               'Initial_Demographic_Coverage': 0,
                               'Demographic_Coverage': 1,
                               'Primary_Time_Constant': ramp_time,
                               'class': 'NodeLevelHealthTriggeredIVScaleUpSwitch'
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