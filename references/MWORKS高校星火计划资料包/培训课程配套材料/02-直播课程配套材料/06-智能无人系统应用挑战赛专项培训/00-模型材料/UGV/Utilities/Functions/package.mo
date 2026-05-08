package Functions "函数库"
  annotation(__MWORKS(version="2025a"),Protection(access=Access.diagram));
  function ackermann_geometry "阿克曼转向几何计算"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    input Real delta;
    input Real L;
    input Real W;
    output Real delta_inner;
    output Real delta_outer;
  protected
    SI.Length R;
    SI.Angle delta_threshold = 1e-9;
  algorithm
    if abs(delta) < delta_threshold then
      // 直线行驶模式
      delta_inner := 0;
      delta_outer := 0;
    else
      if delta > 0 then
        R := L / max(tan(delta), eps);
      else
        R := L / min(tan(delta), -eps);
      end if;
      delta_inner := atan(L / (R - W / 2)) "内侧轮转角";
      delta_outer := atan(L / (R + W / 2)) "外侧轮转角";
    end if;
    // 附加保护措施
    assert(abs(delta) > delta_threshold or abs(delta_inner + delta_outer) < 1e-6, 
      "直线行驶时转向角应归零", 
      AssertionLevel.warning);
  end ackermann_geometry;
  function angle_diff "角度差计算（-pi到pi）"
    annotation(__MWORKS(version="2025a"),Protection(access=Access.diagram));
    input Real target;
    input Real current;
    output Real diff;
  algorithm
    diff := mod((target - current),(2 * pi));
    if diff > pi then
      diff := diff - 2*pi;
    else
      diff := diff;
    end if;
  end angle_diff;

end Functions;