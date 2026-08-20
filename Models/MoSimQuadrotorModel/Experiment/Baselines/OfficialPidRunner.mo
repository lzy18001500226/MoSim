within MoSimQuadrotorModel.Experiment.Baselines;
model OfficialPidRunner
  "Graphical single-UAV Official PID closed loop — all blocks visible, no hidden adapters"

  parameter Real gust_force[3](each unit = "N") = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1.0;
  parameter Real inertia_scale[3](each min = 0.01) = {1.0, 1.0, 1.0};
  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;
  parameter Real nominal_esc_limit_abs(unit = "rad/s", min = 0) = 200
    "Transparent nominal ESC boundary above the current Official PID command range";
  parameter Integer scenario_mode(min = 0, max = 4) = 0
    "Active trajectory: 0 Climb 1 Hover 2 Step 3 Fig8 4 Spiral";

  // ---- Top row: trajectory source ----
  MoSimQuadrotorModel.Guidance.Trajectories.MultiModeTrajectory reference(
    scenario_mode = scenario_mode,
    altitude_m = 2.0,
    takeoff_duration_s = 5.0,
    x_amplitude_m = 2.0,
    y_amplitude_m = 1.0,
    angular_rate_rad_s = 0.35) 
    annotation(Placement(transformation(origin={-380,185},
extent={{-50,-65},{50,65}})));

  // ---- Main control chain (left to right, y=185) ----
  MoSimQuadrotorModel.Control.PID.WorldFramePassthrough preprocessor 
    annotation(Placement(transformation(origin={-237.5,185},
extent={{-50,-65},{50,65}})));

  MoSimQuadrotorModel.Control.PID.OfficialPidGraphicalCore core 
    annotation(Placement(transformation(origin={-65,184.133},
extent={{-80,-65},{80,65}})),
    __MWORKS(SECInstance=true, PortLabels(labelType="PortName")));

  MoSimQuadrotorModel.Control.PID.YawDampedAmplitudeRouter yaw_router 
    annotation(Placement(transformation(origin={107.5,185},
extent={{-50,-65},{50,65}})));

  MoSimQuadrotorModel.Control.PID.BaselineRotorMapper mapper 
    annotation(Placement(transformation(origin={280,185},
extent={{-80,-65},{80,65}})),
    __MWORKS(SECInstance=true, PortLabels(labelType="PortName")));

  MoSimQuadrotorModel.Experiment.Baselines.ScheduledRotorEfficiencyCompensator fault_compensator(
    rotor_effectiveness = rotor_effectiveness,
    fault_start_s = fault_start_s,
    fault_rotor_index = fault_rotor_index,
    fault_rotor_effectiveness = fault_rotor_effectiveness) 
    annotation(Placement(transformation(origin={321.25,4.383},
extent={{-50,-50},{50,50}})));

  MoSimQuadrotorModel.Vehicle.BaseModules.ESCDrive esc(
    motor_limit_abs = nominal_esc_limit_abs) 
    annotation(Placement(transformation(origin={190,4.383},
extent={{-50,-50},{50,50}})));

  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor1(channel_index = 1) 
    annotation(Placement(transformation(origin={431.25,220},
extent={{-28.75,-30},{28.75,30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor2(channel_index = 2) 
    annotation(Placement(transformation(origin={431.25,141.682},
extent={{-28.75,-30},{28.75,30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor3(channel_index = 3) 
    annotation(Placement(transformation(origin={431.25,63.364375},
extent={{-28.75,-30},{28.75,30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor4(channel_index = 4) 
    annotation(Placement(transformation(origin={431.25,-15.617},
extent={{-28.75,-30},{28.75,30}})));

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
    annotation(Placement(transformation(origin={627.5,102.5},
extent={{-127.5,-147.5},{127.5,147.5}})));

  // ---- Bottom row: hardware/sensor chain (y=0) ----
  MoSimQuadrotorModel.Vehicle.BaseModules.PerceptionInterface perception 
    annotation(Placement(transformation(origin={-380,4.383},
extent={{-50,-50},{50,50}})));

  MoSimQuadrotorModel.Vehicle.BaseModules.FlightController flight_controller 
    annotation(Placement(transformation(origin={-95,4.383},
extent={{-50,-50},{50,50}})));

  MoSimQuadrotorModel.Vehicle.BaseModules.MissionComputer mission_computer 
    annotation(Placement(transformation(origin={-237.5,4.383},
extent={{-50,-50},{50,50}})));

  // Battery sits directly below ESC — single short vertical wire
  MoSimQuadrotorModel.Vehicle.BaseModules.BatteryPower battery(
    voltage_drop_per_second = 0) 
    annotation(Placement(transformation(origin={47.5,4.383},
extent={{-50,-50},{50,50}})));

  // ---- Observable variables ----
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
  // ── Reference → WorldFramePassthrough ────────────────────────────────────
  connect(reference.position_command, preprocessor.pos_ref) 
    annotation(Line(origin={152.5,-0.867},
points={{-482.5,224.867},{-462.5,224.867},{-462.5,218.367},{-445,218.367}},
color={0,0,127}));
  connect(perception.local_position, preprocessor.pos_mea) 
    annotation(Line(origin={152.5,-0.867},
points={{-477.5,15.25},{-462.5,15.25},{-462.5,185.867},{-445,185.867}},
color={0,100,150}));
  connect(plant.attitude, preprocessor.attitude) 
    annotation(Line(origin={152.5,-0.867},
points={{602.5,191.867},{622.5,191.867},{622.5,-54.133},{-462.5,-54.133},{-462.5,153.367},{-445,153.367}},
color={0,100,150}));

  // ── WorldFramePassthrough → PID Core ─────────────────────────────────────
  connect(preprocessor.x_ref, core.x_ref) 
    annotation(Line(origin={152.5,-0.867},
points={{-335,237.867},{-317.5,237.867},{-317.5,242.778},{-299.3,242.778}},
color={0,0,127}));
  connect(preprocessor.y_ref, core.y_ref) 
    annotation(Line(origin={152.5,-0.867},
points={{-335,222.267},{-317.5,222.267},{-317.5,228.333},{-299.3,228.333}},
color={0,0,127}));
  connect(preprocessor.z_ref, core.z_ref) 
    annotation(Line(origin={152.5,-0.867},
points={{-335,206.667},{-317.5,206.667},{-317.5,213.889},{-299.3,213.889}},
color={0,0,127}));
  connect(preprocessor.x_mea, core.x_mea) 
    annotation(Line(origin={152.5,-0.867},
points={{-335,191.067},{-317.5,191.067},{-317.5,199.444},{-299.3,199.444}},
color={0,100,150}));
  connect(preprocessor.y_mea, core.y_mea) 
    annotation(Line(origin={152.5,-0.867},
points={{-335,175.467},{-317.5,175.467},{-317.5,185},{-299.3,185}},
color={0,100,150}));
  connect(preprocessor.z_mea, core.z_mea) 
    annotation(Line(origin={152.5,-0.867},
points={{-335,159.867},{-317.5,159.867},{-317.5,170.556},{-299.3,170.556}},
color={0,100,150}));
  connect(preprocessor.roll_mea, core.roll_mea) 
    annotation(Line(origin={152.5,-0.867},
points={{-335,149.467},{-317.5,149.467},{-317.5,156.111},{-299.3,156.111}},
color={0,100,150}));
  connect(preprocessor.pitch_mea, core.pitch_mea) 
    annotation(Line(origin={152.5,-0.867},
points={{-335,141.667},{-299.3,141.667}},
color={0,100,150}));
  connect(preprocessor.yaw_mea, core.yaw_mea) 
    annotation(Line(origin={152.5,-0.867},
points={{-335,133.867},{-317.5,133.867},{-317.5,127.222},{-299.3,127.222}},
color={0,100,150}));
  connect(preprocessor.yaw_mea, yaw_router.yaw_mea) 
    annotation(Line(origin={152.5,-0.867},
points={{-335,133.867},{-317.5,133.867},{-317.5,95.867},{-45,95.867},{-45,114.367}},
color={0,100,150}));

  // ── Core → Yaw Router ────────────────────────────────────────────────────
  connect(core.y, yaw_router.amplitude_in_1) 
    annotation(Line(origin={152.5,-0.867},
points={{-135.7,233.75},{-112,233.75},{-112,224.867},{-100,224.867}},
color={55,80,115}));
  connect(core.y1, yaw_router.amplitude_in_2) 
    annotation(Line(origin={152.5,-0.867},
points={{-135.7,201.25},{-112,201.25},{-112,198.867},{-100,198.867}},
color={55,80,115}));
  connect(core.y2, yaw_router.amplitude_in_3) 
    annotation(Line(origin={152.5,-0.867},
points={{-135.7,168.75},{-112,168.75},{-112,172.867},{-100,172.867}},
color={55,80,115}));
  connect(core.y3, yaw_router.amplitude_in_4) 
    annotation(Line(origin={152.5,-0.867},
points={{-135.7,136.25},{-112,136.25},{-112,146.867},{-100,146.867}},
color={55,80,115}));
  // ── Yaw Router → Mapper ───────────────────────────────────────────────────
  connect(yaw_router.amplitude_out_1, mapper.amplitude_1) 
    annotation(Line(origin={152.5,-0.867},
points={{10,224.867},{41.9,224.867},{41.9,234.617},{45.7,234.617}},
color={55,80,115}));
  connect(yaw_router.amplitude_out_2, mapper.amplitude_2) 
    annotation(Line(origin={152.5,-0.867},
points={{10,198.867},{41.9,198.867},{41.9,202.117},{45.7,202.117}},
color={55,80,115}));
  connect(yaw_router.amplitude_out_3, mapper.amplitude_3) 
    annotation(Line(origin={152.5,-0.867},
points={{10,172.867},{41.9,172.867},{41.9,169.617},{45.7,169.617}},
color={55,80,115}));
  connect(yaw_router.amplitude_out_4, mapper.amplitude_4) 
    annotation(Line(origin={152.5,-0.867},
points={{10,146.867},{41.9,146.867},{41.9,137.117},{45.7,137.117}},
color={55,80,115}));

  // ── Mapper → Fault Compensator (route via x=235) ─────────────────────────
  connect(mapper.rotor_command_1, fault_compensator.command_in[1]) 
    annotation(Line(origin={152.5,-0.867},
points={{209.3,234.617},{232.5,234.617},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
color={55,80,115}));
  connect(mapper.rotor_command_2, fault_compensator.command_in[2]) 
    annotation(Line(origin={152.5,-0.867},
points={{209.3,202.117},{232.5,202.117},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
color={55,80,115}));
  connect(mapper.rotor_command_3, fault_compensator.command_in[3]) 
    annotation(Line(origin={152.5,-0.867},
points={{209.3,169.617},{232.5,169.617},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
color={55,80,115}));
  connect(mapper.rotor_command_4, fault_compensator.command_in[4]) 
    annotation(Line(origin={152.5,-0.867},
points={{209.3,137.117},{232.5,137.117},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
color={55,80,115}));

  // ── Fault Compensator → ESC ───────────────────────────────────────────────
  connect(fault_compensator.command_out[1], esc.motor_command_raw[1]) 
    annotation(Line(origin={152.5,-0.867},
points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
color={55,80,115}),__MWORKS(BlockSystem(NamedSignal)));
  connect(fault_compensator.command_out[2], esc.motor_command_raw[2]) 
    annotation(Line(origin={152.5,-0.867},
points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
color={55,80,115}),__MWORKS(BlockSystem(NamedSignal)));
  connect(fault_compensator.command_out[3], esc.motor_command_raw[3]) 
    annotation(Line(origin={152.5,-0.867},
points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
color={55,80,115}));
  connect(fault_compensator.command_out[4], esc.motor_command_raw[4]) 
    annotation(Line(origin={152.5,-0.867},
points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
color={55,80,115}),__MWORKS(BlockSystem(NamedSignal)));

  // ── ESC → Motors ──────────────────────────────────────────────────────────
  connect(esc.motor_command[1], motor1.command) 
    annotation(Line(origin={152.5,-0.867},
points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,231.367},{250,231.367}},
color={55,80,115}));
  connect(esc.motor_command[2], motor2.command) 
    annotation(Line(origin={152.5,-0.867},
points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,153.049},{250,153.049}},
color={55,80,115}));
  connect(esc.motor_command[3], motor3.command) 
    annotation(Line(origin={152.5,-0.867},
points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,74.731375},{250,74.731375}},
color={55,80,115}));
  connect(esc.motor_command[4], motor4.command) 
    annotation(Line(origin={152.5,-0.867},
points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,-4.25},{250,-4.25}},
color={55,80,115}));

  // ── Motors → Plant ────────────────────────────────────────────────────────
  connect(motor1.command_to_plant, plant.rotor_command[1]) 
    annotation(Line(origin={0,0},
points={{460,230.5},{485,230.5},{485,191},{500,191}},
color={55,80,115}));
  connect(motor2.command_to_plant, plant.rotor_command[2]) 
    annotation(Line(origin={0,0},
points={{460,152.182},{485,152.182},{485,191},{500,191}},
color={55,80,115}));
  connect(motor3.command_to_plant, plant.rotor_command[3]) 
    annotation(Line(origin={0,0},
points={{460,73.864375},{485,73.864375},{485,191},{500,191}},
color={55,80,115}));
  connect(motor4.command_to_plant, plant.rotor_command[4]) 
    annotation(Line(origin={0,0},
points={{460,-5.117},{485,-5.117},{485,191},{500,191}},
color={55,80,115}));

  // ── Plant rotor speed → Motors (feedback, y=-130) ─────────────────────────
  connect(plant.rotor_speed[1], motor1.speed) 
    annotation(Line(origin={0,0},
points={{755,161.5},{775,161.5},{775,-55},{385,-55},{385,209.5},{402.5,209.5}},
color={130,0,130}));
  connect(plant.rotor_speed[2], motor2.speed) 
    annotation(Line(origin={0,0},
points={{755,161.5},{775,161.5},{775,-55},{385,-55},{385,131.182},{402.5,131.182}},
color={130,0,130}));
  connect(plant.rotor_speed[3], motor3.speed) 
    annotation(Line(origin={0,0},
points={{755,161.5},{775,161.5},{775,-55},{385,-55},{385,52.864375},{402.5,52.864375}},
color={130,0,130}));
  connect(plant.rotor_speed[4], motor4.speed) 
    annotation(Line(origin={0,0},
points={{755,161.5},{775,161.5},{775,-55},{385,-55},{385,-26.117},{402.5,-26.117}},
color={130,0,130}));

  // ── Plant position → Perception (feedback) ────────────────────────────────
  connect(plant.position, perception.position_raw) 
    annotation(Line(origin={152.5,-0.867},
points={{602.5,221.367},{622.5,221.367},{622.5,-54.133},{-602.5,-54.133},{-602.5,5.25},{-587.5,5.25}},
color={0,100,150}));

  // ── Battery → ESC ────────────────────────────────────────────────────────
  connect(battery.bus_voltage, esc.bus_voltage) 
    annotation(Line(origin={152.5,-0.867},
points={{-50,25.25},{-37.5,25.25},{-37.5,5.25},{-17.5,5.25}},
color={80,80,80}));
  connect(battery.power_ok, esc.power_ok) 
    annotation(Line(origin={152.5,-0.867},
points={{-50,5.25},{-37.5,5.25},{-37.5,-17.25},{-17.5,-17.25}},
color={80,80,80}));

  // ── Perception → Flight Controller ────────────────────────────────────────
  connect(perception.gps_position, flight_controller.gps_position) 
    annotation(Line(origin={152.5,-0.867},
points={{-477.5,35.25},{-462.5,35.25},{-462.5,-54.133},{-172.5,-54.133},{-172.5,37.75},{-192.5,37.75}},
color={0,100,150}));
  connect(perception.gps_valid, flight_controller.gps_valid) 
    annotation(Line(origin={152.5,-0.867},
points={{-477.5,-32.25},{-462.5,-32.25},{-462.5,-54.133},{-172.5,-54.133},{-172.5,-32.25},{-192.5,-32.25}},
color={0,100,150}),__MWORKS(BlockSystem(NamedSignal)));
  connect(plant.attitude, flight_controller.attitude_raw) 
    annotation(Line(origin={152.5,-0.867},
points={{602.5,191.867},{622.5,191.867},{622.5,-54.133},{-172.5,-54.133},{-172.5,17.75},{-192.5,17.75}},
color={0,100,150}));
  connect(plant.rotor_speed, flight_controller.motor_speed_raw) 
    annotation(Line(origin={152.5,-0.867},
points={{602.5,162.367},{622.5,162.367},{622.5,-54.133},{-172.5,-54.133},{-172.5,-7.25},{-192.5,-7.25}},
color={130,0,130}));

  // ── Perception + FlightController → Mission Computer ──────────────────────
  connect(perception.local_position, mission_computer.local_position) 
    annotation(Line(origin={152.5,-0.867},
points={{-477.5,15.25},{-449.5,15.25},{-449.5,12.75},{-445,12.75}},
color={0,100,150}));
  connect(flight_controller.position_est, mission_computer.aircraft_position) 
    annotation(Line(origin={152.5,-0.867},
points={{-302.5,37.75},{-317.5,37.75},{-317.5,-54.133},{-462.5,-54.133},{-462.5,30.25},{-445,30.25}},
color={100,70,20}));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin) 
    annotation(Line(origin={152.5,-0.867},
points={{-477.5,-4.75},{-445,-4.75}},
color={0,100,150}));
  connect(flight_controller.estimator_quality, mission_computer.estimator_quality) 
    annotation(Line(origin={152.5,-0.867},
points={{-302.5,-27.25},{-317.5,-27.25},{-317.5,-54.133},{-462.5,-54.133},{-462.5,-22.25},{-445,-22.25}},
color={100,70,20}));

  // ---- Observable variable exports ----
  rotor_command            = esc.motor_command_raw;
  esc_motor_command        = esc.motor_command;
  position_ref             = reference.position_command;
  position                 = plant.position;
  attitude                 = plant.attitude;
  rotor_speed[1]           = motor1.speed_telemetry;
  rotor_speed[2]           = motor2.speed_telemetry;
  rotor_speed[3]           = motor3.speed_telemetry;
  rotor_speed[4]           = motor4.speed_telemetry;
  esc_health               = esc.esc_health;
  esc_saturation_ratio     = esc.saturation_ratio_est;
  mission_reference_position = mission_computer.reference_position;
  position_error_norm      = sqrt(
    (position_ref[1] - position[1])^2 +
    (position_ref[2] - position[2])^2 +
    (position_ref[3] - position[3])^2);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent={{-650,-130},{830,280}},
grid={5,5})),
    __MWORKS(version = "26.3.0"));
end OfficialPidRunner;