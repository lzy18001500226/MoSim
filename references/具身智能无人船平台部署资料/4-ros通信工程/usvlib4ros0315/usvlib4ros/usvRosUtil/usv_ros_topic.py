import time
import threading
import roslibpy

"""
ros环境下安装 ros-melodic-rosbridge-server (melodic是ros版本)
apt-get install ros-melodic-rosbridge-server

启动 roscore 和 rosbridge
roscore
roslaunch rosbridge_server rosbridge_websocket.launch

rosbridge 有 tcp，udp ，websocket 三种启动方式，默认端口 9090
roslibpy 仅支持与 rosbridge的websocket 连接

在非ros环境下，安装roslibpy 
pip install roslibpy -i https://pypi.tuna.tsinghua.edu.cn/simple

"""

from usvlib4ros.usvRosUtil import USVRosbridgeClient,LogUtil
from usvlib4ros.usvRosUtil import RosSrvClientProxy
from usvlib4ros.msg import GlobalData


class RosTopicProxy:

    @classmethod
    def startService(cls):
        """根据autoCommand信息请求route"""
        th = threading.Thread(target=cls.topicHandler)
        th.setDaemon(True)
        th.start()
        pass

    @classmethod
    def getModelParamsSrvCallback(cls,request, response):
        """
        回调函数，不需要设置为 python function
        :param request:
        :param response:
        :return:
        """
        print(request)
        GlobalData.getInstance().modelParams = request['modelParams']
        response['result'] = 1
        return True

    @classmethod
    def firstConnectHandler(cls,deviceId="001"):

        # usvRosPublisher = USVRosbridgeClient()
        # modelReply = GlobalData.getInstance().modelReply
        # modelReplyDict = modelReply.write()
        # usvRosPublisher.startPublicTopicThread(topicName="/usv/001/scada/model/command/reply",
        #                                        msgType="message_pkg/ModelReply", topicMsg=modelReplyDict, frequency=50)

        """订阅消息示例"""
        usvRosSubscriber = USVRosbridgeClient()
        usvRosSubscriber.subscriber(topicName="/usv/%s/ctl/scada/parameter/adjustList"%(deviceId),
                                    msgType="message_pkg/ParameterMonitor",
                                    callback=cls.listenerAdjustParameterCallback)

        """订阅消息示例"""
        usvRosSubscriber = USVRosbridgeClient()
        usvRosSubscriber.subscriber(topicName="/usv/%s/scada/ctl/action/pose"%(deviceId),
                                    msgType="message_pkg/Pose",
                                    callback=cls.listenerPoseCallback)

        # """订阅消息示例"""
        # usvRosSubscriber = USVRosbridgeClient("192.168.3.35", 9090)
        # usvRosSubscriber.subscriber(topicName="/usv/001/ctl/nav/gpsInfo",
        #                             msgType="message_pkg/ParameterMonitor",
        #                             callback=cls.listenerRouteCallback)

        """订阅消息示例"""
        usvRosSubscriber = USVRosbridgeClient()
        usvRosSubscriber.subscriber(topicName="/usv/%s/ctl/nav/autoCommand"%(deviceId),
                                    msgType="message_pkg/AutoCommand",
                                    callback=cls.listenerAutoCommandCallback)

        """订阅消息示例"""
        usvRosSubscriber = USVRosbridgeClient()
        usvRosSubscriber.subscriber(topicName="/usv/%s/scada/model/command"%(deviceId),
                                    msgType="message_pkg/ModelCommand",
                                    callback=cls.listenerModelCommandCallback)

        """
        自定义消息文件
        message_pkg/msg/vehicleCommand.msg:
        bool valid
        bool reversed
        int16 throttlePercent
        int16 rudderPercent
        """
        usvRosPublisher = USVRosbridgeClient()
        autoStatus = GlobalData.getInstance().autoStatus
        autoStatusDict = autoStatus.write()
        usvRosPublisher.startPublicTopicThread(topicName="/usv/%s/ctl/scada/auto/status"%(deviceId),
                                               msgType="message_pkg/AutoStatus", topicMsg=autoStatusDict, frequency=50)

        """订阅消息示例"""
        usvRosSubscriber = USVRosbridgeClient()
        usvRosSubscriber.subscriber(topicName="/usv/%s/ctl/scada/auto/status"%(deviceId),
                                    msgType="message_pkg/AutoStatus",
                                    callback=cls.listenerAutoStatusEchoCallback)


        setParamsSrv = roslibpy.Service(USVRosbridgeClient.ros, "usv/%s/server/setModelParams"%(deviceId),
                                        "message_pkg/SetModelParams")
        setParamsSrv.advertise(cls.getModelParamsSrvCallback)

        """
        自定义消息文件
        message_pkg/msg/RouteMeta.msg:
        string id
        string name
        int32 version
        """
        usvRosPublisher = USVRosbridgeClient()
        routeMeta = GlobalData.getInstance().routeMeta
        routeMetaDict = routeMeta.write()
        usvRosPublisher.startPublicTopicThread(topicName="/usv/%s/ctl/scada/route"%(deviceId),
                                               msgType="message_pkg/RouteMeta", topicMsg=routeMetaDict,
                                               frequency=1)

    @classmethod
    def topicHandler(cls):

        # cls.firstConnectHandler()

        autoCommand = GlobalData.getInstance().autoCommand
        while True:
            try:
                routeUpdateTime,oldRoute = GlobalData.getInstance().getRouteInfo()
                navRouteStartTime = autoCommand.navRouteStartTime
                if routeUpdateTime != navRouteStartTime:
                    """系统导航路线更新时间与 本地缓存路线更新时间不一致，请求最新路线"""
                    route = RosSrvClientProxy.getRoute()
                    """通知导航系统路线已更新 """
                    GlobalData.getInstance().updateRouteInfo(routeUpdateTime=navRouteStartTime,route=route)
            except Exception as e:
                LogUtil.error(e)
            finally:
                time.sleep(0.1)
            pass
        pass



    @classmethod
    def listenerAdjustParameterCallback(cls,parameterMonitorDict):
        """"""
        """
        ParameterMonitor.msg:
        string version
        string subVersion
        Parameter[] data
        """
        version = parameterMonitorDict['version']
        subVersion = parameterMonitorDict['subVersion']
        data = parameterMonitorDict['data']
        for parameterDict in data:
            name = parameterDict['name']
            parameter = GlobalData.getInstance().parameterAdjustMap.get(name)
            if parameter is not None:
                parameter.read(parameterDict)
        pass

    @classmethod
    def listenerPoseCallback(cls,poseDict):
        """"""
        GlobalData.getInstance().pose.read(poseDict=poseDict)
        pass

    @classmethod
    def listenerModelCommandCallback(cls, modelCommandDict):
        """"""
        GlobalData.getInstance().modelCommand.read(modelCommandDict)
        pass

    @classmethod
    def listenerAutoStatusEchoCallback(cls, autoStatusDict):
        """"""
        GlobalData.getInstance().autoStatusEcho.read(autoStatusDict)
        pass


    # @classmethod
    # def listenerRouteCallback(cls,routeDict):
    #     """"""
    #     """
    #     自定义消息文件
    #     message_pkg/msg/Point.msg:
    #     float64 lng
    #     float64 lat
    #     float64 high
    #     float64 cruiseSpeed
    #
    #     message_pkg/msg/Route.msg:
    #     string id
    #     string name
    #     int32 version
    #     Point[] points
    #     Point[] obstacles
    #
    #     route = {'id': '1', 'name': 'route-test', 'version': 22,
    #              'points': [{'lng': 128.4512, 'lat': 38.12451, 'high': 0, 'cruiseSpeed': 5.3}], 'obstacles': []}
    #     """
    #     id = routeDict['id']
    #     name = routeDict['name']
    #     version = routeDict['version']
    #
    #     gloablRoute = GlobalData.getInstance().route
    #     if gloablRoute.id == id and gloablRoute.name == name and gloablRoute.version == version:
    #         return
    #
    #     route = Route()
    #     route.read(routeDict=routeDict)
    #
    #     GlobalData.getInstance().route = route
    #
    #     pass

    @classmethod
    def listenerAutoCommandCallback(cls, autoCommandDict):
        """"""
        GlobalData.getInstance().autoCommand.read(autoCommandDict)
        pass


if __name__ == "__main__":

    USVRosbridgeClient.initRoslibpyLogger()
    USVRosbridgeClient.initUSVRosBridgeConnection("192.168.3.35", 9090)
    """订阅消息示例"""
    usvRosSubscriber = USVRosbridgeClient()
    usvRosSubscriber.subscriber(topicName="/usv/001/ctl/scada/parameter/adjustList", msgType="message_pkg/ParameterMonitor",
                                callback=usvRosSubscriber.defaultSubscriberCallback)



    while True:

        pass

    """
    ros 基本消息类型
    std_msgs/msg/String.msg:
    string data
    """
    usvRosPublisher = USVRosbridgeClient()
    topicMsg = {"data":"hello msg ."}
    usvRosPublisher.startPublicTopicThread(topicName="/SpaceRExample", msgType="std_msgs/String", topicMsg=topicMsg, frequency=50)

    """
    自定义消息文件
    message_pkg/msg/Manual.msg:
    int8 handleOk
    int16 throttlePercent
    int16 rudderPercent
    """
    usvRosPublisher = USVRosbridgeClient()
    manual = {'handleOk':0,'throttlePercent':11,'rudderPercent':22}
    usvRosPublisher.startPublicTopicThread(topicName="/usv/001/scada/ctl/action/manual", msgType="message_pkg/Manual", topicMsg=manual, frequency=50)

    """
    自定义消息文件
    message_pkg/msg/Point.msg:
    float64 lng
    float64 lat
    float64 high
    float64 cruiseSpeed
    
    message_pkg/msg/Route.msg:
    string id
    string name
    int32 version
    Point[] points
    Point[] obstacles
    """
    usvRosPublisher = USVRosbridgeClient()
    route = {'id': '1', 'name': 'route-test', 'version': 22,'points':[{'lng':128.4512,'lat':38.12451,'high':0,'cruiseSpeed':5.3}],'obstacles':[]}
    usvRosPublisher.startPublicTopicThread(topicName="/route", msgType="message_pkg/Route",
                                           topicMsg=route, frequency=50)

    """订阅消息示例"""
    usvRosSubscriber = USVRosbridgeClient()
    usvRosSubscriber.subscriber(topicName="/route", msgType="message_pkg/Route", callback=usvRosSubscriber.defaultSubscriberCallback)

    usvRosSubscriber = USVRosbridgeClient()
    usvRosSubscriber.subscriber(topicName="/SpaceRExample", msgType="std_msgs/String",
                                callback=usvRosSubscriber.defaultSubscriberCallback)

    """服务示例"""

    """
    message_pkg/srv/SetWorkModel.srv:
    int32 workModel
    -----
    int32 result
    """
    start = time.time()
    usvRosSrvClient = USVRosbridgeClient()
    request = {'workModel':1}
    response = usvRosSrvClient.callService("/usv/001/server/switchWorkModel","message_pkg/SetWorkModel",request)
    end = time.time()
    print("Srv %s response is %s , use %s s"%("/usv/001/server/switchWorkModel",response,end-start))

    """
    message_pkg/msg/Point.msg:
    float64 lng
    float64 lat
    float64 high
    float64 cruiseSpeed
    
    message_pkg/msg/Route.msg:
    string id
    string name
    int32 version
    Point[] points
    Point[] obstacles
    
    message_pkg/srv/SetRoute.srv:
    Route route
    -----
    int8 result
    """
    start = time.time()
    usvRosSrvClient = USVRosbridgeClient()
    request = {'route': {'id': '13', 'name': 'route-test2', 'version': 23,'points':[{'lng':138.451211,'lat':30.12451,'high':0,'cruiseSpeed':3.3}],'obstacles':[]}}
    response = usvRosSrvClient.callService("/usv/001/server/setRoute", "message_pkg/SetRoute", request)
    end = time.time()
    print("Srv %s response is %s , use %s s ." % ("/usv/001/server/setRoute", response,end-start))




    while True:
        time.sleep(1)
    pass