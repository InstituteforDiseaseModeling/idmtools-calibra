from dataclasses import dataclass, field

from emodpy.reporters.base import CustomReporter


@dataclass
class Report_TBHIV_ByAge(CustomReporter):
    name: str = field(default="Report_TBHIV_ByAge")
    dll_file: str = field(default="lib_customreport_TBHIV_ReportByAge.dll")

    def add_report(self, max_age_yrs, min_age_yrs, start_year, stop_year):
        self._add_report({
            "Max_Age_Yrs": max_age_yrs,
            "Min_Age_Yrs": min_age_yrs,
            "Start_Year": start_year,
            "Stop_Year": stop_year
        })


@dataclass
class ReportPluginAgeAtInfectionHistogram(CustomReporter):
    name: str = field(default="ReportPluginAgeAtInfectionHistogram")
    dll_file: str = field(default="libReportAgeAtInfectionHistogram_plugin.dll")
    Reports: list = field(default_factory=lambda: [{}])
    age_bins: list = field(default_factory=list)
    interval_years: int = field(default_factory=int)


@dataclass
class ReportHumanMigrationTracking(CustomReporter):
    name: str = field(default="ReportHumanMigrationTracking")
    dll_file: str = field(default="libhumanmigrationtracking.dll")
    Reports: list = field(default_factory=lambda: [{}])


@dataclass
class ReportNodeDemographics(CustomReporter):
    name: str = field(default="ReportNodeDemographics")
    age_bins: list = field(default_factory=list)
    dll_file: str = field(default="libReportNodeDemographics.dll")

    def from_dict(self, data):
        self.age_bins = [r["Age_Bins"] for r in data["Reports"]]

    def add_report(self, age_bins):
        self.age_bins.append(age_bins)

    def to_dict(self):
        self.Reports = [{
            "Age_Bins": ab
        } for ab in self.age_bins]
        return super().to_dict()


@dataclass
class MalariaSummaryReport(CustomReporter):
    name: str = field(default="MalariaSummaryReport")
    dll_file: str = "libmalariasummary_report_plugin.dll"

    def add_report(self, age_bins=None, duration_days=365, event_trigger_list=None, individual_property_filter="",
                   infectiousness_bins=None, max_number_reports=10000, parasitemia_bins=None, report_description="",
                   reporting_interval=30, start_day=0):
        if infectiousness_bins is None:
            infectiousness_bins = []
        if parasitemia_bins is None:
            parasitemia_bins = []
        if event_trigger_list is None:
            event_trigger_list = []
        if age_bins is None:
            age_bins = []
        self._add_report({
            "Age_Bins": age_bins,
            "Duration_Days": duration_days,
            "Event_Trigger_List": event_trigger_list,
            "Individual_Property_Filter": individual_property_filter,
            "Infectiousness_Bins": infectiousness_bins,
            "Max_Number_Reports": max_number_reports,
            "Parasitemia_Bins": parasitemia_bins,
            "Report_Description": report_description,
            "Reporting_Interval": reporting_interval,
            "Start_Day": start_day
        })


@dataclass
class ReportEventCounter(CustomReporter):
    name: str = field(default="ReportEventCounter")
    dll_file: str = field(default="libreporteventcounter.dll")

    def add_report(self, duration_days=10000, event_trigger_list=None, nodeset_config=None,
                   report_description="", start_day=0):
        if nodeset_config is None:
            nodeset_config = {"class": "NodeSetAll"}
        if event_trigger_list is None:
            event_trigger_list = []
        self._add_report({
            "Duration_Days": duration_days,
            "Event_Trigger_List": event_trigger_list,
            "Nodeset_Config": nodeset_config,
            "Report_Description": report_description,
            "Start_Day": start_day
        })


@dataclass
class ReportMalariaFiltered(CustomReporter):
    name: str = field(default="ReportMalariaFiltered")
    dll_file: str = field(default="libReportMalariaFiltered.dll")

    def add_report(self, end_day=0, node_ids_of_interest=None, report_file_name="ReportMalariaFiltered.json",
                   start_day=0):
        if node_ids_of_interest is None:
            node_ids_of_interest = []
        self._add_report({
            "End_Day": end_day,
            "Node_IDs_Of_Interest": node_ids_of_interest,
            "Report_File_Name": report_file_name,
            "Start_Day": start_day
        })


@dataclass
class MalariaImmunityReport(CustomReporter):
    name: str = field(default="MalariaImmunityReport")
    dll_file: str = "libmalariaimmunity_report_plugin.dll"

    def add_report(self, pretty_format=1, age_bins=[], start_day=0, duration_days=10000,
                   nodeset_config={"class": "NodeSetAll"}, event_trigger_list=["EveryUpdate"], max_number_reports=15,
                   report_description="", reporting_interval=15):
        self._add_report({
            "Pretty_Format": pretty_format,
            "Age_Bins": age_bins,
            "Start_Day": start_day,
            "Duration_Days": duration_days,
            "Nodeset_Config": nodeset_config,
            "Event_Trigger_List": event_trigger_list,
            "Max_Number_Reports": max_number_reports,
            "Report_Description": report_description,
            "Reporting_Interval": reporting_interval
        })


@dataclass
class MalariaSurveyJSONAnalyzer(CustomReporter):
    name: str = field(default="MalariaSurveyJSONAnalyzer")
    dll_file: str = "libmalariasurveyJSON_analyzer_plugin.dll"

    def add_report(self, pretty_format=1, start_day=0, duration_days=10000, nodeset_config={"class": "NodeSetAll"},
                   event_trigger_list=["NewClinicalCase"], max_number_reports=15, report_description="Day0",
                   reporting_interval=73):
        self._add_report({
            "Pretty_Format": pretty_format,
            "Start_Day": start_day,
            "Duration_Days": duration_days,
            "Nodeset_Config": nodeset_config,
            "Event_Trigger_List": event_trigger_list,
            "Max_Number_Reports": max_number_reports,
            "Report_Description": report_description,
            "Reporting_Interval": reporting_interval
        })


@dataclass
class MalariaTransmissionReport(CustomReporter):
    name: str = field(default="MalariaTransmissionReport")
    dll_file: str = "libReportMalariaTransmissions.dll"

    def add_report(self, pretty_format=1, start_day=0, duration_days=365, nodeset_config={"class": "NodeSetAll"},
                   event_trigger_list=["NewInfection"], report_description=""):
        self._add_report({
            "Pretty_Format": pretty_format,
            "Start_Day": start_day,
            "Duration_Days": duration_days,
            "Nodeset_Config": nodeset_config,
            "Event_Trigger_List": event_trigger_list,
            "Report_Description": report_description
        })
