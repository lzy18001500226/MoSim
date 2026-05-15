package Internal "内部模型"
  annotation(__MWORKS(version="2025a"),Protection(access=Access.diagram));
  function calcLateralDistance "道路边缘距离计算"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    input Real[2] point "传感器全局坐标";
    input Real[:,3] road "道路坐标点信息";
    input Real width "道路宽度";
    input Boolean is_closed = false;
    output Real dist "距离";
    //
    output Integer idx;
    // output Real t;
     output Real e;
     output Real[2] proj;
    // output Real left_dist "到左侧边缘距离";
    // output Real right_dist "到右侧边缘距离";
     protected
     // Integer idx;
      Real t;
      //Real e;
      //Real[2] proj;
      Real left_dist "到左侧边缘距离";
      Real right_dist "到右侧边缘距离";
  algorithm
    // 1. 寻找最近道路段
    (idx,t,proj) := findClosestPoint(point[1], point[2], road[:,1], road[:,2], is_closed);

    // 2. 计算横向偏差
    e := sqrt((point[1] - proj[1]) ^ 2 + (point[2] - proj[2]) ^ 2);

    // 3.确定左右侧
    if crossProduct(road, point, proj, idx) > 0 then
      left_dist := width / 2 - e;
      right_dist := width / 2 + e;
    else
      left_dist := width / 2 + e;
      right_dist := width / 2 - e;
    end if;

    // 4.给出距离
    dist := min(left_dist, right_dist);
  end calcLateralDistance;
  function findClosestPoint "寻找最近点"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    input Real x;
    input Real y;  //输入：当前点的坐标
    input Real[:] path_x;
    input Real[:] path_y;  //输入：道路中心线路径点数组
    input Boolean is_closed = false "路径是否闭合（环形）";
    output Integer closest_segment_index;  //输出：最近线段的索引
    output Real t;  //输出：在线段上的参数化位置[0,1]
    output Real[2] closest_point;  //输出：投影点坐标[x_p,y_p]
  protected
    Integer n = size(path_x, 1);  //路径点总数
    Real min_dist = Modelica.Constants.inf;  //最小距离初始值
    Real dx;
    Real dy;
    Real px;
    Real py;
    Real seg_length;
    Real dot_proj;
    Real t_temp;
    Real dist_sq;
    Real[2] vec_seg;
    Real[2] vec_point;
    Integer i_next;
    Integer idx;
  algorithm
    // 检验路径有效性
    assert(n >= 2, "路径至少需要两个点", AssertionLevel.error);
    // 遍历所有路径段（相邻点组成的线段）
    for i in 1:(n - 1 + (if is_closed then 1 else 0)) loop
      i_next := if i <= n - 1 then i + 1 else 1;  //闭合路径处理
      idx := if i <= n then i else 1;
      // 步骤1：计算段向量
      dx := path_x[i_next] - path_x[idx];
      dy := path_y[i_next] - path_y[idx];
      vec_seg := {dx, dy};
      seg_length := sqrt(dx * dx + dy * dy);

      // 处理零长度线段（两点重合）
      if seg_length < 1e-6 then
        dist_sq := (x - path_x[idx]) ^ 2 + (y - path_y[idx]) ^ 2;
        if dist_sq < min_dist then
          min_dist := dist_sq;
          closest_segment_index := idx;
          closest_point := {path_x[idx], path_y[idx]};
          t := 0.0;
        end if;
      end if;

      // 步骤2： 计算点到线段的向量投影
      vec_point := {x - path_x[idx], y - path_y[idx]};
      dot_proj := vec_point[1] * dx + vec_point[2] * dy;  //向量点积
      t_temp := dot_proj / (seg_length * seg_length);

      // 步骤3： 约束投影参数t在[0,1]范围内
      if not is_closed and idx == n - 1 then
        t_temp := max(0.0, t_temp);
      else
        t_temp := max(0.0, min(1.0, t_temp));
      end if;


      // 步骤4： 计算投影点坐标

      px := path_x[idx] + t_temp * dx;
      py := path_y[idx] + t_temp * dy;

      // 步骤5： 计算平方距离（避免开方提高效率）
      dist_sq := (x - px) ^ 2 + (y - py) ^ 2;

      // 步骤6： 更新最近线段记录
      if (dist_sq < min_dist) or 
        (abs(dist_sq - min_dist) < 1e-6 and t_temp > t) 
        then
        min_dist := dist_sq;
        closest_segment_index := idx;
        closest_point := {px, py};
        t := t_temp;
      end if;
    end for;
  end findClosestPoint;
  function crossProduct "向量叉积"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    input Real[:,3] road;  //当前道路段
    input Real[2] point;  //传感器点坐标[x,y]
    input Real[2] proj;  //投影点坐标[x_p,y_p]
    input Integer closest_segment_index;  //最近点
    output Real cross;  //叉积结果
  protected
    Integer i = closest_segment_index;  //从最近点搜素获得
    Real road_vec_x;
    Real road_vec_y;
    Real point_vec_x;
    Real point_vec_y;  //道路方向向量
  algorithm
    // 获取当前道路段的向量
    road_vec_x := road[i + 1,1] - road[i,1];
    road_vec_y := road[i + 1,2] - road[i,2];

    // 计算点到投影的向量
    point_vec_x := point[1] - proj[1];
    point_vec_y := point[2] - proj[2];

    // 二维叉积计算（返回三维z分量）
    cross := road_vec_x * point_vec_y - road_vec_x * point_vec_x;
  end crossProduct;
  function safetyField "安全距离场计算"
    annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
    input Real dist_front;
    input Real dist_rear;
    input Real dist_left;
    input Real dist_right;
    //input Real max_steer;
    output Real safe_speed "安全速度";
    output Real steer_safe "转向角";
  protected
    Real dead_zone = 0;  // 死区阈值（rad）0.8*轮距/轴距
    Real steer_angle;
    Real wrapped_angle;  //归一化处理
  algorithm
    //速度决策逻辑
    safe_speed := if dist_front < 0.3 then 0.0 
      else if dist_front < 0.5 then 0.5 
      else 1.0;
    //safe_speed := 3;
    //转向决策逻辑
    if dist_left < dist_right then
      steer_angle := -2 * (1 / dist_right + 0.1) * abs(dist_left - dist_right);
    elseif dist_left > dist_right then
      steer_angle := 2 * (1 / dist_left + 0.1) * abs(dist_left - dist_right);
    else
      steer_angle := 0;
    end if;

    //归一化处理
    wrapped_angle := steer_angle - 2 * pi * floor((steer_angle + pi) / (2 * pi));

    //小偏差不响应
    if abs(wrapped_angle) < dead_zone then
      steer_safe := 0;
    else
      steer_safe := wrapped_angle;
    end if;
  end safetyField;
end Internal;