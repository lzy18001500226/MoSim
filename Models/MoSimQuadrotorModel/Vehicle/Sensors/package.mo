within MoSimQuadrotorModel.Vehicle;
package Sensors "传感器系统"
  extends Modelica.Icons.SensorsPackage;
  model Sensors
    AbsoluteAngles absoluteAngles
      annotation (Placement(transformation(origin = {0.0, 20.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));



    Modelica.Mechanics.MultiBody.Interfaces.Frame_a frame_a
      annotation (Placement(transformation(origin = {-100.0, 0.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}}),
        iconTransformation(origin = {-100.0, 0.0},
          extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Blocks.Interfaces.RealOutput AngleMea[3] "角度测量信号" annotation (Placement(transformation(origin = {110.0, 20.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}}),
      iconTransformation(origin = {110.0, 40.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Interfaces.RealOutput PosMea[3] "位置测量信号" annotation (Placement(transformation(origin = {110.0, -24.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}}),
      iconTransformation(origin = {110.0, -38.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {-7.105427357601002e-15, 0.0},
      lineColor = {200, 200, 200},
      fillColor = {248, 248, 248},
      fillPattern = FillPattern.HorizontalCylinder,
      extent = {{-100.0, -100.0}, {100.0, 100.0}},
      radius = 25.0), Text(origin = {6.0, 0.0},
      lineColor = {136, 136, 136},
      extent = {{-68.0, 60.0}, {68.0, -60.0}},
      textString = "Sensors",
      textStyle = {TextStyle.None},
      textColor = {136, 136, 136})}));
    AbsolutePosition absolutePosition1(
      resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.world) annotation (Placement(transformation(origin = {0.0, -23.974440894568694},
        extent = {{10.0, 10.0}, {-10.0, -10.0}},
        rotation = 180.0)));
  equation
    connect(frame_a, absoluteAngles.frame_a)
      annotation (Line(origin = {-55.0, 10.0},
        points = {{-45.0, -10.0}, {-5.0, -10.0}, {-5.0, 10.0}, {45.0, 10.0}},
        color = {95, 95, 95},
        thickness = 0.5));

    connect(absoluteAngles.angles, AngleMea)
      annotation (Line(origin = {61.0, 19.0},
        points = {{-50.0, 1.0}, {49.0, 1.0}},
        color = {0, 0, 127}));
    connect(absolutePosition1.frame_a, frame_a)
      annotation (Line(origin = {-55.0, -12.0},
        points = {{45.0, -12.0}, {-5.0, -12.0}, {-5.0, 12.0}, {-45.0, 12.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(absolutePosition1.r, PosMea)
      annotation (Line(origin = {61.0, -23.0},
        points = {{-50.0, -1.0}, {49.0, -1.0}},
        color = {0, 0, 127}));
  end Sensors;
  model AbsoluteAngles
    "Measure absolute angles between frame connector and the world frame"
    extends Modelica.Mechanics.MultiBody.Sensors.Internal.PartialAbsoluteSensor;
    import SI = Modelica.SIunits;
    Modelica.Blocks.Interfaces.RealOutput angles[3](
      each final quantity = "Angle",
      each final unit = "rad",
      each displayUnit = "deg")
      "Angles to rotate world frame into frame_a via 'sequence'"
      annotation (Placement(transformation(
        origin = {110, 0},
        extent = {{-10, -10}, {10, 10}})));
    parameter Modelica.Mechanics.MultiBody.Types.RotationSequence sequence(
      min = {1, 1, 1},
      max = {3, 3, 3}) = {1, 2, 3}
      "Angles are returned to rotate world frame around axes sequence[1], sequence[2] and finally sequence[3] into frame_a"
      annotation (Evaluate = true);
    parameter Modelica.Units.SI.Angle guessAngle1 = 0
      "Select angles[1] such that abs(angles[1] - guessAngle1) is a minimum";
  equation
    frame_a.f = zeros(3);
    frame_a.t = zeros(3);
    angles = Modelica.Mechanics.MultiBody.Frames.axesRotationsAngles(
      frame_a.R,
      sequence,
      guessAngle1);
    annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0}), graphics = {Text(origin = {4.5, 122.0},
      lineColor = {0, 0, 255},
      extent = {{-130.5, -24.0}, {130.5, 24.0}},
      textString = "%name",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 255}), Line(origin = {85.0, 0.0},
      points = {{-15.0, 0.0}, {15.0, 0.0}},
      color = {0, 0, 127}), Text(origin = {117.0, -33.0},
      extent = {{-55.0, 11.0}, {55.0, -11.0}},
      textString = "angles")}),
      Documentation(info = "<html>
<p>
This model determines the 3 angles to rotate the world frame
into frame_a along the axes defined by parameter <strong>sequence</strong>.
For example, if sequence = {3,1,2} then the world frame is
rotated around angles[1] along the z-axis, afterwards it is rotated
around angles[2] along the x-axis, and finally it is rotated around
angles[3] along the y-axis and is then identical to frame_a.
The 3 angles are returned in the range
</p>
<pre>
  -<font face=\"Symbol\">p</font> &lt;= angles[i] &lt;= <font face=\"Symbol\">p</font>
</pre>
<p>
There are <strong>two solutions</strong> for \"angles[1]\" in this range.
Via parameter <strong>guessAngle1</strong> (default = 0) the
returned solution is selected such that |angles[1] - guessAngle1| is
minimal. The transformation matrix between the world frame and
frame_a may be in a singular configuration with respect to \"sequence\", i.e.,
there is an infinite number of angle values leading to the same relative
transformation matrix. In this case, the returned solution is
selected by setting angles[1] = guessAngle1. Then angles[2]
and angles[3] can be uniquely determined in the above range.
</p>
<p>
The parameter <strong>sequence</strong> has the restriction that
only values 1,2,3 can be used and that sequence[1] &ne; sequence[2]
and sequence[2] &ne; sequence[3]. Often used values are:
</p>
<pre>
sequence = <strong>{1,2,3}</strong>  // Cardan or Tait-Bryan angle sequence
         = <strong>{3,1,3}</strong>  // Euler angle sequence
         = <strong>{3,2,1}</strong>
</pre>
</html>"));
  end AbsoluteAngles;
  model AbsolutePosition
    "Measure absolute position vector of the origin of a frame connector"
    extends Modelica.Mechanics.MultiBody.Sensors.Internal.PartialAbsoluteSensor;

    Modelica.Blocks.Interfaces.RealOutput r[3](
      each final quantity = "Length",
      each final unit = "m")
      "Absolute position vector resolved in frame defined by resolveInFrame"
      annotation (Placement(transformation(
        extent = {{-10, -10}, {10, 10}},
        origin = {110, 0})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_resolve frame_resolve if
      resolveInFrame == Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.frame_resolve
      "Coordinate system in which output vector r is optionally resolved"
      annotation (Placement(transformation(extent = {{-16, -16}, {16, 16}},
        rotation = -90,
        origin = {0, -100})));

    parameter Modelica.Mechanics.MultiBody.Types.ResolveInFrameA resolveInFrame =
      Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.frame_a
      "Frame in which output vector r shall be resolved (world, frame_a, or frame_resolve)";
  protected
    Modelica.Mechanics.MultiBody.Sensors.Internal.BasicAbsolutePosition position(resolveInFrame = resolveInFrame)
      annotation (Placement(transformation(extent = {{-10, -10}, {10, 10}})));

    Modelica.Mechanics.MultiBody.Interfaces.ZeroPosition zeroPosition if
      not (resolveInFrame == Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.frame_resolve)
      annotation (Placement(transformation(extent = {{20, -40}, {40, -20}})));
  equation
    connect(position.frame_resolve, frame_resolve) annotation (Line(
      points = {{0, -10}, {0, -100}},
      color = {95, 95, 95},
      pattern = LinePattern.Dot));
    connect(zeroPosition.frame_resolve, position.frame_resolve)
      annotation (Line(
        points = {{20, -30}, {0, -30}, {0, -10}},
        color = {95, 95, 95},
        pattern = LinePattern.Dot));
    connect(position.r, r) annotation (Line(
      points = {{11, 0}, {110, 0}}, color = {0, 0, 127}));
    connect(position.frame_a, frame_a) annotation (Line(
      points = {{-10, 0}, {-100, 0}},
      color = {95, 95, 95},
      thickness = 0.5));
    annotation (Icon(coordinateSystem(
      preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}}), graphics = {
      Line(
      points = {{70, 0}, {100, 0}},
      color = {0, 0, 127}),
      Text(
      extent = {{-127, 95}, {134, 143}},
      textString = "%name",
      lineColor = {0, 0, 255}),
      Text(
      extent = {{62, 46}, {146, 16}},
      textString = "r"),
      Text(
      extent = {{15, -67}, {146, -92}},
      lineColor = {95, 95, 95},
      textString = "resolve"),
      Line(
      points = {{0, -96}, {0, -96}, {0, -70}, {0, -70}},
      pattern = LinePattern.Dot)}),
      Documentation(info = "<html>
<p>
The absolute position vector of the origin of frame_a is
determined and provided at the output signal connector <strong>r</strong>.
</p>

<p>
Via parameter <strong>resolveInFrame</strong> it is defined, in which frame
the position vector is resolved:
</p>

<table border=1 cellspacing=0 cellpadding=2>
<tr><th><strong>resolveInFrame =<br>Types.ResolveInFrameA.</strong></th><th><strong>Meaning</strong></th></tr>
<tr><td>world</td>
  <td>Resolve vector in world frame</td></tr>

<tr><td>frame_a</td>
  <td>Resolve vector in frame_a</td></tr>

<tr><td>frame_resolve</td>
  <td>Resolve vector in frame_resolve</td></tr>
</table>

<p>
If resolveInFrame = Types.ResolveInFrameA.frame_resolve, the conditional connector
\"frame_resolve\" is enabled and r is resolved in the frame, to
which frame_resolve is connected. Note, if this connector is enabled, it must
be connected.
</p>

<h4>Example</h4>
<p>
If resolveInFrame = Types.ResolveInFrameA.frame_a, the output vector is
computed as:
</p>

<blockquote><pre>
r = MultiBody.Frames.resolve2(frame_a.R, frame_b.r_0);
</pre></blockquote>
</html>"));
  end AbsolutePosition;
  model SpeedSensor
    "Ideal sensor to measure the absolute flange angular velocity"

    extends Modelica.Mechanics.Rotational.Interfaces.PartialAbsoluteSensor;
    Modelica.Blocks.Interfaces.RealOutput w(unit = "rad/s")
      "Absolute angular velocity of flange as output signal" annotation (
        Placement(transformation(extent = {{100, -10}, {120, 10}})));
  equation
    w = der(flange.phi);
    annotation (
      Documentation(info = "<html>
<p>
Measures the <strong>absolute angular velocity w</strong> of a flange in an ideal
way and provides the result as output signal <strong>w</strong>
(to be further processed with blocks of the Modelica.Blocks library).
</p>
</html>"), Icon(coordinateSystem(
        preserveAspectRatio = true,
        extent = {{-100, -100}, {100, 100}}), graphics = {Text(
        extent = {{70, -30}, {120, -70}},
        textString = "w")}));
  end SpeedSensor;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Sensors;
