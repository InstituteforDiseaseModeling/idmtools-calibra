import logging
import os
import matplotlib
matplotlib.use('Agg', warn=False, force=True)
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
import pandas as pd
import seaborn as sns
from itertool.plotters.base_plotter import BasePlotter
from itertool.utils import StatusPoint

logger = logging.getLogger(__name__)
try:
    from history_matching.gpc import GPC
except ImportError:
    logger.warning("Could not load history matching. You must install itertool with history matching")
    logger.warning("pip install itertool[history-matching]")

sns.set_style('white')
fs = (16, 10)  # Figure size (24,15)


class SeparatrixBHMPlotter(BasePlotter):
    def __init__(self):
        super(SeparatrixBHMPlotter, self).__init__(False)

        self.prediction_grid = pd.DataFrame()
        self.prediction_resolution = 100

    def make_prediction_grid(self):
        # Prediction grid - for plotting when 2 parameters

        assert (len(self.param_names) == 2)

        self.x_var = self.param_names[0]
        self.y_var = self.param_names[1]

        Px = Py = self.prediction_resolution
        px = np.linspace(self.param_info.loc[self.x_var]['Min'], self.param_info.loc[self.x_var]['Max'], Px)
        py = np.linspace(self.param_info.loc[self.y_var]['Min'], self.param_info.loc[self.y_var]['Max'], Py)
        self.Px, self.Py = np.meshgrid(px, py)

        self.prediction_grid = pd.DataFrame({self.x_var: self.Px.flatten(), self.y_var: self.Py.flatten()})
        self.prediction_grid['Outcome'] = np.NaN
        self.prediction_grid.index.name = 'Sample'
        self.prediction_grid.reset_index(inplace=True)

        self.prediction_grid['Implausible'] = False
        self.prediction_grid['Max_Implausibility'] = -1  # For plotting

    def cleanup(self):
        pass

    def visualize(self, iteration_state):
        self.iteration_state = iteration_state
        iteration_status = self.iteration_state.status

        self.directory = self.iteration_state.iteration_directory
        self.param_names = self.iteration_state.param_names

        self.npt = self.iteration_state.next_point_algo.get_state()

        self.data = pd.DataFrame.from_dict(self.npt['data'])
        self.hyperparameters = pd.DataFrame.from_dict(self.npt['hyperparameters'])
        self.emulation = pd.DataFrame.from_dict(self.npt['emulation'])
        self.gpc_vec = [GPC.from_dict(config) if config else None for config in self.npt['gpc_vec']]
        self.param_info = pd.DataFrame.from_dict(self.npt['params'], orient='columns').set_index('Name')
        self.target = self.npt['target_success_probability']
        self.implausibility_threshold = self.npt['implausibility_threshold']
        self.for_plotting = pd.DataFrame.from_dict(self.npt['for_plotting'])

        if self.prediction_grid.shape[0] == 0:
            self.make_prediction_grid()

        if iteration_status == StatusPoint.commission:
            if self.iteration_state.iteration > 0:
                self.visualize_at_start_of_iteration()
        elif iteration_status == StatusPoint.plot:
            self.visualize_at_end_of_iteration()
        else:
            raise Exception('Unknown stage %s' % iteration_status.name)

        ###gc.collect()

    def visualize_at_end_of_iteration(self):
        if len(self.param_names) != 2:
            return

        iteration = self.iteration_state.iteration
        max_iterations = self.npt['max_iterations']

        if iteration == 0:
            return

        prev_data = self.data.loc[self.data['Iteration'] < iteration]
        # prev_data = prev_data.merge( self.emulation, on=['Iteration', 'Sample'])
        prev_data_prediction = self.gpc_vec[iteration].evaluate(prev_data)
        prev_data = prev_data.merge(prev_data_prediction, left_index=True, right_index=True)

        fig, ax = plt.subplots(1, 2, figsize=fs)
        # fig = plt.figure(figsize=fs)
        # ax = []
        # ax.append(fig.add_subplot(1,2,1)) #, projection='3d', proj_type = 'ortho'))
        # ax.append(fig.add_subplot(1,2,2))#, projection='3d', proj_type = 'ortho'))

        success = prev_data['Results'] == 1

        # ax[0].tricontourf(prev_data[self.x_var], prev_data[self.y_var], prev_data['Mean'], levels=25, cmap="RdBu_r")
        triang = mtri.Triangulation(prev_data[self.x_var], prev_data[self.y_var])
        ax[0].tripcolor(triang, prev_data['Mean'], cmap='RdBu_r', shading='gouraud')

        ax[0].tricontour(prev_data[self.x_var], prev_data[self.y_var], prev_data['Mean'], levels=[self.target],
                         linewidths=2, colors='k')
        ax[0].set_xlabel(self.x_var)
        ax[0].set_xlim([self.param_info.loc[self.x_var, 'Min'], self.param_info.loc[self.x_var, 'Max']])
        ax[0].set_ylabel(self.y_var)
        ax[0].set_ylim([self.param_info.loc[self.y_var, 'Min'], self.param_info.loc[self.y_var, 'Max']])
        ax[0].set_title('Mean')

        ax[0].scatter(prev_data.loc[success, self.x_var], prev_data.loc[success, self.y_var], s=50, c='r', marker='o',
                      edgecolors='k', linewidths=1)
        ax[0].scatter(prev_data.loc[~success, self.x_var], prev_data.loc[~success, self.y_var], s=50, c='b', marker='o',
                      edgecolors='k', linewidths=1)

        # ax[1].tricontourf(prev_data[self.x_var], prev_data[self.y_var], np.sqrt(prev_data['Var']), cmap="RdBu_r")
        ax[1].tripcolor(triang, np.sqrt(prev_data['Var']), cmap='RdBu_r', shading='gouraud')

        ax[1].set_xlabel(self.x_var)
        ax[1].set_xlim([self.param_info.loc[self.x_var, 'Min'], self.param_info.loc[self.x_var, 'Max']])
        ax[1].set_ylabel(self.y_var)
        ax[1].set_ylim([self.param_info.loc[self.y_var, 'Min'], self.param_info.loc[self.y_var, 'Max']])
        ax[1].set_title('Stdev')

        ax[1].scatter(prev_data.loc[success, self.x_var], prev_data.loc[success, self.y_var], s=50, c='r', marker='o',
                      edgecolors='k', linewidths=1)
        ax[1].scatter(prev_data.loc[~success, self.x_var], prev_data.loc[~success, self.y_var], s=50, c='b', marker='o',
                      edgecolors='k', linewidths=1)

        plt.savefig(os.path.join(self.directory, 'Separatrix_it%d.png' % iteration))
        plt.close(fig)

    def visualize_at_start_of_iteration(self):
        iteration = self.iteration_state.iteration

        # Plot 2d scatter of points?
        # Plot % space removed - would be zero on iter 0?

        if iteration == 0:
            return

        ########## Hyperparameters and function value
        fig, ax_vec = plt.subplots(nrows=1, ncols=self.hyperparameters.shape[1], sharex=True,
                                   figsize=(16, 10))  # , figsize=fs
        for i, ax in enumerate(ax_vec):
            hp_name = self.hyperparameters.columns[i]
            ax.plot(self.hyperparameters[hp_name], marker='o', ls='-')
            ax.set_title(hp_name)
        plt.savefig(os.path.join(self.directory, 'Separatrix_Hyperparameters_it%d.png' % iteration))
        plt.close(fig)

        ########## Accepted percent
        fig, ax_vec = plt.subplots(nrows=1, ncols=self.hyperparameters.shape[1], sharex=True,
                                   figsize=(16, 10))  # , figsize=fs
        for i, ax in enumerate(ax_vec):
            hp_name = self.hyperparameters.columns[i]
            ax.plot(self.hyperparameters[hp_name], marker='o', ls='-')
            ax.set_title(hp_name)
        plt.savefig(os.path.join(self.directory, 'Separatrix_Hyperparameters_%d.png' % iteration))
        plt.close(fig)

        ########## Evaluate GPC on prediction grid for plotting

        prediction = self.gpc_vec[iteration].evaluate(self.prediction_grid)

        # if 'Mean' in self.data: self.data.drop('Mean', axis=1, inplace=True)
        # if 'Var' in self.data: self.data.drop('Var', axis=1, inplace=True)

        next_data = self.data.loc[self.data['Iteration'] == iteration]

        prev_data = self.data.loc[self.data['Iteration'] < iteration]
        emu_iter = self.emulation.set_index('Iteration').loc[iteration - 1]
        prev_data = prev_data.merge(emu_iter, on=['Sample'])

        train = self.gpc_vec[iteration].training_data.reset_index()  # prev_data.loc[prev_data['Train'] == True]
        train = train.merge(emu_iter, on=['Sample'])
        test = prev_data.loc[prev_data['Train'] == False]

        fig = self.gpc_vec[iteration].plot_errors(train, test, 'Mean', 'Var')
        plt.savefig(os.path.join(self.directory, 'Separatrix_Errors_it%d.png' % iteration))
        plt.close(fig)

        ######
        fig = plt.figure(figsize=fs)
        fig.suptitle('Iteration %d' % iteration, fontsize=12)
        ax1 = fig.add_subplot(1, 2, 1, projection='3d')
        ax2 = fig.add_subplot(1, 2, 2)

        success = prev_data['Results'] == 1

        # ax1.scatter(prev_data[self.x_var], prev_data[self.y_var], 0.5*(prev_data['Results']+1), c='k', marker='*')#, 25, marker='*', color='k')
        ax1.scatter(prev_data.loc[success, self.x_var], prev_data.loc[success, self.y_var],
                    0.5 * (prev_data.loc[success, 'Results'] + 1), s=50, c='g', marker='*')
        ax1.scatter(prev_data.loc[~success, self.x_var], prev_data.loc[~success, self.y_var],
                    0.5 * (prev_data.loc[~success, 'Results'] + 1), s=50, c='r', marker='*')

        # ax1.scatter(self.prediction_grid[self.x_var], self.prediction_grid[self.y_var], prediction['Mean'], c='b', marker='o')
        # cntr = ax1.tricontourf(self.prediction_grid[self.x_var], self.prediction_grid[self.y_var], prediction['Mean'], cmap="Blues", alpha=0.5)
        X = self.prediction_grid[self.x_var].values.reshape(self.prediction_resolution, self.prediction_resolution)
        Y = self.prediction_grid[self.y_var].values.reshape(self.prediction_resolution, self.prediction_resolution)
        Z = prediction['Mean'].values.reshape(self.prediction_resolution, self.prediction_resolution)
        s = np.sqrt(prediction['Var'])
        S = s.values.reshape(self.prediction_resolution, self.prediction_resolution)
        ax1.plot_surface(X, Y, Z, cmap="Blues", alpha=0.5, edgecolors='none', linewidth=0, antialiased=True)

        # ax1.scatter(self.prediction_grid[self.x_var], self.prediction_grid[self.y_var], prediction['Mean'] + 2*np.sqrt(prediction['Var']), c = 'm', marker='o')
        ax1.plot_surface(X, Y, Z + 2 * S, color='k', alpha=0.1, edgecolors='none', linewidth=0, antialiased=True)
        # ax1.scatter(self.prediction_grid[self.x_var], self.prediction_grid[self.y_var], prediction['Mean'] - 2*np.sqrt(prediction['Var']), c = 'c', marker='o')
        ax1.plot_surface(X, Y, Z - 2 * S, color='k', alpha=0.1, edgecolors='none', linewidth=0, antialiased=True)

        ax1.set_xlabel(self.x_var)
        ax1.set_xlim([self.param_info.loc[self.x_var, 'Min'], self.param_info.loc[self.x_var, 'Max']])
        ax1.set_ylabel(self.y_var)
        ax1.set_ylim([self.param_info.loc[self.y_var, 'Min'], self.param_info.loc[self.y_var, 'Max']])
        ax1.set_zlabel('Outcome')
        ax1.set_zlim([-1.2, 1.2])
        ax1.set_title('GPC Metamodel')

        # Add in points from p to increase plotting resolution
        # for it in reversed(range(iteration+1)):
        # TODO: Only evaluate non-implausible points to save time, although will degrate plotting
        self.prediction_grid['Implausibility_%d' % iteration] = np.sqrt(
            (prediction['Mean'] - self.target) ** 2 / prediction['Var'])
        self.prediction_grid['Implausibile_%d' % iteration] = self.prediction_grid[
                                                                  'Implausibility_%d' % iteration] > self.implausibility_threshold
        self.prediction_grid['Implausible'] = self.prediction_grid['Implausible'] | self.prediction_grid[
            'Implausibile_%d' % iteration]
        self.prediction_grid['Max_Implausibility'] = pd.concat(
            [self.prediction_grid['Max_Implausibility'], self.prediction_grid['Implausibility_%d' % iteration]],
            axis=1).max(axis=1)  # Better way?

        self.for_plotting = self.for_plotting.append(
            self.prediction_grid[[self.x_var, self.y_var, 'Max_Implausibility']], ignore_index=True)

        self.for_plotting.loc[self.for_plotting[
                                  'Max_Implausibility'] > self.implausibility_threshold + 2, 'Max_Implausibility'] = self.implausibility_threshold + 2
        ax2.tricontour(self.for_plotting[self.x_var], self.for_plotting[self.y_var],
                       self.for_plotting['Max_Implausibility'], levels=[self.implausibility_threshold], linewidths=2,
                       colors='k')
        levels = list(range(self.implausibility_threshold + 4))
        cntr2 = ax2.tricontourf(self.for_plotting[self.x_var], self.for_plotting[self.y_var],
                                self.for_plotting['Max_Implausibility'], levels=levels, cmap="RdBu_r")

        ax2.plot(next_data[self.x_var], next_data[self.y_var], 'yo')
        ax2.plot(prev_data.loc[success, self.x_var], prev_data.loc[success, self.y_var], 'wo')
        ax2.plot(prev_data.loc[~success, self.x_var], prev_data.loc[~success, self.y_var], 'ko')
        ax2.plot(train[self.x_var], train[self.y_var], 'cx')
        ax2.plot(test[self.x_var], test[self.y_var], 'mx')
        for idx, row in test.iterrows():
            ax2.annotate(xy=(row[self.x_var], row[self.y_var]), s=str(row['Sample']))
        # ax2.contour(self.Px, self.Py, self.Pf, levels = [self.target], colors='k', linestyles='dashed', linewidths=2)
        ax2.set_xlabel(self.x_var)
        ax2.set_xlim([self.param_info.loc[self.x_var, 'Min'], self.param_info.loc[self.x_var, 'Max']])
        ax2.set_ylim([self.param_info.loc[self.y_var, 'Min'], self.param_info.loc[self.y_var, 'Max']])
        ax2.set_ylabel(self.y_var)
        ax2.set_title('Implausibility & Next Samples')

        plt.savefig(os.path.join(self.directory, 'Separatrix_Implausibility_it%d.png' % iteration))
        plt.close(fig)

    def cleanup_plot(self, calib_manager):
        pass
