# 电机转速计算测试
# 20250220 Test Failed
import numpy as np
from scipy.optimize import fsolve

# 电机推力系数 (N/krpm^2) 注意结果单位为力(N)
Ct = 3.25e-4
# 电机反扭系数 (Nm/krpm^2) 注意结果单位为扭矩(Nm)
Cd = 7.9379e-6
arm_length = 0.065/2.0 # 电机力臂长度 单位m
max_thrust = 0.1573 # 单个电机最大推力 单位N (电机最大转速22krpm)
max_torque = 3.842e-03 # 单个电机最大扭矩 单位Nm (电机最大转速22krpm)

# 定义等式
def equations(vars, thrust, mx, my, mz):
    global arm_length, Ct, Cd
    w1, w2, w3, w4 = vars  # 电机转速

    # Eq1 总推力方程
    eq1 = w1**2 + w2**2 + w3**2 + w4**2 - thrust / Ct
    # Eq2 X轴扭矩方程
    eq2 = -w1**2 -w2**2 + w3**2 + w4**2 - mx / (Ct*arm_length)
    # Eq3 Y轴扭矩方程
    eq3 = -w1**2 + w2**2 + w3**2 - w4**2 - my / (Ct*arm_length)
    # Eq4 Z轴扭矩方程
    eq4 = -w1**2 + w2**2 - w3**2 + w4**2 - mz / Cd

    return [eq1, eq2, eq3, eq4]

# 求解电机动力分配
initial_guess = [1.0, 1.0, 1.0, 1.0]  # 初始猜测
thrust, mx, my, mz = 0.4, 0.0, 0.0, 0.1  # 输入参数测试

# 使用 fsolve 求解方程组
solution = fsolve(equations, initial_guess, args=(thrust, mx, my, mz))

# 输出各电机的转速
n1, n2, n3, n4 = solution
print(f"电机1的转速: {n1} RPM")
print(f"电机2的转速: {n2} RPM")
print(f"电机3的转速: {n3} RPM")
print(f"电机4的转速: {n4} RPM")
