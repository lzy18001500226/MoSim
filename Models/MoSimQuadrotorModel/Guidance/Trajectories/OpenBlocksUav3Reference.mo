within MoSimQuadrotorModel.Guidance.Trajectories;
model OpenBlocksUav3Reference
  "UAV 3 trajectory: historical A* planning from (-41, -28) to (41, 28)"

  extends PlannedQuinticReference(
    n_segments = 53,
    p_x = {
      -41.00, -41.00, -41.00, -41.00, -41.00, -40.27,
      -36.58, -34.85, -33.03, -30.08, -28.72, -26.61,
      -23.98, -22.31, -20.50, -18.55, -17.81, -15.81,
      -12.84, -11.37, -10.47, -7.25, -6.40, -4.93,
      -4.14, -3.83, -3.61, -1.84, 0.65, 1.24,
      2.44, 3.24, 5.26, 8.15, 8.55, 10.85,
      13.20, 13.60, 15.39, 17.90, 18.60, 20.70,
      22.57, 24.91, 26.49, 28.40, 30.02, 33.11,
      34.16, 35.41, 36.31, 36.95, 39.75, 41.00},
    p_y = {
      -28.00, -28.00, -28.00, -28.00, -28.00, -27.92,
      -27.50, -27.31, -27.21, -27.05, -26.38, -25.30,
      -24.67, -23.62, -22.56, -21.42, -20.90, -19.18,
      -16.61, -15.34, -15.18, -14.72, -14.44, -12.15,
      -9.95, -7.67, -6.63, -4.69, -1.95, -1.29,
      1.13, 2.76, 3.50, 4.56, 4.90, 7.18,
      9.53, 9.93, 11.63, 14.03, 14.55, 15.70,
      16.97, 16.16, 16.96, 17.39, 17.73, 18.35,
      19.99, 21.43, 23.80, 24.59, 26.95, 28.00},
    p_z = {
      2.10, 2.10, 2.10, 2.10, 2.10, 2.06,
      1.85, 1.75, 1.65, 1.49, 1.65, 1.91,
      1.93, 1.90, 1.58, 1.51, 1.57, 1.73,
      1.97, 2.10, 2.04, 1.80, 1.81, 2.19,
      2.37, 2.42, 2.44, 2.43, 2.42, 2.42,
      2.47, 2.50, 2.31, 2.03, 2.04, 2.17,
      2.31, 2.33, 2.24, 2.12, 2.14, 2.33,
      2.16, 2.00, 1.97, 1.88, 1.87, 1.89,
      2.18, 2.19, 2.06, 2.00, 1.79, 1.69},
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
end OpenBlocksUav3Reference;