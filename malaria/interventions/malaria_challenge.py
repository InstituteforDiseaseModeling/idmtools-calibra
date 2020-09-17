from dtk.utils.Campaign.CampaignClass import *


def add_challenge_trial(config_builder, start_day: int = 0):
    """
        Add an intervention to distribute an infectious challenge mosquito bite to all individuals 
        to the campaign using the **MalariaChallenge** class, a node-level intervention.
    Args:
        config_builder: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` 
            object for building, modifying, and writing campaign configuration files.
        start_day: The day to distribute the intervention; default = 0.

    Returns:
        Dictionary in format {'challenge_start' : start_day}.

    """
    # No mosquitoes or births/deaths
    config_builder.update_params({"Enable_Vital_Dynamics": 0})

    # Infectious-bite challenge
    challenge_event = CampaignEvent(Start_Day=start_day,
                                    Nodeset_Config=NodeSetAll(),
                                    Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                                        Number_Distributions=-1,
                                        Number_Repetitions=1,
                                        Timesteps_Between_Repetitions=1,
                                        Intervention_Config=MalariaChallenge(
                                            Challenge_Type="InfectiousBites",
                                            Infectious_Bite_Count=5)))

    config_builder.add_event(challenge_event)
    return {'challenge_start': start_day}
