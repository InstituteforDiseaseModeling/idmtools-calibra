import os
import sys

from idmtools_calibra.rmse_site import RMSESite 
from idmtools_calibra import calib_base_app as calib_app

import manifest 

class Settings:
    #
    # Run environment controls
    #
    LOCALE = 'CALCULON'
    MODEL_DRIVER = manifest.eradication_path
    #CONFIG_FILENAME = 'config.json'
    REFERENCE_DATA_DIR = manifest.REFERENCE_DATA_DIR 
    INPUT_DIRS = []
    #SIF = "0f228554-04c4-eb11-a9ec-b88303911bc1" # 'dtk_centos.id'
    SIF = manifest.sif
    #SIF_FILENAME = "dtk_centos.sif"
    SIF_FILENAME = manifest.sif_filename

    #
    # Calibration controls
    #

    # The number of parameter sets/samples to run in each calibration iteration
    N_SAMPLES = 125
    # number of randomly seeded simulations per parameter set/sample
    N_REPLICATES = 1 # 5
    # the number of times the algorithm will attempt to optimize the best-guess parameterization
    N_ITERATIONS = 10
    # Calibration state/results will be kept in a directory by this name in the same directory as this file
    CALIBRATION_NAME = 'emod-sir-2'

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
            'MapTo': 'Base_Infectivity_Constant',
            'Guess': 5,
            'Min': 0,
            'Max': 10.0
        },
        {
            'Name': 'b',
            'Dynamic': True,
            'MapTo': 'Infectious_Period_Exponential',
            'Guess': 5,
            'Min': 0.1,
            'Max': 10
        },
        {
            'Name': 'c',
            'Dynamic': True,
            'MapTo': 'Incubation_Period_Constant',
            'Guess': 5,
            'Min': 0,
            'Max': 10
        }
    ]
    volume_fraction = 0.0002
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
    from emodpy.emod_task import EMODTask
    def set_param_fn( config ):
        #config.parameters.Simulation_Duration = 365.0
        config.parameters.Simulation_Duration = 181.0
        config.parameters.Base_Infectivity_Constant = 3.5 
        config.parameters.Enable_Demographics_Reporting = 0 
        config.parameters.Incubation_Period_Constant = 0
        config.parameters.Infectious_Period_Exponential = 4.0 
        #config.parameters.Minimum_End_Time = 90

        return config

    def build_camp():
        """
        Build a campaign input file for the DTK using emod_api. 
        """
        import emod_api.campaign as camp
        import emod_api.interventions.outbreak as ob 

        camp.set_schema( manifest.schema_file )
        
        event = ob.new_intervention( camp, timestep=1, cases=1 )
        camp.add( event )
        return camp

    import emod_generic.bootstrap as dtk
    dtk.setup( manifest.model_dl_dir )
    from idmtools.core.platform_factory import Platform
    platform = Platform(settings.LOCALE, node_group="idm_48cores", priority="AboveNormal")
    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=settings.MODEL_DRIVER,
        campaign_builder=build_camp,
        demog_builder=None,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        ep4_path=manifest.ep4
    )
    task.set_sif( settings.SIF )
    calib_man = calib_app.init( settings, site, task )
    calib_man.platform = platform

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )

    #import bin.sir as sir
    #sir.run_compare()
