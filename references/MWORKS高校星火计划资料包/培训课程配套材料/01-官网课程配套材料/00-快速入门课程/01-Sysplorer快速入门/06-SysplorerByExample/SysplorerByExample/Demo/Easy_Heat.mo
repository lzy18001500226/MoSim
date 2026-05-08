model Easy_Heat "简单热交换"
parameter Modelica.SIunits.Density rou=1000;
parameter Modelica.SIunits.Volume V=2;
parameter Modelica.SIunits.SpecificHeatCapacity Cp=1.8;
parameter Modelica.SIunits.CoefficientOfHeatTransfer h=1000;
parameter Modelica.SIunits.Area A=250;
parameter Modelica.SIunits.Temp_C T_in=80;
parameter Modelica.SIunits.Temp_C  T_s=150;
parameter Modelica.SIunits.MassFlowRate m=20;
Real T_out(start=75);
equation
rou*Cp*V*der(T_out)=m*Cp*(T_in-T_out)+h*A*(T_s-T_out);
end Easy_Heat;