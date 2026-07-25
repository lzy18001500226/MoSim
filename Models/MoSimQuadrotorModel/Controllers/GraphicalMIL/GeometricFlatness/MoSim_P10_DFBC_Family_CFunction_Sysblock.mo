within MoSimQuadrotorModel.Controllers.GraphicalMIL.GeometricFlatness;
model MoSim_P10_DFBC_Family_CFunction_Sysblock
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left(controller_id_in, dt_in, position_x_in, position_y_in, position_z_in, velocity_x_in, velocity_y_in, velocity_z_in, attitude_w_in, attitude_x_in, attitude_y_in, attitude_z_in, angular_velocity_x_in, angular_velocity_y_in, angular_velocity_z_in, reference_position_x_in, reference_position_y_in, reference_position_z_in, reference_velocity_x_in, reference_velocity_y_in, reference_velocity_z_in, reference_acceleration_x_in, reference_acceleration_y_in, reference_acceleration_z_in, reference_jerk_x_in, reference_jerk_y_in, reference_jerk_z_in, reference_snap_x_in, reference_snap_y_in, reference_snap_z_in, reference_yaw_in, reference_yaw_rate_in, reference_yaw_acceleration_in, measurement_stamp_s_in, imu_attitude_w_in, imu_attitude_x_in, imu_attitude_y_in, imu_attitude_z_in, imu_angular_velocity_x_in, imu_angular_velocity_y_in, imu_angular_velocity_z_in, enable_in, reset_in, measurement_stamp_valid_in, enable_disturbance_observer_in, kp_x_in, kp_y_in, kp_z_in, kv_x_in, kv_y_in, kv_z_in, ki_x_in, ki_y_in, ki_z_in, smc_lambda_x_in, smc_lambda_y_in, smc_lambda_z_in, smc_eta_x_in, smc_eta_y_in, smc_eta_z_in, smc_phi_x_in, smc_phi_y_in, smc_phi_z_in, smc_surface_limit_x_in, smc_surface_limit_y_in, smc_surface_limit_z_in, indi_gain_x_in, indi_gain_y_in, indi_gain_z_in, indi_increment_limit_x_in, indi_increment_limit_y_in, indi_increment_limit_z_in, indi_measured_accel_limit_x_in, indi_measured_accel_limit_y_in, indi_measured_accel_limit_z_in, indi_accel_lpf_alpha_in, nmpc_horizon_s_in, nmpc_position_weight_x_in, nmpc_position_weight_y_in, nmpc_position_weight_z_in, nmpc_velocity_weight_x_in, nmpc_velocity_weight_y_in, nmpc_velocity_weight_z_in, nmpc_control_weight_x_in, nmpc_control_weight_y_in, nmpc_control_weight_z_in, nmpc_accel_limit_x_in, nmpc_accel_limit_y_in, nmpc_accel_limit_z_in, nmpc_increment_limit_x_in, nmpc_increment_limit_y_in, nmpc_increment_limit_z_in, high_order_body_rate_limit_x_in, high_order_body_rate_limit_y_in
, high_order_body_rate_limit_z_in, high_order_body_accel_limit_x_in, high_order_body_accel_limit_y_in, high_order_body_accel_limit_z_in, smooth_feedback_gain_x_in, smooth_feedback_gain_y_in, smooth_feedback_gain_z_in, smooth_feedback_bound_x_in, smooth_feedback_bound_y_in, smooth_feedback_bound_z_in, disturbance_observer_gain_x_in, disturbance_observer_gain_y_in, disturbance_observer_gain_z_in, disturbance_compensation_limit_x_in, disturbance_compensation_limit_y_in, disturbance_compensation_limit_z_in, l1_model_decay_in, l1_filter_T_in, l1_gain_x_in, l1_gain_y_in, l1_gain_z_in, l1_comp_limit_x_in, l1_comp_limit_y_in, l1_comp_limit_z_in, drag_feedforward_gain_x_in, drag_feedforward_gain_y_in, drag_feedforward_gain_z_in, safety_accel_limit_x_in, safety_accel_limit_y_in, safety_accel_limit_z_in, fault_rotor_efficiency_1_in, fault_rotor_efficiency_2_in, fault_rotor_efficiency_3_in, fault_rotor_efficiency_4_in, fault_allocation_blend_in, fault_min_efficiency_in, fault_thrust_comp_limit_in, integral_limit_x_in, integral_limit_y_in, integral_limit_z_in, mass_in, gravity_in, hover_percentage_in, min_normalized_thrust_in, max_normalized_thrust_in, tilt_limit_rad_in), Right(desired_attitude_w_out, desired_attitude_x_out, desired_attitude_y_out, desired_attitude_z_out, normalized_thrust_out, collective_thrust_N_out, position_error_x_out, position_error_y_out, position_error_z_out, velocity_error_x_out, velocity_error_y_out, velocity_error_z_out, sliding_surface_x_out, sliding_surface_y_out, sliding_surface_z_out, desired_acceleration_x_out, desired_acceleration_y_out, desired_acceleration_z_out, desired_body_rate_x_out, desired_body_rate_y_out, desired_body_rate_z_out, desired_body_acceleration_x_out, desired_body_acceleration_y_out, desired_body_acceleration_z_out, disturbance_estimate_x_out, disturbance_estimate_y_out, disturbance_estimate_z_out, desired_force_N_x_out, desired_force_N_y_out, desired_force_N_z_out, saturated_out, status_code_out)),BlockSystem(blockKind=BlockKind
.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\p10_mworks_gap_closeout_20260718\\dfbc_family\\codegen"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{-620,-1728.00},{620,1728.00}},grid={2,2})));

  CFunction cFunction
    annotation (Placement(transformation(origin={0,0}, extent={{-80,-1668.00},{80,1668.00}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport controller_id_in
    annotation (Placement(transformation(origin={-500,1668.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport dt_in
    annotation (Placement(transformation(origin={-500,1644.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_x_in
    annotation (Placement(transformation(origin={-500,1620.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_y_in
    annotation (Placement(transformation(origin={-500,1596.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_z_in
    annotation (Placement(transformation(origin={-500,1572.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_x_in
    annotation (Placement(transformation(origin={-500,1548.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_y_in
    annotation (Placement(transformation(origin={-500,1524.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_z_in
    annotation (Placement(transformation(origin={-500,1500.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_w_in
    annotation (Placement(transformation(origin={-500,1476.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_x_in
    annotation (Placement(transformation(origin={-500,1452.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_y_in
    annotation (Placement(transformation(origin={-500,1428.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_z_in
    annotation (Placement(transformation(origin={-500,1404.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport angular_velocity_x_in
    annotation (Placement(transformation(origin={-500,1380.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport angular_velocity_y_in
    annotation (Placement(transformation(origin={-500,1356.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport angular_velocity_z_in
    annotation (Placement(transformation(origin={-500,1332.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x_in
    annotation (Placement(transformation(origin={-500,1308.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y_in
    annotation (Placement(transformation(origin={-500,1284.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z_in
    annotation (Placement(transformation(origin={-500,1260.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x_in
    annotation (Placement(transformation(origin={-500,1236.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y_in
    annotation (Placement(transformation(origin={-500,1212.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z_in
    annotation (Placement(transformation(origin={-500,1188.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x_in
    annotation (Placement(transformation(origin={-500,1164.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y_in
    annotation (Placement(transformation(origin={-500,1140.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z_in
    annotation (Placement(transformation(origin={-500,1116.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_jerk_x_in
    annotation (Placement(transformation(origin={-500,1092.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_jerk_y_in
    annotation (Placement(transformation(origin={-500,1068.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_jerk_z_in
    annotation (Placement(transformation(origin={-500,1044.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_snap_x_in
    annotation (Placement(transformation(origin={-500,1020.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_snap_y_in
    annotation (Placement(transformation(origin={-500,996.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_snap_z_in
    annotation (Placement(transformation(origin={-500,972.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_yaw_in
    annotation (Placement(transformation(origin={-500,948.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_yaw_rate_in
    annotation (Placement(transformation(origin={-500,924.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_yaw_acceleration_in
    annotation (Placement(transformation(origin={-500,900.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport measurement_stamp_s_in
    annotation (Placement(transformation(origin={-500,876.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_attitude_w_in
    annotation (Placement(transformation(origin={-500,852.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_attitude_x_in
    annotation (Placement(transformation(origin={-500,828.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_attitude_y_in
    annotation (Placement(transformation(origin={-500,804.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_attitude_z_in
    annotation (Placement(transformation(origin={-500,780.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_angular_velocity_x_in
    annotation (Placement(transformation(origin={-500,756.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_angular_velocity_y_in
    annotation (Placement(transformation(origin={-500,732.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_angular_velocity_z_in
    annotation (Placement(transformation(origin={-500,708.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_in
    annotation (Placement(transformation(origin={-500,684.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reset_in
    annotation (Placement(transformation(origin={-500,660.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport measurement_stamp_valid_in
    annotation (Placement(transformation(origin={-500,636.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_disturbance_observer_in
    annotation (Placement(transformation(origin={-500,612.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport kp_x_in
    annotation (Placement(transformation(origin={-500,588.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport kp_y_in
    annotation (Placement(transformation(origin={-500,564.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport kp_z_in
    annotation (Placement(transformation(origin={-500,540.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport kv_x_in
    annotation (Placement(transformation(origin={-500,516.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport kv_y_in
    annotation (Placement(transformation(origin={-500,492.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport kv_z_in
    annotation (Placement(transformation(origin={-500,468.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ki_x_in
    annotation (Placement(transformation(origin={-500,444.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ki_y_in
    annotation (Placement(transformation(origin={-500,420.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ki_z_in
    annotation (Placement(transformation(origin={-500,396.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_lambda_x_in
    annotation (Placement(transformation(origin={-500,372.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_lambda_y_in
    annotation (Placement(transformation(origin={-500,348.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_lambda_z_in
    annotation (Placement(transformation(origin={-500,324.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_eta_x_in
    annotation (Placement(transformation(origin={-500,300.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_eta_y_in
    annotation (Placement(transformation(origin={-500,276.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_eta_z_in
    annotation (Placement(transformation(origin={-500,252.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_phi_x_in
    annotation (Placement(transformation(origin={-500,228.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_phi_y_in
    annotation (Placement(transformation(origin={-500,204.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_phi_z_in
    annotation (Placement(transformation(origin={-500,180.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_surface_limit_x_in
    annotation (Placement(transformation(origin={-500,156.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_surface_limit_y_in
    annotation (Placement(transformation(origin={-500,132.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smc_surface_limit_z_in
    annotation (Placement(transformation(origin={-500,108.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport indi_gain_x_in
    annotation (Placement(transformation(origin={-500,84.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport indi_gain_y_in
    annotation (Placement(transformation(origin={-500,60.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport indi_gain_z_in
    annotation (Placement(transformation(origin={-500,36.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport indi_increment_limit_x_in
    annotation (Placement(transformation(origin={-500,12.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport indi_increment_limit_y_in
    annotation (Placement(transformation(origin={-500,-12.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport indi_increment_limit_z_in
    annotation (Placement(transformation(origin={-500,-36.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport indi_measured_accel_limit_x_in
    annotation (Placement(transformation(origin={-500,-60.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport indi_measured_accel_limit_y_in
    annotation (Placement(transformation(origin={-500,-84.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport indi_measured_accel_limit_z_in
    annotation (Placement(transformation(origin={-500,-108.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport indi_accel_lpf_alpha_in
    annotation (Placement(transformation(origin={-500,-132.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_horizon_s_in
    annotation (Placement(transformation(origin={-500,-156.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_position_weight_x_in
    annotation (Placement(transformation(origin={-500,-180.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_position_weight_y_in
    annotation (Placement(transformation(origin={-500,-204.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_position_weight_z_in
    annotation (Placement(transformation(origin={-500,-228.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_velocity_weight_x_in
    annotation (Placement(transformation(origin={-500,-252.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_velocity_weight_y_in
    annotation (Placement(transformation(origin={-500,-276.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_velocity_weight_z_in
    annotation (Placement(transformation(origin={-500,-300.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_control_weight_x_in
    annotation (Placement(transformation(origin={-500,-324.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_control_weight_y_in
    annotation (Placement(transformation(origin={-500,-348.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_control_weight_z_in
    annotation (Placement(transformation(origin={-500,-372.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_accel_limit_x_in
    annotation (Placement(transformation(origin={-500,-396.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_accel_limit_y_in
    annotation (Placement(transformation(origin={-500,-420.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_accel_limit_z_in
    annotation (Placement(transformation(origin={-500,-444.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_increment_limit_x_in
    annotation (Placement(transformation(origin={-500,-468.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_increment_limit_y_in
    annotation (Placement(transformation(origin={-500,-492.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport nmpc_increment_limit_z_in
    annotation (Placement(transformation(origin={-500,-516.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport high_order_body_rate_limit_x_in
    annotation (Placement(transformation(origin={-500,-540.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport high_order_body_rate_limit_y_in
    annotation (Placement(transformation(origin={-500,-564.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport high_order_body_rate_limit_z_in
    annotation (Placement(transformation(origin={-500,-588.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport high_order_body_accel_limit_x_in
    annotation (Placement(transformation(origin={-500,-612.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport high_order_body_accel_limit_y_in
    annotation (Placement(transformation(origin={-500,-636.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport high_order_body_accel_limit_z_in
    annotation (Placement(transformation(origin={-500,-660.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smooth_feedback_gain_x_in
    annotation (Placement(transformation(origin={-500,-684.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smooth_feedback_gain_y_in
    annotation (Placement(transformation(origin={-500,-708.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smooth_feedback_gain_z_in
    annotation (Placement(transformation(origin={-500,-732.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smooth_feedback_bound_x_in
    annotation (Placement(transformation(origin={-500,-756.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smooth_feedback_bound_y_in
    annotation (Placement(transformation(origin={-500,-780.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport smooth_feedback_bound_z_in
    annotation (Placement(transformation(origin={-500,-804.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport disturbance_observer_gain_x_in
    annotation (Placement(transformation(origin={-500,-828.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport disturbance_observer_gain_y_in
    annotation (Placement(transformation(origin={-500,-852.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport disturbance_observer_gain_z_in
    annotation (Placement(transformation(origin={-500,-876.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport disturbance_compensation_limit_x_in
    annotation (Placement(transformation(origin={-500,-900.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport disturbance_compensation_limit_y_in
    annotation (Placement(transformation(origin={-500,-924.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport disturbance_compensation_limit_z_in
    annotation (Placement(transformation(origin={-500,-948.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport l1_model_decay_in
    annotation (Placement(transformation(origin={-500,-972.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport l1_filter_T_in
    annotation (Placement(transformation(origin={-500,-996.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport l1_gain_x_in
    annotation (Placement(transformation(origin={-500,-1020.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport l1_gain_y_in
    annotation (Placement(transformation(origin={-500,-1044.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport l1_gain_z_in
    annotation (Placement(transformation(origin={-500,-1068.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport l1_comp_limit_x_in
    annotation (Placement(transformation(origin={-500,-1092.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport l1_comp_limit_y_in
    annotation (Placement(transformation(origin={-500,-1116.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport l1_comp_limit_z_in
    annotation (Placement(transformation(origin={-500,-1140.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport drag_feedforward_gain_x_in
    annotation (Placement(transformation(origin={-500,-1164.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport drag_feedforward_gain_y_in
    annotation (Placement(transformation(origin={-500,-1188.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport drag_feedforward_gain_z_in
    annotation (Placement(transformation(origin={-500,-1212.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport safety_accel_limit_x_in
    annotation (Placement(transformation(origin={-500,-1236.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport safety_accel_limit_y_in
    annotation (Placement(transformation(origin={-500,-1260.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport safety_accel_limit_z_in
    annotation (Placement(transformation(origin={-500,-1284.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fault_rotor_efficiency_1_in
    annotation (Placement(transformation(origin={-500,-1308.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fault_rotor_efficiency_2_in
    annotation (Placement(transformation(origin={-500,-1332.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fault_rotor_efficiency_3_in
    annotation (Placement(transformation(origin={-500,-1356.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fault_rotor_efficiency_4_in
    annotation (Placement(transformation(origin={-500,-1380.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fault_allocation_blend_in
    annotation (Placement(transformation(origin={-500,-1404.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fault_min_efficiency_in
    annotation (Placement(transformation(origin={-500,-1428.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fault_thrust_comp_limit_in
    annotation (Placement(transformation(origin={-500,-1452.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport integral_limit_x_in
    annotation (Placement(transformation(origin={-500,-1476.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport integral_limit_y_in
    annotation (Placement(transformation(origin={-500,-1500.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport integral_limit_z_in
    annotation (Placement(transformation(origin={-500,-1524.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mass_in
    annotation (Placement(transformation(origin={-500,-1548.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport gravity_in
    annotation (Placement(transformation(origin={-500,-1572.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport hover_percentage_in
    annotation (Placement(transformation(origin={-500,-1596.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport min_normalized_thrust_in
    annotation (Placement(transformation(origin={-500,-1620.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport max_normalized_thrust_in
    annotation (Placement(transformation(origin={-500,-1644.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport tilt_limit_rad_in
    annotation (Placement(transformation(origin={-500,-1668.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_w_out
    annotation (Placement(transformation(origin={500,1668.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_x_out
    annotation (Placement(transformation(origin={500,1560.39},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_y_out
    annotation (Placement(transformation(origin={500,1452.77},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_z_out
    annotation (Placement(transformation(origin={500,1345.16},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out
    annotation (Placement(transformation(origin={500,1237.55},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_N_out
    annotation (Placement(transformation(origin={500,1129.94},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport position_error_x_out
    annotation (Placement(transformation(origin={500,1022.32},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport position_error_y_out
    annotation (Placement(transformation(origin={500,914.71},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport position_error_z_out
    annotation (Placement(transformation(origin={500,807.10},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_x_out
    annotation (Placement(transformation(origin={500,699.48},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_y_out
    annotation (Placement(transformation(origin={500,591.87},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_z_out
    annotation (Placement(transformation(origin={500,484.26},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_x_out
    annotation (Placement(transformation(origin={500,376.65},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_y_out
    annotation (Placement(transformation(origin={500,269.03},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_z_out
    annotation (Placement(transformation(origin={500,161.42},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out
    annotation (Placement(transformation(origin={500,53.81},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out
    annotation (Placement(transformation(origin={500,-53.81},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out
    annotation (Placement(transformation(origin={500,-161.42},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_body_rate_x_out
    annotation (Placement(transformation(origin={500,-269.03},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_body_rate_y_out
    annotation (Placement(transformation(origin={500,-376.65},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_body_rate_z_out
    annotation (Placement(transformation(origin={500,-484.26},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_body_acceleration_x_out
    annotation (Placement(transformation(origin={500,-591.87},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_body_acceleration_y_out
    annotation (Placement(transformation(origin={500,-699.48},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_body_acceleration_z_out
    annotation (Placement(transformation(origin={500,-807.10},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport disturbance_estimate_x_out
    annotation (Placement(transformation(origin={500,-914.71},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport disturbance_estimate_y_out
    annotation (Placement(transformation(origin={500,-1022.32},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport disturbance_estimate_z_out
    annotation (Placement(transformation(origin={500,-1129.94},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_force_N_x_out
    annotation (Placement(transformation(origin={500,-1237.55},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_force_N_y_out
    annotation (Placement(transformation(origin={500,-1345.16},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_force_N_z_out
    annotation (Placement(transformation(origin={500,-1452.77},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport saturated_out
    annotation (Placement(transformation(origin={500,-1560.39},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport status_code_out
    annotation (Placement(transformation(origin={500,-1668.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left(controller_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, attitude_w, attitude_x, attitude_y, attitude_z, angular_velocity_x, angular_velocity_y, angular_velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_jerk_x, reference_jerk_y, reference_jerk_z, reference_snap_x, reference_snap_y, reference_snap_z, reference_yaw, reference_yaw_rate, reference_yaw_acceleration, measurement_stamp_s, imu_attitude_w, imu_attitude_x, imu_attitude_y, imu_attitude_z, imu_angular_velocity_x, imu_angular_velocity_y, imu_angular_velocity_z, enable, reset, measurement_stamp_valid, enable_disturbance_observer, kp_x, kp_y, kp_z, kv_x, kv_y, kv_z, ki_x, ki_y, ki_z, smc_lambda_x, smc_lambda_y, smc_lambda_z, smc_eta_x, smc_eta_y, smc_eta_z, smc_phi_x, smc_phi_y, smc_phi_z, smc_surface_limit_x, smc_surface_limit_y, smc_surface_limit_z, indi_gain_x, indi_gain_y, indi_gain_z, indi_increment_limit_x, indi_increment_limit_y, indi_increment_limit_z, indi_measured_accel_limit_x, indi_measured_accel_limit_y, indi_measured_accel_limit_z, indi_accel_lpf_alpha, nmpc_horizon_s, nmpc_position_weight_x, nmpc_position_weight_y, nmpc_position_weight_z, nmpc_velocity_weight_x, nmpc_velocity_weight_y, nmpc_velocity_weight_z, nmpc_control_weight_x, nmpc_control_weight_y, nmpc_control_weight_z, nmpc_accel_limit_x, nmpc_accel_limit_y, nmpc_accel_limit_z, nmpc_increment_limit_x, nmpc_increment_limit_y, nmpc_increment_limit_z, high_order_body_rate_limit_x, high_order_body_rate_limit_y, high_order_body_rate_limit_z, high_order_body_accel_limit_x, high_order_body_accel_limit_y, high_order_body_accel_limit_z, smooth_feedback_gain_x, smooth_feedback_gain_y, smooth_feedback_gain_z, smooth_feedback_bound_x, smooth_feedback_bound_y, smooth_feedback_bound_z, disturbance_observer_gain_x
, disturbance_observer_gain_y, disturbance_observer_gain_z, disturbance_compensation_limit_x, disturbance_compensation_limit_y, disturbance_compensation_limit_z, l1_model_decay, l1_filter_T, l1_gain_x, l1_gain_y, l1_gain_z, l1_comp_limit_x, l1_comp_limit_y, l1_comp_limit_z, drag_feedforward_gain_x, drag_feedforward_gain_y, drag_feedforward_gain_z, safety_accel_limit_x, safety_accel_limit_y, safety_accel_limit_z, fault_rotor_efficiency_1, fault_rotor_efficiency_2, fault_rotor_efficiency_3, fault_rotor_efficiency_4, fault_allocation_blend, fault_min_efficiency, fault_thrust_comp_limit, integral_limit_x, integral_limit_y, integral_limit_z, mass, gravity, hover_percentage, min_normalized_thrust, max_normalized_thrust, tilt_limit_rad), Right(desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, normalized_thrust, collective_thrust_N, position_error_x, position_error_y, position_error_z, velocity_error_x, velocity_error_y, velocity_error_z, sliding_surface_x, sliding_surface_y, sliding_surface_z, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, desired_body_rate_x, desired_body_rate_y, desired_body_rate_z, desired_body_acceleration_x, desired_body_acceleration_y, desired_body_acceleration_z, disturbance_estimate_x, disturbance_estimate_y, disturbance_estimate_z, desired_force_N_x, desired_force_N_y, desired_force_N_z, saturated, status_code)),PortLabels(labelType="CustomType",labels(label(text="controller_id",instance="controller_id"),label(text="dt",instance="dt"),label(text="position_x",instance="position_x"),label(text="position_y",instance="position_y"),label(text="position_z",instance="position_z"),label(text="velocity_x",instance="velocity_x"),label(text="velocity_y",instance="velocity_y"),label(text="velocity_z",instance="velocity_z"),label(text="attitude_w",instance="attitude_w"),label(text="attitude_x",instance="attitude_x"),label(text="attitude_y",instance="attitude_y"),label(text="attitude_z",instance="attitude_z"
),label(text="angular_velocity_x",instance="angular_velocity_x"),label(text="angular_velocity_y",instance="angular_velocity_y"),label(text="angular_velocity_z",instance="angular_velocity_z"),label(text="reference_position_x",instance="reference_position_x"),label(text="reference_position_y",instance="reference_position_y"),label(text="reference_position_z",instance="reference_position_z"),label(text="reference_velocity_x",instance="reference_velocity_x"),label(text="reference_velocity_y",instance="reference_velocity_y"),label(text="reference_velocity_z",instance="reference_velocity_z"),label(text="reference_acceleration_x",instance="reference_acceleration_x"),label(text="reference_acceleration_y",instance="reference_acceleration_y"),label(text="reference_acceleration_z",instance="reference_acceleration_z"),label(text="reference_jerk_x",instance="reference_jerk_x"),label(text="reference_jerk_y",instance="reference_jerk_y"),label(text="reference_jerk_z",instance="reference_jerk_z"),label(text="reference_snap_x",instance="reference_snap_x"),label(text="reference_snap_y",instance="reference_snap_y"),label(text="reference_snap_z",instance="reference_snap_z"),label(text="reference_yaw",instance="reference_yaw"),label(text="reference_yaw_rate",instance="reference_yaw_rate"),label(text="reference_yaw_acceleration",instance="reference_yaw_acceleration"),label(text="measurement_stamp_s",instance="measurement_stamp_s"),label(text="imu_attitude_w",instance="imu_attitude_w"),label(text="imu_attitude_x",instance="imu_attitude_x"),label(text="imu_attitude_y",instance="imu_attitude_y"),label(text="imu_attitude_z",instance="imu_attitude_z"),label(text="imu_angular_velocity_x",instance="imu_angular_velocity_x"),label(text="imu_angular_velocity_y",instance="imu_angular_velocity_y"),label(text="imu_angular_velocity_z",instance="imu_angular_velocity_z"),label(text="enable",instance="enable"),label(text="reset",instance="reset"),label(text="measurement_stamp_valid",instance="measurement_stamp_valid"
),label(text="enable_disturbance_observer",instance="enable_disturbance_observer"),label(text="kp_x",instance="kp_x"),label(text="kp_y",instance="kp_y"),label(text="kp_z",instance="kp_z"),label(text="kv_x",instance="kv_x"),label(text="kv_y",instance="kv_y"),label(text="kv_z",instance="kv_z"),label(text="ki_x",instance="ki_x"),label(text="ki_y",instance="ki_y"),label(text="ki_z",instance="ki_z"),label(text="smc_lambda_x",instance="smc_lambda_x"),label(text="smc_lambda_y",instance="smc_lambda_y"),label(text="smc_lambda_z",instance="smc_lambda_z"),label(text="smc_eta_x",instance="smc_eta_x"),label(text="smc_eta_y",instance="smc_eta_y"),label(text="smc_eta_z",instance="smc_eta_z"),label(text="smc_phi_x",instance="smc_phi_x"),label(text="smc_phi_y",instance="smc_phi_y"),label(text="smc_phi_z",instance="smc_phi_z"),label(text="smc_surface_limit_x",instance="smc_surface_limit_x"),label(text="smc_surface_limit_y",instance="smc_surface_limit_y"),label(text="smc_surface_limit_z",instance="smc_surface_limit_z"),label(text="indi_gain_x",instance="indi_gain_x"),label(text="indi_gain_y",instance="indi_gain_y"),label(text="indi_gain_z",instance="indi_gain_z"),label(text="indi_increment_limit_x",instance="indi_increment_limit_x"),label(text="indi_increment_limit_y",instance="indi_increment_limit_y"),label(text="indi_increment_limit_z",instance="indi_increment_limit_z"),label(text="indi_measured_accel_limit_x",instance="indi_measured_accel_limit_x"),label(text="indi_measured_accel_limit_y",instance="indi_measured_accel_limit_y"),label(text="indi_measured_accel_limit_z",instance="indi_measured_accel_limit_z"),label(text="indi_accel_lpf_alpha",instance="indi_accel_lpf_alpha"),label(text="nmpc_horizon_s",instance="nmpc_horizon_s"),label(text="nmpc_position_weight_x",instance="nmpc_position_weight_x"),label(text="nmpc_position_weight_y",instance="nmpc_position_weight_y"),label(text="nmpc_position_weight_z",instance="nmpc_position_weight_z"),label(text="nmpc_velocity_weight_x",instance=
"nmpc_velocity_weight_x"),label(text="nmpc_velocity_weight_y",instance="nmpc_velocity_weight_y"),label(text="nmpc_velocity_weight_z",instance="nmpc_velocity_weight_z"),label(text="nmpc_control_weight_x",instance="nmpc_control_weight_x"),label(text="nmpc_control_weight_y",instance="nmpc_control_weight_y"),label(text="nmpc_control_weight_z",instance="nmpc_control_weight_z"),label(text="nmpc_accel_limit_x",instance="nmpc_accel_limit_x"),label(text="nmpc_accel_limit_y",instance="nmpc_accel_limit_y"),label(text="nmpc_accel_limit_z",instance="nmpc_accel_limit_z"),label(text="nmpc_increment_limit_x",instance="nmpc_increment_limit_x"),label(text="nmpc_increment_limit_y",instance="nmpc_increment_limit_y"),label(text="nmpc_increment_limit_z",instance="nmpc_increment_limit_z"),label(text="high_order_body_rate_limit_x",instance="high_order_body_rate_limit_x"),label(text="high_order_body_rate_limit_y",instance="high_order_body_rate_limit_y"),label(text="high_order_body_rate_limit_z",instance="high_order_body_rate_limit_z"),label(text="high_order_body_accel_limit_x",instance="high_order_body_accel_limit_x"),label(text="high_order_body_accel_limit_y",instance="high_order_body_accel_limit_y"),label(text="high_order_body_accel_limit_z",instance="high_order_body_accel_limit_z"),label(text="smooth_feedback_gain_x",instance="smooth_feedback_gain_x"),label(text="smooth_feedback_gain_y",instance="smooth_feedback_gain_y"),label(text="smooth_feedback_gain_z",instance="smooth_feedback_gain_z"),label(text="smooth_feedback_bound_x",instance="smooth_feedback_bound_x"),label(text="smooth_feedback_bound_y",instance="smooth_feedback_bound_y"),label(text="smooth_feedback_bound_z",instance="smooth_feedback_bound_z"),label(text="disturbance_observer_gain_x",instance="disturbance_observer_gain_x"),label(text="disturbance_observer_gain_y",instance="disturbance_observer_gain_y"),label(text="disturbance_observer_gain_z",instance="disturbance_observer_gain_z"),label(text="disturbance_compensation_limit_x"
,instance="disturbance_compensation_limit_x"),label(text="disturbance_compensation_limit_y",instance="disturbance_compensation_limit_y"),label(text="disturbance_compensation_limit_z",instance="disturbance_compensation_limit_z"),label(text="l1_model_decay",instance="l1_model_decay"),label(text="l1_filter_T",instance="l1_filter_T"),label(text="l1_gain_x",instance="l1_gain_x"),label(text="l1_gain_y",instance="l1_gain_y"),label(text="l1_gain_z",instance="l1_gain_z"),label(text="l1_comp_limit_x",instance="l1_comp_limit_x"),label(text="l1_comp_limit_y",instance="l1_comp_limit_y"),label(text="l1_comp_limit_z",instance="l1_comp_limit_z"),label(text="drag_feedforward_gain_x",instance="drag_feedforward_gain_x"),label(text="drag_feedforward_gain_y",instance="drag_feedforward_gain_y"),label(text="drag_feedforward_gain_z",instance="drag_feedforward_gain_z"),label(text="safety_accel_limit_x",instance="safety_accel_limit_x"),label(text="safety_accel_limit_y",instance="safety_accel_limit_y"),label(text="safety_accel_limit_z",instance="safety_accel_limit_z"),label(text="fault_rotor_efficiency_1",instance="fault_rotor_efficiency_1"),label(text="fault_rotor_efficiency_2",instance="fault_rotor_efficiency_2"),label(text="fault_rotor_efficiency_3",instance="fault_rotor_efficiency_3"),label(text="fault_rotor_efficiency_4",instance="fault_rotor_efficiency_4"),label(text="fault_allocation_blend",instance="fault_allocation_blend"),label(text="fault_min_efficiency",instance="fault_min_efficiency"),label(text="fault_thrust_comp_limit",instance="fault_thrust_comp_limit"),label(text="integral_limit_x",instance="integral_limit_x"),label(text="integral_limit_y",instance="integral_limit_y"),label(text="integral_limit_z",instance="integral_limit_z"),label(text="mass",instance="mass"),label(text="gravity",instance="gravity"),label(text="hover_percentage",instance="hover_percentage"),label(text="min_normalized_thrust",instance="min_normalized_thrust"),label(text="max_normalized_thrust",instance="max_normalized_thrust"
),label(text="tilt_limit_rad",instance="tilt_limit_rad"),label(text="desired_attitude_w",instance="desired_attitude_w"),label(text="desired_attitude_x",instance="desired_attitude_x"),label(text="desired_attitude_y",instance="desired_attitude_y"),label(text="desired_attitude_z",instance="desired_attitude_z"),label(text="normalized_thrust",instance="normalized_thrust"),label(text="collective_thrust_N",instance="collective_thrust_N"),label(text="position_error_x",instance="position_error_x"),label(text="position_error_y",instance="position_error_y"),label(text="position_error_z",instance="position_error_z"),label(text="velocity_error_x",instance="velocity_error_x"),label(text="velocity_error_y",instance="velocity_error_y"),label(text="velocity_error_z",instance="velocity_error_z"),label(text="sliding_surface_x",instance="sliding_surface_x"),label(text="sliding_surface_y",instance="sliding_surface_y"),label(text="sliding_surface_z",instance="sliding_surface_z"),label(text="desired_acceleration_x",instance="desired_acceleration_x"),label(text="desired_acceleration_y",instance="desired_acceleration_y"),label(text="desired_acceleration_z",instance="desired_acceleration_z"),label(text="desired_body_rate_x",instance="desired_body_rate_x"),label(text="desired_body_rate_y",instance="desired_body_rate_y"),label(text="desired_body_rate_z",instance="desired_body_rate_z"),label(text="desired_body_acceleration_x",instance="desired_body_acceleration_x"),label(text="desired_body_acceleration_y",instance="desired_body_acceleration_y"),label(text="desired_body_acceleration_z",instance="desired_body_acceleration_z"),label(text="disturbance_estimate_x",instance="disturbance_estimate_x"),label(text="disturbance_estimate_y",instance="disturbance_estimate_y"),label(text="disturbance_estimate_z",instance="disturbance_estimate_z"),label(text="desired_force_N_x",instance="desired_force_N_x"),label(text="desired_force_N_y",instance="desired_force_N_y"),label(text="desired_force_N_z",instance="desired_force_N_z"
),label(text="saturated",instance="saturated"),label(text="status_code",instance="status_code"))),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
      Icon(coordinateSystem(extent={{-200,-100},{200,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2}),graphics={Rectangle(origin={0,0},fillColor={255,255,255},fillPattern=FillPattern.Solid,extent={{-200,100},{200,-100}}),Text(origin={0,0},extent={{-100,20},{100,-20}},textString="C",verticalAlignment=TextAlignment.VCenter),Text(origin={0,-120},lineColor={0,0,0},extent={{-150,20},{150,-20}},textString="%name",fontSize=14,textColor={0,0,0},verticalAlignment=TextAlignment.Top)}),
      Diagram(coordinateSystem(extent={{-100,-100},{100,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2})));

    function func_CFunction
      input SysplorerEmbeddedCoder.Types.Auto controller_id annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto dt annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto position_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto position_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto position_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto velocity_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto velocity_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto velocity_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto attitude_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto attitude_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto attitude_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto attitude_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto angular_velocity_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto angular_velocity_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto angular_velocity_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_position_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_position_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_position_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_velocity_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_velocity_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_velocity_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_jerk_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_jerk_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_jerk_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_snap_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_snap_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_snap_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_yaw annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_yaw_rate annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_yaw_acceleration annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto measurement_stamp_s annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto imu_attitude_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto imu_attitude_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto imu_attitude_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto imu_attitude_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto imu_angular_velocity_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto imu_angular_velocity_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto imu_angular_velocity_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto enable annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reset annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto measurement_stamp_valid annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto enable_disturbance_observer annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto kp_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto kp_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto kp_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto kv_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto kv_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto kv_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto ki_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto ki_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto ki_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_lambda_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_lambda_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_lambda_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_eta_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_eta_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_eta_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_phi_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_phi_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_phi_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_surface_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_surface_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smc_surface_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto indi_gain_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto indi_gain_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto indi_gain_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto indi_increment_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto indi_increment_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto indi_increment_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto indi_measured_accel_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto indi_measured_accel_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto indi_measured_accel_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto indi_accel_lpf_alpha annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_horizon_s annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_position_weight_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_position_weight_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_position_weight_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_velocity_weight_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_velocity_weight_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_velocity_weight_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_control_weight_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_control_weight_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_control_weight_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_accel_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_accel_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_accel_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_increment_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_increment_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto nmpc_increment_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto high_order_body_rate_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto high_order_body_rate_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto high_order_body_rate_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto high_order_body_accel_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto high_order_body_accel_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto high_order_body_accel_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smooth_feedback_gain_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smooth_feedback_gain_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smooth_feedback_gain_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smooth_feedback_bound_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smooth_feedback_bound_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto smooth_feedback_bound_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto disturbance_observer_gain_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto disturbance_observer_gain_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto disturbance_observer_gain_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto disturbance_compensation_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto disturbance_compensation_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto disturbance_compensation_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto l1_model_decay annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto l1_filter_T annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto l1_gain_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto l1_gain_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto l1_gain_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto l1_comp_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto l1_comp_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto l1_comp_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto drag_feedforward_gain_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto drag_feedforward_gain_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto drag_feedforward_gain_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto safety_accel_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto safety_accel_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto safety_accel_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fault_rotor_efficiency_1 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fault_rotor_efficiency_2 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fault_rotor_efficiency_3 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fault_rotor_efficiency_4 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fault_allocation_blend annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fault_min_efficiency annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fault_thrust_comp_limit annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto integral_limit_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto integral_limit_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto integral_limit_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto mass annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto gravity annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto hover_percentage annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto min_normalized_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto max_normalized_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto tilt_limit_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto normalized_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto collective_thrust_N annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto position_error_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto position_error_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto position_error_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto velocity_error_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto velocity_error_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto velocity_error_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto sliding_surface_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto sliding_surface_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto sliding_surface_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_body_rate_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_body_rate_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_body_rate_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_body_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_body_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_body_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto disturbance_estimate_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto disturbance_estimate_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto disturbance_estimate_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_force_N_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_force_N_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_force_N_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto saturated annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto status_code annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
    external "C" MosimPx4ctrlG9FamilyCStepScalar(controller_id,dt,position_x,position_y,position_z,velocity_x,velocity_y,velocity_z,attitude_w,attitude_x,attitude_y,attitude_z,angular_velocity_x,angular_velocity_y,angular_velocity_z,reference_position_x,reference_position_y,reference_position_z,reference_velocity_x,reference_velocity_y,reference_velocity_z,reference_acceleration_x,reference_acceleration_y,reference_acceleration_z,reference_jerk_x,reference_jerk_y,reference_jerk_z,reference_snap_x,reference_snap_y,reference_snap_z,reference_yaw,reference_yaw_rate,reference_yaw_acceleration,measurement_stamp_s,imu_attitude_w,imu_attitude_x,imu_attitude_y,imu_attitude_z,imu_angular_velocity_x,imu_angular_velocity_y,imu_angular_velocity_z,enable,reset,measurement_stamp_valid,enable_disturbance_observer,kp_x,kp_y,kp_z,kv_x,kv_y,kv_z,ki_x,ki_y,ki_z,smc_lambda_x,smc_lambda_y,smc_lambda_z,smc_eta_x,smc_eta_y,smc_eta_z,smc_phi_x,smc_phi_y,smc_phi_z,smc_surface_limit_x,smc_surface_limit_y,smc_surface_limit_z,indi_gain_x,indi_gain_y,indi_gain_z,indi_increment_limit_x,indi_increment_limit_y,indi_increment_limit_z,indi_measured_accel_limit_x,indi_measured_accel_limit_y,indi_measured_accel_limit_z,indi_accel_lpf_alpha,nmpc_horizon_s,nmpc_position_weight_x,nmpc_position_weight_y,nmpc_position_weight_z,nmpc_velocity_weight_x,nmpc_velocity_weight_y,nmpc_velocity_weight_z,nmpc_control_weight_x,nmpc_control_weight_y,nmpc_control_weight_z,nmpc_accel_limit_x,nmpc_accel_limit_y,nmpc_accel_limit_z,nmpc_increment_limit_x,nmpc_increment_limit_y,nmpc_increment_limit_z,high_order_body_rate_limit_x,high_order_body_rate_limit_y,high_order_body_rate_limit_z,high_order_body_accel_limit_x,high_order_body_accel_limit_y,high_order_body_accel_limit_z,smooth_feedback_gain_x,smooth_feedback_gain_y,smooth_feedback_gain_z,smooth_feedback_bound_x,smooth_feedback_bound_y,smooth_feedback_bound_z,disturbance_observer_gain_x,disturbance_observer_gain_y,disturbance_observer_gain_z,disturbance_compensation_limit_x
,disturbance_compensation_limit_y,disturbance_compensation_limit_z,l1_model_decay,l1_filter_T,l1_gain_x,l1_gain_y,l1_gain_z,l1_comp_limit_x,l1_comp_limit_y,l1_comp_limit_z,drag_feedforward_gain_x,drag_feedforward_gain_y,drag_feedforward_gain_z,safety_accel_limit_x,safety_accel_limit_y,safety_accel_limit_z,fault_rotor_efficiency_1,fault_rotor_efficiency_2,fault_rotor_efficiency_3,fault_rotor_efficiency_4,fault_allocation_blend,fault_min_efficiency,fault_thrust_comp_limit,integral_limit_x,integral_limit_y,integral_limit_z,mass,gravity,hover_percentage,min_normalized_thrust,max_normalized_thrust,tilt_limit_rad,desired_attitude_w,desired_attitude_x,desired_attitude_y,desired_attitude_z,normalized_thrust,collective_thrust_N,position_error_x,position_error_y,position_error_z,velocity_error_x,velocity_error_y,velocity_error_z,sliding_surface_x,sliding_surface_y,sliding_surface_z,desired_acceleration_x,desired_acceleration_y,desired_acceleration_z,desired_body_rate_x,desired_body_rate_y,desired_body_rate_z,desired_body_acceleration_x,desired_body_acceleration_y,desired_body_acceleration_z,disturbance_estimate_x,disturbance_estimate_y,disturbance_estimate_z,desired_force_N_x,desired_force_N_y,desired_force_N_z,saturated,status_code)
      annotation (Include="enum MosimPx4ctrlG9ControllerId
{
    MOSIM_PX4CTRL_G9_OFFICIAL_PID = 1,
    MOSIM_PX4CTRL_G9_SE3_BASIC = 2,
    MOSIM_PX4CTRL_G9_DFBC_BASIC = 3,
    MOSIM_PX4CTRL_G9_SMC_BOUNDARY_LAYER = 4,
    MOSIM_PX4CTRL_G9_PID_INDI = 5,
    MOSIM_PX4CTRL_G9_NMPC_OUTER = 6,
    MOSIM_PX4CTRL_G10_L1_AWFF = 7,
    MOSIM_PX4CTRL_G10_SAFETY_FILTER = 8,
    MOSIM_PX4CTRL_G10_FAULT_ALLOCATION = 9,
    MOSIM_PX4CTRL_P10_DFBC_HIGH_ORDER = 10,
    MOSIM_PX4CTRL_P10_DFBC_SMOOTH_ROBUST = 11
};

typedef struct MosimPx4ctrlG9FamilyCVec3
{
    double x;
    double y;
    double z;
} MosimPx4ctrlG9FamilyCVec3;

typedef struct MosimPx4ctrlG9FamilyCQuat
{
    double w;
    double x;
    double y;
    double z;
} MosimPx4ctrlG9FamilyCQuat;

typedef struct MosimPx4ctrlG9FamilyCParams
{
    double kp[3];
    double kv[3];
    double ki[3];
    double smc_lambda[3];
    double smc_eta[3];
    double smc_phi[3];
    double smc_surface_limit[3];
    double indi_gain[3];
    double indi_increment_limit[3];
    double indi_measured_accel_limit[3];
    double indi_accel_lpf_alpha;
    double nmpc_horizon_s;
    double nmpc_position_weight[3];
    double nmpc_velocity_weight[3];
    double nmpc_control_weight[3];
    double nmpc_accel_limit[3];
    double nmpc_increment_limit[3];
    double high_order_body_rate_limit[3];
    double high_order_body_accel_limit[3];
    double smooth_feedback_gain[3];
    double smooth_feedback_bound[3];
    double disturbance_observer_gain[3];
    double disturbance_compensation_limit[3];
    double l1_model_decay;
    double l1_filter_T;
    double l1_gain[3];
    double l1_comp_limit[3];
    double drag_feedforward_gain[3];
    double safety_accel_limit[3];
    double fault_rotor_efficiency[4];
    double fault_allocation_blend;
    double fault_min_efficiency;
    double fault_thrust_comp_limit;
    double integral_limit[3];
    double mass;
    double gravity;
    double hover_percentage;
    double min_normalized_thrust;
    double max_normalized_thrust;
    double tilt_limit_rad;
} MosimPx4ctrlG9FamilyCParams;

typedef struct MosimPx4ctrlG9FamilyCState
{
    double thr2acc;
    double covariance;
    MosimPx4ctrlG9FamilyCVec3 integral_position_error;
    MosimPx4ctrlG9FamilyCVec3 previous_velocity;
    MosimPx4ctrlG9FamilyCVec3 measured_acceleration_lpf;
    MosimPx4ctrlG9FamilyCVec3 previous_command_acceleration;
    MosimPx4ctrlG9FamilyCVec3 disturbance_estimate;
    double previous_measurement_stamp_s;
    int has_previous_velocity;
    int has_previous_measurement_stamp;
} MosimPx4ctrlG9FamilyCState;

typedef struct MosimPx4ctrlG9FamilyCInput
{
    int controller_id;
    double dt;
    MosimPx4ctrlG9FamilyCVec3 position;
    MosimPx4ctrlG9FamilyCVec3 velocity;
    MosimPx4ctrlG9FamilyCQuat attitude;
    MosimPx4ctrlG9FamilyCVec3 angular_velocity;
    MosimPx4ctrlG9FamilyCVec3 reference_position;
    MosimPx4ctrlG9FamilyCVec3 reference_velocity;
    MosimPx4ctrlG9FamilyCVec3 reference_acceleration;
    MosimPx4ctrlG9FamilyCVec3 reference_jerk;
    MosimPx4ctrlG9FamilyCVec3 reference_snap;
    double reference_yaw;
    double reference_yaw_rate;
    double reference_yaw_acceleration;
    double measurement_stamp_s;
    MosimPx4ctrlG9FamilyCQuat imu_attitude;
    MosimPx4ctrlG9FamilyCVec3 imu_angular_velocity;
    int enable;
    int reset;
    int measurement_stamp_valid;
    int enable_disturbance_observer;
} MosimPx4ctrlG9FamilyCInput;

typedef struct MosimPx4ctrlG9FamilyCOutput
{
    MosimPx4ctrlG9FamilyCQuat desired_attitude;
    double normalized_thrust;
    double collective_thrust_n;
    MosimPx4ctrlG9FamilyCVec3 position_error;
    MosimPx4ctrlG9FamilyCVec3 velocity_error;
    MosimPx4ctrlG9FamilyCVec3 sliding_surface;
    MosimPx4ctrlG9FamilyCVec3 desired_acceleration;
    MosimPx4ctrlG9FamilyCVec3 desired_body_rate;
    MosimPx4ctrlG9FamilyCVec3 desired_body_acceleration;
    MosimPx4ctrlG9FamilyCVec3 disturbance_estimate;
    MosimPx4ctrlG9FamilyCVec3 desired_force_n;
    double saturated;
    int status_code;
} MosimPx4ctrlG9FamilyCOutput;

void mosim_px4ctrl_g9_family_c_reset(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state);

void mosim_px4ctrl_g9_family_c_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *output);

void MosimPx4ctrlG9FamilyCStepScalar(
    double controller_id,
    double dt,
    double position_x,
    double position_y,
    double position_z,
    double velocity_x,
    double velocity_y,
    double velocity_z,
    double attitude_w,
    double attitude_x,
    double attitude_y,
    double attitude_z,
    double angular_velocity_x,
    double angular_velocity_y,
    double angular_velocity_z,
    double reference_position_x,
    double reference_position_y,
    double reference_position_z,
    double reference_velocity_x,
    double reference_velocity_y,
    double reference_velocity_z,
    double reference_acceleration_x,
    double reference_acceleration_y,
    double reference_acceleration_z,
    double reference_jerk_x,
    double reference_jerk_y,
    double reference_jerk_z,
    double reference_snap_x,
    double reference_snap_y,
    double reference_snap_z,
    double reference_yaw,
    double reference_yaw_rate,
    double reference_yaw_acceleration,
    double measurement_stamp_s,
    double imu_attitude_w,
    double imu_attitude_x,
    double imu_attitude_y,
    double imu_attitude_z,
    double imu_angular_velocity_x,
    double imu_angular_velocity_y,
    double imu_angular_velocity_z,
    double enable,
    double reset,
    double measurement_stamp_valid,
    double enable_disturbance_observer,
    double kp_x,
    double kp_y,
    double kp_z,
    double kv_x,
    double kv_y,
    double kv_z,
    double ki_x,
    double ki_y,
    double ki_z,
    double smc_lambda_x,
    double smc_lambda_y,
    double smc_lambda_z,
    double smc_eta_x,
    double smc_eta_y,
    double smc_eta_z,
    double smc_phi_x,
    double smc_phi_y,
    double smc_phi_z,
    double smc_surface_limit_x,
    double smc_surface_limit_y,
    double smc_surface_limit_z,
    double indi_gain_x,
    double indi_gain_y,
    double indi_gain_z,
    double indi_increment_limit_x,
    double indi_increment_limit_y,
    double indi_increment_limit_z,
    double indi_measured_accel_limit_x,
    double indi_measured_accel_limit_y,
    double indi_measured_accel_limit_z,
    double indi_accel_lpf_alpha,
    double nmpc_horizon_s,
    double nmpc_position_weight_x,
    double nmpc_position_weight_y,
    double nmpc_position_weight_z,
    double nmpc_velocity_weight_x,
    double nmpc_velocity_weight_y,
    double nmpc_velocity_weight_z,
    double nmpc_control_weight_x,
    double nmpc_control_weight_y,
    double nmpc_control_weight_z,
    double nmpc_accel_limit_x,
    double nmpc_accel_limit_y,
    double nmpc_accel_limit_z,
    double nmpc_increment_limit_x,
    double nmpc_increment_limit_y,
    double nmpc_increment_limit_z,
    double high_order_body_rate_limit_x,
    double high_order_body_rate_limit_y,
    double high_order_body_rate_limit_z,
    double high_order_body_accel_limit_x,
    double high_order_body_accel_limit_y,
    double high_order_body_accel_limit_z,
    double smooth_feedback_gain_x,
    double smooth_feedback_gain_y,
    double smooth_feedback_gain_z,
    double smooth_feedback_bound_x,
    double smooth_feedback_bound_y,
    double smooth_feedback_bound_z,
    double disturbance_observer_gain_x,
    double disturbance_observer_gain_y,
    double disturbance_observer_gain_z,
    double disturbance_compensation_limit_x,
    double disturbance_compensation_limit_y,
    double disturbance_compensation_limit_z,
    double l1_model_decay,
    double l1_filter_T,
    double l1_gain_x,
    double l1_gain_y,
    double l1_gain_z,
    double l1_comp_limit_x,
    double l1_comp_limit_y,
    double l1_comp_limit_z,
    double drag_feedforward_gain_x,
    double drag_feedforward_gain_y,
    double drag_feedforward_gain_z,
    double safety_accel_limit_x,
    double safety_accel_limit_y,
    double safety_accel_limit_z,
    double fault_rotor_efficiency_1,
    double fault_rotor_efficiency_2,
    double fault_rotor_efficiency_3,
    double fault_rotor_efficiency_4,
    double fault_allocation_blend,
    double fault_min_efficiency,
    double fault_thrust_comp_limit,
    double integral_limit_x,
    double integral_limit_y,
    double integral_limit_z,
    double mass,
    double gravity,
    double hover_percentage,
    double min_normalized_thrust,
    double max_normalized_thrust,
    double tilt_limit_rad,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *normalized_thrust,
    double *collective_thrust_N,
    double *position_error_x,
    double *position_error_y,
    double *position_error_z,
    double *velocity_error_x,
    double *velocity_error_y,
    double *velocity_error_z,
    double *sliding_surface_x,
    double *sliding_surface_y,
    double *sliding_surface_z,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *desired_body_rate_x,
    double *desired_body_rate_y,
    double *desired_body_rate_z,
    double *desired_body_acceleration_x,
    double *desired_body_acceleration_y,
    double *desired_body_acceleration_z,
    double *disturbance_estimate_x,
    double *disturbance_estimate_y,
    double *disturbance_estimate_z,
    double *desired_force_N_x,
    double *desired_force_N_y,
    double *desired_force_N_z,
    double *saturated,
    double *status_code);




#include <math.h>
#include <string.h>

static double c_clamp(double value, double lower, double upper)
{
    if (value < lower)
    {
        return lower;
    }
    if (value > upper)
    {
        return upper;
    }
    return value;
}

static double c_sat(double value)
{
    return c_clamp(value, -1.0, 1.0);
}

static double c_safe_positive(double value, double fallback)
{
    return value > 1.0e-9 ? value : fallback;
}

static double c_safe_nonnegative(double value)
{
    return value > 0.0 ? value : 0.0;
}

static int c_vec3_components_equal(
    MosimPx4ctrlG9FamilyCVec3 a,
    MosimPx4ctrlG9FamilyCVec3 b)
{
    return fabs(a.x - b.x) <= 1.0e-12 &&
        fabs(a.y - b.y) <= 1.0e-12 &&
        fabs(a.z - b.z) <= 1.0e-12;
}

static MosimPx4ctrlG9FamilyCVec3 c_vec3(double x, double y, double z)
{
    MosimPx4ctrlG9FamilyCVec3 v;
    v.x = x;
    v.y = y;
    v.z = z;
    return v;
}

static MosimPx4ctrlG9FamilyCQuat c_quat(double w, double x, double y, double z)
{
    MosimPx4ctrlG9FamilyCQuat q;
    q.w = w;
    q.x = x;
    q.y = y;
    q.z = z;
    return q;
}

static MosimPx4ctrlG9FamilyCVec3 c_add(
    MosimPx4ctrlG9FamilyCVec3 a,
    MosimPx4ctrlG9FamilyCVec3 b)
{
    return c_vec3(a.x + b.x, a.y + b.y, a.z + b.z);
}

static MosimPx4ctrlG9FamilyCVec3 c_subtract(
    MosimPx4ctrlG9FamilyCVec3 a,
    MosimPx4ctrlG9FamilyCVec3 b)
{
    return c_vec3(a.x - b.x, a.y - b.y, a.z - b.z);
}

static MosimPx4ctrlG9FamilyCVec3 c_scale(
    MosimPx4ctrlG9FamilyCVec3 v,
    double s)
{
    return c_vec3(v.x * s, v.y * s, v.z * s);
}

static double c_dot(
    MosimPx4ctrlG9FamilyCVec3 a,
    MosimPx4ctrlG9FamilyCVec3 b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static MosimPx4ctrlG9FamilyCVec3 c_cross(
    MosimPx4ctrlG9FamilyCVec3 a,
    MosimPx4ctrlG9FamilyCVec3 b)
{
    return c_vec3(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x);
}

static double c_norm(MosimPx4ctrlG9FamilyCVec3 v)
{
    return sqrt(c_dot(v, v));
}

static MosimPx4ctrlG9FamilyCVec3 c_clamp_vec3(
    MosimPx4ctrlG9FamilyCVec3 value,
    const double limit[3])
{
    return c_vec3(
        c_clamp(value.x, -limit[0], limit[0]),
        c_clamp(value.y, -limit[1], limit[1]),
        c_clamp(value.z, -limit[2], limit[2]));
}

static MosimPx4ctrlG9FamilyCVec3 c_clamp_delta_vec3(
    MosimPx4ctrlG9FamilyCVec3 value,
    MosimPx4ctrlG9FamilyCVec3 previous,
    const double limit[3])
{
    const MosimPx4ctrlG9FamilyCVec3 delta =
        c_clamp_vec3(c_subtract(value, previous), limit);
    return c_add(previous, delta);
}

static MosimPx4ctrlG9FamilyCVec3 c_normalize_vec3(
    MosimPx4ctrlG9FamilyCVec3 v,
    MosimPx4ctrlG9FamilyCVec3 fallback)
{
    const double n = c_norm(v);
    if (n <= 1.0e-12)
    {
        return fallback;
    }
    return c_scale(v, 1.0 / n);
}

static MosimPx4ctrlG9FamilyCQuat c_normalize_quat(MosimPx4ctrlG9FamilyCQuat q)
{
    const double n = sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (n <= 0.0)
    {
        return c_quat(1.0, 0.0, 0.0, 0.0);
    }
    return c_quat(q.w / n, q.x / n, q.y / n, q.z / n);
}

static MosimPx4ctrlG9FamilyCQuat c_conjugate(MosimPx4ctrlG9FamilyCQuat q)
{
    return c_quat(q.w, -q.x, -q.y, -q.z);
}

static MosimPx4ctrlG9FamilyCQuat c_multiply(
    MosimPx4ctrlG9FamilyCQuat a,
    MosimPx4ctrlG9FamilyCQuat b)
{
    return c_normalize_quat(c_quat(
        a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
        a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
        a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
        a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w));
}

static MosimPx4ctrlG9FamilyCQuat c_inverse(MosimPx4ctrlG9FamilyCQuat q)
{
    return c_conjugate(c_normalize_quat(q));
}

static MosimPx4ctrlG9FamilyCQuat c_angle_axis(
    double angle,
    MosimPx4ctrlG9FamilyCVec3 axis)
{
    const double half = 0.5 * angle;
    const double s = sin(half);
    return c_normalize_quat(c_quat(cos(half), axis.x * s, axis.y * s, axis.z * s));
}

static double c_yaw_from_quat(MosimPx4ctrlG9FamilyCQuat q_raw)
{
    const MosimPx4ctrlG9FamilyCQuat q = c_normalize_quat(q_raw);
    return atan2(
        2.0 * (q.x * q.y + q.w * q.z),
        q.w * q.w + q.x * q.x - q.y * q.y - q.z * q.z);
}

static MosimPx4ctrlG9FamilyCQuat c_quat_from_rotation_matrix_columns(
    MosimPx4ctrlG9FamilyCVec3 b1,
    MosimPx4ctrlG9FamilyCVec3 b2,
    MosimPx4ctrlG9FamilyCVec3 b3)
{
    const double m00 = b1.x;
    const double m01 = b2.x;
    const double m02 = b3.x;
    const double m10 = b1.y;
    const double m11 = b2.y;
    const double m12 = b3.y;
    const double m20 = b1.z;
    const double m21 = b2.z;
    const double m22 = b3.z;
    const double trace = m00 + m11 + m22;

    if (trace > 0.0)
    {
        const double s = sqrt(trace + 1.0) * 2.0;
        return c_normalize_quat(c_quat(
            0.25 * s,
            (m21 - m12) / s,
            (m02 - m20) / s,
            (m10 - m01) / s));
    }
    if (m00 > m11 && m00 > m22)
    {
        const double s = sqrt(1.0 + m00 - m11 - m22) * 2.0;
        return c_normalize_quat(c_quat(
            (m21 - m12) / s,
            0.25 * s,
            (m01 + m10) / s,
            (m02 + m20) / s));
    }
    if (m11 > m22)
    {
        const double s = sqrt(1.0 + m11 - m00 - m22) * 2.0;
        return c_normalize_quat(c_quat(
            (m02 - m20) / s,
            (m01 + m10) / s,
            0.25 * s,
            (m12 + m21) / s));
    }
    {
        const double s = sqrt(1.0 + m22 - m00 - m11) * 2.0;
        return c_normalize_quat(c_quat(
            (m10 - m01) / s,
            (m02 + m20) / s,
            (m12 + m21) / s,
            0.25 * s));
    }
}

void mosim_px4ctrl_g9_family_c_reset(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state)
{
    state->thr2acc = params->gravity / params->hover_percentage;
    state->covariance = 1.0e6;
    state->integral_position_error = c_vec3(0.0, 0.0, 0.0);
    state->previous_velocity = c_vec3(0.0, 0.0, 0.0);
    state->measured_acceleration_lpf = c_vec3(0.0, 0.0, 0.0);
    state->previous_command_acceleration = c_vec3(0.0, 0.0, 0.0);
    state->disturbance_estimate = c_vec3(0.0, 0.0, 0.0);
    state->previous_measurement_stamp_s = 0.0;
    state->has_previous_velocity = 0;
    state->has_previous_measurement_stamp = 0;
}

static MosimPx4ctrlG9FamilyCOutput c_disabled_output(
    const MosimPx4ctrlG9FamilyCInput *input)
{
    MosimPx4ctrlG9FamilyCOutput out;
    memset(&out, 0, sizeof(out));
    out.status_code = 1;
    out.desired_attitude = c_normalize_quat(input->imu_attitude);
    return out;
}

static MosimPx4ctrlG9FamilyCVec3 c_pid_acceleration_no_gravity(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    const double dt = input->dt > 0.0 ? input->dt : 0.01;
    out->position_error = c_subtract(input->reference_position, input->position);
    out->velocity_error = c_subtract(input->reference_velocity, input->velocity);
    state->integral_position_error = c_clamp_vec3(
        c_vec3(
            state->integral_position_error.x + out->position_error.x * dt,
            state->integral_position_error.y + out->position_error.y * dt,
            state->integral_position_error.z + out->position_error.z * dt),
        params->integral_limit);
    return c_vec3(
        input->reference_acceleration.x + params->kv[0] * out->velocity_error.x + params->kp[0] * out->position_error.x + params->ki[0] * state->integral_position_error.x,
        input->reference_acceleration.y + params->kv[1] * out->velocity_error.y + params->kp[1] * out->position_error.y + params->ki[1] * state->integral_position_error.y,
        input->reference_acceleration.z + params->kv[2] * out->velocity_error.z + params->kp[2] * out->position_error.z + params->ki[2] * state->integral_position_error.z);
}

static int c_consume_new_measurement_sample(
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    double *dt)
{
    *dt = c_safe_positive(input->dt, 0.01);
    if (!input->measurement_stamp_valid)
    {
        return 1;
    }
    if (!state->has_previous_measurement_stamp)
    {
        state->previous_measurement_stamp_s = input->measurement_stamp_s;
        state->has_previous_measurement_stamp = 1;
        return 1;
    }
    {
        const double measurement_dt =
            input->measurement_stamp_s - state->previous_measurement_stamp_s;
        if (measurement_dt <= 1.0e-6)
        {
            return 0;
        }
        state->previous_measurement_stamp_s = input->measurement_stamp_s;
        *dt = measurement_dt;
    }
    return 1;
}

static MosimPx4ctrlG9FamilyCVec3 c_measured_acceleration_from_velocity(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    double dt)
{
    MosimPx4ctrlG9FamilyCVec3 measured_acceleration;
    const double alpha = c_clamp(params->indi_accel_lpf_alpha, 0.0, 1.0);
    dt = c_safe_positive(dt, 0.01);
    if (state->has_previous_velocity)
    {
        measured_acceleration =
            c_scale(c_subtract(input->velocity, state->previous_velocity), 1.0 / dt);
    }
    else
    {
        measured_acceleration = state->previous_command_acceleration;
    }
    measured_acceleration =
        c_clamp_vec3(measured_acceleration, params->indi_measured_accel_limit);
    if (state->has_previous_velocity)
    {
        state->measured_acceleration_lpf = c_add(
            c_scale(measured_acceleration, alpha),
            c_scale(state->measured_acceleration_lpf, 1.0 - alpha));
    }
    else
    {
        state->measured_acceleration_lpf = measured_acceleration;
    }
    state->previous_velocity = input->velocity;
    state->has_previous_velocity = 1;
    return state->measured_acceleration_lpf;
}

static void c_fill_attitude_thrust_output(
    const MosimPx4ctrlG9FamilyCParams *params,
    const MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out,
    int enforce_limits)
{
    double roll;
    double pitch;
    out->normalized_thrust = out->desired_acceleration.z / state->thr2acc;
    if (enforce_limits)
    {
        const double unclamped = out->normalized_thrust;
        out->normalized_thrust = c_clamp(
            out->normalized_thrust,
            params->min_normalized_thrust,
            params->max_normalized_thrust);
        if (fabs(out->normalized_thrust - unclamped) > 1.0e-12)
        {
            out->saturated = 1.0;
        }
    }
    out->collective_thrust_n =
        out->normalized_thrust * (params->mass * params->gravity / params->hover_percentage);
    out->desired_force_n = c_vec3(
        params->mass * out->desired_acceleration.x,
        params->mass * out->desired_acceleration.y,
        params->mass * out->desired_acceleration.z);
    {
        const double yaw_odom = c_yaw_from_quat(input->attitude);
        const double sin_yaw = sin(yaw_odom);
        const double cos_yaw = cos(yaw_odom);
        roll = (out->desired_acceleration.x * sin_yaw - out->desired_acceleration.y * cos_yaw) / params->gravity;
        pitch = (out->desired_acceleration.x * cos_yaw + out->desired_acceleration.y * sin_yaw) / params->gravity;
    }
    if (enforce_limits)
    {
        const double unclamped_roll = roll;
        const double unclamped_pitch = pitch;
        roll = c_clamp(roll, -params->tilt_limit_rad, params->tilt_limit_rad);
        pitch = c_clamp(pitch, -params->tilt_limit_rad, params->tilt_limit_rad);
        if (fabs(roll - unclamped_roll) > 1.0e-12 ||
            fabs(pitch - unclamped_pitch) > 1.0e-12)
        {
            out->saturated = 1.0;
        }
    }
    {
        const MosimPx4ctrlG9FamilyCQuat q_yaw =
            c_angle_axis(input->reference_yaw, c_vec3(0.0, 0.0, 1.0));
        const MosimPx4ctrlG9FamilyCQuat q_pitch =
            c_angle_axis(pitch, c_vec3(0.0, 1.0, 0.0));
        const MosimPx4ctrlG9FamilyCQuat q_roll =
            c_angle_axis(roll, c_vec3(1.0, 0.0, 0.0));
        const MosimPx4ctrlG9FamilyCQuat q_des_world =
            c_multiply(c_multiply(q_yaw, q_pitch), q_roll);
        out->desired_attitude =
            c_multiply(c_multiply(input->imu_attitude, c_inverse(input->attitude)), q_des_world);
    }
}

static void c_fill_flatness_attitude_output(
    const MosimPx4ctrlG9FamilyCParams *params,
    const MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out,
    MosimPx4ctrlG9FamilyCVec3 force,
    int enforce_limits)
{
    MosimPx4ctrlG9FamilyCVec3 limited_force = force;
    const double force_norm = c_norm(limited_force);
    MosimPx4ctrlG9FamilyCVec3 b3c =
        c_normalize_vec3(limited_force, c_vec3(0.0, 0.0, 1.0));
    const double k_half_pi = 1.57079632679489661923;
    if (enforce_limits && params->tilt_limit_rad > 0.0 && params->tilt_limit_rad < k_half_pi)
    {
        const double min_b3_z = cos(params->tilt_limit_rad);
        if (b3c.z < min_b3_z)
        {
            const double xy_norm = sqrt(b3c.x * b3c.x + b3c.y * b3c.y);
            const double xy_limited = sin(params->tilt_limit_rad);
            if (xy_norm > 1.0e-12)
            {
                b3c.x = b3c.x / xy_norm * xy_limited;
                b3c.y = b3c.y / xy_norm * xy_limited;
            }
            else
            {
                b3c.x = 0.0;
                b3c.y = 0.0;
            }
            b3c.z = min_b3_z;
            b3c = c_normalize_vec3(b3c, c_vec3(0.0, 0.0, 1.0));
            limited_force = c_scale(b3c, force_norm);
            out->saturated = 1.0;
        }
    }
    {
        const MosimPx4ctrlG9FamilyCVec3 b1d =
            c_vec3(cos(input->reference_yaw), sin(input->reference_yaw), 0.0);
        MosimPx4ctrlG9FamilyCVec3 b2c = c_cross(b3c, b1d);
        MosimPx4ctrlG9FamilyCVec3 b1c;
        if (c_norm(b2c) <= 1.0e-9)
        {
            b2c = c_cross(b3c, c_vec3(0.0, 1.0, 0.0));
        }
        b2c = c_normalize_vec3(b2c, c_vec3(0.0, 1.0, 0.0));
        b1c = c_normalize_vec3(c_cross(b2c, b3c), b1d);
        out->desired_attitude = c_multiply(
            c_multiply(input->imu_attitude, c_inverse(input->attitude)),
            c_quat_from_rotation_matrix_columns(b1c, b2c, b3c));
    }
    out->desired_force_n = limited_force;
    out->desired_acceleration = c_vec3(
        limited_force.x / params->mass,
        limited_force.y / params->mass,
        limited_force.z / params->mass);
    out->normalized_thrust =
        c_dot(limited_force, b3c) / (params->mass * state->thr2acc);
    if (enforce_limits)
    {
        const double unclamped = out->normalized_thrust;
        out->normalized_thrust = c_clamp(
            out->normalized_thrust,
            params->min_normalized_thrust,
            params->max_normalized_thrust);
        if (fabs(out->normalized_thrust - unclamped) > 1.0e-12)
        {
            out->saturated = 1.0;
        }
    }
    out->collective_thrust_n =
        out->normalized_thrust * (params->mass * params->gravity / params->hover_percentage);
}

static MosimPx4ctrlG9FamilyCVec3 c_body_rate_from_jerk(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCVec3 desired_force,
    MosimPx4ctrlG9FamilyCVec3 reference_jerk,
    double reference_yaw_rate)
{
    const double thrust_n = c_safe_positive(c_norm(desired_force), params->mass * params->gravity);
    const MosimPx4ctrlG9FamilyCVec3 b3c =
        c_normalize_vec3(desired_force, c_vec3(0.0, 0.0, 1.0));
    const MosimPx4ctrlG9FamilyCVec3 h_omega =
        c_scale(c_cross(b3c, c_scale(reference_jerk, params->mass)), 1.0 / thrust_n);
    return c_clamp_vec3(
        c_vec3(-h_omega.y, h_omega.x, reference_yaw_rate * b3c.z),
        params->high_order_body_rate_limit);
}

static MosimPx4ctrlG9FamilyCVec3 c_body_acceleration_from_snap(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCVec3 desired_force,
    MosimPx4ctrlG9FamilyCVec3 reference_snap,
    double reference_yaw_acceleration)
{
    const double thrust_n = c_safe_positive(c_norm(desired_force), params->mass * params->gravity);
    const MosimPx4ctrlG9FamilyCVec3 b3c =
        c_normalize_vec3(desired_force, c_vec3(0.0, 0.0, 1.0));
    const MosimPx4ctrlG9FamilyCVec3 h_acc =
        c_scale(c_cross(b3c, c_scale(reference_snap, params->mass)), 1.0 / thrust_n);
    return c_clamp_vec3(
        c_vec3(-h_acc.y, h_acc.x, reference_yaw_acceleration * b3c.z),
        params->high_order_body_accel_limit);
}

static void c_dfbc_high_order_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    const MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    MosimPx4ctrlG9FamilyCVec3 force;
    out->position_error = c_subtract(input->reference_position, input->position);
    out->velocity_error = c_subtract(input->reference_velocity, input->velocity);
    force = c_vec3(
        params->mass * (input->reference_acceleration.x + params->kp[0] * out->position_error.x + params->kv[0] * out->velocity_error.x),
        params->mass * (input->reference_acceleration.y + params->kp[1] * out->position_error.y + params->kv[1] * out->velocity_error.y),
        params->mass * (input->reference_acceleration.z + params->kp[2] * out->position_error.z + params->kv[2] * out->velocity_error.z + params->gravity));
    c_fill_flatness_attitude_output(params, state, input, out, force, 1);
    out->desired_body_rate = c_body_rate_from_jerk(
        params, out->desired_force_n, input->reference_jerk, input->reference_yaw_rate);
    out->desired_body_acceleration = c_body_acceleration_from_snap(
        params, out->desired_force_n, input->reference_snap, input->reference_yaw_acceleration);
}

static MosimPx4ctrlG9FamilyCVec3 c_smooth_bounded_feedback(
    const MosimPx4ctrlG9FamilyCParams *params,
    const MosimPx4ctrlG9FamilyCOutput *out)
{
    return c_vec3(
        params->smooth_feedback_bound[0] * tanh(
            (params->kp[0] * out->position_error.x + params->kv[0] * out->velocity_error.x) /
            c_safe_positive(params->smooth_feedback_bound[0], 1.0)),
        params->smooth_feedback_bound[1] * tanh(
            (params->kp[1] * out->position_error.y + params->kv[1] * out->velocity_error.y) /
            c_safe_positive(params->smooth_feedback_bound[1], 1.0)),
        params->smooth_feedback_bound[2] * tanh(
            (params->kp[2] * out->position_error.z + params->kv[2] * out->velocity_error.z) /
            c_safe_positive(params->smooth_feedback_bound[2], 1.0)));
}

static void c_dfbc_smooth_robust_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    MosimPx4ctrlG9FamilyCVec3 bounded_feedback;
    MosimPx4ctrlG9FamilyCVec3 model_acceleration;
    MosimPx4ctrlG9FamilyCVec3 compensated_acceleration;
    MosimPx4ctrlG9FamilyCVec3 residual = c_vec3(0.0, 0.0, 0.0);
    MosimPx4ctrlG9FamilyCVec3 force;
    double measurement_dt = input->dt;
    out->position_error = c_subtract(input->reference_position, input->position);
    out->velocity_error = c_subtract(input->reference_velocity, input->velocity);
    bounded_feedback = c_smooth_bounded_feedback(params, out);
    model_acceleration = c_add(input->reference_acceleration, bounded_feedback);
    if (input->enable_disturbance_observer &&
        c_consume_new_measurement_sample(state, input, &measurement_dt))
    {
        const MosimPx4ctrlG9FamilyCVec3 measured_acceleration =
            c_measured_acceleration_from_velocity(params, state, input, measurement_dt);
        residual = c_subtract(measured_acceleration, state->previous_command_acceleration);
        state->disturbance_estimate = c_clamp_vec3(
            c_vec3(
                (1.0 - params->disturbance_observer_gain[0]) * state->disturbance_estimate.x + params->disturbance_observer_gain[0] * residual.x,
                (1.0 - params->disturbance_observer_gain[1]) * state->disturbance_estimate.y + params->disturbance_observer_gain[1] * residual.y,
                (1.0 - params->disturbance_observer_gain[2]) * state->disturbance_estimate.z + params->disturbance_observer_gain[2] * residual.z),
            params->disturbance_compensation_limit);
    }
    compensated_acceleration = input->enable_disturbance_observer
        ? c_subtract(model_acceleration, state->disturbance_estimate)
        : model_acceleration;
    state->previous_command_acceleration = compensated_acceleration;
    force = c_vec3(
        params->mass * compensated_acceleration.x,
        params->mass * compensated_acceleration.y,
        params->mass * (compensated_acceleration.z + params->gravity));
    c_fill_flatness_attitude_output(params, state, input, out, force, 1);
    out->desired_body_rate = c_body_rate_from_jerk(
        params, out->desired_force_n, input->reference_jerk, input->reference_yaw_rate);
    out->desired_body_acceleration = c_body_acceleration_from_snap(
        params, out->desired_force_n, input->reference_snap, input->reference_yaw_acceleration);
    out->sliding_surface = residual;
    out->disturbance_estimate = state->disturbance_estimate;
}

static void c_se3_or_dfbc_basic_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    const MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    MosimPx4ctrlG9FamilyCVec3 force;
    out->position_error = c_subtract(input->reference_position, input->position);
    out->velocity_error = c_subtract(input->reference_velocity, input->velocity);
    force = c_vec3(
        params->mass * (input->reference_acceleration.x + params->kp[0] * out->position_error.x + params->kv[0] * out->velocity_error.x),
        params->mass * (input->reference_acceleration.y + params->kp[1] * out->position_error.y + params->kv[1] * out->velocity_error.y),
        params->mass * (input->reference_acceleration.z + params->kp[2] * out->position_error.z + params->kv[2] * out->velocity_error.z + params->gravity));
    c_fill_flatness_attitude_output(params, state, input, out, force, 1);
}

static void c_smc_boundary_layer_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    const MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    MosimPx4ctrlG9FamilyCVec3 switching_acceleration;
    MosimPx4ctrlG9FamilyCVec3 force;
    out->position_error = c_subtract(input->reference_position, input->position);
    out->velocity_error = c_subtract(input->reference_velocity, input->velocity);
    out->sliding_surface = c_clamp_vec3(
        c_vec3(
            out->velocity_error.x + params->smc_lambda[0] * out->position_error.x,
            out->velocity_error.y + params->smc_lambda[1] * out->position_error.y,
            out->velocity_error.z + params->smc_lambda[2] * out->position_error.z),
        params->smc_surface_limit);
    switching_acceleration = c_vec3(
        params->smc_eta[0] * c_sat(out->sliding_surface.x / c_safe_positive(fabs(params->smc_phi[0]), 1.0e-9)),
        params->smc_eta[1] * c_sat(out->sliding_surface.y / c_safe_positive(fabs(params->smc_phi[1]), 1.0e-9)),
        params->smc_eta[2] * c_sat(out->sliding_surface.z / c_safe_positive(fabs(params->smc_phi[2]), 1.0e-9)));
    force = c_vec3(
        params->mass * (input->reference_acceleration.x + params->kp[0] * out->position_error.x + params->kv[0] * out->velocity_error.x + switching_acceleration.x),
        params->mass * (input->reference_acceleration.y + params->kp[1] * out->position_error.y + params->kv[1] * out->velocity_error.y + switching_acceleration.y),
        params->mass * (input->reference_acceleration.z + params->kp[2] * out->position_error.z + params->kv[2] * out->velocity_error.z + switching_acceleration.z + params->gravity));
    c_fill_flatness_attitude_output(params, state, input, out, force, 1);
}

static void c_pid_indi_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    const MosimPx4ctrlG9FamilyCVec3 base_acceleration_no_gravity =
        c_pid_acceleration_no_gravity(params, state, input, out);
    double measurement_dt = input->dt;
    const int update_measurement =
        c_consume_new_measurement_sample(state, input, &measurement_dt);
    const int had_previous_velocity = state->has_previous_velocity;
    MosimPx4ctrlG9FamilyCVec3 indi_increment = c_vec3(0.0, 0.0, 0.0);
    if (update_measurement)
    {
        (void)c_measured_acceleration_from_velocity(params, state, input, measurement_dt);
    }
    if (update_measurement && had_previous_velocity)
    {
        const MosimPx4ctrlG9FamilyCVec3 acceleration_residual =
            c_subtract(state->previous_command_acceleration, state->measured_acceleration_lpf);
        indi_increment = c_clamp_vec3(
            c_vec3(
                params->indi_gain[0] * acceleration_residual.x,
                params->indi_gain[1] * acceleration_residual.y,
                params->indi_gain[2] * acceleration_residual.z),
            params->indi_increment_limit);
        out->sliding_surface = acceleration_residual;
    }
    out->desired_acceleration = c_vec3(
        base_acceleration_no_gravity.x + indi_increment.x,
        base_acceleration_no_gravity.y + indi_increment.y,
        base_acceleration_no_gravity.z + indi_increment.z + params->gravity);
    state->previous_command_acceleration = c_vec3(
        out->desired_acceleration.x,
        out->desired_acceleration.y,
        out->desired_acceleration.z - params->gravity);
    c_fill_attitude_thrust_output(params, state, input, out, 1);
}

static void c_nmpc_outer_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    const double horizon = c_clamp(params->nmpc_horizon_s, 0.05, 2.0);
    const double half_horizon_sq = 0.5 * horizon * horizon;
    const double horizon_sq = horizon * horizon;
    const double horizon_fourth = horizon_sq * horizon_sq;
    double unconstrained[3];
    MosimPx4ctrlG9FamilyCVec3 constrained_acceleration;

    out->position_error = c_subtract(input->reference_position, input->position);
    out->velocity_error = c_subtract(input->reference_velocity, input->velocity);
    {
        const MosimPx4ctrlG9FamilyCVec3 reference_position_horizon = c_vec3(
            input->reference_position.x + input->reference_velocity.x * horizon + half_horizon_sq * input->reference_acceleration.x,
            input->reference_position.y + input->reference_velocity.y * horizon + half_horizon_sq * input->reference_acceleration.y,
            input->reference_position.z + input->reference_velocity.z * horizon + half_horizon_sq * input->reference_acceleration.z);
        const MosimPx4ctrlG9FamilyCVec3 reference_velocity_horizon = c_vec3(
            input->reference_velocity.x + input->reference_acceleration.x * horizon,
            input->reference_velocity.y + input->reference_acceleration.y * horizon,
            input->reference_velocity.z + input->reference_acceleration.z * horizon);
        const MosimPx4ctrlG9FamilyCVec3 predicted_position_open_loop = c_vec3(
            input->position.x + input->velocity.x * horizon,
            input->position.y + input->velocity.y * horizon,
            input->position.z + input->velocity.z * horizon);
        const MosimPx4ctrlG9FamilyCVec3 horizon_position_error =
            c_subtract(reference_position_horizon, predicted_position_open_loop);
        const MosimPx4ctrlG9FamilyCVec3 horizon_velocity_error =
            c_subtract(reference_velocity_horizon, input->velocity);
        int i;
        const double hp[3] = {
            horizon_position_error.x,
            horizon_position_error.y,
            horizon_position_error.z};
        const double hv[3] = {
            horizon_velocity_error.x,
            horizon_velocity_error.y,
            horizon_velocity_error.z};
        const double previous[3] = {
            state->previous_command_acceleration.x,
            state->previous_command_acceleration.y,
            state->previous_command_acceleration.z};
        for (i = 0; i < 3; ++i)
        {
            const double wp = c_safe_nonnegative(params->nmpc_position_weight[i]);
            const double wv = c_safe_nonnegative(params->nmpc_velocity_weight[i]);
            const double wu = c_safe_nonnegative(params->nmpc_control_weight[i]);
            const double numerator =
                wp * horizon_sq * hp[i] +
                2.0 * wv * horizon * hv[i] +
                2.0 * wu * previous[i];
            const double denominator =
                0.5 * wp * horizon_fourth + 2.0 * wv * horizon_sq + 2.0 * wu;
            unconstrained[i] = numerator / c_safe_positive(denominator, 1.0e-6);
        }
    }
    constrained_acceleration =
        c_clamp_vec3(c_vec3(unconstrained[0], unconstrained[1], unconstrained[2]), params->nmpc_accel_limit);
    constrained_acceleration =
        c_clamp_delta_vec3(constrained_acceleration, state->previous_command_acceleration, params->nmpc_increment_limit);
    state->previous_command_acceleration = constrained_acceleration;
    out->desired_acceleration = c_vec3(
        constrained_acceleration.x,
        constrained_acceleration.y,
        constrained_acceleration.z + params->gravity);
    out->sliding_surface =
        c_subtract(c_vec3(unconstrained[0], unconstrained[1], unconstrained[2]), constrained_acceleration);
    out->saturated = c_norm(out->sliding_surface) > 1.0e-12 ? 1.0 : 0.0;
    c_fill_attitude_thrust_output(params, state, input, out, 1);
}

static void c_l1_awff_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    const MosimPx4ctrlG9FamilyCVec3 nominal_acceleration_no_gravity =
        c_pid_acceleration_no_gravity(params, state, input, out);
    double measurement_dt = input->dt;
    const int update_measurement =
        c_consume_new_measurement_sample(state, input, &measurement_dt);
    const int had_previous_velocity = state->has_previous_velocity;
    MosimPx4ctrlG9FamilyCVec3 measured_acceleration = state->measured_acceleration_lpf;
    MosimPx4ctrlG9FamilyCVec3 residual = c_vec3(0.0, 0.0, 0.0);

    if (update_measurement)
    {
        measured_acceleration =
            c_measured_acceleration_from_velocity(params, state, input, measurement_dt);
    }
    if (update_measurement && had_previous_velocity)
    {
        MosimPx4ctrlG9FamilyCVec3 adaptive_update;
        const double filter_T = fabs(params->l1_filter_T);
        const double alpha = filter_T > 1.0e-9
            ? c_clamp(measurement_dt / (filter_T + measurement_dt), 0.0, 1.0)
            : 1.0;
        const double model_decay = c_safe_nonnegative(params->l1_model_decay);

        residual = c_subtract(measured_acceleration, state->previous_command_acceleration);
        adaptive_update = c_vec3(
            -params->l1_gain[0] * residual.x - model_decay * state->disturbance_estimate.x,
            -params->l1_gain[1] * residual.y - model_decay * state->disturbance_estimate.y,
            -params->l1_gain[2] * residual.z - model_decay * state->disturbance_estimate.z);
        state->disturbance_estimate = c_clamp_vec3(
            c_add(
                c_scale(state->disturbance_estimate, 1.0 - alpha),
                c_scale(
                    c_add(state->disturbance_estimate, c_scale(adaptive_update, measurement_dt)),
                    alpha)),
            params->l1_comp_limit);
    }

    {
        const MosimPx4ctrlG9FamilyCVec3 drag_feedforward = c_vec3(
            -params->drag_feedforward_gain[0] * input->reference_velocity.x,
            -params->drag_feedforward_gain[1] * input->reference_velocity.y,
            -params->drag_feedforward_gain[2] * input->reference_velocity.z);
        const MosimPx4ctrlG9FamilyCVec3 compensated_acceleration_no_gravity =
            c_add(c_add(nominal_acceleration_no_gravity, state->disturbance_estimate), drag_feedforward);
        state->previous_command_acceleration = compensated_acceleration_no_gravity;
        out->desired_acceleration = c_vec3(
            compensated_acceleration_no_gravity.x,
            compensated_acceleration_no_gravity.y,
            compensated_acceleration_no_gravity.z + params->gravity);
    }

    c_fill_attitude_thrust_output(params, state, input, out, 1);
    out->sliding_surface = residual;
    out->disturbance_estimate = state->disturbance_estimate;
}

static void c_safety_filter_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    const MosimPx4ctrlG9FamilyCVec3 nominal_acceleration_no_gravity =
        c_pid_acceleration_no_gravity(params, state, input, out);
    const MosimPx4ctrlG9FamilyCVec3 limited_acceleration_no_gravity =
        c_clamp_vec3(nominal_acceleration_no_gravity, params->safety_accel_limit);
    const double saturated_before_attitude =
        c_vec3_components_equal(nominal_acceleration_no_gravity, limited_acceleration_no_gravity) ? 0.0 : 1.0;

    out->saturated = saturated_before_attitude;
    out->sliding_surface = c_subtract(nominal_acceleration_no_gravity, limited_acceleration_no_gravity);
    state->previous_command_acceleration = limited_acceleration_no_gravity;
    out->desired_acceleration = c_vec3(
        limited_acceleration_no_gravity.x,
        limited_acceleration_no_gravity.y,
        limited_acceleration_no_gravity.z + params->gravity);
    c_fill_attitude_thrust_output(params, state, input, out, 1);
    out->saturated = out->saturated || saturated_before_attitude;
    out->status_code = out->saturated ? 2 : 0;
}

static void c_fault_allocation_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    int i;
    double min_efficiency = 1.0;
    double mean_efficiency = 0.0;
    double missing_authority;
    double requested_multiplier;
    double bounded_multiplier;
    double uncompensated_thrust;
    double full_thrust_n;
    const MosimPx4ctrlG9FamilyCVec3 nominal_acceleration_no_gravity =
        c_pid_acceleration_no_gravity(params, state, input, out);

    state->previous_command_acceleration = nominal_acceleration_no_gravity;
    out->desired_acceleration = c_vec3(
        nominal_acceleration_no_gravity.x,
        nominal_acceleration_no_gravity.y,
        nominal_acceleration_no_gravity.z + params->gravity);
    c_fill_attitude_thrust_output(params, state, input, out, 1);

    for (i = 0; i < 4; ++i)
    {
        const double eta = c_clamp(
            params->fault_rotor_efficiency[i],
            c_safe_positive(params->fault_min_efficiency, 0.01),
            1.0);
        if (eta < min_efficiency)
        {
            min_efficiency = eta;
        }
        mean_efficiency += eta;
    }
    mean_efficiency *= 0.25;

    missing_authority = c_clamp(1.0 - mean_efficiency, 0.0, 1.0);
    requested_multiplier = 1.0 + c_clamp(params->fault_allocation_blend, 0.0, 1.0) * missing_authority;
    bounded_multiplier = c_clamp(
        requested_multiplier,
        1.0,
        1.0 + c_safe_nonnegative(params->fault_thrust_comp_limit));
    uncompensated_thrust = out->normalized_thrust;
    out->normalized_thrust = c_clamp(
        uncompensated_thrust * bounded_multiplier,
        params->min_normalized_thrust,
        params->max_normalized_thrust);
    full_thrust_n = params->mass * params->gravity / params->hover_percentage;
    out->collective_thrust_n = out->normalized_thrust * full_thrust_n;
    out->desired_force_n = c_vec3(
        out->desired_force_n.x,
        out->desired_force_n.y,
        out->desired_force_n.z * bounded_multiplier);
    out->saturated = out->saturated ||
        missing_authority > 1.0e-12 ||
        fabs(out->normalized_thrust - uncompensated_thrust * bounded_multiplier) > 1.0e-12;
    out->disturbance_estimate = c_vec3(
        missing_authority,
        min_efficiency,
        bounded_multiplier - 1.0);
    out->sliding_surface = c_vec3(
        params->fault_rotor_efficiency[0],
        params->fault_rotor_efficiency[1],
        params->fault_rotor_efficiency[2]);
    out->status_code = missing_authority > 1.0e-12 ? 3 : 0;
}

void mosim_px4ctrl_g9_family_c_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *output)
{
    memset(output, 0, sizeof(*output));
    output->desired_attitude = c_quat(1.0, 0.0, 0.0, 0.0);
    if (input->reset)
    {
        mosim_px4ctrl_g9_family_c_reset(params, state);
    }
    if (!input->enable)
    {
        *output = c_disabled_output(input);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G9_OFFICIAL_PID)
    {
        const MosimPx4ctrlG9FamilyCVec3 acc =
            c_pid_acceleration_no_gravity(params, state, input, output);
        output->desired_acceleration = c_vec3(acc.x, acc.y, acc.z + params->gravity);
        c_fill_attitude_thrust_output(params, state, input, output, 1);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G9_SE3_BASIC ||
        input->controller_id == MOSIM_PX4CTRL_G9_DFBC_BASIC)
    {
        c_se3_or_dfbc_basic_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G9_SMC_BOUNDARY_LAYER)
    {
        c_smc_boundary_layer_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G9_PID_INDI)
    {
        c_pid_indi_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G9_NMPC_OUTER)
    {
        c_nmpc_outer_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G10_L1_AWFF)
    {
        c_l1_awff_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G10_SAFETY_FILTER)
    {
        c_safety_filter_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G10_FAULT_ALLOCATION)
    {
        c_fault_allocation_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_P10_DFBC_HIGH_ORDER)
    {
        c_dfbc_high_order_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_P10_DFBC_SMOOTH_ROBUST)
    {
        c_dfbc_smooth_robust_step(params, state, input, output);
        return;
    }
    *output = c_disabled_output(input);
    output->status_code = 2;
}

void MosimPx4ctrlG9FamilyCStepScalar(
    double controller_id,
    double dt,
    double position_x,
    double position_y,
    double position_z,
    double velocity_x,
    double velocity_y,
    double velocity_z,
    double attitude_w,
    double attitude_x,
    double attitude_y,
    double attitude_z,
    double angular_velocity_x,
    double angular_velocity_y,
    double angular_velocity_z,
    double reference_position_x,
    double reference_position_y,
    double reference_position_z,
    double reference_velocity_x,
    double reference_velocity_y,
    double reference_velocity_z,
    double reference_acceleration_x,
    double reference_acceleration_y,
    double reference_acceleration_z,
    double reference_jerk_x,
    double reference_jerk_y,
    double reference_jerk_z,
    double reference_snap_x,
    double reference_snap_y,
    double reference_snap_z,
    double reference_yaw,
    double reference_yaw_rate,
    double reference_yaw_acceleration,
    double measurement_stamp_s,
    double imu_attitude_w,
    double imu_attitude_x,
    double imu_attitude_y,
    double imu_attitude_z,
    double imu_angular_velocity_x,
    double imu_angular_velocity_y,
    double imu_angular_velocity_z,
    double enable,
    double reset,
    double measurement_stamp_valid,
    double enable_disturbance_observer,
    double kp_x,
    double kp_y,
    double kp_z,
    double kv_x,
    double kv_y,
    double kv_z,
    double ki_x,
    double ki_y,
    double ki_z,
    double smc_lambda_x,
    double smc_lambda_y,
    double smc_lambda_z,
    double smc_eta_x,
    double smc_eta_y,
    double smc_eta_z,
    double smc_phi_x,
    double smc_phi_y,
    double smc_phi_z,
    double smc_surface_limit_x,
    double smc_surface_limit_y,
    double smc_surface_limit_z,
    double indi_gain_x,
    double indi_gain_y,
    double indi_gain_z,
    double indi_increment_limit_x,
    double indi_increment_limit_y,
    double indi_increment_limit_z,
    double indi_measured_accel_limit_x,
    double indi_measured_accel_limit_y,
    double indi_measured_accel_limit_z,
    double indi_accel_lpf_alpha,
    double nmpc_horizon_s,
    double nmpc_position_weight_x,
    double nmpc_position_weight_y,
    double nmpc_position_weight_z,
    double nmpc_velocity_weight_x,
    double nmpc_velocity_weight_y,
    double nmpc_velocity_weight_z,
    double nmpc_control_weight_x,
    double nmpc_control_weight_y,
    double nmpc_control_weight_z,
    double nmpc_accel_limit_x,
    double nmpc_accel_limit_y,
    double nmpc_accel_limit_z,
    double nmpc_increment_limit_x,
    double nmpc_increment_limit_y,
    double nmpc_increment_limit_z,
    double high_order_body_rate_limit_x,
    double high_order_body_rate_limit_y,
    double high_order_body_rate_limit_z,
    double high_order_body_accel_limit_x,
    double high_order_body_accel_limit_y,
    double high_order_body_accel_limit_z,
    double smooth_feedback_gain_x,
    double smooth_feedback_gain_y,
    double smooth_feedback_gain_z,
    double smooth_feedback_bound_x,
    double smooth_feedback_bound_y,
    double smooth_feedback_bound_z,
    double disturbance_observer_gain_x,
    double disturbance_observer_gain_y,
    double disturbance_observer_gain_z,
    double disturbance_compensation_limit_x,
    double disturbance_compensation_limit_y,
    double disturbance_compensation_limit_z,
    double l1_model_decay,
    double l1_filter_T,
    double l1_gain_x,
    double l1_gain_y,
    double l1_gain_z,
    double l1_comp_limit_x,
    double l1_comp_limit_y,
    double l1_comp_limit_z,
    double drag_feedforward_gain_x,
    double drag_feedforward_gain_y,
    double drag_feedforward_gain_z,
    double safety_accel_limit_x,
    double safety_accel_limit_y,
    double safety_accel_limit_z,
    double fault_rotor_efficiency_1,
    double fault_rotor_efficiency_2,
    double fault_rotor_efficiency_3,
    double fault_rotor_efficiency_4,
    double fault_allocation_blend,
    double fault_min_efficiency,
    double fault_thrust_comp_limit,
    double integral_limit_x,
    double integral_limit_y,
    double integral_limit_z,
    double mass,
    double gravity,
    double hover_percentage,
    double min_normalized_thrust,
    double max_normalized_thrust,
    double tilt_limit_rad,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *normalized_thrust,
    double *collective_thrust_N,
    double *position_error_x,
    double *position_error_y,
    double *position_error_z,
    double *velocity_error_x,
    double *velocity_error_y,
    double *velocity_error_z,
    double *sliding_surface_x,
    double *sliding_surface_y,
    double *sliding_surface_z,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *desired_body_rate_x,
    double *desired_body_rate_y,
    double *desired_body_rate_z,
    double *desired_body_acceleration_x,
    double *desired_body_acceleration_y,
    double *desired_body_acceleration_z,
    double *disturbance_estimate_x,
    double *disturbance_estimate_y,
    double *disturbance_estimate_z,
    double *desired_force_N_x,
    double *desired_force_N_y,
    double *desired_force_N_z,
    double *saturated,
    double *status_code)
{
    static MosimPx4ctrlG9FamilyCState states[12];
    static int initialized[12] = {0};
    MosimPx4ctrlG9FamilyCParams params;
    MosimPx4ctrlG9FamilyCInput input;
    MosimPx4ctrlG9FamilyCOutput output;

    params.kp[0] = kp_x;
    params.kp[1] = kp_y;
    params.kp[2] = kp_z;
    params.kv[0] = kv_x;
    params.kv[1] = kv_y;
    params.kv[2] = kv_z;
    params.ki[0] = ki_x;
    params.ki[1] = ki_y;
    params.ki[2] = ki_z;
    params.smc_lambda[0] = smc_lambda_x;
    params.smc_lambda[1] = smc_lambda_y;
    params.smc_lambda[2] = smc_lambda_z;
    params.smc_eta[0] = smc_eta_x;
    params.smc_eta[1] = smc_eta_y;
    params.smc_eta[2] = smc_eta_z;
    params.smc_phi[0] = smc_phi_x;
    params.smc_phi[1] = smc_phi_y;
    params.smc_phi[2] = smc_phi_z;
    params.smc_surface_limit[0] = smc_surface_limit_x;
    params.smc_surface_limit[1] = smc_surface_limit_y;
    params.smc_surface_limit[2] = smc_surface_limit_z;
    params.indi_gain[0] = indi_gain_x;
    params.indi_gain[1] = indi_gain_y;
    params.indi_gain[2] = indi_gain_z;
    params.indi_increment_limit[0] = indi_increment_limit_x;
    params.indi_increment_limit[1] = indi_increment_limit_y;
    params.indi_increment_limit[2] = indi_increment_limit_z;
    params.indi_measured_accel_limit[0] = indi_measured_accel_limit_x;
    params.indi_measured_accel_limit[1] = indi_measured_accel_limit_y;
    params.indi_measured_accel_limit[2] = indi_measured_accel_limit_z;
    params.indi_accel_lpf_alpha = indi_accel_lpf_alpha;
    params.nmpc_horizon_s = nmpc_horizon_s;
    params.nmpc_position_weight[0] = nmpc_position_weight_x;
    params.nmpc_position_weight[1] = nmpc_position_weight_y;
    params.nmpc_position_weight[2] = nmpc_position_weight_z;
    params.nmpc_velocity_weight[0] = nmpc_velocity_weight_x;
    params.nmpc_velocity_weight[1] = nmpc_velocity_weight_y;
    params.nmpc_velocity_weight[2] = nmpc_velocity_weight_z;
    params.nmpc_control_weight[0] = nmpc_control_weight_x;
    params.nmpc_control_weight[1] = nmpc_control_weight_y;
    params.nmpc_control_weight[2] = nmpc_control_weight_z;
    params.nmpc_accel_limit[0] = nmpc_accel_limit_x;
    params.nmpc_accel_limit[1] = nmpc_accel_limit_y;
    params.nmpc_accel_limit[2] = nmpc_accel_limit_z;
    params.nmpc_increment_limit[0] = nmpc_increment_limit_x;
    params.nmpc_increment_limit[1] = nmpc_increment_limit_y;
    params.nmpc_increment_limit[2] = nmpc_increment_limit_z;
    params.high_order_body_rate_limit[0] = high_order_body_rate_limit_x;
    params.high_order_body_rate_limit[1] = high_order_body_rate_limit_y;
    params.high_order_body_rate_limit[2] = high_order_body_rate_limit_z;
    params.high_order_body_accel_limit[0] = high_order_body_accel_limit_x;
    params.high_order_body_accel_limit[1] = high_order_body_accel_limit_y;
    params.high_order_body_accel_limit[2] = high_order_body_accel_limit_z;
    params.smooth_feedback_gain[0] = smooth_feedback_gain_x;
    params.smooth_feedback_gain[1] = smooth_feedback_gain_y;
    params.smooth_feedback_gain[2] = smooth_feedback_gain_z;
    params.smooth_feedback_bound[0] = smooth_feedback_bound_x;
    params.smooth_feedback_bound[1] = smooth_feedback_bound_y;
    params.smooth_feedback_bound[2] = smooth_feedback_bound_z;
    params.disturbance_observer_gain[0] = disturbance_observer_gain_x;
    params.disturbance_observer_gain[1] = disturbance_observer_gain_y;
    params.disturbance_observer_gain[2] = disturbance_observer_gain_z;
    params.disturbance_compensation_limit[0] = disturbance_compensation_limit_x;
    params.disturbance_compensation_limit[1] = disturbance_compensation_limit_y;
    params.disturbance_compensation_limit[2] = disturbance_compensation_limit_z;
    params.l1_model_decay = l1_model_decay;
    params.l1_filter_T = l1_filter_T;
    params.l1_gain[0] = l1_gain_x;
    params.l1_gain[1] = l1_gain_y;
    params.l1_gain[2] = l1_gain_z;
    params.l1_comp_limit[0] = l1_comp_limit_x;
    params.l1_comp_limit[1] = l1_comp_limit_y;
    params.l1_comp_limit[2] = l1_comp_limit_z;
    params.drag_feedforward_gain[0] = drag_feedforward_gain_x;
    params.drag_feedforward_gain[1] = drag_feedforward_gain_y;
    params.drag_feedforward_gain[2] = drag_feedforward_gain_z;
    params.safety_accel_limit[0] = safety_accel_limit_x;
    params.safety_accel_limit[1] = safety_accel_limit_y;
    params.safety_accel_limit[2] = safety_accel_limit_z;
    params.fault_rotor_efficiency[0] = fault_rotor_efficiency_1;
    params.fault_rotor_efficiency[1] = fault_rotor_efficiency_2;
    params.fault_rotor_efficiency[2] = fault_rotor_efficiency_3;
    params.fault_rotor_efficiency[3] = fault_rotor_efficiency_4;
    params.fault_allocation_blend = fault_allocation_blend;
    params.fault_min_efficiency = fault_min_efficiency;
    params.fault_thrust_comp_limit = fault_thrust_comp_limit;
    params.integral_limit[0] = integral_limit_x;
    params.integral_limit[1] = integral_limit_y;
    params.integral_limit[2] = integral_limit_z;
    params.mass = mass;
    params.gravity = gravity;
    params.hover_percentage = hover_percentage;
    params.min_normalized_thrust = min_normalized_thrust;
    params.max_normalized_thrust = max_normalized_thrust;
    params.tilt_limit_rad = tilt_limit_rad;

    input.controller_id = (int)controller_id;
    input.dt = dt;
    input.position = c_vec3(position_x, position_y, position_z);
    input.velocity = c_vec3(velocity_x, velocity_y, velocity_z);
    input.attitude = c_quat(attitude_w, attitude_x, attitude_y, attitude_z);
    input.angular_velocity = c_vec3(angular_velocity_x, angular_velocity_y, angular_velocity_z);
    input.reference_position = c_vec3(reference_position_x, reference_position_y, reference_position_z);
    input.reference_velocity = c_vec3(reference_velocity_x, reference_velocity_y, reference_velocity_z);
    input.reference_acceleration = c_vec3(reference_acceleration_x, reference_acceleration_y, reference_acceleration_z);
    input.reference_jerk = c_vec3(reference_jerk_x, reference_jerk_y, reference_jerk_z);
    input.reference_snap = c_vec3(reference_snap_x, reference_snap_y, reference_snap_z);
    input.reference_yaw = reference_yaw;
    input.reference_yaw_rate = reference_yaw_rate;
    input.reference_yaw_acceleration = reference_yaw_acceleration;
    input.measurement_stamp_s = measurement_stamp_s;
    input.imu_attitude = c_quat(imu_attitude_w, imu_attitude_x, imu_attitude_y, imu_attitude_z);
    input.imu_angular_velocity = c_vec3(imu_angular_velocity_x, imu_angular_velocity_y, imu_angular_velocity_z);
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    input.measurement_stamp_valid = measurement_stamp_valid != 0.0;
    input.enable_disturbance_observer = enable_disturbance_observer != 0.0;

    {
        int state_index = input.controller_id;
        if (state_index < 0 || state_index > 11)
        {
            state_index = 0;
        }
        if (!initialized[state_index])
        {
            mosim_px4ctrl_g9_family_c_reset(&params, &states[state_index]);
            initialized[state_index] = 1;
        }
        mosim_px4ctrl_g9_family_c_step(&params, &states[state_index], &input, &output);
    }

    *desired_attitude_w = output.desired_attitude.w;
    *desired_attitude_x = output.desired_attitude.x;
    *desired_attitude_y = output.desired_attitude.y;
    *desired_attitude_z = output.desired_attitude.z;
    *normalized_thrust = output.normalized_thrust;
    *collective_thrust_N = output.collective_thrust_n;
    *position_error_x = output.position_error.x;
    *position_error_y = output.position_error.y;
    *position_error_z = output.position_error.z;
    *velocity_error_x = output.velocity_error.x;
    *velocity_error_y = output.velocity_error.y;
    *velocity_error_z = output.velocity_error.z;
    *sliding_surface_x = output.sliding_surface.x;
    *sliding_surface_y = output.sliding_surface.y;
    *sliding_surface_z = output.sliding_surface.z;
    *desired_acceleration_x = output.desired_acceleration.x;
    *desired_acceleration_y = output.desired_acceleration.y;
    *desired_acceleration_z = output.desired_acceleration.z;
    *desired_body_rate_x = output.desired_body_rate.x;
    *desired_body_rate_y = output.desired_body_rate.y;
    *desired_body_rate_z = output.desired_body_rate.z;
    *desired_body_acceleration_x = output.desired_body_acceleration.x;
    *desired_body_acceleration_y = output.desired_body_acceleration.y;
    *desired_body_acceleration_z = output.desired_body_acceleration.z;
    *disturbance_estimate_x = output.disturbance_estimate.x;
    *disturbance_estimate_y = output.disturbance_estimate.y;
    *disturbance_estimate_z = output.disturbance_estimate.z;
    *desired_force_N_x = output.desired_force_n.x;
    *desired_force_N_y = output.desired_force_n.y;
    *desired_force_N_z = output.desired_force_n.z;
    *saturated = output.saturated;
    *status_code = (double)output.status_code;
}
");
    end func_CFunction;

    SysplorerEmbeddedCoder.Port.Inport controller_id
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport dt
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport position_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport position_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport position_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport velocity_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport velocity_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport velocity_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport attitude_w
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport attitude_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport attitude_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport attitude_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport angular_velocity_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport angular_velocity_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport angular_velocity_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_position_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_position_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_position_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_velocity_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_velocity_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_velocity_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_jerk_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_jerk_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_jerk_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_snap_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_snap_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_snap_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_yaw
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_yaw_rate
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_yaw_acceleration
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport measurement_stamp_s
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport imu_attitude_w
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport imu_attitude_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport imu_attitude_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport imu_attitude_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport imu_angular_velocity_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport imu_angular_velocity_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport imu_angular_velocity_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport enable
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reset
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport measurement_stamp_valid
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport enable_disturbance_observer
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport kp_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport kp_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport kp_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport kv_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport kv_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport kv_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport ki_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport ki_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport ki_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_lambda_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_lambda_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_lambda_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_eta_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_eta_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_eta_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_phi_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_phi_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_phi_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_surface_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_surface_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smc_surface_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport indi_gain_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport indi_gain_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport indi_gain_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport indi_increment_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport indi_increment_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport indi_increment_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport indi_measured_accel_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport indi_measured_accel_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport indi_measured_accel_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport indi_accel_lpf_alpha
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_horizon_s
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_position_weight_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_position_weight_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_position_weight_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_velocity_weight_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_velocity_weight_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_velocity_weight_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_control_weight_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_control_weight_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_control_weight_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_accel_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_accel_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_accel_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_increment_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_increment_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport nmpc_increment_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport high_order_body_rate_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport high_order_body_rate_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport high_order_body_rate_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport high_order_body_accel_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport high_order_body_accel_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport high_order_body_accel_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smooth_feedback_gain_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smooth_feedback_gain_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smooth_feedback_gain_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smooth_feedback_bound_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smooth_feedback_bound_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport smooth_feedback_bound_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport disturbance_observer_gain_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport disturbance_observer_gain_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport disturbance_observer_gain_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport disturbance_compensation_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport disturbance_compensation_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport disturbance_compensation_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport l1_model_decay
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport l1_filter_T
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport l1_gain_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport l1_gain_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport l1_gain_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport l1_comp_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport l1_comp_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport l1_comp_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport drag_feedforward_gain_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport drag_feedforward_gain_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport drag_feedforward_gain_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport safety_accel_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport safety_accel_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport safety_accel_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fault_rotor_efficiency_1
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fault_rotor_efficiency_2
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fault_rotor_efficiency_3
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fault_rotor_efficiency_4
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fault_allocation_blend
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fault_min_efficiency
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fault_thrust_comp_limit
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport integral_limit_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport integral_limit_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport integral_limit_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport mass
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport gravity
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport hover_percentage
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport min_normalized_thrust
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport max_normalized_thrust
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport tilt_limit_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_attitude_w
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_attitude_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_attitude_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_attitude_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport normalized_thrust
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport collective_thrust_N
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport position_error_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport position_error_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport position_error_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport velocity_error_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport velocity_error_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport velocity_error_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport sliding_surface_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport sliding_surface_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport sliding_surface_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_body_rate_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_body_rate_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_body_rate_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_body_acceleration_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_body_acceleration_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_body_acceleration_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport disturbance_estimate_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport disturbance_estimate_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport disturbance_estimate_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_force_N_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_force_N_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_force_N_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport saturated
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport status_code
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
  equation
    (desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, normalized_thrust, collective_thrust_N, position_error_x, position_error_y, position_error_z, velocity_error_x, velocity_error_y, velocity_error_z, sliding_surface_x, sliding_surface_y, sliding_surface_z, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, desired_body_rate_x, desired_body_rate_y, desired_body_rate_z, desired_body_acceleration_x, desired_body_acceleration_y, desired_body_acceleration_z, disturbance_estimate_x, disturbance_estimate_y, disturbance_estimate_z, desired_force_N_x, desired_force_N_y, desired_force_N_z, saturated, status_code) = func_CFunction(controller_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, attitude_w, attitude_x, attitude_y, attitude_z, angular_velocity_x, angular_velocity_y, angular_velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_jerk_x, reference_jerk_y, reference_jerk_z, reference_snap_x, reference_snap_y, reference_snap_z, reference_yaw, reference_yaw_rate, reference_yaw_acceleration, measurement_stamp_s, imu_attitude_w, imu_attitude_x, imu_attitude_y, imu_attitude_z, imu_angular_velocity_x, imu_angular_velocity_y, imu_angular_velocity_z, enable, reset, measurement_stamp_valid, enable_disturbance_observer, kp_x, kp_y, kp_z, kv_x, kv_y, kv_z, ki_x, ki_y, ki_z, smc_lambda_x, smc_lambda_y, smc_lambda_z, smc_eta_x, smc_eta_y, smc_eta_z, smc_phi_x, smc_phi_y, smc_phi_z, smc_surface_limit_x, smc_surface_limit_y, smc_surface_limit_z, indi_gain_x, indi_gain_y, indi_gain_z, indi_increment_limit_x, indi_increment_limit_y, indi_increment_limit_z, indi_measured_accel_limit_x, indi_measured_accel_limit_y, indi_measured_accel_limit_z, indi_accel_lpf_alpha, nmpc_horizon_s, nmpc_position_weight_x, nmpc_position_weight_y, nmpc_position_weight_z
, nmpc_velocity_weight_x, nmpc_velocity_weight_y, nmpc_velocity_weight_z, nmpc_control_weight_x, nmpc_control_weight_y, nmpc_control_weight_z, nmpc_accel_limit_x, nmpc_accel_limit_y, nmpc_accel_limit_z, nmpc_increment_limit_x, nmpc_increment_limit_y, nmpc_increment_limit_z, high_order_body_rate_limit_x, high_order_body_rate_limit_y, high_order_body_rate_limit_z, high_order_body_accel_limit_x, high_order_body_accel_limit_y, high_order_body_accel_limit_z, smooth_feedback_gain_x, smooth_feedback_gain_y, smooth_feedback_gain_z, smooth_feedback_bound_x, smooth_feedback_bound_y, smooth_feedback_bound_z, disturbance_observer_gain_x, disturbance_observer_gain_y, disturbance_observer_gain_z, disturbance_compensation_limit_x, disturbance_compensation_limit_y, disturbance_compensation_limit_z, l1_model_decay, l1_filter_T, l1_gain_x, l1_gain_y, l1_gain_z, l1_comp_limit_x, l1_comp_limit_y, l1_comp_limit_z, drag_feedforward_gain_x, drag_feedforward_gain_y, drag_feedforward_gain_z, safety_accel_limit_x, safety_accel_limit_y, safety_accel_limit_z, fault_rotor_efficiency_1, fault_rotor_efficiency_2, fault_rotor_efficiency_3, fault_rotor_efficiency_4, fault_allocation_blend, fault_min_efficiency, fault_thrust_comp_limit, integral_limit_x, integral_limit_y, integral_limit_z, mass, gravity, hover_percentage, min_normalized_thrust, max_normalized_thrust, tilt_limit_rad);
  end CFunction;

equation
  connect(controller_id_in, cFunction.controller_id) annotation(Line(points={{-492,1668.00},{-80,1668.00}},color={0,0,127}));
  connect(dt_in, cFunction.dt) annotation(Line(points={{-492,1644.00},{-80,1644.00}},color={0,0,127}));
  connect(position_x_in, cFunction.position_x) annotation(Line(points={{-492,1620.00},{-80,1620.00}},color={0,0,127}));
  connect(position_y_in, cFunction.position_y) annotation(Line(points={{-492,1596.00},{-80,1596.00}},color={0,0,127}));
  connect(position_z_in, cFunction.position_z) annotation(Line(points={{-492,1572.00},{-80,1572.00}},color={0,0,127}));
  connect(velocity_x_in, cFunction.velocity_x) annotation(Line(points={{-492,1548.00},{-80,1548.00}},color={0,0,127}));
  connect(velocity_y_in, cFunction.velocity_y) annotation(Line(points={{-492,1524.00},{-80,1524.00}},color={0,0,127}));
  connect(velocity_z_in, cFunction.velocity_z) annotation(Line(points={{-492,1500.00},{-80,1500.00}},color={0,0,127}));
  connect(attitude_w_in, cFunction.attitude_w) annotation(Line(points={{-492,1476.00},{-80,1476.00}},color={0,0,127}));
  connect(attitude_x_in, cFunction.attitude_x) annotation(Line(points={{-492,1452.00},{-80,1452.00}},color={0,0,127}));
  connect(attitude_y_in, cFunction.attitude_y) annotation(Line(points={{-492,1428.00},{-80,1428.00}},color={0,0,127}));
  connect(attitude_z_in, cFunction.attitude_z) annotation(Line(points={{-492,1404.00},{-80,1404.00}},color={0,0,127}));
  connect(angular_velocity_x_in, cFunction.angular_velocity_x) annotation(Line(points={{-492,1380.00},{-80,1380.00}},color={0,0,127}));
  connect(angular_velocity_y_in, cFunction.angular_velocity_y) annotation(Line(points={{-492,1356.00},{-80,1356.00}},color={0,0,127}));
  connect(angular_velocity_z_in, cFunction.angular_velocity_z) annotation(Line(points={{-492,1332.00},{-80,1332.00}},color={0,0,127}));
  connect(reference_position_x_in, cFunction.reference_position_x) annotation(Line(points={{-492,1308.00},{-80,1308.00}},color={0,0,127}));
  connect(reference_position_y_in, cFunction.reference_position_y) annotation(Line(points={{-492,1284.00},{-80,1284.00}},color={0,0,127}));
  connect(reference_position_z_in, cFunction.reference_position_z) annotation(Line(points={{-492,1260.00},{-80,1260.00}},color={0,0,127}));
  connect(reference_velocity_x_in, cFunction.reference_velocity_x) annotation(Line(points={{-492,1236.00},{-80,1236.00}},color={0,0,127}));
  connect(reference_velocity_y_in, cFunction.reference_velocity_y) annotation(Line(points={{-492,1212.00},{-80,1212.00}},color={0,0,127}));
  connect(reference_velocity_z_in, cFunction.reference_velocity_z) annotation(Line(points={{-492,1188.00},{-80,1188.00}},color={0,0,127}));
  connect(reference_acceleration_x_in, cFunction.reference_acceleration_x) annotation(Line(points={{-492,1164.00},{-80,1164.00}},color={0,0,127}));
  connect(reference_acceleration_y_in, cFunction.reference_acceleration_y) annotation(Line(points={{-492,1140.00},{-80,1140.00}},color={0,0,127}));
  connect(reference_acceleration_z_in, cFunction.reference_acceleration_z) annotation(Line(points={{-492,1116.00},{-80,1116.00}},color={0,0,127}));
  connect(reference_jerk_x_in, cFunction.reference_jerk_x) annotation(Line(points={{-492,1092.00},{-80,1092.00}},color={0,0,127}));
  connect(reference_jerk_y_in, cFunction.reference_jerk_y) annotation(Line(points={{-492,1068.00},{-80,1068.00}},color={0,0,127}));
  connect(reference_jerk_z_in, cFunction.reference_jerk_z) annotation(Line(points={{-492,1044.00},{-80,1044.00}},color={0,0,127}));
  connect(reference_snap_x_in, cFunction.reference_snap_x) annotation(Line(points={{-492,1020.00},{-80,1020.00}},color={0,0,127}));
  connect(reference_snap_y_in, cFunction.reference_snap_y) annotation(Line(points={{-492,996.00},{-80,996.00}},color={0,0,127}));
  connect(reference_snap_z_in, cFunction.reference_snap_z) annotation(Line(points={{-492,972.00},{-80,972.00}},color={0,0,127}));
  connect(reference_yaw_in, cFunction.reference_yaw) annotation(Line(points={{-492,948.00},{-80,948.00}},color={0,0,127}));
  connect(reference_yaw_rate_in, cFunction.reference_yaw_rate) annotation(Line(points={{-492,924.00},{-80,924.00}},color={0,0,127}));
  connect(reference_yaw_acceleration_in, cFunction.reference_yaw_acceleration) annotation(Line(points={{-492,900.00},{-80,900.00}},color={0,0,127}));
  connect(measurement_stamp_s_in, cFunction.measurement_stamp_s) annotation(Line(points={{-492,876.00},{-80,876.00}},color={0,0,127}));
  connect(imu_attitude_w_in, cFunction.imu_attitude_w) annotation(Line(points={{-492,852.00},{-80,852.00}},color={0,0,127}));
  connect(imu_attitude_x_in, cFunction.imu_attitude_x) annotation(Line(points={{-492,828.00},{-80,828.00}},color={0,0,127}));
  connect(imu_attitude_y_in, cFunction.imu_attitude_y) annotation(Line(points={{-492,804.00},{-80,804.00}},color={0,0,127}));
  connect(imu_attitude_z_in, cFunction.imu_attitude_z) annotation(Line(points={{-492,780.00},{-80,780.00}},color={0,0,127}));
  connect(imu_angular_velocity_x_in, cFunction.imu_angular_velocity_x) annotation(Line(points={{-492,756.00},{-80,756.00}},color={0,0,127}));
  connect(imu_angular_velocity_y_in, cFunction.imu_angular_velocity_y) annotation(Line(points={{-492,732.00},{-80,732.00}},color={0,0,127}));
  connect(imu_angular_velocity_z_in, cFunction.imu_angular_velocity_z) annotation(Line(points={{-492,708.00},{-80,708.00}},color={0,0,127}));
  connect(enable_in, cFunction.enable) annotation(Line(points={{-492,684.00},{-80,684.00}},color={0,0,127}));
  connect(reset_in, cFunction.reset) annotation(Line(points={{-492,660.00},{-80,660.00}},color={0,0,127}));
  connect(measurement_stamp_valid_in, cFunction.measurement_stamp_valid) annotation(Line(points={{-492,636.00},{-80,636.00}},color={0,0,127}));
  connect(enable_disturbance_observer_in, cFunction.enable_disturbance_observer) annotation(Line(points={{-492,612.00},{-80,612.00}},color={0,0,127}));
  connect(kp_x_in, cFunction.kp_x) annotation(Line(points={{-492,588.00},{-80,588.00}},color={0,0,127}));
  connect(kp_y_in, cFunction.kp_y) annotation(Line(points={{-492,564.00},{-80,564.00}},color={0,0,127}));
  connect(kp_z_in, cFunction.kp_z) annotation(Line(points={{-492,540.00},{-80,540.00}},color={0,0,127}));
  connect(kv_x_in, cFunction.kv_x) annotation(Line(points={{-492,516.00},{-80,516.00}},color={0,0,127}));
  connect(kv_y_in, cFunction.kv_y) annotation(Line(points={{-492,492.00},{-80,492.00}},color={0,0,127}));
  connect(kv_z_in, cFunction.kv_z) annotation(Line(points={{-492,468.00},{-80,468.00}},color={0,0,127}));
  connect(ki_x_in, cFunction.ki_x) annotation(Line(points={{-492,444.00},{-80,444.00}},color={0,0,127}));
  connect(ki_y_in, cFunction.ki_y) annotation(Line(points={{-492,420.00},{-80,420.00}},color={0,0,127}));
  connect(ki_z_in, cFunction.ki_z) annotation(Line(points={{-492,396.00},{-80,396.00}},color={0,0,127}));
  connect(smc_lambda_x_in, cFunction.smc_lambda_x) annotation(Line(points={{-492,372.00},{-80,372.00}},color={0,0,127}));
  connect(smc_lambda_y_in, cFunction.smc_lambda_y) annotation(Line(points={{-492,348.00},{-80,348.00}},color={0,0,127}));
  connect(smc_lambda_z_in, cFunction.smc_lambda_z) annotation(Line(points={{-492,324.00},{-80,324.00}},color={0,0,127}));
  connect(smc_eta_x_in, cFunction.smc_eta_x) annotation(Line(points={{-492,300.00},{-80,300.00}},color={0,0,127}));
  connect(smc_eta_y_in, cFunction.smc_eta_y) annotation(Line(points={{-492,276.00},{-80,276.00}},color={0,0,127}));
  connect(smc_eta_z_in, cFunction.smc_eta_z) annotation(Line(points={{-492,252.00},{-80,252.00}},color={0,0,127}));
  connect(smc_phi_x_in, cFunction.smc_phi_x) annotation(Line(points={{-492,228.00},{-80,228.00}},color={0,0,127}));
  connect(smc_phi_y_in, cFunction.smc_phi_y) annotation(Line(points={{-492,204.00},{-80,204.00}},color={0,0,127}));
  connect(smc_phi_z_in, cFunction.smc_phi_z) annotation(Line(points={{-492,180.00},{-80,180.00}},color={0,0,127}));
  connect(smc_surface_limit_x_in, cFunction.smc_surface_limit_x) annotation(Line(points={{-492,156.00},{-80,156.00}},color={0,0,127}));
  connect(smc_surface_limit_y_in, cFunction.smc_surface_limit_y) annotation(Line(points={{-492,132.00},{-80,132.00}},color={0,0,127}));
  connect(smc_surface_limit_z_in, cFunction.smc_surface_limit_z) annotation(Line(points={{-492,108.00},{-80,108.00}},color={0,0,127}));
  connect(indi_gain_x_in, cFunction.indi_gain_x) annotation(Line(points={{-492,84.00},{-80,84.00}},color={0,0,127}));
  connect(indi_gain_y_in, cFunction.indi_gain_y) annotation(Line(points={{-492,60.00},{-80,60.00}},color={0,0,127}));
  connect(indi_gain_z_in, cFunction.indi_gain_z) annotation(Line(points={{-492,36.00},{-80,36.00}},color={0,0,127}));
  connect(indi_increment_limit_x_in, cFunction.indi_increment_limit_x) annotation(Line(points={{-492,12.00},{-80,12.00}},color={0,0,127}));
  connect(indi_increment_limit_y_in, cFunction.indi_increment_limit_y) annotation(Line(points={{-492,-12.00},{-80,-12.00}},color={0,0,127}));
  connect(indi_increment_limit_z_in, cFunction.indi_increment_limit_z) annotation(Line(points={{-492,-36.00},{-80,-36.00}},color={0,0,127}));
  connect(indi_measured_accel_limit_x_in, cFunction.indi_measured_accel_limit_x) annotation(Line(points={{-492,-60.00},{-80,-60.00}},color={0,0,127}));
  connect(indi_measured_accel_limit_y_in, cFunction.indi_measured_accel_limit_y) annotation(Line(points={{-492,-84.00},{-80,-84.00}},color={0,0,127}));
  connect(indi_measured_accel_limit_z_in, cFunction.indi_measured_accel_limit_z) annotation(Line(points={{-492,-108.00},{-80,-108.00}},color={0,0,127}));
  connect(indi_accel_lpf_alpha_in, cFunction.indi_accel_lpf_alpha) annotation(Line(points={{-492,-132.00},{-80,-132.00}},color={0,0,127}));
  connect(nmpc_horizon_s_in, cFunction.nmpc_horizon_s) annotation(Line(points={{-492,-156.00},{-80,-156.00}},color={0,0,127}));
  connect(nmpc_position_weight_x_in, cFunction.nmpc_position_weight_x) annotation(Line(points={{-492,-180.00},{-80,-180.00}},color={0,0,127}));
  connect(nmpc_position_weight_y_in, cFunction.nmpc_position_weight_y) annotation(Line(points={{-492,-204.00},{-80,-204.00}},color={0,0,127}));
  connect(nmpc_position_weight_z_in, cFunction.nmpc_position_weight_z) annotation(Line(points={{-492,-228.00},{-80,-228.00}},color={0,0,127}));
  connect(nmpc_velocity_weight_x_in, cFunction.nmpc_velocity_weight_x) annotation(Line(points={{-492,-252.00},{-80,-252.00}},color={0,0,127}));
  connect(nmpc_velocity_weight_y_in, cFunction.nmpc_velocity_weight_y) annotation(Line(points={{-492,-276.00},{-80,-276.00}},color={0,0,127}));
  connect(nmpc_velocity_weight_z_in, cFunction.nmpc_velocity_weight_z) annotation(Line(points={{-492,-300.00},{-80,-300.00}},color={0,0,127}));
  connect(nmpc_control_weight_x_in, cFunction.nmpc_control_weight_x) annotation(Line(points={{-492,-324.00},{-80,-324.00}},color={0,0,127}));
  connect(nmpc_control_weight_y_in, cFunction.nmpc_control_weight_y) annotation(Line(points={{-492,-348.00},{-80,-348.00}},color={0,0,127}));
  connect(nmpc_control_weight_z_in, cFunction.nmpc_control_weight_z) annotation(Line(points={{-492,-372.00},{-80,-372.00}},color={0,0,127}));
  connect(nmpc_accel_limit_x_in, cFunction.nmpc_accel_limit_x) annotation(Line(points={{-492,-396.00},{-80,-396.00}},color={0,0,127}));
  connect(nmpc_accel_limit_y_in, cFunction.nmpc_accel_limit_y) annotation(Line(points={{-492,-420.00},{-80,-420.00}},color={0,0,127}));
  connect(nmpc_accel_limit_z_in, cFunction.nmpc_accel_limit_z) annotation(Line(points={{-492,-444.00},{-80,-444.00}},color={0,0,127}));
  connect(nmpc_increment_limit_x_in, cFunction.nmpc_increment_limit_x) annotation(Line(points={{-492,-468.00},{-80,-468.00}},color={0,0,127}));
  connect(nmpc_increment_limit_y_in, cFunction.nmpc_increment_limit_y) annotation(Line(points={{-492,-492.00},{-80,-492.00}},color={0,0,127}));
  connect(nmpc_increment_limit_z_in, cFunction.nmpc_increment_limit_z) annotation(Line(points={{-492,-516.00},{-80,-516.00}},color={0,0,127}));
  connect(high_order_body_rate_limit_x_in, cFunction.high_order_body_rate_limit_x) annotation(Line(points={{-492,-540.00},{-80,-540.00}},color={0,0,127}));
  connect(high_order_body_rate_limit_y_in, cFunction.high_order_body_rate_limit_y) annotation(Line(points={{-492,-564.00},{-80,-564.00}},color={0,0,127}));
  connect(high_order_body_rate_limit_z_in, cFunction.high_order_body_rate_limit_z) annotation(Line(points={{-492,-588.00},{-80,-588.00}},color={0,0,127}));
  connect(high_order_body_accel_limit_x_in, cFunction.high_order_body_accel_limit_x) annotation(Line(points={{-492,-612.00},{-80,-612.00}},color={0,0,127}));
  connect(high_order_body_accel_limit_y_in, cFunction.high_order_body_accel_limit_y) annotation(Line(points={{-492,-636.00},{-80,-636.00}},color={0,0,127}));
  connect(high_order_body_accel_limit_z_in, cFunction.high_order_body_accel_limit_z) annotation(Line(points={{-492,-660.00},{-80,-660.00}},color={0,0,127}));
  connect(smooth_feedback_gain_x_in, cFunction.smooth_feedback_gain_x) annotation(Line(points={{-492,-684.00},{-80,-684.00}},color={0,0,127}));
  connect(smooth_feedback_gain_y_in, cFunction.smooth_feedback_gain_y) annotation(Line(points={{-492,-708.00},{-80,-708.00}},color={0,0,127}));
  connect(smooth_feedback_gain_z_in, cFunction.smooth_feedback_gain_z) annotation(Line(points={{-492,-732.00},{-80,-732.00}},color={0,0,127}));
  connect(smooth_feedback_bound_x_in, cFunction.smooth_feedback_bound_x) annotation(Line(points={{-492,-756.00},{-80,-756.00}},color={0,0,127}));
  connect(smooth_feedback_bound_y_in, cFunction.smooth_feedback_bound_y) annotation(Line(points={{-492,-780.00},{-80,-780.00}},color={0,0,127}));
  connect(smooth_feedback_bound_z_in, cFunction.smooth_feedback_bound_z) annotation(Line(points={{-492,-804.00},{-80,-804.00}},color={0,0,127}));
  connect(disturbance_observer_gain_x_in, cFunction.disturbance_observer_gain_x) annotation(Line(points={{-492,-828.00},{-80,-828.00}},color={0,0,127}));
  connect(disturbance_observer_gain_y_in, cFunction.disturbance_observer_gain_y) annotation(Line(points={{-492,-852.00},{-80,-852.00}},color={0,0,127}));
  connect(disturbance_observer_gain_z_in, cFunction.disturbance_observer_gain_z) annotation(Line(points={{-492,-876.00},{-80,-876.00}},color={0,0,127}));
  connect(disturbance_compensation_limit_x_in, cFunction.disturbance_compensation_limit_x) annotation(Line(points={{-492,-900.00},{-80,-900.00}},color={0,0,127}));
  connect(disturbance_compensation_limit_y_in, cFunction.disturbance_compensation_limit_y) annotation(Line(points={{-492,-924.00},{-80,-924.00}},color={0,0,127}));
  connect(disturbance_compensation_limit_z_in, cFunction.disturbance_compensation_limit_z) annotation(Line(points={{-492,-948.00},{-80,-948.00}},color={0,0,127}));
  connect(l1_model_decay_in, cFunction.l1_model_decay) annotation(Line(points={{-492,-972.00},{-80,-972.00}},color={0,0,127}));
  connect(l1_filter_T_in, cFunction.l1_filter_T) annotation(Line(points={{-492,-996.00},{-80,-996.00}},color={0,0,127}));
  connect(l1_gain_x_in, cFunction.l1_gain_x) annotation(Line(points={{-492,-1020.00},{-80,-1020.00}},color={0,0,127}));
  connect(l1_gain_y_in, cFunction.l1_gain_y) annotation(Line(points={{-492,-1044.00},{-80,-1044.00}},color={0,0,127}));
  connect(l1_gain_z_in, cFunction.l1_gain_z) annotation(Line(points={{-492,-1068.00},{-80,-1068.00}},color={0,0,127}));
  connect(l1_comp_limit_x_in, cFunction.l1_comp_limit_x) annotation(Line(points={{-492,-1092.00},{-80,-1092.00}},color={0,0,127}));
  connect(l1_comp_limit_y_in, cFunction.l1_comp_limit_y) annotation(Line(points={{-492,-1116.00},{-80,-1116.00}},color={0,0,127}));
  connect(l1_comp_limit_z_in, cFunction.l1_comp_limit_z) annotation(Line(points={{-492,-1140.00},{-80,-1140.00}},color={0,0,127}));
  connect(drag_feedforward_gain_x_in, cFunction.drag_feedforward_gain_x) annotation(Line(points={{-492,-1164.00},{-80,-1164.00}},color={0,0,127}));
  connect(drag_feedforward_gain_y_in, cFunction.drag_feedforward_gain_y) annotation(Line(points={{-492,-1188.00},{-80,-1188.00}},color={0,0,127}));
  connect(drag_feedforward_gain_z_in, cFunction.drag_feedforward_gain_z) annotation(Line(points={{-492,-1212.00},{-80,-1212.00}},color={0,0,127}));
  connect(safety_accel_limit_x_in, cFunction.safety_accel_limit_x) annotation(Line(points={{-492,-1236.00},{-80,-1236.00}},color={0,0,127}));
  connect(safety_accel_limit_y_in, cFunction.safety_accel_limit_y) annotation(Line(points={{-492,-1260.00},{-80,-1260.00}},color={0,0,127}));
  connect(safety_accel_limit_z_in, cFunction.safety_accel_limit_z) annotation(Line(points={{-492,-1284.00},{-80,-1284.00}},color={0,0,127}));
  connect(fault_rotor_efficiency_1_in, cFunction.fault_rotor_efficiency_1) annotation(Line(points={{-492,-1308.00},{-80,-1308.00}},color={0,0,127}));
  connect(fault_rotor_efficiency_2_in, cFunction.fault_rotor_efficiency_2) annotation(Line(points={{-492,-1332.00},{-80,-1332.00}},color={0,0,127}));
  connect(fault_rotor_efficiency_3_in, cFunction.fault_rotor_efficiency_3) annotation(Line(points={{-492,-1356.00},{-80,-1356.00}},color={0,0,127}));
  connect(fault_rotor_efficiency_4_in, cFunction.fault_rotor_efficiency_4) annotation(Line(points={{-492,-1380.00},{-80,-1380.00}},color={0,0,127}));
  connect(fault_allocation_blend_in, cFunction.fault_allocation_blend) annotation(Line(points={{-492,-1404.00},{-80,-1404.00}},color={0,0,127}));
  connect(fault_min_efficiency_in, cFunction.fault_min_efficiency) annotation(Line(points={{-492,-1428.00},{-80,-1428.00}},color={0,0,127}));
  connect(fault_thrust_comp_limit_in, cFunction.fault_thrust_comp_limit) annotation(Line(points={{-492,-1452.00},{-80,-1452.00}},color={0,0,127}));
  connect(integral_limit_x_in, cFunction.integral_limit_x) annotation(Line(points={{-492,-1476.00},{-80,-1476.00}},color={0,0,127}));
  connect(integral_limit_y_in, cFunction.integral_limit_y) annotation(Line(points={{-492,-1500.00},{-80,-1500.00}},color={0,0,127}));
  connect(integral_limit_z_in, cFunction.integral_limit_z) annotation(Line(points={{-492,-1524.00},{-80,-1524.00}},color={0,0,127}));
  connect(mass_in, cFunction.mass) annotation(Line(points={{-492,-1548.00},{-80,-1548.00}},color={0,0,127}));
  connect(gravity_in, cFunction.gravity) annotation(Line(points={{-492,-1572.00},{-80,-1572.00}},color={0,0,127}));
  connect(hover_percentage_in, cFunction.hover_percentage) annotation(Line(points={{-492,-1596.00},{-80,-1596.00}},color={0,0,127}));
  connect(min_normalized_thrust_in, cFunction.min_normalized_thrust) annotation(Line(points={{-492,-1620.00},{-80,-1620.00}},color={0,0,127}));
  connect(max_normalized_thrust_in, cFunction.max_normalized_thrust) annotation(Line(points={{-492,-1644.00},{-80,-1644.00}},color={0,0,127}));
  connect(tilt_limit_rad_in, cFunction.tilt_limit_rad) annotation(Line(points={{-492,-1668.00},{-80,-1668.00}},color={0,0,127}));
  connect(cFunction.desired_attitude_w, desired_attitude_w_out) annotation(Line(points={{80,1668.00},{492,1668.00}},color={0,0,127}));
  connect(cFunction.desired_attitude_x, desired_attitude_x_out) annotation(Line(points={{80,1560.39},{492,1560.39}},color={0,0,127}));
  connect(cFunction.desired_attitude_y, desired_attitude_y_out) annotation(Line(points={{80,1452.77},{492,1452.77}},color={0,0,127}));
  connect(cFunction.desired_attitude_z, desired_attitude_z_out) annotation(Line(points={{80,1345.16},{492,1345.16}},color={0,0,127}));
  connect(cFunction.normalized_thrust, normalized_thrust_out) annotation(Line(points={{80,1237.55},{492,1237.55}},color={0,0,127}));
  connect(cFunction.collective_thrust_N, collective_thrust_N_out) annotation(Line(points={{80,1129.94},{492,1129.94}},color={0,0,127}));
  connect(cFunction.position_error_x, position_error_x_out) annotation(Line(points={{80,1022.32},{492,1022.32}},color={0,0,127}));
  connect(cFunction.position_error_y, position_error_y_out) annotation(Line(points={{80,914.71},{492,914.71}},color={0,0,127}));
  connect(cFunction.position_error_z, position_error_z_out) annotation(Line(points={{80,807.10},{492,807.10}},color={0,0,127}));
  connect(cFunction.velocity_error_x, velocity_error_x_out) annotation(Line(points={{80,699.48},{492,699.48}},color={0,0,127}));
  connect(cFunction.velocity_error_y, velocity_error_y_out) annotation(Line(points={{80,591.87},{492,591.87}},color={0,0,127}));
  connect(cFunction.velocity_error_z, velocity_error_z_out) annotation(Line(points={{80,484.26},{492,484.26}},color={0,0,127}));
  connect(cFunction.sliding_surface_x, sliding_surface_x_out) annotation(Line(points={{80,376.65},{492,376.65}},color={0,0,127}));
  connect(cFunction.sliding_surface_y, sliding_surface_y_out) annotation(Line(points={{80,269.03},{492,269.03}},color={0,0,127}));
  connect(cFunction.sliding_surface_z, sliding_surface_z_out) annotation(Line(points={{80,161.42},{492,161.42}},color={0,0,127}));
  connect(cFunction.desired_acceleration_x, desired_acceleration_x_out) annotation(Line(points={{80,53.81},{492,53.81}},color={0,0,127}));
  connect(cFunction.desired_acceleration_y, desired_acceleration_y_out) annotation(Line(points={{80,-53.81},{492,-53.81}},color={0,0,127}));
  connect(cFunction.desired_acceleration_z, desired_acceleration_z_out) annotation(Line(points={{80,-161.42},{492,-161.42}},color={0,0,127}));
  connect(cFunction.desired_body_rate_x, desired_body_rate_x_out) annotation(Line(points={{80,-269.03},{492,-269.03}},color={0,0,127}));
  connect(cFunction.desired_body_rate_y, desired_body_rate_y_out) annotation(Line(points={{80,-376.65},{492,-376.65}},color={0,0,127}));
  connect(cFunction.desired_body_rate_z, desired_body_rate_z_out) annotation(Line(points={{80,-484.26},{492,-484.26}},color={0,0,127}));
  connect(cFunction.desired_body_acceleration_x, desired_body_acceleration_x_out) annotation(Line(points={{80,-591.87},{492,-591.87}},color={0,0,127}));
  connect(cFunction.desired_body_acceleration_y, desired_body_acceleration_y_out) annotation(Line(points={{80,-699.48},{492,-699.48}},color={0,0,127}));
  connect(cFunction.desired_body_acceleration_z, desired_body_acceleration_z_out) annotation(Line(points={{80,-807.10},{492,-807.10}},color={0,0,127}));
  connect(cFunction.disturbance_estimate_x, disturbance_estimate_x_out) annotation(Line(points={{80,-914.71},{492,-914.71}},color={0,0,127}));
  connect(cFunction.disturbance_estimate_y, disturbance_estimate_y_out) annotation(Line(points={{80,-1022.32},{492,-1022.32}},color={0,0,127}));
  connect(cFunction.disturbance_estimate_z, disturbance_estimate_z_out) annotation(Line(points={{80,-1129.94},{492,-1129.94}},color={0,0,127}));
  connect(cFunction.desired_force_N_x, desired_force_N_x_out) annotation(Line(points={{80,-1237.55},{492,-1237.55}},color={0,0,127}));
  connect(cFunction.desired_force_N_y, desired_force_N_y_out) annotation(Line(points={{80,-1345.16},{492,-1345.16}},color={0,0,127}));
  connect(cFunction.desired_force_N_z, desired_force_N_z_out) annotation(Line(points={{80,-1452.77},{492,-1452.77}},color={0,0,127}));
  connect(cFunction.saturated, saturated_out) annotation(Line(points={{80,-1560.39},{492,-1560.39}},color={0,0,127}));
  connect(cFunction.status_code, status_code_out) annotation(Line(points={{80,-1668.00},{492,-1668.00}},color={0,0,127}));
end MoSim_P10_DFBC_Family_CFunction_Sysblock;