import os
import sys
import json
from importlib import import_module


def load_config_module(config_name):
    # Support of relative paths
    config_name = config_name.replace('\\', '/')
    if '/' in config_name:
        splitted = config_name.split('/')[:-1]
        sys.path.append(os.path.join(os.getcwd(), *splitted))
    else:
        sys.path.append(os.getcwd())

    module_name = os.path.splitext(os.path.basename(config_name))[0]

    try:
        return import_module(module_name)
    except ImportError as e:
        e.args = ("'%s' during loading module '%s' in %s files: %s." %
                  (e.msg, module_name, os.getcwd(), os.listdir(os.getcwd())),)
        raise e


def get_calib_manager(config_name, calib_callback="get_manager"):
    mod = load_config_module(config_name)

    calib_manager = None
    if hasattr(mod, calib_callback):
        func = getattr(mod, calib_callback)
        calib_manager = func()
    else:
        from idmtools_calibra.calib_manager import CalibManager
        for k, v in mod.__dict__.items():
            if isinstance(v, CalibManager):
                calib_manager = v
                break

    # print("Sorry, couldn't locate calib_manager!")
    if calib_manager is None:
        raise Exception(f'Sorry! Unable to locate calib_manager in {config_name}')

    return calib_manager


def read_calib_data(calib_path, force=False):
    try:
        return json.load(open(calib_path, 'rb'))
    except IOError:
        if not force:
            raise Exception(f'Unable to find metadata in {calib_path}')
        else:
            return None
