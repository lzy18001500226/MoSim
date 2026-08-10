within MoSimQuadrotorModel.Control.Implementations.Graphical.PID;
model OfficialPidSysblockMapper "Official PID native graphical rotor command mapper"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(amplitude_1, amplitude_2, amplitude_3, amplitude_4), Right(rotor_command_1, rotor_command_2, rotor_command_3, rotor_command_4)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false), graphics={
    Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,100,150}, fillColor={240,255,240}, fillPattern=FillPattern.Solid),
    Text(origin={0,32}, extent={{-90,18},{90,-18}}, textString="Official PID", textColor={0,100,150}),
    Text(origin={0,0}, extent={{-90,18},{90,-18}}, textString="SYSBLOCK MAPPER", textColor={0,100,150}),
    Text(origin={0,-34}, extent={{-90,14},{90,-14}}, textString="4 IN | 4 OUT", textColor={0,100,150})}),experiment(Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=50,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Port.Inport amplitude_1 
    annotation (Placement(transformation(origin = {-520, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport amplitude_2 
    annotation (Placement(transformation(origin = {-520, 110}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport amplitude_3 
    annotation (Placement(transformation(origin = {-520, 40}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport amplitude_4 
    annotation (Placement(transformation(origin = {-520, -30}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_1 
    annotation (Placement(transformation(origin = {520, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_2 
    annotation (Placement(transformation(origin = {520, 110}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_3 
    annotation (Placement(transformation(origin = {520, 40}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_4 
    annotation (Placement(transformation(origin = {520, -30}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_1(k=-0.25) 
    annotation (Placement(transformation(origin = {-430, 285}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_2(k=0.25) 
    annotation (Placement(transformation(origin = {-430, 240}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_3(k=-0.25) 
    annotation (Placement(transformation(origin = {-430, 195}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_4(k=0.25) 
    annotation (Placement(transformation(origin = {-430, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_sum_12(inputs="++") 
    annotation (Placement(transformation(origin = {-300, 305}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_sum_34(inputs="++") 
    annotation (Placement(transformation(origin = {-300, 135}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_sum(inputs="++") 
    annotation (Placement(transformation(origin = {-180, 220}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_component_1(k=-1) 
    annotation (Placement(transformation(origin = {-70, 270}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_1(inputs="+-") 
    annotation (Placement(transformation(origin = {30, 270}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_1(k=-0.26666666666666666) 
    annotation (Placement(transformation(origin = {-70, 230}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_1(inputs="++") 
    annotation (Placement(transformation(origin = {145, 270}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_1(k=4.632854053414571) 
    annotation (Placement(transformation(origin = {235, 270}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_1(k=64.7923778389665) 
    annotation (Placement(transformation(origin = {235, 230}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_1(inputs="++") 
    annotation (Placement(transformation(origin = {335, 270}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_1(k=1) 
    annotation (Placement(transformation(origin = {430, 270}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_component_2(k=1) 
    annotation (Placement(transformation(origin = {-70, 185}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_2(inputs="+-") 
    annotation (Placement(transformation(origin = {30, 185}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_2(k=0.26666666666666666) 
    annotation (Placement(transformation(origin = {-70, 145}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_2(inputs="++") 
    annotation (Placement(transformation(origin = {145, 185}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_2(k=4.632854053414571) 
    annotation (Placement(transformation(origin = {235, 185}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_2(k=64.7923778389665) 
    annotation (Placement(transformation(origin = {235, 145}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_2(inputs="++") 
    annotation (Placement(transformation(origin = {335, 185}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_2(k=-1) 
    annotation (Placement(transformation(origin = {430, 185}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_component_3(k=-1) 
    annotation (Placement(transformation(origin = {-70, 100}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_3(inputs="+-") 
    annotation (Placement(transformation(origin = {30, 100}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_3(k=-0.26666666666666666) 
    annotation (Placement(transformation(origin = {-70, 60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_3(inputs="++") 
    annotation (Placement(transformation(origin = {145, 100}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_3(k=4.632854053414571) 
    annotation (Placement(transformation(origin = {235, 100}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_3(k=64.7923778389665) 
    annotation (Placement(transformation(origin = {235, 60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_3(inputs="++") 
    annotation (Placement(transformation(origin = {335, 100}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_3(k=1) 
    annotation (Placement(transformation(origin = {430, 100}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_component_4(k=1) 
    annotation (Placement(transformation(origin = {-70, 15}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_4(inputs="+-") 
    annotation (Placement(transformation(origin = {30, 15}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_4(k=0.26666666666666666) 
    annotation (Placement(transformation(origin = {-70, -25}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_4(inputs="++") 
    annotation (Placement(transformation(origin = {145, 15}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_4(k=4.632854053414571) 
    annotation (Placement(transformation(origin = {235, 15}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_4(k=64.7923778389665) 
    annotation (Placement(transformation(origin = {235, -25}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_4(inputs="++") 
    annotation (Placement(transformation(origin = {335, 15}, extent = {{-17, -13}, {17, 13}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_4(k=-1) 
    annotation (Placement(transformation(origin = {430, 15}, extent = {{-17, -13}, {17, 13}})));
  equation
  connect(amplitude_1, yaw_projection_1.u) 
    annotation(Line(points = {{-520, 193}, {-520, 232.5}, {-430, 232.5}, {-430, 272}}, color = {0, 0, 127}));
  connect(amplitude_2, yaw_projection_2.u) 
    annotation(Line(points = {{-520, 123}, {-520, 175}, {-430, 175}, {-430, 227}}, color = {0, 0, 127}));
  connect(amplitude_3, yaw_projection_3.u) 
    annotation(Line(points = {{-520, 53}, {-520, 117.5}, {-430, 117.5}, {-430, 182}}, color = {0, 0, 127}));
  connect(amplitude_4, yaw_projection_4.u) 
    annotation(Line(points = {{-520, -17}, {-520, 60}, {-430, 60}, {-430, 137}}, color = {0, 0, 127}));
  connect(yaw_projection_1.y, yaw_sum_12.u1) 
    annotation(Line(points = {{-413, 285}, {-365, 285}, {-365, 305}, {-317, 305}}, color = {0, 0, 127}));
  connect(yaw_projection_2.y, yaw_sum_12.u2) 
    annotation(Line(points = {{-413, 240}, {-365, 240}, {-365, 305}, {-317, 305}}, color = {0, 0, 127}));
  connect(yaw_projection_3.y, yaw_sum_34.u1) 
    annotation(Line(points = {{-413, 195}, {-365, 195}, {-365, 135}, {-317, 135}}, color = {0, 0, 127}));
  connect(yaw_projection_4.y, yaw_sum_34.u2) 
    annotation(Line(points = {{-413, 150}, {-365, 150}, {-365, 135}, {-317, 135}}, color = {0, 0, 127}));
  connect(yaw_sum_12.y, yaw_sum.u1) 
    annotation(Line(points = {{-283, 305}, {-240, 305}, {-240, 220}, {-197, 220}}, color = {0, 0, 127}));
  connect(yaw_sum_34.y, yaw_sum.u2) 
    annotation(Line(points = {{-283, 135}, {-240, 135}, {-240, 220}, {-197, 220}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_component_1.u) 
    annotation(Line(points = {{-163, 220}, {-125, 220}, {-125, 270}, {-87, 270}}, color = {0, 0, 127}));
  connect(amplitude_1, non_yaw_1.u1) 
    annotation(Line(points = {{-503, 180}, {-245, 180}, {-245, 270}, {13, 270}}, color = {0, 0, 127}));
  connect(yaw_component_1.y, non_yaw_1.u2) 
    annotation(Line(points = {{-53, 270}, {13, 270}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_1.u) 
    annotation(Line(points = {{-163, 220}, {-125, 220}, {-125, 230}, {-87, 230}}, color = {0, 0, 127}));
  connect(non_yaw_1.y, mapped_1.u1) 
    annotation(Line(points = {{47, 270}, {128, 270}}, color = {0, 0, 127}));
  connect(yaw_authority_1.y, mapped_1.u2) 
    annotation(Line(points = {{-53, 230}, {37.5, 230}, {37.5, 270}, {128, 270}}, color = {0, 0, 127}));
  connect(mapped_1.y, command_scale_1.u) 
    annotation(Line(points = {{162, 270}, {218, 270}}, color = {0, 0, 127}));
  connect(command_scale_1.y, hover_plus_1.u1) 
    annotation(Line(points = {{252, 270}, {318, 270}}, color = {0, 0, 127}));
  connect(hover_1.y, hover_plus_1.u2) 
    annotation(Line(points = {{252, 230}, {285, 230}, {285, 270}, {318, 270}}, color = {0, 0, 127}));
  connect(hover_plus_1.y, spin_sign_1.u) 
    annotation(Line(points = {{352, 270}, {413, 270}}, color = {0, 0, 127}));
  connect(spin_sign_1.y, rotor_command_1) 
    annotation(Line(points = {{447, 270}, {475, 270}, {475, 180}, {503, 180}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_component_2.u) 
    annotation(Line(points = {{-163, 220}, {-125, 220}, {-125, 185}, {-87, 185}}, color = {0, 0, 127}));
  connect(amplitude_2, non_yaw_2.u1) 
    annotation(Line(points = {{-503, 110}, {-245, 110}, {-245, 185}, {13, 185}}, color = {0, 0, 127}));
  connect(yaw_component_2.y, non_yaw_2.u2) 
    annotation(Line(points = {{-53, 185}, {13, 185}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_2.u) 
    annotation(Line(points = {{-163, 220}, {-125, 220}, {-125, 145}, {-87, 145}}, color = {0, 0, 127}));
  connect(non_yaw_2.y, mapped_2.u1) 
    annotation(Line(points = {{47, 185}, {128, 185}}, color = {0, 0, 127}));
  connect(yaw_authority_2.y, mapped_2.u2) 
    annotation(Line(points = {{-53, 145}, {37.5, 145}, {37.5, 185}, {128, 185}}, color = {0, 0, 127}));
  connect(mapped_2.y, command_scale_2.u) 
    annotation(Line(points = {{162, 185}, {218, 185}}, color = {0, 0, 127}));
  connect(command_scale_2.y, hover_plus_2.u1) 
    annotation(Line(points = {{252, 185}, {318, 185}}, color = {0, 0, 127}));
  connect(hover_2.y, hover_plus_2.u2) 
    annotation(Line(points = {{252, 145}, {285, 145}, {285, 185}, {318, 185}}, color = {0, 0, 127}));
  connect(hover_plus_2.y, spin_sign_2.u) 
    annotation(Line(points = {{352, 185}, {413, 185}}, color = {0, 0, 127}));
  connect(spin_sign_2.y, rotor_command_2) 
    annotation(Line(points = {{447, 185}, {475, 185}, {475, 110}, {503, 110}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_component_3.u) 
    annotation(Line(points = {{-180, 207}, {-180, 160}, {-70, 160}, {-70, 113}}, color = {0, 0, 127}));
  connect(amplitude_3, non_yaw_3.u1) 
    annotation(Line(points = {{-503, 40}, {-245, 40}, {-245, 100}, {13, 100}}, color = {0, 0, 127}));
  connect(yaw_component_3.y, non_yaw_3.u2) 
    annotation(Line(points = {{-53, 100}, {13, 100}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_3.u) 
    annotation(Line(points = {{-180, 207}, {-180, 140}, {-70, 140}, {-70, 73}}, color = {0, 0, 127}));
  connect(non_yaw_3.y, mapped_3.u1) 
    annotation(Line(points = {{47, 100}, {128, 100}}, color = {0, 0, 127}));
  connect(yaw_authority_3.y, mapped_3.u2) 
    annotation(Line(points = {{-53, 60}, {37.5, 60}, {37.5, 100}, {128, 100}}, color = {0, 0, 127}));
  connect(mapped_3.y, command_scale_3.u) 
    annotation(Line(points = {{162, 100}, {218, 100}}, color = {0, 0, 127}));
  connect(command_scale_3.y, hover_plus_3.u1) 
    annotation(Line(points = {{252, 100}, {318, 100}}, color = {0, 0, 127}));
  connect(hover_3.y, hover_plus_3.u2) 
    annotation(Line(points = {{252, 60}, {285, 60}, {285, 100}, {318, 100}}, color = {0, 0, 127}));
  connect(hover_plus_3.y, spin_sign_3.u) 
    annotation(Line(points = {{352, 100}, {413, 100}}, color = {0, 0, 127}));
  connect(spin_sign_3.y, rotor_command_3) 
    annotation(Line(points = {{447, 100}, {475, 100}, {475, 40}, {503, 40}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_component_4.u) 
    annotation(Line(points = {{-180, 207}, {-180, 117.5}, {-70, 117.5}, {-70, 28}}, color = {0, 0, 127}));
  connect(amplitude_4, non_yaw_4.u1) 
    annotation(Line(points = {{-503, -30}, {-245, -30}, {-245, 15}, {13, 15}}, color = {0, 0, 127}));
  connect(yaw_component_4.y, non_yaw_4.u2) 
    annotation(Line(points = {{-53, 15}, {13, 15}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_4.u) 
    annotation(Line(points = {{-180, 207}, {-180, 97.5}, {-70, 97.5}, {-70, -12}}, color = {0, 0, 127}));
  connect(non_yaw_4.y, mapped_4.u1) 
    annotation(Line(points = {{47, 15}, {128, 15}}, color = {0, 0, 127}));
  connect(yaw_authority_4.y, mapped_4.u2) 
    annotation(Line(points = {{-53, -25}, {37.5, -25}, {37.5, 15}, {128, 15}}, color = {0, 0, 127}));
  connect(mapped_4.y, command_scale_4.u) 
    annotation(Line(points = {{162, 15}, {218, 15}}, color = {0, 0, 127}));
  connect(command_scale_4.y, hover_plus_4.u1) 
    annotation(Line(points = {{252, 15}, {318, 15}}, color = {0, 0, 127}));
  connect(hover_4.y, hover_plus_4.u2) 
    annotation(Line(points = {{252, -25}, {285, -25}, {285, 15}, {318, 15}}, color = {0, 0, 127}));
  connect(hover_plus_4.y, spin_sign_4.u) 
    annotation(Line(points = {{352, 15}, {413, 15}}, color = {0, 0, 127}));
  connect(spin_sign_4.y, rotor_command_4) 
    annotation(Line(points = {{447, 15}, {475, 15}, {475, -30}, {503, -30}}, color = {0, 0, 127}));
  end OfficialPidSysblockMapper;