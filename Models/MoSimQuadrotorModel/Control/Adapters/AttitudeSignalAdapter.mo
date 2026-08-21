within MoSimQuadrotorModel.Control.Adapters;
model AttitudeSignalAdapter
  "Signal adapter for inner-loop attitude controllers: bridges Sysblock outputs + Modelica plant attitude to Sysblock inner-loop core"

  // Inputs from outer-loop Sysblock core (Outport)
  Modelica.Blocks.Interfaces.RealInput desired_roll_rad(unit = "rad") 
    annotation(Placement(transformation(origin = {-110, 70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput desired_pitch_rad(unit = "rad") 
    annotation(Placement(transformation(origin = {-110, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput desired_yaw_rad(unit = "rad") 
    annotation(Placement(transformation(origin = {-110, 30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput collective_thrust_n(unit = "N") 
    annotation(Placement(transformation(origin = {-110, 10}, extent = {{-10, -10}, {10, 10}})));

  // Inputs from plant (Modelica RealOutput)
  Modelica.Blocks.Interfaces.RealInput roll_mea(unit = "rad")
    annotation(Placement(transformation(origin = {-110, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput pitch_mea(unit = "rad")
    annotation(Placement(transformation(origin = {-110, -40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput yaw_mea(unit = "rad")
    annotation(Placement(transformation(origin = {-110, -60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput roll_rate_mea(unit = "rad/s")
    annotation(Placement(transformation(origin = {-110, -80}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput pitch_rate_mea(unit = "rad/s")
    annotation(Placement(transformation(origin = {-110, -100}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput yaw_rate_mea(unit = "rad/s")
    annotation(Placement(transformation(origin = {-110, -120}, extent = {{-10, -10}, {10, 10}})));

  // Outputs to inner-loop Sysblock core (Inport)
  Modelica.Blocks.Interfaces.RealOutput desired_roll_rad_out(unit = "rad") 
    annotation(Placement(transformation(origin = {110, 70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput desired_pitch_rad_out(unit = "rad") 
    annotation(Placement(transformation(origin = {110, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput desired_yaw_rad_out(unit = "rad") 
    annotation(Placement(transformation(origin = {110, 30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput thrust_baseline_out(unit = "1") 
    annotation(Placement(transformation(origin = {110, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput roll_mea_out(unit = "rad") 
    annotation(Placement(transformation(origin = {110, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput pitch_mea_out(unit = "rad") 
    annotation(Placement(transformation(origin = {110, -40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput yaw_mea_out(unit = "rad")
    annotation(Placement(transformation(origin = {110, -60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput roll_rate_mea_out(unit = "rad/s")
    annotation(Placement(transformation(origin = {110, -80}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput pitch_rate_mea_out(unit = "rad/s")
    annotation(Placement(transformation(origin = {110, -100}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput yaw_rate_mea_out(unit = "rad/s")
    annotation(Placement(transformation(origin = {110, -120}, extent = {{-10, -10}, {10, 10}})));

  // Unit conversion parameters
  parameter Real thrust_n_to_amplitude = 6.4
    "Conversion from Newtons to amplitude (nominal hover: 10N thrust → 64 amplitude, matching OfficialPid z_pid output range)";

equation
  // Direct passthrough for angles
  desired_roll_rad_out = desired_roll_rad;
  desired_pitch_rad_out = desired_pitch_rad;
  desired_yaw_rad_out = desired_yaw_rad;
  roll_mea_out = roll_mea;
  pitch_mea_out = pitch_mea;
  yaw_mea_out = yaw_mea;
  roll_rate_mea_out = roll_rate_mea;
  pitch_rate_mea_out = pitch_rate_mea;
  yaw_rate_mea_out = yaw_rate_mea;

  // Unit conversion: thrust (N) → dimensionless amplitude
  thrust_baseline_out = collective_thrust_n * thrust_n_to_amplitude;

  annotation(
    Icon(coordinateSystem(preserveAspectRatio = false, extent = {{-100, -140}, {100, 80}}), graphics = {
      Rectangle(extent = {{-100, 80}, {100, -140}}, lineColor = {200, 0, 200}, fillColor = {255, 240, 255}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 20}, extent = {{-80, 20}, {80, -20}}, textString = "Attitude", textColor = {200, 0, 200}),
      Text(origin = {0, -20}, extent = {{-80, 20}, {80, -20}}, textString = "Adapter", textColor = {200, 0, 200}),
      Line(points = {{-60, 0}, {60, 0}}, color = {200, 0, 200})}),
    Diagram(coordinateSystem(preserveAspectRatio = false, extent = {{-100, -140}, {100, 80}})),__MWORKS(version="26.3.0"));
end AttitudeSignalAdapter;