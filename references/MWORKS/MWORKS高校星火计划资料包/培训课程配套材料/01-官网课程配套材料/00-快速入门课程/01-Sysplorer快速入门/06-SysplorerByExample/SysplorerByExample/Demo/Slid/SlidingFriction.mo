model SlidingFriction "滑动摩擦副"
  //参数
  parameter Boolean Stribeck = true "是否考虑Stribeck效应" 
    annotation(choices(checkBox = true));
  parameter Real mu_c = 0.1 "滑动摩擦系数";
  parameter Real mu_s = 0.12 "静摩擦系数";
  parameter Real mu_v(final unit = "N.s/m") = 0.1 "粘性摩擦系数";
  parameter Modelica.SIunits.Force fN = 10 "法向力";
  parameter Modelica.SIunits.Velocity v_Strb = 0.01 "Stribeck速度常数";
  //变量
  Modelica.SIunits.Force f_fri "总摩擦力";
  Modelica.SIunits.Force f_slip "滑动摩擦力";
  Modelica.SIunits.Force f_stick "最大静摩擦力";
  Modelica.SIunits.Force f_vis "粘性摩擦力";
  Modelica.SIunits.Position s_rel "相对位移";
  Modelica.SIunits.Velocity v_rel "相对速度";
  //接口实例化
  Modelica.Mechanics.Translational.Interfaces.Flange_a flange_a 
    annotation(Placement(transformation(origin = {-100, 0},
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Translational.Interfaces.Flange_b flange_b 
    annotation(Placement(transformation(origin = {100, 0},
    extent = {{-10, -10}, {10, 10}})));
  annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Rectangle(origin={2.66454e-15,10},
fillColor={255,255,255},
fillPattern=FillPattern.Solid,
extent={{-49,8},{49,-8}}), Rectangle(origin={0,-6},
fillColor={0,128,0},
fillPattern=FillPattern.Solid,
extent={{-49,8},{49,-8}}), Line(origin={-78,-2},
points={{-12,0},{12,0}},
color={0,128,0},
thickness=2), Line(origin={-58,3},
points={{-8,-5},{8,5}},
color={0,128,0},
thickness=2), Line(origin={58,-3},
points={{-8,-5},{8,5}},
color={0,128,0},
thickness=2), Line(origin={78,2},
points={{-12,0},{12,0}},
color={0,128,0},
thickness=2)}));
equation
  //运动方程
  s_rel = flange_b.s - flange_a.s;
  v_rel = der(s_rel);
  //摩擦计算
  f_stick = mu_s * fN;
  f_vis = mu_v * v_rel;
  if Stribeck == true then
    f_slip = (mu_c * fN + (mu_c * fN - f_stick) * exp(-3 * abs(v_rel) / v_Strb)) * sign(v_rel);
  else
    f_slip = mu_c * fN;
  end if;
  f_fri = f_slip + f_vis;
  //接口方程
  flange_b.f = f_fri;
  flange_a.f = -f_fri;

end SlidingFriction;