within QuadrotorExperiments.DynamicsUpgrade;
model Sunray150PhysicalWrenchHoverSmoke
  "Hover smoke for the project-owned physical wrench frame adapter"
  Sunray150PhysicalWrenchFrameAdapter adapter;
equation
  adapter.wrapper.motor_command = {
    adapter.wrapper.dynamics.spin_command_sign[1] * adapter.wrapper.dynamics.hover_motor_speed_cmd,
    adapter.wrapper.dynamics.spin_command_sign[2] * adapter.wrapper.dynamics.hover_motor_speed_cmd,
    adapter.wrapper.dynamics.spin_command_sign[3] * adapter.wrapper.dynamics.hover_motor_speed_cmd,
    adapter.wrapper.dynamics.spin_command_sign[4] * adapter.wrapper.dynamics.hover_motor_speed_cmd};
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
  annotation(__MWORKS(hide=true));
end Sunray150PhysicalWrenchHoverSmoke;
