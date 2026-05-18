

import numpy


class IMUInfo():

    def __init__(self):
        self.valid = False

        self.time_now = 0.0
        self.count_yaw = 0
        self.yaw_init = 0.0

        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0

        self.omega_inte = 0.0
        self.omega = 0.0
        self.record_inte = []
        self.record_omega = []

        self.__msg = {"roll":0.0,"pitch":0.0,"yaw":0.0}
        pass

    def read(self, imuDict):
        """

        """
        self.roll = imuDict['roll']
        self.pitch = imuDict['pitch']
        self.yaw = imuDict['yaw']
        pass

    def write(self):
        self.__msg['roll'] = self.roll
        self.__msg['pitch'] = self.pitch
        self.__msg['yaw'] = self.yaw
        pass