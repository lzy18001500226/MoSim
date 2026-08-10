within MoSimQuadrotorModel.Experiment.Runners.Golden;
model OfficialPidSysblockSingleUavRunner
  "Runnable Golden architecture using the native Official PID Sysblock"

  replaceable model Trajectory = MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath 
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
    "Nominal ESC boundary above the native PID command range";

  Trajectory reference 
    annotation(Placement(transformation(origin = {-330, 115}, extent = {{-28, -18}, {28, 18}})));
  // The native Sysblock adapter must be concrete here: MWORKS fails internally
  // when it is used as the default of a replaceable Modelica class slot.
  MoSimQuadrotorModel.Control.Adapters.OfficialPidSysblockRotorAdapter controller 
    annotation(Placement(transformation(origin = {-135, 105}, extent = {{-68, -70}, {68, 70}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.BatteryPower battery(
    voltage_drop_per_second = 0) 
    annotation(Placement(transformation(origin = {-10, -290}, extent = {{-48, -40}, {48, 40}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.ESCDrive esc(
    motor_limit_abs = nominal_esc_limit_abs) 
    annotation(Placement(transformation(origin = {70, 70}, extent = {{-52, -58}, {52, 58}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor1(channel_index = 1) 
    annotation(Placement(transformation(origin = {205, 150}, extent = {{-45, -35}, {45, 35}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor2(channel_index = 2) 
    annotation(Placement(transformation(origin = {205, 65}, extent = {{-45, -35}, {45, 35}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor3(channel_index = 3) 
    annotation(Placement(transformation(origin = {205, -20}, extent = {{-45, -35}, {45, 35}})));
  MoSimQuadrotorModel.Experiment.Runners.Golden.Modules.RotorCommandChannel motor4(channel_index = 4) 
    annotation(Placement(transformation(origin = {205, -105}, extent = {{-45, -35}, {45, 35}})));
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
    annotation(Placement(transformation(origin = {390, 40}, extent = {{-70, -100}, {70, 100}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.PerceptionInterface perception 
    annotation(Placement(transformation(origin = {-315, -45}, extent = {{-55, -70}, {55, 70}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.FlightController flight_controller 
    annotation(Placement(transformation(origin = {-145, -55}, extent = {{-55, -70}, {55, 70}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.MissionComputer mission_computer 
    annotation(Placement(transformation(origin = {-5, -45}, extent = {{-55, -95}, {55, 95}})));
  MoSimQuadrotorModel.Experiment.Templates.Modules.Supervisor system_supervisor 
    annotation(Placement(transformation(origin = {-150, -260}, extent = {{-55, -70}, {55, 70}})));
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0) 
    annotation(Placement(transformation(origin = {-265, 5}, extent = {{-24, -18}, {24, 18}})));

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
    annotation(Line(points = {{-302, 115}, {-203, 115}}, color = {0, 0, 127}));
  connect(reference.velocity_command, controller.velocity_ref) 
    annotation(Line(points = {{-302, 115}, {-280, 115}, {-280, 155}, {-203, 155}}, color = {0, 0, 127}));
  connect(reference.acceleration_command, controller.acceleration_ref) 
    annotation(Line(points = {{-302, 115}, {-270, 115}, {-270, 175}, {-203, 175}}, color = {0, 0, 127}));

  connect(plant.position, perception.position_raw) 
    annotation(Line(points = {{320, -5}, {300, -5}, {300, -200}, {-370, -200}, {-370, -45}}, color = {0, 100, 150}));
  connect(perception.local_position, controller.position_mea) 
    annotation(Line(points = {{-260, -45}, {-245, -45}, {-245, 75}, {-203, 75}}, color = {0, 100, 150}));
  connect(perception.local_position, velocity_estimator.u) 
    annotation(Line(points = {{-260, -45}, {-280, -45}, {-280, 5}, {-289, 5}}, color = {0, 100, 150}));
  connect(velocity_estimator.y, controller.velocity_mea) 
    annotation(Line(points = {{-241, 5}, {-225, 5}, {-225, 55}, {-203, 55}}, color = {0, 100, 150}));
  connect(plant.attitude, controller.attitude_mea) 
    annotation(Line(points = {{320, -25}, {310, -25}, {310, -215}, {-215, -215}, {-215, 35}, {-203, 35}}, color = {0, 100, 150}));

  connect(controller.rotor_command, esc.motor_command_raw) 
    annotation(Line(points = {{-67, 105}, {18, 105}}, color = {0, 0, 127}));
  connect(battery.bus_voltage, esc.bus_voltage) 
    annotation(Line(points = {{38, -274}, {38, 35}, {18, 35}}, color = {80, 80, 80}));
  connect(battery.power_ok, esc.power_ok) 
    annotation(Line(points = {{38, -290}, {20, -290}, {20, 18}, {18, 18}}, color = {80, 80, 80}));

  connect(esc.motor_command[1], motor1.command) 
    annotation(Line(points = {{122, 95}, {145, 95}, {145, 150}, {160, 150}}, color = {0, 0, 127}));
  connect(esc.motor_command[2], motor2.command) 
    annotation(Line(points = {{122, 75}, {135, 75}, {135, 65}, {160, 65}}, color = {0, 0, 127}));
  connect(esc.motor_command[3], motor3.command) 
    annotation(Line(points = {{122, 55}, {135, 55}, {135, -20}, {160, -20}}, color = {0, 0, 127}));
  connect(esc.motor_command[4], motor4.command) 
    annotation(Line(points = {{122, 35}, {145, 35}, {145, -105}, {160, -105}}, color = {0, 0, 127}));
  connect(motor1.command_to_plant, plant.rotor_command[1]) 
    annotation(Line(points = {{250, 150}, {285, 150}, {285, 75}, {320, 75}}, color = {0, 0, 127}));
  connect(motor2.command_to_plant, plant.rotor_command[2]) 
    annotation(Line(points = {{250, 65}, {295, 65}, {295, 65}, {320, 65}}, color = {0, 0, 127}));
  connect(motor3.command_to_plant, plant.rotor_command[3]) 
    annotation(Line(points = {{250, -20}, {295, -20}, {295, 55}, {320, 55}}, color = {0, 0, 127}));
  connect(motor4.command_to_plant, plant.rotor_command[4]) 
    annotation(Line(points = {{250, -105}, {285, -105}, {285, 45}, {320, 45}}, color = {0, 0, 127}));

  connect(plant.rotor_speed[1], motor1.speed) 
    annotation(Line(points = {{320, 15}, {275, 15}, {275, 135}, {160, 135}}, color = {130, 0, 130}));
  connect(plant.rotor_speed[2], motor2.speed) 
    annotation(Line(points = {{320, 5}, {280, 5}, {280, 50}, {160, 50}}, color = {130, 0, 130}));
  connect(plant.rotor_speed[3], motor3.speed) 
    annotation(Line(points = {{320, -5}, {280, -5}, {280, -35}, {160, -35}}, color = {130, 0, 130}));
  connect(plant.rotor_speed[4], motor4.speed) 
    annotation(Line(points = {{320, -15}, {275, -15}, {275, -120}, {160, -120}}, color = {130, 0, 130}));

  connect(perception.gps_position, flight_controller.gps_position) 
    annotation(Line(points = {{-260, -25}, {-200, -25}}, color = {0, 100, 150}));
  connect(plant.attitude, flight_controller.attitude_raw) 
    annotation(Line(points = {{320, -25}, {315, -25}, {315, -230}, {-230, -230}, {-230, -45}, {-200, -45}}, color = {0, 100, 150}));
  connect(plant.rotor_speed, flight_controller.motor_speed_raw) 
    annotation(Line(points = {{320, -15}, {325, -15}, {325, -245}, {-220, -245}, {-220, -100}, {-200, -100}}, color = {130, 0, 130}));
  connect(perception.gps_valid, flight_controller.gps_valid) 
    annotation(Line(points = {{-260, -125}, {-230, -125}, {-230, -135}, {-200, -135}}, color = {0, 100, 150}));

  connect(perception.local_position, mission_computer.local_position) 
    annotation(Line(points = {{-260, -45}, {-230, -45}, {-230, -185}, {-60, -185}}, color = {0, 100, 150}));
  connect(flight_controller.position_est, mission_computer.aircraft_position) 
    annotation(Line(points = {{-90, -10}, {-70, -10}, {-70, 20}, {-60, 20}}, color = {100, 70, 20}));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin) 
    annotation(Line(points = {{-260, -80}, {-210, -80}, {-210, -125}, {-60, -125}}, color = {0, 100, 150}));
  connect(flight_controller.estimator_quality, mission_computer.estimator_quality) 
    annotation(Line(points = {{-90, -110}, {-70, -110}, {-70, -80}, {-60, -80}}, color = {100, 70, 20}));
  connect(battery.voltage_margin, system_supervisor.voltage_margin) 
    annotation(Line(points = {{38, -306}, {0, -306}, {0, -260}, {-95, -260}}, color = {80, 80, 80}));

  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = controller.rotor_command;
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
    Diagram(coordinateSystem(extent = {{-390, -340}, {480, 210}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end OfficialPidSysblockSingleUavRunner;