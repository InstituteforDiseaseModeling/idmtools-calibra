import os
import sys

from idmtools_calibra.rmse_site import RMSESiteSingleChannel as RMSESite
from idmtools_calibra import calib_base_app as calib_app
from settings import Settings

mysettings = Settings()

if __name__ == "__main__":
    import matplotlib
    matplotlib.use( "TkAgg" )
    # site we want to calibrate on - a core organization object for calibra
    site = RMSESite(
        name='rmse_site'
    )
    from idmtools.core.platform_factory import Platform
    platform = Platform(mysettings.LOCALE, node_group="idm_48cores", priority="Highest")
    calib_man = calib_app.init( mysettings, site, platform=platform )

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )

    import bin.sir as sir
    sir.run_compare()
