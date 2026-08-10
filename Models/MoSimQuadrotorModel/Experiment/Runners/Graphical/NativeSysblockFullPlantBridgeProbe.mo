within MoSimQuadrotorModel.Experiment.Runners.Graphical;
model NativeSysblockFullPlantBridgeProbe
  "Diagnostic-only direct native Sysblock to Sunray150 plant probe"

  Modelica.Blocks.Sources.Constant x_ref(k = 0);
  Modelica.Blocks.Sources.Constant y_ref(k = 0);
  Modelica.Blocks.Sources.Constant z_ref(k = 0);
  MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidSysblockRunner controller 
    annotation(
      Placement(transformation(origin = {-120, 0}, extent = {{-70, -130}, {70, 130}})),
      __MWORKS(SECInstance = true));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant 
    annotation(Placement(transformation(origin = {150, 0}, extent = {{-60, -90}, {60, 90}})));

equation
  connect(x_ref.y, controller.x_ref);
  connect(y_ref.y, controller.y_ref);
  connect(z_ref.y, controller.z_ref);
  connect(plant.position[1], controller.x_mea);
  connect(plant.position[2], controller.y_mea);
  connect(plant.position[3], controller.z_mea);
  connect(plant.attitude[1], controller.roll_mea);
  connect(plant.attitude[2], controller.pitch_mea);
  connect(plant.attitude[3], controller.yaw_mea);
  connect(controller.rotor_command_1, plant.rotor_command[1]);
  connect(controller.rotor_command_2, plant.rotor_command[2]);
  connect(controller.rotor_command_3, plant.rotor_command[3]);
  connect(controller.rotor_command_4, plant.rotor_command[4]);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.1, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end NativeSysblockFullPlantBridgeProbe;