within MoSimQuadrotorModel.Guidance.Trajectories;
model OpenBlocksPx4CtrlReference
  "Frozen OpenBlocks A* path with analytic position, velocity, and acceleration"

  extends PlannedQuinticReference(
    n_segments = 53,
    p_x = {
      -41.00, -38.06, -36.13, -32.44, -30.32, -28.70,
      -26.46, -23.66, -21.85, -17.76, -16.08, -13.37,
      -11.45, -7.39, -6.30, -4.33, -3.88, -3.58,
      -1.04, 1.19, 2.04, 3.25, 6.39, 8.26,
      10.21, 13.26, 13.83, 16.94, 18.26, 20.72,
      23.40, 26.00, 28.28, 30.74, 33.64, 35.33,
      37.18, 38.75, 40.26, 41.00, 41.00, 41.00,
      41.00, 41.00, 41.00, 41.00, 41.00, 41.00,
      41.00, 41.00, 41.00, 41.00, 41.00, 41.00,
      41.00, 41.00, 41.00, 41.00, 41.00, 41.00,
      41.00, 41.00, 41.00, 41.00, 41.00, 41.00,
      41.00, 41.00, 41.00, 41.00, 41.00, 41.00,
      41.00, 41.00, 41.00, 41.00, 41.00, 41.00,
      41.00, 41.00, 41.00, 41.00, 41.00, 41.00,
      41.00, 41.00, 41.00, 41.00, 41.00, 41.00,
      41.00},
    p_y = {
      -26.00, -25.44, -25.08, -24.42, -22.67, -20.85,
      -19.89, -18.28, -18.04, -17.87, -18.08, -16.92,
      -16.02, -14.81, -13.66, -11.17, -8.00, -6.62,
      -3.82, -1.35, 0.33, 2.76, 3.92, 4.61,
      6.56, 9.58, 10.14, 13.11, 14.36, 15.72,
      16.84, 16.11, 17.11, 17.26, 16.55, 18.71,
      20.45, 22.46, 24.41, 26.00, 26.00, 26.00,
      26.00, 26.00, 26.00, 26.00, 26.00, 26.00,
      26.00, 26.00, 26.00, 26.00, 26.00, 26.00,
      26.00, 26.00, 26.00, 26.00, 26.00, 26.00,
      26.00, 26.00, 26.00, 26.00, 26.00, 26.00,
      26.00, 26.00, 26.00, 26.00, 26.00, 26.00,
      26.00, 26.00, 26.00, 26.00, 26.00, 26.00,
      26.00, 26.00, 26.00, 26.00, 26.00, 26.00,
      26.00, 26.00, 26.00, 26.00, 26.00, 26.00,
      26.00},
    p_z = {
      2.28, 1.84, 1.57, 1.43, 1.50, 1.78,
      1.57, 1.31, 1.40, 1.71, 1.75, 2.05,
      1.96, 1.79, 1.85, 2.01, 2.32, 2.44,
      2.43, 2.42, 2.45, 2.50, 2.20, 2.02,
      2.13, 2.31, 2.32, 2.16, 2.10, 2.33,
      2.13, 1.77, 1.99, 1.71, 2.00, 2.20,
      2.25, 2.06, 1.60, 1.46, 1.46, 1.46,
      1.46, 1.46, 1.46, 1.46, 1.46, 1.46,
      1.46, 1.46, 1.46, 1.46, 1.46, 1.46,
      1.46, 1.46, 1.46, 1.46, 1.46, 1.46,
      1.46, 1.46, 1.46, 1.46, 1.46, 1.46,
      1.46, 1.46, 1.46, 1.46, 1.46, 1.46,
      1.46, 1.46, 1.46, 1.46, 1.46, 1.46,
      1.46, 1.46, 1.46, 1.46, 1.46, 1.46,
      1.46, 1.46, 1.46, 1.46, 1.46, 1.46,
      1.46},
    segment_duration = {
      5.60, 5.65, 5.65, 5.65, 5.60, 5.65,
      5.65, 5.65, 5.60, 5.65, 5.65, 5.65,
      5.65, 5.60, 5.65, 5.65, 5.65, 5.60,
      5.65, 5.65, 5.65, 5.65, 5.60, 5.65,
      5.65, 5.65, 5.60, 5.65, 5.65, 5.65,
      5.60, 5.65, 5.65, 5.65, 5.65, 5.60,
      5.65, 5.65, 5.65, 5.60, 5.65, 5.65,
      5.65, 5.65, 5.60, 5.65, 5.65, 5.65,
      5.60, 5.65, 5.65, 5.65, 5.64,
      1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
      1.0});

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