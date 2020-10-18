# Example calibration using IMIS (Incremental Mixture Importance Sampling) algorithm.
# Execute directly: 'python example_IMIS_dynamic_config.py'

import os
import copy
from itertool.calib_manager import CalibManager
from itertool.prior import MultiVariatePrior
from itertool.algorithms.imis import IMIS
from itertool.algorithms.optim_tool import OptimTool
from itertool.plotters.likelihood_plotter import LikelihoodPlotter
from itertool.plotters.optim_tool_plotter import OptimToolPlotter
from itertool.plotters.site_data_plotter import SiteDataPlotter
from itertool.utilities.vector import params as vector_params
from malaria import params as malaria_params
from malaria.study_sites.dielmo_calib_site import DielmoCalibSite
from malaria.study_sites.ndiop_calib_site import NdiopCalibSite
from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy.interventions.emod_empty_campaign import EMODEmptyCampaign
from itertool.utilities.helper import generate_default_config_from_exe

CURRENT_DIRECTORY = os.path.dirname(__file__)
INPUT_PATH = os.path.join('..', 'inputs')
INPUT_PATH = os.path.abspath(INPUT_PATH)

# Generate default config from Eradication.exe
exe_path, schema_path, config_path = generate_default_config_from_exe(os.path.join(INPUT_PATH, "bamboo"),
                                                         EradicationBambooBuilds.CI_MALARIA)

demographics_path = os.path.join(INPUT_PATH, "demographics", "birth_cohort_demographics.compiled.json")

# Create task
task = EMODTask.from_files(
    eradication_path=exe_path,
    config_path=config_path,
    demographics_paths=demographics_path
)

# Select a campaign
task.campaign = EMODEmptyCampaign.campaign()

# rRemove parameter
task.config.pop("Serialized_Population_Filenames")

# Update related parameters
task.update_parameters(vector_params.params)  # "Vector_Species_Params" is required
task.update_parameters(malaria_params.params)  # 'Maternal_Antibody_Protection' is required

# Make sure we have the right type
task.set_parameter("Simulation_Type", "MALARIA_SIM")  # default is GENERIC_SIM
task.set_parameter("Incubation_Period_Distribution", "CONSTANT_DISTRIBUTION")  # default is NOT_INITIALIZED
task.set_parameter("Climate_Update_Resolution", "CLIMATE_UPDATE_DAY")  # default is CLIMATE_UPDATE_YEAR

# Update required parameters
task.set_parameter("Custom_Individual_Events", ["Received_Treatment"])  # default has []
task.set_parameter("Insecticides", [])  # in schema without default value; not in default config
task.set_parameter("Load_Balance_Filename", "")

task.set_parameter("Custom_Coordinator_Events", [])
task.set_parameter("Custom_Node_Events", [])
task.set_parameter("Enable_Climate_Stochasticity", 0)
task.set_parameter("Enable_Demographics_Risk", 0)
task.set_parameter("Incubation_Period_Constant", 25)

sites = [
    DielmoCalibSite()
]

prior = MultiVariatePrior.by_range(
    Antigen_Switch_Rate_LOG=('linear', -10, -8),
    # Base_Gametocyte_Production_Rate=('log', 0.001, 0.5),
    # Falciparum_MSP_Variants=('linear_int', 5, 50),
    # Falciparum_Nonspecific_Types=('linear_int', 5, 100),
    # Falciparum_PfEMP1_Variants=('linear_int', 900, 1700),
    # Gametocyte_Stage_Survival_Rate=('linear', 0.5, 0.95),
    # MSP1_Merozoite_Kill_Fraction=('linear', 0.4, 0.7),
    # Max_Individual_Infections=('linear_int', 3, 8),
    # Nonspecific_Antigenicity_Factor=('linear', 0.1, 0.9)
)

plotters = [
    LikelihoodPlotter(combine_sites=True),
    SiteDataPlotter(combine_sites=True)
]


def sample_point_fn(simulation, sample_dimension_values):
    """
    A simple example function that takes a list of sample-point values
    and sets parameters accordingly using the sample-dimension names from the prior.
    Note that more complicated logic, e.g. setting campaign event coverage or habitat abundance by species,
    can be encoded in a similar fashion using custom functions rather than the generic "set_param" or "update_params".
    """

    # TODO: reconcile variable names with Pull Request #687/#733, i.e. function accepts one row of sample_point_table?
    sample_point = prior.to_dict(sample_dimension_values)  # aligns names and values; rounds integer-range_type params

    params_to_update = dict()
    params_to_update['Simulation_Duration'] = 365 * 5 + 1  # shorter for quick test

    for sample_dimension_name, sample_dimension_value in sample_point.items():
        # Apply specific logic to convert sample-point dimensions into simulation configuration parameters
        if '_LOG' in sample_dimension_name:
            param_name = sample_dimension_name.replace('_LOG', '')
            params_to_update[param_name] = pow(10, sample_dimension_value)
        else:
            params_to_update[sample_dimension_name] = sample_dimension_value

    simulation.task.update_parameters(params_to_update)
    return params_to_update


next_point_kwargs = dict(initial_samples=4,
                         samples_per_iteration=2,
                         n_resamples=100)

calib_manager = CalibManager(name='IMIS_default_config',
                             task=task,
                             map_sample_to_model_input_fn=sample_point_fn,
                             sites=sites,
                             next_point=IMIS(prior, **next_point_kwargs),
                             sim_runs_per_param_set=1,
                             max_iterations=2,
                             plotters=plotters)

run_calib_args = {'calib_manager': calib_manager}

if __name__ == "__main__":
    from idmtools.core.platform_factory import Platform
    platform = Platform('COMPS2')
    calib_manager.platform = platform
    calib_manager.run_calibration()
