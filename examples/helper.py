import os
import shutil
from emodpy.utils import download_latest_bamboo, EradicationBambooBuilds, download_latest_schema
from emod_api.schema import get_schema as gs


def download_bamboo_exe(local_dir, platform, plan=EradicationBambooBuilds.MALARIA_WIN):
    """
    Check and download Eradication.exe from bamboo, generate schema and default config file
    Args:
        local_dir: local folder to contain Eradication.exe
        platform: Platform item is being created on
        plan: enum EradicationBambooBuilds

    Returns: exe_path

    """
    env = platform.environment
    exe = "Eradication.exe" if env.lower() == 'belegost' or env.lower() == 'bayesian' else "Eradication"
    exe_path = os.path.join(local_dir, exe)
    if not os.path.exists(exe_path):
        eradication_path_bamboo = download_latest_bamboo(
            plan=plan,
            scheduled_builds_only=False
        )
        # print(eradication_path_bamboo)
        shutil.move(eradication_path_bamboo, exe_path)

    return exe_path


def generate_default_config_from_exe(local_dir, platform, plan=EradicationBambooBuilds.MALARIA_WIN):
    """
    Check and download Eradication.exe from bamboo, generate schema and default config file
    Args:
        local_dir: local folder to contain Eradication.exe
        platform: Platform item is being created on
        plan: enum EradicationBambooBuilds

    Returns: exe_path, config_path

    """
    from emod_api.config import default_from_schema_no_validation as dfs

    env = platform.environment
    exe = "Eradication.exe" if env.lower() == 'belegost' or env.lower() == 'bayesian' else "Eradication"

    exe_path = os.path.join(local_dir, exe)
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
        if os.name == "posix":  # very much hardcoding SLURM target
            gs.dtk_to_schema(exe_path, path_to_write_schema=schema_path)
        else:
            download_latest_schema(plan=plan, scheduled_builds_only=False, out_path=schema_path)

    if not os.path.exists(config_path):
        # generate default config from schema
        dfs.write_default_from_schema(schema_path)
        # use our file name
        shutil.move("default_config.json", config_path)

    return exe_path, schema_path, config_path


def generate_model_config_from_exe(local_dir, platform, plan=EradicationBambooBuilds.MALARIA_WIN, model="MALARIA_SIM"):
    """
    Check and download Eradication.exe from bamboo, generate schema and default config file
    Args:
        local_dir: local folder to contain Eradication.exe
        platform: Platform item is being created on
        plan: enum EradicationBambooBuilds
        model: config model

    Returns: exe_path, config_path

    """
    from emod_api.config import from_schema as fs

    env = platform.environment
    exe = "Eradication.exe" if env.lower() == 'belegost' or env.lower() == 'bayesian' else "Eradication"

    exe_path = os.path.join(local_dir, exe)
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
        if os.name == "posix":  # very much hardcoding SLURM target
            gs.dtk_to_schema(exe_path, path_to_write_schema=schema_path)
        else:
            download_latest_schema(plan=plan, scheduled_builds_only=False, out_path=schema_path)

    # use our file name
    if not os.path.exists(config_path):
        fs.SchemaConfigBuilder(schema_name=schema_path, config_out=config_path, model=model)

    return exe_path, schema_path, config_path
