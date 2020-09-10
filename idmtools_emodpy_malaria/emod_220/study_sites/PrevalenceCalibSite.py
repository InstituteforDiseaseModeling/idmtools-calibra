import logging
from abc import ABCMeta

from idmtools_emodpy_malaria.analyzers.channel_by_age_cohort_analyzer import PrevalenceByAgeCohortAnalyzer
from idmtools_emodpy_malaria.analyzers.helpers import channel_age_json_to_pandas
from idmtools_emodpy_malaria.emod_220.study_sites.site_setup_functions import *
from itertool.calib_site import CalibSite

logger = logging.getLogger(__name__)


class PrevalenceCalibSite(CalibSite):
    """
    An abstract class that implements the simulation setup for prevalence-by-age analyses:
    - Namawala, Tanzania
    - Garki, Nigeria (Rafin Marke, Matsari, Sugungum)
    """

    __metaclass__ = ABCMeta

    reference_dict = {
        "Average Population by Age Bin": [],
        "Age Bin": [],
        "PfPR by Age Bin": []
    }

    def get_setup_functions(self):
        return [
            config_setup_fn(duration=21915),  # 60 years (with leap years)
            summary_report_fn(interval=365),
            site_input_eir_fn(self.name, birth_cohort=True)
        ]

    def get_reference_data(self, reference_type):
        site_ref_type = 'prevalence_by_age'

        if reference_type is not site_ref_type:
            raise Exception("%s does not support %s reference_type, only %s.",
                            self.__class__.__name__, reference_type, site_ref_type)

        reference_data = channel_age_json_to_pandas(self.reference_dict, index_key='Age Bin')

        logger.debug('Reference data:\n  %s', reference_data)
        return reference_data

    def get_analyzers(self):
        return [PrevalenceByAgeCohortAnalyzer(site=self)]
