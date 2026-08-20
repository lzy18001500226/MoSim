within MoSimQuadrotorModel.Guidance.Trajectories;
model OpenBlocksUav2Reference
  "UAV 2 trajectory: historical A* planning from (-43, -26) to (43, 26)"

  extends PlannedQuinticReference(
    n_segments = 53,
    p_x = {
      -43.00, -43.00, -43.00, -41.87, -38.12, -37.02,
      -34.40, -32.38, -30.36, -29.00, -27.72, -25.44,
      -23.41, -22.11, -18.39, -17.17, -14.73, -12.76,
      -11.66, -8.14, -7.12, -5.14, -3.96, -4.02,
      -3.70, -3.16, -1.00, 1.75, 3.39, 3.70,
      6.94, 8.17, 9.07, 9.38, 11.55, 13.75,
      14.10, 16.42, 18.21, 19.96, 21.61, 23.80,
      25.58, 27.26, 29.63, 31.75, 33.65, 34.90,
      36.61, 37.79, 38.97, 40.56, 42.91, 43.00},
    p_y = {
      -26.00, -26.00, -26.00, -25.83, -25.26, -25.09,
      -24.73, -24.45, -22.71, -21.21, -20.68, -19.53,
      -18.09, -18.03, -17.90, -17.93, -17.62, -16.56,
      -16.08, -15.06, -14.70, -12.31, -10.75, -9.20,
      -6.71, -6.15, -3.89, -1.02, 0.70, 0.92,
      1.50, 2.25, 4.31, 5.55, 7.76, 10.00,
      10.35, 12.60, 14.33, 15.33, 16.36, 16.78,
      16.08, 16.99, 17.21, 16.72, 16.55, 18.34,
      19.91, 21.78, 22.56, 23.88, 25.92, 26.00},
    p_z = {
      2.28, 2.28, 2.28, 2.21, 1.96, 1.89,
      1.63, 1.43, 1.70, 1.74, 1.55, 1.56,
      1.28, 1.38, 1.66, 1.79, 2.14, 2.11,
      2.05, 1.84, 1.79, 2.08, 2.08, 2.39,
      2.44, 2.44, 2.46, 2.48, 2.50, 2.49,
      2.26, 2.19, 2.14, 2.12, 2.26, 2.40,
      2.40, 2.23, 2.10, 2.24, 2.22, 2.11,
      1.86, 1.83, 1.83, 1.94, 2.00, 2.12,
      2.21, 2.01, 1.80, 1.76, 1.96, 1.97},
    segment_duration = {
      5.60, 5.65, 5.65, 5.65, 5.60, 5.65,
      5.65, 5.65, 5.60, 5.65, 5.65, 5.65,
      5.65, 5.60, 5.65, 5.65, 5.65, 5.60,
      5.65, 5.65, 5.65, 5.65, 5.60, 5.65,
      5.65, 5.65, 5.60, 5.65, 5.65, 5.65,
      5.60, 5.65, 5.65, 5.65, 5.65, 5.60,
      5.65, 5.65, 5.65, 5.60, 5.65, 5.65,
      5.65, 5.65, 5.60, 5.65, 5.65, 5.65,
      5.60, 5.65, 5.65, 5.65, 5.64});

  Modelica.Blocks.Interfaces.RealOutput velocity_command[3]
    "Reference translational velocity [x, y, z] in m/s";
  Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]
    "Reference translational acceleration [x, y, z] in m/s2";

protected
  function smoothstepSecondDerivative
    input Real tau;
    input Real duration;
    output Real y;
  protected
    Real r;
    Real T;
  algorithm
    T := max(1e-9, duration);
    r := min(1.0, max(0.0, tau / T));
    y := (60.0 * r - 180.0 * r ^ 2 + 120.0 * r ^ 3) / T ^ 2;
  end smoothstepSecondDerivative;

  function interpAcceleration
    input Real a;
    input Real b;
    input Real tau;
    input Real duration;
    output Real y;
  algorithm
    y := (b - a) * smoothstepSecondDerivative(tau, duration);
  end interpAcceleration;

  function piecewiseAcceleration
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
          y := interpAcceleration(value[i], value[i + 1],
            query_time - elapsed, segment_duration[i]);
          found := true;
        else
          elapsed := elapsed + segment_duration[i];
        end if;
      end if;
    end for;
  end piecewiseAcceleration;

equation
  velocity_command[1] = piecewiseRate(p_x, time, n_segments, segment_duration);
  velocity_command[2] = piecewiseRate(p_y, time, n_segments, segment_duration);
  velocity_command[3] = piecewiseRate(p_z, time, n_segments, segment_duration);
  acceleration_command[1] = piecewiseAcceleration(p_x, time, n_segments, segment_duration);
  acceleration_command[2] = piecewiseAcceleration(p_y, time, n_segments, segment_duration);
  acceleration_command[3] = piecewiseAcceleration(p_z, time, n_segments, segment_duration);

  annotation(__MWORKS(hide=true,version="26.3.0"));
end OpenBlocksUav2Reference;