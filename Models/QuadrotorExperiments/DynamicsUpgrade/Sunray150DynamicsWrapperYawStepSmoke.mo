within QuadrotorExperiments.DynamicsUpgrade;
model Sunray150DynamicsWrapperYawStepSmoke
  "Yaw-step smoke for the project-owned Sunray150 dynamics wrapper surface"
  parameter Real yaw_delta_omega2 = 300
    "Small differential omega^2 command preserving approximate total thrust";
  Real yaw_step;
  Real rotor_speed_mag[4](each unit = "rad/s");
  Sunray150DynamicsWrapperSurface wrapper;
equation
  yaw_step = if time >= 0.05 then yaw_delta_omega2 else 0;
  for i in 1:4 loop
    rotor_speed_mag[i] = sqrt(wrapper.dynamics.hover_motor_speed_cmd * wrapper.dynamics.hover_motor_speed_cmd + wrapper.dynamics.yaw_direction[i] * yaw_step);
    wrapper.motor_command[i] = wrapper.dynamics.spin_command_sign[i] * rotor_speed_mag[i];
  end for;
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
  annotation(__MWORKS(hide=true));
end Sunray150DynamicsWrapperYawStepSmoke;
