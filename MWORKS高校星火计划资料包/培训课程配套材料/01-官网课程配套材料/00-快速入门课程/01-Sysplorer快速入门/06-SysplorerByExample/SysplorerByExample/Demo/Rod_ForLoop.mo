model Rod_ForLoop"使用 for 循环对杆内的热传导进行建模"
  annotation(__MWORKS(version="2025b"));
  import SI = Modelica.Units.SI;
  //定义单位
  type ConvectionCoefficient=Real(final quantity=" ConvectionCoefficient", final unit="W/K");
  type ConductionCoefficient=Real(final quantity="ConductionCoefficient", final unit="W.m-1.K-1");


  //定义常数
  constant Real pi = 3.14159;

  //定义参数
  parameter Integer n=10"对传热棒分段的段数";
  parameter SI.Length L=1.0"传热棒长度";
  parameter SI.Radius R=0.1 "传热棒半径";
  parameter SI.Density rho=2.0"材料密度";
  parameter ConvectionCoefficient h=2.0 "对流系数";
  parameter ConductionCoefficient k=10 "传导系数";
  parameter SI.SpecificHeatCapacity C=10.0 "比热";
  parameter SI.Temperature Tamb(displayUnit="K")=300 "环境温度";
  parameter SI.Area A = pi*R^2 "传热棒截面积";
  parameter SI.Volume V = A*L/n "每一节传热棒体积";

  //定义变量
  SI.Temperature T[n];

initial equation
  T = linspace(200,300,n);
equation
  rho*V*C*der(T[1]) = -h*(T[1]-Tamb)-k*A*(T[1]-T[2])/(L/n);
  for i in 2:(n-1) loop
    rho*V*C*der(T[i]) = -k*A*(T[i]-T[i-1])/(L/n)-k*A*(T[i]-T[i+1])/(L/n);
  end for;
  rho*V*C*der(T[end]) = -h*(T[end]-Tamb)-k*A*(T[end]-T[end-1])/(L/n);
  // rho*V*C*der(T[1]) = -h*(T[1]-Tamb)-k*A*(T[1]-T[2])/(L/n);
  // rho*V*C*der(T[2:n-1]) = -k*A*(T[2:n-1]-T[1:n-2])/(L/n)-k*A*(T[2:n-1]-T[3:n])/(L/n);
  // rho*V*C*der(T[end]) = -h*(T[end]-Tamb)-k*A*(T[end]-T[end-1])/(L/n);

end Rod_ForLoop;