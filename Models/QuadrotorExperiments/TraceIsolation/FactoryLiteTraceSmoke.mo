within QuadrotorExperiments.TraceIsolation;
model FactoryLiteTraceSmoke
  "Factory-lite trace integration: trace reference plus navigation display only"
  TraceInlineReference planningReference;
  PlanningNavigationDisplay navigationDisplay(
    n_segments = 1,
    p_x = fill(0.0, 91),
    p_y = fill(0.0, 91),
    p_z = fill(1.0, 91),
    segment_duration = fill(1.0, 90),
    x_min = -1.0,
    x_max = 1.0,
    y_min = -1.0,
    y_max = 1.0,
    boundary_line_diameter_m = 0.0,
    render_boundary_walls = false,
    highlight_local_costmap = false,
    local_costmap_half_cells = 1,
    local_sensed_half_cells = 1,
    render_terrain_blocks = false,
    show_continuous_ground = false,
    show_static_map_mesh = false,
    show_static_map_layers = false,
    max_pillars = 1,
    pillar_count = 0,
    max_wall_groups = 1,
    wall_group_count = 0);

  Modelica.Blocks.Sources.RealExpression actual_position[3](
    y = planningReference.position_command);
  Real x_ref;
  Real y_ref;
  Real z_ref;
  Real yaw_ref;
  Real z_ref_rate;
  Real trace_probe_state(start = 0, fixed = true);

equation
  x_ref = planningReference.position_command[1];
  y_ref = planningReference.position_command[2];
  z_ref = planningReference.position_command[3];
  yaw_ref = planningReference.yaw_ref;
  z_ref_rate = planningReference.z_ref_rate;
  der(trace_probe_state) = x_ref;

  connect(planningReference.position_command, navigationDisplay.reference_position);
  connect(actual_position.y, navigationDisplay.actual_position);

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 2.0, Tolerance = 0.0001, Interval = 0.05));
  annotation(__MWORKS(hide=true));
end FactoryLiteTraceSmoke;
