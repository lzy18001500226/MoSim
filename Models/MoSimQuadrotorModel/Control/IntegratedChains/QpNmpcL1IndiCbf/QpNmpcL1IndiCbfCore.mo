within MoSimQuadrotorModel.Control.IntegratedChains.QpNmpcL1IndiCbf;
model QpNmpcL1IndiCbfCore
  "QP NMPC L1 INDI CBF graphical Sysblock core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(
    __MWORKS(version="26.3.0",modelType=Control,PortArrangement(
Left(x_error, y_error, z_error, z_ref_rate, roll_mea, pitch_mea, yaw_mea, yaw_ref),
Right(y, y1, y2, y3, controller_mode, safety_active, event_code, return_ref_x, return_ref_y, return_ref_z)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false, Algorithm=Euler, IntegratorStep=0.01, Interval=0.01, StartTime=0, StopTime=1, StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-380,-280},{380,280}}, grid={2,2})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true, BlockSystem(blockKind=BlockKind.modelWorkspace), version="26.3.0"));
  end ModelWorkspace;

  SysplorerEmbeddedCoder.Port.Inport x_error 
    annotation(Placement(transformation(origin={-360,220}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error 
    annotation(Placement(transformation(origin={-360,170}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error 
    annotation(Placement(transformation(origin={-360,120}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate 
    annotation(Placement(transformation(origin={-360,70}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea 
    annotation(Placement(transformation(origin={-360,10}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea 
    annotation(Placement(transformation(origin={-360,-50}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea 
    annotation(Placement(transformation(origin={-360,-110}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref 
    annotation(Placement(transformation(origin={-360,-170}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y 
    annotation(Placement(transformation(origin={360,225}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 
    annotation(Placement(transformation(origin={360,175}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 
    annotation(Placement(transformation(origin={360,125}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 
    annotation(Placement(transformation(origin={360,75}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport controller_mode 
    annotation(Placement(transformation(origin={360,25}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport safety_active 
    annotation(Placement(transformation(origin={360,-25}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport event_code 
    annotation(Placement(transformation(origin={360,-75}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport return_ref_x 
    annotation(Placement(transformation(origin={360,-125}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport return_ref_y 
    annotation(Placement(transformation(origin={360,-175}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport return_ref_z 
    annotation(Placement(transformation(origin={360,-225}, extent={{-10,-10},{10,10}})),
      __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));

  MoSimQuadrotorModel.Control.Optimization.QpNmpcL1IndiCbf.QpNmpcL1IndiCbfGraphicalController controller 
    annotation(Placement(transformation(origin={0,0}, extent={{-170,-220},{170,220}})), __MWORKS(SECInstance=true));


equation
  connect(x_error, controller.x_error) annotation(Line(points={{-350,220},{-200,220},{-200,180},{-170,180}}, color={0,0,0}));
  connect(y_error, controller.y_error) annotation(Line(points={{-350,170},{-210,170},{-210,130},{-170,130}}, color={0,0,0}));
  connect(z_error, controller.z_error) annotation(Line(points={{-350,120},{-220,120},{-220,80},{-170,80}}, color={0,0,0}));
  connect(z_ref_rate, controller.z_ref_rate) annotation(Line(points={{-350,70},{-230,70},{-230,30},{-170,30}}, color={0,0,0}));
  connect(roll_mea, controller.roll_mea) annotation(Line(points={{-350,10},{-240,10},{-240,-30},{-170,-30}}, color={0,0,0}));
  connect(pitch_mea, controller.pitch_mea) annotation(Line(points={{-350,-50},{-250,-50},{-250,-80},{-170,-80}}, color={0,0,0}));
  connect(yaw_mea, controller.yaw_mea) annotation(Line(points={{-350,-110},{-260,-110},{-260,-130},{-170,-130}}, color={0,0,0}));
  connect(yaw_ref, controller.yaw_ref) annotation(Line(points={{-350,-170},{-270,-170},{-270,-180},{-170,-180}}, color={0,0,0}));
  connect(controller.y, y) annotation(Line(points={{170,190},{240,190},{240,225},{350,225}}, color={0,0,0}));
  connect(controller.y1, y1) annotation(Line(points={{170,145},{250,145},{250,175},{350,175}}, color={0,0,0}));
  connect(controller.y2, y2) annotation(Line(points={{170,100},{260,100},{260,125},{350,125}}, color={0,0,0}));
  connect(controller.y3, y3) annotation(Line(points={{170,55},{270,55},{270,75},{350,75}}, color={0,0,0}));
  connect(controller.controller_mode, controller_mode) annotation(Line(points={{170,0},{280,0},{280,25},{350,25}}, color={0,0,0}));
  connect(controller.safety_active, safety_active) annotation(Line(points={{170,-45},{290,-45},{290,-25},{350,-25}}, color={0,0,0}));
  connect(controller.event_code, event_code) annotation(Line(points={{170,-90},{300,-90},{300,-75},{350,-75}}, color={0,0,0}));
  connect(controller.return_ref_x, return_ref_x) annotation(Line(points={{170,-135},{280,-135},{280,-125},{350,-125}}, color={0,0,0}));
  connect(controller.return_ref_y, return_ref_y) annotation(Line(points={{170,-180},{270,-180},{270,-175},{350,-175}}, color={0,0,0}));
  connect(controller.return_ref_z, return_ref_z) annotation(Line(points={{170,-225},{350,-225}}, color={0,0,0}));
end QpNmpcL1IndiCbfCore;