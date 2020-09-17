from malaria.interventions.malaria_drugs import drug_params
from dtk.utils.Campaign.CampaignClass import *



def configure_adherent_drug(cb, cost: int=1, doses: list=None, dose_interval: int=1,
                            adherence_config: dict=None,
                            non_adherence_options: list=None,
                            non_adherence_distribution: list=None, max_dose_consideration_duration: int=40,
                            took_dose_event: str="Took_Dose"):

    """
        Add an intervention to create an adherent drug configuration dictionary
        to the campaign using the **AdherentDrug** class, an individual-level 
        intervention which extends the **AntimalarialDrug** class.
        
    Args:
        cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` 
        object for building, modifying, and writing campaign configuration files.
        cost: Unit cost per drug.
        doses: Lists of drugs for each dose. For example,
            ``[["DrugA", DrugB"], ["DrugB"], [], ["DrugB"]]``. The empty list, 
            ``[]``, indicates no drugs for that dose.
        dose_interval: Interval between doses of drugs, in days. Default is 1.
        adherence_config: Dictionary of parameters for defining waning effects
        of drugs, using classes, such as **WaningEffectCombo** and 
        **WaningEffectMapLinearAge**. If not defined, then the following default 
        is used:
            ``{
                "class": "WaningEffectMapLinearAge",
                "Initial_Effect": 1,
                "Durability_Map": {
                    "Times": [
                        0,
                        125
                    ],
                    "Values": [
                        1,
                        1
                    ]
                } 
            }``
        non_adherence_options: List of enums to define what happens when the user
        is not adherent. If not defined then NEXT_UPDATE is used. Enum values are:
        ["STOP", "NEXT_UPDATE", "NEXT_DOSAGE_TIME", "LOST_TAKE_NEXT"].
        non_adherence_distribution: Non adherence probability value(s) assigned to 
        the corresponding options in non_adherence_options. There must be one value
        in this list for each value in non_adherence_options. The sum of these 
        values must equal 1.0.
        max_dose_consideration_duration: Maximum number of days that an individual 
        will consider taking the doses of the drug.
        took_dose_event: Event that gets sent out every time a dose is taken.

    Returns:
    Configured **AdherentDrug** class dictionary
    """

    # built-in default so we can run this function by just putting in the config builder.
    if not adherence_config:
        adherence_config = WaningEffectMapLinearAge(Initial_Effect=1, Durability_Map={"Times": [0.0, 125.0],
                                                                                      "Values": [1.0, 1.0]})
        # the default is for person to take everything not matter what age


    # "SPA"
    if not doses:
        doses = [["Sulfadoxine", "Pyrimethamine",'Amodiaquine'],
                 ['Amodiaquine'],
                 ['Amodiaquine']]

    if not non_adherence_options:
        non_adherence_options = ["NEXT_UPDATE"]
    if not non_adherence_distribution:
        non_adherence_distribution = [1]

    already_added = []
    for dose in doses:
        for drug in dose:
            if drug not in already_added:
                cb.config["parameters"]["Malaria_Drug_Params"][drug] = drug_params[drug]
                already_added.append(drug)

    cb.set_param("PKPD_Model", "CONCENTRATION_VERSUS_TIME")
    cb.config["parameters"]["Malaria_Drug_Params"][drug] = drug_params[drug]
    adherent_drug = AdherentDrug(
        Cost_To_Consumer=cost,
        Doses=doses,
        Dose_Interval=dose_interval,
        Adherence_Config=adherence_config,
        Non_Adherence_Options=non_adherence_options,
        Non_Adherence_Distribution=non_adherence_distribution,
        Max_Dose_Consideration_Duration=max_dose_consideration_duration,
        Took_Dose_Event=took_dose_event)

    return adherent_drug

