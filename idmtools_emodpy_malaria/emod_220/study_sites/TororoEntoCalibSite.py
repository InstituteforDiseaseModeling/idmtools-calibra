import calendar
import logging
import os

from idmtools_emodpy_malaria.emod_220.study_sites.GarkiEntoCalibSites import GarkiEntoCalibSite
from idmtools_emodpy_malaria.study_sites.entomology_calib_site import EntomologyCalibSite

logger = logging.getLogger(__name__)


class TororoEntoCalibSite(EntomologyCalibSite):

    def __init__(self, spec):
        self.metadata = {
            'village': 'Tororo',
            'months': [calendar.month_abbr[i] for i in range(1, 13)],
            'species': [spec]
        }

        super(GarkiEntoCalibSite, self).__init__('Tororo')

    def get_reference_data(self, reference_type):
        super(GarkiEntoCalibSite, self).get_reference_data(reference_type)

        # Load the Parasitology CSV
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reference_csv = os.path.join(dir_path, 'inputs', 'Uganda', 'rough_entomology_Tororo_by_month.csv')
        reference_data = uganda_ento_data(reference_csv, self.metadata)

        return reference_data
