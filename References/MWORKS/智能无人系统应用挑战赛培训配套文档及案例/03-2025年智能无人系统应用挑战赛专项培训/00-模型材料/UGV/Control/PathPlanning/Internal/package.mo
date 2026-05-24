package Internal "内部模型"
  annotation(__MWORKS(version="2025a"),Protection(access=Access.diagram));
  function findClosestSegment "找到距离当前位置最近的路径段"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    input Real x;
    input Real y;
    input Real[:,3] path;
    output Integer closest_index = 1;
    output Real path_progress;
  protected
    Real min_dist = Modelica.Constants.inf;
    Real dist;
    Real seg_progress;
    Real[2] projection;
    Integer n = size(path, 1);
  algorithm
    // 校验路径有效性
    assert(n >= 2, "路径至少需要两个点", AssertionLevel.error);

    for i in 1:n - 1 loop
      (dist,seg_progress,projection) := UGV.Control.PathPlanning.Internal.pointToSegmentDistance(
        {x, y}, 
        {path[i,1], path[i,2]}, 
        {path[i + 1,1], path[i + 1,2]});

      if dist < min_dist then
        min_dist := dist;
        closest_index := i;
        path_progress := seg_progress;
      end if;
    end for;
  end findClosestSegment;
  function calculatePursuitPoint "沿路径计算前瞻点"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    input Real[:,3] path;
    input Integer start_index;
    input Real start_progress;
    input Modelica.Units.SI.Length lookahead;
    output Real[2] pursuit_point;
  protected
    Real remaining = lookahead;
    Integer current_index = start_index;
    Real current_progress = start_progress;
    Real seg_length;
    Real dx;
    Real dy;
  algorithm
    while remaining > 0 and current_index < size(path, 1) loop
      dx := path[current_index + 1,1] - path[current_index,1];
      dy := path[current_index + 1,2] - path[current_index,2];
      seg_length := sqrt(dx * dx + dy * dy);

      if (seg_length * (1 - current_progress)) >= remaining then
        pursuit_point := {
          path[current_index,1] + dx * (current_progress + remaining / seg_length), 
          path[current_index,2] + dy * (current_progress + remaining / seg_length)};
        remaining := 0;
      else
        remaining := remaining - seg_length * (1 - current_progress);
        current_index := current_index + 1;
        current_progress := 0;
      end if;
    end while;
  end calculatePursuitPoint;
  function interpolateSpeed "速度插值函数"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    input Real[:,3] path;
    input Integer index;
    input Real t;
    output Modelica.Units.SI.Velocity v;
  algorithm
    if index >= size(path, 1) then
      v := path[end,3];
    else
      v := path[index,3] + t * (path[index + 1,3] - path[index,3]);
    end if;
  end interpolateSpeed;
  function purePursuitControl "Pure Pursuit转向控制算法"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    input Real x;
    input Real y;
    input Real tx;
    input Real ty;
    output Modelica.Units.SI.Angle delta;
  algorithm
    delta := atan2(ty - y, tx - x);  // 目标点全局角度
  end purePursuitControl;
  function pointToSegmentDistance "计算点到线段的最短距离"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    input Real[2] point;
    input Real[2] segStart;
    input Real[2] segEnd;
    output Real distance;
    output Real t_param;
    output Real[2] projection;
  protected
    Real[2] vec_seg = segEnd - segStart;
    Real segLength = sqrt(vec_seg * vec_seg);
    Real[2] vec_point = point - segStart;
    Real t;
  algorithm
    if segLength < 1e-6 then  // 处理零长度线段
      distance := sqrt((point - segStart) * (point - segStart));
      t_param := 0;
      projection := segStart;
    else
      t := (vec_point * vec_seg) / (segLength * segLength);
      t := max(0, min(1, t));  // 限制在[0,1]范围内
      projection := segStart + t * vec_seg;
      distance := sqrt((point - projection) * (point - projection));
      t_param := t;
    end if;
  end pointToSegmentDistance;






















































end Internal;