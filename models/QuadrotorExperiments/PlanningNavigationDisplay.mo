model PlanningNavigationDisplay
  "Lightweight native 3D navigation display: pillar-cluster obstacle map and short-horizon local plan"
  parameter Integer n_segments(min = 1, max = 5) = 1;
  parameter Real p_x[6] = fill(0.0, 6);
  parameter Real p_y[6] = fill(0.0, 6);
  parameter Real p_z[6] = fill(1.0, 6);
  parameter Real segment_duration[5] = fill(1.0, 5);

  parameter Real x_min = -1.0;
  parameter Real x_max = 7.0;
  parameter Real y_min = -2.5;
  parameter Real y_max = 2.5;
  parameter Real map_z = 0.0;
  parameter Real boundary_line_diameter_m = 0.018;
  parameter Real boundary_wall_height_m = 1.2;
  parameter Real boundary_wall_thickness_m = 0.08;
  parameter Real boundary_wall_x_axis_phase_m = -0.25
    "Shift y-edge walls along x only; do not use for inward/outward correction.";
  parameter Real boundary_wall_y_axis_phase_m = 0.0
    "Shift x-edge walls along y only; do not use for inward/outward correction.";
  parameter Real planned_line_diameter_m = 0.026;
  parameter Real marker_diameter_m = 0.08;
  parameter Real local_costmap_radius_m = 100.0
    "Manual-review radius. Keep large here so the static pillar map is visible in Sysplorer.";
  parameter Real local_plan_horizon_s = 2.0
    "Short forward local plan horizon; do not show the complete global path";
  parameter Integer max_pillars = 40;
  parameter Integer pillar_count(min = 0, max = 40) = 0;
  parameter Real pillar_center[40, 2] = fill(0.0, 40, 2);
  parameter Real pillar_width[40] = fill(0.16, 40);
  parameter Real pillar_height[40] = fill(1.8, 40);
  parameter Real pillar_z_min[40] = fill(0.0, 40);
  parameter Real terrain_cell_size_m = 0.50;
  parameter Integer terrain_x_count = integer(ceil((x_max - x_min) / terrain_cell_size_m));
  parameter Integer terrain_y_count = integer(ceil((y_max - y_min) / terrain_cell_size_m));
  parameter Real terrain_min_height_m = 0.17;
  parameter Real terrain_height_span_m = 0.40;
  parameter Real terrain_fill_scale = 1.0;
  parameter Real terrain_x_offset_m = -0.25;
  parameter Real terrain_y_offset_m = 0.0;

  Modelica.Blocks.Interfaces.RealInput actual_position[3]
    annotation(Placement(transformation(origin = {-120, 30}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.RealInput reference_position[3]
    annotation(Placement(transformation(origin = {-120, -30}, extent = {{-20, -20}, {20, 20}})));

protected
  Real segment_start[5];
  Real segment_end[5];
  Real local_plan_end[3];
  Real local_plan_vector[3];
  Real local_plan_length;
  Real local_plan_direction[3];
  Real lookahead_time;
  Real pillar_position[max_pillars, 3];
  Real pillar_distance_to_uav[max_pillars];
  Boolean pillar_active[max_pillars];
  parameter Integer ground_pillar_count = terrain_x_count * terrain_y_count;
  parameter Integer ground_x_index[ground_pillar_count] = {
    mod(i - 1, terrain_x_count) for i in 1:ground_pillar_count};
  parameter Integer ground_y_index[ground_pillar_count] = {
    div(i - 1, terrain_x_count) for i in 1:ground_pillar_count};
  Real ground_position[ground_pillar_count, 3];
  Real ground_height[ground_pillar_count];
  Real ground_length[ground_pillar_count];
  Real ground_width[ground_pillar_count];
  parameter Integer boundary_wall_x_segment_count = terrain_y_count;
  parameter Integer boundary_wall_y_segment_count = terrain_x_count;
  Real boundary_wall_x_position[2 * boundary_wall_x_segment_count, 3];
  Real boundary_wall_x_width[2 * boundary_wall_x_segment_count];
  Real boundary_wall_y_position[2 * boundary_wall_y_segment_count, 3];
  Real boundary_wall_y_length[2 * boundary_wall_y_segment_count];

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
    input Real value[6];
    input Real query_time;
    input Integer n_segments;
    input Real segment_duration[5];
    output Real y;
  protected
    Real t1;
    Real t2;
    Real t3;
    Real t4;
    Real t5;
  algorithm
    t1 := segment_duration[1];
    t2 := t1 + segment_duration[2];
    t3 := t2 + segment_duration[3];
    t4 := t3 + segment_duration[4];
    t5 := t4 + segment_duration[5];
    y :=
      if query_time <= t1 then value[1] + (value[2] - value[1]) * smoothstep(query_time, segment_duration[1])
      else if n_segments <= 1 then value[2]
      else if query_time <= t2 then value[2] + (value[3] - value[2]) * smoothstep(query_time - t1, segment_duration[2])
      else if n_segments <= 2 then value[3]
      else if query_time <= t3 then value[3] + (value[4] - value[3]) * smoothstep(query_time - t2, segment_duration[3])
      else if n_segments <= 3 then value[4]
      else if query_time <= t4 then value[4] + (value[5] - value[4]) * smoothstep(query_time - t3, segment_duration[4])
      else if n_segments <= 4 then value[5]
      else if query_time <= t5 then value[5] + (value[6] - value[5]) * smoothstep(query_time - t4, segment_duration[5])
      else value[6];
  end localInterp;

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
    each length = boundary_wall_thickness_m,
    width = {boundary_wall_x_width[i] for i in 1:2 * boundary_wall_x_segment_count},
    each height = boundary_wall_height_m,
    each color = {210, 210, 210},
    each specularCoefficient = 0.2);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape boundary_wall_y[2 * boundary_wall_y_segment_count](
    each shapeType = "box",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {boundary_wall_y_position[i, :] for i in 1:2 * boundary_wall_y_segment_count},
    each r_shape = {0, 0, 0},
    each lengthDirection = {1, 0, 0},
    each widthDirection = {0, 1, 0},
    length = {boundary_wall_y_length[i] for i in 1:2 * boundary_wall_y_segment_count},
    each width = boundary_wall_thickness_m,
    each height = boundary_wall_height_m,
    each color = {210, 210, 210},
    each specularCoefficient = 0.2);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape obstacle_pillar[max_pillars](
    each shapeType = "box",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {pillar_position[i, :] for i in 1:max_pillars},
    each r_shape = {0, 0, 0},
    each lengthDirection = {1, 0, 0},
    each widthDirection = {0, 1, 0},
    length = {if pillar_active[i] then pillar_width[i] else 0.0 for i in 1:max_pillars},
    width = {if pillar_active[i] then pillar_width[i] else 0.0 for i in 1:max_pillars},
    height = {if pillar_active[i] then pillar_height[i] else 0.0 for i in 1:max_pillars},
    each color = {210, 210, 210},
    each specularCoefficient = 0.25);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape ground_pillar[ground_pillar_count](
    each shapeType = "box",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {ground_position[i, :] for i in 1:ground_pillar_count},
    each r_shape = {0, 0, 0},
    each lengthDirection = {1, 0, 0},
    each widthDirection = {0, 1, 0},
    length = {ground_length[i] * terrain_fill_scale for i in 1:ground_pillar_count},
    width = {ground_width[i] * terrain_fill_scale for i in 1:ground_pillar_count},
    height = {ground_height[i] for i in 1:ground_pillar_count},
    each color = {255, 255, 255},
    each specularCoefficient = 0.15);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape local_plan_line(
    shapeType = "cylinder",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = reference_position,
    r_shape = {0, 0, 0},
    lengthDirection = local_plan_direction,
    widthDirection = {0, 0, 1},
    length = local_plan_length,
    width = planned_line_diameter_m,
    height = planned_line_diameter_m,
    color = {40, 130, 255},
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
    length = marker_diameter_m * 0.75,
    width = marker_diameter_m * 0.75,
    height = marker_diameter_m * 0.75,
    color = {255, 220, 0},
    specularCoefficient = 0.4);

equation
  segment_start[1] = 0.0;
  segment_start[2] = segment_duration[1];
  segment_start[3] = segment_start[2] + segment_duration[2];
  segment_start[4] = segment_start[3] + segment_duration[3];
  segment_start[5] = segment_start[4] + segment_duration[4];
  segment_end[1] = segment_start[1] + segment_duration[1];
  segment_end[2] = segment_start[2] + segment_duration[2];
  segment_end[3] = segment_start[3] + segment_duration[3];
  segment_end[4] = segment_start[4] + segment_duration[4];
  segment_end[5] = segment_start[5] + segment_duration[5];
  lookahead_time = min(segment_end[n_segments], time + local_plan_horizon_s);
  local_plan_end[1] = localInterp(p_x, lookahead_time, n_segments, segment_duration);
  local_plan_end[2] = localInterp(p_y, lookahead_time, n_segments, segment_duration);
  local_plan_end[3] = localInterp(p_z, lookahead_time, n_segments, segment_duration);
  local_plan_vector[1] = local_plan_end[1] - reference_position[1];
  local_plan_vector[2] = local_plan_end[2] - reference_position[2];
  local_plan_vector[3] = local_plan_end[3] - reference_position[3];
  local_plan_length = sqrt(local_plan_vector[1] ^ 2 + local_plan_vector[2] ^ 2 + local_plan_vector[3] ^ 2);
  local_plan_direction[1] = if local_plan_length > 1e-6 then local_plan_vector[1] / local_plan_length else 1.0;
  local_plan_direction[2] = if local_plan_length > 1e-6 then local_plan_vector[2] / local_plan_length else 0.0;
  local_plan_direction[3] = if local_plan_length > 1e-6 then local_plan_vector[3] / local_plan_length else 0.0;

  for i in 1:max_pillars loop
    pillar_position[i, 1] = pillar_center[i, 1];
    pillar_position[i, 2] = pillar_center[i, 2];
    pillar_position[i, 3] = pillar_z_min[i] + 0.5 * pillar_height[i];
    pillar_distance_to_uav[i] = sqrt((pillar_center[i, 1] - actual_position[1]) ^ 2 + (pillar_center[i, 2] - actual_position[2]) ^ 2);
    pillar_active[i] = i <= pillar_count and pillar_distance_to_uav[i] <= local_costmap_radius_m;
  end for;

  for i in 1:ground_pillar_count loop
    ground_height[i] = terrain_min_height_m + terrain_height_span_m *
      (0.5 + 0.5 * sin(0.91 * ground_x_index[i] + 1.37 * ground_y_index[i]));
    ground_length[i] = max(0.0, min(terrain_cell_size_m,
      x_max - (x_min + terrain_x_offset_m + ground_x_index[i] * terrain_cell_size_m)));
    ground_width[i] = max(0.0, min(terrain_cell_size_m,
      y_max - (y_min + terrain_y_offset_m + ground_y_index[i] * terrain_cell_size_m)));
    ground_position[i, 1] = x_min + terrain_x_offset_m + ground_x_index[i] * terrain_cell_size_m + 0.5 * ground_length[i];
    ground_position[i, 2] = y_min + terrain_y_offset_m + ground_y_index[i] * terrain_cell_size_m + 0.5 * ground_width[i];
    ground_position[i, 3] = map_z + 0.5 * ground_height[i];
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
end PlanningNavigationDisplay;
