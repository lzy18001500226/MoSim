within MoSimQuadrotorModel;
package Parameters
  "Sunray150 parameter provenance records; source labels only, not identified truth"

  extends Modelica.Icons.Package;

  record Sunray150ParameterProvenance
    "Current Sunray150 seed parameter provenance boundary"
    parameter String geometry_source =
      "user-reviewed DAE/Blender screw-pair assembly geometry";
    parameter String geometry_claim_boundary =
      "rotor centers are accepted assembly geometry only; they do not identify mass, inertia, thrust, yaw, lag, drag, damping, or gyro truth";
    parameter Real rotor_center_mworks_dronefixed[4, 3](each unit = "m") = [
      0.053745, -0.053740, -0.014052;
      0.053746,  0.053759, -0.014052;
     -0.053761,  0.053760, -0.014052;
     -0.053761, -0.053739, -0.014052]
      "source=user-reviewed DAE screw-pair fit, mapped to MWORKS Dronefixed1..4 order";
    parameter String rotor_center_manifest =
      "Results/unreal_scene_mapping/sunray150_dae_assembly_parameters_20260604.json";

    parameter String non_geometry_seed_source =
      "YunZong/Gazebo/Sunray SDF migration seeds; not ULog or bench identified";
    parameter Real mass_kg(unit = "kg") = 1.0
      "source=SDF_migration seed; not measured Sunray150 takeoff mass";
    parameter Real body_inertia_diagonal_kg_m2[3](each unit = "kg.m2") = {0.0085, 0.0085, 0.012}
      "source=SDF_migration seed for Ixx/Iyy/Izz; payload and battery sensitive";
    parameter Real sdf_motor_constant(unit = "N/(rad/s)^2") = 8.54858e-06
      "source=Sunray/Gazebo SDF motorConstant seed; not identified thrust curve";
    parameter Real rotor_velocity_slowdown_sim = 10
      "source=Sunray/Gazebo SDF visual rotor slowdown seed";
    parameter Real mworks_lift_coefficient(unit = "N/(rad/s)^2") = 0.000854858
      "source=SDF_migration seed; sdf_motor_constant scaled by rotor_velocity_slowdown_sim^2 for MWORKS visual rotor speed";
    parameter Real yaw_moment_ratio_seed = 0.06
      "source=Sunray/Gazebo SDF momentConstant ratio seed; not identified yaw torque coefficient";
    parameter Real motor_time_constant_up_s(unit = "s") = 0.0125
      "source=Sunray/Gazebo SDF timeConstantUp seed; not ESC/RPM bench identified";
    parameter Real motor_time_constant_down_s(unit = "s") = 0.025
      "source=Sunray/Gazebo SDF timeConstantDown seed; not ESC/RPM bench identified";
    parameter Real spin_command_sign[4] = {1, -1, 1, -1}
      "source=current MWORKS signed visual rotor convention; not PX4 allocation proof";
    parameter Real yaw_direction[4] = {1, -1, 1, -1}
      "source=Sunray SDF turningDirection mapped to MWORKS Dronefixed1..4 order; sign convention remains experimental";

    parameter Real normalized_command_min = 0.0
      "source=interface_seed; lower normalized actuator command bound";
    parameter Real normalized_command_max = 1.0
      "source=interface_seed; upper normalized actuator command bound";
    parameter Real hover_normalized_command = 0.5
      "source=interface_seed placeholder; not measured PWM/throttle/ESC/RPM evidence";

    parameter Boolean enable_rotor_gyro_default = false
      "source=018 static optional layer; default disabled";
    parameter Boolean enable_body_drag_default = false
      "source=018 static optional layer; default disabled";
    parameter Boolean enable_angular_damping_default = false
      "source=018 static optional layer; default disabled";
    parameter Real rotor_polar_inertia_seed[4](each unit = "kg.m2") = {0, 0, 0, 0}
      "source=zero_seed; optional rotor inertia placeholder, not identified";
    parameter Real body_drag_coefficient_seed[3](each unit = "N.s/m") = {0, 0, 0}
      "source=zero_seed; translational drag placeholder, not identified";
    parameter Real angular_damping_coefficient_seed[3](each unit = "N.m.s/rad") = {0, 0, 0}
      "source=zero_seed; angular damping placeholder, not identified";
    parameter Real gyro_axis_sign[4] = {1, -1, 1, -1}
      "source=sign_convention_seed; follows current MWORKS visual spin convention";
    parameter Real gyro_convention_sign = -1
      "source=interface_seed; body-rate cross rotor-angular-momentum convention seed";

    parameter String identification_status =
      "not_identified; retain source labels until PX4 ULog, bench, weighing, or validated system-identification evidence replaces seeds";
    parameter String do_not_promote_boundary =
      "RflySim/Gazebo/YunZong/SDF values are structure or seed references only, not Sunray150 truth";
  end Sunray150ParameterProvenance;
end Parameters;
