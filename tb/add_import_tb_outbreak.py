def add_tb_import_outbreak(task, numcases=1, start_day=0, genome=0, antigen=0, import_age=7300, nodeIDs=[],
                           event_name='Import Cases TB'):
    event_coord = {'class': 'StandardInterventionDistributionEventCoordinator',
                   'Number_Distributions': -1,
                   'Demographic_Coverage': 1.0,
                   'Target_Demographic': 'Everyone',
                   'Number_Repetitions': 1,
                   'Intervention_Config': {
                       'Antigen': antigen,
                       'Genome': genome,
                       'Number_Cases_Per_Node': numcases,
                       'Import_Age': import_age,
                       "class": 'Outbreak'
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
