within MoSimQuadrotorModel.Guidance.Trajectories;
model OpenBlocksPx4CtrlReference
  "Frozen OpenBlocks A* path with analytic position, velocity, and acceleration"

  extends PlannedQuinticReference(
    n_segments = 53,
    p_x = {
      -41.00, -38.06, -36.14, -32.46, -30.40, -28.72,
      -26.61, -23.80, -22.08, -17.85, -16.18, -13.67,
      -11.69, -7.59, -6.55, -4.34, -3.95, -3.65,
      -1.45, 1.11, 1.76, 3.24, 5.67, 8.25,
      9.67, 12.94, 13.64, 16.31, 18.22, 20.67,
      22.60, 25.14, 27.73, 30.64, 32.81, 34.46,
      36.86, 38.41, 40.12, 41.00, 41.00, 41.00,
      41.00, 41.00, 41.00, 41.00, 41.00, 41.00,
      41.00, 41.00, 41.00, 41.00, 41.00, 41.00},
    p_y = {
      -26.00, -25.44, -25.08, -24.43, -22.73, -20.86,
      -19.95, -18.38, -18.05, -17.88, -18.12, -17.09,
      -16.09, -14.87, -13.97, -11.17, -8.52, -6.70,
      -4.26, -1.44, -0.24, 2.76, 3.65, 4.60,
      6.02, 9.27, 9.96, 12.52, 14.34, 15.68,
      16.97, 16.04, 17.05, 17.28, 16.52, 17.97,
      20.15, 22.24, 24.10, 26.00, 26.00, 26.00,
      26.00, 26.00, 26.00, 26.00, 26.00, 26.00,
      26.00, 26.00, 26.00, 26.00, 26.00, 26.00},
    p_z = {
      2.28, 1.84, 1.57, 1.43, 1.49, 1.78,
      1.58, 1.32, 1.38, 1.70, 1.73, 2.06,
      1.97, 1.80, 1.83, 2.01, 2.27, 2.44,
      2.43, 2.42, 2.44, 2.50, 2.27, 2.02,
      2.10, 2.29, 2.33, 2.19, 2.10, 2.33,
      2.16, 1.95, 1.91, 1.71, 2.02, 2.03,
      2.26, 2.09, 1.63, 1.46, 1.46, 1.46,
      1.46, 1.46, 1.46, 1.46, 1.46, 1.46,
      1.46, 1.46, 1.46, 1.46, 1.46, 1.46},
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
end OpenBlocksPx4CtrlReference;