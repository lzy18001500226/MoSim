
import numpy as np
from rosbagUtil import RosBagUtil
class GlobalData:

    rosbagUtil = None
    param_dict = {
        "speed": "速度",
        "rotateSpeed": "加速度",
        "throttlePercent": "throttlePercent",
        "rudderPercent": "rudderPercent",
        "poseModel": "pose模式"
    }
    @classmethod
    def initialize(cls,path):
        cls.rosbagUtil = RosBagUtil(path)

    @classmethod
    def set_timestamp(cls, timestamp):
        cls.timestamp = timestamp

    @classmethod
    def set_speed(cls, speed_value):
        cls.speed = speed_value

    @classmethod
    def get_rosbagUtil(cls):
        return cls.rosbagUtil

    @classmethod
    def get_param_dict(cls):
        return cls.param_dict

    @classmethod
    def get_timestamps(cls):
        return cls.timestamp

    @classmethod
    def get_speeds(cls):
        return cls.speed

