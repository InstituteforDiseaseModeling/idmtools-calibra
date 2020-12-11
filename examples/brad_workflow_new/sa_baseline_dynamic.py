#!/usr/bin/env python
import json
import pathlib  # for a join
import shutil
import os
import sys
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
    RequirementsToAssetCollection
from idmtools_models.templated_script_task import get_script_wrapper_unix_task

# emodpy
from emodpy.emod_task import EMODTask
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files
from emodpy.reporters.custom import Report_TBHIV_ByAge

import emod_api.campaign as camp

import params
import set_config
import manifest

# ****************************************************************
# Features to support:
#
#  Read experiment info from a json file
#  Add Eradication.exe as an asset (Experiment level)
#  Add Custom file as an asset (Simulation level)
#  Add the local asset directory to the task
#  Use builder to sweep simulations
#  How to run dtk_pre_process.py as pre-process
#  Save experiment info to file
# ****************************************************************
from examples.helper import generate_default_config_from_exe, download_reporter
from idmtools_calibra.utilities.mod_fn import ModFn

from tb.add_tb_drug_type import add_tb_drug_type, add_tb_drug


def update_sim_bic(simulation, value):
    simulation.task.config.parameters.Base_Infectivity_Constant = value * 0.1
    return {"Base_Infectivity": value}


def update_sim_random_seed(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def cpr_sens_spec(camp, sensCRP, specCRP):
    import emodpy_tbhiv.interventions.active_diagnostic as ad
    camp.add(ad.ActiveDiagnostic(camp, ['HIVTestedNegative'], sensCRP, specCRP, pos_event='CRPPosHIVNeg', start_day=params.intervention_day))
    camp.add(ad.ActiveDiagnostic(camp, ['HIVTestedPositive'], sensCRP, specCRP, pos_event='CRPPosHIVPos', start_day=params.intervention_day))
    return camp


def add_drugs(simulation, resist_pro):
    add_tb_drug_type(simulation.task, 'DOTSHQ', 180.0, 0.8, 0.03, resist_pro, 0.10, 0.02, mdr_cure_proportion=0.1)
    add_tb_drug_type(simulation.task, 'DOTSLQ', 180.0, 0.5, 0.03, resist_pro, 0.10, 0.02, mdr_cure_proportion=0.1)
    return {'ResistancePro': resist_pro}


def print_params():
    """
    Just a useful convenience function for the user.
    """
    # Display exp_name and nSims
    # TBD: Just loop through them
    print("exp_name: ", params.exp_name)
    print("nSims: ", params.nSims)


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


def build_camp():
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

    # cpr_sens_spec(camp, params.CRP_Sensitivity, params.CRP_Specificity)

    return camp


def build_demog():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    import emodpy_tbhiv.demographics.TBHIVDemographics as Demographics  # OK to call into emod-api
    import emod_api.demographics.DemographicsTemplates as DT

    # demog = Demographics.fromBasicNode( lat=0, lon=0, pop=10000, name=1, forced_id=1 )
    demog = Demographics.fromData(pop=10000, filename_male=manifest.males, filename_female=manifest.females)

    return demog


# Parameter setting functions
def set_run_number(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {'Run_Number': value}


def set_hiv_slow(simulation, pro):
    # this is very breakable right now
    tmp_loc = []
    for i, val in enumerate(simulation.task.config.parameters.TB_CD4_Activation_Vector):
        if i < 3:
            tmp_loc += [pro * val]
        else:
            tmp_loc += [val]
    simulation.task.config.parameters.TB_CD4_Activation_Vector = tmp_loc
    return {'TB_CD4_Activation_Vector': tmp_loc}


def set_primary_hiv_pro(simulation, pro):
    # this is very breakable right now
    tmp_loc = []
    for i, val in enumerate(simulation.task.config.parameters.TB_CD4_Primary_Progression):
        tmp_loc += [pro * val]
    simulation.task.config.parameters.TB_CD4_Primary_Progression = tmp_loc
    return {'TB_CD4_Primary_Progression': tmp_loc}


def set_coinf_death(simulation, rate):
    simulation.task.config.parameters.CoInfection_Mortality_Rate_Off_ART = rate
    return {'CoInfection_Mortality_Rate_Off_ART': rate}


def modify_infectivity(simulation, infectivity):
    simulation.task.config.parameters.Base_Infectivity_Constant = infectivity
    return {'Base_Infectivity': infectivity}


def update_more_config(task):
    task.config.parameters.Demographics_Filenames = ["Trial_Demog_SouthAfrica_3.json",
                                                     'Base_Overlay_SouthAfrica_ReVacc.json']

    task.config.parameters.x_Other_Mortality = 0.34
    task.config.parameters.x_Birth = 1.43

    task.config.parameters.TB_MDR_Fitness_Multiplier = 1.0  # no fitness cost worst case
    task.config.parameters.Simulation_Duration = (params.burn_initial + params.burn_predots + params.To_end_from_DOTS)

    return task


# not needed, but if you want to read drug params from file, this is the way to do it
def set_tbhiv_drup_params_from_file(config, manifest):
    import emod_api.config.default_from_schema_no_validation as dfs

    tbhivdp_map = {}
    with open("drug.json") as f:
        data = json.load(f)
        drugs_key = list(data['TBHIV_Drug_Params'])
        drugs = data['TBHIV_Drug_Params']
        for drug_key, drug_value in drugs.items():
            tbhivdp = dfs.schema_to_config_subnode(manifest.schema_file, ["config", "TBHIV_SIM", "TBHIV_Drug_Params",
                                                                          "<tb_drug_name_goes_here>"])
            for k, v in drug_value.items():
                setattr(tbhivdp.parameters, k, v)
            tbhivdp.parameters.finalize()
            tbhivdp_map[drug_key] = tbhivdp.parameters

    config.parameters.TBHIV_Drug_Params = tbhivdp_map


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


def general_sim(erad_path, ep4_scripts):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    # print_params()

    # Create a platform
    # Show how to dynamically set priority and node_group
    platform = Platform("CALCULON")

    pl = RequirementsToAssetCollection(platform, requirements_path=manifest.requirements)

    # create EMODTask 
    print("Creating EMODTask (from files)...")
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

    report.asset_dir = manifest.plugins_folder

    task = EMODTask.from_default2(
        config_path='my_config.json',
        eradication_path=manifest.eradication_path,
        campaign_builder=build_camp,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        demog_builder=None,
        # here we already loaded demo files to Assets and add filename to config's Demographics_Filenames
        plugin_report=None
    )
    print("Adding asset dir...")
    task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)

    update_more_config(task)

    add_tb_drug(task, 'ACFDOTS')
    add_tb_drug_type(task, 'DOTSMDR', 270, 0.5, 0.03, 0, 0.10, 0.02)
    add_tb_drug_type(task, 'PreDOTSHigh', 180, 0.5, 0.03, 0, 0.10, 0.02)
    add_tb_drug_type(task, 'PreDOTSLow', 180, 0.5, 0.03, 0, 0.10, 0.02)
    add_tb_drug_type(task, 'Universal', 90, 0.8, 0.03, 0.02, 0.10, 0.02)
    # Set task.campaign to None to not send any campaign to comps since we are going to override it later with
    # dtk-pre-process.
    print("Adding local assets (py scripts mainly)...")

    if ep4_scripts is not None:
        for asset in ep4_scripts:
            pathed_asset = Asset(pathlib.PurePath.joinpath(manifest.ep4_path, asset), relative_path="python")
            task.common_assets.add_asset(pathed_asset)

    # Create simulation sweep with builder
    fs1 = [ModFn(set_run_number, value=g) for g in range(0, 10)]
    fs2 = [ModFn(set_primary_hiv_pro, v) for v in [1.5]]
    fs3 = [ModFn(set_hiv_slow, v) for v in [4]]
    fs4 = [ModFn(add_drugs, d) for d in [0.0]]
    fs5 = [ModFn(set_coinf_death, dd) for dd in [1.2e-3]]
    fs6 = [ModFn(modify_infectivity, v) for v in [0.030]]

    builder = SimulationBuilder()
    builder.sweeps.append(fs1)
    builder.sweeps.append(fs2)
    builder.sweeps.append(fs3)
    builder.sweeps.append(fs4)
    builder.sweeps.append(fs5)
    builder.sweeps.append(fs6)
    builder.add_sweep_definition(update_sim_random_seed, range(params.nSims))
    builder.count = len(fs1) * len(fs2) * len(fs3) * len(fs4) * len(fs5) * len(fs6)

    ts = TemplatedSimulations(base_task=task)
    ts.add_builder(builder)

    ts.tags.update({'Simulation_Duration': task.config.parameters.Simulation_Duration})
    ts.tags.update({'x_Other_Mortality': task.config.parameters.x_Other_Mortality})
    ts.tags.update({'TB_Smear_Negative_Infectivity_Multiplier':
                        task.config.parameters.TB_Smear_Negative_Infectivity_Multiplier,
                    'TB_Presymptomatic_Rate': task.config.parameters.TB_Presymptomatic_Rate,
                    'TB_Active_Presymptomatic_Infectivity_Multiplier': task.config.parameters.TB_Active_Presymptomatic_Infectivity_Multiplier})
    # 'Base_Population_Scale_Factor': task.config.parameters.Base_Population_Scale_Factor})  # not in schema
    ts.tags.update({'low_seek': params.low_seek})

    # create experiment from builder
    print(f"Prompting for COMPS creds if necessary...")
    exp_name = os.path.split(sys.argv[0])[1]
    experiment = Experiment.from_template(ts, name=exp_name)

    ac = pl.run()
    other_assets = AssetCollection.from_id(ac, as_copy=True)
    experiment.assets.add_assets(other_assets)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        exit()

    print(f"Experiment {experiment.uid} succeeded.")

    # Save experiment id to file
    with open("COMPS_ID", "w") as fd:
        fd.write(experiment.uid.hex)
    print()
    print(experiment.uid.hex)


def run_test(erad_path):
    general_sim(erad_path, manifest.my_ep4_assets)


if __name__ == "__main__":
    # TBD: user should be allowed to specify (override default) erad_path and input_path from command line
    plan = EradicationBambooBuilds.TBHIV
    print("Retrieving Eradication and schema.json from Bamboo...")
    get_model_files(plan, manifest)
    print("...done.")
    run_test(manifest.eradication_path)
