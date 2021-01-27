import json
import copy
import pathlib
from functools import partial

import numpy as np
from emodpy import emod_task
from emodpy.bamboo import get_model_files
from emodpy.emod_task import EMODTask
from emodpy.reporters.custom import Report_TBHIV_ByAge
from emodpy.utils import EradicationBambooBuilds

from idmtools.assets import Asset, AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
    RequirementsToAssetCollection

import params
import set_config
import manifest

from analyzer_dev.CalibSites import SouthAfricaCalibSite

from idmtools_calibra import calib_manager
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.algorithms.optim_tool import OptimTool

from tb.add_tb_drug_type import add_tb_drug_type, add_tb_drug

sites = [SouthAfricaCalibSite()]  # yeah its plural

initial_pop = 10000
verbose = False
calibration_on = True


# sweep Run_Number
def update_sim_random_seed(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def cpr_sens_spec(camp, sensCRP, specCRP):
    import emodpy_tbhiv.interventions.active_diagnostic as ad
    camp.add(ad.ActiveDiagnostic(camp, ['HIVTestedNegative'], sensCRP, specCRP, pos_event='CRPPosHIVNeg',
                                 start_day=params.intervention_day))
    camp.add(ad.ActiveDiagnostic(camp, ['HIVTestedPositive'], sensCRP, specCRP, pos_event='CRPPosHIVPos',
                                 start_day=params.intervention_day))
    return camp


# sweep drugs
def add_drugs(simulation, resist_pro):
    return add_drugs_calib(simulation.task, resist_pro)


def add_drugs_calib(task, resist_pro):
    add_tb_drug_type(task, 'DOTSHQ', 180.0, 0.8, 0.03, resist_pro, 0.10, 0.02, mdr_cure_proportion=0.1)
    add_tb_drug_type(task, 'DOTSLQ', 180.0, 0.5, 0.03, resist_pro, 0.10, 0.02, mdr_cure_proportion=0.1)
    return {'ResistancePro': resist_pro}


def print_params():
    """
    Just a useful convenience function for the user.
    """
    # Display exp_name and nSims
    # TBD: Just loop through them
    print("exp_name: ", params.exp_name)
    print("nSims: ", params.nSims)


def set_tbhiv_drup_params_from_schema(config, manifest):
    import emod_api.config.default_from_schema_no_validation as dfs

    tbhivdp_map = {}

    for drug_key in config.parameters.TBHIV_Drug_Types:
        tbhivdp = dfs.schema_to_config_subnode(manifest.schema_file, ["config", "TBHIV_SIM", "TBHIV_Drug_Params",
                                                                      "<tb_drug_name_goes_here>"])
        t2 = tbhivdp.copy()
        for k, v in tbhivdp.parameters.items():
            t2.parameters[k] = v
        t2.parameters['Enable_Coinfection'] = 1
        t2.parameters.finalize()
        tbhivdp_map[drug_key] = t2.parameters

    config.parameters.TBHIV_Drug_Params = tbhivdp_map


# not needed, but if you want to read drug params from file, this is the way to do it
def set_tbhiv_drup_params_from_file(config, my_manifest):
    import emod_api.config.default_from_schema_no_validation as dfs

    tbhivdp_map = {}
    with open("drug.json") as f:
        data = json.load(f)
        drugs_key = list(data['TBHIV_Drug_Params'])
        drugs = data['TBHIV_Drug_Params']
        for drug_key, drug_value in drugs.items():
            tbhivdp = dfs.schema_to_config_subnode(my_manifest.schema_file, ["config", "TBHIV_SIM", "TBHIV_Drug_Params",
                                                                          "<tb_drug_name_goes_here>"])
            for k, v in drug_value.items():
                setattr(tbhivdp.parameters, k, v)
            tbhivdp.parameters.finalize()
            tbhivdp_map[drug_key] = tbhivdp.parameters

    config.parameters.TBHIV_Drug_Params = tbhivdp_map


def set_param_fn(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config = set_config.set_config(config)

    config.parameters.x_Other_Mortality = 0.34
    config.parameters.x_Birth = 1.43

    config.parameters.TB_MDR_Fitness_Multiplier = 1.0  # no fitness cost worst case

    config.parameters.Simulation_Duration = params.burn_initial + params.burn_predots + params.To_end_from_DOTS
    config.parameters.TB_Smear_Negative_Infectivity_Multiplier = 0.34604
    config.parameters.TB_Presymptomatic_Rate = 0.01165
    config.parameters.TB_Active_Presymptomatic_Infectivity_Multiplier = 0.34604 * 0.3318

    # config.parameters.Base_Population_Scale_Factor =  1000  # not in schema
    config.parameters.TB_Slow_Progressor_Rate = 0.007 / 365.0
    # config.parameters.Serialization_Times = [ 365 ]
    config.parameters.pop("Serialized_Population_Filenames")

    set_tbhiv_drup_params_from_schema(config, manifest)
    return config


def build_camp(probability_per_step=0, care=None):
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as camp
    import emod_api.interventions.outbreak as ob
    import emodpy_tbhiv.interventions.hiv_seeding as hs
    import emodpy_tbhiv.interventions.cd4diag as cd4
    import emodpy_tbhiv.interventions.hsb as hsb
    import emodpy_tbhiv.interventions.art as art
    import emodpy_tbhiv.interventions.diag_treat_neg as dtn
    import emodpy_tbhiv.interventions.tbhiv_treat as treat
    import emodpy_tbhiv.interventions.ramp_dtn as ramp
    import emodpy_tbhiv.interventions.resist_diag as rd
    import emodpy_tbhiv.interventions.hiv_diag as hd

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file
    # print( f"Telling emod-api to use {manifest.schema_file} as schema." )

    # importation pressure
    seed = ob.seed_by_coverage(40, camp, 0.5)
    camp.add(seed, first=True)

    # initial TB outbreak
    camp.add(hs.HIV(camp, 0.05, 'TB'))

    # HIV incidence, care seeking, and treatment by guidelines
    camp.add(hd.HIVDiagnostic(camp, ['HappyBirthday'], start_day=params.art_start, treatment_fraction=0.23,
                              property_restrictions_list=['QualityOfCare:High'], event_name='HIV Simple Diagnostic'))
    camp.add(hd.HIVDiagnostic(camp, ['HappyBirthday'], start_day=params.art_start, treatment_fraction=0.13,
                              property_restrictions_list=['QualityOfCare:Low'], event_name='HIV Simple Diagnostic'))
    camp.add(cd4.CD4Diag(camp, ['HIVTestedPositive'], start_day=params.art_start, event_name='CD4 Diagnostic'))
    camp.add(hs.HIV(camp, params.hiv_epidemic_start - 1.0, start_day=params.hiv_epidemic_start))
    camp.add(hsb.HSB(camp, ['Below200'], 'Below200', params.seek_200, start_day=params.art_start, duration=-1))
    camp.add(hsb.HSB(camp, ['Below350'], 'Below350', params.seek_350_500, start_day=params.art_start + 3.0 * 365.0,
                     duration=-1))
    camp.add(hsb.HSB(camp, ['Below500'], 'Below500', params.seek_350_500, start_day=params.art_start + 6.0 * 365.0,
                     duration=-1))
    camp.add(art.ART(camp, ['Below200', 'Below350', 'Below500'], start_day=params.art_start))

    # set some drug properties
    camp.add(
        hsb.HSB(camp, ['TBActivation', 'TBFailedDrugRegimen', 'TBTestDefault', 'TBTestNegative', 'TBMDRTestDefault'],
                'TBTestDOTSLow', params.low_seek, start_day=params.burn_initial,
                property_restrictions_list=['QualityOfCare:Low']))
    camp.add(
        hsb.HSB(camp, ['TBActivation', 'TBFailedDrugRegimen', 'TBTestDefault', 'TBTestNegative', 'TBMDRTestDefault'],
                'TBTestDOTSHigh', params.high_seek, start_day=params.burn_initial,
                property_restrictions_list=['QualityOfCare:High']))

    camp.add(
        dtn.DiagnosticTreatNeg(camp, ['TBTestDOTSHigh'], params.sens_smear_pos_pre_GH, params.sens_smear_neg_pre_GH,
                               treatment_fraction=0.8, start_day=params.burn_initial, duration=params.burn_predots,
                               property_restrictions_list=['QualityOfCare:High']))
    camp.add(dtn.DiagnosticTreatNeg(camp, ['TBTestDOTSLow'], params.sens_smear_pos_pre_GL, params.sens_smear_neg_pre_GL,
                                    treatment_fraction=0.8, start_day=params.burn_initial, duration=params.burn_predots,
                                    property_restrictions_list=['QualityOfCare:Low']))

    camp.add(treat.TBHIVDrugTreatment(camp, ['TBTestPositive'], 'PreDOTSLow', start_day=params.burn_initial,
                                      duration=params.burn_predots, latent_multiplier=0,
                                      property_restrictions_list=['QualityOfCare:Low']))

    camp.add(treat.TBHIVDrugTreatment(camp, ['TBTestPositive'], 'PreDOTSHigh', start_day=params.burn_initial,
                                      duration=params.burn_predots, latent_multiplier=0,
                                      property_restrictions_list=['QualityOfCare:High']))

    camp.add(
        dtn.DiagnosticTreatNeg(camp, ['TBTestDOTSHigh'], params.sens_smear_pos_pre_GH, params.sens_smear_neg_pre_GH,
                               treatment_fraction=0.8, start_day=params.dots_start,
                               duration=params.genexpert_introduction - params.dots_start,
                               property_restrictions_list=['QualityOfCare:High']))
    camp.add(dtn.DiagnosticTreatNeg(camp, ['TBTestDOTSLow'], params.sens_smear_pos_pre_GL, params.sens_smear_neg_pre_GL,
                                    treatment_fraction=0.8, start_day=params.dots_start,
                                    duration=params.genexpert_introduction - params.dots_start,
                                    property_restrictions_list=['QualityOfCare:Low']))

    camp.add(ramp.RampDTN(camp, ['TBTestDOTSHigh'], params.length_gene_xpert_ramp, params.sens_smear_pos_GXH,
                          params.sens_smear_neg_GXH, params.sens_smear_pos_pre_GH, params.sens_smear_neg_pre_GH, 0.8,
                          pos_event='ProviderOrdersTBTest', pos_event2='ProviderTestNoR',
                          start_day=params.genexpert_introduction, duration=-1,
                          property_restrictions_list=['QualityOfCare:High']))

    camp.add(ramp.RampDTN(camp, ['TBTestDOTSLow'], params.length_gene_xpert_ramp, params.sens_smear_pos_GXL,
                          params.sens_smear_neg_GXL, params.sens_smear_pos_pre_GL, params.sens_smear_neg_pre_GL, 0.8,
                          pos_event='ProviderOrdersTBTest', pos_event2='ProviderTestNoR',
                          start_day=params.genexpert_introduction, duration=-1,
                          property_restrictions_list=['QualityOfCare:Low']))

    camp.add(
        rd.ResistanceDiagnostic(camp, ['ProviderOrdersTBTest'], params.sens_resistance_L, params.specificity_resistance,
                                neg_event='TBDS_Positive', treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                                start_day=params.genexpert_introduction,
                                property_restrictions_list=['QualityOfCare:Low']))

    camp.add(
        rd.ResistanceDiagnostic(camp, ['ProviderOrdersTBTest'], params.sens_resistance_H, params.specificity_resistance,
                                neg_event='TBDS_Positive', treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                                start_day=params.genexpert_introduction,
                                property_restrictions_list=['QualityOfCare:High']))

    camp.add(rd.ResistanceDiagnostic(camp, ['ProviderTestNoR'], params.sens_resistance_L_clinical,
                                     params.specificity_resistance_clinical, neg_event='TBDS_Positive',
                                     treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                                     start_day=params.genexpert_introduction,
                                     property_restrictions_list=['QualityOfCare:Low']))

    camp.add(rd.ResistanceDiagnostic(camp, ['ProviderTestNoR'], params.sens_resistance_H_clinical,
                                     params.specificity_resistance_clinical, neg_event='TBDS_Positive',
                                     treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                                     start_day=params.genexpert_introduction,
                                     property_restrictions_list=['QualityOfCare:High']))

    camp.add(treat.TBHIVDrugTreatment(camp, ['TBTestPositive', 'TBDS_Positive'], 'DOTSHQ', start_day=params.dots_start,
                                      latent_multiplier=0, property_restrictions_list=['QualityOfCare:High']))

    camp.add(treat.TBHIVDrugTreatment(camp, ['TBTestPositive', 'TBDS_Positive'], 'DOTSLQ', start_day=params.dots_start,
                                      latent_multiplier=0, property_restrictions_list=['QualityOfCare:Low']))

    camp.add(treat.TBHIVDrugTreatment(camp, ['TBMDRTestPositive'], 'DOTSMDR', start_day=params.dots_start,
                                      latent_multiplier=0))

    if care == 'slow':
        camp.add(
            hsb.HSB(camp,
                    ['TBActivation', 'TBFailedDrugRegimen', 'TBTestDefault', 'TBTestNegative', 'TBMDRTestDefault'],
                    'TBTestDOTSLow', probability_per_step, start_day=params.burn_initial,
                    property_restrictions_list=['QualityOfCare:Low']))
    if care == 'fast':
        camp.add(
            hsb.HSB(camp,
                    ['TBActivation', 'TBFailedDrugRegimen', 'TBTestDefault', 'TBTestNegative', 'TBMDRTestDefault'],
                    'TBTestDOTSHigh', probability_per_step, start_day=params.burn_initial,
                    property_restrictions_list=['QualityOfCare:High']))
    return camp


def build_demog():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog settings.
    We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    import emodpy_tbhiv.demographics.TBHIVDemographics as Demographics  # OK to call into emod-api

    # demog = Demographics.fromBasicNode( lat=0, lon=0, pop=10000, name=1, forced_id=1 )
    demog = Demographics.fromData(pop=10000, filename_male=manifest.males, filename_female=manifest.females)

    return demog


def set_primary_hiv_pro(task, pro):
    # this is very breakable right now
    tmp_loc = []
    for i, val in enumerate(task.config.parameters.TB_CD4_Primary_Progression):
        tmp_loc += [pro * val]
    task.config.parameters.TB_CD4_Primary_Progression = tmp_loc
    return {'TB_CD4_Primary_Progression': tmp_loc}


def update_more_config(task):
    # update demographics file in config
    task.config.parameters.Demographics_Filenames = ["Trial_Demog_SouthAfrica_3.json",
                                                     'Base_Overlay_SouthAfrica_ReVacc.json']

    task.config.parameters.x_Other_Mortality = 0.34
    task.config.parameters.x_Birth = 1.43

    task.config.parameters.TB_MDR_Fitness_Multiplier = 1.0  # no fitness cost worst case

    if calibration_on:
        task.config.parameters.Simulation_Duration = params.burn_initial + params.burn_predots + 20.0 * 365.0
    else:
        task.config.parameters.Simulation_Duration = params.burn_initial + params.burn_predots + params.To_end_from_DOTS

    # task.set_parameter('Base_Population_Scale_Factor', initial_pop) not in schema anymore
    return task


parameters = [
    {
        'Name': 'Base_Infectivity_Constant',
        'Dynamic': True,
        'MapTo': 'Base_Infectivity_Constant',
        'Guess': 0.028,
        'Min': 0.013,
        'Max': 0.035
    },
    {
        'Name': 'TB_Fast_Progressor_Fraction_Adult',
        'Dynamic': True,
        'MapTo': 'TB_Fast_Progressor_Fraction_Adult',
        'Guess': 0.10,
        'Min': 0.05,
        'Max': 0.15
    },
    {
        'Name': 'TB_Slow_Progressor_Rate',
        'Dynamic': True,
        'MapTo': 'TB_Slow_Progressor_Rate',
        'Guess': 0.005 / 365.0,
        'Min': 0.002 / 365.0,
        'Max': 0.0075 / 365.0
    },
    {
        'Name': 'TB Presymptomatic Duration Years',
        'Dynamic': True,
        # 'MapTo': 'M'
        'Guess': 100.0 / 365.0,
        'Min': 30.0 / 365.0,
        'Max': 365.0 / 365.0
    },
    {
        'Name': 'TB_Active_Presymptomatic_Infectivity_Multiplier',
        'Dynamic': True,
        'MapTo': 'TB_Active_Presymptomatic_Infectivity_Multiplier',
        # This is based on a relative smear-negative of 0.34604 fixed (ok sig figs not withstanding) so
        # ranging from no infectivity to equivalent to a smear negative case at best
        'Guess': 0.34604 * 0.3318,
        'Min': 0.0,
        'Max': 0.34604
    },
    {
        'Name': 'TBHIV Duration',
        'Dynamic': True,
        # constrain to less than duration without HIV
        'Guess': 1.8,
        'Min': 1.0,
        'Max': 4
    },
    {
        'Name': 'TB Duration',
        'Dynamic': True,
        # constrain to less than duration without HIV
        'Guess': 3.5,
        'Min': 2.5,
        'Max': 4.5
    },
    {
        'Name': 'Relative TB CD4 Infectiousness',
        'Dynamic': True,
        # for parsimony not CD4 or ART dependent
        'Guess': 0.5,
        'Min': 0.1,
        'Max': 0.9
    },

    {
        'Name': 'Post_Infection_Acquisition_Multiplier',
        'Dynamic': True,
        'MapTo': 'Post_Infection_Acquisition_Multiplier',
        'Guess': 0.5,
        'Min': 0.4,
        'Max': 0.8
    },
    {
        'Name': 'CD4_aq_below_200_rel',
        'Dynamic': True,
        # first two
        'Guess': 36.0,
        'Min': 4.0,
        'Max': 60.0
    },
    {
        'Name': 'CD4_aq_200_300_rel',
        'Dynamic': True,
        # third
        'Guess': 14.0,
        'Min': 3.0,
        'Max': 50.0
    },
    {
        'Name': 'CD4_aq_300_400_rel',
        'Dynamic': True,
        # fourth
        'Guess': 12.0,
        'Min': 2.0,
        'Max': 50.0
    },
    {
        'Name': 'CD4_aq_400_500_rel',
        'Dynamic': True,
        # fifth
        'Guess': 2.0,
        'Min': 1.0,
        'Max': 23.0
    },
    {
        'Name': 'CD4_aq_above_500',
        'Dynamic': True,
        # six and 7th (for now 7th is really superfluous in future, but for compatibility)
        'Guess': 1.1,
        'Min': 1.0,
        'Max': 4.0
    },
    {
        'Name': 'Primary HIV multiplier',
        'Dynamic': True,
        # for now
        'Guess': 2.0,
        'Min': 1.0,
        'Max': 4.0
    },
    {
        'Name': 'Death Fraction',
        'Dynamic': True,
        # for now
        'Guess': 0.6,
        'Min': 0.4,
        'Max': 0.7
    },
    {
        'Name': 'ART Factor',
        'Dynamic': True,
        # coinfection death scalar, 0 is like no HIV, 1 like HIV with no ART
        'Guess': 0.7,
        'Min': 0.0,
        'Max': 1.0
    },

    {
        'Name': 'Care Seeking Slow Duration Days',
        'Dynamic': True,
        # for now
        'Guess': 250.0,
        'Min': 90.0,
        'Max': 725.0
    },

    {
        'Name': 'Care Seeking Fast Duration Days',
        'Dynamic': True,
        # for now
        'Guess': 90.0,
        'Min': 30.0,
        'Max': 180.0
    },

]

if verbose:
    print([a['Name'] for a in parameters])
    print('Number params', len(parameters))


def set_slow_seek(task, duration):
    loc_rate = 1.0 / duration
    build_camp_partial = partial(build_camp, probability_per_step=loc_rate, care="slow")
    task.create_campaign_from_callback(build_camp_partial)
    return {'LowSeek_Duration': duration}


def set_fast_seek(task, duration):
    loc_rate = 1.0 / duration
    build_camp_partial = partial(build_camp, probability_per_step=loc_rate, care="fast")
    task.create_campaign_from_callback(build_camp_partial)
    return {'HighSeek_Duration': duration}


def set_cd4_infectivity(task, infectrel):
    len_ob = len(list(task.config.parameters.TB_CD4_Infectiousness))
    param_loc = list(np.repeat(infectrel, len_ob))
    task.config.parameters.TB_CD4_Infectiousness = param_loc
    return {'TB_CD4_Infectiousness': param_loc}


def set_cd4_activation_slow(task, rel, whichn):
    # note base must be set first if we are calibrating that too (so slight danger could be improved)
    base = task.config.parameters.TB_Slow_Progressor_Rate
    vals = task.config.parameters.TB_CD4_Activation_Vector

    for i, _ in enumerate(vals):
        if i in whichn:
            vals[i] = rel * base
    task.config.parameters.TB_CD4_Activation_Vector = vals
    return {'CD4bin_' + str(np.min(whichn)): rel}


def set_duration_no_hiv(task, death_fraction, duration):
    # convert from years to days
    # should be set before setting HIV duration
    duration *= 365.0
    loc_rate_recover = (1.0 - death_fraction) / duration
    loc_rate_mort = death_fraction / (1.0 - death_fraction) * loc_rate_recover

    task.config.parameters.TB_Active_Cure_Rate = loc_rate_recover
    task.config.parameters.TB_Active_Mortality_Rate = loc_rate_mort

    return {'TB_Active_Cure_Rate': loc_rate_recover,
            'TB_Active_Mortality_Rate': loc_rate_mort,
            'Death Fraction': death_fraction,
            'Duration_Years': duration / 365.0}


def set_duration_hiv(task, duration, art_factor):
    # convert from years to days, take care of inequality by constraints (i.e, constraint
    # will take care of possible negative values arising
    duration *= 365.0  # convert to days
    rate1 = task.config.parameters.TB_Active_Cure_Rate
    rate2 = task.config.parameters.TB_Active_Mortality_Rate

    output_rate_loc = (1.0 - duration * (rate1 + rate2)) / duration
    task.config.parameters.CoInfection_Mortality_Rate_Off_ART = output_rate_loc
    task.config.parameters.CoInfection_Mortality_Rate_On_ART = output_rate_loc * art_factor

    return {'CoInfection_Mortality_Rate_Off_ART': output_rate_loc,
            'CoInfection_Mortality_Rate_On_ART': output_rate_loc * art_factor,
            'ART Factor': art_factor,
            'TBHIV Duration': duration / 365.0}


# Now define the mapping function
def map_sample_to_model_input(simulation, sample):
    """
    This method needs to map the samples generated by the next point algorithm to the model inputs (represented here by the cb).
    It is important to note that the sample may be shared by several isntances of this function.
    Therefore it is important to deepcopy the sample at the beginning if we intend to modify it (by calling .pop() for example).
       sample = copy.deepcopy(sample)
    :param simulation: The simulation
    :param sample: The sample containing a values for all the params. e.g. {'Clinical Fever Threshold High':1, ... }
    :return: A dictionary containing the tags that will be attached to the simulation
    """

    tags = {}
    # Make a copy of samples so we can alter it safely
    sample = copy.deepcopy(sample)

    # do the simple mappings first
    for p in parameters:
        if 'MapTo' in p:
            if p['Name'] not in sample:
                print('Warning: %s not in sample, perhaps resuming previous iteration' % p['Name'])
                continue
            value = sample.pop(p['Name'])
            tags.update(simulation.task.set_parameter(p['MapTo'], value))

    # Do the custom mappings (note in this case slow progression gets set before CD4 dep one which is right order)
    # if 'TB Presymptomatic Duration Years' in sample:
    #     value = sample.pop('TB Presymptomatic Duration Years') * 365.0
    #     tags.update(simulation.task.update_parameters({'TB_Presymptomatic_Rate': 1.0 / value}))
    if 'TB Presymptomatic Duration Years' in sample:
        value = sample.pop('TB Presymptomatic Duration Years') * 365.0
        simulation.task.config.parameters.TB_Presymptomatic_Rate = 1.0 / value
        tags.update({'TB_Presymptomatic_Rate': 1.0 / value})
    if 'Relative TB CD4 Infectiousness' in sample:
        value = sample.pop('Relative TB CD4 Infectiousness')
        tags.update(set_cd4_infectivity(simulation.task, value))
    if 'CD4_aq_below_200_rel' in sample:
        value = sample.pop('CD4_aq_below_200_rel')
        tags.update(set_cd4_activation_slow(simulation.task, value, [0, 1]))
    if 'CD4_aq_200_300_rel' in sample:
        value = sample.pop('CD4_aq_200_300_rel')
        tags.update(set_cd4_activation_slow(simulation.task, value, [2]))
    if 'CD4_aq_300_400_rel' in sample:
        value = sample.pop('CD4_aq_300_400_rel')
        tags.update(set_cd4_activation_slow(simulation.task, value, [3]))
    if 'CD4_aq_400_500_rel' in sample:
        value = sample.pop('CD4_aq_400_500_rel')
        tags.update(set_cd4_activation_slow(simulation.task, value, [4]))
    if 'CD4_aq_above_500' in sample:
        value = sample.pop('CD4_aq_above_500')
        tags.update(set_cd4_activation_slow(simulation.task, value, [5, 6]))
    if 'Death Fraction' in sample and 'TB Duration' in sample:
        val_dur = sample.pop('TB Duration')
        val_frac = sample.pop('Death Fraction')

        out_params = set_duration_no_hiv(simulation.task, val_frac, val_dur)
        tags.update(out_params)
    if 'TBHIV Duration' in sample and 'ART Factor' in sample:
        val_art = sample.pop('ART Factor')
        val_dur = sample.pop('TBHIV Duration')
        out_params = set_duration_hiv(simulation.task, val_dur, val_art)
        tags.update(out_params)
    if 'Care Seeking Slow Duration Days' in sample:
        val = sample.pop('Care Seeking Slow Duration Days')
        out_params = set_slow_seek(simulation.task, val)
        tags.update(out_params)
        tags.update({'Care Seeking Slow Duration Days': val})
    if 'Care Seeking Fast Duration Days' in sample:
        val = sample.pop('Care Seeking Fast Duration Days')
        out_params = set_fast_seek(simulation.task, val)
        tags.update(out_params)
        tags.update({'Care Seeking Fast Duration Days': val})
    if 'Primary HIV multiplier' in sample:
        val = sample.pop('Primary HIV multiplier')
        out_params = set_primary_hiv_pro(simulation.task, val)
        tags.update(out_params)

    for name, value in sample.items():
        print('UNUSED PARAMETER:' + name)
    assert (len(sample) == 0)  # All params used

    # this is just updating fixed tags at the end

    tags.update({'Simulation_Duration': simulation.task.config.parameters.Simulation_Duration})
    tags.update({'x_Other_Mortality': simulation.task.config.parameters.x_Other_Mortality})
    tags.update(
        {
            'TB_Smear_Negative_Infectivity_Multiplier': simulation.task.config.parameters.TB_Smear_Negative_Infectivity_Multiplier})
    # 'Base_Population_Scale_Factor': simulation.task.config.parameters.Base_Population_Scale_Factor}) # not in schema

    return tags


def constrain_sample(sample):
    """
    This function is called on every samples and allow the user to edit them before they are passed
    to the map_sample_to_model_input function.
    It is useful to round some parameters as demonstrated below.
    Can do much more here, e.g. for
    # Clinical Fever Threshold High <  MSP1 Merozoite Kill Fraction
    if 'Clinical Fever Threshold High' and 'MSP1 Merozoite Kill Fraction' in sample:
        sample['Clinical Fever Threshold High'] = \
            min( sample['Clinical Fever Threshold High'], sample['MSP1 Merozoite Kill Fraction'] )
    You can omit this function by not specifying it in the OptimTool constructor.
    :param sample: The sample coming from the next point algorithm
    :return: The sample with constrained values
    """
    # care seeking largely handled by priors but can be some overlap
    if 'Care Seeking Slow Duration Days' in sample and 'Care Seeking Fast Duration Days' in sample:
        sample['Care Seeking Fast Duration Days'] = np.minimum(sample['Care Seeking Slow Duration Days'],
                                                               sample['Care Seeking Fast Duration Days'])
    if 'TBHIV Duration' in sample and 'TB Duration' in sample:
        sample['TBHIV Duration'] = np.minimum(sample['TBHIV Duration'], sample['TB Duration'])

    # process as a unit for this fixed CD4 break setup (could be generalized with a bit more work)
    if 'CD4_aq_below_200_rel' in sample and 'CD4_aq_200_300_rel' in sample and 'CD4_aq_300_400_rel' in sample \
            and 'CD4_aq_400_500_rel' in sample and 'CD4_aq_above_500' in sample:
        sample['CD4_aq_below_200_rel'] = np.maximum(sample['CD4_aq_below_200_rel'], sample['CD4_aq_200_300_rel'])
        sample['CD4_aq_300_400_rel'] = np.minimum(sample['CD4_aq_300_400_rel'], sample['CD4_aq_200_300_rel'])
        sample['CD4_aq_400_500_rel'] = np.minimum(sample['CD4_aq_300_400_rel'], sample['CD4_aq_400_500_rel'])
        sample['CD4_aq_above_500'] = np.minimum(sample['CD4_aq_above_500'], sample['CD4_aq_400_500_rel'])

    return sample


def calib_run(task):
    volume_fraction = 0.001  # desired fraction of N-sphere area to unit cube area for numerical derivative (automatic radius scaling with N)
    num_params = len([p for p in parameters if p['Dynamic']])

    if num_params == 0:
        warning_note = \
            """
            /!\\ WARNING /!\\ the OptimTool requires at least one of params with Dynamic set to True. Exiting...                  
            """
        print(warning_note)
        exit()

    r = OptimTool.get_r(num_params, volume_fraction)

    optimtool = OptimTool(parameters,
                          constrain_sample,  # <-- WILL NOT BE SAVED IN ITERATION STATE
                          mu_r=r,
                          # <-- radius for numerical derivatve.  CAREFUL not to go too small with integer parameters
                          sigma_r=r / 10.,  # <-- stdev of radius
                          center_repeats=1,
                          # <-- Number of times to replicate the center (current guess).  Nice to compare intrinsic to extrinsic noise
                          samples_per_iteration=3  # 500
                          # 32 # <-- Samples per iteration, includes center repeats.  Actual number of sims run is this number times number of sites.
                          )

    calib_manager = CalibManager(name='SA_small_radius_CD4_HIV_death_with_TB_signs_demo',
                                 # <-- Please customize this name
                                 task=task,
                                 map_sample_to_model_input_fn=map_sample_to_model_input,
                                 sites=sites,
                                 next_point=optimtool,
                                 sim_runs_per_param_set=1,  # <-- Replicates
                                 max_iterations=3,  # 20 <-- Iterations
                                 plotters=None)

    calib_manager.run_calibration()


def ep4_fn(task):
    task = emod_task.add_ep4_from_path(task, manifest.ep4_path)
    return task


def run_calib(erad_path):
    """
    This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    """
    # Define custom report class
    report = Report_TBHIV_ByAge()

    # we can report all following events. they are listed in console "Campaign is publishing the following events"
    report.add_report(200, 0, 0, 200, [
        'Below500',
        'Below200',
        # 'TBTestPositive', why can't? look here: https://github.com/InstituteforDiseaseModeling/DtkTrunk/blob/TBHIV-Ongoing/reporters/lib_customreport_TBHIV_ReportByAge/Report_TBHIV_ByAge.cpp#L212
        'HIVTestedNegative',
        'HIVTestedPositive',
        'TBTestDOTSHigh',
        'TBTestNegative',
        'TBTestDOTSLow',
        # 'ProviderOrdersTBTest', why can't?
        'TBMDRTestPositive',
        'TBDS_Positive',
        'ProviderTestNoR',
        'Below350',
        'TBTestDefault',
        'TBMDRTestDefault'])
    # add reporter_plugin dir for load needed reporter plugin files
    report.asset_dir = manifest.plugins_folder

    # create EMODTask
    print("Creating EMODTask")
    task = EMODTask.from_default2(
        config_path='my_config.json',
        eradication_path=erad_path,
        campaign_builder=build_camp,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        ep4_custom_cb=ep4_fn,
        demog_builder=None,
        # here we already loaded demo files to Assets and add filename to config's Demographics_Filenames
        plugin_report=report
    )

    print("Adding other asset files from local Assets dir")
    task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)

    # update more config parameters
    update_more_config(task)

    # set some drug properties
    add_tb_drug(task, 'ACFDOTS')
    add_tb_drug_type(task, 'DOTSMDR', 270, 0.5, 0.03, 0, 0.10, 0.02)
    add_tb_drug_type(task, 'PreDOTSHigh', 180, 0.5, 0.03, 0, 0.10, 0.02)
    add_tb_drug_type(task, 'PreDOTSLow', 180, 0.5, 0.03, 0, 0.10, 0.02)
    add_tb_drug_type(task, 'Universal', 90, 0.8, 0.03, 0.02, 0.10, 0.02)

    # add emod-api to COMPS's Assets
    pl = RequirementsToAssetCollection(platform, requirements_path=manifest.requirements)
    ac = pl.run()
    # ac = '015db7d4-913b-eb11-a2c2-f0921c167862'  # emod-api 1.3  stage
    # ac = '796487a2-323e-eb11-a2dd-c4346bcb7271'  # emod-api 1.3 prod
    other_assets = AssetCollection.from_id(ac, as_copy=True)
    task.common_assets.add_assets(other_assets)

    if calibration_on:
        resist = 0.0
        add_drugs_calib(task, resist)
        calib_manager.platform = platform
        calib_run(task)

    else:
        from idmtools.entities.templated_simulation import TemplatedSimulations
        from idmtools.entities.experiment import Experiment
        from idmtools.builders import SimulationBuilder

        # subsample is the fixed part. If varying params that were in calibration, only fix the subsample that you wish to fix and use a separate
        # ModFn for the varying part. Don't put both though, behavior is unclear in that case.
        # Note in general can grab subsample from the CalibManager.json
        subsample = {'ART Factor': 1.0,
                     'Base_Infectivity_Constant': 0.032287,
                     'CD4_aq_200_300_rel': 4.434,
                     'CD4_aq_300_400_rel': 2.0,
                     'CD4_aq_400_500_rel': 1.0,
                     'CD4_aq_above_500': 1.0,
                     'CD4_aq_below_200_rel': 54.55,
                     'Care Seeking Fast Duration Days': 173.14,
                     'Care Seeking Slow Duration Days': 493.25,
                     'Death Fraction': 0.7,
                     'Post_Infection_Acquisition_Multiplier': 0.483,
                     'Primary HIV multiplier': 1.0,
                     'Relative TB CD4 Infectiousness': 0.1,
                     'TB Duration': 2.5,
                     'TB Presymptomatic Duration Years': 0.0821,
                     'TBHIV Duration': 1.82,
                     'TB_Active_Presymptomatic_Infectivity_Multiplier': 0.1660,
                     'TB_Fast_Progressor_Fraction_Adult': 0.15,
                     "TB_Slow_Progressor_Rate": 1.5425e-05}

        # Create simulation sweep with builder
        builder = SimulationBuilder()
        builder.add_sweep_definition(update_sim_random_seed, range(0, 2))
        builder.add_sweep_definition(add_drugs, [0.0, 1.0e-1])
        builder.add_sweep_definition(map_sample_to_model_input, [subsample])

        # create TemplatedSimulations for builder
        ts = TemplatedSimulations(base_task=task)
        ts.add_builder(builder)

        # Create Experiment
        exp_name = 'TB SA experiment'
        experiment = Experiment(name=exp_name)

        experiment.simulations = ts

        # run experiment
        experiment.run(platform=platform)


if __name__ == "__main__":
    # Create a platform
    platform = Platform("CALCULON")
    # platform = Platform("SLURM2")
    # bamboo plan name
    plan = EradicationBambooBuilds.TBHIV
    # download eradication and schema from bamboo, you can comment out get_model_files once you download files to local in next run
    get_model_files(plan, manifest)
    run_calib(manifest.eradication_path)
