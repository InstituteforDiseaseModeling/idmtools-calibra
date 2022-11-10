# flake8: noqa E402
import logging
import os
import matplotlib.pyplot as plt

plt.switch_backend('agg')
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from idmtools.core.enums import ItemType
from idmtools_calibra.iteration_state import IterationState
from idmtools_calibra.plotters.base_plotter import BasePlotter
from idmtools_calibra.process_state import StatusPoint

sns.set_style('white', {'axes.linewidth': 0.5})

logger = logging.getLogger(__name__)


class SiteDataPlotter(BasePlotter):
    def __init__(self, combine_sites=True, num_to_plot=5, ll_all_name: str = 'LL_all.csv'):
        super(SiteDataPlotter, self).__init__(combine_sites)
        self.num_to_plot = num_to_plot
        self.ll_all_name = ll_all_name

    @property
    def directory(self):
        return self.get_plot_directory()

    # ZD [TODO]: self.iteration_state.analyzer_list doesn't keep site info, here we assume all analyzers have different names!!!
    def get_site_analyzer(self, site_name, analyzer_name):
        for site, analyzers in self.site_analyzer_names.items():
            if site_name != site:
                continue
            site_analyzer = f'{site_name}_{analyzer_name}'
            for analyzer in self.iteration_state.analyzer_list:
                if site_analyzer == analyzer.uid:
                    return analyzer
        raise Exception(f'Unable to find analyzer={analyzer_name} for site={site_name}')

    def get_analyzer_data(self, iteration, site_name, analyzer_name):
        site_analyzer = '%s_%s' % (site_name, analyzer_name)
        return IterationState.restore_state(iteration).analyzers[site_analyzer]

    def visualize(self, iteration_state):
        self.iteration_state = iteration_state
        self.site_analyzer_names = iteration_state.site_analyzer_names
        iteration_status = self.iteration_state.status
        if iteration_status != StatusPoint.plot:
            return  # Only plot once results are available
        try:
            if self.combine_sites:
                for site_name, analyzer_names in self.site_analyzer_names.items():
                    sorted_results = self.all_results.sort_values(by='total', ascending=False).reset_index()
                    # self.plot_analyzers(site_name, analyzer_names, sorted_results)
            else:
                for site_name, analyzer_names in self.site_analyzer_names.items():
                    self.combine_by_site(site_name, analyzer_names, self.all_results)
                    sorted_results = self.all_results.sort_values(by=f'{site_name}_total',
                                                                  ascending=False).reset_index()
                    # self.plot_analyzers(site_name, analyzer_names, sorted_results)
        except Exception as e:
            logger.info("SiteDataPlotter could not plot for one or more analyzer(s).")
            raise e

        try:
            self.write_LL_csv()
        except:
            logger.info("Log likelihood CSV could not be created. Skipping...")

    def plot_analyzers(self, site_name, analyzer_names, samples):
        cmin, cmax = samples['total'].describe()[['min', 'max']].tolist()
        cmin = cmin if cmin < cmax else cmax - 1  # avoid divide by zero in color range

        for analyzer_name in analyzer_names:
            site_analyzer = '%s_%s' % (site_name, analyzer_name)
            try:
                os.makedirs(os.path.join(self.directory, site_analyzer))
            except:
                pass

            self.plot_best(site_name, analyzer_name, samples.iloc[:self.num_to_plot])
            self.plot_all(site_name, analyzer_name, samples, clim=(cmin, cmax))

    def plot_best(self, site_name, analyzer_name, samples):

        analyzer = self.get_site_analyzer(site_name, analyzer_name)

        for iteration, iter_samples in samples.groupby('iteration'):
            analyzer_data = self.get_analyzer_data(iteration, site_name, analyzer_name)

            for rank, sample in iter_samples['sample'].iteritems():  # index is rank
                fname = os.path.join(self.directory, f'{site_name}_{analyzer_name}', f'rank{rank:d}')
                fig = plt.figure(fname, figsize=(8, 6))

                analyzer.plot_comparison(fig, analyzer_data['samples'][sample], fmt='-o', color='#CB5FA4', alpha=1,
                                         linewidth=1)
                analyzer.plot_comparison(fig, analyzer_data['ref'], fmt='-o', color='#8DC63F', alpha=1, linewidth=1,
                                         reference=True)

                fig.set_tight_layout(True)

                plt.savefig(fname + '.png', format='PNG')
                plt.close(fig)

    def plot_all(self, site_name, analyzer_name, samples, clim):

        analyzer = self.get_site_analyzer(site_name, analyzer_name)

        fname = os.path.join(self.directory, f'{site_name}_{analyzer_name}_all')
        fig = plt.figure(fname, figsize=(4, 3))
        cmin, cmax = clim

        for iteration, iter_samples in samples.groupby('iteration'):
            analyzer_data = self.get_analyzer_data(iteration, site_name, analyzer_name)
            results_by_sample = iter_samples.reset_index().set_index('sample')['total']
            for sample, result in results_by_sample.iteritems():
                analyzer.plot_comparison(fig, analyzer_data['samples'][sample], fmt='-',
                                         color=cm.Blues((result - cmin) / (cmax - cmin)), alpha=0.5, linewidth=0.5)

        analyzer.plot_comparison(fig, analyzer_data['ref'], fmt='-o', color='#8DC63F', alpha=1, linewidth=1,
                                 reference=True)

        fig.set_tight_layout(True)
        plt.savefig(fname + '.png', format='PNG')
        plt.close(fig)

    def cleanup(self):
        """
        cleanup the existing plots
        :param calib_manager:
        :return:
        """
        if self.combine_sites:
            for site, analyzers in self.site_analyzer_names.items():
                self.cleanup_plot_by_analyzers(site, analyzers, self.all_results)
        else:
            for site, analyzers in self.site_analyzer_names.items():
                self.cleanup_plot_by_analyzers(site, analyzers, self.all_results)

    def cleanup_plot_by_analyzers(self, site, analyzers, samples):
        """
        cleanup the existing plots
        :param site:
        :param analyzers:
        :param samples:
        :return:
        """
        best_samples = samples.iloc[:self.num_to_plot]
        for analyzer in analyzers:
            site_analyzer = f'{site}_{analyzer}'
            self.cleanup_plot_for_best(site_analyzer, best_samples)
            self.cleanup_plot_for_all(site_analyzer)

    def cleanup_plot_for_best(self, site_analyzer, samples):
        """
        cleanup the existing plots
        :param site_analyzer:
        :param samples:
        :return:
        """
        for iteration, iter_samples in samples.groupby('iteration'):
            for rank, sample in iter_samples['sample'].iteritems():  # index is rank
                fname = os.path.join(self.directory, site_analyzer, 'rank%d' % rank)
                plot_path = fname + '.pdf'
                if os.path.exists(plot_path):
                    try:
                        # logger.info("Try to delete %s" % plot_path)
                        os.remove(plot_path)
                        pass
                    except OSError:
                        logger.error(f"Failed to delete {plot_path}")

    def cleanup_plot_for_all(self, site_analyzer):
        """
        cleanup the existing plots
        :param site_analyzer:
        :return:
        """
        fname = os.path.join(self.directory, f'{site_analyzer}_all')
        plot_path = fname + '.pdf'
        if os.path.exists(plot_path):
            try:
                # logger.info("Try to delete %s" % plot_path)
                os.remove(plot_path)
            except OSError:
                logger.error(f"Failed to delete {plot_path}")

    def write_LL_csv(self, ll_all_name: str = None):
        """
        Write the LL_summary.csv with what is in the CalibManager
        """
        if ll_all_name:
            self.ll_all_name = ll_all_name
        # Data needed for the LL_CSV
        # location = self.iteration_state.exp_manager.experiment.location
        iteration_state = self.iteration_state
        iteration = self.iteration_state.iteration
        suite_id = iteration_state.suite_id

        # Deep copy all_results ato not disturb the calibration
        all_results = self.all_results.copy()

        # Index the likelihood-results DataFrame on (iteration, sample) to join with simulation info
        results_df = all_results.reset_index().set_index(['iteration', 'sample'])

        # Get the simulation info from the iteration state
        siminfo_df = pd.DataFrame.from_dict(iteration_state.simulations, orient='index')
        siminfo_df.index.name = 'simid'
        siminfo_df['iteration'] = iteration
        siminfo_df = siminfo_df.rename(columns={'__sample_index__': 'sample'}).reset_index()

        # Group simIDs by sample point and merge back into results
        grouped_simids_df = siminfo_df.groupby(['iteration', 'sample']).simid.agg(lambda x: tuple(x))
        join_results_df = results_df.join(grouped_simids_df, how='right')  # right: only this iteration with new sim info

        platform = self.iteration_state.platform
        sims_paths = platform.create_sim_directory_map(item_id=suite_id, item_type=ItemType.SUITE)

        # Transform the ids in actual paths
        def find_path(el):
            paths = list()
            try:
                for e in el:
                    paths.append(sims_paths[e])
            except Exception as ex:
                pass  # [TODO]: fix issue later.
            return ",".join(paths)

        join_results_df['outputs'] = join_results_df['simid'].apply(find_path)

        # Concatenate with any existing data from previous iterations and dump to file
        csv_path = os.path.join(self.directory, self.ll_all_name)
        if os.path.exists(csv_path):
            current = pd.read_csv(csv_path, index_col=['iteration', 'sample'])
            final_results_df = pd.concat([current, join_results_df])
        else:
            final_results_df = join_results_df
        final_results_df.sort_values(by='total', ascending=False).to_csv(csv_path)
