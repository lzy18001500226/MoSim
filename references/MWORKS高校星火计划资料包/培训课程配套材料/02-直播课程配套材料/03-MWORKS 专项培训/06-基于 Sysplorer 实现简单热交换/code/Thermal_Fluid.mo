model Thermal_Fluid "热模型的流体"
  annotation(__MWORKS(version="2025a"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,NumberOfIntervals=500,StartTime=0,StopTime=1,Tolerance=0.0001));
  Modelica.Thermal.FluidHeatFlow.Components.Pipe pipe(useHeatPort=true,m=2000,medium=medium1,T_q(start=423.15),T0=348.15,T0fixed=true,V_flow(start=0.05)) 
    annotation (Placement(transformation(origin={-256,166}, 
extent={{-26,-26},{26,26}})));
  Modelica.Thermal.HeatTransfer.Sources.FixedTemperature fixedTemperature(T=423.15) 
    annotation (Placement(transformation(origin={-106,94}, 
extent={{10,-10},{-10,10}})));
  parameter Modelica.Thermal.FluidHeatFlow.Media.Medium medium1(cp=1.8) 
    annotation (Placement(transformation(origin={-328,118}, 
extent={{-10,-10},{10,10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection convection 
    annotation (Placement(transformation(origin={-144,94}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Sources.Constant const(k=1000*250) 
    annotation (Placement(transformation(origin={-234,128}, 
extent={{-10,-10},{10,10}})));
  Modelica.Thermal.FluidHeatFlow.Sources.VolumeFlow pump(
    medium=medium1, 
    m=2000, 

    useVolumeFlowInput=false, 
    constantVolumeFlow=0.05,T0=353.15) 
    annotation (Placement(transformation(origin={-312,166}, 
extent={{-10,-10},{10,10}})));
  Modelica.Thermal.FluidHeatFlow.Sources.Ambient ambient1(medium=medium1,T_port(start=353.15),constantAmbientPressure=100000) 
    annotation (Placement(transformation(origin={-352,166}, 
extent={{10,-10},{-10,10}})));
  Modelica.Thermal.FluidHeatFlow.Sources.Ambient ambient2(medium=medium1,T_port(start=353.15),constantAmbientPressure=100000) 
    annotation (Placement(transformation(origin={-182,166}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(fixedTemperature.port, convection.solid) 
  annotation(Line(origin={-116,97}, 
points={{0,-3},{-18,-3}}, 
color={191,0,0}));
  connect(convection.fluid, pipe.heatPort) 
  annotation(Line(origin={-243,113}, 
points={{89,-19},{-13,-19},{-13,27}}, 
color={191,0,0}));
  connect(const.y, convection.Gc) 
  annotation(Line(origin={-214,113}, 
points={{-9,15},{70,15},{70,-9}}, 
color={0,0,127}));
  connect(pump.flowPort_b, pipe.flowPort_a) 
  annotation(Line(origin={-292,166}, 
  points={{-10,0},{10,0}}, 
  color={255,0,0}));
  connect(ambient1.flowPort, pump.flowPort_a) 
  annotation(Line(origin={-334,183}, 
points={{-8,-17},{12,-17}}, 
color={255,0,0}));
  connect(ambient2.flowPort, pipe.flowPort_b) 
  annotation(Line(origin={-230,198}, 
points={{38,-32},{0,-32}}, 
color={255,0,0}));
  end Thermal_Fluid;