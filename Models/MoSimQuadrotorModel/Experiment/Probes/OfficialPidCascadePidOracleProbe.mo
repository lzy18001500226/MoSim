within MoSimQuadrotorModel.Experiment.Probes;
model OfficialPidCascadePidOracleProbe
  "Compare cascade PID commands against an Official PID controlled shared plant"

  MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter official_pid
    annotation(Placement(transformation(origin = {-90, 35}, extent = {{-32, -26}, {32, 26}})));
  MoSimQuadrotorModel.Control.Adapters.CascadePidAttitudeThrustAdapter cascade_pid
    annotation(Placement(transformation(origin = {-90, -40}, extent = {{-32, -26}, {32, 26}})));
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator cascade_allocator
    annotation(Placement(transformation(origin = {10, -40}, extent = {{-32, -26}, {32, 26}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant
    annotation(Placement(transformation(origin = {115, 0}, extent = {{-42, -58}, {42, 58}})));

  Real position[3];
  Real attitude[3];
  Real official_rotor_command[4];
  Real cascade_rotor_command[4];
  Real rotor_command_delta[4];
  Real max_abs_rotor_command_delta;
  Real cascade_attitude_ref[3];
  Real cascade_collective_thrust_delta;
  Real cascade_desired_collective_thrust_n;
  Real cascade_status_code;

equation
  official_pid.position_ref = {0.0, 0.0, 0.0};
  cascade_pid.position_ref = {0.0, 0.0, 0.0};
  connect(plant.position, official_pid.position_mea)
    annotation(Line(points = {{73, -18}, {52, -18}, {52, 15}, {-90, 15}, {-90, 9}}, color = {0, 0, 127}));
  connect(plant.attitude, official_pid.attitude_mea)
    annotation(Line(points = {{73, -30}, {46, -30}, {46, 2}, {-90, 2}, {-90, 9}}, color = {0, 0, 127}));
  connect(plant.position, cascade_pid.position_mea)
    annotation(Line(points = {{73, -18}, {52, -18}, {52, -65}, {-90, -65}, {-90, -66}}, color = {0, 0, 127}));
  connect(plant.attitude, cascade_pid.attitude_mea)
    annotation(Line(points = {{73, -30}, {45, -30}, {45, -74}, {-90, -74}, {-90, -66}}, color = {0, 0, 127}));
  connect(cascade_pid.attitude_ref, cascade_allocator.attitude_ref)
    annotation(Line(points = {{-58, -27}, {-22, -27}}, color = {0, 0, 127}));
  connect(plant.attitude, cascade_allocator.attitude_mea)
    annotation(Line(points = {{73, -30}, {45, -30}, {45, -47}, {10, -47}, {10, -66}}, color = {0, 0, 127}));
  connect(cascade_pid.collective_thrust_delta, cascade_allocator.collective_thrust_delta)
    annotation(Line(points = {{-58, -53}, {-22, -53}}, color = {0, 0, 127}));
  connect(official_pid.rotor_command, plant.rotor_command)
    annotation(Line(points = {{-58, 35}, {73, 35}}, color = {0, 0, 127}));

  position = plant.position;
  attitude = plant.attitude;
  official_rotor_command = official_pid.rotor_command;
  cascade_rotor_command = cascade_allocator.rotor_command;
  rotor_command_delta = cascade_rotor_command - official_rotor_command;
  max_abs_rotor_command_delta = max(max(abs(rotor_command_delta[1]), abs(rotor_command_delta[2])),
    max(abs(rotor_command_delta[3]), abs(rotor_command_delta[4])));
  cascade_attitude_ref = cascade_pid.attitude_ref;
  cascade_collective_thrust_delta = cascade_pid.collective_thrust_delta;
  cascade_desired_collective_thrust_n = cascade_pid.desired_collective_thrust_n;
  cascade_status_code = cascade_pid.status_code;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.002),
    Diagram(coordinateSystem(extent = {{-145, -100}, {170, 85}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end OfficialPidCascadePidOracleProbe;
