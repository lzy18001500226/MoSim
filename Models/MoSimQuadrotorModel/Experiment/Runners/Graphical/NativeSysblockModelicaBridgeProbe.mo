within MoSimQuadrotorModel.Experiment.Runners.Graphical;
model NativeSysblockModelicaBridgeProbe
  "Capability probe: consume the native Official PID Sysblock from a Modelica parent"

  Modelica.Blocks.Sources.Constant x_ref(k = 0);
  Modelica.Blocks.Sources.Constant y_ref(k = 0);
  Modelica.Blocks.Sources.Constant z_ref(k = 0);
  Modelica.Blocks.Sources.Constant x_mea(k = 0);
  Modelica.Blocks.Sources.Constant y_mea(k = 0);
  Modelica.Blocks.Sources.Constant z_mea(k = 0);
  Modelica.Blocks.Sources.Constant roll_mea(k = 0);
  Modelica.Blocks.Sources.Constant pitch_mea(k = 0);
  Modelica.Blocks.Sources.Constant yaw_mea(k = 0);
  MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidNativeSysblockCore controller 
    annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-50, -50}, {50, 50}})),
      __MWORKS(SECInstance = true));
  Modelica.Blocks.Math.Gain sink(k = 1) 
    annotation(Placement(transformation(origin = {120, 0}, extent = {{-18, -12}, {18, 12}})));

equation
  connect(x_ref.y, controller.x_ref);
  connect(y_ref.y, controller.y_ref);
  connect(z_ref.y, controller.z_ref);
  connect(x_mea.y, controller.x_mea);
  connect(y_mea.y, controller.y_mea);
  connect(z_mea.y, controller.z_mea);
  connect(roll_mea.y, controller.roll_mea);
  connect(pitch_mea.y, controller.pitch_mea);
  connect(yaw_mea.y, controller.yaw_mea);
  connect(controller.y, sink.u);

  annotation(
    experiment(Algorithm = Euler, StartTime = 0, StopTime = 0.1, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end NativeSysblockModelicaBridgeProbe;