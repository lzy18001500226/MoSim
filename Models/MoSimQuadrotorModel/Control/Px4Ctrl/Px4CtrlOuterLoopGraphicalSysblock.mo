within MoSimQuadrotorModel.Control.Px4Ctrl;
model Px4CtrlOuterLoopGraphicalSysblock "px4ctrl graphical outer-loop PD and gravity compensation"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(ref_p_x, mea_p_x, ref_v_x, mea_v_x, ref_a_x, ref_p_y, mea_p_y, ref_v_y, mea_v_y, ref_a_y, ref_p_z, mea_p_z, ref_v_z, mea_v_z, ref_a_z), Right(desired_acc_x, desired_acc_y, desired_acc_z)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.02,StoreEventValue=0));
  SysplorerEmbeddedCoder.Port.Inport ref_p_x 
    annotation (Placement(transformation(extent = {{-109,327}, {-83,349}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mea_p_x 
    annotation (Placement(transformation(extent = {{-109,379}, {-83,401}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_v_x 
    annotation (Placement(transformation(extent = {{-109,223}, {-83,245}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mea_v_x 
    annotation (Placement(transformation(extent = {{-109,275}, {-83,297}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_a_x 
    annotation (Placement(transformation(extent = {{-109,-245}, {-83,-223}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum pos_err_x(inputs="+-",isSaturate=false) 
    annotation (Placement(transformation(extent = {{-64,116}, {-32,144}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain kp_x(k=1.5) 
    annotation (Placement(transformation(extent = {{-16,116}, {16,144}})));
  SysplorerEmbeddedCoder.MathOperation.Sum vel_err_x(inputs="+-",isSaturate=false) 
    annotation (Placement(transformation(extent = {{-64,64}, {-32,92}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain kv_x(k=1.5) 
    annotation (Placement(transformation(extent = {{-16,64}, {16,92}})));
  SysplorerEmbeddedCoder.MathOperation.Sum acc_cmd_x(inputs="+++",isSaturate=false) 
    annotation (Placement(transformation(extent = {{30,37}, {66,67}})),__MWORKS(BlockSystem(Instance(u(u1,u2,u3)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2"),label(text="+",instance="u3")))));
  SysplorerEmbeddedCoder.Port.Outport desired_acc_x 
    annotation (Placement(transformation(extent = {{83,41}, {109,63}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_p_y 
    annotation (Placement(transformation(extent = {{-109,119}, {-83,141}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mea_p_y 
    annotation (Placement(transformation(extent = {{-109,171}, {-83,193}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_v_y 
    annotation (Placement(transformation(extent = {{-109,15}, {-83,37}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mea_v_y 
    annotation (Placement(transformation(extent = {{-109,67}, {-83,89}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_a_y 
    annotation (Placement(transformation(extent = {{-109,-297}, {-83,-275}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum pos_err_y(inputs="+-",isSaturate=false) 
    annotation (Placement(transformation(extent = {{-64,12}, {-32,40}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain kp_y(k=1.5) 
    annotation (Placement(transformation(extent = {{-16,12}, {16,40}})));
  SysplorerEmbeddedCoder.MathOperation.Sum vel_err_y(inputs="+-",isSaturate=false) 
    annotation (Placement(transformation(extent = {{-64,-40}, {-32,-12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain kv_y(k=1.5) 
    annotation (Placement(transformation(extent = {{-16,-40}, {16,-12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum acc_cmd_y(inputs="+++",isSaturate=false) 
    annotation (Placement(transformation(extent = {{30,-15}, {66,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2,u3)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2"),label(text="+",instance="u3")))));
  SysplorerEmbeddedCoder.Port.Outport desired_acc_y 
    annotation (Placement(transformation(extent = {{83,-11}, {109,11}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_p_z 
    annotation (Placement(transformation(extent = {{-109,-89}, {-83,-67}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mea_p_z 
    annotation (Placement(transformation(extent = {{-109,-37}, {-83,-15}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_v_z 
    annotation (Placement(transformation(extent = {{-109,-193}, {-83,-171}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mea_v_z 
    annotation (Placement(transformation(extent = {{-109,-141}, {-83,-119}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_a_z 
    annotation (Placement(transformation(origin={-96,-338},
extent={{-13,-11},{13,11}}),
iconTransformation(origin={-101.8,-93.3333},
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum pos_err_z(inputs="+-",isSaturate=false) 
    annotation (Placement(transformation(extent = {{-64,-92}, {-32,-64}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain kp_z(k=1.5) 
    annotation (Placement(transformation(extent = {{-16,-92}, {16,-64}})));
  SysplorerEmbeddedCoder.MathOperation.Sum vel_err_z(inputs="+-",isSaturate=false) 
    annotation (Placement(transformation(extent = {{-64,-144}, {-32,-116}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain kv_z(k=1.5) 
    annotation (Placement(transformation(extent = {{-16,-144}, {16,-116}})));
  SysplorerEmbeddedCoder.MathOperation.Sum acc_cmd_z(inputs="++++",isSaturate=false) 
    annotation (Placement(transformation(extent = {{30,-67}, {66,-37}})),__MWORKS(BlockSystem(Instance(u(u1,u2,u3,u4)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2"),label(text="+",instance="u3"),label(text="+",instance="u4")))));
  SysplorerEmbeddedCoder.Port.Outport desired_acc_z 
    annotation (Placement(transformation(extent = {{83,-63}, {109,-41}})),__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.auto)=-1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Sources.Constant gravity_compensation(k=9.80665) 
    annotation (Placement(transformation(origin={0,-182},
extent={{-16,-14},{16,14}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(ref_p_x, pos_err_x.u1) 
    annotation(Line(origin={0,0},
points={{-80.9804,337.995},{-74,337.995},{-74,137},{-65.8,137}},
color={0,0,127}));
  connect(mea_p_x, pos_err_x.u2) 
    annotation(Line(origin={0,0},
points={{-80.9804,389.995},{-74,389.995},{-74,123},{-65.8,123}},
color={0,0,127}));
  connect(pos_err_x.y, kp_x.u) 
    annotation(Line(points = {{-32,130},{-16,130}}, color = {0,0,127}));
  connect(ref_v_x, vel_err_x.u1) 
    annotation(Line(origin={0,0},
points={{-80.9804,233.995},{-74,233.995},{-74,85},{-65.8,85}},
color={0,0,127}));
  connect(mea_v_x, vel_err_x.u2) 
    annotation(Line(origin={0,0},
points={{-80.9804,285.995},{-74,285.995},{-74,71},{-65.8,71}},
color={0,0,127}));
  connect(vel_err_x.y, kv_x.u) 
    annotation(Line(points = {{-32,78},{-16,78}}, color = {0,0,127}));
  connect(ref_a_x, acc_cmd_x.u1) 
    annotation(Line(origin={0,0},
points={{-80.9804,-234.005},{-24,-234.005},{-24,62},{28.2,62}},
color={0,0,127}));
  connect(kp_x.y, acc_cmd_x.u2) 
    annotation(Line(points = {{16,130},{23,130},{23,52},{30,52}}, color = {0,0,127}));
  connect(kv_x.y, acc_cmd_x.u3) 
    annotation(Line(points = {{16,78},{23,78},{23,52},{30,52}}, color = {0,0,127}));
  connect(acc_cmd_x.y, desired_acc_x) 
    annotation(Line(points = {{66,52},{83,52}}, color = {0,0,127}));
  connect(ref_p_y, pos_err_y.u1) 
    annotation(Line(origin={0,0},
points={{-80.9804,129.995},{-74,129.995},{-74,33},{-65.8,33}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(mea_p_y, pos_err_y.u2) 
    annotation(Line(origin={0,0},
points={{-80.9804,181.995},{-74,181.995},{-74,19},{-65.8,19}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pos_err_y.y, kp_y.u) 
    annotation(Line(points = {{-32,26},{-16,26}}, color = {0,0,127}));
  connect(ref_v_y, vel_err_y.u1) 
    annotation(Line(origin={0,0},
points={{-80.9804,25.9952},{-74,25.9952},{-74,-19},{-65.8,-19}},
color={0,0,127}));
  connect(mea_v_y, vel_err_y.u2) 
    annotation(Line(origin={0,0},
points={{-80.9804,77.9952},{-74,77.9952},{-74,-33},{-65.8,-33}},
color={0,0,127}));
  connect(vel_err_y.y, kv_y.u) 
    annotation(Line(origin={0,0},
points={{-30.2,-26},{-17.8,-26}},
color={0,0,127}));
  connect(ref_a_y, acc_cmd_y.u1) 
    annotation(Line(origin={0,0},
points={{-80.9804,-286.005},{-24,-286.005},{-24,10},{28.2,10}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(kp_y.y, acc_cmd_y.u2) 
    annotation(Line(points = {{16,26},{23,26},{23,0},{30,0}}, color = {0,0,127}));
  connect(kv_y.y, acc_cmd_y.u3) 
    annotation(Line(origin={0,0},
points={{17.8,-26},{23,-26},{23,-10},{28.2,-10}},
color={0,0,127}));
  connect(acc_cmd_y.y, desired_acc_y) 
    annotation(Line(points = {{66,0},{83,0}}, color = {0,0,127}));
  connect(ref_p_z, pos_err_z.u1) 
    annotation(Line(origin={0,0},
points={{-80.9804,-78.0048},{-74,-78.0048},{-74,-71},{-65.8,-71}},
color={0,0,127}));
  connect(mea_p_z, pos_err_z.u2) 
    annotation(Line(origin={0,0},
points={{-80.9804,-26.0048},{-74,-26.0048},{-74,-85},{-65.8,-85}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pos_err_z.y, kp_z.u) 
    annotation(Line(points = {{-32,-78},{-16,-78}}, color = {0,0,127}));
  connect(ref_v_z, vel_err_z.u1) 
    annotation(Line(origin={0,0},
points={{-80.9804,-182.005},{-74,-182.005},{-74,-123},{-65.8,-123}},
color={0,0,127}));
  connect(mea_v_z, vel_err_z.u2) 
    annotation(Line(origin={0,0},
points={{-80.9804,-130.005},{-74,-130.005},{-74,-137},{-65.8,-137}},
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(vel_err_z.y, kv_z.u) 
    annotation(Line(points = {{-32,-130},{-16,-130}}, color = {0,0,127}));
  connect(ref_a_z, acc_cmd_z.u1) 
    annotation(Line(origin={0,52},
points={{-80.9804,-390.005},{-24,-390.005},{-24,-286},{24,-286},{24,-92.75},{28.2,-92.75}},
color={0,0,127}));
  connect(kp_z.y, acc_cmd_z.u2) 
    annotation(Line(origin={0,0},
points={{17.8,-78},{24.4,-78},{24.4,-48.25},{28.2,-48.25}},
color={0,0,127}));
  connect(kv_z.y, acc_cmd_z.u3) 
    annotation(Line(origin={0,0},
points={{17.8,-130},{24.4,-130},{24.4,-55.75},{28.2,-55.75}},
color={0,0,127}));
  connect(acc_cmd_z.y, desired_acc_z) 
    annotation(Line(points = {{66,-52},{83,-52}}, color = {0,0,127}));
  connect(gravity_compensation.y, acc_cmd_z.u4) 
    annotation(Line(origin={0,0},
points={{17.8,-182},{24.4,-182},{24.4,-63.25},{28.2,-63.25}},
color={0,0,127}));

end Px4CtrlOuterLoopGraphicalSysblock;