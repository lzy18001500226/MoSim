import json
import time

from usvlib4ros.usvRosUtil import USVRosbridgeClient,LogUtil
from usvlib4ros.msg import Route


class RosSrvClientProxy:

    Host = "192.168.3.35"
    Port = 9090
    deviceId = "001"

    @classmethod
    def setDeviceId(cls,deviceId = "001"):
        cls.deviceId = deviceId

    @classmethod
    def resetParameterList(cls):
        """
        InitParameterOptimization.srv:
        ---
        int8 result
        """
        usvRosSrvClient = USVRosbridgeClient()
        request = {}
        response = usvRosSrvClient.callService("/usv/%s/srv/ctl/parameter/init"%(cls.deviceId), "message_pkg/InitParameterOptimization", request)
        return response['result'] == 1

    @classmethod
    def typeCheck(cls,value,registerType):
        arrayValue = value
        sameType = True
        if type(value).__name__ != 'list' and  type(value).__name__ != 'tuple':
            arrayValue = [value]

        for data in arrayValue :
            dataType = type(data).__name__
            if dataType != registerType:
                if registerType == 'str' and dataType == 'unicode':
                    continue
                elif registerType == 'float' and dataType == 'int':
                    continue
                else:
                    sameType = False
                    break
            pass
        pass
        return sameType


    @classmethod
    def registAdjustParameter(cls,name,valueType,defaultValue):
        """
        :param name: str,eg "/usv/auto/nav/param/maxSpeed"
        :param defaultValue: valyeType类型的默认值 或 valueType类型的数组或元组
        :param valueType: str in ['int','str','bool','float']

        eg:
        registAdjustParameter("/usv/status","int",1)
        registAdjustParameter("/usv/status","int",[1])
        registAdjustParameter("/usv/status","int",[1,2])
        registAdjustParameter("/usv/status","int",(1,2))
        :return:
        """

        if valueType not in ['int','bool','str','float']:
            raise Exception("valueType %s not in ['int','bool','str','float'] "%(valueType))

        if type(name).__name__ != 'str':
            raise Exception("Name error . %s is not str."%(name))

        if type(defaultValue).__name__ != 'list' and  type(defaultValue).__name__ != 'tuple':
            defaultValue = [defaultValue]

        typeOk = cls.typeCheck(value=defaultValue,registerType=valueType)
        if typeOk is False:
            raise Exception("Defaultvalue %s is not instance of %s ." % (defaultValue,valueType))

        """
        Parameter.msg:
        string type
        string name
        string value

        RegisterParameter.srv
        Parameter parameter
        ---
        int8 result
        string errorMsg
        """
        value = json.dumps(defaultValue)
        parameter = {"name":name,"type":valueType,"value":value}

        usvRosSrvClient = USVRosbridgeClient()
        request = {"parameter":parameter}
        response = usvRosSrvClient.callService("/usv/%s/srv/ctl/parameter/register"%(cls.deviceId),
                                               "message_pkg/RegisterParameter", request)
        if response['result'] != 1:
            LogUtil.error(response['errorMsg'])

        return response['result'] == 1,parameter
        pass

    @classmethod
    def registParameter(cls, parameter):
        """
        :param parameter: msg.Parameter type
        :return:
        """
        """
        Parameter.msg:
        string type
        string name
        string value

        RegisterParameter.srv
        Parameter parameter
        ---
        int8 result
        string errorMsg
        """
        parameterDict = parameter.write()

        usvRosSrvClient = USVRosbridgeClient()
        request = {"parameter": parameterDict}
        response = usvRosSrvClient.callService("/usv/%s/srv/ctl/parameter/register"%(cls.deviceId),
                                               "message_pkg/RegisterParameter", request)
        if response['result'] != 1:
            LogUtil.error(response['errorMsg'])

        return response['result'] == 1
        pass

    @classmethod
    def registMonitorParameter(cls, parameter):
        """
        :param parameter: msg.Parameter type
        :return:
        """
        """
        Parameter.msg:
        string type
        string name
        string value

        RegisterParameter.srv
        Parameter parameter
        ---
        int8 result
        string errorMsg
        """
        parameterDict = parameter.write()

        usvRosSrvClient = USVRosbridgeClient()
        request = {"parameter": parameterDict}
        response = usvRosSrvClient.callService("/usv/%s/srv/ctl/parameter/register/monitor"%(cls.deviceId),
                                               "message_pkg/RegisterParameter", request)

        
        if response['result'] != 1:
            LogUtil.error(response['errorMsg'])

        return response['result'] == 1
        pass

    @classmethod
    def adjustParameter(cls,parameter):
        """
        :param parameter: dict or msg.Parameter
        """
        """
        Parameter.msg:
        string type
        string name
        string value

        RegisterParameter.srv
        Parameter parameter
        ---
        int8 result
        string errorMsg
        """
        parmeterDict = parameter
        if type(parameter).__name__ == 'dict':
            parmeterDict = parameter
        elif type(parameter).__name__ == 'Parameter':
            parmeterDict = parameter.write()

        usvRosSrvClient = USVRosbridgeClient()
        request = {"parameter":parmeterDict}
        response = usvRosSrvClient.callService("/usv/%s/srv/ctl/parameter/register"%(cls.deviceId),
                                               "message_pkg/RegisterParameter", request)
        if response['result'] != 1:
            LogUtil.error(response['errorMsg'])

        return response['result'] == 1
        pass

    @classmethod
    def getRoute(cls):
        usvRosSrvClient = USVRosbridgeClient()
        request = {}
        response = usvRosSrvClient.callService("/usv/%s/server/getRoute"%(cls.deviceId), "message_pkg/getRoute", request)
        routeDict = response['route']
        route = Route()
        route.read(routeDict=routeDict)
        return route
        pass

if __name__ == "__main__":

    USVRosbridgeClient.initRoslibpyLogger()

    # RosSrvClientProxy.resetParameterList()
    paramArray = []
    result , param1 = RosSrvClientProxy.registAdjustParameter(name="/usv/param1",valueType="int",defaultValue=1)
    if result is True:
        paramArray.append(param1)
    result , param2 = RosSrvClientProxy.registAdjustParameter(name="/usv/param2", valueType="int", defaultValue=(2))
    if result is True:
        paramArray.append(param2)
    result , param3 = RosSrvClientProxy.registAdjustParameter(name="/usv/param3", valueType="int", defaultValue=[3])
    if result is True:
        paramArray.append(param3)




    while True:
        time.sleep(1)
    pass