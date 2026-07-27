within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorOfficialPidParityProbe
  "Fixed-input parity probe for the Official PID mixer and offline attitude allocator"

  parameter Real roll_measurement = 0.08;
  parameter Real pitch_measurement = -0.06;
  parameter Real yaw_measurement = 0.10;
  MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter official_pid;
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator offline_allocator;
  Real official_rotor_command[4];
  Real offline_rotor_command[4];
  Real rotor_command_delta[4];
  Real max_abs_rotor_command_delta;

equation
  official_pid.position_ref = {0.0, 0.0, 0.0};
  official_pid.position_mea = {0.0, 0.0, 0.0};
  official_pid.velocity_mea = {0.0, 0.0, 0.0};
  official_pid.attitude_mea = {roll_measurement, pitch_measurement, yaw_measurement};

  offline_allocator.attitude_ref = {0.0, 0.0, 0.0};
  offline_allocator.attitude_mea = {roll_measurement, pitch_measurement, yaw_measurement};
  offline_allocator.collective_thrust_delta = 0.0;

  official_rotor_command = official_pid.rotor_command;
  offline_rotor_command = offline_allocator.rotor_command;
  rotor_command_delta = official_rotor_command - offline_rotor_command;
  max_abs_rotor_command_delta = max(max(abs(rotor_command_delta[1]), abs(rotor_command_delta[2])),
    max(abs(rotor_command_delta[3]), abs(rotor_command_delta[4])));

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end AllocatorOfficialPidParityProbe;
