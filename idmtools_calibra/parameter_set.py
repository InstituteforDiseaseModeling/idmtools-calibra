from copy import deepcopy
import numpy as np


class ParameterSet:

    def __init__(self, param_dict, iteration_number=None, run_number=None, sim_id=None, likelihood=None):
        self.param_dict = param_dict
        self.iteration_number = iteration_number
        self.run_number = run_number
        self.sim_id = sim_id
        self.likelihood = likelihood
        self.likelihood_exponentiated = np.exp(likelihood)
        self.parameterization_id = None  # set this to something else if you want to track sets of ParameterSets

    def to_dict(self):
        return_dict = deepcopy(self.param_dict)
        return_dict['iteration_number'] = self.iteration_number
        return_dict['run_number'] = self.run_number
        return_dict['sim_id'] = self.sim_id
        return_dict['likelihood'] = self.likelihood
        if self.parameterization_id is not None:
            return_dict['parameterization_id'] = self.parameterization_id
        return return_dict

    @staticmethod
    def _get_items(items_to_get, source_dict):
        items_dict = {}
        for item in items_to_get:
            value = source_dict.pop(item)
            if not isinstance(value, str) and np.isnan(value):
                value = None
            items_dict[item] = value
        return items_dict

    @classmethod
    def from_dict(cls, source_dict):
        items_to_get = ['iteration_number', 'run_number', 'sim_id', 'likelihood', 'parameterization_id']
        items_dict = cls._get_items(items_to_get, source_dict)
        parameterization_id = items_dict.pop('parameterization_id')
        param_dict = deepcopy(source_dict)

        ps = cls(param_dict=param_dict, **items_dict)
        ps.parameterization_id = parameterization_id

        return ps
