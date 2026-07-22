within MoSimQuadrotorModel.Controllers.GraphicalMIL.ClassicRobust;

model MoSim_WaveA_CFunction_Sysblock
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left(controller_id_in, dt_in, position_x_in, position_y_in, position_z_in, velocity_x_in, velocity_y_in, velocity_z_in, attitude_w_in, attitude_x_in, attitude_y_in, attitude_z_in, reference_position_x_in, reference_position_y_in, reference_position_z_in, reference_velocity_x_in, reference_velocity_y_in, reference_velocity_z_in, reference_acceleration_x_in, reference_acceleration_y_in, reference_acceleration_z_in, reference_attitude_w_in, reference_attitude_x_in, reference_attitude_y_in, reference_attitude_z_in, reference_body_rate_x_in, reference_body_rate_y_in, reference_body_rate_z_in, reference_yaw_in, collective_thrust_n_in, enable_in, reset_in), Right(desired_attitude_w_out, desired_attitude_x_out, desired_attitude_y_out, desired_attitude_z_out, desired_body_rate_x_out, desired_body_rate_y_out, desired_body_rate_z_out, desired_acceleration_x_out, desired_acceleration_y_out, desired_acceleration_z_out, normalized_thrust_out, commanded_collective_thrust_n_out, command_variant_out, saturated_out, status_code_out)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,
"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\g5_mworks_closeout_20260716\\wave_a\\codegen"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{-340,-620},{340,280}},grid={2,2})));

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
  SysplorerEmbeddedCoder.Port.Inport attitude_w_in
    annotation (Placement(transformation(origin={-300,194},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_x_in
    annotation (Placement(transformation(origin={-300,187},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_y_in
    annotation (Placement(transformation(origin={-300,180},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport attitude_z_in
    annotation (Placement(transformation(origin={-300,173},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x_in
    annotation (Placement(transformation(origin={-300,166},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y_in
    annotation (Placement(transformation(origin={-300,159},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z_in
    annotation (Placement(transformation(origin={-300,152},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x_in
    annotation (Placement(transformation(origin={-300,145},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y_in
    annotation (Placement(transformation(origin={-300,138},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z_in
    annotation (Placement(transformation(origin={-300,131},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x_in
    annotation (Placement(transformation(origin={-300,124},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y_in
    annotation (Placement(transformation(origin={-300,117},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z_in
    annotation (Placement(transformation(origin={-300,110},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_attitude_w_in
    annotation (Placement(transformation(origin={-300,103},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_attitude_x_in
    annotation (Placement(transformation(origin={-300,96},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_attitude_y_in
    annotation (Placement(transformation(origin={-300,89},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_attitude_z_in
    annotation (Placement(transformation(origin={-300,82},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_body_rate_x_in
    annotation (Placement(transformation(origin={-300,75},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_body_rate_y_in
    annotation (Placement(transformation(origin={-300,68},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_body_rate_z_in
    annotation (Placement(transformation(origin={-300,61},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_yaw_in
    annotation (Placement(transformation(origin={-300,54},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport collective_thrust_n_in
    annotation (Placement(transformation(origin={-300,47},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_in
    annotation (Placement(transformation(origin={-300,40},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reset_in
    annotation (Placement(transformation(origin={-300,33},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_w_out
    annotation (Placement(transformation(origin={300,160},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_x_out
    annotation (Placement(transformation(origin={300,151},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_y_out
    annotation (Placement(transformation(origin={300,142},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_z_out
    annotation (Placement(transformation(origin={300,133},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_body_rate_x_out
    annotation (Placement(transformation(origin={300,124},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_body_rate_y_out
    annotation (Placement(transformation(origin={300,115},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_body_rate_z_out
    annotation (Placement(transformation(origin={300,106},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out
    annotation (Placement(transformation(origin={300,97},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out
    annotation (Placement(transformation(origin={300,88},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out
    annotation (Placement(transformation(origin={300,79},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out
    annotation (Placement(transformation(origin={300,70},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport commanded_collective_thrust_n_out
    annotation (Placement(transformation(origin={300,61},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport command_variant_out
    annotation (Placement(transformation(origin={300,52},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport saturated_out
    annotation (Placement(transformation(origin={300,43},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport status_code_out
    annotation (Placement(transformation(origin={300,34},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left(controller_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, attitude_w, attitude_x, attitude_y, attitude_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_attitude_w, reference_attitude_x, reference_attitude_y, reference_attitude_z, reference_body_rate_x, reference_body_rate_y, reference_body_rate_z, reference_yaw, collective_thrust_n, enable, reset), Right(desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, desired_body_rate_x, desired_body_rate_y, desired_body_rate_z, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, normalized_thrust, commanded_collective_thrust_n, command_variant, saturated, status_code)),PortLabels(labelType="CustomType",labels(label(text="controller_id",instance="controller_id"),label(text="dt",instance="dt"),label(text="position_x",instance="position_x"),label(text="position_y",instance="position_y"),label(text="position_z",instance="position_z"),label(text="velocity_x",instance="velocity_x"),label(text="velocity_y",instance="velocity_y"),label(text="velocity_z",instance="velocity_z"),label(text="attitude_w",instance="attitude_w"),label(text="attitude_x",instance="attitude_x"),label(text="attitude_y",instance="attitude_y"),label(text="attitude_z",instance="attitude_z"),label(text="reference_position_x",instance="reference_position_x"),label(text="reference_position_y",instance="reference_position_y"),label(text="reference_position_z",instance="reference_position_z"),label(text="reference_velocity_x",instance="reference_velocity_x"),label(text="reference_velocity_y",instance="reference_velocity_y"),label(text="reference_velocity_z",instance="reference_velocity_z"),label(text="reference_acceleration_x",instance="reference_acceleration_x"),label(text=
"reference_acceleration_y",instance="reference_acceleration_y"),label(text="reference_acceleration_z",instance="reference_acceleration_z"),label(text="reference_attitude_w",instance="reference_attitude_w"),label(text="reference_attitude_x",instance="reference_attitude_x"),label(text="reference_attitude_y",instance="reference_attitude_y"),label(text="reference_attitude_z",instance="reference_attitude_z"),label(text="reference_body_rate_x",instance="reference_body_rate_x"),label(text="reference_body_rate_y",instance="reference_body_rate_y"),label(text="reference_body_rate_z",instance="reference_body_rate_z"),label(text="reference_yaw",instance="reference_yaw"),label(text="collective_thrust_n",instance="collective_thrust_n"),label(text="enable",instance="enable"),label(text="reset",instance="reset"),label(text="desired_attitude_w",instance="desired_attitude_w"),label(text="desired_attitude_x",instance="desired_attitude_x"),label(text="desired_attitude_y",instance="desired_attitude_y"),label(text="desired_attitude_z",instance="desired_attitude_z"),label(text="desired_body_rate_x",instance="desired_body_rate_x"),label(text="desired_body_rate_y",instance="desired_body_rate_y"),label(text="desired_body_rate_z",instance="desired_body_rate_z"),label(text="desired_acceleration_x",instance="desired_acceleration_x"),label(text="desired_acceleration_y",instance="desired_acceleration_y"),label(text="desired_acceleration_z",instance="desired_acceleration_z"),label(text="normalized_thrust",instance="normalized_thrust"),label(text="commanded_collective_thrust_n",instance="commanded_collective_thrust_n"),label(text="command_variant",instance="command_variant"),label(text="saturated",instance="saturated"),label(text="status_code",instance="status_code"))),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
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
      input SysplorerEmbeddedCoder.Types.Auto reference_position_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_position_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_position_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_velocity_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_velocity_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_velocity_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_attitude_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_attitude_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_attitude_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_attitude_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_body_rate_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_body_rate_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_body_rate_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reference_yaw annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto collective_thrust_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto enable annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reset annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_w annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_attitude_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_body_rate_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_body_rate_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_body_rate_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto desired_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto normalized_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto commanded_collective_thrust_n annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto command_variant annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto saturated annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto status_code annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
    external "C" MosimWaveAStepScalar(controller_id,dt,position_x,position_y,position_z,velocity_x,velocity_y,velocity_z,attitude_w,attitude_x,attitude_y,attitude_z,reference_position_x,reference_position_y,reference_position_z,reference_velocity_x,reference_velocity_y,reference_velocity_z,reference_acceleration_x,reference_acceleration_y,reference_acceleration_z,reference_attitude_w,reference_attitude_x,reference_attitude_y,reference_attitude_z,reference_body_rate_x,reference_body_rate_y,reference_body_rate_z,reference_yaw,collective_thrust_n,enable,reset,desired_attitude_w,desired_attitude_x,desired_attitude_y,desired_attitude_z,desired_body_rate_x,desired_body_rate_y,desired_body_rate_z,desired_acceleration_x,desired_acceleration_y,desired_acceleration_z,normalized_thrust,commanded_collective_thrust_n,command_variant,saturated,status_code)
      annotation (Include="enum MosimWaveAControllerId {
    MOSIM_WAVE_A_LQR = 1,
    MOSIM_WAVE_A_LQI = 2,
    MOSIM_WAVE_A_SO3 = 3,
    MOSIM_WAVE_A_BACKSTEPPING = 4
};

typedef struct {
    double dt;
    double position[3];
    double velocity[3];
    double attitude_wxyz[4];
    double reference_position[3];
    double reference_velocity[3];
    double reference_acceleration[3];
    double reference_attitude_wxyz[4];
    double reference_body_rate[3];
    double reference_yaw;
    double collective_thrust_n;
    int enable;
    int reset;
} MosimWaveAInput;

typedef struct {
    double kp[3];
    double kv[3];
    double ki[3];
    double integral_limit[3];
    double backstepping_k1[3];
    double backstepping_k2[3];
    double so3_attitude_gain[3];
    double body_rate_limit[3];
    double mass;
    double gravity;
    double hover_percentage;
    double tilt_limit_rad;
} MosimWaveAParams;

typedef struct {
    double integral_position_error[3];
} MosimWaveAState;

typedef struct {
    double desired_attitude_wxyz[4];
    double desired_body_rate[3];
    double desired_acceleration[3];
    double normalized_thrust;
    double collective_thrust_n;
    int command_variant; /* 1=ATTITUDE_THRUST, 2=BODY_RATE_THRUST */
    int saturated;
    int status_code;
} MosimWaveAOutput;

void mosim_wave_a_default_params(MosimWaveAParams *params);
void mosim_wave_a_reset(MosimWaveAState *state);
int mosim_wave_a_step(
    int controller_id,
    const MosimWaveAParams *params,
    MosimWaveAState *state,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output);




#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static void normalize_quaternion(const double in[4], double out[4])
{
    const double n = sqrt(in[0] * in[0] + in[1] * in[1] + in[2] * in[2] + in[3] * in[3]);
    if (n <= 1.0e-12) {
        out[0] = 1.0; out[1] = 0.0; out[2] = 0.0; out[3] = 0.0;
        return;
    }
    out[0] = in[0] / n; out[1] = in[1] / n; out[2] = in[2] / n; out[3] = in[3] / n;
}

static void attitude_from_acceleration(
    const MosimWaveAParams *params,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output)
{
    double roll = -output->desired_acceleration[1] / params->gravity;
    double pitch = output->desired_acceleration[0] / params->gravity;
    const double unclamped_roll = roll;
    const double unclamped_pitch = pitch;
    roll = clamp_value(roll, -params->tilt_limit_rad, params->tilt_limit_rad);
    pitch = clamp_value(pitch, -params->tilt_limit_rad, params->tilt_limit_rad);
    if (fabs(roll - unclamped_roll) > 1.0e-12 || fabs(pitch - unclamped_pitch) > 1.0e-12) {
        output->saturated = 1;
    }

    {
        const double cy = cos(0.5 * input->reference_yaw);
        const double sy = sin(0.5 * input->reference_yaw);
        const double cp = cos(0.5 * pitch);
        const double sp = sin(0.5 * pitch);
        const double cr = cos(0.5 * roll);
        const double sr = sin(0.5 * roll);
        const double q[4] = {
            cy * cp * cr + sy * sp * sr,
            cy * cp * sr - sy * sp * cr,
            sy * cp * sr + cy * sp * cr,
            sy * cp * cr - cy * sp * sr
        };
        normalize_quaternion(q, output->desired_attitude_wxyz);
    }

    output->normalized_thrust = output->desired_acceleration[2] / (params->gravity / params->hover_percentage);
    {
        const double unclamped = output->normalized_thrust;
        output->normalized_thrust = clamp_value(output->normalized_thrust, 0.0, 1.0);
        if (fabs(unclamped - output->normalized_thrust) > 1.0e-12) output->saturated = 1;
    }
    output->collective_thrust_n = output->normalized_thrust * params->mass * params->gravity / params->hover_percentage;
    output->command_variant = 1;
}

static void outer_loop_step(
    int controller_id,
    const MosimWaveAParams *params,
    MosimWaveAState *state,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output)
{
    int i;
    const double dt = input->dt > 0.0 ? input->dt : 0.01;
    for (i = 0; i < 3; ++i) {
        const double ep = input->reference_position[i] - input->position[i];
        const double ev = input->reference_velocity[i] - input->velocity[i];
        double feedback;
        if (controller_id == MOSIM_WAVE_A_LQI) {
            state->integral_position_error[i] = clamp_value(
                state->integral_position_error[i] + ep * dt,
                -params->integral_limit[i],
                params->integral_limit[i]);
        }
        if (controller_id == MOSIM_WAVE_A_BACKSTEPPING) {
            const double virtual_velocity_error = ev + params->backstepping_k1[i] * ep;
            feedback = params->backstepping_k1[i] * ev + params->backstepping_k2[i] * virtual_velocity_error;
        } else {
            feedback = params->kp[i] * ep + params->kv[i] * ev;
            if (controller_id == MOSIM_WAVE_A_LQI) feedback += params->ki[i] * state->integral_position_error[i];
        }
        output->desired_acceleration[i] = input->reference_acceleration[i] + feedback;
    }
    output->desired_acceleration[2] += params->gravity;
    attitude_from_acceleration(params, input, output);
}

static void so3_step(
    const MosimWaveAParams *params,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output)
{
    double q[4];
    double qd[4];
    double qe[4];
    int i;
    normalize_quaternion(input->attitude_wxyz, q);
    normalize_quaternion(input->reference_attitude_wxyz, qd);
    /* qe = conjugate(q) * qd, shortest-arc sign below. */
    qe[0] = q[0] * qd[0] + q[1] * qd[1] + q[2] * qd[2] + q[3] * qd[3];
    qe[1] = q[0] * qd[1] - q[1] * qd[0] - q[2] * qd[3] + q[3] * qd[2];
    qe[2] = q[0] * qd[2] + q[1] * qd[3] - q[2] * qd[0] - q[3] * qd[1];
    qe[3] = q[0] * qd[3] - q[1] * qd[2] + q[2] * qd[1] - q[3] * qd[0];
    {
        const double sign = qe[0] < 0.0 ? -1.0 : 1.0;
        for (i = 0; i < 3; ++i) {
            const double raw = input->reference_body_rate[i] + 2.0 * params->so3_attitude_gain[i] * sign * qe[i + 1];
            output->desired_body_rate[i] = clamp_value(raw, -params->body_rate_limit[i], params->body_rate_limit[i]);
            if (fabs(raw - output->desired_body_rate[i]) > 1.0e-12) output->saturated = 1;
        }
    }
    memcpy(output->desired_attitude_wxyz, qd, sizeof(qd));
    output->collective_thrust_n = input->collective_thrust_n;
    output->normalized_thrust = clamp_value(
        input->collective_thrust_n / (params->mass * params->gravity / params->hover_percentage),
        0.0,
        1.0);
    output->command_variant = 2;
}

void mosim_wave_a_default_params(MosimWaveAParams *params)
{
    const MosimWaveAParams defaults = {
        {1.6, 1.6, 2.2}, {1.8, 1.8, 2.0}, {0.20, 0.20, 0.30}, {0.50, 0.50, 0.35},
        {1.1, 1.1, 1.3}, {1.8, 1.8, 2.0}, {3.0, 3.0, 1.8}, {5.0, 5.0, 3.0},
        0.67, 9.8, 0.37, 0.5235987755982988
    };
    if (params != NULL) *params = defaults;
}

void mosim_wave_a_reset(MosimWaveAState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

int mosim_wave_a_step(
    int controller_id,
    const MosimWaveAParams *params,
    MosimWaveAState *state,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output)
{
    if (params == NULL || state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_wxyz[0] = 1.0;
    if (input->reset) mosim_wave_a_reset(state);
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    if (controller_id == MOSIM_WAVE_A_LQR || controller_id == MOSIM_WAVE_A_LQI ||
        controller_id == MOSIM_WAVE_A_BACKSTEPPING) {
        outer_loop_step(controller_id, params, state, input, output);
        return 0;
    }
    if (controller_id == MOSIM_WAVE_A_SO3) {
        so3_step(params, input, output);
        return 0;
    }
    output->status_code = -2;
    return -2;
}

void MosimWaveAStepScalar(
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
    double reference_position_x,
    double reference_position_y,
    double reference_position_z,
    double reference_velocity_x,
    double reference_velocity_y,
    double reference_velocity_z,
    double reference_acceleration_x,
    double reference_acceleration_y,
    double reference_acceleration_z,
    double reference_attitude_w,
    double reference_attitude_x,
    double reference_attitude_y,
    double reference_attitude_z,
    double reference_body_rate_x,
    double reference_body_rate_y,
    double reference_body_rate_z,
    double reference_yaw,
    double collective_thrust_n,
    double enable,
    double reset,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *desired_body_rate_x,
    double *desired_body_rate_y,
    double *desired_body_rate_z,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *normalized_thrust,
    double *commanded_collective_thrust_n,
    double *command_variant,
    double *saturated,
    double *status_code)
{
    static MosimWaveAState states[5];
    static int initialized[5] = {0};
    MosimWaveAParams params;
    MosimWaveAInput input;
    MosimWaveAOutput output;
    int id = (int)controller_id;
    mosim_wave_a_default_params(&params);
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.position[0] = position_x; input.position[1] = position_y; input.position[2] = position_z;
    input.velocity[0] = velocity_x; input.velocity[1] = velocity_y; input.velocity[2] = velocity_z;
    input.attitude_wxyz[0] = attitude_w; input.attitude_wxyz[1] = attitude_x;
    input.attitude_wxyz[2] = attitude_y; input.attitude_wxyz[3] = attitude_z;
    input.reference_position[0] = reference_position_x; input.reference_position[1] = reference_position_y;
    input.reference_position[2] = reference_position_z;
    input.reference_velocity[0] = reference_velocity_x; input.reference_velocity[1] = reference_velocity_y;
    input.reference_velocity[2] = reference_velocity_z;
    input.reference_acceleration[0] = reference_acceleration_x;
    input.reference_acceleration[1] = reference_acceleration_y;
    input.reference_acceleration[2] = reference_acceleration_z;
    input.reference_attitude_wxyz[0] = reference_attitude_w;
    input.reference_attitude_wxyz[1] = reference_attitude_x;
    input.reference_attitude_wxyz[2] = reference_attitude_y;
    input.reference_attitude_wxyz[3] = reference_attitude_z;
    input.reference_body_rate[0] = reference_body_rate_x;
    input.reference_body_rate[1] = reference_body_rate_y;
    input.reference_body_rate[2] = reference_body_rate_z;
    input.reference_yaw = reference_yaw;
    input.collective_thrust_n = collective_thrust_n;
    input.enable = enable != 0.0; input.reset = reset != 0.0;
    if (id < 1 || id > 4) id = 0;
    if (!initialized[id]) { mosim_wave_a_reset(&states[id]); initialized[id] = 1; }
    mosim_wave_a_step(id, &params, &states[id], &input, &output);
    *desired_attitude_w = output.desired_attitude_wxyz[0];
    *desired_attitude_x = output.desired_attitude_wxyz[1];
    *desired_attitude_y = output.desired_attitude_wxyz[2];
    *desired_attitude_z = output.desired_attitude_wxyz[3];
    *desired_body_rate_x = output.desired_body_rate[0];
    *desired_body_rate_y = output.desired_body_rate[1];
    *desired_body_rate_z = output.desired_body_rate[2];
    *desired_acceleration_x = output.desired_acceleration[0];
    *desired_acceleration_y = output.desired_acceleration[1];
    *desired_acceleration_z = output.desired_acceleration[2];
    *normalized_thrust = output.normalized_thrust;
    *commanded_collective_thrust_n = output.collective_thrust_n;
    *command_variant = (double)output.command_variant;
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
    SysplorerEmbeddedCoder.Port.Inport attitude_w
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport attitude_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport attitude_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport attitude_z
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
    SysplorerEmbeddedCoder.Port.Inport reference_attitude_w
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_attitude_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_attitude_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_attitude_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_body_rate_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_body_rate_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_body_rate_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reference_yaw
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport collective_thrust_n
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
    SysplorerEmbeddedCoder.Port.Outport desired_body_rate_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_body_rate_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_body_rate_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport normalized_thrust
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport commanded_collective_thrust_n
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport command_variant
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport saturated
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport status_code
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
  equation
    (desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, desired_body_rate_x, desired_body_rate_y, desired_body_rate_z, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, normalized_thrust, commanded_collective_thrust_n, command_variant, saturated, status_code) = func_CFunction(controller_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, attitude_w, attitude_x, attitude_y, attitude_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_attitude_w, reference_attitude_x, reference_attitude_y, reference_attitude_z, reference_body_rate_x, reference_body_rate_y, reference_body_rate_z, reference_yaw, collective_thrust_n, enable, reset);
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
  connect(attitude_w_in, cFunction.attitude_w) annotation(Line(origin={0,0},points={{-250,202},{-50,202}},color={0,0,0}));
  connect(attitude_x_in, cFunction.attitude_x) annotation(Line(origin={0,0},points={{-250,196},{-50,196}},color={0,0,0}));
  connect(attitude_y_in, cFunction.attitude_y) annotation(Line(origin={0,0},points={{-250,190},{-50,190}},color={0,0,0}));
  connect(attitude_z_in, cFunction.attitude_z) annotation(Line(origin={0,0},points={{-250,184},{-50,184}},color={0,0,0}));
  connect(reference_position_x_in, cFunction.reference_position_x) annotation(Line(origin={0,0},points={{-250,178},{-50,178}},color={0,0,0}));
  connect(reference_position_y_in, cFunction.reference_position_y) annotation(Line(origin={0,0},points={{-250,172},{-50,172}},color={0,0,0}));
  connect(reference_position_z_in, cFunction.reference_position_z) annotation(Line(origin={0,0},points={{-250,166},{-50,166}},color={0,0,0}));
  connect(reference_velocity_x_in, cFunction.reference_velocity_x) annotation(Line(origin={0,0},points={{-250,160},{-50,160}},color={0,0,0}));
  connect(reference_velocity_y_in, cFunction.reference_velocity_y) annotation(Line(origin={0,0},points={{-250,154},{-50,154}},color={0,0,0}));
  connect(reference_velocity_z_in, cFunction.reference_velocity_z) annotation(Line(origin={0,0},points={{-250,148},{-50,148}},color={0,0,0}));
  connect(reference_acceleration_x_in, cFunction.reference_acceleration_x) annotation(Line(origin={0,0},points={{-250,142},{-50,142}},color={0,0,0}));
  connect(reference_acceleration_y_in, cFunction.reference_acceleration_y) annotation(Line(origin={0,0},points={{-250,136},{-50,136}},color={0,0,0}));
  connect(reference_acceleration_z_in, cFunction.reference_acceleration_z) annotation(Line(origin={0,0},points={{-250,130},{-50,130}},color={0,0,0}));
  connect(reference_attitude_w_in, cFunction.reference_attitude_w) annotation(Line(origin={0,0},points={{-250,124},{-50,124}},color={0,0,0}));
  connect(reference_attitude_x_in, cFunction.reference_attitude_x) annotation(Line(origin={0,0},points={{-250,118},{-50,118}},color={0,0,0}));
  connect(reference_attitude_y_in, cFunction.reference_attitude_y) annotation(Line(origin={0,0},points={{-250,112},{-50,112}},color={0,0,0}));
  connect(reference_attitude_z_in, cFunction.reference_attitude_z) annotation(Line(origin={0,0},points={{-250,106},{-50,106}},color={0,0,0}));
  connect(reference_body_rate_x_in, cFunction.reference_body_rate_x) annotation(Line(origin={0,0},points={{-250,100},{-50,100}},color={0,0,0}));
  connect(reference_body_rate_y_in, cFunction.reference_body_rate_y) annotation(Line(origin={0,0},points={{-250,94},{-50,94}},color={0,0,0}));
  connect(reference_body_rate_z_in, cFunction.reference_body_rate_z) annotation(Line(origin={0,0},points={{-250,88},{-50,88}},color={0,0,0}));
  connect(reference_yaw_in, cFunction.reference_yaw) annotation(Line(origin={0,0},points={{-250,82},{-50,82}},color={0,0,0}));
  connect(collective_thrust_n_in, cFunction.collective_thrust_n) annotation(Line(origin={0,0},points={{-250,76},{-50,76}},color={0,0,0}));
  connect(enable_in, cFunction.enable) annotation(Line(origin={0,0},points={{-250,70},{-50,70}},color={0,0,0}));
  connect(reset_in, cFunction.reset) annotation(Line(origin={0,0},points={{-250,64},{-50,64}},color={0,0,0}));
  connect(cFunction.desired_attitude_w, desired_attitude_w_out) annotation(Line(origin={0,0},points={{50,160},{250,160}},color={0,0,0}));
  connect(cFunction.desired_attitude_x, desired_attitude_x_out) annotation(Line(origin={0,0},points={{50,153},{250,153}},color={0,0,0}));
  connect(cFunction.desired_attitude_y, desired_attitude_y_out) annotation(Line(origin={0,0},points={{50,146},{250,146}},color={0,0,0}));
  connect(cFunction.desired_attitude_z, desired_attitude_z_out) annotation(Line(origin={0,0},points={{50,139},{250,139}},color={0,0,0}));
  connect(cFunction.desired_body_rate_x, desired_body_rate_x_out) annotation(Line(origin={0,0},points={{50,132},{250,132}},color={0,0,0}));
  connect(cFunction.desired_body_rate_y, desired_body_rate_y_out) annotation(Line(origin={0,0},points={{50,125},{250,125}},color={0,0,0}));
  connect(cFunction.desired_body_rate_z, desired_body_rate_z_out) annotation(Line(origin={0,0},points={{50,118},{250,118}},color={0,0,0}));
  connect(cFunction.desired_acceleration_x, desired_acceleration_x_out) annotation(Line(origin={0,0},points={{50,111},{250,111}},color={0,0,0}));
  connect(cFunction.desired_acceleration_y, desired_acceleration_y_out) annotation(Line(origin={0,0},points={{50,104},{250,104}},color={0,0,0}));
  connect(cFunction.desired_acceleration_z, desired_acceleration_z_out) annotation(Line(origin={0,0},points={{50,97},{250,97}},color={0,0,0}));
  connect(cFunction.normalized_thrust, normalized_thrust_out) annotation(Line(origin={0,0},points={{50,90},{250,90}},color={0,0,0}));
  connect(cFunction.commanded_collective_thrust_n, commanded_collective_thrust_n_out) annotation(Line(origin={0,0},points={{50,83},{250,83}},color={0,0,0}));
  connect(cFunction.command_variant, command_variant_out) annotation(Line(origin={0,0},points={{50,76},{250,76}},color={0,0,0}));
  connect(cFunction.saturated, saturated_out) annotation(Line(origin={0,0},points={{50,69},{250,69}},color={0,0,0}));
  connect(cFunction.status_code, status_code_out) annotation(Line(origin={0,0},points={{50,62},{250,62}},color={0,0,0}));
end MoSim_WaveA_CFunction_Sysblock;
