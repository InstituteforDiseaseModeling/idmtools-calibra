import calendar
import logging
import os

from idmtools_emodpy_malaria.analyzers.channel_by_season_cohort_analyzer import ChannelBySeasonCohortAnalyzer
from idmtools_emodpy_malaria.analyzers.helpers import garki_ento_data
from idmtools_emodpy_malaria.study_sites.entomology_calib_site import EntomologyCalibSite

logger = logging.getLogger(__name__)


class GarkiEntoCalibSite(EntomologyCalibSite):

    def __init__(self, vname, spec):
        self.metadata = {
            'village': vname.replace('_', ' '),
            'months': [calendar.month_abbr[i] for i in range(1, 13)],
            'species': [spec]
        }

        super(GarkiEntoCalibSite, self).__init__(vname.replace('_', ' '))

    def get_reference_data(self, reference_type):
        super(GarkiEntoCalibSite, self).get_reference_data(reference_type)

        # Load the Parasitology CSV
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reference_csv = os.path.join(dir_path, 'inputs', 'GarkiDB_data', 'GarkiDBentomology_MBR.csv')
        reference_data = garki_ento_data(reference_csv, self.metadata)

        return reference_data

    def get_analyzers(self):
        return [ChannelBySeasonCohortAnalyzer(site=self, seasons=self.metadata['months'])]
