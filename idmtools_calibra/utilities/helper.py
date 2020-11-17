import itertools
from logging import getLogger
import pandas as pd
import numpy as np

max_exp_name_len = 255

logger = getLogger(__name__)


def validate_exp_name(exp_name):
    if len(exp_name) > max_exp_name_len:
        print(
            "The experiment name '%s' exceeds the max length %d (%d), please adjust your experiment name. Exiting..." %
            (exp_name, max_exp_name_len, len(exp_name)))
        return False
    else:
        return True

def json_to_pandas(channel_data, bins, channel=None):
    """
    A function to convert nested array channel data from a json file to
    a pandas.Series with the specified MultiIndex binning.
    """

    logger.debug("Converting JSON data from '%s' channel to pandas.Series with %s MultiIndex.", channel, bins.keys())
    bin_tuples = list(itertools.product(*bins.values()))
    multi_index = pd.MultiIndex.from_tuples(bin_tuples, names=bins.keys())

    channel_series = pd.Series(np.array(channel_data).flatten(), index=multi_index, name=channel)
    logger.debug('\n%s', channel_series)
    return channel_series
