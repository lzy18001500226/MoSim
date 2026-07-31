within MoSimQuadrotorModel.Guidance.Planning;
block OpenBlocksPx4CtrlReference
  "Frozen OpenBlocks A* path with analytic position, velocity, and acceleration"

  extends PlannedQuinticReference(
    n_segments = 53,
    p_x = {
      -41, -41, -39, -36.6, -35, -33.4,
      -31, -28.6, -26.2, -25.4, -23.4, -21,
      -18.6, -16.2, -14.2, -12.2, -10.6, -9,
      -7.8, -6.2, -4.6, -3, -1.4, 0.2,
      1.8, 3.4, 5.4, 7.4, 9, 11,
      13.4, 15.8, 17, 17, 16.2, 15.8,
      15.8, 17.4, 19, 21, 22.6, 24.6,
      25.8, 28.2, 30.6, 32.2, 34.2, 35,
      36.2, 36.2, 36.6, 38.6, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41},
    p_y = {
      -26, -26, -24.8, -24.4, -22.8, -21.2,
      -20.4, -19.6, -19.6, -19.2, -17.6, -17.6,
      -16.8, -16, -15.2, -14.8, -13.2, -11.6,
      -10.8, -9.2, -7.6, -6, -4.4, -2.8,
      -1.2, 0.4, 1.6, 1.6, 3.2, 4,
      4.4, 4.8, 6.8, 8, 10.4, 11.2,
      11.6, 13.2, 14.8, 16, 16.8, 18.4,
      19.2, 19.6, 19.6, 19.6, 20.8, 21.2,
      23.2, 23.6, 24, 25.2, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26},
    p_z = {
      1.5, 2.28, 1.9, 1.89, 1.39, 1.46,
      1.7, 2.05, 1.63, 1.38, 1.22, 1.64,
      1.97, 2.02, 1.98, 1.78, 1.94, 2.19,
      2.26, 2.41, 2.47, 2.23, 2.34, 2.21,
      2.47, 2.44, 2.44, 2.26, 1.99, 2.2,
      2.36, 2.26, 2.19, 2.06, 2.15, 2.13,
      2.21, 2.1, 2.02, 2.27, 2.21, 2.1,
      1.6, 1.58, 1.89, 1.99, 2.2, 2.12,
      2, 1.91, 2.09, 1.47, 1.46, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68},
    segment_duration = {
      3, 1.53849838082, 1.58406612103, 1.50867581071, 1.47384387899, 1.65441460149,
      1.66270739442, 1.58624535189, 1.171875, 1.67073072212, 1.58624535189, 1.66097304253,
      1.64734126678, 1.40262843849, 1.33423838098, 1.4768173832, 1.48210318201, 1.171875,
      1.47637245709, 1.47365693694, 1.48140235972, 1.47487882127, 1.47556837952, 1.48283225751,
      1.4732685969, 1.51847705595, 1.30734613515, 1.48358954456, 1.40903526736, 1.58747402647,
      1.58539006014, 1.51916077496, 1.171875, 1.6480615397, 1.171875, 1.171875,
      1.47487882127, 1.47405955188, 1.52717501377, 1.171875, 1.66901740552, 1.171875,
      1.58410625666, 1.57548047899, 1.171875, 1.52461948894, 1.171875, 1.52048547677,
      1.171875, 1.171875, 1.57121052956, 1.64703248196, 3, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1});

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