from reporters.custom import Report_TBHIV_ByAge
from dataclasses import field


class TBReport(Report_TBHIV_ByAge):
    dll_file: str = field(default="libcustomreport_TBHIV_ByAge.dll")
    def add_report(self, max_age_yrs, min_age_yrs, start_year, stop_year, additional_events):
        self._add_report({
            "Additional_Events": additional_events,
            "Max_Age_Yrs": max_age_yrs,
            "Min_Age_Yrs": min_age_yrs,
            "Start_Year": start_year,
            "Stop_Year": stop_year
        })


def add_tb_report(task, start_year=0, stop_year=3000, min_age_yrs=0, max_age_yrs=200, additional_events=[]):
    node_tb_report = TBReport()
    node_tb_report.add_report(start_year=start_year,
                              stop_year=stop_year,
                              min_age_yrs=min_age_yrs,
                              max_age_yrs=max_age_yrs,
                              additional_events=additional_events)
    task.reporters.add_reporter(node_tb_report)
