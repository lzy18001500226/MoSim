within MoSimQuadrotorModel.Experiment.Runners.Graphical;
model NativeSysblockAdapterFullPlantBridgeProbe
  "Diagnostic-only native adapter to Sunray150 plant probe"

  MoSimQuadrotorModel.Control.Adapters.OfficialPidSysblockRotorAdapter controller 
    annotation(Placement(transformation(origin = {-80, 55}, extent = {{-40, -28}, {40, 28}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant 
    annotation(Placement(transformation(origin = {150, 0}, extent = {{-52, -75}, {52, 75}})));
  Modelica.Blocks.Sources.Constant position_ref_source[3](each k = 0);
  Modelica.Blocks.Sources.Constant velocity_ref_source[3](each k = 0);
  Modelica.Blocks.Sources.Constant acceleration_ref_source[3](each k = 0);
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0);
equation
  for i in 1:3 loop
    connect(position_ref_source[i].y, controller.position_ref[i]);
    connect(velocity_ref_source[i].y, controller.velocity_ref[i]);
    connect(acceleration_ref_source[i].y, controller.acceleration_ref[i]);
  end for;
  connect(plant.position, controller.position_mea);
  connect(plant.position, velocity_estimator.u);
  connect(velocity_estimator.y, controller.velocity_mea);
  connect(plant.attitude, controller.attitude_mea);
  connect(controller.rotor_command, plant.rotor_command);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.1, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end NativeSysblockAdapterFullPlantBridgeProbe;