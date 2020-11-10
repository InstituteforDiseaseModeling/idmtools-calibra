from .custom_report import BaseReport
from .custom_report import BaseVectorStatsReport


def add_habitat_report(cb):
    cb.add_reports(BaseReport(type="VectorHabitatReport"))


def add_vector_stats_report(cb):
    cb.add_reports(BaseVectorStatsReport(type="ReportVectorStats"))

def add_vector_stats_malaria_report(cb):
    cb.add_reports(BaseVectorStatsReport(type="ReportVectorStatsMalaria"))

def add_vector_migration_report(cb):
    cb.add_reports(BaseReport(type="ReportVectorMigration"))


def add_human_migration_report(cb):
    cb.add_reports(BaseReport(type="ReportHumanMigrationTracking"))
