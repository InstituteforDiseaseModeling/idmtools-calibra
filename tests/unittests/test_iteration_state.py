import copy
import os
import unittest
from unittest import mock

from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask

from idmtools_calibra.algorithms.optim_tool import OptimTool
from idmtools_calibra.iteration_state import IterationState
from idmtools_calibra.process_state import StatusPoint


class TestIterationState(unittest.TestCase):
    expected_init_state = dict(
        {'iteration': 0,
         'calibration_name': None,
         'calibration_directory': os.getcwd(),
         'task': None,
         'sites': [],
         'suite_id': {},
         'samples_for_this_iteration': {},
         'next_point': {},
         'simulations': {},
         'analyzers': {},
         'results': {},
         'experiment_id': None,
         'next_point_algo': None,
         'analyzer_list': [],
         'site_analyzer_names': {},
         'experiment_builder_function': None,
         'map_sample_to_model_input_fn': None,
         'sim_runs_per_param_set': None,
         'plotters': [],
         'all_results': None,
         'summary_table': None,
         'iteration_start': None,
         'calibration_start': None,
         'resume': False,
         '_status': None}
    )

    def setUp(self):
        self.state = IterationState(calibration_directory=os.getcwd(), platform=Platform("SlurmStage"))

    def example_OptimalTool_settings(self):
        self.state.status = StatusPoint.done
        params = [
            {
                'Name': 'p2',
                'Dynamic': False,
                'Guess': 2000,
                'Min': 1200,
                'Max': 2400

            },
            {
                'Name': 'p1',
                'Dynamic': True,
                'Guess': 0.1,
                'Min': 0,
                'Max': 1,
                'MapTo': 'p1'

            },
        ]
        command = CommandLine("python --version")
        # create CommandTask
        task = CommandTask(command=command)

        optimtool = OptimTool(params, samples_per_iteration=5)
        self.state.next_point_algo = optimtool
        self.state.task = task
        self.state.next_point = optimtool.get_state()
        self.state.simulations = {
            'sims': {'sim_id1': {'p1': 1, 'p2': 2},
                     'sim_id2': {'p1': 3, 'p2': 4}}}
        self.state.analyzers = {'TestAnalyzer': "idmtools_calibra.analyzers.my_analyzer.TestAnalyzer"}
        self.state.results = {'TestAnalyzer': [-13, -11], 'Total': [-13, -11]}

    def test_init(self):
        self.state.__dict__.pop("platform")
        self.assertDictEqual(self.state.__dict__, self.expected_init_state)

    def test_to_save_OptimalTool(self):
        self.example_OptimalTool_settings()
        self.state.to_file()
        iter_state_file = os.path.join('iter0', 'IterationState.json')
        new_state = IterationState.from_file(iter_state_file)
        old_state = copy.deepcopy(self.state)
        self.assertDictEqual(new_state.simulations, old_state.simulations)
        self.assertDictEqual(new_state.analyzers, old_state.analyzers)
        self.assertDictEqual(new_state.results, old_state.results)
        self.assertDictEqual(new_state.next_point, old_state.next_point)
        self.assertEqual(self.state.all_results, None)
        self.assertEqual(self.state.analyzer_list, [])
        self.assertEqual(self.state.analyzers, {'TestAnalyzer': 'idmtools_calibra.analyzers.my_analyzer.TestAnalyzer'})
        self.assertEqual(self.state.calibration_directory, os.getcwd())
        # remove these 2 datatype for comparison since different machine may return different datatypes
        self.state.next_point.pop('regression_dtypes')
        self.state.next_point.pop('state_dtypes')
        self.assertEqual(self.state.next_point,
                         {'mu_r': 0.1, 'sigma_r': 0.02, 'center_repeats': 2, 'rsquared_thresh': 0.5, 'n_dimensions': 0,
                          'params': [{'Name': 'p2', 'Dynamic': False, 'Guess': 2000, 'Min': 1200, 'Max': 2400},
                                     {'Name': 'p1', 'Dynamic': True, 'Guess': 0.1, 'Min': 0, 'Max': 1, 'MapTo': 'p1'}],
                          'samples_per_iteration': 5, 'data': {}, 'data_dtypes': {},
                          'regression': {'Iteration': [], 'Parameter': [], 'Value': []},
                          'state': {'Iteration': [], 'Parameter': [], 'Center': [], 'Min': [], 'Max': [],
                                    'Dynamic': []}})
        self.assertEqual(self.state.results, {'TestAnalyzer': [-13, -11], 'Total': [-13, -11]})
        self.assertEqual(self.state.simulations,
                         {'sims': {'sim_id1': {'p1': 1, 'p2': 2}, 'sim_id2': {'p1': 3, 'p2': 4}}})
        self.assertEqual(self.state.iteration_file, str(os.path.join(os.getcwd(), 'iter0', 'IterationState.json')))
        os.remove(os.path.join('iter0', 'IterationState.json'))

    def test_commission_step(self):
        self.example_OptimalTool_settings()
        self.assertEqual(len(self.state.samples_for_this_iteration), 0)
        # we are not doing real commission to comps, instead we can mock commission_iteration step so we can test
        # everything before real commission
        with mock.patch('idmtools_calibra.iteration_state.IterationState.commission_iteration') as mock_fetch:
            self.state.commission_step()
            self.assertEqual(len(self.state.samples_for_this_iteration), 5)
            for sample in self.state.samples_for_this_iteration:
                self.assertEqual(sample['p2'], 2000.0)  # p2 is not dynamic parameter, so it should not change
                self.assertTrue(sample['p1'] <= 1 or sample['p1'] >= 0)
            self.assertEqual(self.state.status, StatusPoint.commission)

    def test_analyze_step(self):
        pass
