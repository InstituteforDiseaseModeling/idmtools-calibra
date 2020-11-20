def add_tb_treat_anti_tb_propdep_drug(task, drug_names_list, trigger_treatment_list, state_enabled=0, start_day=0,
                                      duration=-1, property_restrictions_list=[], nodeIDs=[], black_period=0,
                                      black_trigger='Blackout', event_name='TB Treatment (old manual-style params)'):
    # used in TB only (legacy) this drug style not used in TBHIV, see add_tbhiv_treat.py for these drugs
    # Format of drug name not consistent with most of current DTK  ie  [  {'Property1':'Value1'}, {'Property2':'Value2'}]  as opposed to one string

    event_coord = {'class': 'StandardInterventionDistributionEventCoordinator',
                   'Number_Distributions': -1,
                   'Number_Repetitions': 1,
                   'Intervention_Config': {
                       'Actual_IndividualIntervention_Config': {
                           'Drug_Type_by_Property': drug_names_list,
                           'Durability_Profile': 'FIXED_DURATION_CONSTANT_EFFECT',
                           'Remaining_Doses': 1,
                           'Enable_State_Specific_Treatment': state_enabled,
                           'class': 'AntiTBPropDepDrug'
                       },
                       'Distribute_On_Return_Home': 0,
                       'Duration': duration,
                       'Blackout_Period': black_period,
                       'Blackout_Event_Trigger': black_trigger,
                       'Blackout_On_First_Occurrence': 0,
                       'Property_Restrictions': property_restrictions_list,
                       'Trigger_Condition_List': trigger_treatment_list,
                       'class': 'NodeLevelHealthTriggeredIV'
                   }
                   }

    node_cfg = {'class': 'NodeSetAll'}
    if nodeIDs:
        node_cfg = {'class': 'NodeSetNodeList',
                    'Node_List': nodeIDs}

    event = {"class": "CampaignEvent",
             "Start_Day": start_day,
             "Event_Coordinator_Config": event_coord,
             "Nodeset_Config": node_cfg,
             "Event_Name": event_name}

    task.campaign.add_event(event)
