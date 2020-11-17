import itertools
import os
from logging import getLogger

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Ellipse
from sklearn.decomposition import PCA

from idmtools_calibra.algorithms.fisher_inf_matrix import trunc_gauss, compute_fisher_inf_matrix
from idmtools_calibra.resamplers.base_resampler import BaseResampler
from idmtools_calibra.resamplers.calibration_point import CalibrationPoint

logger = getLogger(__name__)
user_logger = getLogger('user')


class CramerRaoResampler(BaseResampler):
    def __init__(self, calib_manager=None, **kwargs):
        """
        Args:
            n_resampling_points: The number of resampled points to generate
            kwargs: These are arguments passed directly to the underlying resampling routine.
        """
        super().__init__(calib_manager)
        # self.n_resampling_points = n_resampling_points # the number of points to resample/generate
        self.resample_kwargs = kwargs

    def resample(self, calibrated_points, selection_values, initial_calibration_points):
        """
        Takes in a list of 1+ Point objects and returns method-specific resampled points as a list of Point objects
        The resultant Point objects should be copies of the input Points BUT with Value overridden on each, e.g.::

            new_point = Point.copy(one_of_the_input_calibrated_points)
            for param in new_point.list_params():
              new_point.set_param_value(param, value=SOME_NEW_VALUE)

        Args:
            calibrated_points: input points for this resampling method

        Returns: 
            A list of resampled Point objects
        """

        # selection_values: a DataFrame with columns relevant to selection of calibrated_points

        center_point = initial_calibration_points[0]

        # convert input points to DataFrames
        calibrated_points_df = []
        for i in range(len(calibrated_points)):
            new_item = calibrated_points[i].to_value_dict(parameter_type=CalibrationPoint.DYNAMIC)
            calibrated_points_df.append(new_item)
        calibrated_points_df = pd.DataFrame(calibrated_points_df)
        original_column_names = calibrated_points_df.columns
        calibrated_points_df = selection_values.join(calibrated_points_df)

        # ck4, debugging only, this block
        filename = os.path.join(self.output_location, 'cr-calibrated-points.csv')  # C
        calibrated_points_df.to_csv(filename)

        # temporary, generic column names for the actual parameter names
        # theta_column_names = ['theta%d'%i for i in range(len(original_column_names))]
        # temp_columns = list(selection_values.columns) + theta_column_names
        # calibrated_points_df.columns = temp_columns

        # same as calibrated_points_df but with a LL column on the end
        likelihood_df = pd.DataFrame([{'LL': point.likelihood} for point in calibrated_points])
        likelihood_df = calibrated_points_df.join(likelihood_df)

        # ck4, debugging only, this block
        filename = os.path.join(self.output_location, 'cr-calibrated-points-ll.csv')  # E
        likelihood_df.to_csv(filename)

        # Do the resampling

        # center_point is a list of param values at the center point, must be ordered exactly as calibrated_points_df column-wise
        # obtain min/max of parameter ranges to force results to be within them
        minimums = center_point.get_attribute(key='Min', parameter_type=CalibrationPoint.DYNAMIC)
        maximums = center_point.get_attribute(key='Max', parameter_type=CalibrationPoint.DYNAMIC)
        names = center_point.get_attribute(key='Name', parameter_type=CalibrationPoint.DYNAMIC)

        center_point_as_list = list(
            pd.DataFrame([center_point.to_value_dict(parameter_type=CalibrationPoint.DYNAMIC)]).as_matrix()[0])

        fisher_inf_matrix = compute_fisher_inf_matrix(center_point_as_list, likelihood_df, names)
        covariance = np.linalg.pinv(fisher_inf_matrix)

        # the 2 principal components using PCA
        scaled_covariance = np.dot(
            np.dot(np.asmatrix(np.diag(1 / (np.array(maximums) - np.array(minimums)))), covariance),
            np.asmatrix(np.diag(1 / (np.array(maximums) - np.array(minimums)))))
        pca = PCA(n_components=2)
        pca.fit(scaled_covariance)
        user_logger.info('covariance (scaled): \n', scaled_covariance)
        user_logger.info('principal axes: \n', pca.components_)
        user_logger.info('variance of first 2 principal components: \n', pca.explained_variance_)

        resampled_points_list = trunc_gauss(center_point_as_list, covariance, minimums, maximums,
                                            **self.resample_kwargs)

        # convert resampled points to a list of CalibrationPoint objects (multiple steps here)
        resampled_points_df = pd.DataFrame(data=resampled_points_list, columns=original_column_names)

        # attach static parameters
        names = center_point.get_attribute('Name', parameter_type=CalibrationPoint.STATIC)
        values = center_point.get_attribute('Value', parameter_type=CalibrationPoint.STATIC)
        for i in range(len(names)):
            resampled_points_df = resampled_points_df.assign(**{str(names[i]): values[i]})
        resampled_points_df.sort_index(axis=1, inplace=True)

        # ck4, debugging only
        filename = os.path.join(self.output_location, 'cr-resampled-points.csv')  # J
        resampled_points_df.to_csv(filename)

        resampled_points = self._transform_df_points_to_calibrated_points(center_point,
                                                                          resampled_points_df)

        # ck4, debugging only
        from idmtools_calibra.resamplers.calibration_points import CalibrationPoints
        filename = os.path.join(self.output_location, 'cr-resampled-points-transformed.csv')  # K
        points = CalibrationPoints(resampled_points)
        points.write(filename)

        # this can be anything; will be made available for use in post_analysis() method in the from_resample argument
        for_post_analysis = np.concatenate((covariance, np.array(center_point_as_list)[None, :]), axis=0)

        # ck4, Verification, for review
        # J is the same as K, except for an additional indexing column in J
        # D is the same as E except for the LL column and end-of-line whitespace chars
        # E is the same as LLdata.csv from the RandomPerturbationResampler EXCEPT different param/LL column order (same values)
        #    -- This should be fine, as order preservation is only needed across (in/out) of CR resampling due to column renaming.
        # Parameter number ranges for input (cr-calibrated-points.csv) and output (cr-resampled-points.csv) are similar,
        #    e.g. col0 ~ 1.25, col1 ~ 2000, col2 ~ 0.65, col3 ~ 25

        # return reampled points
        return resampled_points, for_post_analysis

    def post_analysis(self, resampled_points, analyzer_results, from_resample):
        super().post_analysis(resampled_points, analyzer_results, from_resample=from_resample)
        output_filename = os.path.join(self.output_location, 'cr-resampled-points-ll.csv')
        resampled_points_ll_df = pd.DataFrame([rp.to_value_dict(include_likelihood=True) for rp in resampled_points])
        resampled_points_ll_df.to_csv(output_filename)

        covariance_matrix = from_resample[0:-1]
        center_calibrated = from_resample[-1]

        """ plotting """

        def plot_cov_ellipse(cov, pos, nstd=2, ax=None, **kwargs):
            """
            Plots an `nstd` sigma error ellipse based on the specified covariance
            matrix (`cov`). Additional keyword arguments are passed on to the
            ellipse patch artist.

            Args:
                cov : The 2x2 covariance matrix to base the ellipse on
                pos : The location of the center of the ellipse. Expects a 2-element
                    sequence of [x0, y0].
                nstd : The radius of the ellipse in numbers of standard deviations.
                    Defaults to 2 standard deviations.
                ax : The axis that the ellipse will be plotted on. Defaults to the
                    current axis.

                Additional keyword arguments are pass on to the ellipse patch.

            Returns:
                A matplotlib ellipse artist
            """

            def eigsorted(cov):
                vals, vecs = np.linalg.eigh(cov)
                order = vals.argsort()[::-1]
                return vals[order], vecs[:, order]

            if ax is None:
                ax = plt.gca()

            vals, vecs = eigsorted(cov)
            theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))

            # Width and height are "full" widths, not radius
            width, height = 2 * nstd * np.sqrt(vals)
            ellip = Ellipse(xy=pos, width=width, height=height, angle=theta, **kwargs)

            ax.add_artist(ellip)
            return ellip

        def scatterplot_matrix(samples, names, range_min, range_max, Covariance, center, **kwargs):
            """Plots a scatterplot matrix of subplots.  Each row of "data" is plotted
            against other rows, resulting in a nrows by nrows grid of subplots with the
            diagonal subplots labeled with "names".  Additional keyword arguments are
            passed on to matplotlib's "plot" command. Returns the matplotlib figure
            object containg the subplot grid."""
            numvars, numdata = samples.shape
            fig, axes = plt.subplots(nrows=numvars, ncols=numvars, figsize=(8, 8))
            fig.subplots_adjust(right=0.8, hspace=0.05, wspace=0.05)

            for ax in axes.flat:
                # Hide all ticks and labels
                ax.xaxis.set_visible(False)
                ax.yaxis.set_visible(False)

                # Set up ticks only on one side for the "edge" subplots...
                if ax.is_first_col():
                    ax.yaxis.set_ticks_position('left')
                if ax.is_last_col():
                    ax.yaxis.set_ticks_position('right')
                if ax.is_first_row():
                    ax.xaxis.set_ticks_position('top')
                if ax.is_last_row():
                    ax.xaxis.set_ticks_position('bottom')

            # Plot the data.
            for i, j in zip(*np.triu_indices_from(axes, k=1)):
                for x, y in [(i, j), (j, i)]:
                    scatterPlot = axes[x, y].scatter(samples[y], samples[x], **kwargs)
                    row_idx = np.array([y, x])
                    col_idx = np.array([y, x])
                    plot_cov_ellipse(Covariance[row_idx[:, None], col_idx], center[[y, x]], nstd=2, ax=axes[x, y],
                                     alpha=0.3, color='red')
                    if not (range_min is None):
                        axes[x, y].set_xlim(range_min[y], range_max[y])
                    if not (range_max is None):
                        axes[x, y].set_ylim(range_min[x], range_max[x])

            cax = fig.add_axes([0.85, 0.2, 0.05, 0.6])
            fig.colorbar(scatterPlot, cax=cax)
            plt.suptitle('Cramer Rao samples')

            # Label the diagonal subplots...
            for i, label in enumerate(names):
                axes[i, i].annotate(label, (0.5, 0.5), xycoords='axes fraction',
                                    ha='center', va='center')

            # Turn on the proper x or y axes ticks.
            for i, j in zip(range(numvars), itertools.cycle((-1, 0))):
                axes[j, i].xaxis.set_visible(True)
                axes[i, j].yaxis.set_visible(True)

            return fig

        resampled_points_dynamic = pd.DataFrame([rp.to_value_dict(parameter_type=CalibrationPoint.DYNAMIC,
                                                                  include_likelihood=True) for rp in resampled_points])

        pp = sns.pairplot(resampled_points_dynamic[resampled_points_dynamic.columns[0:-1]], size=1.8, aspect=1.8,
                          plot_kws=dict(edgecolor="k", linewidth=0.5), diag_kind="kde", diag_kws=dict(shade=True))

        fig = pp.fig
        fig.subplots_adjust(top=0.93, wspace=0.3)
        fig.savefig(os.path.join(self.output_location, 'samples_pairs.pdf'))
        fig.clf()
        plt.close(fig)
        del pp, fig

        # just to test plot the first two dynamic parameters
        fig, ax = plt.subplots()
        x = resampled_points_dynamic[resampled_points_dynamic.columns[0]]
        y = resampled_points_dynamic[resampled_points_dynamic.columns[1]]
        colors = resampled_points_dynamic[resampled_points_dynamic.columns[-1]]
        plt.scatter(x, y, c=colors, alpha=0.3, cmap='viridis')
        plt.xlabel(resampled_points_dynamic.columns.values[0])
        plt.ylabel(resampled_points_dynamic.columns.values[1])
        plt.title('log-likelihood of the samples')
        plt.xlim([rp._filter_parameters(parameter_type=CalibrationPoint.DYNAMIC) for rp in resampled_points][0][0].min,
                 [rp._filter_parameters(parameter_type=CalibrationPoint.DYNAMIC) for rp in resampled_points][0][0].max)
        plt.ylim([rp._filter_parameters(parameter_type=CalibrationPoint.DYNAMIC) for rp in resampled_points][0][1].min,
                 [rp._filter_parameters(parameter_type=CalibrationPoint.DYNAMIC) for rp in resampled_points][0][1].max)
        plt.colorbar()
        plt.savefig(os.path.join(self.output_location, 'samples_pairs_LL.pdf'))
        fig.clf()
        plt.close(fig)
        del ax, fig

        # scatter plot matrix
        minimums = resampled_points[0].get_attribute(key='Min', parameter_type=CalibrationPoint.DYNAMIC)
        maximums = resampled_points[0].get_attribute(key='Max', parameter_type=CalibrationPoint.DYNAMIC)
        fig = scatterplot_matrix(np.array(resampled_points_dynamic[resampled_points_dynamic.columns[0:-1]]).T,
                                 list(resampled_points_dynamic.columns.values[0:-1]), minimums, maximums,
                                 covariance_matrix, center_calibrated, c=colors, alpha=0.3, cmap='Greens')
        fig.savefig(os.path.join(self.output_location, 'scatterplot_matrix_entireRange.pdf'))
        fig.clf
        del fig

        fig = scatterplot_matrix(np.array(resampled_points_dynamic[resampled_points_dynamic.columns[0:-1]]).T,
                                 list(resampled_points_dynamic.columns.values[0:-1]), range_min=None, range_max=None,
                                 Covariance=covariance_matrix, center=center_calibrated,
                                 c=colors, alpha=0.3, cmap='Greens')
        fig.savefig(os.path.join(self.output_location, 'scatterplot_matrix_NoScale.pdf'))
        fig.clf
        del fig
