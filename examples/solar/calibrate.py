# Execute directly:
# python calibrate.py

import os
from pathlib import Path
import sys

from idmtools.assets import AssetCollection
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.algorithms.optim_tool import OptimTool
from idmtools_calibra.plotters.likelihood_plotter import LikelihoodPlotter
from idmtools_calibra.plotters.optim_tool_plotter import OptimToolPlotter
from idmtools_calibra.plotters.site_data_plotter import SiteDataPlotter
from idmtools.core.platform_factory import Platform
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

import matplotlib
matplotlib.use( "TkAgg" )
import matplotlib.pyplot as plt
import plot

sys.path.append(os.getcwd())
import calib_app
from solar_site import SolarSite 

class Settings:
#
# Run environment controls
#
    LOCALE = 'CALCULON'
    MODEL_DRIVER = Path('bin', 'linear_model.py')
    CONFIG_FILENAME = 'config.json'
    REFERENCE_DATA_DIR = 'reference'
    INPUT_DIRS = []

#
# Calibration controls
#

# The number of parameter sets/samples to run in each calibration iteration
    N_SAMPLES = 20
# number of randomly seeded simulations per parameter set/sample
    N_REPLICATES = 1
# the number of times the algorithm will attempt to optimize the best-guess parameterization
    N_ITERATIONS = 10
# Calibration state/results will be kept in a directory by this name in the same directory as this file
    CALIBRATION_NAME = 'solar_optimtool_linear_model'

    """
    Calibration parameter specification

    Dynamic parameters are those that calibra can use to explore parameter space during calibration, non-dynamic parameters
    are simply overrides of model parameters.

    Name: Human readable name of the parameter to utilize
    Dynamic: True/False, whether this parameter can be altered by the calibration (False still overrides input files)
    MapTo: actual model parameter name to use. If not specified, the map_sample_to_model_input method below will have to
      handle the (more complicated) mapping of this parameter to actual model parameter(s)
    Guess: Initial value for parameter in calibration
    Min: The minimum value the parameter can be in the calibration (if Dynamic is True) (required even if not Dynamic)
    Max: The maximum value the parameter can be in the calibration (if Dynamic is True) (required even if not Dynamic)

    The model in this example has two parameters, 'a' and 'b' used in equation: y = a * x + b, where x is time and y is
    solar power production.
    """
    CALIBRATION_PARAMETERS = [
        {
            'Name': 'linear-coefficient',
            'Dynamic': True,
            'MapTo': 'a',
            'Guess': 50,
            'Min': 0,
            'Max': 400
        },
        {
            'Name': 'constant',
            'Dynamic': True,
            'MapTo': 'b',
            'Guess': 500,
            'Min': 0,
            'Max': 2000
        }
    ]
    volume_fraction = 0.002
    num_to_plot = 5



if __name__ == "__main__":
    # Here we actually execute the calibration
    settings = Settings()
# site we want to calibrate on - a core organization object for calibra
    site = SolarSite(name='solar_site', reference_sources={'production': os.path.join(settings.REFERENCE_DATA_DIR, 'production.csv')})
    calib_man = calib_app.init( settings, site )
    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )
    plot.plot(settings.CALIBRATION_NAME)
