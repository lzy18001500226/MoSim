# PID_Ackermann.mo

- Source: `培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/00-模型材料/UGV/Control/Ackermann_control/PID_Ackermann.mo`
- Category: `quadrotor_uav`
- Score: `92`
- Size: `0.01 MB`
- Extract mode: `text`

## Extracted Text

```text
﻿model PID_Ackermann "阿克曼架构-PID控制"
  annotation(__MWORKS(version = "2025a"), Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={-7.10543e-15,2}, 
lineColor={0,0,0}, 
extent={{-100,12.5},{100,-12.5}}, 
textString="PID控制", 
fontSize=20, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,0})}),Protection(access=Access.diagram));
  extends UGV.Utilities.Icons.Model1;
  //参数区域
  //车辆参数
  parameter Modelica.SIunits.Length L = 2.75 "轴距（前后轮距离）";
  parameter Modelica.SIunits.Length W = 1.5 "轮距（左右轮距离）";
  parameter Modelica.SIunits.Length r = 0.3 "驱动轮半径";
  //PID参数
  parameter Real Kp_psi = 0.8 "偏航角比例系数";
  parameter Real Ki_psi = 0.05 "偏航角积分系数";
  parameter Real Kd_psi = 0.2 "偏航角微分系数";
  parameter Real Kp_v = 1.2 "速度比例系数";
  parameter Real Ki_v = 0.1 "速度积分系数";
  parameter Real Kd_v = 0.3 "速度微分系数";
  Modelica.Blocks.Interfaces.RealInput v_desired 
    "期望速度" annotation(Placement(transformation(origin = {-112.5, 75}, 
    extent = {{-12.5, -12.5}, {12.5, 12.5}}), 
    iconTransformation(origin = {0, 0})));
  Modelica.Blocks.Interfaces.RealInput psi_desired 
    "期望转向" annotation(Placement(transformation(origin = {-112.5, 25}, 
    extent = {{-12.5, -12.5}, {12.5, 12.5}}), 
    iconTransformation(origin = {0, 0})));
  Modelica.Blocks.Interfaces.RealInput current_v 
    "实际速度" annotation(Placement(transformation(origin = {-112.5, -25}, 
    extent = {{-12.5, -12.5}, {12.5, 12.5}}), 
    iconTransformation(origin = {0, 0})));
  Modelica.Blocks.Interfaces.RealInput current_psi 
    "实际转向" annotation(Placement(transformation(origin = {-112.5, -75}, 
    extent = {{-12.5, -12.5}, {12.5, 12.5}}), 
    iconTransformation(origin = {0, 0})));
  Modelica.Blocks.Interfaces.RealOutput rear_speed_l 
    "左后轮转速" annotation(Placement(transformation(origin = {110, 75}, 
    extent = {{-10, -10}, {10, 10}}), 
    iconTransformation(origin = {0, 0})));
  Modelica.Blocks.Interfaces.RealOutput rear_speed_r 
    "右后轮转速" annotation(Placement(transformation(origin = {110, 25}, 
    extent = {{-10, -10}, {10, 10}}), 
    iconTransformation(origin = {0, 0})));
  Modelica.Blocks.Interfaces.RealOutput delta_left 
    "左前轮转向" annotation(Placement(transformation(origin = {110, -25}, 
    extent = {{-10, -10}, {10, 10}}), 
    iconTransformation(origin = {0, 0})));
  Modelica.Blocks.Interfaces.RealOutput delta_right 
    "右前轮转向" annotation(Placement(transformation(origin = {110, -75}, 
    extent = {{-10, -10}, {10, 10}}), 
    iconTransformation(origin = {0, 0})));
  Internal.psi_pid_control psi_pid_control1(Kp_psi=Kp_psi,Ki_psi=Ki_psi,Kd_psi=Kd_psi) 
    "偏航角pid模块" annotation (Placement(transformation(origin={-34,50}, 
extent={{-18,-18},{18,18}})));
  Internal.v_pid_control v_pid_control1(Kp_v=Kp_v,Ki_v=Ki_v,Kd_v=Kd_v) 
    "速度pid模块" annotation (Placement(transformation(origin={-34,-44}, 
extent={{-18,-18},{18,18}})));
  Internal.FW_SteerAngle fW_SteerAngle(L=L) 
    "前轮转向角" annotation (Placement(transformation(origin={13.5,43.75}, 
extent={{-12.5,12.5},{12.5,-12.5}})));
  Internal.ackermann_steer ackermann_steer1(L=L,W=W) 
    "阿克曼构型的前左及前右转角" annotation (Placement(transformation(origin={48,43.75}, 
extent={{-10,-10},{10,10}})));
  Internal.RW_diffCal rW_diffCal(W=W,r=r) 
    "后轮差速模块" annotation (Placement(transformation(origin={48,-39}, 
extent={{-10,10},{10,-10}})));
  equation
  connect(psi_desired, psi_pid_control1.psi_desired) 
  annotation(Line(origin={-83,42}, 
  points={{-29.5,-17},{3,-17},{3,17},{28.75,17}}, 
  color={0,0,127}));
  connect(current_psi, psi_pid_control1.current_psi) 
  annotation(Line(origin={-83,-17}, 
points={{-29.5,-58},{9,-58},{9,58},{28.75,58}}, 
color={0,0,127}));
  connect(v_desired, v_pid_control1.v_desired) 
  annotation(Line(origin={-83,20}, 
  points={{-29.5,55},{3,55},{3,-55},{28.75,-55}}, 
  color={0,0,127}));
  connect(current_v, v_pid_control1.current_v) 
  annotation(Line(origin={-83,-39}, 
  points={{-29.5,14},{9,14},{9,-14},{28.75,-14}}, 
  color={0,0,127}));
  connect(psi_pid_control1.omega_d, fW_SteerAngle.omega_d) 
  annotation(Line(origin={-5,50}, 
points={{-9.2,0},{4.75,0}}, 
color={0,0,127}));
  connect(fW_SteerAngle.delta, ackermann_steer1.delta) 
  annotation(Line(origin={32,44}, 
  points={{-4.75,-0.25},{5,-0.25}}, 
  color={0,0,127}));
  connect(psi_pid_control1.omega_d, rW_diffCal.omega_d) 
  annotation(Line(origin={11,8}, 
  points={{-25.2,42},{-17,42},{-17,-42},{26,-42}}, 
  color={0,0,127}));
  connect(rW_diffCal.rear_speed_l, rear_speed_l) 
  annotation(Line(origin={85,16}, 
  points={{-26,-60},{-17,-60},{-17,59},{25,59}}, 
  color={0,0,127}));
  connect(rW_diffCal.rear_speed_r, rear_speed_r) 
  annotation(Line(origin={85,-4}, 
points={{-26,-30},{-13,-30},{-13,29},{25,29}}, 
color={0,0,127}));
  connect(ackermann_steer1.delta_left, delta_left) 
  annotation(Line(origin={85,12}, 
points={{-26,36.75},{-5,36.75},{-5,-37},{25,-37}}, 
color={0,0,127}));
  connect(ackermann_steer1.delta_right, delta_right) 
  annotation(Line(origin={85,-18}, 
points={{-26,56.75},{-9,56.75},{-9,-57},{25,-57}}, 
color={0,0,127}));
  connect(v_pid_control1.v_cmd, rW_diffCal.v_cmd) 
  annotation(Line(origin={11,-44}, 
  points={{-25.2,0},{26,0}}, 
  color={0,0,127}));
  connect(v_pid_control1.v_cmd, fW_SteerAngle.v_cmd) 
  annotation(Line(origin={-7,-3}, 
points={{-7.2,-41},{1,-41},{1,40.5},{6.75,40.5}}, 
color={0,0,127}));
end PID_Ackermann;
```
