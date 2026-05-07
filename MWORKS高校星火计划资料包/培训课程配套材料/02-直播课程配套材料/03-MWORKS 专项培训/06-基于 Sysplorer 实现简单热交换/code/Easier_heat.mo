model Easier_heat "无量纲的简单换热"
  annotation(__MWORKS(version="2025a"));

parameter Real rou=1000;
parameter Real V=2;
parameter Real Cp=1.8;
parameter Real h=1000;
parameter Real A=250;
parameter Real T_in=80;
parameter Real T_s=150;
parameter Real m=20;
Real T_out(start=75);
equation
rou*V*Cp*der(T_out)=m*Cp*(T_in-T_out)+h*A*(T_s-T_out);

end Easier_heat;