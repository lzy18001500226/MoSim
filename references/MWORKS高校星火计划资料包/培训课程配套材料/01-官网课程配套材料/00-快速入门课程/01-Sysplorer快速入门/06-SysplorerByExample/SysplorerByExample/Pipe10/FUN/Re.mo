function Re "雷诺数"
  annotation(__MWORKS(version="2025b"));
  input Modelica.SIunits.MassFlowRate m_flow "流体质量流速";
  input Modelica.SIunits.DynamicViscosity mu "流体动力粘度";
  input Modelica.SIunits.Length D "当量直径或者水力直径";
  input Modelica.SIunits.Area A = Modelica.Constants.pi / 4 * D * D "流动截面积";
  output Modelica.SIunits.ReynoldsNumber Re "雷诺数";
algorithm
  Re := abs(m_flow) * D / A / mu;
end Re;