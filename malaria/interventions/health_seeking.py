def add_health_seeking(simulation,
                       start_day: int=0,
                       # Note: potential for overlapping drug treatments in the same individual
                       targets: list=None,
                       drug: list=None,
                       nodeIDs: list=None,
                       node_property_restrictions: list=None,
                       ind_property_restrictions: list=None,
                       disqualifying_properties: list=None,
                       drug_ineligibility_duration: int=0,
                       duration: int=-1,
                       repetitions: int=1,
                       tsteps_btwn_repetitions: int=365,
                       broadcast_event_name: str='Received_Treatment'):
    """
    Add a health seeking behavior intervention to the campaign using using 
    the **NodeLevelHealthTriggeredIV** class, a node-level intervention. 
    The intervention will distribute drugs to targeted individuals within 
    the node.
    
    Args:
        simulation:  idmtools Simulation object.
        start_day: Start day of intervention.
        targets: List of dictionaries defining the trigger event and coverage for and 
        properties of individuals to target with the intervention. Default is ``[{
            "trigger":"NewClinicalCase","coverage":0.8,"agemin":15,"agemax":70, 
            "seek":0.4,"rate":0.3},{"trigger":"NewSevereCase","coverage":0.8,"seek":0.6,
            "rate":0.5}]``.  
        drug: List of drug(s) to administer. Default is ``["Artemether","Lumefantrine"]``.
        dosing: The type of anti-malarial drug dosing. Default is ``"FullTreatmentCourse"``. 
            For a list of possible enum values, see **AntimalarialDrug_Dosing_Type_Enum** 
            class in :py:class:`CampaignEnum <dtk.utils.Campaign.CampaignEnum>`.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        node_property_restrictions: List of NodeProperty key:value pairs that nodes must 
            have to receive the intervention. For example, ``[{"NodeProperty1": 
            "PropertyValue1"}, {"NodeProperty2":"PropertyValue2"}]``.         
        ind_property_restrictions: List of IndividualProperty key:value pairs that 
            individuals must have to receive the intervention. For example, 
            ``[{"IndividualProperty1":"PropertyValue1"}, {"IndividualProperty2": 
            "PropertyValue2"}]``.
        disqualifying_properties: List of IndividualProperty key:value pairs that cause 
            an intervention to be aborted. For example, ``[{"IndividualProperty1":
            "PropertyValue1"}, {"IndividualProperty2":"PropertyValue2"}]``.
        drug_ineligibility_duration: Sets a drug ineligibility duration (number of days).
            If set to > 0, use IndividualProperties to prevent people from receiving
            drugs too frequently. Demographics file will need to define the IP DrugStatus 
            with possible values None and RecentDrug. Individuals with status RecentDrug 
            will not receive drugs during drug campaigns, though they are still eligible 
            for receiving diagnostics (in MSAT, etc). Individuals who receive drugs during 
            campaigns will have their DrugStatus changed to RecentDrug for drug 
            ineligibility duration.            
        duration: How long the intervention is active. Default is -1, where intervention 
            never expires.
        repetitions: How many times to repeat creating this intervention. Default is 1.
        tsteps_btwn_repetitions: Time steps between repetitions. Default is 365.
        broadcast_event_name: Event to broadcast when successful health seeking behavior. 
            Default is Received_Treatment.

    Returns:
        None
    """

    if drug is None:
        drug = ['Artemether', 'Lumefantrine']
    if nodeIDs:
        nodeset_config = {
            "Node_List": [nodeIDs],
            "class": "NodeSetNodeList"
        }
    else:
        nodeset_config = {"class": "NodeSetAll"}
    if not node_property_restrictions:
        node_property_restrictions = []
    if not ind_property_restrictions:
        ind_property_restrictions = []
    if not disqualifying_properties:
        disqualifying_properties = []
    if not targets:
        targets = [{'trigger': 'NewClinicalCase', 'coverage': 0.1, 'agemin': 15, 'agemax': 70, 'seek': 0.4, 'rate': 0.3},
                   {'trigger': 'NewSevereCase', 'coverage': 0.8, 'seek': 0.6, 'rate': 0.5}]

    receiving_drugs_event = {
                               "Broadcast_Event": broadcast_event_name,
                               "class": "BroadcastEvent"
                            }

    expire_recent_drugs = {
                           "Maximum_Duration": 0,
                           "Daily_Probability": 1,
                           "Revert": drug_ineligibility_duration,
                           "Target_Property_Key": "DrugStatus",
                           "Target_Property_Value": "RecentDrug",
                           "class": "PropertyValueChanger"
                        }

    drug_config, drugs = get_drug_config(drug, receiving_drugs_event,
                                         drug_ineligibility_duration, expire_recent_drugs)
    if drug_ineligibility_duration > 0:
        drugstatus = {"DrugStatus": "None"}
        if ind_property_restrictions:
            for item in ind_property_restrictions:
                item.update(drugstatus)
        else:
            ind_property_restrictions = [drugstatus]

    for t in targets:

        actual_config = build_actual_treatment_cfg(t['rate'], drug_config, drugs)
        actual_config["Disqualifying_Properties"] = disqualifying_properties
        target_age_min = 0 # age is in years
        target_age_max = 125 #setting defaults in case these are unused
        target_demographic = "Everyone"
        if all([k in t.keys() for k in ['agemin', 'agemax']]):
            target_demographic = "ExplicitAgeRanges"
            target_age_min = t['agemin']
            target_age_max = t['agemax']

        health_seeking_event = {
            'Start_Day': start_day,
            'Nodeset_Config': nodeset_config,
            'Event_Coordinator_Config': {
                'Number_Repetitions': repetitions,
                'Timesteps_Between_Repetitions': tsteps_btwn_repetitions,
                'Intervention_Config': {
                    'Trigger_Condition_List': [t['trigger']],
                    'Duration': duration,
                    'Target_Demographic': target_demographic,
                    'Target_Age_Min': target_age_min,
                    'Target_Age_Max': target_age_max,
                    'Demographic_Coverage': t['coverage'] * t['seek'],
                    'Node_Property_Restrictions': node_property_restrictions,
                    'Property_Restrictions_Within_Node': ind_property_restrictions,
                    'Actual_IndividualIntervention_Config': actual_config,
                    'class': 'NodeLevelHealthTriggeredIV'
                },
                'class': 'StandardInterventionDistributionEventCoordinator'
            },
            'class': 'CampaignEvent'
        }

        simulation.task.campaign.add_event(health_seeking_event)


def add_health_seeking_by_chw(simulation,
                               start_day: int = 0,
                               targets: list = None,
                               drug: list = None,
                               nodeIDs: list = None,
                               node_property_restrictions: list = None,
                               ind_property_restrictions: list = None,
                               disqualifying_properties: list = None,
                               drug_ineligibility_duration: int = 0,
                               duration: int = 3.40282e+38,
                               chw: dict = None):
    """
    Add a health seeking behavior by community health worker intervention to the 
    campaign using the **CommunityHealthWorkerEventCoordinator** class. This 
    intervention includes drug distribution limited by community health worker's 
    distribution rates and other parameters.    

    Note: chw does not have Disqualifying_Properties. Disqualifying_Properties are applied
    to the drug distribution. Person uses chw, but they do not get the drugs chw distributes to them.

    Args:
        simulation: idmtools Simulation object.
        start_day: Start day of intervention.
        targets: List of dictionaries defining the trigger event and coverage for and 
        properties of individuals to target with the intervention. Default is ``[{
            "trigger":"NewClinicalCase","coverage":0.8,"agemin":15,"agemax":70, 
            "seek":0.4,"rate":0.3},{"trigger":"NewSevereCase","coverage":0.8,"seek":0.6,
            "rate":0.5}]``.
        drug: List of drug(s) to administer.
        dosing: The type of anti-malarial drug dosing. Default is FullTreatmentCourse. 
            For a list of possible enum values, see **AntimalarialDrug_Dosing_Type_Enum** 
            class in :py:class:`CampaignEnum <dtk.utils.Campaign.CampaignEnum>`.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        node_property_restrictions: List of NodeProperty key:value pairs that nodes must 
            have to receive the intervention. For example, ``[{"NodeProperty1": 
            "PropertyValue1"}, {"NodeProperty2":"PropertyValue2"}]``.
        ind_property_restrictions: List of IndividualProperty key:value pairs that 
            individuals must have to receive the intervention. For example, 
            ``[{"IndividualProperty1":"PropertyValue1"}, {"IndividualProperty2": 
            "PropertyValue2"}]``.
        disqualifying_properties: List of IndividualProperty key:value pairs that cause 
            an intervention to be aborted. For example, ``[{"IndividualProperty1":
            "PropertyValue1"}, {"IndividualProperty2":"PropertyValue2"}]``.
        drug_ineligibility_duration: Sets a drug ineligibility duration (number of days).
            If set to > 0, use IndividualProperties to prevent people from receiving
            drugs too frequently. Demographics file will need to define the IP DrugStatus 
            with possible values None and RecentDrug. Individuals with status RecentDrug 
            will not receive drugs during drug campaigns, though they are still eligible 
            for receiving diagnostics (in MSAT, etc). Individuals who receive drugs during 
            campaigns will have their DrugStatus changed to RecentDrug for drug 
            ineligibility duration.
        duration: How long the intervention is active. Default is 100000.
        chw: Dictionary of parameters to update in CommunityHealthWorkerEventCoordinator 
            configuration.

    Returns:
        Configured **CommunityHealthWorkerEventCoordinator** class dictionary campaign 
        event wrapped as **RawCampaignObject** class object and added to the 
        :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` object.
    """
    if nodeIDs:
        nodeset_config = {
            'Node_List': nodeIDs,
            'class': 'NodeSetNodeList'
        }
    else:
        nodeset_config = {"class": "NodeSetAll"}

    if not node_property_restrictions:
        node_property_restrictions = []
    if not ind_property_restrictions:
        ind_property_restrictions = []
    if not disqualifying_properties:
        disqualifying_properties = []
    if not targets:
        targets = [{'trigger': 'NewClinicalCase', 'coverage': 0.8, 'agemin': 15, 'agemax': 70, 'seek': 0.4, 'rate': 0.3},
                   {'trigger': 'NewSevereCase', 'coverage': 0.8, 'seek': 0.6, 'rate': 0.5}]

    # we are not using disqualifying properties from healthseeking, just from chw - the still seek, be processed by
    # chw but will be disqualified when receiving drugs
    add_health_seeking(simulation, start_day=start_day, targets=targets, drug=[], nodeIDs=nodeIDs,
                       node_property_restrictions=node_property_restrictions,
                       ind_property_restrictions=ind_property_restrictions,
                       duration=duration, broadcast_event_name='CHW_Give_Drugs')

    if drug_ineligibility_duration > 0:
        drugstatus = {"DrugStatus": "None"}
        if ind_property_restrictions:
            for item in ind_property_restrictions:
                item.update(drugstatus)
        else:
            ind_property_restrictions = [drugstatus]

    receiving_drugs_event = {
        'Broadcast_Event': "Received_Treatment",
        'class': 'BroadcastEvent'
    }

    expire_recent_drugs = {
        'Target_Property_Key': "DrugStatus",
        'Target_Property_Value': "RecentDrug",
        'Daily_Probability': 1,
        'Maximum_Duration': 0,
        'Revert': drug_ineligibility_duration,
        'class': 'PropertyValueChanger'
    }

    # NOTE: node property restrictions isn't working yet for CHWEC (3/29/17)
    chw_config = {
        'Duration': duration,
        'Initial_Amount_Constant': 1000,
        'Initial_Amount_Distribution': "CONSTANT_DISTRIBUTION",
        'Max_Stock': 1000,
        'Waiting_Period': 7,
        'Days_Between_Shipments': 90,
        'Amount_In_Shipment': 1000,
        'Max_Distributed_Per_Day': 5,
        'Target_Demographic': "Everyone",
        'Target_Residents_Only': 0,
        'Demographic_Coverage': 1,
        'Trigger_Condition_List': ["CHW_Give_Drugs"],
        'Property_Restrictions_Within_Node': ind_property_restrictions,
        'Node_Property_Restrictions': node_property_restrictions,
        'class': 'CommunityHealthWorkerEventCoordinator'
    }

    if chw:
        for param, value in chw:
            chw_config[param] = value

    add_health_seeking(simulation, start_day=start_day, targets=targets, drug=[], nodeIDs=nodeIDs,
                       node_property_restrictions=node_property_restrictions,
                       ind_property_restrictions=ind_property_restrictions,
                       duration=duration, broadcast_event_name='CHW_Give_Drugs')

    drug_config, drugs = get_drug_config(drug, receiving_drugs_event,
                                         drug_ineligibility_duration, expire_recent_drugs)
    drug_config.Disqualifying_Properties = disqualifying_properties
    actual_config = build_actual_treatment_cfg(0, drug_config, drugs)
    chw_config.Intervention_Config = actual_config

    chw_event = {
        'Start_Day': start_day,
        'Event_Coordinator_Config': chw_config,
        'Nodeset_Config': nodeset_config,
        'class': 'CampaignEvent'
    }

    simulation.task.campaign.add_event(chw_event)
    return


def get_drug_config(drug: list=None, receiving_drugs_event=None,
                    drug_ineligibility_duration: int = 0, expire_recent_drugs=None):
    """
    Create a list of drugs and (optional) broadcast event.

    Args:
        drug: List of drug(s) to administer. Default is 
            ``["Artemether","Lumefantrine"]``.
        receiving_drugs_event: Broadcasts event, Received_Treatment, 
           when drug_ineligibility_duration is > 1.
        drug_ineligibility_duration: Duration (in days) of ineligibility 
            for an individual to receive drugs, adds expire_recent_drugs.
        expire_recent_drugs: Update IndividualProperty key:value pair to 
            ``{"DrugStatus": "RecentDrug"}``.

    Returns:
        **MultiInterventionDistributor** class object with list of AntimalarialDrugs 
        and (optional) receiving_drugs_event.
    """
    if drug is None:
        drug = ['Artemether', 'Lumefantrine']

    drugs = []
    for d in drug:
        antimalarial_drug = {
            'Cost_To_Consumer': 1,
            'Drug_Type': d,
            'class': 'AntimalarialDrug'
        }
        drugs.append(antimalarial_drug)
    drugs.append(receiving_drugs_event)
    if drug_ineligibility_duration > 0:
        drugs.append(expire_recent_drugs)
    drug_config = {
        'Intervention_List': drugs,
        'class': 'MultiInterventionDistributor'
    }

    return drug_config, drugs


def build_actual_treatment_cfg(rate: float=0, drug_config: any=None, drugs: list=None):
    """
    Modify treatment distribution using **DelayedIntervention** class if 
    there is a rate of people per day greater than what the community 
    health worker can see.

    Args:
        rate: How many people a day community health workter 
            can see on average.
        drug_config: MultiInterventionDistributor with list of 
            AntimalariaDrugs and (optional) receiving_drugs_event.
        drugs: List of AntimalariaDrugs and (optional) 
            receiving_drugs_event.

    Returns:
        Drug distribution config
    """
    if rate > 0:
        actual_config = {
            'Delay_Period_Distribution': "EXPONENTIAL_DISTRIBUTION",
            'Delay_Period_Exponential': 1.0/rate,
            'Actual_IndividualIntervention_Configs': drugs,
            'class': 'DelayedIntervention'
        }
    else:
        actual_config = drug_config

    return actual_config
