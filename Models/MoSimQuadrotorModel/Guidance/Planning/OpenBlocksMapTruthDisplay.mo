within MoSimQuadrotorModel.Guidance.Planning;
model OpenBlocksMapTruthDisplay
  "Canonical OpenBlocks global map truth with a separate local sensing overlay"

  extends PlanningNavigationDisplay(
    final n_segments = 1,
    final p_x = fill(0.0, 91),
    final p_y = fill(0.0, 91),
    final p_z = fill(1.5, 91),
    final segment_duration = fill(1.0, 90),
    final x_min = -45.0,
    final x_max = 45.0,
    final y_min = -30.0,
    final y_max = 30.0,
    final boundary_line_diameter_m = 0.0,
    final render_boundary_walls = false,
    final boundary_wall_height_m = 0.0,
    final boundary_wall_thickness_m = 0.0,
    final highlight_local_costmap = true,
    final local_costmap_radius_m = 6.0,
    final local_costmap_fade_radius_m = 9.0,
    final local_costmap_front_half_angle_rad = 3.141592653589793,
    final local_costmap_update_period_s = 0.05,
    final local_costmap_half_cells = 9,
    final local_costmap_cell_size_m = 1.0,
    final local_sensed_cell_size_m = 1.0,
    final local_sensed_half_cells = 9,
    final local_plan_horizon_s = 4.0,
    final local_plan_point_count = 12,
    final local_plan_max_length_m = 3.5,
    final terrain_cell_size_m = 3.0,
    final terrain_fill_scale = 1.02,
    final render_terrain_blocks = false,
    final show_static_map_mesh = false,
    final terrain_x_offset_m = 0.0,
    final terrain_y_offset_m = 0.0,
    final terrain_render_stride = 2,
    final local_terrain_half_cells = 6,
    final show_continuous_ground = false,
    final show_static_map_layers = true,
    final show_static_grid_overlay = false,
    final show_global_wall_truth = true,
    final max_wall_groups = 8,
    final wall_group_count = 8,
    final wall_arm1_min = {
      {-10.46, -2.61, 0.0}, {6.53, 9.83, 0.0}, {-7.99, -21.20, 0.0},
      {-35.17, -12.99, 0.0}, {17.57, 8.88, 0.0}, {31.68, -24.84, 0.0},
      {-42.84, 17.00, 0.0}, {14.16, 20.00, 0.0}},
    final wall_arm1_max = {
      {-10.14, 15.07, 3.5}, {6.85, 27.51, 3.5}, {9.69, -20.88, 3.5},
      {-17.49, -12.67, 3.5}, {35.25, 9.20, 3.5}, {32.00, -7.16, 3.5},
      {-25.16, 17.32, 3.5}, {31.84, 20.32, 3.5}},
    final wall_arm2_min = {
      {-16.14, -2.77, 0.0}, {3.53, 9.67, 0.0}, {-8.15, -26.88, 0.0},
      {-17.65, -15.99, 0.0}, {17.41, 3.20, 0.0}, {28.68, -7.32, 0.0},
      {-25.32, 17.16, 0.0}, {14.00, 17.00, 0.0}},
    final wall_arm2_max = {
      {-10.30, -2.45, 3.5}, {9.85, 9.99, 3.5}, {-7.83, -21.04, 3.5},
      {-17.33, -9.67, 3.5}, {17.73, 9.04, 3.5}, {35.00, -7.00, 3.5},
      {-25.00, 23.00, 3.5}, {14.32, 23.32, 3.5}});

  annotation(__MWORKS(hide=true,version="26.3.0"));
end OpenBlocksMapTruthDisplay;