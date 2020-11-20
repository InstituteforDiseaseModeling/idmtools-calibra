def add_tb_treat_basic(task, trigger_treatment_list, drug_name='DOTS', inactivation_rate=0, mortality_rate=0,
                       clearance_rate=0, resistance_rate=0,
                       relapse_rate=0, reduced_transmit=1.0, start_day=0, treatment_duration=180,
                       duration=-1, property_restrictions_list=[], nodeIDs=[], black_period=0, black_trigger='Blackout',
                       event_name='TB Treatment (old manual-style params)'):
    # be careful with drug names this is independent of config declared drug classes
    # using this old-school stuff with TBHIV code will work but not recommended

    event_coord = {'class': 'StandardInterventionDistributionEventCoordinator',
                   'Number_Distributions': -1,
                   'Number_Repetitions': 1,
                   'Intervention_Config': {
                       'Actual_IndividualIntervention_Config': {
                           'Drug_Type': drug_name,
                           'TB_Drug_Inactivation_Rate': inactivation_rate,
                           'TB_Drug_Clearance_Rate': clearance_rate,
                           'TB_Drug_Resistance_Rate': resistance_rate,
                           'TB_Drug_Relapse_Rate': relapse_rate,
                           'TB_Drug_Mortality_Rate': mortality_rate,
                           'Reduced_Transmit': reduced_transmit,
                           'Durability_Profile': 'FIXED_DURATION_CONSTANT_EFFECT',
                           'Remaining_Doses': 1,
                           'Primary_Decay_Time_Constant': treatment_duration,
                           'class': 'AntiTBDrug'
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
