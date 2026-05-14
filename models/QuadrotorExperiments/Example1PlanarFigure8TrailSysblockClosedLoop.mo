model Example1PlanarFigure8TrailSysblockClosedLoop
  "Example1 plant with QP/NMPC safety controller and native planar figure-8 review trail"
  parameter Real return_trigger_time_s = 40.0;
  parameter Real land_trigger_time_s = 45.0;
  parameter Real return_altitude_m = 1.0;
  parameter Real landing_altitude_m = 0.15;
  parameter Real descent_rate_mps = 0.8;
  parameter Real takeoff_duration_s = 8.0;
  parameter Real mission_figure8_duration_s = 30.0;
  parameter Real mission_figure8_x_scale_m = 1.8;
  parameter Real mission_figure8_y_scale_m = 0.9;
  parameter Real mission_figure8_start_altitude_m = 0.4;
  parameter Real mission_altitude_m = 0.8;
  parameter Boolean show_online_reference_trail = true
    "Enable planned trajectory line in the native 3D animation";
  parameter Integer online_trail_points = 251
    "5 Hz reference trajectory samples over 50 s for responsive native 3D animation";
  parameter Real online_trail_sample_period_s = 0.2;
  parameter Real online_trail_line_diameter_m = 0.006;
  parameter Real current_position_marker_diameter_m = 0.04;
  parameter Real current_reference_marker_diameter_m = 0.03;
  parameter Real reference_trail_time[online_trail_points] = {(i - 1) * online_trail_sample_period_s for i in 1:online_trail_points};
  parameter Real reference_trail_point[online_trail_points, 3] = {{
      if reference_trail_time[i] <= takeoff_duration_s then 0 else if reference_trail_time[i] <= takeoff_duration_s + mission_figure8_duration_s then mission_figure8_x_scale_m * sin(4 * Modelica.Constants.pi * (reference_trail_time[i] - takeoff_duration_s) / mission_figure8_duration_s) else 0,
      if reference_trail_time[i] <= takeoff_duration_s then 0 else if reference_trail_time[i] <= takeoff_duration_s + mission_figure8_duration_s then mission_figure8_y_scale_m * sin(8 * Modelica.Constants.pi * (reference_trail_time[i] - takeoff_duration_s) / mission_figure8_duration_s) else 0,
      if reference_trail_time[i] <= takeoff_duration_s then mission_altitude_m * reference_trail_time[i] / takeoff_duration_s else if reference_trail_time[i] <= takeoff_duration_s + mission_figure8_duration_s then mission_altitude_m else max(landing_altitude_m, mission_altitude_m - descent_rate_mps * (reference_trail_time[i] - takeoff_duration_s - mission_figure8_duration_s))
    } for i in 1:online_trail_points};
  parameter Real reference_trail_segment_vector[online_trail_points - 1, 3] = {{
      reference_trail_point[i + 1, 1] - reference_trail_point[i, 1],
      reference_trail_point[i + 1, 2] - reference_trail_point[i, 2],
      reference_trail_point[i + 1, 3] - reference_trail_point[i, 3]
    } for i in 1:online_trail_points - 1};
  parameter Real reference_trail_segment_length[online_trail_points - 1] = {
    sqrt(reference_trail_segment_vector[i, 1] ^ 2 + reference_trail_segment_vector[i, 2] ^ 2 + reference_trail_segment_vector[i, 3] ^ 2) for i in 1:online_trail_points - 1};
  parameter Real reference_trail_segment_direction[online_trail_points - 1, 3] = {{
      if reference_trail_segment_length[i] > 1e-6 then reference_trail_segment_vector[i, 1] else 1.0,
      if reference_trail_segment_length[i] > 1e-6 then reference_trail_segment_vector[i, 2] else 0.0,
      if reference_trail_segment_length[i] > 1e-6 then reference_trail_segment_vector[i, 3] else 0.0
    } for i in 1:online_trail_points - 1};

  QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
  QuadrotorModel.Electricals.Actuator actuator1_1;
  QuadrotorModel.Electricals.Actuator actuator1_2;
  QuadrotorModel.Electricals.Actuator actuator1_3;
  QuadrotorModel.Electricals.Actuator actuator1_4;
  QuadrotorModel.Sensors.Sensors sensors1_1;
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];
  Real figure8_phase_time;
  Real figure8_vx_ref;
  Real figure8_vy_ref;

  Modelica.Blocks.Sources.RealExpression mission_ref_x(y = if time <= takeoff_duration_s then 0 else if time <= takeoff_duration_s + mission_figure8_duration_s then mission_figure8_x_scale_m * sin(4 * Modelica.Constants.pi * (time - takeoff_duration_s) / mission_figure8_duration_s) else 0);
  Modelica.Blocks.Sources.RealExpression mission_ref_y(y = if time <= takeoff_duration_s then 0 else if time <= takeoff_duration_s + mission_figure8_duration_s then mission_figure8_y_scale_m * sin(8 * Modelica.Constants.pi * (time - takeoff_duration_s) / mission_figure8_duration_s) else 0);
  Modelica.Blocks.Sources.RealExpression mission_ref_z(y = if time <= takeoff_duration_s then mission_altitude_m * time / takeoff_duration_s else if time <= takeoff_duration_s + mission_figure8_duration_s then mission_altitude_m else max(landing_altitude_m, mission_altitude_m - descent_rate_mps * (time - takeoff_duration_s - mission_figure8_duration_s)));
  Modelica.Blocks.Sources.RealExpression mission_ref_z_rate(y = if time <= takeoff_duration_s then mission_altitude_m / takeoff_duration_s else if time <= takeoff_duration_s + mission_figure8_duration_s then 0 else if mission_altitude_m - descent_rate_mps * (time - takeoff_duration_s - mission_figure8_duration_s) > landing_altitude_m then -descent_rate_mps else 0);
  Modelica.Blocks.Math.Feedback x_error;
  Modelica.Blocks.Math.Feedback y_error;
  Modelica.Blocks.Math.Feedback z_error;
  Modelica.Blocks.Sources.RealExpression yaw_ref(y = if time <= takeoff_duration_s or time > takeoff_duration_s + mission_figure8_duration_s then 0 else Modelica.Math.atan2(figure8_vy_ref, figure8_vx_ref));
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape actual_position_marker(
    shapeType = "sphere",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {sensors1_1.PosMea[1], sensors1_1.PosMea[2], sensors1_1.PosMea[3]},
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = current_position_marker_diameter_m,
    width = current_position_marker_diameter_m,
    height = current_position_marker_diameter_m,
    color = {0, 210, 90},
    specularCoefficient = 0.4);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape current_reference_marker(
    shapeType = "sphere",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {mission_ref_x.y, mission_ref_y.y, mission_ref_z.y},
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = current_reference_marker_diameter_m,
    width = current_reference_marker_diameter_m,
    height = current_reference_marker_diameter_m,
    color = {255, 220, 0},
    specularCoefficient = 0.4);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape reference_trajectory_trail_line[online_trail_points - 1](
    each shapeType = "cylinder",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {reference_trail_point[i, :] for i in 1:online_trail_points - 1},
    each r_shape = {0, 0, 0},
    lengthDirection = reference_trail_segment_direction,
    each widthDirection = {0, 0, 1},
    length = {if show_online_reference_trail then reference_trail_segment_length[i] else 0.0 for i in 1:online_trail_points - 1},
    each width = online_trail_line_diameter_m,
    each height = online_trail_line_diameter_m,
    color = {{255 * (i - 1) / (online_trail_points - 2), 80 + 120 * (i - 1) / (online_trail_points - 2), 255 - 230 * (i - 1) / (online_trail_points - 2)} for i in 1:online_trail_points - 1},
    each specularCoefficient = 0.4);

  AWFF_QPNMPCSafetyController_Sysblock controller3_2(
    return_trigger_time_s = takeoff_duration_s + mission_figure8_duration_s,
    land_trigger_time_s = takeoff_duration_s + mission_figure8_duration_s + 2.0,
    landing_altitude_m = landing_altitude_m);

equation
  figure8_phase_time = if time <= takeoff_duration_s then 0 else if time <= takeoff_duration_s + mission_figure8_duration_s then time - takeoff_duration_s else mission_figure8_duration_s;
  figure8_vx_ref = mission_figure8_x_scale_m * 4 * Modelica.Constants.pi / mission_figure8_duration_s * cos(4 * Modelica.Constants.pi * figure8_phase_time / mission_figure8_duration_s);
  figure8_vy_ref = mission_figure8_y_scale_m * 8 * Modelica.Constants.pi / mission_figure8_duration_s * cos(8 * Modelica.Constants.pi * figure8_phase_time / mission_figure8_duration_s);

  connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
  connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
  connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
  connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
  connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);

  connect(mission_ref_x.y, x_error.u1);
  connect(sensors1_1.PosMea[1], x_error.u2);
  connect(mission_ref_y.y, y_error.u1);
  connect(sensors1_1.PosMea[2], y_error.u2);
  connect(mission_ref_z.y, z_error.u1);
  connect(sensors1_1.PosMea[3], z_error.u2);

  connect(x_error.y, controller3_2.x_error);
  connect(y_error.y, controller3_2.y_error);
  connect(z_error.y, controller3_2.z_error);
  connect(mission_ref_z_rate.y, controller3_2.z_ref_rate);
  connect(sensors1_1.AngleMea[1], controller3_2.roll_mea);
  connect(sensors1_1.AngleMea[2], controller3_2.pitch_mea);
  connect(sensors1_1.AngleMea[3], controller3_2.yaw_mea);
  connect(yaw_ref.y, controller3_2.yaw_ref);

  connect(actuator1_1.u, controller3_2.y);
  connect(actuator1_2.u, controller3_2.y1);
  connect(actuator1_3.u, controller3_2.y2);
  connect(actuator1_4.u, controller3_2.y3);

  connect(actuator1_1.flange_a, speedSensor[1].flange);
  connect(actuator1_2.flange_a, speedSensor[2].flange);
  connect(actuator1_3.flange_a, speedSensor[3].flange);
  connect(actuator1_4.flange_a, speedSensor[4].flange);

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.05));
end Example1PlanarFigure8TrailSysblockClosedLoop;
