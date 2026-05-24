connector Fluid_Portb "流体出口"
  annotation(__MWORKS(version="2025b"),Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Ellipse(origin={-3.5,-5.5},
lineColor={0,0,255},
fillColor={255,255,255},
fillPattern=FillPattern.Solid,
lineThickness=2,
extent={{-95.5,88.5},{95.5,-88.5}})}));
Modelica.SIunits.Pressure p;
flow Modelica.SIunits.MassFlowRate mflow;
stream Modelica.SIunits.SpecificEnthalpy hflow;
end Fluid_Portb;