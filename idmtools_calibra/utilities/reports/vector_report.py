from .custom_report import BaseReport
from .custom_report import BaseVectorStatsReport


def add_habitat_report(cb):
    cb.add_reports(BaseReport(report_type="VectorHabitatReport"))


def add_vector_stats_report(cb):
    cb.add_reports(BaseVectorStatsReport(report_type="ReportVectorStats"))


def add_vector_stats_malaria_report(cb):
    cb.add_reports(BaseVectorStatsReport(report_type="ReportVectorStatsMalaria"))


def add_vector_migration_report(cb):
    cb.add_reports(BaseReport(report_type="ReportVectorMigration"))


def add_human_migration_report(cb):
    cb.add_reports(BaseReport(report_type="ReportHumanMigrationTracking"))
