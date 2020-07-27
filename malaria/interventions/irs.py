import copy
from malaria.interventions.malaria_drug_campaigns import fmda_cfg
from dtk.interventions.irs import node_irs_config
from dtk.utils.Campaign.CampaignClass import *


def add_reactive_node_IRS(config_builder, start: int = 0, listening_duration: int = -1,
                          trigger_coverage: float = 1.0, irs_coverage: float = 1.0,
                          node_selection_type: str = 'DISTANCE_ONLY',
                          reactive_radius: int = 0, irs_ineligibility_duration: int = 60,
                          delay: int = 7, killing_config: any = None, reduction_config: any = None,
                          insecticide: str=None,
                          nodeIDs: list = None, node_property_restrictions: list = None):
    """
    Add a reactive intervention distribution for IRS that is triggered by 
    a Received_Treatment event. This is only appropriate for household 
    models, where nodes represent households.    

    Args:
        config_builder: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` 
            object for building, modifying, and writing campaign configuration files.
        start: The day on which to start distributing the reactive intervention. 
        listening_duration: Duration the intervention exists and listens for triggers.
        trigger_coverage: Probability that a Received_Treatment event triggers reactive 
            IRS activity.
        irs_coverage: Probability that a node receives spraying if reactive IRS activity 
            is triggered.
        node_selection_type: Node_Selection_Type: 
            DISTANCE_ONLY: Sends the event to nodes that are within a given distance.
            MIGRATION_NODES_ONLY: Only sends the event to nodes that the individual can 
                migrate to.
            DISTANCE_AND_MIGRATION: Only sends the event to migratable nodes that are 
                within a given distance.
        reactive_radius: Distance (in km) from initial node within which reactive spraying 
            may be performed.
        irs_ineligibility_duration: How long the node will not be eligible for more spraying.
        delay: Delay in days before the spraying after the trigger event.
        killing_config: either a dictionary or CampaignClass object with the waning of the killing config
            Default is Killing_Config=WaningEffectExponential(Decay_Time_Constant=90, Initial_Effect=0.5)
        reduction_config: either a dictionary or CampaignClass object with the waning of the reduction_config
            Default is Reduction_Config=WaningEffectExponential(Decay_Time_Constant=365, Initial_Effect=0)
        insecticide: name of insecticide to use. Default None.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        node_property_restrictions: List of NodeProperty key:value pairs that nodes must 
            have to receive the intervention. For example, ``[{"NodeProperty1": 
            "PropertyValue1"}, {"NodeProperty2":"PropertyValue2"}]``.

    Returns:
        None

    """

    if node_property_restrictions is None:
        node_property_restrictions = []
    if nodeIDs:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    else:
        nodeset_config = NodeSetAll()
    irs_config = copy.deepcopy(node_irs_config)
    if killing_config:
        irs_config.Killing_Config = killing_config
    if reduction_config:
        irs_config.Reduction_Config = reduction_config
    if insecticide:
        irs_config.Insecticide_Name = insecticide

    irs_trigger_config = fmda_cfg(reactive_radius, node_selection_type, 'Spray_IRS')

    receiving_irs_event = BroadcastNodeEvent(Broadcast_Event="Node_Sprayed")
    recent_irs = NodePropertyValueChanger(Target_NP_Key_Value="SprayStatus:RecentSpray",
                                          Maximum_Duration=0,
                                          Revert=irs_ineligibility_duration)

    irs_config = [irs_config, recent_irs, receiving_irs_event]

    trigger_irs = CampaignEvent(Start_Day=start,
                                Nodeset_Config=nodeset_config,
                                Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                                    Intervention_Config=NodeLevelHealthTriggeredIV(
                                        Demographic_Coverage=trigger_coverage,
                                        Node_Property_Restrictions=node_property_restrictions,
                                        Trigger_Condition_List=["Received_Treatment"],
                                        Duration=listening_duration,
                                        Actual_IndividualIntervention_Config=DelayedIntervention(
                                            Delay_Period_Distribution="CONSTANT_DISTRIBUTION",
                                            Delay_Period_Constant=delay,
                                            Actual_IndividualIntervention_Configs=[irs_trigger_config]))))

    no_spray = {'SprayStatus': 'None'}
    if node_property_restrictions:
        for item in node_property_restrictions:
            item.update(no_spray)
    else:
        node_property_restrictions = [no_spray]

    distribute_irs = CampaignEvent(Event_Name="Distribute IRS",
                                   Start_Day=start,
                                   Nodeset_Config=nodeset_config,
                                   Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                                       Intervention_Config=NodeLevelHealthTriggeredIV(
                                           Node_Property_Restrictions=node_property_restrictions,
                                           Demographic_Coverage=irs_coverage,
                                           Trigger_Condition_List=["Spray_IRS"],
                                           Blackout_On_First_Occurrence=1,
                                           Blackout_Period=1,
                                           Blackout_Event_Trigger="IRS_Blackout",
                                           Actual_NodeIntervention_Config=MultiNodeInterventionDistributor(
                                               Node_Intervention_List=irs_config))))

    config_builder.add_event(trigger_irs)
    config_builder.add_event(distribute_irs)
