within MoSimQuadrotorModel.Planning.Scenarios;
block PlannedQuinticReference
  "Piecewise quintic reference source generated from an accepted A* planning path"
  parameter Integer n_segments(min = 1, max = 90) = 1;
  parameter Real p_x[91] = fill(0.0, 91);
  parameter Real p_y[91] = fill(0.0, 91);
  parameter Real p_z[91] = fill(1.0, 91);
  parameter Real segment_duration[90] = fill(1.0, 90);

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

  function piecewiseInterp
    input Real value[91];
    input Real query_time;
    input Integer n_segments;
    input Real segment_duration[90];
    output Real y;
  protected
    Real elapsed;
    Boolean found;
  algorithm
    elapsed := 0.0;
    y := value[1];
    found := false;
    for i in 1:90 loop
      if not found and i <= n_segments then
        if query_time <= elapsed + segment_duration[i] then
          y := interp(value[i], value[i + 1], query_time - elapsed, segment_duration[i]);
          found := true;
        else
          elapsed := elapsed + segment_duration[i];
          y := value[i + 1];
        end if;
      end if;
    end for;
  end piecewiseInterp;

  function piecewiseRate
    input Real value[91];
    input Real query_time;
    input Integer n_segments;
    input Real segment_duration[90];
    output Real y;
  protected
    Real elapsed;
    Boolean found;
  algorithm
    elapsed := 0.0;
    y := 0.0;
    found := false;
    for i in 1:90 loop
      if not found and i <= n_segments then
        if query_time <= elapsed + segment_duration[i] then
          y := interpRate(value[i], value[i + 1], query_time - elapsed, segment_duration[i]);
          found := true;
        else
          elapsed := elapsed + segment_duration[i];
          y := 0.0;
        end if;
      end if;
    end for;
  end piecewiseRate;

equation
  position_command[1] = piecewiseInterp(p_x, time, n_segments, segment_duration);
  position_command[2] = piecewiseInterp(p_y, time, n_segments, segment_duration);
  position_command[3] = piecewiseInterp(p_z, time, n_segments, segment_duration);
  z_ref_rate = piecewiseRate(p_z, time, n_segments, segment_duration);
  yaw_ref = 0.0;

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {32, 88, 130}, fillColor = {238, 248, 255}, fillPattern = FillPattern.Solid),
      Line(points = {{-80, -20}, {-30, 35}, {20, -5}, {78, 28}}, color = {32, 88, 130}, thickness = 1.2),
      Ellipse(extent = {{-86, -26}, {-74, -14}}, lineColor = {32, 88, 130}, fillColor = {32, 88, 130}, fillPattern = FillPattern.Solid),
      Ellipse(extent = {{72, 22}, {84, 34}}, lineColor = {32, 88, 130}, fillColor = {255, 191, 0}, fillPattern = FillPattern.Solid),
      Text(extent = {{-92, -60}, {92, -86}}, textString = "A* Quintic Ref", textColor = {32, 88, 130})}),
    Diagram(coordinateSystem(extent = {{-120, -80}, {120, 80}})));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end PlannedQuinticReference;