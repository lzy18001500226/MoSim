within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorOfficialPidDynamicParityProbe
  "Dynamic measured-attitude parity probe for official PID and offline allocator"

  parameter Real roll_amplitude = 0.06;
  parameter Real pitch_amplitude = 0.04;
  parameter Real yaw_amplitude = 0.08;
  parameter Real roll_frequency_hz = 1.5;
  parameter Real pitch_frequency_hz = 1.1;
  parameter Real yaw_frequency_hz = 0.7;
  parameter Real offline_derivative_time_constant_s = 0.02;
  MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter official_pid;
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator offline_allocator(
    body_rate_filter_time_constant_s = offline_derivative_time_constant_s);
  Real roll_measurement;
  Real pitch_measurement;
  Real yaw_measurement;
  Real official_rotor_command[4];
  Real offline_rotor_command[4];
  Real rotor_command_delta[4];
  Real max_abs_rotor_command_delta;

equation
  roll_measurement = roll_amplitude * sin(2 * Modelica.Constants.pi * roll_frequency_hz * time);
  pitch_measurement = pitch_amplitude * sin(2 * Modelica.Constants.pi * pitch_frequency_hz * time);
  yaw_measurement = yaw_amplitude * sin(2 * Modelica.Constants.pi * yaw_frequency_hz * time);

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
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1.0, Tolerance = 0.0001,
      Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end AllocatorOfficialPidDynamicParityProbe;