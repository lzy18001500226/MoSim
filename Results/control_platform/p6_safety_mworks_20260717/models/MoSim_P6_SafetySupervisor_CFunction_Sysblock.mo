model MoSim_P6_SafetySupervisor_CFunction_Sysblock
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left(mode_id_in, dt_in, position_x_in, position_y_in, position_z_in, velocity_x_in, velocity_y_in, velocity_z_in, candidate_acceleration_x_in, candidate_acceleration_y_in, candidate_acceleration_z_in, candidate_thrust_in, candidate_tilt_rad_in, reference_position_x_in, reference_position_y_in, reference_position_z_in, home_position_x_in, home_position_y_in, home_position_z_in, obstacle_distance_in, command_age_s_in, state_valid_in, offboard_valid_in, emergency_request_in, return_request_in, land_request_in, enable_in, reset_in), Right(safe_acceleration_x_out, safe_acceleration_y_out, safe_acceleration_z_out, safe_thrust_out, safe_reference_x_out, safe_reference_y_out, safe_reference_z_out, action_out, state_out, active_constraints_out, modified_out, status_code_out)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type"
:"camelCase"}},"interface"
:{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\p6_safety_mworks_20260717\\generated_c"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{-340,-620},{340,280}},grid={2,2})));

  CFunction cFunction 
    annotation (Placement(transformation(origin={0,0}, extent={{-28,-20},{28,20}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mode_id_in 
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
  SysplorerEmbeddedCoder.Port.Inport candidate_acceleration_x_in 
    annotation (Placement(transformation(origin={-300,194},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport candidate_acceleration_y_in 
    annotation (Placement(transformation(origin={-300,187},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport candidate_acceleration_z_in 
    annotation (Placement(transformation(origin={-300,180},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport candidate_thrust_in 
    annotation (Placement(transformation(origin={-300,173},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport candidate_tilt_rad_in 
    annotation (Placement(transformation(origin={-300,166},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x_in 
    annotation (Placement(transformation(origin={-300,159},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y_in 
    annotation (Placement(transformation(origin={-300,152},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z_in 
    annotation (Placement(transformation(origin={-300,145},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport home_position_x_in 
    annotation (Placement(transformation(origin={-300,138},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport home_position_y_in 
    annotation (Placement(transformation(origin={-300,131},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport home_position_z_in 
    annotation (Placement(transformation(origin={-300,124},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport obstacle_distance_in 
    annotation (Placement(transformation(origin={-300,117},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport command_age_s_in 
    annotation (Placement(transformation(origin={-300,110},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport state_valid_in 
    annotation (Placement(transformation(origin={-300,103},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport offboard_valid_in 
    annotation (Placement(transformation(origin={-300,96},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport emergency_request_in 
    annotation (Placement(transformation(origin={-300,89},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport return_request_in 
    annotation (Placement(transformation(origin={-300,82},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport land_request_in 
    annotation (Placement(transformation(origin={-300,75},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_in 
    annotation (Placement(transformation(origin={-300,68},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reset_in 
    annotation (Placement(transformation(origin={-300,61},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport safe_acceleration_x_out 
    annotation (Placement(transformation(origin={300,160},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport safe_acceleration_y_out 
    annotation (Placement(transformation(origin={300,151},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport safe_acceleration_z_out 
    annotation (Placement(transformation(origin={300,142},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport safe_thrust_out 
    annotation (Placement(transformation(origin={300,133},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport safe_reference_x_out 
    annotation (Placement(transformation(origin={300,124},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport safe_reference_y_out 
    annotation (Placement(transformation(origin={300,115},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport safe_reference_z_out 
    annotation (Placement(transformation(origin={300,106},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport action_out 
    annotation (Placement(transformation(origin={300,97},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport state_out 
    annotation (Placement(transformation(origin={300,88},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport active_constraints_out 
    annotation (Placement(transformation(origin={300,79},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport modified_out 
    annotation (Placement(transformation(origin={300,70},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport status_code_out 
    annotation (Placement(transformation(origin={300,61},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left(mode_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, candidate_acceleration_x, candidate_acceleration_y, candidate_acceleration_z, candidate_thrust, candidate_tilt_rad, reference_position_x, reference_position_y, reference_position_z, home_position_x, home_position_y, home_position_z, obstacle_distance, command_age_s, state_valid, offboard_valid, emergency_request, return_request, land_request, enable, reset), Right(safe_acceleration_x, safe_acceleration_y, safe_acceleration_z, safe_thrust, safe_reference_x, safe_reference_y, safe_reference_z, action, state, active_constraints, modified, status_code)),PortLabels(labelType="CustomType",labels(label(text="mode_id",instance="mode_id"),label(text="dt",instance="dt"),label(text="position_x",instance="position_x"),label(text="position_y",instance="position_y"),label(text="position_z",instance="position_z"),label(text="velocity_x",instance="velocity_x"),label(text="velocity_y",instance="velocity_y"),label(text="velocity_z",instance="velocity_z"),label(text="candidate_acceleration_x",instance="candidate_acceleration_x"),label(text="candidate_acceleration_y",instance="candidate_acceleration_y"),label(text="candidate_acceleration_z",instance="candidate_acceleration_z"),label(text="candidate_thrust",instance="candidate_thrust"),label(text="candidate_tilt_rad",instance="candidate_tilt_rad"),label(text="reference_position_x",instance="reference_position_x"),label(text="reference_position_y",instance="reference_position_y"),label(text="reference_position_z",instance="reference_position_z"),label(text="home_position_x",instance="home_position_x"),label(text="home_position_y",instance="home_position_y"),label(text="home_position_z",instance="home_position_z"),label(text="obstacle_distance",instance="obstacle_distance"),label(text="command_age_s",instance="command_age_s"),label(text="state_valid",instance="state_valid"),label(text="offboard_valid",instance
="offboard_valid"),label(text="emergency_request",instance="emergency_request"),label(text="return_request",instance="return_request"),label(text="land_request",instance="land_request"),label(text="enable",instance="enable"),label(text="reset",instance="reset"),label(text="safe_acceleration_x",instance="safe_acceleration_x"),label(text="safe_acceleration_y",instance="safe_acceleration_y"),label(text="safe_acceleration_z",instance="safe_acceleration_z"),label(text="safe_thrust",instance="safe_thrust"),label(text="safe_reference_x",instance="safe_reference_x"),label(text="safe_reference_y",instance="safe_reference_y"),label(text="safe_reference_z",instance="safe_reference_z"),label(text="action",instance="action"),label(text="state",instance="state"),label(text="active_constraints",instance="active_constraints"),label(text="modified",instance="modified"),label(text="status_code",instance="status_code"))),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
      Icon(coordinateSystem(extent={{-200,-100},{200,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2}),graphics={Rectangle(origin={0,0},fillColor={255,255,255},fillPattern=FillPattern.Solid,extent={{-200,100},{200,-100}}),Text(origin={0,0},extent={{-100,20},{100,-20}},textString="C",verticalAlignment=TextAlignment.VCenter),Text(origin={0,-120},lineColor={0,0,0},extent={{-150,20},{150,-20}},textString="%name",fontSize=14,textColor={0,0,0},verticalAlignment=TextAlignment.Top)}),
      Diagram(coordinateSystem(extent={{-100,-100},{100,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2})));

    function func_CFunction
      input SysplorerEmbeddedCoder.Types.Auto mode_id annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto dt annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto position_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto position_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto position_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto velocity_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto velocity_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto velocity_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto candidate_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto candidate_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto candidate_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto candidate_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto candidate_tilt_rad annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_position_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_position_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_position_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto home_position_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto home_position_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto home_position_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto obstacle_distance annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto command_age_s annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto state_valid annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto offboard_valid annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto emergency_request annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto return_request annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto land_request annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto enable annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reset annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto safe_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto safe_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto safe_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto safe_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto safe_reference_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto safe_reference_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto safe_reference_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto action annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto state annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto active_constraints annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto modified annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto status_code annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
    external "C" MosimSafetySupervisorStepScalar(mode_id,dt,position_x,position_y,position_z,velocity_x,velocity_y,velocity_z,candidate_acceleration_x,candidate_acceleration_y,candidate_acceleration_z,candidate_thrust,candidate_tilt_rad,reference_position_x,reference_position_y,reference_position_z,home_position_x,home_position_y,home_position_z,obstacle_distance,command_age_s,state_valid,offboard_valid,emergency_request,return_request,land_request,enable,reset,safe_acceleration_x,safe_acceleration_y,safe_acceleration_z,safe_thrust,safe_reference_x,safe_reference_y,safe_reference_z,action,state,active_constraints,modified,status_code) 
      annotation (Include="enum {
    MOSIM_SAFETY_FILTER = 1,
    MOSIM_SAFETY_CBF = 2,
    MOSIM_SAFETY_REFERENCE_GOVERNOR = 3,
    MOSIM_SAFETY_GEOFENCE = 4,
    MOSIM_SAFETY_EMERGENCY_STOP = 5,
    MOSIM_SAFETY_RETURN_AND_LAND = 6,
    MOSIM_SAFETY_FAILSAFE = 7
};

enum {
    MOSIM_SAFETY_ACTION_PASS = 0,
    MOSIM_SAFETY_ACTION_MODIFY = 1,
    MOSIM_SAFETY_ACTION_HOLD = 2,
    MOSIM_SAFETY_ACTION_RETURN = 3,
    MOSIM_SAFETY_ACTION_LAND = 4,
    MOSIM_SAFETY_ACTION_STOP = 5
};

enum {
    MOSIM_SAFETY_STATE_NOMINAL = 0,
    MOSIM_SAFETY_STATE_HOLD = 1,
    MOSIM_SAFETY_STATE_RETURN = 2,
    MOSIM_SAFETY_STATE_LAND = 3,
    MOSIM_SAFETY_STATE_STOP = 4
};

typedef struct {
    double max_acceleration[3];
    double max_speed[3];
    double max_tilt_rad;
    double min_thrust;
    double max_thrust;
    double geofence_min[3];
    double geofence_max[3];
    double geofence_margin;
    double cbf_alpha;
    double obstacle_min_distance;
    double governor_rate[3];
    double command_timeout_s;
    double return_altitude;
    double land_speed;
} MosimSafetyParams;

typedef struct {
    int state;
    double governed_reference[3];
} MosimSafetyState;

typedef struct {
    double dt;
    double position[3];
    double velocity[3];
    double candidate_acceleration[3];
    double candidate_thrust;
    double candidate_tilt_rad;
    double reference_position[3];
    double home_position[3];
    double obstacle_distance;
    double command_age_s;
    int state_valid;
    int offboard_valid;
    int emergency_request;
    int return_request;
    int land_request;
    int enable;
    int reset;
} MosimSafetyInput;

typedef struct {
    double safe_acceleration[3];
    double safe_thrust;
    double safe_reference[3];
    int action;
    int state;
    unsigned int active_constraints;
    int modified;
    int status_code;
} MosimSafetyOutput;

void mosim_safety_default_params(MosimSafetyParams *params);
void mosim_safety_reset(MosimSafetyState *state);
int mosim_safety_step(int mode, const MosimSafetyParams *params,
                      MosimSafetyState *state, const MosimSafetyInput *input,
                      MosimSafetyOutput *output);




#include <math.h>
#include <stddef.h>
#include <string.h>

enum {
    CONSTRAINT_ACCELERATION = 1u << 0,
    CONSTRAINT_THRUST = 1u << 1,
    CONSTRAINT_TILT = 1u << 2,
    CONSTRAINT_CBF = 1u << 3,
    CONSTRAINT_GEOFENCE = 1u << 4,
    CONSTRAINT_TIMEOUT = 1u << 5,
    CONSTRAINT_INVALID_STATE = 1u << 6,
    CONSTRAINT_EMERGENCY = 1u << 7
};

static double clamp_value(double value, double lower, double upper) {
    return value < lower ? lower : (value > upper ? upper : value);
}

static int finite3(const double value[3]) {
    return isfinite(value[0]) && isfinite(value[1]) && isfinite(value[2]);
}

static int valid_params(const MosimSafetyParams *params) {
    int axis;
    if (params == NULL || params->max_tilt_rad <= 0.0 ||
        params->min_thrust < 0.0 || params->max_thrust <= params->min_thrust ||
        params->command_timeout_s <= 0.0 || params->land_speed <= 0.0) return 0;
    for (axis = 0; axis < 3; ++axis) {
        if (params->max_acceleration[axis] <= 0.0 || params->max_speed[axis] <= 0.0 ||
            params->geofence_max[axis] <= params->geofence_min[axis] ||
            params->governor_rate[axis] <= 0.0) return 0;
    }
    return 1;
}

void mosim_safety_default_params(MosimSafetyParams *params) {
    int axis;
    memset(params, 0, sizeof(*params));
    for (axis = 0; axis < 3; ++axis) {
        params->max_acceleration[axis] = axis == 2 ? 4.0 : 5.0;
        params->max_speed[axis] = axis == 2 ? 2.0 : 3.0;
        params->geofence_min[axis] = axis == 2 ? 0.0 : -8.0;
        params->geofence_max[axis] = axis == 2 ? 4.0 : 8.0;
        params->governor_rate[axis] = axis == 2 ? 0.8 : 1.5;
    }
    params->max_tilt_rad = 0.65;
    params->min_thrust = 0.0;
    params->max_thrust = 1.0;
    params->geofence_margin = 0.4;
    params->cbf_alpha = 2.0;
    params->obstacle_min_distance = 0.8;
    params->command_timeout_s = 0.25;
    params->return_altitude = 1.5;
    params->land_speed = 0.3;
}

void mosim_safety_reset(MosimSafetyState *state) {
    memset(state, 0, sizeof(*state));
    state->state = MOSIM_SAFETY_STATE_NOMINAL;
}

static void apply_envelope(const MosimSafetyParams *params,
                           const MosimSafetyInput *input,
                           MosimSafetyOutput *output) {
    int axis;
    for (axis = 0; axis < 3; ++axis) {
        double bounded = clamp_value(input->candidate_acceleration[axis],
                                     -params->max_acceleration[axis],
                                     params->max_acceleration[axis]);
        if (bounded != input->candidate_acceleration[axis]) {
            output->active_constraints |= CONSTRAINT_ACCELERATION;
            output->modified = 1;
        }
        output->safe_acceleration[axis] = bounded;
    }
    output->safe_thrust = clamp_value(input->candidate_thrust,
                                      params->min_thrust, params->max_thrust);
    if (output->safe_thrust != input->candidate_thrust) {
        output->active_constraints |= CONSTRAINT_THRUST;
        output->modified = 1;
    }
    if (fabs(input->candidate_tilt_rad) > params->max_tilt_rad) {
        double scale = params->max_tilt_rad / fabs(input->candidate_tilt_rad);
        output->safe_acceleration[0] *= scale;
        output->safe_acceleration[1] *= scale;
        output->active_constraints |= CONSTRAINT_TILT;
        output->modified = 1;
    }
}

static void apply_geofence(const MosimSafetyParams *params,
                           const MosimSafetyInput *input,
                           MosimSafetyOutput *output) {
    int axis;
    for (axis = 0; axis < 3; ++axis) {
        double lower = params->geofence_min[axis] + params->geofence_margin;
        double upper = params->geofence_max[axis] - params->geofence_margin;
        double bounded = clamp_value(output->safe_reference[axis], lower, upper);
        if (bounded != output->safe_reference[axis] ||
            input->position[axis] <= params->geofence_min[axis] ||
            input->position[axis] >= params->geofence_max[axis]) {
            output->active_constraints |= CONSTRAINT_GEOFENCE;
            output->modified = 1;
        }
        output->safe_reference[axis] = bounded;
    }
}

static void apply_governor(const MosimSafetyParams *params,
                           MosimSafetyState *state,
                           const MosimSafetyInput *input,
                           MosimSafetyOutput *output) {
    int axis;
    for (axis = 0; axis < 3; ++axis) {
        double limit = params->governor_rate[axis] * input->dt;
        double delta = input->reference_position[axis] - state->governed_reference[axis];
        state->governed_reference[axis] += clamp_value(delta, -limit, limit);
        output->safe_reference[axis] = state->governed_reference[axis];
        if (fabs(delta) > limit) output->modified = 1;
    }
}

static void set_state_action(MosimSafetyState *state, MosimSafetyOutput *output,
                             int next_state, int action) {
    state->state = next_state;
    output->state = next_state;
    output->action = action;
    output->modified = action != MOSIM_SAFETY_ACTION_PASS;
}

int mosim_safety_step(int mode, const MosimSafetyParams *params,
                      MosimSafetyState *state, const MosimSafetyInput *input,
                      MosimSafetyOutput *output) {
    int axis;
    if (state == NULL || input == NULL || output == NULL || !valid_params(params) ||
        mode < MOSIM_SAFETY_FILTER || mode > MOSIM_SAFETY_FAILSAFE ||
        !isfinite(input->dt) || input->dt <= 0.0 || !finite3(input->position) ||
        !finite3(input->velocity) || !finite3(input->candidate_acceleration) ||
        !finite3(input->reference_position) || !finite3(input->home_position) ||
        !isfinite(input->candidate_thrust) || !isfinite(input->candidate_tilt_rad)) {
        if (output != NULL) { memset(output, 0, sizeof(*output)); output->status_code = -1; }
        return -1;
    }
    if (input->reset) {
        mosim_safety_reset(state);
        for (axis = 0; axis < 3; ++axis) state->governed_reference[axis] = input->position[axis];
    }
    memset(output, 0, sizeof(*output));
    output->safe_thrust = input->candidate_thrust;
    output->state = state->state;
    for (axis = 0; axis < 3; ++axis) {
        output->safe_acceleration[axis] = input->candidate_acceleration[axis];
        output->safe_reference[axis] = input->reference_position[axis];
    }
    if (!input->enable) { output->status_code = 1; return 0; }

    apply_envelope(params, input, output);
    if (mode == MOSIM_SAFETY_CBF && input->obstacle_distance < params->obstacle_min_distance) {
        double barrier = params->cbf_alpha * (params->obstacle_min_distance - input->obstacle_distance);
        output->safe_acceleration[0] = fmin(output->safe_acceleration[0], -barrier);
        output->active_constraints |= CONSTRAINT_CBF;
        output->modified = 1;
    }
    if (mode == MOSIM_SAFETY_REFERENCE_GOVERNOR) apply_governor(params, state, input, output);
    if (mode == MOSIM_SAFETY_GEOFENCE || mode == MOSIM_SAFETY_CBF) apply_geofence(params, input, output);

    if (mode == MOSIM_SAFETY_EMERGENCY_STOP && input->emergency_request) {
        for (axis = 0; axis < 3; ++axis) output->safe_acceleration[axis] = 0.0;
        output->safe_thrust = 0.0;
        output->active_constraints |= CONSTRAINT_EMERGENCY;
        set_state_action(state, output, MOSIM_SAFETY_STATE_STOP, MOSIM_SAFETY_ACTION_STOP);
    } else if (mode == MOSIM_SAFETY_RETURN_AND_LAND) {
        if (input->land_request || state->state == MOSIM_SAFETY_STATE_LAND) {
            output->safe_reference[0] = input->home_position[0];
            output->safe_reference[1] = input->home_position[1];
            output->safe_reference[2] = fmax(0.0, input->position[2] - params->land_speed * input->dt);
            set_state_action(state, output, MOSIM_SAFETY_STATE_LAND, MOSIM_SAFETY_ACTION_LAND);
        } else if (input->return_request || state->state == MOSIM_SAFETY_STATE_RETURN) {
            output->safe_reference[0] = input->home_position[0];
            output->safe_reference[1] = input->home_position[1];
            output->safe_reference[2] = fmax(input->home_position[2], params->return_altitude);
            set_state_action(state, output, MOSIM_SAFETY_STATE_RETURN, MOSIM_SAFETY_ACTION_RETURN);
        }
    } else if (mode == MOSIM_SAFETY_FAILSAFE) {
        if (input->emergency_request) {
            output->active_constraints |= CONSTRAINT_EMERGENCY;
            output->safe_thrust = 0.0;
            set_state_action(state, output, MOSIM_SAFETY_STATE_STOP, MOSIM_SAFETY_ACTION_STOP);
        } else if (!input->state_valid) {
            output->active_constraints |= CONSTRAINT_INVALID_STATE;
            for (axis = 0; axis < 3; ++axis) output->safe_reference[axis] = input->position[axis];
            set_state_action(state, output, MOSIM_SAFETY_STATE_LAND, MOSIM_SAFETY_ACTION_LAND);
        } else if (!input->offboard_valid || input->command_age_s > params->command_timeout_s) {
            output->active_constraints |= CONSTRAINT_TIMEOUT;
            for (axis = 0; axis < 3; ++axis) output->safe_reference[axis] = input->position[axis];
            set_state_action(state, output, MOSIM_SAFETY_STATE_HOLD, MOSIM_SAFETY_ACTION_HOLD);
        }
    }
    if (output->action == MOSIM_SAFETY_ACTION_PASS && output->modified)
        output->action = MOSIM_SAFETY_ACTION_MODIFY;
    output->status_code = 1;
    return 0;
}
void MosimSafetySupervisorStepScalar(
    double mode_id,
    double dt,
    double position_x,
    double position_y,
    double position_z,
    double velocity_x,
    double velocity_y,
    double velocity_z,
    double candidate_acceleration_x,
    double candidate_acceleration_y,
    double candidate_acceleration_z,
    double candidate_thrust,
    double candidate_tilt_rad,
    double reference_position_x,
    double reference_position_y,
    double reference_position_z,
    double home_position_x,
    double home_position_y,
    double home_position_z,
    double obstacle_distance,
    double command_age_s,
    double state_valid,
    double offboard_valid,
    double emergency_request,
    double return_request,
    double land_request,
    double enable,
    double reset,
    double *safe_acceleration_x,
    double *safe_acceleration_y,
    double *safe_acceleration_z,
    double *safe_thrust,
    double *safe_reference_x,
    double *safe_reference_y,
    double *safe_reference_z,
    double *action,
    double *state,
    double *active_constraints,
    double *modified,
    double *status_code)
{
    static MosimSafetyState states[8];
    MosimSafetyParams params;
    MosimSafetyInput input;
    MosimSafetyOutput output;
    int id = (int)mode_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.position[0] = position_x; input.position[1] = position_y; input.position[2] = position_z;
    input.velocity[0] = velocity_x; input.velocity[1] = velocity_y; input.velocity[2] = velocity_z;
    input.candidate_acceleration[0] = candidate_acceleration_x;
    input.candidate_acceleration[1] = candidate_acceleration_y;
    input.candidate_acceleration[2] = candidate_acceleration_z;
    input.candidate_thrust = candidate_thrust; input.candidate_tilt_rad = candidate_tilt_rad;
    input.reference_position[0] = reference_position_x;
    input.reference_position[1] = reference_position_y;
    input.reference_position[2] = reference_position_z;
    input.home_position[0] = home_position_x; input.home_position[1] = home_position_y;
    input.home_position[2] = home_position_z;
    input.obstacle_distance = obstacle_distance; input.command_age_s = command_age_s;
    input.state_valid = state_valid != 0.0; input.offboard_valid = offboard_valid != 0.0;
    input.emergency_request = emergency_request != 0.0;
    input.return_request = return_request != 0.0; input.land_request = land_request != 0.0;
    input.enable = enable != 0.0; input.reset = reset != 0.0;
    mosim_safety_default_params(&params);
    if (id < 1 || id > 7) id = 0;
    result = mosim_safety_step(id, &params, &states[id], &input, &output);
    if (result != 0) { memset(&output, 0, sizeof(output)); output.status_code = result; }
    *safe_acceleration_x = output.safe_acceleration[0];
    *safe_acceleration_y = output.safe_acceleration[1];
    *safe_acceleration_z = output.safe_acceleration[2];
    *safe_thrust = output.safe_thrust;
    *safe_reference_x = output.safe_reference[0];
    *safe_reference_y = output.safe_reference[1];
    *safe_reference_z = output.safe_reference[2];
    *action = (double)output.action; *state = (double)output.state;
    *active_constraints = (double)output.active_constraints;
    *modified = (double)output.modified; *status_code = (double)output.status_code;
}
");
    end func_CFunction;

    SysplorerEmbeddedCoder.Port.Inport mode_id 
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
    SysplorerEmbeddedCoder.Port.Inport candidate_acceleration_x 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport candidate_acceleration_y 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport candidate_acceleration_z 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport candidate_thrust 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport candidate_tilt_rad 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_position_x 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_position_y 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_position_z 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport home_position_x 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport home_position_y 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport home_position_z 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport obstacle_distance 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport command_age_s 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport state_valid 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport offboard_valid 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport emergency_request 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport return_request 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport land_request 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport enable 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reset 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport safe_acceleration_x 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport safe_acceleration_y 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport safe_acceleration_z 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport safe_thrust 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport safe_reference_x 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport safe_reference_y 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport safe_reference_z 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport action 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport state 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport active_constraints 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport modified 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport status_code 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
  equation
    (safe_acceleration_x, safe_acceleration_y, safe_acceleration_z, safe_thrust, safe_reference_x, safe_reference_y, safe_reference_z, action, state, active_constraints, modified, status_code) = func_CFunction(mode_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, candidate_acceleration_x, candidate_acceleration_y, candidate_acceleration_z, candidate_thrust, candidate_tilt_rad, reference_position_x, reference_position_y, reference_position_z, home_position_x, home_position_y, home_position_z, obstacle_distance, command_age_s, state_valid, offboard_valid, emergency_request, return_request, land_request, enable, reset);
  end CFunction;

equation
  connect(mode_id_in, cFunction.mode_id) annotation(Line(origin={0,0},points={{-250,250},{-50,250}},color={0,0,0}));
  connect(dt_in, cFunction.dt) annotation(Line(origin={0,0},points={{-250,244},{-50,244}},color={0,0,0}));
  connect(position_x_in, cFunction.position_x) annotation(Line(origin={0,0},points={{-250,238},{-50,238}},color={0,0,0}));
  connect(position_y_in, cFunction.position_y) annotation(Line(origin={0,0},points={{-250,232},{-50,232}},color={0,0,0}));
  connect(position_z_in, cFunction.position_z) annotation(Line(origin={0,0},points={{-250,226},{-50,226}},color={0,0,0}));
  connect(velocity_x_in, cFunction.velocity_x) annotation(Line(origin={0,0},points={{-250,220},{-50,220}},color={0,0,0}));
  connect(velocity_y_in, cFunction.velocity_y) annotation(Line(origin={0,0},points={{-250,214},{-50,214}},color={0,0,0}));
  connect(velocity_z_in, cFunction.velocity_z) annotation(Line(origin={0,0},points={{-250,208},{-50,208}},color={0,0,0}));
  connect(candidate_acceleration_x_in, cFunction.candidate_acceleration_x) annotation(Line(origin={0,0},points={{-250,202},{-50,202}},color={0,0,0}));
  connect(candidate_acceleration_y_in, cFunction.candidate_acceleration_y) annotation(Line(origin={0,0},points={{-250,196},{-50,196}},color={0,0,0}));
  connect(candidate_acceleration_z_in, cFunction.candidate_acceleration_z) annotation(Line(origin={0,0},points={{-250,190},{-50,190}},color={0,0,0}));
  connect(candidate_thrust_in, cFunction.candidate_thrust) annotation(Line(origin={0,0},points={{-250,184},{-50,184}},color={0,0,0}));
  connect(candidate_tilt_rad_in, cFunction.candidate_tilt_rad) annotation(Line(origin={0,0},points={{-250,178},{-50,178}},color={0,0,0}));
  connect(reference_position_x_in, cFunction.reference_position_x) annotation(Line(origin={0,0},points={{-250,172},{-50,172}},color={0,0,0}));
  connect(reference_position_y_in, cFunction.reference_position_y) annotation(Line(origin={0,0},points={{-250,166},{-50,166}},color={0,0,0}));
  connect(reference_position_z_in, cFunction.reference_position_z) annotation(Line(origin={0,0},points={{-250,160},{-50,160}},color={0,0,0}));
  connect(home_position_x_in, cFunction.home_position_x) annotation(Line(origin={0,0},points={{-250,154},{-50,154}},color={0,0,0}));
  connect(home_position_y_in, cFunction.home_position_y) annotation(Line(origin={0,0},points={{-250,148},{-50,148}},color={0,0,0}));
  connect(home_position_z_in, cFunction.home_position_z) annotation(Line(origin={0,0},points={{-250,142},{-50,142}},color={0,0,0}));
  connect(obstacle_distance_in, cFunction.obstacle_distance) annotation(Line(origin={0,0},points={{-250,136},{-50,136}},color={0,0,0}));
  connect(command_age_s_in, cFunction.command_age_s) annotation(Line(origin={0,0},points={{-250,130},{-50,130}},color={0,0,0}));
  connect(state_valid_in, cFunction.state_valid) annotation(Line(origin={0,0},points={{-250,124},{-50,124}},color={0,0,0}));
  connect(offboard_valid_in, cFunction.offboard_valid) annotation(Line(origin={0,0},points={{-250,118},{-50,118}},color={0,0,0}));
  connect(emergency_request_in, cFunction.emergency_request) annotation(Line(origin={0,0},points={{-250,112},{-50,112}},color={0,0,0}));
  connect(return_request_in, cFunction.return_request) annotation(Line(origin={0,0},points={{-250,106},{-50,106}},color={0,0,0}));
  connect(land_request_in, cFunction.land_request) annotation(Line(origin={0,0},points={{-250,100},{-50,100}},color={0,0,0}));
  connect(enable_in, cFunction.enable) annotation(Line(origin={0,0},points={{-250,94},{-50,94}},color={0,0,0}));
  connect(reset_in, cFunction.reset) annotation(Line(origin={0,0},points={{-250,88},{-50,88}},color={0,0,0}));
  connect(cFunction.safe_acceleration_x, safe_acceleration_x_out) annotation(Line(origin={0,0},points={{50,160},{250,160}},color={0,0,0}));
  connect(cFunction.safe_acceleration_y, safe_acceleration_y_out) annotation(Line(origin={0,0},points={{50,153},{250,153}},color={0,0,0}));
  connect(cFunction.safe_acceleration_z, safe_acceleration_z_out) annotation(Line(origin={0,0},points={{50,146},{250,146}},color={0,0,0}));
  connect(cFunction.safe_thrust, safe_thrust_out) annotation(Line(origin={0,0},points={{50,139},{250,139}},color={0,0,0}));
  connect(cFunction.safe_reference_x, safe_reference_x_out) annotation(Line(origin={0,0},points={{50,132},{250,132}},color={0,0,0}));
  connect(cFunction.safe_reference_y, safe_reference_y_out) annotation(Line(origin={0,0},points={{50,125},{250,125}},color={0,0,0}));
  connect(cFunction.safe_reference_z, safe_reference_z_out) annotation(Line(origin={0,0},points={{50,118},{250,118}},color={0,0,0}));
  connect(cFunction.action, action_out) annotation(Line(origin={0,0},points={{50,111},{250,111}},color={0,0,0}));
  connect(cFunction.state, state_out) annotation(Line(origin={0,0},points={{50,104},{250,104}},color={0,0,0}));
  connect(cFunction.active_constraints, active_constraints_out) annotation(Line(origin={0,0},points={{50,97},{250,97}},color={0,0,0}));
  connect(cFunction.modified, modified_out) annotation(Line(origin={0,0},points={{50,90},{250,90}},color={0,0,0}));
  connect(cFunction.status_code, status_code_out) annotation(Line(origin={0,0},points={{50,83},{250,83}},color={0,0,0}));
end MoSim_P6_SafetySupervisor_CFunction_Sysblock;