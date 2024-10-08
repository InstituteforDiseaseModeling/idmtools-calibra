import pandas as pd

from idmtools_calibra.calib_site import CalibSite
from idmtools_calibra.analyzers.rmse_analyzer import RMSEAnalyzer

# The main task of a site object in calibra is to identify reference data sources, load them, and determine what
# analyzers will be used for scoring our calibration simulations.


class RMSESiteSingleChannel(CalibSite):
    def __init__(self, name, reference_sources={'just_one': 'reference/output.csv'}):
        one_key = list(reference_sources.keys())[0]
        self.reference = pd.read_csv(reference_sources[one_key])
        self.ind_col = self.reference.columns[0]
        self.dep_col = self.reference.columns[1]
        super().__init__(name=name)

    def get_reference_data(self, reference_type=None):
        return self.reference

    def get_analyzers(self):
        return [
            RMSEAnalyzer(
                site=self,
                dependent_column=self.dep_col,
                independent_column=self.ind_col,
            )
        ]

    def get_setup_functions(self):
        return super().get_setup_functions()
