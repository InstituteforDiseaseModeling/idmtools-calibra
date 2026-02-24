import manifest

class Settings:
    #
    # Run environment controls
    #
    LOCALE = 'Calculon'
    MODEL_DRIVER = manifest.eradication_path
    REFERENCE_DATA_DIR = manifest.REFERENCE_DATA_DIR 
    INPUT_DIRS = []
    def __init__(self):
        self.SIF = manifest.sif
        self.SIF_FILENAME = manifest.sif_filename

    #
    # Calibration controls
    #

    # The number of parameter sets/samples to run in each calibration iteration
    N_SAMPLES = 50
    # number of randomly seeded simulations per parameter set/sample
    N_REPLICATES = 1 # 5
    # the number of times the algorithm will attempt to optimize the best-guess parameterization
    N_ITERATIONS = 25
    # Calibration state/results will be kept in a directory by this name in the same directory as this file
    CALIBRATION_NAME = 'emod-hint'

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
    """
    CALIBRATION_PARAMETERS = [
        {
            'Name': 'a',
            'Dynamic': True,
            'MapTo': 'demog:group_a_baseinfectivity',
            'Guess': 1,
            'Min': 0.1,
            'Max': 25.0
        },
        {
            'Name': 'b',
            'Dynamic': True,
            'MapTo': 'demog:group_b_baseinfectivity',
            'Guess': 1,
            'Min': 0.1,
            'Max': 10
        },
        {
            'Name': 'c',
            'Dynamic': True,
            'MapTo': 'demog:group_c_baseinfectivity',
            'Guess': 1,
            'Min': 10,
            'Max': 25
        },
        {
            'Name': 'd',
            'Dynamic': True,
            'MapTo': 'demog:group_d_baseinfectivity',
            'Guess': 1,
            'Min': 10,
            'Max': 25.0
        }
    ]
    volume_fraction = 0.002
    num_to_plot = 5

