from typing import Dict
from emodpy.defaults.iemod_default import IEMODDefault
from emodpy.emod_campaign import EMODCampaign


class EMODMalariaSim(IEMODDefault):
    @staticmethod
    def config() -> Dict:
        return {
            "Config_Name": "",
            "Campaign_Filename": "campaign.json",
            "Enable_Interventions": 1,
            "Enable_Spatial_Output": 0,
            "Enable_Property_Output": 0,
            "Enable_Timestep_Channel_In_Report": 0,
            "Enable_Default_Reporting": 1,
            "Enable_Heterogeneous_Intranode_Transmission": 0,
            "Enable_Initial_Susceptibility_Distribution": 0,
            "Enable_Maternal_Infection_Transmission": 0,
            "Enable_Maternal_Protection": 0,
            "Enable_Skipping": 0,
            "Minimum_Adult_Age_Years": 15,
            "Vector_Migration_Base_Rate": 0.5,
            "Geography": "",
            "Node_Grid_Size": 0.042,
            "Default_Geography_Initial_Node_Population": 100,
            "Default_Geography_Torus_Size": 10,
            "Random_Type": "USE_PSEUDO_DES",
            "Run_Number": 5,
            "Serialization_Type": "NONE",
            "Simulation_Duration": 1825,
            "Simulation_Timestep": 1,
            "Simulation_Type": "MALARIA_SIM",
            "Start_Time": 0,
            "Num_Cores": 1,
            "Python_Script_Path": "",
            "Load_Balance_Filename": "",
            "Load_Balance_Scheme": "STATIC",
            "Custom_Coordinator_Events": [

            ],
            "Custom_Reports_Filename": "",
            "Custom_Node_Events": [

            ],
            "Custom_Individual_Events": [
                "Received_Treatment"
            ],
            "Enable_Infectivity_Reservoir": 0,
            "Enable_Termination_On_Zero_Total_Infectivity": 0,
            "Report_Coordinator_Event_Recorder": 0,
            "Report_Node_Event_Recorder": 0,
            "Report_Surveillance_Event_Recorder": 0,
            "Report_Event_Recorder": 0,
            "x_Base_Population": 1,
            "Climate_Model": "CLIMATE_BY_DATA",
            "Climate_Update_Resolution": "CLIMATE_UPDATE_DAY",
            "Enable_Climate_Stochasticity": 0,
            "Air_Temperature_Filename": "",
            "Air_Temperature_Offset": 0,
            "Air_Temperature_Variance": 2,
            "Base_Air_Temperature": 22.0,
            "Relative_Humidity_Filename": "",
            "Relative_Humidity_Scale_Factor": 1,
            "Relative_Humidity_Variance": 0.05,
            "Base_Relative_Humidity": 0.75,
            "Land_Temperature_Filename": "",
            "Land_Temperature_Offset": 0,
            "Land_Temperature_Variance": 2,
            "Base_Land_Temperature": 26.0,
            "Rainfall_Filename": "",
            "Rainfall_Scale_Factor": 1,
            "Enable_Rainfall_Stochasticity": 1,
            "Base_Rainfall": 10.0,
            "Demographics_Filenames": [

            ],
            "Population_Scale_Type": "FIXED_SCALING",
            "Enable_Aging": 1,
            "Age_Initialization_Distribution_Type": "DISTRIBUTION_SIMPLE",
            "Enable_Demographics_Birth": 1,
            "Enable_Demographics_Initial": 1,
            "Enable_Demographics_Other": 0,
            "Enable_Demographics_Reporting": 0,
            "Enable_Demographics_Builtin": 0,
            "Enable_Demographics_Risk": 0,
            "Enable_Immunity_Initialization_Distribution": 0,
            "Susceptibility_Initialization_Distribution_Type": "DISTRIBUTION_OFF",
            "Enable_Initial_Prevalence": 1,
            "Enable_Vital_Dynamics": 1,
            "Death_Rate_Dependence": "NONDISEASE_MORTALITY_BY_AGE_AND_GENDER",
            "Enable_Birth": 1,
            "Birth_Rate_Dependence": "POPULATION_DEP_RATE",
            "Birth_Rate_Time_Dependence": "NONE",
            "x_Birth": 1,
            "Enable_Disease_Mortality": 0,
            "Base_Mortality": 0,
            "Mortality_Time_Course": "DAILY_MORTALITY",
            "x_Other_Mortality": 1,
            "Enable_Natural_Mortality": 1,
            "Individual_Sampling_Type": "TRACK_ALL",
            "Base_Individual_Sample_Rate": 1,
            "Max_Node_Population_Samples": 40,
            "Sample_Rate_0_18mo": 1,
            "Sample_Rate_10_14": 1,
            "Sample_Rate_15_19": 1,
            "Sample_Rate_18mo_4yr": 1,
            "Sample_Rate_20_Plus": 1,
            "Sample_Rate_5_9": 1,
            "Sample_Rate_Birth": 2,
            "Enable_Immunity": 1,
            "Enable_Immune_Decay": 1,
            "Post_Infection_Acquisition_Multiplier": 1,
            "Acquisition_Blocking_Immunity_Decay_Rate": 0.01,
            "Acquisition_Blocking_Immunity_Duration_Before_Decay": 90,
            "Post_Infection_Mortality_Multiplier": 1,
            "Mortality_Blocking_Immunity_Decay_Rate": 0.001,
            "Mortality_Blocking_Immunity_Duration_Before_Decay": 90,
            "Post_Infection_Transmission_Multiplier": 1,
            "Transmission_Blocking_Immunity_Decay_Rate": 0.01,
            "Transmission_Blocking_Immunity_Duration_Before_Decay": 90,
            "x_Population_Immunity": 1,
            "Enable_Susceptibility_Scaling": 0,
            "Susceptibility_Scale_Type": "CONSTANT_SUSCEPTIBILITY",
            "Symptomatic_Infectious_Offset": 0,
            "Incubation_Period_Exponential": 25,
            "Incubation_Period_Distribution": "CONSTANT_DISTRIBUTION",
            "Infectious_Period_Constant": 180,
            "Base_Infectivity": 1,
            "Infectious_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
            "Infectivity_Scale_Type": "CONSTANT_INFECTIVITY",
            "Population_Density_Infectivity_Correction": "CONSTANT_INFECTIVITY",
            "Population_Density_C50": 30,
            "Number_Basestrains": 1,
            "Number_Substrains": 1,
            "Enable_Superinfection": 1,
            "Max_Individual_Infections": 3,
            "Infection_Updates_Per_Timestep": 8,
            "Enable_Maternal_Transmission": 0,
            "Maternal_Transmission_Probability": 0,
            "Migration_Model": "NO_MIGRATION",
            "Migration_Pattern": "WAYPOINTS_HOME",
            "Roundtrip_Waypoints": 5,
            "Enable_Migration_Heterogeneity": 0,
            "Enable_Air_Migration": 0,
            "Air_Migration_Filename": "",
            "x_Air_Migration": 1,
            "Air_Migration_Roundtrip_Duration": 0,
            "Air_Migration_Roundtrip_Probability": 0,
            "Enable_Local_Migration": 0,
            "Local_Migration_Filename": "",
            "x_Local_Migration": 1,
            "Local_Migration_Roundtrip_Duration": 0,
            "Local_Migration_Roundtrip_Probability": 0,
            "Enable_Regional_Migration": 0,
            "Regional_Migration_Filename": "",
            "x_Regional_Migration": 1,
            "Regional_Migration_Roundtrip_Duration": 0,
            "Regional_Migration_Roundtrip_Probability": 0,
            "Enable_Sea_Migration": 0,
            "Sea_Migration_Filename": "",
            "x_Sea_Migration": 1,
            "Sea_Migration_Roundtrip_Duration": 0,
            "Sea_Migration_Roundtrip_Probability": 0,
            "Enable_Sea_Demographics_Modifiers": 0,
            "Sea_Demographics_Modifier_Adult_Males": 1.0,
            "Sea_Demographics_Modifier_Adult_Females": 0.0,
            "Sea_Demographics_Modifier_Child_Males": 0.0,
            "Sea_Demographics_Modifier_Child_Females": 0.0,
            "Enable_Sea_Family_Migration": 0,
            "Sea_Family_Migration_Probability": 0.2,
            "Enable_Family_Migration": 0,
            "Family_Migration_Filename": "",
            "Family_Migration_Roundtrip_Duration": 1.0,
            "x_Family_Migration": 1,
            "Enable_Vector_Species_Report": 0,
            "Vector_Sampling_Type": "VECTOR_COMPARTMENTS_NUMBER",
            "Mosquito_Weight": 1,
            "Enable_Vector_Aging": 0,
            "Enable_Vector_Mortality": 1,
            "Enable_Vector_Migration": 0,
            "Enable_Vector_Migration_Human": 0,
            "Enable_Vector_Migration_Local": 0,
            "Enable_Vector_Migration_Wind": 0,
            "Enable_Temperature_Dependent_Feeding_Cycle": 0,
            "Enable_Vector_Migration_Regional": 0,
            "x_Vector_Migration_Local": 0,
            "x_Vector_Migration_Regional": 0,
            "Vector_Migration_Filename_Local": "",
            "Vector_Migration_Filename_Regional": "",
            "Vector_Migration_Habitat_Modifier": 6.5,
            "Vector_Migration_Food_Modifier": 0,
            "Vector_Migration_Stay_Put_Modifier": 0.3,
            "Age_Dependent_Biting_Risk_Type": "SURFACE_AREA_DEPENDENT",
            "Newborn_Biting_Risk_Multiplier": 0.2,
            "Human_Feeding_Mortality": 0.1,
            "Wolbachia_Infection_Modification": 1.0,
            "Wolbachia_Mortality_Modification": 1.0,
            "HEG_Homing_Rate": 0.0,
            "HEG_Fecundity_Limiting": 0.0,
            "HEG_Model": "OFF",
            "x_Temporary_Larval_Habitat": 1,
            "Vector_Species_Params": [

            ],
            "Egg_Hatch_Density_Dependence": "NO_DENSITY_DEPENDENCE",
            "Enable_Temperature_Dependent_Egg_Hatching": 0,
            "Enable_Egg_Mortality": 0,
            "Enable_Drought_Egg_Hatch_Delay": 0,
            "Temperature_Dependent_Feeding_Cycle": "NO_TEMPERATURE_DEPENDENCE",
            "Insecticides": [

            ],
            "Genome_Markers": [

            ],
            "Incubation_Period_Constant": 25,
            "Infectious_Period_Exponential": 180,
            "Egg_Hatch_Delay_Distribution": "NO_DELAY",
            "Egg_Saturation_At_Oviposition": "SATURATION_AT_OVIPOSITION",
            "Mean_Egg_Hatch_Delay": 0,
            "Rainfall_In_mm_To_Fill_Swamp": 1000.0,
            "Semipermanent_Habitat_Decay_Rate": 0.01,
            "Temporary_Habitat_Decay_Factor": 0.05,
            "Larval_Density_Dependence": "UNIFORM_WHEN_OVERPOPULATION",
            "Vector_Larval_Rainfall_Mortality": "NONE",
            "Malaria_Model": "MALARIA_MECHANISTIC_MODEL",
            "Malaria_Strain_Model": "FALCIPARUM_RANDOM_STRAIN",
            "Enable_Malaria_CoTransmission": 0,
            "Mean_Sporozoites_Per_Bite": 11,
            "Base_Sporozoite_Survival_Fraction": 0.25,
            "Base_Incubation_Period": 7,
            "Merozoites_Per_Hepatocyte": 15000,
            "Antibody_IRBC_Kill_Rate": 1.596,
            "RBC_Destruction_Multiplier": 3.29,
            "Merozoites_Per_Schizont": 16,
            "Parasite_Switch_Type": "RATE_PER_PARASITE_7VARS",
            "Antigen_Switch_Rate": 7.645570124964182e-10,
            "Base_Gametocyte_Production_Rate": 0.06150582,
            "Base_Gametocyte_Mosquito_Survival_Rate": 0.002011099,
            "Falciparum_MSP_Variants": 32,
            "Falciparum_Nonspecific_Types": 76,
            "Falciparum_PfEMP1_Variants": 1070,
            "Gametocyte_Stage_Survival_Rate": 0.588569307,
            "MSP1_Merozoite_Kill_Fraction": 0.511735322,
            "Nonspecific_Antigenicity_Factor": 0.415111634,
            "Number_Of_Asexual_Cycles_Without_Gametocytes": 1,
            "Base_Gametocyte_Fraction_Male": 0.2,
            "Enable_Sexual_Combination": 0,
            "Antibody_CSP_Decay_Days": 90,
            "Antibody_CSP_Killing_Inverse_Width": 1.5,
            "Antibody_CSP_Killing_Threshold": 20,
            "Innate_Immune_Variation_Type": "NONE",
            "Pyrogenic_Threshold": 15000.0,
            "Fever_IRBC_Kill_Rate": 1.4,
            "Max_MSP1_Antibody_Growthrate": 0.045,
            "Antibody_Capacity_Growth_Rate": 0.09,
            "Nonspecific_Antibody_Growth_Rate_Factor": 0.5,
            "Antibody_Stimulation_C50": 30,
            "Antibody_Memory_Level": 0.34,
            "Min_Adapted_Response": 0.05,
            "Cytokine_Gametocyte_Inactivation": 0.01667,
            "Enable_Immunity_Distribution": 0,
            "Enable_Maternal_Antibodies_Transmission": 1,
            "Maternal_Antibodies_Type": "SIMPLE_WANING",
            "Maternal_Antibody_Protection": 0.1327,
            "Maternal_Antibody_Decay_Rate": 0.01,
            "Erythropoiesis_Anemia_Effect": 3.5,
            "Anemia_Mortality_Inverse_Width": 1,
            "Anemia_Mortality_Threshold": 0.654726662830038,
            "Anemia_Severe_Inverse_Width": 10,
            "Anemia_Severe_Threshold": 4.50775824973078,
            "Fever_Mortality_Inverse_Width": 1895.51971624351,
            "Fever_Mortality_Threshold": 3.4005008555391,
            "Fever_Severe_Inverse_Width": 27.5653580403806,
            "Fever_Severe_Threshold": 3.98354299722192,
            "Parasite_Mortality_Inverse_Width": 327.51594505874,
            "Parasite_Mortality_Threshold": 851138.0382023759,
            "Parasite_Severe_Inverse_Width": 56.5754896048744,
            "Parasite_Severe_Threshold": 851031.2877445256,
            "Clinical_Fever_Threshold_High": 1.5,
            "Clinical_Fever_Threshold_Low": 0.5,
            "Min_Days_Between_Clinical_Incidents": 14,
            "PfHRP2_Boost_Rate": 0.018,
            "PfHRP2_Decay_Rate": 0.167,
            "Report_Detection_Threshold_Blood_Smear_Gametocytes": 20,
            "Report_Detection_Threshold_Blood_Smear_Parasites": 20,
            "Report_Detection_Threshold_Fever": 1.0,
            "Report_Detection_Threshold_PCR_Gametocytes": 0.05,
            "Report_Detection_Threshold_PCR_Parasites": 0.05,
            "Report_Detection_Threshold_PfHRP2": 5.0,
            "Report_Detection_Threshold_True_Parasite_Density": 0.0,
            "Gametocyte_Smear_Sensitivity": 0.1,
            "Parasite_Smear_Sensitivity": 0.1,
            "Fever_Detection_Threshold": 1,
            "PCR_Sensitivity": 20,
            "RDT_Sensitivity": 0.01,
            "New_Diagnostic_Sensitivity": 0.025,
            "PKPD_Model": "CONCENTRATION_VERSUS_TIME",
            "Malaria_Drug_Params": {
                "Artemether": {
                    "Drug_Cmax": 114,
                    "Drug_Decay_T1": 0.12,
                    "Drug_Decay_T2": 0.12,
                    "Drug_Vd": 1,
                    "Drug_PKPD_C50": 0.6,
                    "Drug_Fulltreatment_Doses": 6,
                    "Drug_Dose_Interval": 0.5,
                    "Drug_Gametocyte02_Killrate": 2.5,
                    "Drug_Gametocyte34_Killrate": 1.5,
                    "Drug_GametocyteM_Killrate": 0.7,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 8.9,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 1,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 3,
                            "Fraction_Of_Adult_Dose": 0.25

                        },
                        {
                            "Upper_Age_In_Years": 6,
                            "Fraction_Of_Adult_Dose": 0.5

                        },
                        {
                            "Upper_Age_In_Years": 10,
                            "Fraction_Of_Adult_Dose": 0.75

                        }

                    ]

                },
                "Lumefantrine": {
                    "Drug_Cmax": 1017,
                    "Drug_Decay_T1": 1.3,
                    "Drug_Decay_T2": 2.0,
                    "Drug_Vd": 1.2,
                    "Drug_PKPD_C50": 280,
                    "Drug_Fulltreatment_Doses": 6,
                    "Drug_Dose_Interval": 0.5,
                    "Drug_Gametocyte02_Killrate": 2.4,
                    "Drug_Gametocyte34_Killrate": 0.0,
                    "Drug_GametocyteM_Killrate": 0.0,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 4.8,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 0.35,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 3,
                            "Fraction_Of_Adult_Dose": 0.25

                        },
                        {
                            "Upper_Age_In_Years": 6,
                            "Fraction_Of_Adult_Dose": 0.5

                        },
                        {
                            "Upper_Age_In_Years": 10,
                            "Fraction_Of_Adult_Dose": 0.75

                        }

                    ]

                },
                "DHA": {
                    "Drug_Cmax": 200,
                    "Drug_Decay_T1": 0.12,
                    "Drug_Decay_T2": 0.12,
                    "Drug_Vd": 1,
                    "Drug_PKPD_C50": 0.6,
                    "Drug_Fulltreatment_Doses": 3,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 2.5,
                    "Drug_Gametocyte34_Killrate": 1.5,
                    "Drug_GametocyteM_Killrate": 0.7,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 9.2,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 1,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 0.83,
                            "Fraction_Of_Adult_Dose": 0.375

                        },
                        {
                            "Upper_Age_In_Years": 2.83,
                            "Fraction_Of_Adult_Dose": 0.5

                        },
                        {
                            "Upper_Age_In_Years": 5.25,
                            "Fraction_Of_Adult_Dose": 0.625

                        },
                        {
                            "Upper_Age_In_Years": 7.33,
                            "Fraction_Of_Adult_Dose": 0.75

                        },
                        {
                            "Upper_Age_In_Years": 9.42,
                            "Fraction_Of_Adult_Dose": 0.875

                        }

                    ]

                },
                "Piperaquine": {
                    "Drug_Cmax": 30,
                    "Drug_Decay_T1": 0.17,
                    "Drug_Decay_T2": 41,
                    "Drug_Vd": 49,
                    "Drug_PKPD_C50": 5,
                    "Drug_Fulltreatment_Doses": 3,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 2.3,
                    "Drug_Gametocyte34_Killrate": 0.0,
                    "Drug_GametocyteM_Killrate": 0.0,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 4.6,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 0,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 0.83,
                            "Fraction_Of_Adult_Dose": 0.375

                        },
                        {
                            "Upper_Age_In_Years": 2.83,
                            "Fraction_Of_Adult_Dose": 0.5

                        },
                        {
                            "Upper_Age_In_Years": 5.25,
                            "Fraction_Of_Adult_Dose": 0.625

                        },
                        {
                            "Upper_Age_In_Years": 7.33,
                            "Fraction_Of_Adult_Dose": 0.75

                        },
                        {
                            "Upper_Age_In_Years": 9.42,
                            "Fraction_Of_Adult_Dose": 0.875

                        }

                    ]

                },
                "Primaquine": {
                    "Drug_Cmax": 75,
                    "Drug_Decay_T1": 0.36,
                    "Drug_Decay_T2": 0.36,
                    "Drug_Vd": 1,
                    "Drug_PKPD_C50": 15,
                    "Drug_Fulltreatment_Doses": 1,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 2.0,
                    "Drug_Gametocyte34_Killrate": 5.0,
                    "Drug_GametocyteM_Killrate": 50.0,
                    "Drug_Hepatocyte_Killrate": 0.1,
                    "Max_Drug_IRBC_Kill": 0.0,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 1,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 5,
                            "Fraction_Of_Adult_Dose": 0.17

                        },
                        {
                            "Upper_Age_In_Years": 9,
                            "Fraction_Of_Adult_Dose": 0.33

                        },
                        {
                            "Upper_Age_In_Years": 14,
                            "Fraction_Of_Adult_Dose": 0.67

                        }

                    ]

                },
                "Chloroquine": {
                    "Drug_Cmax": 150,
                    "Drug_Decay_T1": 8.9,
                    "Drug_Decay_T2": 244,
                    "Drug_Vd": 3.9,
                    "Drug_PKPD_C50": 150,
                    "Drug_Fulltreatment_Doses": 3,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 0.0,
                    "Drug_Gametocyte34_Killrate": 0.0,
                    "Drug_GametocyteM_Killrate": 0.0,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 4.8,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 1,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 5,
                            "Fraction_Of_Adult_Dose": 0.17

                        },
                        {
                            "Upper_Age_In_Years": 9,
                            "Fraction_Of_Adult_Dose": 0.33

                        },
                        {
                            "Upper_Age_In_Years": 14,
                            "Fraction_Of_Adult_Dose": 0.67

                        }

                    ]

                },
                "Artesunate": {
                    "Drug_Cmax": 200,
                    "Drug_Decay_T1": 0.12,
                    "Drug_Decay_T2": 0.12,
                    "Drug_Vd": 1,
                    "Drug_PKPD_C50": 0.03,
                    "Drug_Fulltreatment_Doses": 3,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 2.5,
                    "Drug_Gametocyte34_Killrate": 1.5,
                    "Drug_GametocyteM_Killrate": 0.7,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 4.2,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 1,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 2,
                            "Fraction_Of_Adult_Dose": 0.22

                        },
                        {
                            "Upper_Age_In_Years": 5,
                            "Fraction_Of_Adult_Dose": 0.44

                        }

                    ]

                },
                "Sulfadoxine": {
                    "Drug_Cmax": 105.8,
                    "Drug_Decay_T1": 8.55,
                    "Drug_Decay_T2": 8.55,
                    "Drug_Vd": 1,
                    "Drug_PKPD_C50": 0.2,
                    "Drug_Fulltreatment_Doses": 1,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 0.0,
                    "Drug_Gametocyte34_Killrate": 0.0,
                    "Drug_GametocyteM_Killrate": 0.0,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 0.506,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 1,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 2,
                            "Fraction_Of_Adult_Dose": 0.167

                        },
                        {
                            "Upper_Age_In_Years": 5,
                            "Fraction_Of_Adult_Dose": 0.33

                        }

                    ]

                },
                "Pyrimethamine": {
                    "Drug_Cmax": 354.1,
                    "Drug_Decay_T1": 5.411,
                    "Drug_Decay_T2": 5.411,
                    "Drug_Vd": 1,
                    "Drug_PKPD_C50": 2,
                    "Drug_Fulltreatment_Doses": 1,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 0.0,
                    "Drug_Gametocyte34_Killrate": 0.0,
                    "Drug_GametocyteM_Killrate": 0.0,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 0.6,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 1,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 2,
                            "Fraction_Of_Adult_Dose": 0.167

                        },
                        {
                            "Upper_Age_In_Years": 5,
                            "Fraction_Of_Adult_Dose": 0.33

                        }

                    ]

                },
                "Amodiaquine": {
                    "Drug_Cmax": 1185,
                    "Drug_Decay_T1": 0.12,
                    "Drug_Decay_T2": 6.25,
                    "Drug_Vd": 2.51,
                    "Drug_PKPD_C50": 35.5,
                    "Drug_Fulltreatment_Doses": 3,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 0.0,
                    "Drug_Gametocyte34_Killrate": 0.0,
                    "Drug_GametocyteM_Killrate": 0.0,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 0.67089,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 1,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 1,
                            "Fraction_Of_Adult_Dose": 0.22

                        },
                        {
                            "Upper_Age_In_Years": 5,
                            "Fraction_Of_Adult_Dose": 0.44

                        }

                    ]

                },
                "Amodiaquine_for_AS_combination": {
                    "Drug_Cmax": 537,
                    "Drug_Decay_T1": 0.12,
                    "Drug_Decay_T2": 6.25,
                    "Drug_Vd": 2.51,
                    "Drug_PKPD_C50": 80,
                    "Drug_Fulltreatment_Doses": 3,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 0.0,
                    "Drug_Gametocyte34_Killrate": 0.0,
                    "Drug_GametocyteM_Killrate": 0.0,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 0.7089,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 1,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 1,
                            "Fraction_Of_Adult_Dose": 0.22

                        },
                        {
                            "Upper_Age_In_Years": 5,
                            "Fraction_Of_Adult_Dose": 0.44

                        }

                    ]

                },
                "Abstract": {
                    "Drug_Cmax": 100,
                    "Drug_Decay_T1": 10,
                    "Drug_Decay_T2": 10,
                    "Drug_Vd": 1,
                    "Drug_PKPD_C50": 10,
                    "Drug_Fulltreatment_Doses": 3,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 0.0,
                    "Drug_Gametocyte34_Killrate": 0.0,
                    "Drug_GametocyteM_Killrate": 0.0,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 4.8,
                    "Drug_Adherence_Rate": 1.0,
                    "Bodyweight_Exponent": 1,
                    "Fractional_Dose_By_Upper_Age": [
                        {
                            "Upper_Age_In_Years": 3,
                            "Fraction_Of_Adult_Dose": 0.25

                        },
                        {
                            "Upper_Age_In_Years": 6,
                            "Fraction_Of_Adult_Dose": 0.5

                        },
                        {
                            "Upper_Age_In_Years": 10,
                            "Fraction_Of_Adult_Dose": 0.75

                        }

                    ]

                },
                "Vehicle": {
                    "Drug_Cmax": 10,
                    "Drug_Decay_T1": 1,
                    "Drug_Decay_T2": 1,
                    "Drug_Vd": 10,
                    "Drug_PKPD_C50": 5,
                    "Drug_Fulltreatment_Doses": 1,
                    "Drug_Dose_Interval": 1,
                    "Drug_Gametocyte02_Killrate": 0.0,
                    "Drug_Gametocyte34_Killrate": 0.0,
                    "Drug_GametocyteM_Killrate": 0.0,
                    "Drug_Hepatocyte_Killrate": 0.0,
                    "Max_Drug_IRBC_Kill": 0.0,
                    "Bodyweight_Exponent": 0,
                    "Fractional_Dose_By_Upper_Age": [

                    ]

                }

            }

        }

    @staticmethod
    def campaign() -> EMODCampaign:
        return EMODCampaign.load_from_dict({
            "Campaign_Name": "Empty campaign",
            "Events": [],
            "Use_Defaults": 1
        })

    @staticmethod
    def demographics() -> Dict:
        nodes = [(0, .3, 311), (0, .2, 511), (0, .1, 711), (.1, .3, 911),
                 (.1, .2, 1111), (.1, .1, 1311), (.2, .3, 1511), (.2, .2, 1711), (.2, .1, 1911)]

        return {"generic_scenarios_demographics.json": {
            "Metadata": {
                "DateCreated": "Mon Nov 4 07:00:00 2019",
                "Tool": "notepad",
                "Author": "YeChen",
                "IdReference": "0",
                "NodeCount": 9,
                "Resolution": 150
            },
            "Defaults": {
                "NodeAttributes": {
                    "Altitude": 0,
                    "Airport": 0,
                    "Region": 1,
                    "Seaport": 0,
                    "BirthRate": 0.0,
                    "InitialPopulation": 0
                },
                "IndividualAttributes": {
                    "AgeDistributionFlag": 1,
                    "AgeDistribution1": 0.0,
                    "AgeDistribution2": 43800.0,
                    "PrevalenceDistributionFlag": 0,
                    "PrevalenceDistribution1": 0.0,
                    "PrevalenceDistribution2": 0.0,
                    "SusceptibilityDistributionFlag": 0,
                    "SusceptibilityDistribution1": 1,
                    "SusceptibilityDistribution2": 0,
                    "RiskDistributionFlag": 0,
                    "RiskDistribution1": 1,
                    "RiskDistribution2": 0,
                    "MigrationHeterogeneityDistributionFlag": 2,
                    "MigrationHeterogeneityDistribution1": 15,
                    "MigrationHeterogeneityDistribution2": 5
                }
            },
            "Nodes": [
                {"NodeID": i + 1, "NodeAttributes": {"Longitude": n[0], "Latitude": n[1], "InitialPopulation": n[2]}}
                for i, n in enumerate(nodes)]
        }}
