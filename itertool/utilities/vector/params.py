# --------------------------------------------------------------
# Cohort model parameters
# --------------------------------------------------------------
from itertool.utilities.vector import larval_habitat

disease_params = {
    "Incubation_Period_Distribution": "CONSTANT_DISTRIBUTION",
    "Incubation_Period_Constant": 25,  ###

    "Infectious_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
    "Infectious_Period_Exponential": 180,
    "Base_Infectivity": 1,

    "Enable_Superinfection": 1,
    "Max_Individual_Infections": 5,
    "Infection_Updates_Per_Timestep": 1,  ###

    "Post_Infection_Acquisition_Multiplier": 1,
    "Post_Infection_Mortality_Multiplier": 1,
    "Post_Infection_Transmission_Multiplier": 1

}

cohort_params = {

    'Enable_Vector_Species_Report' : 0,
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

    # placeholder param values
    "Vector_Migration_Habitat_Modifier": 6.5,
    "Vector_Migration_Food_Modifier": 0,
    "Vector_Migration_Stay_Put_Modifier": 0.3,

    "Age_Dependent_Biting_Risk_Type": "SURFACE_AREA_DEPENDENT",
    "Newborn_Biting_Risk_Multiplier": 0.2,  # for LINEAR option (also picked up by InputEIR)
    "Human_Feeding_Mortality": 0.1,

    "Wolbachia_Infection_Modification": 1.0,
    "Wolbachia_Mortality_Modification": 1.0,
    "HEG_Homing_Rate": 0.0,
    "HEG_Fecundity_Limiting": 0.0,
    "HEG_Model": "OFF",

    "x_Temporary_Larval_Habitat": 1,
    "Vector_Species_Params": [],
    "Egg_Hatch_Density_Dependence": "NO_DENSITY_DEPENDENCE",
    "Enable_Temperature_Dependent_Egg_Hatching": 0,
    "Enable_Egg_Mortality": 0,
    "Enable_Drought_Egg_Hatch_Delay": 0,
    "Temperature_Dependent_Feeding_Cycle": "NO_TEMPERATURE_DEPENDENCE",
    "Insecticides": [],
    "Genome_Markers": []
}

params = cohort_params.copy()
params.update(disease_params)
params.update(larval_habitat.params)

# --------------------------------------------------------------
# Individual-mosquito model (rather than cohort-based model)
# --------------------------------------------------------------

individual_params = cohort_params.copy()
individual_params["Vector_Sampling_Type"] = "TRACK_ALL_VECTORS"

# --------------------------------------------------------------
# Using VECTOR_SIM as a vivax model
# --------------------------------------------------------------

vivax_semitropical_params = disease_params.copy()
vivax_semitropical_params.update({
    "Incubation_Period_Distribution": "CONSTANT_DISTRIBUTION",
    "Incubation_Period_Constant": 18,  # shorter time until gametocyte emergence

    "Infectious_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
    "Infectious_Period_Exponential": 240,  # Guadalcanal, East Timor
    "Base_Infectivity": 1,

    "Enable_Superinfection": 0,
    "Max_Individual_Infections": 1,
})

vivax_chesson_params = vivax_semitropical_params.copy()
vivax_chesson_params.update({
    "Infectious_Period_Exponential": 40,  # French Guiana
})
