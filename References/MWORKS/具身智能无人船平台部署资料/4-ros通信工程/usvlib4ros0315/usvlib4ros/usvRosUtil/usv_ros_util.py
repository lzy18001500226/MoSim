import time
import logging
import threading
import roslibpy
import traceback
import inspect

"""
ros环境下安装 ros-melodic-rosbridge-server (melodic是ros版本)
apt-get install ros-melodic-rosbridge-server

启动 roscore 和 rosbridge
roscore
roslaunch rosbridge_server rosbridge_websocket.launch

rosbridge 有 tcp，udp ，websocket 三种启动方式，默认端口 9090
roslibpy 仅支持与 rosbridge的websocket 连接

------------------------------------------------------------

在非ros环境下，安装roslibpy 
pip install roslibpy -i https://pypi.tuna.tsinghua.edu.cn/simple

"""

class LogUtil:

    @classmethod
    def info(cls, msg):
        frame = inspect.stack()[1]
        name = frame[1].rsplit('/', 1)[-1]
        lino = frame[2]
        print("%s(%s):%s" % (name, lino, msg))

    @classmethod
    def error(cls, msg):
        traceback.print_exc()
        print(msg)

    @classmethod
    def debug(cls, msg):
        frame = inspect.stack()[1]
        name = frame[1].rsplit('/', 1)[-1]
        lino = frame[2]
        print("%s(%s):%s" % (name, lino, msg))


class USVRosbridgeClient:
    Host = "192.168.3.35"
    Port = 9090
    ros = None

    @classmethod
    def initUSVRosBridgeConnection(cls, host, port):
        cls.Host = host
        cls.Port = port
        cls.ros = roslibpy.Ros(host=cls.Host, port=cls.Port)
        cls.ros.run()

    pass

    @classmethod
    def isRosConnected(cls):
        return cls.ros.is_connected

    """
    roslibpy use websocket connect rosbridge_server,default port 9090
    """
    def __init__(self):

        if USVRosbridgeClient.ros is None:
            USVRosbridgeClient.ros = roslibpy.Ros(host=USVRosbridgeClient.Host, port=USVRosbridgeClient.Port)
            USVRosbridgeClient.ros.run()

        self.ros = USVRosbridgeClient.ros
        self.topic = None
        self.service = None
        self.cond = threading.Condition()
        pass

    @classmethod
    def initRoslibpyLogger(cls):
        """初始化roslibpy日志模块"""
        logging.getLogger('twisted').setLevel(logging.ERROR)
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        logging.getLogger('twisted').addHandler(ch)

    def startPublicTopicThread(self, topicName, msgType=None, frequency=1, topicMsg=None):
        """
        :param topicName: 话题名 eg "/route","/auto/param"
        :param msgType : 消息类型名，
            在ros环境下 可使用 rosmsg list 查看可用类型名
            eg：
            std_msgs 类型 ："std_msgs/String" ， "std_msgs/Int8"
            自定义 msg ： "message_pkg/Manual"
        :param topicMsg:  消息内容
            类型：dict，字段可使用 rosmsg info msgName 查看
            eg：
            #rosmsg info std_msgs/String
            string data

            topicMsg = {'data':'some msg str'}
            eg:
            #rosmsg info message_pkg/Manual
            int8 handleOk
            int16 throttlePercent
            int16 rudderPercent

            topicMsg = {'handleOk':0,'throttlePercent':11,'rudderPercent':22}
        :return:
        """
        if topicName is None:
            raise Exception("topicName is None")
        if msgType is None:
            raise Exception("msgType is None")
        if topicMsg is None :
            raise Exception("topicMsg is None")

        th = threading.Thread(target=self.__publisher, args=(topicName, msgType, frequency, topicMsg))
        th.setDaemon(True)
        th.start()

    def __publisher(self,topicName=None,msgName=None,frequency=1,topicMsg=None):

        self.topic = roslibpy.Topic(self.ros, topicName, msgName)
        loopTime = 1.0 / frequency
        while self.ros.is_connected:
            # print(topicMsg)

            self.topic.publish(topicMsg)
            time.sleep(loopTime)

    def publisherOnce(self,topicName=None,msgName=None,topicMsg=None):
        if self.topic is None:
            self.topic = roslibpy.Topic(self.ros, topicName, msgName)
        self.topic.publish(topicMsg)

    def subscriber(self, topicName, msgType=None, callback=None):
        """
        no block
        :param topicName:   eg "/usv/001/scada/ctl/action/manual"
        :param msgType:     eg "message_pkg/Manual" , "std_msgs/String"
        :param callback: 接收到订阅消息后回调函数
        :return:
        """
        if topicName is None:
            raise Exception("topicName is None")
        if msgType is None:
            raise Exception("msgName is None")
        if callback is None:
            raise Exception("subscriber callback is None")

        self.topic = roslibpy.Topic(self.ros, topicName, msgType)
        self.topic.subscribe(callback=callback)
        pass

    def defaultSubscriberCallback(self,message):
        """
        :param message ： dict type； key是订阅消息类型的所有字段，value为对应字段值
        可在ros环境下 使用 rosmsg info msgType 查看订阅消息所包含的字段
         eg：
        #rosmsg info std_msgs/String
        string data

        message = {'data':'some msg str'}
        eg:
        #rosmsg info message_pkg/Manual
        int8 handleOk
        int16 throttlePercent
        int16 rudderPercent

        message = {'handleOk':0,'throttlePercent':11,'rudderPercent':22}
        """
        print("Recvived message type= %s : %s"%(type(message),message))

        pass

    def callService(self,serviceName=None,srvType=None,request=None,callback=None,errorCallback=None,timeout=0):
        """
        callback = None is Blocking mode else No-Blocking mode

        :param serviceName:
        :param srvType:
        :param request dict eg

        :param callback:
        :param errorCallback:
        :param timeout:
        :return:
        """

        self.service = roslibpy.Service(self.ros,serviceName,srvType)
        response = self.service.call(request,callback=callback,errback=errorCallback,timeout=timeout)

        if response is not None:
            #print("%s response is %s"%(serviceName,response))
            pass
        # self.service.unadvertise()
        return response

    def advertiseService(self,serviceName=None,srvType=None,callback=None):
        self.service = roslibpy.Service(self.ros, serviceName, srvType)
        self.service.advertise(callback)

    def get_param(self,param_name, default=None):
        try:
            self.ros.wait_for_service('/rosapi/get_param')
            param_value = self.ros.get_param(param_name)
            if param_value is None:
                param_value = default
        except Exception as e:
            param_value = default
        return  param_value

    pass




if __name__ == "__main__":

    USVRosbridgeClient.initRoslibpyLogger()

    """
    ros 基本消息类型
    std_msgs/msg/String.msg:
    string data
    """
    # usvRosPublisher = USVRosbridgeClient("192.168.3.35", 9090)
    # topicMsg = {"data":"hello msg ."}
    # usvRosPublisher.startPublicTopicThread(topicName="/SpaceRExample", msgType="std_msgs/String", topicMsg=topicMsg, frequency=50)

    """
    自定义消息文件
    message_pkg/msg/Manual.msg:
    int8 handleOk
    int16 throttlePercent
    int16 rudderPercent
    """
    # usvRosPublisher = USVRosbridgeClient("192.168.3.35", 9090)
    # manual = {'handleOk':0,'throttlePercent':11,'rudderPercent':22}
    # usvRosPublisher.startPublicTopicThread(topicName="/usv/001/scada/ctl/action/manual", msgType="message_pkg/Manual", topicMsg=manual, frequency=50)

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
    # usvRosPublisher = USVRosbridgeClient("192.168.3.35", 9090)
    # route = {'id': '1', 'name': 'route-test', 'version': 22,'points':[{'lng':128.4512,'lat':38.12451,'high':0,'cruiseSpeed':5.3}],'obstacles':[]}
    # usvRosPublisher.startPublicTopicThread(topicName="/route", msgType="message_pkg/Route",
    #                                        topicMsg=route, frequency=50)

    """订阅消息示例"""
    # usvRosSubscriber = USVRosbridgeClient("192.168.3.35", 9090)
    # usvRosSubscriber.subscriber(topicName="/route", msgType="message_pkg/Route", callback=usvRosSubscriber.defaultSubscriberCallback)
    #
    # usvRosSubscriber = USVRosbridgeClient("192.168.3.35", 9090)
    # usvRosSubscriber.subscriber(topicName="/SpaceRExample", msgType="std_msgs/String",
    #                             callback=usvRosSubscriber.defaultSubscriberCallback)

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