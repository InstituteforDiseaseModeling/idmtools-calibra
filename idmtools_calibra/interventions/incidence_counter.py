from idmtools_calibra.utils.Campaign.CampaignClass import *


def add_incidence_counter(cb,
                          start_day=0,
                          count_duration=365,
                          count_triggers=None,
                          threshold_type='COUNT',
                          action_list=None,
                          coverage=1,
                          repetitions=1,
                          tsteps_btwn_repetitions=None,
                          target_group='Everyone',
                          nodeIDs=None,
                          node_property_restrictions=None,
                          ind_property_restrictions=None
                          ):
    """
    Add an intervention that monitors for the number of new cases that occur
    during a given time period using the **IncidenceEventCoordinator** class.


    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            that will receive the intervention.
        start_day: The day to distribute the intervention (**Start_Day**
            parameter).
        repetitions: The number of times to repeat the intervention.
        tsteps_btwn_repetitions:  The number of time steps between repetitions.
        count_duration: The number of time steps during which to monitor for
            new cases.
        count_triggers: A list of the events that will increment the
            monitor's count.
            Default: ['NewClinicalCase', 'NewSevereCase']
        threshold_type: To monitor raw counts, use COUNT; to normalize
            by population, use PERCENTAGE.
        action_list: List (array) of dictionaries, including the values specified with the
            following parameters: Event_To_Broadcast, Event_Type, Threshold.
            Default:
            [{"Event_To_Broadcast": "Action1",
                        "Event_Type": Action_Value_Event_Type_Enum.INDIVIDUAL,
                        "Threshold": 10},
                       {{"Event_To_Broadcast": "Action2",
                         "Event_Type": Action_Value_Event_Type_Enum.NODE,
                         "Threshold": 100}}]
        coverage: The demographic coverage of the monitoring. This value
            affects the probability that a **count_trigger** will be counted by
            is ignored for calculating the denominator for PERCENTAGE.
        target_group: Optionally, the age range that monitoring is restricted
            to, formatted as a dict of ``{'agemin': x, 'agemax': y}``. By
            default, everyone is monitored.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention (
            **Property_Restrictions_Within_Node** parameter). In the format
            ``[{"IndividualProperty1: "PropertyValue1"},
            {"IndividualProperty2: "IndividualValue2"} ...]``.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention (**Node_Property_Restrictions**
            parameter). In the format ``[{"NodeProperty1": "PropertyValue1"},
            {"NodeProperty2": "PropertyValue2"}, ...]``.

    Returns:
        None

    Example:
        ::

            cb = DTKConfigBuilder.from_defaults(sim_example)
            add_incidence_counter(cb, start_day=1, count_duration=90,
                                  count_triggers=['NewClinicalCase',
                                                  'NewSevereCase'],
                                  threshold_type='PERCENTAGE',
                                  action_list= [{"Event_To_Broadcast": "Action1",
                                    "Event_Type": Action_Value_Event_Type_Enum.INDIVIDUAL,
                                    "Threshold": 0.1},
                                   {{"Event_To_Broadcast": "Action2",
                                    "Event_Type": Action_Value_Event_Type_Enum.NODE,
                                    "Threshold": 0.5}}]
                                  coverage=1, repetitions=4,
                                  tsteps_btwn_repetitions=90,
                                  target_group='Everyone',
                                  node_property_restrictions=[{'Place':'Rural'}]
                                 )

    """
    if not count_triggers:
        count_triggers = ['NewClinicalCase', 'NewSevereCase']
    if not ind_property_restrictions:
        ind_property_restrictions = []
    if not node_property_restrictions:
        node_property_restrictions = []
    if not nodeIDs:
        nodeset_config = NodeSetAll()
    else:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    if not action_list:
        action_list = [{"Event_To_Broadcast": "Action1",
                        "Event_Type": Action_Value_Event_Type_Enum.INDIVIDUAL,
                        "Threshold": 10},
                       {{"Event_To_Broadcast": "Action2",
                         "Event_Type": Action_Value_Event_Type_Enum.NODE,
                         "Threshold": 100}}]
    if not tsteps_btwn_repetitions:
        tsteps_btwn_repetitions = count_duration

    monitoring_event = CampaignEvent(
        Start_Day=start_day,
        Nodeset_Config=nodeset_config,
        Event_Coordinator_Config=IncidenceEventCoordinator(
            Number_Repetitions=repetitions,
            Timesteps_Between_Repetitions=tsteps_btwn_repetitions,
            Incidence_Counter={
                "Count_Events_For_Num_Timesteps": count_duration,
                "Trigger_Condition_List": count_triggers,
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": coverage,
                "Node_Property_Restrictions": node_property_restrictions,
                "Property_Restrictions_Within_Node": ind_property_restrictions
            },
            Responder={
                "Threshold_Type": threshold_type,
                "Action_List": action_list
            }
        )
    )
    if target_group != 'Everyone':
        monitoring_event.Event_Coordinator_Config.Incidene_Counter.update({
            "Target_Demographic": "ExplicitAgeRanges",  # Otherwise default is Everyone
            "Target_Age_Min": target_group['agemin'],
            "Target_Age_Max": target_group['agemax']
        })

    cb.add_event(monitoring_event)
