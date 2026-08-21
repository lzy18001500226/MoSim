within MoSimQuadrotorModel.Vehicle;
package GroundModel "地面模型"

  model TouchModel "接触模型"
    //接触参数设定
    import SI = Modelica.SIunits;
    parameter Real n(unit = "1") = 1.5 "非线性指数" 
      annotation (Dialog(group = "接触参数设置", enable = ForceType == 2));
    parameter Modelica.Units.SI.Distance delta(displayUnit = "mm") = 0.0001 "穿透深度阈值" 
      annotation (Dialog(group = "接触参数设置", enable = ForceType == 2));
    parameter Modelica.Units.SI.TranslationalDampingConstant C = 10000 "接触阻尼" 
      annotation (Dialog(group = "接触参数设置", enable = ForceType == 2));
    parameter Modelica.Units.SI.TranslationalSpringConstant K = 1e5 "接触刚度" 
      annotation (Dialog(group = "接触参数设置", enable = ForceType == 2));
    parameter Modelica.Units.SI.Radius R1 = 0.001 "接触半径" 
      annotation (Dialog(group = "接触参数设置", enable = ForceType == 2));
    //摩擦力参数设定
    parameter Modelica.Units.SI.Velocity V_s = 0 "最大静摩擦对应的相对滑移速度" 
      annotation (Dialog(group = "摩擦力参数", enable = ForceType == 2));
    parameter Modelica.Units.SI.CoefficientOfFriction Cst = 0 "静摩擦系数" 
      annotation (Dialog(group = "摩擦力参数", enable = ForceType == 2));
    parameter Modelica.Units.SI.Velocity Vtr = 0 "动摩擦对应的相对滑移速度" 
      annotation (Dialog(group = "摩擦力参数", enable = ForceType == 2));
    parameter Modelica.Units.SI.CoefficientOfFriction Cdy = 0 "动摩擦系数" 
      annotation (Dialog(group = "摩擦力参数", enable = ForceType == 2));
    //状态变量定义
    Modelica.Units.SI.Position P[3] "两物体质心相对位置矢量";
    Modelica.Units.SI.Force F[3] "接触弹力矢量值";
    Modelica.Units.SI.Force f[3] "接触摩擦力矢量值";
    Modelica.Units.SI.Force F_C "接触阻尼系数";
    Modelica.Units.SI.Velocity V[3] "接触点速度矢量";
    Modelica.Units.SI.Distance x "穿透深度";
    //模型实例化
    Modelica.Mechanics.MultiBody.Forces.WorldForce Fs(resolveInFrame=Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.frame_resolve) "合外力（除重力）" annotation (Placement(transformation(origin = {2.0, 0.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}},
        rotation = 360.0)));
    annotation (Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0})),
      Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
        grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0},
        lineColor = {0, 0, 255},
        fillColor = {255, 255, 255},
        fillPattern = FillPattern.Solid,
        extent = {{-100.0, 100.0}, {100.0, -100.0}}), Rectangle(origin = {0.0, -60.0},
        lineColor = {85, 85, 255},
        fillColor = {255, 255, 255},
        fillPattern = FillPattern.HorizontalCylinder,
        extent = {{-100.0, 40.0}, {100.0, -40.0}}), Rectangle(origin = {0.0, -80.0},
        fillColor = {255, 255, 255},
        pattern = LinePattern.None,
        fillPattern = FillPattern.Solid,
        extent = {{-100.0, 20.0}, {100.0, -20.0}}), Ellipse(origin = {1.0, 46.0},
        rotation = 90.0,
        lineColor = {0, 85, 255},
        fillColor = {0, 0, 0},
        fillPattern = FillPattern.Sphere,
        extent = {{-38.0, 39.0}, {38.0, -39.0}}), Text(origin = {0.0, 129.0},
        rotation = 360.0,
        lineColor = {0, 0, 0},
        extent = {{100.0, -35.0}, {-100.0, 35.0}},
        textString = "%name",
        textColor = {0, 0, 0}), Text(origin = {2.0, -123.0},
        rotation = 360.0,
        lineColor = {0, 0, 0},
        extent = {{100.0, -35.0}, {-100.0, 35.0}},
        textString = "点面接触模型",
        textStyle = {TextStyle.None},
        textColor = {0, 0, 0})}),__MWORKS(version="26.3.0"));
    Modelica.Mechanics.MultiBody.Sensors.RelativePosition R_p(resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameAB.frame_a)
      "相对位置矢量" annotation (Placement(transformation(origin = {0.0, 40.0},
        extent = {{-10.0, 10.0}, {10.0, -10.0}})));

    Modelica.Mechanics.MultiBody.Sensors.RelativeVelocity R_v(resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameAB.frame_a)
      "相对速度矢量" annotation (Placement(transformation(origin = {4.440892098500626e-16, -40.0},
        extent = {{10.0, 10.0}, {-10.0, -10.0}},
        rotation = 180.0)));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_a frame_a 
      annotation (Placement(transformation(origin = {-100.0, 0.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}},
        rotation = 180.0)));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_b frame_b 
      annotation (Placement(transformation(origin = {100.0, 0.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}},
        rotation = 180.0)));
    //方程
  equation
    //接触判定条件方程
    x = max((R1 - P[3]), 0);
    //接触阻尼方程
    F_C = MoSimQuadrotorModel.Vehicle.Utilities.Functions.Step(x, 0, 0, delta, C);
    //接触弹力方程
    F[1] = 0;
    F[2] = 0;
    F[3] = if x > 0 then max((K * x ^ n - F_C * V[3]), 0) else 0;
    //接触摩擦力方程
    f[1] = if abs(V[1]) > 0 then MoSimQuadrotorModel.Vehicle.Utilities.Functions.Friction(F[3], V[1], V_s, Cst, Vtr, Cdy) else 0;
    f[2] = if abs(V[2]) > 0 then MoSimQuadrotorModel.Vehicle.Utilities.Functions.Friction(F[3], V[3], V_s, Cst, Vtr, Cdy) else 0;
    f[3] = 0 * V[3];
    //参数传递方程
    V = R_v.v_rel;
    P = R_p.r_rel;
    F - f = Fs.force;
    //连接方程
    connect(Fs.frame_b, frame_b) 
      annotation (Line(origin = {56.0, 0.0},
        points = {{-44.0, 0.0}, {44.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(R_p.frame_b, frame_b) 
      annotation (Line(origin = {57.0, 13.0},
        points = {{-47.0, 27.0}, {3.0, 27.0}, {3.0, -13.0}, {43.0, -13.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(R_v.frame_b, frame_b) 
      annotation (Line(origin = {55.0, -24.0},
        points = {{-45.0, -16.0}, {5.0, -16.0}, {5.0, 24.0}, {45.0, 24.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(R_v.frame_a, frame_a) 
      annotation (Line(origin = {-55.0, -20.0},
        points = {{45.0, -20.0}, {-5.0, -20.0}, {-5.0, 20.0}, {-45.0, 20.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(R_p.frame_a, frame_a) 
      annotation (Line(origin = {-55.0, 20.0},
        points = {{45.0, 20.0}, {-5.0, 20.0}, {-5.0, -20.0}, {-45.0, -20.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(Fs.frame_resolve, frame_a) 
      annotation (Line(origin = {-49.0, -10.0},
        points = {{51.0, 0.0}, {51.0, -10.0}, {-11.0, -10.0}, {-11.0, 10.0}, {-51.0, 10.0}},
        color = {95, 95, 95},
        pattern = LinePattern.Dot));
  end TouchModel;
  annotation (Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0})),
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      preserveAspectRatio = false,
      grid = {2.0, 2.0}), graphics = {Line(origin = {2.0, 0.0},
      points = {{-62.0, 0.0}, {62.0, 0.0}}), Line(origin = {0.0, -20.0},
      points = {{-40.0, 0.0}, {40.0, 0.0}}), Line(origin = {0.0, -40.0},
      points = {{-20.0, 0.0}, {20.0, 0.0}}), Ellipse(origin = {1.0, 21.0},
      fillColor = {255, 255, 255},
      extent = {{-21.0, 21.0}, {21.0, -21.0}})}));
  extends Modelica.Icons.Package;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end GroundModel;