import os
import copy
import numpy as np

from idmtools.assets import Asset
from idmtools.core.platform_factory import Platform
from idmtools_calibra.utilities.mod_fn import ModFn
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.algorithms.optim_tool import OptimTool

from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy.interventions.emod_empty_campaign import EMODEmptyCampaign

from examples.helper import download_bamboo_exe, download_reporter

from tb.add_tbhiv_treat import add_tbhiv_treat
from tb.add_active_diagnostic import add_active_diagnostic
from tb.add_hiv_incidence import add_hiv_incidence
from tb.add_diagnostic_treat_neg import add_diagnostic_treat_neg
from tb.add_simple_health_seeking import add_simple_health_seeking
from tb.add_ramp_diagnostic_treat_neg import add_ramp_diagnostic_treat_neg
from tb.add_cd4_diagnostic import add_cd4_diagnostic
from tb.add_art import add_art
from tb.add_resistance_diagnostic import add_resistance_diagnostic
from tb.add_tb_drug_type import add_tb_drug_type
from tb.add_tbhiv_outbreak import add_tbhiv_outbreak
from tb.add_simple_hiv_diagnostic import add_simple_hiv_diagnostic
from tb.tb_custom_reports import add_tb_report
from analyzer_dev.CalibSites import SouthAfricaCalibSite

CURRENT_DIRECTORY = os.path.dirname(__file__)
INPUT_PATH = os.path.join('..', 'inputs')
INPUT_PATH = os.path.abspath(INPUT_PATH)

platform = Platform('CALCULON')  # switch to BELEGOST with platform = Platform('BELEGOST')
env = platform.environment

plan = EradicationBambooBuilds.TBHIV_WIN if env.lower() == 'belegost' or env.lower() == 'bayesian' \
    else EradicationBambooBuilds.TBHIV

# Test latest bamboo Eradication.exe (it won't download if exists already)
exe_path = download_bamboo_exe(os.path.join(INPUT_PATH, 'bamboo'), platform, plan=plan)
reporter_plugins = os.path.join(INPUT_PATH, 'bamboo', 'reporter_plugins')
download_reporter(reporter_plugins,  plan=plan)

config_path = os.path.join(INPUT_PATH, 'tb_config.json')

# Create task: windows
task = EMODTask.from_files(
    eradication_path=exe_path,
    config_path=config_path,
)
# for load so report flag
task.is_linux = False if env.lower() == 'belegost' or env.lower() == 'bayesian' else True
# Select a campaign
task.campaign = EMODEmptyCampaign.campaign()

# Add required files as assets
a1 = Asset(os.path.join(INPUT_PATH, 'assets', 'Base_Overlay_SouthAfrica_ReVacc.json'))
a2 = Asset(os.path.join(INPUT_PATH, 'assets', 'Trial_Demog_SouthAfrica_3.json'))
task.common_assets.add_assets([a1, a2])

# Add reporter folder
task.reporters.add_dll_folder(reporter_plugins)

#  Add required parameter
task.set_parameter("Custom_Coordinator_Events", [])
task.set_parameter("Enable_Abort_Zero_Infectivity", 0)
task.set_parameter("Custom_Node_Events", [])
task.set_parameter("Enable_Infectivity_Reservoir", 0)
task.set_parameter("Enable_Initial_Susceptibility_Distribution", 0)
task.set_parameter("Post_Infection_Mortality_Multiplier", 1)
task.set_parameter("Post_Infection_Transmission_Multiplier", 1)
task.set_parameter("Report_Coordinator_Event_Recorder", 0)
task.set_parameter("Report_Node_Event_Recorder", 0)
task.set_parameter("Report_Surveillance_Event_Recorder", 0)

# parameters to set once debugging is done
task.set_parameter('logLevel_default', 'ERROR')
# cb.disable('Default_Reporting')
task.set_parameter('Enable_Default_Reporting', 0)

sites = [SouthAfricaCalibSite()]  # yeah its plural

initial_pop = 10000
verbose = True
calibration_on = False


# Parameter setting functions
def set_run_number(simulation, value):
    simulation.task.set_parameter('Run_Number', value)
    return {'Run_Number': value}


def set_hiv_slow(task, pro):
    # this is very breakable right now
    tmp_loc = []
    for i, val in enumerate(task.get_parameter('TB_CD4_Activation_Vector')):
        if i < 3:
            tmp_loc += [pro * val]
        else:
            tmp_loc += [val]
    task.set_parameter('TB_CD4_Activation_Vector', tmp_loc)
    return {'TB_CD4_Activation_Vector': tmp_loc}


def set_primary_hiv_pro(task, pro):
    # this is very breakable right now
    tmp_loc = []
    for i, val in enumerate(task.get_parameter('TB_CD4_Primary_Progression')):
        tmp_loc += [pro * val]
    task.set_parameter('TB_CD4_Primary_Progression', tmp_loc)
    return {'TB_CD4_Primary_Progression': tmp_loc}


def set_coinf_death(task, rate):
    task.set_parameter('CoInfection_Mortality_Rate_Off_ART', rate)
    return {'CoInfection_Mortality_Rate_Off_ART': rate}


# intervention functions

def cpr_sens_spec(task, sensCRP, specCRP):
    add_active_diagnostic(task, ['HIVTestedNegative'], sensCRP, specCRP, start_day=intervention_day,
                          pos_event='CRPPosHIVNeg')
    add_active_diagnostic(task, ['HIVTestedPositive'], sensCRP, specCRP,
                          start_day=intervention_day, pos_event='CRPPosHIVPos')
    return {'CRPSensSpec': (sensCRP, specCRP)}


def modify_infectivity(task, infectivity):
    task.set_parameter('Base_Infectivity', infectivity)
    return {'Base_Infectivity': infectivity}


def add_drugs(simulation, resist_pro):
    add_tb_drug_type(simulation.task, 'DOTSHQ', 180.0, 0.8, 0.03, resist_pro, 0.10, 0.02, mdr_cure_proportion=0.1)
    add_tb_drug_type(simulation.task, 'DOTSLQ', 180.0, 0.5, 0.03, resist_pro, 0.10, 0.02, mdr_cure_proportion=0.1)
    return {'ResistancePro': resist_pro}


def add_drugs_calib(task, resist_pro):
    add_tb_drug_type(task, 'DOTSHQ', 180.0, 0.8, 0.03, resist_pro, 0.10, 0.02, mdr_cure_proportion=0.1)
    add_tb_drug_type(task, 'DOTSLQ', 180.0, 0.5, 0.03, resist_pro, 0.10, 0.02, mdr_cure_proportion=0.1)
    return {'ResistancePro': resist_pro}


params = [
    {
        'Name': 'Base_Infectivity',
        'Dynamic': True,
        'MapTo': 'Base_Infectivity',
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
    print([a['Name'] for a in params])
    print('Number params', len(params))

# campaign parameters
burn_initial = 1 * 365
burn_predots = 100 * 365

dots_start = burn_initial + burn_predots
hiv_epidemic_start = dots_start - 15 * 365
art_start = hiv_epidemic_start + 21 * 365
genexpert_introduction = dots_start + 9 * 365
length_gene_xpert_ramp = 3 * 365  # PLOS one
To_end_from_DOTS = 50 * 365
# passive seeking rates
high_seek = 1.0 / (3 * 30)
low_seek = 1.0 / (7 * 30)
b_offset = dots_start / 365.0 - 2000  # ie DOTS starting in 2000
# ART introduction in 2007
seek_200 = 1.0 / (30.0)
seek_350_500 = 1.0 / (60.0)

# sensitivities PreDOTS
sens_smear_neg_pre_GL = 0.4
sens_smear_pos_pre_GL = 0.7

sens_smear_neg_pre_GH = 0.4
sens_smear_pos_pre_GH = 0.7

sens_smear_neg_GXL = 0.7
sens_smear_pos_GXL = 0.7
sens_smear_pos_GXH = 0.99
sens_smear_neg_GXH = 0.9

sens_resistance_L = 0.5
sens_resistance_H = 0.7
specificity_resistance = 1.00
sens_resistance_L_clinical = 0.5
sens_resistance_H_clinical = 0.7
specificity_resistance_clinical = 1.00

CRP_Sensitivity = 0.91
CRP_Specificity = 0.59

intervention_day = dots_start + 18.0 * 365

dots_plus_15 = dots_start + 15.0 * 365.0
task.update_parameters({'TB_Smear_Negative_Infectivity_Multiplier': 0.34604, 'TB_Presymptomatic_Rate': 0.01165,
                        'TB_Active_Presymptomatic_Infectivity_Multiplier': 0.34604 * 0.3318})
low_seek = 1.0 / 263.0

# Set demographics files
tmp_name = 'Trial_Demog_SouthAfrica_3.json'
task.set_parameter('Demographics_Filenames', [tmp_name, 'Base_Overlay_SouthAfrica_ReVacc.json'])
task.set_parameter('x_Other_Mortality', 0.34)
task.set_parameter('x_Birth', 1.43)
additional_events = ['ProviderTestNoR'] + ["Below200", "Below350", "Below500", "Above500"]

# set underlying parameters (cut one of these
task.set_parameter('Listed_Events',
                   ['TotalPos', 'TBMonitoring', 'Delay', 'Blackout', 'TBTestPreDOTSLow', 'TBTestPreDOTSHigh',
                    'TBDS_Positive',
                    'TBTestDOTSHigh', 'TBTestDOTSLow', 'Seek200', 'Seek350', 'Seek500', 'CRPPosHIVPos', 'CRPPosHIVNeg',
                    'LAMPosHIVPos', 'LAMPosHIVNeg', 'TLAM', 'B100', 'None', 'TruePos', 'TruePosHIV', 'B200', 'Bmiddle',
                    'BCG_Eligible_HIV', 'Disqualify'] + [
                       'ProviderTestNoR'])

task.set_parameter('Custom_Individual_Events',
                   ['TotalPos', 'TBMonitoring', 'Delay', 'Blackout', 'TBTestPreDOTSLow', 'TBTestPreDOTSHigh',
                    'TBDS_Positive',
                    'TBTestDOTSHigh', 'TBTestDOTSLow', 'Seek200', 'Seek350', 'Seek500', 'CRPPosHIVPos',
                    'CRPPosHIVNeg', 'LAMPosHIVPos', 'LAMPosHIVNeg', 'TLAM', 'B100', 'None', 'TruePos',
                    'TruePosHIV', 'B200', 'Bmiddle', 'BCG_Eligible_HIV', 'Disqualify'] + additional_events)

task.set_parameter('TB_MDR_Fitness_Multiplier', 1.0)  # no fitness cost worst case
if calibration_on:
    task.set_parameter('Simulation_Duration', burn_initial + burn_predots + 20.0 * 365.0)
else:
    task.set_parameter('Simulation_Duration', burn_initial + burn_predots + To_end_from_DOTS)
task.set_parameter('Base_Population_Scale_Factor', initial_pop)

# add reporting
add_tb_report(task, stop_year=2000,
              additional_events=['TLAM', 'TruePos', 'TruePosHIV', 'B200', 'Bmiddle', 'Seek200', 'Seek350', 'Seek500',
                                 'CRPPosHIVNeg', 'CRPPosHIVPos', 'B100', 'LAMPosHIVPos', 'LAMPosHIVNeg',
                                 'HIVTestedNegative', 'HIVTestedPositive', 'TotalPos', 'TBMonitoring'])

# Should use following line with new Eradication
# from emodpy.reporters.custom import Report_TBHIV_ByAge
# report = Report_TBHIV_ByAge()
# report.add_report(200, 0, 0, 200,
#                  [['TLAM', 'TruePos', 'TruePosHIV', 'B200', 'Bmiddle', 'Seek200', 'Seek350', 'Seek500',
#                     'CRPPosHIVNeg', 'CRPPosHIVPos', 'B100', 'LAMPosHIVPos', 'LAMPosHIVNeg',
#                     'HIVTestedNegative', 'HIVTestedPositive', 'TotalPos', 'TBMonitoring']])
# task.reporters.add_reporter(report)


# block of functions to be used in calibration

def set_slow_seek(cbin, duration):
    loc_rate = 1.0 / duration
    add_simple_health_seeking(cbin, ['TBActivation', 'TBFailedDrugRegimen', 'TBTestDefault', 'TBTestNegative',
                                   'TBMDRTestDefault'],
                            'TBTestDOTSLow', loc_rate, start_day=burn_initial,
                              duration=-1, property_restrictions_list=['Care_Quality:Low'])

    return {'LowSeek_Duration': duration}


def set_fast_seek(cbin, duration):
    loc_rate = 1.0 / duration
    add_simple_health_seeking(cbin, ['TBActivation', 'TBFailedDrugRegimen', 'TBTestDefault', 'TBTestNegative',
                                   'TBMDRTestDefault'],
                            'TBTestDOTSHigh', loc_rate, start_day=burn_initial,
                              duration=-1, property_restrictions_list=['Care_Quality:High'])
    return {'HighSeek_Duration': duration}


def set_cd4_infectivity(cbin, infectrel):
    len_ob = len(list(cbin.get_parameter('TB_CD4_Infectiousness')))
    param_loc = list(np.repeat(infectrel, len_ob))
    cbin.set_parameter('TB_CD4_Infectiousness', param_loc)
    return {'TB_CD4_Infectiousness': param_loc}


def set_cd4_activation_slow(cbin, rel, whichn):
    # note base must be set first if we are calibrating that too (so slight danger could be improved)
    base = cbin.get_parameter('TB_Slow_Progressor_Rate')
    vals = cbin.get_parameter('TB_CD4_Activation_Vector')

    for i, _ in enumerate(vals):
        if i in whichn:
            vals[i] = rel * base
    cbin.set_parameter('TB_CD4_Activation_Vector', vals)
    return {'CD4bin_' + str(np.min(whichn)): rel}


def set_duration_no_hiv(cbin, death_fraction, duration):
    # convert from years to days
    # should be set before setting HIV duration
    duration *= 365.0
    loc_rate_recover = (1.0 - death_fraction) / duration
    loc_rate_mort = death_fraction / (1.0 - death_fraction) * loc_rate_recover

    cbin.set_parameter('TB_Active_Cure_Rate', loc_rate_recover)
    cbin.set_parameter('TB_Active_Mortality_Rate', loc_rate_mort)

    return {'TB_Active_Cure_Rate': loc_rate_recover,
            'TB_Active_Mortality_Rate': loc_rate_mort,
            'Death Fraction': death_fraction,
            'Duration_Years': duration / 365.0}


def set_duration_hiv(cbin, duration, art_factor):
    # convert from years to days, take care of inequality by constraints (i.e, constraint
    # will take care of possible negative values arising
    duration *= 365.0  # convert to days
    rate1 = cbin.get_parameter('TB_Active_Cure_Rate')
    rate2 = cbin.get_parameter('TB_Active_Mortality_Rate')

    output_rate_loc = (1.0 - duration * (rate1 + rate2)) / duration
    task.set_parameter('CoInfection_Mortality_Rate_Off_ART', output_rate_loc)
    task.set_parameter('CoInfection_Mortality_Rate_On_ART', output_rate_loc * art_factor)

    return {'CoInfection_Mortality_Rate_Off_ART': output_rate_loc,
            'CoInfection_Mortality_Rate_On_ART': output_rate_loc * art_factor,
            'ART Factor': art_factor,
            'TBHIV Duration': duration / 365.0}


if calibration_on:
    resist = 0.0
    add_drugs_calib(task, resist)

# initial TB outbreak
add_tbhiv_outbreak(task, 0.05, 'TB')
task.set_parameter('TB_Slow_Progressor_Rate', 0.007 / 365.0)

# HIV incidence, care seeking, and treatment by guidelines
add_simple_hiv_diagnostic(task, ['HappyBirthday'], start_day=art_start, treatment_fraction=0.23,
                          property_restrictions_list=['Care_Quality:High'])
add_simple_hiv_diagnostic(task, ['HappyBirthday'], start_day=art_start, treatment_fraction=0.13,
                          property_restrictions_list=['Care_Quality:Low'])
add_cd4_diagnostic(task, ['HIVTestedPositive'], start_day=art_start)

add_hiv_incidence(task, hiv_epidemic_start - 1.0, start_day=hiv_epidemic_start)
add_simple_health_seeking(task, ['Below200'], 'Seek200', seek_200, start_day=art_start, duration=-1)
add_simple_health_seeking(task, ['Below350'], 'Seek350', seek_350_500, start_day=art_start + 3.0 * 365.0, duration=-1)
add_simple_health_seeking(task, ['Below500'], 'Seek500', seek_350_500, start_day=art_start + 6.0 * 365.0, duration=-1)
add_art(task, ['Seek200', 'Seek350', 'Seek500'], start_day=art_start)

# set some drug properties
add_tb_drug_type(task, 'DOTSMDR', 270, 0.5, 0.03, 0, 0.10, 0.02)
add_tb_drug_type(task, 'PreDOTSHigh', 180, 0.5, 0.03, 0, 0.10, 0.02)
add_tb_drug_type(task, 'PreDOTSLow', 180, 0.5, 0.03, 0, 0.10, 0.02)
add_tb_drug_type(task, 'Universal', 90, 0.8, 0.03, 0.02, 0.10, 0.02)

add_diagnostic_treat_neg(task, ['TBTestDOTSHigh'], sens_smear_pos_pre_GH, sens_smear_neg_pre_GH,
                         treatment_fraction=0.8,
                         start_day=burn_initial, duration=burn_predots,
                         property_restrictions_list=['Care_Quality:High'])
add_diagnostic_treat_neg(task, ['TBTestDOTSLow'], sens_smear_pos_pre_GL, sens_smear_neg_pre_GL,
                         treatment_fraction=0.8,
                         start_day=burn_initial, duration=burn_predots,
                         property_restrictions_list=['Care_Quality:Low'])

add_tbhiv_treat(task, 'PreDOTSLow', ['TBTestPositive'], start_day=burn_initial, duration=burn_predots,
                latent_multiplier=0, property_restrictions_list=['Care_Quality:Low'])

add_tbhiv_treat(task, 'PreDOTSHigh', ['TBTestPositive'], start_day=burn_initial, duration=burn_predots,
                latent_multiplier=0, property_restrictions_list=['Care_Quality:High'])

add_diagnostic_treat_neg(task, ['TBTestDOTSHigh'], sens_smear_pos_pre_GH, sens_smear_neg_pre_GH, treatment_fraction=0.8,
                         start_day=dots_start, duration=genexpert_introduction - dots_start,
                         property_restrictions_list=['Care_Quality:High'])
add_diagnostic_treat_neg(task, ['TBTestDOTSLow'], sens_smear_pos_pre_GL, sens_smear_neg_pre_GL, treatment_fraction=0.8,
                         start_day=dots_start, duration=genexpert_introduction - dots_start,
                         property_restrictions_list=['Care_Quality:Low'])

add_ramp_diagnostic_treat_neg(task, ['TBTestDOTSHigh'], length_gene_xpert_ramp, sens_smear_pos_GXH, sens_smear_neg_GXH,
                              sens_smear_pos_pre_GH, sens_smear_neg_pre_GH, 0.8, treatment_fraction=0.8,
                              pos_event='ProviderOrdersTBTest', pos_event2='ProviderTestNoR',
                              start_day=genexpert_introduction, duration=-1,
                              property_restrictions_list=['Care_Quality:High'])

add_ramp_diagnostic_treat_neg(task, ['TBTestDOTSLow'], length_gene_xpert_ramp, sens_smear_pos_GXL, sens_smear_neg_GXL,
                              sens_smear_pos_pre_GL, sens_smear_neg_pre_GL, 0.8, treatment_fraction=0.8,
                              pos_event='ProviderOrdersTBTest', pos_event2='ProviderTestNoR',
                              start_day=genexpert_introduction, duration=-1,
                              property_restrictions_list=['Care_Quality:Low'])

add_resistance_diagnostic(task, ['ProviderOrdersTBTest'], sens_resistance_L, specificity_resistance,
                          neg_event='TBDS_Positive',
                          treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                          start_day=genexpert_introduction, property_restrictions_list=['Care_Quality:Low'])

add_resistance_diagnostic(task, ['ProviderOrdersTBTest'], sens_resistance_H, specificity_resistance,
                          neg_event='TBDS_Positive',
                          treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                          start_day=genexpert_introduction, property_restrictions_list=['Care_Quality:High'])

add_resistance_diagnostic(task, ['ProviderTestNoR'], sens_resistance_L_clinical, specificity_resistance_clinical,
                          neg_event='TBDS_Positive',
                          treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                          start_day=genexpert_introduction, property_restrictions_list=['Care_Quality:Low'])

add_resistance_diagnostic(task, ['ProviderTestNoR'], sens_resistance_H_clinical, specificity_resistance_clinical,
                          neg_event='TBDS_Positive',
                          treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                          start_day=genexpert_introduction, property_restrictions_list=['Care_Quality:High'])

add_tbhiv_treat(task, 'DOTSHQ', ['TBTestPositive', 'TBDS_Positive'], start_day=dots_start,
                latent_multiplier=0, property_restrictions_list=['Care_Quality:High'])

add_tbhiv_treat(task, 'DOTSLQ', ['TBTestPositive', 'TBDS_Positive'], start_day=dots_start,
                latent_multiplier=0, property_restrictions_list=['Care_Quality:Low'])

add_tbhiv_treat(task, 'DOTSMDR', ['TBMDRTestPositive'], start_day=dots_start,
                latent_multiplier=0)


# Now define the mapping function

###################################################
###################################################

def map_sample_to_model_input(simulation, sample):
    """
    This method needs to map the samples generated by the next point algorithm to the model inputs (represented here by the cb).
    It is important to note that the sample may be shared by several isntances of this function.
    Therefore it is important to deepcopy the sample at the beginning if we intend to modify it (by calling .pop() for example).
       sample = copy.deepcopy(sample)
    :param cb: The config builder representing the model inputs for this particular simulation
    :param sample: The sample containing a values for all the params. e.g. {'Clinical Fever Threshold High':1, ... }
    :return: A dictionary containing the tags that will be attached to the simulation
    """

    tags = {}
    # Make a copy of samples so we can alter it safely
    sample = copy.deepcopy(sample)

    # do the simple mappings first
    for p in params:
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
        simulation.task.update_parameters({'TB_Presymptomatic_Rate': 1.0 / value})
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

    tags.update({'Simulation_Duration': simulation.task.get_parameter('Simulation_Duration')})
    tags.update({'x_Other_Mortality': simulation.task.get_parameter('x_Other_Mortality')})
    tags.update(
        {'TB_Smear_Negative_Infectivity_Multiplier': simulation.task.get_parameter(
            'TB_Smear_Negative_Infectivity_Multiplier'),
            'Base_Population_Scale_Factor': simulation.task.get_parameter('Base_Population_Scale_Factor')})

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


if calibration_on:

    volume_fraction = 0.001  # desired fraction of N-sphere area to unit cube area for numerical derivative (automatic radius scaling with N)
    num_params = len([p for p in params if p['Dynamic']])

    if num_params == 0:
        warning_note = \
            """
            /!\\ WARNING /!\\ the OptimTool requires at least one of params with Dynamic set to True. Exiting...                  
            """
        print(warning_note)
        exit()

    r = OptimTool.get_r(num_params, volume_fraction)

    optimtool = OptimTool(params,
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

    run_calib_args = {'calib_manager': calib_manager}
else:

    # subsample is the fixed part. If varying params that were in calibration, only fix the subsample that you wish to fix and use a separate
    # ModFn for the varying part. Don't put both though, behavior is unclear in that case.
    # Note in general can grab subsample from the CalibManager.json
    subsample = {'ART Factor': 1.0,
                 'Base_Infectivity': 0.032287,
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

    from idmtools.builders import SimulationBuilder

    fs1 = [ModFn(set_run_number, value=i) for i in range(0, 2)]  # 100
    fs2 = [ModFn(add_drugs, resist) for resist in [0.0, 1.0e-1]]
    fs3 = [ModFn(map_sample_to_model_input, ss) for ss in [subsample]]

    builder = SimulationBuilder()
    builder.sweeps.append(fs1)
    builder.sweeps.append(fs2)
    builder.sweeps.append(fs3)
    builder.count = len(fs1) * len(fs2) * len(fs3)

if __name__ == "__main__":
    if calibration_on:
        calib_manager.platform = platform
        calib_manager.run_calibration()
    else:
        from idmtools.entities.templated_simulation import TemplatedSimulations
        from idmtools.entities.experiment import Experiment

        ts = TemplatedSimulations(base_task=task)
        ts.add_builder(builder)

        # Create Experiment
        exp_name = 'TB SA experiment'
        experiment = Experiment(name=exp_name)

        # Add simulation using templates
        experiment.simulations = ts

        # run experiment
        experiment.run(platform=platform)
