# 20250220 Wakkk
# Quadrotor SE3 Control Demo
import mujoco
import mujoco.viewer as viewer
import numpy as np
from se3_controller import *
from motor_mixer import *

gravity = 9.8066        # 重力加速度 单位m/s^2
mass = 0.033            # 飞行器质量 单位kg
Ct = 3.25e-4            # 电机推力系数 (N/krpm^2)
Cd = 7.9379e-6          # 电机反扭系数 (Nm/krpm^2)

arm_length = 0.065/2.0  # 电机力臂长度 单位m
max_thrust = 0.1573     # 单个电机最大推力 单位N (电机最大转速22krpm)
max_torque = 3.842e-03  # 单个电机最大扭矩 单位Nm (电机最大转速22krpm)

# 仿真周期 1000Hz 1ms 0.001s
dt = 0.001

# 根据电机转速计算电机推力
def calc_motor_force(krpm):
    global Ct
    return Ct * krpm**2

# 根据推力计算电机转速
def calc_motor_speed_by_force(force):
    global max_thrust
    if force > max_thrust:
        force = max_thrust
    elif force < 0:
        force = 0
    return np.sqrt(force / Ct)

# 根据扭矩计算电机转速 注意返回数值为转速绝对值 根据实际情况决定转速是增加还是减少
def calc_motor_speed_by_torque(torque):
    global max_torque
    if torque > max_torque:  # 扭矩绝对值限制
        torque = max_torque
    return np.sqrt(torque / Cd)

# 根据电机转速计算电机转速
def calc_motor_speed(force):
    if force > 0:
        return calc_motor_speed_by_force(force)

# 根据电机转速计算电机扭矩
def calc_motor_torque(krpm):
    global Cd
    return Cd * krpm**2

# 根据电机转速计算电机归一化输入
def calc_motor_input(krpm):
    if krpm > 22:
        krpm = 22
    elif krpm < 0:
        krpm = 0
    _force = calc_motor_force(krpm)
    _input = _force / max_thrust
    if _input > 1:
        _input = 1
    elif _input < 0:
        _input = 0
    return _input

# 加载模型回调函数
def load_callback(m=None, d=None):
    mujoco.set_mjcb_control(None)
    m = mujoco.MjModel.from_xml_path('./crazyfile/scene.xml')
    d = mujoco.MjData(m)
    if m is not None:
        mujoco.set_mjcb_control(lambda m, d: control_callback(m, d))  # 设置控制回调函数
    return m, d

# 简易平面圆形轨迹生成
def simple_trajectory(time):
    wait_time = 1.5     # 起飞到开始点等待时间
    height = 0.3        # 绕圈高度
    radius = 0.5        # 绕圈半径
    speed = 0.3         # 绕圈速度
    # 构建机头朝向
    _cos = np.cos(2*np.pi*speed*(time-wait_time))
    _sin = np.sin(2*np.pi*speed*(time-wait_time))
    _heading = np.array([-_sin, _cos, 0])
    # 首先等待起飞到目标开始点位
    if time < wait_time:
        return np.array([radius, 0, height]), np.array([0.0, 1.0, 0.0])  # Start Point
    # 随后开始绕圈(逆时针旋转)
    _x = radius * _cos
    _y = radius * _sin
    _z = height
    return np.array([_x, _y, _z]), _heading  # Trajectory Point And Heading

# 初始化SE3控制器
ctrl = SE3Controller()
# 设置参数
ctrl.kx = 0.6
ctrl.kv = 0.4
ctrl.kR = 6.0
ctrl.kw = 1.0
# 初始化电机动力分配器
mixer = Mixer()
torque_scale = 0.001 # 控制器控制量到实际扭矩(Nm)的缩放系数(因为是无模型控制所以需要此系数)

log_count = 0
def control_callback(m, d):
    global log_count, gravity, mass, dt

    _pos = d.qpos
    _vel = d.qvel
    _acc = d.qacc

    _sensor_data = d.sensordata
    gyro_x = _sensor_data[0]
    gyro_y = _sensor_data[1]
    gyro_z = _sensor_data[2]
    acc_x = _sensor_data[3]
    acc_y = _sensor_data[4]
    acc_z = _sensor_data[5]
    quat_w = _sensor_data[6]
    quat_x = _sensor_data[7]
    quat_y = _sensor_data[8]
    quat_z = _sensor_data[9]
    quat = np.array([quat_x, quat_y, quat_z, quat_w])  # x y z w
    omega = np.array([gyro_x, gyro_y, gyro_z])  # 角速度

    # 构建目标状态
    # goal_pos, goal_heading = simple_trajectory(d.time)        # 目标位置
    goal_pos, goal_heading = np.array([0.0, 0.0, 0.3]), np.array([1.0, 0.0, 0.0])  # 目标位置

    goal_vel = np.array([0, 0, 0])              # 目标速度
    goal_quat = np.array([0.0,0.0,0.0,1.0])     # 目标四元数(无用)
    goal_omega = np.array([0, 0, 0])            # 目标角速度
    goal_state = State(goal_pos, goal_vel, goal_quat, goal_omega)
    # 构建当前状态
    curr_state = State(_pos, _vel, quat, omega)

    # 更新控制器
    # forward = np.array([1.0, 0.0, 0.0])  # 前向方向
    forward = goal_heading
    control_command = ctrl.control_update(curr_state, goal_state, dt, forward)
    ctrl_thrust = control_command.thrust    # 总推力控制量(mg为单位)
    ctrl_torque = control_command.angular   # 三轴扭矩控制量

    # Mixer
    mixer_thrust = ctrl_thrust * gravity * mass     # 机体总推力(N)
    mixer_torque = ctrl_torque * torque_scale       # 机体扭矩(Nm)
    # 输出到电机
    motor_speed = mixer.calculate(mixer_thrust, mixer_torque[0], mixer_torque[1], mixer_torque[2]) # 动力分配
    d.actuator('motor1').ctrl[0] = calc_motor_input(motor_speed[0])
    d.actuator('motor2').ctrl[0] = calc_motor_input(motor_speed[1])
    d.actuator('motor3').ctrl[0] = calc_motor_input(motor_speed[2])
    d.actuator('motor4').ctrl[0] = calc_motor_input(motor_speed[3])

    log_count += 1
    if log_count >= 500:
        log_count = 0
        # 这里输出log
        # print(f"Control Linear: X:{ctrl_linear[0]:.2f} Y:{ctrl_linear[1]:.2f} Z:{ctrl_linear[2]:.2f}")
        # print(f"Quat: x:{quat[0]:.2f} y:{quat[1]:.2f} z:{quat[2]:.2f} w:{quat[3]:.2f}")
        # print(f"Control Angular: X:{ctrl_torque[0]:.2f} Y:{ctrl_torque[1]:.2f} Z:{ctrl_torque[2]:.2f}")
        # print(f"Control Thrust: {ctrl_thrust:.4f}")
        # print(f"Position: X:{_pos[0]:.2f} Y:{_pos[1]:.2f} Z:{_pos[2]:.2f}")
        # radius = np.linalg.norm(_pos[:2])
        # print(f"Radius: {radius:.2f}")


if __name__ == '__main__':
    viewer.launch(loader=load_callback)
