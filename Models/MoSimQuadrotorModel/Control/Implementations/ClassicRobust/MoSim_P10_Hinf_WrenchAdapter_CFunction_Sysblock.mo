within MoSimQuadrotorModel.Control.Implementations.ClassicRobust;
model MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left(state_roll_in, state_pitch_in, state_yaw_in, state_p_in, state_q_in, state_r_in, state_u_in, state_v_in, state_w_in, state_x_in, state_y_in, state_z_in, reference_roll_in, reference_pitch_in, reference_yaw_in, reference_p_in, reference_q_in, reference_r_in, reference_u_in, reference_v_in, reference_w_in, reference_x_in, reference_y_in, reference_z_in, enable_in, reset_in, mass_in, gravity_in, force_min_n_in, force_max_n_in, torque_limit_nm_in, roll_stiffness_nm_per_rad_in, pitch_stiffness_nm_per_rad_in, yaw_stiffness_nm_per_rad_in, hover_percentage_in, tilt_limit_rad_in, yaw_correction_limit_rad_in, min_normalized_thrust_in, max_normalized_thrust_in), Right(wrench_force_n_out, wrench_tau_x_nm_out, wrench_tau_y_nm_out, wrench_tau_z_nm_out, desired_attitude_w_out, desired_attitude_x_out, desired_attitude_y_out, desired_attitude_z_out, normalized_thrust_out, collective_thrust_n_out, adapted_roll_rad_out, adapted_pitch_rad_out, adapted_yaw_rad_out, saturated_out, status_code_out, source_command_variant_out, adapted_command_variant_out)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode"
:false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\p10_mworks_gap_closeout_20260718\\hinf_hover_wrench\\codegen"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{-620,-516.00},{620,516.00}},grid={2,2})));

  CFunction cFunction
    annotation (Placement(transformation(origin={0,0}, extent={{-80,-456.00},{80,456.00}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_roll_in
    annotation (Placement(transformation(origin={-500,456.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_pitch_in
    annotation (Placement(transformation(origin={-500,432.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_yaw_in
    annotation (Placement(transformation(origin={-500,408.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_p_in
    annotation (Placement(transformation(origin={-500,384.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_q_in
    annotation (Placement(transformation(origin={-500,360.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_r_in
    annotation (Placement(transformation(origin={-500,336.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_u_in
    annotation (Placement(transformation(origin={-500,312.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_v_in
    annotation (Placement(transformation(origin={-500,288.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_w_in
    annotation (Placement(transformation(origin={-500,264.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_x_in
    annotation (Placement(transformation(origin={-500,240.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_y_in
    annotation (Placement(transformation(origin={-500,216.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_z_in
    annotation (Placement(transformation(origin={-500,192.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_roll_in
    annotation (Placement(transformation(origin={-500,168.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_pitch_in
    annotation (Placement(transformation(origin={-500,144.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_yaw_in
    annotation (Placement(transformation(origin={-500,120.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_p_in
    annotation (Placement(transformation(origin={-500,96.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_q_in
    annotation (Placement(transformation(origin={-500,72.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_r_in
    annotation (Placement(transformation(origin={-500,48.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_u_in
    annotation (Placement(transformation(origin={-500,24.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_v_in
    annotation (Placement(transformation(origin={-500,0.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_w_in
    annotation (Placement(transformation(origin={-500,-24.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_x_in
    annotation (Placement(transformation(origin={-500,-48.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_y_in
    annotation (Placement(transformation(origin={-500,-72.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_z_in
    annotation (Placement(transformation(origin={-500,-96.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_in
    annotation (Placement(transformation(origin={-500,-120.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reset_in
    annotation (Placement(transformation(origin={-500,-144.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mass_in
    annotation (Placement(transformation(origin={-500,-168.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport gravity_in
    annotation (Placement(transformation(origin={-500,-192.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport force_min_n_in
    annotation (Placement(transformation(origin={-500,-216.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport force_max_n_in
    annotation (Placement(transformation(origin={-500,-240.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport torque_limit_nm_in
    annotation (Placement(transformation(origin={-500,-264.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_stiffness_nm_per_rad_in
    annotation (Placement(transformation(origin={-500,-288.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_stiffness_nm_per_rad_in
    annotation (Placement(transformation(origin={-500,-312.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_stiffness_nm_per_rad_in
    annotation (Placement(transformation(origin={-500,-336.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport hover_percentage_in
    annotation (Placement(transformation(origin={-500,-360.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport tilt_limit_rad_in
    annotation (Placement(transformation(origin={-500,-384.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_correction_limit_rad_in
    annotation (Placement(transformation(origin={-500,-408.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport min_normalized_thrust_in
    annotation (Placement(transformation(origin={-500,-432.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport max_normalized_thrust_in
    annotation (Placement(transformation(origin={-500,-456.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport wrench_force_n_out
    annotation (Placement(transformation(origin={500,456.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport wrench_tau_x_nm_out
    annotation (Placement(transformation(origin={500,399.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport wrench_tau_y_nm_out
    annotation (Placement(transformation(origin={500,342.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport wrench_tau_z_nm_out
    annotation (Placement(transformation(origin={500,285.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_w_out
    annotation (Placement(transformation(origin={500,228.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_x_out
    annotation (Placement(transformation(origin={500,171.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_y_out
    annotation (Placement(transformation(origin={500,114.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_z_out
    annotation (Placement(transformation(origin={500,57.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out
    annotation (Placement(transformation(origin={500,0.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n_out
    annotation (Placement(transformation(origin={500,-57.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport adapted_roll_rad_out
    annotation (Placement(transformation(origin={500,-114.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport adapted_pitch_rad_out
    annotation (Placement(transformation(origin={500,-171.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport adapted_yaw_rad_out
    annotation (Placement(transformation(origin={500,-228.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport saturated_out
    annotation (Placement(transformation(origin={500,-285.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport status_code_out
    annotation (Placement(transformation(origin={500,-342.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport source_command_variant_out
    annotation (Placement(transformation(origin={500,-399.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport adapted_command_variant_out
    annotation (Placement(transformation(origin={500,-456.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left(state_roll, state_pitch, state_yaw, state_p, state_q, state_r, state_u, state_v, state_w, state_x, state_y, state_z, reference_roll, reference_pitch, reference_yaw, reference_p, reference_q, reference_r, reference_u, reference_v, reference_w, reference_x, reference_y, reference_z, enable, reset, mass, gravity, force_min_n, force_max_n, torque_limit_nm, roll_stiffness_nm_per_rad, pitch_stiffness_nm_per_rad, yaw_stiffness_nm_per_rad, hover_percentage, tilt_limit_rad, yaw_correction_limit_rad, min_normalized_thrust, max_normalized_thrust), Right(wrench_force_n, wrench_tau_x_nm, wrench_tau_y_nm, wrench_tau_z_nm, desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, normalized_thrust, collective_thrust_n, adapted_roll_rad, adapted_pitch_rad, adapted_yaw_rad, saturated, status_code, source_command_variant, adapted_command_variant)),PortLabels(labelType="CustomType",labels(label(text="state_roll",instance="state_roll"),label(text="state_pitch",instance="state_pitch"),label(text="state_yaw",instance="state_yaw"),label(text="state_p",instance="state_p"),label(text="state_q",instance="state_q"),label(text="state_r",instance="state_r"),label(text="state_u",instance="state_u"),label(text="state_v",instance="state_v"),label(text="state_w",instance="state_w"),label(text="state_x",instance="state_x"),label(text="state_y",instance="state_y"),label(text="state_z",instance="state_z"),label(text="reference_roll",instance="reference_roll"),label(text="reference_pitch",instance="reference_pitch"),label(text="reference_yaw",instance="reference_yaw"),label(text="reference_p",instance="reference_p"),label(text="reference_q",instance="reference_q"),label(text="reference_r",instance="reference_r"),label(text="reference_u",instance="reference_u"),label(text="reference_v",instance="reference_v"),label(text="reference_w",instance="reference_w"),label(text="reference_x",instance="reference_x"),label(text="reference_y",instance
="reference_y"),label(text="reference_z",instance="reference_z"),label(text="enable",instance="enable"),label(text="reset",instance="reset"),label(text="mass",instance="mass"),label(text="gravity",instance="gravity"),label(text="force_min_n",instance="force_min_n"),label(text="force_max_n",instance="force_max_n"),label(text="torque_limit_nm",instance="torque_limit_nm"),label(text="roll_stiffness_nm_per_rad",instance="roll_stiffness_nm_per_rad"),label(text="pitch_stiffness_nm_per_rad",instance="pitch_stiffness_nm_per_rad"),label(text="yaw_stiffness_nm_per_rad",instance="yaw_stiffness_nm_per_rad"),label(text="hover_percentage",instance="hover_percentage"),label(text="tilt_limit_rad",instance="tilt_limit_rad"),label(text="yaw_correction_limit_rad",instance="yaw_correction_limit_rad"),label(text="min_normalized_thrust",instance="min_normalized_thrust"),label(text="max_normalized_thrust",instance="max_normalized_thrust"),label(text="wrench_force_n",instance="wrench_force_n"),label(text="wrench_tau_x_nm",instance="wrench_tau_x_nm"),label(text="wrench_tau_y_nm",instance="wrench_tau_y_nm"),label(text="wrench_tau_z_nm",instance="wrench_tau_z_nm"),label(text="desired_attitude_w",instance="desired_attitude_w"),label(text="desired_attitude_x",instance="desired_attitude_x"),label(text="desired_attitude_y",instance="desired_attitude_y"),label(text="desired_attitude_z",instance="desired_attitude_z"),label(text="normalized_thrust",instance="normalized_thrust"),label(text="collective_thrust_n",instance="collective_thrust_n"),label(text="adapted_roll_rad",instance="adapted_roll_rad"),label(text="adapted_pitch_rad",instance="adapted_pitch_rad"),label(text="adapted_yaw_rad",instance="adapted_yaw_rad"),label(text="saturated",instance="saturated"),label(text="status_code",instance="status_code"),label(text="source_command_variant",instance="source_command_variant"),label(text="adapted_command_variant",instance="adapted_command_variant"))),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind
=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
      Icon(coordinateSystem(extent={{-200,-100},{200,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2}),graphics={Rectangle(origin={0,0},fillColor={255,255,255},fillPattern=FillPattern.Solid,extent={{-200,100},{200,-100}}),Text(origin={0,0},extent={{-100,20},{100,-20}},textString="C",verticalAlignment=TextAlignment.VCenter),Text(origin={0,-120},lineColor={0,0,0},extent={{-150,20},{150,-20}},textString="%name",fontSize=14,textColor={0,0,0},verticalAlignment=TextAlignment.Top)}),
      Diagram(coordinateSystem(extent={{-100,-100},{100,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2})));

    function func_CFunction
      input SysplorerEmbeddedCoder.Types.Auto state_roll annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_pitch annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_yaw annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_p annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_q annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_r annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_u annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_v annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_roll annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_pitch annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_yaw annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_p annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_q annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_r annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_u annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_v annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto enable annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reset annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto mass annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto gravity annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto force_min_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto force_max_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto torque_limit_nm annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto roll_stiffness_nm_per_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto pitch_stiffness_nm_per_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto yaw_stiffness_nm_per_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto hover_percentage annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto tilt_limit_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto yaw_correction_limit_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto min_normalized_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto max_normalized_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto wrench_force_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto wrench_tau_x_nm annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto wrench_tau_y_nm annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto wrench_tau_z_nm annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto normalized_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto collective_thrust_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto adapted_roll_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto adapted_pitch_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto adapted_yaw_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto saturated annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto status_code annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto source_command_variant annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto adapted_command_variant annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
    external "C" MosimP10HinfWrenchAdapterStepScalar(state_roll,state_pitch,state_yaw,state_p,state_q,state_r,state_u,state_v,state_w,state_x,state_y,state_z,reference_roll,reference_pitch,reference_yaw,reference_p,reference_q,reference_r,reference_u,reference_v,reference_w,reference_x,reference_y,reference_z,enable,reset,mass,gravity,force_min_n,force_max_n,torque_limit_nm,roll_stiffness_nm_per_rad,pitch_stiffness_nm_per_rad,yaw_stiffness_nm_per_rad,hover_percentage,tilt_limit_rad,yaw_correction_limit_rad,min_normalized_thrust,max_normalized_thrust,wrench_force_n,wrench_tau_x_nm,wrench_tau_y_nm,wrench_tau_z_nm,desired_attitude_w,desired_attitude_x,desired_attitude_y,desired_attitude_z,normalized_thrust,collective_thrust_n,adapted_roll_rad,adapted_pitch_rad,adapted_yaw_rad,saturated,status_code,source_command_variant,adapted_command_variant)
      annotation (Include="typedef struct {
    double state[12];
    double reference[12];
    int enable;
    int reset;
} MosimWaveBHinfInput;

typedef struct {
    double gain[4][12];
    double mass;
    double gravity;
    double force_min_n;
    double force_max_n;
    double torque_limit_nm;
} MosimWaveBHinfParams;

typedef struct {
    double wrench[4];
    int saturated;
    int status_code;
    int command_variant; /* 3=WRENCH */
} MosimWaveBHinfOutput;

void mosim_wave_b_hinf_default_params(MosimWaveBHinfParams *params);
int mosim_wave_b_hinf_step(
    const MosimWaveBHinfParams *params,
    const MosimWaveBHinfInput *input,
    MosimWaveBHinfOutput *output);





typedef struct {
    double state[12];
    double reference[12];
    int enable;
    int reset;
} MosimP10HinfAdapterInput;

typedef struct {
    double mass;
    double gravity;
    double force_min_n;
    double force_max_n;
    double torque_limit_nm;
    double attitude_stiffness[3];
    double hover_percentage;
    double tilt_limit_rad;
    double yaw_correction_limit_rad;
    double min_normalized_thrust;
    double max_normalized_thrust;
} MosimP10HinfAdapterParams;

typedef struct {
    double wrench[4];
    double desired_attitude[4];
    double normalized_thrust;
    double collective_thrust_n;
    double adapted_euler[3];
    int saturated;
    int status_code;
    int source_command_variant;
    int adapted_command_variant;
} MosimP10HinfAdapterOutput;

void mosim_p10_hinf_adapter_default_params(MosimP10HinfAdapterParams *params);
int mosim_p10_hinf_adapter_step(
    const MosimP10HinfAdapterParams *params,
    const MosimP10HinfAdapterInput *input,
    MosimP10HinfAdapterOutput *output);

void MosimP10HinfWrenchAdapterStepScalar(
    double state_roll,
    double state_pitch,
    double state_yaw,
    double state_p,
    double state_q,
    double state_r,
    double state_u,
    double state_v,
    double state_w,
    double state_x,
    double state_y,
    double state_z,
    double reference_roll,
    double reference_pitch,
    double reference_yaw,
    double reference_p,
    double reference_q,
    double reference_r,
    double reference_u,
    double reference_v,
    double reference_w,
    double reference_x,
    double reference_y,
    double reference_z,
    double enable,
    double reset,
    double mass,
    double gravity,
    double force_min_n,
    double force_max_n,
    double torque_limit_nm,
    double roll_stiffness_nm_per_rad,
    double pitch_stiffness_nm_per_rad,
    double yaw_stiffness_nm_per_rad,
    double hover_percentage,
    double tilt_limit_rad,
    double yaw_correction_limit_rad,
    double min_normalized_thrust,
    double max_normalized_thrust,
    double *wrench_force_n,
    double *wrench_tau_x_nm,
    double *wrench_tau_y_nm,
    double *wrench_tau_z_nm,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *normalized_thrust,
    double *collective_thrust_n,
    double *adapted_roll_rad,
    double *adapted_pitch_rad,
    double *adapted_yaw_rad,
    double *saturated,
    double *status_code,
    double *source_command_variant,
    double *adapted_command_variant);




#include <math.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper, int *saturated)
{
    if (value < lower) {
        *saturated = 1;
        return lower;
    }
    if (value > upper) {
        *saturated = 1;
        return upper;
    }
    return value;
}

void mosim_wave_b_hinf_default_params(MosimWaveBHinfParams *params)
{
    static const double gain[4][12] = {
        {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 102.07465646871916, 0.0, 0.0, 160.7556564350713},
        {-521.4516779287975, 0.0, 0.0, -10.806018318480602, 0.0, 0.0, 0.0, -437.5189132603606, 0.0, 0.0, -1050.0326682458417, 0.0},
        {0.0, -521.451677928797, 0.0, 0.0, -10.806018318480536, 0.0, 437.51891326036105, 0.0, 0.0, 1050.0326682458376, 0.0, 0.0},
        {0.0, 0.0, -125.5903565899079, 0.0, 0.0, -25.26141057148942, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0}
    };
    int row;
    if (params == NULL) return;
    memset(params, 0, sizeof(*params));
    for (row = 0; row < 4; ++row) {
        memcpy(params->gain[row], gain[row], sizeof(gain[row]));
    }
    params->mass = 1.0;
    params->gravity = 9.80665;
    params->force_min_n = 0.0;
    params->force_max_n = 25.0;
    params->torque_limit_nm = 8.0;
}

int mosim_wave_b_hinf_step(
    const MosimWaveBHinfParams *params,
    const MosimWaveBHinfInput *input,
    MosimWaveBHinfOutput *output)
{
    int command;
    int state_index;
    if (params == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->command_variant = 3;
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    if (!isfinite(params->mass) || !isfinite(params->gravity) ||
        params->force_max_n < params->force_min_n || params->torque_limit_nm <= 0.0) {
        output->status_code = 2;
        return -2;
    }
    for (state_index = 0; state_index < 12; ++state_index) {
        if (!isfinite(input->state[state_index]) || !isfinite(input->reference[state_index])) {
            output->status_code = 2;
            return -2;
        }
    }
    output->wrench[0] = params->mass * params->gravity;
    for (command = 0; command < 4; ++command) {
        for (state_index = 0; state_index < 12; ++state_index) {
            output->wrench[command] += params->gain[command][state_index] *
                (input->state[state_index] - input->reference[state_index]);
        }
    }
    output->wrench[0] = clamp_value(output->wrench[0], params->force_min_n,
                                    params->force_max_n, &output->saturated);
    for (command = 1; command < 4; ++command) {
        output->wrench[command] = clamp_value(output->wrench[command],
            -params->torque_limit_nm, params->torque_limit_nm, &output->saturated);
    }
    return 0;
}



#include <math.h>
#include <string.h>

static double adapter_clamp_value(double value, double lower, double upper, int *saturated)
{
    if (value < lower) {
        *saturated = 1;
        return lower;
    }
    if (value > upper) {
        *saturated = 1;
        return upper;
    }
    return value;
}

static int params_valid(const MosimP10HinfAdapterParams *params)
{
    int axis;
    if (params == NULL || !isfinite(params->mass) || params->mass <= 0.0 ||
        !isfinite(params->gravity) || params->gravity <= 0.0 ||
        params->force_max_n < params->force_min_n || params->torque_limit_nm <= 0.0 ||
        params->hover_percentage <= 0.0 || params->max_normalized_thrust < params->min_normalized_thrust ||
        params->tilt_limit_rad <= 0.0 || params->yaw_correction_limit_rad <= 0.0) {
        return 0;
    }
    for (axis = 0; axis < 3; ++axis) {
        if (!isfinite(params->attitude_stiffness[axis]) || params->attitude_stiffness[axis] <= 0.0) {
            return 0;
        }
    }
    return 1;
}

static void euler_to_quaternion(double roll, double pitch, double yaw, double quaternion[4])
{
    const double cr = cos(0.5 * roll);
    const double sr = sin(0.5 * roll);
    const double cp = cos(0.5 * pitch);
    const double sp = sin(0.5 * pitch);
    const double cy = cos(0.5 * yaw);
    const double sy = sin(0.5 * yaw);
    quaternion[0] = cr * cp * cy + sr * sp * sy;
    quaternion[1] = sr * cp * cy - cr * sp * sy;
    quaternion[2] = cr * sp * cy + sr * cp * sy;
    quaternion[3] = cr * cp * sy - sr * sp * cy;
}

void mosim_p10_hinf_adapter_default_params(MosimP10HinfAdapterParams *params)
{
    if (params == NULL) return;
    memset(params, 0, sizeof(*params));
    params->mass = 1.0;
    params->gravity = 9.80665;
    params->force_min_n = 0.0;
    params->force_max_n = 25.0;
    params->torque_limit_nm = 8.0;
    params->attitude_stiffness[0] = 30.0;
    params->attitude_stiffness[1] = 30.0;
    params->attitude_stiffness[2] = 40.0;
    params->hover_percentage = 0.37;
    params->tilt_limit_rad = 0.35;
    params->yaw_correction_limit_rad = 0.20;
    params->min_normalized_thrust = 0.0;
    params->max_normalized_thrust = 0.62;
}

int mosim_p10_hinf_adapter_step(
    const MosimP10HinfAdapterParams *params,
    const MosimP10HinfAdapterInput *input,
    MosimP10HinfAdapterOutput *output)
{
    MosimWaveBHinfParams hinf_params;
    MosimWaveBHinfInput hinf_input;
    MosimWaveBHinfOutput hinf_output;
    double thrust_scale;
    int axis;
    int return_code;
    if (params == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->source_command_variant = 3;
    output->adapted_command_variant = 1;
    if (!params_valid(params)) {
        output->status_code = 2;
        return -2;
    }
    memset(&hinf_input, 0, sizeof(hinf_input));
    for (axis = 0; axis < 12; ++axis) {
        hinf_input.state[axis] = input->state[axis];
        hinf_input.reference[axis] = input->reference[axis];
    }
    hinf_input.enable = input->enable;
    hinf_input.reset = input->reset;
    mosim_wave_b_hinf_default_params(&hinf_params);
    hinf_params.mass = params->mass;
    hinf_params.gravity = params->gravity;
    hinf_params.force_min_n = params->force_min_n;
    hinf_params.force_max_n = params->force_max_n;
    hinf_params.torque_limit_nm = params->torque_limit_nm;
    return_code = mosim_wave_b_hinf_step(&hinf_params, &hinf_input, &hinf_output);
    if (return_code != 0 || hinf_output.status_code != 0) {
        output->status_code = hinf_output.status_code;
        return return_code;
    }
    for (axis = 0; axis < 4; ++axis) output->wrench[axis] = hinf_output.wrench[axis];
    output->saturated = hinf_output.saturated;
    output->collective_thrust_n = hinf_output.wrench[0];
    thrust_scale = params->mass * params->gravity / params->hover_percentage;
    output->normalized_thrust = adapter_clamp_value(
        output->collective_thrust_n / thrust_scale,
        params->min_normalized_thrust,
        params->max_normalized_thrust,
        &output->saturated);
    output->adapted_euler[0] = adapter_clamp_value(
        input->reference[0] + output->wrench[1] / params->attitude_stiffness[0],
        -params->tilt_limit_rad,
        params->tilt_limit_rad,
        &output->saturated);
    output->adapted_euler[1] = adapter_clamp_value(
        input->reference[1] + output->wrench[2] / params->attitude_stiffness[1],
        -params->tilt_limit_rad,
        params->tilt_limit_rad,
        &output->saturated);
    output->adapted_euler[2] = input->reference[2] + adapter_clamp_value(
        output->wrench[3] / params->attitude_stiffness[2],
        -params->yaw_correction_limit_rad,
        params->yaw_correction_limit_rad,
        &output->saturated);
    euler_to_quaternion(
        output->adapted_euler[0], output->adapted_euler[1], output->adapted_euler[2],
        output->desired_attitude);
    output->status_code = 0;
    return 0;
}

void MosimP10HinfWrenchAdapterStepScalar(
    double state_roll, double state_pitch, double state_yaw,
    double state_p, double state_q, double state_r,
    double state_u, double state_v, double state_w,
    double state_x, double state_y, double state_z,
    double reference_roll, double reference_pitch, double reference_yaw,
    double reference_p, double reference_q, double reference_r,
    double reference_u, double reference_v, double reference_w,
    double reference_x, double reference_y, double reference_z,
    double enable, double reset, double mass, double gravity,
    double force_min_n, double force_max_n, double torque_limit_nm,
    double roll_stiffness_nm_per_rad, double pitch_stiffness_nm_per_rad,
    double yaw_stiffness_nm_per_rad, double hover_percentage,
    double tilt_limit_rad, double yaw_correction_limit_rad,
    double min_normalized_thrust, double max_normalized_thrust,
    double *wrench_force_n, double *wrench_tau_x_nm, double *wrench_tau_y_nm,
    double *wrench_tau_z_nm, double *desired_attitude_w, double *desired_attitude_x,
    double *desired_attitude_y, double *desired_attitude_z, double *normalized_thrust,
    double *collective_thrust_n, double *adapted_roll_rad, double *adapted_pitch_rad,
    double *adapted_yaw_rad, double *saturated, double *status_code,
    double *source_command_variant, double *adapted_command_variant)
{
    const double state[12] = {state_roll, state_pitch, state_yaw, state_p, state_q, state_r,
                              state_u, state_v, state_w, state_x, state_y, state_z};
    const double reference[12] = {reference_roll, reference_pitch, reference_yaw,
                                  reference_p, reference_q, reference_r, reference_u,
                                  reference_v, reference_w, reference_x, reference_y, reference_z};
    MosimP10HinfAdapterParams params;
    MosimP10HinfAdapterInput input;
    MosimP10HinfAdapterOutput output;
    int index;
    mosim_p10_hinf_adapter_default_params(&params);
    params.mass = mass;
    params.gravity = gravity;
    params.force_min_n = force_min_n;
    params.force_max_n = force_max_n;
    params.torque_limit_nm = torque_limit_nm;
    params.attitude_stiffness[0] = roll_stiffness_nm_per_rad;
    params.attitude_stiffness[1] = pitch_stiffness_nm_per_rad;
    params.attitude_stiffness[2] = yaw_stiffness_nm_per_rad;
    params.hover_percentage = hover_percentage;
    params.tilt_limit_rad = tilt_limit_rad;
    params.yaw_correction_limit_rad = yaw_correction_limit_rad;
    params.min_normalized_thrust = min_normalized_thrust;
    params.max_normalized_thrust = max_normalized_thrust;
    memset(&input, 0, sizeof(input));
    for (index = 0; index < 12; ++index) {
        input.state[index] = state[index];
        input.reference[index] = reference[index];
    }
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    (void)mosim_p10_hinf_adapter_step(&params, &input, &output);
    *wrench_force_n = output.wrench[0];
    *wrench_tau_x_nm = output.wrench[1];
    *wrench_tau_y_nm = output.wrench[2];
    *wrench_tau_z_nm = output.wrench[3];
    *desired_attitude_w = output.desired_attitude[0];
    *desired_attitude_x = output.desired_attitude[1];
    *desired_attitude_y = output.desired_attitude[2];
    *desired_attitude_z = output.desired_attitude[3];
    *normalized_thrust = output.normalized_thrust;
    *collective_thrust_n = output.collective_thrust_n;
    *adapted_roll_rad = output.adapted_euler[0];
    *adapted_pitch_rad = output.adapted_euler[1];
    *adapted_yaw_rad = output.adapted_euler[2];
    *saturated = (double)output.saturated;
    *status_code = (double)output.status_code;
    *source_command_variant = (double)output.source_command_variant;
    *adapted_command_variant = (double)output.adapted_command_variant;
}
");
    end func_CFunction;

    SysplorerEmbeddedCoder.Port.Inport state_roll
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_pitch
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_yaw
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_p
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_q
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_r
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_u
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_v
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_w
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_roll
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_pitch
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_yaw
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_p
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_q
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_r
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_u
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_v
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_w
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport enable
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reset
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport mass
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport gravity
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport force_min_n
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport force_max_n
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport torque_limit_nm
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport roll_stiffness_nm_per_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport pitch_stiffness_nm_per_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport yaw_stiffness_nm_per_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport hover_percentage
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport tilt_limit_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport yaw_correction_limit_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport min_normalized_thrust
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport max_normalized_thrust
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport wrench_force_n
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport wrench_tau_x_nm
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport wrench_tau_y_nm
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport wrench_tau_z_nm
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
    SysplorerEmbeddedCoder.Port.Outport collective_thrust_n
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport adapted_roll_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport adapted_pitch_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport adapted_yaw_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport saturated
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport status_code
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport source_command_variant
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport adapted_command_variant
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
  equation
    (wrench_force_n, wrench_tau_x_nm, wrench_tau_y_nm, wrench_tau_z_nm, desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, normalized_thrust, collective_thrust_n, adapted_roll_rad, adapted_pitch_rad, adapted_yaw_rad, saturated, status_code, source_command_variant, adapted_command_variant) = func_CFunction(state_roll, state_pitch, state_yaw, state_p, state_q, state_r, state_u, state_v, state_w, state_x, state_y, state_z, reference_roll, reference_pitch, reference_yaw, reference_p, reference_q, reference_r, reference_u, reference_v, reference_w, reference_x, reference_y, reference_z, enable, reset, mass, gravity, force_min_n, force_max_n, torque_limit_nm, roll_stiffness_nm_per_rad, pitch_stiffness_nm_per_rad, yaw_stiffness_nm_per_rad, hover_percentage, tilt_limit_rad, yaw_correction_limit_rad, min_normalized_thrust, max_normalized_thrust);
  end CFunction;

equation
  connect(state_roll_in, cFunction.state_roll) annotation(Line(points={{-492,456.00},{-80,456.00}},color={0,0,127}));
  connect(state_pitch_in, cFunction.state_pitch) annotation(Line(points={{-492,432.00},{-80,432.00}},color={0,0,127}));
  connect(state_yaw_in, cFunction.state_yaw) annotation(Line(points={{-492,408.00},{-80,408.00}},color={0,0,127}));
  connect(state_p_in, cFunction.state_p) annotation(Line(points={{-492,384.00},{-80,384.00}},color={0,0,127}));
  connect(state_q_in, cFunction.state_q) annotation(Line(points={{-492,360.00},{-80,360.00}},color={0,0,127}));
  connect(state_r_in, cFunction.state_r) annotation(Line(points={{-492,336.00},{-80,336.00}},color={0,0,127}));
  connect(state_u_in, cFunction.state_u) annotation(Line(points={{-492,312.00},{-80,312.00}},color={0,0,127}));
  connect(state_v_in, cFunction.state_v) annotation(Line(points={{-492,288.00},{-80,288.00}},color={0,0,127}));
  connect(state_w_in, cFunction.state_w) annotation(Line(points={{-492,264.00},{-80,264.00}},color={0,0,127}));
  connect(state_x_in, cFunction.state_x) annotation(Line(points={{-492,240.00},{-80,240.00}},color={0,0,127}));
  connect(state_y_in, cFunction.state_y) annotation(Line(points={{-492,216.00},{-80,216.00}},color={0,0,127}));
  connect(state_z_in, cFunction.state_z) annotation(Line(points={{-492,192.00},{-80,192.00}},color={0,0,127}));
  connect(reference_roll_in, cFunction.reference_roll) annotation(Line(points={{-492,168.00},{-80,168.00}},color={0,0,127}));
  connect(reference_pitch_in, cFunction.reference_pitch) annotation(Line(points={{-492,144.00},{-80,144.00}},color={0,0,127}));
  connect(reference_yaw_in, cFunction.reference_yaw) annotation(Line(points={{-492,120.00},{-80,120.00}},color={0,0,127}));
  connect(reference_p_in, cFunction.reference_p) annotation(Line(points={{-492,96.00},{-80,96.00}},color={0,0,127}));
  connect(reference_q_in, cFunction.reference_q) annotation(Line(points={{-492,72.00},{-80,72.00}},color={0,0,127}));
  connect(reference_r_in, cFunction.reference_r) annotation(Line(points={{-492,48.00},{-80,48.00}},color={0,0,127}));
  connect(reference_u_in, cFunction.reference_u) annotation(Line(points={{-492,24.00},{-80,24.00}},color={0,0,127}));
  connect(reference_v_in, cFunction.reference_v) annotation(Line(points={{-492,0.00},{-80,0.00}},color={0,0,127}));
  connect(reference_w_in, cFunction.reference_w) annotation(Line(points={{-492,-24.00},{-80,-24.00}},color={0,0,127}));
  connect(reference_x_in, cFunction.reference_x) annotation(Line(points={{-492,-48.00},{-80,-48.00}},color={0,0,127}));
  connect(reference_y_in, cFunction.reference_y) annotation(Line(points={{-492,-72.00},{-80,-72.00}},color={0,0,127}));
  connect(reference_z_in, cFunction.reference_z) annotation(Line(points={{-492,-96.00},{-80,-96.00}},color={0,0,127}));
  connect(enable_in, cFunction.enable) annotation(Line(points={{-492,-120.00},{-80,-120.00}},color={0,0,127}));
  connect(reset_in, cFunction.reset) annotation(Line(points={{-492,-144.00},{-80,-144.00}},color={0,0,127}));
  connect(mass_in, cFunction.mass) annotation(Line(points={{-492,-168.00},{-80,-168.00}},color={0,0,127}));
  connect(gravity_in, cFunction.gravity) annotation(Line(points={{-492,-192.00},{-80,-192.00}},color={0,0,127}));
  connect(force_min_n_in, cFunction.force_min_n) annotation(Line(points={{-492,-216.00},{-80,-216.00}},color={0,0,127}));
  connect(force_max_n_in, cFunction.force_max_n) annotation(Line(points={{-492,-240.00},{-80,-240.00}},color={0,0,127}));
  connect(torque_limit_nm_in, cFunction.torque_limit_nm) annotation(Line(points={{-492,-264.00},{-80,-264.00}},color={0,0,127}));
  connect(roll_stiffness_nm_per_rad_in, cFunction.roll_stiffness_nm_per_rad) annotation(Line(points={{-492,-288.00},{-80,-288.00}},color={0,0,127}));
  connect(pitch_stiffness_nm_per_rad_in, cFunction.pitch_stiffness_nm_per_rad) annotation(Line(points={{-492,-312.00},{-80,-312.00}},color={0,0,127}));
  connect(yaw_stiffness_nm_per_rad_in, cFunction.yaw_stiffness_nm_per_rad) annotation(Line(points={{-492,-336.00},{-80,-336.00}},color={0,0,127}));
  connect(hover_percentage_in, cFunction.hover_percentage) annotation(Line(points={{-492,-360.00},{-80,-360.00}},color={0,0,127}));
  connect(tilt_limit_rad_in, cFunction.tilt_limit_rad) annotation(Line(points={{-492,-384.00},{-80,-384.00}},color={0,0,127}));
  connect(yaw_correction_limit_rad_in, cFunction.yaw_correction_limit_rad) annotation(Line(points={{-492,-408.00},{-80,-408.00}},color={0,0,127}));
  connect(min_normalized_thrust_in, cFunction.min_normalized_thrust) annotation(Line(points={{-492,-432.00},{-80,-432.00}},color={0,0,127}));
  connect(max_normalized_thrust_in, cFunction.max_normalized_thrust) annotation(Line(points={{-492,-456.00},{-80,-456.00}},color={0,0,127}));
  connect(cFunction.wrench_force_n, wrench_force_n_out) annotation(Line(points={{80,456.00},{492,456.00}},color={0,0,127}));
  connect(cFunction.wrench_tau_x_nm, wrench_tau_x_nm_out) annotation(Line(points={{80,399.00},{492,399.00}},color={0,0,127}));
  connect(cFunction.wrench_tau_y_nm, wrench_tau_y_nm_out) annotation(Line(points={{80,342.00},{492,342.00}},color={0,0,127}));
  connect(cFunction.wrench_tau_z_nm, wrench_tau_z_nm_out) annotation(Line(points={{80,285.00},{492,285.00}},color={0,0,127}));
  connect(cFunction.desired_attitude_w, desired_attitude_w_out) annotation(Line(points={{80,228.00},{492,228.00}},color={0,0,127}));
  connect(cFunction.desired_attitude_x, desired_attitude_x_out) annotation(Line(points={{80,171.00},{492,171.00}},color={0,0,127}));
  connect(cFunction.desired_attitude_y, desired_attitude_y_out) annotation(Line(points={{80,114.00},{492,114.00}},color={0,0,127}));
  connect(cFunction.desired_attitude_z, desired_attitude_z_out) annotation(Line(points={{80,57.00},{492,57.00}},color={0,0,127}));
  connect(cFunction.normalized_thrust, normalized_thrust_out) annotation(Line(points={{80,0.00},{492,0.00}},color={0,0,127}));
  connect(cFunction.collective_thrust_n, collective_thrust_n_out) annotation(Line(points={{80,-57.00},{492,-57.00}},color={0,0,127}));
  connect(cFunction.adapted_roll_rad, adapted_roll_rad_out) annotation(Line(points={{80,-114.00},{492,-114.00}},color={0,0,127}));
  connect(cFunction.adapted_pitch_rad, adapted_pitch_rad_out) annotation(Line(points={{80,-171.00},{492,-171.00}},color={0,0,127}));
  connect(cFunction.adapted_yaw_rad, adapted_yaw_rad_out) annotation(Line(points={{80,-228.00},{492,-228.00}},color={0,0,127}));
  connect(cFunction.saturated, saturated_out) annotation(Line(points={{80,-285.00},{492,-285.00}},color={0,0,127}));
  connect(cFunction.status_code, status_code_out) annotation(Line(points={{80,-342.00},{492,-342.00}},color={0,0,127}));
  connect(cFunction.source_command_variant, source_command_variant_out) annotation(Line(points={{80,-399.00},{492,-399.00}},color={0,0,127}));
  connect(cFunction.adapted_command_variant, adapted_command_variant_out) annotation(Line(points={{80,-456.00},{492,-456.00}},color={0,0,127}));
end MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock;
