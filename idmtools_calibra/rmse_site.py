import pandas as pd

from idmtools_calibra.calib_site import CalibSite
from idmtools_calibra.analyzers.rmse_analyzer import RMSEAnalyzer

# The main task of a site object in calibra is to identify reference data sources, load them, and determine what
# analyzers will be used for scoring our calibration simulations.


class RMSESite(CalibSite):
    def __init__(self, name, reference_sources):
        self.reference_dict = {}
        for channel, file_path in reference_sources.items():
            self.reference_dict[channel] = pd.read_csv(file_path)
            self.ind_col = self.reference_dict[channel].columns[0]
            self.dep_col = self.reference_dict[channel].columns[1]
        super().__init__(name=name)

    def get_reference_data(self, reference_type):
        return self.reference_dict[reference_type]

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
