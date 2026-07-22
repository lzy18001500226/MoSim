within MoSimQuadrotorModel.Dynamics;
model WrapperHoverSmoke
  "Hover smoke for the project-owned Sunray150 dynamics wrapper surface"
  WrapperSurface wrapper;
equation
  wrapper.motor_command = {
    wrapper.dynamics.spin_command_sign[1] * wrapper.dynamics.hover_motor_speed_cmd,
    wrapper.dynamics.spin_command_sign[2] * wrapper.dynamics.hover_motor_speed_cmd,
    wrapper.dynamics.spin_command_sign[3] * wrapper.dynamics.hover_motor_speed_cmd,
    wrapper.dynamics.spin_command_sign[4] * wrapper.dynamics.hover_motor_speed_cmd};
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
  annotation(__MWORKS(hide=true));
end WrapperHoverSmoke;