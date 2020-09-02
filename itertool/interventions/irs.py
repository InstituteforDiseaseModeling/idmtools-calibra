import copy, random
from dtk.interventions.triggered_campaign_delay_event import triggered_campaign_delay_event
from dtk.utils.Campaign.CampaignClass import *

irs_housingmod_master = IRSHousingModification(
    Killing_Config=WaningEffectExponential(
        Initial_Effect=0.5,
        Decay_Time_Constant=90
    ),
    Blocking_Config=WaningEffectExponential(
        Initial_Effect=0.0,
        Decay_Time_Constant=730
    ),
    Cost_To_Consumer=8.0
)

node_irs_config = SpaceSpraying(
    Reduction_Config=WaningEffectExponential(
        Decay_Time_Constant=365,
        Initial_Effect=0
    ),
    Cost_To_Consumer=1.0,
    Habitat_Target=SpaceSpraying_Habitat_Target_Enum.ALL_HABITATS,
    Killing_Config=WaningEffectExponential(
        Decay_Time_Constant=90,
        Initial_Effect=0.5
    ),
    Spray_Kill_Target=SpaceSpraying_Spray_Kill_Target_Enum.SpaceSpray_Indoor
)


def add_IRS(config_builder, start: int = 0, coverage_by_ages: list = None, cost: int = 1, nodeIDs: list = None,
            killing_config: any = None,
            blocking_config: any = None, insecticide: str = None, node_property_restrictions: list = None,
            ind_property_restrictions: list = None, triggered_campaign_delay: int = 0,
            trigger_condition_list: list = None,
            listening_duration: int = -1,
            check_eligibility_at_trigger: bool = False):
    """
    Add an indoor residual spraying (IRS) intervention using the
    **IRSHousingModification** class, an individual-level intervention. This
    can be distributed on a scheduled day or can be triggered by a list of
    events.
    
    Args:
        config_builder: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            containing the campaign configuration.
        start: The day on which to start distributing the intervention
            (**Start_Day** parameter) or the day to begin monitoring for
            events that trigger IRS.
        coverage_by_ages: A list of dictionaries defining the coverage per
            age group or birth-triggered intervention. For example,
            ``[{"coverage":1,"min": 1, "max": 10},{"coverage":1,"min": 11,
            "max": 50}]``
        cost: The per-unit cost (**Cost_To_Consumer** parameter).
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        killing_config: The value passed gets directly assigned to the Killing_Config parameter.
            Durations are in days.
            Default is killing_config = WaningEffectExponential(Initial_Effect=0.5, Decay_Time_Constant=90)
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
        blocking_config: The value passed gets directly assigned to the Blocking_Config parameter.
            Durations are in days.
            Default is blocking_config=WaningEffectExponential(Initial_Effect=0.0,Decay_Time_Constant=730)
            This could be dictionary such as:
            {
                "Box_Duration": 3650,
                "Initial_Effect": 0,
                "class": "WaningEffectBox"
            }
            OR CampaignClass-created object/parameter configuration such as:
            WaningEffectExponential(
                    Decay_Time_Constant=450,
                    Initial_Effect=0.8
            )
        insecticide: Insecticide name to be used with the intervention, must match one from config.json
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention (
            **Property_Restrictions_Within_Node** parameter). In the format ``[{
            "BitingRisk":"High"}, {"IsCool":"Yes}]``.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention (**Node_Property_Restrictions**
            parameter). In the format ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``
        triggered_campaign_delay: After the trigger is received, the number of
            time steps until the campaign starts. Eligibility of people or nodes
            for the campaign is evaluated on the start day, not the triggered
            day.
        trigger_condition_list: (Optional) A list of the events that will
            trigger the IRS intervention. If included, **start** is the day
            when monitoring for triggers begins. This argument cannot
            configure birth-triggered IRS (use **coverage_by_ages** instead).
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
            killing_config = WaningEffectRandomBox( Initial_Effect=0.95, Expected_Discard_Time=200)
            blocking_config = WaningEffectExponential(Decay_Time_Constant=450, Initial_Effect=0.8)
            add_IRS(config_builder, start=1,
                    coverage_by_ages=[{"coverage":1,"min": 1, "max": 18},
                                      {"coverage":0.6,"min": 19, "max": 80}],
                    cost=1, nodeIDs=[1, 2, 5],
                    duration=90, listening_duration=-1)
    """

    receiving_irs_event = BroadcastEvent(Broadcast_Event="Received_IRS")
    irs_housingmod = copy.deepcopy(irs_housingmod_master)

    if insecticide:
        irs_housingmod.Insecticide_Name = insecticide
    if killing_config:
        irs_housingmod.Killing_Config = killing_config
    if blocking_config:
        irs_housingmod.Blocking_Config = blocking_config
    if not nodeIDs:
        nodeset_config = NodeSetAll()
    else:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    irs_housingmod.Cost_To_Consumer = cost
    if not node_property_restrictions:
        node_property_restrictions = []
    if not ind_property_restrictions:
        ind_property_restrictions = []
    if not coverage_by_ages:
        raise ValueError("Please define coverage_by_ages. A list of dictionaries defining the coverage per"
                         "age group or birth-triggered intervention. For example,"
                         '``[{"coverage":1,"min": 1, "max": 10},{"coverage":1,"min": 11,'
                         '"max": 50}]``"')

    irs_housingmod_w_event = MultiInterventionDistributor(Intervention_List=[irs_housingmod, receiving_irs_event])

    if triggered_campaign_delay:
        trigger_node_property_restrictions = []
        trigger_ind_property_restrictions = []
        if check_eligibility_at_trigger:
            trigger_node_property_restrictions = node_property_restrictions
            trigger_ind_property_restrictions = ind_property_restrictions
            node_property_restrictions = []
            ind_property_restrictions = []
        trigger_condition_list = [triggered_campaign_delay_event(config_builder, start=start, nodeIDs=nodeIDs,
                                                                 triggered_campaign_delay=triggered_campaign_delay,
                                                                 trigger_condition_list=trigger_condition_list,
                                                                 listening_duration=listening_duration,
                                                                 ind_property_restrictions=trigger_node_property_restrictions,
                                                                 node_property_restrictions=trigger_ind_property_restrictions)]

    for coverage_by_age in coverage_by_ages:
        if trigger_condition_list:
            if 'birth' not in coverage_by_age.keys():
                IRS_event = CampaignEvent(
                    Start_Day=int(start),
                    Nodeset_Config=nodeset_config,
                    Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                        Intervention_Config=NodeLevelHealthTriggeredIV(
                            Trigger_Condition_List=trigger_condition_list,
                            Duration=listening_duration,
                            Property_Restrictions_Within_Node=ind_property_restrictions,
                            Node_Property_Restrictions=node_property_restrictions,
                            Demographic_Coverage=coverage_by_age["coverage"],
                            Target_Residents_Only=True,
                            Actual_IndividualIntervention_Config=irs_housingmod_w_event
                        )
                    )
                )

                if all([k in coverage_by_age.keys() for k in ['min', 'max']]):
                    IRS_event.Event_Coordinator_Config.Intervention_Config.Target_Demographic = NodeLevelHealthTriggeredIV_Target_Demographic_Enum.ExplicitAgeRanges
                    IRS_event.Event_Coordinator_Config.Intervention_Config.Target_Age_Min = coverage_by_age["min"]
                    IRS_event.Event_Coordinator_Config.Intervention_Config.Target_Age_Max = coverage_by_age["max"]

                config_builder.add_event(IRS_event)

        else:
            IRS_event = CampaignEvent(
                Start_Day=int(start),
                Nodeset_Config=nodeset_config,
                Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                    Demographic_Coverage=coverage_by_age["coverage"],
                    Target_Residents_Only=True,
                    Node_Property_Restrictions=node_property_restrictions,
                    Intervention_Config=irs_housingmod_w_event
                )
            )

            if all([k in coverage_by_age.keys() for k in ['min', 'max']]):
                IRS_event.Event_Coordinator_Config.Target_Demographic = StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.ExplicitAgeRanges
                IRS_event.Event_Coordinator_Config.Target_Age_Min = coverage_by_age["min"]
                IRS_event.Event_Coordinator_Config.Target_Age_Max = coverage_by_age["max"]

            if 'birth' in coverage_by_age.keys() and coverage_by_age['birth']:
                birth_triggered_intervention = BirthTriggeredIV(
                    Duration=coverage_by_age.get('duration', -1),  # default to forever if duration not specified
                    Demographic_Coverage=coverage_by_age["coverage"],
                    Actual_IndividualIntervention_Config=irs_housingmod_w_event
                )

                IRS_event.Event_Coordinator_Config.Intervention_Config = birth_triggered_intervention
                del IRS_event.Event_Coordinator_Config.Demographic_Coverage
                del IRS_event.Event_Coordinator_Config.Target_Residents_Only

            if ind_property_restrictions and 'birth' in coverage_by_age.keys() and coverage_by_age['birth']:
                IRS_event.Event_Coordinator_Config.Intervention_Config.Property_Restrictions_Within_Node = ind_property_restrictions
            elif ind_property_restrictions:
                IRS_event.Event_Coordinator_Config.Property_Restrictions_Within_Node = ind_property_restrictions

            if node_property_restrictions:
                IRS_event.Event_Coordinator_Config.Node_Property_Restrictions = node_property_restrictions

            config_builder.add_event(IRS_event)


def add_node_IRS(config_builder, start: int = 1, cost: int = None, killing_config: any = None,
                 reduction_config: any = None, insecticide: str = None,
                 irs_ineligibility_duration: int = 0, nodeIDs: list = None, node_property_restrictions: list = None,
                 triggered_campaign_delay: int = 0, trigger_condition_list: list = None, listening_duration: int = -1,
                 check_eligibility_at_trigger: bool = False):
    """
    Add an indoor residual spraying (IRS) intervention using the
    **SpaceSpraying** class, a node-level intervention. This can be distributed
    on a scheduled day or can be triggered by a list of events.

    Args:
        config_builder: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            containing the campaign configuration.
        start: The day on which to start distributing the intervention
            (**Start_Day** parameter) or the day to begin monitoring for
            events that trigger IRS.
        killing_config: The value passed gets directly assigned to the Killing_Config parameter.
            Durations are in days.
            Default is killing_config = WaningEffectExponential(Initial_Effect=0.5, Decay_Time_Constant=90)
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
        reduction_config: The configuration of larval habitat reduction and waning for space spraying.
            The value passed in is directly assigned to the Reduction_Config parameter
            Durations are in days.
            Default is reduction_config=WaningEffectExponential(Decay_Time_Constant=365, Initial_Effect=0)
            This could be dictionary such as:
            {
                "Box_Duration": 3650,
                "Initial_Effect": 0,
                "class": "WaningEffectBox"
            }
            OR CampaignClass-created object/parameter configuration such as:
            WaningEffectExponential(
                    Decay_Time_Constant=450,
                    Initial_Effect=0.8
            )
        insecticide: Insecticide name to be used with the intervention, must match one from config.json
        cost: The per-unit cost (**Cost_To_Consumer** parameter).
        irs_ineligibility_duration: The number of time steps after a node is
            sprayed before it is eligible for another round of IRS.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention (**Node_Property_Restrictions**
            parameter). In the format ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``
        triggered_campaign_delay: After the trigger is received, the number of
            time steps until the campaign starts. Eligibility of people or nodes
            for the campaign is evaluated on the start day, not the triggered
            day.
        trigger_condition_list: (Optional) A list of the events that will
            trigger the IRS intervention. If included, **start** is the day
            when monitoring for triggers begins. This argument cannot
            configure birth-triggered IRS (use **coverage_by_ages** instead).
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
            reduction_config ={
                "Box_Duration": 3650,
                "Initial_Effect": 0,
                "class": "WaningEffectBox"
            }
            killing_config = WaningEffectRandomBox(
                    Initial_Effect=0.95,
                    Expected_Discard_Time=200
            )
            add_node_IRS(config_builder, start=15, killing_config = killing_config, cost=1,
                         irs_ineligibility_duration=14, nodeIDs=[2, 25],
                         triggered_campaign_delay=7,
                         trigger_condition_list=['NewSevereCase'],
                         listening_duration=-1)
    """
    irs_config = copy.deepcopy(node_irs_config)
    if killing_config:
        irs_config.Killing_Config = killing_config
    if reduction_config:
        irs_config.Reduction_Config = reduction_config
    if not nodeIDs:
        nodeset_config = NodeSetAll()
    else:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    if not node_property_restrictions:
        node_property_restrictions = []
    if insecticide:
        irs_config.Insecticide_Name = insecticide
    if cost:
        irs_config.Cost_To_Consumer = cost

    node_sprayed_event = BroadcastNodeEvent(Broadcast_Event="Node_Sprayed")

    IRS_event = CampaignEvent(
        Start_Day=int(start),
        Nodeset_Config=nodeset_config,
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            Node_Property_Restrictions=node_property_restrictions,
            Intervention_Config=MultiInterventionDistributor(
                Intervention_List=[irs_config, node_sprayed_event]
            )
        ),
        Event_Name="Node Level IRS"
    )

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

        IRS_event.Event_Coordinator_Config.Intervention_Config = NodeLevelHealthTriggeredIV(
            Blackout_On_First_Occurrence=True,
            Blackout_Event_Trigger="IRS_Blackout_%d" % random.randint(0, 10000),
            Blackout_Period=1,
            Node_Property_Restrictions=node_property_restrictions,
            Duration=listening_duration,
            Trigger_Condition_List=trigger_condition_list,
            Actual_NodeIntervention_Config=MultiNodeInterventionDistributor(
                Node_Intervention_List=[irs_config, node_sprayed_event]),
            Target_Residents_Only=True
        )

        del IRS_event.Event_Coordinator_Config.Node_Property_Restrictions

    irc_cfg = copy.copy(IRS_event)

    if irs_ineligibility_duration > 0:
        recent_irs = NodePropertyValueChanger(
            Target_NP_Key_Value="SprayStatus:RecentSpray",
            Daily_Probability=1.0,
            Maximum_Duration=0,
            Revert=irs_ineligibility_duration
        )

        if trigger_condition_list:
            irc_cfg.Event_Coordinator_Config.Intervention_Config.Actual_IndividualIntervention_Config.Intervention_List.append(
                recent_irs)
            if not node_property_restrictions:
                irc_cfg.Event_Coordinator_Config.Intervention_Config.Node_Property_Restrictions = [
                    {'SprayStatus': 'None'}]
            else:
                for n, np in enumerate(node_property_restrictions):
                    node_property_restrictions[n]['SprayStatus'] = 'None'
                irc_cfg.Event_Coordinator_Config.Intervention_Config.Node_Property_Restrictions = node_property_restrictions
        else:
            irc_cfg.Event_Coordinator_Config.Intervention_Config.Intervention_List.append(recent_irs)
            if not node_property_restrictions:
                irc_cfg.Event_Coordinator_Config.Node_Property_Restrictions = [{'SprayStatus': 'None'}]
            else:
                for n, np in enumerate(node_property_restrictions):
                    node_property_restrictions[n]['SprayStatus'] = 'None'
                irc_cfg.Event_Coordinator_Config.Node_Property_Restrictions = node_property_restrictions

    config_builder.add_event(irc_cfg)
