import os
import sys
import copy
import numpy as np
# from kf_emod_task import KF_EMODTask
from tb_emod_task import TB_EMODTask
from idmtools.assets import AssetCollection, Asset

from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy.interventions.emod_empty_campaign import EMODEmptyCampaign
from idmtools_calibra.utilities.mod_fn import ModFn
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.algorithms.optim_tool import OptimTool
from idmtools_calibra.utilities.helper import generate_default_config_from_exe

# from tb.TBCustomReports import *
from tb.add_tbhiv_treat import add_tbhiv_treat
from tb.add_ActiveDiagnostic import add_ActiveDiagnostic
from tb.add_HIVIncidence import add_HIVIncidence
from tb.add_DiagnosticTreatNeg import add_DiagnosticTreatNeg
from tb.add_SimpleHealthSeeking import add_SimpleHealthSeeking
from tb.add_Ramp_DiagnosticTreatNeg import add_Ramp_DiagnosticTreatNeg
from tb.add_cd4diagnostic import add_cd4diagnostic
from tb.add_art import add_art
from tb.add_ResistanceDiagnostic import add_ResistanceDiagnostic
from tb.add_tb_drug_type import add_tb_drug_type
from tb.add_tbhiv_outbreak import add_tbhiv_outbreak
from tb.add_simplehivdiagnostic import add_simplehivdiagnostic
# from tb.utils.TBCustomReports import add_tb_report
from tb.TBCustomReports import add_tb_report

CURRENT_DIRECTORY = os.path.dirname(__file__)
INPUT_PATH = os.path.join('..', 'inputs')
INPUT_PATH = os.path.abspath(INPUT_PATH)

print(INPUT_PATH)
print(os.path.exists(INPUT_PATH))


# Parameter setting functions
def setRunNumber(task, run):
    task.set_parameter('Run_Number', run)
    return {'Run_Number': run}


def setHIVslow(simulation, pro):
    # this is very breakable right now
    tmp_loc = []
    for i, val in enumerate(simulation.task.get_parameter('TB_CD4_Activation_Vector')):
        if i < 3:
            tmp_loc += [pro * val]
        else:
            tmp_loc += [val]
    simulation.task.set_parameter('TB_CD4_Activation_Vector', tmp_loc)
    return {'TB_CD4_Activation_Vector': tmp_loc}


def setprimaryHIVpro(simulation, pro):
    # this is very breakable right now
    tmp_loc = []
    for i, val in enumerate(simulation.task.get_parameter('TB_CD4_Primary_Progression')):
        tmp_loc += [pro * val]
    simulation.task.set_parameter('TB_CD4_Primary_Progression', tmp_loc)
    return {'TB_CD4_Primary_Progression': tmp_loc}


def setCoinfDeath(simulation, rate):
    simulation.task.set_parameter('CoInfection_Mortality_Rate_Off_ART', rate)
    return {'CoInfection_Mortality_Rate_Off_ART': rate}


# intervention functions

def CRPSensSpec(task, sensCRP, specCRP):
    add_ActiveDiagnostic(task, ['HIVTestedNegative'], sensCRP, specCRP, start_day=intervention_day,
                         pos_event='CRPPosHIVNeg')
    add_ActiveDiagnostic(task, ['HIVTestedPositive'], sensCRP, specCRP,
                         start_day=intervention_day, pos_event='CRPPosHIVPos')
    return {'CRPSensSpec': (sensCRP, specCRP)}


def ModifyInfectivity(simulation, infectivity):
    simulation.task.set_parameter('Base_Infectivity', infectivity)
    return {'Base_Infectivity': infectivity}


def Add_Drugs(simulation, resist_pro):
    add_tb_drug_type(simulation.task, 'DOTSHQ', 180.0, 0.8, 0.03, resist_pro, 0.10, 0.02, mdr_cure_proportion=0.1)
    add_tb_drug_type(simulation.task, 'DOTSLQ', 180.0, 0.5, 0.03, resist_pro, 0.10, 0.02, mdr_cure_proportion=0.1)
    return {'ResistancePro': resist_pro}


# use Bradley's EXE
exe_path = r'C:\Projects\itertool_zdu2\examples\inputs\Eradication_decline.exe'  # Brad's exe
config_path = os.path.join(INPUT_PATH, 'tb_config.json')

# Create task
task = TB_EMODTask.from_files(
    eradication_path=exe_path,
    config_path=config_path,
)

task.legacy_exe = True

# Select a campaign
task.campaign = EMODEmptyCampaign.campaign()

a1 = Asset(os.path.join(INPUT_PATH, 'assets', 'Base_Overlay_SouthAfrica_ReVacc.json'))
a2 = Asset(os.path.join(INPUT_PATH, 'assets', 'Trial_Demog_SouthAfrica_3.json'))
a3 = Asset(os.path.join(INPUT_PATH, 'dlls', 'reporter_plugins', 'libcustomreport_TBHIV_ByAge.dll'),
           relative_path='reporter_plugins')
# a3 = Asset(os.path.join(INPUT_PATH, 'dlls', 'reporter_plugins', 'lib_customreport_TBHIV_ReportByAge.so'), relative_path='reporter_plugins')    # SLURM

# a4 = Asset(os.path.join(INPUT_PATH, 'dlls', 'reporter_plugins', 'lib_customreport_TBHIV_ReportByAge.dll'), relative_path='reporter_plugins')

task.common_assets.add_assets([a1, a2, a3])

# [TODO] zdu: set more missing parameter
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

task.set_parameter("Post_Infection_Acquisition_Multiplier", 0.5)

# parameters to set once debugging is done
task.set_parameter('logLevel_default', 'ERROR')
# Disable Default_Reporting
task.set_parameter('Enable_Default_Reporting', 0)  # [TODO]: zdu

exp_name = 'Timing Test'

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
# cb.update_params({'TB_Smear_Negative_Infectivity_Multiplier': 0.34604, 'TB_Presymptomatic_Rate': 0.01165,
#                   'TB_Active_Presymptomatic_Infectivity_Multiplier': 0.34604 * 0.3318}, validate=True)
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
                       'ProviderTestNoR'])  # [TODO] zdu: manually add ['ProviderTestNoR']

task.set_parameter('Custom_Individual_Events',
                   ['TotalPos', 'TBMonitoring', 'Delay', 'Blackout', 'TBTestPreDOTSLow', 'TBTestPreDOTSHigh',
                    'TBDS_Positive',
                    'TBTestDOTSHigh', 'TBTestDOTSLow', 'Seek200', 'Seek350', 'Seek500', 'CRPPosHIVPos',
                    'CRPPosHIVNeg', 'LAMPosHIVPos', 'LAMPosHIVNeg', 'TLAM', 'B100', 'None', 'TruePos',
                    'TruePosHIV', 'B200', 'Bmiddle', 'BCG_Eligible_HIV', 'Disqualify'] + additional_events)

task.set_parameter('TB_MDR_Fitness_Multiplier', 1.0)  # no fitness cost worst case
task.set_parameter('Simulation_Duration', burn_initial + burn_predots + To_end_from_DOTS)
task.set_parameter('Base_Population_Scale_Factor', 1000)

# add reporting
add_tb_report(task, stop_year=2000,
              additional_events=['TLAM', 'TruePos', 'TruePosHIV', 'B200', 'Bmiddle', 'Seek200', 'Seek350', 'Seek500',
                                 'CRPPosHIVNeg', 'CRPPosHIVPos', 'B100', 'LAMPosHIVPos', 'LAMPosHIVNeg',
                                 'HIVTestedNegative', 'HIVTestedPositive', 'TotalPos', 'TBMonitoring'],
              type='Report_TBHIV_ByAge')

# initial TB outbreak
add_tbhiv_outbreak(task, 0.05, 'TB')
task.set_parameter('TB_Slow_Progressor_Rate', 0.007 / 365.0)

# HIV incidence, care seeking, and treatment by guidelines
add_simplehivdiagnostic(task, ['HappyBirthday'], start_day=art_start, treatment_fraction=0.23,
                        property_restrictions_list=['Care_Quality:High'])
add_simplehivdiagnostic(task, ['HappyBirthday'], start_day=art_start, treatment_fraction=0.13,
                        property_restrictions_list=['Care_Quality:Low'])
add_cd4diagnostic(task, ['HIVTestedPositive'], start_day=art_start)

add_HIVIncidence(task, hiv_epidemic_start - 1.0, start_day=hiv_epidemic_start)
add_SimpleHealthSeeking(task, ['Below200'], 'Seek200', seek_200, start_day=art_start, duration=-1)
add_SimpleHealthSeeking(task, ['Below350'], 'Seek350', seek_350_500, start_day=art_start + 3.0 * 365.0, duration=-1)
add_SimpleHealthSeeking(task, ['Below500'], 'Seek500', seek_350_500, start_day=art_start + 6.0 * 365.0, duration=-1)
add_art(task, ['Seek200', 'Seek350', 'Seek500'], start_day=art_start)

# set some drug properties
add_tb_drug_type(task, 'DOTSMDR', 270, 0.5, 0.03, 0, 0.10, 0.02)
add_tb_drug_type(task, 'PreDOTSHigh', 180, 0.5, 0.03, 0, 0.10, 0.02)
add_tb_drug_type(task, 'PreDOTSLow', 180, 0.5, 0.03, 0, 0.10, 0.02)
add_tb_drug_type(task, 'Universal', 90, 0.8, 0.03, 0.02, 0.10, 0.02)

add_SimpleHealthSeeking(task, ['TBActivation', 'TBFailedDrugRegimen', 'TBTestDefault', 'TBTestNegative',
                               'TBMDRTestDefault'],
                        'TBTestDOTSLow', low_seek, start_day=burn_initial,
                        duration=-1, property_restrictions_list=['Care_Quality:Low'])

add_SimpleHealthSeeking(task, ['TBActivation', 'TBFailedDrugRegimen', 'TBTestDefault', 'TBTestNegative',
                               'TBMDRTestDefault'],
                        'TBTestDOTSHigh', high_seek, start_day=burn_initial,
                        duration=-1, property_restrictions_list=['Care_Quality:High'])

add_DiagnosticTreatNeg(task, ['TBTestDOTSHigh'], sens_smear_pos_pre_GH, sens_smear_neg_pre_GH,
                       treatment_fraction=0.8,
                       start_day=burn_initial, duration=burn_predots,
                       property_restrictions_list=['Care_Quality:High'])
add_DiagnosticTreatNeg(task, ['TBTestDOTSLow'], sens_smear_pos_pre_GL, sens_smear_neg_pre_GL,
                       treatment_fraction=0.8,
                       start_day=burn_initial, duration=burn_predots,
                       property_restrictions_list=['Care_Quality:Low'])

add_tbhiv_treat(task, 'PreDOTSLow', ['TBTestPositive'], start_day=burn_initial, duration=burn_predots,
                latent_multiplier=0, property_restrictions_list=['Care_Quality:Low'])

add_tbhiv_treat(task, 'PreDOTSHigh', ['TBTestPositive'], start_day=burn_initial, duration=burn_predots,
                latent_multiplier=0, property_restrictions_list=['Care_Quality:High'])

add_DiagnosticTreatNeg(task, ['TBTestDOTSHigh'], sens_smear_pos_pre_GH, sens_smear_neg_pre_GH, treatment_fraction=0.8,
                       start_day=dots_start, duration=genexpert_introduction - dots_start,
                       property_restrictions_list=['Care_Quality:High'])
add_DiagnosticTreatNeg(task, ['TBTestDOTSLow'], sens_smear_pos_pre_GL, sens_smear_neg_pre_GL, treatment_fraction=0.8,
                       start_day=dots_start, duration=genexpert_introduction - dots_start,
                       property_restrictions_list=['Care_Quality:Low'])

add_Ramp_DiagnosticTreatNeg(task, ['TBTestDOTSHigh'], length_gene_xpert_ramp, sens_smear_pos_GXH, sens_smear_neg_GXH,
                            sens_smear_pos_pre_GH, sens_smear_neg_pre_GH, 0.8, treatment_fraction=0.8,
                            pos_event='ProviderOrdersTBTest', pos_event2='ProviderTestNoR',
                            start_day=genexpert_introduction, duration=-1,
                            property_restrictions_list=['Care_Quality:High'])

add_Ramp_DiagnosticTreatNeg(task, ['TBTestDOTSLow'], length_gene_xpert_ramp, sens_smear_pos_GXL, sens_smear_neg_GXL,
                            sens_smear_pos_pre_GL, sens_smear_neg_pre_GL, 0.8, treatment_fraction=0.8,
                            pos_event='ProviderOrdersTBTest', pos_event2='ProviderTestNoR',
                            start_day=genexpert_introduction, duration=-1,
                            property_restrictions_list=['Care_Quality:Low'])

add_ResistanceDiagnostic(task, ['ProviderOrdersTBTest'], sens_resistance_L, specificity_resistance,
                         neg_event='TBDS_Positive',
                         treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                         start_day=genexpert_introduction, property_restrictions_list=['Care_Quality:Low'])

add_ResistanceDiagnostic(task, ['ProviderOrdersTBTest'], sens_resistance_H, specificity_resistance,
                         neg_event='TBDS_Positive',
                         treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                         start_day=genexpert_introduction, property_restrictions_list=['Care_Quality:High'])

add_ResistanceDiagnostic(task, ['ProviderTestNoR'], sens_resistance_L_clinical, specificity_resistance_clinical,
                         neg_event='TBDS_Positive',
                         treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                         start_day=genexpert_introduction, property_restrictions_list=['Care_Quality:Low'])

add_ResistanceDiagnostic(task, ['ProviderTestNoR'], sens_resistance_H_clinical, specificity_resistance_clinical,
                         neg_event='TBDS_Positive',
                         treatment_fraction=0.5, treatment_fraction_negative_test=1.0,
                         start_day=genexpert_introduction, property_restrictions_list=['Care_Quality:High'])

add_tbhiv_treat(task, 'DOTSHQ', ['TBTestPositive', 'TBDS_Positive'], start_day=dots_start,
                latent_multiplier=0, property_restrictions_list=['Care_Quality:High'])

add_tbhiv_treat(task, 'DOTSLQ', ['TBTestPositive', 'TBDS_Positive'], start_day=dots_start,
                latent_multiplier=0, property_restrictions_list=['Care_Quality:Low'])

add_tbhiv_treat(task, 'DOTSMDR', ['TBMDRTestPositive'], start_day=dots_start,
                latent_multiplier=0)

from idmtools.builders import SimulationBuilder
from emodpy.emod_task import EMODTask
from functools import partial

fs1 = [ModFn(partial(EMODTask.set_parameter_sweep_callback, param="Run_Number", value=g)) for g in range(0, 10)]
fs2 = [ModFn(setprimaryHIVpro, v) for v in [1.5]]  # [TODO] zdu: these methods need to take simulation as input!!
fs3 = [ModFn(setHIVslow, v) for v in [4]]
fs4 = [ModFn(Add_Drugs, d) for d in [0.0]]
fs5 = [ModFn(setCoinfDeath, dd) for dd in [1.2e-3]]
fs6 = [ModFn(ModifyInfectivity, v) for v in [0.030]]

builder = SimulationBuilder()
builder.sweeps.append(fs1)
builder.sweeps.append(fs2)
builder.sweeps.append(fs3)
builder.sweeps.append(fs4)
builder.sweeps.append(fs5)
builder.sweeps.append(fs6)
builder.count = len(fs1) * len(fs2) * len(fs3) * len(fs4) * len(fs5) * len(fs6)

from idmtools.entities.templated_simulation import TemplatedSimulations

ts = TemplatedSimulations(base_task=task)
ts.add_builder(builder)

# builder.tags.update({'Simulation_Duration': cb.get_param('Simulation_Duration')})
# builder.tags.update({'x_Other_Mortality': cb.get_param('x_Other_Mortality')})
# builder.tags.update({'TB_Smear_Negative_Infectivity_Multiplier':
#                          cb.get_param('TB_Smear_Negative_Infectivity_Multiplier'),
#                      'TB_Presymptomatic_Rate': cb.get_param('TB_Presymptomatic_Rate'),
#                      'TB_Active_Presymptomatic_Infectivity_Multiplier': cb.get_param(
#                          'TB_Active_Presymptomatic_Infectivity_Multiplier'),
#                      'Base_Population_Scale_Factor': cb.get_param('Base_Population_Scale_Factor')})
# builder.tags.update({'low_seek': low_seek})

ts.tags.update({'Simulation_Duration': task.get_parameter('Simulation_Duration')})
ts.tags.update({'x_Other_Mortality': task.get_parameter('x_Other_Mortality')})
ts.tags.update({'TB_Smear_Negative_Infectivity_Multiplier':
                    task.get_parameter('TB_Smear_Negative_Infectivity_Multiplier'),
                'TB_Presymptomatic_Rate': task.get_parameter('TB_Presymptomatic_Rate'),
                'TB_Active_Presymptomatic_Infectivity_Multiplier': task.get_parameter(
                    'TB_Active_Presymptomatic_Infectivity_Multiplier'),
                'Base_Population_Scale_Factor': task.get_parameter('Base_Population_Scale_Factor')})
ts.tags.update({'low_seek': low_seek})

# run_sim_args = {
#     'exp_name': exp_name,
#     'config_builder': cb,
#     'exp_builder': builder
# }

if __name__ == "__main__":
    # SetupParser.init()
    # exp_manager = ExperimentManagerFactory.from_cb(cb)
    # exp_manager.run_simulations(**run_sim_args)

    from idmtools.core.platform_factory import Platform
    platform = Platform('COMPS2')  # SLURM

    # from idmtools.entities.templated_simulation import TemplatedSimulations
    from idmtools.entities.experiment import Experiment

    #
    # ts = TemplatedSimulations(base_task=task)
    # ts.add_builder(builder)

    exp_name = 'Timing Test idm 1'  # [TODO] zdu: test with simple name
    experiment = Experiment(name=exp_name)

    # create mixed experiment from two templates
    experiment.simulations = ts

    # run experiment
    experiment.run(platform=platform)
