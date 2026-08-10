within MoSimQuadrotorModel.Vehicle;
package Utilities "附件"
  extends Modelica.Icons.UtilitiesPackage;



  package Functions "函数库"
    extends Modelica.Icons.Package;
    extends Modelica.Icons.FunctionsPackage;
    function Step "三次阶跃函数"
      extends Modelica.Icons.Function;
      input Real x "自变量，可以是时间或时间的任一函数";
      input Real x_0 "自变量的STEP函数开始值，可以是常数或函数表达式或设计变量";
      input Real h_0 "STEP函数的初始值，可以是常数或函数表达式或设计变量";
      input Real x_1 "自变量的STEP函数结束值，可以是常数或函数表达式或设计变量";
      input Real h_1 "STEP函数的最终值，可以是常数或函数表达式或设计变量";
      output Real y "函数输出值";
    algorithm
      y := if x <= x_0 then h_0 else if x > x_0 and x < x_1 then h_0 + ((h_1 - h_0) * ((x - x_0) / (x_1 - x_0)) ^ 2) * (3 - 2 * ((x - x_0) / (x_1 - x_0))) else h_1;
    end Step;
    function Friction "摩擦力"
      extends Modelica.Icons.Function;
      import SI = Modelica.SIunits;
      //输入参数
      input Modelica.Units.SI.Force N "法向载荷";
      input Modelica.Units.SI.Velocity V "相对滑移速度";
      input Modelica.Units.SI.Velocity V_s "最大静摩擦对应的相对滑移速度";
      input Modelica.Units.SI.CoefficientOfFriction Cst "静摩擦系数";
      input Modelica.Units.SI.Velocity Vtr "动摩擦对应的相对滑移速度";
      input Modelica.Units.SI.CoefficientOfFriction Cdy "动摩擦系数";
      output Modelica.Units.SI.Force F_f "摩擦力";
      //中间变量
    algorithm
      F_f := N * MoSimQuadrotorModel.Vehicle.Utilities.Functions.Step(V, -V_s, -1, V_s, 1) * MoSimQuadrotorModel.Vehicle.Utilities.Functions.Step(abs(V), V_s, Cst, Vtr, Cdy);
    end Friction;
  end Functions;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Utilities;