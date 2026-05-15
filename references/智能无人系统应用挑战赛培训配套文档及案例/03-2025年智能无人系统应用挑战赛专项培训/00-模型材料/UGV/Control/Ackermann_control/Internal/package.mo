package Internal "内部模型"
  annotation(__MWORKS(version="2025a"),Protection(access=Access.diagram));
  model psi_pid_control "偏航角PID控制"
    annotation(__MWORKS(version="2025a"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2}),graphics = {Text(origin={3,-1}, 
  lineColor={0,0,0}, 
  extent={{-69,53},{69,-53}}, 
  textString="psi", 
  textStyle={TextStyle.None}, 
  textColor={0,0,0}, 
  horizontalAlignment=LinePattern.None)}),Protection(access=Access.diagram));
  extends UGV.Utilities.Icons.Model1;
   //PID参数
    parameter Real Kp_psi = 0.8 "偏航角比例系数";
    parameter Real Ki_psi = 0.05 "偏航角积分系数";
    parameter Real Kd_psi = 0.2 "偏航角微分系数";
    Modelica.Blocks.Interfaces.RealInput current_psi 
      annotation (Placement(transformation(origin={-112.5,-50}, 
  extent={{-12.5,-12.5},{12.5,12.5}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealOutput omega_d 
      annotation (Placement(transformation(origin={110,0}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput psi_desired 
      annotation (Placement(transformation(origin={-112.5,50}, 
  extent={{-12.5,-12.5},{12.5,12.5}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Math.Gain P(k = Kp_psi) 
      annotation (Placement(transformation(origin={-10,40}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain I(k = Ki_psi) 
      annotation (Placement(transformation(origin={-10,0}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain D(k = Kd_psi) 
      annotation (Placement(transformation(origin={-10,-40}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Continuous.Integrator integrator 
      annotation (Placement(transformation(origin={-42,0}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Continuous.Derivative derivative 
      annotation (Placement(transformation(origin={-42,-40}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Add3 add3_1 
      annotation (Placement(transformation(origin={36,0}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain gain3(k = 1) 
      annotation (Placement(transformation(origin={76,0}, 
  extent={{-10,-10},{10,10}})));
    angle_diff angle_diff1 
      annotation (Placement(transformation(origin={-80,0}, 
  extent={{-10,-10},{10,10}})));
  equation
    connect(integrator.y, I.u) 
    annotation(Line(origin={-15,0}, 
points={{-16,0},{-7,0}}, 
color={0,0,127}));
    connect(derivative.y, D.u) 
    annotation(Line(origin={-14,-54}, 
points={{-17,14},{-8,14}}, 
color={0,0,127}));
    connect(I.y, add3_1.u2) 
    annotation(Line(origin={41,0}, 
points={{-40,0},{-17,0}}, 
color={0,0,127}));
    connect(P.y, add3_1.u1) 
    annotation(Line(origin={14,31}, 
points={{-13,9},{-4,9},{-4,-23},{10,-23}}, 
color={0,0,127}));
    connect(D.y, add3_1.u3) 
    annotation(Line(origin={42,-31}, 
points={{-41,-9},{-32,-9},{-32,23},{-18,23}}, 
color={0,0,127}));
    connect(add3_1.y, gain3.u) 
    annotation(Line(origin={91,0}, 
  points={{-44,0},{-27,0}}, 
  color={0,0,127}));
    connect(P.u, angle_diff1.error_psi) 
    annotation(Line(origin={-23,40}, 
points={{1,0},{-41,0},{-41,-40},{-46,-40}}, 
color={0,0,127}));
    connect(gain3.y, omega_d) 
    annotation(Line(origin={99,0}, 
    points={{-12,0},{11,0}}, 
    color={0,0,127}));
    connect(psi_desired, angle_diff1.psi_desired) 
    annotation(Line(origin={-83,48}, 
  points={{-29.5,2},{-13,2},{-13,-43},{-8.25,-43}}, 
  color={0,0,127}));
    connect(current_psi, angle_diff1.current_psi) 
    annotation(Line(origin={-83,-7}, 
  points={{-29.5,-43},{-13,-43},{-13,2},{-8.25,2}}, 
  color={0,0,127}));
    connect(angle_diff1.error_psi, integrator.u) 
    annotation(Line(origin={-61,0}, 
    points={{-8,0},{7,0}}, 
    color={0,0,127}));
    connect(angle_diff1.error_psi, derivative.u) 
    annotation(Line(origin={-61,-20}, 
    points={{-8,20},{-3,20},{-3,-20},{7,-20}}, 
    color={0,0,127}));
    end psi_pid_control;
  model angle_diff "角度差计算（-pi到pi）"
    annotation(__MWORKS(version = "2025a"), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={1,0}, 
lineColor={0,0,0}, 
extent={{-55,42},{55,-42}}, 
textString="a1-a2", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}),Protection(access=Access.diagram));
    extends UGV.Utilities.Icons.Model1;
    Modelica.Blocks.Interfaces.RealInput current_psi 
      annotation(Placement(transformation(origin = {-112.5, -50}, 
      extent = {{-12.5, -12.5}, {12.5, 12.5}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput psi_desired 
      annotation(Placement(transformation(origin = {-112.5, 50}, 
      extent = {{-12.5, -12.5}, {12.5, 12.5}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput error_psi 
      annotation(Placement(transformation(origin = {110, 0}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
  equation
    error_psi = UGV.Utilities.Functions.angle_diff(psi_desired, current_psi);
  end angle_diff;
  model v_pid_control "速度PID控制"
    annotation(__MWORKS(version="2025a"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={-1,3}, 
lineColor={0,0,0}, 
extent={{-53,45},{53,-45}}, 
textString="V", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}),Protection(access=Access.diagram));
  extends UGV.Utilities.Icons.Model1;
   //PID参数
    parameter Real Kp_v = 1.2 "速度比例系数";
    parameter Real Ki_v = 0.1 "速度积分系数";
    parameter Real Kd_v = 0.3 "速度微分系数";
    Modelica.Blocks.Interfaces.RealInput current_v 
      annotation (Placement(transformation(origin={-112.5,-50}, 
  extent={{-12.5,-12.5},{12.5,12.5}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput v_desired 
      annotation (Placement(transformation(origin={-112.5,50}, 
  extent={{-12.5,-12.5},{12.5,12.5}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealOutput v_cmd 
      annotation (Placement(transformation(origin={110,0}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Math.Gain P(k = Kp_v) 
      annotation (Placement(transformation(origin={-4,40}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain I(k = Ki_v) 
      annotation (Placement(transformation(origin={-4,0}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain D(k = Kd_v) 
      annotation (Placement(transformation(origin={-4,-40}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Continuous.Integrator integrator 
      annotation (Placement(transformation(origin={-36,0}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Continuous.Derivative derivative 
      annotation (Placement(transformation(origin={-36,-40}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Add3 add3_1 
      annotation (Placement(transformation(origin={38,0}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain gain3(k = 1) 
      annotation (Placement(transformation(origin={78,0}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Add add(k2=-1) 
      annotation (Placement(transformation(origin={-72,-3.95075e-22}, 
  extent={{-10,-10},{10,10}})));
  equation
    connect(integrator.y, I.u) 
    annotation(Line(origin={-9,0}, 
  points={{-16,0},{-7,0}}, 
  color={0,0,127}));
    connect(derivative.y, D.u) 
    annotation(Line(origin={-8,-54}, 
  points={{-17,14},{-8,14}}, 
  color={0,0,127}));
    connect(I.y, add3_1.u2) 
    annotation(Line(origin={43,0}, 
  points={{-36,0},{-17,0}}, 
  color={0,0,127}));
    connect(P.y, add3_1.u1) 
    annotation(Line(origin={16,31}, 
  points={{-9,9},{-4,9},{-4,-23},{10,-23}}, 
  color={0,0,127}));
    connect(D.y, add3_1.u3) 
    annotation(Line(origin={44,-31}, 
  points={{-37,-9},{-32,-9},{-32,23},{-18,23}}, 
  color={0,0,127}));
    connect(add3_1.y, gain3.u) 
    annotation(Line(origin={93,0}, 
  points={{-44,0},{-27,0}}, 
  color={0,0,127}));
    connect(gain3.y, v_cmd) 
    annotation(Line(origin={100,0}, 
    points={{-11,0},{10,0}}, 
    color={0,0,127}));
    connect(v_desired, add.u1) 
    annotation(Line(origin={-98,28}, 
    points={{-14.5,22},{4,22},{4,-22},{14,-22}}, 
    color={0,0,127}));
    connect(current_v, add.u2) 
    annotation(Line(origin={-98,-28}, 
    points={{-14.5,-22},{4,-22},{4,22},{14,22}}, 
    color={0,0,127}));
    connect(add.y, integrator.u) 
    annotation(Line(origin={-56,0}, 
  points={{-5,-3.95075e-22},{8,0}}, 
  color={0,0,127}));
    connect(add.y, P.u) 
    annotation(Line(origin={-40,20}, 
  points={{-21,-20},{-16,-20},{-16,20},{24,20}}, 
  color={0,0,127}));
    connect(add.y, derivative.u) 
    annotation(Line(origin={-56,-20}, 
  points={{-5,20},{0,20},{0,-20},{8,-20}}, 
  color={0,0,127}));

  end v_pid_control;
  model FW_SteerAngle "前轮转向角"
    annotation(__MWORKS(version = "2025a"), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2}),graphics = {Text(origin={0,4}, 
  lineColor={0,0,0}, 
  extent={{-74,50},{74,-50}}, 
  textString="FW
Steer"        , 
  textStyle={TextStyle.None}, 
  textColor={0,0,0}, 
  horizontalAlignment=LinePattern.None)}),Protection(access=Access.diagram));
    extends UGV.Utilities.Icons.Model1;
    parameter Modelica.SIunits.Length L = 2.75 "轴距（前后轮距离）";
    SI.Angle last_delta(start = 0) "存储上次转向角";
    Modelica.Blocks.Interfaces.RealInput v_cmd 
      annotation(Placement(transformation(origin = {-110, 50}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput omega_d 
      annotation(Placement(transformation(origin = {-110, -50}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput delta 
      annotation(Placement(transformation(origin = {110, 0}, 
      extent = {{-10, -10}, {10, 10}})));
    initial equation
    delta = 0;
    last_delta = 0;
  algorithm
    if abs(v_cmd) > 0.1 then
    // 有效速度范围时计算新转向角
      delta := atan(omega_d * L / v_cmd);
      last_delta := delta;
    else
    // 低速时保持上次转向角
      delta := last_delta;
      last_delta := last_delta;
    end if;
    // 保护条件（避免除零）
    assert(abs(v_cmd) > 1e-3 or abs(omega_d) < 1e-3,"低速时禁止转向操作",AssertionLevel.warning);
  end FW_SteerAngle;
  model ackermann_steer "阿克曼转向几何计算"
    annotation(__MWORKS(version = "2025a"), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2})), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2}), graphics = {Text(origin = {-1, 5}, 
      lineColor = {0, 0, 0}, 
      extent = {{-75, 47}, {75, -47}}, 
      textString = "ackermann
Steer"    , 
      textStyle = {TextStyle.None}, 
      textColor = {0, 0, 0}, 
      horizontalAlignment = LinePattern.None)}),Protection(access=Access.diagram));
    extends UGV.Utilities.Icons.Model1;
    parameter Modelica.SIunits.Length L = 2.75 "轴距（前后轮距离）";
    parameter Modelica.SIunits.Length W = 1.5 "轮距（左右轮距离）";
    parameter Real maxsteer = 0.523599 "最大转向角30度";
    Modelica.Blocks.Interfaces.RealInput delta 
      annotation(Placement(transformation(origin = {-110, 0}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput delta_left 
      annotation(Placement(transformation(origin = {110, 50}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput delta_right 
      annotation(Placement(transformation(origin = {110, -50}, 
      extent = {{-10, -10}, {10, 10}})));
  algorithm
    (delta_left,delta_right) := UGV.Utilities.Functions.ackermann_geometry(delta, L, W);

    if delta_left >= maxsteer then
      delta_left := maxsteer;
    end if;
    if delta_left >= -maxsteer and delta_left < maxsteer then
      delta_left := delta_left;
    end if;
    if delta_left < -maxsteer then
      delta_left := -maxsteer;
    end if;

    if delta_right >= maxsteer then
      delta_right := maxsteer;
    end if;
    if delta_right >= -maxsteer and delta_right < maxsteer then
      delta_right := delta_right;
    end if;
    if delta_right < -maxsteer then
      delta_right := -maxsteer;
    end if;
  end ackermann_steer;
  model RW_diffCal "后轮差速计算"
    annotation(__MWORKS(version = "2025a"), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2}),graphics = {Text(origin={-1,4}, 
  lineColor={0,0,0}, 
  extent={{-75,46},{75,-46}}, 
  textString="RW
diffCal"            , 
  textStyle={TextStyle.None}, 
  textColor={0,0,0}, 
  horizontalAlignment=LinePattern.None)}),Protection(access=Access.diagram));
    extends UGV.Utilities.Icons.Model1;
    parameter Modelica.SIunits.Length W = 1.5 "轮距（左右轮距离）";
    parameter Modelica.SIunits.Length r = 0.3 "驱动轮半径";
    SI.Velocity v_left "中间变量左后轮速度";
    SI.Velocity v_right "中间变量右后轮速度";
    Modelica.Blocks.Interfaces.RealInput v_cmd 
      annotation(Placement(transformation(origin = {-110, 50}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput omega_d 
      annotation(Placement(transformation(origin = {-110, -50}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput rear_speed_l 
      annotation(Placement(transformation(origin = {110, 50}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput rear_speed_r 
      annotation(Placement(transformation(origin = {110, -50}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
  equation
    if abs(v_cmd) < 0.01 and abs(omega_d) < 0.01 then
      rear_speed_l = 0;
      rear_speed_r = 0;
      v_left = 0;
      v_right = 0;
    else
      v_left = v_cmd - (omega_d * W / 2);
      v_right = v_cmd + (omega_d * W / 2);
      rear_speed_l = v_left / r;//单位 rad/s
      rear_speed_r = v_right / r;
      // rear_speed_l = v_right / r;//单位 rad/s
      // rear_speed_r = v_left / r;
    end if;
  end RW_diffCal;

end Internal;