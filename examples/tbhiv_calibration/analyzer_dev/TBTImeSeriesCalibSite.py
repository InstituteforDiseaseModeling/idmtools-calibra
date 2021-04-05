import logging
from abc import ABCMeta

# from calibtool.CalibSite import CalibSite
from idmtools_calibra.calib_site import CalibSite
from .TBCalibAnalyzer import TBCalibAnalyzer

logger = logging.getLogger(__name__)


class TBTimeSeriesCalibSite(CalibSite):
    """
    An abstract class that implements the simulation setup for TB time series
    - South Africa Country model
    - Nigeria Country Model
    """

    __metaclass__ = ABCMeta

    metadata = {
    }

    def get_setup_functions(self):
        return []

    def get_reference_data(self, reference_type):
        site_ref_type = 'tb_time_series'

        if reference_type is not site_ref_type:
            raise Exception("%s does not support %s reference_type, only %s.",
                            self.__class__.__name__, reference_type, site_ref_type)

    def get_analyzers(self):
        return [TBCalibAnalyzer(site=self, input_vars=[],
                                local_dir='None', start_year=0, year_range=[1990, 2019],
                                columns=['Incidence', 'DiseaseDeaths'])]
