# from dtk.utils.Campaign.CampaignClass import *


def drug_configs_from_code(simulation, drug_code: str = None):
    """
        Add a drug config to the simulation configuration based on its code and add the corresponding AntimalarialDrug
        intervention to the return dictionary. The drug_code needs to be one identified in the ``drug_cfg`` dictionary.

    For example passing the ``MDA_ALP`` drug code, will add the drugs config for Artemether, Lumefantrine, Primaquine
    to the configuration file and will return a dictionary containing a Full Treatment course for those 3 drugs.

    Args:
        cb:  The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` that will receive the drug configuration
        drug_code:  Code of the drug to add
        # drug_ineligibility_duration: used as a flag, if anything is present, we add ["DrugStatus:RecentDrug"]
            as Disqualifying_Properties

    Returns:
        A dictionary containing the parameters for an intervention using the given drug

    """
    if not drug_code:
        raise Exception("Please pass in a drug_code.\n"
                        "Available drug codes:\n"
                        "\"ALP\": Artemether, Lumefantrine, Primaquine.\n"
                        "\"AL\": Artemether, Lumefantrine. \n"
                        "\"ASAQ\": Artesunate, Amodiaquine.\n"
                        "\"DP\": DHA, Piperaquine.\n"
                        "\"DPP\": DHA, Piperaquine, Primaquine.\n"
                        "\"PPQ\": Piperaquine.\n"
                        "\"DHA_PQ\": DHA, Primaquine.\n"
                        "\"DHA\": DHA.\n"
                        "\"PMQ\": Primaquine.\n"
                        "\"DA\": DHA, Abstract.\n"
                        "\"CQ\": Chloroquine.\n"
                        "\"SP\": Sulfadoxine, Pyrimethamine.\n"
                        "\"SPP\": Sulfadoxine, Pyrimethamine, Primaquine.\n"
                        "\"SPA\": Sulfadoxine, Pyrimethamine, Amodiaquine.\n"
                        "\"Vehicle\": Vehicle.\n")
    drug_array = drug_cfg[drug_code]

    simulation.task.set_parameter("PKPD_Model", "CONCENTRATION_VERSUS_TIME")

    drug_configs = []
    for drug in drug_array:
        simulation.task.config["parameters"]["Malaria_Drug_Params"][drug] = drug_params[drug]
        drug_intervention = {"Drug_Type": drug, "Cost_To_Consumer": 1.5, "class": "AntimalarialDrug"}
        drug_configs.append(drug_intervention)
    return drug_configs


def set_drug_param(cb, drugname: str = None, parameter: str = None, value: any = None):
    """
    Set a drug parameter in the config builder passed.
    Args:
        cb:  cb: :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` containing the simulation configuration
        drugname: The drug that has a parameter to set
        parameter: The parameter to set
        value: The new value to set

    Returns:
        configured drug param value to modify drug
    """
    if not drugname or not parameter or not value:
        raise Exception("Please pass in all: drugname, parameter, and value.\n")
    cb.config['parameters']['Malaria_Drug_Params'][drugname][parameter] = value
    return {'.'.join([drugname, parameter]): value}


def get_drug_param(cb, drugname: str = None, parameter: str = None):
    """
        Get a parameter for a given drug
    Args:
        cb:  cb: :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` containing the simulation configuration
        drugname: The drug that has a parameter to set
        parameter: The parameter to set

    Returns:
        Value of the drug parameter
    """
    if not drugname or not parameter:
        raise Exception("Please pass in all: drugname, and parameter.\n")

    try:
        return cb.config['parameters']['Malaria_Drug_Params'][drugname][parameter]
    except:
        print('Unable to get parameter %s for drug %s' % (parameter, drugname))
        return None


# Definitions of drug blocks
drug_params = {

    # Parameterized according to simple model and 50 kg person
    "Artemether": {
        # Drug PkPd
        "Drug_Cmax": 114,  # dose/(Vc+Vp)*0.5
        "Drug_Decay_T1": 0.12,
        "Drug_Decay_T2": 0.12,
        "Drug_Vd": 1,
        "Drug_PKPD_C50": 0.6,  # based on 2 nM IC50

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 6,
        "Drug_Dose_Interval": 0.5,

        # These are daily parasite killing rates for:
        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 2.5,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 1.5,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.7,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 8.9,  # ... asexual parasites
        # "Max_Drug_IRBC_Kill":         2.9,   # ... asexual parasites, drug resistant

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 1,
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 3, "Fraction_Of_Adult_Dose": 0.25},
                                         {"Upper_Age_In_Years": 6, "Fraction_Of_Adult_Dose": 0.5},
                                         {"Upper_Age_In_Years": 10, "Fraction_Of_Adult_Dose": 0.75}]
    },

    "Lumefantrine": {
        # Drug PkPd
        "Drug_Cmax": 1017,
        "Drug_Decay_T1": 1.3,
        "Drug_Decay_T2": 2.0,
        "Drug_Vd": 1.2,
        "Drug_PKPD_C50": 280,

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 6,
        "Drug_Dose_Interval": 0.5,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 2.4,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 0.0,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.0,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 4.8,  # ... asexual parasites

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 0.35,
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 3, "Fraction_Of_Adult_Dose": 0.25},
                                         {"Upper_Age_In_Years": 6, "Fraction_Of_Adult_Dose": 0.5},
                                         {"Upper_Age_In_Years": 10, "Fraction_Of_Adult_Dose": 0.75}]
    },

    "DHA": {
        # Drug PkPd
        "Drug_Cmax": 200,
        "Drug_Decay_T1": 0.12,
        "Drug_Decay_T2": 0.12,
        "Drug_Vd": 1,
        "Drug_PKPD_C50": 0.6,

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 3,
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 2.5,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 1.5,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.7,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 9.2,  # ... asexual parasites
        # "Max_Drug_IRBC_Kill":         3.2,   # ... asexual parasites, drug resistant

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 1,
        # current sigma-tau dosing
        # "Fractional_Dose_By_Upper_Age":
        # [{"Upper_Age_In_Years": 2, "Fraction_Of_Adult_Dose": 0.17},
        # {"Upper_Age_In_Years": 6, "Fraction_Of_Adult_Dose": 0.33},
        # {"Upper_Age_In_Years": 11, "Fraction_Of_Adult_Dose": 0.67}]
        # dosing recommended by Tarning CPT 2012
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 0.83, "Fraction_Of_Adult_Dose": 0.375},
                                         {"Upper_Age_In_Years": 2.83, "Fraction_Of_Adult_Dose": 0.5},
                                         {"Upper_Age_In_Years": 5.25, "Fraction_Of_Adult_Dose": 0.625},
                                         {"Upper_Age_In_Years": 7.33, "Fraction_Of_Adult_Dose": 0.75},
                                         {"Upper_Age_In_Years": 9.42, "Fraction_Of_Adult_Dose": 0.875}]
    },

    "Piperaquine": {
        # Drug PkPd
        "Drug_Cmax": 30,  # 10.4,
        "Drug_Decay_T1": 0.17,
        "Drug_Decay_T2": 41,
        "Drug_Vd": 49,
        "Drug_PKPD_C50": 5,

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 3,
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 2.3,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 0.0,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.0,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 4.6,  # ... asexual parasites

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 0,
        # current sigma-tau dosing
        # "Fractional_Dose_By_Upper_Age":
        # [{"Upper_Age_In_Years": 2, "Fraction_Of_Adult_Dose": 0.17},
        # {"Upper_Age_In_Years": 6, "Fraction_Of_Adult_Dose": 0.33},
        # {"Upper_Age_In_Years": 11, "Fraction_Of_Adult_Dose": 0.67}]
        # dosing recommended by Tarning CPT 2012
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 0.83, "Fraction_Of_Adult_Dose": 0.375},
                                         {"Upper_Age_In_Years": 2.83, "Fraction_Of_Adult_Dose": 0.5},
                                         {"Upper_Age_In_Years": 5.25, "Fraction_Of_Adult_Dose": 0.625},
                                         {"Upper_Age_In_Years": 7.33, "Fraction_Of_Adult_Dose": 0.75},
                                         {"Upper_Age_In_Years": 9.42, "Fraction_Of_Adult_Dose": 0.875}]
    },

    "Primaquine": {
        # Drug PkPd
        "Drug_Cmax": 75,
        # 19.5 for 0.065 mg.kg, 30 for 0.1mg/kg, 75 for 0.25 mg/kg, 120 for 0.4 mg/kg, 225 for 0.75 mg/kg
        "Drug_Decay_T1": 0.36,
        "Drug_Decay_T2": 0.36,
        "Drug_Vd": 1,
        "Drug_PKPD_C50": 15,  # 183,

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 1,  # cmax and dosing for single 45 mg (adult) dose
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 2.0,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 5.0,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 50.0,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.1,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 0.0,  # ... asexual parasites

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 1,
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 5, "Fraction_Of_Adult_Dose": 0.17},
                                         {"Upper_Age_In_Years": 9, "Fraction_Of_Adult_Dose": 0.33},
                                         {"Upper_Age_In_Years": 14, "Fraction_Of_Adult_Dose": 0.67}]
    },
    "Chloroquine": {
        # Drug PkPd
        "Drug_Cmax": 150,
        "Drug_Decay_T1": 8.9,
        "Drug_Decay_T2": 244,
        "Drug_Vd": 3.9,
        "Drug_PKPD_C50": 150,

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 3,
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 0.0,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 0.0,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.0,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 4.8,  # ... asexual parasites

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 1,
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 5, "Fraction_Of_Adult_Dose": 0.17},
                                         {"Upper_Age_In_Years": 9, "Fraction_Of_Adult_Dose": 0.33},
                                         {"Upper_Age_In_Years": 14, "Fraction_Of_Adult_Dose": 0.67}]
    },

    "Artesunate": {
        # Drug PkPd
        "Drug_Cmax": 200,  # mu g
        "Drug_Decay_T1": 0.12,  # Gerardin et al (2015)
        "Drug_Decay_T2": 0.12,
        "Drug_Vd": 1,
        "Drug_PKPD_C50": 0.03,  # 0.03 mu g - Sanz et al 2012

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 3,
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 2.5,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 1.5,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.7,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 4.2,  # Gerardin et al (2015)# 8.5,  # ... asexual parasites; Sanz et al 2012

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 1,
        #
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 2, "Fraction_Of_Adult_Dose": 0.22},
                                         {"Upper_Age_In_Years": 5, "Fraction_Of_Adult_Dose": 0.44}]
    },

    "Sulfadoxine": {
        # Drug PkPd
        "Drug_Cmax": 105.8,  # ... Bell et al. 2010
        "Drug_Decay_T1": 8.55,
        "Drug_Decay_T2": 8.55,  # Barnes et al
        "Drug_Vd": 1,
        "Drug_PKPD_C50": 0.2,  # 0.6855,

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 1,
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 0.0,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 0.0,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.0,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 0.506,  # 0.533864,  # ... asexual parasites

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 1,
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 2, "Fraction_Of_Adult_Dose": 0.167},
                                         {"Upper_Age_In_Years": 5, "Fraction_Of_Adult_Dose": 0.33}]
    },

    "Pyrimethamine": {
        # Drug PkPd
        "Drug_Cmax": 354.1,  # ... Bell et al. 2006
        "Drug_Decay_T1": 5.411,
        "Drug_Decay_T2": 5.411,
        "Drug_Vd": 1,
        "Drug_PKPD_C50": 2, # 0.03,
        # ... Pertersen Eskild 1987

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 1,
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 0.0,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 0.0,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.0,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 0.6,  # 0.1,  #

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd ... Zongo et al. 2015
        "Bodyweight_Exponent": 1,
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 2, "Fraction_Of_Adult_Dose": 0.167},
                                         {"Upper_Age_In_Years": 5, "Fraction_Of_Adult_Dose": 0.33}]
    },

    "Amodiaquine": {
        # Drug PkPd
        "Drug_Cmax": 1185,  # 1185 ng/ml ... Adjei et al. 2008
        "Drug_Decay_T1": 0.12,
        "Drug_Decay_T2": 6.25,
        "Drug_Vd": 2.51,
        "Drug_PKPD_C50": 35.5, 

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 3,
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 0.0,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 0.0,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.0,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 0.67089, # 0.7089,

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 1,
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 1, "Fraction_Of_Adult_Dose": 0.22},
                                         {"Upper_Age_In_Years": 5, "Fraction_Of_Adult_Dose": 0.44}]
    },


    "Amodiaquine_for_AS_combination": {
        # Drug PkPd
        "Drug_Cmax": 537,
        "Drug_Decay_T1": 0.12,
        "Drug_Decay_T2": 6.25,
        "Drug_Vd": 2.51,
        "Drug_PKPD_C50": 80,

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 3,
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 0.0,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 0.0,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.0,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 0.7089,  #

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 1,
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 1, "Fraction_Of_Adult_Dose": 0.22},
                                         {"Upper_Age_In_Years": 5, "Fraction_Of_Adult_Dose": 0.44}]
    },

    "Abstract": {  # abstracted drug
        # Drug PkPd
        "Drug_Cmax": 100,
        "Drug_Decay_T1": 10,
        "Drug_Decay_T2": 10,
        "Drug_Vd": 1,
        "Drug_PKPD_C50": 10,

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 3,
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 0.0,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 0.0,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.0,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 4.8,  # ... asexual parasites

        # Adherence rate for subsequent doses
        "Drug_Adherence_Rate": 1.0,

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 1,
        "Fractional_Dose_By_Upper_Age": [{"Upper_Age_In_Years": 3, "Fraction_Of_Adult_Dose": 0.25},
                                         {"Upper_Age_In_Years": 6, "Fraction_Of_Adult_Dose": 0.5},
                                         {"Upper_Age_In_Years": 10, "Fraction_Of_Adult_Dose": 0.75}]
    },

    "Vehicle": {  # empty drug
        # Drug PkPd
        "Drug_Cmax": 10,
        "Drug_Decay_T1": 1,
        "Drug_Decay_T2": 1,
        "Drug_Vd": 10,
        "Drug_PKPD_C50": 5,

        # Treatment regimen
        "Drug_Fulltreatment_Doses": 1,
        "Drug_Dose_Interval": 1,

        # These are daily parasite killing rates for:
        "Drug_Gametocyte02_Killrate": 0.0,  # ... gametocyte - early stages
        "Drug_Gametocyte34_Killrate": 0.0,  # ...            - late stages
        "Drug_GametocyteM_Killrate": 0.0,  # ...            - mature
        "Drug_Hepatocyte_Killrate": 0.0,  # ... hepatocytes
        "Max_Drug_IRBC_Kill": 0.0,  # ... asexual parasites

        # Cmax modifications due to age-based dosing and bodyweight-dependence Vd
        "Bodyweight_Exponent": 0,
        "Fractional_Dose_By_Upper_Age": []
    }
}

# Different configurations of regimens and drugs
drug_cfg = {
    "ALP": ["Artemether", "Lumefantrine", "Primaquine"],
    "AL": ["Artemether", "Lumefantrine"],
    "ASA": ["Artesunate", "Amodiaquine"],
    "DP": ["DHA", "Piperaquine"],
    "DPP": ["DHA", "Piperaquine", "Primaquine"],
    "PPQ": ["Piperaquine"],
    "DHA_PQ": ["DHA", "Primaquine"],
    "DHA": ["DHA"],
    "PMQ": ["Primaquine"],
    "DA": ["DHA", "Abstract"],
    "CQ": ["Chloroquine"],
    "SP": ["Sulfadoxine", "Pyrimethamine"],
    "SPP": ["Sulfadoxine", "Pyrimethamine", 'Primaquine'],
    "SPA": ["Sulfadoxine", "Pyrimethamine", 'Amodiaquine'],
    "Vehicle": ["Vehicle"]
}