import json


class Parameter:

    def __init__(self,name='',dataType='int',defaultData=0):
        """
        :param name: str
        :param type: str in ['int','float','bool','str']
        :param defaultData: eg if type is 'int',defaultData can be : 1, [1] , or [1,2,3]
        """
        self.name = name
        self.type = dataType
        self.value = defaultData
        self.__isList = type(defaultData).__name__ == 'list'
        self.__valueStr = ''
        self.__msgDict = {'name':'','type':'','value':'[]'}
        pass

    def read(self, parameterDict):
        """
        poseDict eg: {'type':'int','name':'/auto/nav/param1','value':'[1]'}
        """
        self.msgDict = parameterDict

        self.type = parameterDict['type']
        self.name = parameterDict['name']
        self.__valueStr = parameterDict['value']
        value = json.loads(self.__valueStr)
        if self.__isList:
            self.value = value
        else:
            self.value = value[0]
        pass

    def write(self):
        if self.__isList:
            self.__msgDict['value'] = json.dumps(self.value)
        else:
            self.__msgDict['value'] = json.dumps([self.value])

        self.__msgDict['name'] = self.name
        self.__msgDict['type'] = self.type
        return self.__msgDict
        pass

