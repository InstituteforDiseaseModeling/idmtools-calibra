import os
import json
from idmtools_calibra.resamplers.calibration_point import CalibrationPoint


class CalibrationPoints(object):
    def __init__(self, points):
        self.points = points

    def write(self, filename):
        point_dicts = [p.to_dict() for p in self.points]
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(point_dicts, f)

    @classmethod
    def read(cls, filename):
        with open(filename) as f:
            list_of_dicts = json.load(f)
        point_list = [CalibrationPoint.from_dict(p) for p in list_of_dicts]
        return cls(points=point_list)
