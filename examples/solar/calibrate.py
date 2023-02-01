#!/usr/bin/env python
import os

from idmtools_calibra import calib_base_app as calib_app
from solar_site import SolarSite 
import settings

mysettings = settings.Settings()

if __name__ == "__main__":
    import matplotlib
    matplotlib.use( "TkAgg" )
    import plot
    # site we want to calibrate on - a core organization object for calibra
    site = SolarSite(
        name='solar_site',
        reference_sources={'production': os.path.join(mysettings.REFERENCE_DATA_DIR, 'production.csv')}
    )
    # Next two lines aren't required but default priority is Lowest so your jobs can get stuck.
    from idmtools.core.platform_factory import Platform
    platform = Platform(mysettings.LOCALE, node_group="idm_48cores", priority="Normal")
    calib_man = calib_app.init( mysettings, site, platform=platform )

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )
    plot.plot(mysettings.CALIBRATION_NAME)
