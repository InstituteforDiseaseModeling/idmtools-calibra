from __future__ import division
import numpy as np
import pandas as pd

DEFAULT_PERTURBATION_AND_RESOLUTION = 0.01


def perturbed_points(center, xmin, xmax, m=10, n=5, sample_size=1, resolution_raw=None):
    # Atiye Alaeddini, 12/11/2017
    # generate perturbed points around the center
    """
    Having the estimated optimal point (θ*), the next step is generating a set of perturbed
    points (samples). At this step, you can specify the size of perturbation (resolution).
    In case you do not input the perturbation size (resolution_raw=None), the script will
    pick a perturbation using the given range for each parameter (Xmin-Xmax).
    You need to allocate per-realization (M) and cross-realization (N). Note that :math:`M>p^2`,
    where p is the number of parameters (size of θ). The number of cross-realization (N)
    should be set depending on the uncertainty of the model at the given final point (θ*).
    To choose N, you can use Chebyshev's inequality.

    You can allocate number of replicates of the model (n). The log-likelihood at each point
    obtains from n replicates of the model with different run numbers. Then these n
    replicates are used to compute the likelihood at that point. When we have a model with
    high uncertainty, the easiest way to compute the likelihood might be taking average of
    the multiple (n) replicates of the model run to compute the likelihood. Note that the
    algorithm only accepts n=1 now. But the Cramer Rao script has the potential to accept
    higher n, whenever a smoothing technique which requires multiple replicates of the model
    for computing the likelihood be added to the Analyzers.

    Args:
        center: center point    1xp nparray
        xmin: minimum of parameters    1xp nparray
        xmax: maximum of parameters    1xp nparray
        m: number of Hessian estimates    scalar-positive integer
        n: number of pseudodata vectors    scalar-positive integer
        sample_size: sample size    scalar-positive integer
        resolution_raw: minimum meaningful perturbation for each parameter   1xp nparray

    Returns:
        X_perturbed: perturbed points    (4MNn x 4+p) nparray
    """
    # dimension of center point
    p = len(center)

    # set the minimum meaningful perturbation size per parameter if not passed in by the user
    if resolution_raw is None:
        resolution = DEFAULT_PERTURBATION_AND_RESOLUTION * np.ones(p)
    else:
        resolution = resolution_raw / (xmax - xmin)

    # 0-1 scaled center point for perturbing, per parameter
    x_scaled = (center - xmin) / (xmax - xmin)

    # initial perturbation size selection
    c = np.maximum(DEFAULT_PERTURBATION_AND_RESOLUTION * np.ones(p), resolution)

    # ensure that no perturbation exceeds 0/1 relative to the scaled center point
    too_big = (x_scaled + c) > 1
    too_small = (x_scaled - c) < 0
    c[too_big] = np.minimum(1 - x_scaled[too_big], resolution[too_big])
    c[too_small] = np.minimum(x_scaled[too_small], resolution[too_small])

    x_perturbed = np.zeros(shape=(4 * m * n * sample_size, 4 + p))
    x_perturbed[:, 0] = np.tile(range(4), n * sample_size * m).astype(int)
    x_perturbed[:, 1] = np.repeat(range(n), 4 * sample_size * m)
    x_perturbed[:, 2] = np.tile(np.repeat(range(m), 4 * sample_size), n)

    counter = 0
    for j in range(n):
        run_numbers = np.random.randint(1, 101, sample_size)
        x_perturbed[
            (j * (4 * sample_size * m)):
            ((j + 1) * (4 * sample_size * m)), 3
        ] = np.tile(np.repeat(run_numbers, 4), m)

        for k in range(m):

            np.random.seed()

            # perturbation vectors
            delta = np.random.choice([-1, 1], size=(1, p))
            theta_plus = x_scaled + (c * delta)
            theta_minus = x_scaled - (c * delta)

            if (0 > theta_plus).any() or (theta_plus > 1).any():
                theta_plus = x_scaled

            if (theta_minus < 0).any() or (theta_minus > 1).any():
                theta_minus = x_scaled

            delta_tilde = np.random.choice([-1, 1], size=(1, p))
            c_tilde = np.random.uniform(low=0.25, high=0.75) * c

            theta_plus_plus = theta_plus + c_tilde * delta_tilde
            theta_plus_minus = theta_plus - c_tilde * delta_tilde
            theta_minus_plus = theta_minus + c_tilde * delta_tilde
            theta_minus_minus = theta_minus - c_tilde * delta_tilde

            while (((0 > theta_plus_plus).any() or (theta_plus_plus > 1).any()) and  # noqa: W504
                   ((theta_plus_minus < 0).any() or (theta_plus_minus > 1).any())) or \
                    (((0 > theta_minus_plus).any() or (theta_minus_plus > 1).any()) and  # noqa: W504
                     ((theta_minus_minus < 0).any() or (theta_minus_minus > 1).any())):
                delta_tilde = np.random.choice([-1, 1], size=(1, p))
                c_tilde = np.random.uniform(low=0.25, high=0.5) * c
                theta_plus_plus = theta_plus + c_tilde * delta_tilde
                theta_plus_minus = theta_plus - c_tilde * delta_tilde
                theta_minus_plus = theta_minus + c_tilde * delta_tilde
                theta_minus_minus = theta_minus - c_tilde * delta_tilde

            if (0 > theta_plus_plus).any() or (theta_plus_plus > 1).any():
                theta_plus_plus = theta_plus

            if (0 > theta_minus_plus).any() or (theta_minus_plus > 1).any():
                theta_minus_plus = theta_minus

            if (0 > theta_plus_minus).any() or (theta_plus_minus > 1).any():
                theta_plus_minus = theta_plus

            if (0 > theta_minus_minus).any() or (theta_minus_minus > 1).any():
                theta_minus_minus = theta_minus

            # back to original scale
            theta_plus_plus_real_value = theta_plus_plus * (xmax - xmin) + xmin
            theta_plus_minus_real_value = theta_plus_minus * (xmax - xmin) + xmin
            theta_minus_plus_real_value = theta_minus_plus * (xmax - xmin) + xmin
            theta_minus_minus_real_value = theta_minus_minus * (xmax - xmin) + xmin
            x_perturbed[(counter + 0):(counter + 4 * sample_size + 0):4, 4:] = np.tile(theta_plus_plus_real_value,
                                                                                       (sample_size, 1))
            x_perturbed[(counter + 1):(counter + 4 * sample_size + 1):4, 4:] = np.tile(theta_plus_minus_real_value,
                                                                                       (sample_size, 1))
            x_perturbed[(counter + 2):(counter + 4 * sample_size + 2):4, 4:] = np.tile(theta_minus_plus_real_value,
                                                                                       (sample_size, 1))
            x_perturbed[(counter + 3):(counter + 4 * sample_size + 3):4, 4:] = np.tile(theta_minus_minus_real_value,
                                                                                       (sample_size, 1))

            counter += 4 * sample_size

    # X_perturbed[:,0:4] = X_perturbed[:,0:4].astype(int)
    # convert to pandas DataFrame
    df_perturbed = pd.DataFrame(data=x_perturbed,
                                columns=(['i(1to4)', 'j(1toN)', 'k(1toM)', 'run_number'] + ['theta'] * p))

    return df_perturbed


def compute_fisher_inf_matrix(center_point, df_ll_points, data_columns):
    """
    Compute the Fisher Information matrix using the LL of perturbed points

    Computation of the Fisher information matrix (covariance matrix)
    This step returns a p×p covariance matrix, called Σ.

    Atiye Alaeddini, 12/15/2017

    Args:
        center_point: center point    (1 x p) nparray
        df_ll_points: Log Likelihood of points    DataFrame
        data_columns: List of columns to filter points with


    Returns:
        Fisher: Fisher Information matrix    (p x p) np array
    """

    rounds = df_ll_points['j(1toN)'].as_matrix()  # j
    samples_per_round = df_ll_points['k(1toM)'].as_matrix()  # k, points[:, 2]
    rounds = (max(rounds) + 1).astype(int)
    m = (max(samples_per_round) + 1).astype(int)
    # n = int((np.shape(rounds)[0]) / (4 * m * rounds))

    plus_plus_points = df_ll_points.loc[df_ll_points['i(1to4)'] == 0].filter(data_columns).as_matrix()
    plus_minus_points = df_ll_points.loc[df_ll_points['i(1to4)'] == 1].filter(data_columns).as_matrix()
    minus_plus_points = df_ll_points.loc[df_ll_points['i(1to4)'] == 2].filter(data_columns).as_matrix()
    minus_minus_points = df_ll_points.loc[df_ll_points['i(1to4)'] == 3].filter(data_columns).as_matrix()

    ll_plus_plus_points = df_ll_points.loc[df_ll_points['i(1to4)'] == 0, 'LL'].as_matrix()
    ll_plus_minus_points = df_ll_points.loc[df_ll_points['i(1to4)'] == 1, 'LL'].as_matrix()
    ll_minus_plus_points = df_ll_points.loc[df_ll_points['i(1to4)'] == 2, 'LL'].as_matrix()
    ll_minus_minus_points = df_ll_points.loc[df_ll_points['i(1to4)'] == 3, 'LL'].as_matrix()

    # dimension of X
    p = len(center_point)

    # Hessian
    h_bar = np.zeros(shape=(p, p, rounds))
    h_bar_avg = np.zeros(shape=(p, p, rounds))

    for i in range(rounds):
        # reset the data (samples) used for evaluation of the log likelihood
        # initialization
        h_hat = np.zeros(shape=(p, p, m))
        h_hat_avg = np.zeros(shape=(p, p, m))
        g_p = np.zeros(shape=(p, m))
        g_m = np.zeros(shape=(p, m))

        plus_plus_round_i = plus_plus_points[(i * m):((i + 1) * m), :]
        plus_minus_round_i = plus_minus_points[(i * m):((i + 1) * m), :]
        minus_plus_round_i = minus_plus_points[(i * m):((i + 1) * m), :]
        minus_minus_round_i = minus_minus_points[(i * m):((i + 1) * m), :]

        logl_pp_round_i = ll_plus_plus_points[(i * m):((i + 1) * m)]
        logl_pm_round_i = ll_plus_minus_points[(i * m):((i + 1) * m)]
        logl_mp_round_i = ll_minus_plus_points[(i * m):((i + 1) * m)]
        logl_mm_round_i = ll_minus_minus_points[(i * m):((i + 1) * m)]

        for k in range(m):
            theta_plus_plus = plus_plus_round_i[k]
            theta_plus_minus = plus_minus_round_i[k]
            theta_minus_plus = minus_plus_round_i[k]
            theta_minus_minus = minus_minus_round_i[k]

            logl_pp = logl_pp_round_i[k]
            logl_pm = logl_pm_round_i[k]
            logl_mp = logl_mp_round_i[k]
            logl_mm = logl_mm_round_i[k]

            # if all((thetaPlusPlus - thetaPlusMinus) != 0) and all((thetaMinusPlus - thetaMinusMinus) != 0) and all(
            #         (thetaPlusPlus - thetaMinusPlus) != 0):
            g_p[:, k] = div0((logl_pp - logl_pm), (theta_plus_plus - theta_plus_minus))
            g_m[:, k] = div0((logl_mp - logl_mm), (theta_minus_plus - theta_minus_minus))

            s = np.dot((div0(1, (theta_plus_plus - theta_minus_plus)))[:, None],
                       (g_p[:, k] - g_m[:, k])[None, :])  # H_hat
            h_hat[:, :, k] = .5 * (s + s.T)

            h_hat_avg[:, :, k] = k / (k + 1) * h_hat_avg[:, :, k - 1] + 1 / (k + 1) * h_hat[:, :, k]

            # else:
            #     H_hat_avg[:, :, k] = H_hat_avg[:, :, k - 1]

        # H_bar[:, :, i] = .5 * (
        #     H_hat_avg[:, :, M - 1] - sqrtm(np.linalg.matrix_power(H_hat_avg[:, :, M - 1], 2) + 1e-6 * np.eye(p))
        # )
        h_bar[:, :, i] = - np.real(_get_a_plus(-h_hat_avg[:, :, m - 1]))
        h_bar_avg[:, :, i] = i / (i + 1) * h_bar_avg[:, :, i - 1] + 1 / (i + 1) * h_bar[:, :, i]

    fisher = -1 * h_bar_avg[:, :, rounds - 1]
    return fisher


def sample_cov_ellipse(cov, pos, num_of_pts=10):
    """
    Sample 'num_of_pts' points from the specified covariance
    matrix (`cov`).

    Args:
        cov : 2-D array_like, The covariance matrix (inverse of fisher matrix). It must be symmetric and positive-semidefinite for proper sampling.
        pos : 1-D array_like, The location of the center of the ellipse, Mean of the multi variate distribution
        num_of_pts : The number of sample points.

    Returns:
        ndarray of the drawn samples, of shape (num_of_pts,).
    """
    return np.random.multivariate_normal(pos, cov, num_of_pts)


def trunc_gauss(mu, sigma, low_bound, high_bound, num_of_pts, batch_size=100):
    samples = []
    while len(samples) < num_of_pts:
        # generate a new batch of samples
        new_samples = np.random.multivariate_normal(mu, sigma, batch_size)

        # determine which new samples are in-bounds and keep them
        for sample_index in range(len(new_samples)):
            out_of_bounds = False
            new_sample = new_samples[sample_index]
            for param_index in range(len(new_sample)):
                if (new_sample[param_index] < low_bound[param_index]) or (
                        new_sample[param_index] > high_bound[param_index]):
                    out_of_bounds = True
                    break
            if not out_of_bounds:
                samples.append(new_sample)

    # trim off any extra sample points and return as a numpy.ndarray
    samples = np.array(samples)[0:num_of_pts]
    return samples


def div0(a, b):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide(a, b)
        c[~ np.isfinite(c)] = 0  # -inf inf NaN
    return c


def _get_a_plus(a):
    eig_val, eig_vec = np.linalg.eigh(a)
    q = eig_vec
    x_diag = np.diag(np.maximum(eig_val, 0))
    return q * x_diag * q.T


def _get_ps(a, w):
    w05 = w ** .5
    return np.linalg.inv(w05) * _get_a_plus(w05 * a * w05) * np.linalg.inv(w05)


def _get_pu(a, w) -> np.ndarray:
    a_ret = np.array(a.copy())
    a_ret[w > 0] = np.array(w)[w > 0]
    return a_ret


def near_pd(a, nit=10):
    n = a.shape[0]
    # W is the matrix used for the norm (assumed to be Identity matrix here)
    # the algorithm should work for any diagonal W
    w = np.identity(n)
    delta_s = 0
    yk = a.copy()
    for k in range(nit):
        rk = yk - delta_s
        xk = _get_ps(rk, w=w)
        delta_s = xk - rk
        yk = _get_pu(xk, w=w)
    return yk
