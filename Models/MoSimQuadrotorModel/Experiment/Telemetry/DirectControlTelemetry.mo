within MoSimQuadrotorModel.Experiment.Telemetry;
block DirectControlTelemetry
  "Visible result endpoint for native Official PID reference and mapper diagnostics"

  Modelica.Blocks.Interfaces.RealInput trajectory_bus[6]
    "[velocity(1:3), acceleration(4:6)]" 
    annotation(Placement(
      transformation(origin = {-100, 45}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, 45}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealInput mapper_bus[10]
    "[yaw amplitude, non-yaw(2:5), mapped(6:9), collective error(10)]" 
    annotation(Placement(
      transformation(origin = {-100, -45}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, -45}, extent = {{-8, -8}, {8, 8}})));

  Real trajectory_velocity_command[3] "Recorded trajectory velocity command";
  Real trajectory_acceleration_command[3] "Recorded trajectory acceleration command";
  Real mapper_yaw_amplitude "Recorded yaw-amplitude projection";
  Real mapper_non_yaw_amplitude[4] "Recorded non-yaw mapper amplitudes";
  Real mapper_mapped_amplitude[4] "Recorded physical-yaw mapped amplitudes";
  Real mapper_mapped_collective_amplitude_error
    "Recorded collective-preservation error";

equation
  trajectory_velocity_command = trajectory_bus[1:3];
  trajectory_acceleration_command = trajectory_bus[4:6];
  mapper_yaw_amplitude = mapper_bus[1];
  mapper_non_yaw_amplitude = mapper_bus[2:5];
  mapper_mapped_amplitude = mapper_bus[6:9];
  mapper_mapped_collective_amplitude_error = mapper_bus[10];

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 110, 80},
        fillColor = {242, 255, 250}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 22}, extent = {{-86, 20}, {86, -20}},
        textString = "Direct control", textColor = {0, 110, 80}),
      Text(origin = {0, -36}, extent = {{-86, 18}, {86, -18}},
        textString = "telemetry", textColor = {0, 110, 80})}),
    Diagram(coordinateSystem(extent = {{-120, -80}, {120, 80}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end DirectControlTelemetry;