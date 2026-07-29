within MoSimQuadrotorModel.Dynamics;
model YawStepSmoke
  "Yaw-step smoke for the experimental Sunray150 rotor dynamics upgrade"
  parameter Real yaw_delta_omega2 = 300
    "Small differential omega^2 command preserving approximate total thrust";
  Real yaw_step;
  Real rotor_speed_mag[4](each unit = "rad/s");
  RotorActuatorCore dynamics;
equation
  yaw_step = if time >= 0.05 then yaw_delta_omega2 else 0;
  for i in 1:4 loop
    rotor_speed_mag[i] = sqrt(dynamics.hover_motor_speed_cmd * dynamics.hover_motor_speed_cmd + dynamics.yaw_direction[i] * yaw_step);
    dynamics.motor_command[i] = dynamics.spin_command_sign[i] * rotor_speed_mag[i];
  end for;
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
  annotation(__MWORKS(hide=true));
end YawStepSmoke;