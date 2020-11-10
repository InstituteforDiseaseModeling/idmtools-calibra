from dtk.utils.Campaign.CampaignClass import *
from dtk.utils.Campaign.CampaignEnum import *


seir_vitaldynamics_campaign = Campaign(
    Use_Defaults=True,
    Events=[
        CampaignEvent(
            Campaign_Name="Pre-outbreak Immunity",
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
                Number_Repetitions=10,
                Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.Everyone,
                Timesteps_Between_Repetitions=730
            ),
            Nodeset_Config=NodeSetAll(),
            Start_Day=1
        ),
        CampaignEvent(
            Campaign_Name="Outbreak",
            Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                Demographic_Coverage=0.001,
                Intervention_Config=OutbreakIndividual(
                    Antigen=0,
                    Event_Name="Outbreak",              # [TODO]: un-defined
                    Genome=0,
                    Outbreak_Source="ImportCases"       # [TODO]: un-defined
                ),
                Number_Repetitions=10,
                Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.Everyone,
                Timesteps_Between_Repetitions=730
            ),
            Nodeset_Config=NodeSetAll(),
            Start_Day=5
        )
    ]
)
