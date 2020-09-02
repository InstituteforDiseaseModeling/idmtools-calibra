import random
from dtk.interventions.triggered_campaign_delay_event import triggered_campaign_delay_event
from dtk.utils.Campaign.CampaignClass import *
from dtk.interventions.support_scripts import validate_distribution_dictionary


# the old MigrateTo has now been split into MigrateIndividuals and MigrateFamily.
# add_migration_event adds a MigrateIndividuals event.
def add_migration_event(cb, nodeto, start_day: int=0, coverage=1, repetitions=1, tsteps_btwn=365,
                        duration_at_node: dict= None,
                        duration_before_leaving: dict = None,
                        target='Everyone', nodesfrom=None,
                        ind_property_restrictions=None, node_property_restrictions=None, triggered_campaign_delay=0,
                        trigger_condition_list=None, listening_duration=-1, check_eligibility_at_trigger=False):

    """
    Add a migration event to a campaign that moves individuals from one node
    to another using the **MigrateIndividuals** class.

    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            containing the campaign configuration.
        nodeto: The NodeID that the individuals will travel to.
        start_day: A list of days when intervention is distributed
            (**Start_Day** parameter).
        coverage: The proportion of the population covered by the intervention
            (**Demographic_Coverage** parameter).
        repetitions: The number of times to repeat the intervention
            (**Number_Repetitions** parameter).
        tsteps_btwn: The number of time steps between repetitions.
        duration_before_leaving: Dictionary of parameters that define the distribution for duration before leaving node,
            including the distribution
            Default: {"Duration_Before_Leaving_Distribution":"CONSTANT_DISTRIBUTION",
                        "Duration_Before_Leaving_Constant" : 14}
            Durations are in days.
            Examples:
                {"Duration_Before_Leaving_Distribution":"GAUSSIAN_DISTRIBUTION",
                "Duration_Before_Leaving_Gaussian_Mean": 14, "Duration_Before_Leaving_Gaussian_Std_Dev" 3}
                {"Duration_Before_Leaving_Distribution":"POISSON_DISTRIBUTION",
                "Duration_Before_Leaving_Poisson_Mean" 30}
        duration_at_node: Dictionary of parameters that define the distribution for duration at node,
            including the distribution
            Default: {"Duration_At_Node_Distribution":"CONSTANT_DISTRIBUTION", "Duration_At_Node_Constant" : 14}
            Durations are in days.
            Examples:
                {"Duration_At_Node_Distribution":"GAUSSIAN_DISTRIBUTION",
                "Duration_At_Node_Gaussian_Mean": 14, "Duration_At_Node_Gaussian_Std_Dev" 3}
                {"Duration_At_Node_Distribution":"POISSON_DISTRIBUTION", "Duration_At_Node_Poisson_Mean" 30}
        target: The individuals to target with the intervention. To
            restrict by age, provide a dictionary of {'agemin' : x, 'agemax' :
            y}. Default is targeting everyone.
        nodesfrom: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention
            (**Property_Restrictions_Within_Node** parameter). In the format
            ``[{"BitingRisk":"High"}, {"IsCool":"Yes}]``.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention
            (**Node_Property_Restrictions** parameter). In the format
            ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``.
        triggered_campaign_delay: After the trigger is received, the number of
            time steps until distribution starts. Eligibility of people or nodes
            for the campaign is evaluated on the start day, not the triggered
            day.
        trigger_condition_list: A list of the events that will
            trigger the intervention. If included, **start_days** is
            then used to distribute **NodeLevelHealthTriggeredIV**.
        listening_duration: The number of time steps that the distributed
            event will monitor for triggers. Default is -1, which is
            indefinitely.

    Returns:
        None


    NOTE:
        Previous was of setting discard times is no longer available, you can translate it to the current way by:
        discard_times the old way {'halflife1': 260, 'halflife2': 2106, 'fraction1': float(table_dict['fast_fraction'])

        discard_times translated = {"Expiration_Period_Distribution": "DUAL_EXPONENTIAL_DISTRIBUTION",
                 "Expiration_Period_Mean_1": discard_halflife, or halflife1
                 "Expiration_Period_Mean_2": 365 * 40, or halflife2
                 "Expiration_Period_Proportion_1": 1 or 'fraction1'}


    Example:
        ::
            cb = DTKConfigBuilder.from_defaults(sim_example)
            dan = {"Duration_At_Node_Distribution":"POISSON_DISTRIBUTION", "Duration_At_Node_Poisson_Mean" 30}
            dbl = {"Duration_Before_Leaving_Distribution":"GAUSSIAN_DISTRIBUTION",
                "Duration_Before_Leaving_Gaussian_Mean": 14, "Duration_Before_Leaving_Gaussian_Std_Dev" 3}
            add_migration_event(cb, nodeto=5, start_day=1, coverage=0.75, duration_at_node = dan,
                                duration_before_leaving = dbl,
                                repetitions=1, tsteps_btwn=90,
                                target='Everyone', nodesfrom={"class": "NodeSetAll"},
                                node_property_restrictions=[{"Place": "Rural"}])
    """
    if nodesfrom:
        node_cfg = NodeSetNodeList(Node_List=nodesfrom)
    else:
        node_cfg = NodeSetAll()
    if not ind_property_restrictions:
        ind_property_restrictions = []
    if not node_property_restrictions:
        node_property_restrictions = []
    if not duration_at_node:
        duration_at_node = {"Duration_At_Node_Distribution": "CONSTANT_DISTRIBUTION",
                            "Duration_At_Node_Constant": 14}
    if not duration_before_leaving:
        duration_before_leaving = {"Duration_Before_Leaving_Distribution": "CONSTANT_DISTRIBUTION",
                                   "Duration_Before_Leaving_Constant": 14}
    validate_distribution_dictionary("Duration_Before_Leaving", duration_before_leaving)
    validate_distribution_dictionary("Duration_At_Node", duration_at_node)

    migration_event = MigrateIndividuals(NodeID_To_Migrate_To=nodeto)
    for param in duration_before_leaving:
        setattr(migration_event, param, duration_before_leaving[param])
    for param in duration_at_node:
        setattr(migration_event, param, duration_at_node[param])

    if trigger_condition_list:
        if repetitions > 1 or triggered_campaign_delay > 0:
            trigger_node_property_restrictions = []
            trigger_ind_property_restrictions = []
            if check_eligibility_at_trigger:
                trigger_node_property_restrictions = node_property_restrictions
                trigger_ind_property_restrictions = ind_property_restrictions
                node_property_restrictions = []
                ind_property_restrictions = []
            event_to_send_out = random.randrange(100000)
            for x in range(repetitions):
                # create a trigger for each of the delays.
                triggered_campaign_delay_event(cb, start=start_day, nodeIDs=nodesfrom,
                                               triggered_campaign_delay=triggered_campaign_delay + x * tsteps_btwn,
                                               trigger_condition_list=trigger_condition_list,
                                               listening_duration=listening_duration,
                                               event_to_send_out=event_to_send_out,
                                               ind_property_restrictions=trigger_ind_property_restrictions,
                                               node_property_restrictions=trigger_node_property_restrictions)
            trigger_condition_list = [str(event_to_send_out)]

        event = CampaignEvent(
            Event_Name="Migration Event Triggered",
            Start_Day=start_day,
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Intervention_Config=NodeLevelHealthTriggeredIV(
                    Duration=listening_duration,
                    Trigger_Condition_List=trigger_condition_list,
                    Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum[target],
                    Target_Residents_Only=True,
                    Node_Property_Restrictions=node_property_restrictions,
                    Property_Restrictions_Within_Node=ind_property_restrictions,
                    Demographic_Coverage=coverage,
                    Actual_IndividualIntervention_Config=migration_event
                )
            ),
            Nodeset_Config=node_cfg
        )

        if isinstance(target, dict) and all([k in target.keys() for k in ['agemin', 'agemax']]):
            event.Event_Coordinator_Config.Intervention_Config.Target_Demographic = StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.ExplicitAgeRanges
            event.Event_Coordinator_Config.Intervention_Config.Target_Age_Min = target['agemin']
            event.Event_Coordinator_Config.Intervention_Config.Target_Age_Max = target['agemax']

    else:
        event = CampaignEvent(
            Event_Name="Migration Event",
            Start_Day=start_day,
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Property_Restrictions_Within_Node=ind_property_restrictions,
                Node_Property_Restrictions=node_property_restrictions,
                Number_Distributions=-1,
                Number_Repetitions=repetitions,
                Target_Residents_Only=True,
                Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum[target],
                Timesteps_Between_Repetitions=tsteps_btwn,
                Demographic_Coverage=coverage,
                Intervention_Config=migration_event
            ),
            Nodeset_Config=node_cfg
        )

        if isinstance(target, dict) and all([k in target for k in ['agemin', 'agemax']]):
            event.Event_Coordinator_Config.Target_Demographic = StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.ExplicitAgeRanges
            event.Event_Coordinator_Config.Target_Age_Min = target['agemin']
            event.Event_Coordinator_Config.Target_Age_Max = target['agemax']

    cb.add_event(event)

