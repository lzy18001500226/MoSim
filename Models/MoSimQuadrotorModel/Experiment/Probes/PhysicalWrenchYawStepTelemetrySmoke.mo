within MoSimQuadrotorModel.Experiment.Probes;
model PhysicalWrenchYawStepTelemetrySmoke
  "Yaw-step telemetry for the project-owned force-and-torque physical path"

  parameter Real yaw_delta_omega2 = 300
    "Differential omega squared command preserving total thrust";
  Real yaw_step;
  Real rotor_speed_magnitude[4](each unit = "rad/s");
  MoSimQuadrotorModel.Vehicle.PhysicalWrenchAdapter adapter;
  MoSimQuadrotorModel.Vehicle.Sensors.AbsoluteAngles angle_sensor;
  Real attitude[3];
  Real applied_yaw_torque(unit = "N.m");
  Real total_thrust(unit = "N");
  Real rotor_speed[4](each unit = "rad/s");

equation
  yaw_step = if time >= 0.05 then yaw_delta_omega2 else 0;
  for i in 1:4 loop
    rotor_speed_magnitude[i] = sqrt(
      adapter.wrapper.dynamics.hover_motor_speed_cmd * adapter.wrapper.dynamics.hover_motor_speed_cmd
        + adapter.wrapper.dynamics.yaw_direction[i] * yaw_step);
    adapter.wrapper.motor_command[i] =
      adapter.wrapper.dynamics.spin_command_sign[i] * rotor_speed_magnitude[i];
    rotor_speed[i] = adapter.wrapper.dynamics.omega[i];
  end for;
  connect(angle_sensor.frame_a, adapter.body.frame_a);
  attitude = angle_sensor.angles;
  applied_yaw_torque = adapter.applied_yaw_torque_body;
  total_thrust = adapter.wrapper_total_thrust;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.15, Tolerance = 0.0001,
      Interval = 0.0001),
    __MWORKS(version = "26.3.0"));
end PhysicalWrenchYawStepTelemetrySmoke;
