import os
import sys
from functools import partial

from idmtools_calibra.rmse_site import RMSESite 
from idmtools_calibra import calib_base_app as calib_app

from settings import Settings
import test_and_plot as tap

settings = Settings()

def camp_mapper( build_camp_actual, mapto_key, value ):
    """
    This callback function maps paraemters names for the campaign from calibra strings to
    the actual 'build_camp' function parameter names. We hook it up in the main function. See:

    calib_app.campaign_mapper = camp_mapper

    """
    camp_fn_param = mapto_key.split( ":" )[1]
    if camp_fn_param == "eff": # this maps to a value in settings.py
        build_camp_actual = partial( build_camp_actual, eff=value )
    elif camp_fn_param == "dur": # this maps to a value in settings.py
        build_camp_actual = partial( build_camp_actual, dur=value )
    else:
        raise ValueError( f"{camp_fn_param} is not a valid calibration target." )
    return build_camp_actual

if __name__ == "__main__":
    import matplotlib
    matplotlib.use( "TkAgg" )
    # site we want to calibrate on - a core organization object for calibra
    site = RMSESite(
        name='rmse_site',
        reference_sources={'production': os.path.join(settings.REFERENCE_DATA_DIR, 'output.csv')}
    )
    task, platform = tap.get_task()
    calib_man = calib_app.init( settings, site, task, platform )
    calib_app.campaign_builder_fn = tap.build_camp
    calib_app.campaign_mapper = camp_mapper
    calib_man.platform = platform

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    calib_app.go( calib_man )

    tap.test_and_plot()
