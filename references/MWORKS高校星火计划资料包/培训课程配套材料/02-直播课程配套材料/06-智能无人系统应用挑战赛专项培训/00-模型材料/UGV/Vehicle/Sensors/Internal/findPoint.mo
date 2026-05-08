function findPoint "寻找坐标点"
  annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
  input Real x;
  input Real y;  //输入：当前小车的坐标
  input Real obs_x;
  input Real obs_y;  //输入：障碍物点数组
  input Real yaw;  //输入：偏航角
  //output Integer closest_obs_index;  //输出：最近障碍物点的索引
  output Real vec_seg[2];  //输出：障碍物到小车的向量
protected
  Real dx;
  Real dy;
  Real vec_obsW[2];  // 最近障碍物到小车的向量,世界系
  Real vec_obsB[2];  // 最近障碍物到小车的向量,本体系
algorithm
    // 步骤1：计算障碍物到小车的向量
    dx := obs_x - x;
    dy := obs_y - y;
    vec_obsW := {dx, dy};

    // 步骤2： 坐标系转换，世界→本体
    vec_obsB[1] := cos(yaw) * vec_obsW[1] + sin(yaw) * vec_obsW[2];
    vec_obsB[2] := -sin(yaw) * vec_obsW[1] + cos(yaw) * vec_obsW[2];

    // 步骤3： 输出向量
    vec_seg := {vec_obsB[1], vec_obsB[2]};

end findPoint;