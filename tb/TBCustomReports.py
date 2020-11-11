# from dtk.utils.reports import *
# from itertool.utilities.reports.custom_report import BaseReport
from emodpy.reporters.base import CustomReporter
from reporters.custom import Report_TBHIV_ByAge


class TBReport(CustomReporter):
    dlls = {'Report_TBAge': 'libcustomreport_TBAge.dll',
            'Report_TBHIV_Basic': 'libcustomreport_TBHIV_Basic.dll',
            'Report_TBHIV_All_Ages': 'libcustomreport_TBHIV_All_Ages.dll',
            'Report_TBHIV_ByAge': 'libcustomreport_TBHIV_ByAge.dll'}

    def __init__(self,
                 start_year=0,
                 stop_year=3000,  # default of some large number we won't reach
                 min_age_yrs=0,  # for reporters which restrict age range
                 max_age_yrs=200,  # for reporters which restrict age range
                 additional_events=[],
                 IP_key_to_collect=[],
                 type=""):

        Report_TBHIV_ByAge.__init__(self, type)
        self.start_year = start_year
        self.stop_year = stop_year
        self.IP_key_to_collect = IP_key_to_collect
        if (type in ['Report_TBHIV_All_Ages', 'Report_TBHIV_ByAge']):
            self.max_age_yrs = max_age_yrs
            self.min_age_yrs = min_age_yrs
            self.additional_events = additional_events

    def to_dict_bk(self):
        d = super(TBReport, self).to_dict()

        d.update({"Start_Year": self.start_year,
                  "Stop_Year": self.stop_year})
        if self.max_age_yrs:
            d.update({"Min_Age_Yrs": self.min_age_yrs,
                      "Max_Age_Yrs": self.max_age_yrs})
        if self.IP_key_to_collect:
            d.update({"IP_Key_To_Collect": self.IP_key_to_collect})
        if self.additional_events:
            d.update({'Additional_Events': self.additional_events})
        return d

    def to_dict(self):
        d = super(TBReport, self).to_dict()

        dd = {}
        dd.update({"Start_Year": self.start_year,
                  "Stop_Year": self.stop_year})
        if self.max_age_yrs:
            dd.update({"Min_Age_Yrs": self.min_age_yrs,
                      "Max_Age_Yrs": self.max_age_yrs})
        if self.IP_key_to_collect:
            dd.update({"IP_Key_To_Collect": self.IP_key_to_collect})
        if self.additional_events:
            dd.update({'Additional_Events': self.additional_events})

        d['Reports'].append(dd)
        return d


def add_tb_report(task, start_year=0, stop_year=3000, min_age_yrs=0, max_age_yrs=200, additional_events=[],
                  type='Report_TBAge', IP_key_to_collect=''):
    node_tb_report = TBReport(start_year=start_year,
                              stop_year=stop_year,
                              min_age_yrs=min_age_yrs,
                              max_age_yrs=max_age_yrs,
                              IP_key_to_collect=IP_key_to_collect,
                              additional_events=additional_events,
                              type=type)
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
    from emodpy.emod_task import EMODTask
    from itertool.utilities.emod_malaria_sim import EMODMalariaSim

    exe_path = r"/examples/inputs/bamboo/Eradication.exe"

    task = EMODTask.from_default(default=EMODMalariaSim(), eradication_path=exe_path, ep4_custom_cb=None)

    # This is a legacy executable -> set it in the task
    # Points the reporters to the correct dll path
    # task.reporters.add_dll_folder(os.path.join(INPUT_PATH))

    # Create a report TBHIV by Age and add a couple of reports to it
    report = Report_TBHIV_ByAge()
    report.add_report(200, 0, 0, 200)
    report.add_report(100, 0, 0, 100)

    task.reporters.add_reporter(report)
    print(task.reporters.json)


if __name__ == "__main__":
    demo_1()
    exit()

    demo_2()
    exit()
