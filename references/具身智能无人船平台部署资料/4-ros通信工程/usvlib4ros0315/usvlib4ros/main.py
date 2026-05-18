# This is a sample Python script.

# Press Alt+Shift+X to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import time
import sys
import os

# 获取当前目录
current_directory = os.getcwd()
print(current_directory)
# 将当前目录添加到 sys.path
if current_directory not in sys.path:
    sys.path.append(current_directory)

from usvlib4ros import LogUtil,USVRosbridgeClient,RosSrvClientProxy,RosTopicProxy
from usvlib4ros import GlobalData
from usvlib4ros import USVAutoNavigationService


class USVNavMain:

    local_run = 0

    @classmethod
    def start(cls,host,port):
        if cls.local_run == 0 :
            cls.local_run = 1
            USVRosbridgeClient.initRoslibpyLogger()
            GlobalData.Instance = GlobalData().getInstance()
            USVRosbridgeClient.initUSVRosBridgeConnection(host,port)
            RosTopicProxy.startService()
            USVAutoNavigationService.startService()
        pass
    pass


def start_usv_nav():
    USVNavMain.start("121.41.106.238",8236)
    autoStatus = GlobalData.getInstance().autoStatus
    return autoStatus.adviseThrottle,autoStatus.adviseRudder


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # USVNavMain.start("121.41.106.238",8236)
    USVNavMain.start("192.168.3.35", 9090)
    while True:
        time.sleep(1)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
