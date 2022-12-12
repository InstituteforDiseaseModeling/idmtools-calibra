#!/usr/bin/env python
import os

from idmtools_calibra import calib_base_app as calib_app
from solar_site import SolarSite 
import settings

settings = settings.Settings()

if __name__ == "__main__":
    import matplotlib
    matplotlib.use( "TkAgg" )
    import plot
    # site we want to calibrate on - a core organization object for calibra
    site = SolarSite(
        name='solar_site',
        reference_sources={'production': os.path.join(settings.REFERENCE_DATA_DIR, 'production.csv')}
    )
    calib_man = calib_app.init( settings, site )

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )
    plot.plot(settings.CALIBRATION_NAME)
