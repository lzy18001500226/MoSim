within MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust;
model LqrBaselineGraphicalRunner
  "lqr_baseline graphical Sysblock review runner with the common aircraft template"

  parameter Real gust_force[3](each unit = "N") = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1;
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1};
  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;
  parameter Real nominal_esc_limit_abs(unit = "rad/s", min = 0) = 110;
  parameter Integer scenario_mode(min = 0, max = 4) = 0;
  Modelica.Blocks.Sources.Constant zero(k = 0) 
    annotation(Placement(transformation(origin = {-470, -180}, extent = {{-16, -16}, {16, 16}})));
  Modelica.Blocks.Sources.Constant dt(k = 0.01) 
    annotation(Placement(transformation(origin = {-470, -220}, extent = {{-16, -16}, {16, 16}})));
  Modelica.Blocks.Sources.Constant enable(k = 1) 
    annotation(Placement(transformation(origin = {-470, -260}, extent = {{-16, -16}, {16, 16}})));
  MoSimQuadrotorModel.Guidance.Trajectories.MultiModeTrajectory reference(scenario_mode = scenario_mode) 
    annotation(Placement(transformation(origin = {-380, 185}, extent = {{-50, -65}, {50, 65}})));
  MoSimQuadrotorModel.Control.Adapters.LqrSignalAdapter adapter 
    annotation(Placement(transformation(origin = {-220, 185}, extent = {{-50, -120}, {50, 120}})));
  MoSimQuadrotorModel.Control.ClassicRobust.LqrBaseline.LqrBaselineCore core 
    annotation(Placement(transformation(origin = {-65, 185}, extent = {{-80, -65}, {80, 65}})), __MWORKS(SECInstance = true));
  MoSimQuadrotorModel.Control.Adapters.AttitudeSignalAdapter attitude_adapter 
    annotation(Placement(transformation(origin = {90, 185}, extent = {{-40, -40}, {40, 40}})));
  MoSimQuadrotorModel.Control.InnerLoop.AttitudeTrackingCore inner_loop
    annotation(Placement(transformation(origin = {220, 185}, extent = {{-60, -60}, {60, 60}})));
  MoSimQuadrotorModel.Experiment.Baselines.ScheduledRotorEfficiencyCompensator fault_compensator(
    rotor_effectiveness = rotor_effectiveness, fault_start_s = fault_start_s,
    fault_rotor_index = fault_rotor_index, fault_rotor_effectiveness = fault_rotor_effectiveness) 
    annotation(Placement(transformation(origin = {320, 5}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.ESCDrive esc(motor_limit_abs = nominal_esc_limit_abs) 
    annotation(Placement(transformation(origin = {190, 5}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.BatteryPower battery(voltage_drop_per_second = 0) 
    annotation(Placement(transformation(origin = {55, 5}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor1(channel_index = 1) 
    annotation(Placement(transformation(origin = {465, 220}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor2(channel_index = 2) 
    annotation(Placement(transformation(origin = {465, 142}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor3(channel_index = 3) 
    annotation(Placement(transformation(origin = {465, 64}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor4(channel_index = 4) 
    annotation(Placement(transformation(origin = {465, -14}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(
    rotor_effectiveness = rotor_effectiveness, gust_force = gust_force,
    gust_start_s = gust_start_s, gust_duration_s = gust_duration_s,
    mass_scale = mass_scale, inertia_scale = inertia_scale,
    fault_start_s = fault_start_s, fault_rotor_index = fault_rotor_index,
    fault_rotor_effectiveness = fault_rotor_effectiveness) 
    annotation(Placement(transformation(origin = {650, 100}, extent = {{-127.5, -147.5}, {127.5, 147.5}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.PerceptionInterface perception 
    annotation(Placement(transformation(origin = {-380, 5}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.FlightController flight_controller 
    annotation(Placement(transformation(origin = {-95, 5}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.MissionComputer mission_computer 
    annotation(Placement(transformation(origin = {-235, 5}, extent = {{-50, -50}, {50, 50}})));

  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real esc_motor_command[4];
  Real rotor_speed[4];
  Real esc_health[4];
  Real esc_saturation_ratio;
  Real mission_reference_position[3];
  Real position_error_norm;

equation
  connect(plant.position[1], adapter.position_x) annotation(Line(points={{650,-47.5},{-270,305}}, color={0,0,127}));
  connect(plant.position[2], adapter.position_y) annotation(Line(points={{650,-47.5},{-270,293}}, color={0,0,127}));
  connect(plant.position[3], adapter.position_z) annotation(Line(points={{650,-47.5},{-270,281}}, color={0,0,127}));
  connect(plant.VelMea[1], adapter.velocity_x) annotation(Line(points={{650,-47.5},{-270,269}}, color={0,0,127}));
  connect(plant.VelMea[2], adapter.velocity_y) annotation(Line(points={{650,-47.5},{-270,257}}, color={0,0,127}));
  connect(plant.VelMea[3], adapter.velocity_z) annotation(Line(points={{650,-47.5},{-270,245}}, color={0,0,127}));
  connect(reference.position_command[1], adapter.reference_position_x) annotation(Line(points={{-330,185},{-270,233}}, color={0,0,127}));
  connect(reference.position_command[2], adapter.reference_position_y) annotation(Line(points={{-330,185},{-270,221}}, color={0,0,127}));
  connect(reference.position_command[3], adapter.reference_position_z) annotation(Line(points={{-330,185},{-270,209}}, color={0,0,127}));
  connect(reference.velocity_command[1], adapter.reference_velocity_x) annotation(Line(points={{-330,185},{-270,197}}, color={0,0,127}));
  connect(reference.velocity_command[2], adapter.reference_velocity_y) annotation(Line(points={{-330,185},{-270,185}}, color={0,0,127}));
  connect(reference.velocity_command[3], adapter.reference_velocity_z) annotation(Line(points={{-330,185},{-270,173}}, color={0,0,127}));
  connect(reference.acceleration_command[1], adapter.reference_acceleration_x) annotation(Line(points={{-330,185},{-270,161}}, color={0,0,127}));
  connect(reference.acceleration_command[2], adapter.reference_acceleration_y) annotation(Line(points={{-330,185},{-270,149}}, color={0,0,127}));
  connect(reference.acceleration_command[3], adapter.reference_acceleration_z) annotation(Line(points={{-330,185},{-270,137}}, color={0,0,127}));
  connect(dt.y, adapter.dt) annotation(Line(points={{-454,-220},{-270,125}}, color={0,0,127}));
  connect(enable.y, adapter.enable) annotation(Line(points={{-454,-260},{-270,113}}, color={0,0,127}));
  connect(adapter.position_x_out, core.position_x) annotation(Line(points={{-170,305},{-145,250}}, color={0,0,127}));
  connect(adapter.position_y_out, core.position_y) annotation(Line(points={{-170,293},{-145,240}}, color={0,0,127}));
  connect(adapter.position_z_out, core.position_z) annotation(Line(points={{-170,281},{-145,230}}, color={0,0,127}));
  connect(adapter.velocity_x_out, core.velocity_x) annotation(Line(points={{-170,269},{-145,220}}, color={0,0,127}));
  connect(adapter.velocity_y_out, core.velocity_y) annotation(Line(points={{-170,257},{-145,210}}, color={0,0,127}));
  connect(adapter.velocity_z_out, core.velocity_z) annotation(Line(points={{-170,245},{-145,200}}, color={0,0,127}));
  connect(adapter.reference_position_x_out, core.reference_position_x) annotation(Line(points={{-170,233},{-145,190}}, color={0,0,127}));
  connect(adapter.reference_position_y_out, core.reference_position_y) annotation(Line(points={{-170,221},{-145,180}}, color={0,0,127}));
  connect(adapter.reference_position_z_out, core.reference_position_z) annotation(Line(points={{-170,209},{-145,170}}, color={0,0,127}));
  connect(adapter.reference_velocity_x_out, core.reference_velocity_x) annotation(Line(points={{-170,197},{-145,160}}, color={0,0,127}));
  connect(adapter.reference_velocity_y_out, core.reference_velocity_y) annotation(Line(points={{-170,185},{-145,150}}, color={0,0,127}));
  connect(adapter.reference_velocity_z_out, core.reference_velocity_z) annotation(Line(points={{-170,173},{-145,140}}, color={0,0,127}));
  connect(adapter.reference_acceleration_x_out, core.reference_acceleration_x) annotation(Line(points={{-170,161},{-145,130}}, color={0,0,127}));
  connect(adapter.reference_acceleration_y_out, core.reference_acceleration_y) annotation(Line(points={{-170,149},{-145,120}}, color={0,0,127}));
  connect(adapter.reference_acceleration_z_out, core.reference_acceleration_z) annotation(Line(points={{-170,137},{-145,110}}, color={0,0,127}));
  connect(adapter.dt_out, core.dt) annotation(Line(points={{-170,125},{-145,100}}, color={0,0,127}));
  connect(adapter.enable_out, core.enable) annotation(Line(points={{-170,113},{-145,90}}, color={0,0,127}));
  connect(core.desired_roll_rad_out, attitude_adapter.desired_roll_rad) annotation(Line(points={{15,250},{50,211}}, color={0,0,127}));
  connect(core.desired_pitch_rad_out, attitude_adapter.desired_pitch_rad) annotation(Line(points={{15,240},{50,201}}, color={0,0,127}));
  connect(zero.y, attitude_adapter.desired_yaw_rad) annotation(Line(points={{-454,-180},{30,-180},{30,195},{50,195}}, color={0,0,127}));
  connect(core.collective_thrust_n_out, attitude_adapter.collective_thrust_n) annotation(Line(points={{15,220},{50,189}}, color={0,0,127}));
  connect(plant.attitude[1], attitude_adapter.roll_mea) annotation(Line(points={{650,-47.5},{-20,320},{-20,169},{50,169}}, color={0,0,127}));
  connect(plant.attitude[2], attitude_adapter.pitch_mea) annotation(Line(points={{650,-47.5},{-10,310},{-10,163},{50,163}}, color={0,0,127}));
  connect(plant.attitude[3], attitude_adapter.yaw_mea) annotation(Line(points={{650,-47.5},{0,300},{0,157},{50,157}}, color={0,0,127}));
  connect(plant.BodyRateMea[1], attitude_adapter.roll_rate_mea) annotation(Line(points={{650,-47.5},{10,290},{10,151},{50,151}}, color={0,0,127}));
  connect(plant.BodyRateMea[2], attitude_adapter.pitch_rate_mea) annotation(Line(points={{650,-47.5},{20,280},{20,145},{50,145}}, color={0,0,127}));
  connect(plant.BodyRateMea[3], attitude_adapter.yaw_rate_mea) annotation(Line(points={{650,-47.5},{30,270},{30,139},{50,139}}, color={0,0,127}));
  connect(attitude_adapter.desired_roll_rad_out, inner_loop.desired_roll_rad) annotation(Line(points={{130,211},{160,245}}, color={0,0,127}));
  connect(attitude_adapter.desired_pitch_rad_out, inner_loop.desired_pitch_rad) annotation(Line(points={{130,201},{160,231}}, color={0,0,127}));
  connect(attitude_adapter.desired_yaw_rad_out, inner_loop.desired_yaw_rad) annotation(Line(points={{130,195},{160,217}}, color={0,0,127}));
  connect(attitude_adapter.thrust_baseline_out, inner_loop.thrust_baseline) annotation(Line(points={{130,189},{160,189}}, color={0,0,127}));
  connect(attitude_adapter.roll_mea_out, inner_loop.roll_mea) annotation(Line(points={{130,169},{160,175}}, color={0,0,127}));
  connect(attitude_adapter.pitch_mea_out, inner_loop.pitch_mea) annotation(Line(points={{130,163},{160,161}}, color={0,0,127}));
  connect(attitude_adapter.yaw_mea_out, inner_loop.yaw_mea) annotation(Line(points={{130,157},{160,147}}, color={0,0,127}));
  connect(attitude_adapter.roll_rate_mea_out, inner_loop.roll_rate_mea) annotation(Line(points={{130,151},{160,133}}, color={0,0,127}));
  connect(attitude_adapter.pitch_rate_mea_out, inner_loop.pitch_rate_mea) annotation(Line(points={{130,145},{160,119}}, color={0,0,127}));
  connect(attitude_adapter.yaw_rate_mea_out, inner_loop.yaw_rate_mea) annotation(Line(points={{130,139},{160,105}}, color={0,0,127}));
  connect(inner_loop.amplitude_1, fault_compensator.command_in[1]) annotation(Line(points={{280,221},{270,-30}}, color={0,0,127}));
  connect(inner_loop.amplitude_2, fault_compensator.command_in[2]) annotation(Line(points={{280,197},{270,-40}}, color={0,0,127}));
  connect(inner_loop.amplitude_3, fault_compensator.command_in[3]) annotation(Line(points={{280,173},{270,-50}}, color={0,0,127}));
  connect(inner_loop.amplitude_4, fault_compensator.command_in[4]) annotation(Line(points={{280,149},{270,-60}}, color={0,0,127}));
  connect(fault_compensator.command_out[1], esc.motor_command_raw[1]) annotation(Line(points={{-440,-110},{-120,-92}}, color={0,0,127}));
  connect(fault_compensator.command_out[2], esc.motor_command_raw[2]) annotation(Line(points={{-440,-124},{-120,-106}}, color={0,0,127}));
  connect(fault_compensator.command_out[3], esc.motor_command_raw[3]) annotation(Line(points={{-440,-138},{-120,-120}}, color={0,0,127}));
  connect(fault_compensator.command_out[4], esc.motor_command_raw[4]) annotation(Line(points={{-440,-152},{-120,-134}}, color={0,0,127}));
  connect(esc.motor_command[1], motor1.command) annotation(Line(points={{-440,-166},{-120,-148}}, color={0,0,127}));
  connect(esc.motor_command[2], motor2.command) annotation(Line(points={{-440,-180},{-120,-162}}, color={0,0,127}));
  connect(esc.motor_command[3], motor3.command) annotation(Line(points={{-440,-194},{-120,-176}}, color={0,0,127}));
  connect(esc.motor_command[4], motor4.command) annotation(Line(points={{-440,-208},{-120,-190}}, color={0,0,127}));
  connect(motor1.command_to_plant, plant.rotor_command[1]) annotation(Line(points={{-440,-222},{-120,-204}}, color={0,0,127}));
  connect(motor2.command_to_plant, plant.rotor_command[2]) annotation(Line(points={{-440,-236},{-120,-218}}, color={0,0,127}));
  connect(motor3.command_to_plant, plant.rotor_command[3]) annotation(Line(points={{-440,-250},{-120,-232}}, color={0,0,127}));
  connect(motor4.command_to_plant, plant.rotor_command[4]) annotation(Line(points={{-440,-264},{-120,-246}}, color={0,0,127}));
  connect(plant.rotor_speed[1], motor1.speed) annotation(Line(points={{-440,-278},{-120,-260}}, color={0,0,127}));
  connect(plant.rotor_speed[2], motor2.speed) annotation(Line(points={{-440,-292},{-120,-274}}, color={0,0,127}));
  connect(plant.rotor_speed[3], motor3.speed) annotation(Line(points={{-440,-306},{-120,-288}}, color={0,0,127}));
  connect(plant.rotor_speed[4], motor4.speed) annotation(Line(points={{-440,-320},{-120,-302}}, color={0,0,127}));
  connect(battery.bus_voltage, esc.bus_voltage) annotation(Line(points={{-440,-334},{-120,-316}}, color={0,0,127}));
  connect(battery.power_ok, esc.power_ok) annotation(Line(points={{-440,-348},{-120,-330}}, color={0,0,127}));
  connect(plant.position, perception.position_raw) annotation(Line(points={{-440,-362},{-120,-344}}, color={0,0,127}));
  connect(perception.gps_position, flight_controller.gps_position) annotation(Line(points={{-440,-376},{-120,-358}}, color={0,0,127}));
  connect(perception.gps_valid, flight_controller.gps_valid) annotation(Line(points={{-440,-390},{-120,-372}}, color={0,0,127}));
  connect(plant.attitude, flight_controller.attitude_raw) annotation(Line(points={{-440,-404},{-120,-386}}, color={0,0,127}));
  connect(plant.rotor_speed, flight_controller.motor_speed_raw) annotation(Line(points={{-440,-418},{-120,-400}}, color={0,0,127}));
  connect(perception.local_position, mission_computer.local_position) annotation(Line(points={{-440,-432},{-120,-414}}, color={0,0,127}));
  connect(flight_controller.position_est, mission_computer.aircraft_position) annotation(Line(points={{-440,-446},{-120,-428}}, color={0,0,127}));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin) annotation(Line(points={{-440,-460},{-120,-442}}, color={0,0,127}));
  connect(flight_controller.estimator_quality, mission_computer.estimator_quality) annotation(Line(points={{-440,-474},{-120,-456}}, color={0,0,127}));

  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command[1] = inner_loop.amplitude_1;
  rotor_command[2] = inner_loop.amplitude_2;
  rotor_command[3] = inner_loop.amplitude_3;
  rotor_command[4] = inner_loop.amplitude_4;
  esc_motor_command = esc.motor_command;
  rotor_speed[1] = motor1.speed_telemetry;
  rotor_speed[2] = motor2.speed_telemetry;
  rotor_speed[3] = motor3.speed_telemetry;
  rotor_speed[4] = motor4.speed_telemetry;
  esc_health = esc.esc_health;
  esc_saturation_ratio = esc.saturation_ratio_est;
  mission_reference_position = mission_computer.reference_position;
  position_error_norm = sqrt((position_ref[1] - position[1])^2 + (position_ref[2] - position[2])^2 + (position_ref[3] - position[3])^2);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-520, -400}, {830, 300}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end LqrBaselineGraphicalRunner;