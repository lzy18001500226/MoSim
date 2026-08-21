within MoSimQuadrotorModel.Experiment.OpenBlocks.Px4Ctrl.Formation;
model ThreeUavHeterogeneousOpenBlocksRunner
  "Three-UAV heterogeneous OpenBlocks obstacle avoidance: independent A* quintic references per UAV,
   pairwise ECBF safety filter, Px4Ctrl baseline control chains"

  // ── Observable outputs ────────────────────────────────────────────────────────
  Modelica.Blocks.Interfaces.RealOutput pos_1[3](each unit = "m")
    "UAV 1 position [x, y, z]" 
    annotation(Placement(transformation(origin={800,220.5}, extent={{-15,-15},{15,15}})));
  Modelica.Blocks.Interfaces.RealOutput att_1[3](each unit = "rad")
    "UAV 1 attitude [roll, pitch, yaw]" 
    annotation(Placement(transformation(origin={800,191}, extent={{-15,-15},{15,15}})));
  Modelica.Blocks.Interfaces.RealOutput pos_2[3](each unit = "m")
    "UAV 2 position [x, y, z]" 
    annotation(Placement(transformation(origin={800,-174.5}, extent={{-15,-15},{15,15}})));
  Modelica.Blocks.Interfaces.RealOutput att_2[3](each unit = "rad")
    "UAV 2 attitude [roll, pitch, yaw]" 
    annotation(Placement(transformation(origin={800,-204}, extent={{-15,-15},{15,15}})));
  Modelica.Blocks.Interfaces.RealOutput pos_3[3](each unit = "m")
    "UAV 3 position [x, y, z]" 
    annotation(Placement(transformation(origin={800,-569.5}, extent={{-15,-15},{15,15}})));
  Modelica.Blocks.Interfaces.RealOutput att_3[3](each unit = "rad")
    "UAV 3 attitude [roll, pitch, yaw]" 
    annotation(Placement(transformation(origin={800,-599}, extent={{-15,-15},{15,15}})));

  // ── Shared parameters ─────────────────────────────────────────────────────────
  parameter Real nominal_esc_limit_abs(unit = "rad/s", min = 0) = 110
    "Sunray150 virtual-plant rotor-speed safety boundary";
  parameter Real gust_force[3](each unit = "N") = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1;
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1};
  parameter Real rotor_effectiveness_1[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real rotor_effectiveness_2[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real rotor_effectiveness_3[4](each min = 0, each max = 1) = {1, 1, 1, 1};

  // ── ECBF safety filter parameters ────────────────────────────────────────────
  parameter Boolean ecbf_enabled = true
    "Set false to bypass ECBF and feed nominal references directly";
  parameter Real pair_minimum_distance_m(unit = "m", min = 0.1) = 1.0;
  parameter Real pair_activation_distance_m(unit = "m") = 1.5;

  // ── Independent OpenBlocks A* trajectory references ──────────────────────────
  MoSimQuadrotorModel.Guidance.Trajectories.OpenBlocksPx4CtrlReference openblocks_ref_1 
    annotation(Placement(transformation(origin={-827.5,-40}, extent={{-92.5,-142.528},{92.5,142.528}})));
  MoSimQuadrotorModel.Guidance.Trajectories.OpenBlocksUav2Reference openblocks_ref_2 
    annotation(Placement(transformation(origin={-827.5,-170}, extent={{-92.5,-142.528},{92.5,142.528}})));
  MoSimQuadrotorModel.Guidance.Trajectories.OpenBlocksUav3Reference openblocks_ref_3 
    annotation(Placement(transformation(origin={-827.5,-300}, extent={{-92.5,-142.528},{92.5,142.528}})));

  // ── Pairwise ECBF safety filter ───────────────────────────────────────────────
  MoSimQuadrotorModel.Guidance.Formation.ThreeUavPairwiseEcbfReferenceSafetyFilter ecbf_filter(
    enabled                    = ecbf_enabled,
    pair_minimum_distance_m    = pair_minimum_distance_m,
    pair_activation_distance_m = pair_activation_distance_m) 
    annotation(Placement(transformation(origin={-595,-105.853},
extent={{-92.5,-142.528},{92.5,142.528}})));

  // ══ UAV 1 control chain ═══════════════════════════════════════════════════════
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlInputSampler input_sampler_1 
    annotation(Placement(transformation(origin = {-237.5, 185}, extent = {{-50, -65}, {50, 65}})));
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlBaselineCore  controller_core_1 
    annotation(Placement(transformation(origin = {-65, 185}, extent = {{-80, -65}, {80, 65}})),
    __MWORKS(SECInstance=true, PortLabels(labelType="PortName")));
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlOutputBridge  output_bridge_1 
    annotation(Placement(transformation(origin = {107.5, 185}, extent = {{-50, -65}, {50, 65}})));
  MoSimQuadrotorModel.Control.PID.BaselineRotorMapper       mapper_1 
    annotation(Placement(transformation(origin = {280, 185}, extent = {{-80, -65}, {80, 65}})),
    __MWORKS(SECInstance=true, PortLabels(labelType="PortName")));
  MoSimQuadrotorModel.Experiment.Baselines.ScheduledRotorEfficiencyCompensator 
    fault_compensator_1(rotor_effectiveness = rotor_effectiveness_1) 
    annotation(Placement(transformation(origin = {321.25, 4.383}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.ESCDrive          esc_1(motor_limit_abs = nominal_esc_limit_abs) 
    annotation(Placement(transformation(origin = {190, 4.383}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.BatteryPower      battery_1(voltage_drop_per_second = 0) 
    annotation(Placement(transformation(origin = {47.5, 4.383}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.PerceptionInterface  perception_1 
    annotation(Placement(transformation(origin = {-380, 4.383}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.FlightController     flight_controller_1 
    annotation(Placement(transformation(origin = {-95, 4.383}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.MissionComputer      mission_computer_1 
    annotation(Placement(transformation(origin = {-237.5, 4.383}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor1_1(channel_index = 1) 
    annotation(Placement(transformation(origin = {431.25, 220}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor1_2(channel_index = 2) 
    annotation(Placement(transformation(origin = {431.25, 141.682}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor1_3(channel_index = 3) 
    annotation(Placement(transformation(origin = {431.25, 63.364}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor1_4(channel_index = 4) 
    annotation(Placement(transformation(origin = {431.25, -15.617}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant_1(
    initial_position_m  = {0, 1.2, 0},
    rotor_effectiveness = rotor_effectiveness_1,
    gust_force          = gust_force,
    gust_start_s        = gust_start_s,
    gust_duration_s     = gust_duration_s,
    mass_scale          = mass_scale,
    inertia_scale       = inertia_scale) 
    annotation(Placement(transformation(origin = {627.5, 102.5}, extent = {{-127.5, -147.5}, {127.5, 147.5}})));

  // ══ UAV 2 control chain ═══════════════════════════════════════════════════════
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlInputSampler input_sampler_2 
    annotation(Placement(transformation(origin = {-237.5, -210}, extent = {{-50, -65}, {50, 65}})));
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlBaselineCore  controller_core_2 
    annotation(Placement(transformation(origin = {-65, -210}, extent = {{-80, -65}, {80, 65}})),
    __MWORKS(SECInstance=true, PortLabels(labelType="PortName")));
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlOutputBridge  output_bridge_2 
    annotation(Placement(transformation(origin = {107.5, -210}, extent = {{-50, -65}, {50, 65}})));
  MoSimQuadrotorModel.Control.PID.BaselineRotorMapper       mapper_2 
    annotation(Placement(transformation(origin = {280, -210}, extent = {{-80, -65}, {80, 65}})),
    __MWORKS(SECInstance=true, PortLabels(labelType="PortName")));
  MoSimQuadrotorModel.Experiment.Baselines.ScheduledRotorEfficiencyCompensator 
    fault_compensator_2(rotor_effectiveness = rotor_effectiveness_2) 
    annotation(Placement(transformation(origin = {321.25, -390.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.ESCDrive          esc_2(motor_limit_abs = nominal_esc_limit_abs) 
    annotation(Placement(transformation(origin = {190, -390.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.BatteryPower      battery_2(voltage_drop_per_second = 0) 
    annotation(Placement(transformation(origin = {47.5, -390.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.PerceptionInterface  perception_2 
    annotation(Placement(transformation(origin = {-380, -390.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.FlightController     flight_controller_2 
    annotation(Placement(transformation(origin = {-95, -390.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.MissionComputer      mission_computer_2 
    annotation(Placement(transformation(origin = {-237.5, -390.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor2_1(channel_index = 1) 
    annotation(Placement(transformation(origin = {431.25, -175}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor2_2(channel_index = 2) 
    annotation(Placement(transformation(origin = {431.25, -253.318}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor2_3(channel_index = 3) 
    annotation(Placement(transformation(origin = {431.25, -331.636}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor2_4(channel_index = 4) 
    annotation(Placement(transformation(origin = {431.25, -410.617}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant_2(
    initial_position_m  = {-1.0392304845, -0.6, 0},
    rotor_effectiveness = rotor_effectiveness_2,
    gust_force          = gust_force,
    gust_start_s        = gust_start_s,
    gust_duration_s     = gust_duration_s,
    mass_scale          = mass_scale,
    inertia_scale       = inertia_scale) 
    annotation(Placement(transformation(origin = {627.5, -292.5}, extent = {{-127.5, -147.5}, {127.5, 147.5}})));

  // ══ UAV 3 control chain ═══════════════════════════════════════════════════════
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlInputSampler input_sampler_3 
    annotation(Placement(transformation(origin = {-237.5, -605}, extent = {{-50, -65}, {50, 65}})));
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlBaselineCore  controller_core_3 
    annotation(Placement(transformation(origin = {-65, -605}, extent = {{-80, -65}, {80, 65}})),
    __MWORKS(SECInstance=true, PortLabels(labelType="PortName")));
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlOutputBridge  output_bridge_3 
    annotation(Placement(transformation(origin = {107.5, -605}, extent = {{-50, -65}, {50, 65}})));
  MoSimQuadrotorModel.Control.PID.BaselineRotorMapper       mapper_3 
    annotation(Placement(transformation(origin = {280, -605}, extent = {{-80, -65}, {80, 65}})),
    __MWORKS(SECInstance=true, PortLabels(labelType="PortName")));
  MoSimQuadrotorModel.Experiment.Baselines.ScheduledRotorEfficiencyCompensator 
    fault_compensator_3(rotor_effectiveness = rotor_effectiveness_3) 
    annotation(Placement(transformation(origin = {321.25, -785.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.ESCDrive          esc_3(motor_limit_abs = nominal_esc_limit_abs) 
    annotation(Placement(transformation(origin = {190, -785.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.BatteryPower      battery_3(voltage_drop_per_second = 0) 
    annotation(Placement(transformation(origin = {47.5, -785.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.PerceptionInterface  perception_3 
    annotation(Placement(transformation(origin = {-380, -785.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.FlightController     flight_controller_3 
    annotation(Placement(transformation(origin = {-95, -785.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.MissionComputer      mission_computer_3 
    annotation(Placement(transformation(origin = {-237.5, -785.617}, extent = {{-50, -50}, {50, 50}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor3_1(channel_index = 1) 
    annotation(Placement(transformation(origin = {431.25, -570}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor3_2(channel_index = 2) 
    annotation(Placement(transformation(origin = {431.25, -648.318}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor3_3(channel_index = 3) 
    annotation(Placement(transformation(origin = {431.25, -726.636}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor3_4(channel_index = 4) 
    annotation(Placement(transformation(origin = {431.25, -805.617}, extent = {{-28.75, -30}, {28.75, 30}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant_3(
    initial_position_m  = {1.0392304845, -0.6, 0},
    rotor_effectiveness = rotor_effectiveness_3,
    gust_force          = gust_force,
    gust_start_s        = gust_start_s,
    gust_duration_s     = gust_duration_s,
    mass_scale          = mass_scale,
    inertia_scale       = inertia_scale) 
    annotation(Placement(transformation(origin = {627.5, -687.5}, extent = {{-127.5, -147.5}, {127.5, 147.5}})));

  // ── Map display: preserve the native OpenBlocks truth/reference view ─────────
  MoSimQuadrotorModel.Environment.Maps.OpenBlocksMapTruthDisplay nav_display 
    annotation(
      Placement(transformation(origin={-380,-125}, extent={{-50,-50},{50,50}})),
      __MWORKS(hide=true));

  // ── Observable variables ──────────────────────────────────────────────────────
  Real position_ref_1[3];
  Real position_ref_2[3];
  Real position_ref_3[3];
  Real position_1[3];
  Real position_2[3];
  Real position_3[3];
  Real attitude_1[3];
  Real attitude_2[3];
  Real attitude_3[3];
  Real position_error_norm_1;
  Real position_error_norm_2;
  Real position_error_norm_3;
  Real minimum_pair_distance_m;
  Real max_position_error_norm;

equation

  // ── Observable assignments ────────────────────────────────────────────────────
  position_ref_1 = openblocks_ref_1.position_command;
  position_ref_2 = openblocks_ref_2.position_command;
  position_ref_3 = openblocks_ref_3.position_command;
  position_1 = plant_1.position;
  position_2 = plant_2.position;
  position_3 = plant_3.position;
  attitude_1 = plant_1.attitude;
  attitude_2 = plant_2.attitude;
  attitude_3 = plant_3.attitude;

  position_error_norm_1 = sqrt((position_1[1] - position_ref_1[1])^2 +
                                (position_1[2] - position_ref_1[2])^2 +
                                (position_1[3] - position_ref_1[3])^2);
  position_error_norm_2 = sqrt((position_2[1] - position_ref_2[1])^2 +
                                (position_2[2] - position_ref_2[2])^2 +
                                (position_2[3] - position_ref_2[3])^2);
  position_error_norm_3 = sqrt((position_3[1] - position_ref_3[1])^2 +
                                (position_3[2] - position_ref_3[2])^2 +
                                (position_3[3] - position_ref_3[3])^2);

  minimum_pair_distance_m = min(min(
    sqrt((position_1[1] - position_2[1])^2 + (position_1[2] - position_2[2])^2 + (position_1[3] - position_2[3])^2),
    sqrt((position_1[1] - position_3[1])^2 + (position_1[2] - position_3[2])^2 + (position_1[3] - position_3[3])^2)),
    sqrt((position_2[1] - position_3[1])^2 + (position_2[2] - position_3[2])^2 + (position_2[3] - position_3[3])^2));

  max_position_error_norm = max(max(position_error_norm_1, position_error_norm_2), position_error_norm_3);

  // ── Plant actual states → ECBF filter (feedback inputs) ──────────────────────
  ecbf_filter.actual_position_1 = plant_1.position;
  ecbf_filter.actual_velocity_1 = plant_1.VelMea;
  ecbf_filter.actual_position_2 = plant_2.position;
  ecbf_filter.actual_velocity_2 = plant_2.VelMea;
  ecbf_filter.actual_position_3 = plant_3.position;
  ecbf_filter.actual_velocity_3 = plant_3.VelMea;

  // ══════════════════════════════════════════════════════════════════════════════
  // ══ UAV 1 CONTROL CHAIN (Y offset = 0) ═══════════════════════════════════════
  // ══════════════════════════════════════════════════════════════════════════════

  // ── ECBF safe reference → Input sampler 1 ─────────────────────────────────────
  connect(ecbf_filter.safe_position_1[1], input_sampler_1.pos_ref_x) 
    annotation(Line(origin={0,0},
points={{-502.5,-6.08333},{-450,-6.08333},{-450,171.875},{-310,171.875},{-310,246.389},{-289.3,246.389}},
color={0,0,127}));
  connect(ecbf_filter.safe_position_1[2], input_sampler_1.pos_ref_y) 
    annotation(Line(origin={0,0},
points={{-502.5,-6.08333},{-450,-6.08333},{-450,171.875},{-310,171.875},{-310,239.167},{-289.3,239.167}},
color={0,0,127}));
  connect(ecbf_filter.safe_position_1[3], input_sampler_1.pos_ref_z) 
    annotation(Line(origin={0,0},
points={{-502.5,-6.08333},{-450,-6.08333},{-450,171.875},{-310,171.875},{-310,231.944},{-289.3,231.944}},
color={0,0,127}));
  connect(ecbf_filter.safe_velocity_1[1], input_sampler_1.vel_ref_x) 
    annotation(Line(origin={0,0},
points={{-502.5,-34.589},{-450,-34.589},{-450,224.722},{-289.3,224.722}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(ecbf_filter.safe_velocity_1[2], input_sampler_1.vel_ref_y) 
    annotation(Line(origin={0,0},
points={{-502.5,-34.5889},{-450,-34.5889},{-450,217.5},{-289.3,217.5}},
color={0,0,127}));
  connect(ecbf_filter.safe_velocity_1[3], input_sampler_1.vel_ref_z) 
    annotation(Line(origin={0,0},
points={{-502.5,-34.5889},{-450,-34.5889},{-450,210.278},{-289.3,210.278}},
color={0,0,127}));
  connect(ecbf_filter.safe_acceleration_1[1], input_sampler_1.acc_ref_x) 
    annotation(Line(origin={0,0},
points={{-502.5,-63.0944},{-450,-63.0944},{-450,203.056},{-289.3,203.056}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(ecbf_filter.safe_acceleration_1[2], input_sampler_1.acc_ref_y) 
    annotation(Line(origin={0,0},
points={{-502.5,-63.0944},{-450,-63.0944},{-450,195.833},{-289.3,195.833}},
color={0,0,127}));
  connect(ecbf_filter.safe_acceleration_1[3], input_sampler_1.acc_ref_z) 
    annotation(Line(origin={0,0},
points={{-502.5,-63.0944},{-450,-63.0944},{-450,188.611},{-289.3,188.611}},
color={0,0,127}));

  // ── Plant measurements → Input sampler 1 ──────────────────────────────────────
  connect(plant_1.position[1], input_sampler_1.pos_mea_x) 
    annotation(Line(origin={0,0},
  points={{755,220.5},{775,220.5},{775,-55},{-310,-55},{-310,181.389},{-289.3,181.389}},
  color={0,100,150}));
  connect(plant_1.position[2], input_sampler_1.pos_mea_y) 
    annotation(Line(origin={0,0},
  points={{755,220.5},{775,220.5},{775,-55},{-310,-55},{-310,174.167},{-289.3,174.167}},
  color={0,100,150}));
  connect(plant_1.position[3], input_sampler_1.pos_mea_z) 
    annotation(Line(origin={0,0},
  points={{755,220.5},{775,220.5},{775,-55},{-310,-55},{-310,166.944},{-289.3,166.944}},
  color={0,100,150}));
  connect(plant_1.VelMea[1], input_sampler_1.vel_mea_x) 
    annotation(Line(origin={0,0},
  points={{755,132},{775,132},{775,-55},{-310,-55},{-310,159.722},{-289.3,159.722}},
  color={0,100,150}),__MWORKS(BlockSystem(NamedSignal)));
  connect(plant_1.VelMea[2], input_sampler_1.vel_mea_y) 
    annotation(Line(origin={0,0},
  points={{755,132},{775,132},{775,-55},{-310,-55},{-310,152.5},{-289.3,152.5}},
  color={0,100,150}));
  connect(plant_1.VelMea[3], input_sampler_1.vel_mea_z) 
    annotation(Line(origin={0,0},
  points={{755,132},{775,132},{775,-55},{-310,-55},{-310,145.278},{-289.3,145.278}},
  color={0,100,150}));
  connect(plant_1.attitude[1], input_sampler_1.att_roll) 
    annotation(Line(origin={0,0},
  points={{755,191},{775,191},{775,-55},{-310,-55},{-310,138.056},{-289.3,138.056}},
  color={0,100,150}));
  connect(plant_1.attitude[2], input_sampler_1.att_pitch) 
    annotation(Line(origin={0,0},
  points={{755,191},{775,191},{775,-55},{-310,-55},{-310,130.833},{-289.3,130.833}},
  color={0,100,150}));
  connect(plant_1.attitude[3], input_sampler_1.att_yaw) 
    annotation(Line(origin={0,0},
  points={{755,191},{775,191},{775,-55},{-310,-55},{-310,123.611},{-289.3,123.611}},
  color={0,100,150}));

  // ── Input sampler → Controller core 1 ─────────────────────────────────────────
  connect(input_sampler_1.s_pos_ref_x, controller_core_1.x_ref) 
    annotation(Line(origin={0,0},points={{-187.5,243.16},{-145,243.16}},color={0,0,127}));
  connect(input_sampler_1.s_pos_ref_y, controller_core_1.y_ref) 
    annotation(Line(origin={0,0},points={{-187.5,236.32},{-145,236.32}},color={0,0,127}));
  connect(input_sampler_1.s_pos_ref_z, controller_core_1.z_ref) 
    annotation(Line(origin={0,0},points={{-187.5,229.47},{-145,229.47}},color={0,0,127}));
  connect(input_sampler_1.s_vel_ref_x, controller_core_1.vx_ref) 
    annotation(Line(origin={0,0},points={{-187.5,222.63},{-145,222.63}},color={0,0,127}));
  connect(input_sampler_1.s_vel_ref_y, controller_core_1.vy_ref) 
    annotation(Line(origin={0,0},points={{-187.5,215.79},{-145,215.79}},color={0,0,127}));
  connect(input_sampler_1.s_vel_ref_z, controller_core_1.vz_ref) 
    annotation(Line(origin={0,0},points={{-187.5,208.95},{-145,208.95}},color={0,0,127}));
  connect(input_sampler_1.s_acc_ref_x, controller_core_1.ax_ref) 
    annotation(Line(origin={0,0},points={{-187.5,202.11},{-145,202.11}},color={0,0,127}));
  connect(input_sampler_1.s_acc_ref_y, controller_core_1.ay_ref) 
    annotation(Line(origin={0,0},points={{-187.5,195.26},{-145,195.26}},color={0,0,127}));
  connect(input_sampler_1.s_acc_ref_z, controller_core_1.az_ref) 
    annotation(Line(origin={0,0},points={{-187.5,188.42},{-145,188.42}},color={0,0,127}));
  connect(input_sampler_1.s_pos_mea_x, controller_core_1.x_mea) 
    annotation(Line(origin={0,0},points={{-187.5,181.58},{-145,181.58}},color={0,100,150}));
  connect(input_sampler_1.s_pos_mea_y, controller_core_1.y_mea) 
    annotation(Line(origin={0,0},points={{-187.5,174.74},{-145,174.74}},color={0,100,150}));
  connect(input_sampler_1.s_pos_mea_z, controller_core_1.z_mea) 
    annotation(Line(origin={0,0},points={{-187.5,167.89},{-145,167.89}},color={0,100,150}));
  connect(input_sampler_1.s_vel_mea_x, controller_core_1.vx_mea) 
    annotation(Line(origin={0,0},points={{-187.5,161.05},{-145,161.05}},color={0,100,150}));
  connect(input_sampler_1.s_vel_mea_y, controller_core_1.vy_mea) 
    annotation(Line(origin={0,0},points={{-187.5,154.21},{-145,154.21}},color={0,100,150}));
  connect(input_sampler_1.s_vel_mea_z, controller_core_1.vz_mea) 
    annotation(Line(origin={0,0},points={{-187.5,147.37},{-145,147.37}},color={0,100,150}));
  connect(input_sampler_1.s_att_roll, controller_core_1.roll_mea) 
    annotation(Line(origin={0,0},points={{-187.5,140.53},{-145,140.53}},color={0,100,150}));
  connect(input_sampler_1.s_att_pitch, controller_core_1.pitch_mea) 
    annotation(Line(origin={0,0},points={{-187.5,133.68},{-145,133.68}},color={0,100,150}));
  connect(input_sampler_1.s_att_yaw, controller_core_1.yaw_mea) 
    annotation(Line(origin={0,0},points={{-187.5,126.84},{-145,126.84}},color={0,100,150}));

  // ── Controller core → Output bridge 1 ─────────────────────────────────────────
  connect(controller_core_1.y,  output_bridge_1.amp_1) 
    annotation(Line(origin={0,0},points={{15,233.75},{57.5,233.75}},color={55,80,115}));
  connect(controller_core_1.y1, output_bridge_1.amp_2) 
    annotation(Line(origin={0,0},points={{15,201.25},{57.5,201.25}},color={55,80,115}));
  connect(controller_core_1.y2, output_bridge_1.amp_3) 
    annotation(Line(origin={0,0},points={{15,168.75},{57.5,168.75}},color={55,80,115}));
  connect(controller_core_1.y3, output_bridge_1.amp_4) 
    annotation(Line(origin={0,0},points={{15,136.25},{57.5,136.25}},color={55,80,115}));

  // ── Output bridge → Mapper 1 ──────────────────────────────────────────────────
  connect(output_bridge_1.out_1, mapper_1.amplitude_1) 
    annotation(Line(origin={0,0},points={{157.5,233.75},{200,233.75}},color={55,80,115}));
  connect(output_bridge_1.out_2, mapper_1.amplitude_2) 
    annotation(Line(origin={0,0},points={{157.5,201.25},{200,201.25}},color={55,80,115}));
  connect(output_bridge_1.out_3, mapper_1.amplitude_3) 
    annotation(Line(origin={0,0},points={{157.5,168.75},{200,168.75}},color={55,80,115}));
  connect(output_bridge_1.out_4, mapper_1.amplitude_4) 
    annotation(Line(origin={0,0},points={{157.5,136.25},{200,136.25}},color={55,80,115}));

  // ── Mapper → Fault Compensator 1 (route via x=330, y=-55 bus) ────────────────
  connect(mapper_1.rotor_command_1, fault_compensator_1.command_in[1]) 
    annotation(Line(origin={152.5,-0.867},
  points={{209.3,234.617},{232.5,234.617},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));
  connect(mapper_1.rotor_command_2, fault_compensator_1.command_in[2]) 
    annotation(Line(origin={152.5,-0.867},
  points={{209.3,202.117},{232.5,202.117},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));
  connect(mapper_1.rotor_command_3, fault_compensator_1.command_in[3]) 
    annotation(Line(origin={152.5,-0.867},
  points={{209.3,169.617},{232.5,169.617},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));
  connect(mapper_1.rotor_command_4, fault_compensator_1.command_in[4]) 
    annotation(Line(origin={152.5,-0.867},
  points={{209.3,137.117},{232.5,137.117},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));

  // ── Fault Compensator → ESC 1 ──────────────────────────────────────────────────
  connect(fault_compensator_1.command_out[1], esc_1.motor_command_raw[1]) 
    annotation(Line(origin={152.5,-0.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));
  connect(fault_compensator_1.command_out[2], esc_1.motor_command_raw[2]) 
    annotation(Line(origin={152.5,-0.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));
  connect(fault_compensator_1.command_out[3], esc_1.motor_command_raw[3]) 
    annotation(Line(origin={152.5,-0.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}));
  connect(fault_compensator_1.command_out[4], esc_1.motor_command_raw[4]) 
    annotation(Line(origin={152.5,-0.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));

  // ── ESC → Motors 1 ────────────────────────────────────────────────────────────
  connect(esc_1.motor_command[1], motor1_1.command) 
    annotation(Line(origin={152.5,-0.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,231.367},{250,231.367}},
  color={55,80,115}));
  connect(esc_1.motor_command[2], motor1_2.command) 
    annotation(Line(origin={152.5,-0.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,153.049},{250,153.049}},
  color={55,80,115}));
  connect(esc_1.motor_command[3], motor1_3.command) 
    annotation(Line(origin={152.5,-0.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,74.731375},{250,74.731375}},
  color={55,80,115}));
  connect(esc_1.motor_command[4], motor1_4.command) 
    annotation(Line(origin={152.5,-0.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,-4.25},{250,-4.25}},
  color={55,80,115}));

  // ── Motors → Plant 1 ──────────────────────────────────────────────────────────
  connect(motor1_1.command_to_plant, plant_1.rotor_command[1]) 
    annotation(Line(origin={0,0},
  points={{460,230.5},{485,230.5},{485,191},{500,191}},
  color={55,80,115}));
  connect(motor1_2.command_to_plant, plant_1.rotor_command[2]) 
    annotation(Line(origin={0,0},
  points={{460,152.182},{485,152.182},{485,191},{500,191}},
  color={55,80,115}));
  connect(motor1_3.command_to_plant, plant_1.rotor_command[3]) 
    annotation(Line(origin={0,0},
  points={{460,73.864375},{485,73.864375},{485,191},{500,191}},
  color={55,80,115}));
  connect(motor1_4.command_to_plant, plant_1.rotor_command[4]) 
    annotation(Line(origin={0,0},
  points={{460,-5.117},{485,-5.117},{485,191},{500,191}},
  color={55,80,115}));

  // ── Plant rotor speed → Motors 1 (feedback) ───────────────────────────────────
  connect(plant_1.rotor_speed[1], motor1_1.speed) 
    annotation(Line(origin={0,0},
  points={{755,161.5},{775,161.5},{775,-55},{385,-55},{385,209.5},{402.5,209.5}},
  color={130,0,130}));
  connect(plant_1.rotor_speed[2], motor1_2.speed) 
    annotation(Line(origin={0,0},
  points={{755,161.5},{775,161.5},{775,-55},{385,-55},{385,131.182},{402.5,131.182}},
  color={130,0,130}));
  connect(plant_1.rotor_speed[3], motor1_3.speed) 
    annotation(Line(origin={0,0},
  points={{755,161.5},{775,161.5},{775,-55},{385,-55},{385,52.864375},{402.5,52.864375}},
  color={130,0,130}));
  connect(plant_1.rotor_speed[4], motor1_4.speed) 
    annotation(Line(origin={0,0},
  points={{755,161.5},{775,161.5},{775,-55},{385,-55},{385,-26.117},{402.5,-26.117}},
  color={130,0,130}));

  // ── Plant position → Perception 1 (feedback) ──────────────────────────────────
  connect(plant_1.position, perception_1.position_raw) 
    annotation(Line(origin={152.5,-0.867},
  points={{602.5,221.367},{622.5,221.367},{622.5,-54.133},{-602.5,-54.133},{-602.5,5.25},{-587.5,5.25}},
  color={0,100,150}));

  // ── Battery → ESC 1 ───────────────────────────────────────────────────────────
  connect(battery_1.bus_voltage, esc_1.bus_voltage) 
    annotation(Line(origin={152.5,-0.867},
  points={{-50,25.25},{-37.5,25.25},{-37.5,5.25},{-17.5,5.25}},
  color={80,80,80}));
  connect(battery_1.power_ok, esc_1.power_ok) 
    annotation(Line(origin={152.5,-0.867},
  points={{-50,5.25},{-37.5,5.25},{-37.5,-17.25},{-17.5,-17.25}},
  color={80,80,80}));

  // ── Perception → Flight Controller 1 ──────────────────────────────────────────
  connect(perception_1.gps_position, flight_controller_1.gps_position) 
    annotation(Line(origin={152.5,-0.867},
  points={{-477.5,35.25},{-462.5,35.25},{-462.5,-54.133},{-172.5,-54.133},{-172.5,37.75},{-192.5,37.75}},
  color={0,100,150}));
  connect(perception_1.gps_valid, flight_controller_1.gps_valid) 
    annotation(Line(origin={152.5,-0.867},
  points={{-477.5,-32.25},{-462.5,-32.25},{-462.5,-54.133},{-172.5,-54.133},{-172.5,-32.25},{-192.5,-32.25}},
  color={0,100,150}), __MWORKS(BlockSystem(NamedSignal)));
  connect(plant_1.attitude, flight_controller_1.attitude_raw) 
    annotation(Line(origin={152.5,-0.867},
  points={{602.5,191.867},{622.5,191.867},{622.5,-54.133},{-172.5,-54.133},{-172.5,17.75},{-192.5,17.75}},
  color={0,100,150}));
  connect(plant_1.rotor_speed, flight_controller_1.motor_speed_raw) 
    annotation(Line(origin={152.5,-0.867},
  points={{602.5,162.367},{622.5,162.367},{622.5,-54.133},{-172.5,-54.133},{-172.5,-7.25},{-192.5,-7.25}},
  color={130,0,130}));

  // ── Perception + FlightController → Mission Computer 1 ────────────────────────
  connect(perception_1.local_position, mission_computer_1.local_position) 
    annotation(Line(origin={152.5,-0.867},
  points={{-477.5,15.25},{-449.5,15.25},{-449.5,12.75},{-445,12.75}},
  color={0,100,150}));
  connect(flight_controller_1.position_est, mission_computer_1.aircraft_position) 
    annotation(Line(origin={152.5,-0.867},
  points={{-302.5,37.75},{-317.5,37.75},{-317.5,-54.133},{-462.5,-54.133},{-462.5,30.25},{-445,30.25}},
  color={100,70,20}));
  connect(perception_1.obstacle_margin, mission_computer_1.obstacle_margin) 
    annotation(Line(origin={152.5,-0.867},
  points={{-477.5,-4.75},{-445,-4.75}},
  color={0,100,150}));
  connect(flight_controller_1.estimator_quality, mission_computer_1.estimator_quality) 
    annotation(Line(origin={152.5,-0.867},
  points={{-302.5,-27.25},{-317.5,-27.25},{-317.5,-54.133},{-462.5,-54.133},{-462.5,-22.25},{-445,-22.25}},
  color={100,70,20}));

  // <<UAV_1_CHAIN_END>>


  // ══════════════════════════════════════════════════════════════════════════════
  // ══ UAV 2 CONTROL CHAIN (Y offset = -395) ════════════════════════════════════
  // ══════════════════════════════════════════════════════════════════════════════

  // ── ECBF safe reference → Input sampler 2 ─────────────────────────────────────
  connect(ecbf_filter.safe_position_2[1], input_sampler_2.pos_ref_x) 
    annotation(Line(origin={0,0},
points={{-502.5,-91.6},{-450,-91.6},{-450,-148.611},{-289.3,-148.611}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(ecbf_filter.safe_position_2[2], input_sampler_2.pos_ref_y) 
    annotation(Line(origin={0,0},
points={{-502.5,-91.6},{-450,-91.6},{-450,-155.833},{-289.3,-155.833}},
color={0,0,127}));
  connect(ecbf_filter.safe_position_2[3], input_sampler_2.pos_ref_z) 
    annotation(Line(origin={0,0},
points={{-502.5,-91.6},{-450,-91.6},{-450,-163.056},{-289.3,-163.056}},
color={0,0,127}));
  connect(ecbf_filter.safe_velocity_2[1], input_sampler_2.vel_ref_x) 
    annotation(Line(origin={0,0},
points={{-502.5,-120.106},{-450,-120.106},{-450,-170.278},{-289.3,-170.278}},
color={0,0,127}));
  connect(ecbf_filter.safe_velocity_2[2], input_sampler_2.vel_ref_y) 
    annotation(Line(origin={0,0},
points={{-502.5,-120.106},{-450,-120.106},{-450,-177.5},{-289.3,-177.5}},
color={0,0,127}));
  connect(ecbf_filter.safe_velocity_2[3], input_sampler_2.vel_ref_z) 
    annotation(Line(origin={0,0},
points={{-502.5,-120.106},{-450,-120.106},{-450,-184.722},{-289.3,-184.722}},
color={0,0,127}));
  connect(ecbf_filter.safe_acceleration_2[1], input_sampler_2.acc_ref_x) 
    annotation(Line(origin={0,0},
points={{-502.5,-148.611},{-450,-148.611},{-450,-191.944},{-289.3,-191.944}},
color={0,0,127}));
  connect(ecbf_filter.safe_acceleration_2[2], input_sampler_2.acc_ref_y) 
    annotation(Line(origin={0,0},
points={{-502.5,-148.611},{-450,-148.611},{-450,-199.167},{-289.3,-199.167}},
color={0,0,127}));
  connect(ecbf_filter.safe_acceleration_2[3], input_sampler_2.acc_ref_z) 
    annotation(Line(origin={0,0},
points={{-502.5,-148.6114},{-450,-148.6114},{-450,-206.389},{-289.3,-206.389}},
color={0,0,127}));

  // ── Plant measurements → Input sampler 2 ──────────────────────────────────────
  connect(plant_2.position[1], input_sampler_2.pos_mea_x) 
    annotation(Line(origin={0,0},
  points={{755,-174.5},{775,-174.5},{775,-450},{-310,-450},{-310,-213.611},{-289.3,-213.611}},
  color={0,100,150}));
  connect(plant_2.position[2], input_sampler_2.pos_mea_y) 
    annotation(Line(origin={0,0},
  points={{755,-174.5},{775,-174.5},{775,-450},{-310,-450},{-310,-220.833},{-289.3,-220.833}},
  color={0,100,150}));
  connect(plant_2.position[3], input_sampler_2.pos_mea_z) 
    annotation(Line(origin={0,0},
  points={{755,-174.5},{775,-174.5},{775,-450},{-310,-450},{-310,-228.056},{-289.3,-228.056}},
  color={0,100,150}));
  connect(plant_2.VelMea[1], input_sampler_2.vel_mea_x) 
    annotation(Line(origin={0,0},
  points={{755,-263},{775,-263},{775,-450},{-310,-450},{-310,-235.278},{-289.3,-235.278}},
  color={0,100,150}),__MWORKS(BlockSystem(NamedSignal)));
  connect(plant_2.VelMea[2], input_sampler_2.vel_mea_y) 
    annotation(Line(origin={0,0},
  points={{755,-263},{775,-263},{775,-450},{-310,-450},{-310,-242.5},{-289.3,-242.5}},
  color={0,100,150}));
  connect(plant_2.VelMea[3], input_sampler_2.vel_mea_z) 
    annotation(Line(origin={0,0},
  points={{755,-263},{775,-263},{775,-450},{-310,-450},{-310,-249.722},{-289.3,-249.722}},
  color={0,100,150}));
  connect(plant_2.attitude[1], input_sampler_2.att_roll) 
    annotation(Line(origin={0,0},
  points={{755,-204},{775,-204},{775,-450},{-310,-450},{-310,-256.944},{-289.3,-256.944}},
  color={0,100,150}));
  connect(plant_2.attitude[2], input_sampler_2.att_pitch) 
    annotation(Line(origin={0,0},
  points={{755,-204},{775,-204},{775,-450},{-310,-450},{-310,-264.167},{-289.3,-264.167}},
  color={0,100,150}));
  connect(plant_2.attitude[3], input_sampler_2.att_yaw) 
    annotation(Line(origin={0,0},
points={{755,-204},{775,-204},{775,-450},{-310,-450},{-310,-271.389},{-289.3,-271.389}},
color={0,100,150}));

  // ── Input sampler → Controller core 2 ─────────────────────────────────────────
  connect(input_sampler_2.s_pos_ref_x, controller_core_2.x_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-151.84},{-145,-151.84}},color={0,0,127}));
  connect(input_sampler_2.s_pos_ref_y, controller_core_2.y_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-158.68},{-145,-158.68}},color={0,0,127}));
  connect(input_sampler_2.s_pos_ref_z, controller_core_2.z_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-165.53},{-145,-165.53}},color={0,0,127}));
  connect(input_sampler_2.s_vel_ref_x, controller_core_2.vx_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-172.37},{-145,-172.37}},color={0,0,127}));
  connect(input_sampler_2.s_vel_ref_y, controller_core_2.vy_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-179.21},{-145,-179.21}},color={0,0,127}));
  connect(input_sampler_2.s_vel_ref_z, controller_core_2.vz_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-186.05},{-145,-186.05}},color={0,0,127}));
  connect(input_sampler_2.s_acc_ref_x, controller_core_2.ax_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-192.89},{-145,-192.89}},color={0,0,127}));
  connect(input_sampler_2.s_acc_ref_y, controller_core_2.ay_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-199.74},{-145,-199.74}},color={0,0,127}));
  connect(input_sampler_2.s_acc_ref_z, controller_core_2.az_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-206.58},{-145,-206.58}},color={0,0,127}));
  connect(input_sampler_2.s_pos_mea_x, controller_core_2.x_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-213.42},{-145,-213.42}},color={0,100,150}));
  connect(input_sampler_2.s_pos_mea_y, controller_core_2.y_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-220.26},{-145,-220.26}},color={0,100,150}));
  connect(input_sampler_2.s_pos_mea_z, controller_core_2.z_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-227.11},{-145,-227.11}},color={0,100,150}));
  connect(input_sampler_2.s_vel_mea_x, controller_core_2.vx_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-233.95},{-145,-233.95}},color={0,100,150}));
  connect(input_sampler_2.s_vel_mea_y, controller_core_2.vy_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-240.79},{-145,-240.79}},color={0,100,150}));
  connect(input_sampler_2.s_vel_mea_z, controller_core_2.vz_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-247.63},{-145,-247.63}},color={0,100,150}));
  connect(input_sampler_2.s_att_roll, controller_core_2.roll_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-254.47},{-145,-254.47}},color={0,100,150}));
  connect(input_sampler_2.s_att_pitch, controller_core_2.pitch_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-261.32},{-145,-261.32}},color={0,100,150}));
  connect(input_sampler_2.s_att_yaw, controller_core_2.yaw_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-268.16},{-145,-268.16}},color={0,100,150}));

  // ── Controller core → Output bridge 2 ─────────────────────────────────────────
  connect(controller_core_2.y,  output_bridge_2.amp_1) 
    annotation(Line(origin={0,0},points={{15,-161.25},{57.5,-161.25}},color={55,80,115}));
  connect(controller_core_2.y1, output_bridge_2.amp_2) 
    annotation(Line(origin={0,0},points={{15,-193.75},{57.5,-193.75}},color={55,80,115}));
  connect(controller_core_2.y2, output_bridge_2.amp_3) 
    annotation(Line(origin={0,0},points={{15,-226.25},{57.5,-226.25}},color={55,80,115}));
  connect(controller_core_2.y3, output_bridge_2.amp_4) 
    annotation(Line(origin={0,0},points={{15,-258.75},{57.5,-258.75}},color={55,80,115}));

  // ── Output bridge → Mapper 2 ──────────────────────────────────────────────────
  connect(output_bridge_2.out_1, mapper_2.amplitude_1) 
    annotation(Line(origin={0,0},points={{157.5,-161.25},{200,-161.25}},color={55,80,115}));
  connect(output_bridge_2.out_2, mapper_2.amplitude_2) 
    annotation(Line(origin={0,0},points={{157.5,-193.75},{200,-193.75}},color={55,80,115}));
  connect(output_bridge_2.out_3, mapper_2.amplitude_3) 
    annotation(Line(origin={0,0},points={{157.5,-226.25},{200,-226.25}},color={55,80,115}));
  connect(output_bridge_2.out_4, mapper_2.amplitude_4) 
    annotation(Line(origin={0,0},points={{157.5,-258.75},{200,-258.75}},color={55,80,115}));

  // ── Mapper → Fault Compensator 2 (route via x=330, y=-450 bus) ───────────────
  connect(mapper_2.rotor_command_1, fault_compensator_2.command_in[1]) 
    annotation(Line(origin={152.5,-395.867},
  points={{209.3,234.617},{232.5,234.617},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));
  connect(mapper_2.rotor_command_2, fault_compensator_2.command_in[2]) 
    annotation(Line(origin={152.5,-395.867},
  points={{209.3,202.117},{232.5,202.117},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));
  connect(mapper_2.rotor_command_3, fault_compensator_2.command_in[3]) 
    annotation(Line(origin={152.5,-395.867},
  points={{209.3,169.617},{232.5,169.617},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));
  connect(mapper_2.rotor_command_4, fault_compensator_2.command_in[4]) 
    annotation(Line(origin={152.5,-395.867},
  points={{209.3,137.117},{232.5,137.117},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));

  // ── Fault Compensator → ESC 2 ──────────────────────────────────────────────────
  connect(fault_compensator_2.command_out[1], esc_2.motor_command_raw[1]) 
    annotation(Line(origin={152.5,-395.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));
  connect(fault_compensator_2.command_out[2], esc_2.motor_command_raw[2]) 
    annotation(Line(origin={152.5,-395.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));
  connect(fault_compensator_2.command_out[3], esc_2.motor_command_raw[3]) 
    annotation(Line(origin={152.5,-395.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}));
  connect(fault_compensator_2.command_out[4], esc_2.motor_command_raw[4]) 
    annotation(Line(origin={152.5,-395.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));

  // ── ESC → Motors 2 ────────────────────────────────────────────────────────────
  connect(esc_2.motor_command[1], motor2_1.command) 
    annotation(Line(origin={152.5,-395.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,231.367},{250,231.367}},
  color={55,80,115}));
  connect(esc_2.motor_command[2], motor2_2.command) 
    annotation(Line(origin={152.5,-395.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,153.049},{250,153.049}},
  color={55,80,115}));
  connect(esc_2.motor_command[3], motor2_3.command) 
    annotation(Line(origin={152.5,-395.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,74.731375},{250,74.731375}},
  color={55,80,115}));
  connect(esc_2.motor_command[4], motor2_4.command) 
    annotation(Line(origin={152.5,-395.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,-4.25},{250,-4.25}},
  color={55,80,115}));

  // ── Motors → Plant 2 ──────────────────────────────────────────────────────────
  connect(motor2_1.command_to_plant, plant_2.rotor_command[1]) 
    annotation(Line(origin={0,0},
  points={{460,-164.5},{485,-164.5},{485,-204},{500,-204}},
  color={55,80,115}));
  connect(motor2_2.command_to_plant, plant_2.rotor_command[2]) 
    annotation(Line(origin={0,0},
  points={{460,-242.818},{485,-242.818},{485,-204},{500,-204}},
  color={55,80,115}));
  connect(motor2_3.command_to_plant, plant_2.rotor_command[3]) 
    annotation(Line(origin={0,0},
  points={{460,-321.135625},{485,-321.135625},{485,-204},{500,-204}},
  color={55,80,115}));
  connect(motor2_4.command_to_plant, plant_2.rotor_command[4]) 
    annotation(Line(origin={0,0},
  points={{460,-400.117},{485,-400.117},{485,-204},{500,-204}},
  color={55,80,115}));

  // ── Plant rotor speed → Motors 2 (feedback) ───────────────────────────────────
  connect(plant_2.rotor_speed[1], motor2_1.speed) 
    annotation(Line(origin={0,0},
  points={{755,-233.5},{775,-233.5},{775,-450},{385,-450},{385,-185.5},{402.5,-185.5}},
  color={130,0,130}));
  connect(plant_2.rotor_speed[2], motor2_2.speed) 
    annotation(Line(origin={0,0},
  points={{755,-233.5},{775,-233.5},{775,-450},{385,-450},{385,-263.818},{402.5,-263.818}},
  color={130,0,130}));
  connect(plant_2.rotor_speed[3], motor2_3.speed) 
    annotation(Line(origin={0,0},
  points={{755,-233.5},{775,-233.5},{775,-450},{385,-450},{385,-342.135625},{402.5,-342.135625}},
  color={130,0,130}));
  connect(plant_2.rotor_speed[4], motor2_4.speed) 
    annotation(Line(origin={0,0},
  points={{755,-233.5},{775,-233.5},{775,-450},{385,-450},{385,-421.117},{402.5,-421.117}},
  color={130,0,130}));

  // ── Plant position → Perception 2 (feedback) ──────────────────────────────────
  connect(plant_2.position, perception_2.position_raw) 
    annotation(Line(origin={152.5,-395.867},
points={{602.5,221.367},{622.5,221.367},{622.5,-54.133},{-602.5,-54.133},{-602.5,5.25},{-587.5,5.25}},
color={0,100,150}));

  // ── Battery → ESC 2 ───────────────────────────────────────────────────────────
  connect(battery_2.bus_voltage, esc_2.bus_voltage) 
    annotation(Line(origin={152.5,-395.867},
  points={{-50,25.25},{-37.5,25.25},{-37.5,5.25},{-17.5,5.25}},
  color={80,80,80}));
  connect(battery_2.power_ok, esc_2.power_ok) 
    annotation(Line(origin={152.5,-395.867},
  points={{-50,5.25},{-37.5,5.25},{-37.5,-17.25},{-17.5,-17.25}},
  color={80,80,80}));

  // ── Perception → Flight Controller 2 ──────────────────────────────────────────
  connect(perception_2.gps_position, flight_controller_2.gps_position) 
    annotation(Line(origin={152.5,-395.867},
  points={{-477.5,35.25},{-462.5,35.25},{-462.5,-54.133},{-172.5,-54.133},{-172.5,37.75},{-192.5,37.75}},
  color={0,100,150}));
  connect(perception_2.gps_valid, flight_controller_2.gps_valid) 
    annotation(Line(origin={152.5,-395.867},
  points={{-477.5,-32.25},{-462.5,-32.25},{-462.5,-54.133},{-172.5,-54.133},{-172.5,-32.25},{-192.5,-32.25}},
  color={0,100,150}), __MWORKS(BlockSystem(NamedSignal)));
  connect(plant_2.attitude, flight_controller_2.attitude_raw) 
    annotation(Line(origin={152.5,-395.867},
  points={{602.5,191.867},{622.5,191.867},{622.5,-54.133},{-172.5,-54.133},{-172.5,17.75},{-192.5,17.75}},
  color={0,100,150}));
  connect(plant_2.rotor_speed, flight_controller_2.motor_speed_raw) 
    annotation(Line(origin={152.5,-395.867},
  points={{602.5,162.367},{622.5,162.367},{622.5,-54.133},{-172.5,-54.133},{-172.5,-7.25},{-192.5,-7.25}},
  color={130,0,130}));

  // ── Perception + FlightController → Mission Computer 2 ────────────────────────
  connect(perception_2.local_position, mission_computer_2.local_position) 
    annotation(Line(origin={152.5,-395.867},
  points={{-477.5,15.25},{-449.5,15.25},{-449.5,12.75},{-445,12.75}},
  color={0,100,150}));
  connect(flight_controller_2.position_est, mission_computer_2.aircraft_position) 
    annotation(Line(origin={152.5,-395.867},
  points={{-302.5,37.75},{-317.5,37.75},{-317.5,-54.133},{-462.5,-54.133},{-462.5,30.25},{-445,30.25}},
  color={100,70,20}));
  connect(perception_2.obstacle_margin, mission_computer_2.obstacle_margin) 
    annotation(Line(origin={152.5,-395.867},
  points={{-477.5,-4.75},{-445,-4.75}},
  color={0,100,150}));
  connect(flight_controller_2.estimator_quality, mission_computer_2.estimator_quality) 
    annotation(Line(origin={152.5,-395.867},
  points={{-302.5,-27.25},{-317.5,-27.25},{-317.5,-54.133},{-462.5,-54.133},{-462.5,-22.25},{-445,-22.25}},
  color={100,70,20}));

  // <<UAV_2_CHAIN_END>>


  // ══════════════════════════════════════════════════════════════════════════════
  // ══ UAV 3 CONTROL CHAIN (Y offset = -790) ════════════════════════════════════
  // ══════════════════════════════════════════════════════════════════════════════

  // ── ECBF safe reference → Input sampler 3 ─────────────────────────────────────
  connect(ecbf_filter.safe_position_3[1], input_sampler_3.pos_ref_x) 
    annotation(Line(origin={0,0},
points={{-502.5,-91.6},{-450,-91.6},{-450,-543.611},{-289.3,-543.611}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(ecbf_filter.safe_position_3[2], input_sampler_3.pos_ref_y) 
    annotation(Line(origin={0,0},
points={{-502.5,-91.6},{-450,-91.6},{-450,-550.833},{-289.3,-550.833}},
color={0,0,127}));
  connect(ecbf_filter.safe_position_3[3], input_sampler_3.pos_ref_z) 
    annotation(Line(origin={0,0},
points={{-502.5,-91.6},{-450,-91.6},{-450,-558.056},{-289.3,-558.056}},
color={0,0,127}));
  connect(ecbf_filter.safe_velocity_3[1], input_sampler_3.vel_ref_x) 
    annotation(Line(origin={0,0},
points={{-502.5,-120.106},{-450,-120.106},{-450,-565.278},{-289.3,-565.278}},
color={0,0,127}));
  connect(ecbf_filter.safe_velocity_3[2], input_sampler_3.vel_ref_y) 
    annotation(Line(origin={0,0},
points={{-502.5,-120.106},{-450,-120.106},{-450,-572.5},{-289.3,-572.5}},
color={0,0,127}));
  connect(ecbf_filter.safe_velocity_3[3], input_sampler_3.vel_ref_z) 
    annotation(Line(origin={0,0},
points={{-502.5,-120.106},{-450,-120.106},{-450,-579.722},{-289.3,-579.722}},
color={0,0,127}));
  connect(ecbf_filter.safe_acceleration_3[1], input_sampler_3.acc_ref_x) 
    annotation(Line(origin={0,0},
points={{-502.5,-148.611},{-450,-148.611},{-450,-586.944},{-289.3,-586.944}},
color={0,0,127}));
  connect(ecbf_filter.safe_acceleration_3[2], input_sampler_3.acc_ref_y) 
    annotation(Line(origin={0,0},
points={{-502.5,-148.611},{-450,-148.611},{-450,-594.167},{-289.3,-594.167}},
color={0,0,127}));
  connect(ecbf_filter.safe_acceleration_3[3], input_sampler_3.acc_ref_z) 
    annotation(Line(origin={0,0},
points={{-502.5,-148.6114},{-450,-148.6114},{-450,-601.389},{-289.3,-601.389}},
color={0,0,127}));

  // ── Plant measurements → Input sampler 3 ──────────────────────────────────────
  connect(plant_3.position[1], input_sampler_3.pos_mea_x) 
    annotation(Line(origin={0,0},
  points={{755,-569.5},{775,-569.5},{775,-845},{-310,-845},{-310,-608.611},{-289.3,-608.611}},
  color={0,100,150}));
  connect(plant_3.position[2], input_sampler_3.pos_mea_y) 
    annotation(Line(origin={0,0},
  points={{755,-569.5},{775,-569.5},{775,-845},{-310,-845},{-310,-615.833},{-289.3,-615.833}},
  color={0,100,150}));
  connect(plant_3.position[3], input_sampler_3.pos_mea_z) 
    annotation(Line(origin={0,0},
  points={{755,-569.5},{775,-569.5},{775,-845},{-310,-845},{-310,-623.056},{-289.3,-623.056}},
  color={0,100,150}));
  connect(plant_3.VelMea[1], input_sampler_3.vel_mea_x) 
    annotation(Line(origin={0,0},
  points={{755,-658},{775,-658},{775,-845},{-310,-845},{-310,-630.278},{-289.3,-630.278}},
  color={0,100,150}),__MWORKS(BlockSystem(NamedSignal)));
  connect(plant_3.VelMea[2], input_sampler_3.vel_mea_y) 
    annotation(Line(origin={0,0},
  points={{755,-658},{775,-658},{775,-845},{-310,-845},{-310,-637.5},{-289.3,-637.5}},
  color={0,100,150}));
  connect(plant_3.VelMea[3], input_sampler_3.vel_mea_z) 
    annotation(Line(origin={0,0},
  points={{755,-658},{775,-658},{775,-845},{-310,-845},{-310,-644.722},{-289.3,-644.722}},
  color={0,100,150}));
  connect(plant_3.attitude[1], input_sampler_3.att_roll) 
    annotation(Line(origin={0,0},
  points={{755,-599},{775,-599},{775,-845},{-310,-845},{-310,-651.944},{-289.3,-651.944}},
  color={0,100,150}));
  connect(plant_3.attitude[2], input_sampler_3.att_pitch) 
    annotation(Line(origin={0,0},
  points={{755,-599},{775,-599},{775,-845},{-310,-845},{-310,-659.167},{-289.3,-659.167}},
  color={0,100,150}));
  connect(plant_3.attitude[3], input_sampler_3.att_yaw) 
    annotation(Line(origin={0,0},
points={{755,-599},{775,-599},{775,-845},{-310,-845},{-310,-666.389},{-289.3,-666.389}},
color={0,100,150}));

  // ── Input sampler → Controller core 3 ─────────────────────────────────────────
  connect(input_sampler_3.s_pos_ref_x, controller_core_3.x_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-546.84},{-145,-546.84}},color={0,0,127}));
  connect(input_sampler_3.s_pos_ref_y, controller_core_3.y_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-553.68},{-145,-553.68}},color={0,0,127}));
  connect(input_sampler_3.s_pos_ref_z, controller_core_3.z_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-560.53},{-145,-560.53}},color={0,0,127}));
  connect(input_sampler_3.s_vel_ref_x, controller_core_3.vx_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-567.37},{-145,-567.37}},color={0,0,127}));
  connect(input_sampler_3.s_vel_ref_y, controller_core_3.vy_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-574.21},{-145,-574.21}},color={0,0,127}));
  connect(input_sampler_3.s_vel_ref_z, controller_core_3.vz_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-581.05},{-145,-581.05}},color={0,0,127}));
  connect(input_sampler_3.s_acc_ref_x, controller_core_3.ax_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-587.89},{-145,-587.89}},color={0,0,127}));
  connect(input_sampler_3.s_acc_ref_y, controller_core_3.ay_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-594.74},{-145,-594.74}},color={0,0,127}));
  connect(input_sampler_3.s_acc_ref_z, controller_core_3.az_ref) 
    annotation(Line(origin={0,0},points={{-187.5,-601.58},{-145,-601.58}},color={0,0,127}));
  connect(input_sampler_3.s_pos_mea_x, controller_core_3.x_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-608.42},{-145,-608.42}},color={0,100,150}));
  connect(input_sampler_3.s_pos_mea_y, controller_core_3.y_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-615.26},{-145,-615.26}},color={0,100,150}));
  connect(input_sampler_3.s_pos_mea_z, controller_core_3.z_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-622.11},{-145,-622.11}},color={0,100,150}));
  connect(input_sampler_3.s_vel_mea_x, controller_core_3.vx_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-628.95},{-145,-628.95}},color={0,100,150}));
  connect(input_sampler_3.s_vel_mea_y, controller_core_3.vy_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-635.79},{-145,-635.79}},color={0,100,150}));
  connect(input_sampler_3.s_vel_mea_z, controller_core_3.vz_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-642.63},{-145,-642.63}},color={0,100,150}));
  connect(input_sampler_3.s_att_roll, controller_core_3.roll_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-649.47},{-145,-649.47}},color={0,100,150}));
  connect(input_sampler_3.s_att_pitch, controller_core_3.pitch_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-656.32},{-145,-656.32}},color={0,100,150}));
  connect(input_sampler_3.s_att_yaw, controller_core_3.yaw_mea) 
    annotation(Line(origin={0,0},points={{-187.5,-663.16},{-145,-663.16}},color={0,100,150}));

  // ── Controller core → Output bridge 3 ─────────────────────────────────────────
  connect(controller_core_3.y,  output_bridge_3.amp_1) 
    annotation(Line(origin={0,0},points={{15,-556.25},{57.5,-556.25}},color={55,80,115}));
  connect(controller_core_3.y1, output_bridge_3.amp_2) 
    annotation(Line(origin={0,0},points={{15,-588.75},{57.5,-588.75}},color={55,80,115}));
  connect(controller_core_3.y2, output_bridge_3.amp_3) 
    annotation(Line(origin={0,0},points={{15,-621.25},{57.5,-621.25}},color={55,80,115}));
  connect(controller_core_3.y3, output_bridge_3.amp_4) 
    annotation(Line(origin={0,0},points={{15,-653.75},{57.5,-653.75}},color={55,80,115}));

  // ── Output bridge → Mapper 3 ──────────────────────────────────────────────────
  connect(output_bridge_3.out_1, mapper_3.amplitude_1) 
    annotation(Line(origin={0,0},points={{157.5,-556.25},{200,-556.25}},color={55,80,115}));
  connect(output_bridge_3.out_2, mapper_3.amplitude_2) 
    annotation(Line(origin={0,0},points={{157.5,-588.75},{200,-588.75}},color={55,80,115}));
  connect(output_bridge_3.out_3, mapper_3.amplitude_3) 
    annotation(Line(origin={0,0},points={{157.5,-621.25},{200,-621.25}},color={55,80,115}));
  connect(output_bridge_3.out_4, mapper_3.amplitude_4) 
    annotation(Line(origin={0,0},points={{157.5,-653.75},{200,-653.75}},color={55,80,115}));

  // ── Mapper → Fault Compensator 3 (route via x=330, y=-845 bus) ───────────────
  connect(mapper_3.rotor_command_1, fault_compensator_3.command_in[1]) 
    annotation(Line(origin={152.5,-790.867},
  points={{209.3,234.617},{232.5,234.617},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));
  connect(mapper_3.rotor_command_2, fault_compensator_3.command_in[2]) 
    annotation(Line(origin={152.5,-790.867},
  points={{209.3,202.117},{232.5,202.117},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));
  connect(mapper_3.rotor_command_3, fault_compensator_3.command_in[3]) 
    annotation(Line(origin={152.5,-790.867},
  points={{209.3,169.617},{232.5,169.617},{232.5,-54.133},{102.5,-54.133},{102.5,5.25},{118.75,5.25}},
  color={55,80,115}));
  connect(mapper_3.rotor_command_4, fault_compensator_3.command_in[4]) 
    annotation(Line(origin={0,0},
  points={{361.8,-484.133},{385,-484.133},{385,-845},{255,-845},{255,-785.617},{271.25,-785.617}},
  color={55,80,115}));

  // ── Fault Compensator → ESC 3 ──────────────────────────────────────────────────
  connect(fault_compensator_3.command_out[1], esc_3.motor_command_raw[1]) 
    annotation(Line(origin={152.5,-790.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));
  connect(fault_compensator_3.command_out[2], esc_3.motor_command_raw[2]) 
    annotation(Line(origin={152.5,-790.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));
  connect(fault_compensator_3.command_out[3], esc_3.motor_command_raw[3]) 
    annotation(Line(origin={152.5,-790.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}));
  connect(fault_compensator_3.command_out[4], esc_3.motor_command_raw[4]) 
    annotation(Line(origin={152.5,-790.867},
  points={{218.75,5.25},{232.5,5.25},{232.5,-54.133},{-37.5,-54.133},{-37.5,27.75},{-17.5,27.75}},
  color={55,80,115}), __MWORKS(BlockSystem(NamedSignal)));

  // ── ESC → Motors 3 ────────────────────────────────────────────────────────────
  connect(esc_3.motor_command[1], motor3_1.command) 
    annotation(Line(origin={152.5,-790.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,231.367},{250,231.367}},
  color={55,80,115}));
  connect(esc_3.motor_command[2], motor3_2.command) 
    annotation(Line(origin={152.5,-790.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,153.049},{250,153.049}},
  color={55,80,115}));
  connect(esc_3.motor_command[3], motor3_3.command) 
    annotation(Line(origin={152.5,-790.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,74.731375},{250,74.731375}},
  color={55,80,115}));
  connect(esc_3.motor_command[4], motor3_4.command) 
    annotation(Line(origin={152.5,-790.867},
  points={{92.5,22.75},{102.5,22.75},{102.5,-54.133},{232.5,-54.133},{232.5,-4.25},{250,-4.25}},
  color={55,80,115}));

  // ── Motors → Plant 3 ──────────────────────────────────────────────────────────
  connect(motor3_1.command_to_plant, plant_3.rotor_command[1]) 
    annotation(Line(origin={0,0},
  points={{460,-559.5},{485,-559.5},{485,-599},{500,-599}},
  color={55,80,115}));
  connect(motor3_2.command_to_plant, plant_3.rotor_command[2]) 
    annotation(Line(origin={0,0},
  points={{460,-637.818},{485,-637.818},{485,-599},{500,-599}},
  color={55,80,115}));
  connect(motor3_3.command_to_plant, plant_3.rotor_command[3]) 
    annotation(Line(origin={0,0},
  points={{460,-716.135625},{485,-716.135625},{485,-599},{500,-599}},
  color={55,80,115}));
  connect(motor3_4.command_to_plant, plant_3.rotor_command[4]) 
    annotation(Line(origin={0,0},
  points={{460,-795.117},{485,-795.117},{485,-599},{500,-599}},
  color={55,80,115}));

  // ── Plant rotor speed → Motors 3 (feedback) ───────────────────────────────────
  connect(plant_3.rotor_speed[1], motor3_1.speed) 
    annotation(Line(origin={0,0},
  points={{755,-628.5},{775,-628.5},{775,-845},{385,-845},{385,-580.5},{402.5,-580.5}},
  color={130,0,130}));
  connect(plant_3.rotor_speed[2], motor3_2.speed) 
    annotation(Line(origin={0,0},
  points={{755,-628.5},{775,-628.5},{775,-845},{385,-845},{385,-658.818},{402.5,-658.818}},
  color={130,0,130}));
  connect(plant_3.rotor_speed[3], motor3_3.speed) 
    annotation(Line(origin={0,0},
  points={{755,-628.5},{775,-628.5},{775,-845},{385,-845},{385,-737.135625},{402.5,-737.135625}},
  color={130,0,130}));
  connect(plant_3.rotor_speed[4], motor3_4.speed) 
    annotation(Line(origin={0,0},
  points={{755,-628.5},{775,-628.5},{775,-845},{385,-845},{385,-816.117},{402.5,-816.117}},
  color={130,0,130}));

  // ── Plant position → Perception 3 (feedback) ──────────────────────────────────
  connect(plant_3.position, perception_3.position_raw) 
    annotation(Line(origin={152.5,-790.867},
points={{602.5,221.367},{622.5,221.367},{622.5,-54.133},{-602.5,-54.133},{-602.5,5.25},{-587.5,5.25}},
color={0,100,150}));

  // ── Battery → ESC 3 ───────────────────────────────────────────────────────────
  connect(battery_3.bus_voltage, esc_3.bus_voltage) 
    annotation(Line(origin={152.5,-790.867},
  points={{-50,25.25},{-37.5,25.25},{-37.5,5.25},{-17.5,5.25}},
  color={80,80,80}));
  connect(battery_3.power_ok, esc_3.power_ok) 
    annotation(Line(origin={152.5,-790.867},
  points={{-50,5.25},{-37.5,5.25},{-37.5,-17.25},{-17.5,-17.25}},
  color={80,80,80}));

  // ── Perception → Flight Controller 3 ──────────────────────────────────────────
  connect(perception_3.gps_position, flight_controller_3.gps_position) 
    annotation(Line(origin={152.5,-790.867},
  points={{-477.5,35.25},{-462.5,35.25},{-462.5,-54.133},{-172.5,-54.133},{-172.5,37.75},{-192.5,37.75}},
  color={0,100,150}));
  connect(perception_3.gps_valid, flight_controller_3.gps_valid) 
    annotation(Line(origin={152.5,-790.867},
  points={{-477.5,-32.25},{-462.5,-32.25},{-462.5,-54.133},{-172.5,-54.133},{-172.5,-32.25},{-192.5,-32.25}},
  color={0,100,150}), __MWORKS(BlockSystem(NamedSignal)));
  connect(plant_3.attitude, flight_controller_3.attitude_raw) 
    annotation(Line(origin={152.5,-790.867},
  points={{602.5,191.867},{622.5,191.867},{622.5,-54.133},{-172.5,-54.133},{-172.5,17.75},{-192.5,17.75}},
  color={0,100,150}));
  connect(plant_3.rotor_speed, flight_controller_3.motor_speed_raw) 
    annotation(Line(origin={152.5,-790.867},
  points={{602.5,162.367},{622.5,162.367},{622.5,-54.133},{-172.5,-54.133},{-172.5,-7.25},{-192.5,-7.25}},
  color={130,0,130}));

  // ── Perception + FlightController → Mission Computer 3 ────────────────────────
  connect(perception_3.local_position, mission_computer_3.local_position) 
    annotation(Line(origin={152.5,-790.867},
  points={{-477.5,15.25},{-449.5,15.25},{-449.5,12.75},{-445,12.75}},
  color={0,100,150}));
  connect(flight_controller_3.position_est, mission_computer_3.aircraft_position) 
    annotation(Line(origin={152.5,-790.867},
  points={{-302.5,37.75},{-317.5,37.75},{-317.5,-54.133},{-462.5,-54.133},{-462.5,30.25},{-445,30.25}},
  color={100,70,20}));
  connect(perception_3.obstacle_margin, mission_computer_3.obstacle_margin) 
    annotation(Line(origin={152.5,-790.867},
  points={{-477.5,-4.75},{-445,-4.75}},
  color={0,100,150}));
  connect(flight_controller_3.estimator_quality, mission_computer_3.estimator_quality) 
    annotation(Line(origin={152.5,-790.867},
  points={{-302.5,-27.25},{-317.5,-27.25},{-317.5,-54.133},{-462.5,-54.133},{-462.5,-22.25},{-445,-22.25}},
  color={100,70,20}));

  // ── UAV 1 → native OpenBlocks map truth/reference display ────────────────────
  connect(plant_1.position[1], nav_display.actual_position[1]) 
    annotation(Line(points={{755,220.5},{800,220.5},{800,-112.5},{-430,-112.5}},
      color={0,100,150}));
  connect(plant_1.position[2], nav_display.actual_position[2]) 
    annotation(Line(points={{755,220.5},{800,220.5},{800,-112.5},{-430,-112.5}},
      color={0,100,150}));
  connect(plant_1.position[3], nav_display.actual_position[3]) 
    annotation(Line(points={{755,220.5},{800,220.5},{800,-112.5},{-430,-112.5}},
      color={0,100,150}));
  connect(openblocks_ref_1.position_command[1], nav_display.reference_position[1]) 
    annotation(Line(points={{-735,-40},{-700,-40},{-700,-137.5},{-430,-137.5}},
      color={0,0,127}));
  connect(openblocks_ref_1.position_command[2], nav_display.reference_position[2]) 
    annotation(Line(points={{-735,-40},{-700,-40},{-700,-137.5},{-430,-137.5}},
      color={0,0,127}));
  connect(openblocks_ref_1.position_command[3], nav_display.reference_position[3]) 
    annotation(Line(points={{-735,-40},{-700,-40},{-700,-137.5},{-430,-137.5}},
      color={0,0,127}));

  // <<UAV_3_CHAIN_END>>


  // ══════════════════════════════════════════════════════════════════════════════
  // ══ FORMATION CROSS-CONNECTIONS (Three Independent Trajectories → ECBF) ══════
  // ══════════════════════════════════════════════════════════════════════════════

  // ── UAV 1 trajectory reference → ECBF filter ──────────────────────────────────
  connect(openblocks_ref_1.position_command[1], ecbf_filter.nominal_position_1[1]) 
    annotation(Line(origin={0,0},
  points={{-735,-40},{-705,-40},{-705,-35.433},{-662.5,-35.433}},
  color={0,0,127}));
  connect(openblocks_ref_1.position_command[2], ecbf_filter.nominal_position_1[2]) 
    annotation(Line(origin={0,0},
  points={{-735,-40},{-705,-40},{-705,-35.433},{-662.5,-35.433}},
  color={0,0,127}));
  connect(openblocks_ref_1.position_command[3], ecbf_filter.nominal_position_1[3]) 
    annotation(Line(origin={0,0},
  points={{-735,-40},{-705,-40},{-705,-35.433},{-662.5,-35.433}},
  color={0,0,127}));
  connect(openblocks_ref_1.velocity_command[1], ecbf_filter.nominal_velocity_1[1]) 
    annotation(Line(origin={0,0},
  points={{-735,-40},{-705,-40},{-705,-63.939},{-662.5,-63.939}},
  color={0,0,127}));
  connect(openblocks_ref_1.velocity_command[2], ecbf_filter.nominal_velocity_1[2]) 
    annotation(Line(origin={0,0},
  points={{-735,-40},{-705,-40},{-705,-63.939},{-662.5,-63.939}},
  color={0,0,127}));
  connect(openblocks_ref_1.velocity_command[3], ecbf_filter.nominal_velocity_1[3]) 
    annotation(Line(origin={0,0},
  points={{-735,-40},{-705,-40},{-705,-63.939},{-662.5,-63.939}},
  color={0,0,127}));
  connect(openblocks_ref_1.acceleration_command[1], ecbf_filter.nominal_acceleration_1[1]) 
    annotation(Line(origin={0,0},
  points={{-735,-40},{-705,-40},{-705,-92.444},{-662.5,-92.444}},
  color={0,0,127}));
  connect(openblocks_ref_1.acceleration_command[2], ecbf_filter.nominal_acceleration_1[2]) 
    annotation(Line(origin={0,0},
  points={{-735,-40},{-705,-40},{-705,-92.444},{-662.5,-92.444}},
  color={0,0,127}));
  connect(openblocks_ref_1.acceleration_command[3], ecbf_filter.nominal_acceleration_1[3]) 
    annotation(Line(origin={0,0},
  points={{-735,-40},{-705,-40},{-705,-92.444},{-662.5,-92.444}},
  color={0,0,127}));

  // ── UAV 2 trajectory reference → ECBF filter ──────────────────────────────────
  connect(openblocks_ref_2.position_command[1], ecbf_filter.nominal_position_2[1]) 
    annotation(Line(origin={0,0},
  points={{-735,-170},{-705,-170},{-705,-35.433},{-662.5,-35.433}},
  color={0,0,127}));
  connect(openblocks_ref_2.position_command[2], ecbf_filter.nominal_position_2[2]) 
    annotation(Line(origin={0,0},
  points={{-735,-170},{-705,-170},{-705,-35.433},{-662.5,-35.433}},
  color={0,0,127}));
  connect(openblocks_ref_2.position_command[3], ecbf_filter.nominal_position_2[3]) 
    annotation(Line(origin={0,0},
  points={{-735,-170},{-705,-170},{-705,-35.433},{-662.5,-35.433}},
  color={0,0,127}));
  connect(openblocks_ref_2.velocity_command[1], ecbf_filter.nominal_velocity_2[1]) 
    annotation(Line(origin={0,0},
  points={{-735,-170},{-705,-170},{-705,-63.939},{-662.5,-63.939}},
  color={0,0,127}));
  connect(openblocks_ref_2.velocity_command[2], ecbf_filter.nominal_velocity_2[2]) 
    annotation(Line(origin={0,0},
  points={{-735,-170},{-705,-170},{-705,-63.939},{-662.5,-63.939}},
  color={0,0,127}));
  connect(openblocks_ref_2.velocity_command[3], ecbf_filter.nominal_velocity_2[3]) 
    annotation(Line(origin={0,0},
  points={{-735,-170},{-705,-170},{-705,-63.939},{-662.5,-63.939}},
  color={0,0,127}));
  connect(openblocks_ref_2.acceleration_command[1], ecbf_filter.nominal_acceleration_2[1]) 
    annotation(Line(origin={0,0},
  points={{-735,-170},{-705,-170},{-705,-92.444},{-662.5,-92.444}},
  color={0,0,127}));
  connect(openblocks_ref_2.acceleration_command[2], ecbf_filter.nominal_acceleration_2[2]) 
    annotation(Line(origin={0,0},
  points={{-735,-170},{-705,-170},{-705,-92.444},{-662.5,-92.444}},
  color={0,0,127}));
  connect(openblocks_ref_2.acceleration_command[3], ecbf_filter.nominal_acceleration_2[3]) 
    annotation(Line(origin={0,0},
  points={{-735,-170},{-705,-170},{-705,-92.444},{-662.5,-92.444}},
  color={0,0,127}));

  // ── UAV 3 trajectory reference → ECBF filter ──────────────────────────────────
  connect(openblocks_ref_3.position_command[1], ecbf_filter.nominal_position_3[1]) 
    annotation(Line(origin={0,0},
  points={{-735,-300},{-705,-300},{-705,-35.433},{-662.5,-35.433}},
  color={0,0,127}));
  connect(openblocks_ref_3.position_command[2], ecbf_filter.nominal_position_3[2]) 
    annotation(Line(origin={0,0},
  points={{-735,-300},{-705,-300},{-705,-35.433},{-662.5,-35.433}},
  color={0,0,127}));
  connect(openblocks_ref_3.position_command[3], ecbf_filter.nominal_position_3[3]) 
    annotation(Line(origin={0,0},
  points={{-735,-300},{-705,-300},{-705,-35.433},{-662.5,-35.433}},
  color={0,0,127}));
  connect(openblocks_ref_3.velocity_command[1], ecbf_filter.nominal_velocity_3[1]) 
    annotation(Line(origin={0,0},
  points={{-735,-300},{-705,-300},{-705,-63.939},{-662.5,-63.939}},
  color={0,0,127}));
  connect(openblocks_ref_3.velocity_command[2], ecbf_filter.nominal_velocity_3[2]) 
    annotation(Line(origin={0,0},
  points={{-735,-300},{-705,-300},{-705,-63.939},{-662.5,-63.939}},
  color={0,0,127}));
  connect(openblocks_ref_3.velocity_command[3], ecbf_filter.nominal_velocity_3[3]) 
    annotation(Line(origin={0,0},
  points={{-735,-300},{-705,-300},{-705,-63.939},{-662.5,-63.939}},
  color={0,0,127}));
  connect(openblocks_ref_3.acceleration_command[1], ecbf_filter.nominal_acceleration_3[1]) 
    annotation(Line(origin={0,0},
  points={{-735,-300},{-705,-300},{-705,-92.444},{-662.5,-92.444}},
  color={0,0,127}));
  connect(openblocks_ref_3.acceleration_command[2], ecbf_filter.nominal_acceleration_3[2]) 
    annotation(Line(origin={0,0},
  points={{-735,-300},{-705,-300},{-705,-92.444},{-662.5,-92.444}},
  color={0,0,127}));
  connect(openblocks_ref_3.acceleration_command[3], ecbf_filter.nominal_acceleration_3[3]) 
    annotation(Line(origin={0,0},
  points={{-735,-300},{-705,-300},{-705,-92.444},{-662.5,-92.444}},
  color={0,0,127}));

  // ══════════════════════════════════════════════════════════════════════════════
  // ══ OBSERVABLE EXPORTS ════════════════════════════════════════════════════════
  // ══════════════════════════════════════════════════════════════════════════════

  connect(plant_1.position, pos_1) annotation(Line(origin={0,0},
    points={{755,220.5},{785,220.5}},
    color={0,100,150}));
  connect(plant_1.attitude, att_1) annotation(Line(origin={0,0},
    points={{755,191},{785,191}},
    color={0,100,150}));
  connect(plant_2.position, pos_2) annotation(Line(origin={0,0},
    points={{755,-174.5},{785,-174.5}},
    color={0,100,150}));
  connect(plant_2.attitude, att_2) annotation(Line(origin={0,0},
    points={{755,-204},{785,-204}},
    color={0,100,150}));
  connect(plant_3.position, pos_3) annotation(Line(origin={0,0},
    points={{755,-569.5},{785,-569.5}},
    color={0,100,150}));
  connect(plant_3.attitude, att_3) annotation(Line(origin={0,0},
    points={{755,-599},{785,-599}},
    color={0,100,150}));

  annotation(
    Icon(coordinateSystem(extent={{-920,-900},{920,900}}), graphics={
      Rectangle(extent={{-920,-900},{920,900}}, lineColor={28,108,200}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),
      Text(extent={{-800,850},{800,750}}, textString="Three UAV", textColor={28,108,200}),
      Text(extent={{-800,650},{800,550}}, textString="Heterogeneous", textColor={28,108,200}),
      Text(extent={{-800,450},{800,350}}, textString="OpenBlocks", textColor={0,140,72}),
      Text(extent={{-800,250},{800,150}}, textString="Obstacle Avoidance", textColor={238,46,47}),
      Text(extent={{-800,50},{800,-50}}, textString="with ECBF", textColor={217,67,180}),
      Ellipse(extent={{-600,-200},{-400,-400}}, lineColor={28,108,200}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),
      Ellipse(extent={{-200,-200},{0,-400}}, lineColor={28,108,200}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),
      Ellipse(extent={{200,-200},{400,-400}}, lineColor={28,108,200}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),
      Line(points={{-500,-250},{-100,-250}}, color={217,67,180}, thickness=2, pattern=LinePattern.Dash),
      Line(points={{-100,-250},{300,-250}}, color={217,67,180}, thickness=2, pattern=LinePattern.Dash),
      Line(points={{-500,-350},{300,-350}}, color={217,67,180}, thickness=2, pattern=LinePattern.Dash),
      Text(extent={{-650,-450},{-350,-550}}, textString="UAV 1", textColor={28,108,200}),
      Text(extent={{-250,-450},{50,-550}}, textString="UAV 2", textColor={28,108,200}),
      Text(extent={{150,-450},{450,-550}}, textString="UAV 3", textColor={28,108,200}),
      Polygon(points={{-520,-280},{-480,-280},{-500,-320},{-520,-280}}, lineColor={0,140,72}, fillColor={0,140,72}, fillPattern=FillPattern.Solid),
      Polygon(points={{-120,-280},{-80,-280},{-100,-320},{-120,-280}}, lineColor={0,140,72}, fillColor={0,140,72}, fillPattern=FillPattern.Solid),
      Polygon(points={{280,-280},{320,-280},{300,-320},{280,-280}}, lineColor={0,140,72}, fillColor={0,140,72}, fillPattern=FillPattern.Solid),
      Text(extent={{-800,-600},{800,-700}}, textString="Independent A* Trajectories", textColor={0,140,72}),
      Text(extent={{-800,-750},{800,-850}}, textString="Pairwise Collision Avoidance", textColor={217,67,180})}),
    Diagram(coordinateSystem(extent={{-920,-900},{920,900}})),
    experiment(StartTime=0, StopTime=120, Tolerance=1e-06, Interval=0.005),
    __OpenModelica_simulationFlags(lv="LOG_STATS", outputFormat="mat", s="dassl"),
    __MWORKS(version="26.3.0"));
end ThreeUavHeterogeneousOpenBlocksRunner;
