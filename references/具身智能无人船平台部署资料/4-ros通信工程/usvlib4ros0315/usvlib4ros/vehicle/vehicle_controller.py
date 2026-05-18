
from usvlib4ros import USVRosbridgeClient,RosTopicProxy,DictToObject,Constants,LogUtil
import threading
import time


class VehicleController:

    def __init__(self):
        self.mode = 0
        self.vehicleCtrlMode = Constants.VehicleCtrl.Low_High_Mode
        self.vehicleLowHighMode = 1

        self.action = DictToObject(**{"throttlePercent":0,"rudderPercent":0})
        self.battery = None
        self.ctlStatus = None

        self.cruiseStatus =  DictToObject(**{"mode":0,"cruiseSpeed":0,"cruiseHeading":0}) #巡航状态

        self.cmdPublisher = USVRosbridgeClient()
        self.pidPublisher = USVRosbridgeClient()
        self.heartPublisher = USVRosbridgeClient()
        self.lightPublisher = USVRosbridgeClient()
        pass

    def startService(self):

        actionSubscriber = USVRosbridgeClient()
        actionSubscriber.subscriber(topicName="/usv/001/ctl/scada/action",
                                    msgType="message_pkg/Action",
                                    callback=self.__actionListener)

        cruiseStatusSubscriber = USVRosbridgeClient()
        cruiseStatusSubscriber.subscriber(topicName="/usv/001/ctl/scada/cruise/status",
                                    msgType="message_pkg/CruiseStatus",
                                    callback=self.__cruiseStatusListener)

        batterySubscriber = USVRosbridgeClient()
        batterySubscriber.subscriber(topicName="/usv/001/battery",
                                    msgType="vehicle_msgs_pkg/BatteryStatus",
                                    callback=self.__batteryListener)
        #
        ctlStatusSubscriber = USVRosbridgeClient()
        ctlStatusSubscriber.subscriber(topicName="/usv/001/ctlStatus",
                                     msgType="vehicle_msgs_pkg/VehicleStatus",
                                     callback=self.__ctlStatusListener)

        # self.heartPublisher.startPublicTopicThread(topicName="/usv/001/scada/action/heart",msgType="vehicle_msgs_pkg/Heart",)
        # self.__cruiseCmdPublisherOnce()

        th1 = threading.Thread(target=self.heart)
        th1.setDaemon(True)
        th1.start()

        th = threading.Thread(target=self.run)
        th.setDaemon(True)
        th.start()
        pass

    """
    
    
    """

    def heart(self):
        msg = {'time':time.time()}
        while True:
            try:
                msg = {'time': time.time()}
                self.heartPublisher.publisherOnce("/usv/001/scada/action/heart","vehicle_msgs_pkg/Heart",msg)
            except Exception as e:
                LogUtil.error(e)
                pass
            finally:

                time.sleep(0.1)

    def run(self):
        while True:
            try:
                start = time.time()
                now = start
                speed = 0
                heading = 0
                light = 0
                while True:
                    # speed = speed + 1 #1000 #1000# int(self.maxSpeed * self.action.throttlePercent)    #速度：2byte，速度（m/s）x 100。
                    # if speed > 2000:
                    mode = 4
                    speed = 0
                    heading = 0
                    tmp = (int)(time.time() - start)
                    # light = light+1
                    if tmp < 10:
                        light = 0
                        mode = 0
                    else:
                        mode = 0
                        light = 0
                        # if self.ctlStatus is not None and self.ctlStatus.controlMode == 0:
                        #船遥控器模式
                        # mode = 5
                        speed = 0
                        heading = 0

                    # 0:低层，1:高层，2:定速，3:定向，4:定速定向，5:遥控器控制

                    self.cmdPublisher.publisherOnce("/usv/001/scada/action/cmd","vehicle_msgs_pkg/CruiseCmd",{"mode":mode,"speed":speed,"heading":heading})
                    self.lightPublisher.publisherOnce("/usv/001/light","vehicle_msgs_pkg/Light",{"switch":light})
                    #
                    # self.sensorPublisher.publisherOnce("/usv/001/sensor","vehicle_msgs_pkg/SensorInfo",self.sensorInfo)
                    self.pidPublisher.publisherOnce("/usv/001/pid", "vehicle_msgs_pkg/Pid",
                                                    {"Kp": 2.0, "Ki": 0, "Kd": 0.5})

                    tmp = time.time() - now;
                    now = time.time()
                    print("time %s , speed %s "%(tmp,speed))
                    time.sleep(0.1)
                    pass
            except Exception as e:
                LogUtil.error(e)
            finally:
                time.sleep(1)
        pass

    def __actionListener(self,actionMsgDict):
        """

        Action.msg:
        int16
        throttlePercent
        int16
        rudderPercent.
        """
        self.action = DictToObject(**actionMsgDict)

    def __ctlStatusListener(self, ctlStatusMsgDict):
        """

        Action.msg:
        int16
        throttlePercent
        int16
        rudderPercent.
        """
        self.ctlStatus = DictToObject(**ctlStatusMsgDict)

    def __batteryListener(self,batteryMsgDict):
        """

        Action.msg:
        int16
        throttlePercent
        int16
        rudderPercent.
        """
        self.battery = DictToObject(**batteryMsgDict)

    def __cruiseStatusListener(self,cruiseStatusMsgDict):
        print(cruiseStatusMsgDict)
        cruiseStatus = DictToObject(**cruiseStatusMsgDict)
        # if cruiseStatus.mode > 0 :
        #     cruiseStatus.mode = cruiseStatus.mode + 1
        # else:
        #     cruiseStatus.mode = self.vehicleLowHighMode

        # if cruiseStatus.mode != self.cruiseStatus.mode:
        self.cruiseStatus = cruiseStatus
        # self.__cruiseCmdPublisherOnce()
        """"""

    def __cruiseCmdPublisherOnce(self):
        """"""
        """
        cruise ctl
        """
        mode = self.cruiseStatus.mode
        speed = self.cruiseStatus.cruiseSpeed
        heading = self.cruiseStatus.cruiseHeading
        self.cruisePublisher.publisherOnce("/usv/001/scada/action/auto", "vehicle_msgs_pkg/CruiseCmd",
                                        {"mode": mode,"speed": speed,"heading":heading})
    pass

if __name__=="__main__":
    Host = "192.168.144.119"
    USVRosbridgeClient.Host = "192.168.144.119"
    USVRosbridgeClient.Host = Host

    vehicle = VehicleController()
    vehicle.startService()

    cruisePub = USVRosbridgeClient()
    manualPub = USVRosbridgeClient()

    cruise = {"mode":0,"cruiseSpeed":0.5,"cruiseHeading":100} #mode 模式，0，1，2，3，4。cruiseSpeed；m/s。cruiseHeading： °
    manual = {'handleOk':1,'throttlePercent':10,'rudderPercent':10} #左右电机百分比[-100，100]

    while True:
        now = time.time()

        # estmatesValue = headingsIMU
        # datasMeasured = [headingsGPS, headingsIMU, headingsCompass]
        # datasEstmate = [estmatesValue, estmatesValue, estmatesValue]

        # cruise['mode'] = cruise['mode'] + 1
        # if cruise['mode'] >= 5:
        #     cruise['mode'] = 0
        # cruise['mode'] = 2
        # cruise['cruiseSpeed'] = 0.1
        # cruise['cruiseHeading'] = 9
        # cruisePub.publisherOnce(topicName="/usv/001/ctl/scada/cruise/status",
        #                             msgName="message_pkg/CruiseStatus",topicMsg=cruise)
        # request = cruise
        # cruisePub.callService("/usv/001/server/setCruise","message_pkg/SetCruise",request)

        time.sleep(0.1)
