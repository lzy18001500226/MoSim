package Control "控制部分"
  model Control_Allocation
    extends USV.Utilities.Icons.Model;
    annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={2,-2}, 
lineColor={0,0,0}, 
extent={{-62,32},{62,-32}}, 
textString="Control_Allocation", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}));
    Modelica.Blocks.Interfaces.RealInput surge 
      annotation(Placement(transformation(origin = {-120, 50}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput yaw 
      annotation(Placement(transformation(origin = {-120, -50}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput right 
      annotation(Placement(transformation(origin = {110, 50}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput left 
      annotation(Placement(transformation(origin = {110, -50}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Components.Control_Allocation control_Allocation 
      annotation(Placement(transformation(origin = {-40, 3.55271e-15}, 
      extent = {{-20, -20}, {20, 20}})));
    Utilities.Math.Signed_Square_Root signed_Square_Root[2] 
      annotation(Placement(transformation(origin = {6, 0}, 
      extent = {{-10, -10}, {10, 10}})));
    Components.Thrust thrust 
      annotation(Placement(transformation(origin = {52, -2.22045e-16}, 
      extent = {{-10, -10}, {10, 10}})));
  equation
    connect(surge, control_Allocation.tau[1]) 
      annotation(Line(origin = {-92, 25}, 
      points = {{-28, 25}, {12, 25}, {12, -25}, {28, -25}}, 
      color = {0, 0, 127}));
    connect(yaw, control_Allocation.tau[2]) 
      annotation(Line(origin = {-92, -25}, 
      points = {{-28, -25}, {12, -25}, {12, 25}, {28, 25}}, 
      color = {0, 0, 127}));
    connect(control_Allocation.n_abs_n, signed_Square_Root.u) 
      annotation(Line(origin = {-12, 0}, 
      points = {{-6, 3.55271e-15}, {6, 3.55271e-15}, {6, 0}}, 
      color = {0, 0, 127}));
    connect(signed_Square_Root[1].y, thrust.L) 
      annotation(Line(origin = {24, 3}, 
      points = {{-7, -3}, {0, -3}, {0, 2}, {16, 2}}, 
      color = {0, 0, 127}));
    connect(signed_Square_Root[2].y, thrust.R) 
      annotation(Line(origin = {24, -2}, 
      points = {{-7, 2}, {0, 2}, {0, -3}, {16, -3}}, 
      color = {0, 0, 127}));
    connect(thrust.Thrust, right) 
      annotation(Line(origin = {87, 28}, 
      points = {{-24, -23}, {-7, -23}, {-7, 22}, {23, 22}}, 
      color = {0, 0, 127}));
    connect(thrust.Thrust1, left) 
      annotation(Line(origin = {87, -27}, 
      points = {{-24, 22}, {-7, 22}, {-7, -23}, {23, -23}}, 
      color = {0, 0, 127}));
  end Control_Allocation;

end Control;