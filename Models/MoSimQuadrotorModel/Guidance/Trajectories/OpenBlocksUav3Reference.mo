within MoSimQuadrotorModel.Guidance.Trajectories;
model OpenBlocksUav3Reference
  "UAV 3 trajectory: historical A* planning from (-41, -28) to (41, 28)"

  extends PlannedQuinticReference(
    n_segments = 53,
    p_x = {
      -41.00, -41.00, -41.00, -41.00, -41.00, -40.34,
      -36.71, -34.85, -33.24, -30.12, -28.94, -26.61,
      -24.18, -22.60, -20.81, -18.88, -17.89, -16.14,
      -13.15, -11.43, -10.85, -7.46, -6.57, -4.97,
      -4.21, -3.92, -3.68, -2.30, 0.29, 1.24,
      2.06, 3.24, 4.50, 7.84, 8.35, 10.15,
      12.81, 13.57, 14.68, 17.43, 18.23, 20.63,
      22.44, 24.12, 26.22, 27.39, 29.46, 32.53,
      33.72, 35.31, 35.78, 36.55, 38.67, 41.00},
    p_y = {
      -28.00, -28.00, -28.00, -28.00, -28.00, -27.93,
      -27.52, -27.31, -27.22, -27.05, -26.49, -25.30,
      -24.72, -23.82, -22.72, -21.62, -20.97, -19.46,
      -16.88, -15.39, -15.23, -14.75, -14.70, -12.20,
      -10.16, -8.34, -6.71, -5.20, -2.34, -1.30,
      0.37, 2.75, 3.22, 4.45, 4.69, 6.50,
      9.14, 9.89, 10.96, 13.58, 14.35, 15.66,
      16.90, 16.71, 16.22, 17.17, 17.62, 18.23,
      19.27, 20.91, 22.62, 24.26, 26.04, 28.00},
    p_z = {
      2.10, 2.10, 2.10, 2.10, 2.10, 2.06,
      1.86, 1.75, 1.66, 1.50, 1.62, 1.91,
      1.93, 1.90, 1.66, 1.49, 1.56, 1.70,
      1.95, 2.09, 2.06, 1.81, 1.77, 2.18,
      2.35, 2.40, 2.44, 2.43, 2.42, 2.42,
      2.45, 2.50, 2.38, 2.06, 2.03, 2.13,
      2.29, 2.33, 2.27, 2.14, 2.10, 2.33,
      2.17, 2.10, 2.16, 1.90, 1.87, 1.89,
      2.05, 2.23, 2.11, 2.04, 1.87, 1.69},
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
end OpenBlocksUav3Reference;