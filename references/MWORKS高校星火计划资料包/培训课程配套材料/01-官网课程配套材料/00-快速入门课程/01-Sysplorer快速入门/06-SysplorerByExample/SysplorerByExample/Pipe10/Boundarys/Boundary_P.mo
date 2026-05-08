model Boundary_P "压力边界"
  annotation(__MWORKS(version="2025b"),Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Ellipse(origin={-31,13},
fillColor={0,170,255},
fillPattern=FillPattern.Horizontal,
extent={{-69,63},{69,-63}})}));
outer.SysplorerByExample.Pipe10.Sys.System system;
parameter Modelica.SIunits.Pressure p=2.01e5;
parameter Modelica.SIunits.Temperature T=293.15;
  Connectors.Fluid_Porta Porta 
    annotation (Placement(transformation(origin={-120,20},
extent={{-10,-10},{10,10}})));

equation
Porta.p=p;
Porta.hflow=system.cp*(T-273.15);
end Boundary_P;