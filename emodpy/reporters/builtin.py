from dataclasses import dataclass, field

from emodpy.reporters.base import BuiltInReporter


@dataclass
class ReporterVectorGenerics(BuiltInReporter):
    Gender: str = field(default="GENDER_FEMALE")
    Species: str = field(default=None)
    Stratify_By: str = field(default="GENOME")
    class_name: str = field(default="ReportVectorGenetics")


@dataclass
class ReportNodeDemographics(BuiltInReporter):
    Stratify_By_Gender: bool = field(default=False)
    Age_Bins: list = field(default_factory=list)
    class_name: str = field(default="ReportNodeDemographics")


@dataclass
class MalariaSummaryReport(BuiltInReporter):
    class_name: str = field(default="MalariaSummaryReport")


@dataclass
class MalariaPatientJSONReport(BuiltInReporter):
    class_name: str = field(default="MalariaPatientJSONReport")


@dataclass
class ReportHumanMigrationTracking(BuiltInReporter):
    class_name: str = field(default="ReportHumanMigrationTracking")
