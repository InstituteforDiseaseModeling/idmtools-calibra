def add_tbhiv_outbreak(task, coverage,disease, genome= 0, antigen= 0, start_day= 1, nodeIDs= [], event_name= 'OutbreakIndividualTBorHIV'):

#sisease must be 'TB' or 'HIV'


    event_coord    = { 'class' : 'StandardInterventionDistributionEventCoordinator',
                       'Number_Distributions': -1,
                       'Demographic_Coverage': coverage,
                       'Target_Demographic' : 'Everyone',
                       'Number_Repetitions': 1,
                        'Intervention_Config': {
                            'Antigen': antigen,
                            'Genome': genome,
                            'Outbreak_Source': 'PrevalenceIncrease',
                            'Infection_Type': disease,
                            "class": 'OutbreakIndividualTBorHIV'
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