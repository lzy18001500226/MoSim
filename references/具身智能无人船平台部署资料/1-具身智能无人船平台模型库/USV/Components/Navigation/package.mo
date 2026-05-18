package Navigation "导航算法"
  annotation(__MWORKS(version="2025a"));
  model NavSys "导航系统模型"
    extends USV.Utilities.Icons.Model;
    annotation(__MWORKS(version = "2025a"), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={2,-3}, 
lineColor={0,0,0}, 
extent={{-74,59},{74,-59}}, 
textString="Navigation", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}));

    //参数
    parameter Real routeWPRadius = 2.5 "导航点有效半径，m";
    //变量
    Real headingPrev2Ship;
    Real headingPrev2Next;
    Real distanceAB;
    Real degreeShipB;
    Real degreeShipAB;
    Real radShipAB;
    Real distanceRouteX;
    Real distanceRouteY;
    Real distanceRouteYB;
    Integer direct2WP;
    Real distance4Calc;
    Real simbolFlag;
    Real degreeCut;
    Real degree4Calc;
    Real A;
    Modelica.Blocks.Interfaces.RealInput lng 
      annotation(Placement(transformation(origin = {-109.091, 90.9091}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput lat 
      annotation(Placement(transformation(origin = {-109.091, 72.7273}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput realSpeed 
      annotation(Placement(transformation(origin = {-109.091, 54.5455}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput heading 
      annotation(Placement(transformation(origin = {-109.091, 36.3636}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput destLng 
      annotation(Placement(transformation(origin = {-109.091, 18.1818}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput advisedThrottle 
      annotation(Placement(transformation(origin = {110, 66.6667}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput advisedRudder 
      annotation(Placement(transformation(origin = {110, 0}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput destLat 
      annotation(Placement(transformation(origin = {-109.091, -1.42109e-14}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput prevLng 
      annotation(Placement(transformation(origin = {-109.091, -18.1818}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput prevLat 
      annotation(Placement(transformation(origin = {-109.091, -36.3636}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput shipToPrevWPDistance 
      annotation(Placement(transformation(origin = {-109.091, -54.5455}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput shipToNextWPDistance 
      annotation(Placement(transformation(origin = {-109.091, -72.7273}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput shipToRouteDistance 
      annotation(Placement(transformation(origin = {-109.091, -90.9091}, 
      extent = {{-9.09091, -9.09091}, {9.09091, 9.09091}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput advisedHeading 
      annotation(Placement(transformation(origin = {110, -66.6667}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
  algorithm
    //先进行坐标转化，以prev导航点A为原点，dest导航点B为North（0度）方向
    headingPrev2Ship := USV.Components.Navigation.Functions.formatDegree
      (
      USV.Components.Navigation.Functions.headingAB(prevLng, prevLat, lng, lat)
      );
    headingPrev2Next := USV.Components.Navigation.Functions.formatDegree
      (
      USV.Components.Navigation.Functions.headingAB(prevLng, prevLat, destLng, destLat)
      );

    distanceAB := USV.Components.Navigation.Functions.calcGPSDistance(prevLng, prevLat, destLng, destLat);
    degreeShipB := USV.Components.Navigation.Functions.formatDegree
      (
      USV.Components.Navigation.Functions.headingAB(lng, lat, destLng, destLat)
      );
    A := USV.Components.Navigation.Functions.headingAB(lng, lat, destLng, destLat);
    degreeShipAB := headingPrev2Ship - headingPrev2Next;
    radShipAB := d2r(degreeShipAB);

    distanceRouteX := shipToRouteDistance;
    distanceRouteY := shipToPrevWPDistance * cos(radShipAB);
    distanceRouteYB := distanceAB - distanceRouteY;

    direct2WP := 0;  //是否是直行到A或B导航点
    if abs(distanceRouteYB) >= abs(distanceAB) then
      //如果当前船在A->B连线（A在原点，B总是在正北方）的下方，则直接行驶到导航点A
      direct2WP := 1;  //直接行驶到A
    end if;

    if distanceRouteYB <= 0 then
      //如果当前船在A->B连线（A在原点，B总是在正北方）的上方，则直接行驶到导航点B
      direct2WP := 2;  //直接行驶到B
    end if;

    if abs(distanceRouteYB) < routeWPRadius or abs(distanceRouteX) < routeWPRadius then
      //如果距离B导航点纵坐标或横坐标之一在5米之内，则直行到导航点A或B
      direct2WP := 2;  //直接行驶到B
    end if;

    advisedHeading := 0.0;
    distance4Calc := 0.0;

    if direct2WP == 1 then
      //直接行驶到A
      advisedHeading := USV.Components.Navigation.Functions.formatDegree(headingPrev2Ship + 180);
      distance4Calc := shipToPrevWPDistance;
    elseif direct2WP == 2 then
      //直接行驶到B
      advisedHeading := degreeShipB;
      distance4Calc := shipToNextWPDistance;
    else
      simbolFlag := 1;
      if distanceRouteX >= 0 then
        simbolFlag := -1;
      end if;

      degreeCut := USV.Components.Navigation.Functions.calcDegreeCutByDistance(abs(distanceRouteX));
      advisedHeading := USV.Components.Navigation.Functions.formatDegree(headingPrev2Next + degreeCut * simbolFlag);

      if degreeCut > 45 then
        distance4Calc := distanceRouteX;
      else
        distance4Calc := 1000;
      end if;
    end if;

    if advisedHeading > 180 then
      advisedHeading := advisedHeading - 360;
    elseif advisedHeading < -180 then
      advisedHeading := advisedHeading + 360;
    end if;

    degree4Calc := advisedHeading - heading;
    if degree4Calc > 180 then
      degree4Calc := degree4Calc - 360;
    elseif degree4Calc < -180 then
      degree4Calc := degree4Calc + 360;
    end if;

    (advisedThrottle,advisedRudder) := USV.Components.Navigation.Functions.toPercent(distance4Calc, degree4Calc);
  end NavSys;

end Navigation;