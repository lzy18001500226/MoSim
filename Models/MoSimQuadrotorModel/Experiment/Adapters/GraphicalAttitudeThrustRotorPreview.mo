within MoSimQuadrotorModel.Experiment.Adapters;
model GraphicalAttitudeThrustRotorPreview
  "Visible attitude/thrust-to-four-rotor review adapter"

  parameter Real hover_speed_rad_s(unit = "rad/s") = 64.7923778389665
    "Nominal hover rotor speed from Sunray150Parameters";
  parameter Real climb_margin_ratio = 0.82
    "Thrust margin above hover for climb (82% = 1.82× gravity max, supports 8 m/s^2 accel)";
  parameter Real descent_margin_ratio = 0.82
    "Thrust margin below hover for descent (82% = 0.18× gravity min)";

  parameter Real max_speed_rad_s(unit = "rad/s") = hover_speed_rad_s * sqrt(1.0 + climb_margin_ratio)
    "Maximum speed: produces 1.15× gravity";
  parameter Real min_speed_rad_s(unit = "rad/s") = hover_speed_rad_s * sqrt(1.0 - descent_margin_ratio)
    "Minimum speed: produces 0.85× gravity";
  parameter Real speed_range_rad_s(unit = "rad/s") = max_speed_rad_s - min_speed_rad_s;

  parameter Real attitude_to_speed_gain = 2.0
    "Converts attitude reference (rad) to differential rotor speed (rad/s)";

  Modelica.Blocks.Interfaces.RealInput roll_ref 
    annotation(Placement(transformation(origin = {-270, 90}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput pitch_ref 
    annotation(Placement(transformation(origin = {-270, 30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput yaw_ref 
    annotation(Placement(transformation(origin = {-270, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput collective_thrust 
    annotation(Placement(transformation(origin = {-270, -90}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4] 
    annotation(Placement(transformation(origin = {270, 0}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Math.Gain roll_gain[4](k = {attitude_to_speed_gain, -attitude_to_speed_gain, -attitude_to_speed_gain, attitude_to_speed_gain}) 
    annotation(Placement(transformation(origin = {-140, 90}, extent = {{-20, -12}, {20, 12}})));
  Modelica.Blocks.Math.Gain pitch_gain[4](k = {-attitude_to_speed_gain, -attitude_to_speed_gain, attitude_to_speed_gain, attitude_to_speed_gain}) 
    annotation(Placement(transformation(origin = {-140, 30}, extent = {{-20, -12}, {20, 12}})));
  Modelica.Blocks.Math.Gain yaw_gain[4](k = {-attitude_to_speed_gain, attitude_to_speed_gain, -attitude_to_speed_gain, attitude_to_speed_gain}) 
    annotation(Placement(transformation(origin = {-140, -30}, extent = {{-20, -12}, {20, 12}})));

  Modelica.Blocks.Math.Gain thrust_scale[4](each k = speed_range_rad_s) 
    annotation(Placement(transformation(origin = {-140, -90}, extent = {{-20, -12}, {20, 12}})));
  Modelica.Blocks.Math.Add thrust_bias[4](each k2 = 1) 
    annotation(Placement(transformation(origin = {-50, -90}, extent = {{-20, -12}, {20, 12}})));
  Modelica.Blocks.Sources.Constant min_speed[4](each k = min_speed_rad_s) 
    annotation(Placement(transformation(origin = {-140, -130}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Math.Sum rotor_sum[4](each nin = 4) 
    annotation(Placement(transformation(origin = {110, 0}, extent = {{-30, -70}, {30, 70}})));

equation
  connect(collective_thrust, thrust_scale[1].u) 
    annotation(Line(points = {{-270, -90}, {-160, -90}}, color = {0, 0, 127}));
  connect(collective_thrust, thrust_scale[2].u) 
    annotation(Line(points = {{-270, -90}, {-160, -90}}, color = {0, 0, 127}));
  connect(collective_thrust, thrust_scale[3].u) 
    annotation(Line(points = {{-270, -90}, {-160, -90}}, color = {0, 0, 127}));
  connect(collective_thrust, thrust_scale[4].u) 
    annotation(Line(points = {{-270, -90}, {-160, -90}}, color = {0, 0, 127}));
  connect(thrust_scale[1].y, thrust_bias[1].u1) 
    annotation(Line(points = {{-120, -90}, {-70, -90}}, color = {0, 0, 127}));
  connect(thrust_scale[2].y, thrust_bias[2].u1) 
    annotation(Line(points = {{-120, -90}, {-70, -90}}, color = {0, 0, 127}));
  connect(thrust_scale[3].y, thrust_bias[3].u1) 
    annotation(Line(points = {{-120, -90}, {-70, -90}}, color = {0, 0, 127}));
  connect(thrust_scale[4].y, thrust_bias[4].u1) 
    annotation(Line(points = {{-120, -90}, {-70, -90}}, color = {0, 0, 127}));
  connect(min_speed[1].y, thrust_bias[1].u2) 
    annotation(Line(points = {{-129, -130}, {-70, -100}}, color = {0, 0, 127}));
  connect(min_speed[2].y, thrust_bias[2].u2) 
    annotation(Line(points = {{-129, -130}, {-70, -100}}, color = {0, 0, 127}));
  connect(min_speed[3].y, thrust_bias[3].u2) 
    annotation(Line(points = {{-129, -130}, {-70, -100}}, color = {0, 0, 127}));
  connect(min_speed[4].y, thrust_bias[4].u2) 
    annotation(Line(points = {{-129, -130}, {-70, -100}}, color = {0, 0, 127}));
  connect(roll_ref, roll_gain[1].u) 
    annotation(Line(points = {{-270, 90}, {-160, 90}}, color = {0, 0, 127}));
  connect(roll_ref, roll_gain[2].u) 
    annotation(Line(points = {{-270, 90}, {-210, 90}, {-210, 30}, {-160, 30}}, color = {0, 0, 127}));
  connect(roll_ref, roll_gain[3].u) 
    annotation(Line(points = {{-270, 90}, {-220, 90}, {-220, -30}, {-160, -30}}, color = {0, 0, 127}));
  connect(roll_ref, roll_gain[4].u) 
    annotation(Line(points = {{-270, 90}, {-230, 90}, {-230, -90}, {-160, -90}}, color = {0, 0, 127}));
  connect(pitch_ref, pitch_gain[1].u) 
    annotation(Line(points = {{-270, 30}, {-200, 30}, {-200, 70}, {-160, 70}}, color = {0, 0, 127}));
  connect(pitch_ref, pitch_gain[2].u) 
    annotation(Line(points = {{-270, 30}, {-160, 30}}, color = {0, 0, 127}));
  connect(pitch_ref, pitch_gain[3].u) 
    annotation(Line(points = {{-270, 30}, {-200, 30}, {-200, -50}, {-160, -50}}, color = {0, 0, 127}));
  connect(pitch_ref, pitch_gain[4].u) 
    annotation(Line(points = {{-270, 30}, {-210, 30}, {-210, -110}, {-160, -110}}, color = {0, 0, 127}));
  connect(yaw_ref, yaw_gain[1].u) 
    annotation(Line(points = {{-270, -30}, {-220, -30}, {-220, 50}, {-160, 50}}, color = {0, 0, 127}));
  connect(yaw_ref, yaw_gain[2].u) 
    annotation(Line(points = {{-270, -30}, {-210, -30}, {-210, 10}, {-160, 10}}, color = {0, 0, 127}));
  connect(yaw_ref, yaw_gain[3].u) 
    annotation(Line(points = {{-270, -30}, {-160, -30}}, color = {0, 0, 127}));
  connect(yaw_ref, yaw_gain[4].u) 
    annotation(Line(points = {{-270, -30}, {-200, -30}, {-200, -70}, {-160, -70}}, color = {0, 0, 127}));

  connect(roll_gain[1].y, rotor_sum[1].u[1]) 
    annotation(Line(points = {{-120, 90}, {50, 90}}, color = {0, 0, 127}));
  connect(pitch_gain[1].y, rotor_sum[1].u[2]) 
    annotation(Line(points = {{-120, 30}, {50, 50}}, color = {0, 0, 127}));
  connect(yaw_gain[1].y, rotor_sum[1].u[3]) 
    annotation(Line(points = {{-120, -30}, {50, 10}}, color = {0, 0, 127}));
  connect(thrust_bias[1].y, rotor_sum[1].u[4]) 
    annotation(Line(points = {{-30, -90}, {50, -30}}, color = {0, 0, 127}));
  connect(roll_gain[2].y, rotor_sum[2].u[1]) 
    annotation(Line(points = {{-120, 90}, {10, 90}, {10, 30}, {50, 30}}, color = {0, 0, 127}));
  connect(pitch_gain[2].y, rotor_sum[2].u[2]) 
    annotation(Line(points = {{-120, 30}, {50, 10}}, color = {0, 0, 127}));
  connect(yaw_gain[2].y, rotor_sum[2].u[3]) 
    annotation(Line(points = {{-120, -30}, {10, -30}, {10, -10}, {50, -10}}, color = {0, 0, 127}));
  connect(thrust_bias[2].y, rotor_sum[2].u[4]) 
    annotation(Line(points = {{-30, -90}, {50, -30}}, color = {0, 0, 127}));
  connect(roll_gain[3].y, rotor_sum[3].u[1]) 
    annotation(Line(points = {{-120, 90}, {20, 90}, {20, -10}, {50, -10}}, color = {0, 0, 127}));
  connect(pitch_gain[3].y, rotor_sum[3].u[2]) 
    annotation(Line(points = {{-120, 30}, {20, 30}, {20, -30}, {50, -30}}, color = {0, 0, 127}));
  connect(yaw_gain[3].y, rotor_sum[3].u[3]) 
    annotation(Line(points = {{-120, -30}, {50, -50}}, color = {0, 0, 127}));
  connect(thrust_bias[3].y, rotor_sum[3].u[4]) 
    annotation(Line(points = {{-30, -90}, {50, -70}}, color = {0, 0, 127}));
  connect(roll_gain[4].y, rotor_sum[4].u[1]) 
    annotation(Line(points = {{-120, 90}, {30, 90}, {30, -50}, {50, -50}}, color = {0, 0, 127}));
  connect(pitch_gain[4].y, rotor_sum[4].u[2]) 
    annotation(Line(points = {{-120, 30}, {30, 30}, {30, -70}, {50, -70}}, color = {0, 0, 127}));
  connect(yaw_gain[4].y, rotor_sum[4].u[3]) 
    annotation(Line(points = {{-120, -30}, {30, -30}, {30, -90}, {50, -90}}, color = {0, 0, 127}));
  connect(thrust_bias[4].y, rotor_sum[4].u[4]) 
    annotation(Line(points = {{-30, -90}, {50, -110}}, color = {0, 0, 127}));
  connect(rotor_sum[1].y, rotor_command[1]) 
    annotation(Line(points = {{170, 50}, {270, 0}}, color = {0, 0, 127}));
  connect(rotor_sum[2].y, rotor_command[2]) 
    annotation(Line(points = {{170, 17}, {270, 0}}, color = {0, 0, 127}));
  connect(rotor_sum[3].y, rotor_command[3]) 
    annotation(Line(points = {{170, -17}, {270, 0}}, color = {0, 0, 127}));
  connect(rotor_sum[4].y, rotor_command[4]) 
    annotation(Line(points = {{170, -50}, {270, 0}}, color = {0, 0, 127}));

  annotation(
    Diagram(coordinateSystem(extent = {{-290, -130}, {290, 130}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {120, 80, 40},
        fillColor = {255, 248, 235}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 20}, extent = {{-90, 18}, {90, -18}}, textString = "ATTITUDE"),
      Text(origin = {0, -20}, extent = {{-90, 18}, {90, -18}}, textString = "ROTOR PREVIEW")}),
    __MWORKS(version = "26.3.0"));
end GraphicalAttitudeThrustRotorPreview;