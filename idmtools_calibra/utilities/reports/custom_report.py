from emodpy.reporters.base import BuiltInReporter

def format(reports):
    reports_json = {"Use_Defaults": 1, "Reports": []}
    for r in reports:
        reports_json['Reports'].append(r.to_dict())
    return reports_json


class BaseReport(BuiltInReporter):
    dlls = {}

    def __init__(self, report_type=""):
        self.type = report_type

    def to_dict(self):
        try:
            d = dict(Pretty_Format=self.pretty_format)
        except AttributeError:
            d = dict()
        d["class"] = self.type
        return d

    def get_dll_path(self):
        dll = self.dlls.get(self.type, None)
        return 'reporter_plugins', dll


class BaseVectorStatsReport(BaseReport):
    dlls = {}

    def __init__(self, stratify_by_species=1, species_list=None, report_type=""):
        BaseReport.__init__(self, report_type)
        if species_list is None:
            species_list = []
        self.stratify_by_species = stratify_by_species
        self.species_list = species_list

    def to_dict(self):
        d = super(BaseVectorStatsReport, self).to_dict()
        d.update({"Stratify_By_Species": self.stratify_by_species,
                  "Species_List": self.species_list})
        return d


class BaseVectorGeneticsReport(BaseReport):
    dlls = {}

    def __init__(self,
                 species='',
                 gender='VECTOR_FEMALE',
                 include_vector_state_columns=0,
                 specific_genome_combinations_for_stratification=None,
                 allele_combinations_for_stratification=None,
                 stratify_by='',
                 combine_similar_genomes=0,
                 report_type=""):

        BaseReport.__init__(self, report_type)
        self.species = species
        self.gender = gender
        self.include_vector_state_columns = include_vector_state_columns
        if not allele_combinations_for_stratification:
            allele_combinations_for_stratification = []
        self.allele_combinations_for_stratification = allele_combinations_for_stratification
        self.stratify_by = stratify_by
        self.combine_similar_genomes = combine_similar_genomes
        if not specific_genome_combinations_for_stratification:
            specific_genome_combinations_for_stratification = [
                {
                    "Allele_Combination": [
                        ["X", "*"]
                    ]
                }
            ]
        self.specific_genome_combinations_for_stratification = specific_genome_combinations_for_stratification

    def to_dict(self):
        d = super(BaseVectorGeneticsReport, self).to_dict()
        d.update({"Species": self.species,
                  "Gender": self.gender,
                  "Include_Vector_State_Columns": self.include_vector_state_columns,
                  "Stratify_By": self.stratify_by,
                  "Allele_Combinations_For_Stratification": self.allele_combinations_for_stratification,
                  "Combine_Similar_Genomes": self.combine_similar_genomes,
                  "Specific_Genome_Combinations_For_Stratification": self.specific_genome_combinations_for_stratification
                  })
        return d


class BaseDemographicsReport(BaseReport):
    dlls = {}

    def __init__(self, stratify_by_gender=0, age_bins=None, ip_key_to_collect="", report_type=""):

        BaseReport.__init__(self, report_type)
        self.stratify_by_gender = stratify_by_gender
        if not age_bins:
            age_bins = []
        self.age_bins = age_bins
        self.IP_key_to_collect = ip_key_to_collect

    def to_dict(self):
        d = super(BaseDemographicsReport, self).to_dict()
        d.update({"Stratify_By_Gender": self.stratify_by_gender,
                  "Age_Bins": self.age_bins})
        if self.IP_key_to_collect:
            d.update({"IP_Key_To_Collect": self.IP_key_to_collect})
        return d


class BaseEventReport(BaseReport):
    dlls = {}

    def __init__(self, event_trigger_list, start_day=0, duration_days=1000000, report_description="", nodeset_config=None, report_type=""):
        BaseReport.__init__(self, report_type)
        self.start_day = start_day
        self.duration_days = duration_days
        self.report_description = report_description
        if not nodeset_config:
            nodeset_config = {"class": "NodeSetAll"}
        self.nodeset_config = nodeset_config
        self.event_trigger_list = event_trigger_list

    def to_dict(self):
        d = super(BaseEventReport, self).to_dict()
        d.update({"Start_Day": self.start_day,
                  "Duration_Days": self.duration_days,
                  "Report_Description": self.report_description,
                  "Nodeset_Config": self.nodeset_config,
                  "Event_Trigger_List": self.event_trigger_list})
        return d


class BaseEventReportIntervalOutput(BaseEventReport):
    dlls = {}

    def __init__(self, event_trigger_list, start_day=0, duration_days=1000000, report_description="", nodeset_config=None, max_number_reports=15, reporting_interval=73, report_type=""):
        BaseEventReport.__init__(self, event_trigger_list, start_day, duration_days,
                                 report_description, nodeset_config, report_type)
        self.max_number_reports = max_number_reports
        self.reporting_interval = reporting_interval

    def to_dict(self):
        d = super(BaseEventReportIntervalOutput, self).to_dict()
        d["Max_Number_Reports"] = self.max_number_reports
        d["Reporting_Interval"] = self.reporting_interval
        return d


class BaseMalariaTransmissionReport(BaseReport):
    dlls = {}

    def __init__(self, start_day=0, duration_days=10000, report_description='', nodes=None, report_type='ReportSimpleMalariaTransmissionJSON', pretty_format=1):

        BaseReport.__init__(self, report_type)
        self.start_day = start_day
        self.duration_days = duration_days
        self.pretty_format = pretty_format
        if not nodes:
            self.nodeset_config = {"class": "NodeSetAll"}
        else:
            self.nodeset_config = {"class": "NodeSetNodeList", "Node_List": nodes}
        self.report_description = report_description

    def to_dict(self):
        d = super(BaseMalariaTransmissionReport, self).to_dict()
        d.update({"Report_Description": self.report_description,
                  "Start_Day": self.start_day,
                  "Duration_Days": self.duration_days,
                  "Nodeset_Config": self.nodeset_config,
                  "Pretty_Format": self.pretty_format})
        return d


def add_node_demographics_report(cb, stratify_by_gender=0, age_bins=None, ip_key_to_collect=''):
    node_demographics_report = BaseDemographicsReport(stratify_by_gender=stratify_by_gender, age_bins=age_bins, ip_key_to_collect=ip_key_to_collect, report_type='ReportNodeDemographics')
    cb.add_reports(node_demographics_report)


def add_human_migration_tracking_report(cb):
    human_migration_tracking_report = BaseReport(report_type='ReportHumanMigrationTracking')
    cb.add_reports(human_migration_tracking_report)
