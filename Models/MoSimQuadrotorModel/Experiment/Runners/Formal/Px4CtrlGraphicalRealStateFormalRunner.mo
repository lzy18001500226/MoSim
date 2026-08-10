within MoSimQuadrotorModel.Experiment.Runners.Formal;
model Px4CtrlGraphicalRealStateFormalRunner
  "Formal whole-aircraft closure using the graphical PX4CTRL and plant truth state"

  parameter Real controller_sample_period_s(unit = "s") = 0.01
    "Compatibility parameter; the graphical Sysblock carries the 0.01 s sample time";
  parameter Real quaternion_domain_margin(min = 0, max = 0.01) = 1e-7;
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_collective_thrust_n = 4
    * profile.mworks_visual_thrust_coefficient
    * profile.mworks_hover_visual_rotor_speed_rad_s ^ 2;
  parameter Real gust_force[3](each unit = "N") = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1;
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1};
  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;

  MoSimQuadrotorModel.Control.Implementations.Sysblocks.PX4CTRL_Original_OuterLoop_Graphical_Sysblock graphical_outer 
    annotation(
      Placement(transformation(origin = {-100, 75}, extent = {{-55, -55}, {55, 55}})),
      __MWORKS(SECInstance = true));
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator offline_inner_allocator(
    profile = profile,
    use_body_rate_mea = true) 
    annotation(Placement(transformation(origin = {55, 75}, extent = {{-45, -28}, {45, 28}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(
    profile = profile,
    rotor_effectiveness = rotor_effectiveness,
    gust_force = gust_force,
    gust_start_s = gust_start_s,
    gust_duration_s = gust_duration_s,
    mass_scale = mass_scale,
    inertia_scale = inertia_scale,
    fault_start_s = fault_start_s,
    fault_rotor_index = fault_rotor_index,
    fault_rotor_effectiveness = fault_rotor_effectiveness) 
    annotation(Placement(transformation(origin = {165, 5}, extent = {{-52, -75}, {52, 75}})));
  replaceable model Trajectory = MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath;
  Trajectory reference 
    annotation(Placement(transformation(origin = {-205, 75}, extent = {{-20, -15}, {20, 15}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_position_ref[3](
    each samplePeriod = controller_sample_period_s,
    each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_velocity_ref[3](
    each samplePeriod = controller_sample_period_s,
    each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_acceleration_ref[3](
    each samplePeriod = controller_sample_period_s,
    each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_position[3](
    each samplePeriod = controller_sample_period_s,
    each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_attitude[3](
    each samplePeriod = controller_sample_period_s,
    each y_start = 0);
  Modelica.Blocks.Sources.Constant ref_yaw_zero(k = 0) 
    annotation(Placement(transformation(extent = {{-15, -50}, {15, -10}})));
  Modelica.Blocks.Math.Gain graphical_output_capture[8](each k = 1);

  Real position_ref[3];
  Real velocity_ref[3];
  Real acceleration_ref[3];
  Real position[3];
  Real velocity_mea[3](each unit = "m/s");
  Real attitude[3](each unit = "rad");
  Real body_rate_mea[3](each unit = "rad/s");
  Real quat_xyzw[4];
  Real quat_wxyz[4];
  Real desired_acc[3](each unit = "m/s2");
  Real attitude_ref[3](each unit = "rad");
  Real collective_thrust_delta(unit = "N") annotation(Placement(transformation(extent={{-15,136},{15,176}})));
  Real rotor_command[4](each unit = "rad/s");
  Real position_error_norm annotation(Placement(transformation(extent={{-15,-72},{15,-32}})));
  Real attitude_mea_from_quat[3];
  Real quat_norm annotation(Placement(transformation(extent={{-15,-176},{15,-136}})));
  Real pitch_argument annotation(Placement(transformation(extent={{-15,32},{15,72}})));
  Real pitch_argument_safe annotation(Placement(transformation(extent={{-15,-20},{15,20}})));
  Real quaternion_norm_error annotation(Placement(transformation(extent={{-15,-228},{15,-188}})));
  Real quat_to_euler_error[3];

equation
  connect(reference.position_command, sampled_position_ref.u);
  connect(sampled_position_ref[1].y, graphical_outer.ref_px);
  connect(sampled_position_ref[2].y, graphical_outer.ref_py);
  connect(sampled_position_ref[3].y, graphical_outer.ref_pz);
  connect(reference.velocity_command, sampled_velocity_ref.u);
  connect(sampled_velocity_ref[1].y, graphical_outer.ref_vx);
  connect(sampled_velocity_ref[2].y, graphical_outer.ref_vy);
  connect(sampled_velocity_ref[3].y, graphical_outer.ref_vz);
  connect(reference.acceleration_command, sampled_acceleration_ref.u);
  connect(sampled_acceleration_ref[1].y, graphical_outer.ref_ax);
  connect(sampled_acceleration_ref[2].y, graphical_outer.ref_ay);
  connect(sampled_acceleration_ref[3].y, graphical_outer.ref_az);
  connect(ref_yaw_zero.y, graphical_outer.ref_yaw);

  connect(plant.position, sampled_position.u);
  connect(sampled_position[1].y, graphical_outer.px);
  connect(sampled_position[2].y, graphical_outer.py);
  connect(sampled_position[3].y, graphical_outer.pz);
  connect(plant.VelMea[1], graphical_outer.vx);
  connect(plant.VelMea[2], graphical_outer.vy);
  connect(plant.VelMea[3], graphical_outer.vz);

  quat_xyzw = plant.QuatMea;
  quat_wxyz = {quat_xyzw[4], quat_xyzw[1], quat_xyzw[2], quat_xyzw[3]};
  quat_norm = max(1e-12, sqrt(sum(quat_wxyz[i] ^ 2 for i in 1:4)));
  pitch_argument = 2 * (quat_wxyz[1] * quat_wxyz[3] + quat_wxyz[2] * quat_wxyz[4])
    / quat_norm ^ 2;
  pitch_argument_safe = min(1 - quaternion_domain_margin,
    max(-1 + quaternion_domain_margin, pitch_argument));
  attitude_mea_from_quat[1] = atan2(2 * (quat_wxyz[1] * quat_wxyz[2]
    - quat_wxyz[3] * quat_wxyz[4]), quat_wxyz[1] ^ 2 - quat_wxyz[2] ^ 2
    - quat_wxyz[3] ^ 2 + quat_wxyz[4] ^ 2);
  attitude_mea_from_quat[2] = if pitch_argument >= 1 then Modelica.Constants.pi / 2 
    else if pitch_argument <= -1 then -Modelica.Constants.pi / 2 
    else asin(pitch_argument_safe);
  attitude_mea_from_quat[3] = atan2(2 * (quat_wxyz[1] * quat_wxyz[4]
    - quat_wxyz[2] * quat_wxyz[3]), quat_wxyz[1] ^ 2 + quat_wxyz[2] ^ 2
    - quat_wxyz[3] ^ 2 - quat_wxyz[4] ^ 2);
  quaternion_norm_error = quat_norm - 1;
  sampled_attitude.u = attitude_mea_from_quat;
  connect(sampled_attitude[3].y, graphical_outer.yaw_mea);

  connect(graphical_outer.desired_acc_x, graphical_output_capture[1].u);
  connect(graphical_outer.desired_acc_y, graphical_output_capture[2].u);
  connect(graphical_outer.desired_acc_z, graphical_output_capture[3].u);
  connect(graphical_outer.roll_cmd, graphical_output_capture[4].u);
  connect(graphical_outer.pitch_cmd, graphical_output_capture[5].u);
  connect(graphical_outer.yaw_cmd, graphical_output_capture[6].u);
  connect(graphical_outer.collective_thrust_n, graphical_output_capture[7].u);
  connect(graphical_outer.normalized_thrust, graphical_output_capture[8].u);
  desired_acc = {graphical_output_capture[1].y, graphical_output_capture[2].y,
    graphical_output_capture[3].y};
  attitude_ref = {-graphical_output_capture[4].y, graphical_output_capture[5].y,
    graphical_output_capture[6].y};
  collective_thrust_delta = graphical_output_capture[7].y - hover_collective_thrust_n;
  connect(plant.BodyRateMea, offline_inner_allocator.body_rate_mea);
  offline_inner_allocator.attitude_ref = attitude_ref;
  offline_inner_allocator.attitude_mea = attitude_mea_from_quat;
  offline_inner_allocator.collective_thrust_delta = collective_thrust_delta;
  connect(offline_inner_allocator.rotor_command, plant.rotor_command);

  position_ref = reference.position_command;
  velocity_ref = reference.velocity_command;
  acceleration_ref = reference.acceleration_command;
  position = plant.position;
  velocity_mea = plant.VelMea;
  attitude = attitude_mea_from_quat;
  body_rate_mea = plant.BodyRateMea;
  rotor_command = plant.rotor_command;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);
  quat_to_euler_error = attitude_mea_from_quat - plant.attitude;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-250, -260}, {240, 150}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end Px4CtrlGraphicalRealStateFormalRunner;