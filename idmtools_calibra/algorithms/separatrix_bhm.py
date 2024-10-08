import logging

import numpy as np
import pandas as pd

from idmtools_calibra.algorithms.next_point_algorithm import NextPointAlgorithm

logger = logging.getLogger(__name__)
user_logger = logging.getLogger('user')
try:
    from history_matching.gpc import GPC
except ImportError as ex:
    user_logger.error("Separatrix_BHM requires history matching")
    raise ex


class SeparatrixBHM(NextPointAlgorithm):
    """
    Separatrix using Bayesian History Matching

    The basic idea of Separatrix is that each simulation results in a success (+1) or a failure (-1), and the success probability varies as a function of the input parameters.  We seek an isocline of the the latent success probability function.
    """

    def __init__(self,
                 params,
                 constrain_sample_fn=lambda s: s,  # Allows the user to move samples in order to meet a constraint
                 implausibility_threshold=3,
                 # Essentially the risk tolerance.  Higher numbers will be more careful to not reject potentially good regions of parameter space, but the result is that more iteration/simulations will be required
                 target_success_probability=0.7,  # This is the success probability isocline that we seek to identify
                 num_past_iterations_to_include_in_metamodel=3,
                 # When emulating the latent success probability function, include simulation results from this many previous iterations.  NOTE: Set <0 to include all previous simulation.
                 samples_per_iteration=32,  # Number of samples to simulate on a typical iteration
                 samples_final_iteration=128,  # Number of samples in simulate on the final iteration
                 max_iterations=10,  # Number of iterations (determines when to use samples_final_iteration)
                 training_frac=0.8
                 # Fraction of simulations to use a training data (will plot in cyan instead of magenta)
                 ):

        super(SeparatrixBHM, self).__init__()
        self.args = locals()  # Store inputs in case set_state is called later and we want to override with new (user) args
        del self.args['self']
        self.need_resolve = False

        self.constrain_sample_fn = constrain_sample_fn
        self.max_iterations = max_iterations

        self.emulation = pd.DataFrame(columns=['Iteration', 'Sample', 'Mean', 'Var'])
        self.for_plotting = pd.DataFrame()

        self.param_info = pd.DataFrame(params).reset_index(drop=True).set_index('Name')
        self.param_names = self.param_info.index.values.tolist()

        self.implausibility_threshold = implausibility_threshold  # Check that does not go up over iterations!
        self.target_success_probability = target_success_probability  # This cannot change, make sure it doesn't!

        # These can change on an iteration-by-iteration basis
        self.num_past_iterations_to_include_in_metamodel = int(num_past_iterations_to_include_in_metamodel)
        self.samples_per_iteration = int(samples_per_iteration)
        self.samples_final_iteration = int(samples_final_iteration)
        self.training_frac = training_frac

        self.n_dimensions = len(self.param_info)
        self.x_min = {k: v['Min'] for k, v in self.param_info.iterrows()}
        self.x_max = {k: v['Max'] for k, v in self.param_info.iterrows()}

        # GPC hyperparameter guess and range bounds
        # TODO: Resolve these
        # TODO: Allow user to enter guess values and bounds!
        self.theta_guess = np.array(
            [20] + [0.5] * self.n_dimensions)  # sigma^2 followed by squared lengthscales for each dimension
        self.bounds = ((0.005, 100),) + tuple(self.n_dimensions * ((0.001, 2.0),))
        self.hyperparameters = pd.DataFrame(
            columns=['sigma^2'] + ['lengthscale^2_%d' % i for i in range(self.n_dimensions)] + ['fun',
                                                                                                'accepted percent',
                                                                                                'success'])
        self.hyperparameters.loc[0] = np.append([np.NaN] * (self.n_dimensions + 2), [100, np.NaN])
        self.gpc_vec = []

        self.data = pd.DataFrame()

    def cleanup(self):
        pass

    def resolve_args(self, iteration):
        # Have args from user and from set_state.
        # Note this is called only right before commissioning a new iteration, likely from 'resume'

        # TODO: be more sensitive with params, user could have added or removed variables, need to adjust
        # TODO: Check min <=  max for params
        # TODO: could clean this up with a helper function
        if 'params' in self.args['params']:
            self.param_info = pd.DataFrame(self.args['params']).reset_index(drop=True).set_index('Name')

        self.implausibility_threshold = self.args[
            'implausibility_threshold'] if 'implausibility_threshold' in self.args else self.implausibility_threshold
        self.target_success_probability = self.args[
            'target_success_probability'] if 'target_success_probability' in self.args else self.target_success_probability
        self.num_past_iterations_to_include_in_metamodel = self.args[
            'num_past_iterations_to_include_in_metamodel'] if 'num_past_iterations_to_include_in_metamodel' in self.args else self.num_past_iterations_to_include_in_metamodel
        self.training_frac = self.args['training_frac'] if 'training_frac' in self.args else self.training_frac
        self.samples_per_iteration = self.args[
            'samples_per_iteration'] if 'samples_per_iteration' in self.args else self.samples_per_iteration
        self.samples_final_iteration = self.args[
            'samples_final_iteration'] if 'samples_final_iteration' in self.args else self.samples_final_iteration

        self.n_dimensions = len(self.param_info)
        self.x_min = {k: v['Min'] for k, v in self.param_info.iterrows()}
        self.x_max = {k: v['Max'] for k, v in self.param_info.iterrows()}

        self.need_resolve = False

    def add_samples(self, samples, iteration):
        samples_cpy = samples.copy()
        samples_cpy.index.name = '__sample_index__'
        samples_cpy['Iteration'] = iteration
        samples_cpy.reset_index(inplace=True)

        self.data = pd.concat([self.data, samples_cpy], ignore_index=True)
        self.data['__sample_index__'] = self.data['__sample_index__'].astype(int)

    def get_samples_for_iteration(self, iteration):
        # Update args
        if self.need_resolve:
            self.resolve_args(iteration)

        if iteration == 0:
            # Choose initial samples by LHS
            samples = self.choose_initial_samples()
        else:
            # Choose initial samples by History Matching
            samples = self.choose_samples_via_history_matching(iteration)

        samples.reset_index(drop=True, inplace=True)
        return self.generate_samples_from_df(samples)

    def set_results_for_iteration(self, iteration, results):
        results = results.total.tolist()
        logger.info('%s: Choosing samples at iteration %d:', self.__class__.__name__, iteration)
        logger.debug('Results:\n%s', results)

        data_by_iter = self.data.set_index('Iteration')
        if iteration + 1 in data_by_iter.index.unique():
            # Been here before, reset
            data_by_iter = data_by_iter.loc[:iteration]

            emulation_by_iter = self.emulation_index('Iteration')
            self.emulation = emulation_by_iter.loc[:iteration - 1].reset_index()

        # Store results ... even if changed
        data_by_iter.loc[iteration, 'Results'] = results
        self.data = data_by_iter.reset_index()

    def set_gpc_vec(self, iteration, gpc):
        if len(self.gpc_vec) == iteration:
            self.gpc_vec.append(gpc)
        else:
            assert (len(self.gpc_vec) >= iteration)
            self.gpc_vec[iteration] = gpc

    def choose_initial_samples(self):
        self.data = pd.DataFrame(columns=['Iteration', '__sample_index__', 'Train', 'Results', *self.get_param_names()])
        self.data['Iteration'] = self.data['Iteration'].astype(int)
        self.data['__sample_index__'] = self.data['__sample_index__'].astype(int)

        self.n_dimensions = len(self.param_info)

        iteration = 0

        N = self.samples_per_iteration if self.max_iterations > 1 else self.samples_final_iteration
        initial_samples = pd.DataFrame(np.random.rand(N, self.n_dimensions), columns=self.param_names)

        # Scale
        for param_name, v in self.param_info.iterrows():
            initial_samples[param_name] = v['Min'] + initial_samples[param_name] * (v['Max'] - v['Min'])
        initial_samples.index.name = 'Sample'
        initial_samples.reset_index(inplace=True)
        initial_samples['Train'] = False
        initial_samples.loc[
            np.random.binomial(n=1, p=self.training_frac, size=initial_samples.shape[0]) == 1, 'Train'] = True
        initial_samples = initial_samples.apply(self.constrain_sample_fn, axis=1)

        self.add_samples(initial_samples, iteration)

        self.set_gpc_vec(iteration, None)  # No GPC for iter 0

        return initial_samples[self.param_names]

    def choose_samples_via_history_matching(self, iteration):
        train = self.data.loc[self.data['Train']]
        if self.num_past_iterations_to_include_in_metamodel > 0:
            train = train.loc[train['Iteration'] >= iteration - self.num_past_iterations_to_include_in_metamodel]

        # Fit the emulator (GPC)
        gpc = GPC(self.param_names, 'Results', train, self.param_info,
                  kernel_mode='RBF',
                  kernel_params=self.theta_guess,  # Sigma_f^2, lengthscale_x^2, lengthscale_y^2, ...
                  verbose=False,
                  debug=False
                  )

        self.set_gpc_vec(iteration, gpc)

        # Optimize hyperparameters
        optim = self.gpc_vec[iteration].optimize_hyperparameters(
            x0=self.theta_guess,
            bounds=self.bounds,
            eps=1e-3,
            disp=False,
            maxiter=15000
        )
        self.theta_guess = optim.x  # Set result as guess for nex titeration

        emulation_results = self.gpc_vec[iteration].evaluate(self.data)
        emulation_results['Iteration'] = iteration - 1
        emulation_results['Sample'] = self.data['Sample']
        self.emulation = pd.concat([self.emulation, emulation_results])

        # Refocusing
        next_samples = pd.DataFrame(columns=self.param_names + ['Implausible'])
        accepted = 0
        tried = 0
        self.for_plotting = pd.DataFrame(columns=self.param_names)

        N = self.samples_per_iteration if iteration < self.max_iterations - 1 else self.samples_final_iteration
        while next_samples.shape[0] < N:
            n = N - next_samples.shape[0]
            if tried > 0 and accepted > 0:
                n = int(np.ceil(n / (accepted / tried)))
            proposal = pd.DataFrame(np.random.rand(n, 2), columns=self.param_names)

            # Scale
            for param_name, v in self.param_info.iterrows():
                proposal[param_name] = v['Min'] + proposal[param_name] * (v['Max'] - v['Min'])

            # User constraint fn
            proposal = proposal.apply(self.constrain_sample_fn, axis=1)

            proposal['Implausible'] = False
            proposal['Max_Implausibility'] = -1  # For plotting
            for it in reversed(range(1, iteration + 1)):
                # TODO: Only evaluate non-implausible points to save time, although will degrade plotting
                ret = self.gpc_vec[it].evaluate(proposal)
                proposal['Implausibility_%d' % it] = np.sqrt(
                    (ret['Mean'] - self.target_success_probability) ** 2 / ret['Var'])
                proposal['Implausibile_%d' % it] = proposal['Implausibility_%d' % it] > self.implausibility_threshold
                proposal['Implausible'] = proposal['Implausible'] | proposal['Implausibile_%d' % it]
                proposal['Max_Implausibility'] = pd.concat(
                    [proposal['Max_Implausibility'], proposal['Implausibility_%d' % it]], axis=1).max(
                    axis=1)  # Better way?

            self.for_plotting = self.for_plotting.append(proposal[self.param_names + ['Max_Implausibility']],
                                                         ignore_index=True)
            new_samples = proposal.loc[~proposal['Implausible']]
            next_samples = next_samples.append(proposal.loc[~proposal['Implausible']])
            tried = tried + n
            accepted = accepted + new_samples.shape[0]
            accepted_percent = 100 * accepted / tried
            user_logger.info('Found %d new samples, now have %d of %d. Acceptance rate is %.0f%%' % (
                new_samples.shape[0], next_samples.shape[0], N, accepted_percent))

        self.hyperparameters.loc[iteration] = np.append(self.gpc_vec[iteration].theta,
                                                        [optim['fun'], accepted_percent, optim['success']])

        next_samples = next_samples.iloc[:N]  # Trim if needed
        next_samples['Iteration'] = iteration
        next_samples['Train'] = False
        next_samples.loc[np.random.binomial(n=1, p=self.training_frac, size=next_samples.shape[0]) == 1, 'Train'] = True
        n = self.data.shape[0]
        next_samples['Sample'] = list(range(n + 1, n + next_samples.shape[0] + 1))
        self.add_samples(next_samples, iteration)

        return next_samples[self.param_names]

    def end_condition(self):
        # TODO: Stopping condition ... possibly based on reductions in grown of implausible volume
        logger.info('Continuing iterations ...')
        return False

    def get_final_samples(self):
        """
        Return some number of samples from the residual non-implausible area:
        """

        return {'final_samples': self.prep_for_dict(self.data)}

    def prep_for_dict(self, df):
        return df.where(~df.isnull(), other=None).to_dict(orient='list')

    def get_state(self):

        separatrix_state = dict(
            implausibility_threshold=self.implausibility_threshold,
            target_success_probability=self.target_success_probability,
            num_past_iterations_to_include_in_metamodel=self.num_past_iterations_to_include_in_metamodel,
            training_frac=self.training_frac,
            samples_per_iteration=self.samples_per_iteration,
            samples_final_iteration=self.samples_final_iteration,
            n_dimensions=self.n_dimensions,
            params=self.prep_for_dict(self.param_info.reset_index()),

            hyperparameters=self.prep_for_dict(self.hyperparameters),
            data=self.prep_for_dict(self.data),
            data_dtypes={name: str(data.dtype) for name, data in self.data.items()},

            emulation=self.prep_for_dict(self.emulation),
            emulation_dtypes={name: str(data.dtype) for name, data in self.emulation.items()},

            for_plotting=self.prep_for_dict(self.for_plotting),
            max_iterations=self.max_iterations,

            gpc_vec=[g.save() if g else None for g in self.gpc_vec]
        )
        return separatrix_state

    def set_state(self, state, iteration):

        self.implausibility_threshold = state['implausibility_threshold']
        self.target_success_probability = state['target_success_probability']
        self.num_past_iterations_to_include_in_metamodel = state['num_past_iterations_to_include_in_metamodel']
        self.training_frac = state['training_frac']
        self.samples_per_iteration = state['samples_per_iteration']
        self.samples_final_iteration = state['samples_final_iteration']
        self.n_dimensions = state['n_dimensions']

        self.param_info = pd.DataFrame.from_dict(state['params'], orient='columns').set_index('Name')

        self.max_iterations = state['max_iterations']

        self.hyperparameters = pd.DataFrame.from_dict(state['hyperparameters'], orient='columns')
        self.emulation = pd.DataFrame.from_dict(state['emulation'], orient='columns')

        data_dtypes = state['data_dtypes']
        self.data = pd.DataFrame.from_dict(state['data'], orient='columns')
        for c in self.data.columns:  # Argh
            self.data[c] = self.data[c].astype(data_dtypes[c])

        self.for_plotting = pd.DataFrame.from_dict(state['for_plotting'], orient='columns')

        self.gpc_vec = [GPC.from_dict(config) if config else None for config in state['gpc_vec']]

        self.need_resolve = True

    def get_param_names(self):
        return self.param_names
