within MoSimQuadrotorModel.Experiment.Runners.Golden;
model AdapterSingleUavGoldenRunner
  "Graphical single-UAV closed loop with one concrete rotor-command adapter"

  replaceable model Controller =
    MoSimQuadrotorModel.Control.Adapters.OfficialPIDGraphicalRotorAdapter 
    constrainedby MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;
  replaceable model Trajectory =
    MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath 
    constrainedby MoSimQuadrotorModel.Guidance.Trajectories.PartialTrajectory;

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

  Trajectory reference 
    annotation(Placement(transformation(origin = {-500, 145}, extent = {{-32, -22}, {32, 22}})));
  // Sysplorer binds movable top-level wires only for concrete, unconditional
  // connect equations. Keep adapter and direct paths in separate models.
  Controller controller 
    annotation(Placement(
      transformation(origin = {-285, 135}, extent = {{-70, -70}, {70, 70}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.BatteryPower battery(
    voltage_drop_per_second = 0) 
    annotation(Placement(transformation(origin={60,-165},
extent={{-45,-45},{45,45}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.ESCDrive esc(
    motor_limit_abs = nominal_esc_limit_abs) 
    annotation(Placement(transformation(origin = {125, 135}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor1(channel_index = 1) 
    annotation(Placement(transformation(origin = {280, 190}, extent = {{-35, -35}, {35, 35}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor2(channel_index = 2) 
    annotation(Placement(transformation(origin = {280, 115}, extent = {{-35, -35}, {35, 35}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor3(channel_index = 3) 
    annotation(Placement(transformation(origin = {280, 40}, extent = {{-35, -35}, {35, 35}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor4(channel_index = 4) 
    annotation(Placement(transformation(origin = {280, -35}, extent = {{-35, -35}, {35, 35}})));
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
    annotation(Placement(transformation(origin = {505, 80}, extent = {{-100, -100}, {100, 100}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.PerceptionInterface perception 
    annotation(Placement(transformation(origin = {-455, -150}, extent = {{-55, -55}, {55, 55}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.FlightController flight_controller 
    annotation(Placement(transformation(origin = {-260, -150}, extent = {{-60, -60}, {60, 60}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.MissionComputer mission_computer 
    annotation(Placement(transformation(origin = {-80, -150}, extent = {{-60, -60}, {60, 60}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.Supervisor system_supervisor 
    annotation(Placement(transformation(origin={175,-175},
 extent={{-35,-35},{35,35}})));
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
    annotation(Placement(
      transformation(origin = {555, -60}, extent = {{-50, -100}, {50, 100}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.SystemTelemetry system_telemetry 
    annotation(Placement(transformation(origin = {720, -60}, extent = {{-60, -100}, {60, 100}})));
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0) 
    annotation(Placement(
      transformation(origin = {-365, 25}, extent = {{-24, -18}, {24, 18}})));

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
  connect(reference.position_command, controller.position_ref) 
    annotation(Line(points = {{-468, 158.2}, {-420, 158.2}, {-420, 177}, {-362, 177}}, color = {0, 0, 127}));
  connect(reference.velocity_command, controller.velocity_ref) 
    annotation(Line(points = {{-464.8, 145}, {-410, 145}, {-410, 159.5}, {-362, 159.5}}, color = {0, 0, 127}));
  connect(reference.acceleration_command, controller.acceleration_ref) 
    annotation(Line(points = {{-464.8, 131.8}, {-400, 131.8}, {-400, 142}, {-362, 142}}, color = {0, 0, 127}));
  connect(perception.local_position, controller.position_mea) 
    annotation(Line(points = {{-394.5, -139}, {-390, -139}, {-390, 121}, {-362, 121}}, color = {0, 100, 150}));
  connect(perception.local_position, velocity_estimator.u) 
    annotation(Line(points = {{-394.5, -139}, {-389, -139}, {-389, 25}}, color = {0, 100, 150}));
  connect(velocity_estimator.y, controller.velocity_mea) 
    annotation(Line(points = {{-341, 25}, {-335, 25}, {-335, 103.5}, {-362, 103.5}}, color = {0, 100, 150}));
  connect(plant.attitude, controller.attitude_mea) 
    annotation(Line(points = {{405, 15}, {385, 15}, {385, -300}, {-375, -300}, {-375, 86}, {-362, 86}}, color = {0, 100, 150}));
  connect(controller.rotor_command, esc.motor_command_raw) 
    annotation(Line(points = {{-208, 135}, {55, 135}, {55, 157.5}, {70, 157.5}}, color = {0, 0, 127}));
  rotor_command = controller.rotor_command;

  connect(plant.position, perception.position_raw) 
    annotation(Line(points = {{405, 35}, {380, 35}, {380, -270}, {-530, -270}, {-530, -150}, {-510, -150}}, color = {0, 100, 150}));
  connect(battery.bus_voltage, esc.bus_voltage) 
    annotation(Line(points = {{109.5, -147}, {114, -147}, {114, 135}, {70, 135}},
      color = {80, 80, 80}));
  connect(battery.power_ok, esc.power_ok) 
    annotation(Line(points = {{109.5, -165}, {120, -165}, {120, 112.5}, {70, 112.5}},
      color = {80, 80, 80}));

  connect(esc.motor_command[1], motor1.command) 
    annotation(Line(points = {{175, 153}, {205, 153}, {205, 202}, {245, 202}}, color = {0, 0, 127}));
  connect(esc.motor_command[2], motor2.command) 
    annotation(Line(points = {{175, 153}, {215, 153}, {215, 127}, {245, 127}}, color = {0, 0, 127}));
  connect(esc.motor_command[3], motor3.command) 
    annotation(Line(points = {{175, 153}, {215, 153}, {215, 52}, {245, 52}}, color = {0, 0, 127}));
  connect(esc.motor_command[4], motor4.command) 
    annotation(Line(points = {{175, 153}, {205, 153}, {205, -23}, {245, -23}}, color = {0, 0, 127}));
  connect(motor1.command_to_plant, plant.rotor_command[1]) 
    annotation(Line(points = {{315, 202}, {345, 202}, {345, 115}, {405, 115}}, color = {0, 0, 127}));
  connect(motor2.command_to_plant, plant.rotor_command[2]) 
    annotation(Line(points = {{315, 127}, {355, 127}, {355, 105}, {405, 105}}, color = {0, 0, 127}));
  connect(motor3.command_to_plant, plant.rotor_command[3]) 
    annotation(Line(points = {{315, 52}, {365, 52}, {365, 95}, {405, 95}}, color = {0, 0, 127}));
  connect(motor4.command_to_plant, plant.rotor_command[4]) 
    annotation(Line(points = {{315, -23}, {375, -23}, {375, 85}, {405, 85}}, color = {0, 0, 127}));

  connect(plant.rotor_speed[1], motor1.speed) 
    annotation(Line(points = {{405, 55}, {395, 55}, {395, 178}, {245, 178}}, color = {130, 0, 130}));
  connect(plant.rotor_speed[2], motor2.speed) 
    annotation(Line(points = {{405, 45}, {400, 45}, {400, 103}, {245, 103}}, color = {130, 0, 130}));
  connect(plant.rotor_speed[3], motor3.speed) 
    annotation(Line(points = {{405, 35}, {395, 35}, {395, 28}, {245, 28}}, color = {130, 0, 130}));
  connect(plant.rotor_speed[4], motor4.speed) 
    annotation(Line(points = {{405, 25}, {400, 25}, {400, -47}, {245, -47}}, color = {130, 0, 130}));

  connect(perception.gps_position, flight_controller.gps_position) 
    annotation(Line(points = {{-400, -117}, {-400, -75}, {-194, -75}, {-194, -111}}, color = {0, 100, 150}));
  connect(plant.attitude, flight_controller.attitude_raw) 
    annotation(Line(points = {{405, 15}, {390, 15}, {390, -285}, {-185, -285}, {-185, -135}, {-194, -135}}, color = {0, 100, 150}));
  connect(plant.rotor_speed, flight_controller.motor_speed_raw) 
    annotation(Line(points = {{405, 35}, {400, 35}, {400, -315}, {-175, -315}, {-175, -165}, {-194, -165}}, color = {130, 0, 130}));
  connect(perception.gps_valid, flight_controller.gps_valid) 
    annotation(Line(points = {{-400, -191}, {-400, -205}, {-194, -205}, {-194, -195}}, color = {0, 100, 150}));

  connect(perception.local_position, mission_computer.local_position) 
    annotation(Line(points = {{-400, -139}, {-390, -139}, {-390, -220}, {-146, -220}, {-146, -141}}, color = {0, 100, 150}));
  connect(flight_controller.position_est, mission_computer.aircraft_position) 
    annotation(Line(points = {{-326, -111}, {-345, -111}, {-345, -230}, {-146, -230}, {-146, -120}}, color = {100, 70, 20}));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin) 
    annotation(Line(points = {{-400, -161}, {-385, -161}, {-385, -225}, {-146, -225}, {-146, -162}}, color = {0, 100, 150}));
  connect(flight_controller.estimator_quality, mission_computer.estimator_quality) 
    annotation(Line(points = {{-326, -189}, {-350, -189}, {-350, -235}, {-146, -235}, {-146, -183}}, color = {100, 70, 20}));
  connect(battery.voltage_margin, system_supervisor.voltage_margin) 
    annotation(Line(points = {{109.5, -183}, {132.75, -183}, {132.75, -148.75}, {136.5, -148.75}},
      color = {80, 80, 80}));

  connect(telemetry_bus.vehicle_bus, system_telemetry.vehicle_bus) 
    annotation(Line(points = {{605, 0}, {660, 0}}, color = {55, 80, 115}));
  connect(telemetry_bus.autonomy_bus, system_telemetry.autonomy_bus) 
    annotation(Line(points = {{605, -120}, {660, -120}}, color = {55, 80, 115}));

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
    Diagram(
      coordinateSystem(extent = {{-600, -340}, {800, 260}}, grid = {5, 5}),
      graphics = {
        Text(origin = {10, 238}, extent = {{-320, 14}, {320, -14}},
          textString = "Official PID / Sunray150 Golden Closed Loop",
          fontSize = 22, textColor = {45, 45, 45})}),
    __MWORKS(version = "26.3.0"));
end AdapterSingleUavGoldenRunner;