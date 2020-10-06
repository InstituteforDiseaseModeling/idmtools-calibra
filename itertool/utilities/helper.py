import os
import shutil
from emodpy.utils import download_latest_bamboo, EradicationBambooBuilds
from emod_api.config import default_from_schema_no_validation as dfs
from emod_api.schema import get_schema as gs

max_exp_name_len = 255


def validate_exp_name(exp_name):
    if len(exp_name) > max_exp_name_len:
        print(
            "The experiment name '%s' exceeds the max length %d (%d), please adjust your experiment name. Exiting..." %
            (exp_name, max_exp_name_len, len(exp_name)))
        return False
    else:
        return True


def generate_default_config_from_exe(local_dir, plan=EradicationBambooBuilds.CI_GENERIC):
    """
    Check and down;oad Eradication.exe from bamboo, generate schema and default config file
    Args:
        local_dir: local folder to contain Eradication.exe
        plan: enum EradicationBambooBuilds

    Returns: exe_path, config_path

    """
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
    gs.dtk_to_schema(exe_path, path_to_write_schema=schema_path)
    # generate default config from schema
    dfs.write_default_from_schema(schema_path)
    # use our file name
    shutil.move("default_config.json", config_path)

    return exe_path, config_path
