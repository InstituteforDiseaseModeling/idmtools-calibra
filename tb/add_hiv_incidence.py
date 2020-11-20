def add_hiv_incidence(task, time_offset, reps= -1, interval= 1, start_day=0, nodeIDs=[], event_name ='HIV Incidence'):

 # note reps= -1 is repeat forever in DTK
    event_coord    = { 'class' : 'GroupInterventionDistributionEventCoordinatorHIV',
                       'Number_Distributions': -1,
                       'Time_Offset': time_offset,
                       'Number_Repetitions': reps,
                       'Timesteps_Between_Repetitions': interval,
                       'Intervention_Config': {
                                   'class': 'OutbreakIndividualTBorHIV',
                                   'Antigen': 0,
                                   'Genome': 0,
                                   'Outbreak_Source': 'PrevalenceIncrease',
                                   'Infection_Type': 'HIV'
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