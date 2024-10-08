import os
import sys

from idmtools_calibra.rmse_site import RMSESiteSingleChannel as RMSESite
from idmtools_calibra import calib_base_app as calib_app

import manifest 
from settings import Settings

mysettings = Settings()

if __name__ == "__main__":
    import matplotlib
    matplotlib.use( "TkAgg" )
    # site we want to calibrate on - a core organization object for calibra
    site = RMSESite(
        name='rmse_site',
        reference_sources={'production': os.path.join(mysettings.REFERENCE_DATA_DIR, 'output.csv')}
    )

    import test_and_plot as tap
    task,platform = tap.get_task() 
    #task.set_sif( mysettings.SIF )
    calib_man = calib_app.init( settings=mysettings, site=site, task=task, platform=platform )
    #calib_man.platform = platform

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )

    tap.go()
