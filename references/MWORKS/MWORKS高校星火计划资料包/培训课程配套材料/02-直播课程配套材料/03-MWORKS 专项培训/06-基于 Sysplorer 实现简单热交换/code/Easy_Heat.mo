model Easy_Heat "简单热交换-文本-带量纲"
parameter Modelica.SIunits.Density rou=1000;
parameter Modelica.SIunits.Volume V=2;
parameter Modelica.SIunits.SpecificHeatCapacity Cp=1.8;
parameter Modelica.SIunits.CoefficientOfHeatTransfer h=100;
parameter Modelica.SIunits.Area A=250;
parameter Modelica.SIunits.Temp_C T_in=80;
parameter Modelica.SIunits.Temp_C  T_s=150;
parameter Modelica.SIunits.MassFlowRate m=20;

Modelica.SIunits.Temp_C T_out(start=75);
  annotation(experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,NumberOfIntervals=500,StartTime=0,StopTime=1,Tolerance=0.0001));
equation
rou*Cp*V*der(T_out)=m*Cp*(T_in-T_out)+h*A*(T_s-T_out);
end Easy_Heat;