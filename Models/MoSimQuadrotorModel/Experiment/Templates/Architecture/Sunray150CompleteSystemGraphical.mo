within MoSimQuadrotorModel.Experiment.Templates.Architecture;
model Sunray150CompleteSystemGraphical
  "Sunray150 complete graphical system with px4ctrl data flow"
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
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealOutput gps_position[3] 
      annotation (Placement(transformation(origin = {110, 60}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealOutput local_position[3] 
      annotation (Placement(transformation(origin = {110, 20}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealOutput obstacle_margin 
      annotation (Placement(transformation(origin = {110, -20}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealOutput health 
      annotation (Placement(transformation(origin = {110, -55}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealOutput gps_valid 
      annotation (Placement(transformation(origin = {110, -75}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealOutput mid360_valid 
      annotation (Placement(transformation(origin = {110, -95}, extent = {{-8, -8}, {8, 8}})));
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
        Bitmap(origin = {-58, 18}, extent = {{-48, -48}, {48, 48}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/GPS.png"),
        Bitmap(origin = {58, 18}, extent = {{-48, -48}, {48, 48}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/MId360.png"),
        Text(origin = {0, -78}, extent = {{-100, 14}, {100, -14}}, textString = "GPS + Mid360", textColor = {0, 100, 150})}));
    annotation(__MWORKS(hide=true));
  end PerceptionInterfaceModule;

  block V6XFlightControllerModule
    "Top-level V6X flight-controller interface"
    parameter Real estimator_position_T = 0.08;
    parameter Real estimator_attitude_T = 0.03;
    parameter Real estimator_motor_T = 0.05;
    Modelica.Blocks.Interfaces.RealInput gps_position[3] 
      annotation (Placement(transformation(origin = {110, 65}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealInput attitude_raw[3] 
      annotation (Placement(transformation(origin = {110, 25}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealInput motor_speed_raw[4] 
      annotation (Placement(transformation(origin = {110, -25}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealInput gps_valid 
      annotation (Placement(transformation(origin = {110, -75}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput position_est[3] 
      annotation (Placement(transformation(origin = {-110, 65}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput attitude_est[3] 
      annotation (Placement(transformation(origin = {-110, 30}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput motor_speed_est[4] 
      annotation (Placement(transformation(origin = {-110, -5}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput health 
      annotation (Placement(transformation(origin = {-110, -35}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_quality 
      annotation (Placement(transformation(origin = {-110, -65}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_mode 
      annotation (Placement(transformation(origin = {-110, -90}, extent = {{-7, -7}, {7, 7}})));
  equation
    position_est = gps_position;
    attitude_est = attitude_raw;
    motor_speed_est = motor_speed_raw;
    estimator_quality = if gps_valid > 0.5 then 1 else 0.45;
    estimator_mode = if gps_valid > 0.5 then 1 else 2;
    health = estimator_quality;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {100, 70, 20}, fillColor = {255, 248, 235}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 14}, extent = {{-96, -54.154}, {96, 54.154}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/V6X.png"),
        Text(origin = {0, -78}, extent = {{-95, 14}, {95, -14}}, textString = "V6X", textColor = {100, 70, 20})}));
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
      annotation (Placement(transformation(origin = {-110, 50}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput local_position[3] 
      annotation (Placement(transformation(origin = {-110, 15}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput obstacle_margin 
      annotation (Placement(transformation(origin = {-110, -20}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput estimator_quality 
      annotation (Placement(transformation(origin = {-110, -55}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput reference_position[3] 
      annotation (Placement(transformation(origin = {110, 65}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput reference_velocity[3] 
      annotation (Placement(transformation(origin = {110, 42}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput reference_acceleration[3] 
      annotation (Placement(transformation(origin = {110, 20}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput yaw_reference 
      annotation (Placement(transformation(origin = {110, -2}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput z_reference_rate 
      annotation (Placement(transformation(origin = {110, -22}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput health 
      annotation (Placement(transformation(origin = {110, -10}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput flight_mode 
      annotation (Placement(transformation(origin = {110, -30}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput active_setpoint_source 
      annotation (Placement(transformation(origin = {110, -50}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput safety_status 
      annotation (Placement(transformation(origin = {110, -70}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput event_code 
      annotation (Placement(transformation(origin = {110, -90}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput obstacle_avoid_active 
      annotation (Placement(transformation(origin = {110, -112}, extent = {{-5, -5}, {5, 5}})));
    MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath trajectory(gain(k = 1));
    Real degraded_nav_active;
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
    for i in 1:3 loop
      reference_velocity[i] = if flight_mode >= 6 then 0 else trajectory.velocity_command[i];
      reference_acceleration[i] = if flight_mode >= 6 then 0 else trajectory.acceleration_command[i];
    end for;
    yaw_reference = 0;
    z_reference_rate = 0;
    health = min(estimator_quality, if obstacle_margin >= obstacle_warning_margin_m then 1 else 0.6);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {80, 80, 80}, fillColor = {248, 248, 248}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 14}, extent = {{-96, -72}, {96, 72}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/ORIN_NX.png"),
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
      annotation (Placement(transformation(origin = {-110, 75}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput degraded_nav_active 
      annotation (Placement(transformation(origin = {110, 85}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput obstacle_avoid_active 
      annotation (Placement(transformation(origin = {110, 70}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_quality 
      annotation (Placement(transformation(origin = {110, 55}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_mode 
      annotation (Placement(transformation(origin = {110, 40}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput flight_mode 
      annotation (Placement(transformation(origin = {110, 25}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput active_setpoint_source 
      annotation (Placement(transformation(origin = {110, 10}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput safety_status 
      annotation (Placement(transformation(origin = {110, -5}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput event_code 
      annotation (Placement(transformation(origin = {110, -20}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput battery_low_active 
      annotation (Placement(transformation(origin = {110, -35}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput offboard_loss_active 
      annotation (Placement(transformation(origin = {110, -50}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput mission_failure_active 
      annotation (Placement(transformation(origin = {110, -65}, extent = {{-7, -7}, {7, 7}})));
    Modelica.Blocks.Interfaces.RealOutput geofence_breach_active 
      annotation (Placement(transformation(origin = {110, -80}, extent = {{-7, -7}, {7, 7}})));
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
      annotation (Placement(transformation(origin = {110, 40}, extent = {{-9, -9}, {9, 9}})));
    Modelica.Blocks.Interfaces.RealOutput power_ok 
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-9, -9}, {9, 9}})));
    Modelica.Blocks.Interfaces.RealOutput voltage_margin 
      annotation (Placement(transformation(origin = {110, -40}, extent = {{-9, -9}, {9, 9}})));
  equation
    bus_voltage = max(low_voltage, nominal_voltage - voltage_drop_per_second * time);
    voltage_margin = max(0, (bus_voltage - low_voltage) / (nominal_voltage - low_voltage));
    power_ok = if voltage_margin > 0.05 then 1 else 0;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {80, 80, 80}, fillColor = {250, 250, 250}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 20}, extent = {{-96, -76.304}, {96, 76.304}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/Battery.png"),
        Text(origin = {0, -78}, extent = {{-90, 14}, {90, -14}}, textString = "Battery", textColor = {80, 80, 80})}));
    annotation(__MWORKS(hide=true));
  end BatteryPowerModule;

  block ESCDriveModule
    "Electronic speed controller abstraction between control allocation and motors"
    parameter Real nominal_voltage = 16.8;
    parameter Real motor_limit_abs = 80.0;
    Modelica.Blocks.Interfaces.RealInput motor_command_raw[4] 
      annotation (Placement(transformation(origin = {-110, 45}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealInput bus_voltage 
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealInput power_ok 
      annotation (Placement(transformation(origin = {-110, -45}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealOutput motor_command[4] 
      annotation (Placement(transformation(origin = {110, 35}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealOutput esc_health[4] 
      annotation (Placement(transformation(origin = {110, -20}, extent = {{-8, -8}, {8, 8}})));
    Modelica.Blocks.Interfaces.RealOutput saturation_ratio_est 
      annotation (Placement(transformation(origin = {110, -65}, extent = {{-8, -8}, {8, 8}})));
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
        Bitmap(origin = {0, 18}, extent = {{-80, -75.649}, {80, 75.649}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/ESC.png"),
        Text(origin = {0, -78}, extent = {{-90, 14}, {90, -14}}, textString = "ESC", textColor = {70, 70, 120})}));
    annotation(__MWORKS(hide=true));
  end ESCDriveModule;

  block Px4CtrlControllerModule
    "px4ctrl ATTITUDE_THRUST loop with the FormalRunner sampled boundary"
    parameter Real controller_sample_period_s = 0.01;
    Modelica.Blocks.Interfaces.RealInput reference_position[3] 
      annotation (Placement(transformation(origin = {-110, 75}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput reference_velocity[3] 
      annotation (Placement(transformation(origin = {-110, 45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput reference_acceleration[3] 
      annotation (Placement(transformation(origin = {-110, 15}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput position_est[3] 
      annotation (Placement(transformation(origin = {-110, -20}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput attitude_est[3] 
      annotation (Placement(transformation(origin = {-110, -55}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput motor_command[4] 
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-5, -5}, {5, 5}})));

    MoSimQuadrotorModel.Control.Adapters.Px4CtrlAttitudeThrustAdapter px4ctrl_outer_loop 
      annotation (Placement(transformation(origin = {-5, 42}, extent = {{-34, -24}, {34, 24}})));
    MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator offline_inner_allocator 
      annotation (Placement(transformation(origin = {65, 18}, extent = {{-34, -24}, {34, 24}})));
    Modelica.Blocks.Discrete.UnitDelay sampled_position_ref[3](
      each samplePeriod = controller_sample_period_s, each y_start = 0);
    Modelica.Blocks.Discrete.UnitDelay sampled_velocity_ref[3](
      each samplePeriod = controller_sample_period_s, each y_start = 0);
    Modelica.Blocks.Discrete.UnitDelay sampled_acceleration_ref[3](
      each samplePeriod = controller_sample_period_s, each y_start = 0);
    Modelica.Blocks.Discrete.UnitDelay sampled_position[3](
      each samplePeriod = controller_sample_period_s, each y_start = 0);
    Modelica.Blocks.Discrete.UnitDelay sampled_attitude[3](
      each samplePeriod = controller_sample_period_s, each y_start = 0);
    Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
      each k = 1,
      each T = 0.05,
      each initType = Modelica.Blocks.Types.Init.InitialOutput,
      each y_start = 0) 
      annotation (Placement(transformation(origin = {-20, -62}, extent = {{-18, -12}, {18, 12}})));
  equation
    connect(reference_position, sampled_position_ref.u);
    connect(sampled_position_ref.y, px4ctrl_outer_loop.position_ref);
    connect(reference_velocity, sampled_velocity_ref.u);
    connect(sampled_velocity_ref.y, px4ctrl_outer_loop.velocity_ref);
    connect(reference_acceleration, sampled_acceleration_ref.u);
    connect(sampled_acceleration_ref.y, px4ctrl_outer_loop.acceleration_ref);
    connect(position_est, sampled_position.u);
    connect(sampled_position.y, px4ctrl_outer_loop.position_mea);
    connect(sampled_position.y, velocity_estimator.u);
    connect(velocity_estimator.y, px4ctrl_outer_loop.velocity_mea);
    connect(attitude_est, sampled_attitude.u);
    connect(sampled_attitude.y, px4ctrl_outer_loop.attitude_mea);
    connect(px4ctrl_outer_loop.attitude_ref, offline_inner_allocator.attitude_ref) 
      annotation (Line(points = {{29, 52}, {31, 52}}, color = {0, 0, 127}));
    connect(sampled_attitude.y, offline_inner_allocator.attitude_mea) 
      annotation (Line(points = {{-60, -55}, {35, -55}, {35, 18}}, color = {0, 0, 127}));
    connect(px4ctrl_outer_loop.collective_thrust_delta, offline_inner_allocator.collective_thrust_delta) 
      annotation (Line(points = {{29, 28}, {31, 28}, {31, -6}}, color = {0, 0, 127}));
    connect(offline_inner_allocator.rotor_command, motor_command) 
      annotation (Line(points = {{99, 18}, {110, 18}, {110, 0}}, color = {0, 0, 127}));
    annotation (
      Diagram(coordinateSystem(extent = {{-130, -90}, {130, 90}}, grid = {2, 2})),
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 130, 0}, fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-70, 45}, {70, -45}}, lineColor = {0, 130, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid),
        Text(origin = {0, 8}, extent = {{-65, 25}, {65, -25}}, textString = "px4ctrl", textColor = {0, 130, 0}),
        Text(origin = {0, -66}, extent = {{-90, 15}, {90, -15}}, textString = "outer loop + allocator", textColor = {0, 130, 0})}));
    annotation(__MWORKS(hide=true));
  end Px4CtrlControllerModule;

  block MotorDriveModule
    "Visible motor command channel backed by the canonical Sunray150 assembly"
    Modelica.Blocks.Interfaces.RealInput command 
      annotation (Placement(transformation(origin = {-110, 35}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput rotor_speed_raw 
      annotation (Placement(transformation(origin = {-110, -35}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput rotor_command 
      annotation (Placement(transformation(origin = {110, 35}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput speed 
      annotation (Placement(transformation(origin = {110, -35}, extent = {{-5, -5}, {5, 5}})));
  equation
    rotor_command = command;
    speed = rotor_speed_raw;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {130, 0, 130}, fillColor = {252, 244, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 14}, extent = {{-96, -54.48}, {96, 54.48}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/motor.png"),
        Text(origin = {0, -80}, extent = {{-80, 14}, {80, -14}}, textString = "%name", textColor = {130, 0, 130})}));
    annotation(__MWORKS(hide=true));
  end MotorDriveModule;

  block MotorTelemetryModule
    "Grouped rotor-speed feedback used to keep the top-level diagram readable"
    Modelica.Blocks.Interfaces.RealInput rotor_speed_raw[4] 
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput rotor_speed_est[4] 
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-5, -5}, {5, 5}})));
  equation
    rotor_speed_est = rotor_speed_raw;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {70, 70, 70}, fillColor = {250, 250, 250}, fillPattern = FillPattern.Solid),
        Text(origin = {0, 18}, extent = {{-92, 18}, {92, -18}}, textString = "Motor telemetry", textColor = {70, 70, 70}),
        Text(origin = {0, -42}, extent = {{-82, 14}, {82, -14}}, textString = "speed feedback", textColor = {70, 70, 70})}));
    annotation(__MWORKS(hide=true));
  end MotorTelemetryModule;

  model Sunray150AirframeSensorModule
    "Canonical Sunray150 physical assembly with state and rotor-speed outputs"
    Modelica.Blocks.Interfaces.RealInput rotor_command[4] 
      annotation (Placement(transformation(origin = {-110, 45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput position[3] 
      annotation (Placement(transformation(origin = {110, 45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput attitude[3] 
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput rotor_speed[4] 
      annotation (Placement(transformation(origin = {110, -45}, extent = {{-5, -5}, {5, 5}})));
    MoSimQuadrotorModel.Vehicle.Sunray150Assembly assembly;
  equation
    connect(rotor_command, assembly.rotor_command);
    connect(assembly.position, position);
    connect(assembly.attitude, attitude);
    connect(assembly.rotor_speed, rotor_speed);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {160, 80, 0}, fillColor = {255, 250, 240}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 10}, extent = {{-96, -96}, {96, 96}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/Sunray150.png"),
        Text(origin = {0, -86}, extent = {{-95, 14}, {95, -14}}, textString = "Sunray150", textColor = {160, 80, 0})}));
    annotation(__MWORKS(hide=true));
  end Sunray150AirframeSensorModule;

  PerceptionInterfaceModule perception 
    annotation (Placement(transformation(origin = {375, -185}, extent = {{-55, -55}, {55, 55}})));
  V6XFlightControllerModule flight_controller 
    annotation (Placement(transformation(origin = {-250, -185}, extent = {{-60, -60}, {60, 60}})));
  ORINNXMissionComputerModule mission_computer 
    annotation (Placement(transformation(origin = {-460, 120}, extent = {{-60, -60}, {60, 60}})));
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
    annotation (Placement(transformation(origin = {-460, -175}, extent = {{-35, -35}, {35, 35}})));
  BatteryPowerModule battery(voltage_drop_per_second = system_battery_voltage_drop_per_second) 
    annotation (Placement(transformation(origin = {-60, -175}, extent = {{-45, -45}, {45, 45}})));
  Px4CtrlControllerModule controller 
    annotation (Placement(transformation(origin = {-250, 120}, extent = {{-75, -75}, {75, 75}})));
  ESCDriveModule esc 
    annotation (Placement(transformation(origin = {-60, 120}, extent = {{-50, -50}, {50, 50}})));
  MotorDriveModule motor1 
    annotation (Placement(transformation(origin = {115, 170}, extent = {{-35, -35}, {35, 35}})));
  MotorDriveModule motor2 
    annotation (Placement(transformation(origin = {115, 95}, extent = {{-35, -35}, {35, 35}})));
  MotorDriveModule motor3 
    annotation (Placement(transformation(origin = {115, 20}, extent = {{-35, -35}, {35, 35}})));
  MotorDriveModule motor4 
    annotation (Placement(transformation(origin = {115, -55}, extent = {{-35, -35}, {35, 35}})));
  Sunray150AirframeSensorModule airframe 
    annotation (Placement(transformation(origin = {380, 80}, extent = {{-100, -100}, {100, 100}})));
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
  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real position_error_norm;

equation
  system_degraded_nav_active = system_supervisor.degraded_nav_active;
  system_obstacle_avoid_active = mission_computer.obstacle_avoid_active;
  system_estimator_quality = flight_controller.estimator_quality;
  system_estimator_mode = flight_controller.estimator_mode;
  system_flight_mode = if system_supervisor.safety_status > 0.5 then system_supervisor.flight_mode else mission_computer.flight_mode;
  system_active_setpoint_source = if system_supervisor.safety_status > 0.5 then system_supervisor.active_setpoint_source else mission_computer.active_setpoint_source;
  system_safety_status = if system_supervisor.safety_status > 0.5 then system_supervisor.safety_status else mission_computer.safety_status;
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
  system_event_code = if system_failsafe_safety_status > 0.5 then system_failsafe_event_code else mission_computer.event_code;
  system_supervisor_keepalive = 0.001 * system_event_code + 0.001 * system_estimator_quality + 0.001 * system_battery_low_active + 0.001 * system_offboard_loss_active + 0.001 * system_mission_failure_active + 0.001 * system_geofence_breach_active;
  position_ref = mission_computer.reference_position;
  position = airframe.position;
  attitude = airframe.attitude;
  rotor_command = esc.motor_command;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);
  connect(airframe.position, perception.position_raw) 
    annotation (Line(points = {{480, 125}, {540, 125}, {540, -300}, {19.5, -300}, {19.5, -185}}, color = {110, 130, 145}, thickness = 0.08));
  connect(perception.gps_position, flight_controller.gps_position) 
    annotation (Line(points = {{140.5, -152}, {220, -152}, {220, -270}, {-184, -270}, {-184, -146}}, color = {110, 130, 145}, thickness = 0.08));
  flight_controller.gps_valid = perception.gps_valid;
  connect(perception.local_position, mission_computer.local_position) 
    annotation (Line(points = {{140.5, -174}, {220, -174}, {220, -285}, {-560, -285}, {-560, 129}, {-526, 129}}, color = {110, 130, 145}, thickness = 0.08, visible = false));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin) 
    annotation (Line(points = {{140.5, -196}, {230, -196}, {230, -290}, {-570, -290}, {-570, 108}, {-526, 108}}, color = {110, 130, 145}, thickness = 0.08, visible = false));
  mission_computer.estimator_quality = flight_controller.estimator_quality;
  connect(airframe.attitude, flight_controller.attitude_raw) 
    annotation (Line(points = {{480, 80}, {525, 80}, {525, -125}, {-184, -125}, {-184, -170}}, color = {110, 130, 145}, thickness = 0.08, visible = false));
  connect(airframe.rotor_speed, flight_controller.motor_speed_raw) 
    annotation (Line(points = {{480, 35}, {510, 35}, {510, -270}, {-184, -270}, {-184, -200}}, color = {110, 130, 145}, thickness = 0.08, visible = false));
  connect(flight_controller.position_est, mission_computer.aircraft_position) 
    annotation (Line(points = {{-316, -146}, {-365, -146}, {-365, -80}, {-545, -80}, {-545, 150}, {-526, 150}}, color = {110, 130, 145}, thickness = 0.08, visible = false));
  connect(mission_computer.reference_position, controller.reference_position) 
    annotation (Line(points = {{-394, 159}, {-365, 159}, {-365, 172.5}, {-332.5, 172.5}}, color = {110, 130, 145}, thickness = 0.08));
  connect(mission_computer.reference_velocity, controller.reference_velocity) 
    annotation (Line(points = {{-394, 145}, {-365, 145}, {-365, 150}, {-332.5, 150}}, color = {110, 130, 145}, thickness = 0.08));
  connect(mission_computer.reference_acceleration, controller.reference_acceleration) 
    annotation (Line(points = {{-394, 132}, {-365, 132}, {-365, 127.5}, {-332.5, 127.5}}, color = {110, 130, 145}, thickness = 0.08));
  connect(flight_controller.position_est, controller.position_est) 
    annotation (Line(points = {{-316, -146}, {-345, -146}, {-345, 97.5}, {-332.5, 97.5}}, color = {110, 130, 145}, thickness = 0.08));
  connect(flight_controller.attitude_est, controller.attitude_est) 
    annotation (Line(points = {{-316, -167}, {-355, -167}, {-355, 71.25}, {-332.5, 71.25}}, color = {110, 130, 145}, thickness = 0.08));
  connect(controller.motor_command, esc.motor_command_raw) 
    annotation (Line(points = {{-167.5, 120}, {-140, 120}, {-140, 142.5}, {-115, 142.5}}, color = {110, 130, 145}, thickness = 0.08));
  connect(battery.bus_voltage, esc.bus_voltage) 
    annotation (Line(points = {{-19.5, -157}, {-125, -157}, {-125, 120}, {-115, 120}}, color = {110, 130, 145}, thickness = 0.08));
  connect(battery.power_ok, esc.power_ok) 
    annotation (Line(points = {{-19.5, -175}, {-135, -175}, {-135, 97.5}, {-115, 97.5}}, color = {110, 130, 145}, thickness = 0.08));
  connect(battery.voltage_margin, system_supervisor.voltage_margin) 
    annotation (Line(points = {{-19.5, -193}, {-50, -193}, {-50, -240}, {-510, -240}, {-510, -148.75}, {-498.5, -148.75}}, color = {110, 130, 145}, thickness = 0.08, visible = false));
  connect(esc.motor_command[1], motor1.command) 
    annotation (Line(points = {{-5, 137.5}, {30, 137.5}, {30, 182.25}, {76.5, 182.25}}, color = {0, 0, 127}, thickness = 0.1));
  connect(esc.motor_command[2], motor2.command) 
    annotation (Line(points = {{-5, 137.5}, {40, 137.5}, {40, 107.25}, {76.5, 107.25}}, color = {0, 0, 127}, thickness = 0.1));
  connect(esc.motor_command[3], motor3.command) 
    annotation (Line(points = {{-5, 137.5}, {40, 137.5}, {40, 32.25}, {76.5, 32.25}}, color = {0, 0, 127}, thickness = 0.1));
  connect(esc.motor_command[4], motor4.command) 
    annotation (Line(points = {{-5, 137.5}, {30, 137.5}, {30, -42.75}, {76.5, -42.75}}, color = {0, 0, 127}, thickness = 0.1));
  connect(motor1.rotor_command, airframe.rotor_command[1]) 
    annotation (Line(points = {{153.5, 182.25}, {190, 182.25}, {190, 160}, {250, 160}, {250, 125}, {270, 125}}, color = {0, 0, 127}, thickness = 0.1));
  connect(motor2.rotor_command, airframe.rotor_command[2]) 
    annotation (Line(points = {{153.5, 107.25}, {200, 107.25}, {200, 145}, {250, 145}, {250, 125}, {270, 125}}, color = {0, 0, 127}, thickness = 0.1));
  connect(motor3.rotor_command, airframe.rotor_command[3]) 
    annotation (Line(points = {{153.5, 32.25}, {210, 32.25}, {210, 130}, {250, 130}, {250, 125}, {270, 125}}, color = {0, 0, 127}, thickness = 0.1));
  connect(motor4.rotor_command, airframe.rotor_command[4]) 
    annotation (Line(points = {{153.5, -42.75}, {220, -42.75}, {220, 115}, {250, 115}, {250, 125}, {270, 125}}, color = {0, 0, 127}, thickness = 0.1));
  connect(airframe.rotor_speed[1], motor1.rotor_speed_raw) 
    annotation (Line(points = {{480, 35}, {500, 35}, {500, 245}, {50, 245}, {50, 170}, {76.5, 170}}, color = {110, 130, 145}, thickness = 0.08, visible = false));
  connect(airframe.rotor_speed[2], motor2.rotor_speed_raw) 
    annotation (Line(points = {{480, 35}, {505, 35}, {505, 250}, {55, 250}, {55, 95}, {76.5, 95}}, color = {110, 130, 145}, thickness = 0.08, visible = false));
  connect(airframe.rotor_speed[3], motor3.rotor_speed_raw) 
    annotation (Line(points = {{480, 35}, {510, 35}, {510, 255}, {60, 255}, {60, 20}, {76.5, 20}}, color = {110, 130, 145}, thickness = 0.08, visible = false));
  connect(airframe.rotor_speed[4], motor4.rotor_speed_raw) 
    annotation (Line(points = {{480, 35}, {515, 35}, {515, 260}, {65, 260}, {65, -55}, {76.5, -55}}, color = {110, 130, 145}, thickness = 0.08, visible = false));

  annotation(
    Diagram(
      coordinateSystem(extent = {{-600, -320}, {700, 320}}, grid = {5, 5})),
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Sunray150CompleteSystemGraphical;