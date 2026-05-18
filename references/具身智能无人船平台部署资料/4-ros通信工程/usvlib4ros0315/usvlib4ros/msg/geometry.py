

class Vector3:

    def __init__(self,**kwargs):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        pass

class Pose:

    def __init__(self):

        self.header = {}
        self.lng = 0.0
        self.lat = 0.0
        self.high = 0.0

        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0

        self.speed = 0.0
        self.rotateSpeed = 0.0

        pass

    def read(self, poseDict):
        """
        poseDict eg: {'header': {},'lng':138.451211,'lat':30.12451,'high':0, 'roll':138.451211,'pitch':30.12451,'yaw':0,'speed':0,'rotateSpeed':0}
        """
        self.header = poseDict['header']
        self.lng = poseDict['lng']
        self.lat = poseDict['lat']
        self.high = poseDict['high']

        self.roll = poseDict['roll']
        self.pitch = poseDict['pitch']
        self.yaw = poseDict['yaw']

        self.speed = poseDict['speed']
        self.rotateSpeed = poseDict['rotateSpeed']
        pass