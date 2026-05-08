model Pipe "管道本体"
  annotation(__MWORKS(version="2025b"),Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Rectangle(origin={-46,19},
fillColor={0,0,255},
fillPattern=FillPattern.Solid,
extent={{-50,25},{50,-25}})}));
  import Modelica.Constants;
outer.SysplorerByExample.Pipe10.Sys.System system;
extends SysplorerByExample.Pipe10.Sys.PartialPorts(dmflow=0);
parameter Modelica.SIunits.Density rho=1000"液体密度" 
 annotation (Dialog(tab = "工质参数"));
  parameter Modelica.SIunits.DynamicViscosity mu = 0.0018 "动力粘度" 
    annotation (Dialog(tab = "工质参数"));
  parameter Modelica.SIunits.Length L = 1 "管道长度" 
    annotation (Dialog(tab = "结构参数"));
  parameter Modelica.SIunits.Diameter d(min = 0.0) = 0.02 "管道直径" 
    annotation (Dialog(tab = "结构参数"));
  parameter Modelica.SIunits.Height deltaH = 0 "管道进出口高度差" 
    annotation (Dialog(tab = "结构参数"));
  parameter Modelica.SIunits.Height epsilon = 6e-5 "绝对粗糙度" 
    annotation (Dialog(tab = "结构参数"));
  final parameter Modelica.SIunits.Acceleration g = system.g "重力加速度";
  Modelica.SIunits.Area A=d^2*Constants.pi/4;
  Modelica.SIunits.Volume V = L * A "管道容积";
  Modelica.SIunits.Diameter Dh = d "水力直径";
  Modelica.SIunits.Pressure p_in(start = p_start) "入口压力";
  Modelica.SIunits.MassFlowRate m_outflow "出口质量流量";
  Modelica.SIunits.ReynoldsNumber Re "管道流动的雷诺数";
  Real j = L / A "惯性损失系数";
  Real zeta = lambda * L / (2 * d * A ^ 2) "沿程阻力损失系数";
  Real lambda "摩擦损失系数";
  Modelica.SIunits.SpecificEnthalpy h[2] "从a.b口流入的比焓";
equation
//雷诺数
Re=.SysplorerByExample.Pipe10.FUN.Re(m_outflow,mu,Dh,A);
//摩擦系数
lambda=.SysplorerByExample.Pipe10.FUN.lambda (Re,d,epsilon);
m_outflow =-Portb.mflow;
p_in=Porta.p;
h[1]=inStream(Porta.hflow);
h[2]=inStream(Portb.hflow);

Porta.hflow=h[2]+system.g*deltaH;
Portb.hflow=h[1]-system.g*deltaH;

dp=j*der(m_outflow)+(1/rho)*zeta*(m_outflow)^2*sign(m_outflow)+rho*g*deltaH;
end Pipe;