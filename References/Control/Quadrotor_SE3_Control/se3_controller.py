# SE3 控制器
# 20250220 Wakkk
import numpy as np
import geometry

class State:
    # 四元数顺序 x y z w
    def __init__(self, pos, vel, quat, omega):
        self.position = pos     # x y z
        self.velocity = vel     # x y z
        self.quaternion = quat  # x y z w
        self.omega = omega      # x y z

    def update(self, pos, vel, quat, omega):
        self.position = pos
        self.velocity = vel
        self.quaternion = quat
        self.omega = omega

class Control_Command:
    # thrust: 总推力
    # wx wy wz三轴扭矩
    def __init__(self, thrust, wx, wy, wz):
        self.thrust = thrust
        self.angular = np.array([wx, wy, wz])

class SE3Controller:
    def __init__(self):
        self.goal_state: State = None
        self.current_state: State = None
        self.kx = 0.0  # 位置控制反馈系数
        self.kv = 0.0  # 速度控制反馈系数
        self.kR = 0.0  # SO3控制反馈系数
        self.kw = 0.0 # 角速度控制反馈系数
        self.gravity = np.array([0.0, 0.0, -1.0])  # 重力加速度矢量方向

    def set_current_state(self, state: State):
        self.current_state = state

    def set_goal_state(self, state: State):
        self.goal_state = state

    # 计算线性误差
    def update_linear_error(self):
        if self.goal_state is None or self.current_state is None:
            print("Error: goal or current state is None")
            return
        # Errors
        e_x = np.zeros(3)   # 位置误差
        e_v = np.zeros(3)   # 速度误差
        # Position Error
        e_x[0] = self.current_state.position[0] - self.goal_state.position[0]
        e_x[1] = self.current_state.position[1] - self.goal_state.position[1]
        e_x[2] = self.current_state.position[2] - self.goal_state.position[2]
        # ex_norm = np.linalg.norm(e_x)
        # if ex_norm > self.ex_norm_max:
        #     e_x = e_x / ex_norm * self.ex_norm_max  # 限制误差大小
        # Velocity Error
        e_v[0] = self.current_state.velocity[0] - self.goal_state.velocity[0]
        e_v[1] = self.current_state.velocity[1] - self.goal_state.velocity[1]
        e_v[2] = self.current_state.velocity[2] - self.goal_state.velocity[2]
        return e_x, e_v

    # 计算SO3误差
    # trans_control: 位移控制量 forward: 目标机头Yaw朝向(向量)
    def update_angular_error(self, trans_control, forward):
        if self.goal_state is None or self.current_state is None:
            print("Error: goal or current state is None")
            return
        e_R = np.zeros(3)   # 姿态误差
        e_w = np.zeros(3)   # 角速度误差
        q_curr = geometry.GeoQuaternion(self.current_state.quaternion[0],
                                     self.current_state.quaternion[1],
                                     self.current_state.quaternion[2],
                                     self.current_state.quaternion[3])
        R_curr = q_curr.getRotationMatrix()  # 计算当前旋转矩阵
        # 根据线性位移控制量计算目标机体推力方向(Z轴指向)
        goal_z = trans_control - self.gravity
        goal_z_norm = np.linalg.norm(goal_z)
        if goal_z_norm > 1e-6:
            goal_z /= goal_z_norm  # Z轴指向单位化
        else:
            goal_z = R_curr[:, 2]  # 保持当前机体z轴朝向

        up = goal_z
        right_des = np.cross(forward, up)  # 根据当前z轴和目标朝向计算机体右侧朝向
        right_des /= np.linalg.norm(right_des)  # 归一化确保数值精度
        proj_fwd_des = np.cross(up, right_des)  # 重新计算目标朝向

        R_goal = np.zeros((3, 3))  # 构建目标旋转矩阵
        R_goal[:, 0] = right_des   # X轴为机体右侧朝向
        R_goal[:, 1] = proj_fwd_des  # Y轴为目标朝向
        R_goal[:, 2] = up          # Z轴为向上方向

        thrust = goal_z_norm  # 目标推力大小(g为单位)

        # 使用目标姿态四元数作为目标姿态
        # q_goal = geometry.GeoQuaternion(self.goal_state.quaternion[0],
        #                             self.goal_state.quaternion[1],
        #                             self.goal_state.quaternion[2],
        #                             self.goal_state.quaternion[3])
        # R_goal = q_goal.getRotationMatrix()  # 计算目标旋转矩阵

        # vee 求解so3误差
        e_R = 0.5 * geometry.veemap(np.dot(R_goal.T, R_curr) -
                                    np.dot(R_curr.T, R_goal))
        # Angular velocity
        w_curr = np.zeros(3)
        w_des = np.zeros(3)

        w_curr = self.current_state.omega
        w_des = self.goal_state.omega

        # 计算角速度误差
        e_w = np.zeros(3)
        e_w = w_curr - np.dot(R_curr.T, np.dot(R_goal, w_des))
        return e_R, e_w, thrust

    # 控制更新函数(外部调用)
    # 关于目标姿态: 若forward为None, 则使用目标姿态四元数作为目标姿态, 否则使用forward作为目标机头朝向作为目标姿态
    def control_update(self, current_state: State, goal_state: State, dt, forward):
        self.current_state = current_state
        self.goal_state = goal_state
        e_x, e_v = self.update_linear_error()
        # 位置速度控制(线性控制)
        x = -self.kx * e_x[0] - self.kv * e_v[0] + self.goal_state.velocity[0]
        y = -self.kx * e_x[1] - self.kv * e_v[1] + self.goal_state.velocity[1]
        z = -self.kx * e_x[2] - self.kv * e_v[2] + self.goal_state.velocity[2]
        trans_control = np.array([x, y, z])  # 位移线性控制量
        e_R, e_w, thrust = self.update_angular_error(trans_control, forward)
        # 姿态控制(角速度控制)
        # self.kw * e_w[0] 表示要使得在目标系中有预期的角速度的在当前坐标系中的误差 算是一种前馈补偿
        # self.goal_state.omega[0] 表示当前坐标系中的目标角速度
        wx = -self.kR * e_R[0] - self.kw * e_w[0] + self.goal_state.omega[0]
        wy = -self.kR * e_R[1] - self.kw * e_w[1] + self.goal_state.omega[1]
        wz = -self.kR * e_R[2] - self.kw * e_w[2] + self.goal_state.omega[2]
        control_command = Control_Command(thrust, wx, wy, wz)
        return control_command
