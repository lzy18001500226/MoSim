within MoSimQuadrotorModel.Planning.Scenarios;
model PlanningNavigationDisplay
  "Lightweight native 3D navigation display: pillar-cluster obstacle map and short-horizon local plan"
  parameter Integer n_segments(min = 1, max = 90) = 1;
  parameter Real p_x[91] = fill(0.0, 91);
  parameter Real p_y[91] = fill(0.0, 91);
  parameter Real p_z[91] = fill(1.0, 91);
  parameter Real segment_duration[90] = fill(1.0, 90);

  parameter Real x_min = -1.0;
  parameter Real x_max = 7.0;
  parameter Real y_min = -2.5;
  parameter Real y_max = 2.5;
  parameter Real map_z = 0.0;
  parameter Real boundary_line_diameter_m = 0.018;
  parameter Real boundary_wall_height_m = 1.2;
  parameter Real boundary_wall_thickness_m = 0.08;
  parameter Boolean render_boundary_walls = false
    "Set false for large maps; disabled walls keep the map coordinates but avoid large zero-height wall arrays.";
  parameter Real boundary_wall_x_axis_phase_m = -0.25
    "Shift y-edge walls along x only; do not use for inward/outward correction.";
  parameter Real boundary_wall_y_axis_phase_m = 0.0
    "Shift x-edge walls along y only; do not use for inward/outward correction.";
  parameter Real planned_line_diameter_m = 0.026;
  parameter Real marker_diameter_m = 0.08;
  parameter Boolean highlight_local_costmap = true
    "If true, render all obstacles and recolor obstacles currently covered by the abstract Mid360 local map.";
  parameter Real local_costmap_radius_m = 2.2
    "Abstract Mid360 local map radius used only for native 3D review.";
  parameter Real local_costmap_fade_radius_m = 9.0
    "Weakly render near-field objects between local_costmap_radius_m and this radius; hide farther objects.";
  parameter Real local_costmap_front_half_angle_rad = 2.356194490192345
    "Kept for compatibility. Current review mode uses spherical/radial sensing, not square or forward-sector recoloring.";
  parameter Real local_costmap_update_period_s = 0.05
    "Abstract local map update period, 20 Hz.";
  parameter Integer local_costmap_half_cells(min = 1) = 1
    "Local grid half-width. 2 means a fixed 5x5 ground-cell window around the UAV.";
  parameter Real local_costmap_cell_size_m = terrain_cell_size_m
    "Abstract local occupancy-grid cell size for sensing highlight; decoupled from coarse terrain display cells.";
  parameter Real local_sensed_cell_size_m = 0.32
    "Fine local sensing footprint cell size. Keep near obstacle pillar size; do not apply to full-map terrain.";
  parameter Real local_sensed_grid_update_step_m = 2.0
    "Quantization step for local terrain display center. Larger than cell size to reduce full-layer animation refreshes.";
  parameter Integer local_sensed_half_cells(min = 1) = 10
    "Fine local sensing footprint half-width. 10 with 0.32 m cells covers the 3 m sensing sphere.";
  parameter Real local_sensed_ground_thickness_m = 0.045
    "Thin overlay used only to show the currently sensed local map.";
  parameter Real local_plan_horizon_s = 2.0
    "Short forward local plan horizon; do not show the complete global path";
  parameter Integer local_plan_point_count(min = 2, max = 12) = 12
    "Number of sampled future points used to render the local exploratory plan curve.";
  parameter Real local_plan_max_length_m = 1.5
    "Limit local plan arrow length so it stays inside the local map window.";
  parameter Real body_axis_length_m = 0.35;
  parameter Real body_axis_diameter_m = 0.018;
  parameter Integer max_pillars = 144;
  parameter Integer pillar_count(min = 0, max = max_pillars) = 0;
  parameter Real pillar_center[max_pillars, 2] = fill(0.0, max_pillars, 2);
  parameter Real pillar_length[max_pillars] = fill(0.16, max_pillars);
  parameter Real pillar_width[max_pillars] = fill(0.16, max_pillars);
  parameter Real pillar_height[max_pillars] = fill(1.8, max_pillars);
  parameter Real pillar_z_min[max_pillars] = fill(0.0, max_pillars);
  parameter Integer max_wall_groups = 8;
  parameter Integer wall_group_count(min = 0, max = max_wall_groups) = 0;
  parameter Real wall_arm1_min[max_wall_groups, 3] = fill(0.0, max_wall_groups, 3);
  parameter Real wall_arm1_max[max_wall_groups, 3] = fill(0.0, max_wall_groups, 3);
  parameter Real wall_arm2_min[max_wall_groups, 3] = fill(0.0, max_wall_groups, 3);
  parameter Real wall_arm2_max[max_wall_groups, 3] = fill(0.0, max_wall_groups, 3);
  parameter Real terrain_cell_size_m = 0.50;
  parameter Integer terrain_x_count = integer(ceil((x_max - x_min) / terrain_cell_size_m));
  parameter Integer terrain_y_count = integer(ceil((y_max - y_min) / terrain_cell_size_m));
  parameter Real terrain_min_height_m = 0.17;
  parameter Real terrain_height_span_m = 0.40;
  parameter Real terrain_fill_scale = 1.0;
  parameter Boolean render_terrain_blocks = false
    "Render the global low-resolution terrain block map. Disable for GUI review when native animation becomes too heavy.";
  parameter Real terrain_x_offset_m = -0.25;
  parameter Real terrain_y_offset_m = 0.0;
  parameter Integer terrain_render_stride(min = 1) = 1
    "Render every Nth terrain cell in each horizontal direction. 1 means full 3D grid; 2 keeps the same map coordinates with fewer GUI objects.";
  parameter Integer local_terrain_half_cells(min = 1) = 6
    "Kept for compatibility with older rolling-terrain configs; full-map terrain rendering now uses terrain_x_count * terrain_y_count cells.";
  parameter Boolean show_continuous_ground = false
    "Render a continuous base plate below terrain texture cells to avoid visual cracks.";
  parameter Real continuous_ground_thickness_m = 0.03;
  parameter Boolean show_static_map_mesh = true
    "Render one pre-generated STL mesh for dense 0.2 m volumetric terrain columns and 1000 random obstacles.";
  parameter String static_map_mesh_uri =
    "modelica://QuadrotorModel/Resources/Visualization/map_open_blocks_static_obstacle_columns_0p2_h2p8_3p5.stl";
  parameter Boolean show_static_map_layers = true
    "Render review-friendly split static map layers: five volumetric terrain-column height bands, obstacle mesh, and grid overlay.";
  parameter String static_terrain_band_mesh_uri[5] = {
    "modelica://QuadrotorModel/Resources/Visualization/map_open_blocks_static_terrain_band_1_ground_0p2.stl",
    "modelica://QuadrotorModel/Resources/Visualization/map_open_blocks_static_terrain_band_2_ground_0p2.stl",
    "modelica://QuadrotorModel/Resources/Visualization/map_open_blocks_static_terrain_band_3_ground_0p2.stl",
    "modelica://QuadrotorModel/Resources/Visualization/map_open_blocks_static_terrain_band_4_ground_0p2.stl",
    "modelica://QuadrotorModel/Resources/Visualization/map_open_blocks_static_terrain_band_5_ground_0p2.stl"};
  parameter String static_obstacle_mesh_uri =
    "modelica://QuadrotorModel/Resources/Visualization/map_open_blocks_static_obstacle_columns_0p2_h2p8_3p5.stl";
  parameter String static_grid_mesh_uri =
    "modelica://QuadrotorModel/Resources/Visualization/map_open_blocks_static_terrain_grid_2m_patch0p2.stl";
  parameter Boolean show_static_grid_overlay = false
    "Keep false for GUI review unless explicit grid debugging is needed. Dark grid lines hide terrain stair steps.";

  Modelica.Blocks.Interfaces.RealInput actual_position[3]
    annotation(Placement(transformation(origin = {-120, 30}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.RealInput reference_position[3]
    annotation(Placement(transformation(origin = {-120, -30}, extent = {{-20, -20}, {20, 20}})));

protected
  Real segment_start[90];
  Real segment_end[90];
  Real local_plan_end[3];
  Real local_plan_point[12, 3];
  Real local_plan_sample_time[12];
  Real local_plan_segment_vector[11, 3];
  Real local_plan_segment_length[11];
  Real local_plan_segment_direction[11, 3];
  Real lookahead_time;
  Real pillar_position[max_pillars, 3];
  Real pillar_distance_to_uav[max_pillars];
  Real pillar_bearing_dot[max_pillars];
  Boolean pillar_active[max_pillars];
  Boolean pillar_sensed[max_pillars];
  Boolean pillar_near[max_pillars];
  Boolean pillar_occluded[max_pillars];
  Real wall_arm1_position[max_wall_groups, 3];
  Real wall_arm2_position[max_wall_groups, 3];
  Real wall_arm1_display_position[max_wall_groups, 3];
  Real wall_arm2_display_position[max_wall_groups, 3];
  Real wall_arm1_length[max_wall_groups];
  Real wall_arm2_length[max_wall_groups];
  Real wall_arm1_display_length[max_wall_groups];
  Real wall_arm2_display_length[max_wall_groups];
  Real wall_arm1_display_radius[max_wall_groups];
  Real wall_arm2_display_radius[max_wall_groups];
  Real wall_arm1_width[max_wall_groups];
  Real wall_arm2_width[max_wall_groups];
  Real wall_arm1_height[max_wall_groups];
  Real wall_arm2_height[max_wall_groups];
  Real wall_arm1_distance_to_uav[max_wall_groups];
  Real wall_arm2_distance_to_uav[max_wall_groups];
  Real wall_arm1_dx_to_uav[max_wall_groups];
  Real wall_arm1_dy_to_uav[max_wall_groups];
  Real wall_arm2_dx_to_uav[max_wall_groups];
  Real wall_arm2_dy_to_uav[max_wall_groups];
  Boolean wall_arm1_sensed[max_wall_groups];
  Boolean wall_arm2_sensed[max_wall_groups];
  Boolean wall_arm1_near[max_wall_groups];
  Boolean wall_arm2_near[max_wall_groups];
  Boolean wall_arm1_occluded[max_wall_groups];
  Boolean wall_arm2_occluded[max_wall_groups];
  Real wall_arm1_length_direction[max_wall_groups, 3];
  Real wall_arm2_length_direction[max_wall_groups, 3];
  Real wall_arm1_width_direction[max_wall_groups, 3];
  Real wall_arm2_width_direction[max_wall_groups, 3];
  Boolean wall_arm1_x_axis[max_wall_groups];
  Boolean wall_arm2_x_axis[max_wall_groups];
  Real sensed_position[3];
  Real local_heading_vector[2];
  Real local_heading_norm;
  Real local_costmap_update_index;
  Real local_grid_center_x;
  Real local_grid_center_y;
  Real local_window_half_width_m;
  parameter Integer local_terrain_width_cells = 2 * local_terrain_half_cells + 1;
  parameter Integer local_sensed_width_cells = 2 * local_sensed_half_cells + 1;
  parameter Integer local_sensed_ground_count = local_sensed_width_cells * local_sensed_width_cells;
  parameter Integer local_sensed_x_index[local_sensed_ground_count] = {
    mod(i - 1, local_sensed_width_cells) - local_sensed_half_cells for i in 1:local_sensed_ground_count};
  parameter Integer local_sensed_y_index[local_sensed_ground_count] = {
    div(i - 1, local_sensed_width_cells) - local_sensed_half_cells for i in 1:local_sensed_ground_count};
  parameter Integer terrain_render_x_count = integer(ceil(terrain_x_count / terrain_render_stride));
  parameter Integer terrain_render_y_count = integer(ceil(terrain_y_count / terrain_render_stride));
  parameter Integer ground_pillar_count = terrain_render_x_count * terrain_render_y_count;
  parameter Integer ground_x_index[ground_pillar_count] = {
    terrain_render_stride * mod(i - 1, terrain_render_x_count) for i in 1:ground_pillar_count};
  parameter Integer ground_y_index[ground_pillar_count] = {
    terrain_render_stride * div(i - 1, terrain_render_x_count) for i in 1:ground_pillar_count};
  Real ground_position[ground_pillar_count, 3];
  Real ground_center[ground_pillar_count, 2];
  Real ground_height[ground_pillar_count];
  Real ground_length[ground_pillar_count];
  Real ground_width[ground_pillar_count];
  Real ground_distance_to_uav[ground_pillar_count];
  Real ground_bearing_dot[ground_pillar_count];
  Boolean ground_sensed[ground_pillar_count];
  Boolean ground_near[ground_pillar_count];
  Boolean ground_occluded[ground_pillar_count];
  Real local_sensed_ground_position[local_sensed_ground_count, 3];
  Real local_sensed_ground_height[local_sensed_ground_count];
  Real local_sensed_ground_distance[local_sensed_ground_count];
  Boolean local_sensed_ground_active[local_sensed_ground_count];
  Boolean local_sensed_ground_near[local_sensed_ground_count];
  Boolean local_sensed_ground_occluded[local_sensed_ground_count];
  parameter Integer boundary_wall_x_segment_count = if render_boundary_walls then terrain_y_count else 1;
  parameter Integer boundary_wall_y_segment_count = if render_boundary_walls then terrain_x_count else 1;
  Real boundary_wall_x_position[2 * boundary_wall_x_segment_count, 3];
  Real boundary_wall_x_width[2 * boundary_wall_x_segment_count];
  Real boundary_wall_y_position[2 * boundary_wall_y_segment_count, 3];
  Real boundary_wall_y_length[2 * boundary_wall_y_segment_count];
  Real local_terrain_center_x;
  Real local_terrain_center_y;

  function smoothstep
    input Real tau;
    input Real duration;
    output Real y;
  protected
    Real r;
  algorithm
    r := min(1.0, max(0.0, tau / max(1e-9, duration)));
    y := 10.0 * r ^ 3 - 15.0 * r ^ 4 + 6.0 * r ^ 5;
  end smoothstep;

  function localInterp
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
    y := value[1];
    found := false;
    for i in 1:90 loop
      if not found and i <= n_segments then
        if query_time <= elapsed + segment_duration[i] then
          y := value[i] + (value[i + 1] - value[i]) * smoothstep(query_time - elapsed, segment_duration[i]);
          found := true;
        else
          elapsed := elapsed + segment_duration[i];
          y := value[i + 1];
        end if;
      end if;
    end for;
  end localInterp;

  function localTerrainHeight
    "Match the deterministic static-map terrain height field for local radar review."
    input Real x;
    input Real y;
    output Real z;
  protected
    Real value;
    Real normalized;
    Real smooth_height;
  algorithm
    value :=
      0.30 * sin(0.075 * x + 0.031 * y + 0.4) +
      0.24 * sin(-0.044 * x + 0.089 * y + 1.7) +
      0.22 * sin(0.210 * x - 0.135 * y + 2.1) +
      0.16 * sin(0.390 * x + 0.310 * y) +
      0.08 * sin(0.770 * x - 0.570 * y + 0.8);
    normalized := max(0.0, min(1.0, 0.5 + 0.62 * tanh(1.55 * value)));
    smooth_height := 0.10 + 1.40 * normalized;
    z := max(0.10, min(1.50, floor(smooth_height / 0.01 + 0.5) * 0.01));
  end localTerrainHeight;

  function clampReal
    input Real value;
    input Real low;
    input Real high;
    output Real y;
  algorithm
    y := min(high, max(low, value));
  end clampReal;

  function clippedIntervalLow
    input Real axis_min;
    input Real axis_max;
    input Real query_axis;
    input Real perpendicular_distance;
    input Real radius;
    output Real y;
  protected
    Real center;
    Real half_length;
  algorithm
    center := clampReal(query_axis, min(axis_min, axis_max), max(axis_min, axis_max));
    half_length := sqrt(max(0.0, radius ^ 2 - perpendicular_distance ^ 2));
    y := max(min(axis_min, axis_max), center - half_length);
  end clippedIntervalLow;

  function clippedIntervalHigh
    input Real axis_min;
    input Real axis_max;
    input Real query_axis;
    input Real perpendicular_distance;
    input Real radius;
    output Real y;
  protected
    Real center;
    Real half_length;
  algorithm
    center := clampReal(query_axis, min(axis_min, axis_max), max(axis_min, axis_max));
    half_length := sqrt(max(0.0, radius ^ 2 - perpendicular_distance ^ 2));
    y := min(max(axis_min, axis_max), center + half_length);
  end clippedIntervalHigh;

  function segmentBoxIntersectionT
    "First XY intersection ratio between segment p0-p1 and an axis-aligned box."
    input Real x0;
    input Real y0;
    input Real x1;
    input Real y1;
    input Real bx0;
    input Real by0;
    input Real bx1;
    input Real by1;
    input Real inflate;
    output Boolean hit;
    output Real t_hit;
  protected
    Real dx;
    Real dy;
    Real t0;
    Real t1;
    Real p;
    Real q;
    Real r;
    Real lo_x;
    Real hi_x;
    Real lo_y;
    Real hi_y;
  algorithm
    dx := x1 - x0;
    dy := y1 - y0;
    t0 := 0.0;
    t1 := 1.0;
    hit := true;
    lo_x := min(bx0, bx1) - inflate;
    hi_x := max(bx0, bx1) + inflate;
    lo_y := min(by0, by1) - inflate;
    hi_y := max(by0, by1) + inflate;

    p := -dx;
    q := x0 - lo_x;
    if hit then
      if abs(p) <= 1e-12 then
        hit := q >= 0.0;
      else
        r := q / p;
        if p < 0.0 then
          if r > t1 then
            hit := false;
          else
            t0 := max(t0, r);
          end if;
        else
          if r < t0 then
            hit := false;
          else
            t1 := min(t1, r);
          end if;
        end if;
      end if;
    end if;

    p := dx;
    q := hi_x - x0;
    if hit then
      if abs(p) <= 1e-12 then
        hit := q >= 0.0;
      else
        r := q / p;
        if p < 0.0 then
          if r > t1 then
            hit := false;
          else
            t0 := max(t0, r);
          end if;
        else
          if r < t0 then
            hit := false;
          else
            t1 := min(t1, r);
          end if;
        end if;
      end if;
    end if;

    p := -dy;
    q := y0 - lo_y;
    if hit then
      if abs(p) <= 1e-12 then
        hit := q >= 0.0;
      else
        r := q / p;
        if p < 0.0 then
          if r > t1 then
            hit := false;
          else
            t0 := max(t0, r);
          end if;
        else
          if r < t0 then
            hit := false;
          else
            t1 := min(t1, r);
          end if;
        end if;
      end if;
    end if;

    p := dy;
    q := hi_y - y0;
    if hit then
      if abs(p) <= 1e-12 then
        hit := q >= 0.0;
      else
        r := q / p;
        if p < 0.0 then
          if r > t1 then
            hit := false;
          else
            t0 := max(t0, r);
          end if;
        else
          if r < t0 then
            hit := false;
          else
            t1 := min(t1, r);
          end if;
        end if;
      end if;
    end if;

    t_hit := t0;
  end segmentBoxIntersectionT;

  function occludedByWallArms
    "Approximate Mid360 XY line-of-sight occlusion by fixed L/T wall arms."
    input Real sx;
    input Real sy;
    input Real tx;
    input Real ty;
    input Integer skip_group;
    input Integer skip_arm;
    input Integer max_groups;
    input Integer wall_group_count;
    input Real wall_arm1_min[max_groups, 3];
    input Real wall_arm1_max[max_groups, 3];
    input Real wall_arm2_min[max_groups, 3];
    input Real wall_arm2_max[max_groups, 3];
    output Boolean blocked;
  protected
    Boolean hit;
    Real t_hit;
  algorithm
    blocked := false;
    for j in 1:max_groups loop
      if not blocked and j <= wall_group_count then
        (hit, t_hit) := segmentBoxIntersectionT(
          sx, sy, tx, ty,
          wall_arm1_min[j, 1], wall_arm1_min[j, 2],
          wall_arm1_max[j, 1], wall_arm1_max[j, 2],
          0.02);
        if hit and t_hit > 1e-6 and t_hit < 0.985 and not (j == skip_group and skip_arm == 1) then
          blocked := true;
        end if;
      end if;
      if not blocked and j <= wall_group_count then
        (hit, t_hit) := segmentBoxIntersectionT(
          sx, sy, tx, ty,
          wall_arm2_min[j, 1], wall_arm2_min[j, 2],
          wall_arm2_max[j, 1], wall_arm2_max[j, 2],
          0.02);
        if hit and t_hit > 1e-6 and t_hit < 0.985 and not (j == skip_group and skip_arm == 2) then
          blocked := true;
        end if;
      end if;
    end for;
  end occludedByWallArms;

public
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape map_boundary_x_min(
    shapeType = "cylinder",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {x_min + 0.5 * boundary_wall_thickness_m, 0.5 * (y_min + y_max), map_z + 0.5 * boundary_wall_height_m},
    r_shape = {0, 0, 0},
    lengthDirection = {0, 1, 0},
    widthDirection = {1, 0, 0},
    length = y_max - y_min,
    width = boundary_line_diameter_m,
    height = boundary_line_diameter_m,
    color = {90, 90, 90},
    specularCoefficient = 0.2);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape map_boundary_x_max(
    shapeType = "cylinder",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {x_max, y_min, map_z},
    r_shape = {0, 0, 0},
    lengthDirection = {0, 1, 0},
    widthDirection = {1, 0, 0},
    length = y_max - y_min,
    width = boundary_line_diameter_m,
    height = boundary_line_diameter_m,
    color = {90, 90, 90},
    specularCoefficient = 0.2);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape map_boundary_y_min(
    shapeType = "cylinder",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {x_min, y_min, map_z},
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = x_max - x_min,
    width = boundary_line_diameter_m,
    height = boundary_line_diameter_m,
    color = {90, 90, 90},
    specularCoefficient = 0.2);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape map_boundary_y_max(
    shapeType = "cylinder",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {x_min, y_max, map_z},
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = x_max - x_min,
    width = boundary_line_diameter_m,
    height = boundary_line_diameter_m,
    color = {90, 90, 90},
    specularCoefficient = 0.2);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape boundary_wall_x[2 * boundary_wall_x_segment_count](
    each shapeType = "box",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {boundary_wall_x_position[i, :] for i in 1:2 * boundary_wall_x_segment_count},
    each r_shape = {0, 0, 0},
    each lengthDirection = {1, 0, 0},
    each widthDirection = {0, 1, 0},
    length = {if render_boundary_walls then boundary_wall_thickness_m else 0.0 for i in 1:2 * boundary_wall_x_segment_count},
    width = {if render_boundary_walls then boundary_wall_x_width[i] else 0.0 for i in 1:2 * boundary_wall_x_segment_count},
    height = {if render_boundary_walls then boundary_wall_height_m else 0.0 for i in 1:2 * boundary_wall_x_segment_count},
    each color = {210, 210, 210},
    each specularCoefficient = 0.2);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape boundary_wall_y[2 * boundary_wall_y_segment_count](
    each shapeType = "box",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {boundary_wall_y_position[i, :] for i in 1:2 * boundary_wall_y_segment_count},
    each r_shape = {0, 0, 0},
    each lengthDirection = {1, 0, 0},
    each widthDirection = {0, 1, 0},
    length = {if render_boundary_walls then boundary_wall_y_length[i] else 0.0 for i in 1:2 * boundary_wall_y_segment_count},
    width = {if render_boundary_walls then boundary_wall_thickness_m else 0.0 for i in 1:2 * boundary_wall_y_segment_count},
    height = {if render_boundary_walls then boundary_wall_height_m else 0.0 for i in 1:2 * boundary_wall_y_segment_count},
    each color = {210, 210, 210},
    each specularCoefficient = 0.2);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape obstacle_pillar[max_pillars](
    each shapeType = "box",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {pillar_position[i, :] for i in 1:max_pillars},
    r_shape = {{-0.5 * pillar_length[i], 0.0, 0.0} for i in 1:max_pillars},
    each lengthDirection = {1, 0, 0},
    each widthDirection = {0, 1, 0},
    length = {if pillar_sensed[i] or pillar_near[i] then pillar_length[i] else 0.0 for i in 1:max_pillars},
    width = {if pillar_sensed[i] or pillar_near[i] then pillar_width[i] else 0.0 for i in 1:max_pillars},
    height = {if pillar_sensed[i] or pillar_near[i] then pillar_height[i] else 0.0 for i in 1:max_pillars},
    color = {if pillar_sensed[i] then {70, 160, 255} else {238, 238, 238} for i in 1:max_pillars},
    each specularCoefficient = 0.25);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape wall_arm1[max_wall_groups](
    each shapeType = "box",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {wall_arm1_display_position[i, :] for i in 1:max_wall_groups},
    each r_shape = {0, 0, 0},
    lengthDirection = {wall_arm1_length_direction[i, :] for i in 1:max_wall_groups},
    widthDirection = {wall_arm1_width_direction[i, :] for i in 1:max_wall_groups},
    length = {if i <= wall_group_count and (wall_arm1_sensed[i] or wall_arm1_near[i]) then wall_arm1_display_length[i] else 0.0 for i in 1:max_wall_groups},
    width = {if i <= wall_group_count and (wall_arm1_sensed[i] or wall_arm1_near[i]) then wall_arm1_width[i] else 0.0 for i in 1:max_wall_groups},
    height = {if i <= wall_group_count and (wall_arm1_sensed[i] or wall_arm1_near[i]) then wall_arm1_height[i] else 0.0 for i in 1:max_wall_groups},
    color = {if wall_arm1_sensed[i] then {120, 155, 185} else {238, 238, 238} for i in 1:max_wall_groups},
    each specularCoefficient = 0.25);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape wall_arm2[max_wall_groups](
    each shapeType = "box",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {wall_arm2_display_position[i, :] for i in 1:max_wall_groups},
    each r_shape = {0, 0, 0},
    lengthDirection = {wall_arm2_length_direction[i, :] for i in 1:max_wall_groups},
    widthDirection = {wall_arm2_width_direction[i, :] for i in 1:max_wall_groups},
    length = {if i <= wall_group_count and (wall_arm2_sensed[i] or wall_arm2_near[i]) then wall_arm2_display_length[i] else 0.0 for i in 1:max_wall_groups},
    width = {if i <= wall_group_count and (wall_arm2_sensed[i] or wall_arm2_near[i]) then wall_arm2_width[i] else 0.0 for i in 1:max_wall_groups},
    height = {if i <= wall_group_count and (wall_arm2_sensed[i] or wall_arm2_near[i]) then wall_arm2_height[i] else 0.0 for i in 1:max_wall_groups},
    color = {if wall_arm2_sensed[i] then {120, 155, 185} else {238, 238, 238} for i in 1:max_wall_groups},
    each specularCoefficient = 0.25);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape continuous_ground(
    shapeType = "box",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {x_min + 0.5 * (x_max - x_min), y_min + 0.5 * (y_max - y_min), map_z - 0.5 * continuous_ground_thickness_m},
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = if show_continuous_ground then x_max - x_min else 0.0,
    width = if show_continuous_ground then y_max - y_min else 0.0,
    height = continuous_ground_thickness_m,
    color = {180, 180, 180},
    specularCoefficient = 0.12);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape static_map_mesh(
    shapeType = if show_static_map_mesh and not show_static_map_layers then static_map_mesh_uri else "box",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {0, 0, 0},
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = if show_static_map_mesh and not show_static_map_layers then 1.0 else 0.0,
    width = if show_static_map_mesh and not show_static_map_layers then 1.0 else 0.0,
    height = if show_static_map_mesh and not show_static_map_layers then 1.0 else 0.0,
    color = {230, 230, 230},
    specularCoefficient = 0.12);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape static_terrain_band_mesh[5](
    shapeType = {if show_static_map_layers then static_terrain_band_mesh_uri[i] else "box" for i in 1:5},
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    each r = {0, 0, 0},
    each r_shape = {0, 0, 0},
    each lengthDirection = {1, 0, 0},
    each widthDirection = {0, 1, 0},
    each length = if show_static_map_layers then 1.0 else 0.0,
    each width = if show_static_map_layers then 1.0 else 0.0,
    each height = if show_static_map_layers then 1.0 else 0.0,
    color = {
      if show_static_map_layers then {210, 236, 248} else {232, 232, 232},
      if show_static_map_layers then {184, 224, 236} else {232, 232, 232},
      if show_static_map_layers then {158, 210, 206} else {232, 232, 232},
      if show_static_map_layers then {180, 205, 150} else {232, 232, 232},
      if show_static_map_layers then {218, 190, 125} else {232, 232, 232}},
    each specularCoefficient = 0.10);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape static_obstacle_mesh(
    shapeType = if show_static_map_layers and show_static_grid_overlay then static_obstacle_mesh_uri else "box",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {0, 0, 0},
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = if show_static_map_layers and show_static_grid_overlay then 1.0 else 0.0,
    width = if show_static_map_layers and show_static_grid_overlay then 1.0 else 0.0,
    height = if show_static_map_layers and show_static_grid_overlay then 1.0 else 0.0,
    color = {150, 150, 150},
    specularCoefficient = 0.20);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape static_grid_mesh(
    shapeType = if show_static_map_layers and show_static_grid_overlay then static_grid_mesh_uri else "box",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {0, 0, 0},
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = if show_static_map_layers and show_static_grid_overlay then 1.0 else 0.0,
    width = if show_static_map_layers and show_static_grid_overlay then 1.0 else 0.0,
    height = if show_static_map_layers and show_static_grid_overlay then 1.0 else 0.0,
    color = {60, 80, 95},
    specularCoefficient = 0.05);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape ground_pillar[ground_pillar_count](
    each shapeType = "box",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {ground_position[i, :] for i in 1:ground_pillar_count},
    each r_shape = {0, 0, 0},
    each lengthDirection = {1, 0, 0},
    each widthDirection = {0, 1, 0},
    length = {if render_terrain_blocks and (ground_sensed[i] or ground_near[i]) then ground_length[i] * terrain_fill_scale else 0.0 for i in 1:ground_pillar_count},
    width = {if render_terrain_blocks and (ground_sensed[i] or ground_near[i]) then ground_width[i] * terrain_fill_scale else 0.0 for i in 1:ground_pillar_count},
    height = {if render_terrain_blocks and (ground_sensed[i] or ground_near[i]) then ground_height[i] else 0.0 for i in 1:ground_pillar_count},
    color = {if ground_sensed[i] then {210, 232, 255} else {225, 225, 225} for i in 1:ground_pillar_count},
    each specularCoefficient = 0.15);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape local_sensed_ground[local_sensed_ground_count](
    each shapeType = "box",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {local_sensed_ground_position[i, :] for i in 1:local_sensed_ground_count},
    each r_shape = {0, 0, 0},
    each lengthDirection = {1, 0, 0},
    each widthDirection = {0, 1, 0},
    length = {if local_sensed_ground_active[i] or local_sensed_ground_near[i] then local_sensed_cell_size_m else 0.0 for i in 1:local_sensed_ground_count},
    width = {if local_sensed_ground_active[i] or local_sensed_ground_near[i] then local_sensed_cell_size_m else 0.0 for i in 1:local_sensed_ground_count},
    height = {if local_sensed_ground_active[i] or local_sensed_ground_near[i] then local_sensed_ground_height[i] else 0.0 for i in 1:local_sensed_ground_count},
    color = {if local_sensed_ground_active[i] then {170, 220, 255} else {242, 242, 242} for i in 1:local_sensed_ground_count},
    each specularCoefficient = 0.12);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape local_plan_curve[11](
    each shapeType = "cylinder",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {local_plan_point[i, :] for i in 1:11},
    each r_shape = {0, 0, 0},
    lengthDirection = {local_plan_segment_direction[i, :] for i in 1:11},
    each widthDirection = {0, 0, 1},
    length = {if i < local_plan_point_count then local_plan_segment_length[i] else 0.0 for i in 1:11},
    each width = planned_line_diameter_m,
    each height = planned_line_diameter_m,
    each color = {40, 130, 255},
    each specularCoefficient = 0.35);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape body_x_axis(
    shapeType = "cylinder",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = actual_position,
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = body_axis_length_m,
    width = body_axis_diameter_m,
    height = body_axis_diameter_m,
    color = {230, 50, 50},
    specularCoefficient = 0.35);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape body_y_axis(
    shapeType = "cylinder",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = actual_position,
    r_shape = {0, 0, 0},
    lengthDirection = {0, 1, 0},
    widthDirection = {1, 0, 0},
    length = body_axis_length_m,
    width = body_axis_diameter_m,
    height = body_axis_diameter_m,
    color = {40, 190, 80},
    specularCoefficient = 0.35);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape body_z_axis(
    shapeType = "cylinder",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = actual_position,
    r_shape = {0, 0, 0},
    lengthDirection = {0, 0, 1},
    widthDirection = {1, 0, 0},
    length = body_axis_length_m,
    width = body_axis_diameter_m,
    height = body_axis_diameter_m,
    color = {50, 100, 255},
    specularCoefficient = 0.35);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape current_actual_marker(
    shapeType = "sphere",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = actual_position,
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = marker_diameter_m,
    width = marker_diameter_m,
    height = marker_diameter_m,
    color = {0, 210, 90},
    specularCoefficient = 0.4);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape current_reference_marker(
    shapeType = "sphere",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = reference_position,
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = 0.0,
    width = 0.0,
    height = 0.0,
    color = {255, 220, 0},
    specularCoefficient = 0.4);

equation
  segment_start[1] = 0.0;
  segment_end[1] = segment_duration[1];
  for i in 2:90 loop
    segment_start[i] = segment_end[i - 1];
    segment_end[i] = segment_start[i] + segment_duration[i];
  end for;
  lookahead_time = min(segment_end[n_segments], time + local_plan_horizon_s);
  local_plan_end[1] = localInterp(p_x, lookahead_time, n_segments, segment_duration);
  local_plan_end[2] = localInterp(p_y, lookahead_time, n_segments, segment_duration);
  local_plan_end[3] = localInterp(p_z, lookahead_time, n_segments, segment_duration);
  local_plan_sample_time[1] = time;
  local_plan_point[1, 1] = actual_position[1];
  local_plan_point[1, 2] = actual_position[2];
  local_plan_point[1, 3] = actual_position[3];
  for i in 2:12 loop
    local_plan_sample_time[i] = min(segment_end[n_segments],
      time + local_plan_horizon_s * (i - 1) / max(1, local_plan_point_count - 1));
    local_plan_point[i, 1] = localInterp(p_x, local_plan_sample_time[i], n_segments, segment_duration);
    local_plan_point[i, 2] = localInterp(p_y, local_plan_sample_time[i], n_segments, segment_duration);
    local_plan_point[i, 3] = localInterp(p_z, local_plan_sample_time[i], n_segments, segment_duration);
  end for;
  for i in 1:11 loop
    local_plan_segment_vector[i, 1] = local_plan_point[i + 1, 1] - local_plan_point[i, 1];
    local_plan_segment_vector[i, 2] = local_plan_point[i + 1, 2] - local_plan_point[i, 2];
    local_plan_segment_vector[i, 3] = local_plan_point[i + 1, 3] - local_plan_point[i, 3];
    local_plan_segment_length[i] = min(local_plan_max_length_m / max(1, local_plan_point_count - 1),
      sqrt(local_plan_segment_vector[i, 1] ^ 2 + local_plan_segment_vector[i, 2] ^ 2 + local_plan_segment_vector[i, 3] ^ 2));
    local_plan_segment_direction[i, 1] = if local_plan_segment_length[i] > 1e-6 then local_plan_segment_vector[i, 1] /
      sqrt(local_plan_segment_vector[i, 1] ^ 2 + local_plan_segment_vector[i, 2] ^ 2 + local_plan_segment_vector[i, 3] ^ 2) else 1.0;
    local_plan_segment_direction[i, 2] = if local_plan_segment_length[i] > 1e-6 then local_plan_segment_vector[i, 2] /
      sqrt(local_plan_segment_vector[i, 1] ^ 2 + local_plan_segment_vector[i, 2] ^ 2 + local_plan_segment_vector[i, 3] ^ 2) else 0.0;
    local_plan_segment_direction[i, 3] = if local_plan_segment_length[i] > 1e-6 then local_plan_segment_vector[i, 3] /
      sqrt(local_plan_segment_vector[i, 1] ^ 2 + local_plan_segment_vector[i, 2] ^ 2 + local_plan_segment_vector[i, 3] ^ 2) else 0.0;
  end for;
  local_costmap_update_index = floor(time / max(1e-6, local_costmap_update_period_s));
  sensed_position[1] = actual_position[1];
  sensed_position[2] = actual_position[2];
  sensed_position[3] = actual_position[3];
  local_heading_vector[1] = local_plan_end[1] - sensed_position[1];
  local_heading_vector[2] = local_plan_end[2] - sensed_position[2];
  local_heading_norm = sqrt(local_heading_vector[1] ^ 2 + local_heading_vector[2] ^ 2);
  local_grid_center_x = x_min + terrain_x_offset_m +
    floor((sensed_position[1] - x_min - terrain_x_offset_m) / local_sensed_grid_update_step_m) * local_sensed_grid_update_step_m +
    0.5 * local_sensed_grid_update_step_m;
  local_grid_center_y = y_min + terrain_y_offset_m +
    floor((sensed_position[2] - y_min - terrain_y_offset_m) / local_sensed_grid_update_step_m) * local_sensed_grid_update_step_m +
    0.5 * local_sensed_grid_update_step_m;
  local_window_half_width_m = (local_costmap_half_cells + 0.5) * local_costmap_cell_size_m;
  local_terrain_center_x = x_min + terrain_x_offset_m +
    floor((sensed_position[1] - x_min - terrain_x_offset_m) / terrain_cell_size_m) * terrain_cell_size_m +
    0.5 * terrain_cell_size_m;
  local_terrain_center_y = y_min + terrain_y_offset_m +
    floor((sensed_position[2] - y_min - terrain_y_offset_m) / terrain_cell_size_m) * terrain_cell_size_m +
    0.5 * terrain_cell_size_m;

  for i in 1:max_pillars loop
    pillar_position[i, 1] = pillar_center[i, 1];
    pillar_position[i, 2] = pillar_center[i, 2];
    pillar_position[i, 3] = pillar_z_min[i] + 0.5 * pillar_height[i];
    pillar_distance_to_uav[i] = sqrt((pillar_center[i, 1] - sensed_position[1]) ^ 2 + (pillar_center[i, 2] - sensed_position[2]) ^ 2);
    pillar_bearing_dot[i] =
      if pillar_distance_to_uav[i] > 1e-6 and local_heading_norm > 1e-6 then
        ((pillar_center[i, 1] - sensed_position[1]) * local_heading_vector[1] +
        (pillar_center[i, 2] - sensed_position[2]) * local_heading_vector[2]) /
        (pillar_distance_to_uav[i] * local_heading_norm)
      else 1.0;
    pillar_active[i] = i <= pillar_count;
    pillar_occluded[i] = i <= pillar_count and occludedByWallArms(
      sensed_position[1], sensed_position[2], pillar_center[i, 1], pillar_center[i, 2],
      0, 0, max_wall_groups, wall_group_count,
      wall_arm1_min, wall_arm1_max, wall_arm2_min, wall_arm2_max);
    pillar_sensed[i] = i <= pillar_count and highlight_local_costmap and
      pillar_distance_to_uav[i] <= local_costmap_radius_m and not pillar_occluded[i];
    pillar_near[i] = i <= pillar_count and highlight_local_costmap and
      pillar_distance_to_uav[i] > local_costmap_radius_m and
      pillar_distance_to_uav[i] <= local_costmap_fade_radius_m and not pillar_occluded[i];
  end for;

  for i in 1:max_wall_groups loop
    wall_arm1_x_axis[i] = abs(wall_arm1_max[i, 1] - wall_arm1_min[i, 1]) >= abs(wall_arm1_max[i, 2] - wall_arm1_min[i, 2]);
    wall_arm2_x_axis[i] = abs(wall_arm2_max[i, 1] - wall_arm2_min[i, 1]) >= abs(wall_arm2_max[i, 2] - wall_arm2_min[i, 2]);

    wall_arm1_length[i] = if wall_arm1_x_axis[i] then
      abs(wall_arm1_max[i, 1] - wall_arm1_min[i, 1]) else abs(wall_arm1_max[i, 2] - wall_arm1_min[i, 2]);
    wall_arm2_length[i] = if wall_arm2_x_axis[i] then
      abs(wall_arm2_max[i, 1] - wall_arm2_min[i, 1]) else abs(wall_arm2_max[i, 2] - wall_arm2_min[i, 2]);
    wall_arm1_width[i] = if wall_arm1_x_axis[i] then
      abs(wall_arm1_max[i, 2] - wall_arm1_min[i, 2]) else abs(wall_arm1_max[i, 1] - wall_arm1_min[i, 1]);
    wall_arm2_width[i] = if wall_arm2_x_axis[i] then
      abs(wall_arm2_max[i, 2] - wall_arm2_min[i, 2]) else abs(wall_arm2_max[i, 1] - wall_arm2_min[i, 1]);
    wall_arm1_height[i] = abs(wall_arm1_max[i, 3] - wall_arm1_min[i, 3]);
    wall_arm2_height[i] = abs(wall_arm2_max[i, 3] - wall_arm2_min[i, 3]);

    wall_arm1_position[i, 1] = if wall_arm1_x_axis[i] then min(wall_arm1_min[i, 1], wall_arm1_max[i, 1])
      else 0.5 * (wall_arm1_min[i, 1] + wall_arm1_max[i, 1]);
    wall_arm1_position[i, 2] = if wall_arm1_x_axis[i] then 0.5 * (wall_arm1_min[i, 2] + wall_arm1_max[i, 2])
      else min(wall_arm1_min[i, 2], wall_arm1_max[i, 2]);
    wall_arm1_position[i, 3] = 0.5 * (wall_arm1_min[i, 3] + wall_arm1_max[i, 3]);
    wall_arm2_position[i, 1] = if wall_arm2_x_axis[i] then min(wall_arm2_min[i, 1], wall_arm2_max[i, 1])
      else 0.5 * (wall_arm2_min[i, 1] + wall_arm2_max[i, 1]);
    wall_arm2_position[i, 2] = if wall_arm2_x_axis[i] then 0.5 * (wall_arm2_min[i, 2] + wall_arm2_max[i, 2])
      else min(wall_arm2_min[i, 2], wall_arm2_max[i, 2]);
    wall_arm2_position[i, 3] = 0.5 * (wall_arm2_min[i, 3] + wall_arm2_max[i, 3]);
    wall_arm1_dx_to_uav[i] = if sensed_position[1] < min(wall_arm1_min[i, 1], wall_arm1_max[i, 1]) then
      min(wall_arm1_min[i, 1], wall_arm1_max[i, 1]) - sensed_position[1]
      else if sensed_position[1] > max(wall_arm1_min[i, 1], wall_arm1_max[i, 1]) then
      sensed_position[1] - max(wall_arm1_min[i, 1], wall_arm1_max[i, 1])
      else 0.0;
    wall_arm1_dy_to_uav[i] = if sensed_position[2] < min(wall_arm1_min[i, 2], wall_arm1_max[i, 2]) then
      min(wall_arm1_min[i, 2], wall_arm1_max[i, 2]) - sensed_position[2]
      else if sensed_position[2] > max(wall_arm1_min[i, 2], wall_arm1_max[i, 2]) then
      sensed_position[2] - max(wall_arm1_min[i, 2], wall_arm1_max[i, 2])
      else 0.0;
    wall_arm2_dx_to_uav[i] = if sensed_position[1] < min(wall_arm2_min[i, 1], wall_arm2_max[i, 1]) then
      min(wall_arm2_min[i, 1], wall_arm2_max[i, 1]) - sensed_position[1]
      else if sensed_position[1] > max(wall_arm2_min[i, 1], wall_arm2_max[i, 1]) then
      sensed_position[1] - max(wall_arm2_min[i, 1], wall_arm2_max[i, 1])
      else 0.0;
    wall_arm2_dy_to_uav[i] = if sensed_position[2] < min(wall_arm2_min[i, 2], wall_arm2_max[i, 2]) then
      min(wall_arm2_min[i, 2], wall_arm2_max[i, 2]) - sensed_position[2]
      else if sensed_position[2] > max(wall_arm2_min[i, 2], wall_arm2_max[i, 2]) then
      sensed_position[2] - max(wall_arm2_min[i, 2], wall_arm2_max[i, 2])
      else 0.0;
    wall_arm1_distance_to_uav[i] = sqrt(wall_arm1_dx_to_uav[i] ^ 2 + wall_arm1_dy_to_uav[i] ^ 2);
    wall_arm2_distance_to_uav[i] = sqrt(wall_arm2_dx_to_uav[i] ^ 2 + wall_arm2_dy_to_uav[i] ^ 2);
    wall_arm1_occluded[i] = i <= wall_group_count and occludedByWallArms(
      sensed_position[1], sensed_position[2],
      clampReal(sensed_position[1], min(wall_arm1_min[i, 1], wall_arm1_max[i, 1]), max(wall_arm1_min[i, 1], wall_arm1_max[i, 1])),
      clampReal(sensed_position[2], min(wall_arm1_min[i, 2], wall_arm1_max[i, 2]), max(wall_arm1_min[i, 2], wall_arm1_max[i, 2])),
      i, 1, max_wall_groups, wall_group_count,
      wall_arm1_min, wall_arm1_max, wall_arm2_min, wall_arm2_max);
    wall_arm2_occluded[i] = i <= wall_group_count and occludedByWallArms(
      sensed_position[1], sensed_position[2],
      clampReal(sensed_position[1], min(wall_arm2_min[i, 1], wall_arm2_max[i, 1]), max(wall_arm2_min[i, 1], wall_arm2_max[i, 1])),
      clampReal(sensed_position[2], min(wall_arm2_min[i, 2], wall_arm2_max[i, 2]), max(wall_arm2_min[i, 2], wall_arm2_max[i, 2])),
      i, 2, max_wall_groups, wall_group_count,
      wall_arm1_min, wall_arm1_max, wall_arm2_min, wall_arm2_max);
    wall_arm1_sensed[i] = highlight_local_costmap and wall_arm1_distance_to_uav[i] <= local_costmap_radius_m and not wall_arm1_occluded[i];
    wall_arm2_sensed[i] = highlight_local_costmap and wall_arm2_distance_to_uav[i] <= local_costmap_radius_m and not wall_arm2_occluded[i];
    wall_arm1_near[i] = false;
    wall_arm2_near[i] = false;
    wall_arm1_display_radius[i] = if wall_arm1_sensed[i] then local_costmap_radius_m else 0.0;
    wall_arm2_display_radius[i] = if wall_arm2_sensed[i] then local_costmap_radius_m else 0.0;

    wall_arm1_display_length[i] = if wall_arm1_x_axis[i] then
      max(0.0,
        clippedIntervalHigh(wall_arm1_min[i, 1], wall_arm1_max[i, 1], sensed_position[1], wall_arm1_dy_to_uav[i], wall_arm1_display_radius[i]) -
        clippedIntervalLow(wall_arm1_min[i, 1], wall_arm1_max[i, 1], sensed_position[1], wall_arm1_dy_to_uav[i], wall_arm1_display_radius[i]))
      else
      max(0.0,
        clippedIntervalHigh(wall_arm1_min[i, 2], wall_arm1_max[i, 2], sensed_position[2], wall_arm1_dx_to_uav[i], wall_arm1_display_radius[i]) -
        clippedIntervalLow(wall_arm1_min[i, 2], wall_arm1_max[i, 2], sensed_position[2], wall_arm1_dx_to_uav[i], wall_arm1_display_radius[i]));
    wall_arm2_display_length[i] = if wall_arm2_x_axis[i] then
      max(0.0,
        clippedIntervalHigh(wall_arm2_min[i, 1], wall_arm2_max[i, 1], sensed_position[1], wall_arm2_dy_to_uav[i], wall_arm2_display_radius[i]) -
        clippedIntervalLow(wall_arm2_min[i, 1], wall_arm2_max[i, 1], sensed_position[1], wall_arm2_dy_to_uav[i], wall_arm2_display_radius[i]))
      else
      max(0.0,
        clippedIntervalHigh(wall_arm2_min[i, 2], wall_arm2_max[i, 2], sensed_position[2], wall_arm2_dx_to_uav[i], wall_arm2_display_radius[i]) -
        clippedIntervalLow(wall_arm2_min[i, 2], wall_arm2_max[i, 2], sensed_position[2], wall_arm2_dx_to_uav[i], wall_arm2_display_radius[i]));
    wall_arm1_display_position[i, 1] = if wall_arm1_x_axis[i] then
      clippedIntervalLow(wall_arm1_min[i, 1], wall_arm1_max[i, 1], sensed_position[1], wall_arm1_dy_to_uav[i], wall_arm1_display_radius[i])
      else 0.5 * (wall_arm1_min[i, 1] + wall_arm1_max[i, 1]);
    wall_arm1_display_position[i, 2] = if wall_arm1_x_axis[i] then
      0.5 * (wall_arm1_min[i, 2] + wall_arm1_max[i, 2])
      else clippedIntervalLow(wall_arm1_min[i, 2], wall_arm1_max[i, 2], sensed_position[2], wall_arm1_dx_to_uav[i], wall_arm1_display_radius[i]);
    wall_arm1_display_position[i, 3] = wall_arm1_position[i, 3];
    wall_arm2_display_position[i, 1] = if wall_arm2_x_axis[i] then
      clippedIntervalLow(wall_arm2_min[i, 1], wall_arm2_max[i, 1], sensed_position[1], wall_arm2_dy_to_uav[i], wall_arm2_display_radius[i])
      else 0.5 * (wall_arm2_min[i, 1] + wall_arm2_max[i, 1]);
    wall_arm2_display_position[i, 2] = if wall_arm2_x_axis[i] then
      0.5 * (wall_arm2_min[i, 2] + wall_arm2_max[i, 2])
      else clippedIntervalLow(wall_arm2_min[i, 2], wall_arm2_max[i, 2], sensed_position[2], wall_arm2_dx_to_uav[i], wall_arm2_display_radius[i]);
    wall_arm2_display_position[i, 3] = wall_arm2_position[i, 3];

    wall_arm1_length_direction[i, 1] = if wall_arm1_x_axis[i] then 1.0 else 0.0;
    wall_arm1_length_direction[i, 2] = if wall_arm1_x_axis[i] then 0.0 else 1.0;
    wall_arm1_length_direction[i, 3] = 0.0;
    wall_arm2_length_direction[i, 1] = if wall_arm2_x_axis[i] then 1.0 else 0.0;
    wall_arm2_length_direction[i, 2] = if wall_arm2_x_axis[i] then 0.0 else 1.0;
    wall_arm2_length_direction[i, 3] = 0.0;
    wall_arm1_width_direction[i, 1] = if wall_arm1_x_axis[i] then 0.0 else 1.0;
    wall_arm1_width_direction[i, 2] = if wall_arm1_x_axis[i] then 1.0 else 0.0;
    wall_arm1_width_direction[i, 3] = 0.0;
    wall_arm2_width_direction[i, 1] = if wall_arm2_x_axis[i] then 0.0 else 1.0;
    wall_arm2_width_direction[i, 2] = if wall_arm2_x_axis[i] then 1.0 else 0.0;
    wall_arm2_width_direction[i, 3] = 0.0;
  end for;

  for i in 1:ground_pillar_count loop
    ground_height[i] = terrain_min_height_m + terrain_height_span_m *
      (0.5 + 0.5 * sin(0.91 * ground_x_index[i] + 1.37 * ground_y_index[i]));
    ground_length[i] = max(0.0, min(terrain_cell_size_m * terrain_render_stride,
      x_max - (x_min + terrain_x_offset_m + ground_x_index[i] * terrain_cell_size_m)));
    ground_width[i] = max(0.0, min(terrain_cell_size_m * terrain_render_stride,
      y_max - (y_min + terrain_y_offset_m + ground_y_index[i] * terrain_cell_size_m)));
    ground_position[i, 1] = x_min + terrain_x_offset_m + ground_x_index[i] * terrain_cell_size_m + 0.5 * ground_length[i];
    ground_position[i, 2] = y_min + terrain_y_offset_m + ground_y_index[i] * terrain_cell_size_m + 0.5 * ground_width[i];
    ground_position[i, 3] = map_z + 0.5 * ground_height[i];
    ground_center[i, 1] = ground_position[i, 1];
    ground_center[i, 2] = ground_position[i, 2];
    ground_distance_to_uav[i] = sqrt((ground_center[i, 1] - sensed_position[1]) ^ 2 + (ground_center[i, 2] - sensed_position[2]) ^ 2);
    ground_bearing_dot[i] =
      if ground_distance_to_uav[i] > 1e-6 and local_heading_norm > 1e-6 then
        ((ground_center[i, 1] - sensed_position[1]) * local_heading_vector[1] +
        (ground_center[i, 2] - sensed_position[2]) * local_heading_vector[2]) /
        (ground_distance_to_uav[i] * local_heading_norm)
      else 1.0;
    ground_occluded[i] = occludedByWallArms(
      sensed_position[1], sensed_position[2], ground_center[i, 1], ground_center[i, 2],
      0, 0, max_wall_groups, wall_group_count,
      wall_arm1_min, wall_arm1_max, wall_arm2_min, wall_arm2_max);
    ground_sensed[i] = highlight_local_costmap and ground_distance_to_uav[i] <= local_costmap_radius_m and not ground_occluded[i];
    ground_near[i] = highlight_local_costmap and ground_distance_to_uav[i] > local_costmap_radius_m and
      ground_distance_to_uav[i] <= local_costmap_fade_radius_m and not ground_occluded[i];
  end for;

  for i in 1:local_sensed_ground_count loop
    local_sensed_ground_position[i, 1] = local_grid_center_x + local_sensed_x_index[i] * local_sensed_cell_size_m;
    local_sensed_ground_position[i, 2] = local_grid_center_y + local_sensed_y_index[i] * local_sensed_cell_size_m;
    local_sensed_ground_height[i] = localTerrainHeight(local_sensed_ground_position[i, 1], local_sensed_ground_position[i, 2]);
    local_sensed_ground_position[i, 3] = map_z + 0.5 * local_sensed_ground_height[i];
    local_sensed_ground_distance[i] = sqrt(
      (local_sensed_ground_position[i, 1] - sensed_position[1]) ^ 2 +
      (local_sensed_ground_position[i, 2] - sensed_position[2]) ^ 2);
    local_sensed_ground_occluded[i] = occludedByWallArms(
      sensed_position[1], sensed_position[2],
      local_sensed_ground_position[i, 1], local_sensed_ground_position[i, 2],
      0, 0, max_wall_groups, wall_group_count,
      wall_arm1_min, wall_arm1_max, wall_arm2_min, wall_arm2_max);
    local_sensed_ground_active[i] = highlight_local_costmap and
      local_sensed_ground_position[i, 1] >= x_min and local_sensed_ground_position[i, 1] <= x_max and
      local_sensed_ground_position[i, 2] >= y_min and local_sensed_ground_position[i, 2] <= y_max and
      local_sensed_ground_distance[i] <= local_costmap_radius_m and not local_sensed_ground_occluded[i];
    local_sensed_ground_near[i] = highlight_local_costmap and
      local_sensed_ground_position[i, 1] >= x_min and local_sensed_ground_position[i, 1] <= x_max and
      local_sensed_ground_position[i, 2] >= y_min and local_sensed_ground_position[i, 2] <= y_max and
      local_sensed_ground_distance[i] > local_costmap_radius_m and
      local_sensed_ground_distance[i] <= local_costmap_fade_radius_m and not local_sensed_ground_occluded[i];
  end for;

  for i in 1:boundary_wall_x_segment_count loop
    boundary_wall_x_width[i] = max(0.0, min(terrain_cell_size_m, y_max - (y_min + (i - 1) * terrain_cell_size_m)));
    boundary_wall_x_position[i, 1] = x_min;
    boundary_wall_x_position[i, 2] = y_min + boundary_wall_y_axis_phase_m + (i - 1) * terrain_cell_size_m + 0.5 * boundary_wall_x_width[i];
    boundary_wall_x_position[i, 3] = map_z + 0.5 * boundary_wall_height_m;
    boundary_wall_x_width[i + boundary_wall_x_segment_count] = boundary_wall_x_width[i];
    boundary_wall_x_position[i + boundary_wall_x_segment_count, 1] = x_max - boundary_wall_thickness_m;
    boundary_wall_x_position[i + boundary_wall_x_segment_count, 2] = boundary_wall_x_position[i, 2];
    boundary_wall_x_position[i + boundary_wall_x_segment_count, 3] = boundary_wall_x_position[i, 3];
  end for;

  for i in 1:boundary_wall_y_segment_count loop
    boundary_wall_y_length[i] = max(0.0, min(terrain_cell_size_m, x_max - (x_min + (i - 1) * terrain_cell_size_m)));
    boundary_wall_y_position[i, 1] = x_min + boundary_wall_x_axis_phase_m + (i - 1) * terrain_cell_size_m + 0.5 * boundary_wall_y_length[i];
    boundary_wall_y_position[i, 2] = y_min + 0.5 * boundary_wall_thickness_m;
    boundary_wall_y_position[i, 3] = map_z + 0.5 * boundary_wall_height_m;
    boundary_wall_y_length[i + boundary_wall_y_segment_count] = boundary_wall_y_length[i];
    boundary_wall_y_position[i + boundary_wall_y_segment_count, 1] = boundary_wall_y_position[i, 1];
    boundary_wall_y_position[i + boundary_wall_y_segment_count, 2] = y_max - 0.5 * boundary_wall_thickness_m;
    boundary_wall_y_position[i + boundary_wall_y_segment_count, 3] = boundary_wall_y_position[i, 3];
  end for;

  annotation(defaultComponentName = "navigationDisplay");
  annotation(__MWORKS(hide=true));
end PlanningNavigationDisplay;
