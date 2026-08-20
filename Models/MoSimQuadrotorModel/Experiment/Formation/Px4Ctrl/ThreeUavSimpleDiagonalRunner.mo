within MoSimQuadrotorModel.Experiment.Formation.Px4Ctrl;
model ThreeUavSimpleDiagonalRunner
  "Three-UAV simple diagonal formation: (0,0,1) → (10,10,5) with time-offset takeoff, no obstacles"

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

  // ── Diagnostic metrics ────────────────────────────────────────────────────────
  Modelica.Blocks.Interfaces.RealOutput minimum_pair_distance_m(unit = "m")
    "Minimum pairwise distance among all three UAVs"
    annotation(Placement(transformation(origin={800,-700}, extent={{-15,-15},{15,15}})));
  Modelica.Blocks.Interfaces.RealOutput max_position_error_norm(unit = "m")
    "Maximum position error among all three UAVs"
    annotation(Placement(transformation(origin={800,-740}, extent={{-15,-15},{15,15}})));

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

  // ── Simple diagonal trajectory references ─────────────────────────────────────
  MoSimQuadrotorModel.Guidance.Trajectories.SimpleDiagonalReference ref_1(
    start_time = 0,
    x_start = 0, y_start = 0, z_start = 1,
    x_end = 10, y_end = 10, z_end = 5,
    duration = 60)
    annotation(Placement(transformation(origin={-827.5,-40}, extent={{-92.5,-142.528},{92.5,142.528}})));

  MoSimQuadrotorModel.Guidance.Trajectories.SimpleDiagonalReference ref_2(
    start_time = 5,
    x_start = 0, y_start = 0, z_start = 1,
    x_end = 10, y_end = 10, z_end = 5,
    duration = 60)
    annotation(Placement(transformation(origin={-827.5,-170}, extent={{-92.5,-142.528},{92.5,142.528}})));

  MoSimQuadrotorModel.Guidance.Trajectories.SimpleDiagonalReference ref_3(
    start_time = 10,
    x_start = 0, y_start = 0, z_start = 1,
    x_end = 10, y_end = 10, z_end = 5,
    duration = 60)
    annotation(Placement(transformation(origin={-827.5,-300}, extent={{-92.5,-142.528},{92.5,142.528}})));

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
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant_1(
    initial_position_m  = {0, 0, 0},
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
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant_2(
    initial_position_m  = {0, 0, 0},
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
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant_3(
    initial_position_m  = {0, 0, 0},
    rotor_effectiveness = rotor_effectiveness_3,
    gust_force          = gust_force,
    gust_start_s        = gust_start_s,
    gust_duration_s     = gust_duration_s,
    mass_scale          = mass_scale,
    inertia_scale       = inertia_scale)
    annotation(Placement(transformation(origin = {627.5, -687.5}, extent = {{-127.5, -147.5}, {127.5, 147.5}})));

protected
  Real d12, d13, d23;
  Real err1, err2, err3;

equation
  // ── UAV 1 connections ─────────────────────────────────────────────────────────
  connect(ref_1.position_command[1], input_sampler_1.pos_ref_x);
  connect(ref_1.position_command[2], input_sampler_1.pos_ref_y);
  connect(ref_1.position_command[3], input_sampler_1.pos_ref_z);
  connect(ref_1.velocity_command[1], input_sampler_1.vel_ref_x);
  connect(ref_1.velocity_command[2], input_sampler_1.vel_ref_y);
  connect(ref_1.velocity_command[3], input_sampler_1.vel_ref_z);
  input_sampler_1.acc_ref_x = 0;
  input_sampler_1.acc_ref_y = 0;
  input_sampler_1.acc_ref_z = 0;
  connect(plant_1.position_m[1], input_sampler_1.pos_mea_x);
  connect(plant_1.position_m[2], input_sampler_1.pos_mea_y);
  connect(plant_1.position_m[3], input_sampler_1.pos_mea_z);
  connect(plant_1.velocity_mps[1], input_sampler_1.vel_mea_x);
  connect(plant_1.velocity_mps[2], input_sampler_1.vel_mea_y);
  connect(plant_1.velocity_mps[3], input_sampler_1.vel_mea_z);
  connect(plant_1.attitude_rad[1], input_sampler_1.att_roll);
  connect(plant_1.attitude_rad[2], input_sampler_1.att_pitch);
  connect(plant_1.attitude_rad[3], input_sampler_1.att_yaw);

  connect(input_sampler_1.s_pos_err_x, controller_core_1.position_error[1]);
  connect(input_sampler_1.s_pos_err_y, controller_core_1.position_error[2]);
  connect(input_sampler_1.s_pos_err_z, controller_core_1.position_error[3]);
  connect(input_sampler_1.s_vel_err_x, controller_core_1.velocity_error[1]);
  connect(input_sampler_1.s_vel_err_y, controller_core_1.velocity_error[2]);
  connect(input_sampler_1.s_vel_err_z, controller_core_1.velocity_error[3]);
  connect(input_sampler_1.s_vel_ref_x, controller_core_1.velocity_reference[1]);
  connect(input_sampler_1.s_vel_ref_y, controller_core_1.velocity_reference[2]);
  connect(input_sampler_1.s_vel_ref_z, controller_core_1.velocity_reference[3]);
  connect(input_sampler_1.s_att_roll, controller_core_1.attitude_actual[1]);
  connect(input_sampler_1.s_att_pitch, controller_core_1.attitude_actual[2]);
  connect(input_sampler_1.s_att_yaw, controller_core_1.attitude_actual[3]);

  connect(controller_core_1.thrust_reference, output_bridge_1.thrust_input);
  connect(controller_core_1.attitude_reference, output_bridge_1.attitude_input);
  connect(output_bridge_1.thrust_output, mapper_1.collective_thrust);
  connect(output_bridge_1.attitude_output, mapper_1.attitude_reference);
  connect(plant_1.attitude_rad, mapper_1.attitude_actual);
  connect(mapper_1.rotor_speed_command, plant_1.rotor_speed_command_radps);

  // ── UAV 2 connections ─────────────────────────────────────────────────────────
  connect(ref_2.position_command[1], input_sampler_2.pos_ref_x);
  connect(ref_2.position_command[2], input_sampler_2.pos_ref_y);
  connect(ref_2.position_command[3], input_sampler_2.pos_ref_z);
  connect(ref_2.velocity_command[1], input_sampler_2.vel_ref_x);
  connect(ref_2.velocity_command[2], input_sampler_2.vel_ref_y);
  connect(ref_2.velocity_command[3], input_sampler_2.vel_ref_z);
  input_sampler_2.acc_ref_x = 0;
  input_sampler_2.acc_ref_y = 0;
  input_sampler_2.acc_ref_z = 0;
  connect(plant_2.position_m[1], input_sampler_2.pos_mea_x);
  connect(plant_2.position_m[2], input_sampler_2.pos_mea_y);
  connect(plant_2.position_m[3], input_sampler_2.pos_mea_z);
  connect(plant_2.velocity_mps[1], input_sampler_2.vel_mea_x);
  connect(plant_2.velocity_mps[2], input_sampler_2.vel_mea_y);
  connect(plant_2.velocity_mps[3], input_sampler_2.vel_mea_z);
  connect(plant_2.attitude_rad[1], input_sampler_2.att_roll);
  connect(plant_2.attitude_rad[2], input_sampler_2.att_pitch);
  connect(plant_2.attitude_rad[3], input_sampler_2.att_yaw);

  connect(input_sampler_2.s_pos_err_x, controller_core_2.position_error[1]);
  connect(input_sampler_2.s_pos_err_y, controller_core_2.position_error[2]);
  connect(input_sampler_2.s_pos_err_z, controller_core_2.position_error[3]);
  connect(input_sampler_2.s_vel_err_x, controller_core_2.velocity_error[1]);
  connect(input_sampler_2.s_vel_err_y, controller_core_2.velocity_error[2]);
  connect(input_sampler_2.s_vel_err_z, controller_core_2.velocity_error[3]);
  connect(input_sampler_2.s_vel_ref_x, controller_core_2.velocity_reference[1]);
  connect(input_sampler_2.s_vel_ref_y, controller_core_2.velocity_reference[2]);
  connect(input_sampler_2.s_vel_ref_z, controller_core_2.velocity_reference[3]);
  connect(input_sampler_2.s_att_roll, controller_core_2.attitude_actual[1]);
  connect(input_sampler_2.s_att_pitch, controller_core_2.attitude_actual[2]);
  connect(input_sampler_2.s_att_yaw, controller_core_2.attitude_actual[3]);

  connect(controller_core_2.thrust_reference, output_bridge_2.thrust_input);
  connect(controller_core_2.attitude_reference, output_bridge_2.attitude_input);
  connect(output_bridge_2.thrust_output, mapper_2.collective_thrust);
  connect(output_bridge_2.attitude_output, mapper_2.attitude_reference);
  connect(plant_2.attitude_rad, mapper_2.attitude_actual);
  connect(mapper_2.rotor_speed_command, plant_2.rotor_speed_command_radps);

  // ── UAV 3 connections ─────────────────────────────────────────────────────────
  connect(ref_3.position_command[1], input_sampler_3.pos_ref_x);
  connect(ref_3.position_command[2], input_sampler_3.pos_ref_y);
  connect(ref_3.position_command[3], input_sampler_3.pos_ref_z);
  connect(ref_3.velocity_command[1], input_sampler_3.vel_ref_x);
  connect(ref_3.velocity_command[2], input_sampler_3.vel_ref_y);
  connect(ref_3.velocity_command[3], input_sampler_3.vel_ref_z);
  input_sampler_3.acc_ref_x = 0;
  input_sampler_3.acc_ref_y = 0;
  input_sampler_3.acc_ref_z = 0;
  connect(plant_3.position_m[1], input_sampler_3.pos_mea_x);
  connect(plant_3.position_m[2], input_sampler_3.pos_mea_y);
  connect(plant_3.position_m[3], input_sampler_3.pos_mea_z);
  connect(plant_3.velocity_mps[1], input_sampler_3.vel_mea_x);
  connect(plant_3.velocity_mps[2], input_sampler_3.vel_mea_y);
  connect(plant_3.velocity_mps[3], input_sampler_3.vel_mea_z);
  connect(plant_3.attitude_rad[1], input_sampler_3.att_roll);
  connect(plant_3.attitude_rad[2], input_sampler_3.att_pitch);
  connect(plant_3.attitude_rad[3], input_sampler_3.att_yaw);

  connect(input_sampler_3.s_pos_err_x, controller_core_3.position_error[1]);
  connect(input_sampler_3.s_pos_err_y, controller_core_3.position_error[2]);
  connect(input_sampler_3.s_pos_err_z, controller_core_3.position_error[3]);
  connect(input_sampler_3.s_vel_err_x, controller_core_3.velocity_error[1]);
  connect(input_sampler_3.s_vel_err_y, controller_core_3.velocity_error[2]);
  connect(input_sampler_3.s_vel_err_z, controller_core_3.velocity_error[3]);
  connect(input_sampler_3.s_vel_ref_x, controller_core_3.velocity_reference[1]);
  connect(input_sampler_3.s_vel_ref_y, controller_core_3.velocity_reference[2]);
  connect(input_sampler_3.s_vel_ref_z, controller_core_3.velocity_reference[3]);
  connect(input_sampler_3.s_att_roll, controller_core_3.attitude_actual[1]);
  connect(input_sampler_3.s_att_pitch, controller_core_3.attitude_actual[2]);
  connect(input_sampler_3.s_att_yaw, controller_core_3.attitude_actual[3]);

  connect(controller_core_3.thrust_reference, output_bridge_3.thrust_input);
  connect(controller_core_3.attitude_reference, output_bridge_3.attitude_input);
  connect(output_bridge_3.thrust_output, mapper_3.collective_thrust);
  connect(output_bridge_3.attitude_output, mapper_3.attitude_reference);
  connect(plant_3.attitude_rad, mapper_3.attitude_actual);
  connect(mapper_3.rotor_speed_command, plant_3.rotor_speed_command_radps);

  // ── Observable outputs ────────────────────────────────────────────────────────
  connect(plant_1.position_m, pos_1);
  connect(plant_1.attitude_rad, att_1);
  connect(plant_2.position_m, pos_2);
  connect(plant_2.attitude_rad, att_2);
  connect(plant_3.position_m, pos_3);
  connect(plant_3.attitude_rad, att_3);

  // ── Diagnostic metrics ────────────────────────────────────────────────────────
  d12 = sqrt((pos_1[1] - pos_2[1])^2 + (pos_1[2] - pos_2[2])^2 + (pos_1[3] - pos_2[3])^2);
  d13 = sqrt((pos_1[1] - pos_3[1])^2 + (pos_1[2] - pos_3[2])^2 + (pos_1[3] - pos_3[3])^2);
  d23 = sqrt((pos_2[1] - pos_3[1])^2 + (pos_2[2] - pos_3[2])^2 + (pos_2[3] - pos_3[3])^2);
  minimum_pair_distance_m = min(d12, min(d13, d23));

  err1 = sqrt((pos_1[1] - ref_1.position_command[1])^2 +
              (pos_1[2] - ref_1.position_command[2])^2 +
              (pos_1[3] - ref_1.position_command[3])^2);
  err2 = sqrt((pos_2[1] - ref_2.position_command[1])^2 +
              (pos_2[2] - ref_2.position_command[2])^2 +
              (pos_2[3] - ref_2.position_command[3])^2);
  err3 = sqrt((pos_3[1] - ref_3.position_command[1])^2 +
              (pos_3[2] - ref_3.position_command[2])^2 +
              (pos_3[3] - ref_3.position_command[3])^2);
  max_position_error_norm = max(err1, max(err2, err3));

  annotation(
    experiment(StartTime = 0, StopTime = 80, Interval = 0.005, __Dymola_Algorithm = "Dassl"),
    __MWORKS(version = "26.3.0"));
end ThreeUavSimpleDiagonalRunner;
