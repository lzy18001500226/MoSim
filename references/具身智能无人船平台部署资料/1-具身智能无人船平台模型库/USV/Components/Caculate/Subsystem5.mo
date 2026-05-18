model Subsystem5
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Rectangle(origin={0,-0.513173}, 
lineColor={0,0,0}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-100,-100},{100,100}}, 
radius=25), Text(origin={6.41444,-4.61857}, 
lineColor={255,0,0}, 
extent={{-70.8179,34.126},{70.8179,-34.126}}, 
textString="Subsystem5", 
textStyle={TextStyle.None}, 
textColor={255,0,0}, 
horizontalAlignment=LinePattern.None)}));
  Modelica.Blocks.Interfaces.RealInput psi[3] 
    "角度" annotation (Placement(transformation(origin={-110.772,-0.27288}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Sin sin 
    annotation (Placement(transformation(origin={-51.0133,75.0677}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Cos cos1 
    annotation (Placement(transformation(origin={-49.2759,34.3965}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const(k=0) 
    annotation (Placement(transformation(origin={-49.7814,-35.6013}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const1(k=1) 
    annotation (Placement(transformation(origin={-49.334,-80.6053}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Gain gain(k=-1) 
    annotation (Placement(transformation(origin={26.7276,74.0934}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput Jn[3,3] 
    annotation (Placement(transformation(origin={110.49,-0.699978}, 
extent={{-10,-10},{10,10}})));
equation
  connect(psi[3], sin.u) 
  annotation(Line(origin={-87,37}, 
  points={{-23.772,-37.27288},{4.26325,-37.27288},{4.26325,38.0677},{23.9867,38.0677}}, 
  color={0,0,127}));
  connect(psi[3], cos1.u) 
  annotation(Line(origin={-86,17}, 
  points={{-24.772,-17.27288},{3.26325,-17.27288},{3.26325,17.3965},{24.7241,17.3965}}, 
  color={0,0,127}));
  connect(sin.y, gain.u) 
  annotation(Line(origin={-22,76}, 
points={{-18.0133,-0.9323},{36.7276,-0.9323},{36.7276,-1.90659}}, 
color={0,0,127}));
  connect(cos1.y, Jn[1,1]) 
  annotation(Line(origin={36,17}, 
  points={{-74.2759,17.3965},{-36,17.3965},{-36,-17.699978},{74.49,-17.699978}}, 
  color={0,0,127}));
  connect(cos1.y, Jn[2,2]) 
  annotation(Line(origin={36,17}, 
points={{-74.2759,17.3965},{-36.1143,17.3965},{-36.1143,-17.699978},{74.49,-17.699978}}, 
color={0,0,127}));
  connect(gain.y, Jn[1,2]) 
  annotation(Line(origin={65,37}, 
points={{-27.2724,37.0934},{5.26957,37.0934},{5.26957,-37.699978},{45.49,-37.699978}}, 
color={0,0,127}));
  connect(const.y, Jn[1,3]) 
  annotation(Line(origin={36,-18}, 
  points={{-74.7814,-17.6013},{-36,-17.6013},{-36,17.300022},{74.49,17.300022}}, 
  color={0,0,127}));
  connect(const.y, Jn[2,3]) 
  annotation(Line(origin={36,-18}, 
points={{-74.7814,-17.6013},{-36.1186,-17.6013},{-36.1186,17.300022},{74.49,17.300022}}, 
color={0,0,127}));
  connect(const.y, Jn[3,1]) 
  annotation(Line(origin={36,-18}, 
points={{-74.7814,-17.6013},{-36.0284,-17.6013},{-36.0284,17.300022},{74.49,17.300022}}, 
color={0,0,127}));
  connect(const.y, Jn[3,2]) 
  annotation(Line(origin={36,-18}, 
points={{-74.7814,-17.6013},{-36.0717,-17.6013},{-36.0717,17.300022},{74.49,17.300022}}, 
color={0,0,127}));
  connect(sin.y, Jn[2,1]) 
  annotation(Line(origin={35,37}, 
points={{-75.0133,38.0677},{-35.0843,38.0677},{-35.0843,-37.699978},{75.49,-37.699978}}, 
color={0,0,127}));
  connect(const1.y, Jn[3,3]) 
  annotation(Line(origin={36,-41}, 
  points={{-74.334,-39.6053},{-36,-39.6053},{-36,40.300022},{74.49,40.300022}}, 
  color={0,0,127}));
  end Subsystem5;