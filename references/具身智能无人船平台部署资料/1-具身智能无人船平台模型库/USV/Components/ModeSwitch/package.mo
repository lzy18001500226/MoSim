package ModeSwitch "模式切换"
  annotation(__MWORKS(version="2025a"));
  model Auto_Switch "遥控/自动导航模式切换"
    extends USV.Utilities.Icons.Model;
    annotation(__MWORKS(version = "2025a"), Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={5,2}, 
lineColor={0,0,0}, 
extent={{-59,46},{59,-46}}, 
textString="RC/Auto", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}));
    Modelica.Blocks.Interfaces.BooleanInput valid 
      annotation(Placement(transformation(origin={-110,50}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput advisedThrottle 
      annotation(Placement(transformation(origin={-110,16.6667}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput advisedRudder 
      annotation(Placement(transformation(origin={-110,-16.6667}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealOutput Throttle 
      annotation(Placement(transformation(origin={110,50}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealOutput Rudder 
      annotation(Placement(transformation(origin={110,-50}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Logical.Switch switch1 
      annotation(Placement(transformation(origin={46,50}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Logical.Switch switch2 
      annotation(Placement(transformation(origin={46,-50}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Interfaces.IntegerInput workmodel 
      annotation (Placement(transformation(origin={-110,83.3333}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Logical.IntegerEquality integerEquality 
      annotation (Placement(transformation(origin={-34,72}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.IntegerConstant integerConstant(k=2) 
      annotation (Placement(transformation(origin={-64,42}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Logical.And and1 
      annotation (Placement(transformation(origin={4,33}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Interfaces.RealInput RCThrottle 
      annotation(Placement(transformation(origin={-110,-50}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput RCRudder 
      annotation(Placement(transformation(origin={-110,-83.3333}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
  equation
    connect(switch1.y, Throttle) 
      annotation(Line(origin = {62, 50}, 
      points = {{-5, 0}, {48, 0}}, 
      color = {0, 0, 127}));
    connect(switch2.y, Rudder) 
      annotation(Line(origin = {62, -50}, 
      points = {{-5, 0}, {48, 0}}, 
      color = {0, 0, 127}));
    connect(advisedThrottle, switch1.u1) 
      annotation(Line(origin = {-38, 29}, 
      points = {{-72, -29}, {-46, -29}, {-46, 29}, {72, 29}}, 
      color = {0, 0, 127}));
    connect(advisedRudder, switch2.u1) 
      annotation(Line(origin={-38,-54}, 
points={{-72,37.3333},{-44,37.3333},{-44,12},{72,12}}, 
color={0,0,127}));
    connect(integerConstant.y, integerEquality.u2) 
    annotation(Line(origin={-45,55}, 
points={{-8,-13},{-5,-13},{-5,9},{-1,9}}, 
color={255,127,0}));
    connect(workmodel, integerEquality.u1) 
    annotation(Line(origin={-74,75}, 
points={{-36,8.3333},{24,8.3333},{24,-3},{28,-3}}, 
color={255,127,0}));
    connect(valid, and1.u2) 
    annotation(Line(origin={-59,25}, 
points={{-51,25},{-19,25},{-19,0},{51,0}}, 
color={255,0,255}));
    connect(integerEquality.y, and1.u1) 
    annotation(Line(origin={-11,54}, 
points={{-12,18},{-5,18},{-5,-21},{3,-21}}, 
color={255,0,255}));
    connect(and1.y, switch1.u2) 
    annotation(Line(origin={25,42}, 
    points={{-10,-9},{-1,-9},{-1,8},{9,8}}, 
    color={255,0,255}));
    connect(and1.y, switch2.u2) 
    annotation(Line(origin={25,-8}, 
    points={{-10,41},{-1,41},{-1,-42},{9,-42}}, 
    color={255,0,255}));
    connect(RCThrottle, switch1.u3) 
    annotation(Line(origin={-38,-4}, 
    points={{-72,-46},{20,-46},{20,22},{66,22},{66,46},{72,46}}, 
    color={0,0,127}));
    connect(RCRudder, switch2.u3) 
    annotation(Line(origin={-38,-71}, 
    points={{-72,-12.3333},{20,-12.3333},{20,13},{72,13}}, 
    color={0,0,127}));

  end Auto_Switch;

end ModeSwitch;