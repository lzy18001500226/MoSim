
from globalData import GlobalData
class Calc():
    def __init__(self, path):
        GlobalData.initialize(path)
        self.gdUtil = GlobalData().get_rosbagUtil()
        pass

    def getData(self,topic,field):
        datas = self.gdUtil.getTopicMsgFieldList(topic,field)
        list_param_r1 = []
        list_param_r2 = []
        for data in datas:
            import time
            timeArray = time.localtime(data[0] / 1000000000) 
            otherStyleTime = time.strftime("%H:%M:%S", timeArray)
            list_param_r1.append(otherStyleTime)
            list_param_r2.append(data[1])
        GlobalData.set_timestamp(list_param_r1)
        return list_param_r1, list_param_r2