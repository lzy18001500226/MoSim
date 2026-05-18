model YawOpreation "偏航指令操作"
extends USV.Utilities.Icons.Model;
constant Real pi=Modelica.Constants.pi;
parameter Real yaw0=0"初始偏航";
parameter Real k=pi/6"变化速率";
  Modelica.Blocks.Interfaces.BooleanInput right 
    annotation (Placement(transformation(origin={-120.266,60.2953}, 
extent={{-20,-20},{20,20}})));
  Modelica.Blocks.Interfaces.BooleanInput left 
    annotation (Placement(transformation(origin={-121.239,-60.9436}, 
extent={{-20,-20},{20,20}})));
  Modelica.Blocks.Interfaces.RealOutput yaw 
    annotation (Placement(transformation(origin={110.865,-0.972462}, 
extent={{-10,-10},{10,10}})));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
initial equation
yaw=yaw0;
algorithm
when  right==true then
yaw:=pre(yaw)+k;
end when;
when left==true then
yaw:=pre(yaw)-k;
end when;
end YawOpreation;