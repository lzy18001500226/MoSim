within MoSimQuadrotorModel.Parameters;
record Sunray150VirtualPx4Classic
  "Virtual Sunray150 profile mirrored from Config/plant/sunray150_virtual_px4_classic_profile.json"

  parameter String profile_id = "sunray150_virtual_px4_classic_v1";
  parameter String motor_seed_source = "PX4_Gazebo_default_seed";
  parameter String geometry_source = "user-reviewed DAE/Blender assembly";
  parameter String inertia_source = "YunZong SDF seed";
  parameter String claim_boundary =
    "Virtual simulation seed only; not real-aircraft system identification truth";

  parameter Real gravity_mps2(unit = "m/s2") = 9.80665;
  parameter Real takeoff_mass_kg(unit = "kg") = 1.0;
  parameter Real rotor_mass_kg(unit = "kg") = 0.005;
  parameter Real mworks_quad_chassis_body_mass_kg(unit = "kg") = 0.980;
  parameter Real mworks_physical_wrench_body_mass_kg(unit = "kg") = 1.0;
  parameter Real ros1_nested_base_link_mass_kg(unit = "kg") = 0.953;
  parameter Real ros1_inline_base_link_mass_kg(unit = "kg") = 0.963;
  parameter Real ros1_flight_imu_mass_kg(unit = "kg") = 0.015;
  parameter Real ros1_nested_mid360_mass_kg(unit = "kg") = 0.010;
  parameter Real ros1_camera_sensor_mass_kg(unit = "kg") = 0.001;
  parameter Integer ros1_camera_sensor_count = 2;
  parameter Real body_inertia_diagonal_kg_m2[3](each unit = "kg.m2") =
    {0.0085, 0.0085, 0.012};
  parameter Real rotor_inertia_diagonal_kg_m2[3](each unit = "kg.m2") =
    {9.75e-7, 0.000173104, 0.000174004};

  parameter Real mworks_rotor_center_m[4, 3](each unit = "m") = [
    0.053745, -0.053740, -0.014052;
    0.053746,  0.053759, -0.014052;
   -0.053761,  0.053760, -0.014052;
   -0.053761, -0.053739, -0.014052];
  parameter Real gazebo_rotor_center_m[4, 3](each unit = "m") = [
    0.053745, -0.053740, -0.014052;
   -0.053761,  0.053760, -0.014052;
    0.053746,  0.053759, -0.014052;
   -0.053761, -0.053739, -0.014052];
  parameter Real mworks_spin_command_sign[4] = {1, -1, 1, -1};
  parameter Real mworks_yaw_direction[4] = {1, -1, 1, -1};
  parameter Real mid360_mount_pose_m_rpy[6] =
    {-0.000005, 0.032295, 0.050167, 0, 0, 4.712389};
  parameter Real mid360_inline_ray_sensor_pose_m_rpy[6] =
    {-0.000005, 0.032295, 0.150167, 0, 0, 4.712389};

  parameter Real motor_max_rotor_velocity_rad_s(unit = "rad/s") = 1100;
  parameter Real motor_constant_n_per_rad_s2(unit = "N/(rad/s)^2") = 5.84e-6;
  parameter Real moment_constant_ratio_m(unit = "m") = 0.06;
  parameter Real motor_time_constant_up_s(unit = "s") = 0.0125;
  parameter Real motor_time_constant_down_s(unit = "s") = 0.025;
  parameter Real rotor_drag_coefficient = 0.000175;
  parameter Real rolling_moment_coefficient = 1e-6;
  parameter Real rotor_velocity_slowdown_sim = 10;
  parameter Real mworks_visual_thrust_coefficient(unit = "N/(rad/s)^2") =
    0.000584;
  parameter Real mworks_hover_visual_rotor_speed_rad_s(unit = "rad/s") =
    64.7923778389665;
  parameter Real mworks_max_visual_rotor_speed_rad_s(unit = "rad/s") = 110;
  parameter Real mworks_hover_normalized_command = 0.589021616717877;
  parameter Real mworks_controller_hover_percentage = 0.37
    "Controller-side thrust-map calibration; not rotor-speed normalization";
  parameter Real px4ctrl_hov_percent = 0.37;
  parameter Boolean px4ctrl_thrust_estimate_enable = false
    "Keep nominal virtual px4ctrl mapping deterministic until a recorded hover recalibration";

  annotation(__MWORKS(version="26.3.0"));
end Sunray150VirtualPx4Classic;
