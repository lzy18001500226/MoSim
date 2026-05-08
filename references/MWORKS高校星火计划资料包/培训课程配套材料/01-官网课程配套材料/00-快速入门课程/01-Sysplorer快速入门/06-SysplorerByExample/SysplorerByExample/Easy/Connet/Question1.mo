package Question1 "外部连接器"
  extends Modelica.Icons.Package;

  model Oil "油液模型"
    parameter Modelica.SIunits.Density Rio = 0.86 "油液密度";
    parameter Modelica.SIunits.Volume V = 10 "体积";
    parameter Modelica.SIunits.KinematicViscosity v = 41.4 "运动粘度";
    parameter Modelica.SIunits.DynamicViscosity miu = 20 "动力粘度";
    parameter Modelica.SIunits.Pressure p = 5 "饱和蒸汽压力";
    annotation (
      defaultComponentName = "oil",
      defaultComponentPrefixes = "inner");
  end Oil;
  model Component "读取油液的动力粘度和密度"
    outer Question1.Oil oil;
    Modelica.SIunits.Density Rio2 "油液密度";
    Modelica.SIunits.Volume V2 "体积";
    Modelica.SIunits.KinematicViscosity v2 "运动粘度";
    Modelica.SIunits.DynamicViscosity miu2 "动力粘度";
    Modelica.SIunits.Pressure p1 "饱和蒸汽压力";
  equation
    Rio2 = oil.Rio;
    miu2 = oil.miu;
    V2 = oil.V;
    v2 = oil.v;
    p1 = oil.p;
  end Component;
  model zujian "组件"
    Component component 
      annotation (Placement(transformation(origin={-38,86},
extent={{-10,-10},{10,10}})));
    inner Oil oil 
      annotation (Placement(transformation(origin = {-80.0, 85.99999999999999},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  end zujian;
end Question1;