# Wheel.mo

- Source: `培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/00-模型材料/UGV/Vehicle/Tire/Wheel.mo`
- Category: `quadrotor_uav`
- Score: `70`
- Size: `0.00 MB`
- Extract mode: `text`

## Extracted Text

```text
﻿model Wheel "无人车车轮模型"
  extends TADynamics.Vehicle.Wheels.Template.Wheel(
    redeclare TADynamics.Vehicle.Wheels.Component.ForceCal97 forceFormula, 
    data97(qsy1 = 0.01),mass1(visual1(shapeType="modelica://UGV/Resources/VisualModel/wheel.stl"),spindle(animation=false)));
  annotation (
    Diagram(coordinateSystem(extent = {{-160.0, -90.0}, {160.0, 90.0}}, 
      preserveAspectRatio = false, 
      grid = {2.0, 2.0})), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      preserveAspectRatio = false, 
      grid = {2.0, 2.0})), 
    Protection(access=Access.diagram), 
    Documentation(link="modelica://TADynamics/Resource/Doc/Default.html"));
end Wheel;
```
