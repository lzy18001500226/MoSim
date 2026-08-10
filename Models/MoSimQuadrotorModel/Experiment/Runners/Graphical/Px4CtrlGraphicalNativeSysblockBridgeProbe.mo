within MoSimQuadrotorModel.Experiment.Runners.Graphical;
model Px4CtrlGraphicalNativeSysblockBridgeProbe
  "Capability probe: consume the native graphical PX4CTRL Sysblock from a Modelica parent"

  Modelica.Blocks.Sources.Constant input_source[17](each k = 0);
  Modelica.Blocks.Math.Gain output_sink[8](each k = 1);
  MoSimQuadrotorModel.Control.Implementations.Sysblocks.PX4CTRL_Original_OuterLoop_Graphical_Sysblock controller 
    annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-55, -55}, {55, 55}})),
      __MWORKS(SECInstance = true));

equation
  connect(input_source[1].y, controller.ref_px);
  connect(input_source[2].y, controller.px);
  connect(input_source[3].y, controller.ref_vx);
  connect(input_source[4].y, controller.vx);
  connect(input_source[5].y, controller.ref_ax);
  connect(input_source[6].y, controller.ref_py);
  connect(input_source[7].y, controller.py);
  connect(input_source[8].y, controller.ref_vy);
  connect(input_source[9].y, controller.vy);
  connect(input_source[10].y, controller.ref_ay);
  connect(input_source[11].y, controller.ref_pz);
  connect(input_source[12].y, controller.pz);
  connect(input_source[13].y, controller.ref_vz);
  connect(input_source[14].y, controller.vz);
  connect(input_source[15].y, controller.ref_az);
  connect(input_source[16].y, controller.yaw_mea);
  connect(input_source[17].y, controller.ref_yaw);

  connect(controller.desired_acc_x, output_sink[1].u);
  connect(controller.desired_acc_y, output_sink[2].u);
  connect(controller.desired_acc_z, output_sink[3].u);
  connect(controller.roll_cmd, output_sink[4].u);
  connect(controller.pitch_cmd, output_sink[5].u);
  connect(controller.yaw_cmd, output_sink[6].u);
  connect(controller.collective_thrust_n, output_sink[7].u);
  connect(controller.normalized_thrust, output_sink[8].u);

  annotation(
    experiment(Algorithm = Euler, StartTime = 0, StopTime = 0.1, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end Px4CtrlGraphicalNativeSysblockBridgeProbe;