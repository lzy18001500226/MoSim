#!/usr/bin/env python
#coding:utf-8

import threading
import time

from usvlib4ros.msg import Point,GlobalData,Parameter,Constants,Route
from usvlib4ros.usvRosUtil import LogUtil,RosSrvClientProxy

from usvlib4ros.navigation.autp_pilot_service import AutoPilotService
from usvlib4ros.navigation.route_plan_service import RoutePlanService
from usvlib4ros.navigation.avoid_collision_service import AvoidCollisionService


class USVAutoNavigationService():

    Instance = None

    """
    USV auto navigation service
    """
    @classmethod
    def startService(cls):
        usvAutoNavService = cls.getInstance()
        navThread = threading.Thread(target= usvAutoNavService.run)
        navThread.setDaemon(True)
        navThread.start()
        pass

    @classmethod
    def getInstance(cls):
        if cls.Instance is None :
            cls.Instance = USVAutoNavigationService()
        return cls.Instance

    def __init__(self,xyzAxis = True) :
        
        """unity adjust parameter list"""
        """unity show parameter list"""
        # self.dispalyParameterList = {}

        self.localRouteUpdateTime = 0.0 #s

        self.route = Route()
        self.localRouteUpdateTime = -1

        self.routePlaneService = RoutePlanService(wayPointRadius=1.0,route=self.route)
        self.autoPilotService = AutoPilotService()
        self.avoidCollisionService = AvoidCollisionService()

        self.destPoint = Point()   #目标点  lng lat high speed
        self.destPointIndex = -1   #目标点self.destPoint在导航点GlobalData.getInstance().route.points中的下标，-1表示无导航点。
        self.prevPoint = Point()
        self.prevPointIndex = -1
        pass

    def reset(self):
        self.destPoint = Point()   #目标点 lng lat high
        self.destPointIndex = -1   #目标点self.destPoint在导航点GlobalData.getInstance().route.points中的下标，-1表示无导航点。
        self.prevPoint = Point()
        self.prevPointIndex = -1

    def run(self):
        """"""
        """register parameter """
        """adjust parameter data update by topic thread"""
        self.registerParameter()

        while True:
            try:

                self.navigationHandler()
                """monitor parameter data update by this thread"""
                self.setMonitorParameterValue()
                pass
            except Exception as e:
                LogUtil.error(e)
                pass
            finally:
                time.sleep(0.02)#100ms

    def registerParameter(self):
        """"""
        """重启导航模块后 清空已有参数列表"""
        RosSrvClientProxy.resetParameterList()
        """adjust parameter data update by topic thread"""

        """导航点有效半径，船位于此半径内即为达到导航点"""
        name = '/usv/auto/plan/attainRadius'
        attainRadius = Parameter(name=name,dataType='float',defaultData=2)
        result = RosSrvClientProxy.registParameter(attainRadius)
        if result:
            GlobalData.getInstance().parameterAdjustMap.update({name:attainRadius})
            self.routePlaneService.wayPointRadius = attainRadius.value

        param2 = Parameter(name='/usv/auto/param2', dataType='int', defaultData=[20])
        result = RosSrvClientProxy.registParameter(param2)
        if result:
            GlobalData.getInstance().parameterAdjustMap.update({'/usv/auto/param2': param2})

        param3 = Parameter(name='/usv/auto/param3', dataType='int', defaultData=[30,31])
        result = RosSrvClientProxy.registParameter(param3)
        if result:
            GlobalData.getInstance().parameterAdjustMap.update({'/usv/auto/param3': param3})

        param4 = Parameter(name='/usv/auto/param4', dataType='float', defaultData=[40.1, 40.2])
        result = RosSrvClientProxy.registParameter(param4)
        if result:
            GlobalData.getInstance().parameterAdjustMap.update({'/usv/auto/param4': param4})

        param5 = Parameter(name='/usv/auto/param5', dataType='bool', defaultData=True)
        result = RosSrvClientProxy.registParameter(param5)
        if result:
            GlobalData.getInstance().parameterAdjustMap.update({'/usv/auto/param5': param5})

        param6 = Parameter(name='/usv/auto/param6', dataType='str', defaultData='some msg')
        result = RosSrvClientProxy.registParameter(param6)
        if result:
            GlobalData.getInstance().parameterAdjustMap.update({'/usv/auto/param6': param6})

        """monitor parameter """
        #TODO

        pass

    def setMonitorParameterValue(self):
        """monitor parameter """

        pass


    def __loadVehiclePoseInfo(self):
        """
        isAuto  : True 自动导航;False 非自动导航
        isReturn:True 自动返航;False 非自动返航
        lng     : 航行器当前经度
        lat     : 航行器当前纬度
        realSpeed:航行器当前速度 m/s
        realRotateSpeed:航行器当前角速度 °/s
        """
        workModel = GlobalData.getInstance().autoCommand.workModel
        isReturn = workModel == Constants.WorkMode.AutoReturn
        isAuto = workModel == Constants.WorkMode.Auto

        lng = GlobalData.getInstance().gpsInfo.lng
        lat = GlobalData.getInstance().gpsInfo.lat
        heading = GlobalData.getInstance().gpsInfo.heading
        realSpeed = GlobalData.getInstance().gpsInfo.speed
        realRotateSpeed = 0.0 # TODO °/s

        # if GlobalData.getInstance().autoCommand.poseModel == Constants.PoseMode.UintyPose:
        lng = GlobalData.getInstance().pose.lng
        lat = GlobalData.getInstance().pose.lat
        heading = GlobalData.getInstance().pose.yaw
        if heading > 180 :
            heading = heading - 360
        realSpeed = GlobalData.getInstance().pose.speed
        realRotateSpeed = GlobalData.getInstance().pose.rotateSpeed

        return isAuto,isReturn,lng,lat,heading,realSpeed,realRotateSpeed


    def __reloadNavigationRoute(self, route):
        """return True:new route"""
        """更新route"""
        self.route = route # load route info from global data
        self.routePlaneService.reset(route=self.route)

        """设置目标点"""
        startIndex = self.route.startIndex
        self.destPointIndex = startIndex
        self.destPoint = Point()
        if len(self.route.points) > startIndex >= 0:
            self.destPoint = self.route.points[startIndex]

        """update global data with current route meta info"""
        # GlobalData.getInstance().routeMeta.id = self.route.id
        # GlobalData.getInstance().routeMeta.name = self.route.name
        # GlobalData.getInstance().routeMeta.version = self.route.version
        #
        # GlobalData.getInstance().routeMeta.write()

        LogUtil.info("Use route %s .start at point %s ."%(GlobalData.getInstance().routeMeta.write(),startIndex))
        return True

    def navigationHandler(self):
        """
        导航算法:       
        """

        """
        navigation output 
        """
        adviseOutputValid = False   #导航算法输出是否有效; True 有效； False 无效

        adviseSpeed = 0.0           #导航算法建议速度 m/s
        adviseRotate = 0.0          #导航算法建议角速度 °/s
        advisedHeading = 0          #导航算法建议航向 [-180°，180°]（北向0°，东向90°）
        nextPointIndex = 0          #前往导航点下标
        shipToNextWPDistance = 0    #船与导航点距离

        try:
            """导航点有效达到半径"""
            attainRadius = GlobalData.getInstance().parameterAdjustMap.get('/usv/auto/plan/attainRadius')
            self.routePlaneService.wayPointRadius = attainRadius.value
            pass
        except Exception as e:
            LogUtil.error(e)

        try:

            """
            获取航行器姿态和位置
            isAuto  : True 自动导航;False 非自动导航
            isReturn:True 自动返航;False 非自动返航
            lng     : 航行器当前经度
            lat     : 航行器当前纬度
            realSpeed:航行器当前速度 m/s
            realRotateSpeed:航行器当前角速度 °/s
            """
            isAuto,isReturn,lng,lat,heading,realSpeed,realRotateSpeed = self.__loadVehiclePoseInfo()

            """获取全局路线信息与导航算法路线信息比较"""
            globalRouteUpdateTime,globalRoute = GlobalData.getInstance().getRouteInfo()
            if globalRouteUpdateTime != self.localRouteUpdateTime:
                """当前修改了导航路线"""
                self.__reloadNavigationRoute(globalRoute)
                self.localRouteUpdateTime = globalRouteUpdateTime
                adviseOutputValid = False #
                return
            
            if isAuto is not True or len(self.route.points) == 0:
                """当前非自动模式，不启用导航算法"""
                adviseOutputValid = False #
                return
            
            """自动模式，路线已加载，开始导航"""
            adviseOutputValid = True

            """路径规划"""
            self.routePlaneService.setCurrentPos(lng,lat,isReturn)

            """获取路径规划结果"""
            try:
                                
                nextPointIndex = self.routePlaneService.curNextIndex
                prevPointIndex = self.routePlaneService.curPrevIndex

                nextPoint = self.route.points[nextPointIndex]
                if prevPointIndex < 0 or prevPointIndex >= len(self.route.points):
                    prevPointIndex = nextPointIndex

                if nextPointIndex != self.destPointIndex or nextPoint != self.destPoint:
                    """切换目标点"""
                    LogUtil.info("Goto point[%s] = \r\n[%s]"%(nextPointIndex,nextPoint))

                self.destPointIndex = nextPointIndex
                self.destPoint = self.route.points[self.destPointIndex] #目标点
                self.prevPointIndex = prevPointIndex
                self.prevPoint = self.route.points[self.prevPointIndex] #目标点
            except Exception as e:
                LogUtil.error(e)
           
            if self.destPointIndex == -1 :
                """无导航目标点"""
                adviseOutputValid = False
                return 
                pass

            """自动导航相关数据"""
            destLng = self.destPoint.lng
            destLat = self.destPoint.lat
            prevLng = self.prevPoint.lng
            prevLat = self.prevPoint.lat
            shipToRouteDistance = self.routePlaneService.distanceMetersShip2RouteLine
            shipToNextWPDistance = self.routePlaneService.distanceMetersShip2NextWP
            shipToPrevWPDistance = self.routePlaneService.shipDistanceA

            """导航算法可调参数赋值"""
            # self.autoPilotService.maxSpeed = self.adjustParameterList['/auto/pilot/maxSpeedParam']
            # self.autoPilotService.maxRotateSpeed = self.adjustParameterList['/auto/pilot/maxRotateParam']

            """通过 prevPoint，destPoint，ship位置计算建议速度和角速度"""
            self.autoPilotService.setConditions(realSpeed,heading,lng,lat,destLng,destLat,prevLng,prevLat,shipToPrevWPDistance,shipToNextWPDistance,shipToRouteDistance)
            
            """get result"""
            adviseSpeed = self.autoPilotService.advisedSpeed
            adviseRotate = self.autoPilotService.advisedRotateSpeed
            advisedHeading = self.autoPilotService.advisedHeading
            LogUtil.info("Goto index = %s, heading : %s = > %s .distance=%s .speed = %s , rotate = %s ."%(self.destPointIndex,heading,advisedHeading,shipToNextWPDistance,adviseSpeed, adviseRotate))
            
            """"
            障碍物信息 self.route.obstacles[]
            """
            """避障"""
            adviseSpeed ,adviseRotate , advisedHeading = self.avoidCollisionService.calcSafeVoyage(lng,lat,heading,realSpeed,realRotateSpeed,adviseSpeed,adviseRotate,advisedHeading,self.route.obstacles)
            pass 
        except Exception as e:
            LogUtil.error(e)
        finally:
            if adviseOutputValid is False:
                adviseSpeed = 0
                adviseRotate = 0
                advisedHeading = 0
                shipToNextWPDistance = 0
                nextPointIndex = 0

            # GlobalData.getInstance().autoStatus.updateAutoStatus(adviseSpeed, adviseRotate, advisedHeading,nextPointIndex,shipToNextWPDistance)
        return adviseSpeed,adviseRotate,advisedHeading,nextPointIndex,shipToNextWPDistance
        pass

    
    pass