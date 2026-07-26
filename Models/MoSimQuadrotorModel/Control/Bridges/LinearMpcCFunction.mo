within MoSimQuadrotorModel.Control.Bridges;
model LinearMpcCFunction
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left(controller_id_in, dt_in, position_x_in, position_y_in, position_z_in, velocity_x_in, velocity_y_in, velocity_z_in, reference_position_x_in, reference_position_y_in, reference_position_z_in, reference_velocity_x_in, reference_velocity_y_in, reference_velocity_z_in, reference_acceleration_x_in, reference_acceleration_y_in, reference_acceleration_z_in, reference_yaw_in, mass_kg_in, gravity_mps2_in, hover_percentage_in, max_tilt_rad_in, min_collective_thrust_n_in, max_collective_thrust_n_in, enable_in, reset_in), Right(desired_attitude_w_out, desired_attitude_x_out, desired_attitude_y_out, desired_attitude_z_out, normalized_thrust_out, collective_thrust_n_out, desired_acceleration_x_out, desired_acceleration_y_out, desired_acceleration_z_out, unconstrained_acceleration_x_out, unconstrained_acceleration_y_out, unconstrained_acceleration_z_out, auxiliary_x_out, auxiliary_y_out, auxiliary_z_out, solver_cost_out, solver_iterations_out, saturated_out, status_code_out)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\g6_formal_champion_promotion_20260725\\linear_mpc\\generated_c"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{-620,-360.00},{620,360.00}},grid={2,2})));

  CFunction cFunction
    annotation (Placement(transformation(origin={0,0}, extent={{-80,-300.00},{80,300.00}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport controller_id_in
    annotation (Placement(transformation(origin={-500,300.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport dt_in
    annotation (Placement(transformation(origin={-500,276.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_x_in
    annotation (Placement(transformation(origin={-500,252.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_y_in
    annotation (Placement(transformation(origin={-500,228.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport position_z_in
    annotation (Placement(transformation(origin={-500,204.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_x_in
    annotation (Placement(transformation(origin={-500,180.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_y_in
    annotation (Placement(transformation(origin={-500,156.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport velocity_z_in
    annotation (Placement(transformation(origin={-500,132.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x_in
    annotation (Placement(transformation(origin={-500,108.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y_in
    annotation (Placement(transformation(origin={-500,84.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z_in
    annotation (Placement(transformation(origin={-500,60.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x_in
    annotation (Placement(transformation(origin={-500,36.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y_in
    annotation (Placement(transformation(origin={-500,12.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z_in
    annotation (Placement(transformation(origin={-500,-12.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x_in
    annotation (Placement(transformation(origin={-500,-36.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y_in
    annotation (Placement(transformation(origin={-500,-60.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z_in
    annotation (Placement(transformation(origin={-500,-84.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reference_yaw_in
    annotation (Placement(transformation(origin={-500,-108.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mass_kg_in
    annotation (Placement(transformation(origin={-500,-132.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport gravity_mps2_in
    annotation (Placement(transformation(origin={-500,-156.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport hover_percentage_in
    annotation (Placement(transformation(origin={-500,-180.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport max_tilt_rad_in
    annotation (Placement(transformation(origin={-500,-204.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport min_collective_thrust_n_in
    annotation (Placement(transformation(origin={-500,-228.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport max_collective_thrust_n_in
    annotation (Placement(transformation(origin={-500,-252.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_in
    annotation (Placement(transformation(origin={-500,-276.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reset_in
    annotation (Placement(transformation(origin={-500,-300.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_w_out
    annotation (Placement(transformation(origin={500,300.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_x_out
    annotation (Placement(transformation(origin={500,266.67},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_y_out
    annotation (Placement(transformation(origin={500,233.33},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_attitude_z_out
    annotation (Placement(transformation(origin={500,200.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out
    annotation (Placement(transformation(origin={500,166.67},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n_out
    annotation (Placement(transformation(origin={500,133.33},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out
    annotation (Placement(transformation(origin={500,100.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out
    annotation (Placement(transformation(origin={500,66.67},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out
    annotation (Placement(transformation(origin={500,33.33},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport unconstrained_acceleration_x_out
    annotation (Placement(transformation(origin={500,0.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport unconstrained_acceleration_y_out
    annotation (Placement(transformation(origin={500,-33.33},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport unconstrained_acceleration_z_out
    annotation (Placement(transformation(origin={500,-66.67},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_x_out
    annotation (Placement(transformation(origin={500,-100.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_y_out
    annotation (Placement(transformation(origin={500,-133.33},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_z_out
    annotation (Placement(transformation(origin={500,-166.67},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport solver_cost_out
    annotation (Placement(transformation(origin={500,-200.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport solver_iterations_out
    annotation (Placement(transformation(origin={500,-233.33},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport saturated_out
    annotation (Placement(transformation(origin={500,-266.67},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport status_code_out
    annotation (Placement(transformation(origin={500,-300.00},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left(controller_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_yaw, mass_kg, gravity_mps2, hover_percentage, max_tilt_rad, min_collective_thrust_n, max_collective_thrust_n, enable, reset), Right(desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, normalized_thrust, collective_thrust_n, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, unconstrained_acceleration_x, unconstrained_acceleration_y, unconstrained_acceleration_z, auxiliary_x, auxiliary_y, auxiliary_z, solver_cost, solver_iterations, saturated, status_code)),PortLabels(labelType="CustomType",labels(label(text="controller_id",instance="controller_id"),label(text="dt",instance="dt"),label(text="position_x",instance="position_x"),label(text="position_y",instance="position_y"),label(text="position_z",instance="position_z"),label(text="velocity_x",instance="velocity_x"),label(text="velocity_y",instance="velocity_y"),label(text="velocity_z",instance="velocity_z"),label(text="reference_position_x",instance="reference_position_x"),label(text="reference_position_y",instance="reference_position_y"),label(text="reference_position_z",instance="reference_position_z"),label(text="reference_velocity_x",instance="reference_velocity_x"),label(text="reference_velocity_y",instance="reference_velocity_y"),label(text="reference_velocity_z",instance="reference_velocity_z"),label(text="reference_acceleration_x",instance="reference_acceleration_x"),label(text="reference_acceleration_y",instance="reference_acceleration_y"),label(text="reference_acceleration_z",instance="reference_acceleration_z"),label(text="reference_yaw",instance="reference_yaw"),label(text="mass_kg",instance="mass_kg"),label(text="gravity_mps2",instance="gravity_mps2"),label(text="hover_percentage",instance="hover_percentage"),label(text="max_tilt_rad",instance="max_tilt_rad"),label(text="min_collective_thrust_n",instance="min_collective_thrust_n"),label(text="max_collective_thrust_n",instance="max_collective_thrust_n"),label(text="enable",instance="enable"),label(text="reset",instance="reset"),label(text="desired_attitude_w",instance="desired_attitude_w"),label(text="desired_attitude_x",instance="desired_attitude_x"),label(text="desired_attitude_y",instance="desired_attitude_y"),label(text="desired_attitude_z",instance="desired_attitude_z"),label(text="normalized_thrust",instance="normalized_thrust"),label(text="collective_thrust_n",instance="collective_thrust_n"),label(text="desired_acceleration_x",instance="desired_acceleration_x"),label(text="desired_acceleration_y",instance="desired_acceleration_y"),label(text="desired_acceleration_z",instance="desired_acceleration_z"),label(text="unconstrained_acceleration_x",instance="unconstrained_acceleration_x"),label(text="unconstrained_acceleration_y",instance="unconstrained_acceleration_y"),label(text="unconstrained_acceleration_z",instance="unconstrained_acceleration_z"),label(text="auxiliary_x",instance="auxiliary_x"),label(text="auxiliary_y",instance="auxiliary_y"),label(text="auxiliary_z",instance="auxiliary_z"),label(text="solver_cost",instance="solver_cost"),label(text="solver_iterations",instance="solver_iterations"),label(text="saturated",instance="saturated"),label(text="status_code",instance="status_code"))),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
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
      output SysplorerEmbeddedCoder.Types.Auto unconstrained_acceleration_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto unconstrained_acceleration_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto unconstrained_acceleration_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto auxiliary_x annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto auxiliary_y annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto auxiliary_z annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto solver_cost annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto solver_iterations annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto saturated annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto status_code annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
    external "C" MosimMpcStepScalar(controller_id,dt,position_x,position_y,position_z,velocity_x,velocity_y,velocity_z,reference_position_x,reference_position_y,reference_position_z,reference_velocity_x,reference_velocity_y,reference_velocity_z,reference_acceleration_x,reference_acceleration_y,reference_acceleration_z,reference_yaw,mass_kg,gravity_mps2,hover_percentage,max_tilt_rad,min_collective_thrust_n,max_collective_thrust_n,enable,reset,desired_attitude_w,desired_attitude_x,desired_attitude_y,desired_attitude_z,normalized_thrust,collective_thrust_n,desired_acceleration_x,desired_acceleration_y,desired_acceleration_z,unconstrained_acceleration_x,unconstrained_acceleration_y,unconstrained_acceleration_z,auxiliary_x,auxiliary_y,auxiliary_z,solver_cost,solver_iterations,saturated,status_code)
      annotation (Include="enum MosimMpcControllerId {
    MOSIM_MPC_LINEAR = 1,
    MOSIM_MPC_ROBUST = 2,
    MOSIM_MPC_ADAPTIVE = 3,
    MOSIM_MPC_TUBE = 4,
    MOSIM_MPC_EXPLICIT_GAIN_SCHEDULED = 5,
    MOSIM_MPC_ILQR = 6,
    MOSIM_MPC_MPPI = 7
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
} MosimMpcInput;

typedef struct {
    double horizon_s;
    double position_weight[3];
    double velocity_weight[3];
    double control_weight[3];
    double acceleration_limit[3];
    double increment_limit[3];
    double robust_bound[3];
    double tube_position_gain[3];
    double tube_velocity_gain[3];
    double adaptive_rate;
    double adaptive_scale_min;
    double adaptive_scale_max;
    double schedule_error_threshold;
    double ilqr_step_size;
    double mppi_temperature;
    double mppi_noise_scale[3];
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimMpcParams;

typedef struct {
    double previous_acceleration[3];
    double adaptive_scale;
    unsigned long step_count;
} MosimMpcState;

typedef struct {
    double desired_acceleration[3];
    double desired_attitude_wxyz[4];
    double normalized_thrust;
    double collective_thrust_n;
    double unconstrained_acceleration[3];
    double auxiliary[3];
    double solver_cost;
    int solver_iterations;
    int saturated;
    int status_code;
} MosimMpcOutput;

void mosim_mpc_default_params(MosimMpcParams *params);
void mosim_mpc_reset(MosimMpcState *state);
int mosim_mpc_step(
    int controller_id,
    const MosimMpcParams *params,
    MosimMpcState *state,
    const MosimMpcInput *input,
    MosimMpcOutput *output);




#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static double norm3(const double value[3])
{
    return sqrt(value[0] * value[0] + value[1] * value[1] + value[2] * value[2]);
}

static int finite3(const double value[3])
{
    return isfinite(value[0]) && isfinite(value[1]) && isfinite(value[2]);
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

static void quaternion_from_rotation(double rotation[3][3], double q[4])
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

static int params_valid(const MosimMpcParams *params)
{
    int axis;
    if (!isfinite(params->horizon_s) || params->horizon_s <= 0.0 || params->horizon_s > 2.0 ||
        !isfinite(params->adaptive_rate) || params->adaptive_rate < 0.0 ||
        !isfinite(params->adaptive_scale_min) || !isfinite(params->adaptive_scale_max) ||
        params->adaptive_scale_min <= 0.0 || params->adaptive_scale_max < params->adaptive_scale_min ||
        !isfinite(params->schedule_error_threshold) || params->schedule_error_threshold <= 0.0 ||
        !isfinite(params->ilqr_step_size) || params->ilqr_step_size <= 0.0 ||
        !isfinite(params->mppi_temperature) || params->mppi_temperature <= 0.0 ||
        !isfinite(params->mass_kg) || params->mass_kg <= 0.0 ||
        !isfinite(params->gravity_mps2) || params->gravity_mps2 <= 0.0 ||
        !isfinite(params->hover_percentage) || params->hover_percentage <= 0.0 || params->hover_percentage > 1.0 ||
        !isfinite(params->max_tilt_rad) || params->max_tilt_rad <= 0.0 ||
        params->max_tilt_rad >= 1.5707963267948966 ||
        !isfinite(params->min_collective_thrust_n) || !isfinite(params->max_collective_thrust_n) ||
        params->min_collective_thrust_n < 0.0 || params->max_collective_thrust_n <= params->min_collective_thrust_n) return 0;
    for (axis = 0; axis < 3; ++axis) {
        if (!isfinite(params->position_weight[axis]) || params->position_weight[axis] <= 0.0 ||
            !isfinite(params->velocity_weight[axis]) || params->velocity_weight[axis] < 0.0 ||
            !isfinite(params->control_weight[axis]) || params->control_weight[axis] <= 0.0 ||
            !isfinite(params->acceleration_limit[axis]) || params->acceleration_limit[axis] <= 0.0 ||
            !isfinite(params->increment_limit[axis]) || params->increment_limit[axis] <= 0.0 ||
            !isfinite(params->robust_bound[axis]) || params->robust_bound[axis] < 0.0 ||
            !isfinite(params->tube_position_gain[axis]) || params->tube_position_gain[axis] < 0.0 ||
            !isfinite(params->tube_velocity_gain[axis]) || params->tube_velocity_gain[axis] < 0.0 ||
            !isfinite(params->mppi_noise_scale[axis]) || params->mppi_noise_scale[axis] < 0.0) return 0;
    }
    return 1;
}

static double stage_cost(double ep, double ev, double acceleration, const MosimMpcParams *params, int axis)
{
    const double horizon = params->horizon_s;
    const double predicted_position_error = ep + horizon * ev - 0.5 * horizon * horizon * acceleration;
    const double predicted_velocity_error = ev - horizon * acceleration;
    return params->position_weight[axis] * predicted_position_error * predicted_position_error +
        params->velocity_weight[axis] * predicted_velocity_error * predicted_velocity_error +
        params->control_weight[axis] * acceleration * acceleration;
}

static double linear_solution(double ep, double ev, double previous, const MosimMpcParams *params, int axis)
{
    const double horizon = params->horizon_s;
    const double horizon_sq = horizon * horizon;
    const double numerator = params->position_weight[axis] * horizon_sq * ep +
        2.0 * params->velocity_weight[axis] * horizon * ev +
        2.0 * params->control_weight[axis] * previous;
    const double denominator = 0.5 * params->position_weight[axis] * horizon_sq * horizon_sq +
        2.0 * params->velocity_weight[axis] * horizon_sq + 2.0 * params->control_weight[axis];
    return numerator / fmax(denominator, 1.0e-9);
}

static double ilqr_solution(double ep, double ev, double initial, const MosimMpcParams *params, int axis)
{
    double acceleration = initial;
    const double h = params->horizon_s;
    const double hessian = 0.5 * params->position_weight[axis] * h * h * h * h +
        2.0 * params->velocity_weight[axis] * h * h + 2.0 * params->control_weight[axis];
    int iteration;
    for (iteration = 0; iteration < 5; ++iteration) {
        const double pe = ep + h * ev - 0.5 * h * h * acceleration;
        const double ve = ev - h * acceleration;
        const double gradient = -params->position_weight[axis] * h * h * pe -
            2.0 * params->velocity_weight[axis] * h * ve +
            2.0 * params->control_weight[axis] * acceleration;
        acceleration -= params->ilqr_step_size * gradient / fmax(hessian, 1.0e-9);
    }
    return acceleration;
}

static double mppi_solution(double ep, double ev, double initial, const MosimMpcParams *params, int axis, double *cost_out)
{
    static const double samples[7] = {-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5};
    double weighted = 0.0;
    double weight_sum = 0.0;
    double min_cost = HUGE_VAL;
    double costs[7];
    double candidates[7];
    int sample;
    for (sample = 0; sample < 7; ++sample) {
        candidates[sample] = initial + samples[sample] * params->mppi_noise_scale[axis];
        costs[sample] = stage_cost(ep, ev, candidates[sample], params, axis);
        if (costs[sample] < min_cost) min_cost = costs[sample];
    }
    for (sample = 0; sample < 7; ++sample) {
        const double weight = exp(-(costs[sample] - min_cost) / params->mppi_temperature);
        weighted += weight * candidates[sample];
        weight_sum += weight;
    }
    if (cost_out != NULL) *cost_out = min_cost;
    return weighted / fmax(weight_sum, 1.0e-12);
}

static int command_from_acceleration(
    const MosimMpcParams *params,
    const MosimMpcInput *input,
    MosimMpcOutput *output)
{
    double force[3];
    double b1_reference[3];
    double b1[3];
    double b2[3];
    double b3[3];
    double rotation[3][3];
    double force_norm;
    double horizontal_acceleration = hypot(output->desired_acceleration[0], output->desired_acceleration[1]);
    double horizontal_limit = fmax(0.0, output->desired_acceleration[2]) * tan(params->max_tilt_rad);
    int axis;
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
    output->collective_thrust_n = clamp_value(force_norm, params->min_collective_thrust_n, params->max_collective_thrust_n);
    if (fabs(output->collective_thrust_n - force_norm) > 1.0e-12) output->saturated = 1;
    output->normalized_thrust = clamp_value(
        output->collective_thrust_n / (params->mass_kg * params->gravity_mps2 / params->hover_percentage), 0.0, 1.0);
    return 0;
}

void mosim_mpc_default_params(MosimMpcParams *params)
{
    const MosimMpcParams defaults = {
        0.25,
        {1.0, 1.0, 1.2}, {0.08, 0.08, 0.10}, {0.002, 0.002, 0.003},
        {4.0, 4.0, 2.5}, {1.2, 1.2, 0.8}, {0.25, 0.25, 0.20},
        {0.35, 0.35, 0.45}, {0.18, 0.18, 0.25},
        0.08, 0.75, 1.25, 0.75, 0.65, 0.30, {0.35, 0.35, 0.25},
        1.0, 9.80665, 0.37, 0.5235987755982988, 0.0, 16.0
    };
    if (params != NULL) *params = defaults;
}

void mosim_mpc_reset(MosimMpcState *state)
{
    if (state == NULL) return;
    memset(state, 0, sizeof(*state));
    state->adaptive_scale = 1.0;
}

int mosim_mpc_step(
    int controller_id,
    const MosimMpcParams *params,
    MosimMpcState *state,
    const MosimMpcInput *input,
    MosimMpcOutput *output)
{
    int axis;
    int rc;
    if (params == NULL || state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_wxyz[0] = 1.0;
    if (input->reset) mosim_mpc_reset(state);
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
    if (controller_id < MOSIM_MPC_LINEAR || controller_id > MOSIM_MPC_MPPI) {
        output->status_code = -2;
        return -2;
    }
    if (controller_id == MOSIM_MPC_ADAPTIVE) {
        double adaptation_signal = 0.0;
        for (axis = 0; axis < 3; ++axis) {
            adaptation_signal += (input->reference_position[axis] - input->position[axis]) *
                (input->reference_velocity[axis] - input->velocity[axis]);
        }
        state->adaptive_scale = clamp_value(
            state->adaptive_scale + params->adaptive_rate * adaptation_signal * input->dt / 3.0,
            params->adaptive_scale_min, params->adaptive_scale_max);
    }
    for (axis = 0; axis < 3; ++axis) {
        const double ep = input->reference_position[axis] - input->position[axis];
        const double ev = input->reference_velocity[axis] - input->velocity[axis];
        double acceleration = linear_solution(ep, ev, state->previous_acceleration[axis], params, axis);
        double limit = params->acceleration_limit[axis];
        if (controller_id == MOSIM_MPC_ROBUST) {
            acceleration += params->robust_bound[axis] * tanh(4.0 * (ep + params->horizon_s * ev));
            output->auxiliary[axis] = params->robust_bound[axis];
        } else if (controller_id == MOSIM_MPC_ADAPTIVE) {
            acceleration *= state->adaptive_scale;
            output->auxiliary[axis] = state->adaptive_scale;
        } else if (controller_id == MOSIM_MPC_TUBE) {
            acceleration += params->tube_position_gain[axis] * ep + params->tube_velocity_gain[axis] * ev;
            limit = fmax(0.1, limit - params->robust_bound[axis]);
            output->auxiliary[axis] = limit;
        } else if (controller_id == MOSIM_MPC_EXPLICIT_GAIN_SCHEDULED) {
            const double schedule = clamp_value(fabs(ep) / params->schedule_error_threshold, 0.0, 1.0);
            acceleration += schedule * (params->tube_position_gain[axis] * ep + params->tube_velocity_gain[axis] * ev);
            output->auxiliary[axis] = schedule;
        } else if (controller_id == MOSIM_MPC_ILQR) {
            acceleration = ilqr_solution(ep, ev, acceleration, params, axis);
            output->solver_iterations = 5;
        } else if (controller_id == MOSIM_MPC_MPPI) {
            double cost = 0.0;
            acceleration = mppi_solution(ep, ev, acceleration, params, axis, &cost);
            output->solver_cost += cost;
            output->solver_iterations = 7;
        }
        acceleration += input->reference_acceleration[axis];
        output->unconstrained_acceleration[axis] = acceleration;
        acceleration = clamp_value(acceleration, -limit, limit);
        acceleration = clamp_value(acceleration,
            state->previous_acceleration[axis] - params->increment_limit[axis],
            state->previous_acceleration[axis] + params->increment_limit[axis]);
        if (fabs(acceleration - output->unconstrained_acceleration[axis]) > 1.0e-12) output->saturated = 1;
        state->previous_acceleration[axis] = acceleration;
        output->desired_acceleration[axis] = acceleration;
        if (controller_id != MOSIM_MPC_MPPI) output->solver_cost += stage_cost(ep, ev, acceleration, params, axis);
    }
    output->desired_acceleration[2] += params->gravity_mps2;
    state->step_count += 1UL;
    rc = command_from_acceleration(params, input, output);
    if (rc != 0) {
        output->status_code = rc;
        return rc;
    }
    return 0;
}
void MosimMpcStepScalar(
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
    double *unconstrained_acceleration_x,
    double *unconstrained_acceleration_y,
    double *unconstrained_acceleration_z,
    double *auxiliary_x,
    double *auxiliary_y,
    double *auxiliary_z,
    double *solver_cost,
    double *solver_iterations,
    double *saturated,
    double *status_code)
{
    static MosimMpcState states[8];
    static unsigned char initialized[8];
    MosimMpcParams params;
    MosimMpcInput input;
    MosimMpcOutput output;
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
    mosim_mpc_default_params(&params);
    params.mass_kg = mass_kg;
    params.gravity_mps2 = gravity_mps2;
    params.hover_percentage = hover_percentage;
    params.max_tilt_rad = max_tilt_rad;
    params.min_collective_thrust_n = min_collective_thrust_n;
    params.max_collective_thrust_n = max_collective_thrust_n;
    if (id < 1 || id > 7) id = 0;
    if (id != 0 && !initialized[id]) {
        mosim_mpc_reset(&states[id]);
        initialized[id] = 1;
    }
    result = mosim_mpc_step(id, &params, &states[id], &input, &output);
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
    *unconstrained_acceleration_x = output.unconstrained_acceleration[0];
    *unconstrained_acceleration_y = output.unconstrained_acceleration[1];
    *unconstrained_acceleration_z = output.unconstrained_acceleration[2];
    *auxiliary_x = output.auxiliary[0];
    *auxiliary_y = output.auxiliary[1];
    *auxiliary_z = output.auxiliary[2];
    *solver_cost = output.solver_cost;
    *solver_iterations = (double)output.solver_iterations;
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
    SysplorerEmbeddedCoder.Port.Outport unconstrained_acceleration_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport unconstrained_acceleration_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport unconstrained_acceleration_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport auxiliary_x
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport auxiliary_y
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport auxiliary_z
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport solver_cost
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport solver_iterations
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport saturated
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport status_code
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
  equation
    (desired_attitude_w, desired_attitude_x, desired_attitude_y, desired_attitude_z, normalized_thrust, collective_thrust_n, desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, unconstrained_acceleration_x, unconstrained_acceleration_y, unconstrained_acceleration_z, auxiliary_x, auxiliary_y, auxiliary_z, solver_cost, solver_iterations, saturated, status_code) = func_CFunction(controller_id, dt, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, reference_yaw, mass_kg, gravity_mps2, hover_percentage, max_tilt_rad, min_collective_thrust_n, max_collective_thrust_n, enable, reset);
  end CFunction;

equation
  connect(controller_id_in, cFunction.controller_id) annotation(Line(points={{-492,300.00},{-80,300.00}},color={0,0,127}));
  connect(dt_in, cFunction.dt) annotation(Line(points={{-492,276.00},{-80,276.00}},color={0,0,127}));
  connect(position_x_in, cFunction.position_x) annotation(Line(points={{-492,252.00},{-80,252.00}},color={0,0,127}));
  connect(position_y_in, cFunction.position_y) annotation(Line(points={{-492,228.00},{-80,228.00}},color={0,0,127}));
  connect(position_z_in, cFunction.position_z) annotation(Line(points={{-492,204.00},{-80,204.00}},color={0,0,127}));
  connect(velocity_x_in, cFunction.velocity_x) annotation(Line(points={{-492,180.00},{-80,180.00}},color={0,0,127}));
  connect(velocity_y_in, cFunction.velocity_y) annotation(Line(points={{-492,156.00},{-80,156.00}},color={0,0,127}));
  connect(velocity_z_in, cFunction.velocity_z) annotation(Line(points={{-492,132.00},{-80,132.00}},color={0,0,127}));
  connect(reference_position_x_in, cFunction.reference_position_x) annotation(Line(points={{-492,108.00},{-80,108.00}},color={0,0,127}));
  connect(reference_position_y_in, cFunction.reference_position_y) annotation(Line(points={{-492,84.00},{-80,84.00}},color={0,0,127}));
  connect(reference_position_z_in, cFunction.reference_position_z) annotation(Line(points={{-492,60.00},{-80,60.00}},color={0,0,127}));
  connect(reference_velocity_x_in, cFunction.reference_velocity_x) annotation(Line(points={{-492,36.00},{-80,36.00}},color={0,0,127}));
  connect(reference_velocity_y_in, cFunction.reference_velocity_y) annotation(Line(points={{-492,12.00},{-80,12.00}},color={0,0,127}));
  connect(reference_velocity_z_in, cFunction.reference_velocity_z) annotation(Line(points={{-492,-12.00},{-80,-12.00}},color={0,0,127}));
  connect(reference_acceleration_x_in, cFunction.reference_acceleration_x) annotation(Line(points={{-492,-36.00},{-80,-36.00}},color={0,0,127}));
  connect(reference_acceleration_y_in, cFunction.reference_acceleration_y) annotation(Line(points={{-492,-60.00},{-80,-60.00}},color={0,0,127}));
  connect(reference_acceleration_z_in, cFunction.reference_acceleration_z) annotation(Line(points={{-492,-84.00},{-80,-84.00}},color={0,0,127}));
  connect(reference_yaw_in, cFunction.reference_yaw) annotation(Line(points={{-492,-108.00},{-80,-108.00}},color={0,0,127}));
  connect(mass_kg_in, cFunction.mass_kg) annotation(Line(points={{-492,-132.00},{-80,-132.00}},color={0,0,127}));
  connect(gravity_mps2_in, cFunction.gravity_mps2) annotation(Line(points={{-492,-156.00},{-80,-156.00}},color={0,0,127}));
  connect(hover_percentage_in, cFunction.hover_percentage) annotation(Line(points={{-492,-180.00},{-80,-180.00}},color={0,0,127}));
  connect(max_tilt_rad_in, cFunction.max_tilt_rad) annotation(Line(points={{-492,-204.00},{-80,-204.00}},color={0,0,127}));
  connect(min_collective_thrust_n_in, cFunction.min_collective_thrust_n) annotation(Line(points={{-492,-228.00},{-80,-228.00}},color={0,0,127}));
  connect(max_collective_thrust_n_in, cFunction.max_collective_thrust_n) annotation(Line(points={{-492,-252.00},{-80,-252.00}},color={0,0,127}));
  connect(enable_in, cFunction.enable) annotation(Line(points={{-492,-276.00},{-80,-276.00}},color={0,0,127}));
  connect(reset_in, cFunction.reset) annotation(Line(points={{-492,-300.00},{-80,-300.00}},color={0,0,127}));
  connect(cFunction.desired_attitude_w, desired_attitude_w_out) annotation(Line(points={{80,300.00},{492,300.00}},color={0,0,127}));
  connect(cFunction.desired_attitude_x, desired_attitude_x_out) annotation(Line(points={{80,266.67},{492,266.67}},color={0,0,127}));
  connect(cFunction.desired_attitude_y, desired_attitude_y_out) annotation(Line(points={{80,233.33},{492,233.33}},color={0,0,127}));
  connect(cFunction.desired_attitude_z, desired_attitude_z_out) annotation(Line(points={{80,200.00},{492,200.00}},color={0,0,127}));
  connect(cFunction.normalized_thrust, normalized_thrust_out) annotation(Line(points={{80,166.67},{492,166.67}},color={0,0,127}));
  connect(cFunction.collective_thrust_n, collective_thrust_n_out) annotation(Line(points={{80,133.33},{492,133.33}},color={0,0,127}));
  connect(cFunction.desired_acceleration_x, desired_acceleration_x_out) annotation(Line(points={{80,100.00},{492,100.00}},color={0,0,127}));
  connect(cFunction.desired_acceleration_y, desired_acceleration_y_out) annotation(Line(points={{80,66.67},{492,66.67}},color={0,0,127}));
  connect(cFunction.desired_acceleration_z, desired_acceleration_z_out) annotation(Line(points={{80,33.33},{492,33.33}},color={0,0,127}));
  connect(cFunction.unconstrained_acceleration_x, unconstrained_acceleration_x_out) annotation(Line(points={{80,0.00},{492,0.00}},color={0,0,127}));
  connect(cFunction.unconstrained_acceleration_y, unconstrained_acceleration_y_out) annotation(Line(points={{80,-33.33},{492,-33.33}},color={0,0,127}));
  connect(cFunction.unconstrained_acceleration_z, unconstrained_acceleration_z_out) annotation(Line(points={{80,-66.67},{492,-66.67}},color={0,0,127}));
  connect(cFunction.auxiliary_x, auxiliary_x_out) annotation(Line(points={{80,-100.00},{492,-100.00}},color={0,0,127}));
  connect(cFunction.auxiliary_y, auxiliary_y_out) annotation(Line(points={{80,-133.33},{492,-133.33}},color={0,0,127}));
  connect(cFunction.auxiliary_z, auxiliary_z_out) annotation(Line(points={{80,-166.67},{492,-166.67}},color={0,0,127}));
  connect(cFunction.solver_cost, solver_cost_out) annotation(Line(points={{80,-200.00},{492,-200.00}},color={0,0,127}));
  connect(cFunction.solver_iterations, solver_iterations_out) annotation(Line(points={{80,-233.33},{492,-233.33}},color={0,0,127}));
  connect(cFunction.saturated, saturated_out) annotation(Line(points={{80,-266.67},{492,-266.67}},color={0,0,127}));
  connect(cFunction.status_code, status_code_out) annotation(Line(points={{80,-300.00},{492,-300.00}},color={0,0,127}));
end LinearMpcCFunction;
