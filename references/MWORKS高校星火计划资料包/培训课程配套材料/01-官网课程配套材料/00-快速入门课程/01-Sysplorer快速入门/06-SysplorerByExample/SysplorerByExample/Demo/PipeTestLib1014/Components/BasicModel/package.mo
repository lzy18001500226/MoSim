package BasicModel "基类模型"
  partial model PartialTwoPorts "双接口"
    parameter Modelica.SIunits.Pressure p_start = 1.0135e5 
      annotation (Dialog(tab = "初始条件"));
    Modelica.SIunits.MassFlowRate dm_flow "进出口质量损失";
    Modelica.SIunits.Pressure dp "进出口压力损失";
    Interfaces.FluidInterfaces.FluidPort_a port_a 
      annotation (Placement(transformation(origin = {-100.0, 0.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Interfaces.FluidInterfaces.FluidPort_b port_b 
      annotation (Placement(transformation(origin = {100.0, 0.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  equation
    dp = port_a.p - port_b.p;
    //压差方程
    port_a.m_flow + port_b.m_flow = dm_flow;
    //质量守恒方程
  end PartialTwoPorts;

end BasicModel;