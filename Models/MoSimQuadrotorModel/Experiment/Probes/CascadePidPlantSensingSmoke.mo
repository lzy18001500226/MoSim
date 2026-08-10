within MoSimQuadrotorModel.Experiment.Probes;
model CascadePidPlantSensingSmoke
  "Plant-to-cascade-PID sensing-only startup isolation"

  MoSimQuadrotorModel.Control.Adapters.CascadePidAttitudeThrustAdapter controller;
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant;
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0);
  Real attitude_ref[3];
  Real collective_thrust_delta;
  Real status_code;

equation
  plant.rotor_command = {MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s,
    -MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s,
    MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s,
    -MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s};
  controller.position_ref = {1.0, -0.5, 0.8};
  connect(plant.position, controller.position_mea);
  connect(plant.position, velocity_estimator.u);
  connect(velocity_estimator.y, controller.velocity_mea);
  connect(plant.attitude, controller.attitude_mea);
  attitude_ref = controller.attitude_ref;
  collective_thrust_delta = controller.collective_thrust_delta;
  status_code = controller.status_code;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end CascadePidPlantSensingSmoke;