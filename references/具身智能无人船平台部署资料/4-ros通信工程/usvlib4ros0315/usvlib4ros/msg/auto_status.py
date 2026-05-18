from .constant import Constants
"""当前自动模式、导航开始时间等元信息"""

class AutoStatusMeta:

    def __init__(self):
        self.workModel = Constants.WorkMode.Ready       #船舶任务模式：就绪，遥控，自动，自动返航
        self.navRouteStartTime = 0.0                    #导航路线开始时间，单位：s
        self.poseModel = Constants.PoseMode.UintyPose   #定位模式：实船GPS或虚拟Unity定位

    def read(self,autoStatusDict):
        """"""
        """
        AutoCommand.msg:
        int8 workModel
        int8 poseModel
        float64 navRouteStartTime
        """
        self.workModel = autoStatusDict['workModel']
        self.poseModel = autoStatusDict['poseModel']
        self.navRouteStartTime = autoStatusDict['navRouteStartTime']


"""当前自动状态，包含建议油门，航向，目标点，等信息"""
class AutoStatus():

    def __init__(self) :
        self.adviseThrottle = 0     #油门[-100,100]，百分比
        self.adviseRudder = 0       #舵向[-100,100]，百分比
        self.adviseHeading = 0.0    #航向[-180,180]°
        self.pointIndex = 0         #目标点下标
        self.distance = 0.0         #船与目标点距离
        self.__msgDict = {'adviseThrottle':0,'adviseRudder':0,'adviseHeading':0.0,'pointIndex':0,"distance":0.0}
        pass

    def read(self,msgDict):
        self.adviseThrottle = msgDict['adviseThrottle']
        self.adviseRudder = msgDict['adviseRudder']
        self.adviseHeading = msgDict['adviseHeading']
        self.pointIndex = msgDict['pointIndex']
        self.distance = msgDict['distance']
        return self

    def updateAutoStatus(self,adviseThrottle,adviseRudder,adviseHeading,pointIndex,distance):
        self.adviseThrottle = int(adviseThrottle)
        self.adviseRudder = int(adviseRudder)
        self.adviseHeading = adviseHeading
        self.pointIndex = int(pointIndex)
        self.distance = distance
        self.write()
        return self

    def write(self):
        self.__msgDict['adviseThrottle'] = self.adviseThrottle
        self.__msgDict['adviseRudder'] = self.adviseRudder
        self.__msgDict['adviseHeading'] = self.adviseHeading
        self.__msgDict['pointIndex'] = self.pointIndex
        self.__msgDict['distance'] = self.distance
        return self.__msgDict
