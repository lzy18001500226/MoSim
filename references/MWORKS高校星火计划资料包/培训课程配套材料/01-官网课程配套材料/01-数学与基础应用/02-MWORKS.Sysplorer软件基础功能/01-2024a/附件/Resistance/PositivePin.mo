within Resistance;
connector PositivePin "正极"
  Modelica.SIunits.Voltage v "电势";//势变量
  flow Modelica.SIunits.Current i "电流";//流变量
  annotation (Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0}, 
      lineColor = {0, 0, 255}, 
      fillColor = {0, 0, 255}, 
      fillPattern = FillPattern.Solid, 
      extent = {{-100.0, 100.0}, {100.0, -100.0}})}));
end PositivePin;