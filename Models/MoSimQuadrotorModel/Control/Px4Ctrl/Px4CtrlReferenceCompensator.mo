within MoSimQuadrotorModel.Control.Px4Ctrl;
model Px4CtrlReferenceCompensator "Graphical x/y px4ctrl trajectory-reference compensator"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(x_ref, y_ref, vx_ref, vy_ref, ax_ref, ay_ref, vx_mea, vy_mea), Right(x_ref_equivalent, y_ref_equivalent)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1));
  SysplorerEmbeddedCoder.Port.Inport x_ref 
    annotation (Placement(transformation(origin = {-520, 220}, extent = {{-11, -8}, {11, 8}})));
  SysplorerEmbeddedCoder.Port.Inport y_ref 
    annotation (Placement(transformation(origin = {-520, 100}, extent = {{-11, -8}, {11, 8}})));
  SysplorerEmbeddedCoder.Port.Inport vx_ref 
    annotation (Placement(transformation(origin = {-520, 180}, extent = {{-11, -8}, {11, 8}})));
  SysplorerEmbeddedCoder.Port.Inport vy_ref 
    annotation (Placement(transformation(origin = {-520, 60}, extent = {{-11, -8}, {11, 8}})));
  SysplorerEmbeddedCoder.Port.Inport ax_ref 
    annotation (Placement(transformation(origin = {-520, 140}, extent = {{-11, -8}, {11, 8}})));
  SysplorerEmbeddedCoder.Port.Inport ay_ref 
    annotation (Placement(transformation(origin = {-520, 20}, extent = {{-11, -8}, {11, 8}})));
  SysplorerEmbeddedCoder.Port.Inport vx_mea 
    annotation (Placement(transformation(origin = {-520, -20}, extent = {{-11, -8}, {11, 8}})));
  SysplorerEmbeddedCoder.Port.Inport vy_mea 
    annotation (Placement(transformation(origin = {-520, -60}, extent = {{-11, -8}, {11, 8}})));
  SysplorerEmbeddedCoder.Port.Outport x_ref_equivalent 
    annotation (Placement(transformation(origin = {500, 180}, extent = {{-11, -8}, {11, 8}})));
  SysplorerEmbeddedCoder.Port.Outport y_ref_equivalent 
    annotation (Placement(transformation(origin = {500, 40}, extent = {{-11, -8}, {11, 8}})));
  SysplorerEmbeddedCoder.MathOperation.Sum x_velocity_error(inputs="+-",isSaturate=false) 
    annotation (Placement(transformation(origin = {-360, 160}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum y_velocity_error(inputs="+-",isSaturate=false) 
    annotation (Placement(transformation(origin = {-360, 20}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain x_acceleration_scale(k=0.6666666666666666) 
    annotation (Placement(transformation(origin = {-340, 100}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain y_acceleration_scale(k=0.6666666666666666) 
    annotation (Placement(transformation(origin = {-340, -40}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum x_reference_with_velocity(inputs="++",isSaturate=false) 
    annotation (Placement(transformation(origin = {-120, 190}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum y_reference_with_velocity(inputs="++",isSaturate=false) 
    annotation (Placement(transformation(origin = {-120, 50}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum x_reference_equation(inputs="++",isSaturate=false) 
    annotation (Placement(transformation(origin = {180, 180}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum y_reference_equation(inputs="++",isSaturate=false) 
    annotation (Placement(transformation(origin = {180, 40}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(vx_ref, x_velocity_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(vx_mea, x_velocity_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(vy_ref, y_velocity_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(vy_mea, y_velocity_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ax_ref, x_acceleration_scale.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ay_ref, y_acceleration_scale.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(x_ref, x_reference_with_velocity.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(x_velocity_error.y, x_reference_with_velocity.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_ref, y_reference_with_velocity.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_velocity_error.y, y_reference_with_velocity.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(x_reference_with_velocity.y, x_reference_equation.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(x_acceleration_scale.y, x_reference_equation.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_reference_with_velocity.y, y_reference_equation.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_acceleration_scale.y, y_reference_equation.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(x_reference_equation.y, x_ref_equivalent) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_reference_equation.y, y_ref_equivalent) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));

end Px4CtrlReferenceCompensator;