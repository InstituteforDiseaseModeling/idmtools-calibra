import copy
import math
import collections
from dtk.utils.Campaign.CampaignClass import *


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def add_vaccine(cb, vaccine_type: str='RTSS', vaccine_params: dict=None, start_days: list=None,
                coverage: float=1.0, repetitions: int=1, tsteps_btwn_repetitions: int=365,
                nodes: list=None, target_group: any='Everyone', node_property_restrictions: list=None,
                ind_property_restrictions: list=None, disqualifying_properties: list=None,
                trigger_condition_list: list=None, triggered_delay: int=0,
                listening_duration: int=-1, target_residents_only: bool=1):
    """
    Add vaccine distribution event and returns vaccine coverage parameters.

    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` 
            object for building, modifying, and writing campaign 
            configuration files.
        vaccine_type: String describing vaccine type. Default is RTSS. 
            Available options are:
            * RTSS
            * PEV
            * TBV
        vaccine_params: (Optional) dictionary of vaccine configuration 
            parameters. Params come from pre-defined vaccine_type.
        start_days: List of ints of days when vaccine is given out. 
            Default is None (day 0, beginning of simulation).
        coverage: Demographic coverage of the intervention. 
            Default is 1, everyone.
        repetitions: How many times to repeat vaccine distribution. 
            Default is 3.
        tsteps_btwn_repetitions: How long between vaccine distributions. 
            Default is 60 days.
        nodes: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        target_group: A dictionary of ``{'agemin': x, 'agemax': y}`` to 
            target vaccine to individuals between x and y years 
            of age. Default is Everyone.
        node_property_restrictions: List of NodeProperty key:value pairs that nodes 
            must have to receive the diagnostic intervention. For example, 
            ``[{"NodeProperty1":"PropertyValue1"}, 
            {"NodeProperty2":"PropertyValue2"}]``. Default is no restrictions.
        ind_property_restrictions: List of IndividualProperty key:value pairs that 
            individuals must have to receive the diagnostic intervention. 
            For example, ``[{"IndividualProperty1":"PropertyValue1"}, 
            {"IndividualProperty2":"PropertyValue2"}]``. Default is no restrictions.
        disqualifying_properties: List of IndividualProperty key:value pairs that 
            cause an intervention to be aborted. For example, 
            ``[{"IndividualProperty1":"PropertyValue1"}, 
            {"IndividualProperty2":"PropertyValue2"}]``.
        trigger_condition_list: List of events that trigger the vaccine distribution 
            and creates a triggered intervention that is distributed on ``start_days[0]``. 
            Default is a non-triggered intervention unless this is present.
        triggered_delay: If triggered intervention then a delay before vaccines are 
            distributed. Default is 0.
        listening_duration: If triggered intervention then how long intervention will 
            exist and wait for a trigger. Default is -1, ongoing.
        target_residents_only: When set to true (1), the intervention is only 
            distributed to individuals for whom the node is their home node 
            (they are not visitors from another node).

    Returns:
        Vaccine coverage params
    """
    if vaccine_type not in ['RTSS', 'PEV', 'TBV']:
        raise ValueError("Unknown vaccine type: {}; valid vaccines:\n"
                         " \"RTSS\": simple vaccine\n"
                         " \"PEV\": preerythrocytic vaccine\n"
                         " \"TBV\": sexual stage vacine \n".format(vaccine_type))
    if ind_property_restrictions is None:
        ind_property_restrictions = []
    if node_property_restrictions is None:
        node_property_restrictions = []
    if disqualifying_properties is None:
        disqualifying_properties = []
    if nodes:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    else:
        nodeset_config = NodeSetAll()
    if not start_days:
        start_days = [0]

    vaccine_dict = load_vaccines()
    vaccine = copy.deepcopy(vaccine_dict[vaccine_type])

    if vaccine_params:
        for param in vaccine_params:
            setattr(vaccine, param, vaccine_params[param])

    receiving_vaccine_event = BroadcastEvent(Broadcast_Event="Received_Vaccine")
    interventions = [vaccine, receiving_vaccine_event]

    if trigger_condition_list:
        if triggered_delay > 0:
            actual_config = DelayedIntervention(
                Delay_Period_Distribution="CONSTANT_DISTRIBUTION",
                Delay_Period_Constant=triggered_delay,
                Actual_IndividualIntervention_Configs=interventions
            )
        else:
            actual_config = MultiInterventionDistributor(Intervention_List=interventions)

        vaccine_event = CampaignEvent(
            Start_Day=start_days[0],
            Nodeset_Config=nodeset_config,
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Intervention_Config=NodeLevelHealthTriggeredIV(
                    Node_Property_Restrictions=node_property_restrictions,
                    Property_Restrictions_Within_Node=ind_property_restrictions,
                    Disqualifying_Properties=disqualifying_properties,
                    Demographic_Coverage=coverage,
                    Trigger_Condition_List=trigger_condition_list,
                    Duration=listening_duration,
                    Target_Residents_Only=target_residents_only,
                    Actual_IndividualIntervention_Config=actual_config)))

        if target_group != 'Everyone':
            vaccine_event.Event_Coordinator_Config.Intervention_Config.Target_Demographic = "ExplicitAgeRanges"
            vaccine_event.Event_Coordinator_Config.Intervention_Config.Target_Age_Min = target_group['agemin']
            vaccine_event.Event_Coordinator_Config.Intervention_Config.Target_Age_Max = target_group['agemax']

        cb.add_event(vaccine_event)

    else:
        for start_day in start_days:
            vaccine_event = CampaignEvent(
                Start_Day=start_day,
                Nodeset_Config=nodeset_config,
                Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                    Node_Property_Restrictions=node_property_restrictions,
                    Property_Restrictions_Within_Node=ind_property_restrictions,
                    Demographic_Coverage=coverage,
                    Intervention_Config=MultiInterventionDistributor(
                        Intervention_List=interventions),
                    Number_Repetitions=repetitions,
                    Target_Age_Max=125,
                    Target_Age_Min=0,
                    Target_Demographic="Everyone",
                    Timesteps_Between_Repetitions=tsteps_btwn_repetitions))

            if target_group != 'Everyone':
                vaccine_event.Event_Coordinator_Config.Target_Demographic = "ExplicitAgeRanges"
                vaccine_event.Event_Coordinator_Config.Target_Age_Min = target_group['agemin']
                vaccine_event.Event_Coordinator_Config.Target_Age_Max = target_group['agemax']

            cb.add_event(vaccine_event)

    if vaccine_params:
        return_params = flatten(vaccine_params, parent_key=vaccine_type)
        return_params.update({"{vaccine}_Coverage".format(vaccine=vaccine_type): coverage})
    else:
        return_params = {"{vaccine}_Coverage".format(vaccine=vaccine_type): coverage}

    return return_params


def load_vaccines():
    """

    Returns: Dictionary of vaccine types.

    """
    # Pre-erythrocytic simple vaccine
    preerythrocytic_vaccine = SimpleVaccine(
        Vaccine_Type="AcquisitionBlocking",
        Vaccine_Take=1,
        Waning_Config=WaningEffectExponential(
            Initial_Effect=0.9,
            Decay_Time_Constant=(365 * 5)/math.log(2)),
        Cost_To_Consumer=15,
        Efficacy_Is_Multiplicative=0)

    # Transmission-blocking sexual-stage vaccine
    sexual_stage_vaccine = copy.deepcopy(preerythrocytic_vaccine)
    sexual_stage_vaccine.Vaccine_Type = "TransmissionBlocking"

    # RTS,S simple vaccine
    rtss_simple_vaccine = copy.deepcopy(preerythrocytic_vaccine)
    rtss_simple_vaccine.Waning_Config = WaningEffectExponential(
        Initial_Effect=0.8,
        Decay_Time_Constant=(365 * 1.125) / math.log(2)) # 13.5 month half-life

    vaccine_dict = {'RTSS': rtss_simple_vaccine,
                    'PEV': preerythrocytic_vaccine,
                    'TBV': sexual_stage_vaccine}

    return vaccine_dict
