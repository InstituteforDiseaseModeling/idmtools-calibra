import json
from idmtools.entities import IAnalyzer
from itertool.utilities.Encoding import GeneralEncoder


class BaseCalibrationAnalyzer(IAnalyzer):
    def __init__(self, uid=None, working_dir=None, parse=True, need_dir_map=False, filenames=None,
                 reference_data=None, weight=1):
        super().__init__(uid=uid, working_dir=working_dir, parse=parse, filenames=filenames)
        self.reference_data = reference_data
        self.weight = weight

    def cache(self):
        return json.dumps(self, cls=GeneralEncoder)
