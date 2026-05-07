model Race1 "无人系统大赛模型"
  annotation(__MWORKS(version = "2025a",ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=25,ContinueTimeVector),AnimationCamParam(CamUp = {-5.4512e-14, 1, -7.63142e-13}, CamCenter = {1.72393, -0.164805, -0.06175}, CamEye = {1.72393, -0.164805, 0.04075}, CamScale = {6.6601})), Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Rectangle(origin={26,-26}, 
fillColor={230,230,230}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{-218,174},{218,-174}}), Rectangle(origin={196,-3}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{-44,89},{44,-89}}), Rectangle(origin={71,-3}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{69,89},{-69,-89}}), Rectangle(origin={-99,-3}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{89,89},{-89,-89}}), Line(origin={26,98}, 
points={{-218,0},{218,0}}, 
thickness=1), Text(origin={31,121}, 
lineColor={0,0,127}, 
extent={{-113,15},{113,-15}}, 
textString="无人系统大赛模型(初赛)", 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,127}), Text(origin={-28,-84}, 
lineColor={0,0,127}, 
extent={{-19,8},{19,-8}}, 
textString="控制", 
fontSize=28, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,127}), Text(origin={121.5,-84}, 
lineColor={0,0,127}, 
extent={{-13.5,8},{13.5,-8}}, 
textString="车辆", 
fontSize=28, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,127}), Text(origin={211,-84}, 
lineColor={0,0,127}, 
extent={{-27,10},{27,-10}}, 
textString="环境与计分", 
fontSize=28, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,127}), Line(origin={26,-104}, 
points={{-218,0},{218,0}}, 
thickness=1), Line(origin={26,-130}, 
points={{-218,0},{218,0}}, 
thickness=1), Text(origin={27,-118}, 
lineColor={0,0,127}, 
extent={{-87,8},{87,-8}}, 
textString="车辆状态与得分情况", 
fontSize=36, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,127}), Rectangle(origin={-156.5,-165}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{-30.5,23},{30.5,-23}}), Rectangle(origin={-85.5,-165}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{-30.5,23},{30.5,-23}}), Rectangle(origin={-13.5,-165}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{-30.5,23},{30.5,-23}}), Rectangle(origin={60.5,-165}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{-30.5,23},{30.5,-23}}), Rectangle(origin={136.5,-165}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{-30.5,23},{30.5,-23}}), Text(origin={-157,-154}, 
lineColor={0,0,127}, 
extent={{-27,8},{27,-8}}, 
textString="小车速度(m/s)", 
fontSize=18, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,127}), Text(origin={-85,-154}, 
lineColor={0,0,127}, 
extent={{-25,6},{25,-6}}, 
textString="小车转向(deg)", 
fontSize=18, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,127}), Text(origin={-14,-154}, 
lineColor={0,0,127}, 
extent={{-27,6},{27,-6}}, 
textString="道路碰撞次数", 
fontSize=24, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,127}), Text(origin={61,-154}, 
lineColor={0,0,127}, 
extent={{-27,6},{27,-6}}, 
textString="障碍碰撞次数", 
fontSize=24, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,127}), Rectangle(origin={209.5,-165}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{-30.5,23},{30.5,-23}}), Text(origin={138,-154}, 
lineColor={255,0,0}, 
extent={{-19,6},{19,-6}}, 
textString="避障得分", 
fontSize=24, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={255,0,0}), Text(origin={-157,-174}, 
lineColor={0,0,0}, 
extent={{-25,8},{25,-8}}, 
textString="%v", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={-86,-174}, 
lineColor={0,0,0}, 
extent={{-25,8},{25,-8}}, 
textString="%yaw", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={-13,-174}, 
lineColor={0,0,0}, 
extent={{-28,8},{28,-8}}, 
textString="%cR", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={61,-174}, 
lineColor={0,0,0}, 
extent={{-28,8},{28,-8}}, 
textString="%cO", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={138,-174}, 
lineColor={0,0,0}, 
extent={{-25,8},{25,-8}}, 
textString="%P", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Rectangle(origin={-142,-41}, 
lineColor={255,0,0}, 
fillColor={255,255,255}, 
pattern=LinePattern.DashDot, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{-42,39},{42,-39}}), Text(origin={32,-212}, 
lineColor={0,0,0}, 
extent={{-166,6},{166,-6}}, 
textString="©苏州同元软控技术有限公司版权所有，仅用于无人系统大赛，未经许可不得复制、传播或以其他方式使用", 
fontName="微软雅黑", 
textStyle={TextStyle.None}, 
textColor={0,0,0}), Text(origin={-136,-11}, 
lineColor={255,0,0}, 
extent={{-40,3},{40,-3}}, 
textString="避障算法（选手建模）", 
fontSize=22, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={255,0,0}), Rectangle(origin={-307,-16}, 
fillColor={230,230,230}, 
fillPattern=FillPattern.Solid, 
lineThickness=1, 
extent={{-89,112},{89,-112}}), Text(origin={-310,-16}, 
lineColor={0,0,128}, 
extent={{-76,84},{76,-84}}, 
textString="车辆参数：
轴距：0.11m
轮距：0.165m
传感器位于前后左右四个位置

注意事项：
1. 选手只需要对红框中避障算法模块
使用Sysblock进行建模，其余模型
无需改动；
2. 仿真前点击仿真设置-仿真调速-勾选
“启用调速以减慢仿真”，即可在仿真
时查看图形界面车辆状态与得分情况的
动态显示；
3. 仿真前点击仿真设置-模型翻译-勾选
“参数估值以便优化模型”；
4. 小车每碰撞一次扣0.4分，综合考虑
小车跑完一圈用时完成总分评判，具体
细则请参看赛题说明。", 
fontSize=26, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,128}, 
horizontalAlignment=TextAlignment.Left), Text(origin={211,-174}, 
lineColor={0,0,0}, 
extent={{-25,-8},{25,8}}, 
textString="%T", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={211,-154}, 
lineColor={255,0,0}, 
extent={{-25,6},{25,-6}}, 
textString="行驶时间(s)", 
fontSize=24, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={255,0,0})}), experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.05,StartTime=0,StopTime=inf,Tolerance=0.0001),Protection(access=Access.packageDuplicate));
  Vehicle.VehicleBody.Body4DOF4S_TD body3DOF1_1(v_start = 2) 
    "四自由度无人车多体模型，x，y，z及绕z轴偏转" annotation(Placement(transformation(origin = {67, -44}, 
    extent = {{-27, -27}, {27, 27}})));
  //   inner TADynamics.Roads.RoadModel.flatRoad road(L0=1000,B0=10,x_start=-10) if false 
  //     annotation (Placement(transformation(origin={130,-58}, 
  // extent={{-10,-10},{10,10}})));
  Control.Ackermann_control.PID_Ackermann pID_Ackermann(L = body3DOF1_1.wheelbase, W = body3DOF1_1.track_front, r = 0.03, Kp_v = 100, Kp_psi = 40, Kd_v = 0.5, Ki_psi = 0.15, Kd_psi = 0.1) 
    "基于阿克曼构型的PID模型，用于控制小车期望速度与期望转角与实际速度与转角趋近" annotation(Placement(transformation(origin = {-51, -44}, 
    extent = {{-27, -27}, {27, 27}})));
  Control.PathPlanning.PathPlanner pathPlanner(path = road.roadMap, lookahead_gain = 0.1, wheelbase = body3DOF1_1.wheelbase, lookahead_base = 2) 
    "路径规划模型，用于控制小车循迹运动" annotation(Placement(transformation(origin = {-141, 52.000009}, 
    extent = {{-27, -27}, {27, 27}})));
  inner Modelica.Mechanics.MultiBody.World world(n = {0, 0, -1}, animateWorld = false, animateGravity = false, animateGround = false, enableAnimation = true) 
    "世界模型" annotation(Placement(transformation(origin={198,-56}, 
extent={{-15,-15},{15,15}})));
  Vehicle.Sensors.distanceSensor1 distanceSensor1(road = road.roadMap, width = road.roadWidth, L = body3DOF1_1.wheelbase, W = body3DOF1_1.track_front, obs = road.obstaclePoint, is_closed = true) 
    "传感器模型，用于模拟无人车到各向的距离" annotation(Placement(transformation(origin = {67, 52}, 
    extent = {{27, -27}, {-27, 27}})));
  inner Road.TabularRoadObstacle road(roadMap = {{0, 0, 1}, {2.585, 0, 1}, {6.76, 0.045, 1}, {10.845, 0.045, 1}, {14.93, 0.045, 1}, {19.015, 0.045, 1}, {23.235, 0.045, 1}, {27.275, 0.045, 1}, {31.495, 0.045, 1}, {31.995, 0.135, 1}, {32.495, 0.225, 1}, {32.8725, 0.4075, 1}, {33.25, 0.59, 1}, {33.5, 0.8175, 1}, {33.75, 1.045, 1}, {34.1, 1.4075, 1}, {34.45, 1.77, 1}, {34.61, 2.1525, 1}, {34.77, 2.535, 1}, {34.89, 2.9475, 1}, {35.01, 3.36, 1}, {35.075, 3.805, 1}, {35.14, 4.25, 1}, {35.18, 5.15, 1}, {35.165, 7.275, 1}, {35.155, 9.405, 1}, {35.165, 12.975, 1}, {35.165, 16.31, 1}, {35.165, 27.68, 1}, {35.1, 28.0925, 1}, {35.035, 28.505, 1}, {34.835, 28.8425, 1}, {34.635, 29.18, 1}, {34.3775, 29.4725, 1}, {34.12, 29.765, 1}, {33.8, 30.005, 1}, {33.48, 30.245, 1}, {33.11, 30.415, 1}, {32.74, 30.585, 1}, {32.3475, 30.7425, 1}, {31.955, 30.825, 1}, {31.545, 30.8825, 1}, {31.135, 30.865, 1}, {30.74, 30.8525, 1}, {30.345, 30.84, 1}, {29.9025, 30.735, 1}, {29.46, 30.63, 1}, {29.035, 30.4575, 1}, {28.61, 30.285, 1}, {28.23, 30.07, 1}, {27.85, 29.855, 1}, {27.515, 29.5575, 1}, {27.18, 29.26, 1}, {26.905, 28.935, 1}, {26.63, 28.61, 1}, {26.4325, 28.225, 1}, {26.235, 27.84, 1}, {26.11, 27.4225, 1}, {25.985, 27.005, 1}, {25.985, 26.5525, 1}, {25.985, 26.1, 1}, {26.3675, 19.3875, 1}, {26.75, 12.675, 1}, {26.68, 12.2175, 1}, {26.61, 11.76, 1}, {26.4475, 11.3475, 1}, {26.285, 10.935, 1}, {26.055, 10.565, 1}, {25.825, 10.195, 1}, {25.5, 9.8925, 1}, {25.175, 9.59, 1}, {24.7875, 9.355, 1}, {24.4, 9.12, 1}, {23.99, 8.98, 1}, {23.58, 8.84, 1}, {23.1475, 8.8075, 1}, {22.715, 8.775, 1}, {22.26, 8.8525, 1}, {21.805, 8.93, 1}, {21.3575, 9.115, 1}, {20.91, 9.3, 1}, {20.555, 9.5675, 1}, {20.2, 9.835, 1}, {19.935, 10.1725, 1}, {19.67, 10.51, 1}, {19.4675, 10.8825, 1}, {19.265, 11.255, 1}, {19.1325, 11.685, 1}, {19, 12.115, 1}, {18.93, 12.5475, 1}, {18.86, 12.98, 1}, {18.8575, 13.4225, 1}, {18.855, 13.865, 1}, {18.9025, 14.31, 1}, {18.95, 14.755, 1}, {18.9825, 15.1025, 1}, {19.015, 15.45, 1}, {19.0025
, 15.8275, 1}, {18.99, 16.205, 1}, {18.915, 16.55
, 1}, {18.84, 16.895, 1}, {18.7225, 17.245, 1}, {18.605, 17.595, 1}, {18.4175, 17.9075, 1}, {18.23, 18.22, 1}, {18, 18.4925, 1}, {17.77, 18.765, 1}, {17.4925, 18.9825, 1}, {17.215, 19.2, 1}, {16.8675, 19.36, 1}, {16.52, 19.52, 1}, {16.1425, 19.6275, 1}, {15.765, 19.735, 1}, {15.3675, 19.8, 1}, {14.97, 19.865, 1}, {14.5725, 19.88, 1}, {14.175, 19.895, 1}, {13.7775, 19.8725, 1}, {13.38, 19.85, 1}, {12.9875, 19.76, 1}, {12.595, 19.67, 1}, {12.21, 19.53, 1}, {11.825, 19.39, 1}, {11.4875, 19.215, 1}, {11.15, 19.04, 1}, {10.835, 18.795, 1}, {10.52, 18.55, 1}, {10.2625, 18.2, 1}, {10.005, 17.85, 1}, {9.8375, 17.4575, 1}, {9.67, 17.065, 1}, {9.5975, 16.6675, 1}, {9.525, 16.27, 1}, {9.4875, 15.8525, 1}, {9.45, 15.435, 1}, {9.4425, 15.0075, 1}, {9.435, 14.58, 1}, {9.4225, 14.1525, 1}, {9.41, 13.725, 1}, {9.3575, 13.3, 1}, {9.305, 12.875, 1}, {9.21, 12.4675, 1}, {9.115, 12.06, 1}, {8.97, 11.715, 1}, {8.825, 11.37, 1}, {8.6325, 11.025, 1}, {8.44, 10.68, 1}, {8.2075, 10.395, 1}, {7.975, 10.11, 1}, {7.7025, 9.86, 1}, {7.43, 9.61, 1}, {7.105, 9.415, 1}, {6.78, 9.22, 1}, {6.4425, 9.1, 1}, {6.105, 8.98, 1}, {5.7525, 8.95, 1}, {5.4, 8.92, 1}, {5.0225, 9, 1}, {4.645, 9.08, 1}, {4.2075, 9.23, 1}, {3.77, 9.38, 1}, {3.4025, 9.625, 1}, {3.035, 9.87, 1}, {2.73, 10.1775, 1}, {2.425, 10.485, 1}, {2.1825, 10.855, 1}, {1.94, 11.225, 1}, {1.785, 11.6425, 1}, {1.63, 12.06, 1}, {1.4975, 12.5, 1}, {1.365, 12.94, 1}, {1.2875, 13.385, 1}, {1.21, 13.83, 1}, {1.185, 14.26, 1}, {1.16, 14.69, 1}, {1.15, 15.1675, 1}, {1.14, 15.645, 1}, {1.14, 16.1325, 1}, {1.14, 16.62, 1}, {1.14, 17.1, 1}, {1.14, 17.58, 1}, {1.2075, 18.0425, 1}, {1.275, 18.505, 1}, {1.3825, 18.96, 1}, {1.49, 19.415, 1}, {1.68, 19.8525, 1}, {1.87, 20.29, 1}, {2.1425, 20.6625, 1}, {2.415, 21.035, 1}, {2.795, 21.35, 1}, {3.175, 21.665, 1}, {3.5225, 21.82, 1}, {3.87, 21.975, 1}, {4.2575, 22.0425, 1}, {4.645, 22.11, 1}, {5.025, 22.1425, 1}, {5.405, 22.175, 1}, {5.795, 22.175, 1}, {6.185, 22.175, 1}, {6.59, 22.175, 1}, {6.995, 22.175, 1}, {7.4
, 22.175, 1}, {7.805, 22.175, 1}, {8.145, 22.175, 1}, {8.485, 22.175, 1}, {8.905, 22.175, 1}, {9.325, 22.175, 1}, {10.145, 22.175, 1}, {10.965, 22.175, 1}, {11.825, 22.175, 1}, {12.685, 22.175, 1}, {13.495, 22.175, 1}, {14.305, 22.175, 1}, {15.1475, 22.2175, 1}, {15.99, 22.26, 1}, {16.5125, 22.5325, 1}, {17.035, 22.805, 1}, {17.44, 23.1925, 1}, {17.845, 23.58, 1}, {18.125, 24.0675, 1}, {18.405, 24.555, 1}, {18.5125, 25.1025, 1}, {18.62, 25.65, 1}, {18.6525, 26.2125, 1}, {18.685, 26.775, 1}, {18.5775, 27.335, 1}, {18.47, 27.895, 1}, {18.2225, 28.4075, 1}, {17.975, 28.92, 1}, {17.595, 29.335, 1}, {17.215, 29.75, 1}, {16.52, 30.1625, 1}, {15.825, 30.575, 1}, {15.0475, 30.725, 1}, {14.27, 30.875, 1}, {13.4525, 30.9, 1}, {12.635, 30.925, 1}, {11.825, 30.89, 1}, {11.015, 30.855, 1}, {4.44, 30.7975, 1}, {-2.135, 30.74, 1}, {-2.6975, 30.5675, 1}, {-3.26, 30.395, 1}, {-3.69, 30.0725, 1}, {-4.12, 29.75, 1}, {-4.525, 29.345, 1}, {-4.93, 28.94, 1}, {-5.2525, 28.5, 1}, {-5.575, 28.06, 1}, {-5.8225, 27.565, 1}, {-6.07, 27.07, 1}, {-6.26, 26.54, 1}, {-6.45, 26.01, 1}, {-6.59, 25.4475, 1}, {-6.73, 24.885, 1}, {-6.845, 24.3575, 1}, {-6.96, 23.83, 1}, {-7.1425, 17.48, 1}, {-7.325, 11.13, 1}, {-7.31, 10.525, 1}, {-7.295, 9.92, 1}, {-7.2775, 9.3, 1}, {-7.26, 8.68, 1}, {-7.2175, 8.07, 1}, {-7.175, 7.46, 1}, {-7.1175, 6.855, 1}, {-7.06, 6.25, 1}, {-6.9375, 5.655, 1}, {-6.815, 5.06, 1}, {-6.6475, 4.49, 1}, {-6.48, 3.92, 1}, {-6.2425, 3.35, 1}, {-6.005, 2.78, 1}, {-5.7225, 2.2675, 1}, {-5.44, 1.755, 1}, {-5.0175, 1.365, 1}, {-4.595, 0.975, 1}, {-4.0925, 0.72, 1}, {-3.59, 0.465, 1}, {-3.085, 0.315, 1}, {-2.58, 0.165, 1}, {-1.985, 0.12, 1}, {-1.39, 0.075, 1}, {-1.0075, 0.06, 1}, {-0.625, 0.045, 1}, {-0.4375, 0.0225, 1}, {-0.25, 0, 1}, {0, 0, 1}}, obstaclePoint = {{2.585, 0.045, -0.1105}, {14.93, 0.045, -0.1105}, {27.275, 0.045, -0.1105}, {33.5, 0.8175, -0.1105}, {35.165, 27.68, -0.1105}, {31.955, 30.9, -0.1105}, {26.11, 27.4225, -0.1105}, {23.58, 8.84, -0.1105}, {19.265, 11.255, -0.1105
}, 
    {
    17.4925, 18.9825, -0.1105}, {10.52, 18.55
    , -0.1105}, {7.975, 10.11, -0.1105}, {8.5, 10.22, -0.1105}, {1.14, 16.62, -0.1105}, {10.145, 22.175, -0.1105}, {18.62, 25.65, -0.1105}, {4.44, 30.7975, -0.1105}, {-5.575, 28.06, -0.1105}, {-7.295, 9.92, -0.1105}, {-5.7225, 2.2675, -0.1105}}, roadWidth = 1.25, surface(r_0 = {0, 0, 0.252}), obstacleHeight = 0.1, obstacleSize = 0.1) 
    "可设置障碍的道路模型" annotation(Placement(transformation(origin={198,64}, 
extent={{-15,-15},{15,15}})));
  Control.ObstacleAvoidanceController.ObsAvoidController_Sysblock2 obsAvoidController_Sysblock 
    "避障算法模型，用于控制小车遇到障碍或道路边缘时的运动决策" annotation(Placement(transformation(origin = {-141, -45.23}, 
    extent = {{-27, -27}, {27, 27}})), __MWORKS(SECInstance = true));
  Control.ControlAllocate.CtrlAlloc ctrlAlloc(factor_pp = 1, factor_oa = 0.5) 
    "控制分配模型，用于平衡路径规划与避障算法的作用比例" annotation(Placement(transformation(origin = {-51, 52}, 
    extent = {{-27, -27}, {27, 27}})));
  CountPoint.CountPoint countPoint 
    "避障计分模块" annotation(Placement(transformation(origin={198,1}, 
extent={{-15,-15},{15,15}})));
  Real v;
  Real yaw;
  Real cR;
  Real cO;
  Real P;
  Real T;
equation
  distanceSensor1.fdist = pathPlanner.lookahead_dist;
  //参数面板
  // v = floor(body3DOF1_1.v[1] * 100)/100;
  // yaw = floor((body3DOF1_1.angles[3] * 180 / pi)*100)/100;
  // cR = floor(countPoint.counterR*100)/100;
  // cO = floor(countPoint.counterO*100)/100;
  // P = floor(countPoint.finalPoints*100)/100;
  // T = floor(time*100)/100;
  v = body3DOF1_1.v[1];
  yaw = body3DOF1_1.angles[3];
  cR = countPoint.counterR;
  cO = countPoint.counterO;
  P = countPoint.finalPoints;
  T = time;
  connect(pID_Ackermann.rear_speed_l, body3DOF1_1.rl_speed) 
    annotation(Line(origin={80,19}, 
points={{-101.3,-42.75},{-64,-42.75},{-64,-77.58},{-42.7,-77.58}}, 
color={0,0,127}, 
thickness=1));
  connect(pID_Ackermann.rear_speed_r, body3DOF1_1.rr_speed) 
    annotation(Line(origin={140,-1}, 
points={{-161.3,-36.25},{-124,-36.25},{-124,-45.7},{-102.7,-45.7}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.angles[3], pID_Ackermann.current_psi) 
    annotation(Line(origin={84,4.99935}, 
points={{12.7,-28.4793},{38,-28.4793},{38,-5},{-188,-5},{-188,-69.2493},{-165.375,-69.2493}}, 
color={0,0,127}, 
thickness=1));
  connect(pID_Ackermann.delta_left, body3DOF1_1.fl_steer) 
    annotation(Line(origin={86,6}, 
points={{-107.3,-56.75},{-70,-56.75},{-70,-40.82},{-48.7,-40.82}}, 
color={0,0,127}, 
thickness=1));
  connect(pID_Ackermann.delta_right, body3DOF1_1.fr_steer) 
    annotation(Line(origin={85,5}, 
points={{-106.3,-69.25},{-69,-69.25},{-69,-28.48},{-47.7,-28.48}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.v[1], pID_Ackermann.current_v) 
    annotation(Line(origin={85,5.99935}, 
points={{11.7,-40.81935},{37,-40.81935},{37,-6},{-189,-6},{-189,-56.74935},{-166.375,-56.74935}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.v[1], pathPlanner.v) 
    annotation(Line(origin={-17,32.9994}, 
points={{113.7,-67.8194},{139,-67.8194},{139,-32.9994},{-163,-32.9994},{-163,1.0006},{-153.7,1.0006}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.r[1], pathPlanner.x) 
    annotation(Line(origin={-17,25.9994}, 
points={{113.7,-73.2394},{139,-73.2394},{139,-25.9994},{-163,-25.9994},{-163,44.0006},{-153.7,44.0006}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.r[2], pathPlanner.y) 
    annotation(Line(origin={-17,25.9994}, 
points={{113.7,-73.2394},{139,-73.2394},{139,-25.9994},{-163,-25.9994},{-163,26.0006},{-153.7,26.0006}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.Rsensor, distanceSensor1.right_sensor) 
    annotation(Line(origin={122,-79.58}, 
points={{-40.96,5.88},{-40.96,1.58},{0,1.58},{0,127.079991},{-25.3,127.079991}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.Lsensor, distanceSensor1.left_sensor) 
    annotation(Line(origin={114,-75.58}, 
points={{-42.68,1.88},{-42.68,-2.42},{8,-2.42},{8,132.080009},{-17.3,132.080009}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.Bsensor, distanceSensor1.rear_sensor) 
    annotation(Line(origin={106,-71.58}, 
points={{-44.4,-2.12},{-44.4,-6.42},{16,-6.42},{16,137.08},{-9.3,137.08}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.Fsensor, distanceSensor1.front_sensor) 
    annotation(Line(origin={98,-67.58}, 
points={{-46.12,-6.12},{-46.12,-10.42},{24,-10.42},{24,142.079991},{-1.3,142.079991}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.r[1:2], distanceSensor1.vehicle_position) 
    annotation(Line(origin={154,-72.58}, 
points={{-57.3,25.34},{-32,25.34},{-32,111.08},{-57.3,111.08}}, 
color={0,0,127}, 
thickness=1));
  connect(body3DOF1_1.angles[3], distanceSensor1.yaw) 
    annotation(Line(origin={157,-66.58}, 
points={{-60.3,43.1},{-35,43.1},{-35,96.08},{-60.3,96.08}}, 
color={0,0,127}, 
thickness=1));
  connect(obsAvoidController_Sysblock.front_dist, distanceSensor1.front_dist) 
    annotation(Line(origin={-60,7}, 
points={{-109.8,-31.98},{-120,-31.98},{-120,-7},{76,-7},{76,67.499991},{97.3,67.499991}}, 
color={0,0,0}, 
thickness=1));
  connect(obsAvoidController_Sysblock.rear_dist, distanceSensor1.rear_dist) 
    annotation(Line(origin={-60,-6}, 
points={{-109.8,-32.48},{-120,-32.48},{-120,6},{76,6},{76,71.5},{97.3,71.5}}, 
color={0,0,0}, 
thickness=1));
  connect(obsAvoidController_Sysblock.left_dist, distanceSensor1.left_dist) 
    annotation(Line(origin={-60,-20}, 
points={{-109.8,-31.98},{-120,-31.98},{-120,20},{76,20},{76,76.500009},{97.3,76.500009}}, 
color={0,0,0}, 
thickness=1));
  connect(obsAvoidController_Sysblock.right_dist, distanceSensor1.right_dist) 
    annotation(Line(origin={-60,-33}, 
points={{-109.8,-32.48},{-120,-32.48},{-120,33},{76,33},{76,80.499991},{97.3,80.499991}}, 
color={0,0,0}, 
thickness=1));
  connect(ctrlAlloc.speed, pID_Ackermann.v_desired) 
    annotation(Line(origin={-45,109}, 
points={{23.7,-43.5},{61,-43.5},{61,-109},{-59,-109},{-59,-132.75},{-36.375,-132.75}}, 
color={0,0,127}, 
thickness=1));
  connect(ctrlAlloc.steer, pID_Ackermann.psi_desired) 
    annotation(Line(origin={-45,96}, 
points={{23.7,-57.5},{61,-57.5},{61,-96},{-59,-96},{-59,-133.25},{-36.375,-133.25}}, 
color={0,0,127}, 
thickness=1));
  connect(pathPlanner.target_v, ctrlAlloc.speed_pp) 
    annotation(Line(origin={-150.3,109.75}, 
points={{39,-44.25},{46.3,-44.25},{46.3,-37.5},{69.6,-37.5}}, 
color={0,0,127}, 
thickness=1));
  connect(pathPlanner.steering_angle, ctrlAlloc.steer_pp) 
    annotation(Line(origin={-150,90}, 
points={{38.7,-51.499991},{46,-51.499991},{46,-44.75},{69.3,-44.75}}, 
color={0,0,127}, 
thickness=1));
  connect(obsAvoidController_Sysblock.speed, ctrlAlloc.speed_oa) 
    annotation(Line(origin={-16,35}, 
points={{-96.2,-66.73},{-88,-66.73},{-88,23.75},{-64.7,23.75}}, 
color={0,0,0}, 
thickness=1));
  connect(obsAvoidController_Sysblock.steer, ctrlAlloc.steer_oa) 
    annotation(Line(origin={-11,14}, 
points={{-101.2,-72.73},{-93,-72.73},{-93,17.75},{-69.7,17.75}}, 
color={0,0,0}, 
thickness=1));
  connect(distanceSensor1.DisRoad, countPoint.DisRoad) 
  annotation(Line(origin={102,19}, 
points={{-64.7,19.5},{-86,19.5},{-86,-19},{74,-19},{74,-10.5},{79.5,-10.5}}, 
color={0,0,127}, 
thickness=1));
  connect(distanceSensor1.DisObstacle, countPoint.DisObstacle) 
  annotation(Line(origin={102,12}, 
points={{-64.7,17.500009},{-86,17.500009},{-86,-12},{74,-12},{74,-18.5},{79.5,-18.5}}, 
color={0,0,127}, 
thickness=1));
  end Race1;