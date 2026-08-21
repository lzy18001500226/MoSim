within MoSimQuadrotorModel.Experiment.OpenBlocks.Px4Ctrl.SingleUav;
model Px4CtrlOpenBlocksRunner
  "Single-UAV Px4Ctrl OpenBlocks obstacle avoidance with dynamic MAT reference"

  parameter Real gust_force[3](each unit = "N") = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1;
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1};
  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;
  parameter Real nominal_esc_limit_abs(unit = "rad/s", min = 0) = 110
    "Sunray150 virtual-plant rotor-speed safety boundary";
  parameter Real controller_sample_period_s(unit = "s") = 0.01
    "Sample period for the 100 Hz px4ctrl discrete controller";

  // ---- Top row: trajectory source (x=-380, y=185) ----
  MoSimQuadrotorModel.Guidance.Trajectories.OpenBlocksDynamicReference reference 
    annotation(Placement(transformation(origin={-380,185},
  extent={{-50,-65},{50,65}})));

  // ---- Input sampler: 18-ch ZOH (x=-200, y=185) ----
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlInputSampler input_sampler 
    annotation(Placement(transformation(origin={-237.5,185},
extent={{-50,-65},{50,65}})));

  // ---- Main control chain (x=-30, y=185) ----
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlBaselineCore controller_core 
    annotation(Placement(transformation(origin={-65,185},
extent={{-80,-65},{80,65}})),
    __MWORKS(SECInstance=true, PortLabels(labelType="PortName")));

  // ---- Output bridge: rotor sign correction (x=120, y=185) ----
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlOutputBridge output_bridge 
    annotation(Placement(transformation(origin={107.5,185},
extent={{-50,-65},{50,65}})));

  MoSimQuadrotorModel.Control.PID.BaselineRotorMapper mapper 
    annotation(Placement(transformation(origin={280,185},
extent={{-80,-65},{80,65}})),
    __MWORKS(SECInstance=true, PortLabels(labelType="PortName")));

  // ---- Bottom row: hardware/sensor chain (y=4, same x as OfficialPidRunner) ----
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

  MoSimQuadrotorModel.Vehicle.BaseModules.BatteryPower battery(
    voltage_drop_per_second = 0) 
    annotation(Placement(transformation(origin={47.5,4.383},
  extent={{-50,-50},{50,50}})));

  MoSimQuadrotorModel.Vehicle.BaseModules.PerceptionInterface perception 
    annotation(Placement(transformation(origin={-380,4.383},
  extent={{-50,-50},{50,50}})));

  MoSimQuadrotorModel.Vehicle.BaseModules.FlightController flight_controller 
    annotation(Placement(transformation(origin={-95,4.383},
  extent={{-50,-50},{50,50}})));

  MoSimQuadrotorModel.Vehicle.BaseModules.MissionComputer mission_computer 
    annotation(Placement(transformation(origin={-237.5,4.383},
  extent={{-50,-50},{50,50}})));

  // ---- Right side: motors and plant ----
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

  // initial position: OpenBlocks starts at trajectory entry point
  parameter Real initial_position_m[3](each unit = "m") = {-41.0, -26.0, 1.5}
    "Ground start position for OpenBlocks scenario";

  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(
    initial_position_m = initial_position_m,
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

  MoSimQuadrotorModel.Environment.Maps.OpenBlocksMapTruthDisplay nav_display 
    annotation(
      Placement(transformation(origin={-380,84.8458},
extent={{-50,-20.1542},{50,20.1542}})),
      __MWORKS(hide=true));

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
  // ── Reference → Input sampler ─────────────────────────────────────────────────
  connect(reference.position_command[1], input_sampler.pos_ref_x) 
    annotation(Line(origin={0,0},
points={{-330,224},{-310,224},{-310,246.389},{-289.3,246.389}},
color={0,0,127}));
  connect(reference.position_command[2], input_sampler.pos_ref_y) 
    annotation(Line(origin={0,0},
points={{-330,224},{-310,224},{-310,239.167},{-289.3,239.167}},
color={0,0,127}));
  connect(reference.position_command[3], input_sampler.pos_ref_z) 
    annotation(Line(origin={0,0},
points={{-330,224},{-310,224},{-310,231.944},{-289.3,231.944}},
color={0,0,127}));
  connect(reference.velocity_command[1], input_sampler.vel_ref_x) 
    annotation(Line(origin={0,0},
points={{-330,185},{-310,185},{-310,224.722},{-289.3,224.722}},
color={0,0,127}));
  connect(reference.velocity_command[2], input_sampler.vel_ref_y) 
    annotation(Line(origin={0,0},
points={{-330,185},{-310,185},{-310,217.5},{-289.3,217.5}},
color={0,0,127}));
  connect(reference.velocity_command[3], input_sampler.vel_ref_z) 
    annotation(Line(origin={0,0},
points={{-330,185},{-310,185},{-310,210.278},{-289.3,210.278}},
color={0,0,127}));
  connect(reference.acceleration_command[1], input_sampler.acc_ref_x) 
    annotation(Line(origin={0,0},
points={{-330,146},{-310,146},{-310,203.056},{-289.3,203.056}},
color={0,0,127}));
  connect(reference.acceleration_command[2], input_sampler.acc_ref_y) 
    annotation(Line(origin={0,0},
points={{-330,146},{-310,146},{-310,195.833},{-289.3,195.833}},
color={0,0,127}));
  connect(reference.acceleration_command[3], input_sampler.acc_ref_z) 
    annotation(Line(origin={0,0},
points={{-330,146},{-310,146},{-310,188.611},{-289.3,188.611}},
color={0,0,127}));

  // ── Plant measurements → Input sampler ────────────────────────────────────────
  connect(plant.position[1], input_sampler.pos_mea_x) 
    annotation(Line(origin={0,0},
points={{755,220.5},{775,220.5},{775,-55},{-310,-55},{-310,181.389},{-289.3,181.389}},
color={0,100,150}));
  connect(plant.position[2], input_sampler.pos_mea_y) 
    annotation(Line(origin={0,0},
points={{755,220.5},{775,220.5},{775,-55},{-310,-55},{-310,174.167},{-289.3,174.167}},
color={0,100,150}));
  connect(plant.position[3], input_sampler.pos_mea_z) 
    annotation(Line(origin={0,0},
points={{755,220.5},{775,220.5},{775,-55},{-310,-55},{-310,166.944},{-289.3,166.944}},
color={0,100,150}));
  connect(plant.VelMea[1], input_sampler.vel_mea_x) 
    annotation(Line(origin={0,0},
points={{755,132},{775,132},{775,-55},{-310,-55},{-310,159.722},{-289.3,159.722}},
color={0,100,150}),__MWORKS(BlockSystem(NamedSignal)));
  connect(plant.VelMea[2], input_sampler.vel_mea_y) 
    annotation(Line(origin={0,0},
points={{755,132},{775,132},{775,-55},{-310,-55},{-310,152.5},{-289.3,152.5}},
color={0,100,150}));
  connect(plant.VelMea[3], input_sampler.vel_mea_z) 
    annotation(Line(origin={0,0},
points={{755,132},{775,132},{775,-55},{-310,-55},{-310,145.278},{-289.3,145.278}},
color={0,100,150}));
  connect(plant.attitude[1], input_sampler.att_roll) 
    annotation(Line(origin={0,0},
points={{755,191},{775,191},{775,-55},{-310,-55},{-310,138.056},{-289.3,138.056}},
color={0,100,150}));
  connect(plant.attitude[2], input_sampler.att_pitch) 
    annotation(Line(origin={0,0},
points={{755,191},{775,191},{775,-55},{-310,-55},{-310,130.833},{-289.3,130.833}},
color={0,100,150}));
  connect(plant.attitude[3], input_sampler.att_yaw) 
    annotation(Line(origin={0,0},
points={{755,191},{775,191},{775,-55},{-310,-55},{-310,123.611},{-289.3,123.611}},
color={0,100,150}));

  // ── Input sampler → Controller core ──────────────────────────────────────────
  connect(input_sampler.s_pos_ref_x, controller_core.x_ref) 
    annotation(Line(origin={0,0},
points={{-182.5,243.5},{-165,243.5},{-165,246.389},{-146.8,246.389}},
color={0,0,127}));
  connect(input_sampler.s_pos_ref_y, controller_core.y_ref) 
    annotation(Line(origin={0,0},
points={{-182.5,235.7},{-165,235.7},{-165,239.167},{-146.8,239.167}},
color={0,0,127}));
  connect(input_sampler.s_pos_ref_z, controller_core.z_ref) 
    annotation(Line(origin={0,0},
points={{-182.5,227.9},{-165,227.9},{-165,231.944},{-146.8,231.944}},
color={0,0,127}));
  connect(input_sampler.s_vel_ref_x, controller_core.vx_ref) 
    annotation(Line(origin={0,0},
points={{-182.5,220.1},{-165,220.1},{-165,224.722},{-146.8,224.722}},
color={0,0,127}));
  connect(input_sampler.s_vel_ref_y, controller_core.vy_ref) 
    annotation(Line(origin={0,0},
points={{-182.5,212.3},{-165,212.3},{-165,217.5},{-146.8,217.5}},
color={0,0,127}));
  connect(input_sampler.s_vel_ref_z, controller_core.vz_ref) 
    annotation(Line(origin={0,0},
points={{-182.5,204.5},{-165,204.5},{-165,210.278},{-146.8,210.278}},
color={0,0,127}));
  connect(input_sampler.s_acc_ref_x, controller_core.ax_ref) 
    annotation(Line(origin={0,0},
points={{-182.5,196.7},{-165,196.7},{-165,203.056},{-146.8,203.056}},
color={0,0,127}));
  connect(input_sampler.s_acc_ref_y, controller_core.ay_ref) 
    annotation(Line(origin={0,0},
points={{-182.5,188.9},{-165,188.9},{-165,195.833},{-146.8,195.833}},
color={0,0,127}));
  connect(input_sampler.s_acc_ref_z, controller_core.az_ref) 
    annotation(Line(origin={0,0},
points={{-182.5,181.1},{-165,181.1},{-165,188.611},{-146.8,188.611}},
color={0,0,127}));
  connect(input_sampler.s_pos_mea_x, controller_core.x_mea) 
    annotation(Line(origin={0,0},
points={{-182.5,173.3},{-165,173.3},{-165,181.389},{-146.8,181.389}},
color={0,100,150}));
  connect(input_sampler.s_pos_mea_y, controller_core.y_mea) 
    annotation(Line(origin={0,0},
points={{-182.5,165.5},{-165,165.5},{-165,174.167},{-146.8,174.167}},
color={0,100,150}));
  connect(input_sampler.s_pos_mea_z, controller_core.z_mea) 
    annotation(Line(origin={0,0},
points={{-182.5,157.7},{-165,157.7},{-165,166.944},{-146.8,166.944}},
color={0,100,150}));
  connect(input_sampler.s_vel_mea_x, controller_core.vx_mea) 
    annotation(Line(origin={0,0},
points={{-182.5,149.9},{-165,149.9},{-165,159.722},{-146.8,159.722}},
color={0,100,150}));
  connect(input_sampler.s_vel_mea_y, controller_core.vy_mea) 
    annotation(Line(origin={0,0},
points={{-182.5,142.1},{-165,142.1},{-165,152.5},{-146.8,152.5}},
color={0,100,150}),__MWORKS(BlockSystem(NamedSignal)));
  connect(input_sampler.s_vel_mea_z, controller_core.vz_mea) 
    annotation(Line(origin={0,0},
points={{-182.5,134.3},{-165,134.3},{-165,145.278},{-146.8,145.278}},
color={0,100,150}));
  connect(input_sampler.s_att_roll, controller_core.roll_mea) 
    annotation(Line(origin={0,0},
points={{-182.5,129.1},{-165,129.1},{-165,138.056},{-146.8,138.056}},
color={0,100,150}));
  connect(input_sampler.s_att_pitch, controller_core.pitch_mea) 
    annotation(Line(origin={0,0},
points={{-182.5,125.2},{-165,125.2},{-165,130.833},{-146.8,130.833}},
color={0,100,150}));
  connect(input_sampler.s_att_yaw, controller_core.yaw_mea) 
    annotation(Line(origin={0,0},
points={{-182.5,121.3},{-165,121.3},{-165,123.611},{-146.8,123.611}},
color={0,100,150}));

  // ── Controller core → Output bridge ──────────────────────────────────────────
  connect(controller_core.y, output_bridge.amp_1) 
    annotation(Line(origin={0,0},
points={{16.8,233.75},{30.9,233.75},{30.9,224},{52.5,224}},
color={55,80,115}));
  connect(controller_core.y1, output_bridge.amp_2) 
    annotation(Line(origin={0,0},
points={{16.8,201.25},{30.9,201.25},{30.9,198},{52.5,198}},
color={55,80,115}));
  connect(controller_core.y2, output_bridge.amp_3) 
    annotation(Line(origin={0,0},
points={{16.8,168.75},{30.9,168.75},{30.9,172},{52.5,172}},
color={55,80,115}));
  connect(controller_core.y3, output_bridge.amp_4) 
    annotation(Line(origin={0,0},
points={{16.8,136.25},{30.9,136.25},{30.9,146},{52.5,146}},
color={55,80,115}));

  // ── Output bridge → Mapper ────────────────────────────────────────────────────
  connect(output_bridge.out_1, mapper.amplitude_1) 
    annotation(Line(origin={0,0},
points={{162.5,224},{180,224},{180,233.75},{198.2,233.75}},
color={55,80,115}));
  connect(output_bridge.out_2, mapper.amplitude_2) 
    annotation(Line(origin={0,0},
points={{162.5,198},{180,198},{180,201.25},{198.2,201.25}},
color={55,80,115}));
  connect(output_bridge.out_3, mapper.amplitude_3) 
    annotation(Line(origin={0,0},
points={{162.5,172},{180,172},{180,168.75},{198.2,168.75}},
color={55,80,115}));
  connect(output_bridge.out_4, mapper.amplitude_4) 
    annotation(Line(origin={0,0},
points={{162.5,146},{180,146},{180,136.25},{198.2,136.25}},
color={55,80,115}));

  // ── Mapper → Fault Compensator (route via x=330, y=-55 bus) ──────────────────
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

  // ── Fault Compensator → ESC ────────────────────────────────────────────────────
  connect(fault_compensator.command_out[1], esc.motor_command_raw[1]) 
    annotation(Line(origin={152.5,-0.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));
  connect(fault_compensator.command_out[2], esc.motor_command_raw[2]) 
    annotation(Line(origin={152.5,-0.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));
  connect(fault_compensator.command_out[3], esc.motor_command_raw[3]) 
    annotation(Line(origin={152.5,-0.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}));
  connect(fault_compensator.command_out[4], esc.motor_command_raw[4]) 
    annotation(Line(origin={152.5,-0.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));

  // ── ESC → Motors ──────────────────────────────────────────────────────────────
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

  // ── Motors → Plant ────────────────────────────────────────────────────────────
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

  // ── Plant rotor speed → Motors (feedback) ─────────────────────────────────────
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

  // ── Plant position → Perception (feedback) ────────────────────────────────────
  connect(plant.position, perception.position_raw) 
    annotation(Line(origin={152.5,-0.867},
points={{602.5,221.367},{622.5,221.367},{622.5,-54.133},{-602.5,-54.133},{-602.5,5.25},{-587.5,5.25}},
color={0,100,150}));

  // ── Battery → ESC ─────────────────────────────────────────────────────────────
  connect(battery.bus_voltage, esc.bus_voltage) 
    annotation(Line(origin={152.5,-0.867},
  points={{-50,25.25},{-37.5,25.25},{-37.5,5.25},{-17.5,5.25}},
  color={80,80,80}));
  connect(battery.power_ok, esc.power_ok) 
    annotation(Line(origin={152.5,-0.867},
  points={{-50,5.25},{-37.5,5.25},{-37.5,-17.25},{-17.5,-17.25}},
  color={80,80,80}));

  // ── Perception → Flight Controller ────────────────────────────────────────────
  connect(perception.gps_position, flight_controller.gps_position) 
    annotation(Line(origin={152.5,-0.867},
  points={{-477.5,35.25},{-462.5,35.25},{-462.5,-54.133},{-172.5,-54.133},{-172.5,37.75},{-192.5,37.75}},
  color={0,100,150}));
  connect(perception.gps_valid, flight_controller.gps_valid) 
    annotation(Line(origin={152.5,-0.867},
  points={{-477.5,-32.25},{-462.5,-32.25},{-462.5,-54.133},{-172.5,-54.133},{-172.5,-32.25},{-192.5,-32.25}},
  color={0,100,150}), __MWORKS(BlockSystem(NamedSignal)));
  connect(plant.attitude, flight_controller.attitude_raw) 
    annotation(Line(origin={152.5,-0.867},
  points={{602.5,191.867},{622.5,191.867},{622.5,-54.133},{-172.5,-54.133},{-172.5,17.75},{-192.5,17.75}},
  color={0,100,150}));
  connect(plant.rotor_speed, flight_controller.motor_speed_raw) 
    annotation(Line(origin={152.5,-0.867},
  points={{602.5,162.367},{622.5,162.367},{622.5,-54.133},{-172.5,-54.133},{-172.5,-7.25},{-192.5,-7.25}},
  color={130,0,130}));

  // ── Perception + FlightController → Mission Computer ──────────────────────────
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

  // ── Reference + Plant → Map Display ───────────────────────────────────────────
  connect(plant.position[1], nav_display.actual_position[1]) 
    annotation(Line(origin={152.5,-0.867},
points={{602.5,221.367},{622.5,221.367},{622.5,-55.25},{-604.5,-55.25},{-604.5,91.759},{-592.5,91.759}},
color={0,100,150}));
  connect(plant.position[2], nav_display.actual_position[2]) 
    annotation(Line(origin={152.5,-0.867},
points={{602.5,221.367},{622.5,221.367},{622.5,-55.25},{-604.5,-55.25},{-604.5,91.759},{-592.5,91.759}},
color={0,100,150}));
  connect(plant.position[3], nav_display.actual_position[3]) 
    annotation(Line(origin={152.5,-0.867},
points={{602.5,221.367},{622.5,221.367},{622.5,-55.25},{-604.5,-55.25},{-604.5,91.759},{-592.5,91.759}},
color={0,100,150}));
  connect(reference.position_command[1], nav_display.reference_position[1]) 
    annotation(Line(origin={0,0},
points={{-330,224},{-310,224},{-310,-55},{-452,-55},{-452,78.7995},{-440,78.7995}},
color={0,0,127}));
  connect(reference.position_command[2], nav_display.reference_position[2]) 
    annotation(Line(origin={0,0},
points={{-330,224},{-310,224},{-310,-55},{-452,-55},{-452,78.7995},{-440,78.7995}},
color={0,0,127}));
  connect(reference.position_command[3], nav_display.reference_position[3]) 
    annotation(Line(origin={0,0},
points={{-330,224},{-310,224},{-310,-55},{-452,-55},{-452,78.7995},{-440,78.7995}},
color={0,0,127}));

  // ── Observable exports ────────────────────────────────────────────────────────
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
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 120,
      Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent={{-650,-400},{830,280}},
  grid={5,5})),
    __MWORKS(version = "26.3.0"));
end Px4CtrlOpenBlocksRunner;