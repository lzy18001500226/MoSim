within MoSimQuadrotorModel.Control.SlidingMode.SmcBoundaryLayer;
model SmcBoundaryLayerCore "smc_boundary_layer graphical control core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{-560,-180},{560,180}},grid={2,2})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.MathOperation.Gain lambda_position(k=2.0) annotation(Placement(transformation(origin={-220,100},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum sliding_surface(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-90,50},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation boundary_layer(lowLimit=-0.4,upLimit=0.4) annotation(Placement(transformation(origin={40,50},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Gain switching_gain(k=0.1) annotation(Placement(transformation(origin={170,50},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={300,0},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation acceleration_limit(lowLimit=-4.0,upLimit=4.0) annotation(Placement(transformation(origin={430,0},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Port.Outport command annotation(Placement(transformation(origin={520,20},extent={{-12,-10},{12,10}})));
  SysplorerEmbeddedCoder.Port.Inport position_error_in 
    annotation (Placement(transformation(origin = {-480, 100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_error_in 
    annotation (Placement(transformation(origin = {-480, 0}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport auxiliary_in 
    annotation (Placement(transformation(origin = {-480, -100}, extent = {{-14, -11}, {14, 11}})));
equation
  connect(lambda_position.y, sliding_surface.u1) annotation(Line(points={{-198,100},{-150,100},{-150,58},{-112,58}},color={0,90,160},thickness=0.75));
  connect(sliding_surface.y, boundary_layer.u) annotation(Line(points={{-68,50},{18,50}},color={0,90,160},thickness=0.75));
  connect(boundary_layer.y, switching_gain.u) annotation(Line(points={{62,50},{148,50}},color={0,90,160},thickness=0.75));
  connect(switching_gain.y, acceleration_sum.u1) annotation(Line(points={{192,50},{240,50},{240,8},{278,8}},color={0,90,160},thickness=0.75));
  connect(acceleration_sum.y, acceleration_limit.u) annotation(Line(points={{322,0},{408,0}},color={0,90,160},thickness=0.75));
  connect(acceleration_limit.y, command) annotation(Line(points={{452,0},{480,0},{480,20},{508,20}},color={0,90,160},thickness=0.75));
  connect(position_error_in, lambda_position.u) 
    annotation(Line(points = {{-466, 100}, {-242, 100}}, color = {0, 0, 127}));
  connect(velocity_error_in, sliding_surface.u2) 
    annotation(Line(points = {{-466, 0}, {-289, 0}, {-289, 50}, {-112, 50}}, color = {0, 0, 127}));
  connect(auxiliary_in, acceleration_sum.u2) 
    annotation(Line(points = {{-466, -100}, {-94, -100}, {-94, 0}, {278, 0}}, color = {0, 0, 127}));
end SmcBoundaryLayerCore;
