within MoSimQuadrotorModel.Experiment.Adapters;
model GraphicalAccelerationRotorPreview
  "Visible acceleration-to-rotor review adapter"

  Modelica.Blocks.Interfaces.RealInput acceleration_x 
    annotation(Placement(transformation(origin = {-260, 90}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput acceleration_y 
    annotation(Placement(transformation(origin = {-260, 30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput acceleration_z 
    annotation(Placement(transformation(origin = {-260, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput collective_thrust 
    annotation(Placement(transformation(origin = {-260, -90}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4] 
    annotation(Placement(transformation(origin = {260, 0}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Math.Gain x_gain[4](each k = 1) 
    annotation(Placement(transformation(origin = {-130, 90}, extent = {{-20, -12}, {20, 12}})));
  Modelica.Blocks.Math.Gain y_gain[4](each k = 1) 
    annotation(Placement(transformation(origin = {-130, 30}, extent = {{-20, -12}, {20, 12}})));
  Modelica.Blocks.Math.Gain z_gain[4](each k = 1) 
    annotation(Placement(transformation(origin = {-130, -30}, extent = {{-20, -12}, {20, 12}})));
  Modelica.Blocks.Math.Gain thrust_gain[4](each k = 1) 
    annotation(Placement(transformation(origin = {-130, -90}, extent = {{-20, -12}, {20, 12}})));
  Modelica.Blocks.Math.Sum rotor_sum[4](each nin = 4) 
    annotation(Placement(transformation(origin = {100, 0}, extent = {{-30, -70}, {30, 70}})));

equation
  connect(acceleration_x, x_gain[1].u) 
    annotation(Line(points = {{-260, 90}, {-150, 90}}, color = {0, 0, 127}));
  connect(acceleration_x, x_gain[2].u) 
    annotation(Line(points = {{-260, 90}, {-200, 90}, {-200, 30}, {-150, 30}}, color = {0, 0, 127}));
  connect(acceleration_x, x_gain[3].u) 
    annotation(Line(points = {{-260, 90}, {-210, 90}, {-210, -30}, {-150, -30}}, color = {0, 0, 127}));
  connect(acceleration_x, x_gain[4].u) 
    annotation(Line(points = {{-260, 90}, {-220, 90}, {-220, -90}, {-150, -90}}, color = {0, 0, 127}));
  connect(acceleration_y, y_gain[1].u) 
    annotation(Line(points = {{-260, 30}, {-190, 30}, {-190, 70}, {-150, 70}}, color = {0, 0, 127}));
  connect(acceleration_y, y_gain[2].u) 
    annotation(Line(points = {{-260, 30}, {-150, 30}}, color = {0, 0, 127}));
  connect(acceleration_y, y_gain[3].u) 
    annotation(Line(points = {{-260, 30}, {-190, 30}, {-190, -50}, {-150, -50}}, color = {0, 0, 127}));
  connect(acceleration_y, y_gain[4].u) 
    annotation(Line(points = {{-260, 30}, {-200, 30}, {-200, -110}, {-150, -110}}, color = {0, 0, 127}));
  connect(acceleration_z, z_gain[1].u) 
    annotation(Line(points = {{-260, -30}, {-210, -30}, {-210, 50}, {-150, 50}}, color = {0, 0, 127}));
  connect(acceleration_z, z_gain[2].u) 
    annotation(Line(points = {{-260, -30}, {-200, -30}, {-200, 10}, {-150, 10}}, color = {0, 0, 127}));
  connect(acceleration_z, z_gain[3].u) 
    annotation(Line(points = {{-260, -30}, {-150, -30}}, color = {0, 0, 127}));
  connect(acceleration_z, z_gain[4].u) 
    annotation(Line(points = {{-260, -30}, {-190, -30}, {-190, -70}, {-150, -70}}, color = {0, 0, 127}));
  connect(collective_thrust, thrust_gain[1].u) 
    annotation(Line(points = {{-260, -90}, {-230, -90}, {-230, 30}, {-150, 30}}, color = {0, 0, 127}));
  connect(collective_thrust, thrust_gain[2].u) 
    annotation(Line(points = {{-260, -90}, {-150, -90}}, color = {0, 0, 127}));
  connect(collective_thrust, thrust_gain[3].u) 
    annotation(Line(points = {{-260, -90}, {-210, -90}, {-210, -30}, {-150, -30}}, color = {0, 0, 127}));
  connect(collective_thrust, thrust_gain[4].u) 
    annotation(Line(points = {{-260, -90}, {-200, -90}, {-200, 90}, {-150, 90}}, color = {0, 0, 127}));
  connect(x_gain[1].y, rotor_sum[1].u[1]) 
    annotation(Line(points = {{-110, 90}, {40, 90}}, color = {0, 0, 127}));
  connect(y_gain[1].y, rotor_sum[1].u[2]) 
    annotation(Line(points = {{-110, 30}, {40, 50}}, color = {0, 0, 127}));
  connect(z_gain[1].y, rotor_sum[1].u[3]) 
    annotation(Line(points = {{-110, -30}, {40, 10}}, color = {0, 0, 127}));
  connect(thrust_gain[1].y, rotor_sum[1].u[4]) 
    annotation(Line(points = {{-110, -90}, {20, -20}, {40, -10}}, color = {0, 0, 127}));
  connect(x_gain[2].y, rotor_sum[2].u[1]) 
    annotation(Line(points = {{-110, 90}, {0, 90}, {0, 30}, {40, 30}}, color = {0, 0, 127}));
  connect(y_gain[2].y, rotor_sum[2].u[2]) 
    annotation(Line(points = {{-110, 30}, {40, 10}}, color = {0, 0, 127}));
  connect(z_gain[2].y, rotor_sum[2].u[3]) 
    annotation(Line(points = {{-110, -30}, {0, -30}, {0, -10}, {40, -10}}, color = {0, 0, 127}));
  connect(thrust_gain[2].y, rotor_sum[2].u[4]) 
    annotation(Line(points = {{-110, -90}, {0, -90}, {0, -30}, {40, -30}}, color = {0, 0, 127}));
  connect(x_gain[3].y, rotor_sum[3].u[1]) 
    annotation(Line(points = {{-110, 90}, {10, 90}, {10, -10}, {40, -10}}, color = {0, 0, 127}));
  connect(y_gain[3].y, rotor_sum[3].u[2]) 
    annotation(Line(points = {{-110, 30}, {10, 30}, {10, -30}, {40, -30}}, color = {0, 0, 127}));
  connect(z_gain[3].y, rotor_sum[3].u[3]) 
    annotation(Line(points = {{-110, -30}, {40, -50}}, color = {0, 0, 127}));
  connect(thrust_gain[3].y, rotor_sum[3].u[4]) 
    annotation(Line(points = {{-110, -90}, {10, -90}, {10, -70}, {40, -70}}, color = {0, 0, 127}));
  connect(x_gain[4].y, rotor_sum[4].u[1]) 
    annotation(Line(points = {{-110, 90}, {20, 90}, {20, -50}, {40, -50}}, color = {0, 0, 127}));
  connect(y_gain[4].y, rotor_sum[4].u[2]) 
    annotation(Line(points = {{-110, 30}, {20, 30}, {20, -70}, {40, -70}}, color = {0, 0, 127}));
  connect(z_gain[4].y, rotor_sum[4].u[3]) 
    annotation(Line(points = {{-110, -30}, {20, -30}, {20, -90}, {40, -90}}, color = {0, 0, 127}));
  connect(thrust_gain[4].y, rotor_sum[4].u[4]) 
    annotation(Line(points = {{-110, -90}, {40, -110}}, color = {0, 0, 127}));
  connect(rotor_sum[1].y, rotor_command[1]) 
    annotation(Line(points = {{160, 50}, {260, 0}}, color = {0, 0, 127}));
  connect(rotor_sum[2].y, rotor_command[2]) 
    annotation(Line(points = {{160, 17}, {260, 0}}, color = {0, 0, 127}));
  connect(rotor_sum[3].y, rotor_command[3]) 
    annotation(Line(points = {{160, -17}, {260, 0}}, color = {0, 0, 127}));
  connect(rotor_sum[4].y, rotor_command[4]) 
    annotation(Line(points = {{160, -50}, {260, 0}}, color = {0, 0, 127}));

  annotation(
    Diagram(coordinateSystem(extent = {{-280, -130}, {280, 130}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {80, 80, 120},
        fillColor = {245, 240, 255}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 20}, extent = {{-90, 18}, {90, -18}}, textString = "ACCEL"),
      Text(origin = {0, -20}, extent = {{-90, 18}, {90, -18}}, textString = "ROTOR PREVIEW")}),
    __MWORKS(version = "26.3.0"));
end GraphicalAccelerationRotorPreview;