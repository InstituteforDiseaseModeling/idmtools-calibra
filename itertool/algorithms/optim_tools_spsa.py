import logging

import numpy as np
import pandas as pd

from itertool.algorithms.next_point_algorithm import NextPointAlgorithm

logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimToolSPSA(NextPointAlgorithm):
    """
    OptimToolSPSA

    The basic idea of OptimToolSPSA is
    """

    def cleanup(self):
        pass

    def __init__(self, params, constrain_sample_fn, comps_per_iteration=10):
        super().__init__()
        self.args = locals()  # Store inputs in case set_state is called later and we want to override with new (user) args
        del self.args['self']
        self.need_resolve = False

        self.constrain_sample_fn = constrain_sample_fn

        self.state = pd.DataFrame(columns=['Iteration', 'Parameter', 'Center', 'Hessian', 'Min', 'Max', 'Dynamic'])
        self.state['Iteration'] = self.state['Iteration'].astype(int)

        self.params = params  # TODO: Check min <= center <= max
        self.comps_per_iteration = int(comps_per_iteration)

        self.x_min = {p['Name']: p['Min'] for p in self.params}
        self.x_max = {p['Name']: p['Max'] for p in self.params}
        self.Dynamic = {p['Name']: p['Dynamic'] for p in self.params}
        self.n_dimensions = None
        self.data = pd.DataFrame()

    def resolve_args(self, iteration):
        # Have args from user and from set_state.
        # Note this is called only right before commissioning a new iteration, likely from 'resume'

        # TODO: be more sensitive with params, user could have added or removed variables, need to adjust
        # TODO: Check min <= center <= max for params
        # TODO: could clean this up with a helper function
        self.params = self.args[
            'params'] if 'params' in self.args else self.params  # Guess may move, but should be ignored
        self.comps_per_iteration = self.args[
            'comps_per_iteration'] if 'comps_per_iteration' in self.args else self.comps_per_iteration

        self.n_dimensions = len(self.params)
        self.x_min = {p['Name']: p['Min'] for p in self.params}
        self.x_max = {p['Name']: p['Max'] for p in self.params}
        self.Dynamic = {p['Name']: p['Dynamic'] for p in self.params}

        self.need_resolve = False

        """
        # TODO: Allow user to override current 'Center' value
        state_by_iter = self.state.set_index('Iteration')
        if iteration == 0:
            # Not sure this would happen, but just in case
            cur_val = {p['Name']:p['Guess'] for p in self.params}
        else:
            cur_val = {s['Parameter']:s['Center'] for (i,s) in state_by_iter.loc[iteration-1].iterrows()}

        iter_state = pd.DataFrame(columns=['Iteration', 'Parameter', 'Center', 'Min', 'Max', 'Dynamic'])
        for param in self.params:
            iter_state.loc[len(iter_state)] = [iteration, param['Name'], cur_val[param['Name']], param['Min'], param['Max'], param['Dynamic']]

        self.state = self.state.loc[:iteration-1]
        self.state.reset_index(inplace=True)
        self.state = pd.concat([self.state, iter_state], ignore_index=True)
        self.state['Iteration'] = self.state['Iteration'].astype(int)

        with pd.option_context("display.max_rows", 500, "display.max_columns", 500):
            print(self.state)
            raw_input('resolve_args')
        """

    def _get_X_center(self, iteration):
        state_by_iter = self.state.reset_index(drop=True).set_index(['Iteration', 'Parameter'])
        assert (iteration in state_by_iter.index.get_level_values('Iteration'))
        return state_by_iter.loc[iteration]['Center']

    def _get_Hessian(self, iteration):
        state_by_iter = self.state.reset_index(drop=True).set_index(['Iteration', 'Parameter'])
        assert (iteration in state_by_iter.index.get_level_values('Iteration'))
        return state_by_iter.loc[iteration]['Hessian']

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
            # Choose initial samples
            samples = self.choose_initial_samples()
        else:
            # Regress inputs and results from previous iteration
            # Move X_center, choose samples, save in dataframe
            samples = self.stochastic_newton_raphson(iteration)

        samples.reset_index(drop=True, inplace=True)
        return self.generate_samples_from_df(samples)

    def clamp(self, X):

        # print("X.before:\n{}".format(X))

        # X should be a data frame
        for pname in X.columns:
            X[pname] = np.minimum(self.x_max[pname], np.maximum(self.x_min[pname], X[pname]))

        return X

    def set_results_for_iteration(self, iteration, results):
        results = results.total.tolist()
        logger.info('%s: Choosing samples at iteration %d:', self.__class__.__name__, iteration)
        logger.debug('Results:\n%s', results)

        data_by_iter = self.data.set_index('Iteration')
        if iteration + 1 in data_by_iter.index.unique():
            # Been here before, reset
            data_by_iter = data_by_iter.loc[:iteration]

            state_by_iter = self.state.set_index('Iteration')
            self.state = state_by_iter.loc[:iteration].reset_index()

        # Store results ... even if changed
        data_by_iter.loc[iteration, 'Results'] = results
        self.data = data_by_iter.reset_index()

    def choose_initial_samples(self):
        self.data = pd.DataFrame(columns=[['Iteration', '__sample_index__', 'Results'] + self.get_param_names()])
        self.data['Iteration'] = self.data['Iteration'].astype(int)
        self.data['__sample_index__'] = self.data['__sample_index__'].astype(int)

        self.n_dimensions = len(self.params)
        size_of_dynamic_params = sum(self.Dynamic.values())
        iteration = 0

        # Clear self.state in case of resuming iteration 0 from commission
        self.state = pd.DataFrame(columns=['Iteration', 'Parameter', 'Center', 'Hessian', 'Min', 'Max', 'Dynamic'])
        self.state['Iteration'] = self.state['Iteration'].astype(int)

        # dummy_counter = -1
        for param in self.params:
            hessian_dict = {p['Name']: p['aprioriHessian'] for p in self.params}
            # if (param['Dynamic'] is True):
            #     dummy_counter += 1
            print(iteration, param['Name'], param['Guess'], param['Min'], param['Max'], param['Dynamic'])
            self.state.loc[len(self.state)] = [iteration, param['Name'], param['Guess'], hessian_dict,
                                               param['Min'], param['Max'], param['Dynamic']]
            # self.state.loc[len(self.state)] = [iteration, param['Name'], param['Guess'], param['aprioriHessian']*np.eye(1,size_of_dynamic_params,dummy_counter),
            #                                    param['Min'], param['Max'], param['Dynamic']]
            print(self.state)

        initial_samples = self.choose_and_clamp_samples_for_iteration(iteration)

        self.add_samples(initial_samples, iteration)

        return initial_samples

    def stochastic_newton_raphson(self, iteration):

        assert (iteration >= 1)

        def proj_spd(A):
            # NOTE: the input matrix is assumed to be symmetric
            d, v = np.linalg.eigh(A)
            A = v * np.diag(np.maximum(abs(d), 1e-5)) * (v.T)  # (v * np.maximum(abs(d), 1e-5)).dot(v.T)
            A = (A + A.T) / 2
            return (A)

        def proj_nd(A):
            # NOTE: the input matrix is assumed to be symmetric
            d, v = np.linalg.eigh(A)
            A = v * np.diag(np.minimum(-abs(d), -1e-5)) * (v.T)  # (v * np.maximum(abs(d), 1e-5)).dot(v.T)
            A = (A + A.T) / 2
            return (A)

        # DYNAMIC ON PREVIOUS ITERATION WHEN COMMISSIONED ...
        state_prev_iter = self.state.set_index('Iteration').loc[iteration - 1]
        dynamic_params = [r['Parameter'] for idx, r in state_prev_iter.iterrows() if r['Dynamic']]

        self.data.set_index('Iteration', inplace=True)
        latest_dynamic_samples = self.data.loc[iteration - 1, dynamic_params].values
        latest_results = self.data.loc[iteration - 1, 'Results'].values

        x_min = np.asarray([self.x_min[pname] for pname in dynamic_params])
        x_max = np.asarray([self.x_max[pname] for pname in dynamic_params])

        x_current = latest_dynamic_samples[0]
        x_current_scaled = (x_current - x_min) / (x_max - x_min)

        # H_sign = -1 # Hessian should be neg. semi definite (maximization)
        p = x_current.size
        M = self.comps_per_iteration
        hessian_dynamic = [r['Hessian'] for idx, r in state_prev_iter.iterrows() if r['Dynamic']]
        h_current_list = []  # np.asmatrix(np.concatenate(Hessian_elements))
        for i in range(len(dynamic_params)):
            h_current_list.append([p for idx, p in hessian_dynamic[i].items() if idx in dynamic_params])
        h_current_est = np.asmatrix(np.array(h_current_list))

        largest_step_size = np.abs(np.array([1] * p) - np.array([0] * p)) / 5

        # optimization parameters
        a0, step = 2, .85
        a0 = step * (1 + a0) ** (0.602)
        a = a0 * (iteration + 1 + a0) ** (-0.602)
        # TODO: assumed here that there is no prior Hessian information 
        w = .8 * (iteration + 1) ** (-.501) if iteration > 1 else 1

        g_avg = np.zeros(shape=(p, M))
        s_avg = np.zeros(shape=(p, p, M))

        for k in range(M):
            np.random.seed()

            theta_plus = (np.array(latest_dynamic_samples[4 * k + 1]) - x_min) / (x_max - x_min)
            theta_minus = (np.array(latest_dynamic_samples[4 * k + 2]) - x_min) / (x_max - x_min)
            f_plus = latest_results[4 * k + 1]
            f_minus = latest_results[4 * k + 2]

            gk = (f_plus - f_minus) / (theta_plus - theta_minus)
            g_avg[:, k] = k / (k + 1) * g_avg[:, k - 1] + 1 / (k + 1) * gk.T

            theta_plus_plus = (np.array(latest_dynamic_samples[4 * k + 3]) - x_min) / (x_max - x_min)
            theta_minus_plus = (np.array(latest_dynamic_samples[4 * k + 4]) - x_min) / (x_max - x_min)
            f_plus_plus = latest_results[4 * k + 3]
            f_minus_plus = latest_results[4 * k + 4]

            g_p = (f_plus_plus - f_plus) / (theta_plus_plus - theta_plus)
            g_m = (f_minus_plus - f_minus) / (theta_plus_plus - theta_plus)

            sk = np.dot((1 / (theta_plus - theta_minus))[:, None], (g_p - g_m)[None, :])
            s_avg[:, :, k] = k / (k + 1) * s_avg[:, :, k - 1] + 1 / (k + 1) * sk

        g = g_avg[:, M - 1]
        h_hat = .5 * (s_avg[:, :, M - 1] + s_avg[:, :, M - 1].T)
        h_bar = (1 - w) * h_current_est + w * h_hat
        h_2bar = proj_nd(h_bar)  # H_bar#.5*(H_bar - sqrtm(np.linalg.matrix_power(H_bar,2)+1e-6*np.eye(p)))
        h_2bar_inv = np.linalg.inv(h_2bar)

        # update x
        update = np.array(h_2bar_inv.dot(g)).flatten()

        if (np.abs(update) > largest_step_size).any():
            update = np.linalg.norm(largest_step_size) * update / np.linalg.norm(update)

        x_next_scaled = x_current_scaled - a * update  # x_{n+1} = x_n - a_n H_n^{-1} G_n
        x_next = x_next_scaled * (x_max - x_min) + x_min
        hessian_next = h_bar

        self.data.reset_index(inplace=True)

        old_center = self._get_X_center(iteration - 1)
        old_center_of_dynamic_params = old_center[dynamic_params].values
        new_dynamic_center = x_next.tolist()

        # max_idx = np.argmax(latest_results)
        # if np.max(latest_results) >
        # 'Stepping to argmax of %f at:' % latest_results[max_idx], latest_dynamic_samples[max_idx]
        # new_dynamic_center = latest_dynamic_samples[max_idx].tolist()

        new_center_dict = old_center.to_dict()  # {k:v for k,v in zip(self.get_param_names(), old_center)}
        new_center_dict.update({k: v for k, v in zip(dynamic_params, new_dynamic_center)})

        old_hessian = self._get_Hessian(iteration - 1)
        old_dynamic_hessian = [old_hessian[p] for p in dynamic_params]

        old_hessian_of_dynamic_params = old_hessian[dynamic_params].values
        new_list_dynamic_hessian = hessian_next.tolist()
        new_list_dynamic_hessian.append(dynamic_params)
        keys = new_list_dynamic_hessian[-1]

        new_dynamic_hessian = old_dynamic_hessian
        for i in range(len(dynamic_params)):
            new_dynamic_hessian[i].update({k: v for k, v in zip(dynamic_params, new_list_dynamic_hessian[i])})

        new_hessian_dict = old_hessian.to_dict()
        new_hessian_dict.update({k: v for k, v in zip(dynamic_params, new_dynamic_hessian)})

        # User may have added or removed params
        param_names = [p['Name'] for p in self.params]
        # Remove -
        new_center_df = {k: v for k, v in new_center_dict.items() if k in param_names}
        new_hessian_df = {k: v for k, v in new_hessian_dict.items() if k in param_names}
        # Add -
        new_params = {p['Name']: p['Guess'] for p in self.params if p['Name'] not in new_center_dict}
        new_center_dict.update(new_params)
        new_hessian_dict.update(new_params)

        # CLAMP
        new_center_df = pd.Series(new_center_dict, name=0).to_frame().transpose()
        new_hessian_df = pd.Series(new_hessian_dict, name=0).to_frame().transpose()
        new_center_df = self.clamp(new_center_df)

        # USER CONSTRAINT FN
        new_center_df = new_center_df.apply(self.constrain_sample_fn, axis=1)

        new_state = pd.DataFrame({
            'Iteration': [iteration] * self.n_dimensions,
            'Parameter': new_center_df.columns.values,
            'Center': new_center_df.as_matrix()[0],
            'Hessian': new_hessian_df.as_matrix()[0],
            'Min': [self.x_min[pname] for pname in new_center_df.columns.values],
            'Max': [self.x_max[pname] for pname in new_center_df.columns.values],
            'Dynamic': [self.Dynamic[pname] for pname in new_center_df.columns.values]
        })

        self.state = self.state.query('Iteration < @iteration')
        self.state = pd.concat([self.state, new_state], ignore_index=True)

        samples = self.choose_and_clamp_samples_for_iteration(iteration)
        self.add_samples(samples, iteration)

        return samples

    def choose_and_clamp_samples_for_iteration(self, iteration):
        m = self.comps_per_iteration
        state_by_iter = self.state.set_index('Iteration')
        # Will vary parameters that are 'Dyanmic' on this iteration
        samples = self.sample_simultaneous_perturbation(m, iteration, state_by_iter.loc[iteration])

        # Clamp and constrain
        samples = self.clamp(samples)
        samples = samples.apply(self.constrain_sample_fn, axis=1)

        return samples  # Order shouldn't matter now, so dropped [self.get_param_names()]

    def sample_simultaneous_perturbation(self, M, iteration, state, resolution=None):
        # Pick samples x+c\Delta, x-c\Delta, x+c\Delta+c_tilde\Delta_tilde, x-c\Delta+c_tilde\Delta_tilde

        assert (M > 0)

        dynamic_state = state.query('Dynamic == True')
        dynamic_state_by_param = dynamic_state.set_index('Parameter')

        x_min = np.array([dynamic_state_by_param.loc[pname, 'Min'] for pname in dynamic_state['Parameter']])
        x_max = np.array([dynamic_state_by_param.loc[pname, 'Max'] for pname in dynamic_state['Parameter']])
        x_current = np.array([dynamic_state_by_param.loc[pname, 'Center'] for pname in dynamic_state['Parameter']])

        c0 = .02 * (x_max - x_min) / M ** 0.5
        c = c0 * (iteration + 1) ** (-0.101)

        if resolution is None:
            resolution = 0.5 * c0

        # making sure all plus/minus points in range
        too_big = (x_current + c) > x_max
        too_small = (x_current - c) < x_min
        c[too_big] = np.maximum(x_max[too_big] - x_current[too_big], resolution[too_big])
        c[too_small] = np.maximum(x_current[too_small] - x_min[too_small], resolution[too_small])

        deviations = []

        for k in range(M):
            np.random.seed()

            delta = np.round(np.random.uniform(0, 1, len(c0))) * 2 - 1
            theta_plus = x_current + (c * delta)
            theta_minus = x_current - (c * delta)

            if (x_min > theta_plus).any() or (theta_plus > x_max).any():
                theta_plus = x_current

            if (theta_minus < x_min).any() or (theta_minus > x_max).any():
                theta_minus = x_current

            deviations.append((c * delta).tolist())
            deviations.append((-c * delta).tolist())

            delta_tilde = np.round(np.random.uniform(0, 1, len(c0))) * 2 - 1
            c_tilde = np.random.uniform(low=1, high=2) * c
            theta_plus_plus = theta_plus + c_tilde * delta_tilde
            theta_minus_plus = theta_minus + c_tilde * delta_tilde

            while (theta_plus_plus < x_min).any() or (theta_plus_plus > x_max).any() or (theta_minus_plus < x_min).any() or (
                    theta_minus_plus > x_max).any():
                delta_tilde = np.round(np.random.uniform(0, 1, len(c0))) * 2 - 1
                c_tilde = np.random.uniform(low=1, high=2) * c
                theta_plus_plus = theta_plus + c_tilde * delta_tilde
                theta_minus_plus = theta_minus + c_tilde * delta_tilde

            deviations.append((c * delta + c_tilde * delta_tilde).tolist())
            deviations.append((-c * delta + c_tilde * delta_tilde).tolist())

        X_center = state.reset_index(drop=True).set_index(['Parameter'])[['Center']]
        xc = X_center.transpose().reset_index(drop=True)
        xc.columns.name = ""

        samples = pd.concat([xc] * (4 * M + 1)).reset_index(drop=True)
        # print(samples)

        dt = np.transpose(deviations)

        dynamic_state_by_param = dynamic_state.set_index('Parameter')
        for i, pname in enumerate(dynamic_state['Parameter']):
            Xcen = dynamic_state_by_param.loc[pname, 'Center']
            samples.loc[1:(4 * M + 1), pname] = Xcen + dt[i]

        return samples

    def end_condition(self):
        print("end_condition")
        # Stopping Criterion: good rsqared with small norm?
        # Return True to stop, False to continue
        logger.info('Continuing iterations ...')
        return False

    def get_final_samples(self):
        """
        Resample Stage:
        """
        print("get_final_samples")
        state_by_iteration = self.state.set_index('Iteration')
        last_iter = sorted(state_by_iteration.index.unique())[-1]

        X_Center = self._get_X_center(last_iter)
        xc = X_Center.to_frame().transpose().reset_index(drop=True)
        xc.columns.name = ""

        dtypes = {name: str(data.dtype) for name, data in xc.iteritems()}
        final_samples_NaN_to_Null = xc.where(~xc.isnull(), other=None)
        return {'final_samples': final_samples_NaN_to_Null.to_dict(orient='list'), 'final_samples_dtypes': dtypes}

    def prep_for_dict(self, df):
        # Needed for Windows compatibility
        # nulls = df.isnull()
        # if nulls.values.any():
        #    df[nulls] = None
        # return df.to_dict(orient='list')

        return df.where(~df.isnull(), other=None).to_dict(orient='list')

    def get_state(self):
        optimtool_state = dict(
            n_dimensions=self.n_dimensions,
            params=self.params,
            comps_per_iteration=self.comps_per_iteration,

            data=self.prep_for_dict(self.data),
            data_dtypes={name: str(data.dtype) for name, data in self.data.iteritems()},

            state=self.prep_for_dict(self.state),
            state_dtypes={name: str(data.dtype) for name, data in self.state.iteritems()}
        )
        return optimtool_state

    def set_state(self, state, iteration):
        self.n_dimensions = state['n_dimensions']
        self.params = state['params']  # NOTE: This line will override any updated user params passed to __init__
        self.comps_per_iteration = state['comps_per_iteration']

        data_dtypes = state['data_dtypes']
        self.data = pd.DataFrame.from_dict(state['data'], orient='columns')
        for c in self.data.columns:  # Argh
            self.data[c] = self.data[c].astype(data_dtypes[c])

        state_dtypes = state['state_dtypes']
        self.state = pd.DataFrame.from_dict(state['state'], orient='columns')
        for c in self.state.columns:  # Argh
            self.state[c] = self.state[c].astype(state_dtypes[c])

        self.need_resolve = True

    def get_param_names(self):
        return [p['Name'] for p in self.params]
