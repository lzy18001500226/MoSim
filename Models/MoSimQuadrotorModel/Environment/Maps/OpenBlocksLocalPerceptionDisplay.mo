within MoSimQuadrotorModel.Environment.Maps;
model OpenBlocksLocalPerceptionDisplay
  "Local perception display: ground and walls inside 9 m, with a 6 m core and 6-9 m fade"

  extends PlanningNavigationDisplay(
    final x_min = -45.0,
    final x_max = 45.0,
    final y_min = -30.0,
    final y_max = 30.0,
    final show_static_map_mesh = false,
    final show_static_map_layers = false,
    final show_global_wall_truth = false,
    final render_terrain_blocks = true,
    final terrain_render_stride = 2,
    final highlight_local_costmap = true,
    final local_costmap_radius_m = 6.0,
    final local_costmap_fade_radius_m = 9.0,
    final wall_group_count = 8,
    final wall_arm1_min = {
      {-10.46, -2.61, 0.0}, {6.53, 9.83, 0.0}, {-7.99, -21.20, 0.0},
      {-35.17, -12.99, 0.0}, {17.57, 8.88, 0.0}, {31.68, -24.84, 0.0},
      {-42.84, 17.00, 0.0}, {14.16, 20.00, 0.0}},
    final wall_arm1_max = {
      {-6.49, 5.28, 2.5}, {30.37, 17.77, 2.5}, {10.09, -9.88, 2.5},
      {-14.01, -3.35, 2.5}, {38.55, 16.82, 2.5}, {39.62, -18.90, 2.5},
      {-22.86, 28.32, 2.5}, {34.14, 28.00, 2.5}},
    final wall_arm2_min = {
      {-10.46, -2.61, 0.0}, {6.53, 9.83, 0.0}, {-7.99, -21.20, 0.0},
      {-35.17, -12.99, 0.0}, {17.57, 8.88, 0.0}, {31.68, -24.84, 0.0},
      {-42.84, 17.00, 0.0}, {14.16, 20.00, 0.0}},
    final wall_arm2_max = {
      {-2.52, -10.55, 2.5}, {14.47, 1.89, 2.5}, {0.09, -29.14, 2.5},
      {-43.11, -20.93, 2.5}, {9.63, 0.94, 2.5}, {23.74, -32.78, 2.5},
      {-50.78, 8.06, 2.5}, {6.22, 12.06, 2.5}});

  annotation(
    defaultComponentName = "nav_display",
    Documentation(info = "<html>
<p>Local perception radar display for single-UAV scenarios.</p>
<p>Only renders obstacles and ground within the local sensing radius (6 m core, 9 m fade).</p>
<p>Does not display the global map background or static terrain layers.</p>
</html>"),__MWORKS(version="26.3.0"));
end OpenBlocksLocalPerceptionDisplay;