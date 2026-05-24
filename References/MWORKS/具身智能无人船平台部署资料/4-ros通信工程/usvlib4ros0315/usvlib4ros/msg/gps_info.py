

import numpy


class GPSInfo():

    def __init__(self):
        self.valid = False

        self.roll = 0.0
        self.pitch = 0.0
        self.heading = 0.0

        self.speed = 0.0
        self.groundKnots = 0.0

        self.lng = 0.0
        self.lat = 0.0
        self.high = 0.0

        self.rotateSpeed = 0.0

        self.lngBuffer = numpy.zeros(50,dtype=numpy.float64)
        self.latBuffer = numpy.zeros(50,dtype=numpy.float64)
        pass

    def read(self, gpsDict):
        """
        poseDict eg: {'header': {},'lng':138.451211,'lat':30.12451,'high':0, 'roll':138.451211,'pitch':30.12451,'yaw':0,'speed':0,'rotateSpeed':0}
        """
        self.header = gpsDict['header']
        self.lng = gpsDict['lng']
        self.lat = gpsDict['lat']
        self.high = gpsDict['high']

        self.roll = gpsDict['roll']
        self.pitch = gpsDict['pitch']
        self.heading = gpsDict['yaw']

        self.speed = gpsDict['speed']
        self.rotateSpeed = gpsDict['rotateSpeed']
        pass