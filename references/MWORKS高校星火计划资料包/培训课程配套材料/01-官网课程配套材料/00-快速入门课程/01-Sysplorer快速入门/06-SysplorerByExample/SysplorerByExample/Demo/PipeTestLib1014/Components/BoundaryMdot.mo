model BoundaryMdot "流量边界"
  outer .SysplorerByExample.Demo.PipeTestLib1014.System system;
  parameter Modelica.SIunits.MassFlowRate m_flow = 1 "流量" 
    annotation (Dialog(enable = not use_mflow_in));
  parameter Modelica.SIunits.Temperature T = 293.15 "温度";
  parameter Boolean use_mflow_in = false "压力由外部接口输入" 
    annotation (Dialog(group = "数据来源选项"), Evaluate = true,
      HideResult = true, choices(checkBox = true));
  Modelica.Blocks.Interfaces.RealInput mflow_in if use_mflow_in
    "外部给定压力" annotation (Placement(transformation(
      origin = {-60, 100},
      extent = {{-20, -20}, {20, 20}},
      rotation = 270)));

  Interfaces.FluidInterfaces.FluidPort_a port_a 
    annotation (Placement(transformation(origin = {100.0, 0.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  if use_mflow_in then
    port_a.m_flow = -mflow_in;
  else
    port_a.m_flow = -m_flow;
  end if;
  port_a.h = system.cp * (T - 273.15);
  annotation (
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0}), graphics = {Ellipse(origin = {0.0, 0.0},
      lineColor = {66, 132, 197},
      fillColor = {66, 132, 197},
      fillPattern = FillPattern.Solid,
      extent = {{-80.0, 80.0}, {80.0, -80.0}}), Text(origin = {2.0, 7.0},
      extent = {{-52.0, 53.0}, {52.0, -53.0}},
      textString = "Mdot",
      textStyle = {TextStyle.None})}));

end BoundaryMdot;