model Sunray150PlanningOpenBlocksColorMapReview
  "Video-review variant with the global colored static map enabled"
  extends Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop(
    navigationDisplay(
      show_static_map_mesh = false,
      show_static_map_layers = true,
      show_static_grid_overlay = false,
      render_terrain_blocks = false,
      show_continuous_ground = false,
      highlight_local_costmap = true,
      local_costmap_radius_m = 6,
      local_costmap_fade_radius_m = 9));

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 80.1247340259, Tolerance = 0.0001, Interval = 0.05));
end Sunray150PlanningOpenBlocksColorMapReview;
