within MoSimQuadrotorModel;
package Parameters
  "Source-labeled Sunray150 virtual parameter records"

  extends Modelica.Icons.Package;

  record Sunray150ParameterProvenance
    "Backward-compatible provenance view of the active virtual profile"
    extends Sunray150VirtualPx4Classic;

    parameter String profile_json_path =
      "Config/plant/sunray150_virtual_px4_classic_profile.json";
    parameter String geometry_claim_boundary =
      "Rotor centers and MID360 pose come from the user-reviewed DAE/Blender assembly only; they do not identify dynamics.";
    parameter Real rotor_center_mworks_dronefixed[4, 3](each unit = "m") =
      mworks_rotor_center_m;
    parameter String non_geometry_seed_source =
      "YunZong SDF inertia seed plus PX4 Gazebo Classic Iris motor-model seed; neither is measured Sunray150 truth.";
    parameter String official_pid_source_anchor =
      "Models/MoSimQuadrotorModel/Vehicle/Blocks/package.mo, Vehicle.Blocks.Controller.Controller";
    parameter String official_pid_case_reference =
      "Tongyuan MWORKS competition quadrotor case: https://mohub.net/model/2355/summary";
    parameter String official_pid_provenance_boundary =
      "The embedded graphical Controller.Controller is retained as the supplied Official PID source. OfficialPIDRotorAdapter only maps its existing position/attitude and rotor-output boundary to the Sunray150 physical plant; it does not replace the PID core. The original source core has no velocity or acceleration feedforward port, so those held formal-runner signals remain intentionally unused by the Official PID baseline.";
    parameter Real mass_kg(unit = "kg") = takeoff_mass_kg;
    parameter Real sdf_motor_constant(unit = "N/(rad/s)^2") =
      motor_constant_n_per_rad_s2;
    parameter Real mworks_lift_coefficient(unit = "N/(rad/s)^2") =
      mworks_visual_thrust_coefficient;
    parameter Real yaw_moment_ratio_seed = moment_constant_ratio_m;
    parameter Real spin_command_sign[4] = mworks_spin_command_sign;
    parameter Real yaw_direction[4] = mworks_yaw_direction;
    parameter Real normalized_command_min = 0.0;
    parameter Real normalized_command_max = 1.0;
    parameter Real hover_normalized_command = mworks_hover_normalized_command;
    parameter String identification_status =
      "not_identified; replace only with a ULog/bench profile and its validation evidence";
    parameter String do_not_promote_boundary =
      "The active profile is a source-labeled virtual simulation seed, not identified Sunray150 real-aircraft truth.";
    parameter Boolean enable_rotor_gyro_default = false;
    parameter Boolean enable_body_drag_default = false;
    parameter Boolean enable_angular_damping_default = false;
    parameter Real rotor_polar_inertia_seed[4](each unit = "kg.m2") = {0, 0, 0, 0};
    parameter Real body_drag_coefficient_seed[3](each unit = "N.s/m") = {0, 0, 0};
    parameter Real angular_damping_coefficient_seed[3](each unit = "N.m.s/rad") = {0, 0, 0};
    annotation(__MWORKS(version="26.3.0"));
  end Sunray150ParameterProvenance;

  constant Real sunray150_virtual_px4_classic_mass_kg(unit = "kg") = 1.0
    "Static mirror of Sunray150VirtualPx4Classic.takeoff_mass_kg";
  constant Real sunray150_virtual_px4_classic_gravity_mps2(unit = "m/s2") = 9.80665
    "Static mirror of Sunray150VirtualPx4Classic.gravity_mps2";
  constant Real sunray150_virtual_px4_classic_visual_thrust_coefficient(unit = "N/(rad/s)^2") = 0.000584
    "Static mirror of Sunray150VirtualPx4Classic.mworks_visual_thrust_coefficient";
  constant Real sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s(unit = "rad/s") = 64.7923778389665
    "Static mirror of Sunray150VirtualPx4Classic.mworks_hover_visual_rotor_speed_rad_s";
  constant Real sunray150_virtual_px4_classic_max_visual_rotor_speed_rad_s(unit = "rad/s") = 110.0
    "Static mirror of Sunray150VirtualPx4Classic.mworks_max_visual_rotor_speed_rad_s";
  constant Real sunray150_virtual_px4_classic_px4ctrl_hover_percentage = 0.37
    "Static mirror of Sunray150VirtualPx4Classic.px4ctrl_hov_percent; runtime calibration, not a rotor-speed normalization";
  constant Real sunray150_virtual_px4_classic_mworks_controller_hover_percentage = 0.37
    "Static mirror of Sunray150VirtualPx4Classic.mworks_controller_hover_percentage";
  constant Real sunray150_virtual_px4_classic_ros1_nested_base_link_mass_kg(unit = "kg") = 0.953
    "ROS1 Gazebo Classic nested-MID360 base mass, including two 1 g camera sensor models in total-mass closure";
  constant Real sunray150_virtual_px4_classic_ros1_inline_base_link_mass_kg(unit = "kg") = 0.963
    "ROS1 Gazebo Classic inline-MID360 base mass, including two 1 g camera sensor models in total-mass closure";

  annotation(__MWORKS(version="26.3.0"));
end Parameters;
