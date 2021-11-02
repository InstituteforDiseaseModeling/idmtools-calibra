from idmtools_calibra.utilities.resume_manager import ResumeManager
from idmtools_calibra.plotters.site_data_plotter import SiteDataPlotter


def generate_ll_all(calib_manager, num_to_plot=5):
    # retrieve the latest iteration
    # max_iteration = calib_manager.max_iterations
    rm = ResumeManager(calib_manager, iter_step='plot')
    latest_iteration = rm.calib_manager.current_iteration.iteration
    max_iteration = latest_iteration + 1

    # get SiteDataPlotter
    sp = None
    for plotter in calib_manager.plotters:
        if isinstance(plotter, SiteDataPlotter):
            sp = plotter
            break
    if sp is None:
        sp = SiteDataPlotter(num_to_plot=num_to_plot, combine_sites=True)
        # raise ModuleNotFoundError("Calibration is missing SiteDataPlotter!")

    # build ll_all.csv
    ll_all_name = "ll_all_final.csv"
    for i in range(max_iteration):
        rm = ResumeManager(calib_manager, iteration=i, iter_step='plot')
        it = rm.calib_manager.current_iteration
        sp = SiteDataPlotter(num_to_plot=5, combine_sites=True)
        sp.iteration_state = it
        sp.write_LL_csv(ll_all_name=ll_all_name)
