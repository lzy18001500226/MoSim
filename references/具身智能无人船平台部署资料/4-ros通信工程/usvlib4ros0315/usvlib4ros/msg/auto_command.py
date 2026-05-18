from .constant import Constants


class AutoCommand:

    def __init__(self):
        self.workModel = Constants.WorkMode.Ready #
        self.navRouteStartTime = 0.0 #导航路线开始时间
        self.poseModel = Constants.PoseMode.UintyPose

    def read(self,autoCommandDict):
        """"""
        """
        AutoCommand.msg:
        int8 workModel
        int8 poseModel
        float64 navRouteStartTime
        """
        self.workModel = autoCommandDict['workModel']
        self.poseModel = autoCommandDict['poseModel']
        self.navRouteStartTime = autoCommandDict['navRouteStartTime']

