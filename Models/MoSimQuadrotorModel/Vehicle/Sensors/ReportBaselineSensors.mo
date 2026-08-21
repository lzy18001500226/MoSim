within MoSimQuadrotorModel.Vehicle.Sensors;
model ReportBaselineSensors
  "Report-era position and attitude sensor footprint for EquationBridge replay"

  AbsoluteAngles absoluteAngles;
  Modelica.Mechanics.MultiBody.Interfaces.Frame_a frame_a;
  Modelica.Blocks.Interfaces.RealOutput AngleMea[3] "Angle measurement";
  Modelica.Blocks.Interfaces.RealOutput PosMea[3] "Position measurement";
  Modelica.Blocks.Interfaces.RealOutput VelMea[3](each unit = "m/s")
    "World-frame linear velocity measurement";
  Modelica.Blocks.Interfaces.RealOutput BodyRateMea[3](each unit = "rad/s")
    "Body-frame angular velocity measurement";
  Modelica.Blocks.Interfaces.RealOutput QuatMea[4]
    "World-to-body orientation quaternion in Modelica order {x, y, z, w}";
  AbsolutePosition absolutePosition1(
    resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.world);
  Modelica.Mechanics.MultiBody.Sensors.AbsoluteVelocity absoluteVelocity(
    resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.world);
  Modelica.Mechanics.MultiBody.Sensors.AbsoluteAngularVelocity absoluteAngularVelocity(
    resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.frame_a);
  annotation(__MWORKS(version="26.3.0"));

equation
  connect(frame_a, absoluteAngles.frame_a);
  connect(absoluteAngles.angles, AngleMea);
  connect(absolutePosition1.frame_a, frame_a);
  connect(absolutePosition1.r, PosMea);
  connect(absoluteVelocity.frame_a, frame_a);
  connect(absoluteVelocity.v, VelMea);
  connect(absoluteAngularVelocity.frame_a, frame_a);
  connect(absoluteAngularVelocity.w, BodyRateMea);
  QuatMea = Modelica.Mechanics.MultiBody.Frames.to_Q(frame_a.R);
end ReportBaselineSensors;