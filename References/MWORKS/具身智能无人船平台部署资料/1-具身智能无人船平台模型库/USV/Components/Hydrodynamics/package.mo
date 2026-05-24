package Hydrodynamics "水动系数计算"
  model Hydrodynamic_Coefficients "水动系数"
    extends USV.Utilities.Icons.Model;
    Modelica.Blocks.Interfaces.RealInput m 
      annotation(Placement(transformation(origin = {-130, 124}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {-110, 90}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealInput LCG 
      annotation(Placement(transformation(origin = {-130, 79.3333}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {-110, 70}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealInput rho 
      annotation(Placement(transformation(origin = {-130, 34.6667}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {-110, 50}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealInput L 
      annotation(Placement(transformation(origin = {-130, -10}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {-110, 30}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealInput C_d 
      annotation(Placement(transformation(origin = {-130, -54.6667}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {-110, 10}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealInput T 
      annotation(Placement(transformation(origin = {-130, -99.3333}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {-110, -10}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealInput B_hull 
      annotation(Placement(transformation(origin = {-130, -144}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {-110, -30}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealInput Xu 
      annotation(Placement(transformation(origin = {-130, -188.667}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {-110, -50}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealInput Xuu 
      annotation(Placement(transformation(origin = {-130, -233.333}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {-110, -70}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealInput V_local[3] 
      annotation(Placement(transformation(origin = {-130, -278}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {-110, -90}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput Hydd_Coef[19] 
      annotation(Placement(transformation(origin = {568, -89.3333}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {110, 0}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain(k = -0.075) 
      annotation(Placement(transformation(origin = {244, 356}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain1(k = 0.9) 
      annotation(Placement(transformation(origin = {408, 328}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Product product1 
      annotation(Placement(transformation(origin = {356, 328}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain2(k = -1 * Modelica.Constants.pi) 
      annotation(Placement(transformation(origin = {309, 322}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Product product2 
      annotation(Placement(transformation(origin = {276, 322}, 
      extent = {{-10, -10}, {10, 10}})));
    Utilities.Math.power power1 
      annotation(Placement(transformation(origin = {228, 316}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain3(k = 0.2) 
      annotation(Placement(transformation(origin = {408, 290}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Product product3 
      annotation(Placement(transformation(origin = {356, 290}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain4(k = 0.5) 
      annotation(Placement(transformation(origin = {326, 284}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Add add 
      annotation(Placement(transformation(origin = {296, 284}, 
      extent = {{-10, -10}, {10, 10}})));
    Utilities.Math.power power2 
      annotation(Placement(transformation(origin = {258, 290}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Add add1(k2 = -1) 
      annotation(Placement(transformation(origin = {233, 290}, 
      extent = {{-5, -5}, {5, 5}})));
    Utilities.Math.power power3 
      annotation(Placement(transformation(origin = {258, 278}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain5(k = 2.5) 
      annotation(Placement(transformation(origin = {408, 252}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain6(k = 1.2) 
      annotation(Placement(transformation(origin = {408, 214}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Add add2 
      annotation(Placement(transformation(origin = {372, 214}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Product product4 
      annotation(Placement(transformation(origin = {334, 220}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain7(k = 1 / 3) 
      annotation(Placement(transformation(origin = {301, 217}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Add add3 
      annotation(Placement(transformation(origin = {276, 217}, 
      extent = {{-5, -5}, {5, 5}})));
    Utilities.Math.power power4(n = 3) 
      annotation(Placement(transformation(origin = {253, 228}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Add add4(k2 = -1) 
      annotation(Placement(transformation(origin = {210, 228}, 
      extent = {{-5, -5}, {5, 5}})));
    Utilities.Math.power power5(n = 3) 
      annotation(Placement(transformation(origin = {253, 214}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain8(k = -1 * Modelica.Constants.pi * 4.75 / 4) 
      annotation(Placement(transformation(origin = {334, 190}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.MultiProduct multiProduct(nu = 3) 
      annotation(Placement(transformation(origin = {301, 190}, 
      extent = {{-6, -6}, {6, 6}})));
    Utilities.Math.power power6(n = 4) 
      annotation(Placement(transformation(origin = {253, 176}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain9(k = 1) 
      annotation(Placement(transformation(origin = {408, 176}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain10(k = -1) 
      annotation(Placement(transformation(origin = {372, 176}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.MultiProduct multiProduct1(nu = 3) 
      annotation(Placement(transformation(origin = {301, 164}, 
      extent = {{-6, -6}, {6, 6}})));
    Modelica.Blocks.Math.Product product5 
      annotation(Placement(transformation(origin = {228, 140}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain11(k = 1) 
      annotation(Placement(transformation(origin = {408, 138}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain12(k = -1 / 2) 
      annotation(Placement(transformation(origin = {372, 138}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.MultiProduct multiProduct2(nu = 3) 
      annotation(Placement(transformation(origin = {340, 138}, 
      extent = {{-6, -6}, {6, 6}})));
    Modelica.Blocks.Math.Add add5(k2 = -1) 
      annotation(Placement(transformation(origin = {300, 102}, 
      extent = {{-5, -5}, {5, 5}})));
    Utilities.Math.power power7(n = 2) 
      annotation(Placement(transformation(origin = {253, 105}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain13(k = 0.5) 
      annotation(Placement(transformation(origin = {408, 100}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.MultiProduct multiProduct3(nu = 3) 
      annotation(Placement(transformation(origin = {356, 70}, 
      extent = {{-6, -6}, {6, 6}})));
    Modelica.Blocks.Math.Gain gain14(k = Modelica.Constants.pi / 2) 
      annotation(Placement(transformation(origin = {300, 81}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Product product6 
      annotation(Placement(transformation(origin = {276, 81}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Product product7 
      annotation(Placement(transformation(origin = {276, 59}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain15(k = -40) 
      annotation(Placement(transformation(origin = {225, 70}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Abs abs1 
      annotation(Placement(transformation(origin = {225, 47}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Add3 add3_1 
      annotation(Placement(transformation(origin = {263, -5}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Add add6(k2 = 1, k1 = -1) 
      annotation(Placement(transformation(origin = {285, 25}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain16(k = 0.1) 
      annotation(Placement(transformation(origin = {263, 27.6}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Division division 
      annotation(Placement(transformation(origin = {225, 27.6}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Sources.Constant const(k = 1.1) 
      annotation(Placement(transformation(origin = {225, 8.2}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain17(k = 0.0045) 
      annotation(Placement(transformation(origin = {203, -5}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Division division1 
      annotation(Placement(transformation(origin = {181, -5}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain18(k = 0.016) 
      annotation(Placement(transformation(origin = {203, -24}, 
      extent = {{-5, -5}, {5, 5}})));
    Utilities.Math.power power8 
      annotation(Placement(transformation(origin = {181, -24}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain19(k = 1) 
      annotation(Placement(transformation(origin = {408, 62}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain20(k = 1) 
      annotation(Placement(transformation(origin = {408, 24}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain21(k = -1 / 3) 
      annotation(Placement(transformation(origin = {376, 24}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.MultiProduct multiProduct4(nu = 3) 
      annotation(Placement(transformation(origin = {356, -4}, 
      extent = {{-6, -6}, {6, 6}})));
    Modelica.Blocks.Math.Add add7(k2 = 1, k1 = 1) 
      annotation(Placement(transformation(origin = {323, 5.2}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain22(k = 3) 
      annotation(Placement(transformation(origin = {408, -14}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.MultiProduct multiProduct5(nu = 3) 
      annotation(Placement(transformation(origin = {356, -36}, 
      extent = {{-6, -6}, {6, 6}})));
    Modelica.Blocks.Math.Sqrt sqrt1 
      annotation(Placement(transformation(origin = {332, -36}, 
      extent = {{-6, -6}, {6, 6}})));
    Modelica.Blocks.Math.Add add8 
      annotation(Placement(transformation(origin = {308, -64}, 
      extent = {{-6, -6}, {6, 6}})));
    Utilities.Math.power power9 
      annotation(Placement(transformation(origin = {254, -64}, 
      extent = {{-5, -5}, {5, 5}})));
    Utilities.Math.power power10 
      annotation(Placement(transformation(origin = {254, -80}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain23(k = 1) 
      annotation(Placement(transformation(origin = {408, -112}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain24(k = 0.06) 
      annotation(Placement(transformation(origin = {408, -144}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain25(k = 1) 
      annotation(Placement(transformation(origin = {408, -176}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain26(k = 1) 
      annotation(Placement(transformation(origin = {408, -208}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain27(k = 0.02) 
      annotation(Placement(transformation(origin = {408, -240}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.MultiProduct multiProduct6(nu = 3) 
      annotation(Placement(transformation(origin = {356, -240}, 
      extent = {{-6, -6}, {6, 6}})));
    Utilities.Math.power power11 
      annotation(Placement(transformation(origin = {319, -240}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Gain gain28(k = 1) 
      annotation(Placement(transformation(origin = {408, -272}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain29(k = -0.25) 
      annotation(Placement(transformation(origin = {352, -272}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.MultiProduct multiProduct7(nu = 3) 
      annotation(Placement(transformation(origin = {320, -272}, 
      extent = {{-6, -6}, {6, 6}})));
    Modelica.Blocks.Math.Add add9 
      annotation(Placement(transformation(origin = {268, -272}, 
      extent = {{-6, -6}, {6, 6}})));
    Utilities.Math.power power12(n = 4) 
      annotation(Placement(transformation(origin = {232, -260}, 
      extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Math.Add add10(k2 = -1) 
      annotation(Placement(transformation(origin = {196, -260}, 
      extent = {{-6, -6}, {6, 6}})));
    Utilities.Math.power power13(n = 4) 
      annotation(Placement(transformation(origin = {232, -275.6}, 
      extent = {{-5, -5}, {5, 5}})));
    annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2}), graphics = {Text(origin = {813, 32}, 
      lineColor = {0, 0, 0}, 
      extent = {{-95, -314}, {95, 314}}, 
      textString = "1. X_u_dot
2. Y_v_dot
3. Y_r_dot
4. N_v_dot
5. N_r_dot
6. X_u
7. X_u|u|
8. Y_v|v|
9. Y_v|r|
10. Y_v
11. Y_r|v|
12. Y_r|r|
13. Y_r
14. N_v|v|
15. N_v
16. N_v|r|
17. N_r|v|
18. N_r
19. N_r|r|"  , 
      textStyle = {TextStyle.None}, 
      textColor = {0, 0, 0}, 
      horizontalAlignment = LinePattern.None)}),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={3,1}, 
lineColor={0,0,0}, 
extent={{-77,31},{77,-31}}, 
textString="Hydrodynamic_Coefficient", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}));
  equation
    connect(m, gain.u) 
      annotation(Line(origin = {-21, 147}, 
      points = {{-109, -23}, {-79, -23}, {-79, 209}, {253, 209}}, 
      color = {0, 0, 127}));
    connect(gain.y, Hydd_Coef[1]) 
      annotation(Line(origin = {412, 133}, 
      points = {{-157, 223}, {118, 223}, {118, -222.3333}, {156, -222.3333}}, 
      color = {0, 0, 127}));
    connect(gain1.y, Hydd_Coef[2]) 
      annotation(Line(origin = {494, 119}, 
      points = {{-75, 209}, {26, 209}, {26, -208.3333}, {74, -208.3333}}, 
      color = {0, 0, 127}));
    connect(product1.y, gain1.u) 
      annotation(Line(origin = {382, 328}, 
      points = {{-15, 0}, {14, 0}}, 
      color = {0, 0, 127}));
    connect(L, product1.u1) 
      annotation(Line(origin = {107, 162}, 
      points = {{-237, -172}, {-177, -172}, {-177, 172}, {237, 172}}, 
      color = {0, 0, 127}));
    connect(product1.u2, gain2.y) 
      annotation(Line(origin = {329, 322}, 
      points = {{15, 0}, {-14.5, 0}}, 
      color = {0, 0, 127}));
    connect(gain2.u, product2.y) 
      annotation(Line(origin = {295, 322}, 
      points = {{8, 0}, {-8, 0}}, 
      color = {0, 0, 127}));
    connect(product2.u1, rho) 
      annotation(Line(origin = {67, 181}, 
      points = {{197, 147}, {151, 147}, {151, 163}, {-147, 163}, {-147, -146.3333}, {-197, -146.3333}}, 
      color = {0, 0, 127}));
    connect(product2.u2, power1.y) 
      annotation(Line(origin = {252, 316}, 
      points = {{12, 0}, {-13, 0}}, 
      color = {0, 0, 127}));
    connect(power1.u, T) 
      annotation(Line(origin = {43, 108}, 
      points = {{173, 208}, {-73, 208}, {-73, -207.3333}, {-173, -207.3333}}, 
      color = {0, 0, 127}));
    connect(gain3.y, Hydd_Coef[3]) 
      annotation(Line(origin = {494, 100}, 
      points = {{-75, 190}, {16, 190}, {16, -189.3333}, {74, -189.3333}}, 
      color = {0, 0, 127}));
    connect(gain3.u, product3.y) 
      annotation(Line(origin = {382, 290}, 
      points = {{14, 0}, {-15, 0}}, 
      color = {0, 0, 127}));
    connect(gain2.y, product3.u1) 
      annotation(Line(origin = {329, 309}, 
      points = {{-14.5, 13}, {5, 13}, {5, -13}, {15, -13}}, 
      color = {0, 0, 127}));
    connect(gain4.y, product3.u2) 
      annotation(Line(origin = {329, 284}, 
      points = {{2.5, 0}, {15, 0}}, 
      color = {0, 0, 127}));
    connect(gain4.u, add.y) 
      annotation(Line(origin = {314, 284}, 
      points = {{6, 0}, {-7, 0}}, 
      color = {0, 0, 127}));
    connect(add.u1, power2.y) 
      annotation(Line(origin = {274, 290}, 
      points = {{10, 0}, {-10.5, 0}}, 
      color = {0, 0, 127}));
    connect(power2.u, add1.y) 
      annotation(Line(origin = {243, 290}, 
      points = {{9, 0}, {-4.5, 0}}, 
      color = {0, 0, 127}));
    connect(L, add1.u1) 
      annotation(Line(origin = {49, 162}, 
      points = {{-179, -172}, {-119, -172}, {-119, 172}, {151, 172}, {151, 131}, {178, 131}}, 
      color = {0, 0, 127}));
    connect(LCG, add1.u2) 
      annotation(Line(origin = {49, 215}, 
      points = {{-179, -135.6667}, {-139, -135.6667}, {-139, 135}, {147, 135}, {147, 72}, {178, 72}}, 
      color = {0, 0, 127}));
    connect(add.u2, power3.y) 
      annotation(Line(origin = {274, 278}, 
      points = {{10, 0}, {-10.5, 0}}, 
      color = {0, 0, 127}));
    connect(LCG, power3.u) 
      annotation(Line(origin = {61, 215}, 
      points = {{-191, -135.6667}, {-151, -135.6667}, {-151, 135}, {135, 135}, {135, 63}, {191, 63}}, 
      color = {0, 0, 127}));
    connect(gain5.u, product3.y) 
      annotation(Line(origin = {382, 271}, 
      points = {{14, -19}, {2, -19}, {2, 19}, {-15, 19}}, 
      color = {0, 0, 127}));
    connect(gain5.y, Hydd_Coef[4]) 
      annotation(Line(origin = {494, 81}, 
      points = {{-75, 171}, {6, 171}, {6, -170.3333}, {74, -170.3333}}, 
      color = {0, 0, 127}));
    connect(gain6.y, Hydd_Coef[5]) 
      annotation(Line(origin = {494, 62}, 
      points = {{-75, 152}, {-4, 152}, {-4, -151.3333}, {74, -151.3333}}, 
      color = {0, 0, 127}));
    connect(gain6.u, add2.y) 
      annotation(Line(origin = {390, 214}, 
      points = {{6, 0}, {-7, 0}}, 
      color = {0, 0, 127}));
    connect(add2.u1, product4.y) 
      annotation(Line(origin = {349, 220}, 
      points = {{11, 0}, {-9.5, 0}}, 
      color = {0, 0, 127}));
    connect(gain2.y, product4.u1) 
      annotation(Line(origin = {321, 273}, 
      points = {{-6.5, 49}, {-5, 49}, {-5, -50}, {7, -50}}, 
      color = {0, 0, 127}));
    connect(product4.u2, gain7.y) 
      annotation(Line(origin = {317, 217}, 
      points = {{11, 0}, {-10.5, 0}}, 
      color = {0, 0, 127}));
    connect(gain7.u, add3.y) 
      annotation(Line(origin = {288, 217}, 
      points = {{7, 0}, {-6.5, 0}}, 
      color = {0, 0, 127}));
    connect(add3.u1, power4.y) 
      annotation(Line(origin = {263, 220}, 
      points = {{7, 0}, {1, 0}, {1, 8}, {-4.5, 8}}, 
      color = {0, 0, 127}));
    connect(power4.u, add4.y) 
      annotation(Line(origin = {243, 228}, 
      points = {{4, 0}, {-27.5, 0}}, 
      color = {0, 0, 127}));
    connect(L, add4.u1) 
      annotation(Line(origin = {49, 162}, 
      points = {{-179, -172}, {-119, -172}, {-119, 172}, {141, 172}, {141, 69}, {155, 69}}, 
      color = {0, 0, 127}));
    connect(LCG, add4.u2) 
      annotation(Line(origin = {49, 215}, 
      points = {{-179, -135.6667}, {-139, -135.6667}, {-139, 135}, {137, 135}, {137, 10}, {155, 10}}, 
      color = {0, 0, 127}));
    connect(add3.u2, power5.y) 
      annotation(Line(origin = {264, 214}, 
      points = {{6, 0}, {-5.5, 0}}, 
      color = {0, 0, 127}));
    connect(LCG, power5.u) 
      annotation(Line(origin = {59, 215}, 
      points = {{-189, -135.6667}, {-149, -135.6667}, {-149, 135}, {127, 135}, {127, -1}, {188, -1}}, 
      color = {0, 0, 127}));
    connect(gain8.y, add2.u2) 
      annotation(Line(origin = {350, 199}, 
      points = {{-10.5, -9}, {0, -9}, {0, 9}, {10, 9}}, 
      color = {0, 0, 127}));
    connect(gain8.u, multiProduct.y) 
      annotation(Line(origin = {320, 190}, 
      points = {{8, 0}, {-11.98, 0}}, 
      color = {0, 0, 127}));
    connect(rho, multiProduct.u[1]) 
      annotation(Line(origin = {83, 189}, 
      points = {{-213, -154.3333}, {-163, -154.3333}, {-163, 155}, {97, 155}, {97, 1}, {212, 1}}, 
      color = {0, 0, 127}));
    connect(B_hull, multiProduct.u[2]) 
      annotation(Line(origin = {83, 23}, 
      points = {{-213, -167}, {-103, -167}, {-103, 167}, {212, 167}}, 
      color = {0, 0, 127}));
    connect(T, power6.u) 
      annotation(Line(origin = {59, 61}, 
      points = {{-189, -160.3333}, {-89, -160.3333}, {-89, 115}, {188, 115}}, 
      color = {0, 0, 127}));
    connect(power6.y, multiProduct.u[3]) 
      annotation(Line(origin = {277, 183}, 
      points = {{-18.5, -7}, {3, -7}, {3, 7}, {18, 7}}, 
      color = {0, 0, 127}));
    connect(Xu, Hydd_Coef[6]) 
      annotation(Line(origin = {219, -139}, 
      points = {{-349, -49.667}, {-229, -49.667}, {-229, 49.6667}, {349, 49.6667}}, 
      color = {0, 0, 127}));
    connect(Xuu, Hydd_Coef[7]) 
      annotation(Line(origin = {219, -161}, 
      points = {{-349, -72.333}, {-219, -72.333}, {-219, 71.6667}, {349, 71.6667}}, 
      color = {0, 0, 127}));
    connect(gain9.y, Hydd_Coef[8]) 
      annotation(Line(origin = {494, 43}, 
      points = {{-75, 133}, {-14, 133}, {-14, -132.3333}, {74, -132.3333}}, 
      color = {0, 0, 127}));
    connect(gain9.u, gain10.y) 
      annotation(Line(origin = {387, 176}, 
      points = {{9, 0}, {-9.5, 0}}, 
      color = {0, 0, 127}));
    connect(multiProduct1.y, gain10.u) 
      annotation(Line(origin = {337, 170}, 
      points = {{-28.98, -6}, {13, -6}, {13, 6}, {29, 6}}, 
      color = {0, 0, 127}));
    connect(L, multiProduct1.u[1]) 
      annotation(Line(origin = {83, 77}, 
      points = {{-213, -87}, {-153, -87}, {-153, 87}, {212, 87}}, 
      color = {0, 0, 127}));
    connect(C_d, multiProduct1.u[2]) 
      annotation(Line(origin = {83, 55}, 
      points = {{-213, -109.667}, {-143, -109.667}, {-143, 109}, {212, 109}}, 
      color = {0, 0, 127}));
    connect(product5.y, multiProduct1.u[3]) 
      annotation(Line(origin = {267, 146}, 
      points = {{-28, -6}, {13, -6}, {13, 18}, {28, 18}}, 
      color = {0, 0, 127}));
    connect(rho, product5.u1) 
      annotation(Line(origin = {43, 84}, 
      points = {{-173, -49.3333}, {-123, -49.3333}, {-123, 62}, {173, 62}}, 
      color = {0, 0, 127}));
    connect(T, product5.u2) 
      annotation(Line(origin = {43, 17}, 
      points = {{-173, -116.3333}, {-73, -116.3333}, {-73, 117}, {173, 117}}, 
      color = {0, 0, 127}));
    connect(gain11.u, gain12.y) 
      annotation(Line(origin = {387, 138}, 
      points = {{9, 0}, {-9.5, 0}}, 
      color = {0, 0, 127}));
    connect(gain12.u, multiProduct2.y) 
      annotation(Line(origin = {357, 138}, 
      points = {{9, 0}, {-9.98, 0}}, 
      color = {0, 0, 127}));
    connect(C_d, multiProduct2.u[1]) 
      annotation(Line(origin = {102, 42}, 
      points = {{-232, -96.6667}, {-162, -96.6667}, {-162, 78}, {182, 78}, {182, 96}, {232, 96}}, 
      color = {0, 0, 127}));
    connect(add5.y, multiProduct2.u[2]) 
      annotation(Line(origin = {320, 120}, 
      points = {{-14.5, -18}, {0, -18}, {0, 18}, {14, 18}}, 
      color = {0, 0, 127}));
    connect(add5.u1, power7.y) 
      annotation(Line(origin = {276, 105}, 
      points = {{18, 0}, {-17.5, 0}}, 
      color = {0, 0, 127}));
    connect(add4.y, power7.u) 
      annotation(Line(origin = {231, 167}, 
      points = {{-15.5, 61}, {7, 61}, {7, -15}, {13, -15}, {13, -62}, {16, -62}}, 
      color = {0, 0, 127}));
    connect(power3.y, add5.u2) 
      annotation(Line(origin = {279, 189}, 
      points = {{-15.5, 89}, {-5, 89}, {-5, 35}, {12, 35}, {12, -90}, {15, -90}}, 
      color = {0, 0, 127}));
    connect(product5.y, multiProduct2.u[3]) 
      annotation(Line(origin = {287, 139}, 
      points = {{-48, 1}, {43.8, 1}, {43.8, -1}, {47, -1}}, 
      color = {0, 0, 127}));
    connect(gain11.y, Hydd_Coef[9]) 
      annotation(Line(origin = {494, 24}, 
      points = {{-75, 114}, {-24, 114}, {-24, -113.3333}, {74, -113.3333}}, 
      color = {0, 0, 127}));
    connect(gain13.y, Hydd_Coef[10]) 
      annotation(Line(origin = {494, 5}, 
      points = {{-75, 95}, {-34, 95}, {-34, -94.3333}, {74, -94.3333}}, 
      color = {0, 0, 127}));
    connect(gain13.u, multiProduct3.y) 
      annotation(Line(origin = {388, 100}, 
      points = {{8, 0}, {-8, 0}, {-8, -30}, {-24.98, -30}}, 
      color = {0, 0, 127}));
    connect(gain14.y, multiProduct3.u[1]) 
      annotation(Line(origin = {328, 76}, 
      points = {{-22.5, 5}, {12, 5}, {12, -6}, {22, -6}}, 
      color = {0, 0, 127}));
    connect(gain14.u, product6.y) 
      annotation(Line(origin = {288, 81}, 
      points = {{6, 0}, {-6.5, 0}}, 
      color = {0, 0, 127}));
    connect(L, product6.u1) 
      annotation(Line(origin = {70, 50}, 
      points = {{-200, -60}, {-140, -60}, {-140, 60}, {170, 60}, {170, 34}, {200, 34}}, 
      color = {0, 0, 127}));
    connect(T, product6.u2) 
      annotation(Line(origin = {70, 0}, 
      points = {{-200, -99.3333}, {-100, -99.3333}, {-100, 100}, {166, 100}, {166, 78}, {200, 78}}, 
      color = {0, 0, 127}));
    connect(product7.y, multiProduct3.u[2]) 
      annotation(Line(origin = {316, 65}, 
      points = {{-34.5, -6}, {24, -6}, {24, 5}, {34, 5}}, 
      color = {0, 0, 127}));
    connect(gain15.y, product7.u1) 
      annotation(Line(origin = {250, 66}, 
      points = {{-19.5, 4}, {10, 4}, {10, -4}, {20, -4}}, 
      color = {0, 0, 127}));
    connect(rho, gain15.u) 
      annotation(Line(origin = {45, 62}, 
      points = {{-175, -27.3333}, {-125, -27.3333}, {-125, 28}, {171, 28}, {171, 8}, {174, 8}}, 
      color = {0, 0, 127}));
    connect(abs1.y, product7.u2) 
      annotation(Line(origin = {250, 52}, 
      points = {{-19.5, -5}, {10, -5}, {10, 4}, {20, 4}}, 
      color = {0, 0, 127}));
    connect(V_local[2], abs1.u) 
      annotation(Line(origin = {45, -115}, 
      points = {{-175, -163}, {-35, -163}, {-35, 162}, {174, 162}}, 
      color = {0, 0, 127}));
    connect(add6.u2, add3_1.y) 
      annotation(Line(origin = {276, 4}, 
      points = {{2.8, 16.4}, {-2.8, 16.4}, {-2.8, -10}, {-5.4, -10}}, 
      color = {0, 0, 127}));
    connect(gain16.y, add6.u1) 
      annotation(Line(origin = {274, 28}, 
      points = {{-5.5, -0.4}, {4.8, -0.4}}, 
      color = {0, 0, 127}));
    connect(gain16.u, division.y) 
      annotation(Line(origin = {252, 28}, 
      points = {{5, -0.4}, {-21.5, -0.4}}, 
      color = {0, 0, 127}));
    connect(B_hull, division.u1) 
      annotation(Line(origin = {45, -57}, 
      points = {{-175, -87}, {-65, -87}, {-65, 87.6}, {174, 87.6}}, 
      color = {0, 0, 127}));
    connect(T, division.u2) 
      annotation(Line(origin = {45, -37}, 
      points = {{-175, -62.3333}, {-75, -62.3333}, {-75, 61.6}, {174, 61.6}}, 
      color = {0, 0, 127}));
    connect(const.y, add3_1.u1) 
      annotation(Line(origin = {244, 4}, 
      points = {{-13.5, 4.2}, {10, 4.2}, {10, -5}, {13, -5}}, 
      color = {0, 0, 127}));
    connect(add3_1.u2, gain17.y) 
      annotation(Line(origin = {233, -5}, 
      points = {{24, 0}, {-24.5, 0}}, 
      color = {0, 0, 127}));
    connect(gain17.u, division1.y) 
      annotation(Line(origin = {192, -5}, 
      points = {{5, 0}, {-5.5, 0}}, 
      color = {0, 0, 127}));
    connect(L, division1.u1) 
      annotation(Line(origin = {23, -6}, 
      points = {{-153, -4}, {-93, -4}, {-93, 4}, {152, 4}}, 
      color = {0, 0, 127}));
    connect(T, division1.u2) 
      annotation(Line(origin = {23, -54}, 
      points = {{-153, -45.3333}, {-53, -45.3333}, {-53, 46}, {152, 46}}, 
      color = {0, 0, 127}));
    connect(gain18.y, add3_1.u3) 
      annotation(Line(origin = {233, -16}, 
      points = {{-24.5, -8}, {21, -8}, {21, 7}, {24, 7}}, 
      color = {0, 0, 127}));
    connect(gain18.u, power8.y) 
      annotation(Line(origin = {192, -24}, 
      points = {{5, 0}, {-5.5, 0}}, 
      color = {0, 0, 127}));
    connect(division.y, power8.u) 
      annotation(Line(origin = {203, 2}, 
      points = {{27.5, 25.6}, {30, 25.6}, {30, 18.6}, {-31, 18.6}, {-31, -26}, {-28, -26}}, 
      color = {0, 0, 127}));
    connect(add6.y, multiProduct3.u[3]) 
      annotation(Line(origin = {320, 48}, 
      points = {{-29.5, -23}, {20, -23}, {20, 22}, {30, 22}}, 
      color = {0, 0, 127}));
    connect(gain19.y, Hydd_Coef[11]) 
      annotation(Line(origin = {494, -14}, 
      points = {{-75, 76}, {-44, 76}, {-44, -75.3333}, {74, -75.3333}}, 
      color = {0, 0, 127}));
    connect(gain12.y, gain19.u) 
      annotation(Line(origin = {387, 100}, 
      points = {{-9.5, 38}, {1, 38}, {1, -38}, {9, -38}}, 
      color = {0, 0, 127}));
    connect(gain20.y, Hydd_Coef[12]) 
      annotation(Line(origin = {494, -33}, 
      points = {{-75, 57}, {-54, 57}, {-54, -56.3333}, {74, -56.3333}}, 
      color = {0, 0, 127}));
    connect(gain21.y, gain20.u) 
      annotation(Line(origin = {389, 25}, 
      points = {{-7.5, -1}, {7, -1}}, 
      color = {0, 0, 127}));
    connect(multiProduct4.y, gain21.u) 
      annotation(Line(origin = {367, 10}, 
      points = {{-3.98, -14}, {-0.96, -14}, {-0.96, 14}, {3, 14}}, 
      color = {0, 0, 127}));
    connect(add7.y, multiProduct4.u[1]) 
      annotation(Line(origin = {339, 1}, 
      points = {{-10.5, 4.2}, {3, 4.2}, {3, -5}, {11, -5}}, 
      color = {0, 0, 127}));
    connect(power4.y, add7.u1) 
      annotation(Line(origin = {288, 118}, 
      points = {{-29.5, 110}, {26, 110}, {26, -109.8}, {29, -109.8}}, 
      color = {0, 0, 127}));
    connect(power5.y, add7.u2) 
      annotation(Line(origin = {288, 108}, 
      points = {{-29.5, 106}, {-21, 106}, {-21, 102}, {26, 102}, {26, -105.8}, {29, -105.8}}, 
      color = {0, 0, 127}));
    connect(product5.y, multiProduct4.u[2]) 
      annotation(Line(origin = {295, 68}, 
      points = {{-56, 72}, {35.8, 72}, {35.8, -72}, {55, -72}}, 
      color = {0, 0, 127}));
    connect(C_d, multiProduct4.u[3]) 
      annotation(Line(origin = {110, -29}, 
      points = {{-240, -25.6667}, {170, -25.6667}, {170, 25}, {240, 25}}, 
      color = {0, 0, 127}));
    connect(gain22.y, Hydd_Coef[13]) 
      annotation(Line(origin = {494, -52}, 
      points = {{-75, 38}, {-64, 38}, {-64, -37.3333}, {74, -37.3333}}, 
      color = {0, 0, 127}));
    connect(multiProduct5.y, gain22.u) 
      annotation(Line(origin = {380, -25}, 
      points = {{-16.98, -11}, {0, -11}, {0, 11}, {16, 11}}, 
      color = {0, 0, 127}));
    connect(gain2.y, multiProduct5.u[1]) 
      annotation(Line(origin = {332, 143}, 
      points = {{-17.5, 179}, {8, 179}, {8, 3}, {18.04, 3}, {18.04, -65}, {14.8, -65}, {14.8, -179}, {18, -179}}, 
      color = {0, 0, 127}));
    connect(multiProduct5.u[2], sqrt1.y) 
      annotation(Line(origin = {340, -36}, 
      points = {{10, 0}, {-1.4, 0}}, 
      color = {0, 0, 127}));
    connect(sqrt1.u, add8.y) 
      annotation(Line(origin = {320, -36}, 
      points = {{4.8, 0}, {-2.8, 0}, {-2.8, -28}, {-5.4, -28}}, 
      color = {0, 0, 127}));
    connect(power9.y, add8.u1) 
      annotation(Line(origin = {280, -62}, 
      points = {{-20.5, -2}, {0, -2}, {0, 1.6}, {20.8, 1.6}}, 
      color = {0, 0, 127}));
    connect(power10.y, add8.u2) 
      annotation(Line(origin = {280, -74}, 
      points = {{-20.5, -6}, {12, -6}, {12, 6.4}, {20.8, 6.4}}, 
      color = {0, 0, 127}));
    connect(V_local[1], power9.u) 
      annotation(Line(origin = {59, -171}, 
      points = {{-189, -107}, {-49, -107}, {-49, 107}, {189, 107}}, 
      color = {0, 0, 127}));
    connect(V_local[2], power10.u) 
      annotation(Line(origin = {59, -179}, 
      points = {{-189, -99}, {-49, -99}, {-49, 99}, {189, 99}}, 
      color = {0, 0, 127}));
    connect(L, multiProduct5.u[3]) 
      annotation(Line(origin = {110, -27}, 
      points = {{-240, 17}, {-180, 17}, {-180, -17}, {236.8, -17}, {236.8, -9}, {240, -9}}, 
      color = {0, 0, 127}));
    connect(gain23.y, Hydd_Coef[14]) 
      annotation(Line(origin = {470, -102}, 
      points = {{-51, -10}, {-40, -10}, {-40, 12.6667}, {98, 12.6667}}, 
      color = {0, 0, 127}));
    connect(gain12.y, gain23.u) 
      annotation(Line(origin = {362, 12}, 
      points = {{15.5, 126}, {18, 126}, {18, 119}, {-18, 119}, {-18, -124}, {34, -124}}, 
      color = {0, 0, 127}));
    connect(gain24.y, Hydd_Coef[15]) 
      annotation(Line(origin = {494, -117}, 
      points = {{-75, -27}, {-54, -27}, {-54, 27.6667}, {74, 27.6667}}, 
      color = {0, 0, 127}));
    connect(multiProduct5.y, gain24.u) 
      annotation(Line(origin = {380, -90}, 
      points = {{-16.98, 54}, {0, 54}, {0, -54}, {16, -54}}, 
      color = {0, 0, 127}));
    connect(gain25.y, Hydd_Coef[16]) 
      annotation(Line(origin = {494, -133}, 
      points = {{-75, -43}, {-44, -43}, {-44, 43.6667}, {74, 43.6667}}, 
      color = {0, 0, 127}));
    connect(gain21.y, gain25.u) 
      annotation(Line(origin = {389, -76}, 
      points = {{-7.5, 100}, {-1, 100}, {-1, -100}, {7, -100}}, 
      color = {0, 0, 127}));
    connect(gain21.y, gain26.u) 
      annotation(Line(origin = {389, -92}, 
      points = {{-7.5, 116}, {3, 116}, {3, -116}, {7, -116}}, 
      color = {0, 0, 127}));
    connect(gain26.y, Hydd_Coef[17]) 
      annotation(Line(origin = {494, -149}, 
      points = {{-75, -59}, {-34, -59}, {-34, 59.6667}, {74, 59.6667}}, 
      color = {0, 0, 127}));
    connect(gain27.y, Hydd_Coef[18]) 
      annotation(Line(origin = {494, -165}, 
      points = {{-75, -75}, {-24, -75}, {-24, 75.6667}, {74, 75.6667}}, 
      color = {0, 0, 127}));
    connect(gain27.u, multiProduct6.y) 
      annotation(Line(origin = {380, -240}, 
      points = {{16, 0}, {-16.98, 0}}, 
      color = {0, 0, 127}));
    connect(gain2.y, multiProduct6.u[1]) 
      annotation(Line(origin = {332, 41}, 
      points = {{-17.5, 281}, {8, 281}, {8, 105}, {18.04, 105}, {18.04, 37}, {14.8, 37}, {14.8, -281}, {18, -281}}, 
      color = {0, 0, 127}));
    connect(sqrt1.y, multiProduct6.u[2]) 
      annotation(Line(origin = {344, -138}, 
      points = {{-5.4, 102}, {2.8, 102}, {2.8, -102}, {6, -102}}, 
      color = {0, 0, 127}));
    connect(multiProduct6.u[3], power11.y) 
      annotation(Line(origin = {337, -240}, 
      points = {{13, 0}, {-12.5, -2.84217e-14}}, 
      color = {0, 0, 127}));
    connect(L, power11.u) 
      annotation(Line(origin = {92, -125}, 
      points = {{-222, 115}, {-162, 115}, {-162, -115}, {221, -115}}, 
      color = {0, 0, 127}));
    connect(gain28.y, Hydd_Coef[19]) 
      annotation(Line(origin = {494, -181}, 
      points = {{-75, -91}, {-14, -91}, {-14, 91.6667}, {74, 91.6667}}, 
      color = {0, 0, 127}));
    connect(gain28.u, gain29.y) 
      annotation(Line(origin = {380, -272}, 
      points = {{16, 0}, {-17, 0}}, 
      color = {0, 0, 127}));
    connect(gain29.u, multiProduct7.y) 
      annotation(Line(origin = {334, -272}, 
      points = {{6, 0}, {-6.98, 0}}, 
      color = {0, 0, 127}));
    connect(multiProduct7.u[1], add9.y) 
      annotation(Line(origin = {294, -272}, 
      points = {{20, 0}, {-19.4, 0}}, 
      color = {0, 0, 127}));
    connect(power12.y, add9.u1) 
      annotation(Line(origin = {249, -268}, 
      points = {{-11.5, 8}, {8.6, 8}, {8.6, -0.4}, {11.8, -0.4}}, 
      color = {0, 0, 127}));
    connect(power12.u, add10.y) 
      annotation(Line(origin = {214, -260}, 
      points = {{12, 0}, {-11.4, 0}}, 
      color = {0, 0, 127}));
    connect(L, add10.u1) 
      annotation(Line(origin = {29, -133}, 
      points = {{-159, 123}, {-99, 123}, {-99, -123.4}, {159.8, -123.4}}, 
      color = {0, 0, 127}));
    connect(LCG, add10.u2) 
      annotation(Line(origin = {29, -92}, 
      points = {{-159, 171.3333}, {-119, 171.3333}, {-119, -171.6}, {159.8, -171.6}}, 
      color = {0, 0, 127}));
    connect(add9.u2, power13.y) 
      annotation(Line(origin = {249, -276}, 
      points = {{11.8, 0.4}, {-11.5, 0.4}}, 
      color = {0, 0, 127}));
    connect(LCG, power13.u) 
      annotation(Line(origin = {48, -98}, 
      points = {{-178, 177.3333}, {-138, 177.3333}, {-138, -177.6}, {178, -177.6}}, 
      color = {0, 0, 127}));
    connect(product5.y, multiProduct7.u[2]) 
      annotation(Line(origin = {278, -66}, 
      points = {{-39, 206}, {32.8, 206}, {32.8, 10}, {39.2, 10}, {39.2, -167}, {32.8, -167}, {32.8, -206}, {36, -206}}, 
      color = {0, 0, 127}));
    connect(C_d, multiProduct7.u[3]) 
      annotation(Line(origin = {92, -163}, 
      points = {{-222, 108.333}, {-152, 108.333}, {-152, -67}, {208, -67}, {208, -109}, {222, -109}}, 
      color = {0, 0, 127}));
  end Hydrodynamic_Coefficients;

end Hydrodynamics;