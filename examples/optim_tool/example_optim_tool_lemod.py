# Example calibration using OtimTool algorithm for Light EMOD (lemod).
# Execute directly: 'python example_optim_tool_lemod.py'

"""
Requires idmtools, idmtools_calibra, and (currently for minor reasons) emodpy to be installed, e.g.:
<activate virtual environment>
cd
pip install idmtools[full] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
git clone https://github.com/InstituteforDiseaseModeling/idmtools_calibra.git
cd idmtools_calibra
python setup.py develop
pip install emodpy --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
"""

from dataclasses import dataclass, field
from functools import partial

import os
import copy
from typing import Optional

from idmtools.assets import AssetCollection
from idmtools.entities import CommandLine
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

from idmtools_calibra.analyzers.base_calibration_analyzer import BaseCalibrationAnalyzer
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.calib_site import CalibSite
from idmtools_calibra.algorithms.optim_tool import OptimTool
from idmtools_calibra.plotters.likelihood_plotter import LikelihoodPlotter
from idmtools_calibra.plotters.optim_tool_plotter import OptimToolPlotter
from idmtools_calibra.plotters.site_data_plotter import SiteDataPlotter
from emodpy.emod_task import EMODTask
from idmtools.core.platform_factory import Platform

#
# Run environment controls
#

# Where to run the calibration simulations. Only CALCULON for now.
LOCALE = 'CALCULON'
# The asset collection id of the singularity environment to run the simulations in on Calculon.
ENVIRONMENT_ASSET_COLLECTION_ID = '6197d2a5-f234-eb11-a2dd-c4346bcb7271'
# This is a directory containing directories/files (executable, inputs) that will be needed by the simulations
INPUT_DIR = os.path.join('..', '..', '..', 'idmtools', 'examples', 'python_model', 'inputs', 'lemod', 'Assets')

#
# Calibration controls
#

# The number of parameter sets/samples to run in each calibration iteration
N_SAMPLES = 3
# number of randomly seeded simulations per parameter set/sample (dummy analyzer cannot handle > 1)
N_REPLICATES = 1
# the number of times the algorithm will attempt to optimize the best-guess parameterization
N_ITERATIONS = 2
# Calibration state/results will be kept in a directory by this name in the same directory as this file
CALIBRATION_NAME = 'Optimtool_lemod_development'

"""
Calibration parameter specification

Name: Human readable name of the parameter to utilize
Dynamic: True/False, whether this parameter can be altered by the calibration (False still overrides input files)
MapTo: actual model name to use. If not specified, the map_sample_to_model_input method below will have to handle
    the (more complicated) mapping of this parameter to actual model parameter(s)
Guess: Initial value for parameter in calibration
Min: The minimum value the parameter can be in the calibration (if Dynamic is True) (required even if not Dynamic)
Max: The maximum value the parameter can be in the calibration (if Dynamic is True) (required even if not Dynamic)
"""
CALIBRATION_PARAMETERS = [
    {
        'Name': "Postpartum infecund 6-11 months",
        'Dynamic': False,
        'MapTo': "postpartum_infecund_6-11",
        'Guess': 0.25,
        'Min': 0.2,
        'Max': 0.3
    },
    {
        'Name': 'Abortion probability',
        'Dynamic': True,
        'MapTo': 'abortion_prob',
        'Guess': 0.1,
        'Min': 0.05,
        'Max': 0.15

    }
]



platform = Platform(LOCALE)


# REAL task class for overriding command generation behavior for python tasks in singularity
# (may need some refining for commit to be nicer).
@dataclass
class SingularityJSONConfiguredPythonTask(JSONConfiguredPythonTask):
    provided_command: Optional[CommandLine] = field(default_factory=lambda: CommandLine(), metadata={"md": True})

    def pre_creation(self, parent, platform):
        super().pre_creation(parent=parent, platform=platform)
        self.command = self.provided_command


# dummy stand-in for real analyzers for exercising the calibration harness
class TestAnalyzer(BaseCalibrationAnalyzer):
    def __init__(self, channel, reference_data):
        self.channel = channel
        super().__init__(reference_data=reference_data)

    def map(self, data, item):
        # ck4, TODO: 1/28/2021 make the map return result depend on reference data
        import random
        return [random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)]

    def reduce(self, all_data):
        # ck4, TODO: 1/28/2021 group all_data by sample, compute scores on a per-sample basis (e.g. 5 samples -> 5 result values
        result = []
        for item, value in all_data.items():
            result.append(sum(value))  # dummy operation
        return result


# dummy stand-in for real calibration site for exercising the calibration harness
class FPSite(CalibSite):
    reference_dict = {
        'test1': [1, 2, 3],
        'test2': [10, 20, 30]
    }

    def get_reference_data(self, reference_type):
        """
        Callback function for derived classes to pass site-specific reference data
        that is requested by analyzers by the relevant reference_type.
        """
        return self.reference_dict[reference_type]

    def get_analyzers(self):
        """
        Derived classes return a list of BaseComparisonAnalyzer instances
        that have been passed a reference to the CalibSite for site-specific analyzer setup.
        """
        return [TestAnalyzer(channel='test1', reference_data=self.reference_dict['test1']),
                TestAnalyzer(channel='test2', reference_data=self.reference_dict['test2'])]

    def get_setup_functions(self):
        """
        Derived classes return a list of functions to apply site-specific modifications to the base configuration.
        These are combined into a single function using the SiteFunctions helper class in the CalibSite constructor.
        """
        return []


command = CommandLine("singularity exec ./Assets/fp_lemod-0.1.sif python3 Assets/run_senegal.py %s" % LOCALE)
assets = AssetCollection.from_directory(INPUT_DIR)
assets.add_assets(AssetCollection.from_id(item_id=ENVIRONMENT_ASSET_COLLECTION_ID))
task = SingularityJSONConfiguredPythonTask(script_path=os.path.join(INPUT_DIR, "run_senegal.py"),
                                           common_assets=assets,
                                           provided_command=command)

# List of site we want to calibrate on
sites = [FPSite(name='Senegal')]

# The default plotters used in an Optimization with OptimTool
plotters = [LikelihoodPlotter(combine_sites=True),
            SiteDataPlotter(num_to_plot=5, combine_sites=True),
            OptimToolPlotter()  # OTP must be last because it calls gc.collect()
            ]


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
    Args:
        sample: The sample coming from the next point algorithm

    Returns: The sample with constrained values

    """
    # Convert Falciparum MSP Variants to nearest integer
    if 'Min Days Between Clinical Incidents' in sample:
        sample['Min Days Between Clinical Incidents'] = int(round(sample['Min Days Between Clinical Incidents']))

    if 'Falciparum PfEMP1 Variants' in sample:
        sample['Falciparum PfEMP1 Variants'] = int(round(sample['Falciparum PfEMP1 Variants']))

    return sample


def map_sample_to_model_input(simulation, sample):
    """
    This method maps the samples generated by the next point algorithm to the model inputs (represented here by the cb).
    It is important to note that the sample may be shared by several isntances of this function.
    Therefore it is important to deepcopy the sample at the beginning if we intend to modify it (by calling .pop() for example).
       sample = copy.deepcopy(sample)
    All parameters specified for dynamic calibration (above) that do not have a MapTo value must have associated mapping
        logic in this method.
    Args:
        simulation: idmtool simulation
        sample: The sample containing a values for all the params. e.g. {'Clinical Fever Threshold High':1, ... }

    Returns: A dictionary containing the tags that will be attached to the simulation
    """

    tags = {}
    # Make a copy of samples so we can alter it safely
    sample = copy.deepcopy(sample)

    # Can perform custom mapping, e.g. a trivial example
    if 'Clinical Fever Threshold High' in sample:
        value = sample.pop('Clinical Fever Threshold High')
        tags.update(simulation.task.set_parameter('Clinical_Fever_Threshold_High', value))

    for p in CALIBRATION_PARAMETERS:
        if 'MapTo' in p:
            if p['Name'] not in sample:
                print('Warning: %s not in sample, perhaps resuming previous iteration' % p['Name'])
                continue
            value = sample.pop(p['Name'])
            tags.update(simulation.task.set_parameter(p['MapTo'], value))

    for name, value in sample.items():
        print('UNUSED PARAMETER:' + name)
    assert (len(sample) == 0)  # All params used

    # # For testing only, the duration should be handled by the site !! Please remove before running in prod!
    # tags.update(simulation.task.set_parameter("Simulation_Duration", 365 + 1))

    return tags


# Just for fun, let the numerical derivative baseline scale with the number of dimensions
volume_fraction = 0.01  # desired fraction of N-sphere area to unit cube area for numerical derivative (automatic radius scaling with N)
n_dynamic_parameters = len([p for p in CALIBRATION_PARAMETERS if p['Dynamic']])

if n_dynamic_parameters == 0:
    warning_note = \
        """
        /!\\ WARNING /!\\ the OptimTool requires at least one of params with Dynamic set to True. Exiting...                  
        """
    print(warning_note)
    exit()

r = OptimTool.get_r(n_dynamic_parameters, volume_fraction)

optimtool = OptimTool(CALIBRATION_PARAMETERS,
                      constrain_sample,  # <-- WILL NOT BE SAVED IN ITERATION STATE
                      mu_r=r,
                      # <-- radius for numerical derivatve.  CAREFUL not to go too small with integer parameters
                      sigma_r=r / 10.,  # <-- stdev of radius
                      center_repeats=1,
                      # <-- Number of times to replicate the center (current guess).  Nice to compare intrinsic to extrinsic noise
                      samples_per_iteration=N_SAMPLES
                      # <-- Samples per iteration, includes center repeats.  Actual number of sims run is this number times number of replicates.
                      )

calib_manager = CalibManager(name=CALIBRATION_NAME,  # <-- Please customize this name
                             task=task,
                             map_sample_to_model_input_fn=map_sample_to_model_input,
                             sites=sites,
                             next_point=optimtool,
                             sim_runs_per_param_set=N_REPLICATES,  # <-- Replicates
                             max_iterations=N_ITERATIONS,  # <-- Iterations
                             plotters=plotters)#,
                             # map_replicates_callback=partial(EMODTask.set_parameter_sweep_callback, param="Run_Number"))

run_calib_args = {
    "calib_manager": calib_manager
}

if __name__ == "__main__":
    calib_manager.platform = platform
    calib_manager.run_calibration()
