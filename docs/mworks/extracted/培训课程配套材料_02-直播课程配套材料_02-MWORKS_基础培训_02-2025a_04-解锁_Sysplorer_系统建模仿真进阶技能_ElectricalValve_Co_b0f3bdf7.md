# PID_Controller.mo

- Source: `培训课程配套材料/02-直播课程配套材料/02-MWORKS 基础培训/02-2025a/04-解锁 Sysplorer 系统建模仿真进阶技能/ElectricalValve/Controller/PID_Controller.mo`
- Category: `sysplorer_modeling`
- Score: `74`
- Size: `0.00 MB`
- Extract mode: `text`

## Extracted Text

```text
﻿model PID_Controller "PID控制器"
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Rectangle(origin={0,0}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-100,100},{100,-100}}), Text(origin={1,0}, 
lineColor={0,0,0}, 
extent={{-87,77.5},{87,-77.5}}, 
textString="PID
控制器", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}));
  Modelica.Blocks.Continuous.Integrator integrator 
    annotation (Placement(transformation(origin={-34,-4}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Gain gain 
    annotation (Placement(transformation(origin={-34,30}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput y "Connector of Real output signal" 
    annotation (Placement(transformation(origin={38,-4}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={110,-2.22045e-16}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput u "Connector of Real input signal" 
    annotation (Placement(transformation(origin={-108,-4}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={-110,0}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Add3 add3_1 
    annotation (Placement(transformation(origin={2,-4}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Continuous.Derivative derivative 
    annotation (Placement(transformation(origin={-34,-34}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(integrator.u, u) 
  annotation(Line(origin={-77,-4}, 
  points={{31,0},{-31,0}}, 
  color={0,0,127}));
  connect(gain.u, u) 
  annotation(Line(origin={-77,13}, 
  points={{31,17},{7,17},{7,-17},{-31,-17}}, 
  color={0,0,127}));
  connect(y, add3_1.y) 
  annotation(Line(origin={26,-4}, 
  points={{12,0},{-13,0}}, 
  color={0,0,127}));
  connect(integrator.y, add3_1.u2) 
  annotation(Line(origin={-16,-4}, 
  points={{-7,0},{6,0}}, 
  color={0,0,127}));
  connect(add3_1.u1, gain.y) 
  annotation(Line(origin={-16,17}, 
  points={{6,-13},{0,-13},{0,13},{-7,13}}, 
  color={0,0,127}));
  connect(derivative.y, add3_1.u3) 
  annotation(Line(origin={-16,-23}, 
  points={{-7,-11},{0,-11},{0,11},{6,11}}, 
  color={0,0,127}));
  connect(derivative.u, u) 
  annotation(Line(origin={-77,-19}, 
  points={{31,-15},{7,-15},{7,15},{-31,15}}, 
  color={0,0,127}));
  end PID_Controller;
```
