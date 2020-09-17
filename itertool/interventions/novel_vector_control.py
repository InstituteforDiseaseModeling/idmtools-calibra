from dtk.utils.Campaign.CampaignClass import *
from dtk.vector.species import get_species_names, get_species_param_block
import copy


def add_ATSB(cb, start_day: int=0, coverage: float=0.15, kill_cfg: any=None, duration: int=180, duration_std_dev: int=14,
             insecticide: str = None, nodeIDs: list=None, node_property_restrictions: list=None):
    """
    Add an attractive targeted sugar bait (ATSB) intervention (**SugarTrap** class) using the
    **StandardInterventionDistributionEventCoordinator**.

    Args:
        cb: The The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` 
            containing the campaign configuration.
        start_day: The day on which to start distributing the intervention (**Start_Day** parameter).
        coverage: The proportion of the population that will receive the 
            intervention (**Demographic_Coverage** parameter).
        kill_cfg: Dictionary representing configuration for
         **Killing_Config_Per_Species** or a list of such dictionaries.
        duration: The length of time the ATSB is active for, independent
            of the waning profile of killing. This allows the node to prematurely
            get rid of the ATSB, much like **UsageDependentBednet** allows
            bednet users to get rid of good bednets. The expiration time
            is drawn from a Gaussian distribution with (mu, s) = (**duration**,
            **duration_std_dev**). 
        duration_std_dev: Width of the Gaussian distribution from which 
            the ATSB expiration time is drawn.
        insecticide:  Sets **Insecticide_Name** for the intervention.
        nodeIDs: The list of nodes to apply this intervention to 
            (**Node_List** parameter). If not provided, set value of NodeSetAll.
        node_property_restrictions: The NodeProperty key:value pairs that 
            nodes must have to receive the intervention (**Node_Property_Restrictions** 
            parameter).
    Returns:
        None

    Example:
        ::

            cb = DTKConfigBuilder.from_defaults("MALARIA_SIM")
            kill_cfg =  WaningEffectBoxExponential(Initial_Effect=0.0337*coverage, Box_Duration=180,
                Decay_Time_Constant=30)
            or
            kill_cfg = {"Box_Duration": 3650,
                        "Initial_Effect": 0.93,
                        "class": "WaningEffectBox"}
            add_ATSB(cb, start=30, coverage=0.15, kill_cfg=kill_cfg,
                     duration=90, duration_std_dev=7,
                     node_property_restrictions= [{"Place": "Rural"}])
    """
    if node_property_restrictions is None:
        node_property_restrictions = []
    if nodeIDs:
        node_cfg = NodeSetNodeList(Node_List=nodeIDs)
    else:
        node_cfg = NodeSetAll()

    cfg_species = []
    for vector_species in cb.get_param("Vector_Species_Params"):
        if vector_species["Vector_Sugar_Feeding_Frequency"] != "VECTOR_SUGAR_FEEDING_NONE":
            cfg_species.append(vector_species["Name"])

    if not cfg_species:
        raise ValueError("No species found without 'VECTOR_SUGAR_FEEDING_NONE' setting. "
                         "Please review/update and try again.\n")
    if not kill_cfg:
        kill_cfg = WaningEffectBoxExponential(
            Initial_Effect=0.0337*coverage,
            Box_Duration=180,
            Decay_Time_Constant=30)

    atsb_config = SugarTrap(
        Cost_To_Consumer=3.75,
        Killing_Config=kill_cfg,
        Expiration_Distribution="GAUSSIAN_DISTRIBUTION",
        Expiration_Gaussian_Mean=duration,
        Expiration_Gaussian_Std_Dev=duration_std_dev
    )

    if insecticide:
        atsb_config.Insecticide_Name = insecticide

    event = CampaignEvent(
        Start_Day=start_day,
        Nodeset_Config=node_cfg,
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            Intervention_Config=atsb_config,
            Intervention_Name="Attractive Toxic Sugar Bait",
            Demographic_Coverage=1,
            Node_Property_Restrictions=node_property_restrictions,
        )
    )
    cb.add_event(event)


def add_topical_repellent(config_builder, start_day: int=0, coverage_by_ages: list=None, cost: float=0,
                          insecticide: str=None,
                          repelling_initial: float=0.95, repelling_duration=0.3,
                          repetitions: int=1, tsteps_btwn: int=1, nodeIDs: list=None,
                          node_property_restrictions: list=None, ind_property_restrictions: list=None):
    """
    Add a topical insect repellent intervention (**SimpleIndividualRepellent** class)
    using the **StandardInterventionDistributionEventCoordinator** or a **BirthTriggeredIV**

    Args:
        config_builder: The The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` containing the 
            campaign configuration.
        start_day: The day on which to start distributing the intervention (**Start_Day** parameter).
        coverage_by_ages: A list of dictionaries defining the coverage per
            age group or birth-triggered intervention. For example,
            ``[{"birth":1, "duration":365, "coverage":0.9}, {"coverage":1, "age_min": 1, "age_max": 10},
            {"coverage":0.5,"age_min": 11,"age_max": 50}]`` If "birth":0, birth-triggered intervention will not be
            distributed.
        cost: The cost of each individual application (**Cost_To_Consumer** parameter).
        insecticide:  Sets **Insecticide_Name** for the intervention.
        repelling_initial: The initial blocking effect of the repellent
            (**Initial_Effect** parameter).
        repelling_duration: The duration of the effectiveness (**Box_Duration**
            parameter with the **WaningEffectBox** class).
        repetitions: The number of times to repeat the intervention 
            (**Number_Repetitions** parameter).
        tsteps_btwn: The timesteps between repeated distributions
            (**Timesteps_Between_Repetitions** parameter).
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention
            (**Node_Property_Restrictions** parameter). In the format
            ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``.
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention
            (**Property_Restrictions_Within_Node** parameter). In the format
            ``[{"BitingRisk":"High"}, {"IsCool":"Yes}]``.
    Returns:
        None

    Example:
        ::

            config_builder = DTKConfigBuilder.from_defaults("MALARIA_SIM")
            add_topical_repellent(config_builder, start=10,
                                  coverage_by_ages = [{"birth": 1,
                                                       "duration": -1,
                                                       "coverage": 0.75},
                                                       ],
                                  cost=1, initial_blocking=0.86, duration=0.3,
                                  repetitions=2, interval=1, nodeIDs=[1, 4, 19])
    """
    if not coverage_by_ages:
        raise ValueError('''Please define a list of coverages by age, in format of: 
        "[{"birth":1, "duration":365, "coverage":0.9}, {"coverage":1,"age_min": 1, "age_max": 10},
        {"coverage":0.5,"age_min": 11,"age_max": 50}] ")''' + "\n")
    if node_property_restrictions is None:
        node_property_restrictions = []
    if ind_property_restrictions is None:
        ind_property_restrictions = []
    if nodeIDs:
        node_cfg = NodeSetNodeList(Node_List=nodeIDs)
    else:
        node_cfg = NodeSetAll()

    repellent = SimpleIndividualRepellent(
        Cost_To_Consumer=cost,
        Event_Name="Individual Repellent",
        Repelling_Config=WaningEffectBox(
            Initial_Effect=repelling_initial,
            Box_Duration=repelling_duration
        )
    )
    if insecticide:
        repellent.Insecticide_Name = insecticide

    for coverage_by_age in coverage_by_ages:
        if 'birth' in coverage_by_age.keys():
            if coverage_by_age['birth']:
                repellent_event = CampaignEvent(
                    Start_Day=start_day,
                    Nodeset_Config=node_cfg,
                    Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                        Intervention_Config=BirthTriggeredIV(
                            Node_Property_Restrictions=node_property_restrictions,
                            Property_Restrictions_Within_Node=ind_property_restrictions,
                            Duration=coverage_by_age.get('duration', -1),
                            Demographic_Coverage=coverage_by_age["coverage"],
                            Actual_IndividualIntervention_Config=repellent
                        )
                    )
                )
                config_builder.add_event(repellent_event)
        else:
            repellent_event = CampaignEvent(
                Start_Day=start_day,
                Nodeset_Config=node_cfg,
                Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                    Node_Property_Restrictions=node_property_restrictions,
                    Property_Restrictions_Within_Node=ind_property_restrictions,
                    Target_Residents_Only=0,
                    Demographic_Coverage=coverage_by_age["coverage"],
                    Target_Demographic="ExplicitAgeRanges",
                    Target_Age_Min=coverage_by_age["age_min"],
                    Target_Age_Max=coverage_by_age["age_max"],
                    Number_Repetitions=repetitions,
                    Timesteps_Between_Repetitions=tsteps_btwn,
                    Intervention_Config=repellent
                )
            )
            config_builder.add_event(repellent_event)


def add_ors_node(config_builder, start_day: int=0, spray_coverage: float=1, killing_initial: float=0.95,
                 killing_decay: int=100, cost: float=1, insecticide: str=None, nodeIDs: list=None,
                 node_property_restrictions: list=None):
    """
    Add an outdoor residential spraying intervention (**SpaceSpraying** class) using
    **StandardInterventionDistributionEventCoordinator**

    Args:
        config_builder: The The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` 
            containing the campaign configuration.
        start_day: The day on which to start distributing the intervention
            (**Start_Day** parameter).
        spray_coverage: Portion of node that is being sprayed
        killing_initial:  The initial killing effect of the outdoor spraying
            (**Initial_Effect** parameter).
        killing_decay: The exponential decay length, in days (**Decay_Time_Constant**
            in **Killing_Config**).
        cost: The cost of each individual application (**Cost_To_Consumer** 
            parameter).
        insecticide:  Sets **Insecticide_Name** for the intervention.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List** 
            parameter). If not provided, set value of NodeSetAll.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention
            (**Node_Property_Restrictions** parameter). In the format
            ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``.

    Returns:
        None

    Example:
        ::

            config_builder = DTKConfigBuilder.from_defaults("MALARIA_SIM")
            add_ors_node(config_builder, start_day=200, spray_coverage=0.8,
                         killing_initial=0.85, killing_duration=45, cost=1,
                         nodeIDs=[1, 4, 7])
    """
    if not node_property_restrictions:
        node_property_restrictions = []
    if nodeIDs:
        node_cfg = NodeSetNodeList(Node_List=nodeIDs)
    else:
        node_cfg = NodeSetAll()

    ors_event = CampaignEvent(
                Event_Name="Outdoor Residual Spray",
                Nodeset_Config=node_cfg,
                Start_Day=start_day,
                Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                    Node_Property_Restrictions=node_property_restrictions,
                    Intervention_Config=SpaceSpraying(
                            Spray_Kill_Target=SpaceSpraying_Spray_Kill_Target_Enum.SpaceSpray_FemalesAndMales,
                            Habitat_Target=SpaceSpraying_Habitat_Target_Enum.ALL_HABITATS,
                            Spray_Coverage=spray_coverage,
                            Cost_To_Consumer=cost,
                            Killing_Config=WaningEffectExponential(
                                Initial_Effect=killing_initial,
                                Decay_Time_Constant=killing_decay
                            )
                        )
                )
    )
    if insecticide:
        ors_event.Event_Coordinator_Config.Intervention_Config.Insecticide_Name = insecticide

    config_builder.add_event(ors_event)


def add_larvicides(config_builder, start_day: int=0, habitat_target: str="ALL_HABITATS", spray_coverage: float=1,
                   killing_initial: float=1, killing_duration: int=100, killing_decay: int=150, cost: float=1,
                   insecticide: str=None,
                   nodeIDs: list=None, node_property_restrictions: list=None):
    """
    Add a mosquito larvicide intervention to the campaign using the
    **Larvicides** class, please note the Killing and Blocking configurations are using
    **WaningEffectBoxExponential** class.


    Args:
        config_builder: The :py:class:`DTKConfigBuilder
            <dtk.utils.core.DTKConfigBuilder>` containing the campaign
            configuration.
        start_day: The day on which to start distributing the larvicide
            (**Start_Day** parameter).
        habitat_target: The larval habitat type targeted by the larvicide, needs to be all upper_case
            (**Habitat_Target** parameter).
        spray_coverage: Portion of the node that's being sprayed.
        killing_initial: for WaningEffectBoxExponential, the initial larval killing efficacy
            (**Initial_Effect** in **Killing_Config**).
        killing_duration: for WaningEffectBoxExponentialThe box duration of the effect in days
            (**Box_Duration** in **Killing_Config**).
        killing_decay: for WaningEffectBoxExponential The exponential decay length, in days
            (**Decay_Time_Constant** in **Killing_Config**).
        cost: The cost of each individual application (**Cost_To_Consumer**
            parameter).
        insecticide:  Sets **Insecticide_Name** for the intervention.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention
            (**Node_Property_Restrictions** parameter). In the format
            ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``.
    Returns:
        None

    Example:
        ::
            config_builder = DTKConfigBuilder.from_defaults("MALARIA_SIM")
            add_larvicides(config_builder, start=725, killing_initial=0.75,
            habitat_target="HUMAN_POPULATION",
            nodeIDs=[2, 5, 7])
    """

    if node_property_restrictions is None:
        node_property_restrictions = []
    if nodeIDs:
        node_cfg = NodeSetNodeList(Node_List=nodeIDs)
    else:
        node_cfg = NodeSetAll()

    event = CampaignEvent(
        Start_Day=start_day,
        Nodeset_Config=node_cfg,
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            Node_Property_Restrictions=node_property_restrictions,
            Intervention_Config=Larvicides(
                        Spray_Coverage=spray_coverage,
                        Habitat_Target=Larvicides_Habitat_Target_Enum[habitat_target],
                        Cost_To_Consumer=cost,
                        Larval_Killing_Config=WaningEffectBoxExponential(
                            Box_Duration=killing_duration,
                            Decay_Time_Constant=killing_decay,
                            Initial_Effect=killing_initial
                        )
                    )
        )
    )
    if insecticide:
        event.Event_Coordinator_Config.Intervention_Config.Insecticide_Name = insecticide
    config_builder.add_event(event)


def add_eave_tubes(config_builder, start_day: int=0, coverage: float=1, killing_initial: float=1.0,
                   killing_decay: int=180, blocking_initial: float=1.0, blocking_decay: int=730,
                   outdoor_killing_discount: float=0.3, cost: float=0, insecticide: str=None,
                   outdoor_insecticide: str=None,
                   nodeIDs: list=None, node_property_restrictions: list=None, ind_property_restrictions: list=None):
    """
    Add insecticidal tubes to the eaves of houses (**IRSHousingModification** intervention class) and
    an outdoor residential spraying intervention (**SpaceSpraying** class) using
    **StandardInterventionDistributionEventCoordinator** (see add_ors_node)

    Args:
        config_builder: The The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` 
            containing the campaign configuration.
        start_day: The day on which to start distributing the intervention
            (**Start_Day** parameter).
        coverage: The proportion of the population that will receive the intervention 
            (**Demographic_Coverage** parameter).
        killing_initial:  The initial killing effect of the eave tubes
            (**Initial_Effect** parameter in **Killing_Config**).
        killing_decay: The exponential decay constant of the effectiveness
            (**Decay_Time_Constant** parameter with the **WaningEffectExponential** 
            class).
        blocking_initial:  The initial blocking effect of the eave tubes
            (**Initial_Effect** parameter in **Blocking_Config**).
        blocking_decay: The exponential decay constant of the effectiveness
            (**Decay_Time_Constant** parameter with the **WaningEffectExponential** class).
        outdoor_killing_discount: The value to differentially scale initial 
            killing effect for outdoor vectors vs. indoor vectors.
        cost: The cost of each individual application (**Cost_To_Consumer** parameter).
        insecticide:  Sets **Insecticide_Name** for the IRSHousingModification intervention.
        outdoor_insecticide: Sets **Insecticide_Name** for the SpaceSpraying intervention. If this parameter is None,
            but IRSHousingModification's insecticide is set - same insecticide is used for both.
        nodeIDs: The list of nodes to apply this intervention to (**Node_List** 
            parameter). If not provided, set value of NodeSetAll.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention
            (**Node_Property_Restrictions** parameter). In the format
            ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``.
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention
            (**Property_Restrictions_Within_Node** parameter). In the format
            ``[{"BitingRisk":"High"}, {"IsCool":"Yes}]``.

    Returns:
        None

    Example:
        ::

            config_builder = DTKConfigBuilder.from_defaults('MALARIA_SIM')
            add_eave_tubes(config_builder, start_day=37, coverage=0.65,
                           killing_initial=0.85, killing_decay=90,
                           blocking_initial=0.95, blocking_decay=365,
                           outdoor_killing_discount=0.3, cost=1,
                           nodeIDs=[33, 56, 7])
    """
    if node_property_restrictions is None:
        node_property_restrictions = []
    if ind_property_restrictions is None:
        ind_property_restrictions = []
    if nodeIDs:
        node_cfg = NodeSetNodeList(Node_List=nodeIDs)
    else:
        node_cfg = NodeSetAll()

    indoor_event = CampaignEvent(
        Start_Day=start_day,
        Nodeset_Config=node_cfg,
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            Node_Property_Restrictions=node_property_restrictions,
            Property_Restrictions_Within_Node=ind_property_restrictions,
            Demographic_Coverage=coverage,
            Intervention_Config=IRSHousingModification(
                Cost_To_Consumer=cost,
                Killing_Config=WaningEffectExponential(
                    Initial_Effect=killing_initial,
                    Decay_Time_Constant=killing_decay
                ),
                Blocking_Config=WaningEffectExponential(
                    Initial_Effect=blocking_initial,
                    Decay_Time_Constant=blocking_decay
                )
            )
        )
    )
    if insecticide:
        indoor_event.Event_Coordinator_Config.Intervention_Config.Insecticide_Name = insecticide
        if not outdoor_insecticide:
            outdoor_insecticide = insecticide

    config_builder.add_event(indoor_event)

    add_ors_node(config_builder, start_day=start_day, spray_coverage=coverage,
                 killing_initial=killing_initial*outdoor_killing_discount,
                 killing_decay=killing_decay, cost=cost, insecticide=outdoor_insecticide,
                 nodeIDs=nodeIDs, node_property_restrictions=node_property_restrictions)
