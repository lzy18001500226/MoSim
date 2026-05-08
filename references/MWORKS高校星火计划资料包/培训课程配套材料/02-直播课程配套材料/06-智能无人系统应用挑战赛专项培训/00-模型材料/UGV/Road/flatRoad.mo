block flatRoad "平坦道路"
  extends UGV.Utilities.Icons.road;
  parameter Boolean direction = true "true: 道路正方向为x+";
  parameter Modelica.Units.SI.Position x_start = 0 "道路起始x值";
  parameter Modelica.Units.SI.Length L0 = 2 "平整道路长度,仅应用于可视化";
  parameter Modelica.Units.SI.Distance B0 = 2 "平整道路宽度,仅应用于可视化";

  constant Real h = -0.365 "道路高度";
  constant Real mue = 1 "道路摩擦系数";
  String Name = "道路模型" annotation(Dialog);
  //xy方向单调递增常量数组，用于函数缺省值0315
  constant Real mapZ0[:,:] = {{0, 1, 2, 3}, {0, 0, 0, 0}, {1, 0, 0, 0}, {2, 0, 0, 0}, {3, 0, 0, 0}};
  constant Real mapMu0[:,:] = {{0, 1, 2, 3}, {0, 1, 1, 1}, {1, 1, 1, 1}, {2, 1, 1, 1}, {3, 1, 1, 1}};
  constant Real mapN0[:,:] = {{0, 1, 2, 3}, {0, 1, 1, 1}, {1, 1, 1, 1}, {2, 1, 1, 1}, {3, 1, 1, 1}};


  final parameter Real roadMap[:,:] = {{0, 1, 2}, {1, 0, 0}, {2, 0, 0}} 
    "纵向第一列为x方向，横向第一排为y方向，表格内表示各个（x，y）下的高度z";

  //摩擦系数信息roadMuMap
  final parameter Real roadMUEMap[:,:] = {{0, 1, 2}, {1, 0, 0}, {2, 0, 0}} "纵向第一列为x方向，横向第一排为y方向，表格内表示各个（x，y）下的摩擦系数mue";

  constant Integer N1 = size(roadMap, 1);
  constant Integer N2 = size(roadMap, 2);
  final parameter Real road_N_Map1[:,:] = MapNVector(roadMap, N1, N2, 1);
  final parameter Real road_N_Map2[:,:] = MapNVector(roadMap, N1, N2, 2);
  final parameter Real road_N_Map3[:,:] = MapNVector(roadMap, N1, N2, 3);
  final parameter Real roadMap_Cali[:,:] = roadMap_Calibration(roadMap, N1, N2);
  //修正readMap，以用于查表LZZ
  function roadMap_Calibration "路网"
    input Real x[:,:];
    input Integer N1;
    input Integer N2;
    output Real roadMap_Cali[N1,N2];
    annotation(Protection(access=Access.diagram));
  algorithm
    for i in 1:N1 loop
      roadMap_Cali[i,1] := -x[i,1];
    end for;
    for j in 2:N2 loop
      for i in 1:N1 loop
        roadMap_Cali[i,j] := x[i,j];
      end for;
    end for;
  end roadMap_Calibration;
  //求每个点的法向量,n[1],n[2],n[3]分别保存在三个表格中
  function MapNVector "生成法向量"
    input Real x[:,:];
    input Integer N1;
    input Integer N2;
    input Integer D;  //法向量第D个值
    output Real roadMap_NVector[N1,N2];
  protected
    Real A[3];
    Real B[3];
    Real n[3];
    annotation(Protection(access=Access.diagram));
  algorithm
    if D == 1 or D == 2 then
      roadMap_NVector[1,1] := 0;
      roadMap_NVector[N1,N2] := 0;
      //给定Y坐标和最后一排向量为0
      for j in 2:N2 loop
        roadMap_NVector[1,j] := x[1,j];
        roadMap_NVector[N1 - 1,j] := 0;
      end for;
      //给定坐标和最后一列向量为0
      for i in 2:N1 loop
        roadMap_NVector[i,1] := -x[i,1];
        roadMap_NVector[i,N2] := 0;
      end for;
    //D == 3 n[z]
    else
      roadMap_NVector[1,1] := 1;
      roadMap_NVector[N1,N2] := 1;
      //给定Y坐标和最后一排向量为0
      for j in 2:N2 loop
        roadMap_NVector[1,j] := x[1,j];
        roadMap_NVector[N1 - 1,j] := 1;
      end for;
      //给定坐标和最后一列向量为0
      for i in 2:N1 loop
        roadMap_NVector[i,1] := -x[i,1];
        roadMap_NVector[i,N2] := 1;
      end for;
    end if;
    //中间个点法向量    
    for j in 2:N2 - 1 loop
      for i in 2:N1 - 1 loop
        A[1] := x[i,1] - x[i,1];
        A[2] := x[1,j + 1] - x[1,j];
        A[3] := x[i,j + 1] - x[i,j];

        B[1] := x[i + 1,1] - x[i,1];
        B[2] := x[1,j] - x[1,j];
        B[3] := x[i + 1,j] - x[i,j];

        n := cross(A, B);
        roadMap_NVector[i,j] := n[D];
      end for;
    end for;
  end MapNVector;


  TYBase.Mechanics.MultiBody.Visualizers.VisualShape section1(
    Height = 0.01, 
    r0 = {x_start, 0, h}, 
    Length = if direction then L0 else -L0, 
    Width = if direction then B0 else -B0, 
    Material = {1000, 1000, 1000, 1} * 0.1) 
    annotation(extent = [-72, 30; -52, 50], 
    Placement(transformation(origin = {-92.0, 50.0}, 
    extent = {{-22.0, -22.0}, {22.0, 22.0}})));

  function getZ "获得道路高度"
    input Modelica.Units.SI.Position x;
    input Modelica.Units.SI.Position y;
    input Real roadMap[:,:] = mapZ0;  //0315
    output Modelica.Units.SI.Position z;
  algorithm
    z := h;
    annotation(Protection(access=Access.diagram));
  end getZ;

  function getMue "获得道路摩擦系数"
    input Modelica.Units.SI.Position x;
    input Modelica.Units.SI.Position y;
    input Real roadMueMap[:,:] = mapMu0;  //0315
    output Real mu;
  algorithm
    mu := mue;
    annotation(Protection(access=Access.diagram));
  end getMue;

  function getNVector "获得道路法向量"
    input Modelica.Units.SI.Position x;
    input Modelica.Units.SI.Position y;
    input Real road_N_Map1[:,:] = mapZ0;  //0315
    input Real road_N_Map2[:,:] = mapZ0;  //0315
    input Real road_N_Map3[:,:] = mapN0;  //0315
    output Real n[3];
  algorithm
    n := {0, 0, 1};
    annotation(Protection(access=Access.diagram));
  end getNVector;
equation
  section1.S = identity(3);
  section1.r = {0, 0, 0};
  annotation(Diagram(coordinateSystem(extent = {{-140.0, -100.0}, {140.0, 100.0}}, 
    preserveAspectRatio = false, 
    grid = {2.0, 2.0})), defaultComponentPrefixes = "inner", 
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Text(origin = {4.44089e-15, -133.306}, 
    rotation = 180, 
    extent = {{-100, 30}, {100, -30}}, 
    textString = "%Name", 
    fontName = "微软雅黑", 
    textStyle = {TextStyle.None})}), 
    Protection(access=Access.diagram), 
    Documentation(link="modelica://TADynamics/Resource/Doc/flatRoad.html"), 
    defaultComponentName = "road", 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, -0.10000000000000142}, 
    extent = {{-100.0, 40.1}, {100.0, -40.1}}), Polygon(origin = {-0.10000000000000142, -1.2999999999999972}, 
    lineColor = {128, 128, 128}, 
    fillColor = {128, 128, 128}, 
    fillPattern = FillPattern.Solid, 
    points = {{-24.9, 37.5}, {-99.1, -18.700000000000003}, {-99.1, -37.5}, {99.1, -37.5}, {99.1, -18.700000000000003}, {20.1, 37.5}, {-24.9, 37.5}}), Polygon(origin = {0.2999999999999998, -17.0}, 
    lineColor = {192, 192, 192}, 
    fillColor = {192, 192, 192}, 
    fillPattern = FillPattern.Solid, 
    points = {{-7.5, -17.0}, {7.5, -17.0}, {4.1000000000000005, 17.0}, {-4.5, 17.0}, {-7.5, -17.0}}), Polygon(origin = {0.0, 23.0}, 
    lineColor = {192, 192, 192}, 
    fillColor = {192, 192, 192}, 
    fillPattern = FillPattern.Solid, 
    points = {{-3.2, -7.0}, {3.2, -7.0}, {2.0, 7.0}, {-2.0, 7.0}, {-3.2, -7.0}}), Text(origin = {0.0, 70.0}, 
    extent = {{-100.0, 30.0}, {100.0, -30.0}}, 
    textString = "%name")}), 
    Protection(access = Access.diagram));
end flatRoad;