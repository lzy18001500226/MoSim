model AWFF_FullController_Sysblock_SIL_Constant "AWFF full controller constant-input SIL reference"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.01,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-260,-220},{220,220}},grid={2,2})));

  SysplorerEmbeddedCoder.Sources.Constant x_error_source(k=0.05) 
    annotation(Placement(transformation(origin={-220,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Constant y_error_source(k=-0.03) 
    annotation(Placement(transformation(origin={-220,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Constant z_error_source(k=0.1) 
    annotation(Placement(transformation(origin={-220,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Constant z_ref_rate_source(k=0.0) 
    annotation(Placement(transformation(origin={-220,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Constant roll_mea_source(k=0.01) 
    annotation(Placement(transformation(origin={-220,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Constant pitch_mea_source(k=-0.01) 
    annotation(Placement(transformation(origin={-220,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Constant yaw_mea_source(k=0.02) 
    annotation(Placement(transformation(origin={-220,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Constant yaw_ref_source(k=0.0) 
    annotation(Placement(transformation(origin={-220,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));

  QuadrotorControllerBlocks.AWFF_FullController_Sysblock controller 
    annotation(Placement(transformation(origin={-20,0},extent={{-55,-55},{55,55}})));

  SysplorerEmbeddedCoder.Port.Outport y 
    annotation(Placement(transformation(origin={160,120},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 
    annotation(Placement(transformation(origin={160,40},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 
    annotation(Placement(transformation(origin={160,-40},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 
    annotation(Placement(transformation(origin={160,-120},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(x_error_source.y, controller.x_error) annotation(Line(origin={-128,164},points={{-80,16},{53,16},{53,15.7}},color={0,0,0}));
  connect(y_error_source.y, controller.y_error) annotation(Line(origin={-128,111},points={{-80,19},{53,19},{53,13.4}},color={0,0,0}));
  connect(z_error_source.y, controller.z_error) annotation(Line(origin={-128,59},points={{-80,21},{53,21},{53,7.0}},color={0,0,0}));
  connect(z_ref_rate_source.y, controller.z_ref_rate) annotation(Line(origin={-128,14},points={{-80,16},{53,16},{53,-0.2}},color={0,0,0}));
  connect(roll_mea_source.y, controller.roll_mea) annotation(Line(origin={-128,-17},points={{-80,-13},{53,-13},{53,3.8}},color={0,0,0}));
  connect(pitch_mea_source.y, controller.pitch_mea) annotation(Line(origin={-128,-65},points={{-80,-15},{53,-15},{53,3.4}},color={0,0,0}));
  connect(yaw_mea_source.y, controller.yaw_mea) annotation(Line(origin={-128,-114},points={{-80,-16},{53,-16},{53,-2.2}},color={0,0,0}));
  connect(yaw_ref_source.y, controller.yaw_ref) annotation(Line(origin={-128,-166},points={{-80,-14},{53,-14},{53,-9.5}},color={0,0,0}));
  connect(controller.y, y) annotation(Line(origin={81,120},points={{-40.5,-4.7},{67,0}},color={0,0,0}));
  connect(controller.y1, y1) annotation(Line(origin={81,40},points={{-40.5,-2.2},{67,0}},color={0,0,0}));
  connect(controller.y2, y2) annotation(Line(origin={81,-40},points={{-40.5,2.2},{67,0}},color={0,0,0}));
  connect(controller.y3, y3) annotation(Line(origin={81,-120},points={{-40.5,4.7},{67,0}},color={0,0,0}));
end AWFF_FullController_Sysblock_SIL_Constant;