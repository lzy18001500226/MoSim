model Pipe_with "管道"
  import Modelica.Constants;
  outer .SysplorerByExample.Demo.PipeTestLib1014.System system;
  extends BasicModel.PartialTwoPorts(dm_flow = 0);
  parameter Modelica.SIunits.Density rho = 1000 "液体密度" 
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


  Modelica.SIunits.Area A = d ^ 2 * Constants.pi / 4 "管道截面积";
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
//在 Modelica 中，函数名前面的点（.）表示完全限定名（fully qualified name），用于明确指定函数所在的包路径。
  Re = .SysplorerByExample.Demo.PipeTestLib1014.Utilities.Functions.Re(m_outflow, mu, Dh, A);
  //雷诺数方程
  lambda = .SysplorerByExample.Demo.PipeTestLib1014.Utilities.Functions.lambda(Re, d, epsilon);
  //摩擦损失系数方程
  m_outflow = -port_b.m_flow;
  //出口流量方程
  p_in = port_a.p;
  //进口压力方程
  dp = j * der(m_outflow) + sign(m_outflow) * zeta * m_outflow ^ 2 / rho + rho * g * deltaH;
   h[1] = inStream(port_a.h);
   h[2] = inStream(port_b.h);
  port_b.h = inStream(port_a.h) - system.g*deltaH;
  port_a.h= inStream(port_b.h) + system.g*deltaH;



  //能量平衡
  //connect(port_a1, heattrasfer.heatPorts);
  //换热模块与外部接口连接
  annotation (Icon(graphics = {
    Rectangle(extent = {{-100, 40}, {100, -40}},
    color = {0, 0, 0}, fillPattern = FillPattern.Solid,
    fillColor = {0, 140, 255}, thickness = 0.25)}),
    Documentation(info = "<p>管道压降公式"));
end Pipe_with;