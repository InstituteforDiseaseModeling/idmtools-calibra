import os
import pandas as pd
import sys

from idmtools_calibra.calib_site import CalibSite

sys.path.append(os.getcwd())
from rmse_analyzer import RMSEAnalyzer


# The main task of a site object in calibra is to identify reference data sources, load them, and determine what
# analyzers will be used for scoring our calibration simulations.
class SolarSite(CalibSite):
    def __init__(self, name, reference_sources):
        self.reference_dict = {}
        for channel, file_path in reference_sources.items():
            self.reference_dict[channel] = pd.read_csv(file_path)
        super().__init__(name=name)

    def get_reference_data(self, reference_type):
        return self.reference_dict[reference_type]

    def get_analyzers(self):
        return [RMSEAnalyzer(site=self, dependent_column='production', independent_column='date')]

    def get_setup_functions(self):
        return super().get_setup_functions()
