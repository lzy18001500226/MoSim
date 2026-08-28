within MoSimQuadrotorModel.Control.Adapters;
model OfficialPidSysblockAttitudeThrustAdapter
  "Native Official PID Sysblock outer-loop at the ATTITUDE_THRUST boundary"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter Real legacy_hover_speed_rad_s = 13.985413115099604
    "Calibration speed used by the native graphical mapper";
  parameter Real hover_speed_rad_s =
    MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s;
  parameter Real visual_thrust_coefficient =
    MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_visual_thrust_coefficient;
  parameter Real command_scale = hover_speed_rad_s / legacy_hover_speed_rad_s
    "Same amplitude-to-rotor-speed scale as OfficialPidSysblockMapper";
  parameter Real collective_thrust_slope_n_per_rad_s =
    8 * visual_thrust_coefficient * hover_speed_rad_s;
  parameter Real native_collective_thrust_n_per_amplitude =
    collective_thrust_slope_n_per_rad_s * command_scale
    "Maps the graphical common-mode amplitude to physical collective thrust";
  parameter Real yaw_reference_rad = 0
    "The native graphical core has a fixed zero-yaw outer reference";

  MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidSysblockCore
    controller_core
    annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-82, -105}, {82, 105}})),
      __MWORKS(SECInstance = true, PortLabels(labelType = "PortName")));
  Modelica.Blocks.Math.Gain native_collective_thrust_mapper(
    k = native_collective_thrust_n_per_amplitude)
    "Visible hybrid boundary scale after the Sysblock's graphical z command"
    annotation(Placement(transformation(origin = {105, -75}, extent = {{-15, -15}, {15, 15}})));

equation
  connect(position_ref[1], controller_core.x_ref)
    annotation(Line(points = {{-150, 90}, {-82, 90}}, color = {0, 0, 127}));
  connect(position_ref[2], controller_core.y_ref)
    annotation(Line(points = {{-150, 90}, {-105, 90}, {-105, 45}, {-82, 45}}, color = {0, 0, 127}));
  connect(position_ref[3], controller_core.z_ref)
    annotation(Line(points = {{-150, 90}, {-115, 90}, {-115, 0}, {-82, 0}}, color = {0, 0, 127}));
  connect(position_mea[1], controller_core.x_mea)
    annotation(Line(points = {{-150, 0}, {-82, 20}}, color = {0, 100, 150}));
  connect(position_mea[2], controller_core.y_mea)
    annotation(Line(points = {{-150, 0}, {-105, 0}, {-105, -25}, {-82, -25}}, color = {0, 100, 150}));
  connect(position_mea[3], controller_core.z_mea)
    annotation(Line(points = {{-150, 0}, {-115, 0}, {-115, -50}, {-82, -50}}, color = {0, 100, 150}));
  connect(attitude_mea[1], controller_core.roll_mea)
    annotation(Line(points = {{-150, -90}, {-115, -90}, {-115, -80}, {-82, -80}}, color = {0, 100, 150}));
  connect(attitude_mea[2], controller_core.pitch_mea)
    annotation(Line(points = {{-150, -90}, {-105, -90}, {-105, -105}, {-82, -105}}, color = {0, 100, 150}));
  connect(attitude_mea[3], controller_core.yaw_mea)
    annotation(Line(points = {{-150, -90}, {-95, -90}, {-95, -130}, {-82, -130}}, color = {0, 100, 150}));

  // These are direct graphical-core signals, not a parallel PID reimplementation.
  // OfflineAttitudeRateAllocator uses the matching roll sign convention.
  connect(controller_core.roll_ref_limit.y, attitude_ref[1])
    annotation(Line(points = {{-45, 25}, {45, 25}, {45, 75}, {150, 75}}, color = {0, 0, 127}));
  connect(controller_core.pitch_ref_limit.y, attitude_ref[2])
    annotation(Line(points = {{-45, 45}, {55, 45}, {55, 25}, {150, 25}}, color = {0, 0, 127}));
  attitude_ref[3] = yaw_reference_rad;
  // MWORKS accepts graphical-block variables only in connection equations in
  // a hybrid model, so retain this scale as an explicit visible boundary block.
  connect(controller_core.thrust_command.y, native_collective_thrust_mapper.u)
    annotation(Line(points = {{-45, -15}, {70, -15}, {70, -75}, {90, -75}}, color = {0, 0, 127}));
  connect(native_collective_thrust_mapper.y, collective_thrust_delta)
    annotation(Line(points = {{120, -75}, {150, -75}}, color = {0, 0, 127}));

  annotation(
    Documentation(info = "<html><p>Hybrid boundary adapter for the native graphical Official PID Sysblock. Roll, pitch, and vertical-command signals are read directly from visible blocks in <code>OfficialPidSysblockCore</code>; this model does not reproduce the PID law in Modelica or C.</p><p>The vertical amplitude is converted with the same hover-speed, thrust-coefficient, and command-scale chain used by <code>OfficialPidSysblockMapper</code>. The existing core has a fixed graphical yaw-reference block, so formal use exposes the fixed yaw parameter and RT1 carries its protocol yaw separately. This is MWORKS-only control-path evidence, not PX4/Gazebo flight evidence.</p></html>"),
    Diagram(coordinateSystem(extent = {{-170, -160}, {170, 160}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 130, 0},
        fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 25}, extent = {{-90, 18}, {90, -18}},
        textString = "Official PID", textColor = {0, 130, 0}),
      Text(origin = {0, -25}, extent = {{-90, 18}, {90, -18}},
        textString = "SYSBLOCK RT1", textColor = {0, 100, 150})}),
    __MWORKS(version = "26.3.0"));
end OfficialPidSysblockAttitudeThrustAdapter;
