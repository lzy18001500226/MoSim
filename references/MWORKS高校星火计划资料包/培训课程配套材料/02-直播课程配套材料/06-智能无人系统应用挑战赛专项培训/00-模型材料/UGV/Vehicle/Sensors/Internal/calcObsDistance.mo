function calcObsDistance "障碍物距离计算"
  annotation(__MWORKS(version = "2025a"),Protection(access=Access.diagram));
  input Real[2] point "传感器全局坐标";
  input Real[:,3] obs "障碍物坐标点信息";
  input Real yaw "小车偏航角";
  output Real distF "前向距离";
  output Real distB "后向距离";
  output Real distL "左侧距离";
  output Real distR "右侧距离";
  output Real vec_obsB[2] "最近障碍物到小车的向量,本体系";
protected
  parameter Real L = 0.11 "轴距";
  parameter Real W = 0.165 "轮距";

  //Integer idx;  // 最近点索引
  //Real vec_obsW[2];  // 最近障碍物到小车的向量,世界系
  //Real vec_obsB[2];  // 最近障碍物到小车的向量,本体系
algorithm
  // 1. 寻找最近障碍物
  vec_obsB := findClosestObs(point[1], point[2], obs[:,1], obs[:,2], yaw);

  // // 2. 坐标系转换，世界→本体
  // vec_obsB[1] := cos(yaw) * vec_obsW[1] + sin(yaw) * vec_obsW[2];
  // vec_obsB[2] := -sin(yaw) * vec_obsW[1] + cos(yaw) * vec_obsW[2];

  // 3.给出距离
  distF := vec_obsB[1] - L / 2;
  distL := vec_obsB[2] - W / 2;
  distR := vec_obsB[2] + W / 2;
  distB := vec_obsB[1] + L / 2;



end calcObsDistance;