model MoSim_P8_DISTRIBUTED_MPC_FORMATION_GRAPHICAL_MIL "P8 distributed mpc formation formation signal chain"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.02),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.02,IntegratorStep=0.02,StartTime=0,StopTime=0.4,StoreEventValue=0),Diagram(coordinateSystem(extent={{-570,-150},{570,150}},grid={2,2})));
  SysplorerEmbeddedCoder.Sources.Constant horizon_reference(k=2.0) annotation(Placement(transformation(origin={-500,90},extent={{-24,-18},{24,18}})));
  SysplorerEmbeddedCoder.MathOperation.Gain neighbor_prediction(k=0.75) annotation(Placement(transformation(origin={-350,90},extent={{-24,-18},{24,18}})));
  SysplorerEmbeddedCoder.Sources.Constant measured_group_state(k=0.35) annotation(Placement(transformation(origin={-350,-80},extent={{-24,-18},{24,18}})));
  SysplorerEmbeddedCoder.MathOperation.Sum prediction_error(inputs="+-") annotation(Placement(transformation(origin={-190,40},extent={{-24,-18},{24,18}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain distributed_optimization(k=0.6) annotation(Placement(transformation(origin={-30,40},extent={{-24,-18},{24,18}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation constraint_projection(lowLimit=-1.5,upLimit=1.5) annotation(Placement(transformation(origin={140,40},extent={{-24,-18},{24,18}})));
  SysplorerEmbeddedCoder.MathOperation.Gain three_uav_reference_distribution(k=3.0) annotation(Placement(transformation(origin={320,40},extent={{-24,-18},{24,18}})));
  SysplorerEmbeddedCoder.Port.Outport formation_command annotation(Placement(transformation(origin={520,90},extent={{-24,-18},{24,18}})));
  SysplorerEmbeddedCoder.Port.Outport formation_error annotation(Placement(transformation(origin={520,10},extent={{-24,-18},{24,18}})));
  SysplorerEmbeddedCoder.Port.Outport minimum_pair_distance annotation(Placement(transformation(origin={520,-70},extent={{-24,-18},{24,18}})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(horizon_reference.y,neighbor_prediction.u) annotation(Line(points={{-476,90},{-374,90}},color={0,0,0}));
  connect(neighbor_prediction.y,prediction_error.u1) annotation(Line(points={{-326,90},{-260,90},{-260,48},{-214,48}},color={0,0,0}));
  connect(measured_group_state.y,prediction_error.u2) annotation(Line(points={{-326,-80},{-260,-80},{-260,32},{-214,32}},color={0,0,0}));
  connect(prediction_error.y,distributed_optimization.u) annotation(Line(points={{-166,40},{-54,40}},color={0,0,0}));
  connect(distributed_optimization.y,constraint_projection.u) annotation(Line(points={{-6,40},{116,40}},color={0,0,0}));
  connect(constraint_projection.y,three_uav_reference_distribution.u) annotation(Line(points={{164,40},{296,40}},color={0,0,0}));
  connect(three_uav_reference_distribution.y,formation_command) annotation(Line(points={{344,40},{430,40},{430,90},{496,90}},color={0,0,0}));
  connect(prediction_error.y,formation_error) annotation(Line(points={{-166,40},{430,40},{430,10},{496,10}},color={0,0,0}));
  connect(constraint_projection.y,minimum_pair_distance) annotation(Line(points={{164,40},{400,40},{400,-70},{496,-70}},color={0,0,0}));
end MoSim_P8_DISTRIBUTED_MPC_FORMATION_GRAPHICAL_MIL;