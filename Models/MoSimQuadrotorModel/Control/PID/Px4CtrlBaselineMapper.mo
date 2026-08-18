within MoSimQuadrotorModel.Control.PID;
model Px4CtrlBaselineMapper "Native graphical px4ctrl signed rotor mapper with the OfficialPidRunner 4-in/4-out slot boundary"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(amplitude_1, amplitude_2, amplitude_3, amplitude_4), Right(rotor_command_1, rotor_command_2, rotor_command_3, rotor_command_4)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=50,StoreEventValue=0));
  SysplorerEmbeddedCoder.Port.Inport amplitude_1
    annotation (Placement(transformation(origin = {-560, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport amplitude_2
    annotation (Placement(transformation(origin = {-560, 110}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport amplitude_3
    annotation (Placement(transformation(origin = {-560, 40}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport amplitude_4
    annotation (Placement(transformation(origin = {-560, -30}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_1
    annotation (Placement(transformation(origin = {560, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_2
    annotation (Placement(transformation(origin = {560, 110}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_3
    annotation (Placement(transformation(origin = {560, 40}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_4
    annotation (Placement(transformation(origin = {560, -30}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_1(k=-0.25)
    annotation (Placement(transformation(origin = {-450, 270}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_2(k=0.25)
    annotation (Placement(transformation(origin = {-450, 210}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_3(k=-0.25)
    annotation (Placement(transformation(origin = {-450, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_4(k=0.25)
    annotation (Placement(transformation(origin = {-450, 90}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_sum(inputs="++++",isSaturate=false)
    annotation (Placement(transformation(origin = {-345, 180}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2,u3,u4)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2"),label(text="+",instance="u3"),label(text="+",instance="u4")))));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_1(inputs="++",isSaturate=false)
    annotation (Placement(transformation(origin = {-210, 270}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_1(k=-0.26666666666666666)
    annotation (Placement(transformation(origin = {-210, 238}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_1(inputs="++",isSaturate=false)
    annotation (Placement(transformation(origin = {-65, 270}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_1(k=4.632854053414571)
    annotation (Placement(transformation(origin = {65, 270}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_1(k=64.7923778389665)
    annotation (Placement(transformation(origin = {65, 238}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_1(inputs="++",isSaturate=false)
    annotation (Placement(transformation(origin = {205, 270}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_1(k=1)
    annotation (Placement(transformation(origin = {350, 270}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_2(inputs="+-",isSaturate=false)
    annotation (Placement(transformation(origin = {-210, 180}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_2(k=0.26666666666666666)
    annotation (Placement(transformation(origin = {-210, 148}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_2(inputs="++",isSaturate=false)
    annotation (Placement(transformation(origin = {-65, 180}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_2(k=4.632854053414571)
    annotation (Placement(transformation(origin = {65, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_2(k=64.7923778389665)
    annotation (Placement(transformation(origin = {65, 148}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_2(inputs="++",isSaturate=false)
    annotation (Placement(transformation(origin = {205, 180}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_2(k=-1)
    annotation (Placement(transformation(origin = {350, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_3(inputs="++",isSaturate=false)
    annotation (Placement(transformation(origin = {-210, 90}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_3(k=-0.26666666666666666)
    annotation (Placement(transformation(origin = {-210, 58}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_3(inputs="++",isSaturate=false)
    annotation (Placement(transformation(origin = {-65, 90}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_3(k=4.632854053414571)
    annotation (Placement(transformation(origin = {65, 90}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_3(k=64.7923778389665)
    annotation (Placement(transformation(origin = {65, 58}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_3(inputs="++",isSaturate=false)
    annotation (Placement(transformation(origin = {205, 90}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_3(k=1)
    annotation (Placement(transformation(origin = {350, 90}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_4(inputs="+-",isSaturate=false)
    annotation (Placement(transformation(origin = {-210, 0}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_4(k=0.26666666666666666)
    annotation (Placement(transformation(origin = {-210, -32}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_4(inputs="++",isSaturate=false)
    annotation (Placement(transformation(origin = {-65, 0}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_4(k=4.632854053414571)
    annotation (Placement(transformation(origin = {65, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_4(k=64.7923778389665)
    annotation (Placement(transformation(origin = {65, -32}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_4(inputs="++",isSaturate=false)
    annotation (Placement(transformation(origin = {205, 0}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap)),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_4(k=-1)
    annotation (Placement(transformation(origin = {350, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_ceiling_1(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min,portNumber=2,isSaturate=false)
    annotation (Placement(transformation(origin = {275, 270}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_floor_1(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max,portNumber=2,isSaturate=false)
    annotation (Placement(transformation(origin = {315, 270}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.Sources.Constant command_upper_limit_1(k=110)
    annotation (Placement(transformation(origin = {275, 302}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.Sources.Constant command_lower_limit_1(k=0)
    annotation (Placement(transformation(origin = {315, 238}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_ceiling_2(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min,portNumber=2,isSaturate=false)
    annotation (Placement(transformation(origin = {275, 180}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_floor_2(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max,portNumber=2,isSaturate=false)
    annotation (Placement(transformation(origin = {315, 180}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.Sources.Constant command_upper_limit_2(k=110)
    annotation (Placement(transformation(origin = {275, 212}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.Sources.Constant command_lower_limit_2(k=0)
    annotation (Placement(transformation(origin = {315, 148}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_ceiling_3(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min,portNumber=2,isSaturate=false)
    annotation (Placement(transformation(origin = {275, 90}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_floor_3(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max,portNumber=2,isSaturate=false)
    annotation (Placement(transformation(origin = {315, 90}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.Sources.Constant command_upper_limit_3(k=110)
    annotation (Placement(transformation(origin = {275, 122}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.Sources.Constant command_lower_limit_3(k=0)
    annotation (Placement(transformation(origin = {315, 58}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_ceiling_4(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min,portNumber=2,isSaturate=false)
    annotation (Placement(transformation(origin = {275, 0}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_floor_4(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max,portNumber=2,isSaturate=false)
    annotation (Placement(transformation(origin = {315, 0}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.Sources.Constant command_upper_limit_4(k=110)
    annotation (Placement(transformation(origin = {275, 32}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  SysplorerEmbeddedCoder.Sources.Constant command_lower_limit_4(k=0)
    annotation (Placement(transformation(origin = {315, -32}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(SampleTime(auto=true)=-1)));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(amplitude_1, yaw_projection_1.u)
    annotation(Line(points = {{-543, 180}, {-505, 180}, {-505, 270}, {-467, 270}}, color = {0, 0, 127}));
  connect(yaw_projection_1.y, yaw_sum.u1)
    annotation(Line(points = {{-433, 270}, {-397.5, 270}, {-397.5, 192}, {-362, 192}}, color = {0, 0, 127}));
  connect(amplitude_2, yaw_projection_2.u)
    annotation(Line(points = {{-543, 110}, {-505, 110}, {-505, 210}, {-467, 210}}, color = {0, 0, 127}));
  connect(yaw_projection_2.y, yaw_sum.u2)
    annotation(Line(points = {{-433, 210}, {-397.5, 210}, {-397.5, 184}, {-362, 184}}, color = {0, 0, 127}));
  connect(amplitude_3, yaw_projection_3.u)
    annotation(Line(points = {{-543, 40}, {-505, 40}, {-505, 150}, {-467, 150}}, color = {0, 0, 127}));
  connect(yaw_projection_3.y, yaw_sum.u3)
    annotation(Line(points = {{-433, 150}, {-397.5, 150}, {-397.5, 176}, {-362, 176}}, color = {0, 0, 127}));
  connect(amplitude_4, yaw_projection_4.u)
    annotation(Line(points = {{-543, -30}, {-505, -30}, {-505, 90}, {-467, 90}}, color = {0, 0, 127}));
  connect(yaw_projection_4.y, yaw_sum.u4)
    annotation(Line(points = {{-433, 90}, {-397.5, 90}, {-397.5, 168}, {-362, 168}}, color = {0, 0, 127}));
  connect(amplitude_1, non_yaw_1.u1)
    annotation(Line(points = {{-543, 180}, {-385, 180}, {-385, 282}, {-227, 282}}, color = {0, 0, 127}));
  connect(yaw_sum.y, non_yaw_1.u2)
    annotation(Line(points = {{-328, 180}, {-277.5, 180}, {-277.5, 274}, {-227, 274}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_1.u)
    annotation(Line(points = {{-328, 180}, {-277.5, 180}, {-277.5, 238}, {-227, 238}}, color = {0, 0, 127}));
  connect(non_yaw_1.y, mapped_1.u1)
    annotation(Line(points = {{-193, 270}, {-137.5, 270}, {-137.5, 282}, {-82, 282}}, color = {0, 0, 127}));
  connect(yaw_authority_1.y, mapped_1.u2)
    annotation(Line(points = {{-193, 238}, {-137.5, 238}, {-137.5, 274}, {-82, 274}}, color = {0, 0, 127}));
  connect(mapped_1.y, command_scale_1.u)
    annotation(Line(points = {{-48, 270}, {0, 270}, {48, 270}}, color = {0, 0, 127}));
  connect(command_scale_1.y, hover_plus_1.u1)
    annotation(Line(points = {{82, 270}, {135, 270}, {135, 282}, {188, 282}}, color = {0, 0, 127}));
  connect(hover_1.y, hover_plus_1.u2)
    annotation(Line(points = {{82, 238}, {135, 238}, {135, 274}, {188, 274}}, color = {0, 0, 127}));
  connect(spin_sign_1.y, rotor_command_1)
    annotation(Line(points = {{367, 270}, {455, 270}, {455, 180}, {543, 180}}, color = {0, 0, 127}));
  connect(amplitude_2, non_yaw_2.u1)
    annotation(Line(points = {{-543, 110}, {-385, 110}, {-385, 192}, {-227, 192}}, color = {0, 0, 127}));
  connect(yaw_sum.y, non_yaw_2.u2)
    annotation(Line(points = {{-328, 180}, {-277.5, 180}, {-277.5, 184}, {-227, 184}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_2.u)
    annotation(Line(points = {{-328, 180}, {-277.5, 180}, {-277.5, 148}, {-227, 148}}, color = {0, 0, 127}));
  connect(non_yaw_2.y, mapped_2.u1)
    annotation(Line(points = {{-193, 180}, {-137.5, 180}, {-137.5, 192}, {-82, 192}}, color = {0, 0, 127}));
  connect(yaw_authority_2.y, mapped_2.u2)
    annotation(Line(points = {{-193, 148}, {-137.5, 148}, {-137.5, 184}, {-82, 184}}, color = {0, 0, 127}));
  connect(mapped_2.y, command_scale_2.u)
    annotation(Line(points = {{-48, 180}, {0, 180}, {48, 180}}, color = {0, 0, 127}));
  connect(command_scale_2.y, hover_plus_2.u1)
    annotation(Line(points = {{82, 180}, {135, 180}, {135, 192}, {188, 192}}, color = {0, 0, 127}));
  connect(hover_2.y, hover_plus_2.u2)
    annotation(Line(points = {{82, 148}, {135, 148}, {135, 184}, {188, 184}}, color = {0, 0, 127}));
  connect(spin_sign_2.y, rotor_command_2)
    annotation(Line(points = {{367, 180}, {455, 180}, {455, 110}, {543, 110}}, color = {0, 0, 127}));
  connect(amplitude_3, non_yaw_3.u1)
    annotation(Line(points = {{-543, 40}, {-385, 40}, {-385, 102}, {-227, 102}}, color = {0, 0, 127}));
  connect(yaw_sum.y, non_yaw_3.u2)
    annotation(Line(points = {{-328, 180}, {-277.5, 180}, {-277.5, 94}, {-227, 94}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_3.u)
    annotation(Line(points = {{-328, 180}, {-277.5, 180}, {-277.5, 58}, {-227, 58}}, color = {0, 0, 127}));
  connect(non_yaw_3.y, mapped_3.u1)
    annotation(Line(points = {{-193, 90}, {-137.5, 90}, {-137.5, 102}, {-82, 102}}, color = {0, 0, 127}));
  connect(yaw_authority_3.y, mapped_3.u2)
    annotation(Line(points = {{-193, 58}, {-137.5, 58}, {-137.5, 94}, {-82, 94}}, color = {0, 0, 127}));
  connect(mapped_3.y, command_scale_3.u)
    annotation(Line(points = {{-48, 90}, {0, 90}, {48, 90}}, color = {0, 0, 127}));
  connect(command_scale_3.y, hover_plus_3.u1)
    annotation(Line(points = {{82, 90}, {135, 90}, {135, 102}, {188, 102}}, color = {0, 0, 127}));
  connect(hover_3.y, hover_plus_3.u2)
    annotation(Line(points = {{82, 58}, {135, 58}, {135, 94}, {188, 94}}, color = {0, 0, 127}));
  connect(spin_sign_3.y, rotor_command_3)
    annotation(Line(points = {{367, 90}, {455, 90}, {455, 40}, {543, 40}}, color = {0, 0, 127}));
  connect(amplitude_4, non_yaw_4.u1)
    annotation(Line(points = {{-543, -30}, {-385, -30}, {-385, 12}, {-227, 12}}, color = {0, 0, 127}));
  connect(yaw_sum.y, non_yaw_4.u2)
    annotation(Line(points = {{-328, 180}, {-277.5, 180}, {-277.5, 4}, {-227, 4}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_4.u)
    annotation(Line(points = {{-328, 180}, {-277.5, 180}, {-277.5, -32}, {-227, -32}}, color = {0, 0, 127}));
  connect(non_yaw_4.y, mapped_4.u1)
    annotation(Line(points = {{-193, 0}, {-137.5, 0}, {-137.5, 12}, {-82, 12}}, color = {0, 0, 127}));
  connect(yaw_authority_4.y, mapped_4.u2)
    annotation(Line(points = {{-193, -32}, {-137.5, -32}, {-137.5, 4}, {-82, 4}}, color = {0, 0, 127}));
  connect(mapped_4.y, command_scale_4.u)
    annotation(Line(points = {{-48, 0}, {0, 0}, {48, 0}}, color = {0, 0, 127}));
  connect(command_scale_4.y, hover_plus_4.u1)
    annotation(Line(points = {{82, 0}, {135, 0}, {135, 12}, {188, 12}}, color = {0, 0, 127}));
  connect(hover_4.y, hover_plus_4.u2)
    annotation(Line(points = {{82, -32}, {135, -32}, {135, 4}, {188, 4}}, color = {0, 0, 127}));
  connect(spin_sign_4.y, rotor_command_4)
    annotation(Line(points = {{367, 0}, {455, 0}, {455, -30}, {543, -30}}, color = {0, 0, 127}));
  connect(hover_plus_1.y, command_ceiling_1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_upper_limit_1.y, command_ceiling_1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_ceiling_1.y, command_floor_1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_lower_limit_1.y, command_floor_1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_floor_1.y, spin_sign_1.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(hover_plus_2.y, command_ceiling_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_upper_limit_2.y, command_ceiling_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_ceiling_2.y, command_floor_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_lower_limit_2.y, command_floor_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_floor_2.y, spin_sign_2.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(hover_plus_3.y, command_ceiling_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_upper_limit_3.y, command_ceiling_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_ceiling_3.y, command_floor_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_lower_limit_3.y, command_floor_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_floor_3.y, spin_sign_3.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(hover_plus_4.y, command_ceiling_4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_upper_limit_4.y, command_ceiling_4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_ceiling_4.y, command_floor_4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_lower_limit_4.y, command_floor_4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_floor_4.y, spin_sign_4.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  end Px4CtrlBaselineMapper;