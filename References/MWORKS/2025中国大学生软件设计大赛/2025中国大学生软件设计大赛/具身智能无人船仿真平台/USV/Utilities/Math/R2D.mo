model R2D "弧度转角度"
constant Real pi=Modelica.Constants.pi;
  annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Rectangle(origin={0,0}, 
lineColor={0,0,0}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-100,-100},{100,100}}, 
radius=25), Text(origin={9.82217,1.09135}, 
lineColor={0,0,0}, 
extent={{-55,35},{55,-35}}, 
textString="R2D", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  Modelica.Blocks.Interfaces.RealInput w 
    "rad/s" annotation (Placement(transformation(origin={-111.045,-0.545684}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput u 
    "deg/s" annotation (Placement(transformation(origin={110.132,-0.367848}, 
extent={{-10,-10},{10,10}})));
equation
u=w*180/pi;
end R2D;