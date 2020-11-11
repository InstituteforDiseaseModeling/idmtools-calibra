# from dtk.utils.reports import *
# from itertool.utilities.reports.custom_report import BaseReport
from emodpy.reporters.base import CustomReporter
from reporters.custom import Report_TBHIV_ByAge


class TBReport(Report_TBHIV_ByAge):
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


def demo_1():
    """
    {
       "Reports":[

       ],
       "Custom_Reports":{
          "Use_Explicit_Dlls":1,
          "Report_TBHIV_ByAge":{
             "Enabled":1,
             "Reports":[

             ],
             "Start_Year":0,
             "Stop_Year":2000,
             "Min_Age_Yrs":0,
             "Max_Age_Yrs":200,
             "Additional_Events":[
                "TLAM",
                "TruePos",
                "TruePosHIV",
                "B200",
                "Bmiddle",
                "Seek200",
                "Seek350",
                "Seek500",
                "CRPPosHIVNeg",
                "CRPPosHIVPos",
                "B100",
                "LAMPosHIVPos",
                "LAMPosHIVNeg",
                "HIVTestedNegative",
                "HIVTestedPositive",
                "TotalPos",
                "TBMonitoring"
             ]
          }
       }
    }
    """
    from emodpy.emod_task import EMODTask
    from itertool.utilities.emod_malaria_sim import EMODMalariaSim

    exe_path = r"/examples/inputs/bamboo/Eradication.exe"
    task = EMODTask.from_default(default=EMODMalariaSim(), eradication_path=exe_path, ep4_custom_cb=None)
    add_tb_report(task, stop_year=2000,
                  additional_events=['TLAM', 'TruePos', 'TruePosHIV', 'B200', 'Bmiddle', 'Seek200', 'Seek350',
                                     'Seek500', 'CRPPosHIVNeg', 'CRPPosHIVPos', 'B100', 'LAMPosHIVPos', 'LAMPosHIVNeg',
                                     'HIVTestedNegative', 'HIVTestedPositive', 'TotalPos', 'TBMonitoring'],
                  type='Report_TBHIV_ByAge')
    print(task.reporters.json)


def demo_2():
    """
    {
      "Reports": [],
      "Custom_Reports": {
        "Use_Explicit_Dlls": 1,
        "Report_TBHIV_ByAge": {
          "Enabled": 1,
          "Reports": [
            {
              "Max_Age_Yrs": 200,
              "Min_Age_Yrs": 0,
              "Start_Year": 0,
              "Stop_Year": 200
            },
            {
              "Max_Age_Yrs": 100,
              "Min_Age_Yrs": 0,
              "Start_Year": 0,
              "Stop_Year": 100
            }
          ]
        }
      }
    }

    """
    from emodpy.emod_task import EMODTask
    from itertool.utilities.emod_malaria_sim import EMODMalariaSim

    exe_path = r"/examples/inputs/bamboo/Eradication.exe"
    task = EMODTask.from_default(default=EMODMalariaSim(), eradication_path=exe_path, ep4_custom_cb=None)

    # This is a legacy executable -> set it in the task
    # Points the reporters to the correct dll path
    # task.reporters.add_dll_folder(os.path.join(INPUT_PATH))

    # Create a report TBHIV by Age and add a couple of reports to it
    report = Report_TBHIV_ByAge()       # [TODO] zdu: add_report should support input: additional_events
    report.add_report(200, 0, 0, 200)
    report.add_report(100, 0, 0, 100)

    task.reporters.add_reporter(report)
    print(task.reporters.json)


if __name__ == "__main__":
    # demo_1()
    # exit()

    demo_2()
    exit()
