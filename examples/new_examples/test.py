import os
import sys

from emodpy.emod_task import EMODTask
from idmtools.assets import AssetCollection, Asset
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations

CURRENT_DIRECTORY = os.path.dirname(__file__)
INPUT_PATH = os.path.join('Assets')
INPUT_PATH = os.path.abspath(INPUT_PATH)

exe_path = os.path.join(INPUT_PATH, "Eradication")
demo_path = os.path.join(INPUT_PATH, "demographics.json")
task = EMODTask.from_files(
    eradication_path=exe_path,
    config_path='my_config.json',
    campaign_path='campaign.json',
    demographics_paths=demo_path
)
task.use_embedded_python=True
platform = Platform('CALCULON', node_group='idm_48cores', priority='Highest')  # switch to BELEGOST with platform = Platform('BELEGOST')
env = platform.environment
task.is_linux = False if env.lower() == 'belegost' or env.lower() == 'bayesian' else True
task.transient_assets.add_asset("custom_reports.json")
pathed_asset = Asset(os.path.join(INPUT_PATH, 'python', 'dtk_post_process.py'), relative_path="python")
task.common_assets.add_asset(pathed_asset)
exp_name = os.path.split(sys.argv[0])[1]

# ts = TemplatedSimulations(base_task=task)
# b = SimulationBuilder()
# #b.add_sweep_definition(replace_something, (.1, .2, .5, .7))
# ts.add_builder(b)

experiment = Experiment.from_task(task, name=exp_name)

other_assets = AssetCollection.from_id("6550b0a2-8b3b-eb11-a2dd-c4346bcb7271", as_copy=True)
experiment.assets.add_assets(other_assets)
experiment.run()
