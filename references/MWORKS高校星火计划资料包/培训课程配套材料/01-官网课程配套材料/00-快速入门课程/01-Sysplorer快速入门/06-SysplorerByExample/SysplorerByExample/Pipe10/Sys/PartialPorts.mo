partial model PartialPorts "双接口"
  annotation(__MWORKS(version="2025b"));
  parameter Modelica.SIunits.Pressure p_start=1.01e5;
  Modelica.SIunits.MassFlowRate dmflow;
  Modelica.SIunits.Pressure dp;
  Connectors.Fluid_Porta Porta 
    annotation (Placement(transformation(origin={-100,20},
extent={{-10,-10},{10,10}})));
  Connectors.Fluid_Portb Portb 
    annotation (Placement(transformation(origin={10,20},
extent={{-10,-10},{10,10}})));
equation
dmflow=Porta.mflow+Portb.mflow;
dp=Porta.p-Portb.p;
end PartialPorts;