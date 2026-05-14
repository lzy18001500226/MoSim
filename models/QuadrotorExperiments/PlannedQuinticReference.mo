block PlannedQuinticReference
  "Piecewise quintic reference source generated from an accepted A* planning path"
  parameter Integer n_segments(min = 1, max = 5) = 1;
  parameter Real p_x[6] = fill(0.0, 6);
  parameter Real p_y[6] = fill(0.0, 6);
  parameter Real p_z[6] = fill(1.0, 6);
  parameter Real segment_duration[5] = fill(1.0, 5);

  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    annotation(Placement(transformation(origin = {100, 40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput z_ref_rate
    annotation(Placement(transformation(origin = {100, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput yaw_ref
    annotation(Placement(transformation(origin = {100, -40}, extent = {{-10, -10}, {10, 10}})));

protected
  function smoothstep
    input Real tau;
    input Real duration;
    output Real y;
  protected
    Real r;
  algorithm
    r := min(1.0, max(0.0, tau / max(1e-9, duration)));
    y := 10.0 * r ^ 3 - 15.0 * r ^ 4 + 6.0 * r ^ 5;
  end smoothstep;

  function smoothstepDerivative
    input Real tau;
    input Real duration;
    output Real y;
  protected
    Real r;
    Real T;
  algorithm
    T := max(1e-9, duration);
    r := min(1.0, max(0.0, tau / T));
    y := (30.0 * r ^ 2 - 60.0 * r ^ 3 + 30.0 * r ^ 4) / T;
  end smoothstepDerivative;

  function interp
    input Real a;
    input Real b;
    input Real tau;
    input Real duration;
    output Real y;
  algorithm
    y := a + (b - a) * smoothstep(tau, duration);
  end interp;

  function interpRate
    input Real a;
    input Real b;
    input Real tau;
    input Real duration;
    output Real y;
  algorithm
    y := (b - a) * smoothstepDerivative(tau, duration);
  end interpRate;

  Real t1;
  Real t2;
  Real t3;
  Real t4;
  Real t5;

equation
  t1 = segment_duration[1];
  t2 = t1 + segment_duration[2];
  t3 = t2 + segment_duration[3];
  t4 = t3 + segment_duration[4];
  t5 = t4 + segment_duration[5];

  position_command[1] =
    if time <= t1 then interp(p_x[1], p_x[2], time, segment_duration[1])
    else if n_segments <= 1 then p_x[2]
    else if time <= t2 then interp(p_x[2], p_x[3], time - t1, segment_duration[2])
    else if n_segments <= 2 then p_x[3]
    else if time <= t3 then interp(p_x[3], p_x[4], time - t2, segment_duration[3])
    else if n_segments <= 3 then p_x[4]
    else if time <= t4 then interp(p_x[4], p_x[5], time - t3, segment_duration[4])
    else if n_segments <= 4 then p_x[5]
    else if time <= t5 then interp(p_x[5], p_x[6], time - t4, segment_duration[5])
    else p_x[6];
  position_command[2] =
    if time <= t1 then interp(p_y[1], p_y[2], time, segment_duration[1])
    else if n_segments <= 1 then p_y[2]
    else if time <= t2 then interp(p_y[2], p_y[3], time - t1, segment_duration[2])
    else if n_segments <= 2 then p_y[3]
    else if time <= t3 then interp(p_y[3], p_y[4], time - t2, segment_duration[3])
    else if n_segments <= 3 then p_y[4]
    else if time <= t4 then interp(p_y[4], p_y[5], time - t3, segment_duration[4])
    else if n_segments <= 4 then p_y[5]
    else if time <= t5 then interp(p_y[5], p_y[6], time - t4, segment_duration[5])
    else p_y[6];
  position_command[3] =
    if time <= t1 then interp(p_z[1], p_z[2], time, segment_duration[1])
    else if n_segments <= 1 then p_z[2]
    else if time <= t2 then interp(p_z[2], p_z[3], time - t1, segment_duration[2])
    else if n_segments <= 2 then p_z[3]
    else if time <= t3 then interp(p_z[3], p_z[4], time - t2, segment_duration[3])
    else if n_segments <= 3 then p_z[4]
    else if time <= t4 then interp(p_z[4], p_z[5], time - t3, segment_duration[4])
    else if n_segments <= 4 then p_z[5]
    else if time <= t5 then interp(p_z[5], p_z[6], time - t4, segment_duration[5])
    else p_z[6];
  z_ref_rate =
    if time <= t1 then interpRate(p_z[1], p_z[2], time, segment_duration[1])
    else if n_segments <= 1 then 0.0
    else if time <= t2 then interpRate(p_z[2], p_z[3], time - t1, segment_duration[2])
    else if n_segments <= 2 then 0.0
    else if time <= t3 then interpRate(p_z[3], p_z[4], time - t2, segment_duration[3])
    else if n_segments <= 3 then 0.0
    else if time <= t4 then interpRate(p_z[4], p_z[5], time - t3, segment_duration[4])
    else if n_segments <= 4 then 0.0
    else if time <= t5 then interpRate(p_z[5], p_z[6], time - t4, segment_duration[5])
    else 0.0;
  yaw_ref = 0.0;

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {32, 88, 130}, fillColor = {238, 248, 255}, fillPattern = FillPattern.Solid),
      Line(points = {{-80, -20}, {-30, 35}, {20, -5}, {78, 28}}, color = {32, 88, 130}, thickness = 1.2),
      Ellipse(extent = {{-86, -26}, {-74, -14}}, lineColor = {32, 88, 130}, fillColor = {32, 88, 130}, fillPattern = FillPattern.Solid),
      Ellipse(extent = {{72, 22}, {84, 34}}, lineColor = {32, 88, 130}, fillColor = {255, 191, 0}, fillPattern = FillPattern.Solid),
      Text(extent = {{-92, -60}, {92, -86}}, textString = "A* Quintic Ref", textColor = {32, 88, 130})}),
    Diagram(coordinateSystem(extent = {{-120, -80}, {120, 80}})));
end PlannedQuinticReference;
