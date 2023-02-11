import json
import os
import shutil

import pandas as pd
from COMPS.utils import get_output_files_for_experiment as comps_getter

from idmtools.core import ItemType


def download_experiment_files(platform, directory, calibra_name, files_to_get):
    with open(os.path.join(os.path.join(directory, calibra_name, 'CalibManager.json')), 'r') as fp:
        cm = json.load(fp)
        suite_id = cm['suites'][0]['id']
        experiments = platform.get_children(suite_id, ItemType.SUITE, force=True)
        for experiment in experiments:
            comps_getter.get_files(experiment.uid, files_to_get=files_to_get)
        return experiments


def delete_experiments(experiments):
    for experiment in experiments:
        try:
            shutil.rmtree(os.path.join(experiment.id))
        except OSError as error:
            print(error)
            print("Directory '% s' can not be removed" % os.path.join(experiment.id))


def get_output_data(experiments, simulation_id, value):
    """
    Return simulation's output/output.csv {value} column
    """
    for experiment in experiments:
        for it in os.scandir(experiment.id):
            if it.name == simulation_id:
                df = pd.read_csv(os.path.join(it.path, "output.csv"))
                return df[value]