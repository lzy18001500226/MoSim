
import threading

ROS_MODE = 0

if ROS_MODE == 0:
    from .pose import Pose
    from .vehicle_command import VehicleHighPercentCommand
    from .route import Point,Route,RouteMeta
    from .gps_info import GPSInfo
    from .auto_status import AutoStatus,AutoStatusMeta
    from .model_command import ModelCommand,ModelReply
elif ROS_MODE == 1:
    pass


class DictToObject:

    def __init__(self,**kwargs):
        for key,value in kwargs.items():
            if isinstance(value,dict):
                setattr(self,key,DictToObject(**value))
            else:
                setattr(self,key,value)
    pass



class USV_ROS_STSTUS:
    NO_INIT = 0
    INIT = 1
    FIRST_CONNECTED = 2
    INIT_FINISH = 3


class GlobalData:

    Instance = None

    # def __new__(cls, *args, **kwargs):
    #     """单例模式"""
    #     if cls.Instance is None:
    #         cls.Instance = super(GlobalData, cls).__new__(cls)
    #     return cls.Instance

    @classmethod
    def getInstance(cls):
        if cls.Instance is None:
            cls.Instance = GlobalData()

        return cls.Instance

    def __init__(self):
        """"""
        GlobalData.Instance = self
        """input"""
        self.pose = Pose()                  #unity仿真船位置
        self.gpsInfo = GPSInfo()            #实船GPS
        self.autoCommand = AutoStatusMeta()    #前自动模式、导航开始时间等元信息
        self.autoCommandTemp = self.autoCommand
        self.modelCommand = ModelCommand()      #模型输入参数
        self.__routeUpdateTime = 0.0        #单位 s, 系统缓存路线更新时间
        self.__route = Route()              #系统缓存导航路线
        self.autoStatusEcho = AutoStatus()  #订阅自己发布的AutoStatus信息

        """output"""
        self.routeMeta = RouteMeta()        #当前自动导航使用路线信息
        self.autoStatus = AutoStatus()      #当前自动导航输出控制状态信息
        self.modelReply = ModelReply()      #模型输出

        """local tmp"""
        self.routeUpdateFlag = False            # False 没有新路线； True 路线更新，请调用 GlobalData.getInstance().consumerRoute()获取新路线
        self.parameterAdjustMap = {}
        self.parameterMonitorMap = {}
        self.routeLock = threading.Lock()
        self.ros_state = USV_ROS_STSTUS.NO_INIT
        """
        modelParams 船模形固有属性，初始化在此赋值，可通过unity设置
        L=1.3;
        B=0.64;
        Bhull=0.21;
        mass=50;
        LCG=0.45;
        g=9.8;
        T=0.12;
        Cd=0.5;
        rho=1000;
        Xu_linear=75.55;
        Xu_poly=-25;
        Xuu_linear=-70.92;
        Xuu_poly=0;
        """
        self.modelParams = [1.3,0.64,0.21,  50,0.45,9.8,  0.12,0.5,1000,  75.55,-25,-70.92,  0]
        pass

    def getRouteInfo(self):
        try:
            self.routeLock.acquire()
            return self.__routeUpdateTime,self.__route
        finally:
            self.routeLock.release()

    def updateRouteInfo(self,route,routeUpdateTime):
        try:
            self.routeLock.acquire()
            self.__route = route
            self.__routeUpdateTime = routeUpdateTime
            self.routeUpdateFlag = True
        finally:
            self.routeLock.release()

    def consumerRoute(self):
        route = None
        try:
            self.routeLock.acquire()
            route = self.__route
            self.routeUpdateFlag = False
        finally:
            self.routeLock.release()
        return route


    pass