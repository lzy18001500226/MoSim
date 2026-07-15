# 四旋翼电机动力分配器
# https://zhuanlan.zhihu.com/p/91305836
import numpy as np

class Mixer:
    def __init__(self):
        self.Ct  = 3.25e-4    # 电机推力系数 (N/krpm^2) 注意结果单位为力(N)
        self.Cd  = 7.9379e-6  # 电机反扭系数 (Nm/krpm^2) 注意结果单位为扭矩(Nm)
        self.L   = 0.065/2.0   # 电机力臂长度 单位m
        self.max_thrust  = 0.1573 # 单个电机最大推力 单位N (电机最大转速22krpm)
        self.max_torque  = 3.842e-03 # 单个电机最大扭矩 单位Nm (电机最大转速22krpm)
        self.max_speed   = 22 # 电机最大转速(krpm)
        # 动力分配正向矩阵
        self.mat = np.array([
            [self.Ct, self.Ct, self.Ct, self.Ct],                                   # F total
            [self.Ct*self.L, -self.Ct*self.L, -self.Ct*self.L, self.Ct*self.L],     # Mx + - - +
            [-self.Ct*self.L, -self.Ct*self.L, self.Ct*self.L, self.Ct*self.L],     # My - - + +
            [-self.Cd, self.Cd, -self.Cd, self.Cd]                                  # Mz - + - +
        ])
        # 动力分配逆向矩阵
        self.inv_mat = np.linalg.inv(self.mat)

    # 动力分配
    # thrust: 机体总推力 单位N
    # mx, my, mz: 三轴扭矩 单位Nm
    def calculate(self, thrust, mx, my, mz):
        Mx, My = mx, my  # Copy
        Mz = 0 # 首先进行X Y轴分配
        control_input = np.array([thrust, Mx, My, Mz])
        motor_speed_squ = self.inv_mat @ control_input
        # X Y Z三轴动力分配的顺序决定最终取舍的不同
        # 一般情况下 首先对X Y轴动力进行分配 余量用于分配Z轴
        max_value = np.max(motor_speed_squ)
        min_value = np.min(motor_speed_squ)
        ref_value = np.sum(motor_speed_squ) / 4.0  # 参考转速(不施加扭矩时的转速平方)
        # print(f"ref_value:{ref_value}")
        max_trim_scale = 1.0
        min_trim_scale = 1.0
        if max_value > self.max_speed **2: # 存在电机动力饱和 计算缩放因子进行缩放
            # print(f"Max Overflow")
            max_trim_scale = (self.max_speed ** 2 - ref_value)/(max_value - ref_value)
        if min_value < 0: # 存在电机动力负饱和 计算缩放因子进行缩放
            # print(f"Min Overflow")
            min_trim_scale = (ref_value)/(ref_value - min_value)
        scale = min(max_trim_scale, min_trim_scale)
        # print(f"Trim Scale:{scale}")
        # 对X Y扭矩施加缩放因子
        Mx = Mx * scale
        My = My * scale
        # 重新计算电机转速平方
        control_input = np.array([thrust, Mx, My, Mz])
        motor_speed_squ = self.inv_mat @ control_input
        # print(f"motor_speed_squ:{motor_speed_squ}")
        # print(f"Original Torque: Mx:{Mx/scale:.6f} My:{My/scale:.6f} Trimed Torque: Mx:{Mx:.6f} My:{My:.6f}")
        if scale < 1.0: # 存在Trim 不进行Z轴扭矩分配 直接返回
            # 这里需要强行进行一下绝对值
            motor_speed_squ = np.abs(motor_speed_squ)
            return np.sqrt(motor_speed_squ)  # 返回电机转速
        else: # 仍然有余量 可以进行Z轴扭矩分配
            Mz = mz
            control_input_withz = np.array([thrust, Mx, My, Mz])  # 添加Z轴扭矩重新计算
            motor_speed_squ_withz = self.inv_mat @ control_input_withz
            # 判断是否饱和
            max_value = np.max(motor_speed_squ_withz)
            min_value = np.min(motor_speed_squ_withz)
            max_index = np.argmax(motor_speed_squ_withz)
            min_index = np.argmin(motor_speed_squ_withz)
            max_trim_scale_z = 1.0
            min_trim_scale_z = 1.0
            if max_value > self.max_speed **2: # 存在电机动力饱和 计算缩放因子进行缩放
                # print(f"Z Max Overflow")
                max_trim_scale_z = (self.max_speed ** 2 - motor_speed_squ[max_index])/(max_value - motor_speed_squ[max_index])
            if min_value < 0: # 存在电机动力负饱和 计算缩放因子进行缩放
                # print(f"Z Min Overflow")
                min_trim_scale_z = (motor_speed_squ[min_index])/(motor_speed_squ[min_index] - min_value)
            scale_z = min(max_trim_scale_z, min_trim_scale_z)
            # 对Z轴扭矩施加缩放因子
            Mz = Mz * scale_z
            # 重新计算电机转速平方
            control_input_withz = np.array([thrust, Mx, My, Mz])
            motor_speed_squ_withz = self.inv_mat @ control_input_withz
            # print(f"motor_speed_squ:{motor_speed_squ_withz}")
            # print(f"Original Torque: Mx:{Mx/scale:.6f} My:{My/scale:.6f} Mz:{Mz/scale_z:.6f} Trimed Torque: Mx:{Mx:.6f} My:{My:.6f} Mz:{Mz:.6f}")
            motor_speed_squ = np.abs(motor_speed_squ)
            return np.sqrt(motor_speed_squ_withz)  # 返回电机转速


if __name__ == '__main__':
    # 计算测试
    thrust = 0.1  # 总推力输出为0.4N
    Mx = 0.0
    My = 0.0
    Mz = 0.0

    mixer = Mixer()
    motor_speed = mixer.calculate(thrust, Mx, My, Mz)
    print(f"Motor Speed:{motor_speed}")
