import sys
from idmtools_calibra.utilities.reports.custom_report import BaseReport, BaseEventReport, BaseEventReportIntervalOutput, \
    BaseMalariaTransmissionReport


class MalariaReport(BaseEventReportIntervalOutput):
    dlls = {}

    def __init__(self,
                 event_trigger_list,
                 start_day=0,
                 duration_days=1000000,
                 report_description="",
                 nodeset_config=None,
                 age_bins=None,
                 parasitemia_bins=None,
                 infection_bins=None,
                 max_number_reports=15,
                 reporting_interval=73,
                 ipfilter="",
                 type=""):
        BaseEventReportIntervalOutput.__init__(self, event_trigger_list, start_day, duration_days,
                                               report_description, nodeset_config, max_number_reports,
                                               reporting_interval, type)
        if not age_bins:
            age_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 125]
        self.age_bins = age_bins
        if not parasitemia_bins:
            parasitemia_bins = []
        self.parasitemia_bins = parasitemia_bins
        if not infection_bins:
            infection_bins = []
        self.infection_bins = infection_bins
        self.ipfilter = ipfilter
        if not nodeset_config:
            nodeset_config = {"class": "NodeSetAll"}
        self.nodeset_config = nodeset_config

    def to_dict(self):
        d = super(MalariaReport, self).to_dict()
        d["Age_Bins"] = self.age_bins
        d["Parasitemia_Bins"] = self.parasitemia_bins
        d["Infectiousness_Bins"] = self.infection_bins
        d["Individual_Property_Filter"] = self.ipfilter
        return d


def add_summary_report(simulation, start=0, interval=365, nreports=10000,
                       description='AnnualAverage',
                       duration_days=100000,
                       age_bins=None,
                       parasitemia_bins=None,
                       infection_bins=None,
                       nodes=None,
                       ipfilter=""):
    if not age_bins:
        age_bins = [1.0 / 12, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                    11, 12, 13, 14, 15, 20, 25, 30, 40, 50, 60, 125]
    if not parasitemia_bins:
        parasitemia_bins = [50.0, 500.0, 5000.0, sys.maxsize]
    if not infection_bins:
        infection_bins = [20.0, 40.0, 60.0, 80.0, 100.0]
    if not nodes:
        nodes = {"class": "NodeSetAll"}

    from emodpy.reporters.builtin import MalariaSummaryReport
    summary_report = MalariaSummaryReport()
    summary_report.parameters = {
        "Age_Bins": age_bins,
        "Duration_Days": duration_days,
        "Event_Trigger_List": ['EveryUpdate'],
        "Individual_Property_Filter": ipfilter,
        "Infectiousness_Bins": infection_bins,
        "Max_Number_Reports": nreports,
        "Parasitemia_Bins": parasitemia_bins,
        "Report_Description": description,
        "Reporting_Interval": interval,
        "nodeset_config": nodes,
        "Start_Day": start
    }

    simulation.task.reporters.add_reporter(summary_report)


def add_immunity_report(simulation, start=0, interval=365, nreports=10000,
                        description='AnnualAverage',
                        parasitemia_bins=None,
                        age_bins=None):
    if not age_bins:
        age_bins = [1.0 / 12, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                    11, 12, 13, 14, 15, 20, 25, 30, 40, 50, 60, 125]
    if not parasitemia_bins:
        parasitemia_bins = [50.0, 500.0, 5000.0, sys.maxsize]

    immunity_report = MalariaReport(event_trigger_list=['EveryUpdate'],
                                    start_day=start,
                                    report_description=description,
                                    age_bins=age_bins,
                                    parasitemia_bins=parasitemia_bins,
                                    max_number_reports=nreports,
                                    reporting_interval=interval)
    immunity_report.type = "MalariaImmunityReport"
    simulation.task.reporters.add_report(immunity_report)


def add_survey_report(simulation, survey_days, reporting_interval=21,
                      trigger=None, nreports=1,
                      nodes=None, description=''):
    if not trigger:
        trigger = ["EveryUpdate"]
    if not nodes:
        nodes = {"class": "NodeSetAll"}

    survey_reports = [BaseEventReportIntervalOutput(
        event_trigger_list=trigger,
        start_day=survey_day,
        max_number_reports=nreports,
        reporting_interval=reporting_interval,
        report_description='%sDay_%d' % (description, survey_day),
        type="MalariaSurveyJSONAnalyzer",
        nodeset_config=nodes) for survey_day in survey_days]
    simulation.task.reporters.add_reports(*survey_reports)


def add_patient_report(simulation):
    simulation.task.reporters.add_report(BaseReport(type="MalariaPatientJSONReport"))


def add_habitat_report(simulation):
    simulation.task.reporter.add_reports(BaseReport(type="VectorHabitatReport"))


class FilteredMalariaReport(BaseReport):
    def __init__(self,
                 start_day=0,
                 end_day=1000000,
                 nodes=None,
                 description='',
                 type="ReportMalariaFiltered"):
        if not nodes:
            nodes = []
        BaseReport.__init__(self, type=type)
        self.start_day = start_day
        self.end_day = end_day
        self.nodes = list(nodes)
        self.description = description

    def to_dict(self):
        d = super(FilteredMalariaReport, self).to_dict()
        d.update({"Start_Day": self.start_day,
                  "End_Day": self.end_day,
                  "Node_IDs_Of_Interest": self.nodes,
                  "Report_File_Name": 'ReportMalariaFiltered' + self.description + '.json'})
        return d


class FilteredMalariaSpatialReport(BaseReport):
    def __init__(self,
                 channels=None,
                 start_day=0,
                 end_day=1000000,
                 interval=1,
                 nodes=None,
                 description='',
                 type="SpatialReportMalariaFiltered"):
        if not channels:
            channels = ["Population"]
        if not nodes:
            nodes = []
        BaseReport.__init__(self, type)
        self.channels = channels
        self.start_day = start_day
        self.end_day = end_day
        self.interval = interval
        self.nodes = nodes
        self.description = description

    def to_dict(self):
        d = super(FilteredMalariaSpatialReport, self).to_dict()
        d.update({"Start_Day": self.start_day,
                  "End_Day": self.end_day,
                  "Spatial_Output_Channels": self.channels,
                  "Reporting_Interval": self.interval,
                  "Node_IDs_Of_Interest": self.nodes,
                  "Report_File_Name": 'SpatialReportMalariaFiltered' + self.description})
        return d


def add_filtered_report(simulation, start=0, end=10000, nodes=None, description=''):
    if not nodes:
        nodes = []
    filtered_report = FilteredMalariaReport(start_day=start, end_day=end, nodes=nodes,
                                            description=description)
    simulation.task.reporters.add_report(filtered_report)


def add_filtered_spatial_report(simulation, start=0, end=10000, channels=None,
                                interval=1, nodes=None, description=''):
    if not nodes:
        nodes = []
    if not channels:
        channels = ["Population"]
    spatial_report = FilteredMalariaSpatialReport(channels=channels, start_day=start,
                                                  end_day=end, interval=interval,
                                                  nodes=nodes, description=description,
                                                  type="SpatialReportMalariaFiltered")
    simulation.task.reporters.add_report(spatial_report)


def add_malaria_transmission_report(simulation, start=0, duration=10000, description='',
                                    nodes=None):
    malaria_transmission_report = BaseMalariaTransmissionReport(start_day=start,
                                                                duration_days=duration,
                                                                report_description=description,
                                                                nodes=nodes)
    simulation.task.reporters.add_report(malaria_transmission_report)


def add_event_counter_report(simulation, event_trigger_list, start=0, duration=10000, description='',
                             nodes=None):
    if not nodes:
        nodes = {"class": "NodeSetAll"}

    event_counter_report = BaseEventReport(event_trigger_list, start_day=start,
                                           duration_days=duration,
                                           report_description=description,
                                           nodeset_config=nodes,
                                           type='ReportEventCounter')
    simulation.task.reporters.add_reports(event_counter_report)
