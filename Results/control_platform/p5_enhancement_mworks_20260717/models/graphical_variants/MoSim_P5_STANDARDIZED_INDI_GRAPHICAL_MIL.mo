model MoSim_P5_STANDARDIZED_INDI_GRAPHICAL_MIL "P5 representative native graphical x-axis structure: standardized_indi"
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
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_increment_error(inputs="+-") annotation(Placement(transformation(origin={-120,-60},extent={{-18,-14},{18,14}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain indi_increment_gain(k=0.12) annotation(Placement(transformation(origin={-20,-60},extent={{-18,-14},{18,14}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation increment_limit(lowLimit=-0.35,upLimit=0.35) annotation(Placement(transformation(origin={80,-60},extent={{-18,-14},{18,14}})));
  SysplorerEmbeddedCoder.MathOperation.Sum indi_command(inputs="++") annotation(Placement(transformation(origin={180,30},extent={{-18,-14},{18,14}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation acceleration_limit(lowLimit=-4.0,upLimit=4.0) annotation(Placement(transformation(origin={290,30},extent={{-18,-14},{18,14}})));
  SysplorerEmbeddedCoder.Port.Outport command_x annotation(Placement(transformation(origin={430,30},extent={{-14,-12},{14,12}})));
  SysplorerEmbeddedCoder.Port.Outport compensation_x annotation(Placement(transformation(origin={430,-60},extent={{-14,-12},{14,12}})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(position_error_x.y,position_feedback.u) annotation(Line(points={{-434,100},{-368,100}},color={0,0,0}));
  connect(velocity_error_x.y,velocity_feedback.u) annotation(Line(points={{-434,40},{-368,40}},color={0,0,0}));
  connect(position_feedback.y,nominal_acceleration.u1) annotation(Line(points={{-332,100},{-286,100},{-286,78},{-268,78}},color={0,0,0}));
  connect(velocity_feedback.y,nominal_acceleration.u2) annotation(Line(points={{-332,40},{-286,40},{-286,62},{-268,62}},color={0,0,0}));
  connect(nominal_acceleration.y,acceleration_increment_error.u1) annotation(Line(points={{-232,70},{-170,70},{-170,-52},{-138,-52}},color={0,0,0}));
  connect(measured_acceleration_x.y,acceleration_increment_error.u2) annotation(Line(points={{-434,-80},{-170,-80},{-170,-68},{-138,-68}},color={0,0,0}));
  connect(acceleration_increment_error.y,indi_increment_gain.u) annotation(Line(points={{-102,-60},{-38,-60}},color={0,0,0}));
  connect(indi_increment_gain.y,increment_limit.u) annotation(Line(points={{-2,-60},{62,-60}},color={0,0,0}));
  connect(nominal_acceleration.y,indi_command.u1) annotation(Line(points={{-232,70},{140,70},{140,38},{162,38}},color={0,0,0}));
  connect(increment_limit.y,indi_command.u2) annotation(Line(points={{98,-60},{140,-60},{140,22},{162,22}},color={0,0,0}));
  connect(indi_command.y,acceleration_limit.u) annotation(Line(points={{198,30},{272,30}},color={0,0,0}));
  connect(acceleration_limit.y,command_x) annotation(Line(points={{308,30},{416,30}},color={0,0,0}));
  connect(increment_limit.y,compensation_x) annotation(Line(points={{98,-60},{416,-60}},color={0,0,0}));
end MoSim_P5_STANDARDIZED_INDI_GRAPHICAL_MIL;