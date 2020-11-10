from dtk.utils.Campaign.CampaignClass import *
from dtk.utils.Campaign.CampaignEnum import *


dengue_campaign = Campaign(Campaign_Name="Campaign - Bednets, IRS and Vaccines", Use_Defaults=1)

ce1 = CampaignEvent(
     Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
          Intervention_Config=OutbreakIndividualDengue(Strain_Id_Name="Strain_1"),
          Target_Age_Min=0,
          Target_Age_Max=1.725,
          Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.ExplicitAgeRanges
     ),
     Nodeset_Config=NodeSetAll(),
     Start_Day=100
)

ce2 = CampaignEvent(
     Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
          Intervention_Config=OutbreakIndividualDengue(Strain_Id_Name="Strain_2"),
          Demographic_Coverage=0,
          Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.Everyone
     ),
     Nodeset_Config=NodeSetAll(),
     Start_Day=5000
)


ce3 = CampaignEvent(
     Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
          Intervention_Config=OutbreakIndividualDengue(Strain_Id_Name="Strain_3"),
          Demographic_Coverage=0,
          Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.Everyone
     ),
     Nodeset_Config=NodeSetAll(),
     Start_Day=5000
)


ce4 = CampaignEvent(
     Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
          Intervention_Config=OutbreakIndividualDengue(Strain_Id_Name="Strain_4"),
          Demographic_Coverage=0,
          Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.Everyone
     ),
     Nodeset_Config=NodeSetAll(),
     Start_Day=5000
)


dengue_campaign.add_campaign_event(ce1)
dengue_campaign.add_campaign_event(ce2)
dengue_campaign.add_campaign_event(ce3)
dengue_campaign.add_campaign_event(ce4)