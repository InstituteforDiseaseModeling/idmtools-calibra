import os
import sys
from functools import partial

from idmtools_calibra.rmse_site import RMSESiteSingleChannel as RMSESite
from idmtools_calibra.analyzers.rmse_analyzer import RMSEAnalyzer 
from idmtools_calibra import calib_base_app as calib_app

from settings import Settings
import run_and_plot as tap

settings = Settings()

def demog_mapper( build_demog_actual, mapto_key, value ):
    """
    This callback function maps paraemters names for the demogaign from calibra strings to
    the actual 'build_demog' function parameter names. We hook it up in the main function. See:

    calib_app.demogaign_mapper = demog_mapper

    """
    demog_fn_param = mapto_key.split( ":" )[1]
    #print( f"In demog_mapper: demog_fn_param = {demog_fn_param}." )
    if demog_fn_param == "group_a_baseinfectivity": # this maps to a value in settings.py
        build_demog_actual = partial( build_demog_actual, hint_group_a_bi=value )
    elif demog_fn_param == "group_b_baseinfectivity": # this maps to a value in settings.py
        build_demog_actual = partial( build_demog_actual, hint_group_b_bi=value )
    elif demog_fn_param == "group_c_baseinfectivity": # this maps to a value in settings.py
        build_demog_actual = partial( build_demog_actual, hint_group_c_bi=value )
    elif demog_fn_param == "group_d_baseinfectivity": # this maps to a value in settings.py
        build_demog_actual = partial( build_demog_actual, hint_group_d_bi=value )
    else:
        raise ValueError( f"{demog_fn_param} is not a valid calibration target." )
    return build_demog_actual

if __name__ == "__main__":
    import run_and_plot as tap
    # site we want to calibrate on - a core organization object for calibra
    site = RMSESite(
        name='rmse_site',
        reference_sources={'production': os.path.join(settings.REFERENCE_DATA_DIR, 'output.csv')}
    )
    task, platform = tap.get_task()
    calib_man = calib_app.init( settings, site, task, platform=platform )
    import model
    calib_app.campaign_builder_fn = model.build_camp
    calib_app.demog_builder_fn = model.build_demog
    calib_app.demog_mapper = demog_mapper

    # Required variable/dict in calibration scripts
    run_calib_args = {
        "calib_manager": calib_man
    }
    def lse_cost_fn( series1, series2, series3 ):
        #return (((series1 - series2)*series3) ** 2).mean() ** 0.5
        return (((series1 - series2) ** 2)*series3).sum()

    RMSEAnalyzer.set_custom_cost_fn( lse_cost_fn )

    calib_app.go( calib_man )

    tap.test_and_plot()
