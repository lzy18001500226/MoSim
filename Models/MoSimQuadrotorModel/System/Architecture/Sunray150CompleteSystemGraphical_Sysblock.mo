within MoSimQuadrotorModel.System.Architecture;
model Sunray150CompleteSystemGraphical_Sysblock
  "Sunray150 complete graphical system with project AWFF Sysblock data flow"
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";
  parameter Real system_degraded_nav_start_s = 1e9;
  parameter Real system_degraded_nav_end_s = 1e9;
  parameter Real system_battery_voltage_drop_per_second = 0.002;
  parameter Real system_battery_low_start_s = 1e9;
  parameter Real system_battery_low_end_s = 1e9;
  parameter Real system_offboard_loss_start_s = 1e9;
  parameter Real system_offboard_loss_end_s = 1e9;
  parameter Real system_mission_failure_start_s = 1e9;
  parameter Real system_mission_failure_end_s = 1e9;
  parameter Real system_geofence_breach_start_s = 1e9;
  parameter Real system_geofence_breach_end_s = 1e9;

  block PerceptionInterfaceModule
    "Top-level perception interface: GPS/GNSS and Mid360 local-map data"
    parameter Real gps_dropout_start_s = 1e9;
    parameter Real gps_dropout_end_s = 1e9;
    parameter Real mid360_dropout_start_s = 1e9;
    parameter Real mid360_dropout_end_s = 1e9;
    parameter Real nominal_obstacle_margin_m = 5.0;
    Modelica.Blocks.Interfaces.RealInput position_raw[3]
      annotation (Placement(transformation(origin = {-110, 20}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput gps_position[3]
      annotation (Placement(transformation(origin = {110, 45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput local_position[3]
      annotation (Placement(transformation(origin = {110, 5}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput obstacle_margin
      annotation (Placement(transformation(origin = {110, -35}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput health
      annotation (Placement(transformation(origin = {110, -75}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput gps_valid
      annotation (Placement(transformation(origin = {110, -105}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput mid360_valid
      annotation (Placement(transformation(origin = {110, -130}, extent = {{-5, -5}, {5, 5}})));
  equation
    gps_position = position_raw;
    local_position = position_raw;
    gps_valid = if time >= gps_dropout_start_s and time <= gps_dropout_end_s then 0 else 1;
    mid360_valid = if time >= mid360_dropout_start_s and time <= mid360_dropout_end_s then 0 else 1;
    obstacle_margin = if mid360_valid > 0.5 then nominal_obstacle_margin_m else 0.2;
    health = 0.5 * gps_valid + 0.5 * mid360_valid;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 100, 150}, fillColor = {242, 252, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {-58, 18}, extent = {{-48, -48}, {48, 48}}, fileName = "modelica://MoSimQuadrotorModel/Plant/Resources/Images/GPS.png"),
        Bitmap(origin = {58, 18}, extent = {{-48, -48}, {48, 48}}, fileName = "modelica://MoSimQuadrotorModel/Plant/Resources/Images/MId360.png"),
        Text(origin = {0, -78}, extent = {{-100, 14}, {100, -14}}, textString = "GPS + Mid360", textColor = {0, 100, 150})}));
    annotation(__MWORKS(hide=true));
  end PerceptionInterfaceModule;

  block V6XFlightControllerModule
    "Top-level V6X/PX6C flight-controller interface"
    parameter Real estimator_position_T = 0.08;
    parameter Real estimator_attitude_T = 0.03;
    parameter Real estimator_motor_T = 0.05;
    Modelica.Blocks.Interfaces.RealInput gps_position[3]
      annotation (Placement(transformation(origin = {-110, 55}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput attitude_raw[3]
      annotation (Placement(transformation(origin = {-110, 10}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput motor_speed_raw[4]
      annotation (Placement(transformation(origin = {-110, -45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput gps_valid
      annotation (Placement(transformation(origin = {-110, -80}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput position_est[3]
      annotation (Placement(transformation(origin = {110, 55}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput attitude_est[3]
      annotation (Placement(transformation(origin = {110, 10}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput motor_speed_est[4]
      annotation (Placement(transformation(origin = {110, -45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput health
      annotation (Placement(transformation(origin = {110, -80}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_quality
      annotation (Placement(transformation(origin = {110, -110}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_mode
      annotation (Placement(transformation(origin = {110, -135}, extent = {{-5, -5}, {5, 5}})));
    Real position_est_state[3](start = {0, 0, 0}, fixed = {true, true, true});
    Real attitude_est_state[3](start = {0, 0, 0}, fixed = {true, true, true});
    Real motor_speed_est_state[4](start = {MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s, -MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s, MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s, -MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s}, fixed = {true, true, true, true});
  equation
    for i in 1:3 loop
      der(position_est_state[i]) = if gps_valid > 0.5 then (gps_position[i] - position_est_state[i]) / estimator_position_T else 0;
      der(attitude_est_state[i]) = (attitude_raw[i] - attitude_est_state[i]) / estimator_attitude_T;
      position_est[i] = position_est_state[i];
      attitude_est[i] = attitude_est_state[i];
    end for;
    for i in 1:4 loop
      der(motor_speed_est_state[i]) = (motor_speed_raw[i] - motor_speed_est_state[i]) / estimator_motor_T;
      motor_speed_est[i] = motor_speed_est_state[i];
    end for;
    estimator_quality = if gps_valid > 0.5 then 1 else 0.45;
    estimator_mode = if gps_valid > 0.5 then 1 else 2;
    health = estimator_quality;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {100, 70, 20}, fillColor = {255, 248, 235}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 14}, extent = {{-96, -54}, {96, 54}}, fileName = "modelica://MoSimQuadrotorModel/Plant/Resources/Images/V6X.png"),
        Text(origin = {0, -78}, extent = {{-95, 14}, {95, -14}}, textString = "V6X / PX6C", textColor = {100, 70, 20})}));
    annotation(__MWORKS(hide=true));
  end V6XFlightControllerModule;

  block ORINNXMissionComputerModule
    "Top-level ORIN NX mission computer with internal trajectory source"
    parameter Real takeoff_time_s = 3.0;
    parameter Real return_altitude_m = 1.0;
    parameter Real landing_altitude_m = 0.15;
    parameter Real obstacle_warning_margin_m = 0.6;
    parameter Real estimator_degraded_threshold = 0.6;
    parameter Real degraded_nav_start_s = 1e9;
    parameter Real degraded_nav_end_s = 1e9;
    Modelica.Blocks.Interfaces.RealInput aircraft_position[3]
      annotation (Placement(transformation(origin = {-110, 40}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput local_position[3]
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput obstacle_margin
      annotation (Placement(transformation(origin = {-110, -45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput estimator_quality
      annotation (Placement(transformation(origin = {-110, -80}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput reference_position[3]
      annotation (Placement(transformation(origin = {110, 50}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput yaw_reference
      annotation (Placement(transformation(origin = {110, 5}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput z_reference_rate
      annotation (Placement(transformation(origin = {110, -40}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput health
      annotation (Placement(transformation(origin = {110, -80}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput flight_mode
      annotation (Placement(transformation(origin = {110, -110}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput active_setpoint_source
      annotation (Placement(transformation(origin = {110, -135}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput safety_status
      annotation (Placement(transformation(origin = {110, -160}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput event_code
      annotation (Placement(transformation(origin = {110, -185}, extent = {{-5, -5}, {5, 5}})));
    MoSimQuadrotorModel.Plant.PathPlanning.ClimbPath trajectory(gain(k = 1));
    Real degraded_nav_active;
    Real obstacle_avoid_active;
  equation
    degraded_nav_active = if estimator_quality < estimator_degraded_threshold then 1 else if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 1 else 0;
    obstacle_avoid_active = if obstacle_margin < obstacle_warning_margin_m then 1 else 0;
    flight_mode = if degraded_nav_active > 0.5 then 6 else if obstacle_avoid_active > 0.5 then 4 else if time < takeoff_time_s then 3 else 5;
    active_setpoint_source = if degraded_nav_active > 0.5 then 90 else if obstacle_avoid_active > 0.5 then 60 else if time < takeoff_time_s then 30 else 40;
    safety_status = if degraded_nav_active > 0.5 then 3 else if obstacle_avoid_active > 0.5 then 2 else 0;
    event_code = if degraded_nav_active > 0.5 then 60 else if obstacle_avoid_active > 0.5 then 40 else if time < takeoff_time_s then 30 else 50;
    reference_position[1] = if flight_mode >= 6 then 0 else trajectory.position_command[1];
    reference_position[2] = if flight_mode >= 6 then 0 else trajectory.position_command[2];
    reference_position[3] = if flight_mode >= 6 then return_altitude_m else if flight_mode >= 3 then trajectory.position_command[3] else landing_altitude_m;
    yaw_reference = 0;
    z_reference_rate = 0;
    health = min(estimator_quality, if obstacle_margin >= obstacle_warning_margin_m then 1 else 0.6);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {80, 80, 80}, fillColor = {248, 248, 248}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 14}, extent = {{-96, -72}, {96, 72}}, fileName = "modelica://MoSimQuadrotorModel/Plant/Resources/Images/ORIN_NX.png"),
        Text(origin = {0, -82}, extent = {{-95, 14}, {95, -14}}, textString = "ORIN NX", textColor = {80, 80, 80})}));
    annotation(__MWORKS(hide=true));
  end ORINNXMissionComputerModule;

  block SystemSupervisorModule
    "System-level failsafe supervisor for exported mode/event evidence"
    parameter Real degraded_nav_start_s = 1e9;
    parameter Real degraded_nav_end_s = 1e9;
    parameter Real battery_low_start_s = 1e9;
    parameter Real battery_low_end_s = 1e9;
    parameter Real offboard_loss_start_s = 1e9;
    parameter Real offboard_loss_end_s = 1e9;
    parameter Real mission_failure_start_s = 1e9;
    parameter Real mission_failure_end_s = 1e9;
    parameter Real geofence_breach_start_s = 1e9;
    parameter Real geofence_breach_end_s = 1e9;
    parameter Real battery_low_threshold = 0.1;
    parameter Real takeoff_time_s = 3.0;
    Modelica.Blocks.Interfaces.RealInput voltage_margin
      annotation (Placement(transformation(origin = {-110, 75}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput degraded_nav_active
      annotation (Placement(transformation(origin = {110, 60}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput obstacle_avoid_active
      annotation (Placement(transformation(origin = {110, 35}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_quality
      annotation (Placement(transformation(origin = {110, 10}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_mode
      annotation (Placement(transformation(origin = {110, -15}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput flight_mode
      annotation (Placement(transformation(origin = {110, -40}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput active_setpoint_source
      annotation (Placement(transformation(origin = {110, -65}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput safety_status
      annotation (Placement(transformation(origin = {110, -90}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput event_code
      annotation (Placement(transformation(origin = {110, -115}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput battery_low_active
      annotation (Placement(transformation(origin = {110, -140}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput offboard_loss_active
      annotation (Placement(transformation(origin = {110, -165}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput mission_failure_active
      annotation (Placement(transformation(origin = {110, -190}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput geofence_breach_active
      annotation (Placement(transformation(origin = {110, -215}, extent = {{-5, -5}, {5, 5}})));
  equation
    degraded_nav_active = if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 1 else 0;
    battery_low_active = if voltage_margin < battery_low_threshold then 1 else if time >= battery_low_start_s and time <= battery_low_end_s then 1 else 0;
    offboard_loss_active = if time >= offboard_loss_start_s and time <= offboard_loss_end_s then 1 else 0;
    mission_failure_active = if time >= mission_failure_start_s and time <= mission_failure_end_s then 1 else 0;
    geofence_breach_active = if time >= geofence_breach_start_s and time <= geofence_breach_end_s then 1 else 0;
    obstacle_avoid_active = 0;
    estimator_quality = if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 0.45 else 1;
    estimator_mode = if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 2 else 1;
    flight_mode = if geofence_breach_active > 0.5 then 6 else if mission_failure_active > 0.5 then 6 else if offboard_loss_active > 0.5 then 6 else if battery_low_active > 0.5 then 6 else if degraded_nav_active > 0.5 then 6 else if time < takeoff_time_s then 3 else 5;
    active_setpoint_source = if geofence_breach_active > 0.5 then 94 else if mission_failure_active > 0.5 then 93 else if offboard_loss_active > 0.5 then 92 else if battery_low_active > 0.5 then 91 else if degraded_nav_active > 0.5 then 90 else if time < takeoff_time_s then 30 else 40;
    safety_status = if geofence_breach_active > 0.5 then 7 else if mission_failure_active > 0.5 then 6 else if offboard_loss_active > 0.5 then 5 else if battery_low_active > 0.5 then 4 else if degraded_nav_active > 0.5 then 3 else 0;
    event_code = if geofence_breach_active > 0.5 then 64 else if mission_failure_active > 0.5 then 63 else if offboard_loss_active > 0.5 then 62 else if battery_low_active > 0.5 then 61 else if degraded_nav_active > 0.5 then 60 else if time < takeoff_time_s then 30 else 50;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {120, 0, 0}, fillColor = {255, 245, 245}, fillPattern = FillPattern.Solid),
        Text(origin = {0, 18}, extent = {{-95, 25}, {95, -25}}, textString = "System", textColor = {120, 0, 0}),
        Text(origin = {0, -38}, extent = {{-95, 25}, {95, -25}}, textString = "Supervisor", textColor = {120, 0, 0})}));
    annotation(__MWORKS(hide=true));
  end SystemSupervisorModule;

  block BatteryPowerModule
    "Battery power source abstraction for system-level graphical review"
    parameter Real nominal_voltage = 16.8;
    parameter Real low_voltage = 14.0;
    parameter Real voltage_drop_per_second = 0.002;
    Modelica.Blocks.Interfaces.RealOutput bus_voltage
      annotation (Placement(transformation(origin = {110, 40}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput power_ok
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput voltage_margin
      annotation (Placement(transformation(origin = {110, -40}, extent = {{-5, -5}, {5, 5}})));
  equation
    bus_voltage = max(low_voltage, nominal_voltage - voltage_drop_per_second * time);
    voltage_margin = max(0, (bus_voltage - low_voltage) / (nominal_voltage - low_voltage));
    power_ok = if voltage_margin > 0.05 then 1 else 0;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {80, 80, 80}, fillColor = {250, 250, 250}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 8}, extent = {{-96, -62}, {96, 62}}, fileName = "modelica://MoSimQuadrotorModel/Plant/Resources/Images/Battery.png"),
        Text(origin = {0, -78}, extent = {{-90, 14}, {90, -14}}, textString = "Battery", textColor = {80, 80, 80})}));
    annotation(__MWORKS(hide=true));
  end BatteryPowerModule;

  block ESCDriveModule
    "Electronic speed controller abstraction between control allocation and motors"
    parameter Real nominal_voltage = 16.8;
    parameter Real motor_limit_abs = 80.0;
    Modelica.Blocks.Interfaces.RealInput motor_command_raw[4]
      annotation (Placement(transformation(origin = {-110, 45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput bus_voltage
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput power_ok
      annotation (Placement(transformation(origin = {-110, -45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput motor_command[4]
      annotation (Placement(transformation(origin = {110, 35}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput esc_health[4]
      annotation (Placement(transformation(origin = {110, -20}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput saturation_ratio_est
      annotation (Placement(transformation(origin = {110, -65}, extent = {{-5, -5}, {5, 5}})));
    Real voltage_scale;
    Real saturated_count;
  equation
    voltage_scale = max(0.0, min(1.0, bus_voltage / nominal_voltage));
    saturated_count =
      (if abs(motor_command_raw[1] * voltage_scale) >= motor_limit_abs then 1 else 0) +
      (if abs(motor_command_raw[2] * voltage_scale) >= motor_limit_abs then 1 else 0) +
      (if abs(motor_command_raw[3] * voltage_scale) >= motor_limit_abs then 1 else 0) +
      (if abs(motor_command_raw[4] * voltage_scale) >= motor_limit_abs then 1 else 0);
    for i in 1:4 loop
      motor_command[i] = if power_ok > 0.5 then max(-motor_limit_abs, min(motor_limit_abs, motor_command_raw[i] * voltage_scale)) else 0;
      esc_health[i] = power_ok * voltage_scale;
    end for;
    saturation_ratio_est = saturated_count / 4;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {70, 70, 120}, fillColor = {246, 246, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 8}, extent = {{-96, -62}, {96, 62}}, fileName = "modelica://MoSimQuadrotorModel/Plant/Resources/Images/ESC.png"),
        Text(origin = {0, -78}, extent = {{-90, 14}, {90, -14}}, textString = "ESC", textColor = {70, 70, 120})}));
    annotation(__MWORKS(hide=true));
  end ESCDriveModule;

  block AWFFControllerModule
    "Encapsulated AWFF graphical controller, error generation, hover trim, and motor command scaling"
    parameter Real hover_motor_speed_cmd = MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s;
    parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604;
    parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd;
    Modelica.Blocks.Interfaces.RealInput reference_position[3]
      annotation (Placement(transformation(origin = {-110, 70}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput position_est[3]
      annotation (Placement(transformation(origin = {-110, 25}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput attitude_est[3]
      annotation (Placement(transformation(origin = {-110, -20}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput yaw_reference
      annotation (Placement(transformation(origin = {-110, -60}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput z_reference_rate
      annotation (Placement(transformation(origin = {-110, -90}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput motor_command[4]
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-5, -5}, {5, 5}})));

    Modelica.Blocks.Math.Feedback x_error;
    Modelica.Blocks.Math.Feedback y_error;
    Modelica.Blocks.Math.Feedback z_error;
    AWFF_FullControllerEquation_Sysblock controller;
    Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Add motor1_hover_sum;
    Modelica.Blocks.Math.Add motor2_hover_sum;
    Modelica.Blocks.Math.Add motor3_hover_sum;
    Modelica.Blocks.Math.Add motor4_hover_sum;
  equation
    connect(reference_position[1], x_error.u1);
    connect(position_est[1], x_error.u2);
    connect(reference_position[2], y_error.u1);
    connect(position_est[2], y_error.u2);
    connect(reference_position[3], z_error.u1);
    connect(position_est[3], z_error.u2);
    connect(x_error.y, controller.x_error);
    connect(y_error.y, controller.y_error);
    connect(z_error.y, controller.z_error);
    connect(z_reference_rate, controller.z_ref_rate);
    connect(attitude_est[1], controller.roll_mea);
    connect(attitude_est[2], controller.pitch_mea);
    connect(attitude_est[3], controller.yaw_mea);
    connect(yaw_reference, controller.yaw_ref);
    connect(controller.y, motor1_delta_scale.u);
    connect(controller.y1, motor2_delta_scale.u);
    connect(controller.y2, motor3_delta_scale.u);
    connect(controller.y3, motor4_delta_scale.u);
    connect(motor1_delta_scale.y, motor1_hover_sum.u1);
    connect(motor2_delta_scale.y, motor2_hover_sum.u1);
    connect(motor3_delta_scale.y, motor3_hover_sum.u1);
    connect(motor4_delta_scale.y, motor4_hover_sum.u1);
    connect(hover_u1.y, motor1_hover_sum.u2);
    connect(hover_u2.y, motor2_hover_sum.u2);
    connect(hover_u3.y, motor3_hover_sum.u2);
    connect(hover_u4.y, motor4_hover_sum.u2);
    connect(motor1_hover_sum.y, motor_command[1]);
    connect(motor2_hover_sum.y, motor_command[2]);
    connect(motor3_hover_sum.y, motor_command[3]);
    connect(motor4_hover_sum.y, motor_command[4]);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 130, 0}, fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-70, 45}, {70, -45}}, lineColor = {0, 130, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid),
        Text(origin = {0, 5}, extent = {{-65, 25}, {65, -25}}, textString = "AWFF", textColor = {0, 130, 0}),
        Text(origin = {0, -72}, extent = {{-90, 15}, {90, -15}}, textString = "controller", textColor = {0, 130, 0})}));
    annotation(__MWORKS(hide=true));
  end AWFFControllerModule;

  model MotorDriveModule
    "Motor actuator with speed feedback, shown as one top-level motor block"
    parameter Real initial_speed = MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s;
    Modelica.Blocks.Interfaces.RealInput command
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput speed
      annotation (Placement(transformation(origin = {110, -45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Mechanics.Rotational.Interfaces.Flange_b flange
      annotation (Placement(transformation(origin = {110, 45}, extent = {{-5, -5}, {5, 5}})));
    MoSimQuadrotorModel.Plant.Electricals.Actuator actuator(dcpm(wMechanical(start = initial_speed)));
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor;
  equation
    connect(command, actuator.u);
    connect(actuator.flange_a, flange);
    connect(actuator.flange_a, speedSensor.flange);
    connect(speedSensor.w, speed);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {130, 0, 130}, fillColor = {252, 244, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 14}, extent = {{-96, -55}, {96, 55}}, fileName = "modelica://MoSimQuadrotorModel/Plant/Resources/Images/motor.png"),
        Text(origin = {0, -80}, extent = {{-80, 14}, {80, -14}}, textString = "%name", textColor = {130, 0, 130})}));
    annotation(__MWORKS(hide=true));
  end MotorDriveModule;

  model Sunray150AirframeSensorModule
    "Sunray150 airframe, rotor flanges, and sensor outputs"
    Modelica.Mechanics.Rotational.Interfaces.Flange_a rotor_flange[4]
      annotation (Placement(transformation(origin = {-110, 40}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput position[3]
      annotation (Placement(transformation(origin = {110, 45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput attitude[3]
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-5, -5}, {5, 5}})));
    MoSimQuadrotorModel.Plant.Mechanics.QuadChassis chassis;
    MoSimQuadrotorModel.Plant.Sensors.Sensors sensors;
  equation
    connect(rotor_flange[1], chassis.flange_a);
    connect(rotor_flange[2], chassis.flange_a1);
    connect(rotor_flange[3], chassis.flange_a2);
    connect(rotor_flange[4], chassis.flange_a3);
    connect(chassis.frame_a, sensors.frame_a);
    connect(sensors.PosMea, position);
    connect(sensors.AngleMea, attitude);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {160, 80, 0}, fillColor = {255, 250, 240}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 10}, extent = {{-96, -96}, {96, 96}}, fileName = "modelica://MoSimQuadrotorModel/Plant/Resources/Images/Sunray150.png"),
        Text(origin = {0, -86}, extent = {{-95, 14}, {95, -14}}, textString = "Sunray150", textColor = {160, 80, 0})}));
    annotation(__MWORKS(hide=true));
  end Sunray150AirframeSensorModule;

  PerceptionInterfaceModule perception
    annotation (Placement(transformation(origin = {-760, -145}, extent = {{-135, -135}, {135, 135}})));
  V6XFlightControllerModule flight_controller
    annotation (Placement(transformation(origin={-275,-230},
extent={{-125,-125},{125,125}})));
  ORINNXMissionComputerModule mission_computer
    annotation (Placement(transformation(origin = {-760, 170}, extent = {{-130, -130}, {130, 130}})));
  SystemSupervisorModule system_supervisor(
    degraded_nav_start_s = system_degraded_nav_start_s,
    degraded_nav_end_s = system_degraded_nav_end_s,
    battery_low_start_s = system_battery_low_start_s,
    battery_low_end_s = system_battery_low_end_s,
    offboard_loss_start_s = system_offboard_loss_start_s,
    offboard_loss_end_s = system_offboard_loss_end_s,
    mission_failure_start_s = system_mission_failure_start_s,
    mission_failure_end_s = system_mission_failure_end_s,
    geofence_breach_start_s = system_geofence_breach_start_s,
    geofence_breach_end_s = system_geofence_breach_end_s)
    annotation (Placement(transformation(origin = {-455, 300}, extent = {{-70, -70}, {70, 70}})));
  BatteryPowerModule battery(voltage_drop_per_second = system_battery_voltage_drop_per_second)
    annotation (Placement(transformation(origin = {-90, -315}, extent = {{-72, -72}, {72, 72}})));
  AWFFControllerModule controller(
    hover_motor_speed_cmd = hover_motor_speed_cmd,
    legacy_hover_motor_speed_cmd = legacy_hover_motor_speed_cmd,
    motor_command_scale = motor_command_scale)
    annotation (Placement(transformation(origin={-285,149},
extent={{-110,-110},{110,110}})));
  ESCDriveModule esc
    annotation (Placement(transformation(origin = {-20, -90}, extent = {{-80, -80}, {80, 80}})));
  MotorDriveModule motor1(initial_speed = hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {250, 255}, extent = {{-72, -72}, {72, 72}})));
  MotorDriveModule motor2(initial_speed = -hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {250, 85}, extent = {{-72, -72}, {72, 72}})));
  MotorDriveModule motor3(initial_speed = hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {250, -85}, extent = {{-72, -72}, {72, 72}})));
  MotorDriveModule motor4(initial_speed = -hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {250, -255}, extent = {{-72, -72}, {72, 72}})));
  Sunray150AirframeSensorModule airframe
    annotation (Placement(transformation(origin = {630, 0}, extent = {{-150, -150}, {150, 150}})));
  Real system_degraded_nav_active;
  Real system_obstacle_avoid_active;
  Real system_estimator_quality;
  Real system_estimator_mode;
  Real system_flight_mode;
  Real system_active_setpoint_source;
  Real system_failsafe_setpoint_source;
  Real system_safety_status;
  Real system_failsafe_safety_status;
  Real system_failsafe_status_code;
  Real system_failsafe_source_code;
  Real system_event_code;
  Real system_failsafe_event_code;
  Real system_battery_voltage;
  Real system_voltage_margin;
  Real system_esc_saturation_ratio;
  Real system_battery_low_active;
  Real system_offboard_loss_active;
  Real system_mission_failure_active;
  Real system_geofence_breach_active;
  Real system_supervisor_keepalive;

equation
  system_degraded_nav_active = system_supervisor.degraded_nav_active;
  system_obstacle_avoid_active = system_supervisor.obstacle_avoid_active;
  system_estimator_quality = system_supervisor.estimator_quality;
  system_estimator_mode = system_supervisor.estimator_mode;
  system_flight_mode = system_supervisor.flight_mode;
  system_active_setpoint_source = system_supervisor.active_setpoint_source;
  system_safety_status = system_supervisor.safety_status;
  system_battery_voltage = battery.bus_voltage;
  system_voltage_margin = battery.voltage_margin;
  system_esc_saturation_ratio = esc.saturation_ratio_est;
  system_battery_low_active = system_supervisor.battery_low_active;
  system_offboard_loss_active = system_supervisor.offboard_loss_active;
  system_mission_failure_active = system_supervisor.mission_failure_active;
  system_geofence_breach_active = system_supervisor.geofence_breach_active;
  system_failsafe_safety_status = if time >= system_geofence_breach_start_s and time <= system_geofence_breach_end_s then 7 else if time >= system_mission_failure_start_s and time <= system_mission_failure_end_s then 6 else if time >= system_offboard_loss_start_s and time <= system_offboard_loss_end_s then 5 else if battery.voltage_margin < 0.1 or (time >= system_battery_low_start_s and time <= system_battery_low_end_s) then 4 else if time >= system_degraded_nav_start_s and time <= system_degraded_nav_end_s then 3 else 0;
  system_failsafe_setpoint_source = if system_failsafe_safety_status >= 3 then system_failsafe_safety_status + 87 else if time < 3.0 then 30 else 40;
  system_failsafe_event_code = if time >= system_geofence_breach_start_s and time <= system_geofence_breach_end_s then 64 else if time >= system_mission_failure_start_s and time <= system_mission_failure_end_s then 63 else if time >= system_offboard_loss_start_s and time <= system_offboard_loss_end_s then 62 else if battery.voltage_margin < 0.1 or (time >= system_battery_low_start_s and time <= system_battery_low_end_s) then 61 else if time >= system_degraded_nav_start_s and time <= system_degraded_nav_end_s then 60 else if time < 3.0 then 30 else 50;
  system_failsafe_status_code = if time >= system_geofence_breach_start_s and time <= system_geofence_breach_end_s then 7 else if time >= system_mission_failure_start_s and time <= system_mission_failure_end_s then 6 else if time >= system_offboard_loss_start_s and time <= system_offboard_loss_end_s then 5 else if battery.voltage_margin < 0.1 or (time >= system_battery_low_start_s and time <= system_battery_low_end_s) then 4 else if time >= system_degraded_nav_start_s and time <= system_degraded_nav_end_s then 3 else 0;
  system_failsafe_source_code = if time >= system_geofence_breach_start_s and time <= system_geofence_breach_end_s then 94 else if time >= system_mission_failure_start_s and time <= system_mission_failure_end_s then 93 else if time >= system_offboard_loss_start_s and time <= system_offboard_loss_end_s then 92 else if battery.voltage_margin < 0.1 or (time >= system_battery_low_start_s and time <= system_battery_low_end_s) then 91 else if time >= system_degraded_nav_start_s and time <= system_degraded_nav_end_s then 90 else if time < 3.0 then 30 else 40;
  system_event_code = system_failsafe_event_code;
  system_supervisor_keepalive = 0.001 * system_event_code + 0.001 * system_estimator_quality + 0.001 * system_battery_low_active + 0.001 * system_offboard_loss_active + 0.001 * system_mission_failure_active + 0.001 * system_geofence_breach_active;
  connect(airframe.position, perception.position_raw)
    annotation (Line(points = {{792, 68}, {825, 68}, {825, -385}, {-950, -385}, {-950, -124}, {-909, -124}}, color = {110, 130, 145}, thickness = 0.08));
  connect(perception.gps_position, flight_controller.gps_position)
    annotation (Line(origin={0,0},
points={{-611.5,-84.25},{-420.75,-84.25},{-420.75,-161.25},{-412.5,-161.25}},
color={110,130,145},
thickness=0.08));
  flight_controller.gps_valid = perception.gps_valid;
  connect(perception.local_position, mission_computer.local_position)
    annotation (Line(points = {{-611, -140}, {-575, -140}, {-575, 170}, {-903, 170}}, color = {110, 130, 145}, thickness = 0.08));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin)
    annotation (Line(points = {{-611, -182}, {-560, -182}, {-560, 122}, {-903, 122}}, color = {110, 130, 145}, thickness = 0.08));
  mission_computer.estimator_quality = flight_controller.estimator_quality;
  connect(airframe.attitude, flight_controller.attitude_raw)
    annotation (Line(origin={0,0},
points={{795,0},{804.5,0},{804.5,-357},{-420.75,-357},{-420.75,-217.5},{-412.5,-217.5}},
color={110,130,145},
thickness=0.08));
  connect(motor1.speed, flight_controller.motor_speed_raw[1])
    annotation (Line(origin={0,0},
points={{329.2,222.6},{-420.75,222.6},{-420.75,-286.25},{-412.5,-286.25}},
color={110,130,145},
thickness=0.08));
  connect(motor2.speed, flight_controller.motor_speed_raw[2])
    annotation (Line(origin={0,0},
points={{329.2,52.6},{334.8,52.6},{334.8,145},{-420.75,145},{-420.75,-286.25},{-412.5,-286.25}},
color={110,130,145},
thickness=0.08));
  connect(motor3.speed, flight_controller.motor_speed_raw[3])
    annotation (Line(origin={0,0},
points={{329.2,-117.4},{334.8,-117.4},{334.8,-357},{-420.75,-357},{-420.75,-286.25},{-412.5,-286.25}},
color={110,130,145},
thickness=0.08));
  connect(motor4.speed, flight_controller.motor_speed_raw[4])
    annotation (Line(origin={0,0},
points={{329.2,-287.4},{334.8,-287.4},{334.8,-357},{-420.75,-357},{-420.75,-286.25},{-412.5,-286.25}},
color={110,130,145},
thickness=0.08));
  connect(flight_controller.position_est, mission_computer.aircraft_position)
    annotation (Line(origin={0,0},
points={{-137.5,-161.25},{33.4584,-161.25},{33.4584,302},{-911.5,302},{-911.5,222},{-903,222}},
color={110,130,145},
thickness=0.08));
  connect(mission_computer.reference_position, controller.reference_position)
    annotation (Line(origin={0,0},
points={{-617,235},{-413.5,235},{-413.5,226},{-406,226}},
color={110,130,145},
thickness=0.08));
  connect(flight_controller.position_est, controller.position_est)
    annotation (Line(origin={0,0},
points={{-137.5,-161.25},{33.4584,-161.25},{33.4584,261},{-413.5,261},{-413.5,176.5},{-406,176.5}},
color={110,130,145},
thickness=0.08));
  connect(flight_controller.attitude_est, controller.attitude_est)
    annotation (Line(origin={0,0},
points={{-137.5,-217.5},{33.4584,-217.5},{33.4584,261},{-413.5,261},{-413.5,127},{-406,127}},
color={110,130,145},
thickness=0.08));
  connect(mission_computer.yaw_reference, controller.yaw_reference)
    annotation (Line(origin={0,0},
points={{-617,176.5},{-413.5,176.5},{-413.5,83},{-406,83}},
color={110,130,145},
thickness=0.08));
  connect(mission_computer.z_reference_rate, controller.z_reference_rate)
    annotation (Line(origin={0,0},
points={{-617,118},{-413.5,118},{-413.5,50},{-406,50}},
color={110,130,145},
thickness=0.08));
  connect(controller.motor_command, esc.motor_command_raw)
    annotation (Line(points = {{-164, 149}, {-120, 149}, {-120, -54}, {-108, -54}}, color = {110, 130, 145}, thickness = 0.08));
  connect(battery.bus_voltage, esc.bus_voltage)
    annotation (Line(points = {{-11, -286}, {-120, -286}, {-120, -90}, {-108, -90}}, color = {110, 130, 145}, thickness = 0.08));
  connect(battery.power_ok, esc.power_ok)
    annotation (Line(points = {{-11, -315}, {-130, -315}, {-130, -126}, {-108, -126}}, color = {110, 130, 145}, thickness = 0.08));
  connect(battery.voltage_margin, system_supervisor.voltage_margin)
    annotation (Line(points = {{-11, -344}, {20, -344}, {20, 352}, {-532, 352}}, color = {110, 130, 145}, thickness = 0.08));
  connect(esc.motor_command[1], motor1.command)
    annotation (Line(points = {{68, -62}, {95, -62}, {95, 255}, {171, 255}}, color = {110, 130, 145}, thickness = 0.08));
  connect(esc.motor_command[2], motor2.command)
    annotation (Line(points = {{68, -62}, {132, -62}, {132, 85}, {171, 85}}, color = {110, 130, 145}, thickness = 0.08));
  connect(esc.motor_command[3], motor3.command)
    annotation (Line(points = {{68, -62}, {132, -62}, {132, -85}, {171, -85}}, color = {110, 130, 145}, thickness = 0.08));
  connect(esc.motor_command[4], motor4.command)
    annotation (Line(points = {{68, -62}, {95, -62}, {95, -255}, {171, -255}}, color = {110, 130, 145}, thickness = 0.08));
  connect(motor1.flange, airframe.rotor_flange[1])
    annotation (Line(points = {{330, 288}, {430, 288}, {430, 60}, {465, 60}}, color = {115, 115, 115}, thickness = 0.1));
  connect(motor2.flange, airframe.rotor_flange[2])
    annotation (Line(points = {{330, 118}, {440, 118}, {440, 72}, {465, 72}}, color = {115, 115, 115}, thickness = 0.1));
  connect(motor3.flange, airframe.rotor_flange[3])
    annotation (Line(points = {{330, -52}, {440, -52}, {440, 84}, {465, 84}}, color = {115, 115, 115}, thickness = 0.1));
  connect(motor4.flange, airframe.rotor_flange[4])
    annotation (Line(points = {{330, -222}, {430, -222}, {430, 96}, {465, 96}}, color = {115, 115, 115}, thickness = 0.1));

  annotation(
    Diagram(coordinateSystem(extent={{-980,-430},{850,380}},
grid={5,5}),graphics = {Rectangle(origin={-760,10},
lineColor={0,0,127},
pattern=LinePattern.Dash,
extent={{-180,320},{180,-355}}), Text(origin={-760,355},
lineColor={0,0,127},
extent={{-150,14},{150,-14}},
textString="mission and perception",
textColor={0,0,127}), Rectangle(origin={-430,-145},
lineColor={100,70,20},
pattern=LinePattern.Dash,
extent={{-150,130},{150,-130}}), Text(origin={-270,-70},
lineColor={100,70,20},
extent={{-125,14},{125,-14}},
textString="flight controller",
textColor={100,70,20}), Rectangle(origin={-120,40},
lineColor={0,130,0},
pattern=LinePattern.Dash,
extent={{-145,150},{145,-150}}), Text(origin={-285,231},
lineColor={0,130,0},
extent={{-115,14},{115,-14}},
textString="control law",
textColor={0,130,0}), Rectangle(origin={-55,-205},
lineColor={70,70,120},
pattern=LinePattern.Dash,
extent={{-125,175},{125,-190}}), Text(origin={-55,-395},
lineColor={70,70,120},
extent={{-105,14},{105,-14}},
textString="power and ESC",
textColor={70,70,120}), Rectangle(origin={250,0},
lineColor={130,0,130},
pattern=LinePattern.Dash,
extent={{-100,340},{100,-340}}), Text(origin={250,360},
lineColor={130,0,130},
extent={{-95,14},{95,-14}},
textString="motor drives",
textColor={130,0,130}), Rectangle(origin={630,0},
lineColor={160,80,0},
pattern=LinePattern.Dash,
extent={{-180,185},{180,-185}}), Text(origin={630,210},
lineColor={160,80,0},
extent={{-130,14},{130,-14}},
textString="Sunray150 airframe",
textColor={160,80,0})}),
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Sunray150CompleteSystemGraphical_Sysblock;
