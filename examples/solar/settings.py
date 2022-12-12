import os
thing=1
class Settings:
    #
    # Run environment controls
    #
    LOCALE = 'CALCULON'
    MODEL_DRIVER = os.path.join('bin', 'linear_model.py')
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

    Dynamic parameters are those that calibra can use to explore parameter space during calibration, 
        non-dynamic parameters are simply overrides of model parameters.

    Name: Human readable name of the parameter to utilize
    Dynamic: True/False, whether this parameter can be altered by the calibration (False still overrides input files)
    MapTo: actual model parameter name to use. If not specified, the map_sample_to_model_input method below will 
        have to handle the (more complicated) mapping of this parameter to actual model parameter(s)
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


