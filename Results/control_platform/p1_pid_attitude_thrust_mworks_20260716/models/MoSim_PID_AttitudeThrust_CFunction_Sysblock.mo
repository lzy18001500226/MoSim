model MoSim_PID_AttitudeThrust_CFunction_Sysblock
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left(algorithm_id_in, dt_in, position_x_in, position_y_in, position_z_in, velocity_x_in, velocity_y_in, velocity_z_in, attitude_w_in, attitude_x_in, attitude_y_in, attitude_z_in, angular_velocity_x_in, angular_velocity_y_in, angular_velocity_z_in, reference_position_x_in, reference_position_y_in, reference_position_z_in, reference_velocity_x_in, reference_velocity_y_in, reference_velocity_z_in, reference_acceleration_x_in, reference_acceleration_y_in, reference_acceleration_z_in, reference_yaw_in, mass_kg_in, gravity_mps2_in, max_tilt_rad_in, min_collective_thrust_n_in, max_collective_thrust_n_in, schedule_x_in, schedule_y_in, schedule_z_in, fuzzy_error_x_in, fuzzy_error_y_in, fuzzy_error_z_in, neural_residual_x_in, neural_residual_y_in, neural_residual_z_in, enable_in, reset_in), Right(desired_attitude_w_out, desired_attitude_x_out, desired_attitude_y_out, desired_attitude_z_out, desired_collective_thrust_n_out, desired_acceleration_x_out, desired_acceleration_y_out, desired_acceleration_z_out, position_error_x_out, position_error_y_out, position_error_z_out, velocity_error_x_out, velocity_error_y_out, velocity_error_z_out, scheduled_gain_x_out, scheduled_gain_y_out, scheduled_gain_z_out, saturated_out, status_code_out, algorithm_id_out_out)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail"
:""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\p1_pid_attitude_thrust_mworks_20260716\\generated_c_v2"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{-340,-620},{340,280}},grid={2,2})));

  CFunction cFunction
    annotation (Placement(transformation(origin={0,0}, extent={{-28,-20},{28,20}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport algorithm_id_in
    annotation (Placement(transformation(origin={-300,250},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport dt_in
    annotation (Placement(transformation(origin={-300,243},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_x_in
    annotation (Placement(transformation(origin={-300,236},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_y_in
    annotation (Placement(transformation(origin={-300,229},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_z_in
    annotation (Placement(transformation(origin={-300,222},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_x_in
    annotation (Placement(transformation(origin={-300,215},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_y_in
    annotation (Placement(transformation(origin={-300,208},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_z_in
    annotation (Placement(transformation(origin={-300,201},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_w_in
    annotation (Placement(transformation(origin={-300,194},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_x_in
    annotation (Placement(transformation(origin={-300,187},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_y_in
    annotation (Placement(transformation(origin={-300,180},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_z_in
    annotation (Placement(transformation(origin={-300,173},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport angular_velocity_x_in
    annotation (Placement(transformation(origin={-300,166},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport angular_velocity_y_in
    annotation (Placement(transformation(origin={-300,159},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport angular_velocity_z_in
    annotation (Placement(transformation(origin={-300,152},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x_in
    annotation (Placement(transformation(origin={-300,145},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y_in
    annotation (Placement(transformation(origin={-300,138},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z_in
    annotation (Placement(transformation(origin={-300,131},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x_in
    annotation (Placement(transformation(origin={-300,124},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y_in
    annotation (Placement(transformation(origin={-300,117},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z_in
    annotation (Placement(transformation(origin={-300,110},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x_in
    annotation (Placement(transformation(origin={-300,103},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y_in
    annotation (Placement(transformation(origin={-300,96},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z_in
    annotation (Placement(transformation(origin={-300,89},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_yaw_in
    annotation (Placement(transformation(origin={-300,82},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mass_kg_in
    annotation (Placement(transformation(origin={-300,75},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport gravity_mps2_in
    annotation (Placement(transformation(origin={-300,68},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport max_tilt_rad_in
    annotation (Placement(transformation(origin={-300,61},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport min_collective_thrust_n_in
    annotation (Placement(transformation(origin={-300,54},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport max_collective_thrust_n_in
    annotation (Placement(transformation(origin={-300,47},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport schedule_x_in
    annotation (Placement(transformation(origin={-300,40},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport schedule_y_in
    annotation (Placement(transformation(origin={-300,33},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport schedule_z_in
    annotation (Placement(transformation(origin={-300,26},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fuzzy_error_x_in
    annotation (Placement(transformation(origin={-300,19},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fuzzy_error_y_in
    annotation (Placement(transformation(origin={-300,12},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fuzzy_error_z_in
    annotation (Placement(transformation(origin={-300,5},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport neural_residual_x_in
    annotation (Placement(transformation(origin={-300,-2},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport neural_residual_y_in
    annotation (Placement(transformation(origin={-300,-9},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport neural_residual_z_in
    annotation (Placement(transformation(origin={-300,-16},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_in
    annotation (Placement(transformation(origin={-300,-23},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reset_in
    annotation (Placement(transformation(origin={-300,-30},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_w_out
    annotation (Placement(transformation(origin={300,160},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_x_out
    annotation (Placement(transformation(origin={300,151},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_y_out
    annotation (Placement(transformation(origin={300,142},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_z_out
    annotation (Placement(transformation(origin={300,133},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_collective_thrust_n_out
    annotation (Placement(transformation(origin={300,124},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out
    annotation (Placement(transformation(origin={300,115},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out
    annotation (Placement(transformation(origin={300,106},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out
    annotation (Placement(transformation(origin={300,97},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport position_error_x_out
    annotation (Placement(transformation(origin={300,88},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport position_error_y_out
    annotation (Placement(transformation(origin={300,79},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport position_error_z_out
    annotation (Placement(transformation(origin={300,70},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_x_out
    annotation (Placement(transformation(origin={300,61},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_y_out
    annotation (Placement(transformation(origin={300,52},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_z_out
    annotation (Placement(transformation(origin={300,43},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain_x_out
    annotation (Placement(transformation(origin={300,34},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain_y_out
    annotation (Placement(transformation(origin={300,25},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain_z_out
    annotation (Placement(transformation(origin={300,16},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport saturated_out
    annotation (Placement(transformation(origin={300,7},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport status_code_out
    annotation (Placement(transformation(origin={300,-2},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport algorithm_id_out_out
    annotation (Placement(transformation(origin={300,-11},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left(algorithm_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, attitude_w, attitude_x, attitude_y, attitude_z, angular_velocity_x, angular_velocity_y, angular_velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_yaw, mass_kg, gravity_mps2, max_tilt_rad, min_collective_thrust_n, max_collective_thrust_n, schedule_x, schedule_y, schedule_z, fuzzy_error_x, fuzzy_error_y, fuzzy_error_z, neural_residual_x, neural_residual_y, neural_residual_z, enable, reset), Right(desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, desired_collective_thrust_n, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, position_error_x, position_error_y, position_error_z, velocity_error_x, velocity_error_y, velocity_error_z, scheduled_gain_x, scheduled_gain_y, scheduled_gain_z, saturated, status_code, algorithm_id_out)),PortLabels(labelType="CustomType",labels(label(text="algorithm_id",instance="algorithm_id"),label(text="dt",instance="dt"),label(text="position_x",instance="position_x"),label(text="position_y",instance="position_y"),label(text="position_z",instance="position_z"),label(text="velocity_x",instance="velocity_x"),label(text="velocity_y",instance="velocity_y"),label(text="velocity_z",instance="velocity_z"),label(text="attitude_w",instance="attitude_w"),label(text="attitude_x",instance="attitude_x"),label(text="attitude_y",instance="attitude_y"),label(text="attitude_z",instance="attitude_z"),label(text="angular_velocity_x",instance="angular_velocity_x"),label(text="angular_velocity_y",instance="angular_velocity_y"),label(text="angular_velocity_z",instance="angular_velocity_z"),label(text="reference_position_x",instance="reference_position_x"),label(text="reference_position_y",instance="reference_position_y"
),label(text="reference_position_z",instance="reference_position_z"),label(text="reference_velocity_x",instance="reference_velocity_x"),label(text="reference_velocity_y",instance="reference_velocity_y"),label(text="reference_velocity_z",instance="reference_velocity_z"),label(text="reference_acceleration_x",instance="reference_acceleration_x"),label(text="reference_acceleration_y",instance="reference_acceleration_y"),label(text="reference_acceleration_z",instance="reference_acceleration_z"),label(text="reference_yaw",instance="reference_yaw"),label(text="mass_kg",instance="mass_kg"),label(text="gravity_mps2",instance="gravity_mps2"),label(text="max_tilt_rad",instance="max_tilt_rad"),label(text="min_collective_thrust_n",instance="min_collective_thrust_n"),label(text="max_collective_thrust_n",instance="max_collective_thrust_n"),label(text="schedule_x",instance="schedule_x"),label(text="schedule_y",instance="schedule_y"),label(text="schedule_z",instance="schedule_z"),label(text="fuzzy_error_x",instance="fuzzy_error_x"),label(text="fuzzy_error_y",instance="fuzzy_error_y"),label(text="fuzzy_error_z",instance="fuzzy_error_z"),label(text="neural_residual_x",instance="neural_residual_x"),label(text="neural_residual_y",instance="neural_residual_y"),label(text="neural_residual_z",instance="neural_residual_z"),label(text="enable",instance="enable"),label(text="reset",instance="reset"),label(text="desired_attitude_w",instance="desired_attitude_w"),label(text="desired_attitude_x",instance="desired_attitude_x"),label(text="desired_attitude_y",instance="desired_attitude_y"),label(text="desired_attitude_z",instance="desired_attitude_z"),label(text="desired_collective_thrust_n",instance="desired_collective_thrust_n"),label(text="desired_acceleration_x",instance="desired_acceleration_x"),label(text="desired_acceleration_y",instance="desired_acceleration_y"),label(text="desired_acceleration_z",instance="desired_acceleration_z"),label(text="position_error_x",instance="position_error_x"
),label(text="position_error_y",instance="position_error_y"),label(text="position_error_z",instance="position_error_z"),label(text="velocity_error_x",instance="velocity_error_x"),label(text="velocity_error_y",instance="velocity_error_y"),label(text="velocity_error_z",instance="velocity_error_z"),label(text="scheduled_gain_x",instance="scheduled_gain_x"),label(text="scheduled_gain_y",instance="scheduled_gain_y"),label(text="scheduled_gain_z",instance="scheduled_gain_z"),label(text="saturated",instance="saturated"),label(text="status_code",instance="status_code"),label(text="algorithm_id_out",instance="algorithm_id_out"))),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
      Icon(coordinateSystem(extent={{-200,-100},{200,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2}),graphics={Rectangle(origin={0,0},fillColor={255,255,255},fillPattern=FillPattern.Solid,extent={{-200,100},{200,-100}}),Text(origin={0,0},extent={{-100,20},{100,-20}},textString="C",verticalAlignment=TextAlignment.VCenter),Text(origin={0,-120},lineColor={0,0,0},extent={{-150,20},{150,-20}},textString="%name",fontSize=14,textColor={0,0,0},verticalAlignment=TextAlignment.Top)}),
      Diagram(coordinateSystem(extent={{-100,-100},{100,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2})));

    function func_CFunction
      input SysplorerEmbeddedCoder.Types.Auto algorithm_id annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
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
      input SysplorerEmbeddedCoder.Types.Auto reference_yaw annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto mass_kg annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto gravity_mps2 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto max_tilt_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto min_collective_thrust_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto max_collective_thrust_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto schedule_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto schedule_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto schedule_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fuzzy_error_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fuzzy_error_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fuzzy_error_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto neural_residual_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto neural_residual_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto neural_residual_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto enable annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reset annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_collective_thrust_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto position_error_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto position_error_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto position_error_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto velocity_error_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto velocity_error_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto velocity_error_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto scheduled_gain_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto scheduled_gain_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto scheduled_gain_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto saturated annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto status_code annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto algorithm_id_out annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
    external "C" MosimPidAttitudeThrustStepScalar(algorithm_id,dt,position_x,position_y,position_z,velocity_x,velocity_y,velocity_z,attitude_w,attitude_x,attitude_y,attitude_z,angular_velocity_x,angular_velocity_y,angular_velocity_z,reference_position_x,reference_position_y,reference_position_z,reference_velocity_x,reference_velocity_y,reference_velocity_z,reference_acceleration_x,reference_acceleration_y,reference_acceleration_z,reference_yaw,mass_kg,gravity_mps2,max_tilt_rad,min_collective_thrust_n,max_collective_thrust_n,schedule_x,schedule_y,schedule_z,fuzzy_error_x,fuzzy_error_y,fuzzy_error_z,neural_residual_x,neural_residual_y,neural_residual_z,enable,reset,desired_attitude_w,desired_attitude_x,desired_attitude_y,desired_attitude_z,desired_collective_thrust_n,desired_acceleration_x,desired_acceleration_y,desired_acceleration_z,position_error_x,position_error_y,position_error_z,velocity_error_x,velocity_error_y,velocity_error_z,scheduled_gain_x,scheduled_gain_y,scheduled_gain_z,saturated,status_code,algorithm_id_out)
      annotation (Include="typedef struct {
    double kp;
    double ki;
    double kd;
    double feedforward_gain;
    double output_min;
    double output_max;
    double integral_min;
    double integral_max;
    double anti_windup_gain;
    double derivative_filter_tau;
    double schedule_gain;
    double fuzzy_gain;
    double neural_gain;
    double neural_residual_limit;
} MosimPidConfig;

typedef struct {
    double integral;
    double filtered_derivative;
    double previous_error;
    int initialized;
} MosimPidState;

typedef struct {
    double setpoint;
    double measurement;
    double feedforward;
    double schedule;
    double fuzzy_error;
    double neural_residual;
    double dt;
    int reset;
    int enable;
} MosimPidInput;

typedef struct {
    double command;
    double unsaturated_command;
    double error;
    double integral;
    double scheduled_gain;
    int saturated;
    int status_code;
} MosimPidOutput;

typedef struct {
    MosimPidState outer;
    MosimPidState inner;
} MosimCascadePidState;

typedef struct {
    double outer_reference;
    double outer_measurement;
    double inner_measurement;
    double feedforward;
    double schedule;
    double fuzzy_error;
    double neural_residual;
    double dt;
    int reset;
    int enable;
} MosimCascadePidInput;

typedef struct {
    double outer_command;
    double command;
    int saturated;
    int status_code;
} MosimCascadePidOutput;

void mosim_pid_default_config(MosimPidConfig *config);
void mosim_pid_reset(MosimPidState *state);
int mosim_pid_step(const MosimPidConfig *config, MosimPidState *state,
                   const MosimPidInput *input, MosimPidOutput *output);
int mosim_cascade_pid_step(const MosimPidConfig *outer_config,
                           const MosimPidConfig *inner_config,
                           MosimCascadePidState *state,
                           const MosimCascadePidInput *input,
                           MosimCascadePidOutput *output);




#include <math.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static int finite_config(const MosimPidConfig *config)
{
    const double values[] = {
        config->kp, config->ki, config->kd, config->feedforward_gain,
        config->output_min, config->output_max, config->integral_min,
        config->integral_max, config->anti_windup_gain,
        config->derivative_filter_tau, config->schedule_gain,
        config->fuzzy_gain, config->neural_gain,
        config->neural_residual_limit
    };
    size_t index;
    for (index = 0; index < sizeof(values) / sizeof(values[0]); ++index) {
        if (!isfinite(values[index])) return 0;
    }
    return config->output_min <= config->output_max &&
           config->integral_min <= config->integral_max &&
           config->derivative_filter_tau >= 0.0 &&
           config->neural_residual_limit >= 0.0;
}

static double effective_gain(const MosimPidConfig *config,
                             const MosimPidInput *input)
{
    const double residual = clamp_value(input->neural_residual,
                                        -config->neural_residual_limit,
                                        config->neural_residual_limit);
    const double fuzzy_term = tanh(input->fuzzy_error);
    const double gain = 1.0 + config->schedule_gain * input->schedule +
                        config->fuzzy_gain * fuzzy_term +
                        config->neural_gain * residual;
    return clamp_value(gain, 0.25, 4.0);
}

void mosim_pid_default_config(MosimPidConfig *config)
{
    const MosimPidConfig defaults = {
        1.0, 0.0, 0.0, 0.0, -1.0, 1.0, -1.0, 1.0, 0.2, 0.0,
        0.0, 0.0, 0.0, 0.0
    };
    if (config != NULL) *config = defaults;
}

void mosim_pid_reset(MosimPidState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

int mosim_pid_step(const MosimPidConfig *config, MosimPidState *state,
                   const MosimPidInput *input, MosimPidOutput *output)
{
    double error;
    double derivative;
    double gain;
    double unsaturated;
    double command;
    double saturation_error;
    if (config == NULL || state == NULL || input == NULL || output == NULL ||
        !finite_config(config) || !isfinite(input->setpoint) ||
        !isfinite(input->measurement) || !isfinite(input->feedforward) ||
        !isfinite(input->schedule) || !isfinite(input->fuzzy_error) ||
        !isfinite(input->neural_residual) || !isfinite(input->dt) ||
        input->dt <= 0.0) {
        if (output != NULL) memset(output, 0, sizeof(*output));
        if (output != NULL) output->status_code = -1;
        return -1;
    }
    memset(output, 0, sizeof(*output));
    if (input->reset) mosim_pid_reset(state);
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    error = input->setpoint - input->measurement;
    derivative = state->initialized ? (error - state->previous_error) / input->dt : 0.0;
    if (config->derivative_filter_tau > 0.0) {
        const double alpha = input->dt / (config->derivative_filter_tau + input->dt);
        state->filtered_derivative += alpha * (derivative - state->filtered_derivative);
        derivative = state->filtered_derivative;
    } else {
        state->filtered_derivative = derivative;
    }
    gain = effective_gain(config, input);
    state->integral += gain * error * input->dt;
    state->integral = clamp_value(state->integral, config->integral_min,
                                  config->integral_max);
    unsaturated = gain * config->kp * error + config->ki * state->integral +
                  gain * config->kd * derivative +
                  config->feedforward_gain * input->feedforward;
    command = clamp_value(unsaturated, config->output_min, config->output_max);
    saturation_error = command - unsaturated;
    if (config->anti_windup_gain > 0.0) {
        state->integral += config->anti_windup_gain * saturation_error * input->dt;
        state->integral = clamp_value(state->integral, config->integral_min,
                                      config->integral_max);
    }
    state->previous_error = error;
    state->initialized = 1;
    output->command = command;
    output->unsaturated_command = unsaturated;
    output->error = error;
    output->integral = state->integral;
    output->scheduled_gain = gain;
    output->saturated = fabs(command - unsaturated) > 1e-12;
    return 0;
}

int mosim_cascade_pid_step(const MosimPidConfig *outer_config,
                           const MosimPidConfig *inner_config,
                           MosimCascadePidState *state,
                           const MosimCascadePidInput *input,
                           MosimCascadePidOutput *output)
{
    MosimPidInput outer_input;
    MosimPidInput inner_input;
    MosimPidOutput outer_output;
    MosimPidOutput inner_output;
    int result;
    if (outer_config == NULL || inner_config == NULL || state == NULL ||
        input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    if (input->reset) {
        mosim_pid_reset(&state->outer);
        mosim_pid_reset(&state->inner);
    }
    outer_input.setpoint = input->outer_reference;
    outer_input.measurement = input->outer_measurement;
    outer_input.feedforward = input->feedforward;
    outer_input.schedule = input->schedule;
    outer_input.fuzzy_error = input->fuzzy_error;
    outer_input.neural_residual = input->neural_residual;
    outer_input.dt = input->dt;
    outer_input.reset = 0;
    outer_input.enable = input->enable;
    result = mosim_pid_step(outer_config, &state->outer, &outer_input, &outer_output);
    if (result != 0) { output->status_code = result; return result; }
    if (!input->enable) {
        output->status_code = outer_output.status_code;
        return 0;
    }
    inner_input = outer_input;
    inner_input.setpoint = outer_output.command;
    inner_input.measurement = input->inner_measurement;
    inner_input.reset = 0;
    result = mosim_pid_step(inner_config, &state->inner, &inner_input, &inner_output);
    if (result != 0) { output->status_code = result; return result; }
    output->outer_command = outer_output.command;
    output->command = inner_output.command;
    output->saturated = outer_output.saturated || inner_output.saturated;
    return 0;
}
enum MosimPidAttitudeThrustAlgorithm {
    MOSIM_PID_CASCADE = 1,
    MOSIM_PID_GAIN_SCHEDULED = 2,
    MOSIM_PID_FUZZY = 3,
    MOSIM_PID_NEURAL = 4,
    MOSIM_PID_ANTI_WINDUP = 5,
    MOSIM_PID_FEEDFORWARD_PROFILE = 6
};

typedef struct {
    double x;
    double y;
    double z;
} MosimPidVec3;

typedef struct {
    double w;
    double x;
    double y;
    double z;
} MosimPidQuat;

typedef struct {
    int algorithm_id;
    MosimPidConfig position[3];
    MosimPidConfig velocity[3];
    double mass_kg;
    double gravity_mps2;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimPidAttitudeThrustParams;

typedef struct {
    MosimPidState position[3];
    MosimPidState velocity[3];
} MosimPidAttitudeThrustState;

typedef struct {
    int algorithm_id;
    double dt;
    MosimPidVec3 position_enu_m;
    MosimPidVec3 velocity_enu_mps;
    MosimPidQuat attitude_enu_flu_wxyz;
    MosimPidVec3 angular_velocity_flu_radps;
    MosimPidVec3 reference_position_enu_m;
    MosimPidVec3 reference_velocity_enu_mps;
    MosimPidVec3 reference_acceleration_enu_mps2;
    double reference_yaw_enu_rad;
    MosimPidVec3 schedule;
    MosimPidVec3 fuzzy_error;
    MosimPidVec3 neural_residual;
    int reset;
    int enable;
} MosimPidAttitudeThrustInput;

typedef struct {
    MosimPidQuat desired_attitude_enu_flu_wxyz;
    double desired_collective_thrust_n;
    MosimPidVec3 desired_acceleration_enu_mps2;
    MosimPidVec3 position_error_enu_m;
    MosimPidVec3 velocity_error_enu_mps;
    MosimPidVec3 scheduled_gain;
    int saturated;
    int status_code;
    int algorithm_id;
} MosimPidAttitudeThrustOutput;

void mosim_pid_attitude_thrust_default_params(
    int algorithm_id,
    MosimPidAttitudeThrustParams *params);
void mosim_pid_attitude_thrust_reset(MosimPidAttitudeThrustState *state);
int mosim_pid_attitude_thrust_step(
    const MosimPidAttitudeThrustParams *params,
    MosimPidAttitudeThrustState *state,
    const MosimPidAttitudeThrustInput *input,
    MosimPidAttitudeThrustOutput *output);




#include <math.h>
#include <stddef.h>
#include <string.h>

static double attitude_clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static MosimPidVec3 vec3(double x, double y, double z)
{
    MosimPidVec3 value = {x, y, z};
    return value;
}

static MosimPidVec3 cross(MosimPidVec3 a, MosimPidVec3 b)
{
    return vec3(a.y * b.z - a.z * b.y,
                a.z * b.x - a.x * b.z,
                a.x * b.y - a.y * b.x);
}

static double norm(MosimPidVec3 value)
{
    return sqrt(value.x * value.x + value.y * value.y + value.z * value.z);
}

static MosimPidVec3 normalize_vec3(MosimPidVec3 value, MosimPidVec3 fallback)
{
    const double magnitude = norm(value);
    if (!isfinite(magnitude) || magnitude <= 1.0e-12) return fallback;
    return vec3(value.x / magnitude, value.y / magnitude, value.z / magnitude);
}

static MosimPidQuat normalize_quat(MosimPidQuat value)
{
    const double magnitude = sqrt(value.w * value.w + value.x * value.x +
                                  value.y * value.y + value.z * value.z);
    MosimPidQuat identity = {1.0, 0.0, 0.0, 0.0};
    if (!isfinite(magnitude) || magnitude <= 1.0e-12) return identity;
    value.w /= magnitude;
    value.x /= magnitude;
    value.y /= magnitude;
    value.z /= magnitude;
    if (value.w < 0.0) {
        value.w = -value.w;
        value.x = -value.x;
        value.y = -value.y;
        value.z = -value.z;
    }
    return value;
}

static MosimPidQuat quat_from_columns(MosimPidVec3 b1, MosimPidVec3 b2,
                                      MosimPidVec3 b3)
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
    MosimPidQuat q;
    if (trace > 0.0) {
        const double s = 2.0 * sqrt(trace + 1.0);
        q.w = 0.25 * s;
        q.x = (m21 - m12) / s;
        q.y = (m02 - m20) / s;
        q.z = (m10 - m01) / s;
    } else if (m00 > m11 && m00 > m22) {
        const double s = 2.0 * sqrt(1.0 + m00 - m11 - m22);
        q.w = (m21 - m12) / s;
        q.x = 0.25 * s;
        q.y = (m01 + m10) / s;
        q.z = (m02 + m20) / s;
    } else if (m11 > m22) {
        const double s = 2.0 * sqrt(1.0 + m11 - m00 - m22);
        q.w = (m02 - m20) / s;
        q.x = (m01 + m10) / s;
        q.y = 0.25 * s;
        q.z = (m12 + m21) / s;
    } else {
        const double s = 2.0 * sqrt(1.0 + m22 - m00 - m11);
        q.w = (m10 - m01) / s;
        q.x = (m02 + m20) / s;
        q.y = (m12 + m21) / s;
        q.z = 0.25 * s;
    }
    return normalize_quat(q);
}

static int finite_vec3(MosimPidVec3 value)
{
    return isfinite(value.x) && isfinite(value.y) && isfinite(value.z);
}

static int finite_quat(MosimPidQuat value)
{
    return isfinite(value.w) && isfinite(value.x) &&
           isfinite(value.y) && isfinite(value.z);
}

static int valid_algorithm(int algorithm_id)
{
    return algorithm_id >= MOSIM_PID_CASCADE &&
           algorithm_id <= MOSIM_PID_FEEDFORWARD_PROFILE;
}

static void configure_axis(MosimPidConfig *position,
                           MosimPidConfig *velocity)
{
    mosim_pid_default_config(position);
    position->kp = 1.0;
    position->ki = 0.10;
    position->kd = 0.05;
    position->output_min = -2.0;
    position->output_max = 2.0;
    position->integral_min = -1.0;
    position->integral_max = 1.0;
    position->anti_windup_gain = 0.4;
    position->derivative_filter_tau = 0.05;

    mosim_pid_default_config(velocity);
    velocity->kp = 2.0;
    velocity->ki = 0.20;
    velocity->kd = 0.10;
    velocity->output_min = -5.0;
    velocity->output_max = 5.0;
    velocity->integral_min = -2.0;
    velocity->integral_max = 2.0;
    velocity->anti_windup_gain = 0.4;
    velocity->derivative_filter_tau = 0.03;
}

void mosim_pid_attitude_thrust_default_params(
    int algorithm_id,
    MosimPidAttitudeThrustParams *params)
{
    size_t axis;
    if (params == NULL) return;
    memset(params, 0, sizeof(*params));
    params->algorithm_id = algorithm_id;
    for (axis = 0; axis < 3; ++axis) {
        configure_axis(&params->position[axis], &params->velocity[axis]);
    }
    if (algorithm_id == MOSIM_PID_GAIN_SCHEDULED) {
        for (axis = 0; axis < 3; ++axis) params->velocity[axis].schedule_gain = 0.4;
    } else if (algorithm_id == MOSIM_PID_FUZZY) {
        for (axis = 0; axis < 3; ++axis) params->velocity[axis].fuzzy_gain = 0.3;
    } else if (algorithm_id == MOSIM_PID_NEURAL) {
        for (axis = 0; axis < 3; ++axis) {
            params->velocity[axis].neural_gain = 0.2;
            params->velocity[axis].neural_residual_limit = 0.25;
        }
    } else if (algorithm_id == MOSIM_PID_ANTI_WINDUP) {
        for (axis = 0; axis < 3; ++axis) {
            params->position[axis].anti_windup_gain = 1.0;
            params->velocity[axis].anti_windup_gain = 1.0;
        }
    } else if (algorithm_id == MOSIM_PID_FEEDFORWARD_PROFILE) {
        for (axis = 0; axis < 3; ++axis) params->velocity[axis].feedforward_gain = 1.0;
    }
    params->mass_kg = 1.0;
    params->gravity_mps2 = 9.80665;
    params->max_tilt_rad = 0.52359877559829887308;
    params->min_collective_thrust_n = 0.0;
    params->max_collective_thrust_n = 19.6133;
}

void mosim_pid_attitude_thrust_reset(MosimPidAttitudeThrustState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

static double component(MosimPidVec3 value, size_t axis)
{
    if (axis == 0) return value.x;
    if (axis == 1) return value.y;
    return value.z;
}

static void set_component(MosimPidVec3 *value, size_t axis, double item)
{
    if (axis == 0) value->x = item;
    else if (axis == 1) value->y = item;
    else value->z = item;
}

static int valid_input(const MosimPidAttitudeThrustParams *params,
                       const MosimPidAttitudeThrustInput *input)
{
    return params != NULL && input != NULL && valid_algorithm(input->algorithm_id) &&
           params->algorithm_id == input->algorithm_id &&
           isfinite(input->dt) && input->dt > 0.0 &&
           isfinite(params->mass_kg) && params->mass_kg > 0.0 &&
           isfinite(params->gravity_mps2) && params->gravity_mps2 > 0.0 &&
           isfinite(params->max_tilt_rad) && params->max_tilt_rad >= 0.0 &&
           params->max_tilt_rad < 1.57079632679489661923 &&
           isfinite(params->min_collective_thrust_n) &&
           isfinite(params->max_collective_thrust_n) &&
           params->min_collective_thrust_n <= params->max_collective_thrust_n &&
           finite_vec3(input->position_enu_m) &&
           finite_vec3(input->velocity_enu_mps) &&
           finite_quat(input->attitude_enu_flu_wxyz) &&
           finite_vec3(input->angular_velocity_flu_radps) &&
           finite_vec3(input->reference_position_enu_m) &&
           finite_vec3(input->reference_velocity_enu_mps) &&
           finite_vec3(input->reference_acceleration_enu_mps2) &&
           isfinite(input->reference_yaw_enu_rad) &&
           finite_vec3(input->schedule) && finite_vec3(input->fuzzy_error) &&
           finite_vec3(input->neural_residual);
}

int mosim_pid_attitude_thrust_step(
    const MosimPidAttitudeThrustParams *params,
    MosimPidAttitudeThrustState *state,
    const MosimPidAttitudeThrustInput *input,
    MosimPidAttitudeThrustOutput *output)
{
    MosimPidAttitudeThrustState working_state;
    MosimPidVec3 acceleration = {0.0, 0.0, 0.0};
    MosimPidVec3 b1d;
    MosimPidVec3 b2;
    MosimPidVec3 b1;
    MosimPidVec3 b3;
    double horizontal;
    double horizontal_limit;
    double thrust;
    size_t axis;
    if (output == NULL || state == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_enu_flu_wxyz.w = 1.0;
    output->status_code = -1;
    if (!valid_input(params, input)) return -1;
    output->algorithm_id = input->algorithm_id;
    if (!input->enable) {
        if (input->reset) mosim_pid_attitude_thrust_reset(state);
        output->desired_attitude_enu_flu_wxyz =
            normalize_quat(input->attitude_enu_flu_wxyz);
        output->status_code = 1;
        return 0;
    }
    working_state = *state;
    if (input->reset) mosim_pid_attitude_thrust_reset(&working_state);

    for (axis = 0; axis < 3; ++axis) {
        MosimPidInput position_input;
        MosimPidInput velocity_input;
        MosimPidOutput position_output;
        MosimPidOutput velocity_output;
        const double reference_position = component(input->reference_position_enu_m, axis);
        const double position = component(input->position_enu_m, axis);
        const double reference_velocity = component(input->reference_velocity_enu_mps, axis);
        const double velocity = component(input->velocity_enu_mps, axis);
        memset(&position_input, 0, sizeof(position_input));
        position_input.setpoint = reference_position;
        position_input.measurement = position;
        position_input.schedule = component(input->schedule, axis);
        position_input.fuzzy_error = component(input->fuzzy_error, axis);
        position_input.neural_residual = component(input->neural_residual, axis);
        position_input.dt = input->dt;
        position_input.enable = 1;
        if (mosim_pid_step(&params->position[axis], &working_state.position[axis],
                           &position_input, &position_output) != 0) return -1;

        memset(&velocity_input, 0, sizeof(velocity_input));
        velocity_input.setpoint = reference_velocity + position_output.command;
        velocity_input.measurement = velocity;
        velocity_input.feedforward = component(input->reference_acceleration_enu_mps2, axis);
        velocity_input.schedule = component(input->schedule, axis);
        velocity_input.fuzzy_error = component(input->fuzzy_error, axis);
        velocity_input.neural_residual = component(input->neural_residual, axis);
        velocity_input.dt = input->dt;
        velocity_input.enable = 1;
        if (mosim_pid_step(&params->velocity[axis], &working_state.velocity[axis],
                           &velocity_input, &velocity_output) != 0) return -1;
        set_component(&acceleration, axis, velocity_output.command);
        set_component(&output->position_error_enu_m, axis, reference_position - position);
        set_component(&output->velocity_error_enu_mps, axis,
                      velocity_input.setpoint - velocity);
        set_component(&output->scheduled_gain, axis, velocity_output.scheduled_gain);
        output->saturated = output->saturated || position_output.saturated ||
                            velocity_output.saturated;
    }

    acceleration.z += params->gravity_mps2;
    horizontal = hypot(acceleration.x, acceleration.y);
    horizontal_limit = fmax(acceleration.z, 0.0) * tan(params->max_tilt_rad);
    if (horizontal > horizontal_limit && horizontal > 1.0e-12) {
        const double scale = horizontal_limit / horizontal;
        acceleration.x *= scale;
        acceleration.y *= scale;
        output->saturated = 1;
    }
    b3 = normalize_vec3(acceleration, vec3(0.0, 0.0, 1.0));
    b1d = vec3(cos(input->reference_yaw_enu_rad),
               sin(input->reference_yaw_enu_rad), 0.0);
    b2 = cross(b3, b1d);
    if (norm(b2) <= 1.0e-9) b2 = cross(b3, vec3(0.0, 1.0, 0.0));
    b2 = normalize_vec3(b2, vec3(0.0, 1.0, 0.0));
    b1 = normalize_vec3(cross(b2, b3), b1d);
    output->desired_attitude_enu_flu_wxyz = quat_from_columns(b1, b2, b3);
    thrust = params->mass_kg * norm(acceleration);
    output->desired_collective_thrust_n = attitude_clamp_value(
        thrust, params->min_collective_thrust_n,
        params->max_collective_thrust_n);
    if (fabs(output->desired_collective_thrust_n - thrust) > 1.0e-12)
        output->saturated = 1;
    output->desired_acceleration_enu_mps2 = acceleration;
    output->status_code = 0;
    *state = working_state;
    return 0;
}
void MosimPidAttitudeThrustStepScalar(
    double algorithm_id,
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
    double reference_yaw,
    double mass_kg,
    double gravity_mps2,
    double max_tilt_rad,
    double min_collective_thrust_n,
    double max_collective_thrust_n,
    double schedule_x,
    double schedule_y,
    double schedule_z,
    double fuzzy_error_x,
    double fuzzy_error_y,
    double fuzzy_error_z,
    double neural_residual_x,
    double neural_residual_y,
    double neural_residual_z,
    double enable,
    double reset,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *desired_collective_thrust_n,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *position_error_x,
    double *position_error_y,
    double *position_error_z,
    double *velocity_error_x,
    double *velocity_error_y,
    double *velocity_error_z,
    double *scheduled_gain_x,
    double *scheduled_gain_y,
    double *scheduled_gain_z,
    double *saturated,
    double *status_code,
    double *algorithm_id_out)
{
    static MosimPidAttitudeThrustState states[7];
    MosimPidAttitudeThrustParams params;
    MosimPidAttitudeThrustInput input;
    MosimPidAttitudeThrustOutput output;
    int id = (int)algorithm_id;
    memset(&input, 0, sizeof(input));
    input.algorithm_id = id;
    input.dt = dt;
    input.position_enu_m = vec3(position_x, position_y, position_z);
    input.velocity_enu_mps = vec3(velocity_x, velocity_y, velocity_z);
    input.attitude_enu_flu_wxyz.w = attitude_w;
    input.attitude_enu_flu_wxyz.x = attitude_x;
    input.attitude_enu_flu_wxyz.y = attitude_y;
    input.attitude_enu_flu_wxyz.z = attitude_z;
    input.angular_velocity_flu_radps = vec3(angular_velocity_x, angular_velocity_y, angular_velocity_z);
    input.reference_position_enu_m = vec3(reference_position_x, reference_position_y, reference_position_z);
    input.reference_velocity_enu_mps = vec3(reference_velocity_x, reference_velocity_y, reference_velocity_z);
    input.reference_acceleration_enu_mps2 = vec3(reference_acceleration_x, reference_acceleration_y, reference_acceleration_z);
    input.reference_yaw_enu_rad = reference_yaw;
    input.schedule = vec3(schedule_x, schedule_y, schedule_z);
    input.fuzzy_error = vec3(fuzzy_error_x, fuzzy_error_y, fuzzy_error_z);
    input.neural_residual = vec3(neural_residual_x, neural_residual_y, neural_residual_z);
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    mosim_pid_attitude_thrust_default_params(id, &params);
    params.mass_kg = mass_kg;
    params.gravity_mps2 = gravity_mps2;
    params.max_tilt_rad = max_tilt_rad;
    params.min_collective_thrust_n = min_collective_thrust_n;
    params.max_collective_thrust_n = max_collective_thrust_n;
    if (id < 1 || id > 6 || mosim_pid_attitude_thrust_step(&params, &states[id], &input, &output) != 0) {
        memset(&output, 0, sizeof(output));
        output.desired_attitude_enu_flu_wxyz.w = 1.0;
        output.status_code = -1;
    }
    *desired_attitude_w = output.desired_attitude_enu_flu_wxyz.w;
    *desired_attitude_x = output.desired_attitude_enu_flu_wxyz.x;
    *desired_attitude_y = output.desired_attitude_enu_flu_wxyz.y;
    *desired_attitude_z = output.desired_attitude_enu_flu_wxyz.z;
    *desired_collective_thrust_n = output.desired_collective_thrust_n;
    *desired_acceleration_x = output.desired_acceleration_enu_mps2.x;
    *desired_acceleration_y = output.desired_acceleration_enu_mps2.y;
    *desired_acceleration_z = output.desired_acceleration_enu_mps2.z;
    *position_error_x = output.position_error_enu_m.x;
    *position_error_y = output.position_error_enu_m.y;
    *position_error_z = output.position_error_enu_m.z;
    *velocity_error_x = output.velocity_error_enu_mps.x;
    *velocity_error_y = output.velocity_error_enu_mps.y;
    *velocity_error_z = output.velocity_error_enu_mps.z;
    *scheduled_gain_x = output.scheduled_gain.x;
    *scheduled_gain_y = output.scheduled_gain.y;
    *scheduled_gain_z = output.scheduled_gain.z;
    *saturated = (double)output.saturated;
    *status_code = (double)output.status_code;
    *algorithm_id_out = (double)output.algorithm_id;
}
");
    end func_CFunction;

    SysplorerEmbeddedCoder.Port.Inport algorithm_id
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
    SysplorerEmbeddedCoder.Port.Inport reference_yaw
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport mass_kg
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport gravity_mps2
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport max_tilt_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport min_collective_thrust_n
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport max_collective_thrust_n
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport schedule_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport schedule_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport schedule_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fuzzy_error_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fuzzy_error_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fuzzy_error_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport neural_residual_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport neural_residual_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport neural_residual_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport enable
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reset
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_attitude_w
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_attitude_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_attitude_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_attitude_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_collective_thrust_n
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z
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
    SysplorerEmbeddedCoder.Port.Outport scheduled_gain_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport scheduled_gain_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport scheduled_gain_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport saturated
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport status_code
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport algorithm_id_out
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
  equation
    (desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, desired_collective_thrust_n, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, position_error_x, position_error_y, position_error_z, velocity_error_x, velocity_error_y, velocity_error_z, scheduled_gain_x, scheduled_gain_y, scheduled_gain_z, saturated, status_code, algorithm_id_out) = func_CFunction(algorithm_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, attitude_w, attitude_x, attitude_y, attitude_z, angular_velocity_x, angular_velocity_y, angular_velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_yaw, mass_kg, gravity_mps2, max_tilt_rad, min_collective_thrust_n, max_collective_thrust_n, schedule_x, schedule_y, schedule_z, fuzzy_error_x, fuzzy_error_y, fuzzy_error_z, neural_residual_x, neural_residual_y, neural_residual_z, enable, reset);
  end CFunction;

equation
  connect(algorithm_id_in, cFunction.algorithm_id) annotation(Line(origin={0,0},points={{-250,250},{-50,250}},color={0,0,0}));
  connect(dt_in, cFunction.dt) annotation(Line(origin={0,0},points={{-250,244},{-50,244}},color={0,0,0}));
  connect(position_x_in, cFunction.position_x) annotation(Line(origin={0,0},points={{-250,238},{-50,238}},color={0,0,0}));
  connect(position_y_in, cFunction.position_y) annotation(Line(origin={0,0},points={{-250,232},{-50,232}},color={0,0,0}));
  connect(position_z_in, cFunction.position_z) annotation(Line(origin={0,0},points={{-250,226},{-50,226}},color={0,0,0}));
  connect(velocity_x_in, cFunction.velocity_x) annotation(Line(origin={0,0},points={{-250,220},{-50,220}},color={0,0,0}));
  connect(velocity_y_in, cFunction.velocity_y) annotation(Line(origin={0,0},points={{-250,214},{-50,214}},color={0,0,0}));
  connect(velocity_z_in, cFunction.velocity_z) annotation(Line(origin={0,0},points={{-250,208},{-50,208}},color={0,0,0}));
  connect(attitude_w_in, cFunction.attitude_w) annotation(Line(origin={0,0},points={{-250,202},{-50,202}},color={0,0,0}));
  connect(attitude_x_in, cFunction.attitude_x) annotation(Line(origin={0,0},points={{-250,196},{-50,196}},color={0,0,0}));
  connect(attitude_y_in, cFunction.attitude_y) annotation(Line(origin={0,0},points={{-250,190},{-50,190}},color={0,0,0}));
  connect(attitude_z_in, cFunction.attitude_z) annotation(Line(origin={0,0},points={{-250,184},{-50,184}},color={0,0,0}));
  connect(angular_velocity_x_in, cFunction.angular_velocity_x) annotation(Line(origin={0,0},points={{-250,178},{-50,178}},color={0,0,0}));
  connect(angular_velocity_y_in, cFunction.angular_velocity_y) annotation(Line(origin={0,0},points={{-250,172},{-50,172}},color={0,0,0}));
  connect(angular_velocity_z_in, cFunction.angular_velocity_z) annotation(Line(origin={0,0},points={{-250,166},{-50,166}},color={0,0,0}));
  connect(reference_position_x_in, cFunction.reference_position_x) annotation(Line(origin={0,0},points={{-250,160},{-50,160}},color={0,0,0}));
  connect(reference_position_y_in, cFunction.reference_position_y) annotation(Line(origin={0,0},points={{-250,154},{-50,154}},color={0,0,0}));
  connect(reference_position_z_in, cFunction.reference_position_z) annotation(Line(origin={0,0},points={{-250,148},{-50,148}},color={0,0,0}));
  connect(reference_velocity_x_in, cFunction.reference_velocity_x) annotation(Line(origin={0,0},points={{-250,142},{-50,142}},color={0,0,0}));
  connect(reference_velocity_y_in, cFunction.reference_velocity_y) annotation(Line(origin={0,0},points={{-250,136},{-50,136}},color={0,0,0}));
  connect(reference_velocity_z_in, cFunction.reference_velocity_z) annotation(Line(origin={0,0},points={{-250,130},{-50,130}},color={0,0,0}));
  connect(reference_acceleration_x_in, cFunction.reference_acceleration_x) annotation(Line(origin={0,0},points={{-250,124},{-50,124}},color={0,0,0}));
  connect(reference_acceleration_y_in, cFunction.reference_acceleration_y) annotation(Line(origin={0,0},points={{-250,118},{-50,118}},color={0,0,0}));
  connect(reference_acceleration_z_in, cFunction.reference_acceleration_z) annotation(Line(origin={0,0},points={{-250,112},{-50,112}},color={0,0,0}));
  connect(reference_yaw_in, cFunction.reference_yaw) annotation(Line(origin={0,0},points={{-250,106},{-50,106}},color={0,0,0}));
  connect(mass_kg_in, cFunction.mass_kg) annotation(Line(origin={0,0},points={{-250,100},{-50,100}},color={0,0,0}));
  connect(gravity_mps2_in, cFunction.gravity_mps2) annotation(Line(origin={0,0},points={{-250,94},{-50,94}},color={0,0,0}));
  connect(max_tilt_rad_in, cFunction.max_tilt_rad) annotation(Line(origin={0,0},points={{-250,88},{-50,88}},color={0,0,0}));
  connect(min_collective_thrust_n_in, cFunction.min_collective_thrust_n) annotation(Line(origin={0,0},points={{-250,82},{-50,82}},color={0,0,0}));
  connect(max_collective_thrust_n_in, cFunction.max_collective_thrust_n) annotation(Line(origin={0,0},points={{-250,76},{-50,76}},color={0,0,0}));
  connect(schedule_x_in, cFunction.schedule_x) annotation(Line(origin={0,0},points={{-250,70},{-50,70}},color={0,0,0}));
  connect(schedule_y_in, cFunction.schedule_y) annotation(Line(origin={0,0},points={{-250,64},{-50,64}},color={0,0,0}));
  connect(schedule_z_in, cFunction.schedule_z) annotation(Line(origin={0,0},points={{-250,58},{-50,58}},color={0,0,0}));
  connect(fuzzy_error_x_in, cFunction.fuzzy_error_x) annotation(Line(origin={0,0},points={{-250,52},{-50,52}},color={0,0,0}));
  connect(fuzzy_error_y_in, cFunction.fuzzy_error_y) annotation(Line(origin={0,0},points={{-250,46},{-50,46}},color={0,0,0}));
  connect(fuzzy_error_z_in, cFunction.fuzzy_error_z) annotation(Line(origin={0,0},points={{-250,40},{-50,40}},color={0,0,0}));
  connect(neural_residual_x_in, cFunction.neural_residual_x) annotation(Line(origin={0,0},points={{-250,34},{-50,34}},color={0,0,0}));
  connect(neural_residual_y_in, cFunction.neural_residual_y) annotation(Line(origin={0,0},points={{-250,28},{-50,28}},color={0,0,0}));
  connect(neural_residual_z_in, cFunction.neural_residual_z) annotation(Line(origin={0,0},points={{-250,22},{-50,22}},color={0,0,0}));
  connect(enable_in, cFunction.enable) annotation(Line(origin={0,0},points={{-250,16},{-50,16}},color={0,0,0}));
  connect(reset_in, cFunction.reset) annotation(Line(origin={0,0},points={{-250,10},{-50,10}},color={0,0,0}));
  connect(cFunction.desired_attitude_w, desired_attitude_w_out) annotation(Line(origin={0,0},points={{50,160},{250,160}},color={0,0,0}));
  connect(cFunction.desired_attitude_x, desired_attitude_x_out) annotation(Line(origin={0,0},points={{50,153},{250,153}},color={0,0,0}));
  connect(cFunction.desired_attitude_y, desired_attitude_y_out) annotation(Line(origin={0,0},points={{50,146},{250,146}},color={0,0,0}));
  connect(cFunction.desired_attitude_z, desired_attitude_z_out) annotation(Line(origin={0,0},points={{50,139},{250,139}},color={0,0,0}));
  connect(cFunction.desired_collective_thrust_n, desired_collective_thrust_n_out) annotation(Line(origin={0,0},points={{50,132},{250,132}},color={0,0,0}));
  connect(cFunction.desired_acceleration_x, desired_acceleration_x_out) annotation(Line(origin={0,0},points={{50,125},{250,125}},color={0,0,0}));
  connect(cFunction.desired_acceleration_y, desired_acceleration_y_out) annotation(Line(origin={0,0},points={{50,118},{250,118}},color={0,0,0}));
  connect(cFunction.desired_acceleration_z, desired_acceleration_z_out) annotation(Line(origin={0,0},points={{50,111},{250,111}},color={0,0,0}));
  connect(cFunction.position_error_x, position_error_x_out) annotation(Line(origin={0,0},points={{50,104},{250,104}},color={0,0,0}));
  connect(cFunction.position_error_y, position_error_y_out) annotation(Line(origin={0,0},points={{50,97},{250,97}},color={0,0,0}));
  connect(cFunction.position_error_z, position_error_z_out) annotation(Line(origin={0,0},points={{50,90},{250,90}},color={0,0,0}));
  connect(cFunction.velocity_error_x, velocity_error_x_out) annotation(Line(origin={0,0},points={{50,83},{250,83}},color={0,0,0}));
  connect(cFunction.velocity_error_y, velocity_error_y_out) annotation(Line(origin={0,0},points={{50,76},{250,76}},color={0,0,0}));
  connect(cFunction.velocity_error_z, velocity_error_z_out) annotation(Line(origin={0,0},points={{50,69},{250,69}},color={0,0,0}));
  connect(cFunction.scheduled_gain_x, scheduled_gain_x_out) annotation(Line(origin={0,0},points={{50,62},{250,62}},color={0,0,0}));
  connect(cFunction.scheduled_gain_y, scheduled_gain_y_out) annotation(Line(origin={0,0},points={{50,55},{250,55}},color={0,0,0}));
  connect(cFunction.scheduled_gain_z, scheduled_gain_z_out) annotation(Line(origin={0,0},points={{50,48},{250,48}},color={0,0,0}));
  connect(cFunction.saturated, saturated_out) annotation(Line(origin={0,0},points={{50,41},{250,41}},color={0,0,0}));
  connect(cFunction.status_code, status_code_out) annotation(Line(origin={0,0},points={{50,34},{250,34}},color={0,0,0}));
  connect(cFunction.algorithm_id_out, algorithm_id_out_out) annotation(Line(origin={0,0},points={{50,27},{250,27}},color={0,0,0}));
end MoSim_PID_AttitudeThrust_CFunction_Sysblock;