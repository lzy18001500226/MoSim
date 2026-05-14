#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy 
from sunray_msgs.msg import UAVState, UAVControlCMD, UAVSetup 
from geometry_msgs.msg import PoseStamped 
from astar import AStar
import signal 
import sys 
import numpy as np
from external import Obs, Servo
from sunray_msgs.msg import Competion
from std_msgs.msg import String

class Controller:
    def __init__(self):
        self.node_name = "competiton_demo" 
        self.uav_state = UAVState() 
        self.uav_cmd = UAVControlCMD() 
        self.uav_setup = UAVSetup() 
        self.competion = Competion()

        self.state = 0 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
        self.debug = "等待开始"
        self.last_debug = ""

        "获取参数，构建无人机名称"
        self.uav_id = rospy.get_param("~uav_id", 1)
        self.uav_name = rospy.get_param("~uav_name", "uav")
        self.uav_name = f"/{self.uav_name}{self.uav_id}"

        "订阅无人机状态消息和障碍物位置消息，发布无人机控制指令和设置指令"
        self.uav_state_sub = rospy.Subscriber(
            self.uav_name + "/sunray/uav_state", UAVState, self.uav_state_cb)
        self.control_cmd_pub = rospy.Publisher(
            self.uav_name + "/sunray/uav_control_cmd", UAVControlCMD, queue_size=1)
        self.uav_setup_pub = rospy.Publisher(
            self.uav_name + "/sunray/setup", UAVSetup, queue_size=1)
        
        self.competion_pub = rospy.Publisher('/CompetionState', Competion, queue_size=1)
        self.debug_pub = rospy.Publisher('/CompetionDebug', String, queue_size=1)

        self.sim = rospy.get_param("/sim", False)
        self.obs = Obs(sim=self.sim)  # 是否为仿真模式
        self.obs.open()  # 打开障碍物订阅
        self.servo = Servo(self.uav_name)

        self.start_x, self.start_y = -2.5, -2.5
        self.goal_x, self.goal_y = 2.02, -0.56
        # self.goal_x, self.goal_y = 0.88, -0.42
        self.obstacle_coords = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]
        self.astar = AStar()
    
        "初始化控制指令和圆形轨迹参数"
        '''
        # 控制命令期望值
        float32[3] desired_pos          ## 期望位置，单位：[m]
        float32[3] desired_vel          ## 期望速度，单位：[m/s]
        float32[3] desired_acc          ## 期望加速度，单位：[m/s^2]
        float32[3] desired_att          ## 期望姿态，单位：[rad]
        float32 desired_yaw             ## 期望偏航角，单位：[rad]
        float32 desired_yaw_rate        ## 期望偏航角角速率，单位：[rad/s]
        '''
        self.uav_cmd.cmd = 0
        self.uav_cmd.desired_pos = [0.0, 0.0, 0.0]
        self.uav_cmd.desired_vel = [0.0, 0.0, 0.0]
        self.uav_cmd.desired_acc = [0.0, 0.0, 0.0]
        self.uav_cmd.desired_att = [0.0, 0.0, 0.0]
        self.uav_cmd.desired_yaw = 0.0
        self.uav_cmd.desired_yaw_rate = 0.0

        "设置参数"
        self.center_x, self.center_y = 0.0, 0.0 #圆形轨迹中心点
        self.radius = 1.0 #圆形轨迹半径
        self.num_points = 50 #圆形轨迹点数
        self.k_p, self.z_k_p = 1.5, 0.5 #速度控制p控制器
        self.k_p_accel = 2.0 #加速度控制p控制器
        self.max_accel = 1.0 #最大加速度
        self.max_vel = 1.0 #最大速度
        self.height = 1.1 #飞行高度
        self.pose = PoseStamped()
        if(self.sim == True):
            self.points = [
                [1.27, -0.56, self.height], # 随机避障区终点
                [1.27, 0.13, self.height],   # 小框中心位置
                [1.46, 1.27, self.height],  # 大框中心位置
                [1.46, 1.36, self.height],  # 穿框后终点
                [0.11, 1.67, self.height],  # 风扰区
                [0.0, 0.0, self.height]     # 投放区
            ] 
        else:
            self.points = [
                [2.02, -0.56, self.height], # 随机避障区终点
                [2.02, 0.0, self.height],   # 小框中心位置
                [2.13, 1.14, self.height],  # 大框中心位置
                [2.17, 1.36, self.height],  # 穿框后终点
                [0.11, 1.67, self.height],  # 风扰区
                [0.0, 0.0, self.height]     # 投放区
            ] 

        "退出信号处理"
        signal.signal(signal.SIGINT, self.my_sigint_handler)

    "处理CTRL+C信号"
    def my_sigint_handler(self, sig, frame):
        rospy.loginfo(f"{self.node_name}: exit...")
        rospy.signal_shutdown("User interrupted")
        sys.exit(0)

    "无人机状态回调函数"
    def uav_state_cb(self, msg):
        self.uav_state = msg
    
    "等待无人机连接"
    def wait_for_connection(self):
        rate = rospy.Rate(1.0) #1 Hz
        times = 0
        while not rospy.is_shutdown() and not self.uav_state.connected:
            times += 1
            if times > 5:
                rospy.loginfo(f"{self.node_name}:Wait for UAV connect...")
            rate.sleep()
        rospy.loginfo(f"{self.node_name}:UAV connected!")

    "切换到cmd控制模式"
    def set_control_mode(self):
        rate = rospy.Rate(1.0) #1 Hz
        while not rospy.is_shutdown() and self.uav_state.control_mode != UAVSetup.CMD_CONTROL:
            self.uav_setup.cmd = UAVSetup.SET_CONTROL_MODE
            self.uav_setup.control_mode = "CMD_CONTROL"
            self.uav_setup_pub.publish(self.uav_setup)
            rospy.loginfo(f"{self.node_name}:SET_CONTROL_MODE -> [{self.uav_setup.control_mode}]")
            rate.sleep()
        rospy.loginfo(f"{self.node_name}:UAV control_mode set to [{self.uav_setup.control_mode}] successfully!")

    "解锁无人机"
    def arm_uav(self):
        self.state = 1 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
        for i in range(2, 0, -1): 
            rospy.loginfo(f"{self.node_name}: Arm UAV in {i} sec...")
            rospy.sleep(1.0)
        rate = rospy.Rate(1.0)
        while not rospy.is_shutdown() and not self.uav_state.armed:
            self.uav_setup.cmd = UAVSetup.ARM 
            self.uav_setup_pub.publish(self.uav_setup)
            rospy.loginfo(f"{self.node_name}: ARM UAV now.")
            rate.sleep()
        rospy.loginfo(f"{self.node_name}: ARM UAV successfully!")

    "起飞无人机"
    def takeoff(self):
        self.state = 2 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
        rate = rospy.Rate(0.25)
        while not rospy.is_shutdown() and abs(self.uav_state.position[2] - self.uav_state.home_pos[2] - self.uav_state.takeoff_height) > 0.2: 
            self.uav_cmd.cmd = UAVControlCMD.Takeoff
            self.uav_cmd.header.stamp = rospy.Time.now()
            self.control_cmd_pub.publish(self.uav_cmd)
            rospy.loginfo(f"{self.node_name}: Takeoff UAV now.")
            rate.sleep()
        rospy.loginfo(f"{self.node_name}: Takeoff UAV successfully!")

    "悬停无人机"
    def hover(self, time=1):
        rospy.sleep(1.0)
        rospy.loginfo(f"{self.node_name}: Send UAV Hover cmd.")
        self.uav_cmd.cmd = UAVControlCMD.Hover
        self.uav_cmd.header.stamp = rospy.Time.now()
        self.control_cmd_pub.publish(self.uav_cmd)
        rospy.sleep(time)

    "单点位置控制接口"
    def pose_ctrl(self, x, y, z):
        rate = rospy.Rate(20.0)  # 20 Hz
        count = 0
        while not rospy.is_shutdown():
            self.uav_cmd.header.stamp = rospy.Time.now()
            self.uav_cmd.cmd = UAVControlCMD.XyzPos  # 位置模式
            self.uav_cmd.desired_pos = [x, y, z]
            self.control_cmd_pub.publish(self.uav_cmd)
            dx = x - self.uav_state.position[0]
            dy = y - self.uav_state.position[1]
            dz = z - self.uav_state.position[2]
            if abs(dx) < 0.1 and abs(dy) < 0.1 and abs(dz) < 0.2:
                count += 1
            else:
                count = 0

            if count > 40:
                rospy.loginfo(f"{self.node_name}: Reached target position ({x}, {y}, {z})")
                break
            rate.sleep()

    "单点速度控制接口"
    def vel_ctrl(self, vx, vy, vz):
        self.uav_cmd.header.stamp = rospy.Time.now()
        self.uav_cmd.cmd = UAVControlCMD.XyzVel
        self.uav_cmd.desired_vel = [vx, vy, vz]
        self.control_cmd_pub.publish(self.uav_cmd)

    "自定义飞行,使用速度控制接口"
    def custom_fly_vel(self):
        rate = rospy.Rate(20.0)  # 20 Hz

        for idx, point in enumerate(self.points):
            rospy.loginfo(f"{self.node_name}: Flying to point {idx+1}: {point}")
            target_x, target_y, target_z = point

            while not rospy.is_shutdown():
                dx = target_x - self.uav_state.position[0]
                dy = target_y - self.uav_state.position[1]
                dz = target_z - self.uav_state.position[2]

                vx = self.k_p * dx
                vy = self.k_p * dy
                vz = self.z_k_p * dz

                vx = min(max(vx, -self.max_vel), self.max_vel)
                vy = min(max(vy, -self.max_vel), self.max_vel)
                vz = min(max(vz, -self.max_vel), self.max_vel)

                self.uav_cmd.header.stamp = rospy.Time.now()
                self.uav_cmd.cmd = UAVControlCMD.XyzVel
                self.uav_cmd.desired_vel = [vx, vy, vz]
                self.control_cmd_pub.publish(self.uav_cmd)

                if abs(dx) < 0.15 and abs(dy) < 0.15 and abs(dz) < 0.2:
                    rospy.loginfo(f"{self.node_name}: Reached point {idx+1}")
                    if idx == 6:
                        self.hover()
                    break

                rate.sleep()

    "自定义飞行：使用位置控制接口"
    def custom_fly_pose(self):
        rate = rospy.Rate(20.0)  # 20 Hz
        self.state = 4 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
        for idx, point in enumerate(self.points):
            rospy.loginfo(f"{self.node_name}: Flying to point {idx+1}: {point}")
            target_x, target_y, target_z = point

            drop_count = 0  # 投放计数
            while not rospy.is_shutdown():
                self.uav_cmd.header.stamp = rospy.Time.now()
                self.uav_cmd.cmd = UAVControlCMD.XyzPos  # 位置模式
                self.uav_cmd.desired_pos = [target_x, target_y, target_z]
                self.control_cmd_pub.publish(self.uav_cmd)

                dx = target_x - self.uav_state.position[0]
                dy = target_y - self.uav_state.position[1]
                dz = target_z - self.uav_state.position[2]

                if abs(dx) < 0.15 and abs(dy) < 0.15 and abs(dz) < 0.2:
                    rospy.loginfo(f"{self.node_name}: Reached point {idx+1}")
                    
                    if idx == 4:
                        self.state = 5 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
                        self.hover(10)
                        break

                    if idx == 5:
                        self.state = 6 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
                        self.hover()
                        while True:
                            self.uav_cmd.header.stamp = rospy.Time.now()
                            self.uav_cmd.cmd = UAVControlCMD.XyzPos  # 位置模式
                            self.uav_cmd.desired_pos = [target_x, target_y, target_z]
                            self.control_cmd_pub.publish(self.uav_cmd)

                            dx = target_x - self.uav_state.position[0]
                            dy = target_y - self.uav_state.position[1]
                            # dz = target_z - 0.07 - self.uav_state.position[2]
                            dz = target_z - self.uav_state.position[2]

                            if abs(dx) < 0.1 and abs(dy) < 0.1 and abs(dz) < 0.1:
                                drop_count += 1
                            else:
                                drop_count = 0
                            
                            if drop_count > 20:
                                self.servo.servo_drop()  # 投放
                                self.state = 7 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
                                self.hover()
                                break

                            rate.sleep()

                    break

                rate.sleep()

    "返回原点(速度控制)"
    def return_to_origin_vel(self):
        rate = rospy.Rate(20.0)
        count = 0
        self.pose.pose.position.x = -2.0
        self.pose.pose.position.y = -2.0
        self.pose.pose.position.z = self.height

        while not rospy.is_shutdown():
            dx = self.pose.pose.position.x - self.uav_state.position[0]
            dy = self.pose.pose.position.y - self.uav_state.position[1]
            dz = self.pose.pose.position.z - self.uav_state.position[2]

            vx = self.k_p * dx
            vy = self.k_p * dy
            vz = self.z_k_p * dz

            vx = min(max(vx, -self.max_vel), self.max_vel)
            vy = min(max(vy, -self.max_vel), self.max_vel)
            vz = min(max(vz, -self.max_vel), self.max_vel)

            self.uav_cmd.header.stamp = rospy.Time.now()
            self.uav_cmd.cmd = UAVControlCMD.XyzVel
            self.uav_cmd.desired_vel = [vx, vy, vz]
            self.control_cmd_pub.publish(self.uav_cmd)

            if abs(self.uav_state.position[0] - self.pose.pose.position.x) < 0.1 and \
               abs(self.uav_state.position[1] - self.pose.pose.position.y) < 0.1:
                count += 1
            else:
                count = 0

            if count > 40:
                rospy.loginfo(f"{self.node_name}: Arrived at origin (velocity control).")
                break

            rate.sleep()

    "返回原点（位置控制）"
    def return_to_origin_pose(self):
        self.state = 8 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
        rate = rospy.Rate(20.0)
        count = 0
        target_x = self.uav_state.home_pos[0]
        target_y = self.uav_state.home_pos[1]
        print(self.uav_state.home_pos)
        target_z = self.height

        while not rospy.is_shutdown():
            self.uav_cmd.header.stamp = rospy.Time.now()
            self.uav_cmd.cmd = UAVControlCMD.XyzPos   
            self.uav_cmd.desired_pos = [target_x, target_y, target_z]
            self.control_cmd_pub.publish(self.uav_cmd)

            dx = target_x - self.uav_state.position[0]
            dy = target_y - self.uav_state.position[1]

            if abs(dx) < 0.1 and abs(dy) < 0.1:
                count += 1
            else:
                count = 0

            if count > 20:
                rospy.loginfo(f"{self.node_name}: Arrived at origin (position control).")
                break 

            rate.sleep()

    "降落"
    def land(self):
        self.state = 9 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
        rate = rospy.Rate(2.0)
        while not rospy.is_shutdown() and (self.uav_state.control_mode != UAVSetup.LAND_CONTROL or self.uav_state.landed_state != 1):
            self.uav_cmd.header.stamp = rospy.Time.now()
            self.uav_cmd.cmd = UAVControlCMD.Land
            self.control_cmd_pub.publish(self.uav_cmd)
            rospy.loginfo(f"{self.node_name}: Land UAV now.")
            rate.sleep()

        rate = rospy.Rate(2.0)  # 1 Hz
        while not rospy.is_shutdown() and self.uav_state.landed_state != 1:
            rospy.loginfo(f"{self.node_name}: Landing")
            rate.sleep()

        rospy.loginfo(f"{self.node_name}: Land UAV successfully!")
        rospy.loginfo(f"{self.node_name}: Demo finished, quit!")

    "A*规划"
    def astar_plan_and_fly(self):
        self.state = 3 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
        # A*参数
        origin = (self.start_x, self.start_y)
        resolution = 0.05 # 分辨率
        rows, cols = 120, 120 # 栅格地图大小
        inflation_radius = 0.54 # 膨胀半径
        self.points[-1] = [self.obs.get_delivery()[0], self.obs.get_delivery()[1], self.height]  # 更新投放点位置
        self.obstacle_coords = self.obs.get_obstacles()
        # print(self.obstacle_coords)
        
        # 生成grid（带膨胀）
        grid = self.astar.create_grid_from_obstacles(
            self.obstacle_coords, rows, cols, resolution, origin, inflation_radius)
        
        # 发布栅格地图到rviz
        self.astar.publish_occupancy_grid(grid, origin, resolution)
        
        # 获取起点和终点的栅格坐标
        start_x, start_y = self.uav_state.position[0], self.uav_state.position[1]
        start_grid = self.astar.world_to_grid(start_x, start_y, origin, resolution)
        goal_grid = self.astar.world_to_grid(self.goal_x, self.goal_y, origin, resolution)
        
        # 调试信息：打印坐标转换结果
        rospy.loginfo(f"起点世界坐标: ({start_x:.2f}, {start_y:.2f})")
        rospy.loginfo(f"终点世界坐标: ({self.goal_x:.2f}, {self.goal_y:.2f})")
        rospy.loginfo(f"起点栅格坐标: {start_grid}")
        rospy.loginfo(f"终点栅格坐标: {goal_grid}")
        
        # 检查起点和终点是否在地图范围内
        if not (0 <= start_grid[0] < rows and 0 <= start_grid[1] < cols):
            rospy.logerr(f"起点超出地图范围: {start_grid}, 地图大小: ({rows}, {cols})")
            self.land()
            return
        if not (0 <= goal_grid[0] < rows and 0 <= goal_grid[1] < cols):
            rospy.logerr(f"终点超出地图范围: {goal_grid}, 地图大小: ({rows}, {cols})")
            self.land()
            return
            
        # 检查起点和终点是否在障碍物内
        if grid[start_grid[0], start_grid[1]] == 1:
            rospy.logwarn(f"起点位于障碍物内: {start_grid}, 尝试寻找附近可通行点")
            start_grid = self.astar.find_nearest_free_cell(grid, start_grid)
            if start_grid is None:
                rospy.logerr("无法找到可通行的起点")
                self.land()
                return
                
        if grid[goal_grid[0], goal_grid[1]] == 1:
            rospy.logwarn(f"终点位于障碍物内: {goal_grid}, 尝试寻找附近可通行点")
            goal_grid = self.astar.find_nearest_free_cell(grid, goal_grid)
            if goal_grid is None:
                rospy.logerr("无法找到可通行的终点")
                self.land()
                return
        
        # 路径规划
        path = self.astar.search(start_grid, goal_grid, grid)
        if not path or len(path) < 2:
            rospy.logwarn("A*未找到有效路径，任务中止！")
            rospy.loginfo(f"栅格地图障碍物数量: {np.sum(grid == 1)}")
            rospy.loginfo(f"栅格地图自由空间数量: {np.sum(grid == 0)}")
            self.land()
            return
        # 路径点还原为世界坐标
        waypoints = [self.astar.grid_to_world(gy, gx, origin, resolution) for gy, gx in path]
        
        # 路径平滑化处理 - 减少路径点数量以提高速度
        rospy.loginfo(f"原始路径点数: {len(waypoints)}")
        waypoints = self.astar.smooth_path(waypoints, smoothing_factor=0.3, iterations=3)
        # 减少插值点数量，或跳过插值直接使用平滑路径
        # waypoints = self.astar.interpolate_path(waypoints, num_points=2)  # 注释掉减少路径点
        if not self.astar.is_path_safe(waypoints, grid, origin, resolution):
            rospy.logwarn("平滑路径不安全，回退到原始A*路径")
            waypoints = [self.astar.grid_to_world(gy, gx, origin, resolution) for gy, gx in path]
        
        # 进一步减少路径点 - 每隔几个点取一个
        if len(waypoints) > 10:
            step = max(1, len(waypoints) // 8)  # 最多保留8个关键点
            key_waypoints = waypoints[::step]
            if waypoints[-1] not in key_waypoints:
                key_waypoints.append(waypoints[-1])  # 确保包含终点
            waypoints = key_waypoints
        
        rospy.loginfo(f"优化后路径点数: {len(waypoints)}")
        
        # 发布路径到rviz
        self.astar.publish_path(waypoints)
        
        # 控制无人机依次飞向waypoints（位置控制）
        rate = rospy.Rate(30.0)
        for idx, (wx, wy) in enumerate(waypoints):
            rospy.loginfo(f"A*航点 {idx+1}/{len(waypoints)}: ({wx:.2f}, {wy:.2f}, {self.height:.2f})")
            while not rospy.is_shutdown():
                self.uav_cmd.header.stamp = rospy.Time.now()
                self.uav_cmd.cmd = UAVControlCMD.XyzPos
                self.uav_cmd.desired_pos = [wx, wy, self.height]
                self.control_cmd_pub.publish(self.uav_cmd)
                dx = wx - self.uav_state.position[0]
                dy = wy - self.uav_state.position[1]
                dz = self.height - self.uav_state.position[2]
                if abs(dx) < 0.15 and abs(dy) < 0.15 and abs(dz) < 0.2:
                    break
                rate.sleep()

        # 控制无人机依次飞向waypoints（速度控制）
        # rate = rospy.Rate(20.0)
        # for idx, (wx, wy) in enumerate(waypoints):
        #     rospy.loginfo(f"A*航点 {idx+1}/{len(waypoints)}: ({wx:.2f}, {wy:.2f}, {self.height:.2f})")
        #     target_x, target_y, target_z = wx, wy, self.height
            
        #     while not rospy.is_shutdown():
        #         dx = target_x - self.uav_state.position[0]
        #         dy = target_y - self.uav_state.position[1]
        #         dz = target_z - self.uav_state.position[2]

        #         if abs(dx) < 0.15 and abs(dy) < 0.15 and abs(dz) < 0.2:
        #             break

        #         vx = self.k_p * dx
        #         vy = self.k_p * dy
        #         vz = self.z_k_p * dz
                
        #         vx = min(max(vx, -self.max_vel), self.max_vel)
        #         vy = min(max(vy, -self.max_vel), self.max_vel)
        #         vz = min(max(vz, -self.max_vel), self.max_vel)
                
        #         self.uav_cmd.header.stamp = rospy.Time.now()
        #         self.uav_cmd.cmd = UAVControlCMD.XyzVel
        #         self.uav_cmd.desired_vel = [vx, vy, vz]
        #         self.control_cmd_pub.publish(self.uav_cmd)
                
        #         rate.sleep()

        # 控制无人机依次飞向waypoints（加速度控制）
        # rate = rospy.Rate(30.0)
        # for idx, (wx, wy) in enumerate(waypoints):
        #     rospy.loginfo(f"A*航点 {idx+1}/{len(waypoints)}: ({wx:.2f}, {wy:.2f}, {self.height:.2f})")
        #     target_x, target_y, target_z = wx, wy, self.height
            
        #     while not rospy.is_shutdown():
        #         dx = target_x - self.uav_state.position[0]
        #         dy = target_y - self.uav_state.position[1]
        #         dz = target_z - self.uav_state.position[2]

        #         if abs(dx) < 0.15 and abs(dy) < 0.15 and abs(dz) < 0.2:
        #             break

        #         desired_vx = self.k_p * dx
        #         desired_vy = self.k_p * dy
        #         desired_vz = self.z_k_p * dz
                
        #         desired_vx = min(max(desired_vx, -self.max_vel), self.max_vel)
        #         desired_vy = min(max(desired_vy, -self.max_vel), self.max_vel)
        #         desired_vz = min(max(desired_vz, -self.max_vel), self.max_vel)

        #         error_vx = desired_vx - self.uav_state.velocity[0]
        #         error_vy = desired_vy - self.uav_state.velocity[1]
        #         error_vz = desired_vz - self.uav_state.velocity[2]

        #         ax = self.k_p_accel * error_vx
        #         ay = self.k_p_accel * error_vy
        #         az = self.k_p_accel * error_vz

        #         ax = min(max(ax, -self.max_accel), self.max_accel)
        #         ay = min(max(ay, -self.max_accel), self.max_accel)
        #         az = min(max(az, -self.max_accel), self.max_accel)
                
        #         self.uav_cmd.header.stamp = rospy.Time.now()
        #         self.uav_cmd.cmd = UAVControlCMD.PosVelAccYaw
        #         self.uav_cmd.desired_pos = [target_x, target_y, target_z]
        #         self.uav_cmd.desired_vel = [desired_vx, desired_vy, desired_vz]
        #         self.uav_cmd.desired_acc = [ax, ay, az]
        #         self.control_cmd_pub.publish(self.uav_cmd)
                
        #         rate.sleep()
        rospy.loginfo("A*路径已完成!")


    "主程序"
    def run(self):
        self.wait_for_connection()
        self.set_control_mode()
        self.arm_uav()
        self.takeoff()
        self.hover()
        self.astar_plan_and_fly()
        self.custom_fly_pose()
        self.return_to_origin_pose()
        self.servo.servo_init()
        self.land()
        self.state = 10 # 0: 等待开始 1: 解锁无人机 2: 起飞 3: 随机避障区 4: 穿框区 5: 风扰区 6: 投送区 7: 投送完成 8: 返航 9: 降落 10:结束
        rospy.sleep(3)

    "舵机开闭测试"
    def drop_test(self, state='close'):
        self.wait_for_connection()
        self.set_control_mode()

        if state=='close':
            self.servo.servo_init()     # 闭合
        else:
            self.servo.servo_drop()   # 开启

    "打印运行点位用于测试是否订阅成功"
    def points_print(self):
        self.wait_for_connection()
        rospy.sleep(3) # 等待数据更新
        self.points[-1] = [self.obs.get_delivery()[0], self.obs.get_delivery()[1], self.height]  # 更新投放点位置
        self.obstacle_coords = self.obs.get_obstacles()
        # 打印当前无人机位置
        print("当前无人机位置:")
        print(self.uav_state.position) 
        # 打印所有运行点位
        print("所有运行点位:")
        for point in self.points:
            print(point)
        # 打印所有障碍物点位
        print("所有障碍物点位:")
        for obs in self.obstacle_coords:
            print(obs)

    def competition_topic_pub(self, event):
        self.competion.header.stamp = rospy.Time.now()
        self.competion.obstacle_r = 0.25
        self.competion.central_a = 1
        self.competion.obstacle_1 = [self.obs.get_obstacles()[0][0], self.obs.get_obstacles()[0][1]]
        self.competion.obstacle_2 = [self.obs.get_obstacles()[1][0], self.obs.get_obstacles()[1][1]]
        self.competion.obstacle_3 = [self.obs.get_obstacles()[2][0], self.obs.get_obstacles()[2][1]]
        self.competion.delivery = [self.obs.get_delivery()[0], self.obs.get_delivery()[1]]
        self.competion.large_box = [self.points[2][0], self.points[2][1]]
        self.competion.small_box = [self.points[1][0], self.points[1][1]]
        
        # 判断当前状态
        if self.state == 0:
            self.debug = "Wait to start"
        elif self.state == 1:   
            self.debug = "Arming the UAV"
        elif self.state == 2:
            self.debug = "Takeoff"
        elif self.state == 3:
            self.debug = "Obstacle avoidance zone"
        elif self.state == 4:
            self.debug = "Crossing zone"    
        elif self.state == 5:
            self.debug = "Wind disturbance zone"
        elif self.state == 6:
            self.debug = "Delivery zone"
        elif self.state == 7:
            self.debug = "Delivery complete"
        elif self.state == 8:
            self.debug = "Return to origin"
        elif self.state == 9:
            self.debug = "Landing"
        elif self.state == 10:
            self.debug = "End"

        self.competion_pub.publish(self.competion)

        if self.last_debug != self.debug:
            self.debug_pub.publish(self.debug)
            self.last_debug = self.debug

    def debug_timer(self, event):
            self.debug_pub.publish(self.debug)

if __name__ == "__main__":
    rospy.init_node("Astar_demo", anonymous=True)
    try:
        controller = Controller()
        controller.node_name = rospy.get_name()
        rospy.Timer(rospy.Duration(0.25), controller.competition_topic_pub)
        rospy.Timer(rospy.Duration(1), controller.debug_timer)
        controller.run()                # 完整流程
        # controller.points_print()     # 打印运行点位
        # controller.drop_test('close')   # 闭合抛投器
        # controller.drop_test('open')    # 开启抛投器
    except rospy.ROSInterruptException:
        pass
