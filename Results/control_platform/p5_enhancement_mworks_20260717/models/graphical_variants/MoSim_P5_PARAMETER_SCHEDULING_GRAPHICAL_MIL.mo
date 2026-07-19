model MoSim_P5_PARAMETER_SCHEDULING_GRAPHICAL_MIL "P5 representative native graphical x-axis structure: parameter_scheduling"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{-520,-220},{520,220}},grid={2,2})));
  SysplorerEmbeddedCoder.Sources.Constant position_error_x(k=0.8) annotation(Placement(transformation(origin={-450,100},extent={{-16,-12},{16,12}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_error_x(k=0.4) annotation(Placement(transformation(origin={-450,40},extent={{-16,-12},{16,12}})));
  SysplorerEmbeddedCoder.Sources.Constant measured_acceleration_x(k=0.1) annotation(Placement(transformation(origin={-450,-80},extent={{-16,-12},{16,12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain position_feedback(k=11.0) annotation(Placement(transformation(origin={-350,100},extent={{-18,-14},{18,14}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_feedback(k=6.5) annotation(Placement(transformation(origin={-350,40},extent={{-18,-14},{18,14}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nominal_acceleration(inputs="++") annotation(Placement(transformation(origin={-250,70},extent={{-18,-14},{18,14}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain error_normalization(k=2.857143) annotation(Placement(transformation(origin={-260,-80},extent={{-18,-14},{18,14}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation blend_limit(lowLimit=0.0,upLimit=1.0) annotation(Placement(transformation(origin={-160,-80},extent={{-18,-14},{18,14}})));
  SysplorerEmbeddedCoder.MathOperation.Gain gain_range(k=0.35) annotation(Placement(transformation(origin={-60,-80},extent={{-18,-14},{18,14}})));
  SysplorerEmbeddedCoder.Sources.Constant base_gain(k=1.0) annotation(Placement(transformation(origin={-60,-140},extent={{-16,-12},{16,12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum effective_gain_scale(inputs="++") annotation(Placement(transformation(origin={40,-100},extent={{-18,-14},{18,14}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain scheduled_feedback(k=1.0) annotation(Placement(transformation(origin={40,70},extent={{-18,-14},{18,14}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation acceleration_limit(lowLimit=-4.0,upLimit=4.0) annotation(Placement(transformation(origin={180,70},extent={{-18,-14},{18,14}})));
  SysplorerEmbeddedCoder.Port.Outport command_x annotation(Placement(transformation(origin={400,70},extent={{-14,-12},{14,12}})));
  SysplorerEmbeddedCoder.Port.Outport gain_scale annotation(Placement(transformation(origin={400,-100},extent={{-14,-12},{14,12}})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(position_error_x.y,position_feedback.u) annotation(Line(points={{-434,100},{-368,100}},color={0,0,0}));
  connect(velocity_error_x.y,velocity_feedback.u) annotation(Line(points={{-434,40},{-368,40}},color={0,0,0}));
  connect(position_feedback.y,nominal_acceleration.u1) annotation(Line(points={{-332,100},{-286,100},{-286,78},{-268,78}},color={0,0,0}));
  connect(velocity_feedback.y,nominal_acceleration.u2) annotation(Line(points={{-332,40},{-286,40},{-286,62},{-268,62}},color={0,0,0}));
  connect(position_error_x.y,error_normalization.u) annotation(Line(points={{-434,100},{-300,100},{-300,-80},{-278,-80}},color={0,0,0}));
  connect(error_normalization.y,blend_limit.u) annotation(Line(points={{-242,-80},{-178,-80}},color={0,0,0}));
  connect(blend_limit.y,gain_range.u) annotation(Line(points={{-142,-80},{-78,-80}},color={0,0,0}));
  connect(gain_range.y,effective_gain_scale.u1) annotation(Line(points={{-42,-80},{0,-80},{0,-92},{22,-92}},color={0,0,0}));
  connect(base_gain.y,effective_gain_scale.u2) annotation(Line(points={{-44,-140},{0,-140},{0,-108},{22,-108}},color={0,0,0}));
  connect(nominal_acceleration.y,scheduled_feedback.u) annotation(Line(points={{-232,70},{22,70}},color={0,0,0}));
  connect(scheduled_feedback.y,acceleration_limit.u) annotation(Line(points={{58,70},{162,70}},color={0,0,0}));
  connect(acceleration_limit.y,command_x) annotation(Line(points={{198,70},{386,70}},color={0,0,0}));
  connect(effective_gain_scale.y,gain_scale) annotation(Line(points={{58,-100},{386,-100}},color={0,0,0}));
end MoSim_P5_PARAMETER_SCHEDULING_GRAPHICAL_MIL;