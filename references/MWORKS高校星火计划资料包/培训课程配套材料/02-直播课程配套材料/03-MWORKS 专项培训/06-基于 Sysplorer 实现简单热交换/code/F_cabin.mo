model F_cabin
  annotation(__MWORKS(version="2025a"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Rectangle(origin={-80,2}, 
fillColor={0,0,255}, 
fillPattern=FillPattern.Backward, 
extent={{-20,100},{20,-100}})}));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor heatcapacitor[n + 1](C = 1.8*1000*2, T(start = 348.15)) 
    annotation (
      Placement(transformation(origin={-24,124}, 
extent={{-16,-16},{16,16}})));
  Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port[:] 
    annotation (Placement(transformation(origin={64,98}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={-50,2}, 
extent={{-10,-10},{10,10}})));
  Modelica.Thermal.HeatTransfer.Sources.FixedTemperature fixedTemperature(T=423.15) 
    annotation (Placement(transformation(origin={-142,92}, 
extent={{-10,-10},{10,10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection convection 
    annotation (Placement(transformation(origin={-75,98}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const(k=1000*250) 
    annotation (Placement(transformation(origin={-112,124}, 
extent={{-10,-10},{10,10}})));
equation
  connect(const.y, convection.Gc) 
  annotation(Line(origin={-96,103}, 
points={{-5,21},{21,21},{21,5}}, 
color={0,0,127}));
  connect(fixedTemperature.port, convection.solid) 
  annotation(Line(origin={-108,95}, 
  points={{-24,-3},{23,-3},{23,3}}, 
  color={191,0,0}));
  connect(convection.fluid, heatcapacitor[1].port) 
  annotation(Line(origin={-47,102}, 
points={{-18,-4},{23,-4},{23,6}}, 
color={191,0,0}));
  connect(heatcapacitor[1].port, port[1]) 
  annotation(Line(origin={40,51}, 
points={{-64,57},{24,57},{24,47}}, 
color={191,0,0}));
  end F_cabin;