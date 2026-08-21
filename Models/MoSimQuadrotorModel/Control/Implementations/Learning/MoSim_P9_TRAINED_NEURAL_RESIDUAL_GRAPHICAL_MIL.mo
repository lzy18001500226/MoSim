within MoSimQuadrotorModel.Control.Implementations.Learning;

model MoSim_P9_TRAINED_NEURAL_RESIDUAL_GRAPHICAL_MIL "P9 trained neural residual learning-control signal chain"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.02),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.02,IntegratorStep=0.02,StartTime=0,StopTime=0.4,StoreEventValue=0),Diagram(coordinateSystem(extent={{-690,-150},{690,150}},grid={2,2})));
  SysplorerEmbeddedCoder.Sources.Constant measured_state(k=0.55) annotation(Placement(transformation(origin={-520,90},extent={{-26,-18},{26,18}})));
  SysplorerEmbeddedCoder.MathOperation.Gain feature_normalization(k=0.8) annotation(Placement(transformation(origin={-370,90},extent={{-26,-18},{26,18}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hidden_layer_inference(k=0.45) annotation(Placement(transformation(origin={-210,90},extent={{-26,-18},{26,18}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation bounded_neural_residual(lowLimit=-0.25,upLimit=0.25) annotation(Placement(transformation(origin={-40,90},extent={{-26,-18},{26,18}})));
  SysplorerEmbeddedCoder.Sources.Constant nominal_acceleration(k=9.81) annotation(Placement(transformation(origin={-210,-70},extent={{-26,-18},{26,18}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nominal_acceleration_merge(inputs="++") annotation(Placement(transformation(origin={140,40},extent={{-26,-18},{26,18}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain attitude_thrust_projection(k=0.34) annotation(Placement(transformation(origin={320,40},extent={{-26,-18},{26,18}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation command_guard(lowLimit=0.0,upLimit=1.0) annotation(Placement(transformation(origin={470,40},extent={{-26,-18},{26,18}})));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust annotation(Placement(transformation(origin={620,90},extent={{-26,-18},{26,18}})));
  SysplorerEmbeddedCoder.Port.Outport learning_action annotation(Placement(transformation(origin={620,10},extent={{-26,-18},{26,18}})));
  SysplorerEmbeddedCoder.Port.Outport fallback_active annotation(Placement(transformation(origin={620,-70},extent={{-26,-18},{26,18}})));
  SysplorerEmbeddedCoder.Sources.Constant fallback_flag(k=0.0) annotation(Placement(transformation(origin={470,-70},extent={{-26,-18},{26,18}})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(measured_state.y,feature_normalization.u) annotation(Line(points={{-494,90},{-396,90}},color={0,0,0}));
  connect(feature_normalization.y,hidden_layer_inference.u) annotation(Line(points={{-344,90},{-236,90}},color={0,0,0}));
  connect(hidden_layer_inference.y,bounded_neural_residual.u) annotation(Line(points={{-184,90},{-66,90}},color={0,0,0}));
  connect(bounded_neural_residual.y,nominal_acceleration_merge.u1) annotation(Line(points={{-14,90},{60,90},{60,48},{114,48}},color={0,0,0}));
  connect(nominal_acceleration.y,nominal_acceleration_merge.u2) annotation(Line(points={{-184,-70},{60,-70},{60,32},{114,32}},color={0,0,0}));
  connect(nominal_acceleration_merge.y,attitude_thrust_projection.u) annotation(Line(points={{166,40},{294,40}},color={0,0,0}));
  connect(attitude_thrust_projection.y,command_guard.u) annotation(Line(points={{346,40},{444,40}},color={0,0,0}));
  connect(command_guard.y,normalized_thrust) annotation(Line(points={{496,40},{550,40},{550,90},{594,90}},color={0,0,0}));
  connect(bounded_neural_residual.y,learning_action) annotation(Line(points={{-14,90},{540,90},{540,10},{594,10}},color={0,0,0}));
  connect(fallback_flag.y,fallback_active) annotation(Line(points={{496,-70},{594,-70}},color={0,0,0}));
end MoSim_P9_TRAINED_NEURAL_RESIDUAL_GRAPHICAL_MIL;
