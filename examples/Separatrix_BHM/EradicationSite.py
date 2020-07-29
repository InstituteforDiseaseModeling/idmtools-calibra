import importlib
import os
import pandas as pd
import logging
from calibtool.CalibSite import CalibSite
from EradicationAnalyzer import EradicationAnalyzer

logger = logging.getLogger(__name__)

class EradicationSite(CalibSite):
    metadata = { }

    def __init__(self, **kwargs):
        self.analyzers = [EradicationAnalyzer()]
        # Must come at the end:
        super(EradicationSite, self).__init__('EradicationSite')

    def get_setup_functions(self):
        return [ ]

    def get_analyzers(self):
        return self.analyzers

    def get_reference_data(self, reference_type):
        return None
