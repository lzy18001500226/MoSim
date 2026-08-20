within MoSimQuadrotorModel.Control.Optimization.NmpcOuter;
model NmpcOuterCore "nmpc_outer graphical control core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{-560,-180},{560,180}},grid={2,2})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.MathOperation.Gain position_prediction(k=1.0) annotation(Placement(transformation(origin={-200,80},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_prediction(k=0.5) annotation(Placement(transformation(origin={-200,0},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay horizon_state(initCond=0.0) annotation(Placement(transformation(origin={-80,40},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum quadratic_optimizer(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={60,40},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain command_increment(k=0.1) annotation(Placement(transformation(origin={190,40},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_command(initCond=0.0) annotation(Placement(transformation(origin={320,40},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation command_limit(lowLimit=-3.5,upLimit=3.5) annotation(Placement(transformation(origin={450,40},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Port.Outport command annotation(Placement(transformation(origin={540,60},extent={{-12,-10},{12,10}})));
  SysplorerEmbeddedCoder.Port.Inport position_error_in 
    annotation (Placement(transformation(origin = {-320, 80}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_error_in 
    annotation (Placement(transformation(origin = {-320, 0}, extent = {{-14, -11}, {14, 11}})));
equation
  connect(position_error_in, position_prediction.u) 
    annotation(Line(points = {{-306, 80}, {-222, 80}}, color = {0, 0, 127}));
  connect(velocity_error_in, velocity_prediction.u) 
    annotation(Line(points = {{-306, 0}, {-222, 0}}, color = {0, 0, 127}));
  connect(position_prediction.y, quadratic_optimizer.u1) annotation(Line(points={{-178,80},{20,80},{20,48},{38,48}},color={0,90,160},thickness=0.75));
  connect(velocity_prediction.y, quadratic_optimizer.u2) annotation(Line(points={{-178,0},{20,0},{20,40},{38,40}},color={0,90,160},thickness=0.75));
  connect(horizon_state.y, quadratic_optimizer.u3) annotation(Line(points={{-58,40},{0,40},{0,32},{38,32}},color={0,90,160},thickness=0.75));
  connect(quadratic_optimizer.y, command_increment.u) annotation(Line(points={{82,40},{168,40}},color={0,90,160},thickness=0.75));
  connect(command_increment.y, previous_command.u1) annotation(Line(points={{212,40},{298,40}},color={0,90,160},thickness=0.75));
  connect(previous_command.y, command_limit.u) annotation(Line(points={{342,40},{428,40}},color={0,90,160},thickness=0.75));
  connect(command_limit.y, command) annotation(Line(points={{472,40},{500,40},{500,60},{528,60}},color={0,90,160},thickness=0.75));
end NmpcOuterCore;
