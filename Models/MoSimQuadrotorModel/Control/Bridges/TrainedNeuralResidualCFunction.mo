within MoSimQuadrotorModel.Control.Bridges;
model TrainedNeuralResidualCFunction
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left(mode_in, dt_in, position_x_in, position_y_in, position_z_in, velocity_x_in, velocity_y_in, velocity_z_in, attitude_w_in, attitude_x_in, attitude_y_in, attitude_z_in, angular_velocity_x_in, angular_velocity_y_in, angular_velocity_z_in, reference_position_x_in, reference_position_y_in, reference_position_z_in, reference_velocity_x_in, reference_velocity_y_in, reference_velocity_z_in, reference_acceleration_x_in, reference_acceleration_y_in, reference_acceleration_z_in, reference_yaw_in, mass_kg_in, gravity_mps2_in, hover_percentage_in, max_tilt_rad_in, min_collective_thrust_n_in, max_collective_thrust_n_in, enable_in, learning_enable_in, reset_in), Right(desired_attitude_w_out, desired_attitude_x_out, desired_attitude_y_out, desired_attitude_z_out, desired_collective_thrust_n_out, normalized_thrust_out, desired_acceleration_x_out, desired_acceleration_y_out, desired_acceleration_z_out, learning_action_x_out, learning_action_y_out, learning_action_z_out, scheduled_gain_x_out, scheduled_gain_y_out, scheduled_gain_z_out, fallback_active_out, status_code_out, mode_out_out)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\g6_formal_champion_promotion_20260725\\trained_neural_residual\\generated_c"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{-620,-456.00},{620,456.00}},grid={2,2})));

  CFunction cFunction
    annotation (Placement(transformation(origin={0,0}, extent={{-80,-396.00},{80,396.00}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mode_in
    annotation (Placement(transformation(origin={-500,396.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport dt_in
    annotation (Placement(transformation(origin={-500,372.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_x_in
    annotation (Placement(transformation(origin={-500,348.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_y_in
    annotation (Placement(transformation(origin={-500,324.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_z_in
    annotation (Placement(transformation(origin={-500,300.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_x_in
    annotation (Placement(transformation(origin={-500,276.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_y_in
    annotation (Placement(transformation(origin={-500,252.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_z_in
    annotation (Placement(transformation(origin={-500,228.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_w_in
    annotation (Placement(transformation(origin={-500,204.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_x_in
    annotation (Placement(transformation(origin={-500,180.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_y_in
    annotation (Placement(transformation(origin={-500,156.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_z_in
    annotation (Placement(transformation(origin={-500,132.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport angular_velocity_x_in
    annotation (Placement(transformation(origin={-500,108.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport angular_velocity_y_in
    annotation (Placement(transformation(origin={-500,84.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport angular_velocity_z_in
    annotation (Placement(transformation(origin={-500,60.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x_in
    annotation (Placement(transformation(origin={-500,36.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y_in
    annotation (Placement(transformation(origin={-500,12.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z_in
    annotation (Placement(transformation(origin={-500,-12.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x_in
    annotation (Placement(transformation(origin={-500,-36.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y_in
    annotation (Placement(transformation(origin={-500,-60.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z_in
    annotation (Placement(transformation(origin={-500,-84.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x_in
    annotation (Placement(transformation(origin={-500,-108.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y_in
    annotation (Placement(transformation(origin={-500,-132.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z_in
    annotation (Placement(transformation(origin={-500,-156.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_yaw_in
    annotation (Placement(transformation(origin={-500,-180.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mass_kg_in
    annotation (Placement(transformation(origin={-500,-204.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport gravity_mps2_in
    annotation (Placement(transformation(origin={-500,-228.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport hover_percentage_in
    annotation (Placement(transformation(origin={-500,-252.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport max_tilt_rad_in
    annotation (Placement(transformation(origin={-500,-276.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport min_collective_thrust_n_in
    annotation (Placement(transformation(origin={-500,-300.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport max_collective_thrust_n_in
    annotation (Placement(transformation(origin={-500,-324.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_in
    annotation (Placement(transformation(origin={-500,-348.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport learning_enable_in
    annotation (Placement(transformation(origin={-500,-372.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reset_in
    annotation (Placement(transformation(origin={-500,-396.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_w_out
    annotation (Placement(transformation(origin={500,396.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_x_out
    annotation (Placement(transformation(origin={500,349.41},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_y_out
    annotation (Placement(transformation(origin={500,302.82},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_z_out
    annotation (Placement(transformation(origin={500,256.24},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_collective_thrust_n_out
    annotation (Placement(transformation(origin={500,209.65},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out
    annotation (Placement(transformation(origin={500,163.06},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out
    annotation (Placement(transformation(origin={500,116.47},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out
    annotation (Placement(transformation(origin={500,69.88},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out
    annotation (Placement(transformation(origin={500,23.29},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport learning_action_x_out
    annotation (Placement(transformation(origin={500,-23.29},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport learning_action_y_out
    annotation (Placement(transformation(origin={500,-69.88},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport learning_action_z_out
    annotation (Placement(transformation(origin={500,-116.47},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain_x_out
    annotation (Placement(transformation(origin={500,-163.06},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain_y_out
    annotation (Placement(transformation(origin={500,-209.65},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain_z_out
    annotation (Placement(transformation(origin={500,-256.24},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport fallback_active_out
    annotation (Placement(transformation(origin={500,-302.82},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport status_code_out
    annotation (Placement(transformation(origin={500,-349.41},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport mode_out_out
    annotation (Placement(transformation(origin={500,-396.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left(mode, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, attitude_w, attitude_x, attitude_y, attitude_z, angular_velocity_x, angular_velocity_y, angular_velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_yaw, mass_kg, gravity_mps2, hover_percentage, max_tilt_rad, min_collective_thrust_n, max_collective_thrust_n, enable, learning_enable, reset), Right(desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, desired_collective_thrust_n, normalized_thrust, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, learning_action_x, learning_action_y, learning_action_z, scheduled_gain_x, scheduled_gain_y, scheduled_gain_z, fallback_active, status_code, mode_out)),PortLabels(labelType="CustomType",labels(label(text="mode",instance="mode"),label(text="dt",instance="dt"),label(text="position_x",instance="position_x"),label(text="position_y",instance="position_y"),label(text="position_z",instance="position_z"),label(text="velocity_x",instance="velocity_x"),label(text="velocity_y",instance="velocity_y"),label(text="velocity_z",instance="velocity_z"),label(text="attitude_w",instance="attitude_w"),label(text="attitude_x",instance="attitude_x"),label(text="attitude_y",instance="attitude_y"),label(text="attitude_z",instance="attitude_z"),label(text="angular_velocity_x",instance="angular_velocity_x"),label(text="angular_velocity_y",instance="angular_velocity_y"),label(text="angular_velocity_z",instance="angular_velocity_z"),label(text="reference_position_x",instance="reference_position_x"),label(text="reference_position_y",instance="reference_position_y"),label(text="reference_position_z",instance="reference_position_z"),label(text="reference_velocity_x",instance="reference_velocity_x"),label(text="reference_velocity_y",instance="reference_velocity_y"),label(text="reference_velocity_z",instance="reference_velocity_z"),label(text="reference_acceleration_x",instance="reference_acceleration_x"),label(text="reference_acceleration_y",instance="reference_acceleration_y"),label(text="reference_acceleration_z",instance="reference_acceleration_z"),label(text="reference_yaw",instance="reference_yaw"),label(text="mass_kg",instance="mass_kg"),label(text="gravity_mps2",instance="gravity_mps2"),label(text="hover_percentage",instance="hover_percentage"),label(text="max_tilt_rad",instance="max_tilt_rad"),label(text="min_collective_thrust_n",instance="min_collective_thrust_n"),label(text="max_collective_thrust_n",instance="max_collective_thrust_n"),label(text="enable",instance="enable"),label(text="learning_enable",instance="learning_enable"),label(text="reset",instance="reset"),label(text="desired_attitude_w",instance="desired_attitude_w"),label(text="desired_attitude_x",instance="desired_attitude_x"),label(text="desired_attitude_y",instance="desired_attitude_y"),label(text="desired_attitude_z",instance="desired_attitude_z"),label(text="desired_collective_thrust_n",instance="desired_collective_thrust_n"),label(text="normalized_thrust",instance="normalized_thrust"),label(text="desired_acceleration_x",instance="desired_acceleration_x"),label(text="desired_acceleration_y",instance="desired_acceleration_y"),label(text="desired_acceleration_z",instance="desired_acceleration_z"),label(text="learning_action_x",instance="learning_action_x"),label(text="learning_action_y",instance="learning_action_y"),label(text="learning_action_z",instance="learning_action_z"),label(text="scheduled_gain_x",instance="scheduled_gain_x"),label(text="scheduled_gain_y",instance="scheduled_gain_y"),label(text="scheduled_gain_z",instance="scheduled_gain_z"),label(text="fallback_active",instance="fallback_active"),label(text="status_code",instance="status_code"),label(text="mode_out",instance="mode_out"))),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
      Icon(coordinateSystem(extent={{-200,-100},{200,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2}),graphics={Rectangle(origin={0,0},fillColor={255,255,255},fillPattern=FillPattern.Solid,extent={{-200,100},{200,-100}}),Text(origin={0,0},extent={{-100,20},{100,-20}},textString="C",verticalAlignment=TextAlignment.VCenter),Text(origin={0,-120},lineColor={0,0,0},extent={{-150,20},{150,-20}},textString="%name",fontSize=14,textColor={0,0,0},verticalAlignment=TextAlignment.Top)}),
      Diagram(coordinateSystem(extent={{-100,-100},{100,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2})));

    function func_CFunction
      input SysplorerEmbeddedCoder.Types.Auto mode annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
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
      input SysplorerEmbeddedCoder.Types.Auto hover_percentage annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto max_tilt_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto min_collective_thrust_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto max_collective_thrust_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto enable annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto learning_enable annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reset annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_collective_thrust_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto normalized_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto learning_action_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto learning_action_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto learning_action_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto scheduled_gain_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto scheduled_gain_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto scheduled_gain_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto fallback_active annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto status_code annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto mode_out annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
    external "C" MosimLearningAttitudeThrustStepScalar(mode,dt,position_x,position_y,position_z,velocity_x,velocity_y,velocity_z,attitude_w,attitude_x,attitude_y,attitude_z,angular_velocity_x,angular_velocity_y,angular_velocity_z,reference_position_x,reference_position_y,reference_position_z,reference_velocity_x,reference_velocity_y,reference_velocity_z,reference_acceleration_x,reference_acceleration_y,reference_acceleration_z,reference_yaw,mass_kg,gravity_mps2,hover_percentage,max_tilt_rad,min_collective_thrust_n,max_collective_thrust_n,enable,learning_enable,reset,desired_attitude_w,desired_attitude_x,desired_attitude_y,desired_attitude_z,desired_collective_thrust_n,normalized_thrust,desired_acceleration_x,desired_acceleration_y,desired_acceleration_z,learning_action_x,learning_action_y,learning_action_z,scheduled_gain_x,scheduled_gain_y,scheduled_gain_z,fallback_active,status_code,mode_out)
      annotation (Include="#define MOSIM_LEARNING_OBSERVATION_SIZE 12
#define MOSIM_LEARNING_ACTION_SIZE 3
#define MOSIM_NEURAL_HIDDEN_SIZE 12
#define MOSIM_RL_HIDDEN_SIZE 16
#define MOSIM_LEARNING_ARTIFACT_SHA256 \"4d480c6ad4738da75b4f7bfdf824658b7878ea511a52935ed2be4fff0d043e45\"
typedef struct {
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
int mosim_pid_attitude_thrust_apply_acceleration(
    const MosimPidAttitudeThrustParams *params,
    double reference_yaw_enu_rad,
    MosimPidVec3 desired_acceleration_enu_mps2,
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
        for (axis = 0; axis < 3; ++axis) params->velocity[axis].feedforward_gain = 0.5;
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
    if (mosim_pid_attitude_thrust_apply_acceleration(
            params, input->reference_yaw_enu_rad, acceleration, output) != 0) return -1;
    output->status_code = 0;
    *state = working_state;
    return 0;
}

int mosim_pid_attitude_thrust_apply_acceleration(
    const MosimPidAttitudeThrustParams *params,
    double reference_yaw_enu_rad,
    MosimPidVec3 desired_acceleration_enu_mps2,
    MosimPidAttitudeThrustOutput *output)
{
    MosimPidVec3 b1d;
    MosimPidVec3 b2;
    MosimPidVec3 b1;
    MosimPidVec3 b3;
    double horizontal;
    double horizontal_limit;
    double thrust;
    if (params == NULL || output == NULL || !finite_vec3(desired_acceleration_enu_mps2) ||
        !isfinite(reference_yaw_enu_rad) || !isfinite(params->mass_kg) ||
        params->mass_kg <= 0.0 || !isfinite(params->max_tilt_rad) ||
        params->max_tilt_rad < 0.0 || params->max_tilt_rad >= 1.57079632679489661923 ||
        !isfinite(params->min_collective_thrust_n) ||
        !isfinite(params->max_collective_thrust_n) ||
        params->min_collective_thrust_n > params->max_collective_thrust_n) return -1;
    horizontal = hypot(desired_acceleration_enu_mps2.x, desired_acceleration_enu_mps2.y);
    horizontal_limit = fmax(desired_acceleration_enu_mps2.z, 0.0) * tan(params->max_tilt_rad);
    if (horizontal > horizontal_limit && horizontal > 1.0e-12) {
        const double scale = horizontal_limit / horizontal;
        desired_acceleration_enu_mps2.x *= scale;
        desired_acceleration_enu_mps2.y *= scale;
        output->saturated = 1;
    }
    b3 = normalize_vec3(desired_acceleration_enu_mps2, vec3(0.0, 0.0, 1.0));
    b1d = vec3(cos(reference_yaw_enu_rad), sin(reference_yaw_enu_rad), 0.0);
    b2 = cross(b3, b1d);
    if (norm(b2) <= 1.0e-9) b2 = cross(b3, vec3(0.0, 1.0, 0.0));
    b2 = normalize_vec3(b2, vec3(0.0, 1.0, 0.0));
    b1 = normalize_vec3(cross(b2, b3), b1d);
    output->desired_attitude_enu_flu_wxyz = quat_from_columns(b1, b2, b3);
    thrust = params->mass_kg * norm(desired_acceleration_enu_mps2);
    output->desired_collective_thrust_n = attitude_clamp_value(
        thrust, params->min_collective_thrust_n,
        params->max_collective_thrust_n);
    if (fabs(output->desired_collective_thrust_n - thrust) > 1.0e-12)
        output->saturated = 1;
    output->desired_acceleration_enu_mps2 = desired_acceleration_enu_mps2;
    return 0;
}
static const double MOSIM_LEARNING_OBSERVATION_SCALE[12] = {
    2.5,
    2.5,
    2.5,
    3,
    3,
    3,
    3,
    3,
    3,
    3,
    3,
    3
};

static const double MOSIM_NEURAL_W1[144] = {
    -0.071548174567216627,
    0.12356972959904969,
    -0.043824659897999545,
    -0.10918836732008147,
    -0.1092614620377011,
    0.0032903828712236255,
    -0.03981519705965425,
    0.067962521254047739,
    -0.026312301295198542,
    0.27394120510678022,
    0.037966179297400038,
    0.13591580530036274,
    -0.08717792948468088,
    -0.0058641746727977201,
    0.1793721966851991,
    -0.1786530248040861,
    0.26770706454018861,
    0.031509511574785806,
    0.016872348058331588,
    0.0092291482167393725,
    -0.042030628093007144,
    0.15609459138022994,
    -0.17509439189571843,
    -0.07871938902221412,
    0.16406868545788028,
    0.00050714667201514317,
    0.17193312550977471,
    0.076471972189552859,
    -0.079669444782158899,
    0.10583432075442861,
    0.006293591315164453,
    0.21560800172336897,
    0.079407759626349717,
    0.04265480308096798,
    0.2913568722474581,
    0.072602922390428357,
    0.018828397364877104,
    -0.096501906660918485,
    -0.17213839750223131,
    0.15179792655316382,
    0.033059681127129495,
    0.030494101766125156,
    -0.029273950808636595,
    0.12683386566301183,
    0.00022710035256710067,
    -0.037488473843946192,
    0.098802217744249576,
    0.2722887732700372,
    0.086260547762467013,
    0.0062148451672853046,
    0.04436788005155614,
    -0.003235414179569547,
    -0.023013579989531956,
    -0.049636593110528163,
    -0.056564612018055169,
    0.10818031527341057,
    -0.016385534767086131,
    0.071379082473875144,
    -0.12796250202763568,
    0.016264145379609914,
    0.015233703733030454,
    0.077933976208957395,
    -0.076980915908758232,
    -0.0045202138878804084,
    0.067209129366946813,
    0.02679779272778084,
    -0.16189485614947108,
    0.11901252385995388,
    0.0074342672301247253,
    -0.002550171960931115,
    -0.022134439328401319,
    -0.1422161221666908,
    -0.0080355470897885365,
    0.063129498732371905,
    -0.029491570877817889,
    0.13112568394519936,
    0.035994972352220135,
    -0.10302691295197552,
    -0.15996018924182837,
    0.10965459788788742,
    -0.047976284609349169,
    -0.2573437501485481,
    -0.061365749501970671,
    0.066646938880801601,
    0.19645421527000786,
    -0.11791198606494911,
    -0.1495505993366292,
    0.061452857147826945,
    -0.20239759202626997,
    0.052637488297970526,
    -0.050419389385599547,
    0.017217647297057569,
    -0.062805899872396362,
    -0.14441019341083991,
    0.12130868241602585,
    0.071640812470842224,
    -0.0044173399689954613,
    -0.12488398833059658,
    -0.036673825468532213,
    -0.018289126108131982,
    0.0077100008881022686,
    -0.20996475378950835,
    0.027400506496228355,
    -0.018582328154044418,
    0.016374381743405646,
    0.020798400586623526,
    0.021995957343082774,
    0.021407670968751149,
    0.033381190249766511,
    0.040486231834389409,
    0.33008738688882788,
    0.065777988162565526,
    0.26373999904634782,
    -0.24755274659952362,
    0.088221808282199957,
    -0.05202910110120431,
    0.056734169587462822,
    -0.1448946511004276,
    -0.014999562918146803,
    0.12371548930173835,
    0.0016659568501081533,
    -0.1142087465142272,
    -0.047008228559228621,
    0.1502798364217458,
    -0.036901707938845459,
    0.072657515181361224,
    0.0052003543225835535,
    -0.45105022057491662,
    0.025239165533560756,
    -0.26537662080395896,
    0.42006774553584947,
    0.16268383437435291,
    0.10649937791165585,
    0.058811621708246387,
    0.059617692819426332,
    -0.09449083966814073,
    0.064342702569188628,
    0.24148916169112064,
    0.51582844439146758,
    -0.031072087167889263,
    -1.3236259953879277,
    0.10376733723210693,
    0.086801246858916117,
    -0.16679321863894231
};

static const double MOSIM_NEURAL_B1[12] = {
    0.27252632360316204,
    -0.31179852933995356,
    0.021587485996673286,
    0.59549588139582776,
    -0.10955925354988232,
    -0.25025639859960602,
    -0.0023987945326166731,
    -0.0085498001508730655,
    0.0085888058324592523,
    0.22639665859679864,
    0.051514790392397584,
    0.13657260861530013
};

static const double MOSIM_NEURAL_W2[36] = {
    -0.43978857721574149,
    0.27390064935580305,
    0.3171640404486088,
    -0.10101537344426531,
    -0.24047093989627993,
    0.34334766094600916,
    -0.35756859710141503,
    0.3321277100739034,
    0.10540131090115985,
    -0.45025222823645955,
    -0.20674528922015015,
    -0.02482934179649578,
    -0.20946822014897154,
    0.34418033726795499,
    0.19539376739368058,
    0.18069215966646623,
    0.049039283159572365,
    0.28958463220545194,
    0.068088592693085981,
    -0.14654992724435439,
    -0.22971580179865791,
    0.33992932354708316,
    0.16444600084358263,
    0.20540647157762756,
    0.0097948755428189874,
    -0.04452040130358418,
    0.43424476447691018,
    0.29368404603431369,
    0.18137065427655247,
    0.016205887111010307,
    0.074162320789750838,
    -0.40411078033546399,
    0.34338853801038477,
    0.22888259836640382,
    0.21417690049450624,
    -0.15543934852177763
};

static const double MOSIM_NEURAL_B2[3] = {
    0.25467724605436165,
    -0.03978910289013713,
    0.12278233316638093
};

static const double MOSIM_RL_W1[192] = {
    -0.11133357882499695,
    0.1554446816444397,
    -0.44469910860061646,
    0.13438564538955688,
    -0.39296072721481323,
    -0.23311340808868408,
    0.79780244827270508,
    0.030108189210295677,
    -0.017848508432507515,
    -0.0022831761743873358,
    -0.20617368817329407,
    0.61192256212234497,
    0.072449050843715668,
    0.083321399986743927,
    0.238974928855896,
    -0.56904751062393188,
    0.086142800748348236,
    -0.66204357147216797,
    0.39014697074890137,
    -0.186968132853508,
    0.20332317054271698,
    -0.22512054443359375,
    -0.061367496848106384,
    0.047898810356855392,
    -0.18065726757049561,
    -0.20530533790588379,
    -0.89059996604919434,
    0.1105668917298317,
    -0.29294130206108093,
    -0.47593003511428833,
    0.02774493396282196,
    -0.50066590309143066,
    -0.31409797072410583,
    -0.038127519190311432,
    -0.18702542781829834,
    0.67000925540924072,
    0.802482008934021,
    0.51635527610778809,
    -0.09049823135137558,
    -0.31696897745132446,
    -0.18751490116119385,
    0.51458185911178589,
    -0.062901519238948822,
    0.54222506284713745,
    0.17992274463176727,
    -0.31409439444541931,
    -0.19295775890350342,
    -0.17920079827308655,
    0.29829764366149902,
    0.15407101809978485,
    -0.057088427245616913,
    -0.38828915357589722,
    0.43507832288742065,
    -0.66252219676971436,
    -0.1933993399143219,
    0.069799050688743591,
    0.074297495186328888,
    0.51466244459152222,
    0.62489831447601318,
    0.12644511461257935,
    -0.18012075126171112,
    -0.31646734476089478,
    0.25226172804832458,
    -0.43529626727104187,
    0.058141954243183136,
    0.010185739956796169,
    0.0026782520581036806,
    -0.37238532304763794,
    -0.28783124685287476,
    0.096167325973510742,
    -0.51787126064300537,
    -0.18420931696891785,
    0.0055062440223991871,
    -0.18411596119403839,
    -0.090221486985683441,
    0.91268527507781982,
    0.24759013950824738,
    -0.41806524991989136,
    0.41623371839523315,
    0.43638473749160767,
    -0.12645207345485687,
    0.12426756322383881,
    0.47942227125167847,
    -0.57688719034194946,
    0.051816251128911972,
    0.0023469214793294668,
    0.58050328493118286,
    -0.84572547674179077,
    0.48104861378669739,
    0.087086878716945648,
    0.014968491159379482,
    -0.16111719608306885,
    0.2140830010175705,
    -0.20074655115604401,
    -0.27277547121047974,
    0.068240232765674591,
    0.6722913384437561,
    0.17531247437000275,
    0.19804184138774872,
    -0.19568124413490295,
    -0.15990878641605377,
    0.5815388560295105,
    -0.21397785842418671,
    0.35387015342712402,
    0.41716983914375305,
    0.13236492872238159,
    -0.086606673896312714,
    0.13156412541866302,
    0.42196378111839294,
    0.16288481652736664,
    -0.38877385854721069,
    -0.57699048519134521,
    -0.12396685779094696,
    0.017331751063466072,
    0.11854701489210129,
    -0.34914946556091309,
    -0.34968313574790955,
    -0.17983426153659821,
    -0.0022336512338370085,
    0.05733925849199295,
    -0.94454491138458252,
    0.38543659448623657,
    0.067068338394165039,
    0.16744016110897064,
    0.15705491602420807,
    0.045391302555799484,
    -0.76682370901107788,
    0.049551095813512802,
    -0.027178442105650902,
    0.59721142053604126,
    -0.54456591606140137,
    -0.55972188711166382,
    0.27305677533149719,
    0.5199962854385376,
    0.11467507481575012,
    0.15618008375167847,
    -0.38500368595123291,
    -0.11429318785667419,
    -0.29808506369590759,
    -0.39315900206565857,
    -0.1155785396695137,
    -0.43351283669471741,
    0.20631551742553711,
    -0.041026905179023743,
    0.54193568229675293,
    -0.49219012260437012,
    0.054183393716812134,
    0.20677363872528076,
    -0.15083210170269012,
    0.19225199520587921,
    0.29110363125801086,
    -0.22333009541034698,
    -0.50904321670532227,
    -0.14516516029834747,
    0.42146900296211243,
    -0.3564612865447998,
    0.59139782190322876,
    -0.33598321676254272,
    0.42937391996383667,
    -0.092769913375377655,
    -0.18968725204467773,
    0.27382871508598328,
    0.20443709194660187,
    0.15064099431037903,
    0.086554557085037231,
    -0.41980153322219849,
    0.10383403301239014,
    0.52567511796951294,
    0.16543485224246979,
    0.38740536570549011,
    -0.41278862953186035,
    -0.24319203197956085,
    0.85520142316818237,
    -0.21396073698997498,
    0.17291004955768585,
    0.3649865984916687,
    -0.23995994031429291,
    -0.36005204916000366,
    0.24590057134628296,
    -0.04772331565618515,
    -0.35036534070968628,
    0.58861303329467773,
    0.31202441453933716,
    0.4240601658821106,
    0.10129682719707489,
    0.76901108026504517,
    0.1211116835474968,
    0.079363852739334106,
    -0.49856755137443542,
    -0.2871517539024353,
    0.32268163561820984,
    0.18168672919273376
};

static const double MOSIM_RL_B1[16] = {
    -0.076977439224720001,
    -0.034640703350305557,
    -0.099735729396343231,
    0.11652754247188568,
    -0.036704357713460922,
    0.087404079735279083,
    0.087563052773475647,
    0.025452600792050362,
    -0.1059667095541954,
    0.046892642974853516,
    -0.072150491178035736,
    0.025356335565447807,
    0.081691227853298187,
    -0.086907893419265747,
    0.064164452254772186,
    -0.073012903332710266
};

static const double MOSIM_RL_W2[256] = {
    0.2627139687538147,
    -0.2533208429813385,
    0.18249444663524628,
    -0.12440905719995499,
    -0.6087411642074585,
    0.18983812630176544,
    -0.62573802471160889,
    0.48548761010169983,
    0.29851683974266052,
    -0.20477157831192017,
    0.20286338031291962,
    -0.75588661432266235,
    -0.061577983200550079,
    0.2361181229352951,
    0.26576632261276245,
    0.016775108873844147,
    0.13167214393615723,
    0.21825127303600311,
    -0.75195866823196411,
    0.39465978741645813,
    0.59982436895370483,
    0.18040120601654053,
    -0.60308545827865601,
    0.011448550038039684,
    0.1117696687579155,
    0.26580327749252319,
    0.44982624053955078,
    -0.049171138554811478,
    -0.44434809684753418,
    0.08591044694185257,
    0.15069220960140228,
    -0.019411986693739891,
    0.12083353847265244,
    0.2141525000333786,
    0.28079313039779663,
    -0.61953413486480713,
    0.35166221857070923,
    -0.0092345671728253365,
    0.50160861015319824,
    0.18150199949741364,
    0.35444185137748718,
    0.17681685090065002,
    0.10560248047113419,
    -0.097025223076343536,
    -0.68637526035308838,
    0.55801302194595337,
    0.33063092827796936,
    0.27071917057037354,
    0.3302747905254364,
    -0.46772834658622742,
    0.7881426215171814,
    -0.16077408194541931,
    0.42967048287391663,
    0.007695348933339119,
    -0.54245865345001221,
    -0.33709284663200378,
    0.25717782974243164,
    0.25668415427207947,
    0.20215602219104767,
    0.40149214863777161,
    -0.012967498973011971,
    -0.42370274662971497,
    -0.39702519774436951,
    -0.017533576115965843,
    0.46764922142028809,
    -0.099849149584770203,
    0.1266520768404007,
    0.53247815370559692,
    0.54350060224533081,
    -0.30852577090263367,
    0.0092184999957680702,
    0.22289247810840607,
    0.23503048717975616,
    -0.80821925401687622,
    -0.18643373250961304,
    0.24293249845504761,
    0.36316487193107605,
    0.35157468914985657,
    0.1494889110326767,
    0.15465655922889709,
    -0.012890934944152832,
    0.65671408176422119,
    0.59839564561843872,
    0.27748361229896545,
    0.1020478755235672,
    -0.53461998701095581,
    -0.41729509830474854,
    0.12005100399255753,
    -0.71619588136672974,
    0.1759960949420929,
    -0.10689722746610641,
    -0.17183443903923035,
    -0.099642463028430939,
    0.082345984876155853,
    -0.26186609268188477,
    0.3107876181602478,
    0.010930784046649933,
    -0.75918161869049072,
    -0.24858753383159637,
    -0.31263619661331177,
    0.32217532396316528,
    -0.39723432064056396,
    0.096250787377357483,
    -0.35487234592437744,
    -0.57283824682235718,
    -0.021702365949749947,
    0.23693518340587616,
    -0.54526430368423462,
    0.14714282751083374,
    0.22565856575965881,
    -0.099789127707481384,
    0.31245598196983337,
    0.33366093039512634,
    0.45213690400123596,
    0.047875501215457916,
    0.10201030224561691,
    -0.13896040618419647,
    0.50292885303497314,
    0.24095915257930756,
    -0.54392325878143311,
    0.076331712305545807,
    -0.3825860321521759,
    0.43410474061965942,
    -0.27623307704925537,
    0.062539488077163696,
    -0.25899824500083923,
    -0.31561669707298279,
    0.65033233165740967,
    -0.63180547952651978,
    0.34621959924697876,
    0.0072819571942090988,
    -0.51868903636932373,
    0.62431162595748901,
    0.35772630572319031,
    -0.19247467815876007,
    0.36424562335014343,
    0.18145535886287689,
    -0.16617509722709656,
    0.035082165151834488,
    -0.32931500673294067,
    0.64689278602600098,
    -0.12038550525903702,
    0.059601437300443649,
    0.012879368849098682,
    0.34014984965324402,
    -0.079793922603130341,
    0.33880022168159485,
    0.21577951312065125,
    0.16746625304222107,
    0.75191545486450195,
    0.17735309898853302,
    0.21260425448417664,
    -0.70044934749603271,
    0.16943097114562988,
    0.3432350754737854,
    0.24709859490394592,
    0.26745331287384033,
    0.47755548357963562,
    -0.11076492071151733,
    -0.4440251886844635,
    0.23036962747573853,
    -0.028836475685238838,
    -0.40754356980323792,
    -0.39866864681243896,
    0.12140452861785889,
    0.23730646073818207,
    -0.10949547588825226,
    0.51910704374313354,
    -0.15069106221199036,
    -0.41649121046066284,
    -0.42391335964202881,
    0.037944022566080093,
    -0.45559647679328918,
    -0.066392496228218079,
    -0.89647722244262695,
    -0.029946692287921906,
    0.73313271999359131,
    0.37512186169624329,
    -0.070240050554275513,
    -0.062944665551185608,
    0.057932857424020767,
    -0.54610723257064819,
    0.31728702783584595,
    0.10063004493713379,
    0.27533599734306335,
    0.3975241482257843,
    0.24353387951850891,
    -0.24016569554805756,
    0.53650230169296265,
    -0.074731975793838501,
    -0.39182209968566895,
    -0.54868018627166748,
    0.14620053768157959,
    -0.24939489364624023,
    -0.18990711867809296,
    0.1211918443441391,
    -0.10641836374998093,
    0.14578992128372192,
    0.077377274632453918,
    0.57581603527069092,
    0.073370181024074554,
    0.66587173938751221,
    -0.12617245316505432,
    0.24739506840705872,
    0.35372069478034973,
    -0.06296200305223465,
    -0.058937273919582367,
    0.94192987680435181,
    -0.52823293209075928,
    -0.3010580837726593,
    0.18914881348609924,
    0.61751759052276611,
    0.19493207335472107,
    0.016258548945188522,
    0.50289517641067505,
    0.55206042528152466,
    0.24344083666801453,
    -0.070955410599708557,
    0.36816820502281189,
    -0.45078849792480469,
    -0.40847307443618774,
    -0.31836119294166565,
    -0.31480687856674194,
    -0.08183828741312027,
    -0.30914655327796936,
    0.057911515235900879,
    -0.064541146159172058,
    -0.24706897139549255,
    -0.3517279326915741,
    -0.42128723859786987,
    -0.13106468319892883,
    0.18435877561569214,
    0.0019447918748483062,
    -0.27136656641960144,
    0.90644001960754395,
    0.66661953926086426,
    0.1070692390203476,
    0.27449575066566467,
    -0.26508811116218567,
    0.11408209800720215,
    -0.42302131652832031,
    -0.044564828276634216,
    -0.032899346202611923,
    0.27420815825462341,
    -0.048643112182617188,
    0.16136051714420319,
    -0.14051644504070282,
    -0.33915901184082031,
    0.50913023948669434,
    0.23448731005191803,
    -0.27768614888191223,
    -0.18813280761241913,
    0.10366066545248032,
    0.87589401006698608,
    -0.66728103160858154,
    0.032203104346990585
};

static const double MOSIM_RL_B2[16] = {
    0.080701775848865509,
    -0.073274910449981689,
    0.088010087609291077,
    -0.0063655665144324303,
    -0.012414573691785336,
    -0.067838378250598907,
    -0.049675226211547852,
    -0.1003008708357811,
    -0.11640025675296783,
    0.085122428834438324,
    0.08285234123468399,
    0.067019075155258179,
    0.089479997754096985,
    -0.081481128931045532,
    -0.035435959696769714,
    0.065050065517425537
};

static const double MOSIM_RL_W3[48] = {
    -0.08075404167175293,
    -0.014006099663674831,
    -0.1180856004357338,
    -0.068461142480373383,
    -0.0010913601145148277,
    0.0084875021129846573,
    -0.041764024645090103,
    -0.031379226595163345,
    -0.11507025361061096,
    -0.028070226311683655,
    0.061616022139787674,
    -0.047505848109722137,
    -0.041860755532979965,
    0.070026904344558716,
    -0.023007471114397049,
    0.021488988772034645,
    0.062676846981048584,
    0.061750814318656921,
    -0.021868718788027763,
    -0.031149115413427353,
    0.03482794389128685,
    -0.016748327761888504,
    0.054070785641670227,
    0.078585162758827209,
    -0.0073808166198432446,
    0.011434178799390793,
    0.12757313251495361,
    0.038868684321641922,
    -0.015980293974280357,
    -0.056765072047710419,
    0.01431991346180439,
    -0.012509474530816078,
    -0.041212629526853561,
    -0.038104560226202011,
    -0.0089921429753303528,
    -0.1224711611866951,
    -0.054388374090194702,
    -0.031491577625274658,
    -0.10510733723640442,
    -0.015699878334999084,
    0.022406380623579025,
    0.047318894416093826,
    -0.0062820063903927803,
    -0.05730322003364563,
    0.057116381824016571,
    0.11647522449493408,
    -0.0032429839484393597,
    0.0018790973117575049
};

static const double MOSIM_RL_B3[3] = {
    0.049809448421001434,
    -0.061951525509357452,
    -0.10416445136070251
};
enum MosimLearningStatus {
    MOSIM_LEARNING_STATUS_OK = 0,
    MOSIM_LEARNING_STATUS_DISABLED = 1,
    MOSIM_LEARNING_STATUS_FALLBACK = 2
};

typedef struct {
    double values[MOSIM_LEARNING_OBSERVATION_SIZE];
    int enable;
} MosimLearningInput;

typedef struct {
    double values[MOSIM_LEARNING_ACTION_SIZE];
    int status_code;
    int fallback_active;
} MosimLearningOutput;

void mosim_learning_zero_output(MosimLearningOutput *output, int status_code);
int mosim_neural_residual_step(const MosimLearningInput *input, MosimLearningOutput *output);
int mosim_rl_gain_scheduler_step(const MosimLearningInput *input, MosimLearningOutput *output);
const char *mosim_learning_artifact_sha256(void);
#include <math.h>
#include <stddef.h>

#define MOSIM_NEURAL_RESIDUAL_LIMIT 0.6
#define MOSIM_RL_SCHEDULE_LIMIT 0.25

static double learning_clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

void mosim_learning_zero_output(MosimLearningOutput *output, int status_code)
{
    size_t index;
    if (output == NULL) return;
    for (index = 0; index < MOSIM_LEARNING_ACTION_SIZE; ++index) output->values[index] = 0.0;
    output->status_code = status_code;
    output->fallback_active = status_code != MOSIM_LEARNING_STATUS_OK;
}

static int learning_valid_input(const MosimLearningInput *input)
{
    size_t index;
    if (input == NULL) return 0;
    for (index = 0; index < MOSIM_LEARNING_OBSERVATION_SIZE; ++index) {
        if (!isfinite(input->values[index])) return 0;
    }
    return 1;
}

static int prepare_input(const MosimLearningInput *input, double normalized[MOSIM_LEARNING_OBSERVATION_SIZE])
{
    size_t index;
    if (!learning_valid_input(input)) return 0;
    for (index = 0; index < MOSIM_LEARNING_OBSERVATION_SIZE; ++index) {
        normalized[index] = learning_clamp_value(
            input->values[index] / MOSIM_LEARNING_OBSERVATION_SCALE[index], -1.0, 1.0);
    }
    return 1;
}

int mosim_neural_residual_step(const MosimLearningInput *input, MosimLearningOutput *output)
{
    double normalized[MOSIM_LEARNING_OBSERVATION_SIZE];
    double hidden[MOSIM_NEURAL_HIDDEN_SIZE];
    size_t input_index;
    size_t hidden_index;
    size_t output_index;
    if (output == NULL) return -1;
    mosim_learning_zero_output(output, MOSIM_LEARNING_STATUS_FALLBACK);
    if (!learning_valid_input(input)) return -1;
    if (!input->enable) {
        mosim_learning_zero_output(output, MOSIM_LEARNING_STATUS_DISABLED);
        return 0;
    }
    if (!prepare_input(input, normalized)) return -1;
    for (hidden_index = 0; hidden_index < MOSIM_NEURAL_HIDDEN_SIZE; ++hidden_index) {
        double value = MOSIM_NEURAL_B1[hidden_index];
        for (input_index = 0; input_index < MOSIM_LEARNING_OBSERVATION_SIZE; ++input_index) {
            value += normalized[input_index] *
                     MOSIM_NEURAL_W1[input_index * MOSIM_NEURAL_HIDDEN_SIZE + hidden_index];
        }
        hidden[hidden_index] = tanh(value);
    }
    for (output_index = 0; output_index < MOSIM_LEARNING_ACTION_SIZE; ++output_index) {
        double value = MOSIM_NEURAL_B2[output_index];
        for (hidden_index = 0; hidden_index < MOSIM_NEURAL_HIDDEN_SIZE; ++hidden_index) {
            value += hidden[hidden_index] *
                     MOSIM_NEURAL_W2[hidden_index * MOSIM_LEARNING_ACTION_SIZE + output_index];
        }
        if (!isfinite(value)) return -1;
        output->values[output_index] = learning_clamp_value(
            value, -MOSIM_NEURAL_RESIDUAL_LIMIT, MOSIM_NEURAL_RESIDUAL_LIMIT);
    }
    output->status_code = MOSIM_LEARNING_STATUS_OK;
    output->fallback_active = 0;
    return 0;
}

int mosim_rl_gain_scheduler_step(const MosimLearningInput *input, MosimLearningOutput *output)
{
    double normalized[MOSIM_LEARNING_OBSERVATION_SIZE];
    double hidden1[MOSIM_RL_HIDDEN_SIZE];
    double hidden2[MOSIM_RL_HIDDEN_SIZE];
    size_t input_index;
    size_t hidden_index;
    size_t output_index;
    if (output == NULL) return -1;
    mosim_learning_zero_output(output, MOSIM_LEARNING_STATUS_FALLBACK);
    if (!learning_valid_input(input)) return -1;
    if (!input->enable) {
        mosim_learning_zero_output(output, MOSIM_LEARNING_STATUS_DISABLED);
        return 0;
    }
    if (!prepare_input(input, normalized)) return -1;
    for (hidden_index = 0; hidden_index < MOSIM_RL_HIDDEN_SIZE; ++hidden_index) {
        double value = MOSIM_RL_B1[hidden_index];
        for (input_index = 0; input_index < MOSIM_LEARNING_OBSERVATION_SIZE; ++input_index) {
            value += normalized[input_index] *
                     MOSIM_RL_W1[input_index * MOSIM_RL_HIDDEN_SIZE + hidden_index];
        }
        hidden1[hidden_index] = tanh(value);
    }
    for (hidden_index = 0; hidden_index < MOSIM_RL_HIDDEN_SIZE; ++hidden_index) {
        double value = MOSIM_RL_B2[hidden_index];
        for (input_index = 0; input_index < MOSIM_RL_HIDDEN_SIZE; ++input_index) {
            value += hidden1[input_index] *
                     MOSIM_RL_W2[input_index * MOSIM_RL_HIDDEN_SIZE + hidden_index];
        }
        hidden2[hidden_index] = tanh(value);
    }
    for (output_index = 0; output_index < MOSIM_LEARNING_ACTION_SIZE; ++output_index) {
        double value = MOSIM_RL_B3[output_index];
        for (hidden_index = 0; hidden_index < MOSIM_RL_HIDDEN_SIZE; ++hidden_index) {
            value += hidden2[hidden_index] *
                     MOSIM_RL_W3[hidden_index * MOSIM_LEARNING_ACTION_SIZE + output_index];
        }
        if (!isfinite(value)) return -1;
        output->values[output_index] = learning_clamp_value(
            value, 0.0, MOSIM_RL_SCHEDULE_LIMIT);
    }
    output->status_code = MOSIM_LEARNING_STATUS_OK;
    output->fallback_active = 0;
    return 0;
}

const char *mosim_learning_artifact_sha256(void)
{
    return MOSIM_LEARNING_ARTIFACT_SHA256;
}
enum MosimLearningControllerMode {
    MOSIM_LEARNING_NEURAL_RESIDUAL = 1,
    MOSIM_LEARNING_RL_GAIN_SCHEDULER = 2
};

typedef struct {
    int mode;
    double dt;
    MosimPidVec3 position_enu_m;
    MosimPidVec3 velocity_enu_mps;
    MosimPidQuat attitude_enu_flu_wxyz;
    MosimPidVec3 angular_velocity_flu_radps;
    MosimPidVec3 reference_position_enu_m;
    MosimPidVec3 reference_velocity_enu_mps;
    MosimPidVec3 reference_acceleration_enu_mps2;
    double reference_yaw_enu_rad;
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
    int reset;
    int enable;
    int learning_enable;
} MosimLearningAttitudeThrustInput;

typedef struct {
    MosimPidAttitudeThrustOutput control;
    MosimLearningOutput learning;
    double normalized_thrust;
    int mode;
    int fallback_active;
    int status_code;
} MosimLearningAttitudeThrustOutput;

typedef struct {
    MosimPidAttitudeThrustState controller;
    int previous_mode;
} MosimLearningAttitudeThrustState;

void mosim_learning_attitude_thrust_reset(MosimLearningAttitudeThrustState *state);
int mosim_learning_attitude_thrust_step(
    MosimLearningAttitudeThrustState *state,
    const MosimLearningAttitudeThrustInput *input,
    MosimLearningAttitudeThrustOutput *output);
#include <math.h>
#include <stddef.h>
#include <string.h>

static double learning_component(MosimPidVec3 value, size_t axis)
{
    if (axis == 0) return value.x;
    if (axis == 1) return value.y;
    return value.z;
}

static void learning_set_component(MosimPidVec3 *value, size_t axis, double item)
{
    if (axis == 0) value->x = item;
    else if (axis == 1) value->y = item;
    else value->z = item;
}

void mosim_learning_attitude_thrust_reset(MosimLearningAttitudeThrustState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

static void build_observation(const MosimLearningAttitudeThrustInput *input,
                              MosimLearningInput *learning)
{
    size_t axis;
    memset(learning, 0, sizeof(*learning));
    for (axis = 0; axis < 3; ++axis) {
        learning->values[axis] = learning_component(input->reference_position_enu_m, axis) -
                                 learning_component(input->position_enu_m, axis);
        learning->values[3 + axis] = learning_component(input->reference_velocity_enu_mps, axis) -
                                     learning_component(input->velocity_enu_mps, axis);
        learning->values[6 + axis] = learning_component(input->reference_acceleration_enu_mps2, axis);
        learning->values[9 + axis] = learning_component(input->velocity_enu_mps, axis);
    }
    learning->enable = input->enable && input->learning_enable;
}

int mosim_learning_attitude_thrust_step(
    MosimLearningAttitudeThrustState *state,
    const MosimLearningAttitudeThrustInput *input,
    MosimLearningAttitudeThrustOutput *output)
{
    MosimLearningInput learning_input;
    MosimPidAttitudeThrustParams params;
    MosimPidAttitudeThrustInput controller_input;
    int inference_result;
    int controller_id = MOSIM_PID_CASCADE;
    size_t axis;
    if (state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->mode = input->mode;
    if (input->mode != MOSIM_LEARNING_NEURAL_RESIDUAL &&
        input->mode != MOSIM_LEARNING_RL_GAIN_SCHEDULER) {
        output->status_code = -1;
        output->fallback_active = 1;
        return -1;
    }
    if (input->reset || state->previous_mode != input->mode) {
        mosim_learning_attitude_thrust_reset(state);
        state->previous_mode = input->mode;
    }
    build_observation(input, &learning_input);
    if (input->mode == MOSIM_LEARNING_NEURAL_RESIDUAL) {
        inference_result = mosim_neural_residual_step(&learning_input, &output->learning);
    } else {
        inference_result = mosim_rl_gain_scheduler_step(&learning_input, &output->learning);
        controller_id = MOSIM_PID_GAIN_SCHEDULED;
    }
    output->fallback_active = inference_result != 0 || output->learning.fallback_active;
    if (output->fallback_active) controller_id = MOSIM_PID_CASCADE;

    memset(&controller_input, 0, sizeof(controller_input));
    controller_input.algorithm_id = controller_id;
    controller_input.dt = input->dt;
    controller_input.position_enu_m = input->position_enu_m;
    controller_input.velocity_enu_mps = input->velocity_enu_mps;
    controller_input.attitude_enu_flu_wxyz = input->attitude_enu_flu_wxyz;
    controller_input.angular_velocity_flu_radps = input->angular_velocity_flu_radps;
    controller_input.reference_position_enu_m = input->reference_position_enu_m;
    controller_input.reference_velocity_enu_mps = input->reference_velocity_enu_mps;
    controller_input.reference_acceleration_enu_mps2 = input->reference_acceleration_enu_mps2;
    controller_input.reference_yaw_enu_rad = input->reference_yaw_enu_rad;
    controller_input.enable = input->enable;
    controller_input.reset = input->reset;
    if (input->mode == MOSIM_LEARNING_RL_GAIN_SCHEDULER && !output->fallback_active) {
        for (axis = 0; axis < 3; ++axis) {
            learning_set_component(&controller_input.schedule, axis, output->learning.values[axis]);
        }
    }
    mosim_pid_attitude_thrust_default_params(controller_id, &params);
    params.mass_kg = input->mass_kg;
    params.gravity_mps2 = input->gravity_mps2;
    params.max_tilt_rad = input->max_tilt_rad;
    params.min_collective_thrust_n = input->min_collective_thrust_n;
    params.max_collective_thrust_n = input->max_collective_thrust_n;
    if (!isfinite(input->hover_percentage) || input->hover_percentage <= 0.0 ||
        input->hover_percentage > 1.0) {
        output->status_code = -1;
        output->fallback_active = 1;
        return -1;
    }
    if (controller_id == MOSIM_PID_GAIN_SCHEDULED) {
        for (axis = 0; axis < 3; ++axis) params.velocity[axis].schedule_gain = 2.0;
    }
    if (mosim_pid_attitude_thrust_step(
            &params, &state->controller, &controller_input, &output->control) != 0) {
        output->status_code = -1;
        output->fallback_active = 1;
        return -1;
    }
    if (input->mode == MOSIM_LEARNING_NEURAL_RESIDUAL && !output->fallback_active && input->enable) {
        MosimPidVec3 acceleration = output->control.desired_acceleration_enu_mps2;
        for (axis = 0; axis < 3; ++axis) {
            learning_set_component(&acceleration, axis,
                          learning_component(acceleration, axis) + output->learning.values[axis]);
        }
        if (mosim_pid_attitude_thrust_apply_acceleration(
                &params, input->reference_yaw_enu_rad, acceleration, &output->control) != 0) {
            output->status_code = -1;
            output->fallback_active = 1;
            return -1;
        }
    }
    output->normalized_thrust = output->control.desired_collective_thrust_n /
        (params.mass_kg * params.gravity_mps2 / input->hover_percentage);
    if (!isfinite(output->normalized_thrust)) {
        output->status_code = -1;
        output->fallback_active = 1;
        return -1;
    }
    if (output->normalized_thrust < 0.0) output->normalized_thrust = 0.0;
    if (output->normalized_thrust > 1.0) output->normalized_thrust = 1.0;
    output->status_code = 0;
    return 0;
}
void MosimLearningAttitudeThrustStepScalar(
    double mode,
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
    double hover_percentage,
    double max_tilt_rad,
    double min_collective_thrust_n,
    double max_collective_thrust_n,
    double enable,
    double learning_enable,
    double reset,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *desired_collective_thrust_n,
    double *normalized_thrust,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *learning_action_x,
    double *learning_action_y,
    double *learning_action_z,
    double *scheduled_gain_x,
    double *scheduled_gain_y,
    double *scheduled_gain_z,
    double *fallback_active,
    double *status_code,
    double *mode_out)
{
    static MosimLearningAttitudeThrustState states[3];
    MosimLearningAttitudeThrustInput input;
    MosimLearningAttitudeThrustOutput output;
    int id = (int)mode;
    int result;
    memset(&input, 0, sizeof(input));
    input.mode = id; input.dt = dt;
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
    input.mass_kg = mass_kg; input.gravity_mps2 = gravity_mps2;
    input.hover_percentage = hover_percentage; input.max_tilt_rad = max_tilt_rad;
    input.min_collective_thrust_n = min_collective_thrust_n;
    input.max_collective_thrust_n = max_collective_thrust_n;
    input.enable = enable != 0.0; input.learning_enable = learning_enable != 0.0;
    input.reset = reset != 0.0;
    if (id < 1 || id > 2) id = 0;
    result = mosim_learning_attitude_thrust_step(&states[id], &input, &output);
    if (result != 0) {
        memset(&output, 0, sizeof(output));
        output.control.desired_attitude_enu_flu_wxyz.w = 1.0;
        output.fallback_active = 1; output.status_code = result; output.mode = id;
    }
    *desired_attitude_w = output.control.desired_attitude_enu_flu_wxyz.w;
    *desired_attitude_x = output.control.desired_attitude_enu_flu_wxyz.x;
    *desired_attitude_y = output.control.desired_attitude_enu_flu_wxyz.y;
    *desired_attitude_z = output.control.desired_attitude_enu_flu_wxyz.z;
    *desired_collective_thrust_n = output.control.desired_collective_thrust_n;
    *normalized_thrust = output.normalized_thrust;
    *desired_acceleration_x = output.control.desired_acceleration_enu_mps2.x;
    *desired_acceleration_y = output.control.desired_acceleration_enu_mps2.y;
    *desired_acceleration_z = output.control.desired_acceleration_enu_mps2.z;
    *learning_action_x = output.learning.values[0];
    *learning_action_y = output.learning.values[1];
    *learning_action_z = output.learning.values[2];
    *scheduled_gain_x = output.control.scheduled_gain.x;
    *scheduled_gain_y = output.control.scheduled_gain.y;
    *scheduled_gain_z = output.control.scheduled_gain.z;
    *fallback_active = (double)output.fallback_active;
    *status_code = (double)output.status_code;
    *mode_out = (double)output.mode;
}
");
    end func_CFunction;

    SysplorerEmbeddedCoder.Port.Inport mode
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
    SysplorerEmbeddedCoder.Port.Inport hover_percentage
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport max_tilt_rad
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport min_collective_thrust_n
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport max_collective_thrust_n
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport enable
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport learning_enable
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
    SysplorerEmbeddedCoder.Port.Outport normalized_thrust
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport learning_action_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport learning_action_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport learning_action_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport scheduled_gain_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport scheduled_gain_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport scheduled_gain_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport fallback_active
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport status_code
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport mode_out
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
  equation
    (desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, desired_collective_thrust_n, normalized_thrust, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, learning_action_x, learning_action_y, learning_action_z, scheduled_gain_x, scheduled_gain_y, scheduled_gain_z, fallback_active, status_code, mode_out) = func_CFunction(mode, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, attitude_w, attitude_x, attitude_y, attitude_z, angular_velocity_x, angular_velocity_y, angular_velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_yaw, mass_kg, gravity_mps2, hover_percentage, max_tilt_rad, min_collective_thrust_n, max_collective_thrust_n, enable, learning_enable, reset);
  end CFunction;

equation
  connect(mode_in, cFunction.mode) annotation(Line(points={{-492,396.00},{-80,396.00}},color={0,0,127}));
  connect(dt_in, cFunction.dt) annotation(Line(points={{-492,372.00},{-80,372.00}},color={0,0,127}));
  connect(position_x_in, cFunction.position_x) annotation(Line(points={{-492,348.00},{-80,348.00}},color={0,0,127}));
  connect(position_y_in, cFunction.position_y) annotation(Line(points={{-492,324.00},{-80,324.00}},color={0,0,127}));
  connect(position_z_in, cFunction.position_z) annotation(Line(points={{-492,300.00},{-80,300.00}},color={0,0,127}));
  connect(velocity_x_in, cFunction.velocity_x) annotation(Line(points={{-492,276.00},{-80,276.00}},color={0,0,127}));
  connect(velocity_y_in, cFunction.velocity_y) annotation(Line(points={{-492,252.00},{-80,252.00}},color={0,0,127}));
  connect(velocity_z_in, cFunction.velocity_z) annotation(Line(points={{-492,228.00},{-80,228.00}},color={0,0,127}));
  connect(attitude_w_in, cFunction.attitude_w) annotation(Line(points={{-492,204.00},{-80,204.00}},color={0,0,127}));
  connect(attitude_x_in, cFunction.attitude_x) annotation(Line(points={{-492,180.00},{-80,180.00}},color={0,0,127}));
  connect(attitude_y_in, cFunction.attitude_y) annotation(Line(points={{-492,156.00},{-80,156.00}},color={0,0,127}));
  connect(attitude_z_in, cFunction.attitude_z) annotation(Line(points={{-492,132.00},{-80,132.00}},color={0,0,127}));
  connect(angular_velocity_x_in, cFunction.angular_velocity_x) annotation(Line(points={{-492,108.00},{-80,108.00}},color={0,0,127}));
  connect(angular_velocity_y_in, cFunction.angular_velocity_y) annotation(Line(points={{-492,84.00},{-80,84.00}},color={0,0,127}));
  connect(angular_velocity_z_in, cFunction.angular_velocity_z) annotation(Line(points={{-492,60.00},{-80,60.00}},color={0,0,127}));
  connect(reference_position_x_in, cFunction.reference_position_x) annotation(Line(points={{-492,36.00},{-80,36.00}},color={0,0,127}));
  connect(reference_position_y_in, cFunction.reference_position_y) annotation(Line(points={{-492,12.00},{-80,12.00}},color={0,0,127}));
  connect(reference_position_z_in, cFunction.reference_position_z) annotation(Line(points={{-492,-12.00},{-80,-12.00}},color={0,0,127}));
  connect(reference_velocity_x_in, cFunction.reference_velocity_x) annotation(Line(points={{-492,-36.00},{-80,-36.00}},color={0,0,127}));
  connect(reference_velocity_y_in, cFunction.reference_velocity_y) annotation(Line(points={{-492,-60.00},{-80,-60.00}},color={0,0,127}));
  connect(reference_velocity_z_in, cFunction.reference_velocity_z) annotation(Line(points={{-492,-84.00},{-80,-84.00}},color={0,0,127}));
  connect(reference_acceleration_x_in, cFunction.reference_acceleration_x) annotation(Line(points={{-492,-108.00},{-80,-108.00}},color={0,0,127}));
  connect(reference_acceleration_y_in, cFunction.reference_acceleration_y) annotation(Line(points={{-492,-132.00},{-80,-132.00}},color={0,0,127}));
  connect(reference_acceleration_z_in, cFunction.reference_acceleration_z) annotation(Line(points={{-492,-156.00},{-80,-156.00}},color={0,0,127}));
  connect(reference_yaw_in, cFunction.reference_yaw) annotation(Line(points={{-492,-180.00},{-80,-180.00}},color={0,0,127}));
  connect(mass_kg_in, cFunction.mass_kg) annotation(Line(points={{-492,-204.00},{-80,-204.00}},color={0,0,127}));
  connect(gravity_mps2_in, cFunction.gravity_mps2) annotation(Line(points={{-492,-228.00},{-80,-228.00}},color={0,0,127}));
  connect(hover_percentage_in, cFunction.hover_percentage) annotation(Line(points={{-492,-252.00},{-80,-252.00}},color={0,0,127}));
  connect(max_tilt_rad_in, cFunction.max_tilt_rad) annotation(Line(points={{-492,-276.00},{-80,-276.00}},color={0,0,127}));
  connect(min_collective_thrust_n_in, cFunction.min_collective_thrust_n) annotation(Line(points={{-492,-300.00},{-80,-300.00}},color={0,0,127}));
  connect(max_collective_thrust_n_in, cFunction.max_collective_thrust_n) annotation(Line(points={{-492,-324.00},{-80,-324.00}},color={0,0,127}));
  connect(enable_in, cFunction.enable) annotation(Line(points={{-492,-348.00},{-80,-348.00}},color={0,0,127}));
  connect(learning_enable_in, cFunction.learning_enable) annotation(Line(points={{-492,-372.00},{-80,-372.00}},color={0,0,127}));
  connect(reset_in, cFunction.reset) annotation(Line(points={{-492,-396.00},{-80,-396.00}},color={0,0,127}));
  connect(cFunction.desired_attitude_w, desired_attitude_w_out) annotation(Line(points={{80,396.00},{492,396.00}},color={0,0,127}));
  connect(cFunction.desired_attitude_x, desired_attitude_x_out) annotation(Line(points={{80,349.41},{492,349.41}},color={0,0,127}));
  connect(cFunction.desired_attitude_y, desired_attitude_y_out) annotation(Line(points={{80,302.82},{492,302.82}},color={0,0,127}));
  connect(cFunction.desired_attitude_z, desired_attitude_z_out) annotation(Line(points={{80,256.24},{492,256.24}},color={0,0,127}));
  connect(cFunction.desired_collective_thrust_n, desired_collective_thrust_n_out) annotation(Line(points={{80,209.65},{492,209.65}},color={0,0,127}));
  connect(cFunction.normalized_thrust, normalized_thrust_out) annotation(Line(points={{80,163.06},{492,163.06}},color={0,0,127}));
  connect(cFunction.desired_acceleration_x, desired_acceleration_x_out) annotation(Line(points={{80,116.47},{492,116.47}},color={0,0,127}));
  connect(cFunction.desired_acceleration_y, desired_acceleration_y_out) annotation(Line(points={{80,69.88},{492,69.88}},color={0,0,127}));
  connect(cFunction.desired_acceleration_z, desired_acceleration_z_out) annotation(Line(points={{80,23.29},{492,23.29}},color={0,0,127}));
  connect(cFunction.learning_action_x, learning_action_x_out) annotation(Line(points={{80,-23.29},{492,-23.29}},color={0,0,127}));
  connect(cFunction.learning_action_y, learning_action_y_out) annotation(Line(points={{80,-69.88},{492,-69.88}},color={0,0,127}));
  connect(cFunction.learning_action_z, learning_action_z_out) annotation(Line(points={{80,-116.47},{492,-116.47}},color={0,0,127}));
  connect(cFunction.scheduled_gain_x, scheduled_gain_x_out) annotation(Line(points={{80,-163.06},{492,-163.06}},color={0,0,127}));
  connect(cFunction.scheduled_gain_y, scheduled_gain_y_out) annotation(Line(points={{80,-209.65},{492,-209.65}},color={0,0,127}));
  connect(cFunction.scheduled_gain_z, scheduled_gain_z_out) annotation(Line(points={{80,-256.24},{492,-256.24}},color={0,0,127}));
  connect(cFunction.fallback_active, fallback_active_out) annotation(Line(points={{80,-302.82},{492,-302.82}},color={0,0,127}));
  connect(cFunction.status_code, status_code_out) annotation(Line(points={{80,-349.41},{492,-349.41}},color={0,0,127}));
  connect(cFunction.mode_out, mode_out_out) annotation(Line(points={{80,-396.00},{492,-396.00}},color={0,0,127}));
end TrainedNeuralResidualCFunction;
