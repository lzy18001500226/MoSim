

class Constants:
    """usv constant"""
    Failed = 0
    Success = 1

    class WorkMode:
        """任务模式"""
        AutoReturn = -1
        Ready = 0
        Mannual = 1
        Auto = 2
        pass

    class PoseMode:
        """定位方式"""
        UintyPose = 2   #仿真unity定位
        gpsPose = 1     #实际GPS设备定位

    class VehicleCtrl:
        """航行器控制模式"""
        Low_High_Mode = 0       #底层模式或高层指令模式
        Speed_Mode = 1          #定速模式
        Heading_Mode = 2        #定向模式
        Speed_Heading_Mode = 3  #定速定向模式

        Max_Speed = 2.0         #最大行驶速度设置，m/s
        Max_Yaw_Speed = 30      #最大转向角速度设置, °/s






