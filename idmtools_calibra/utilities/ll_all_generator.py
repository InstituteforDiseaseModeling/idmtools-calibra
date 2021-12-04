import os
import pandas as pd
from idmtools_calibra.plotters.site_data_plotter import SiteDataPlotter


def generate_ll_all(calib_manager, num_to_plot=5, iteration=None, ll_all_name=None):
    from idmtools_calibra.cli.utils import read_calib_data
    calib_data = read_calib_data(calib_manager.calibration_path)
    # in case environment has been changed and new suite_id & suites are generated

    # load all_results
    results = calib_data.get('results')
    all_results = pd.DataFrame()
    if isinstance(results, dict):
        all_results = pd.DataFrame.from_dict(results, orient='columns')

    all_results.reset_index(inplace=True, drop=True)
    top_columns = ['iteration', 'sample', 'total']
    all_results = all_results.reindex(
        columns=(top_columns + list([a for a in all_results.columns if a not in top_columns])))

    # restore last time location
    if iteration is None:
        current_iteration = calib_data['iteration']
    else:
        current_iteration = iteration

    # get SiteDataPlotter
    sp = None
    for plotter in calib_manager.plotters:
        if isinstance(plotter, SiteDataPlotter):
            sp = plotter
            break
    if sp is None:
        sp = SiteDataPlotter(num_to_plot=num_to_plot, combine_sites=True)

    # build ll_all.csv
    if ll_all_name is None:
        ll_all_name = "ll_all_final.csv"

    # clean existing one
    ll_all_path = os.path.join(calib_manager.directory, '_plots', ll_all_name)
    if os.path.exists(ll_all_path):
        os.remove(ll_all_path)

    for iteration in range(current_iteration + 1):
        it = calib_manager.state_for_iteration(iteration)
        it.all_results = all_results.copy(deep=True)
        it.all_results = all_results[all_results.iteration <= iteration]
        it.all_results.set_index('sample', inplace=True)  # important to keep the same format as original

        sp = SiteDataPlotter(num_to_plot=5, combine_sites=True)
        sp.iteration_state = it
        sp.write_LL_csv(ll_all_name=ll_all_name)
