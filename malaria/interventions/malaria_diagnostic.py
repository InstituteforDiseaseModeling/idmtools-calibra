from dtk.interventions.triggered_campaign_delay_event import triggered_campaign_delay_event
from dtk.utils.Campaign.CampaignClass import *
import random


def add_diagnostic_survey(cb, coverage: float = 1,
                          repetitions: int = 1, tsteps_btwn_repetitions: int = 365, target: object = 'Everyone',
                          start_day: int = 1, diagnostic_type: str = 'BLOOD_SMEAR_PARASITES',
                          diagnostic_threshold: float = 40, measurement_sensitivity: float = 0.1,
                          sensitivity: float = 1,
                          specificity: float = 1, event_name: str = "Diagnostic Survey",
                          nodeIDs: list = None, positive_diagnosis_configs: list = None,
                          negative_diagnosis_configs: list = None, received_test_event: str = 'Received_Test',
                          IP_restrictions: list = None, NP_restrictions: list = None,
                          disqualifying_properties: list = None,
                          trigger_condition_list: list = None, listening_duration: int = -1,
                          triggered_campaign_delay: int = 0, check_eligibility_at_trigger: bool = False,
                          expire_recent_drugs: any = None):

    """
    Add an intervention to create either a scheduled or a triggered event to
    the campaign using the **MalariaDiagnostic** class, an individual-level
    class, to test individuals. Upon positive or negative diagnosis, the
    list of events to occur (as defined in positive_diagnosis_configs or
    negative_diagnosis_configs) is then executed. These events can trigger
    other listening interventions.

    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            object for building, modifying, and writing campaign configuration
            files.
        coverage: The probability an individual receives the diagnostic.
        repetitions: Number of repetitions of the survey intervention.
        tsteps_btwn_repetitions: Timesteps between repetitions.
        target: A dictionary targeting an age range and gender of
            individuals for treatment. In the format
            ``{"agemin": x, "agemax": y, "gender": z}``. Default is Everyone.
        start_day: Beginning of the intervention's existence. If triggered,
            runs on trigger, not on start_day.
        diagnostic_type: Type of malaria diagnostic used. Default is
            **BLOOD_SMEAR**. Available options are:
            * TRUE_INFECTION_STATUS
            * BLOOD_SMEAR
            * PCR
            * PF_HRP2
            * TRUE_PARASITE_DENSITY
            * HAS_FEVER
        diagnostic_threshold: The diagnostic detection threshold based on
            **diagnostic_type**:
            * BLOOD_SMEAR: Use the SusceptibilityMalaria::CheckParasiteCountWithTest()
                to get a parasite density to check against the threshold.
            * PCR: Use the ReportUtilitiesMalaria::NASBADensityWithUncertainty()
                method to calculate a measured parasite density and check
                against the threshold.
            * PF_HRP2: Add a new method to get the PfHRP2 value and check against
                the threshold.
            * TRUE_PARASITE_DENSITY: Check the true/actual parasite density
                against the threshold (DEFAULT).
            * HAS_FEVER: Check the person's fever against the threshold.
        sensitivity: Setting for **Base_Sensitivity** in the MalariaDiagnostic
        specificity: Setting for **Base_Specificity** in the MalariaDiagnostic
        measurement_sensitivity: setting for **Measurement_Sensitivity** in MalariaDiagnostic
        event_name: Description of the event.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        positive_diagnosis_configs: List of events to happen to an individual
            who receives a positive result from test.
        negative_diagnosis_configs: List of events to happen to individual who
            receives a negative result from test.
        received_test_event: String for individuals to broadcast upon receiving
            diagnostic.
        IP_restrictions: List of IndividualProperty key:value pairs that
            individuals must have to receive the diagnostic intervention.
            For example, ``[{"IndividualProperty1":"PropertyValue1"},
            {"IndividualProperty2":"PropertyValue2"}]``. Default is no
            restrictions.
        NP_restrictions: List of NodeProperty key:value pairs that nodes must
            have to receive the diagnostic intervention. For example,
            ``[{"NodeProperty1":"PropertyValue1"},
            {"NodeProperty2":"PropertyValue2"}]``. Default is no
            restrictions.
        disqualifying_properties: List of IndividualProperty key:value pairs that
            cause an intervention to be aborted. For example,
            ``[{"IndividualProperty1":"PropertyValue1"},
            {"IndividualProperty2":"PropertyValue2"}]``.
        trigger_condition_list: List of events that will trigger a diagnostic survey.
        listening_duration: Duration after start day to stop listening for events, as
            specified in **trigger_condition_list**. Default is -1, non-stop
            listening.
        triggered_campaign_delay: Delay of running the intervention after receiving
            a trigger from the **trigger_condition_list**.
        check_eligibility_at_trigger: If triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay.
        expire_recent_drugs: Adds ``[{"DrugStatus:None"}]`` to
            **Property_Restrictions_Within_Node** for positive test config, so
            only those with that property receive drugs.

    Returns:
       None

    """
    if positive_diagnosis_configs is None:
        positive_diagnosis_configs = []
    if negative_diagnosis_configs is None:
        negative_diagnosis_configs = []
    if IP_restrictions is None:
        IP_restrictions = []
    if NP_restrictions is None:
        NP_restrictions = []
    if disqualifying_properties is None:
        disqualifying_properties = []
    if nodeIDs:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)
    else:
        nodeset_config = NodeSetAll()

    received_test_event = BroadcastEvent(Broadcast_Event=received_test_event)

    tested_positive = BroadcastEvent(Broadcast_Event="TestedPositive")
    tested_negative = BroadcastEvent(Broadcast_Event="TestedNegative")
    tested_positive_tether = "TestedPositive_{}".format(random.randint(1, 100000))
    tested_negative_tether = "TestedNegative_{}".format(random.randint(1, 100000))

    if diagnostic_type == "TRUE_INFECTION_STATUS":
        intervention_cfg = StandardDiagnostic(
            Base_Sensitivity=1,
            Base_Specificity=1,
            Days_To_Diagnosis=0,
            Treatment_Fraction=1,
            Event_Or_Config="Config")

    else:
        intervention_cfg = MalariaDiagnostic(
            Event_Or_Config="Config",
            Base_Sensitivity=sensitivity,
            Base_Specificity=specificity,
            Measurement_Sensitivity=measurement_sensitivity,
            Detection_Threshold=diagnostic_threshold,
            Diagnostic_Type=diagnostic_type)

    intervention_cfg.Positive_Diagnosis_Config = MultiInterventionDistributor(
        Intervention_List=[tested_positive, BroadcastEvent(Broadcast_Event=tested_positive_tether)])
    intervention_cfg.Negative_Diagnosis_Config = MultiInterventionDistributor(
        Intervention_List=[tested_negative, BroadcastEvent(Broadcast_Event=tested_negative_tether)])
    interventions = [intervention_cfg, received_test_event]

    gender = "All"
    age_min = 0
    age_max = 9.3228e+35
    if target != "Everyone" and isinstance(target, dict):
        try:
            age_min = target["agemin"]
            age_max = target["agemax"]
            if 'gender' in target:
                gender = target["gender"]
                target = "ExplicitAgeRangesAndGender"
            else:
                target = "ExplicitAgeRanges"
        except KeyError:
            raise KeyError("Unknown target_group parameter. Please pass in 'Everyone' or a dictionary of "
                             "{'agemin' : x, 'agemax' : y, 'gender': 'Female'} to target  to individuals between x and "
                             "y years of age, and (optional) gender.\n")

    if trigger_condition_list:
        if listening_duration == -1:
            diagnosis_config_listening_duration = -1
        else:
            diagnosis_config_listening_duration = listening_duration + 1
        # if once triggered, you want the diagnostic survey to repeat or if there is a delay (or both)
        # this creates a series of broadcast events that once triggered send out "Diagnostic_Survey_Now"
        # at pre-determined intervals
        if repetitions > 1 or triggered_campaign_delay > 0:
            # create a trigger for each of the delays.
            trigger_node_property_restrictions = []
            trigger_ind_property_restrictions = []
            if check_eligibility_at_trigger:
                trigger_node_property_restrictions = NP_restrictions
                trigger_ind_property_restrictions = IP_restrictions
                NP_restrictions = []
                IP_restrictions = []
            broadcast_event = "Diagnostic_Survey_Now_{}".format(random.randint(1, 100000))
            for x in range(repetitions):
                triggered_campaign_delay_event(cb, start_day, nodeIDs=nodeIDs,
                                               triggered_campaign_delay=triggered_campaign_delay + x * tsteps_btwn_repetitions,
                                               trigger_condition_list=trigger_condition_list,
                                               listening_duration=listening_duration, event_to_send_out=broadcast_event,
                                               node_property_restrictions=trigger_node_property_restrictions,
                                               ind_property_restrictions=trigger_ind_property_restrictions)
                trigger_condition_list = [broadcast_event]

        survey_event = CampaignEvent(
            Start_Day=start_day,
            Event_Name=event_name,
            Nodeset_Config=nodeset_config,
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Intervention_Config=NodeLevelHealthTriggeredIV(
                    Trigger_Condition_List=trigger_condition_list,
                    Target_Residents_Only=1,
                    Duration=listening_duration,
                    Demographic_Coverage=coverage,
                    Target_Demographic=target,
                    Target_Age_Min=age_min,
                    Target_Age_Max=age_max,
                    Target_Gender=gender,
                    Property_Restrictions_Within_Node=IP_restrictions,
                    Node_Property_Restrictions=NP_restrictions,
                    Disqualifying_Properties=disqualifying_properties,
                    Actual_IndividualIntervention_Config=MultiInterventionDistributor(
                        Intervention_List=interventions))))

        cb.add_event(survey_event)

    else:
        diagnosis_config_listening_duration = listening_duration
        survey_event = CampaignEvent(
            Start_Day=start_day,
            Event_Name=event_name,
            Nodeset_Config=nodeset_config,
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Node_Property_Restrictions=NP_restrictions,
                Property_Restrictions_Within_Node=IP_restrictions,
                Number_Repetitions=repetitions,
                Timesteps_Between_Repetitions=tsteps_btwn_repetitions,
                Target_Demographic=target,
                Demographic_Coverage=coverage,
                Target_Age_Min=age_min,
                Target_Age_Max=age_max,
                Target_Gender=gender,
                Intervention_Config=MultiInterventionDistributor(
                    Intervention_List=interventions)))

        cb.add_event(survey_event)

    if expire_recent_drugs:
        if IP_restrictions:
            for property_restriction in IP_restrictions:
                property_restriction["DrugStatus"] = "None"
        else:
            IP_restrictions = [{"DrugStatus": "None"}]

    if positive_diagnosis_configs:
        tested_positive_event = CampaignEvent(
            Start_Day=start_day - 1,
            Event_Name=event_name + "Positive Result Action",
            Nodeset_Config=nodeset_config,
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Intervention_Config=NodeLevelHealthTriggeredIV(
                    Duration=diagnosis_config_listening_duration,
                    Property_Restrictions_Within_Node=IP_restrictions,
                    Trigger_Condition_List=[tested_positive_tether],
                    Actual_IndividualIntervention_Config=MultiInterventionDistributor(
                        Intervention_List=positive_diagnosis_configs)
                )
            )
        )
        cb.add_event(tested_positive_event)

    if negative_diagnosis_configs:
        tested_negative_event = CampaignEvent(
            Start_Day=start_day - 1,
            Event_Name=event_name + "Negative Result Action",
            Nodeset_Config=nodeset_config,
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Intervention_Config=NodeLevelHealthTriggeredIV(
                    Duration=diagnosis_config_listening_duration,
                    Trigger_Condition_List=[tested_negative_tether],
                    Actual_IndividualIntervention_Config=MultiInterventionDistributor(
                        Intervention_List=negative_diagnosis_configs)
                    )
                )
            )
        cb.add_event(tested_negative_event)

    return


