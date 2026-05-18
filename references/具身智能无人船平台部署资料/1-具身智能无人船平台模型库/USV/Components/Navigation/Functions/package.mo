package Functions "内部函数"
  annotation(__MWORKS(version="2025a"));
  function formatDegree
    annotation(__MWORKS(version="2025a"));
    input Real degree;
    output Real result;
  algorithm
    result := mod(degree,360.0);
  end formatDegree;
  function headingAB
    annotation(__MWORKS(version = "2025a"));
    input Real lngA;
    input Real latA;
    input Real lngB;
    input Real latB;
    output Real headingDegree;
  protected
    Real deltaLng;
    Real deltaLat;
    Real angle;
    Real headingRad;
    Real pi2;
    Real times;
  algorithm
    deltaLng := lngB - lngA;
    deltaLat := latB - latA;
    angle := atan2(deltaLat, deltaLng);
    headingRad := pi / 2 - angle;
    pi2 := pi * 2;

    // if angle > pi2 or angle < -pi2 then
    //   times := rem(angle,pi2);
    //   headingRad := headingRad - times * pi2;
    // end if;

    // if headingRad < 0 then
    //   headingRad := headingRad + pi2;
    // end if;

    headingRad := mod(headingRad,pi2);
    headingDegree := headingRad * 180 / pi;
  end headingAB;
  function calcGPSDistance
    annotation(__MWORKS(version = "2025a"));
      input Real lng1;
      input Real lat1;
      input Real lng2;
      input Real lat2;
      output Real s;
    protected
      Real a;
      Real b;
      constant Real EARTH_RADIUS = 6378.137; //#km
    algorithm
      a := d2r(lat1) - d2r(lat2);
      b := d2r(lng1) - d2r(lng2);
      s := 2 * asin(sqrt(sin(a/2)^2 + cos(d2r(lat1)) * cos(d2r(lat2)) * sin(b/2)^2));
      s := s * EARTH_RADIUS * 1000;
      s := USV.Utilities.Math.Functions.roundToNDecimal(s,1);
  //   input Real lng1;
  //   input Real lat1;
  //   input Real lng2;
  //   input Real lat2;
  //   output Real s;
  // protected
  //   Real radLat1;
  //   Real radLat2;
  //   Real a;
  //   Real b;
  //   constant Real EARTH_RADIUS = 6378137;  // WGS84地球赤道半径(单位:m)
  // algorithm
  //   // 角度转弧度
  //   radLat1 := lat1 * Modelica.Constants.pi / 180;
  //   radLat2 := lat2 * Modelica.Constants.pi / 180;

  //   // 经纬度差值
  //   a := radLat1 - radLat2;
  //   b := (lng1 - lng2) * Modelica.Constants.pi / 180;

  //   // Haversine公式计算球面距离
  //   s := 2 * Modelica.Math.asin(
  //     sqrt(
  //     Modelica.Math.sin(a / 2) ^ 2 + 
  //     Modelica.Math.cos(radLat1) * Modelica.Math.cos(radLat2) * Modelica.Math.sin(b / 2) ^ 2
  //     )
  //     );

  //   // 转换为米并四舍五入
  //   s := EARTH_RADIUS * s;
  //   s := USV.Utilities.Math.Functions.roundToNDecimal(s,1);
  end calcGPSDistance;
  function calcDegreeCutByDistance
    annotation(__MWORKS(version = "2025a"));
    input Real absDistance2Route;
    output Real cutDegree;
  protected
    Real x;
    Real x2;
  algorithm
    x := absDistance2Route;
    x2 := absDistance2Route * absDistance2Route;
    cutDegree := -0.008316 * x2 + 2.023147 * x;
    if cutDegree < 0 then
      cutDegree := 0;
    end if;
    if cutDegree > 90 then
      cutDegree := 90;
    end if;
  end calcDegreeCutByDistance;
  function toPercent
    annotation(__MWORKS(version = "2025a"));
    input Real shipToNextWPDistance;
    input Real shipHeadingToB;
    output Real speedPercent;
    output Real rotatePercent;
  protected
    constant Real MAX_SPEED = 5;  //#m/s
    constant Real MAX_ROTATE = 40;  //#degree
    Real distance;
    Real heading;
  algorithm
    speedPercent := 1; // [-100,100]
    rotatePercent := 1; //[-100,100]
    distance := shipToNextWPDistance;
    heading := shipHeadingToB;

    if shipToNextWPDistance < 0 then
      speedPercent := -1;
    end if;
    if shipHeadingToB < 0 then
      rotatePercent := -1;
    end if;

    if abs(shipToNextWPDistance) > MAX_SPEED then
      distance := MAX_SPEED * speedPercent;
    end if;
    if abs(shipHeadingToB) > MAX_ROTATE then
      distance := distance /4;
      heading := MAX_ROTATE * rotatePercent;
    end if;

    rotatePercent := floor(heading * 100 / MAX_ROTATE); //[-100,100]
    speedPercent := floor(distance * 100 / MAX_SPEED); //[-100,100]
  end toPercent;
end Functions;