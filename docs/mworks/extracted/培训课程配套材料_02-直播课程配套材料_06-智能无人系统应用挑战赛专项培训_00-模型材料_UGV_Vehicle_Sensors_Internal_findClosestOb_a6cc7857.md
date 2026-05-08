# findClosestObs.mo

- Source: `培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/00-模型材料/UGV/Vehicle/Sensors/Internal/findClosestObs.mo`
- Category: `quadrotor_uav`
- Score: `70`
- Size: `0.00 MB`
- Extract mode: `text`

## Extracted Text

```text
﻿function findClosestObs "寻找最近障碍物"
  annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
  input Real x;
  input Real y;  //输入：当前小车的坐标
  input Real[:] obs_x;
  input Real[:] obs_y;  //输入：障碍物点数组
  input Real yaw;  //输入：偏航角
  //output Integer closest_obs_index;  //输出：最近障碍物点的索引
  output Real vec_seg[2];  //输出：障碍物到小车的向量
protected
  Integer n = size(obs_x, 1);  //障碍点总数
  Real min_dist = Modelica.Constants.inf;  //最小距离初始值
  Real dx;
  Real dy;
  Real dist_sq;
  Real vec_obsW[2];  // 最近障碍物到小车的向量,世界系
  Real vec_obsB[2];  // 最近障碍物到小车的向量,本体系
  Integer closest_obs_index;  //最近障碍物点的索引
algorithm
  // 遍历所有障碍物
  for i in 1:n loop
    // 步骤1：计算障碍物到小车的向量
    dx := obs_x[i] - x;
    dy := obs_y[i] - y;
    vec_obsW := {dx, dy};

    // 步骤2： 坐标系转换，世界→本体
    vec_obsB[1] := cos(yaw) * vec_obsW[1] + sin(yaw) * vec_obsW[2];
    vec_obsB[2] := -sin(yaw) * vec_obsW[1] + cos(yaw) * vec_obsW[2];

    // 步骤3： 计算平方距离（避免开方提高效率）
    dist_sq := vec_obsB[1] ^ 2 + vec_obsB[2] ^ 2;

    // 步骤3： 更新最近障碍物点记录
    if (dist_sq < min_dist) then
      min_dist := dist_sq;
      closest_obs_index := i;
      vec_seg := {vec_obsB[1], vec_obsB[2]};
    end if;
  end for;
end findClosestObs;
```
