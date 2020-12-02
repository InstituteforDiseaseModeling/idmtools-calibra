import math

import numpy as np
from scipy.special import gammaln

"""
Functions below compare "ref" and "sim" columns of a pandas.DataFrame

Where some parameters are considered known (eg. knonw variance) this will be specified in ref
"""


def LL_geometric_mean_normal(raw_data, sim_data, known_variance):
    num_obs = len(raw_data)
    LL_unnormalized = (sum([0.5 * ((raw_data[x] - sim_data[x])) ** 2 / known_variance[x] for x in range(num_obs)])) * -1

    return LL_unnormalized / num_obs
