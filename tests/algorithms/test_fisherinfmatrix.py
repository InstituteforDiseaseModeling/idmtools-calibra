import unittest
import numpy as np
import pandas as pd
import matplotlib as plt
import pytest
from matplotlib.patches import Ellipse

from idmtools_calibra.algorithms.fisher_inf_matrix import compute_fisher_inf_matrix, trunc_gauss


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

@pytest.mark.skip("missing data")
class TestStuff(unittest.TestCase):
    def test_a(self):
        center_point = np.array([0.08, -0.92, .92])
        low_bound = np.array([-1] * 3)
        up_bound = np.array([1] * 2 + [1])
        # df_perturbed_points = perturbed_points(center_point, low_bound, up_bound)
        # print df_perturbed_points
        # df_perturbed_points.to_csv("data2.csv")
        # df_perturbed_points = pd.DataFrame.from_csv("data.csv")
        ll = pd.DataFrame.from_csv("LLdata.csv")
        fisher = compute_fisher_inf_matrix(center_point, ll)
        covariance = np.linalg.inv(fisher)

        print("eigs of fisher: ", np.linalg.eigvals(fisher))
        print("eigs of Covariance: ", np.linalg.eigvals(covariance))

        plt.figure('CramerRao')
        plt.subplot(111)
        x, y = center_point[0:2]
        plt.plot(x, y, 'g.')
        plot_cov_ellipse(covariance[0:2, 0:2], center_point[0:2], nstd=3, alpha=0.6, color='green')
        sample_x, sample_y, sample_z = trunc_gauss(center_point, covariance, low_bound, up_bound, 10).T
        # sample_x, sample_y = np.random.multivariate_normal(center_point[0:2], Covariance[0:2,0:2], 10).T
        print('covariance:\n%s' % covariance)
        print('sample_x:\n%s' % sample_x)
        print('sample_y:\n%s' % sample_y)
        print('sample_z:\n%s' % sample_z)

        plt.plot(sample_x, sample_y, 'x')
        plt.xlim(low_bound[0], up_bound[0])
        plt.ylim(low_bound[1], up_bound[1])
        plt.xlabel('X', fontsize=14)
        plt.ylabel('Y', fontsize=14)

        plt.show()
