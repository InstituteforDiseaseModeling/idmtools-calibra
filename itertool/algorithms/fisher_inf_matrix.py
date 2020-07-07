from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy.linalg import sqrtm

DEFAULT_PERTURBATION_AND_RESOLUTION = 0.01


def perturbed_points(center, Xmin, Xmax, M=10, N=5, n=1, resolution_raw=None):
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
        Xmin: minimum of parameters    1xp nparray
        Xmax: maximum of parameters    1xp nparray
        M: number of Hessian estimates    scalar-positive integer
        N: number of pseudodata vectors    scalar-positive integer
        n: sample size    scalar-positive integer
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
        resolution = resolution_raw / (Xmax - Xmin)

    # 0-1 scaled center point for perturbing, per parameter
    X_scaled = (center - Xmin) / (Xmax - Xmin)

    # initial perturbation size selection
    C = np.maximum(DEFAULT_PERTURBATION_AND_RESOLUTION * np.ones(p), resolution)

    # ensure that no perturbation exceeds 0/1 relative to the scaled center point
    too_big = (X_scaled + C) > 1
    too_small = (X_scaled - C) < 0
    C[too_big] = np.minimum(1 - X_scaled[too_big], resolution[too_big])
    C[too_small] = np.minimum(X_scaled[too_small], resolution[too_small])

    X_perturbed = np.zeros(shape=(4*M*N*n, 4+p))
    X_perturbed[:, 0] = np.tile(range(4), N * n * M).astype(int)
    X_perturbed[:, 1] = np.repeat(range(N),4 * n * M)
    X_perturbed[:, 2] = np.tile(np.repeat(range(M), 4 * n), N)

    counter = 0
    for j in range(N):
        run_numbers = np.random.randint(1,101,n)
        X_perturbed[(j*(4*n*M)):((j+1)*(4*n*M)), 3] = np.tile(np.repeat(run_numbers, 4), M)

        for k in range(M):

            np.random.seed()

            # perturbation vectors
            Delta = np.random.choice([-1, 1], size=(1,p))
            thetaPlus = X_scaled + (C * Delta)
            thetaMinus = X_scaled - (C * Delta)

            if (0 > thetaPlus).any() or (thetaPlus > 1).any():
                thetaPlus = X_scaled

            if (thetaMinus < 0).any() or (thetaMinus > 1).any():
                thetaMinus = X_scaled

            Delta_tilde = np.random.choice([-1, 1], size=(1,p))
            C_tilde = np.random.uniform(low=0.25, high=0.75) * C

            thetaPlusPlus = thetaPlus + C_tilde * Delta_tilde
            thetaPlusMinus = thetaPlus - C_tilde * Delta_tilde
            thetaMinusPlus = thetaMinus + C_tilde * Delta_tilde
            thetaMinusMinus = thetaMinus - C_tilde * Delta_tilde

            while (((0 > thetaPlusPlus).any() or (thetaPlusPlus > 1).any()) and
                       ((thetaPlusMinus < 0).any() or (thetaPlusMinus > 1).any())) or \
                    (((0 > thetaMinusPlus).any() or (thetaMinusPlus > 1).any()) and
                         ((thetaMinusMinus < 0).any() or (thetaMinusMinus > 1).any())):
                Delta_tilde = np.random.choice([-1, 1], size=(1,p))
                C_tilde = np.random.uniform(low=0.25, high=0.5) * C
                thetaPlusPlus = thetaPlus + C_tilde * Delta_tilde
                thetaPlusMinus = thetaPlus - C_tilde * Delta_tilde
                thetaMinusPlus = thetaMinus + C_tilde * Delta_tilde
                thetaMinusMinus = thetaMinus - C_tilde * Delta_tilde

            if ((0 > thetaPlusPlus).any() or (thetaPlusPlus > 1).any()):
                thetaPlusPlus = thetaPlus

            if ((0 > thetaMinusPlus).any() or (thetaMinusPlus > 1).any()):
                thetaMinusPlus = thetaMinus

            if ((0 > thetaPlusMinus).any() or (thetaPlusMinus > 1).any()):
                thetaPlusMinus = thetaPlus

            if ((0 > thetaMinusMinus).any() or (thetaMinusMinus > 1).any()):
                thetaMinusMinus = thetaMinus

            # back to original scale
            thetaPlusPlus_realValue = thetaPlusPlus * (Xmax - Xmin) + Xmin
            thetaPlusMinus_realValue = thetaPlusMinus * (Xmax - Xmin) + Xmin
            thetaMinusPlus_realValue = thetaMinusPlus * (Xmax - Xmin) + Xmin
            thetaMinusMinus_realValue = thetaMinusMinus * (Xmax - Xmin) + Xmin
            X_perturbed[(counter + 0):(counter + 4*n+0):4, 4:] = np.tile(thetaPlusPlus_realValue, (n,1))
            X_perturbed[(counter + 1):(counter + 4*n+1):4, 4:] = np.tile(thetaPlusMinus_realValue, (n,1))
            X_perturbed[(counter + 2):(counter + 4*n+2):4, 4:] = np.tile(thetaMinusPlus_realValue, (n,1))
            X_perturbed[(counter + 3):(counter + 4*n+3):4, 4:] = np.tile(thetaMinusMinus_realValue, (n,1))

            counter += 4*n

    # X_perturbed[:,0:4] = X_perturbed[:,0:4].astype(int)
    # convert to pandas DataFrame
    df_perturbed = pd.DataFrame(data=X_perturbed, columns=(['i(1to4)','j(1toN)','k(1toM)','run_number']+['theta']*p))

    return df_perturbed


def FisherInfMatrix(center_point, df_LL_points, data_columns):
    """
    Compute the Fisher Information matrix using the LL of perturbed points

    Computation of the Fisher information matrix (covariance matrix)
    This step returns a p×p covariance matrix, called Σ.

    Atiye Alaeddini, 12/15/2017

    Args:
        center: center point    (1 x p) nparray
        df_LL_points: Log Likelihood of points    DataFrame



    Returns:
        Fisher: Fisher Information matrix    (p x p) np array
    """

    rounds = df_LL_points['j(1toN)'].as_matrix() # j
    samples_per_round = df_LL_points['k(1toM)'].as_matrix() # k, points[:, 2]
    N = (max(rounds) + 1).astype(int)
    M = (max(samples_per_round) + 1).astype(int)
    n = int((np.shape(rounds)[0])/(4*M*N))

    PlusPlusPoints = df_LL_points.loc[df_LL_points['i(1to4)']==0].filter(data_columns).as_matrix()
    PlusMinusPoints = df_LL_points.loc[df_LL_points['i(1to4)']==1].filter(data_columns).as_matrix()
    MinusPlusPoints = df_LL_points.loc[df_LL_points['i(1to4)']==2].filter(data_columns).as_matrix()
    MinusMinusPoints = df_LL_points.loc[df_LL_points['i(1to4)']==3].filter(data_columns).as_matrix()

    LL_PlusPlusPoints = df_LL_points.loc[df_LL_points['i(1to4)'] == 0, 'LL'].as_matrix()
    LL_PlusMinusPoints = df_LL_points.loc[df_LL_points['i(1to4)'] == 1, 'LL'].as_matrix()
    LL_MinusPlusPoints = df_LL_points.loc[df_LL_points['i(1to4)'] == 2, 'LL'].as_matrix()
    LL_MinusMinusPoints = df_LL_points.loc[df_LL_points['i(1to4)'] == 3, 'LL'].as_matrix()

    # dimension of X
    p = len(center_point)

    # Hessian
    H_bar = np.zeros(shape=(p, p, N))
    H_bar_avg = np.zeros(shape=(p, p, N))

    for i in range(N):
        # reset the data (samples) used for evaluation of the log likelihood
        # initialization
        H_hat = np.zeros(shape=(p, p, M))
        H_hat_avg = np.zeros(shape=(p, p, M))
        G_p = np.zeros(shape=(p, M))
        G_m = np.zeros(shape=(p, M))

        PlusPlus_round_i = PlusPlusPoints[(i * M):((i + 1) * M), :]
        PlusMinus_round_i = PlusMinusPoints[(i * M):((i + 1) * M), :]
        MinusPlus_round_i = MinusPlusPoints[(i * M):((i + 1) * M), :]
        MinusMinus_round_i = MinusMinusPoints[(i * M):((i + 1) * M), :]

        loglPP_round_i = LL_PlusPlusPoints[(i * M):((i + 1) * M)]
        loglPM_round_i = LL_PlusMinusPoints[(i * M):((i + 1) * M)]
        loglMP_round_i = LL_MinusPlusPoints[(i * M):((i + 1) * M)]
        loglMM_round_i = LL_MinusMinusPoints[(i * M):((i + 1) * M)]

        for k in range(M):

            thetaPlusPlus = PlusPlus_round_i[k]
            thetaPlusMinus = PlusMinus_round_i[k]
            thetaMinusPlus = MinusPlus_round_i[k]
            thetaMinusMinus = MinusMinus_round_i[k]

            loglPP = loglPP_round_i[k]
            loglPM = loglPM_round_i[k]
            loglMP = loglMP_round_i[k]
            loglMM = loglMM_round_i[k]

            # if all((thetaPlusPlus - thetaPlusMinus) != 0) and all((thetaMinusPlus - thetaMinusMinus) != 0) and all(
            #         (thetaPlusPlus - thetaMinusPlus) != 0):
            G_p[:, k] = div0((loglPP - loglPM), (thetaPlusPlus - thetaPlusMinus))
            G_m[:, k] = div0((loglMP - loglMM), (thetaMinusPlus - thetaMinusMinus))

            S = np.dot((div0(1, (thetaPlusPlus - thetaMinusPlus)))[:, None], (G_p[:, k] - G_m[:, k])[None, :])  # H_hat
            H_hat[:, :, k] = .5 * (S + S.T)

            H_hat_avg[:, :, k] = k / (k + 1) * H_hat_avg[:, :, k - 1] + 1 / (k + 1) * H_hat[:, :, k]

            # else:
            #     H_hat_avg[:, :, k] = H_hat_avg[:, :, k - 1]

        # H_bar[:, :, i] = .5 * (
        #     H_hat_avg[:, :, M - 1] - sqrtm(np.linalg.matrix_power(H_hat_avg[:, :, M - 1], 2) + 1e-6 * np.eye(p))
        # )
        H_bar[:, :, i] = - np.real(_getAplus(-H_hat_avg[:, :, M - 1]))
        H_bar_avg[:, :, i] = i / (i + 1) * H_bar_avg[:, :, i - 1] + 1 / (i + 1) * H_bar[:, :, i]

    Fisher = -1 * H_bar_avg[:, :, N - 1]
    return Fisher


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
                if (new_sample[param_index] < low_bound[param_index]) or (new_sample[param_index] > high_bound[param_index]):
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
        c = np.true_divide( a, b )
        c[ ~ np.isfinite( c )] = 0  # -inf inf NaN
    return c


def _getAplus(A):
    eigval, eigvec = np.linalg.eigh(A)
    Q = np.matrix(eigvec)
    xdiag = np.matrix(np.diag(np.maximum(eigval, 0)))
    return Q*xdiag*Q.T


def _getPs(A, W=None):
    W05 = np.matrix(W**.5)
    return  W05.I * _getAplus(W05 * A * W05) * W05.I


def _getPu(A, W=None):
    Aret = np.array(A.copy())
    Aret[W > 0] = np.array(W)[W > 0]
    return np.matrix(Aret)


def nearPD(A, nit=10):
    n = A.shape[0]
    W = np.identity(n)
# W is the matrix used for the norm (assumed to be Identity matrix here)
# the algorithm should work for any diagonal W
    deltaS = 0
    Yk = A.copy()
    for k in range(nit):
        Rk = Yk - deltaS
        Xk = _getPs(Rk, W=W)
        deltaS = Xk - Rk
        Yk = _getPu(Xk, W=W)
    return Yk








# def plot_cov_ellipse(cov, pos, nstd=2, ax=None, **kwargs):
#     """
#     Plots an `nstd` sigma error ellipse based on the specified covariance
#     matrix (`cov`). Additional keyword arguments are passed on to the
#     ellipse patch artist.
#
#     Args:
#         cov : The 2x2 covariance matrix to base the ellipse on
#         pos : The location of the center of the ellipse. Expects a 2-element
#             sequence of [x0, y0].
#         nstd : The radius of the ellipse in numbers of standard deviations.
#             Defaults to 2 standard deviations.
#         ax : The axis that the ellipse will be plotted on. Defaults to the
#             current axis.

#     Additional keyword arguments are pass on to the ellipse patch.
#
#     Returns:
#         A matplotlib ellipse artist
#     """
#
#     def eigsorted(cov):
#         vals, vecs = np.linalg.eigh(cov)
#         order = vals.argsort()[::-1]
#         return vals[order], vecs[:, order]
#
#     if ax is None:
#         ax = plt.gca()
#
#     vals, vecs = eigsorted(cov)
#     theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
#
#     # Width and height are "full" widths, not radius
#     width, height = 2 * nstd * np.sqrt(vals)
#     ellip = Ellipse(xy=pos, width=width, height=height, angle=theta, **kwargs)
#
#     ax.add_artist(ellip)
#     return ellip
#
#
# # test
# def test():
#     center_point = np.array([0.08, -0.92, .92])
#     low_bound = np.array([-1] * 3)
#     up_bound = np.array([1] * 2 + [1])
#     # df_perturbed_points = perturbed_points(center_point, low_bound, up_bound)
#     # print df_perturbed_points
#     # df_perturbed_points.to_csv("data2.csv")
#     df_perturbed_points = pd.DataFrame.from_csv("data.csv")
#     ll = pd.DataFrame.from_csv("LLdata.csv")
#     Fisher = FisherInfMatrix(center_point, ll)
#     Covariance = np.linalg.inv(Fisher)
#
#     print("eigs of fisher: ", np.linalg.eigvals(Fisher))
#     print("eigs of Covariance: ", np.linalg.eigvals(Covariance))
#
#     fig3 = plt.figure('CramerRao')
#     ax = plt.subplot(111)
#     x, y = center_point[0:2]
#     plt.plot(x, y, 'g.')
#     plot_cov_ellipse(Covariance[0:2,0:2], center_point[0:2], nstd=3, alpha=0.6, color='green')
#     sample_x, sample_y, sample_z = trunc_gauss(center_point, Covariance, low_bound, up_bound, 10).T
#     # sample_x, sample_y = np.random.multivariate_normal(center_point[0:2], Covariance[0:2,0:2], 10).T
#     print('covariance:\n%s'%Covariance)
#     print('sample_x:\n%s'%sample_x)
#     print('sample_y:\n%s'%sample_y)
#     print('sample_z:\n%s'%sample_z)
#
#     plt.plot(sample_x, sample_y, 'x')
#     plt.xlim(low_bound[0], up_bound[0])
#     plt.ylim(low_bound[1], up_bound[1])
#     plt.xlabel('X', fontsize=14)
#     plt.ylabel('Y', fontsize=14)
#
#     plt.show()

if __name__ == '__main__':
    test()