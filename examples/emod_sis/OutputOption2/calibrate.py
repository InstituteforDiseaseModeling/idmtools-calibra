import os
import sys

from idmtools_calibra.rmse_site import RMSESite 
from idmtools_calibra import calib_base_app as calib_app

from settings import Settings

settings = Settings()

if __name__ == "__main__":
    import matplotlib
    matplotlib.use( "TkAgg" )
    import test_and_plot as tap
    # site we want to calibrate on - a core organization object for calibra
    site = RMSESite(
        name='rmse_site',
        reference_sources={'production': os.path.join(settings.REFERENCE_DATA_DIR, 'output.csv')}
    )
    task, platform = tap.get_task()
    calib_man = calib_app.init( settings, site, task )
    calib_app.campaign_builder_fn = tap.build_camp
    calib_man.platform = platform

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )

    tap.test_and_plot()
