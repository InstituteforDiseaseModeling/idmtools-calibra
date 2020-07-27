import copy
import json
import os
from dataclasses import dataclass, field
from functools import partial
from logging import getLogger
from typing import Union, NoReturn, Optional, Any, Dict, List
from urllib.parse import urlparse
from emodpy.utils import download_eradication
from idmtools import IdmConfigParser
from idmtools.assets import Asset
from idmtools.assets import AssetCollection
from idmtools.entities.command_line import CommandLine
from idmtools.entities.itask import ITask
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification
from idmtools.utils.json import load_json_file
from emodpy import IEMODDefault
from emodpy.emod_file import ClimateFiles, DemographicsFiles, MigrationFiles
from emodpy.emod_campaign import EMODCampaign
from emodpy.interventions import EMODEmptyCampaign
from emodpy.reporters import Reporters

logger = getLogger(__name__)


@dataclass()
class EMODTask(ITask):
    """
    EMODTask allows easy running and configuration of EMOD Experiments and Simulations
    """
    # Experiment Level Assets
    #: Eradication path. Can also be set through config file
    eradication_path: str = field(default=None, compare=False, metadata={"md": True})
    #: Are we using a pre 2.20 Eradication binary. Add a semicolon to the --input-path argument of Eradiction
    legacy_exe: bool = field(default=False, metadata={"md": True})
    #: Common Demographics
    demographics: DemographicsFiles = field(default_factory=lambda: DemographicsFiles('demographics'))
    #: Common Migrations
    migrations: MigrationFiles = field(default_factory=lambda: MigrationFiles('migrations'))
    #: Common Reports
    reporters: Reporters = field(default_factory=lambda: Reporters())
    #: Common Climate
    climate: ClimateFiles = field(default_factory=lambda: ClimateFiles())

    # Simulation Level Configuration objects and files
    #: Represents config.jon
    config: dict = field(default_factory=lambda: {})
    #: Campaign configuration
    campaign: EMODCampaign = field(default_factory=lambda: EMODEmptyCampaign.campaign())
    #: Simulation level demographics such as overlays
    simulation_demographics: DemographicsFiles = field(default_factory=lambda: DemographicsFiles())
    #: Simulation level migrations
    simulation_migrations: MigrationFiles = field(default_factory=lambda: MigrationFiles())

    #: Add --python-script-path to command line
    use_embedded_python: bool = False
    is_linux: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.executable_name = "Eradication.exe"
        if self.eradication_path is not None:
            self.executable_name = os.path.basename(self.eradication_path)
            if urlparse(self.eradication_path).scheme in ('http', 'https',):
                self.eradication_path = download_eradication(self.eradication_path)
            self.eradication_path = os.path.abspath(self.eradication_path)
        else:
            eradication_path = IdmConfigParser().get_option("emodpy", "eradication_path")
            if eradication_path:
                self.eradication_path = eradication_path
                self.executable_name = os.path.basename(self.eradication_path)

    @classmethod
    def from_default(cls, default: IEMODDefault, eradication_path: str = None, **kwargs) -> 'EMODTask':
        """
        Create a task from Defaults

        Args:
            default: Default set to use
            eradication_path: Path to Eradication binary

        Returns:

        """
        task = cls(eradication_path=eradication_path, **kwargs)

        # Add the demographics
        for filename, content in default.demographics().items():
            task.demographics.add_demographics_from_dict(content=content, filename=filename)

        task.config = default.config()
        task.campaign = default.campaign()

        return task

    @classmethod
    def from_files(cls, eradication_path=None, config_path=None, campaign_path=None, demographics_paths=None,
                   custom_reports_path=None, asset_path=None, **kwargs):
        """
        Load custom |EMOD_s| files when creating :class:`EMODTask`.

        Args:
            asset_path: If an asset path is passed, the climate, dlls, and migrations will be searched there
            eradication_path: The eradication.exe path.
            config_path: The custom configuration file.
            campaign_path: The custom campaign file.
            demographics_paths: The custom demographics files (single file or a list).
            custom_reports_path: Custom reports file

        Returns: An initialized experiment
        """
        # Create the experiment
        task = cls(eradication_path=eradication_path, **kwargs)

        # Load the files
        task.load_files(config_path=config_path, campaign_path=campaign_path, demographics_paths=demographics_paths,
                        custom_reports_path=custom_reports_path, asset_path=asset_path)

        return task

    def load_files(self, config_path=None, campaign_path=None, custom_reports_path=None, demographics_paths=None,
                   asset_path=None) -> NoReturn:
        """
        Load files in the experiment/base_simulation.

        Args:
            asset_path: Path to find assets
            config_path: Configuration file path
            campaign_path: Campaign file path
            demographics_paths: Demographics file path
            custom_reports_path: Path for the custom reports file

        """
        if config_path:
            self.config = load_json_file(config_path)["parameters"]

        if campaign_path:
            self.campaign = EMODCampaign.load_from_file(campaign_path)

        if demographics_paths:
            for demog_path in [demographics_paths] if isinstance(demographics_paths, str) else demographics_paths:
                self.demographics.add_demographics_from_file(demog_path)

        if custom_reports_path:
            self.reporters.read_custom_reports_file(custom_reports_path)
            if asset_path:
                # Look for reporters DLLs files
                self.reporters.add_dll_folder(asset_path)

        if asset_path and config_path:
            # Look for climate
            self.climate.read_config_file(config_path, asset_path)

            # Look for migrations
            self.migrations.read_config_file(config_path, asset_path)

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem]):
        """
        Call before a task is executed. This ensures our configuration is properly done

        """
        # Set the demographics
        self.demographics.set_task_config(self)
        self.simulation_demographics.set_task_config(self, extend=True)

        # Set the migrations
        self.simulation_migrations.merge_with(self.migrations)
        self.simulation_migrations.set_task_config(self)

        # Set the climate
        self.climate.set_task_config(self)

        # Set the reporters
        self.reporters.set_task_config(self)

        # Set the campaign filename
        if self.campaign:
            self.config["Campaign_Filename"] = "campaign.json"

        # Gather the custom coordinator, individual, and node events
        self.config["Custom_Coordinator_Events"] = []
        # self.config["Custom_Individual_Events"] = []
        self.config["Custom_Node_Events"] = []
        self.set_command_line()
        super().pre_creation(parent)

    def set_command_line(self) -> NoReturn:
        """
        Builds and sets the command line object

        Returns:

        """
        # Input path is different for legacy exes
        input_path = r"./Assets;." if not (self.legacy_exe or self.is_linux) else "./Assets"

        # Create the command line according to self. location of the model
        if self.use_embedded_python:
            self.command = CommandLine(f"Assets/{self.executable_name}", "--config config.json",  # noqa
                                       f"--input-path {input_path}", f"--dll-path ./Assets",  # noqa
                                       f"--python-script-path ./Assets/python")  # noqa
        else:
            self.command = CommandLine(f"Assets/{self.executable_name}", "--config config.json",  # noqa
                                       f"--input-path {input_path}", f"--dll-path ./Assets")  # noqa

    def gather_common_assets(self) -> AssetCollection:
        """
        Gather Experiment Level Assets
        Returns:

        """
        # Add Eradication.exe to assets
        logger.debug(f"Adding {self.eradication_path}")
        self.common_assets.add_asset(
            Asset(absolute_path=self.eradication_path, filename=self.executable_name),
            fail_on_duplicate=False
        )

        # Add demographics to assets
        self.common_assets.extend(self.demographics.gather_assets())

        # Add DLLS to assets
        self.common_assets.extend(self.reporters.gather_assets(is_linux=self.is_linux))
        # Add the migrations
        self.common_assets.extend(self.migrations.gather_assets())

        # Add the climate
        self.common_assets.extend(self.climate.gather_assets())
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather assets that are per simulation
        Returns:

        """
        config = {"parameters": self.config}

        # Add config and campaign to assets
        self.transient_assets.add_asset(
            Asset(filename="config.json", content=json.dumps(config, sort_keys=True)),
            fail_on_duplicate=False
        )

        if self.campaign:
            self.transient_assets.add_asset(
                Asset(filename="campaign.json", content=self.campaign.json),
                fail_on_duplicate=False
            )

        # Add custom_reporters.json if needed
        if not self.reporters.empty:
            self.transient_assets.add_asset(
                Asset(filename="custom_reports.json", content=self.reporters.json),
                fail_on_duplicate=False
            )

        # Add demographics files to assets
        self.transient_assets.extend(self.simulation_demographics.gather_assets())

        # Add the migrations
        self.transient_assets.extend(self.simulation_migrations.gather_assets())

        return self.transient_assets

    def copy_simulation(self, base_simulation: 'Simulation') -> 'Simulation':
        """
        Called when making copies of a simulation.

        Here we deep copy parts of the simulation to ensure we don't accidentally update objects
        Args:
            base_simulation: Base Simulation

        Returns:

        """
        simulation = copy.deepcopy(base_simulation)

        # Copy the experiment demographics and set them as persisted to prevent change
        demog_copy = copy.deepcopy(self.demographics)
        demog_copy.set_all_persisted()
        simulation.task.demographics.extend(demog_copy)

        # Copy the climate
        climate_copy = copy.deepcopy(self.climate)
        climate_copy.set_all_persisted()
        simulation.task.climate = climate_copy

        # Tale care of the migrations
        migration_copy = copy.deepcopy(self.migrations)
        migration_copy.set_all_persisted()
        simulation.task.simulation_migrations.merge_with(migration_copy)

        # Handle the custom reporters
        reporters_copy = copy.deepcopy(self.reporters)
        reporters_copy.set_all_persisted()
        simulation.task.reporters = reporters_copy

        return simulation

    def set_parameter(self, name: str, value: any) -> dict:
        """
        Set a value in the EMOD config.json file

        Args:
            name: Name of parameter to set
            value: Value to set

        Returns:
            Tags to set
        """
        self.config[name] = value
        return {name: value}

    @staticmethod
    def set_parameter_sweep_callback(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
        """
        Convenience callback for sweeps

        Args:
            simulation: Simulation we are updating
            param: Parameter
            value: Value

        Returns:
            Tags to set on simulation
        """
        if not hasattr(simulation.task, 'set_parameter'):
            raise ValueError("update_task_with_set_parameter can only be used on tasks with a set_parameter")
        return simulation.task.set_parameter(param, value)

    @classmethod
    def set_parameter_partial(cls, parameter: str):
        """
        Convenience callback for sweeps

        Args:
            parameter: Parameter to set

        Returns:

        """
        return partial(cls.set_parameter_sweep_callback, param=parameter)

    def get_parameter(self, name: str, default: Optional[Any] = None):
        """
        Get a parameter in the simulation.

        Args:
            name: The name of the parameter.
            default: Optional, the default value.

        Returns:
            The value of the parameter.
        """
        return self.config.get(name, default)

    def update_parameters(self, params):
        """
        Bulk update the configuration parameter values.

        Args:
            params: A dictionary with new values.

        Returns:
            None
        """
        self.config.update(params)

    def reload_from_simulation(self, simulation: 'Simulation'):
        pass


class EMODTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> EMODTask:
        return EMODTask(**configuration)

    def get_description(self) -> str:
        return "Defines a EMODTask command"

    def get_example_urls(self) -> List[str]:
        from idmtools_models import __version__
        examples = [f'examples']  # noqa
        return [self.get_version_url(f'v{__version__}', x) for x in examples]
