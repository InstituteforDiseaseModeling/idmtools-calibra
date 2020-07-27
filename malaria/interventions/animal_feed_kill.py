import random
from dtk.interventions.triggered_campaign_delay_event import triggered_campaign_delay_event
from dtk.utils.Campaign.CampaignClass import *


def add_animalfeedkill(config_builder, start: int = 1, cost: int = 1,
                       killing_config: any = WaningEffectBox(Initial_Effect=0.95, Box_Duration=30),
                       insecticide: str = None, nodeIDs: list = None, node_property_restrictions: list = None,
                       triggered_campaign_delay: int = 0, trigger_condition_list: list = None,
                       listening_duration: int = -1,
                       check_eligibility_at_trigger: bool = False):
    """
    Adds a node-level AnimalFeedKill intervention, which, in the absense of other interventions works as follows:
    Out of n vectors biting that day (1-anthropophily) portion will attempt to bite animals and out of those the
    killing coefficient will die doing that. So, the intervention kills (biting vectors)*(1-anthropophily)*(killing)
    vectors a day.

    Note: insecticide is currently not implemented so it does nothing
    Args:
        config_builder: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            containing the campaign configuration.
        start: The day on which to start distributing the intervention
            (**Start_Day** parameter) or the day to begin monitoring for
            events that trigger AnimalFeedKill distribution.
        killing_config: The value passed gets directly assigned to the Killing_Config parameter.
            Durations are in days.
            Default is killing_config = WaningEffectBox(Initial_Effect=0.95, Decay_Time_Constant=30)
            This could be dictionary such as:
            {
                "Box_Duration": 3650,
                "Initial_Effect": 0,
                "Decay_Time_Constant": 150,
                "class": "WaningEffectBoxExponential"
            }
            OR CampaignClass-created object/parameter configuration such as:
            WaningEffectRandomBox(
                    Initial_Effect=0.95,
                    Expected_Discard_Time=200
            )
        insecticide: Insecticide name to be used with the intervention, must match one from config.json
        cost: The per-unit cost (**Cost_To_Consumer** parameter).
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention (**Node_Property_Restrictions**
            parameter). In the format ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``
        triggered_campaign_delay: After the trigger is received, the number of
            time steps until the campaign starts. Eligibility of people or nodes
            for the campaign is evaluated on the start day, not the triggered
            day.
        trigger_condition_list: (Optional) A list of the individual events that will
            trigger the AnimalFeedKill intervention. If included, **start** is the day
            when monitoring for triggers begins.
        listening_duration: The number of time steps that the distributed
            event will monitor for triggers. Default is -1, which is indefinitely.
        check_eligibility_at_trigger: if triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay.

    Returns:
        None

    Example:
        ::

            config_builder = DTKConfigBuilder.from_defaults(sim_example)
            killing_config = WaningEffectRandomBox(
                    Initial_Effect=0.85,
                    Expected_Discard_Time=200
            )
            add_animalfeedkill(config_builder, start=15, killing_config = killing_config, cost=300,
                            nodeIDs=[2, 25])
    """
    animalfeedkill_config = AnimalFeedKill(
        Cost_To_Consumer=cost,
        Killing_Config=killing_config
    )
    if not nodeIDs:
        nodeset_config = NodeSetAll()
    else:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    if not node_property_restrictions:
        node_property_restrictions = []
    if insecticide:
        animalfeedkill_config.Insecticide_Name = insecticide

    afk_event = CampaignEvent(
        Start_Day=start,
        Nodeset_Config=nodeset_config,
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            Node_Property_Restrictions=node_property_restrictions,
            Intervention_Config=animalfeedkill_config))

    if trigger_condition_list:
        if triggered_campaign_delay:
            trigger_node_property_restrictions = []
            if check_eligibility_at_trigger:
                trigger_node_property_restrictions = node_property_restrictions
                node_property_restrictions = []
            trigger_condition_list = [str(triggered_campaign_delay_event(config_builder, start, nodeIDs, coverage=1,
                                                                         triggered_campaign_delay=triggered_campaign_delay,
                                                                         trigger_condition_list=trigger_condition_list,
                                                                         listening_duration=listening_duration,
                                                                         node_property_restrictions=trigger_node_property_restrictions))]

        afk_event.Event_Coordinator_Config.Intervention_Config = NodeLevelHealthTriggeredIV(
            Blackout_On_First_Occurrence=True,
            Blackout_Event_Trigger="AnimalFeedKill_Blackout_%d" % random.randint(0, 10000),
            Blackout_Period=1,
            Node_Property_Restrictions=node_property_restrictions,
            Duration=listening_duration,
            Trigger_Condition_List=trigger_condition_list,
            Actual_NodeIntervention_Config=animalfeedkill_config
        )

        del afk_event.Event_Coordinator_Config.Node_Property_Restrictions

    config_builder.add_event(afk_event)
