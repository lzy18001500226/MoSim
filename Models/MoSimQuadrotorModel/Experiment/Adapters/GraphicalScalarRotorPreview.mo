within MoSimQuadrotorModel.Experiment.Adapters;
model GraphicalScalarRotorPreview
  "Visible scalar-to-four-rotor boundary for fixed-input graphical cores"

  parameter Real hover_speed_rad_s(unit = "rad/s") = 64.7923778389665
    "Nominal hover rotor speed from Sunray150Parameters";
  parameter Real hover_command_normalized(min = 0, max = 1) = 0.6515328
    "Normalized command that produces hover (from controller initialization)";
  parameter Real climb_margin_ratio = 0.15
    "Thrust margin above hover for climb (15% = 1.15× gravity max)";
  parameter Real descent_margin_ratio = 0.15
    "Thrust margin below hover for descent (15% = 0.85× gravity min)";

  // Compute speed range centered at actual hover command point
  parameter Real max_speed_rad_s(unit = "rad/s") = hover_speed_rad_s * sqrt(1.0 + climb_margin_ratio)
    "Maximum speed: produces 1.15× gravity";
  parameter Real min_speed_rad_s(unit = "rad/s") = hover_speed_rad_s * sqrt(1.0 - descent_margin_ratio)
    "Minimum speed: produces 0.85× gravity";

  // Linear interpolation: command ∈ [0, 1] → speed ∈ [min_speed, max_speed]
  parameter Real speed_range_rad_s(unit = "rad/s") = max_speed_rad_s - min_speed_rad_s;

  Modelica.Blocks.Interfaces.RealInput command 
    annotation(Placement(transformation(origin = {-150, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4] 
    annotation(Placement(transformation(origin = {150, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain scale[4](each k = speed_range_rad_s) 
    annotation(Placement(transformation(origin = {-30, 0}, extent = {{-20, -50}, {20, 50}})));
  Modelica.Blocks.Math.Add bias[4](each k2 = 1) 
    annotation(Placement(transformation(origin = {30, 0}, extent = {{-20, -50}, {20, 50}})));
  Modelica.Blocks.Sources.Constant min_speed[4](each k = min_speed_rad_s) 
    annotation(Placement(transformation(origin = {-30, -60}, extent = {{-10, -10}, {10, 10}})));

equation
  connect(command, scale[1].u) 
    annotation(Line(points = {{-150, 0}, {-50, 35}}, color = {0, 0, 127}));
  connect(command, scale[2].u) 
    annotation(Line(points = {{-150, 0}, {-50, 12}}, color = {0, 0, 127}));
  connect(command, scale[3].u) 
    annotation(Line(points = {{-150, 0}, {-50, -12}}, color = {0, 0, 127}));
  connect(command, scale[4].u) 
    annotation(Line(points = {{-150, 0}, {-50, -35}}, color = {0, 0, 127}));
  connect(scale[1].y, bias[1].u1) 
    annotation(Line(points = {{-10, 35}, {10, 35}}, color = {0, 0, 127}));
  connect(scale[2].y, bias[2].u1) 
    annotation(Line(points = {{-10, 12}, {10, 12}}, color = {0, 0, 127}));
  connect(scale[3].y, bias[3].u1) 
    annotation(Line(points = {{-10, -12}, {10, -12}}, color = {0, 0, 127}));
  connect(scale[4].y, bias[4].u1) 
    annotation(Line(points = {{-10, -35}, {10, -35}}, color = {0, 0, 127}));
  connect(min_speed[1].y, bias[1].u2) 
    annotation(Line(points = {{-19, -60}, {10, 20}}, color = {0, 0, 127}));
  connect(min_speed[2].y, bias[2].u2) 
    annotation(Line(points = {{-19, -60}, {10, 0}}, color = {0, 0, 127}));
  connect(min_speed[3].y, bias[3].u2) 
    annotation(Line(points = {{-19, -60}, {10, -20}}, color = {0, 0, 127}));
  connect(min_speed[4].y, bias[4].u2) 
    annotation(Line(points = {{-19, -60}, {10, -40}}, color = {0, 0, 127}));
  connect(bias[1].y, rotor_command[1]) 
    annotation(Line(points = {{50, 35}, {150, 35}, {150, 0}}, color = {0, 0, 127}));
  connect(bias[2].y, rotor_command[2]) 
    annotation(Line(points = {{50, 12}, {150, 12}, {150, 0}}, color = {0, 0, 127}));
  connect(bias[3].y, rotor_command[3]) 
    annotation(Line(points = {{50, -12}, {150, -12}, {150, 0}}, color = {0, 0, 127}));
  connect(bias[4].y, rotor_command[4]) 
    annotation(Line(points = {{50, -35}, {150, -35}, {150, 0}}, color = {0, 0, 127}));

  annotation(
    Diagram(coordinateSystem(extent = {{-170, -90}, {170, 90}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {40, 80, 120},
        fillColor = {235, 245, 255}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 20}, extent = {{-85, 18}, {85, -18}}, textString = "SCALAR"),
      Text(origin = {0, -20}, extent = {{-85, 18}, {85, -18}}, textString = "ROTOR PREVIEW")}),
    __MWORKS(version = "26.3.0"));
end GraphicalScalarRotorPreview;