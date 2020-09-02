import numpy as np
import sys
from dtk.interventions.triggered_campaign_delay_event import triggered_campaign_delay_event
from dtk.interventions.support_scripts import validate_distribution_dictionary
from dtk.utils.Campaign.CampaignClass import *


def add_ITN_age_season(config_builder, start: int = 1, demographic_coverage: float = 1, blocking_config: any = None,
                       killing_config: any = None, repelling_config: any = None, insecticide: str = None, discard_times: dict = None,
                       age_dependence: dict = None, seasonal_dependence: dict = None, cost: int = 5,
                       nodeIDs: list = None,
                       birth_triggered: bool = False, duration: int = -1,
                       triggered_campaign_delay: int = 0, trigger_condition_list: list = None,
                       ind_property_restrictions: list = None, node_property_restrictions: list = None,
                       check_eligibility_at_trigger: bool = False):
    """
    Add an insecticide-treated net (ITN) intervention with a seasonal usage
    pattern to the campaign using the **UsageDependentBednet** class. The
    arguments **birth_triggered** and **triggered_condition_list** are mutually
    exclusive. If both are provided, **triggered_condition_list** is ignored.

    You must add the following custom events to your config.json:
        
        * Bednet_Discarded
        * Bednet_Got_New_One
        * Bednet_Using

    Args:

        config_builder: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            containing the campaign configuration.
        start: The day on which to start distributing the bednets
            (**Start_Day** parameter).
        demographic_coverage: Fraction of the population receiving bed nets in a given distribution event
        blocking_config: The value passed gets directly assigned to the Blocking_Config parameter.
            Durations are in days.
            Default is blocking_config= WaningEffectExponential(Decay_Time_Constant=730, Initial_Effect=0.9)
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
        killing_config: The value passed gets directly assigned to the Killing_Config parameter.
            Durations are in days.
            Default is killing_config = WaningEffectExponential(Decay_Time_Constant=1460, Initial_Effect=0.6)
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
        repelling_config: The value passed gets directly assigned to the Repelling_Config parameter.
            Durations are in days.
            Default is repelling_config = WaningEffectExponential(Decay_Time_Constant=1460, Initial_Effect=0.0)
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
        discard_times: A dictionary of parameters needed to define expiration distribution.
            No need to definite the distribution with all its parameters
            Default is bednet being discarded with EXPONENTIAL_DISTRIBUTION with Expiration_Period_Exponential of 10 years
            Examples:
                for Gaussian: {"Expiration_Period_Distribution": "GAUSSIAN_DISTRIBUTION",
                    "Expiration_Period_Gaussian_Mean": 20, "Expiration_Period_Gaussian_Std_Dev":10}
                for Exponential {"Expiration_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
                    "Expiration_Period_Exponential":150}
        age_dependence: A dictionary defining the age dependence of net use.
            Must contain a list of ages in years and list of usage rate. Default
            is uniform across all ages.
            Times are in years of age
            Examples:
                {"Times":[], "Values":[]} or {"youth_cov":0.7, "youth_min_age":3, "youth_max_age":13}
        seasonal_dependence: A dictionary defining the seasonal dependence of net use.
            Default is constant use during the year. Times are given in days
            of the year; values greater than 365 are ignored. Dictionaries
            can be (times, values) for linear spline or (minimum coverage,
            day of maximum coverage) for sinusoidal dynamics.
            Times are days of the year
            Examples:
                {"Times":[], "Values":[]} or {"min_cov":0.45, "max_day":300}
        cost: The per-unit cost (**Cost_To_Consumer** parameter).
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        birth_triggered: If true, event is specified as a birth-triggered intervention.
        duration: If run as a birth-triggered event or a trigger_condition_list,
            specifies the duration for the distribution to continue. Default
            is to continue until the end of the simulation.
        triggered_campaign_delay: (Optional) After the trigger is received,
            the number of time steps until the campaign starts. Eligibility
            of people or nodes for the campaign is evaluated on the start
            day, not the triggered day.
            Delay is in days
        trigger_condition_list: (Optional) A list of the events that will
            trigger the ITN intervention. If included, **start** is the day
            when monitoring for triggers begins. This argument cannot
            configure birth-triggered ITN (use **birth_triggered** instead).
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention (
            **Property_Restrictions_Within_Node** parameter). In the format ``[{
            "BitingRisk":"High"}, {"IsCool":"Yes}]``.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention (**Node_Property_Restrictions**
            parameter). In the format ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``
        check_eligibility_at_trigger: if triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay.


    Returns:
        None

    Example:
        ::

            config_builder = DTKConfigBuilder.from_defaults(sim_example)
            killing_config = WaningEffectConstant(Initial_Effect=0.5) # using CampaignClass
            blocking_config = WaningEffectBox(Box_Duration= 250, Initial_Effect=0.87)
            discard_times = {"Expiration_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
                         "Expiration_Period_Exponential": 10 * 365}
            age_dependence = {"Times": [0, 4, 10, 60],
                       "Values": [1, 0.9, 0.8, 0.5]}
            add_ITN_age_season(config_builder, start=1, demographic_coverage=1, killing_config=killing_config,
                        blocking_config=blocking_config, discard_times = discard_times
                        age_dependence=age_dependence, cost=5, birht_triggered=True, duration=-1,
                        node_property_restrictions=[{"Place": "Rural"]):
    """

    if nodeIDs:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    else:
        nodeset_config = NodeSetAll()
    if not node_property_restrictions:
        node_property_restrictions = []
    if not ind_property_restrictions:
        ind_property_restrictions = []
    if not blocking_config:
        blocking_config = WaningEffectExponential(Decay_Time_Constant=730, Initial_Effect=0.9)
    if not killing_config:
        killing_config = WaningEffectExponential(Decay_Time_Constant=1460, Initial_Effect=0.6)
    if not repelling_config:
        repelling_config = WaningEffectExponential(Decay_Time_Constant=1460, Initial_Effect=0.0)
    if not discard_times:
        discard_times = {"Expiration_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
                         "Expiration_Period_Exponential": 10 * 365}

    # Assign seasonal net usage
    # Times are days of the year
    # Input can be provided either as (times, values) for linear spline or (min coverage, day of maximum coverage)
    # under the assumption of sinusoidal dynamics. In the first case, the same value should be provided
    # for both 0 and 365; times > 365 will be ignored.
    seasonal_times = np.append(np.arange(0, 361, 30), 365)
    seasonal_values = np.linspace(1, 1, len(seasonal_times))
    if not seasonal_dependence:
        pass
    elif all([k in seasonal_dependence.keys() for k in ['Times', 'Values']]):
        seasonal_times = seasonal_dependence['Times']
        seasonal_values = seasonal_dependence['Values']
    elif all([k in seasonal_dependence.keys() for k in ['min_cov', 'max_day']]):
        seasonal_times = np.append(np.arange(0, 361, 30), 365)
        if seasonal_dependence['min_cov'] == 0:
            seasonal_dependence['min_cov'] = seasonal_dependence['min_cov'] + sys.float_info.epsilon
        seasonal_values = (1 - seasonal_dependence['min_cov']) / 2 * np.cos(
            2 * np.pi / 365 * (seasonal_times - seasonal_dependence['max_day'])) + \
                          (1 + seasonal_dependence['min_cov']) / 2
    else:
        raise ValueError('Did not find all the keys were were looking for. Possible dictionaries can be:\n'
                         '{"Times":[], "Values":[]} or {"min_cov":0.45, "max_day":300}\n')

    # Assign age-dependent net usage #
    # Times are ages in years (note difference from seasonal dependence)
    age_times = [0, 125]  # Dan B has hard-coded an upper limit of 125, will return error for larger values
    age_values = [1, 1]
    if not age_dependence:
        pass
    elif all([k in age_dependence.keys() for k in ['Times', 'Values']]):
        age_times = age_dependence['Times']
        age_values = age_dependence['Values']
    elif all([k in age_dependence.keys() for k in ['youth_cov', 'youth_min_age', 'youth_max_age']]):
        age_times = [0, age_dependence['youth_min_age'] - 0.1, age_dependence['youth_min_age'],
                     age_dependence['youth_max_age'] - 0.1, age_dependence['youth_max_age']]
        age_values = [1, 1, age_dependence['youth_cov'], age_dependence['youth_cov'], 1]
    else:
        raise ValueError('Did not find all the keys were were looking for. Possible dictionaries can be:\n'
                         '{"Times":[], "Values":[]} or {"youth_cov":0.7, "youth_min_age":3, "youth_max_age":13}\n')

    itn_campaign = UsageDependentBednet(
        Bednet_Type="ITN",
        Blocking_Config=blocking_config,
        Cost_To_Consumer=cost,
        Killing_Config=killing_config,
        Repelling_Config=repelling_config,
        Usage_Config_List=
        [
            WaningEffectMapLinearAge(
                Initial_Effect=1.0,
                Durability_Map=
                {
                    "Times": list(age_times),
                    "Values": list(age_values)
                }
            ),
            WaningEffectMapLinearSeasonal(
                Initial_Effect=1.0,
                Durability_Map=
                {
                    "Times": list(seasonal_times),
                    "Values": list(seasonal_values)
                }
            )
        ],
        Received_Event="Bednet_Got_New_One",
        Using_Event="Bednet_Using",
        Discard_Event="Bednet_Discarded"
    )

    validate_distribution_dictionary("Expiration_Period", discard_times)
    for param in discard_times:
        setattr(itn_campaign, param, discard_times[param])

    if insecticide:
        itn_campaign.Insecticide_Name = insecticide

    # General or birth-triggered
    if birth_triggered:
        itn_event = CampaignEvent(
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Node_Property_Restrictions=node_property_restrictions,
                Property_Restrictions_Within_Node=ind_property_restrictions,
                Intervention_Config=BirthTriggeredIV(
                    Actual_IndividualIntervention_Config=itn_campaign,
                    Demographic_Coverage=demographic_coverage,
                    Duration=duration
                )
            ),
            Nodeset_Config=nodeset_config,
            Start_Day=start
        )

    else:
        if trigger_condition_list:
            if triggered_campaign_delay:
                trigger_node_property_restrictions = []
                trigger_ind_property_restrictions = []
                if check_eligibility_at_trigger:
                    trigger_node_property_restrictions = node_property_restrictions
                    trigger_ind_property_restrictions = ind_property_restrictions
                    node_property_restrictions = []
                    ind_property_restrictions = []
                trigger_condition_list = [triggered_campaign_delay_event(config_builder, start=start,
                                                                         nodeIDs=nodeIDs,
                                                                         triggered_campaign_delay=triggered_campaign_delay,
                                                                         trigger_condition_list=trigger_condition_list,
                                                                         listening_duration=duration,
                                                                         ind_property_restrictions=trigger_ind_property_restrictions,
                                                                         node_property_restrictions=trigger_node_property_restrictions)]

            itn_event = CampaignEvent(
                Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                    Intervention_Config=NodeLevelHealthTriggeredIV(
                        Demographic_Coverage=demographic_coverage,
                        Duration=duration,
                        Target_Residents_Only=True,
                        Trigger_Condition_List=trigger_condition_list,
                        Property_Restrictions_Within_Node=ind_property_restrictions,
                        Node_Property_Restrictions=node_property_restrictions,
                        Actual_IndividualIntervention_Config=itn_campaign
                    )
                ),
                Nodeset_Config=nodeset_config,
                Start_Day=start
            )
        else:
            itn_event = CampaignEvent(
                Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                    Intervention_Config=itn_campaign,
                    Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.Everyone,
                    Demographic_Coverage=demographic_coverage,
                    Property_Restrictions_Within_Node=ind_property_restrictions,
                    Node_Property_Restrictions=node_property_restrictions,
                    Duration=duration
                ),
                Nodeset_Config=nodeset_config,
                Start_Day=start
            )

    config_builder.add_event(itn_event)
