within MoSimQuadrotorModel.Experiment.Runners.Golden;
model OfficialPidSingleUavGoldenRunner
  "Graphical single-UAV Official PID golden closed loop with a concrete direct path"

  parameter Real gust_force[3](each unit = "N") = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1;
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1};
  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;
  parameter Real nominal_esc_limit_abs(unit = "rad/s", min = 0) = 200
    "Transparent nominal ESC boundary above the current Official PID command range";

  // Keep native Sysblocks at this root layer so their real ports carry the
  // visible command path instead of being hidden behind Modelica adapters.
  MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath reference 
    annotation(Placement(transformation(origin={-460,225},
extent={{-50,-30},{50,30}})));
  MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidSysblockCore core 
    annotation(Placement(transformation(origin={-285,185},
extent={{-85,-70},{85,70}})),__MWORKS(SECInstance=true,
PortLabels(labelType="PortName")));
  Modelica.Blocks.Math.Gain rotor_sign_1(k = 1) 
    annotation(Placement(transformation(origin={-158.75,237.5},
extent={{-16,-10},{16,10}})));
  Modelica.Blocks.Math.Gain rotor_sign_2(k = -1) 
    annotation(Placement(transformation(origin={-158.75,202.5},
extent={{-16,-10},{16,10}})));
  Modelica.Blocks.Math.Gain rotor_sign_3(k = 1) 
    annotation(Placement(transformation(origin={-158.75,167.5},
extent={{-16,-10},{16,10}})));
  Modelica.Blocks.Math.Gain rotor_sign_4(k = -1) 
    annotation(Placement(transformation(origin={-158.75,132.5},
extent={{-16,-10},{16,10}})));
  MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidSysblockMapper mapper 
    annotation(Placement(transformation(origin={-35,185},
extent={{-70,-70},{70,70}})),__MWORKS(SECInstance=true,
PortLabels(labelType="PortName")));
  MoSimQuadrotorModel.Control.Adapters.OfficialPidSysblockMapperDiagnostics mapper_diagnostics 
    annotation(Placement(transformation(origin={-15,80},
extent={{-50,-24},{50,24}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.BatteryPower battery(
    voltage_drop_per_second = 0) 
    annotation(Placement(transformation(origin={-15,-8.75},
extent={{-50,-50},{50,50}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.ESCDrive esc(
    motor_limit_abs = nominal_esc_limit_abs) 
    annotation(Placement(transformation(origin={130,205},
extent={{-50,-50},{50,50}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor1(channel_index = 1) 
    annotation(Placement(transformation(origin={280,220},
extent={{-35,-35},{35,35}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor2(channel_index = 2) 
    annotation(Placement(transformation(origin={280,140.25},
extent={{-35,-35},{35,35}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor3(channel_index = 3) 
    annotation(Placement(transformation(origin={280,60.5},
extent={{-35,-35},{35,35}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor4(channel_index = 4) 
    annotation(Placement(transformation(origin={280,-19.25},
extent={{-35,-35},{35,35}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(
    rotor_effectiveness = rotor_effectiveness,
    gust_force = gust_force,
    gust_start_s = gust_start_s,
    gust_duration_s = gust_duration_s,
    mass_scale = mass_scale,
    inertia_scale = inertia_scale,
    fault_start_s = fault_start_s,
    fault_rotor_index = fault_rotor_index,
    fault_rotor_effectiveness = fault_rotor_effectiveness) 
    annotation(Placement(transformation(origin={502.5,99.75},
extent={{-142.5,-154.75},{142.5,154.75}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.PerceptionInterface perception 
    annotation(Placement(transformation(origin={-460,-9.25},
extent={{-50,-50},{50,50}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.FlightController flight_controller 
    annotation(Placement(transformation(origin={-145,-9.25},
extent={{-50,-50},{50,50}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.MissionComputer mission_computer 
    annotation(Placement(transformation(origin={-302.5,-8.75},
extent={{-50,-50},{50,50}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.Supervisor system_supervisor 
    annotation(Placement(transformation(origin={130,113.75},
extent={{-50,-30},{50,30}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.DirectControlTelemetry direct_control_telemetry 
    annotation(Placement(transformation(origin={-460,135.25},
extent={{-50,-30},{50,30}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.TelemetryBusAggregator telemetry_bus(
    vehicle_values = {
      esc.esc_health[1], esc.esc_health[2], esc.esc_health[3], esc.esc_health[4],
      esc.saturation_ratio_est,
      motor1.speed_telemetry, motor2.speed_telemetry, motor3.speed_telemetry,
      motor4.speed_telemetry,
      plant.VelMea[1], plant.VelMea[2], plant.VelMea[3],
      plant.BodyRateMea[1], plant.BodyRateMea[2], plant.BodyRateMea[3],
      plant.QuatMea[1], plant.QuatMea[2], plant.QuatMea[3], plant.QuatMea[4],
      plant.rotor_thrust[1], plant.rotor_thrust[2], plant.rotor_thrust[3], plant.rotor_thrust[4],
      plant.rotor_yaw_reaction_moment[1], plant.rotor_yaw_reaction_moment[2],
      plant.rotor_yaw_reaction_moment[3], plant.rotor_yaw_reaction_moment[4],
      plant.applied_reaction_yaw_moment},
    autonomy_values = {
      perception.health, perception.mid360_valid,
      flight_controller.attitude_est[1], flight_controller.attitude_est[2], flight_controller.attitude_est[3],
      flight_controller.motor_speed_est[1], flight_controller.motor_speed_est[2],
      flight_controller.motor_speed_est[3], flight_controller.motor_speed_est[4],
      flight_controller.health, flight_controller.estimator_mode,
      mission_computer.reference_position[1], mission_computer.reference_position[2],
      mission_computer.reference_position[3], mission_computer.reference_velocity[1],
      mission_computer.reference_velocity[2], mission_computer.reference_velocity[3],
      mission_computer.reference_acceleration[1], mission_computer.reference_acceleration[2],
      mission_computer.reference_acceleration[3], mission_computer.yaw_reference,
      mission_computer.z_reference_rate, mission_computer.health, mission_computer.flight_mode,
      mission_computer.active_setpoint_source, mission_computer.safety_status, mission_computer.event_code,
      mission_computer.obstacle_avoid_active, system_supervisor.degraded_nav_active,
      system_supervisor.obstacle_avoid_active, system_supervisor.estimator_quality,
      system_supervisor.estimator_mode, system_supervisor.flight_mode,
      system_supervisor.active_setpoint_source, system_supervisor.safety_status,
      system_supervisor.event_code, system_supervisor.battery_low_active,
      system_supervisor.offboard_loss_active, system_supervisor.mission_failure_active,
      system_supervisor.geofence_breach_active}) 
    annotation(Placement(transformation(origin={130,-28.75},
extent={{-50,-30},{50,30}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.SystemTelemetry system_telemetry 
    annotation(Placement(transformation(origin={130,42.5},
extent={{-50,-30},{50,30}})));

  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real rotor_speed[4];
  Real esc_health[4];
  Real esc_saturation_ratio;
  Real mission_reference_position[3];
  Real position_error_norm;

equation
  connect(reference.position_command[1], core.x_ref) 
    annotation(Line(origin={0,0},
points={{-410,243},{-385,243},{-385,247.222},{-371.8,247.222}},
color={0,0,127}));
  connect(reference.position_command[2], core.y_ref) 
    annotation(Line(origin={0,0},
points={{-410,243},{-385,243},{-385,231.667},{-371.8,231.667}},
color={0,0,127}));
  connect(reference.position_command[3], core.z_ref) 
    annotation(Line(origin={0,0},
points={{-410,243},{-385,243},{-385,216.111},{-371.8,216.111}},
color={0,0,127}));
  connect(perception.local_position[1], core.x_mea) 
    annotation(Line(origin={0,0},
points={{-405,0.75},{-385,0.75},{-385,200.556},{-371.8,200.556}},
color={0,100,150}));
  connect(perception.local_position[2], core.y_mea) 
    annotation(Line(origin={0,0},
points={{-405,0.75},{-385,0.75},{-385,185},{-371.8,185}},
color={0,100,150}));
  connect(perception.local_position[3], core.z_mea) 
    annotation(Line(origin={0,0},
points={{-405,0.75},{-385,0.75},{-385,169.444},{-371.8,169.444}},
color={0,100,150}));
  connect(plant.attitude[1], core.roll_mea) 
    annotation(Line(origin={0,0},
points={{645,192.6},{670,192.6},{670,-65},{-385,-65},{-385,153.889},{-371.8,153.889}},
color={0,100,150}));
  connect(plant.attitude[2], core.pitch_mea) 
    annotation(Line(origin={0,0},
points={{645,192.6},{670,192.6},{670,-65},{-385,-65},{-385,138.333},{-371.8,138.333}},
color={0,100,150}));
  connect(plant.attitude[3], core.yaw_mea) 
    annotation(Line(origin={0,0},
points={{645,192.6},{670,192.6},{670,-65},{-385,-65},{-385,122.778},{-371.8,122.778}},
color={0,100,150}));
  connect(core.y, rotor_sign_1.u) 
    annotation(Line(origin={0,0},
points={{-198.2,237.5},{-177.95,237.5}},
color={0,0,127}));
  connect(core.y1, rotor_sign_2.u) 
    annotation(Line(origin={0,0},
points={{-188.2,187.5},{-183.15,187.5},{-183.15,202.5},{-177.95,202.5}},
color={0,0,127}));
  connect(core.y2, rotor_sign_3.u) 
    annotation(Line(origin={0,0},
points={{-198.2,167.5},{-177.95,167.5}},
color={0,0,127}));
  connect(core.y3, rotor_sign_4.u) 
    annotation(Line(origin={0,0},
points={{-198.2,132.5},{-177.95,132.5}},
color={0,0,127}));
  connect(rotor_sign_1.y, mapper.amplitude_1) 
    annotation(Line(origin={0,0},
points={{-141.15,237.5},{-106.8,237.5}},
color={0,0,127}));
  connect(rotor_sign_2.y, mapper.amplitude_2) 
    annotation(Line(origin={0,0},
points={{-141.15,202.5},{-106.8,202.5}},
color={0,0,127}));
  connect(rotor_sign_3.y, mapper.amplitude_3) 
    annotation(Line(origin={0,0},
points={{-141.15,167.5},{-106.8,167.5}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(rotor_sign_4.y, mapper.amplitude_4) 
    annotation(Line(origin={0,0},
points={{-141.15,132.5},{-106.8,132.5}},
color={0,0,127}));
  connect(mapper.rotor_command_1, esc.motor_command_raw[1]) 
    annotation(Line(origin={0,0},
points={{36.8,237.5},{55,237.5},{55,227.5},{75,227.5}},
color={0,0,127}));
  connect(mapper.rotor_command_2, esc.motor_command_raw[2]) 
    annotation(Line(origin={0,0},
points={{36.8,202.5},{55,202.5},{55,227.5},{75,227.5}},
color={0,0,127}));
  connect(mapper.rotor_command_3, esc.motor_command_raw[3]) 
    annotation(Line(origin={0,0},
points={{36.8,167.5},{55,167.5},{55,227.5},{75,227.5}},
color={0,0,127}));
  connect(mapper.rotor_command_4, esc.motor_command_raw[4]) 
    annotation(Line(origin={0,0},
points={{36.8,132.5},{55,132.5},{55,227.5},{75,227.5}},
color={0,0,127}));
  connect(rotor_sign_1.y, mapper_diagnostics.amplitude_1) 
    annotation(Line(origin={0,0},
points={{-141.15,237.5},{-130,237.5},{-130,65.6},{-65,65.6}},
color={55,80,115}));
  connect(rotor_sign_2.y, mapper_diagnostics.amplitude_2) 
    annotation(Line(origin={0,0},
points={{-141.15,202.5},{-130,202.5},{-130,75.2},{-65,75.2}},
color={55,80,115}));
  connect(rotor_sign_3.y, mapper_diagnostics.amplitude_3) 
    annotation(Line(origin={0,0},
points={{-141.15,167.5},{-130,167.5},{-130,84.8},{-65,84.8}},
color={55,80,115}));
  connect(rotor_sign_4.y, mapper_diagnostics.amplitude_4) 
    annotation(Line(origin={0,0},
points={{-141.15,132.5},{-130,132.5},{-130,94.4},{-65,94.4}},
color={55,80,115}));
  connect(reference.direct_control_bus, direct_control_telemetry.trajectory_bus) 
    annotation(Line(origin={0,0},
points={{-410,202.5},{-390,202.5},{-390,180},{-525,180},{-525,148.75},{-510,148.75}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(mapper_diagnostics.direct_control_bus, direct_control_telemetry.mapper_bus) 
    annotation(Line(origin={0,0},
points={{35,80},{55,80},{55,-65},{-525,-65},{-525,121.75},{-510,121.75}},
color={55,80,115}),__MWORKS(BlockSystem(NamedSignal)));
  rotor_command = esc.motor_command_raw;

  connect(plant.position, perception.position_raw) 
    annotation(Line(origin={-3.5,8},
points={{648.5,215.55},{673.5,215.55},{673.5,-73},{-521.5,-73},{-521.5,-17.25},{-511.5,-17.25}},
color={0,100,150}));
  connect(battery.bus_voltage, esc.bus_voltage) 
    annotation(Line(origin={0,0},
points={{40,11.25},{55,11.25},{55,205},{75,205}},
color={80,80,80}));
  connect(battery.power_ok, esc.power_ok) 
    annotation(Line(origin={0,0},
points={{40,-8.75},{55,-8.75},{55,182.5},{75,182.5}},
color={80,80,80}));

  connect(esc.motor_command[1], motor1.command) 
    annotation(Line(origin={0,0},
points={{185,222.5},{205,222.5},{205,232.25},{245,232.25}},
color={0,0,127}));
  connect(esc.motor_command[2], motor2.command) 
    annotation(Line(origin={0,0},
points={{185,222.5},{205,222.5},{205,152.5},{245,152.5}},
color={0,0,127}));
  connect(esc.motor_command[3], motor3.command) 
    annotation(Line(origin={0,0},
points={{185,222.5},{205,222.5},{205,72.75},{245,72.75}},
color={0,0,127}));
  connect(esc.motor_command[4], motor4.command) 
    annotation(Line(origin={0,0},
points={{185,222.5},{205,222.5},{205,-7},{245,-7}},
color={0,0,127}));
  connect(motor1.command_to_plant, plant.rotor_command[1]) 
    annotation(Line(origin={0,0},
points={{315,232.25},{341.5,232.25},{341.5,192.5},{360,192.5}},
color={0,0,127}));
  connect(motor2.command_to_plant, plant.rotor_command[2]) 
    annotation(Line(origin={0,0},
points={{315,152.5},{341.5,152.5},{341.5,192.5},{360,192.5}},
color={0,0,127}));
  connect(motor3.command_to_plant, plant.rotor_command[3]) 
    annotation(Line(origin={0,0},
points={{315,72.75},{341.5,72.75},{341.5,192.5},{360,192.5}},
color={0,0,127}));
  connect(motor4.command_to_plant, plant.rotor_command[4]) 
    annotation(Line(origin={0,0},
points={{315,-7},{341.5,-7},{341.5,192.5},{360,192.5}},
color={0,0,127}));

  connect(plant.rotor_speed[1], motor1.speed) 
    annotation(Line(origin={0,0},
points={{670,161.5},{690,161.5},{690,-65},{205,-65},{205,207.75},{245,207.75}},
color={130,0,130}),__MWORKS(BlockSystem(NamedSignal)));
  connect(plant.rotor_speed[2], motor2.speed) 
    annotation(Line(origin={0,0},
points={{645,161.65},{670,161.65},{670,-65},{205,-65},{205,128},{245,128}},
color={130,0,130}));
  connect(plant.rotor_speed[3], motor3.speed) 
    annotation(Line(origin={0,0},
points={{645,161.65},{670,161.65},{670,-65},{205,-65},{205,48.25},{245,48.25}},
color={130,0,130}));
  connect(plant.rotor_speed[4], motor4.speed) 
    annotation(Line(origin={0,0},
points={{645,161.65},{670,161.65},{670,-65},{205,-65},{205,-31.5},{245,-31.5}},
color={130,0,130}),__MWORKS(BlockSystem(NamedSignal)));

  connect(perception.gps_position, flight_controller.gps_position) 
    annotation(Line(origin={0,0},
points={{-405,20.75},{-385,20.75},{-385,-65},{-80,-65},{-80,23.25},{-90,23.25}},
color={0,100,150}));
  connect(plant.attitude, flight_controller.attitude_raw) 
    annotation(Line(origin={0,0},
points={{645,192.6},{670,192.6},{670,-65},{-80,-65},{-80,3.25},{-90,3.25}},
color={0,100,150}));
  connect(plant.rotor_speed, flight_controller.motor_speed_raw) 
    annotation(Line(origin={0,0},
points={{645,161.65},{670,161.65},{670,-65},{-80,-65},{-80,-21.75},{-90,-21.75}},
color={130,0,130}),__MWORKS(BlockSystem(NamedSignal)));
  connect(perception.gps_valid, flight_controller.gps_valid) 
    annotation(Line(origin={0,0},
points={{-405,-46.75},{-385,-46.75},{-385,-65},{-80,-65},{-80,-46.75},{-90,-46.75}},
color={0,100,150}),__MWORKS(BlockSystem(NamedSignal)));

  connect(perception.local_position, mission_computer.local_position) 
    annotation(Line(origin={0,0},
points={{-405,0.75},{-362,0.75},{-362,-1.25},{-357.5,-1.25}},
color={0,100,150}),__MWORKS(BlockSystem(NamedSignal)));
  connect(flight_controller.position_est, mission_computer.aircraft_position) 
    annotation(Line(origin={0,0},
points={{-200,23.25},{-225,23.25},{-225,-65},{-385,-65},{-385,16.25},{-357.5,16.25}},
color={100,70,20}));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin) 
    annotation(Line(origin={0,0},
points={{-405,-19.25},{-357.5,-19.25},{-357.5,-18.75}},
color={0,100,150}));
  connect(flight_controller.estimator_quality, mission_computer.estimator_quality) 
    annotation(Line(origin={0,0},
points={{-200,-41.75},{-225,-41.75},{-225,-65},{-385,-65},{-385,-36.25},{-357.5,-36.25}},
color={100,70,20}));
  connect(battery.voltage_margin, system_supervisor.voltage_margin) 
    annotation(Line(origin={0,0},
points={{40,-28.75},{55,-28.75},{55,136.25},{75,136.25}},
color={80,80,80}));

  connect(telemetry_bus.vehicle_bus, system_telemetry.vehicle_bus) 
    annotation(Line(origin={0,0},
points={{180,-7.55},{205,-7.55},{205,-65},{55,-65},{55,60.5},{80,60.5}},
color={55,80,115}),__MWORKS(BlockSystem(NamedSignal)));
  connect(telemetry_bus.autonomy_bus, system_telemetry.autonomy_bus) 
    annotation(Line(origin={0,0},
points={{180,-33.95},{205,-33.95},{205,-65},{55,-65},{55,24.5},{80,24.5}},
color={55,80,115}));

  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_speed[1] = motor1.speed_telemetry;
  rotor_speed[2] = motor2.speed_telemetry;
  rotor_speed[3] = motor3.speed_telemetry;
  rotor_speed[4] = motor4.speed_telemetry;
  esc_health = esc.esc_health;
  esc_saturation_ratio = esc.saturation_ratio_est;
  mission_reference_position = mission_computer.reference_position;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent={{-600,-340},{800,260}},
grid={5,5})),
    __MWORKS(version = "26.3.0"));
end OfficialPidSingleUavGoldenRunner;