from dtk.utils.Campaign.CampaignClass import *
from dtk.utils.Campaign.CampaignEnum import *


seirs_campaign = CampaignEvent(
    Use_Defaults=1,
    Events=[
        CampaignEvent(
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Demographic_Coverage=0.001,
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
        ),
        CampaignEvent(
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Demographic_Coverage=0.8,
                Intervention_Config=SimpleVaccine(
                    Cost_To_Consumer=10.0,
                    Reduced_Transmit=0,
                    Vaccine_Take=1,
                    Vaccine_Type=SimpleVaccine_Vaccine_Type_Enum.AcquisitionBlocking,
                    Waning_Config=WaningEffectBox(
                        Box_Duration=3650,
                        Initial_Effect=1
                    )
                ),
                Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.Everyone
            ),
            Event_Name="Outbreak",                              # [TODO]: un-defined
            Nodeset_Config=NodeSetAll(),
            Start_Day=500
        )
    ]
)
