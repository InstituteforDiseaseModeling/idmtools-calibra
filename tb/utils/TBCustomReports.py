from dtk.utils.reports import *

class TBReport(BaseReport):

    dlls = {'Report_TBAge': 'libcustomreport_TBAge.dll',
            'Report_TBHIV_Basic': 'libcustomreport_TBHIV_Basic.dll',
            'Report_TBHIV_All_Ages': 'libcustomreport_TBHIV_All_Ages.dll',
            'Report_TBHIV_ByAge': 'libcustomreport_TBHIV_ByAge.dll'}


    def __init__(self,
                 start_year=0,
                 stop_year= 3000,  #default of some large number we won't reach
                 min_age_yrs= 0,   # for reporters which restrict age range
                 max_age_yrs= 200, # for reporters which restrict age range
                 additional_events = [],
                 IP_key_to_collect= [],
                 type=""):

        BaseReport.__init__(self, type)
        self.start_year = start_year
        self.stop_year = stop_year
        self.IP_key_to_collect = IP_key_to_collect
        if (type in ['Report_TBHIV_All_Ages', 'Report_TBHIV_ByAge']):
            self.max_age_yrs =  max_age_yrs
            self.min_age_yrs = min_age_yrs
            self.additional_events = additional_events

    def to_dict(self):
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


def add_tb_report(cb, start_year= 0, stop_year= 3000, min_age_yrs= 0,max_age_yrs= 200, additional_events=[], type= 'Report_TBAge',  IP_key_to_collect=''):
    node_tb_report = TBReport(start_year= start_year,
                              stop_year=stop_year,
                              min_age_yrs= min_age_yrs,
                              max_age_yrs= max_age_yrs,
                              IP_key_to_collect=IP_key_to_collect,
                              additional_events= additional_events,
                              type=type)
    cb.add_reports(node_tb_report)