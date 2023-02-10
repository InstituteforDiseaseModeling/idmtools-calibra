import os
import unittest
import random

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.pyplot import cm

from idmtools_calibra.algorithms.optim_tool import OptimTool


class NextPointTestWrapper(object):
    """
    A simple wrapper for running iterative loops without all the CalibManager overhead.
    """

    def __init__(self, algo, n_samples):
        self.algo = algo
        self.n_samples = n_samples

    def run(self, max_iterations=100):
        samples = []
        for iteration in range(max_iterations):
            # fake analyzer result
            number_list = [30, 10, 5]
            data = {"MyAnalyzer": [random.choice(number_list) for i in range(self.n_samples)],
                    "total": [random.choice(number_list) for i in range(self.n_samples)]}
            results = pd.DataFrame(data)

            self.algo.samples_per_iteration = self.n_samples
            samples.append(self.algo.get_samples_for_iteration(iteration))
            self.algo.set_results_for_iteration(iteration, results)
            if self.algo.end_condition():
                break
        return samples, self.algo.get_final_samples()


def save_figure(fig, name):
    try:
        os.makedirs('tmp')
    except:
        pass  # directory already exists
    fig.savefig(os.path.join('tmp', '%s.png' % name))


class TestOptimalTools(unittest.TestCase):
    def setUp(self):
        self.n_samples = 100
        params = [{'Name': 'linear-coefficient', 'Dynamic': True, 'MapTo': 'a', 'Guess': 50, 'Min': 0, 'Max': 400},
                  {'Name': 'constant', 'Dynamic': True, 'MapTo': 'b', 'Guess': 500, 'Min': 0, 'Max': 2000}]
        self.params_df = pd.DataFrame(params)
        r = OptimTool.get_r(3, 0.003)
        self.optimtool = OptimTool(
            params,
            mu_r=r,
            sigma_r=r / 10.0,
            samples_per_iteration=self.n_samples,
        )

    def test_sample_hypersphere(self):
        self.n_samples = 10000
        state = self.params_df.drop(columns=['MapTo'])
        state = state.rename(columns = {'Name':'Parameter', 'Guess':'Center'})
        samples = self.optimtool.sample_hypersphere(self.n_samples, state)
        # plot samples. all sample should be all around center in hypersphere circle
        fig = plt.figure(1)
        ax1 = fig.gca()
        ax1.scatter(samples['linear-coefficient'], samples['constant'], s=0.5, c='green')
        fig.show()
        save_figure(fig, "test_sample_hypersphere")

    def test_choose_and_clamp_hypersphere_samples_for_iteration(self):
        self.n_samples = 10000
        # Call sample_hypersphere
        state = self.params_df.drop(columns=['MapTo'])
        state = state.rename(columns = {'Name':'Parameter', 'Guess':'Center'})
        samples = self.optimtool.sample_hypersphere(self.n_samples, state)
        #--------------------------------
        # Call choose_and_clamp_hypersphere_samples_for_iteration which should return similar result as sample_hypersphere
        # but all great than zeros
        iteration = [0,0]
        state['Iteration'] = iteration
        self.optimtool.state = state
        self.optimtool.samples_per_iteration = self.n_samples
        samples_with_clamp = self.optimtool.choose_and_clamp_hypersphere_samples_for_iteration(0)
        # make sure all samples_with_clamp are equal or great than zero
        self.assertTrue(np.all((samples_with_clamp[['linear-coefficient', 'constant']] >= 0).any(axis=1)))
        # plot samples and sample_with_clamp
        fig = plt.figure(2)
        ax1 = fig.gca()
        ax1.scatter(samples['linear-coefficient'], samples['constant'], s=0.5, c='blue')
        ax2 = fig.gca()
        ax2.scatter(samples_with_clamp['linear-coefficient'], samples_with_clamp['constant'], s=0.5, c='red')
        # Compare both samples and samples_with_clamp plots by eyes and they should be all around center in hypersphere
        # and latter ones all great than zero
        fig.show()
        save_figure(fig, "test_choose_and_clamp_hypersphere_samples_for_iteration")

    def test_choose_initial_samples(self):
        self.n_samples = 100
        self.assertEqual(len(self.optimtool.data), 0)
        initial_samples = self.optimtool.choose_initial_samples()
        self.assertEqual(len(self.optimtool.data), self.n_samples)
        self.assertTrue(self.optimtool.data[['linear-coefficient', 'constant']].equals(initial_samples))
        self.assertTrue(np.array_equal(self.optimtool.data['__sample_index__'].values, pd.Series(range(self.n_samples)).values))
        self.assertTrue(self.optimtool.data['Results'].isnull().values.any())
        self.assertTrue(self.optimtool.data['Fitted'].isnull().values.any())

    def test_choose_samples_via_gradient_ascent(self):
        self.n_samples = 10000
        # iter0
        self.optimtool.samples_per_iteration=self.n_samples
        samples_iter0 = self.optimtool.choose_initial_samples()
        self.assertTrue(np.all((samples_iter0[['linear-coefficient', 'constant']] >= 0).any(axis=1)))
        self.optimtool.samples_per_iteration = self.n_samples
        # Fake analyzer result from iter0
        number_list = [0.00004, 0.00003, 0.002]
        data = {"MyAnalyzer": [random.choice(number_list) for i in range(self.n_samples)],
                 "total": [random.choice(number_list) for i in range(self.n_samples)]}
        results = pd.DataFrame(data)
        iteration = 0
        self.optimtool.set_results_for_iteration(iteration, results)

        # iter1
        iteration = 1
        self.optimtool.samples_per_iteration = self.n_samples
        samples_iter1 = self.optimtool.choose_samples_via_gradient_ascent(iteration)
        self.assertTrue(np.all((samples_iter1[['linear-coefficient', 'constant']] >= 0).any(axis=1)))

        # plot samples
        fig = plt.figure(2)
        ax1 = fig.gca()
        ax1.scatter(samples_iter0['linear-coefficient'], samples_iter0['constant'], s=0.5, c='blue')
        ax2 = fig.gca()
        ax2.scatter(samples_iter1['linear-coefficient'], samples_iter1['constant'], s=0.5, c='red')
        # Compare both samples_iter0 and samples_iter1 plots by eyes and they should be all around  current iteration's
        # center in hypersphere and they are all great than zero
        fig.show()
        save_figure(fig, "test_choose_samples_via_gradient_ascent")

    def test_optimal_tools_run(self):
        self.n_samples = 1000
        max_iterations = 10

        tester = NextPointTestWrapper(self.optimtool, self.n_samples)
        samples, final_sample = tester.run(max_iterations=max_iterations)
        self.assertIsNotNone(final_sample['final_samples']['linear-coefficient'])
        self.assertIsNotNone(final_sample['final_samples']['constant'])
        print(final_sample)

        fig = plt.figure(max_iterations)

        color = cm.rainbow(np.linspace(0, 1, max_iterations))
        for i, c in zip(range(max_iterations), color):
            ax1 = fig.gca()
            s = pd.DataFrame(samples[i])
            ax1.scatter(s['linear-coefficient'], s['constant'], s=0.5, c=c)
            fig.show()
        save_figure(fig, "test_optimal_tools_run")



