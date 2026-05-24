

class VehicleHighPercentCommand():

    def __init__(self) :
        self.valid = False
        self.reversed = False #
        self.throttlePercent = 0
        self.rudderPercent = 0
        self.__msgDict = {'valid':False,'reversed':False,'throttlePercent':0,'rudderPercent':0}
        pass

    def updateCommand(self,valid,throttlePercent,rudderPercent,reversed=False):
        self.valid = valid
        self.throttlePercent = int(throttlePercent)
        self.rudderPercent = int(rudderPercent)
        self.reversed = reversed
        self.write()
        pass

    def write(self):
        self.__msgDict['valid'] = self.valid
        self.__msgDict['throttlePercent'] = self.throttlePercent
        self.__msgDict['rudderPercent'] = self.rudderPercent
        self.__msgDict['reversed'] = self.reversed
        return self.__msgDict


class VehicleLowCommand():

    def __init__(self) :
        self.valid = False
        self.updateTime = 0.0
        self.throttlePercent = 0
        self.rudderPercent = 0
        self.__msgDict = {'valid':False,'reversed':False,'throttlePercent':0,'rudderPercent':0}
        pass

    def updateCommand(self,valid,throttlePercent,rudderPercent,reversed=False):
        self.valid = valid
        self.throttlePercent = int(throttlePercent)
        self.rudderPercent = int(rudderPercent)
        self.reversed = reversed
        self.write()
        pass

    def write(self):
        self.__msgDict['valid'] = self.valid
        self.__msgDict['throttlePercent'] = self.throttlePercent
        self.__msgDict['rudderPercent'] = self.rudderPercent
        self.__msgDict['reversed'] = self.reversed
        return self.__msgDict
