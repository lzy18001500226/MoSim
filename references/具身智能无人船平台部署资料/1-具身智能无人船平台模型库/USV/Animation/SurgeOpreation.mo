model SurgeOpreation "指令操作"
extends USV.Utilities.Icons.Model;
parameter Real surge0=10"初速推杆";
parameter Real k=1"变化速率";
  Modelica.Blocks.Interfaces.BooleanInput up 
    annotation (Placement(transformation(origin={-120.266,60.2953}, 
extent={{-20,-20},{20,20}})));
  Modelica.Blocks.Interfaces.BooleanInput down 
    annotation (Placement(transformation(origin={-121.239,-60.9436}, 
extent={{-20,-20},{20,20}})));
  Modelica.Blocks.Interfaces.RealOutput surge 
    annotation (Placement(transformation(origin={110.865,-0.972462}, 
extent={{-10,-10},{10,10}})));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
initial equation
surge=surge0;

algorithm
when  up==true then
surge:=pre(surge)+k;
end when;
when down==true then
surge:=pre(surge)-k;
end when;
end SurgeOpreation;