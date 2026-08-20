within MoSimQuadrotorModel.Guidance.Trajectories;
model OpenBlocksUav2Reference
  "UAV 2 trajectory: historical A* planning from (-43, -26) to (43, 26)"

  extends PlannedQuinticReference(
    n_segments = 53,
    p_x = {
      -43.00, -43.00, -43.00, -41.93, -38.20, -37.03,
      -34.55, -32.38, -30.46, -29.14, -27.81, -25.44,
      -23.46, -22.40, -18.65, -17.43, -15.14, -13.15,
      -11.90, -8.54, -7.18, -5.32, -4.13, -4.08,
      -3.70, -3.36, -1.48, 1.29, 3.22, 3.59,
      6.22, 7.77, 8.97, 9.24, 10.89, 13.43,
      13.96, 15.69, 18.04, 19.04, 20.80, 22.78,
      25.00, 26.72, 28.55, 30.82, 33.17, 34.20,
      35.88, 37.40, 38.70, 40.44, 42.21, 43.00},
    p_y = {
      -26.00, -26.00, -26.00, -25.84, -25.27, -25.09,
      -24.75, -24.45, -22.79, -21.36, -20.73, -19.53,
      -18.13, -18.04, -17.91, -17.89, -17.76, -16.80,
      -16.14, -15.18, -14.78, -12.53, -10.97, -9.64,
      -6.72, -6.36, -4.39, -1.49, 0.52, 0.90,
      1.37, 1.74, 3.53, 5.41, 7.09, 9.68,
      10.21, 11.89, 14.17, 14.81, 15.82, 16.94,
      16.04, 16.92, 17.13, 17.22, 16.53, 17.75,
      19.19, 20.91, 22.45, 23.77, 25.31, 26.00},
    p_z = {
      2.28, 2.28, 2.28, 2.21, 1.97, 1.89,
      1.64, 1.43, 1.69, 1.74, 1.55, 1.56,
      1.29, 1.36, 1.64, 1.74, 2.10, 2.14,
      2.06, 1.86, 1.78, 2.05, 2.08, 2.38,
      2.44, 2.44, 2.46, 2.48, 2.50, 2.50,
      2.31, 2.20, 2.17, 2.11, 2.22, 2.38,
      2.41, 2.28, 2.11, 2.17, 2.27, 2.15,
      1.98, 1.75, 1.96, 1.73, 2.01, 1.98,
      2.29, 2.10, 1.84, 1.75, 1.90, 1.97},
    segment_duration = {
      5.60, 5.60, 5.60, 5.60, 5.60, 5.60,
      5.60, 5.60, 5.60, 5.60, 5.60, 5.60,
      5.60, 5.60, 5.60, 5.60, 5.60, 5.60,
      5.60, 5.60, 5.60, 5.60, 5.60, 5.60,
      5.60, 5.60, 5.60, 5.60, 5.60, 5.60,
      5.60, 5.60, 5.60, 5.60, 5.60, 5.60,
      5.60, 5.60, 5.60, 5.60, 5.60, 5.60,
      5.60, 5.60, 5.60, 5.60, 5.60, 5.60,
      5.60, 5.60, 5.60, 5.60, 7.64});

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