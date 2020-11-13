import itertools
import os
import shutil
from logging import getLogger
from emodpy.utils import download_latest_bamboo, EradicationBambooBuilds
from emod_api.schema import get_schema as gs
import pandas as pd
import numpy as np

max_exp_name_len = 255

logger = getLogger(__name__)


def validate_exp_name(exp_name):
    if len(exp_name) > max_exp_name_len:
        print(
            "The experiment name '%s' exceeds the max length %d (%d), please adjust your experiment name. Exiting..." %
            (exp_name, max_exp_name_len, len(exp_name)))
        return False
    else:
        return True


def download_bamboo_exe(local_dir, plan=EradicationBambooBuilds.MALARIA_WIN):
    """
    Check and download Eradication.exe from bamboo, generate schema and default config file
    Args:
        local_dir: local folder to contain Eradication.exe
        plan: enum EradicationBambooBuilds

    Returns: exe_path

    """
    exe_path = os.path.join(local_dir, "Eradication.exe")
    if not os.path.exists(exe_path):
        eradication_path_bamboo = download_latest_bamboo(
            plan=plan,
            scheduled_builds_only=False
        )
        # print(eradication_path_bamboo)
        shutil.move(eradication_path_bamboo, exe_path)

    return exe_path


def generate_default_config_from_exe(local_dir, plan=EradicationBambooBuilds.MALARIA_WIN):
    """
    Check and download Eradication.exe from bamboo, generate schema and default config file
    Args:
        local_dir: local folder to contain Eradication.exe
        plan: enum EradicationBambooBuilds

    Returns: exe_path, config_path

    """
    from emod_api.config import default_from_schema_no_validation as dfs

    exe_path = os.path.join(local_dir, "Eradication.exe")
    if not os.path.exists(exe_path):
        eradication_path_bamboo = download_latest_bamboo(
            plan=plan,
            scheduled_builds_only=False
        )
        # print(eradication_path_bamboo)
        shutil.move(eradication_path_bamboo, exe_path)

    schema_path = os.path.join(local_dir, f"{plan.name}_schema.json")
    config_path = os.path.join(local_dir, f"{plan.name}_config.json")

    # generate schema
    if not os.path.exists(schema_path):
        gs.dtk_to_schema(exe_path, path_to_write_schema=schema_path)

    if not os.path.exists(config_path):
        # generate default config from schema
        dfs.write_default_from_schema(schema_path)
        # use our file name
        shutil.move("default_config.json", config_path)

    return exe_path, schema_path, config_path


def generate_model_config_from_exe(local_dir, plan=EradicationBambooBuilds.MALARIA_WIN, model="MALARIA_SIM"):
    """
    Check and download Eradication.exe from bamboo, generate schema and default config file
    Args:
        local_dir: local folder to contain Eradication.exe
        plan: enum EradicationBambooBuilds
        model: config model

    Returns: exe_path, config_path

    """
    from emod_api.config import from_schema as fs

    exe_path = os.path.join(local_dir, "Eradication.exe")
    if not os.path.exists(exe_path):
        eradication_path_bamboo = download_latest_bamboo(
            plan=plan,
            scheduled_builds_only=False
        )
        # print(eradication_path_bamboo)
        shutil.move(eradication_path_bamboo, exe_path)

    schema_path = os.path.join(local_dir, f"{plan.name}_schema.json")
    config_path = os.path.join(local_dir, f"{plan.name}_config.json")

    # generate schema
    if not os.path.exists(schema_path):
        gs.dtk_to_schema(exe_path, path_to_write_schema=schema_path)

    # use our file name
    if not os.path.exists(config_path):
        fs.SchemaConfigBuilder(schema_name=schema_path, config_out=config_path, model=model)

    return exe_path, schema_path, config_path


def json_to_pandas(channel_data, bins, channel=None):
    """
    A function to convert nested array channel data from a json file to
    a pandas.Series with the specified MultiIndex binning.
    """

    logger.debug("Converting JSON data from '%s' channel to pandas.Series with %s MultiIndex.", channel, bins.keys())
    bin_tuples = list(itertools.product(*bins.values()))
    multi_index = pd.MultiIndex.from_tuples(bin_tuples, names=bins.keys())

    channel_series = pd.Series(np.array(channel_data).flatten(), index=multi_index, name=channel)
    logger.debug('\n%s', channel_series)
    return channel_series
