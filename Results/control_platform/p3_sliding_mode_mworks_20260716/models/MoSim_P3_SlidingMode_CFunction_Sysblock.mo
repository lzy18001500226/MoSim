model MoSim_P3_SlidingMode_CFunction_Sysblock
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left(controller_id_in, dt_in, position_x_in, position_y_in, position_z_in, velocity_x_in, velocity_y_in, velocity_z_in, reference_position_x_in, reference_position_y_in, reference_position_z_in, reference_velocity_x_in, reference_velocity_y_in, reference_velocity_z_in, reference_acceleration_x_in, reference_acceleration_y_in, reference_acceleration_z_in, reference_yaw_in, mass_kg_in, gravity_mps2_in, hover_percentage_in, max_tilt_rad_in, min_collective_thrust_n_in, max_collective_thrust_n_in, enable_in, reset_in), Right(desired_attitude_w_out, desired_attitude_x_out, desired_attitude_y_out, desired_attitude_z_out, normalized_thrust_out, collective_thrust_n_out, desired_acceleration_x_out, desired_acceleration_y_out, desired_acceleration_z_out, sliding_surface_x_out, sliding_surface_y_out, sliding_surface_z_out, auxiliary_state_x_out, auxiliary_state_y_out, auxiliary_state_z_out, effective_reaching_gain_x_out, effective_reaching_gain_y_out, effective_reaching_gain_z_out, saturated_out, status_code_out)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix"
:false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\p3_sliding_mode_mworks_20260716\\generated_c"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{-340,-620},{340,280}},grid={2,2})));

  CFunction cFunction 
    annotation (Placement(transformation(origin={0,0}, extent={{-28,-20},{28,20}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport controller_id_in 
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
  SysplorerEmbeddedCoder.Port.Inport reference_position_x_in 
    annotation (Placement(transformation(origin={-300,194},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y_in 
    annotation (Placement(transformation(origin={-300,187},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z_in 
    annotation (Placement(transformation(origin={-300,180},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x_in 
    annotation (Placement(transformation(origin={-300,173},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y_in 
    annotation (Placement(transformation(origin={-300,166},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z_in 
    annotation (Placement(transformation(origin={-300,159},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x_in 
    annotation (Placement(transformation(origin={-300,152},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y_in 
    annotation (Placement(transformation(origin={-300,145},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z_in 
    annotation (Placement(transformation(origin={-300,138},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_yaw_in 
    annotation (Placement(transformation(origin={-300,131},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mass_kg_in 
    annotation (Placement(transformation(origin={-300,124},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport gravity_mps2_in 
    annotation (Placement(transformation(origin={-300,117},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport hover_percentage_in 
    annotation (Placement(transformation(origin={-300,110},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport max_tilt_rad_in 
    annotation (Placement(transformation(origin={-300,103},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport min_collective_thrust_n_in 
    annotation (Placement(transformation(origin={-300,96},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport max_collective_thrust_n_in 
    annotation (Placement(transformation(origin={-300,89},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_in 
    annotation (Placement(transformation(origin={-300,82},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reset_in 
    annotation (Placement(transformation(origin={-300,75},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_w_out 
    annotation (Placement(transformation(origin={300,160},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_x_out 
    annotation (Placement(transformation(origin={300,151},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_y_out 
    annotation (Placement(transformation(origin={300,142},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_z_out 
    annotation (Placement(transformation(origin={300,133},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out 
    annotation (Placement(transformation(origin={300,124},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n_out 
    annotation (Placement(transformation(origin={300,115},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out 
    annotation (Placement(transformation(origin={300,106},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out 
    annotation (Placement(transformation(origin={300,97},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out 
    annotation (Placement(transformation(origin={300,88},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_x_out 
    annotation (Placement(transformation(origin={300,79},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_y_out 
    annotation (Placement(transformation(origin={300,70},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_z_out 
    annotation (Placement(transformation(origin={300,61},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_state_x_out 
    annotation (Placement(transformation(origin={300,52},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_state_y_out 
    annotation (Placement(transformation(origin={300,43},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_state_z_out 
    annotation (Placement(transformation(origin={300,34},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport effective_reaching_gain_x_out 
    annotation (Placement(transformation(origin={300,25},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport effective_reaching_gain_y_out 
    annotation (Placement(transformation(origin={300,16},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport effective_reaching_gain_z_out 
    annotation (Placement(transformation(origin={300,7},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport saturated_out 
    annotation (Placement(transformation(origin={300,-2},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport status_code_out 
    annotation (Placement(transformation(origin={300,-11},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left(controller_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_yaw, mass_kg, gravity_mps2, hover_percentage, max_tilt_rad, min_collective_thrust_n, max_collective_thrust_n, enable, reset), Right(desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, normalized_thrust, collective_thrust_n, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, sliding_surface_x, sliding_surface_y, sliding_surface_z, auxiliary_state_x, auxiliary_state_y, auxiliary_state_z, effective_reaching_gain_x, effective_reaching_gain_y, effective_reaching_gain_z, saturated, status_code)),PortLabels(labelType="CustomType",labels(label(text="controller_id",instance="controller_id"),label(text="dt",instance="dt"),label(text="position_x",instance="position_x"),label(text="position_y",instance="position_y"),label(text="position_z",instance="position_z"),label(text="velocity_x",instance="velocity_x"),label(text="velocity_y",instance="velocity_y"),label(text="velocity_z",instance="velocity_z"),label(text="reference_position_x",instance="reference_position_x"),label(text="reference_position_y",instance="reference_position_y"),label(text="reference_position_z",instance="reference_position_z"),label(text="reference_velocity_x",instance="reference_velocity_x"),label(text="reference_velocity_y",instance="reference_velocity_y"),label(text="reference_velocity_z",instance="reference_velocity_z"),label(text="reference_acceleration_x",instance="reference_acceleration_x"),label(text="reference_acceleration_y",instance="reference_acceleration_y"),label(text="reference_acceleration_z",instance="reference_acceleration_z"),label(text="reference_yaw",instance="reference_yaw"),label(text="mass_kg"
,instance="mass_kg"),label(text="gravity_mps2",instance="gravity_mps2"),label(text="hover_percentage",instance="hover_percentage"),label(text="max_tilt_rad",instance="max_tilt_rad"),label(text="min_collective_thrust_n",instance="min_collective_thrust_n"),label(text="max_collective_thrust_n",instance="max_collective_thrust_n"),label(text="enable",instance="enable"),label(text="reset",instance="reset"),label(text="desired_attitude_w",instance="desired_attitude_w"),label(text="desired_attitude_x",instance="desired_attitude_x"),label(text="desired_attitude_y",instance="desired_attitude_y"),label(text="desired_attitude_z",instance="desired_attitude_z"),label(text="normalized_thrust",instance="normalized_thrust"),label(text="collective_thrust_n",instance="collective_thrust_n"),label(text="desired_acceleration_x",instance="desired_acceleration_x"),label(text="desired_acceleration_y",instance="desired_acceleration_y"),label(text="desired_acceleration_z",instance="desired_acceleration_z"),label(text="sliding_surface_x",instance="sliding_surface_x"),label(text="sliding_surface_y",instance="sliding_surface_y"),label(text="sliding_surface_z",instance="sliding_surface_z"),label(text="auxiliary_state_x",instance="auxiliary_state_x"),label(text="auxiliary_state_y",instance="auxiliary_state_y"),label(text="auxiliary_state_z",instance="auxiliary_state_z"),label(text="effective_reaching_gain_x",instance="effective_reaching_gain_x"),label(text="effective_reaching_gain_y",instance="effective_reaching_gain_y"),label(text="effective_reaching_gain_z",instance="effective_reaching_gain_z"),label(text="saturated",instance="saturated"),label(text="status_code",instance="status_code"))),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
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
      input SysplorerEmbeddedCoder.Types.Auto reset annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto normalized_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto collective_thrust_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto sliding_surface_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto sliding_surface_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto sliding_surface_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto auxiliary_state_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto auxiliary_state_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto auxiliary_state_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto effective_reaching_gain_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto effective_reaching_gain_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto effective_reaching_gain_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto saturated annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto status_code annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
    external "C" MosimSlidingModeStepScalar(controller_id,dt,position_x,position_y,position_z,velocity_x,velocity_y,velocity_z,reference_position_x,reference_position_y,reference_position_z,reference_velocity_x,reference_velocity_y,reference_velocity_z,reference_acceleration_x,reference_acceleration_y,reference_acceleration_z,reference_yaw,mass_kg,gravity_mps2,hover_percentage,max_tilt_rad,min_collective_thrust_n,max_collective_thrust_n,enable,reset,desired_attitude_w,desired_attitude_x,desired_attitude_y,desired_attitude_z,normalized_thrust,collective_thrust_n,desired_acceleration_x,desired_acceleration_y,desired_acceleration_z,sliding_surface_x,sliding_surface_y,sliding_surface_z,auxiliary_state_x,auxiliary_state_y,auxiliary_state_z,effective_reaching_gain_x,effective_reaching_gain_y,effective_reaching_gain_z,saturated,status_code) 
      annotation (Include="enum MosimSlidingModeControllerId {
    MOSIM_SMC_INTEGRAL = 1,
    MOSIM_SMC_TERMINAL = 2,
    MOSIM_SMC_NONSINGULAR_TERMINAL = 3,
    MOSIM_SMC_SUPER_TWISTING = 4,
    MOSIM_SMC_ADAPTIVE = 5,
    MOSIM_SMC_FUZZY = 6
};

typedef struct {
    double dt;
    double position[3];
    double velocity[3];
    double reference_position[3];
    double reference_velocity[3];
    double reference_acceleration[3];
    double reference_yaw;
    int enable;
    int reset;
} MosimSlidingModeInput;

typedef struct {
    double lambda[3];
    double linear_gain[3];
    double reaching_gain[3];
    double boundary_layer[3];
    double integral_gain[3];
    double integral_limit[3];
    double terminal_alpha[3];
    double nonsingular_gain[3];
    double super_twisting_k1[3];
    double super_twisting_k2[3];
    double adaptive_rate[3];
    double adaptive_limit[3];
    double fuzzy_gain_delta[3];
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimSlidingModeParams;

typedef struct {
    double position_error_integral[3];
    double super_twisting_integral[3];
    double adaptive_reaching_gain[3];
} MosimSlidingModeState;

typedef struct {
    double desired_acceleration[3];
    double desired_attitude_wxyz[4];
    double normalized_thrust;
    double collective_thrust_n;
    double sliding_surface[3];
    double auxiliary_state[3];
    double effective_reaching_gain[3];
    int saturated;
    int status_code;
} MosimSlidingModeOutput;

void mosim_sliding_mode_default_params(MosimSlidingModeParams *params);
void mosim_sliding_mode_reset(
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state);
int mosim_sliding_mode_step(
    int controller_id,
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state,
    const MosimSlidingModeInput *input,
    MosimSlidingModeOutput *output);




#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static double signed_power(double value, double exponent)
{
    if (value > 0.0) return pow(value, exponent);
    if (value < 0.0) return -pow(-value, exponent);
    return 0.0;
}

static double boundary_sign(double value, double width)
{
    return clamp_value(value / fmax(width, 1.0e-9), -1.0, 1.0);
}

static int finite3(const double value[3])
{
    return isfinite(value[0]) && isfinite(value[1]) && isfinite(value[2]);
}

static int params_valid(const MosimSlidingModeParams *params)
{
    int axis;
    if (!isfinite(params->mass_kg) || params->mass_kg <= 0.0 ||
        !isfinite(params->gravity_mps2) || params->gravity_mps2 <= 0.0 ||
        !isfinite(params->hover_percentage) || params->hover_percentage <= 0.0 ||
        params->hover_percentage > 1.0 ||
        !isfinite(params->max_tilt_rad) || params->max_tilt_rad <= 0.0 ||
        params->max_tilt_rad >= 1.5707963267948966 ||
        !isfinite(params->min_collective_thrust_n) ||
        !isfinite(params->max_collective_thrust_n) ||
        params->min_collective_thrust_n < 0.0 ||
        params->max_collective_thrust_n <= params->min_collective_thrust_n) return 0;
    for (axis = 0; axis < 3; ++axis) {
        if (!isfinite(params->lambda[axis]) || params->lambda[axis] <= 0.0 ||
            !isfinite(params->linear_gain[axis]) || params->linear_gain[axis] < 0.0 ||
            !isfinite(params->reaching_gain[axis]) || params->reaching_gain[axis] < 0.0 ||
            !isfinite(params->boundary_layer[axis]) || params->boundary_layer[axis] <= 0.0 ||
            !isfinite(params->integral_gain[axis]) || params->integral_gain[axis] < 0.0 ||
            !isfinite(params->integral_limit[axis]) || params->integral_limit[axis] < 0.0 ||
            !isfinite(params->terminal_alpha[axis]) || params->terminal_alpha[axis] <= 0.0 ||
            params->terminal_alpha[axis] >= 1.0 ||
            !isfinite(params->nonsingular_gain[axis]) || params->nonsingular_gain[axis] < 0.0 ||
            !isfinite(params->super_twisting_k1[axis]) || params->super_twisting_k1[axis] < 0.0 ||
            !isfinite(params->super_twisting_k2[axis]) || params->super_twisting_k2[axis] < 0.0 ||
            !isfinite(params->adaptive_rate[axis]) || params->adaptive_rate[axis] < 0.0 ||
            !isfinite(params->adaptive_limit[axis]) ||
            params->adaptive_limit[axis] < params->reaching_gain[axis] ||
            !isfinite(params->fuzzy_gain_delta[axis]) || params->fuzzy_gain_delta[axis] < 0.0) return 0;
    }
    return 1;
}

static double norm3(const double value[3])
{
    return sqrt(value[0] * value[0] + value[1] * value[1] + value[2] * value[2]);
}

static void cross3(const double a[3], const double b[3], double out[3])
{
    out[0] = a[1] * b[2] - a[2] * b[1];
    out[1] = a[2] * b[0] - a[0] * b[2];
    out[2] = a[0] * b[1] - a[1] * b[0];
}

static int normalize3(double value[3])
{
    const double length = norm3(value);
    int axis;
    if (length <= 1.0e-12) return -1;
    for (axis = 0; axis < 3; ++axis) value[axis] /= length;
    return 0;
}

static void quaternion_from_rotation(const double rotation[3][3], double q[4])
{
    const double trace = rotation[0][0] + rotation[1][1] + rotation[2][2];
    if (trace > 0.0) {
        const double scale = 2.0 * sqrt(trace + 1.0);
        q[0] = 0.25 * scale;
        q[1] = (rotation[2][1] - rotation[1][2]) / scale;
        q[2] = (rotation[0][2] - rotation[2][0]) / scale;
        q[3] = (rotation[1][0] - rotation[0][1]) / scale;
    } else if (rotation[0][0] > rotation[1][1] && rotation[0][0] > rotation[2][2]) {
        const double scale = 2.0 * sqrt(1.0 + rotation[0][0] - rotation[1][1] - rotation[2][2]);
        q[0] = (rotation[2][1] - rotation[1][2]) / scale;
        q[1] = 0.25 * scale;
        q[2] = (rotation[0][1] + rotation[1][0]) / scale;
        q[3] = (rotation[0][2] + rotation[2][0]) / scale;
    } else if (rotation[1][1] > rotation[2][2]) {
        const double scale = 2.0 * sqrt(1.0 + rotation[1][1] - rotation[0][0] - rotation[2][2]);
        q[0] = (rotation[0][2] - rotation[2][0]) / scale;
        q[1] = (rotation[0][1] + rotation[1][0]) / scale;
        q[2] = 0.25 * scale;
        q[3] = (rotation[1][2] + rotation[2][1]) / scale;
    } else {
        const double scale = 2.0 * sqrt(1.0 + rotation[2][2] - rotation[0][0] - rotation[1][1]);
        q[0] = (rotation[1][0] - rotation[0][1]) / scale;
        q[1] = (rotation[0][2] + rotation[2][0]) / scale;
        q[2] = (rotation[1][2] + rotation[2][1]) / scale;
        q[3] = 0.25 * scale;
    }
    if (q[0] < 0.0) {
        q[0] = -q[0]; q[1] = -q[1]; q[2] = -q[2]; q[3] = -q[3];
    }
}

static int command_from_acceleration(
    const MosimSlidingModeParams *params,
    const MosimSlidingModeInput *input,
    MosimSlidingModeOutput *output)
{
    double force[3];
    double b1_reference[3];
    double b1[3];
    double b2[3];
    double b3[3];
    double rotation[3][3];
    double force_norm;
    double horizontal_acceleration;
    double horizontal_limit;
    int axis;
    horizontal_acceleration = hypot(output->desired_acceleration[0], output->desired_acceleration[1]);
    horizontal_limit = fmax(0.0, output->desired_acceleration[2]) * tan(params->max_tilt_rad);
    if (horizontal_acceleration > horizontal_limit && horizontal_acceleration > 1.0e-12) {
        const double scale = horizontal_limit / horizontal_acceleration;
        output->desired_acceleration[0] *= scale;
        output->desired_acceleration[1] *= scale;
        output->saturated = 1;
    }
    for (axis = 0; axis < 3; ++axis) {
        force[axis] = params->mass_kg * output->desired_acceleration[axis];
        b3[axis] = force[axis];
    }
    force_norm = norm3(force);
    if (normalize3(b3) != 0) return -4;
    b1_reference[0] = cos(input->reference_yaw);
    b1_reference[1] = sin(input->reference_yaw);
    b1_reference[2] = 0.0;
    cross3(b3, b1_reference, b2);
    if (normalize3(b2) != 0) return -4;
    cross3(b2, b3, b1);
    for (axis = 0; axis < 3; ++axis) {
        rotation[axis][0] = b1[axis];
        rotation[axis][1] = b2[axis];
        rotation[axis][2] = b3[axis];
    }
    quaternion_from_rotation(rotation, output->desired_attitude_wxyz);
    output->collective_thrust_n = clamp_value(
        force_norm, params->min_collective_thrust_n, params->max_collective_thrust_n);
    if (fabs(output->collective_thrust_n - force_norm) > 1.0e-12) output->saturated = 1;
    output->normalized_thrust = clamp_value(
        output->collective_thrust_n /
            (params->mass_kg * params->gravity_mps2 / params->hover_percentage),
        0.0, 1.0);
    return 0;
}

void mosim_sliding_mode_default_params(MosimSlidingModeParams *params)
{
    const MosimSlidingModeParams defaults = {
        {4.0, 4.0, 2.0}, {2.75, 2.75, 2.0}, {0.08, 0.08, 0.08}, {0.35, 0.35, 0.35},
        {0.08, 0.08, 0.08}, {0.20, 0.20, 0.20}, {0.90, 0.90, 0.92},
        {0.10, 0.10, 0.10}, {1.6, 1.6, 2.0}, {1.2, 1.2, 1.5},
        {0.04, 0.04, 0.04}, {0.30, 0.30, 0.35}, {0.04, 0.04, 0.04},
        0.67, 9.80665, 0.291, 0.5235987755982988, 0.0, 16.0
    };
    if (params != NULL) *params = defaults;
}

void mosim_sliding_mode_reset(
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state)
{
    int axis;
    if (state == NULL) return;
    memset(state, 0, sizeof(*state));
    if (params != NULL) {
        for (axis = 0; axis < 3; ++axis) {
            state->adaptive_reaching_gain[axis] = params->reaching_gain[axis];
        }
    }
}

static void controller_axis_step(
    int controller_id,
    int axis,
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state,
    const MosimSlidingModeInput *input,
    MosimSlidingModeOutput *output)
{
    const double position_error = input->reference_position[axis] - input->position[axis];
    const double velocity_error = input->reference_velocity[axis] - input->velocity[axis];
    double sliding = velocity_error + params->lambda[axis] * position_error;
    double robust;
    double effective_gain = params->reaching_gain[axis];
    if (controller_id == MOSIM_SMC_INTEGRAL) {
        state->position_error_integral[axis] = clamp_value(
            state->position_error_integral[axis] + position_error * input->dt,
            -params->integral_limit[axis], params->integral_limit[axis]);
        sliding += params->integral_gain[axis] * state->position_error_integral[axis];
    } else if (controller_id == MOSIM_SMC_TERMINAL) {
        sliding = velocity_error + params->lambda[axis] *
            signed_power(position_error, params->terminal_alpha[axis]);
    } else if (controller_id == MOSIM_SMC_NONSINGULAR_TERMINAL) {
        sliding += params->nonsingular_gain[axis] * signed_power(position_error, 1.5);
    } else if (controller_id == MOSIM_SMC_SUPER_TWISTING) {
        const double sign = boundary_sign(sliding, params->boundary_layer[axis]);
        state->super_twisting_integral[axis] = clamp_value(
            state->super_twisting_integral[axis] + params->super_twisting_k2[axis] * sign * input->dt,
            -params->adaptive_limit[axis], params->adaptive_limit[axis]);
        robust = params->super_twisting_k1[axis] * sqrt(fabs(sliding)) * sign +
            state->super_twisting_integral[axis];
        output->sliding_surface[axis] = sliding;
        output->auxiliary_state[axis] = state->super_twisting_integral[axis];
        output->effective_reaching_gain[axis] = params->super_twisting_k1[axis];
        output->desired_acceleration[axis] = input->reference_acceleration[axis] +
            params->lambda[axis] * velocity_error + params->linear_gain[axis] * sliding + robust;
        return;
    } else if (controller_id == MOSIM_SMC_ADAPTIVE) {
        state->adaptive_reaching_gain[axis] = clamp_value(
            state->adaptive_reaching_gain[axis] +
                params->adaptive_rate[axis] * (fabs(sliding) - 0.05) * input->dt,
            params->reaching_gain[axis], params->adaptive_limit[axis]);
        effective_gain = state->adaptive_reaching_gain[axis];
    } else if (controller_id == MOSIM_SMC_FUZZY) {
        const double normalized_error = clamp_value(
            fabs(sliding) / (4.0 * params->boundary_layer[axis]), 0.0, 1.0);
        effective_gain += params->fuzzy_gain_delta[axis] *
            normalized_error * (2.0 - normalized_error);
    }
    robust = effective_gain * boundary_sign(sliding, params->boundary_layer[axis]);
    output->sliding_surface[axis] = sliding;
    output->auxiliary_state[axis] = state->position_error_integral[axis];
    output->effective_reaching_gain[axis] = effective_gain;
    output->desired_acceleration[axis] = input->reference_acceleration[axis] +
        params->lambda[axis] * velocity_error + params->linear_gain[axis] * sliding + robust;
}

int mosim_sliding_mode_step(
    int controller_id,
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state,
    const MosimSlidingModeInput *input,
    MosimSlidingModeOutput *output)
{
    int axis;
    int rc;
    if (params == NULL || state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_wxyz[0] = 1.0;
    if (input->reset) mosim_sliding_mode_reset(params, state);
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    if (!params_valid(params)) {
        output->status_code = -5;
        return -5;
    }
    if (!isfinite(input->dt) || input->dt <= 0.0 || input->dt > 0.1 ||
        !finite3(input->position) || !finite3(input->velocity) ||
        !finite3(input->reference_position) || !finite3(input->reference_velocity) ||
        !finite3(input->reference_acceleration) || !isfinite(input->reference_yaw)) {
        output->status_code = -3;
        return -3;
    }
    if (controller_id < MOSIM_SMC_INTEGRAL || controller_id > MOSIM_SMC_FUZZY) {
        output->status_code = -2;
        return -2;
    }
    for (axis = 0; axis < 3; ++axis) {
        controller_axis_step(controller_id, axis, params, state, input, output);
    }
    output->desired_acceleration[2] += params->gravity_mps2;
    rc = command_from_acceleration(params, input, output);
    if (rc != 0) {
        output->status_code = rc;
        return rc;
    }
    return 0;
}
void MosimSlidingModeStepScalar(
    double controller_id,
    double dt,
    double position_x,
    double position_y,
    double position_z,
    double velocity_x,
    double velocity_y,
    double velocity_z,
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
    double reset,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *normalized_thrust,
    double *collective_thrust_n,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *sliding_surface_x,
    double *sliding_surface_y,
    double *sliding_surface_z,
    double *auxiliary_state_x,
    double *auxiliary_state_y,
    double *auxiliary_state_z,
    double *effective_reaching_gain_x,
    double *effective_reaching_gain_y,
    double *effective_reaching_gain_z,
    double *saturated,
    double *status_code)
{
    static MosimSlidingModeState states[7];
    MosimSlidingModeParams params;
    MosimSlidingModeInput input;
    MosimSlidingModeOutput output;
    int id = (int)controller_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.position[0] = position_x; input.position[1] = position_y; input.position[2] = position_z;
    input.velocity[0] = velocity_x; input.velocity[1] = velocity_y; input.velocity[2] = velocity_z;
    input.reference_position[0] = reference_position_x;
    input.reference_position[1] = reference_position_y;
    input.reference_position[2] = reference_position_z;
    input.reference_velocity[0] = reference_velocity_x;
    input.reference_velocity[1] = reference_velocity_y;
    input.reference_velocity[2] = reference_velocity_z;
    input.reference_acceleration[0] = reference_acceleration_x;
    input.reference_acceleration[1] = reference_acceleration_y;
    input.reference_acceleration[2] = reference_acceleration_z;
    input.reference_yaw = reference_yaw;
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    mosim_sliding_mode_default_params(&params);
    params.mass_kg = mass_kg;
    params.gravity_mps2 = gravity_mps2;
    params.hover_percentage = hover_percentage;
    params.max_tilt_rad = max_tilt_rad;
    params.min_collective_thrust_n = min_collective_thrust_n;
    params.max_collective_thrust_n = max_collective_thrust_n;
    if (id < 1 || id > 6) id = 0;
    result = mosim_sliding_mode_step(id, &params, &states[id], &input, &output);
    if (result != 0) {
        memset(&output, 0, sizeof(output));
        output.desired_attitude_wxyz[0] = 1.0;
        output.status_code = result;
    }
    *desired_attitude_w = output.desired_attitude_wxyz[0];
    *desired_attitude_x = output.desired_attitude_wxyz[1];
    *desired_attitude_y = output.desired_attitude_wxyz[2];
    *desired_attitude_z = output.desired_attitude_wxyz[3];
    *normalized_thrust = output.normalized_thrust;
    *collective_thrust_n = output.collective_thrust_n;
    *desired_acceleration_x = output.desired_acceleration[0];
    *desired_acceleration_y = output.desired_acceleration[1];
    *desired_acceleration_z = output.desired_acceleration[2];
    *sliding_surface_x = output.sliding_surface[0];
    *sliding_surface_y = output.sliding_surface[1];
    *sliding_surface_z = output.sliding_surface[2];
    *auxiliary_state_x = output.auxiliary_state[0];
    *auxiliary_state_y = output.auxiliary_state[1];
    *auxiliary_state_z = output.auxiliary_state[2];
    *effective_reaching_gain_x = output.effective_reaching_gain[0];
    *effective_reaching_gain_y = output.effective_reaching_gain[1];
    *effective_reaching_gain_z = output.effective_reaching_gain[2];
    *saturated = (double)output.saturated;
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
    SysplorerEmbeddedCoder.Port.Outport normalized_thrust 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport collective_thrust_n 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport sliding_surface_x 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport sliding_surface_y 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport sliding_surface_z 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport auxiliary_state_x 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport auxiliary_state_y 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport auxiliary_state_z 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport effective_reaching_gain_x 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport effective_reaching_gain_y 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport effective_reaching_gain_z 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport saturated 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport status_code 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
  equation
    (desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, normalized_thrust, collective_thrust_n, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, sliding_surface_x, sliding_surface_y, sliding_surface_z, auxiliary_state_x, auxiliary_state_y, auxiliary_state_z, effective_reaching_gain_x, effective_reaching_gain_y, effective_reaching_gain_z, saturated, status_code) = func_CFunction(controller_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_yaw, mass_kg, gravity_mps2, hover_percentage, max_tilt_rad, min_collective_thrust_n, max_collective_thrust_n, enable, reset);
  end CFunction;

equation
  connect(controller_id_in, cFunction.controller_id) annotation(Line(origin={0,0},points={{-250,250},{-50,250}},color={0,0,0}));
  connect(dt_in, cFunction.dt) annotation(Line(origin={0,0},points={{-250,244},{-50,244}},color={0,0,0}));
  connect(position_x_in, cFunction.position_x) annotation(Line(origin={0,0},points={{-250,238},{-50,238}},color={0,0,0}));
  connect(position_y_in, cFunction.position_y) annotation(Line(origin={0,0},points={{-250,232},{-50,232}},color={0,0,0}));
  connect(position_z_in, cFunction.position_z) annotation(Line(origin={0,0},points={{-250,226},{-50,226}},color={0,0,0}));
  connect(velocity_x_in, cFunction.velocity_x) annotation(Line(origin={0,0},points={{-250,220},{-50,220}},color={0,0,0}));
  connect(velocity_y_in, cFunction.velocity_y) annotation(Line(origin={0,0},points={{-250,214},{-50,214}},color={0,0,0}));
  connect(velocity_z_in, cFunction.velocity_z) annotation(Line(origin={0,0},points={{-250,208},{-50,208}},color={0,0,0}));
  connect(reference_position_x_in, cFunction.reference_position_x) annotation(Line(origin={0,0},points={{-250,202},{-50,202}},color={0,0,0}));
  connect(reference_position_y_in, cFunction.reference_position_y) annotation(Line(origin={0,0},points={{-250,196},{-50,196}},color={0,0,0}));
  connect(reference_position_z_in, cFunction.reference_position_z) annotation(Line(origin={0,0},points={{-250,190},{-50,190}},color={0,0,0}));
  connect(reference_velocity_x_in, cFunction.reference_velocity_x) annotation(Line(origin={0,0},points={{-250,184},{-50,184}},color={0,0,0}));
  connect(reference_velocity_y_in, cFunction.reference_velocity_y) annotation(Line(origin={0,0},points={{-250,178},{-50,178}},color={0,0,0}));
  connect(reference_velocity_z_in, cFunction.reference_velocity_z) annotation(Line(origin={0,0},points={{-250,172},{-50,172}},color={0,0,0}));
  connect(reference_acceleration_x_in, cFunction.reference_acceleration_x) annotation(Line(origin={0,0},points={{-250,166},{-50,166}},color={0,0,0}));
  connect(reference_acceleration_y_in, cFunction.reference_acceleration_y) annotation(Line(origin={0,0},points={{-250,160},{-50,160}},color={0,0,0}));
  connect(reference_acceleration_z_in, cFunction.reference_acceleration_z) annotation(Line(origin={0,0},points={{-250,154},{-50,154}},color={0,0,0}));
  connect(reference_yaw_in, cFunction.reference_yaw) annotation(Line(origin={0,0},points={{-250,148},{-50,148}},color={0,0,0}));
  connect(mass_kg_in, cFunction.mass_kg) annotation(Line(origin={0,0},points={{-250,142},{-50,142}},color={0,0,0}));
  connect(gravity_mps2_in, cFunction.gravity_mps2) annotation(Line(origin={0,0},points={{-250,136},{-50,136}},color={0,0,0}));
  connect(hover_percentage_in, cFunction.hover_percentage) annotation(Line(origin={0,0},points={{-250,130},{-50,130}},color={0,0,0}));
  connect(max_tilt_rad_in, cFunction.max_tilt_rad) annotation(Line(origin={0,0},points={{-250,124},{-50,124}},color={0,0,0}));
  connect(min_collective_thrust_n_in, cFunction.min_collective_thrust_n) annotation(Line(origin={0,0},points={{-250,118},{-50,118}},color={0,0,0}));
  connect(max_collective_thrust_n_in, cFunction.max_collective_thrust_n) annotation(Line(origin={0,0},points={{-250,112},{-50,112}},color={0,0,0}));
  connect(enable_in, cFunction.enable) annotation(Line(origin={0,0},points={{-250,106},{-50,106}},color={0,0,0}));
  connect(reset_in, cFunction.reset) annotation(Line(origin={0,0},points={{-250,100},{-50,100}},color={0,0,0}));
  connect(cFunction.desired_attitude_w, desired_attitude_w_out) annotation(Line(origin={0,0},points={{50,160},{250,160}},color={0,0,0}));
  connect(cFunction.desired_attitude_x, desired_attitude_x_out) annotation(Line(origin={0,0},points={{50,153},{250,153}},color={0,0,0}));
  connect(cFunction.desired_attitude_y, desired_attitude_y_out) annotation(Line(origin={0,0},points={{50,146},{250,146}},color={0,0,0}));
  connect(cFunction.desired_attitude_z, desired_attitude_z_out) annotation(Line(origin={0,0},points={{50,139},{250,139}},color={0,0,0}));
  connect(cFunction.normalized_thrust, normalized_thrust_out) annotation(Line(origin={0,0},points={{50,132},{250,132}},color={0,0,0}));
  connect(cFunction.collective_thrust_n, collective_thrust_n_out) annotation(Line(origin={0,0},points={{50,125},{250,125}},color={0,0,0}));
  connect(cFunction.desired_acceleration_x, desired_acceleration_x_out) annotation(Line(origin={0,0},points={{50,118},{250,118}},color={0,0,0}));
  connect(cFunction.desired_acceleration_y, desired_acceleration_y_out) annotation(Line(origin={0,0},points={{50,111},{250,111}},color={0,0,0}));
  connect(cFunction.desired_acceleration_z, desired_acceleration_z_out) annotation(Line(origin={0,0},points={{50,104},{250,104}},color={0,0,0}));
  connect(cFunction.sliding_surface_x, sliding_surface_x_out) annotation(Line(origin={0,0},points={{50,97},{250,97}},color={0,0,0}));
  connect(cFunction.sliding_surface_y, sliding_surface_y_out) annotation(Line(origin={0,0},points={{50,90},{250,90}},color={0,0,0}));
  connect(cFunction.sliding_surface_z, sliding_surface_z_out) annotation(Line(origin={0,0},points={{50,83},{250,83}},color={0,0,0}));
  connect(cFunction.auxiliary_state_x, auxiliary_state_x_out) annotation(Line(origin={0,0},points={{50,76},{250,76}},color={0,0,0}));
  connect(cFunction.auxiliary_state_y, auxiliary_state_y_out) annotation(Line(origin={0,0},points={{50,69},{250,69}},color={0,0,0}));
  connect(cFunction.auxiliary_state_z, auxiliary_state_z_out) annotation(Line(origin={0,0},points={{50,62},{250,62}},color={0,0,0}));
  connect(cFunction.effective_reaching_gain_x, effective_reaching_gain_x_out) annotation(Line(origin={0,0},points={{50,55},{250,55}},color={0,0,0}));
  connect(cFunction.effective_reaching_gain_y, effective_reaching_gain_y_out) annotation(Line(origin={0,0},points={{50,48},{250,48}},color={0,0,0}));
  connect(cFunction.effective_reaching_gain_z, effective_reaching_gain_z_out) annotation(Line(origin={0,0},points={{50,41},{250,41}},color={0,0,0}));
  connect(cFunction.saturated, saturated_out) annotation(Line(origin={0,0},points={{50,34},{250,34}},color={0,0,0}));
  connect(cFunction.status_code, status_code_out) annotation(Line(origin={0,0},points={{50,27},{250,27}},color={0,0,0}));
end MoSim_P3_SlidingMode_CFunction_Sysblock;