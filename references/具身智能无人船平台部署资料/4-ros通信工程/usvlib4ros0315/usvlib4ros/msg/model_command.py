

class ModelCommand:

    def __init__(self):
        self.adviseThrottlePercent = 0.0    #建议油门百分比【-100~100】
        self.adviseRudderPercent = 0.0      #建议方向百分比【-100~100】
        self.realSpeedX = 0.0 #扰动速度z
        self.realSpeedY = 0.0 #扰动速度y
        self.realSpeedZ = 0.0 #扰动速度x

    def read(self, modelCommandDict):
        """
        float64 adviseThrottlePercent           --建议油门百分比【-100~100】
        float64 adviseRudderPercent             --建议方向百分比【-100~100】
        float64 realSpeedX                      --扰动速度x
        float64 realSpeedY                      --扰动速度y
        float64 realSpeedZ                      --扰动速度z
        """
        self.adviseThrottlePercent = modelCommandDict['adviseThrottlePercent']
        self.adviseRudderPercent = modelCommandDict['adviseRudderPercent']
        self.realSpeedX = modelCommandDict['realSpeedX']
        self.realSpeedY = modelCommandDict['realSpeedY']
        self.realSpeedZ = modelCommandDict['realSpeedZ']


class ModelReply:

    Instance = None

    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls.Instance is None:
            cls.Instance = super(ModelReply, cls).__new__(cls)
        return cls.Instance

    def __init__(self):
        self.finalSpeedX = 0.0      #前进速度
        self.finalSpeedY = 0.0      #横向速度
        self.finalYaw = 0.0         #转向角速度
        self.modelParams = []           #模型参数
        self.__msgDict = {'finalSpeedX':0.0,'finalSpeedY':0.0,'finalYaw':0.0,'modelParams':[]}

    def read(self, modelCommandDict):
        """"""

        self.finalSpeedX = modelCommandDict['finalSpeedX']
        self.finalSpeedY = modelCommandDict['finalSpeedY']
        self.finalYaw = modelCommandDict['finalYaw']
        self.modelParams = modelCommandDict['modelParams']

    def update(self,finalSpeedX,finalSpeedY,finalYaw,modelParams):
        """
        float64 finalSpeedX                      --前进速度
        float64 finalSpeedY                      --横向速度
        float64 finalYaw                         --转向角速度
        float64[] modelParams                         --模型参数
        """
        self.finalSpeedX = finalSpeedX
        self.finalSpeedY = finalSpeedY
        self.finalYaw = finalYaw
        self.modelParams = modelParams
        self.write()
        return self.__msgDict

    def write(self):
        """
        float64 finalSpeedX                      --前进速度
        float64 finalSpeedY                      --横向速度
        float64 finalYaw                         --转向角速度
        float64[] params                         --模型参数
        """
        self.__msgDict['finalSpeedX'] = self.finalSpeedX
        self.__msgDict['finalSpeedY'] = self.finalSpeedY
        self.__msgDict['finalYaw'] = self.finalYaw
        self.__msgDict['modelParams'] = self.modelParams
        return self.__msgDict


