from dtk.utils.reports import BaseReport


class BaseAgeHistReport(BaseReport):
    dlls = {'ReportPluginAgeAtInfectionHistogram': 'libReportAgeAtInfectionHistogram_plugin.dll'}

    def __init__(self,
                 age_bins=range(100),
                 interval_years=1,
                 type=""):
        BaseReport.__init__(self, type)
        self.age_bins = age_bins
        self.interval_years = interval_years

    def to_dict(self):
        d = super().to_dict()
        d.update({'Age_At_Infection_Histogram_Report_Reporting_Interval_In_Years': self.interval_years,
                  'Age_At_Infection_Histogram_Report_Age_Bin_Upper_Edges_In_Years': self.age_bins})
        return d
