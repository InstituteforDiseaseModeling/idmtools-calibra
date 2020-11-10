from dtk.utils.Campaign.CampaignClass import *
from dtk.utils.Campaign.CampaignEnum import *


sir_campaign = Campaign(
    Campaign_Name="Initial Seeding",
    Use_Defaults=True,
    Events=[
        CampaignEvent(
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Demographic_Coverage=0.0005,
                Intervention_Config=OutbreakIndividual(
                    Antigen=0,
                    Genome=0,
                    Outbreak_Source="PrevalenceIncrease"        # [TODO]: un-defined
                ),
                Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.Everyone
            ),
            Event_Name="Outbreak",                              # [TODO]: un-defined
            Nodeset_Config=NodeSetAll(),
            Start_Day=1
        )
    ]
)
