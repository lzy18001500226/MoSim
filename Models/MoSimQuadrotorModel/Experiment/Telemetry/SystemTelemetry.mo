within MoSimQuadrotorModel.Experiment.Telemetry;
block SystemTelemetry
  "Visible result endpoint with two stable top-level telemetry buses"

  Modelica.Blocks.Interfaces.RealInput vehicle_bus[28]
    "[actuation(1:9), plant state(10:28)]" 
    annotation(Placement(
      transformation(origin = {-100, 60}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, 60}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealInput autonomy_bus[40]
    "[avionics(1:11), mission(12:28), supervisor(29:40)]" 
    annotation(Placement(
      transformation(origin = {-100, -60}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, -60}, extent = {{-8, -8}, {8, 8}})));

  Real esc_health[4];
  Real esc_saturation_ratio;
  Real rotor_speed_telemetry[4];
  Real plant_velocity[3];
  Real plant_body_rate[3];
  Real plant_quaternion[4];
  Real plant_rotor_thrust[4];
  Real plant_rotor_yaw_reaction_moment[4];
  Real plant_applied_reaction_yaw_moment;
  Real perception_health;
  Real perception_mid360_valid;
  Real flight_controller_attitude_est[3];
  Real flight_controller_motor_speed_est[4];
  Real flight_controller_health;
  Real flight_controller_estimator_mode;
  Real mission_reference_position[3];
  Real mission_reference_velocity[3];
  Real mission_reference_acceleration[3];
  Real mission_yaw_reference;
  Real mission_z_reference_rate;
  Real mission_health;
  Real mission_flight_mode;
  Real mission_active_setpoint_source;
  Real mission_safety_status;
  Real mission_event_code;
  Real mission_obstacle_avoid_active;
  Real supervisor_degraded_nav_active;
  Real supervisor_obstacle_avoid_active;
  Real supervisor_estimator_quality;
  Real supervisor_estimator_mode;
  Real supervisor_flight_mode;
  Real supervisor_active_setpoint_source;
  Real supervisor_safety_status;
  Real supervisor_event_code;
  Real supervisor_battery_low_active;
  Real supervisor_offboard_loss_active;
  Real supervisor_mission_failure_active;
  Real supervisor_geofence_breach_active;

equation
  esc_health = vehicle_bus[1:4];
  esc_saturation_ratio = vehicle_bus[5];
  rotor_speed_telemetry = vehicle_bus[6:9];
  plant_velocity = vehicle_bus[10:12];
  plant_body_rate = vehicle_bus[13:15];
  plant_quaternion = vehicle_bus[16:19];
  plant_rotor_thrust = vehicle_bus[20:23];
  plant_rotor_yaw_reaction_moment = vehicle_bus[24:27];
  plant_applied_reaction_yaw_moment = vehicle_bus[28];
  perception_health = autonomy_bus[1];
  perception_mid360_valid = autonomy_bus[2];
  flight_controller_attitude_est = autonomy_bus[3:5];
  flight_controller_motor_speed_est = autonomy_bus[6:9];
  flight_controller_health = autonomy_bus[10];
  flight_controller_estimator_mode = autonomy_bus[11];
  mission_reference_position = autonomy_bus[12:14];
  mission_reference_velocity = autonomy_bus[15:17];
  mission_reference_acceleration = autonomy_bus[18:20];
  mission_yaw_reference = autonomy_bus[21];
  mission_z_reference_rate = autonomy_bus[22];
  mission_health = autonomy_bus[23];
  mission_flight_mode = autonomy_bus[24];
  mission_active_setpoint_source = autonomy_bus[25];
  mission_safety_status = autonomy_bus[26];
  mission_event_code = autonomy_bus[27];
  mission_obstacle_avoid_active = autonomy_bus[28];
  supervisor_degraded_nav_active = autonomy_bus[29];
  supervisor_obstacle_avoid_active = autonomy_bus[30];
  supervisor_estimator_quality = autonomy_bus[31];
  supervisor_estimator_mode = autonomy_bus[32];
  supervisor_flight_mode = autonomy_bus[33];
  supervisor_active_setpoint_source = autonomy_bus[34];
  supervisor_safety_status = autonomy_bus[35];
  supervisor_event_code = autonomy_bus[36];
  supervisor_battery_low_active = autonomy_bus[37];
  supervisor_offboard_loss_active = autonomy_bus[38];
  supervisor_mission_failure_active = autonomy_bus[39];
  supervisor_geofence_breach_active = autonomy_bus[40];

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {55, 80, 115},
        fillColor = {244, 249, 255}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 24}, extent = {{-88, 20}, {88, -20}},
        textString = "Flight data", textColor = {55, 80, 115}),
      Text(origin = {0, -34}, extent = {{-88, 18}, {88, -18}},
        textString = "recorder", textColor = {55, 80, 115})}),
    Diagram(coordinateSystem(extent = {{-120, -100}, {120, 100}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end SystemTelemetry;