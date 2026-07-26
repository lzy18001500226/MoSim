within MoSimQuadrotorModel.Vehicle.Dynamics;
model RotorEffectivenessSmoke
  "Single-rotor effectiveness-loss smoke for the Sunray150 rotor dynamics core"
  parameter Integer degraded_rotor_index = 1
    "1-based rotor index used for the smoke degradation";
  parameter Real degraded_rotor_thrust_effectiveness = 0.85
    "Smoke value only; not an identified Sunray150 fault model";
  parameter Real expected_nominal_total_thrust(unit = "N") = 9.80665
    "Reference hover thrust for the default mass seed";
  RotorActuatorCore dynamics(
    thrust_effectiveness = {
      if degraded_rotor_index == 1 then degraded_rotor_thrust_effectiveness else 1,
      if degraded_rotor_index == 2 then degraded_rotor_thrust_effectiveness else 1,
      if degraded_rotor_index == 3 then degraded_rotor_thrust_effectiveness else 1,
      if degraded_rotor_index == 4 then degraded_rotor_thrust_effectiveness else 1});
  Real total_thrust_loss(unit = "N")
    "Nominal hover thrust minus degraded total thrust";
  Real roll_moment_imbalance(unit = "N.m")
    "Body roll moment caused by asymmetric thrust effectiveness";
  Real pitch_moment_imbalance(unit = "N.m")
    "Body pitch moment caused by asymmetric thrust effectiveness";
  Real yaw_moment_imbalance(unit = "N.m")
    "Body yaw moment caused by asymmetric thrust/reaction effectiveness";
equation
  dynamics.motor_command = {
    dynamics.spin_command_sign[1] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[2] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[3] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[4] * dynamics.hover_motor_speed_cmd};
  total_thrust_loss = expected_nominal_total_thrust - dynamics.total_thrust;
  roll_moment_imbalance = dynamics.total_moment_body[1];
  pitch_moment_imbalance = dynamics.total_moment_body[2];
  yaw_moment_imbalance = dynamics.total_moment_body[3];
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end RotorEffectivenessSmoke;
