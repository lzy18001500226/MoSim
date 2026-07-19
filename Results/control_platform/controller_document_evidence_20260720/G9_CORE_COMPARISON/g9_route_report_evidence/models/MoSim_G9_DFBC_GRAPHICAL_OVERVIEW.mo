model MoSim_G9_DFBC_GRAPHICAL_OVERVIEW "DFBC readable algorithm topology"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.20,StoreEventValue=0),Diagram(coordinateSystem(extent={{-560,-180},{560,180}},grid={2,2})));
  SysplorerEmbeddedCoder.Sources.Constant position_error_source(k=0.15) annotation(Placement(transformation(origin={-480,100},extent={{-14,-11},{14,11}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_error_source(k=-0.03) annotation(Placement(transformation(origin={-480,0},extent={{-14,-11},{14,11}})));
  SysplorerEmbeddedCoder.Sources.Constant auxiliary_source(k=0.02) annotation(Placement(transformation(origin={-480,-100},extent={{-14,-11},{14,11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain position_feedback(k=1.5) annotation(Placement(transformation(origin={-220,100},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_feedback(k=1.5) annotation(Placement(transformation(origin={-220,0},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nominal_force(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-70,50},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discrete.UnitDelay disturbance_state(initCond=0.0) annotation(Placement(transformation(origin={70,-80},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Gain disturbance_compensation(k=-0.4) annotation(Placement(transformation(origin={200,-80},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum robust_force(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={320,20},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation tilt_force_limit(lowLimit=-4.0,upLimit=4.0) annotation(Placement(transformation(origin={450,20},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Port.Outport command annotation(Placement(transformation(origin={520,20},extent={{-12,-10},{12,10}})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(position_error_source.y, position_feedback.u) annotation(Line(points={{-466,100},{-242,100}},color={0,90,160},thickness=0.75));
  connect(velocity_error_source.y, velocity_feedback.u) annotation(Line(points={{-466,0},{-242,0}},color={0,90,160},thickness=0.75));
  connect(position_feedback.y, nominal_force.u1) annotation(Line(points={{-198,100},{-130,100},{-130,58},{-92,58}},color={0,90,160},thickness=0.75));
  connect(velocity_feedback.y, nominal_force.u2) annotation(Line(points={{-198,0},{-130,0},{-130,42},{-92,42}},color={0,90,160},thickness=0.75));
  connect(auxiliary_source.y, disturbance_state.u1) annotation(Line(points={{-466,-100},{20,-100},{20,-80},{48,-80}},color={0,90,160},thickness=0.75));
  connect(disturbance_state.y, disturbance_compensation.u) annotation(Line(points={{92,-80},{178,-80}},color={0,90,160},thickness=0.75));
  connect(nominal_force.y, robust_force.u1) annotation(Line(points={{-48,50},{260,50},{260,28},{298,28}},color={0,90,160},thickness=0.75));
  connect(disturbance_compensation.y, robust_force.u2) annotation(Line(points={{222,-80},{260,-80},{260,12},{298,12}},color={0,90,160},thickness=0.75));
  connect(robust_force.y, tilt_force_limit.u) annotation(Line(points={{342,20},{428,20}},color={0,90,160},thickness=0.75));
  connect(tilt_force_limit.y, command) annotation(Line(points={{472,20},{508,20}},color={0,90,160},thickness=0.75));
end MoSim_G9_DFBC_GRAPHICAL_OVERVIEW;