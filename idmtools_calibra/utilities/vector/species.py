import warnings

param_block = {

    "Larval_Habitat_Types": {
        "TEMPORARY_RAINFALL": 8e8,
        "CONSTANT": 8e7
    },

    "Aquatic_Arrhenius_1": 84200000000,
    "Aquatic_Arrhenius_2": 8328,
    "Aquatic_Mortality_Rate": 0.1,
    "Name": "arabiensis",
    "Immature_Duration": 2,
    "Male_Life_Expectancy": 10,
    "Adult_Life_Expectancy": 20,
    "Days_Between_Feeds": 3,
    "Anthropophily": 0.85,  # species- and site-specific feeding parameters
    "Indoor_Feeding_Fraction": 0.5,
    "Egg_Batch_Size": 100,

    "Vector_Sugar_Feeding_Frequency": "VECTOR_SUGAR_FEEDING_NONE",

    "Acquire_Modifier": 0.2,
    # VECTOR_SIM uses a factor here for human-to-mosquito infectiousness, while MALARIA_SIM explicitly models gametocytes
    "Infected_Arrhenius_1": 117000000000,
    "Infected_Arrhenius_2": 8336,
    "Infected_Egg_Batch_Factor": 0.8,

    "Infectious_Human_Feed_Mortality_Factor": 1.5,
    "Nighttime_Feeding_Fraction": 1,
    "Transmission_Rate": 0.9  # Based on late-2013 calibration of PfPR vs EIR favoring 1.0 to 0.5
}

# An. arabiensis
arabiensis_param_block = param_block.copy()
mod_arabiensis_params = {
    "Name": "arabiensis",
    "Anthropophily": 0.65,
}
arabiensis_param_block.update(mod_arabiensis_params)

# An. funestus
funestus_param_block = param_block.copy()
mod_funestus_params = {
    "Name": "funestus",
    "Larval_Habitat_Types": {
        "WATER_VEGETATION": 2e7
    },
    "Indoor_Feeding_Fraction": 0.95,
    "Anthropophily": 0.65,
}
funestus_param_block.update(mod_funestus_params)

# extra funestus for Munyumbwe
munyumbwe_funestus_param_block = funestus_param_block.copy()

# An. gambiae
gambiae_param_block = param_block.copy()
gambiae_param_block["Indoor_Feeding_Fraction"] = 0.95
gambiae_param_block["Name"] = "gambiae"

# An. farauti
farauti_param_block = param_block.copy()
mod_farauti_params = {
    "Name": "farauti",
    "Larval_Habitat_Types": {
        "BRACKISH_SWAMP": 10000000000
    },
    # WARNING: Adult_Life_Expectancy unadjusted for Prashanth's 2018 corrections
    "Adult_Life_Expectancy": 5.9,
    "Days_Between_Feeds": 2,
    "Anthropophily": 0.97,
    "Indoor_Feeding_Fraction": 0.05,
    "Egg_Batch_Size": 70,
    "Acquire_Modifier": 0.05,
    "Transmission_Rate": 0.8
}
farauti_param_block.update(mod_farauti_params)

# Thailand_Anopheles_Survey_1968.pdf
# An. maculatus
# http://www.bioone.org/doi/full/10.3376/038.034.0108
# http://www.map.ox.ac.uk/explore/mosquito-malaria-vectors/bionomics/anopheles-maculatus/
# previous to 160722, maculatus block had
#    "Larval_Habitat_Types": {
#        "WATER_VEGETATION": 1e7
#    },
#    "Anthropophily": 0.3,
#    "Indoor_Feeding_Fraction": 0.4,
# on 160722, modified to Trung Trop Med Intl Health 2005 data from Ratanakiri
# on 161103, modified to mean values across sites from Trung Trop Med 2005 for anthropophily, indoor feeding fraction
# maculatus seasonal with rainfall (Durnez Malar J 2013), but also found in permanent/semipermanent bodies of water
# near forest camps or rice fields. For more info see https://wiki.idmod.org/display/EMOD/2016/10/21/SE+Asia+Larval+Habitats+Lit+Review
maculatus_param_block = param_block.copy()
mod_maculatus_params = {
    "Name": "maculatus",
    "Larval_Habitat_Types": {
        "TEMPORARY_RAINFALL": 1e7,
        "WATER_VEGETATION": 1e6,
        "CONSTANT": 1e6
    },
    # "Adult_Life_Expectancy": 7,
    "Days_Between_Feeds": 3,
    "Anthropophily": 0.19,
    "Indoor_Feeding_Fraction": 0.01,
    "Egg_Batch_Size": 70,
    "Acquire_Modifier": 0.2,
    "Transmission_Rate": 0.8
}
maculatus_param_block.update(mod_maculatus_params)

# An. minimus
# http://www.bioone.org/doi/abs/10.1603/033.046.0511
# http://www.map.ox.ac.uk/explore/mosquito-malaria-vectors/bionomics/anopheles-minimus/
# previous to 160722, minimus block had
#    "Larval_Habitat_Types": {
#        "WATER_VEGETATION": 1e7
#    },
#    "Anthropophily": 0.93,
#    "Indoor_Feeding_Fraction": 0.95,
# on 160722, modified to Trung Trop Med Intl Health 2005 data from Ratanakiri
# on 161103, modified to mean values across sites from Trung Trop Med 2005 for anthropophily, indoor feeding fraction
# minimus more present during drier periods after rainy season
# for more info see https://wiki.idmod.org/display/EMOD/2016/10/21/SE+Asia+Larval+Habitats+Lit+Review
minimus_param_block = param_block.copy()
mod_minimus_params = {
    "Name": "minimus",
    "Larval_Habitat_Types": {
        "WATER_VEGETATION": 1e7,  # update habitat type?
        "CONSTANT": 1e6
    },
    # "Adult_Life_Expectancy": 7,
    # "Anthropophily": 0.85,
    # "Acquire_Modifier": 0.2,
    "Adult_Life_Expectancy": 25,
    "Anthropophily": 0.5,
    "Acquire_Modifier": 0.8,
    "Days_Between_Feeds": 3,
    "Indoor_Feeding_Fraction": 0.6,
    "Egg_Batch_Size": 70,
    "Transmission_Rate": 0.8
}
minimus_param_block.update(mod_minimus_params)

# An. dirus
# Trung Trop Med Intl Health 2005
# Durnez Malar J 2013
# on 161103, modified to mean values across sites from Trung Trop Med 2005 for anthropophily, indoor feeding fraction
# dirus more abundant during rainy season but also some constant portion in forest
# dirus also has longer lifespan, see https://wiki.idmod.org/display/EMOD/2016/10/21/SE+Asia+Larval+Habitats+Lit+Review
dirus_param_block = param_block.copy()
mod_dirus_params = {
    "Name": "dirus",
    "Larval_Habitat_Types": {
        "TEMPORARY_RAINFALL": 1e7,
        "CONSTANT": 1e6
    },
    # "Adult_Life_Expectancy": 14,
    "Adult_Life_Expectancy": 30,
    "Days_Between_Feeds": 3,
    "Anthropophily": 0.5,
    # "Anthropophily": 0.96,
    "Indoor_Feeding_Fraction": 0.01,
    "Egg_Batch_Size": 70,
    "Acquire_Modifier": 0.2,
    "Transmission_Rate": 0.8
}
dirus_param_block.update(mod_dirus_params)

# An. darlingi
# Parasites and Vectors, Sinka et al 2010
darlingi_param_block = param_block.copy()
mod_darlingi_params = {
    "Name": "darlingi",
    "Larval_Habitat_Types": {
        "WATER_VEGETATION": 1e8,
        "CONSTANT": 1e6,
        "BRACKISH_SWAMP": 1e5
    },
    "Anthropophily": 0.96,
    "Indoor_Feeding_Fraction": 0.6,
}
darlingi_param_block.update(mod_darlingi_params)

# An. albimanus
# CDC Malar J 2016 review
albimanus_param_block = param_block.copy()
mod_albimanus_params = {
    "Name": "albimanus",
    "Larval_Habitat_Types": {  # seasonal with rainfall
        "TEMPORARY_RAINFALL": 1e7,
        "CONSTANT": 1e6
    },
    # WARNING: Adult_Life_Expectancy unadjusted for Prashanth's 2018 corrections
    "Adult_Life_Expectancy": 5,  # daily survival rate somewhere between 0.7 and 0.9
    "Days_Between_Feeds": 3,  # observed 2.6 to 5.2
    "Anthropophily": 0.5,
    "Indoor_Feeding_Fraction": 0.1,
    "Egg_Batch_Size": 70,
    "Acquire_Modifier": 0.2,  # ?
    "Transmission_Rate": 0.8  # ?
}
albimanus_param_block.update(mod_albimanus_params)

# An. aegypti
# Dengue
aegypti_param_block = {
    "Name": "aegypti",
    "Acquire_Modifier": 1,
    "Adult_Life_Expectancy": 14,
    "Anthropophily": 0.95,
    "Aquatic_Arrhenius_1": 9752291.727,
    "Aquatic_Arrhenius_2": 5525.492,
    "Aquatic_Mortality_Rate": 0.12,
    "Cycle_Arrhenius_1": 4.120591E10,
    "Cycle_Arrhenius_2": 7.740230E3,
    "Cycle_Arrhenius_Reduction_Factor": 0.58,
    "Days_Between_Feeds": 3,
    "Egg_Batch_Size": 70,
    "Egg_Survival_Rate": 0.99,
    "Larval_Habitat_Types": {
        "TEMPORARY_RAINFALL": 1.125e10
    },
    "Vector_Sugar_Feeding_Frequency": "VECTOR_SUGAR_FEEDING_NONE",
    "Immature_Duration": 2,
    "Male_Life_Expectancy": 10,
    "Indoor_Feeding_Fraction": 1,
    "Infected_Arrhenius_1": 4.784476E12,
    "Infected_Arrhenius_2": 9550,
    "Infected_Egg_Batch_Factor": 1,
    "Infectious_Human_Feed_Mortality_Factor": 1,
    "Nighttime_Feeding_Fraction": 0,
    "Transmission_Rate": 0.5
}

# Dictionary of params by species name
vector_params_by_species = {
    "arabiensis": arabiensis_param_block,
    "funestus": funestus_param_block,
    "munyumbwe_funestus": munyumbwe_funestus_param_block,
    "farauti": farauti_param_block,
    "gambiae": gambiae_param_block,
    "maculatus": maculatus_param_block,
    "minimus": minimus_param_block,
    "dirus": dirus_param_block,
    "darlingi": darlingi_param_block,
    "albimanus": albimanus_param_block,
    "aegypti": aegypti_param_block
}


def filter_species(simulation, species: list):
    """
    Removes species present in config.json that are NOT in the list that's passed in
    throws ValueError exception is the species you want left are not present in config

    Args:
        simulation: simulation
        species: list is vector names that you want present in your config.json

    Returns:
        Nothing.
    """
    unwanted_vectors = []
    for sp in simulation.task.config["parameters"]["Vector_Species_Params"]:
        if sp["Name"] not in species:
            unwanted_vectors.append(sp)
    for vector in species:
        found = False
        for sp in simulation.task.config["parameters"]["Vector_Species_Params"]:
            if sp["Name"] == vector:
                found = True
        if not found:
            raise ValueError(f"Species {vector} not found in the config.json file, please make sure you are "
                             f"filtering the file down to species present.\n")
    for unwanted in unwanted_vectors:
        simulation.task.config["parameters"]["Vector_Species_Params"].remove(unwanted)


def set_params_by_species(params: dict, ss: list, sim_type: str = "VECTOR_SIM"):
    """

    Args:
        params: params to which you want to append the species
        ss: list of species
        sim_type: sim type you're setting up for

    Returns:
        nothing
    """
    pp = []
    for s in ss:
        pp.append(vector_params_by_species[s].copy())
        if sim_type == "MALARIA_SIM":
            pp[-1]["Acquire_Modifier"] = 0.8  # gametocyte success modeled explicitly

    vector_species_params = {
        "Vector_Species_Params": pp
    }

    params.update(vector_species_params)


def set_species(simulation, species_list: list, overwrite: bool = True):
    """
        Adds species from the list to the config.json in your simulation,
        By default, overwrites whatever species are in config now.
    Args:
        simulation: simulation
        species_list: list of species to add to the simulation
        overwrite: when true - overwrite whatever species are present already with the species in the list
            when false - add the species in the list to the species already present, if species already
            in config, it is left as-is.
            Default: True

    Returns:
        nothing
    """
    pp = [] if overwrite else simulation.task.config['parameters']["Vector_Species_Params"]
    sim_type = simulation.task.config['parameters']["Simulation_Type"]
    for s in species_list:
        if overwrite or not get_species_param_block(simulation, s):
            current_species = vector_params_by_species[s].copy()
            if sim_type == "MALARIA_SIM":
                current_species["Acquire_Modifier"] = 0.8  # gametocyte success modeled explicitly
            pp.append(current_species)

    simulation.task.config["parameters"]['Vector_Species_Params'] = pp


def set_species_param(simulation, species, parameter, value):
    block = get_species_param_block(simulation, species)
    if block is not None:
        simulation.task.config["parameters"]['Vector_Species_Params'][block][parameter] = value
        return {'.'.join([species, parameter]): value}
    else:
        return None


def get_species_names(simulation):
    """
        Returns the list of names of vector species found in the config.
    Args:
        simulation:

    Returns:
        List of all the species present in the config.json
    """
    species = []
    for species_params in simulation.task.config["parameters"]["Vector_Species_Params"]:
        species.append(species_params["Name"])

    return species


def get_species_param_block(simulation, species):
    species_available = []
    for block, vector_species in enumerate(simulation.task.config["parameters"]['Vector_Species_Params']):
        if vector_species["Name"] == species:
            return block
        else:
            species_available.append(vector_species["Name"])
    if not species_available:
        raise Exception("Vector_Species_Param list is empty. No species present. "
                        "Please add species via set_species() \n")
    else:
        raise Exception(f"Species {species} not found in Vector_Species_Params. \n")


def update_species_param(simulation, species, parameter, value, overwrite=True):
    """ Update a 'Vector_Species_Param' variable in a config file; return a length-one dict with a numeric value.

    Args:
        simulation: Simulation
        species: (string) vector species whose parameter will be updated.
        parameter: (string) 'Vector_Species_Param' variable to be updated.
        value: (float, dict) New value for 'parameter'.
            Note that the function only returns the first key-value pair in 'value'.
        overwrite: (logical) Relevant only if 'value' is a dict.
            If True, will replace the entire original parameter with whatever is passed in 'value'.
            If False, will change only the elements specified in 'value'.

    Returns: 
        a dict whose key traces the config parameters from 'species' onward (including the key of 'value' if 'value'
        is a dict) and whose value is equal to the updated config value.
    """
    block = get_species_param_block(simulation, species)
    if isinstance(value, dict):
        if not overwrite:
            # update values in 'parameter' without deleting what's already there.
            # i.e: update the "TEMPORARY RAINFALL" value in a "Larval_Habitat_Types" object
            # without eliminating the "CONSTANT" value
            for k, v in value.items():
                simulation.task.config['parameters']['Vector_Species_Params'][block][parameter][k] = v
        else:
            simulation.task.config['parameters']['Vector_Species_Params'][block][parameter] = value

        if len(value) > 1:
            warnings.warn("value is a dict of length>1, returning only the first value.")

        return {'.'.join([species, key]): val for key, val in value.items()}
    else:
        simulation.task.config['parameters']['Vector_Species_Params'][block][parameter] = value
        return {'.'.join([species, parameter]): value}


def get_species_param(simulation, species, parameter):
    block = get_species_param_block(simulation, species)
    try:
        return simulation.task.config.parameters.Vector_Species_Params[block][parameter]
    except:
        print('Unable to get parameter %s for species %s' % (parameter, species))
        return None


def scale_all_habitats(simulation, scale):
    for species_params in simulation.task.config.parameters.Vector_Species_Params:
        habitats = species_params["Larval_Habitat_Types"]
        scaled_habitats = {h: scale * v for (h, v) in habitats.items()}
        species_params["Larval_Habitat_Types"] = scaled_habitats


def set_larval_habitat(simulation, habitats):
    """
    Set vector species and habitat parameters of config argument and return

    Args::

        simulation: Simulation
        habitats: habitats

    Example::

        habitats = {"arabiensis": {"TEMPORARY_RAINFALL": 1.7e9, "CONSTANT": 1e7}}
    """
    for species, habitat in habitats.items():
        set_species_param(simulation, species, 'Larval_Habitat_Types', habitat)


def set_species_genes(simulation, genes):
    """
    Set vector species and gene parameters of config argument and return

    Example::

        genes = {"arabiensis": [
                            {
                                "Alleles": {
                                            "a0": 0.6,
                                            "a1": 0.4,
                                            "a2": 0.0,
                                        },
                                "Mutations": {
                                            "a1:a2" : 0.01,
                                            "a0:a1" : 0.05
                                        }
                            },
                            {
                                "Alleles": {
                                            "b0": 0.6,
                                            "b1": 0.4
                                        },
                                "Mutations": {}
                            }
                            ]
    """

    for species, gene in genes.items():
        set_species_param(simulation, species, 'Genes', gene)


def set_species_trait_modifiers(simulation, traits):
    """
        Set vector species and gene parameters of config argument and return

        Example::

            traits = {"arabiensis": [{
                                        "Allele_Combinations": [
                                                                ["X","X"],
                                                                ["a0","a1"]
                                                            ],
                                        "Trait_Modifiers": {
                                                                "FECUNDITY": 3,
                                                                "INFECTED_BY_HUMAN": 0.5
                                                            }
                                    },
                                    {
                                        "Allele_Combinations": [
                                                                ["X", "X"],
                                                                ["a1", "a1"]
                                                            ],
                                        "Trait_Modifiers": {
                                                                "FECUNDITY": 6,
                                                                "INFECTED_BY_HUMAN": 0.0
                                                            }
                                    }
                                   ]
        """

    for species, trait in traits.items():
        set_species_param(simulation, species, 'Gene_To_Trait_Modifiers', trait)


def set_species_drivers(simulation, drivers):
    """
        Set vector species and gene parameters of config argument and return.

        Example::

            drivers = {"arabiensis": [
                                    {
                                        "Alleles_Driven": [
                                            {
                                                "Allele_To_Copy": "a1",
                                                "Allele_To_Replace": "a0",
                                                "Copy_To_Likelihood": {
                                                    "a0": 0.1,
                                                    "a1": 0.9
                                                }
                                            },
                                            {
                                                "Allele_To_Copy": "b1",
                                                "Allele_To_Replace": "b0",
                                                "Copy_To_Likelihood": {
                                                    "b0": 0.1,
                                                    "b1": 0.9
                                                }
                                            }
                                        ],
                                        "Driver_Type": "INTEGRAL_AUTONOMOUS",
                                        "Driving_Allele": "a1"
                                    },
                                   ]
        """

    for species, driver in drivers.items():
        set_species_param(simulation, species, 'Drivers', driver)
