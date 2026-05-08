# package.mo

- Source: `培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/00-模型材料/UGV/CountPoint/package.mo`
- Category: `quadrotor_uav`
- Score: `70`
- Size: `0.00 MB`
- Extract mode: `text`

## Extracted Text

```text
﻿package CountPoint "计分模块"
  annotation(__MWORKS(version="2025a"),Protection(access=Access.diagram));
  model CountPoint "计分模块"
    annotation(__MWORKS(version = "2025a"), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2})), Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={-3.55271e-15,-154}, 
rotation=180, 
lineColor={0,0,0}, 
extent={{-230,20},{230,-20}}, 
textString="计分模块", 
fontSize=18, 
fontName="微软雅黑", 
textStyle={TextStyle.Bold}, 
textColor={0,0,0}), Polygon(origin={-46,38}, 
fillColor={255,0,0}, 
fillPattern=FillPattern.Solid, 
points={{-8,4},{-2,14},{4,24},{8,24},{8,12},{8,-24},{2,-24},{2,6},{2,10}}), Ellipse(origin={-20.3372,38}, 
fillColor={255,0,0}, 
fillPattern=FillPattern.Solid, 
extent={{10,24},{-10,-24}}), Ellipse(origin={-20.5,38}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{3.5,12},{-3.5,-12}}), Rectangle(origin={-2.30608,2.40064}, 
rotation=-30, 
fillColor={0,0,0}, 
fillPattern=FillPattern.Solid, 
extent={{2.15064,52.3372},{-2.15064,-52.3372}}), Polygon(origin={14,-26}, 
fillColor={255,0,0}, 
fillPattern=FillPattern.Solid, 
points={{-8,4},{-2,14},{4,24},{8,24},{8,12},{8,-24},{2,-24},{2,6},{2,10}}), Ellipse(origin={38,-26}, 
fillColor={255,0,0}, 
fillPattern=FillPattern.Solid, 
extent={{10,24},{-10,-24}}), Ellipse(origin={37.5,-26}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{3.5,12},{-3.5,-12}})}),Protection(access=Access.diagram));
    extends UGV.Utilities.Icons.Model1;
    //参数
    parameter Real mindis = 0.11 "碰撞阈值";
    Real counterR(start = 0) "道路碰撞计数";
    Real counterO(start = 0) "障碍碰撞计数";
    Modelica.Blocks.Interfaces.RealInput DisRoad "小车与道路间距" 
      annotation(Placement(transformation(origin = {-110, 50}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput DisObstacle "小车与障碍间距" 
      annotation(Placement(transformation(origin = {-110, -50}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    output Real finalPoints "最终得分";
  algorithm
    when DisRoad < mindis then
      counterR := counterR + 1;  //("车辆超出界限，且每超出一次计数")
    end when;
    when DisObstacle < mindis then
      counterO := counterO + 1;  //("车辆超出界限，且每超出一次计数")
    end when;
    finalPoints := 10 - (counterR + counterO) * 0.4;  //最终得分，满分10分，碰撞一次扣0.4分
  end CountPoint;

end CountPoint;
```
