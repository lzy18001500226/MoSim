function calcDistance "距离计算"
  annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
  input Real[2] point "传感器全局坐标";
  input Real[3] path "道路坐标点信息";
  input Real yaw "小车偏航角";
  output Real distF "前向距离";

  parameter Real L = 0.11 "轴距";
  //parameter Real W = 0.165 "轮距";
  //Integer idx;  // 最近点索引
  //Real vec_obsW[2];  // 最近障碍物到小车的向量,世界系
  //Real vec_obsB[2];  // 最近障碍物到小车的向量,本体系
protected
  Real vecB[2];  // 最近点到小车的向量,本体系
algorithm
  // 1. 寻找目标
  vecB := findPoint(point[1], point[2], path[1], path[2], yaw);

  // 3.给出距离
  distF := vecB[1] - L / 2;

end calcDistance;