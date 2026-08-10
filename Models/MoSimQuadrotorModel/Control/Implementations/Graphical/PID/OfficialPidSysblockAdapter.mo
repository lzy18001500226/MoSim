within MoSimQuadrotorModel.Control.Implementations.Graphical.PID;
model OfficialPidSysblockAdapter "Official PID native graphical output adapter"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(core_y, core_y1, core_y2, core_y3), Right(amplitude_1, amplitude_2, amplitude_3, amplitude_4)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=50,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Port.Inport core_y 
    annotation (Placement(transformation(origin = {-180, 90}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport core_y1 
    annotation (Placement(transformation(origin = {-180, 30}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport core_y2 
    annotation (Placement(transformation(origin = {-180, -30}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport core_y3 
    annotation (Placement(transformation(origin = {-180, -90}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport amplitude_1 
    annotation (Placement(transformation(origin = {180, 90}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport amplitude_2 
    annotation (Placement(transformation(origin = {180, 30}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport amplitude_3 
    annotation (Placement(transformation(origin = {180, -30}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport amplitude_4 
    annotation (Placement(transformation(origin = {180, -90}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain output_1_sign(k=1) 
    annotation (Placement(transformation(origin = {0, 90}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain output_2_sign(k=-1) 
    annotation (Placement(transformation(origin = {0, 30}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain output_3_sign(k=1) 
    annotation (Placement(transformation(origin = {0, -30}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain output_4_sign(k=-1) 
    annotation (Placement(transformation(origin = {0, -90}, extent = {{-17, -13}, {17, 13}})));
  equation
  connect(core_y, output_1_sign.u) 
    annotation(Line(points = {{-163, 90}, {-17, 90}}, color = {0, 0, 127}));
  connect(output_1_sign.y, amplitude_1) 
    annotation(Line(points = {{17, 90}, {163, 90}}, color = {0, 0, 127}));
  connect(core_y1, output_2_sign.u) 
    annotation(Line(points = {{-163, 30}, {-17, 30}}, color = {0, 0, 127}));
  connect(output_2_sign.y, amplitude_2) 
    annotation(Line(points = {{17, 30}, {163, 30}}, color = {0, 0, 127}));
  connect(core_y2, output_3_sign.u) 
    annotation(Line(points = {{-163, -30}, {-17, -30}}, color = {0, 0, 127}));
  connect(output_3_sign.y, amplitude_3) 
    annotation(Line(points = {{17, -30}, {163, -30}}, color = {0, 0, 127}));
  connect(core_y3, output_4_sign.u) 
    annotation(Line(points = {{-163, -90}, {-17, -90}}, color = {0, 0, 127}));
  connect(output_4_sign.y, amplitude_4) 
    annotation(Line(points = {{17, -90}, {163, -90}}, color = {0, 0, 127}));
  end OfficialPidSysblockAdapter;