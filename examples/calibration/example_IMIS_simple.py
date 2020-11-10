# Example calibration using IMIS (Incremental Mixture Importance Sampling) algorithm.
# Execute directly: 'python example_IMIS_simple.py'

import os
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.prior import MultiVariatePrior
from idmtools_calibra.algorithms.imis import IMIS
from idmtools_calibra.plotters.likelihood_plotter import LikelihoodPlotter
from idmtools_calibra.plotters.site_data_plotter import SiteDataPlotter
from malaria.study_sites.dielmo_calib_site import DielmoCalibSite
from emodpy.emod_task import EMODTask
from idmtools_calibra.utilities.helper import download_bamboo_exe

CURRENT_DIRECTORY = os.path.dirname(__file__)
INPUT_PATH = os.path.join('..', 'inputs')
INPUT_PATH = os.path.abspath(INPUT_PATH)

# Test latest bamboo Eradication.exe (it won't download if exists already)
exe_path = download_bamboo_exe(os.path.join(INPUT_PATH, 'bamboo'))
config_path = os.path.join(INPUT_PATH, "config.json")
campaign_path = os.path.join(INPUT_PATH, "empty_campaign.json")
demographics_path = os.path.join(INPUT_PATH, "demographics", "birth_cohort_demographics.compiled.json")

# Create task
task = EMODTask.from_files(
    eradication_path=exe_path,
    config_path=config_path,
    campaign_path=campaign_path,
    demographics_paths=demographics_path
)

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

calib_manager = CalibManager(name='IMIS_simple',
                             task=task,
                             map_sample_to_model_input_fn=sample_point_fn,
                             sites=sites,
                             next_point=IMIS(prior, **next_point_kwargs),
                             sim_runs_per_param_set=1,
                             max_iterations=3,
                             plotters=plotters)

run_calib_args = {'calib_manager': calib_manager}

if __name__ == "__main__":
    from idmtools.core.platform_factory import Platform
    platform = Platform('COMPS2')
    calib_manager.platform = platform
    calib_manager.run_calibration()
