from malaria.interventions.malaria_drugs import drug_configs_from_code
from malaria.interventions.malaria_diagnostic import add_diagnostic_survey
from dtk.interventions.triggered_campaign_delay_event import triggered_campaign_delay_event
from copy import deepcopy, copy
import random
from dtk.utils.Campaign.CampaignClass import *


def add_drug_campaign(cb, campaign_type: str = 'MDA', drug_code: str = None, start_days: list = None,
                      coverage: float = 1.0,
                      repetitions: int = 1, tsteps_btwn_repetitions: int = 60,
                      diagnostic_type: str = 'BLOOD_SMEAR_PARASITES',
                      diagnostic_threshold: float = 40, diagnostic_sensitivity: float = 1,
                      diagnostic_specificity: float = 1,
                      measurement_sensitivity: float = 0.1, fmda_radius: int = 0,
                      node_selection_type: str = 'DISTANCE_ONLY',
                      trigger_coverage: float = 1.0, snowballs: int = 0, treatment_delay: int = 0,
                      triggered_campaign_delay: int = 0, nodeIDs: list = None, target_group: any = 'Everyone',
                      drug_ineligibility_duration: int = 0,
                      node_property_restrictions: list = None, ind_property_restrictions: list = None,
                      disqualifying_properties: list = None, trigger_condition_list: list = None,
                      listening_duration: int = -1, adherent_drug_configs: list = None, target_residents_only: int = 1,
                      check_eligibility_at_trigger: bool = False, receiving_drugs_event_name='Received_Campaign_Drugs'):
    """
    Add a drug intervention, as specified in **campaign_type**, to the campaign.
    This intervention uses the **MalariaDiagnostic** class to create either a
    scheduled or a triggered event to the campaign and the **AntimalarialDrug**
    class to configure drug parameters. You can also specify a delay period
    for a triggered event that broadcasts afterwards.

    .. note:: Dosing/Dosing_Type was removed, please use adeherent_drug_configs
        if you want something besides a full treatment. Also,
        drug_ineligibility_duration does not prevent diagnostics from being
        distributed, but it does prevent positively-tested patients from
        receiving the drugs.

    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            object for building, modifying, and writing campaign
            configuration files.
        campaign_type: Type of drug campaign. Default is **MDA**.
            Available options are:
            * MDA
            * MSAT
            * SMC
            * fMDA
            * MTAT
            * rfMSAT
            * rfMDA
        drug_code: The drug code of the drug regimen (AL, DP, etc;
            allowable types are defined in malaria_drugs.py).
        start_days: List of start days (integers) when the drug regimen will
            be distributed. Due to diagnostic/treatment configuration,
            the earliest start day is 1. When trigger_condition_list is used
            then the first entry of start_days is the day to start listening
            for the trigger(s).
        coverage: Demographic coverage of the distribution (fraction of
            people at home during campaign).
        repetitions: Number of repetitions.
        tsteps_btwn_repetitions: Timesteps between the repetitions.
        diagnostic_type: Diagnostic config for diagnostic-dependent
            campaigns:
            * MSAT
            * fMDA
            * rfMSAT
        diagnostic_threshold: Diagnostic config for diagnostic-dependent
            campaigns:
            * MSAT
            * fMDA
            * rfMSAT
        diagnostic_sensitivity: Setting for **Base_Sensitivity** in the MalariaDiagnostic
        diagnostic_specificity: Setting for **Base_Specificity** in the MalariaDiagnostic
        measurement_sensitivity: setting for **Measurement_Sensitivity** in MalariaDiagnostic
        fmda_radius: Radius (in km) of focal response upon finding infection.
            Default is 0. Used with household only.
        node_selection_type: Node selection type for broadcasting focal
            response trigger. Available options are:
            * DISTANCE_ONLY: It will send the event to nodes that are within a
            given distance.
            * MIGRATION_NODES_ONLY: It will only send the event to nodes that
            the individual can migrate to.
            * DISTANCE_AND_MIGRATION: It will only send the even to migratable
            nodes that are within a given distance. Migrateable nodes are Local
            and Regional.
        trigger_coverage: Used with RCD (Reactive Case Detection). Fraction of
            trigger events that will trigger an RCD. Coverage param sets the
            fraction of individuals reached during RCD response.
        snowballs: Number of snowball levels in reactive response.
        treatment_delay: For MSAT and fMDA, the length of time between
            administering diagnostic and giving drugs; for RCD, the length
            of time between treating index case and triggering RCD response.
        triggered_campaign_delay: When using trigger_condition_list, this
            indicates the delay period between receiving the trigger event
            and running the triggered campaign intervention.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        target_group: A dictionary of ``{'agemin': x, 'agemax': y}`` to
            target MDA, SMC, MSAT, fMDA to individuals between x and y years
            of age. Default is Everyone.
        drug_ineligibility_duration: When set to > 0, use IndividualProperties
            to prevent people from receiving drugs too frequently.
            Demographics file will need to define the IP DrugStatus with
            possible values None and RecentDrug. Individuals with status
            RecentDrug will not receive drugs during drug campaigns, though
            they are still eligible for receiving diagnostics (in MSAT, etc).
            Individuals who receive drugs during campaigns will have their
            DrugStatus changed to RecentDrug for drug_ineligibility_duration days.
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
        trigger_condition_list: List of events that will begin a triggerable
            drug campaign, such as MDA, MSAT, SMC, fMDA, and MTAT.
        listening_duration: Duration to listen for the trigger. Default is -1,
            which listens indefinitely.
        adherent_drug_configs: List of adherent drug configurations, which are
            dictionaries from configure_adherent_drug.
        target_residents_only: When set to true (1), the intervention is only
            distributed to individuals for whom the node is their home node.
            They are not visitors from another node.
        check_eligibility_at_trigger: If triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay.
        receiving_drugs_event_name: Event to send out when person received drugs.
            Default: 'Received_Campaign_Drugs'

    Returns:
        Dictionary with drug campaign parameters
    """
    if not drug_code and not adherent_drug_configs:
        raise Exception("You have to pass in  drug_code(AL, DP, etc; allowable types defined in malaria_drugs.py) or"
                        "a list of adherent_drug_configs, which can be generated with adherent_drug.py/configure_"
                        "adherent_drug.\n")
    elif drug_code and adherent_drug_configs:
        raise Exception("You passed in a drug_code AND a list of adherent_drug_configs. Please pick one.\n")
    if adherent_drug_configs:
        drug_configs = adherent_drug_configs
    else:
        drug_configs = drug_configs_from_code(cb, drug_code=drug_code)

    # set up events to broadcast when receiving campaign drug
    receiving_drugs_event = BroadcastEvent(Broadcast_Event=receiving_drugs_event_name)
    if campaign_type[0] == 'r':  # if reactive campaign
        receiving_drugs_event.Broadcast_Event = 'Received_RCD_Drugs'
    if drug_code and 'Vehicle' in drug_code:  # if distributing Vehicle drug
        receiving_drugs_event.Broadcast_Event = "Received_Vehicle"

    expire_recent_drugs = None
    if drug_ineligibility_duration > 0:
        expire_recent_drugs = PropertyValueChanger(
            Target_Property_Key="DrugStatus",
            Target_Property_Value="RecentDrug",
            Revert=drug_ineligibility_duration)

    # set up drug campaign
    if campaign_type == 'MDA' or campaign_type == 'SMC':
        if treatment_delay:
            raise ValueError('"treatment_delay" parameter is not used in MDA or SMC')
        add_MDA(cb, start_days=start_days, coverage=coverage, drug_configs=drug_configs,
                receiving_drugs_event=receiving_drugs_event, repetitions=repetitions,
                tsteps_btwn_repetitions=tsteps_btwn_repetitions, nodeIDs=nodeIDs,
                expire_recent_drugs=expire_recent_drugs, node_property_restrictions=node_property_restrictions,
                ind_property_restrictions=ind_property_restrictions, disqualifying_properties=disqualifying_properties,
                target_group=target_group, trigger_condition_list=trigger_condition_list,
                listening_duration=listening_duration, triggered_campaign_delay=triggered_campaign_delay,
                target_residents_only=target_residents_only, check_eligibility_at_trigger=check_eligibility_at_trigger)

    elif campaign_type == 'MSAT' or campaign_type == 'MTAT':
        add_MSAT(cb, start_days=start_days, coverage=coverage, drug_configs=drug_configs,
                 receiving_drugs_event=receiving_drugs_event, repetitions=repetitions,
                 tsteps_btwn_repetitions=tsteps_btwn_repetitions, treatment_delay=treatment_delay,
                 diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                 diagnostic_specificity=diagnostic_specificity, diagnostic_sensitivity=diagnostic_sensitivity,
                 measurement_sensitivity=measurement_sensitivity,
                 nodeIDs=nodeIDs,
                 expire_recent_drugs=expire_recent_drugs, node_property_restrictions=node_property_restrictions,
                 ind_property_restrictions=ind_property_restrictions, disqualifying_properties=disqualifying_properties,
                 target_group=target_group, trigger_condition_list=trigger_condition_list,
                 triggered_campaign_delay=triggered_campaign_delay, listening_duration=listening_duration,
                 check_eligibility_at_trigger=check_eligibility_at_trigger)

    elif campaign_type == 'fMDA':
        add_fMDA(cb, start_days=start_days, trigger_coverage=trigger_coverage, coverage=coverage,
                 drug_configs=drug_configs, receiving_drugs_event=receiving_drugs_event, repetitions=repetitions,
                 tsteps_btwn_repetitions=tsteps_btwn_repetitions, treatment_delay=treatment_delay,
                 diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                 diagnostic_sensitivity=diagnostic_sensitivity, diagnostic_specificity=diagnostic_specificity,
                 measurement_sensitivity=measurement_sensitivity,
                 fmda_radius=fmda_radius,
                 node_selection_type=node_selection_type, nodeIDs=nodeIDs, expire_recent_drugs=expire_recent_drugs,
                 node_property_restrictions=node_property_restrictions,
                 ind_property_restrictions=ind_property_restrictions,
                 disqualifying_properties=disqualifying_properties, target_group=target_group,
                 trigger_condition_list=trigger_condition_list, listening_duration=listening_duration,
                 triggered_campaign_delay=triggered_campaign_delay,
                 check_eligibility_at_trigger=check_eligibility_at_trigger)

    # not a triggerable campaign
    elif campaign_type == 'rfMSAT':
        add_rfMSAT(cb, start_day=start_days[0], coverage=coverage, drug_configs=drug_configs,
                   receiving_drugs_event=receiving_drugs_event, listening_duration=listening_duration,
                   treatment_delay=treatment_delay, trigger_coverage=trigger_coverage, diagnostic_type=diagnostic_type,
                   diagnostic_threshold=diagnostic_threshold,
                   diagnostic_sensitivity=diagnostic_sensitivity, diagnostic_specificity=diagnostic_specificity,
                   measurement_sensitivity=measurement_sensitivity,
                   fmda_radius=fmda_radius,
                   node_selection_type=node_selection_type, snowballs=snowballs, nodeIDs=nodeIDs,
                   expire_recent_drugs=expire_recent_drugs, node_property_restrictions=node_property_restrictions,
                   ind_property_restrictions=ind_property_restrictions,
                   disqualifying_properties=disqualifying_properties)

    # not a triggerable campaign
    elif campaign_type == 'rfMDA':
        add_rfMDA(cb, start_day=start_days[0], coverage=coverage, drug_configs=drug_configs,
                  receiving_drugs_event=receiving_drugs_event, listening_duration=listening_duration,
                  treatment_delay=treatment_delay, trigger_coverage=trigger_coverage, fmda_radius=fmda_radius,
                  node_selection_type=node_selection_type, nodeIDs=nodeIDs, expire_recent_drugs=expire_recent_drugs,
                  node_property_restrictions=node_property_restrictions,
                  ind_property_restrictions=ind_property_restrictions,
                  disqualifying_properties=disqualifying_properties)

    else:
        raise Exception('Warning: unrecognized campaign type\n')
        pass

    return {'drug_campaign.type': campaign_type,
            'drug_campaign.drugs': drug_code,
            'drug_campaign.trigger_coverage': trigger_coverage,
            'drug_campaign.coverage': coverage
            }


def add_MDA(cb, start_days: list = None, coverage: float = 1.0, drug_configs: list = None,
            receiving_drugs_event: BroadcastEvent = None, repetitions: int = 1, tsteps_btwn_repetitions: int = 60,
            nodeIDs: list = None, expire_recent_drugs: PropertyValueChanger = None,
            node_property_restrictions: list = None,
            ind_property_restrictions: list = None, disqualifying_properties: list = None,
            target_group: any = 'Everyone',
            trigger_condition_list: list = None, listening_duration: int = -1, triggered_campaign_delay: int = 0,
            target_residents_only: int = 1, check_eligibility_at_trigger: bool = False):
    """
        Add MDA (mass drug administration) drug intervention to campaign. If
        there are multiple start days in a list and trigger_condition_list
        is empty, then mda's are created to run on the days in the start_days
        list. If the triggerer_condition_list is present, then a triggered
        mda is created and uses the first day of the start_days. If there are
        repetitions or a triggered_campaign_delay then separate
        nodeleveltriggered interventions are created with a delay that sends
        out an event that triggers the mda. Multiple start days are only
        valid for non-triggered mdas.

    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
        object for building, modifying, and writing campaign configuration files.
        start_days: List of integers.
        coverage: Demographic coverage of mda's.
        drug_configs: List of dictionaries of drug configurations to be
            given out, created in add_drug_campaign.
        receiving_drugs_event: (Optional) Broadcast event container with event
            to be broadcast when drugs received.
        repetitions: Number of repetitions for mda. For triggered mda, this is
            for a repeated mda after a trigger.
        tsteps_btwn_repetitions: Timesteps between repeated scheduled mdas or
            between once-triggered repeated mdas.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        expire_recent_drugs: PropertyValueChanger intervention that updates
            DrugStatus:Recent drug to individual properties.
        node_property_restrictions: List of NodeProperty key:value pairs that nodes
            must have to receive the diagnostic intervention. For example,
            ``[{"NodeProperty1":"PropertyValue1"},
            {"NodeProperty2":"PropertyValue2"}]``. Default is no restrictions.
        disqualifying_properties: List of IndividualProperty key:value pairs that
            cause an intervention to be aborted. For example,
            ``[{"IndividualProperty1":"PropertyValue1"},
            {"IndividualProperty2":"PropertyValue2"}]``.
        target_group: A dictionary targeting an age range and gender of
            individuals for treatment. In the format
            ``{"agemin": x, "agemax": y, "gender": z}``. Default is Everyone.
        trigger_condition_list: List of event triggers upon which mda(s) are
            distributed.
        listening_duration: Duration to listen for the trigger. Default is -1,
            which listens indefinitely.
        triggered_campaign_delay: Delay period between the trigger and the mda.
            Default is 0.
        target_residents_only: When set to true (1), the intervention is only
            distributed to individuals for whom the node is their home node.
            They are not visitors from another node.
        check_eligibility_at_trigger: If triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay.

    Returns:
        None
    """

    if start_days is None:
        start_days = [0]
    if drug_configs is None:
        raise Exception("You have to pass in drug_configs (list of drug configurations).\n")
    if node_property_restrictions is None:
        node_property_restrictions = []
    if ind_property_restrictions is None:
        ind_property_restrictions = []
    if disqualifying_properties is None:
        disqualifying_properties = []
    if nodeIDs:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    else:
        nodeset_config = NodeSetAll()
    interventions = drug_configs + [receiving_drugs_event]

    if expire_recent_drugs:
        interventions = interventions + [expire_recent_drugs]

    gender = "All"
    age_min = 0
    age_max = 9.3228e+35
    if target_group != "Everyone" and isinstance(target_group, dict):
        try:
            age_min = target_group["agemin"]
            age_max = target_group["agemax"]
            if 'gender' in target_group:
                gender = target_group["gender"]
                target_group = "ExplicitAgeRangesAndGender"
            else:
                target_group = "ExplicitAgeRanges"
        except KeyError:
            raise KeyError("Unknown target_group parameter. Please pass in 'Everyone' or a dictionary of "
                           "{'agemin' : x, 'agemax' : y, 'gender': 'Female'} to target  to individuals between x and "
                           "y years of age, and (optional) gender.\n")

    if trigger_condition_list:
        # if once triggered, you want the diagnostic survey to repeat or if there is a delay (or both)
        # this creates a series of broadcast events that once triggered send out broadcast_event
        # at pre-determined intervals
        if repetitions > 1 or triggered_campaign_delay > 0:
            # create a trigger for each of the delays.
            broadcast_event = "MDA_Now_{}".format(random.randint(1, 10000))
            trigger_node_property_restrictions = []
            trigger_ind_property_restrictions = []
            if check_eligibility_at_trigger:
                trigger_node_property_restrictions = node_property_restrictions
                trigger_ind_property_restrictions = ind_property_restrictions
                node_property_restrictions = []
                ind_property_restrictions = []
            for x in range(repetitions):
                triggered_campaign_delay_event(cb, start_days[0], nodeIDs=nodeIDs,
                                               triggered_campaign_delay=triggered_campaign_delay + (
                                                           x * tsteps_btwn_repetitions),
                                               trigger_condition_list=trigger_condition_list,
                                               listening_duration=listening_duration, event_to_send_out=broadcast_event,
                                               node_property_restrictions=trigger_node_property_restrictions,
                                               ind_property_restrictions=trigger_ind_property_restrictions)
            trigger_condition_list = [broadcast_event]

        drug_event = CampaignEvent(
            Start_Day=start_days[0] - 1,
            Nodeset_Config=nodeset_config,
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Intervention_Config=NodeLevelHealthTriggeredIV(
                    Target_Demographic=target_group,
                    Target_Age_Min=age_min,
                    Target_Age_Max=age_max,
                    Target_Gender=gender,
                    Node_Property_Restrictions=node_property_restrictions,
                    Property_Restrictions_Within_Node=ind_property_restrictions,
                    Disqualifying_Properties=disqualifying_properties,
                    Trigger_Condition_List=trigger_condition_list,
                    Duration=listening_duration,
                    Target_Residents_Only=target_residents_only,
                    Actual_IndividualIntervention_Config=MultiInterventionDistributor(
                        Intervention_List=interventions))))

        cb.add_event(drug_event)

    else:
        for start_day in start_days:
            drug_event = CampaignEvent(
                Start_Day=start_day,
                Nodeset_Config=nodeset_config,
                Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                    Target_Demographic=target_group,
                    Target_Age_Min=age_min,
                    Target_Age_Max=age_max,
                    Node_Property_Restrictions=node_property_restrictions,
                    Property_Restrictions_Within_Node=ind_property_restrictions,
                    Demographic_Coverage=coverage,
                    Intervention_Config=MultiInterventionDistributor(
                        Intervention_List=interventions),
                    Number_Repetitions=repetitions,
                    Timesteps_Between_Repetitions=tsteps_btwn_repetitions))

            cb.add_event(drug_event)


def add_MSAT(cb, start_days: list = None, coverage: float = 1.0, drug_configs: list = None,
             receiving_drugs_event: BroadcastEvent = None, repetitions: int = 1, tsteps_btwn_repetitions: int = 60,
             treatment_delay: int = 0, diagnostic_type: str = 'BLOOD_SMEAR_PARASITES',
             diagnostic_threshold: float = 40, diagnostic_sensitivity: float = 1,
             diagnostic_specificity: float = 1, measurement_sensitivity: float = 0.1, nodeIDs: list = None,
             expire_recent_drugs: PropertyValueChanger = None,
             node_property_restrictions: list = None, ind_property_restrictions: list = None,
             disqualifying_properties: list = None, target_group: any = 'Everyone', trigger_condition_list: list = None,
             triggered_campaign_delay: int = 0, listening_duration: int = -1,
             check_eligibility_at_trigger: bool = False):
    """
    Add a MSAT (mass screening and treatment) drug intervention to
    campaign. This is either scheduled (on days from start_days) or
    triggered (when trigger_condition_list is present).

    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            object for building, modifying, and writing campaign configuration files.
        start_days: List of days on which to start the intervention.
        coverage: Demographic coverage of the intervention.
        drug_configs: List of dictionaries of drug configurations to be
            distributed, created in add_drug_campaign.
        receiving_drugs_event: (Optional) Broadcast event container with event
            to be broadcast when drugs received.
        repetitions: How many times the intervention will be repeated.
        tsteps_btwn_repetitions: Time steps between repetitions.
        treatment_delay: Delay before the triggered drug distribution is done.
        diagnostic_type: Diagnostic type. Available options are:
            * TRUE_INFECTION_STATUS
            * BLOOD_SMEAR
            * PCR
            * PF_HRP2
            * TRUE_PARASITE_DENSITY
            * HAS_FEVER
        diagnostic_threshold: Diagnostic threshold values, which are based
            on the selected diagnostic type.
        diagnostic_sensitivity: Setting for **Base_Sensitivity** in the MalariaDiagnostic
        diagnostic_specificity: Setting for **Base_Specificity** in the MalariaDiagnostic
        measurement_sensitivity: setting for **Measurement_Sensitivity** in MalariaDiagnostic
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        expire_recent_drugs:  PropertyValueChanger intervention that updates
            DrugStatus to Recent drug in IndividualProperties.
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
        target_group: A dictionary of ``{'agemin': x, 'agemax': y}`` to
            target MDA, SMC, MSAT, fMDA to individuals between x and y years
            of age. Default is Everyone.
        trigger_condition_list: List of events to trigger MSAT. When trigger_string
            is set, the first entry of start_days is the day that is used to start
            listening for the trigger(s), the campaign happens when the trigger(s)
            is received.
        triggered_campaign_delay: How long to delay the actual intervention
            (drug giving) for after the trigger is received.
        listening_duration: Duration to listen for the trigger. Default is -1,
            which listens indefinitely.
        check_eligibility_at_trigger: If triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay. Default is
            false, checks at distribution.

    Returns:
        None
    """

    if not start_days:
        start_days = [0]
    if not drug_configs:
        raise Exception("You have to pass in drug_configs (list of drug configurations).\n")
    if node_property_restrictions is None:
        node_property_restrictions = []
    if ind_property_restrictions is None:
        ind_property_restrictions = []
    if disqualifying_properties is None:
        disqualifying_properties = []

    event_config = drug_configs + [receiving_drugs_event]
    if expire_recent_drugs:
        event_config.append(expire_recent_drugs)

    if treatment_delay == 0:
        msat_cfg = event_config
    else:
        msat_cfg = [DelayedIntervention(
            Delay_Period_Distribution="CONSTANT_DISTRIBUTION",
            Delay_Period_Constant=treatment_delay,
            Actual_IndividualIntervention_Configs=event_config)]

    # MSAT controlled by MalariaDiagnostic campaign event rather than New_Diagnostic_Sensitivity
    if trigger_condition_list:
        add_diagnostic_survey(cb, coverage=coverage, repetitions=repetitions,
                              tsteps_btwn_repetitions=tsteps_btwn_repetitions,
                              target=target_group, start_day=start_days[0],
                              diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                              sensitivity=diagnostic_sensitivity,
                              specificity=diagnostic_specificity,
                              measurement_sensitivity=measurement_sensitivity,
                              nodeIDs=nodeIDs, positive_diagnosis_configs=msat_cfg,
                              IP_restrictions=ind_property_restrictions, NP_restrictions=node_property_restrictions,
                              disqualifying_properties=disqualifying_properties,
                              trigger_condition_list=trigger_condition_list,
                              listening_duration=listening_duration, triggered_campaign_delay=triggered_campaign_delay,
                              check_eligibility_at_trigger=check_eligibility_at_trigger,
                              expire_recent_drugs=expire_recent_drugs)
    else:
        for start_day in start_days:
            add_diagnostic_survey(cb, coverage=coverage, repetitions=repetitions,
                                  tsteps_btwn_repetitions=tsteps_btwn_repetitions,
                                  target=target_group, start_day=start_day,
                                  diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                                  sensitivity=diagnostic_sensitivity,
                                  specificity=diagnostic_specificity,
                                  measurement_sensitivity=measurement_sensitivity,
                                  nodeIDs=nodeIDs, positive_diagnosis_configs=msat_cfg,
                                  listening_duration=listening_duration,
                                  IP_restrictions=ind_property_restrictions, NP_restrictions=node_property_restrictions,
                                  disqualifying_properties=disqualifying_properties,
                                  expire_recent_drugs=expire_recent_drugs)


def add_fMDA(cb, start_days: list = None, trigger_coverage: float = 1, coverage: float = 1, drug_configs: list = None,
             receiving_drugs_event: BroadcastEvent = None, repetitions: int = 1, tsteps_btwn_repetitions: int = 365,
             treatment_delay: int = 0, diagnostic_type: str = 'BLOOD_SMEAR_PARASITES', diagnostic_threshold: float = 40,
             diagnostic_sensitivity: float = 1, diagnostic_specificity: float = 1, measurement_sensitivity: float = 0.1,
             fmda_radius: int = 0, node_selection_type: str = 'DISTANCE_ONLY', nodeIDs: list = None,
             expire_recent_drugs: PropertyValueChanger = None, node_property_restrictions: list = None,
             ind_property_restrictions: list = None,
             disqualifying_properties: list = None, target_group: any = 'Everyone', trigger_condition_list: list = None,
             listening_duration: int = -1, triggered_campaign_delay: int = 0,
             check_eligibility_at_trigger: bool = False):
    """
    Add a fMDA (focal mass drug administration) drug intervention to
    campaign. The fMDA is based on results from diagnostic survey,
    which is either scheduled (on days from start_days) or
    triggered (when trigger_condition_list is present).

    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            object for building, modifying, and writing campaign configuration files.
        start_days: List of days on which to start the intervention.
        trigger_coverage: Demographic coverage of the triggered intervention.
        coverage: Demographic coverage of the intervention.
        drug_configs: List of dictionaries of drug configurations to be
            distributed, created in add_drug_campaign.
        receiving_drugs_event: (Optional) Broadcast event container with event
            to be broadcast when drugs received.
        repetitions: How many times the intervention will be repeated.
        tsteps_btwn_repetitions: Time steps between repetitions.
        treatment_delay: Delay before the triggered drug distribution is done.
        diagnostic_type: Diagnostic type. Available options are:
            * TRUE_INFECTION_STATUS
            * BLOOD_SMEAR
            * PCR
            * PF_HRP2
            * TRUE_PARASITE_DENSITY
            * HAS_FEVER
        diagnostic_threshold: Diagnostic threshold values, which are based
            on the selected diagnostic type.
        diagnostic_sensitivity: Setting for **Base_Sensitivity** in the MalariaDiagnostic
        diagnostic_specificity: Setting for **Base_Specificity** in the MalariaDiagnostic
        measurement_sensitivity: setting for **Measurement_Sensitivity** in MalariaDiagnostic
        fmda_radius: Radius of the follow up BroadcastToOtherNodes interventions,
            uses node_selection_type.
        node_selection_type: Node selection type for broadcasting fMDA trigger.
            Available options are:
            * DISTANCE_ONLY: Nodes located within the distance specified by fmda_type
            are selected.
            * MIGRATION_NODES_ONLY: Nodes that are local or regional are selected.
            * DISTANCE_AND_MIGRATION: Nodes are selected using DISTANCE_ONLY and
            MIGRATION_NODES_ONLY criteria.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        expire_recent_drugs: PropertyValueChanger intervention that updates DrugStatus
            to Recent drug in IndividualProperties.
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
        target_group: A dictionary of ``{'agemin': x, 'agemax': y}`` to
            target MDA, SMC, MSAT, fMDA to individuals between x and y years
            of age. Default is Everyone.
        trigger_condition_list: List of events to trigger fMDA. When trigger_string
            is set, the first entry of start_days is the day that is used to start
            listening for the trigger(s), the campaign happens when the trigger(s)
            is received.
        listening_duration: Duration to listen for the trigger. Default is -1,
            which listens indefinitely.
        triggered_campaign_delay: How long to delay the actual intervention
            (drug giving) after the trigger is received.
        check_eligibility_at_trigger: If triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay. Default is
            false, checks at distribution.

    Returns:
        None
    """

    if not start_days:
        start_days = [0]
    if not drug_configs:
        raise Exception("You have to pass in drug_configs (list of drug configurations).\n")
    if node_property_restrictions is None:
        node_property_restrictions = []
    if ind_property_restrictions is None:
        ind_property_restrictions = []
    if disqualifying_properties is None:
        disqualifying_properties = []
    if nodeIDs:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    else:
        nodeset_config = NodeSetAll()

    # rewritten to give out a unique trigger for the fmda
    fmda_trigger_tether = "Give_Drugs_fMDA_{}".format(random.randint(1, 10000))
    fmda_trigger_event = BroadcastEvent(Broadcast_Event="Give_Drugs_fMDA")
    fmda_setup = [fmda_cfg(fmda_radius, node_selection_type, event_trigger=fmda_trigger_tether), fmda_trigger_event]

    interventions = drug_configs + [receiving_drugs_event]

    if expire_recent_drugs:
        interventions = interventions + [expire_recent_drugs]

    if treatment_delay > 0:
        fmda_setup = [DelayedIntervention(
            Delay_Period_Distribution="CONSTANT_DISTRIBUTION",
            Delay_Period_Constant=treatment_delay,
            Actual_IndividualIntervention_Configs=fmda_setup)]

    if trigger_condition_list:
        add_diagnostic_survey(cb, coverage=trigger_coverage, repetitions=repetitions,
                              tsteps_btwn_repetitions=tsteps_btwn_repetitions,
                              target=target_group, start_day=start_days[0],
                              diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                              sensitivity=diagnostic_sensitivity,
                              specificity=diagnostic_specificity,
                              measurement_sensitivity=measurement_sensitivity,
                              nodeIDs=nodeIDs, positive_diagnosis_configs=fmda_setup,
                              IP_restrictions=ind_property_restrictions, NP_restrictions=node_property_restrictions,
                              trigger_condition_list=trigger_condition_list,
                              listening_duration=listening_duration, triggered_campaign_delay=triggered_campaign_delay,
                              check_eligibility_at_trigger=check_eligibility_at_trigger,
                              expire_recent_drugs=expire_recent_drugs)

        fmda_distribute_drugs = CampaignEvent(
            Event_Name="Distribute fMDA",
            Start_Day=start_days[0] - 1,
            Nodeset_Config=nodeset_config,
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Intervention_Config=NodeLevelHealthTriggeredIV(
                    Demographic_Coverage=coverage,
                    Blackout_Event_Trigger="fMDA_Blackout_Event_Trigger",
                    Blackout_Period=1,
                    Blackout_On_First_Occurrence=1,
                    Target_Residents_Only=1,
                    Node_Property_Restrictions=node_property_restrictions,
                    Property_Restrictions_Within_Node=ind_property_restrictions,
                    Disqualifying_Properties=disqualifying_properties,
                    Duration=listening_duration,
                    Trigger_Condition_List=[fmda_trigger_tether],
                    Actual_IndividualIntervention_Config=MultiInterventionDistributor(
                        Intervention_List=interventions))))

        cb.add_event(fmda_distribute_drugs)

    else:
        for start_day in start_days:
            # separate event for each repetition, otherwise RCD and fMDA can get entangled.
            for rep in range(repetitions):
                add_diagnostic_survey(cb, coverage=trigger_coverage, repetitions=1,
                                      tsteps_btwn_repetitions=tsteps_btwn_repetitions,
                                      target=target_group, start_day=start_day + tsteps_btwn_repetitions * rep,
                                      diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                                      sensitivity=diagnostic_sensitivity,
                                      specificity=diagnostic_specificity,
                                      measurement_sensitivity=measurement_sensitivity,
                                      nodeIDs=nodeIDs, positive_diagnosis_configs=fmda_setup,
                                      IP_restrictions=ind_property_restrictions,
                                      NP_restrictions=node_property_restrictions,
                                      disqualifying_properties=disqualifying_properties,
                                      expire_recent_drugs=expire_recent_drugs)

        fmda_distribute_drugs = CampaignEvent(
            Start_Day=start_days[0] - 1,
            Nodeset_Config=nodeset_config,
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Intervention_Config=NodeLevelHealthTriggeredIV(
                    Demographic_Coverage=coverage,
                    Blackout_Event_Trigger="fMDA_Blackout_Event_Trigger",
                    Blackout_Period=1,
                    Blackout_On_First_Occurrence=1,
                    Target_Residents_Only=1,
                    Node_Property_Restrictions=node_property_restrictions,
                    Property_Restrictions_Within_Node=ind_property_restrictions,
                    Disqualifying_Properties=disqualifying_properties,
                    Trigger_Condition_List=[fmda_trigger_tether],
                    Actual_IndividualIntervention_Config=MultiInterventionDistributor(
                        Intervention_List=interventions))))

        cb.add_event(fmda_distribute_drugs)


def add_rfMSAT(cb, start_day: int = 0, coverage: float = 1, drug_configs: list = None,
               receiving_drugs_event: BroadcastEvent = None, listening_duration: int = -1, treatment_delay: int = 0,
               trigger_coverage: float = 1, diagnostic_type: str = 'BLOOD_SMEAR_PARASITES',
               diagnostic_threshold: float = 40, diagnostic_sensitivity: float = 1,
               diagnostic_specificity: float = 1, measurement_sensitivity: float = 0.1,
               fmda_radius: int = 0, node_selection_type: str = 'DISTANCE_ONLY', snowballs: int = 0,
               nodeIDs: list = None,
               expire_recent_drugs: PropertyValueChanger = None, node_property_restrictions: list = None,
               ind_property_restrictions: list = None, disqualifying_properties: list = None):
    """
    Add a rfMDA (reactive focal mass drug administration) drug intervention to
    campaign. Detecting malaria triggers diagnostic surveys to run on
    neighboring nodes and so on, up to the number of trigggered interventions
    defined in **snowballs** parameter.

    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            object for building, modifying, and writing campaign configuration files.
        start_day: List of days on which to start the intervention.
        coverage: Demographic coverage of the intervention.
        drug_configs: List of dictionaries of drug configurations to be
            distributed, created in add_drug_campaign.
        receiving_drugs_event: (Optional) Broadcast event container with event
            to be broadcast when drugs received.
        listening_duration: Duration of the existence of the intervention.
        treatment_delay: delay before the triggered drug distribution is done
        trigger_coverage: Demographic coverage for the triggered intervention
        diagnostic_type: Diagnostic type. Available options are:
            * TRUE_INFECTION_STATUS
            * BLOOD_SMEAR
            * PCR
            * PF_HRP2
            * TRUE_PARASITE_DENSITY
            * HAS_FEVER
        diagnostic_threshold: Diagnostic threshold values, which are based
            on the selected diagnostic type.
        diagnostic_sensitivity: Setting for **Base_Sensitivity** in the MalariaDiagnostic
        diagnostic_specificity: Setting for **Base_Specificity** in the MalariaDiagnostic
        measurement_sensitivity: setting for **Measurement_Sensitivity** in MalariaDiagnostic
        fmda_radius: Radius of the follow up BroadcastToOtherNodes interventions,
            uses node_selection_type.
        node_selection_type: Node selection type for broadcasting fMDA trigger.
            Available options are:
            * DISTANCE_ONLY: Nodes located within the distance specified by fmda_type
            are selected.
            * MIGRATION_NODES_ONLY: Nodes that are local or regional are selected.
            * DISTANCE_AND_MIGRATION: Nodes are selected using DISTANCE_ONLY and
            MIGRATION_NODES_ONLY criteria.
        snowballs: Number of triggered interventions after the first.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        expire_recent_drugs: PropertyValueChanger intervention that updates DrugStatus
            to Recent drug in IndividualProperties.
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

    Returns:
        None
    """

    if not drug_configs:
        raise Exception("You have to pass in drug_configs (list of drug configurations).\n")
    if node_property_restrictions is None:
        node_property_restrictions = []
    if ind_property_restrictions is None:
        ind_property_restrictions = []
    if disqualifying_properties is None:
        disqualifying_properties = []
    if nodeIDs:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    else:
        nodeset_config = NodeSetAll()

    fmda_setup = fmda_cfg(fmda_radius, node_selection_type, event_trigger='')  # no trigger used
    snowball_setup = [deepcopy(fmda_setup) for x in range(snowballs + 1)]
    snowball_trigger = 'Diagnostic_Survey_'
    snowball_setup[0].Event_Trigger = snowball_trigger + "0"

    rcd_event = CampaignEvent(
        Event_Name="Trigger RCD MSAT",
        Start_Day=start_day,
        Nodeset_Config=nodeset_config,
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            Intervention_Config=NodeLevelHealthTriggeredIV(
                Demographic_Coverage=trigger_coverage,
                Node_Property_Restrictions=node_property_restrictions,
                Trigger_Condition_List=["Received_Treatment"],
                Duration=listening_duration,
                Actual_IndividualIntervention_Config=DelayedIntervention(
                    Delay_Period_Distribution="CONSTANT_DISTRIBUTION",
                    Delay_Period_Constant=treatment_delay,
                    Actual_IndividualIntervention_Configs=[snowball_setup[0]]))))

    cb.add_event(rcd_event)

    event_config = drug_configs + [receiving_drugs_event]
    if expire_recent_drugs:
        event_config.append(expire_recent_drugs)

    add_diagnostic_survey(cb, coverage=coverage, start_day=start_day,
                          diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                          sensitivity=diagnostic_sensitivity, specificity=diagnostic_specificity,
                          measurement_sensitivity=measurement_sensitivity,
                          nodeIDs=nodeIDs,
                          trigger_condition_list=[snowball_setup[0].Event_Trigger],
                          event_name='Reactive MSAT level 0',
                          positive_diagnosis_configs=event_config,
                          IP_restrictions=ind_property_restrictions, NP_restrictions=node_property_restrictions,
                          disqualifying_properties=disqualifying_properties, expire_recent_drugs=expire_recent_drugs)

    for snowball in range(snowballs):
        snowball_setup[snowball + 1].Event_Trigger = snowball_trigger + str(snowball + 1)
        event_config = [snowball_setup[snowball + 1], receiving_drugs_event] + drug_configs
        curr_trigger = snowball_trigger + str(snowball)
        add_diagnostic_survey(cb, coverage=coverage, start_day=start_day,
                              diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                              sensitivity=diagnostic_sensitivity,
                              specificity=diagnostic_specificity,
                              measurement_sensitivity=measurement_sensitivity,
                              nodeIDs=nodeIDs,
                              trigger_condition_list=[curr_trigger],
                              event_name='Snowball level ' + str(snowball),
                              positive_diagnosis_configs=event_config,
                              IP_restrictions=ind_property_restrictions, NP_restrictions=node_property_restrictions,
                              disqualifying_properties=disqualifying_properties,
                              expire_recent_drugs=expire_recent_drugs)


def add_rfMDA(cb, start_day: int = 0, coverage: float = 1, drug_configs: list = None,
              receiving_drugs_event: BroadcastEvent = None, listening_duration: int = -1, treatment_delay: int = 0,
              trigger_coverage: float = 1, fmda_radius: int = 0, node_selection_type: str = 'DISTANCE_ONLY',
              nodeIDs: list = None, expire_recent_drugs: PropertyValueChanger = None,
              node_property_restrictions: list = None,
              ind_property_restrictions: list = None, disqualifying_properties: list = None):
    """
    This function adds two interventions to your campaign file:
    1) "Received_Treatment"- triggered BroadcastEventToOtherNodes of
    "Give_Drugs_rfMDA" event to fmda_radius, with a "treatment_delay"
    option, and "coverage" coverage.
    2) "Give_Drugs_rfMDA" event-triggered MultiIntervention event
    distributing "drug_configs" drugs, with "trigger_coverage"
    demographic coverage, with an option to restrict to
    {"DrugStatus": "None"} IndividualProperty and optional
    receiving_drugs_event.

    Upon "Received_Treatment" event a delayed "Give_Drugs_rfMDA" is
    sent out to (optionally) neighboring nodes, which triggers giving
    of drugs, and (optionally) an individualproperty change and
    another event being sent.

    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            object for building, modifying, and writing campaign configuration
            files.
        start_day: The day the intervention is distributed. Default is 0.
        coverage: Demographic coverage of the intervention.
        drug_configs: List of dictionaries of drug configurations to be
            distributed, created in add_drug_campaign.
        receiving_drugs_event: Event to be sent out upon receiving drugs.
            Default is 1, everyone.
        listening_duration: Duration of the existence of the intervention.
            Default is ongoing.
        treatment_delay: Delay of treatment (in days) after intervention is triggered.
        trigger_coverage: Demographic coverage for intervention triggered by
            successful treatment.
        fmda_radius: Radius (km) of sending event to other nodes.
        node_selection_type: Node selection type. Available options are:
            * DISTANCE_ONLY: Nodes located within the distance specified by fmda_type
            are selected.
            * MIGRATION_NODES_ONLY: Nodes that are local or regional are selected.
            * DISTANCE_AND_MIGRATION: Nodes are selected using DISTANCE_ONLY and
            MIGRATION_NODES_ONLY criteria.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        expire_recent_drugs: PropertyValueChanger intervention that updates DrugStatus
            to Recent drug in IndividualProperties.
        node_property_restrictions: List of NodeProperty key:value pairs that nodes
            must have to receive the diagnostic intervention. For example,
            ``[{"NodeProperty1":"PropertyValue1"},
            {"NodeProperty2":"PropertyValue2"}]``. Default is no restrictions.
        ind_property_restrictions: List of IndividualProperty key:value pairs that
            individuals must have to receive the diagnostic intervention.
            For example, ``[{"IndividualProperty1":"PropertyValue1"},
            {"IndividualProperty2":"PropertyValue2"}]``. Default is no restrictions.
        disqualifying_properties: ist of IndividualProperty key:value pairs that
            cause an intervention to be aborted. For example,
            ``[{"IndividualProperty1":"PropertyValue1"},
            {"IndividualProperty2":"PropertyValue2"}]``.

    Returns:
        None
    """

    if not drug_configs:
        raise Exception("You must have drug_configs defined. Hint: It's a list of drug configurations.\n")
    interventions = drug_configs
    if receiving_drugs_event:
        interventions = drug_configs + [receiving_drugs_event]
    if nodeIDs:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    else:
        nodeset_config = NodeSetAll()

    if node_property_restrictions is None:
        node_property_restrictions = []
    if ind_property_restrictions is None:
        ind_property_restrictions = []
    if disqualifying_properties is None:
        disqualifying_properties = []

    rfmda_trigger = "Give_Drugs_rfMDA"
    fmda_setup = fmda_cfg(fmda_radius, node_selection_type, event_trigger=rfmda_trigger)

    rcd_event = CampaignEvent(
        Event_Name="Trigger RCD MDA",
        Start_Day=start_day,
        Nodeset_Config=nodeset_config,
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            Intervention_Config=NodeLevelHealthTriggeredIV(
                Demographic_Coverage=trigger_coverage,
                Node_Property_Restrictions=node_property_restrictions,
                Property_Restrictions_Within_Node=ind_property_restrictions,
                Trigger_Condition_List=["Received_Treatment"],
                Duration=listening_duration,
                Actual_IndividualIntervention_Config=DelayedIntervention(
                    Delay_Period_Distribution="CONSTANT_DISTRIBUTION",
                    Delay_Period_Constant=treatment_delay,
                    Actual_IndividualIntervention_Configs=[fmda_setup]))))

    if expire_recent_drugs:
        interventions = interventions + [expire_recent_drugs]

    # distributes drugs to individuals broadcasting "Give_Drugs_rfMDA"
    # who is broadcasting is determined by other events
    # if campaign drugs change (less effective, different cocktail), then this event should have an expiration date.
    fmda_distribute_drugs = CampaignEvent(
        Event_Name="Distribute fMDA",
        Start_Day=start_day,
        Nodeset_Config=nodeset_config,
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            Intervention_Config=NodeLevelHealthTriggeredIV(
                Demographic_Coverage=coverage,
                Node_Property_Restrictions=node_property_restrictions,
                Property_Restrictions_Within_Node=ind_property_restrictions,
                Disqualifying_Properties=disqualifying_properties,
                Duration=listening_duration,
                Trigger_Condition_List=[rfmda_trigger],
                Actual_IndividualIntervention_Config=MultiInterventionDistributor(
                    Intervention_List=interventions))))

    cb.add_event(rcd_event)
    cb.add_event(fmda_distribute_drugs)


def fmda_cfg(fmda_type: any = 0, node_selection_type: str = 'DISTANCE_ONLY', event_trigger: str = 'Give_Drugs'):
    """
    By Default, this is within the node-only (Distance_Only with distance=0).

    Args:
        fmda_type: Radius in km of the follow up BroadcastToOtherNodes interventions, 
            uses node_selection_type.
        node_selection_type: Node selection type for broadcasting to other nodes. 
            Available options are:
            * DISTANCE_ONLY: Nodes located within the distance specified by fmda_type 
            are selected.
            * MIGRATION_NODES_ONLY: Nodes that are local or regional are selected.
            * DISTANCE_AND_MIGRATION: Nodes are selected using DISTANCE_ONLY and 
            MIGRATION_NODES_ONLY criteria.
        event_trigger: String that triggers the broadcast.

    Returns:
        Configured BroadcastEventToOtherNodes
    """
    if isinstance(fmda_type, str):
        fmda_type = 0

    return BroadcastEventToOtherNodes(
        Event_Trigger=event_trigger,
        Include_My_Node=1,
        Node_Selection_Type=node_selection_type,
        Max_Distance_To_Other_Nodes_Km=fmda_type)
