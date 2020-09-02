from dtk.utils.Campaign.CampaignClass import *


def add_mosquito_release(cb, start_day: int = 0, species: str = "arabiensis",
                         number: int = 100, repetitions: int = -1, tsteps_btwn: int = 365,
                         released_genome: list = None,
                         released_wolbachia: str = "VECTOR_WOLBACHIA_FREE",
                         cost: int = 0, release_event: str = None,
                         nodeIDs: list = None):
    """
    Add repeated mosquito release events to the campaign using the
    **MosquitoRelease** class.

    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            containing the campaign configuration.
        start_day: The day of the first release (**Start_Day** parameter).
        species: The name of the released mosquito species (**Released_Species**
            parameter).
        number: The number of mosquitoes released by the intervention
            (**Released_Number** parameter).
        repetitions: The number of times to repeat the intervention
            (**Number_Repetitions** parameter).
        tsteps_btwn:  The number of time steps between repetitions.
        released_genome: A list of allele pairs for each gene in the vector
            genome. Gender is specified using ["X", "X"] or ["X", "Y"].
        released_wolbachia: The Wolbachia type of released mosquitoes. Possible
            values are:
            * WOLBACHIA_FREE
            * VECTOR_WOLBACHIA_A
            * VECTOR_WOLBACHIA_B
            * VECTOR_WOLBACHIA_AB
        cost: fills out **Cost_To_Consumer** parameter, Default = 0
        release_event: Optional, a NODE event that gets send out at the same time as MosquitoRelease happens
            examples: "just_released_mosquitos"
        nodeIDs: List of nodes in which to distribute this intervention.
            Default: None or [], the intervention is distributed to all available nodes
            Example: [1,2,345,1000]

    Returns:
        None

    Example:
        ::

            cb = DTKConfigBuilder.from_defaults(sim_example)
            nodeIDs = [1, 5, 9, 34]
            add_mosquito_release(cb, start_day=1, species="gambiae", number=100,
            repetitions=4, tsteps_btwn=365, gender='VECTOR_FEMALE',
                             released_genome=[['X', 'X']],
                             released_wolbachia="VECTOR_WOLBACHIA_A", nodes)
    """
    if not released_genome:
        released_genome = [['X', 'X']]
    if not nodeIDs:
        nodeset_config = NodeSetAll()
    else:
        nodeset_config = NodeSetNodeList(Node_List=nodeIDs)

    mosquito_release = MosquitoRelease(
                Cost_To_Consumer=cost,
                Released_Genome=released_genome,
                Released_Number=number,
                Released_Species=species,
                Released_Wolbachia=released_wolbachia)

    if release_event:
        release_event = BroadcastNodeEvent(Broadcast_Event=release_event)
        intervention_config = MultiNodeInterventionDistributor(
                        Node_Intervention_List=[mosquito_release, release_event])
    else:
        intervention_config = mosquito_release

    intervention = CampaignEvent(
        Start_Day=start_day,
        Nodeset_Config=nodeset_config,
        Event_Name="Mosquito Release",
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            Number_Repetitions=repetitions,
            Timesteps_Between_Repetitions=tsteps_btwn,
            Intervention_Config=intervention_config))

    cb.add_event(intervention)
