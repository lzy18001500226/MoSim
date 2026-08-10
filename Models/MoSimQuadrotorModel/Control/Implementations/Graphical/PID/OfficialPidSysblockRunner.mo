within MoSimQuadrotorModel.Control.Implementations.Graphical.PID;
model OfficialPidSysblockRunner "Official PID native graphical controller runner"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(x_ref, y_ref, z_ref, x_mea, y_mea, z_mea, roll_mea, pitch_mea, yaw_mea), Right(rotor_command_1, rotor_command_2, rotor_command_3, rotor_command_4)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=50,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Port.Inport x_ref 
    annotation (Placement(transformation(origin = {-520, 260}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport y_ref 
    annotation (Placement(transformation(origin = {-520, 205}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport z_ref 
    annotation (Placement(transformation(origin = {-520, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport x_mea 
    annotation (Placement(transformation(origin = {-520, 95}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport y_mea 
    annotation (Placement(transformation(origin = {-520, 40}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport z_mea 
    annotation (Placement(transformation(origin = {-520, -15}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport roll_mea 
    annotation (Placement(transformation(origin = {-520, -70}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea 
    annotation (Placement(transformation(origin = {-520, -125}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea 
    annotation (Placement(transformation(origin = {-520, -180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_1 
    annotation (Placement(transformation(origin = {520, 110}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_2 
    annotation (Placement(transformation(origin = {520, 35}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_3 
    annotation (Placement(transformation(origin = {520, -40}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_4 
    annotation (Placement(transformation(origin = {520, -115}, extent = {{-17, -13}, {17, 13}})));
  OfficialPidSysblockCore controller_core 
    annotation (Placement(transformation(origin = {-180, 120}, extent = {{-75, -165}, {75, 165}})),__MWORKS(SECInstance=true,PortLabels(labelType="PortName")));
  SysplorerEmbeddedCoder.MathOperation.Gain output_1_sign(k=1) 
    annotation(Placement(transformation(origin = {60, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain output_2_sign(k=-1) 
    annotation(Placement(transformation(origin = {60, 120}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain output_3_sign(k=1) 
    annotation(Placement(transformation(origin = {60, 60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain output_4_sign(k=-1) 
    annotation(Placement(transformation(origin = {60, 0}, extent = {{-17, -13}, {17, 13}})));
  OfficialPidSysblockMapper rotor_mapper 
    annotation (Placement(transformation(origin = {300, 120}, extent = {{-75, -165}, {75, 165}})),__MWORKS(SECInstance=true,PortLabels(labelType="PortName")));
  equation
  connect(x_ref, controller_core.x_ref) 
    annotation(Line(points = {{-503, 260}, {-379, 260}, {-379, 260}, {-255, 260}}, color = {0, 0, 127}));
  connect(y_ref, controller_core.y_ref) 
    annotation(Line(points = {{-503, 205}, {-379, 205}, {-379, 205}, {-255, 205}}, color = {0, 0, 127}));
  connect(z_ref, controller_core.z_ref) 
    annotation(Line(points = {{-503, 150}, {-379, 150}, {-379, 150}, {-255, 150}}, color = {0, 0, 127}));
  connect(x_mea, controller_core.x_mea) 
    annotation(Line(points = {{-503, 95}, {-379, 95}, {-379, 95}, {-255, 95}}, color = {0, 0, 127}));
  connect(y_mea, controller_core.y_mea) 
    annotation(Line(points = {{-503, 40}, {-379, 40}, {-379, 40}, {-255, 40}}, color = {0, 0, 127}));
  connect(z_mea, controller_core.z_mea) 
    annotation(Line(points = {{-503, -15}, {-379, -15}, {-379, -15}, {-255, -15}}, color = {0, 0, 127}));
  connect(roll_mea, controller_core.roll_mea) 
    annotation(Line(points = {{-503, -70}, {-379, -70}, {-379, -70}, {-255, -70}}, color = {0, 0, 127}));
  connect(pitch_mea, controller_core.pitch_mea) 
    annotation(Line(points = {{-503, -125}, {-379, -125}, {-379, -125}, {-255, -125}}, color = {0, 0, 127}));
  connect(yaw_mea, controller_core.yaw_mea) 
    annotation(Line(points = {{-503, -180}, {-379, -180}, {-379, -180}, {-255, -180}}, color = {0, 0, 127}));
  connect(controller_core.y, output_1_sign.u) 
    annotation(Line(points = {{-105, 180}, {0, 180}, {0, 180}, {43, 180}}, color = {0, 0, 127}));
  connect(output_1_sign.y, rotor_mapper.amplitude_1) 
    annotation(Line(points = {{77, 180}, {150, 180}, {150, 180}, {225, 180}}, color = {0, 0, 127}));
  connect(rotor_mapper.rotor_command_1, rotor_command_1) 
    annotation(Line(points = {{375, 180}, {439, 180}, {439, 110}, {503, 110}}, color = {0, 0, 127}));
  connect(controller_core.y1, output_2_sign.u) 
    annotation(Line(points = {{-105, 60}, {0, 60}, {0, 120}, {43, 120}}, color = {0, 0, 127}));
  connect(output_2_sign.y, rotor_mapper.amplitude_2) 
    annotation(Line(points = {{77, 120}, {150, 120}, {150, 110}, {225, 110}}, color = {0, 0, 127}));
  connect(rotor_mapper.rotor_command_2, rotor_command_2) 
    annotation(Line(points = {{375, 110}, {439, 110}, {439, 35}, {503, 35}}, color = {0, 0, 127}));
  connect(controller_core.y2, output_3_sign.u) 
    annotation(Line(points = {{-105, -60}, {0, -60}, {0, 60}, {43, 60}}, color = {0, 0, 127}));
  connect(output_3_sign.y, rotor_mapper.amplitude_3) 
    annotation(Line(points = {{77, 60}, {150, 60}, {150, 40}, {225, 40}}, color = {0, 0, 127}));
  connect(rotor_mapper.rotor_command_3, rotor_command_3) 
    annotation(Line(points = {{375, 40}, {439, 40}, {439, -40}, {503, -40}}, color = {0, 0, 127}));
  connect(controller_core.y3, output_4_sign.u) 
    annotation(Line(points = {{-105, -180}, {0, -180}, {0, 0}, {43, 0}}, color = {0, 0, 127}));
  connect(output_4_sign.y, rotor_mapper.amplitude_4) 
    annotation(Line(points = {{77, 0}, {150, 0}, {150, -30}, {225, -30}}, color = {0, 0, 127}));
  connect(rotor_mapper.rotor_command_4, rotor_command_4) 
    annotation(Line(points = {{375, -30}, {439, -30}, {439, -115}, {503, -115}}, color = {0, 0, 127}));
  end OfficialPidSysblockRunner;
