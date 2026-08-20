within MoSimQuadrotorModel.Experiment.SlidingMode;
model AdaptiveSmcGraphicalRunner
  "adaptive_smc graphical Sysblock review runner with the common aircraft template"

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
  Modelica.Blocks.Sources.Constant hover_thrust(k = 0.37) 
    annotation(Placement(transformation(origin = {-470, -180}, extent = {{-16, -16}, {16, 16}})));
  Modelica.Blocks.Sources.Constant dt(k = 0.01) 
    annotation(Placement(transformation(origin = {-470, -220}, extent = {{-16, -16}, {16, 16}})));
  Modelica.Blocks.Sources.Constant enable(k = 1) 
    annotation(Placement(transformation(origin = {-470, -260}, extent = {{-16, -16}, {16, 16}})));
  MoSimQuadrotorModel.Guidance.Trajectories.MultiModeTrajectory reference(scenario_mode = scenario_mode) 
    annotation(Placement(transformation(origin = {-380, 185}, extent = {{-50, -65}, {50, 65}})));
  MoSimQuadrotorModel.Control.SlidingMode.AdaptiveSmc.AdaptiveSmcCore core 
    annotation(Placement(transformation(origin = {-65, 185}, extent = {{-80, -65}, {80, 65}})), __MWORKS(SECInstance = true));
  MoSimQuadrotorModel.Experiment.Adapters.GraphicalAccelerationRotorPreview output_adapter 
    annotation(Placement(transformation(origin = {108, 185}, extent = {{-50, -50}, {50, 50}})));
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
  connect(core.desired_acceleration_x, output_adapter.acceleration_x) annotation(Line(points={{15,230},{40,230},{40,222},{58,222}}, color={55,80,115}));
  connect(core.desired_acceleration_y, output_adapter.acceleration_y) annotation(Line(points={{15,202},{40,202},{40,194},{58,194}}, color={55,80,115}));
  connect(core.desired_acceleration_z, output_adapter.acceleration_z) annotation(Line(points={{15,174},{40,174},{40,166},{58,166}}, color={55,80,115}));
  connect(hover_thrust.y, output_adapter.collective_thrust) annotation(Line(points={{-100,188},{0,188},{0,178},{100,178}}, color={0,0,127}));
  connect(output_adapter.rotor_command[1], fault_compensator.command_in[1]) annotation(Line(points={{158,130},{205,130},{205,35},{270,35}}, color={55,80,115}));
  connect(output_adapter.rotor_command[2], fault_compensator.command_in[2]) annotation(Line(points={{158,112},{205,112},{205,25},{270,25}}, color={55,80,115}));
  connect(output_adapter.rotor_command[3], fault_compensator.command_in[3]) annotation(Line(points={{158,94},{205,94},{205,15},{270,15}}, color={55,80,115}));
  connect(output_adapter.rotor_command[4], fault_compensator.command_in[4]) annotation(Line(points={{158,76},{205,76},{205,5},{270,5}}, color={55,80,115}));
  connect(fault_compensator.command_out[1], esc.motor_command_raw[1]) annotation(Line(points={{370,30},{245,30},{245,12},{140,12}}, color={55,80,115}));
  connect(fault_compensator.command_out[2], esc.motor_command_raw[2]) annotation(Line(points={{370,20},{245,20},{245,2},{140,2}}, color={55,80,115}));
  connect(fault_compensator.command_out[3], esc.motor_command_raw[3]) annotation(Line(points={{370,10},{245,10},{245,-8},{140,-8}}, color={55,80,115}));
  connect(fault_compensator.command_out[4], esc.motor_command_raw[4]) annotation(Line(points={{370,0},{245,0},{245,-18},{140,-18}}, color={55,80,115}));
  connect(esc.motor_command[1], motor1.command) annotation(Line(points={{240,30},{300,30},{300,220},{436,220}}, color={55,80,115}));
  connect(esc.motor_command[2], motor2.command) annotation(Line(points={{240,20},{300,20},{300,142},{436,142}}, color={55,80,115}));
  connect(esc.motor_command[3], motor3.command) annotation(Line(points={{240,10},{300,10},{300,64},{436,64}}, color={55,80,115}));
  connect(esc.motor_command[4], motor4.command) annotation(Line(points={{240,0},{300,0},{300,-14},{436,-14}}, color={55,80,115}));
  connect(motor1.command_to_plant, plant.rotor_command[1]) annotation(Line(points={{494,220},{522,220}}, color={55,80,115}));
  connect(motor2.command_to_plant, plant.rotor_command[2]) annotation(Line(points={{494,142},{522,142}}, color={55,80,115}));
  connect(motor3.command_to_plant, plant.rotor_command[3]) annotation(Line(points={{494,64},{522,64}}, color={55,80,115}));
  connect(motor4.command_to_plant, plant.rotor_command[4]) annotation(Line(points={{494,-14},{522,-14}}, color={55,80,115}));
  connect(plant.rotor_speed[1], motor1.speed) annotation(Line(points={{777,220},{805,220},{805,-120},{410,-120},{410,220},{494,220}}, color={130,0,130}));
  connect(plant.rotor_speed[2], motor2.speed) annotation(Line(points={{777,142},{805,142},{805,-120},{410,-120},{410,142},{494,142}}, color={130,0,130}));
  connect(plant.rotor_speed[3], motor3.speed) annotation(Line(points={{777,64},{805,64},{805,-120},{410,-120},{410,64},{494,64}}, color={130,0,130}));
  connect(plant.rotor_speed[4], motor4.speed) annotation(Line(points={{777,-14},{805,-14},{805,-120},{410,-120},{410,-14},{494,-14}}, color={130,0,130}));
  connect(battery.bus_voltage, esc.bus_voltage) annotation(Line(points={{105,30},{140,30}}, color={80,80,80}));
  connect(battery.power_ok, esc.power_ok) annotation(Line(points={{105,20},{140,20}}, color={80,80,80}));
  connect(plant.position, perception.position_raw) annotation(Line(points={{522,150},{700,150},{700,-100},{-400,-100},{-400,30},{-430,30}}, color={0,100,150}));
  connect(perception.gps_position, flight_controller.gps_position) annotation(Line(points={{-330,30},{-145,30}}, color={0,100,150}));
  connect(perception.gps_valid, flight_controller.gps_valid) annotation(Line(points={{-330,-20},{-145,-20}}, color={0,100,150}));
  connect(plant.attitude, flight_controller.attitude_raw) annotation(Line(points={{777,191},{820,191},{820,-80},{-170,-80},{-170,15},{-145,15}}, color={0,100,150}));
  connect(plant.rotor_speed, flight_controller.motor_speed_raw) annotation(Line(points={{777,161},{840,161},{840,-90},{-180,-90},{-180,-5},{-145,-5}}, color={130,0,130}));
  connect(perception.local_position, mission_computer.local_position) annotation(Line(points={{-330,10},{-285,10}}, color={0,100,150}));
  connect(flight_controller.position_est, mission_computer.aircraft_position) annotation(Line(points={{-45,25},{-30,25},{-30,-60},{-300,-60},{-300,25},{-285,25}}, color={100,70,20}));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin) annotation(Line(points={{-330,-5},{-285,-5}}, color={0,100,150}));
  connect(flight_controller.estimator_quality, mission_computer.estimator_quality) annotation(Line(points={{-45,-15},{-30,-15},{-30,-60},{-300,-60},{-300,-15},{-285,-15}}, color={100,70,20}));

  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = output_adapter.rotor_command;
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
end AdaptiveSmcGraphicalRunner;