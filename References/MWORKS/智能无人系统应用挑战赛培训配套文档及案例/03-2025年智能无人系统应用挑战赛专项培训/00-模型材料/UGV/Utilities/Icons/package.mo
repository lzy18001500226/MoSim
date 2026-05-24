package Icons "图标"
  annotation(__MWORKS(version="2025a"),Protection(access=Access.diagram));
  model Model1 "模型基类图标"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2})), 
      Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      preserveAspectRatio = false, 
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0}, 
      lineColor = {0, 0, 0}, 
      fillColor = {255, 255, 255}, 
      fillPattern = FillPattern.Solid, 
      extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      radius = 25.0), Rectangle(origin = {0.0, 0.0}, 
      lineColor = {128, 128, 128}, 
      extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      radius = 25.0)}));
  end Model1;

end Icons;