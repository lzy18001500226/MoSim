connector Fluid_Porta "流体进口"
  annotation(__MWORKS(version="2025b"),Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Ellipse(origin={-2,-8},
lineColor={0,0,255},
fillColor={0,0,255},
fillPattern=FillPattern.Solid,
extent={{-92,84},{92,-84}})}));
Modelica.SIunits.Pressure p;
flow Modelica.SIunits.MassFlowRate mflow;
stream Modelica.SIunits.SpecificEnthalpy hflow;
end Fluid_Porta;