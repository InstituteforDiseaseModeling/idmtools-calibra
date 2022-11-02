import os
import sys

from idmtools_calibra.rmse_site import RMSESite 
from idmtools_calibra import calib_base_app as calib_app

class Settings:
    #
    # Run environment controls
    #
    LOCALE = 'CALCULON'
    MODEL_DRIVER = os.path.join('bin', 'sir.py')
    CONFIG_FILENAME = 'config.json'
    REFERENCE_DATA_DIR = 'reference'
    INPUT_DIRS = []
    SIF = "0f228554-04c4-eb11-a9ec-b88303911bc1" # 'dtk_centos.id'
    #SIF = "a91a45d2-46a2-ec11-a9f5-9440c9be2c51"
    SIF_FILENAME = "dtk_centos.sif"

    #
    # Calibration controls
    #

    # The number of parameter sets/samples to run in each calibration iteration
    N_SAMPLES = 20
    # number of randomly seeded simulations per parameter set/sample
    N_REPLICATES = 1
    # the number of times the algorithm will attempt to optimize the best-guess parameterization
    N_ITERATIONS = 20
    # Calibration state/results will be kept in a directory by this name in the same directory as this file
    CALIBRATION_NAME = 'sir'

    """
    Calibration parameter specification

    Dynamic parameters are those that calibra can use to explore parameter space during calibration, 
        non-dynamic parameters are simply overrides of model parameters.

    Name: Human readable name of the parameter to utilize
    Dynamic: True/False, whether this parameter can be altered by the calibration (False still overrides input files)
    MapTo: actual model parameter name to use. If not specified, the map_sample_to_model_input method below will 
        have to handle the (more complicated) mapping of this parameter to actual model parameter(s)
    Guess: Initial value for parameter in calibration
    Min: The minimum value the parameter can be in the calibration (if Dynamic is True) (required even if not Dynamic)
    Max: The maximum value the parameter can be in the calibration (if Dynamic is True) (required even if not Dynamic)

    The model in this example has two parameters, 'a' and 'b'. a -> beta in SIR and b->gamme in SIR.
    Trying to rediscover values of: beta = 0.2, gamma = 0.1
    """
    CALIBRATION_PARAMETERS = [
        {
            'Name': 'beta',
            'Dynamic': True,
            'MapTo': 'a',
            'Guess': 0.5,
            'Min': 0,
            'Max': 1.0
        },
        {
            'Name': 'gamma',
            'Dynamic': True,
            'MapTo': 'b',
            'Guess': 0.5,
            'Min': 0,
            'Max': 1
        }
    ]
    volume_fraction = 0.002
    num_to_plot = 5

settings = Settings()

if __name__ == "__main__":
    import matplotlib
    matplotlib.use( "TkAgg" )
    # site we want to calibrate on - a core organization object for calibra
    site = RMSESite(
        name='rmse_site',
        reference_sources={'production': os.path.join(settings.REFERENCE_DATA_DIR, 'output.csv')}
    )
    calib_man = calib_app.init( settings, site )
    from idmtools.core.platform_factory import Platform
    calib_man.platform = Platform(settings.LOCALE, node_group="idm_48cores", priority="Highest")

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )
