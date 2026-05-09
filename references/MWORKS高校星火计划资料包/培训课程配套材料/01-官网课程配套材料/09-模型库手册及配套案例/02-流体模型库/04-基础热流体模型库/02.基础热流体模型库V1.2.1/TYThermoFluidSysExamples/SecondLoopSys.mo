model SecondLoopSys "二回路系统"
  TYThermoFluidSys.HeatExchangers.SimpleCondenser condenser(Water_in(m_flow(start = 1180.25)), ntubes = 4000, L = 11, D(displayUnit = "mm") = 0.017, e(displayUnit = "mm") = 1e-3, V = 10, A = 1, p_water_in0 = 1.15e5, p_water_out0 = 100000, P0 = 27000, redeclare package Medium = Modelica.Media.Water.StandardWater, dz = 0, gravity_pressure = true, Vf0 = 0.5, Ccond = 0.05, Cevap = 0.05, Tl_start = 340.15, Tv_start = 340.15, redeclare package Medium_w = Modelica.Media.Water.StandardWater) annotation(Placement(transformation(origin = {291, -85.80000000000001}, extent = {{15, -15}, {-15, 15}})));
  TYThermoFluidSys.Boundaries.BoundaryPressure boundaryPressure(redeclare package Medium = Modelica.Media.Water.StandardWater, p = 100000) 
    annotation(Placement(transformation(origin = {231, -64.80000000000001}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Valves.ControlValve controlValve8(p_start = 1.2e5, d = 1, dp_start = 80000, m_flow_start = 1180, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {218, -150.8}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression6(y = 1) 
    annotation(Placement(transformation(origin = {204.25, -105.60000000000002}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Machines.SuterPump suterPump(qv(start = 0.08), table_beta = {{0, -1.42}, {0.0714, -1.328}, {0.1428, -1.211}, {0.2142, -1.056}, {0.2856, -0.87}, {0.357, -0.677}, {0.4284, -0.573}, {0.4998, -0.518}, {0.5712, -0.38}, {0.6426, -0.232}, {0.714, -0.16}, {0.7854, 0}, {0.8568, 0.118}, {0.9282, 0.308}, {0.9996, 0.442}, {1.071, 0.574}, {1.1424, 0.739}, {1.2138, 0.929}, {1.2852, 1.147}, {1.3566, 1.37}, {1.428, 1.599}, {1.4994, 1.839}, {1.5708, 2.08}, {1.6422, 2.3}, {1.7136, 2.48}, {1.785, 2.63}, {1.8564, 2.724}, {1.9278, 2.687}, {1.9992, 2.715}, {2.0706, 2.688}, {2.142, 2.555}, {2.2134, 2.434}, {2.2848, 2.288}, {2.3562, 2.11}, {2.4276, 1.948}, {2.499, 1.825}, {2.5704, 1.732}, {2.6418, 1.644}, {2.7132, 1.576}, {2.7846, 1.533}, {2.856, 1.522}, {2.9274, 1.519}, {2.9988, 1.523}, {3.0702, 1.523}, {3.1416, 1.49}, {3.213, 1.386}, {3.2844, 1.223}, {3.3558, 1.048}, {3.4272, 0.909}, {3.4986, 0.814}, {3.57, 0.766}, {3.6414, 0.734}, {3.7128, 0.678}, {3.7842, 0.624}, {3.8556, 0.57}, {3.927, 0.5}, {3.9984, 0.407}, {4.0698, 0.278}, {4.1412, 0.146}, 
    {4.2126, 0.023}, {4.284, -0.175}, {4.3554, -0.379}, {4.4268, -0.585}, {4.4982, -0.778}, {4.5696, -1.008}, {4.641, -1.277}, {4.7124, -1.56}, {4.7838, -2.07}, {4.8552, -2.48}, {4.9266, -2.7}, {4.998, -2.77}, {5.0694, -2.8}, {5.1408, -2.8}, {5.2122, -2.76}, {5.2836, -2.71}, {5.355, -2.64}, {5.4264, -2.54}, {5.4978, -2.44}, {5.5692, -2.34}, {5.6406, -2.24}, {5.712, -2.12}, {5.7834, -2}, {5.8548, -1.94}, {5.9262, -1.9}, {5.9976, -1.9}, {6.069, -1.85}, {6.1404, -1.75}, {6.2118, -1.63}, {6.283185307, -1.42}}, table_h = {{0, -0.69}, {0.0714, -0.599}, {0.1428, -0.512}, {0.2142, -0.418}, {0.2856, -0.304}, {0.357, -0.181}, {0.4284, -0.078}, {0.4998, -0.011}, {0.5712, 0.032}, {0.6426, 0.074}, {0.714, 0.13}, {0.7854, 0.19}, {0.8568, 0.265}, {0.9282, 0.363}, {0.9996, 0.461}, {1.071, 0.553}, {1.1424, 0.674}, {1.2138, 0.848}, {1.2852, 1.075}, {1.3566, 1.337}, {1.428, 1.629}, {1.4994, 1.929}, {1.5708, 2.18}, {1.6422, 2.334}, {1.7136, 2.518}, {1.785, 2.736}, {1.8564, 2.863}, {1.9278, 2.948}, {1.9992, 3.026}, 
    {2.0706, 3.015}, {2.142, 2.927}, {2.2134, 2.873}, {2.2848, 2.771}, {2.3562, 2.64}, {2.4276, 2.497}, {2.499, 2.441}, {2.5704, 2.378}, {2.6418, 2.336}, {2.7132, 2.288}, {2.7846, 2.209}, {2.856, 2.162}, {2.9274, 2.14}, {2.9988, 2.109}, {3.0702, 2.054}, {3.1416, 1.97}, {3.213, 1.86}, {3.2844, 1.735}, {3.3558, 1.571}, {3.4272, 1.357}, {3.4986, 1.157}, {3.57, 1.106}, {3.6414, 0.927}, {3.7128, 0.846}, {3.7842, 0.744}, {3.8556, 0.64}, {3.927, 0.5}, {3.9984, 0.374}, {4.0698, 0.191}, {4.1412, 0.001}, {4.2126, -0.19}, {4.284, -0.384}, {4.3554, -0.585}, {4.4268, -0.786}, {4.4982, -0.972}, {4.5696, -1.185}, {4.641, -1.372}, {4.7124, -1.5}, {4.7838, -1.94}, {4.8552, -2.16}, {4.9266, -2.29}, {4.998, -2.35}, {5.0694, -2.35}, {5.1408, -2.23}, {5.2122, -2.2}, {5.2836, -2.13}, {5.355, -2.05}, {5.4264, -1.97}, {5.4978, -1.895}, {5.5692, -1.81}, {5.6406, -1.73}, {5.712, -1.6}, {5.7834, -1.42}, {5.8548, -1.13}, {5.9262, -0.95}, {5.9976, -0.93}, {6.069, -0.95}, {6.1404, -1}, {6.2118, -0.92}, {6.283185307, -0.69}}, 
    A = 4, qvr = 1.5, Hr = 10, rho_r = 1, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {170.75, -150.80000000000004}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Boundaries.BoundaryPressure boundaryPressure2(redeclare package Medium = Modelica.Media.Water.StandardWater, p = 100000, energyDefinition = "T", T = 298.15) 
    annotation(Placement(transformation(origin = {125.50000000000003, -150.80000000000004}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Machines.SteamTurbine steamTurbine4(p_in_0 = 4.5e6, p_out_0(displayUnit = "bar") = 20000, m_flow_0 = 0.1, eta_0 = 0.8, h_in_0 = 2925.95e3, redeclare model TurbineEta = TYThermoFluidSys.Machines.Basic.TurbineEffectiveness.EllipticalEfficiency, p_in0 = 3.14e6, p_out0 = 30000, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {140, -46.80000000000001}, extent = {{-10, 10}, {10, -10}})));
  TYThermoFluidSys.Valves.SimpleControlValve controlValve4(p_start = 3.2e6, dp_nominal = 14300, dp_start = 14300, m_flow_start = 0.07, m_flow_nominal = 0.07, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {72.00000000000001, -46.80000000000001}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression4(y = 1) 
    annotation(Placement(transformation(origin = {46, -26.80000000000001}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Machines.Shaft shaft(flange_a(tau(start = 200)), J = 100, N_start = 314.159265358979, If_Speed_Initial = true) 
    annotation(Placement(transformation(origin = {152, -90.80000000000001}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Valves.SimpleControlValve controlValve9(p_start = 43000, m_flow_start = 78.5, dp_nominal = 600, m_flow_nominal = 78.5, dp_start = 600, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {291, -160.8}, extent = {{10, 10}, {-10, -10}}, rotation = 90)));
  Modelica.Blocks.Sources.RealExpression realExpression5(y = 0.8) 
    annotation(Placement(transformation(origin = {324.5, -160.8}, extent = {{10, -10}, {-10, 10}})));
  TYThermoFluidSys.Machines.SuterPump suterPump1(qv(start = 0.08), table_beta = {{0, -1.42}, {0.0714, -1.328}, {0.1428, -1.211}, {0.2142, -1.056}, {0.2856, -0.87}, {0.357, -0.677}, {0.4284, -0.573}, {0.4998, -0.518}, {0.5712, -0.38}, {0.6426, -0.232}, {0.714, -0.16}, {0.7854, 0}, {0.8568, 0.118}, {0.9282, 0.308}, {0.9996, 0.442}, {1.071, 0.574}, {1.1424, 0.739}, {1.2138, 0.929}, {1.2852, 1.147}, {1.3566, 1.37}, {1.428, 1.599}, {1.4994, 1.839}, {1.5708, 2.08}, {1.6422, 2.3}, {1.7136, 2.48}, {1.785, 2.63}, {1.8564, 2.724}, {1.9278, 2.687}, {1.9992, 2.715}, {2.0706, 2.688}, {2.142, 2.555}, {2.2134, 2.434}, {2.2848, 2.288}, {2.3562, 2.11}, {2.4276, 1.948}, {2.499, 1.825}, {2.5704, 1.732}, {2.6418, 1.644}, {2.7132, 1.576}, {2.7846, 1.533}, {2.856, 1.522}, {2.9274, 1.519}, {2.9988, 1.523}, {3.0702, 1.523}, {3.1416, 1.49}, {3.213, 1.386}, {3.2844, 1.223}, {3.3558, 1.048}, {3.4272, 0.909}, {3.4986, 0.814}, {3.57, 0.766}, {3.6414, 0.734}, {3.7128, 0.678}, {3.7842, 0.624}, {3.8556, 0.57}, {3.927, 0.5}, {3.9984, 0.407}, {4.0698, 0.278}, {4.1412, 0.146}, 
    {4.2126, 0.023}, {4.284, -0.175}, {4.3554, -0.379}, {4.4268, -0.585}, {4.4982, -0.778}, {4.5696, -1.008}, {4.641, -1.277}, {4.7124, -1.56}, {4.7838, -2.07}, {4.8552, -2.48}, {4.9266, -2.7}, {4.998, -2.77}, {5.0694, -2.8}, {5.1408, -2.8}, {5.2122, -2.76}, {5.2836, -2.71}, {5.355, -2.64}, {5.4264, -2.54}, {5.4978, -2.44}, {5.5692, -2.34}, {5.6406, -2.24}, {5.712, -2.12}, {5.7834, -2}, {5.8548, -1.94}, {5.9262, -1.9}, {5.9976, -1.9}, {6.069, -1.85}, {6.1404, -1.75}, {6.2118, -1.63}, {6.283185307, -1.42}}, table_h = {{0, -0.69}, {0.0714, -0.599}, {0.1428, -0.512}, {0.2142, -0.418}, {0.2856, -0.304}, {0.357, -0.181}, {0.4284, -0.078}, {0.4998, -0.011}, {0.5712, 0.032}, {0.6426, 0.074}, {0.714, 0.13}, {0.7854, 0.19}, {0.8568, 0.265}, {0.9282, 0.363}, {0.9996, 0.461}, {1.071, 0.553}, {1.1424, 0.674}, {1.2138, 0.848}, {1.2852, 1.075}, {1.3566, 1.337}, {1.428, 1.629}, {1.4994, 1.929}, {1.5708, 2.18}, {1.6422, 2.334}, {1.7136, 2.518}, {1.785, 2.736}, {1.8564, 2.863}, {1.9278, 2.948}, {1.9992, 3.026}, 
    {2.0706, 3.015}, {2.142, 2.927}, {2.2134, 2.873}, {2.2848, 2.771}, {2.3562, 2.64}, {2.4276, 2.497}, {2.499, 2.441}, {2.5704, 2.378}, {2.6418, 2.336}, {2.7132, 2.288}, {2.7846, 2.209}, {2.856, 2.162}, {2.9274, 2.14}, {2.9988, 2.109}, {3.0702, 2.054}, {3.1416, 1.97}, {3.213, 1.86}, {3.2844, 1.735}, {3.3558, 1.571}, {3.4272, 1.357}, {3.4986, 1.157}, {3.57, 1.106}, {3.6414, 0.927}, {3.7128, 0.846}, {3.7842, 0.744}, {3.8556, 0.64}, {3.927, 0.5}, {3.9984, 0.374}, {4.0698, 0.191}, {4.1412, 0.001}, {4.2126, -0.19}, {4.284, -0.384}, {4.3554, -0.585}, {4.4268, -0.786}, {4.4982, -0.972}, {4.5696, -1.185}, {4.641, -1.372}, {4.7124, -1.5}, {4.7838, -1.94}, {4.8552, -2.16}, {4.9266, -2.29}, {4.998, -2.35}, {5.0694, -2.35}, {5.1408, -2.23}, {5.2122, -2.2}, {5.2836, -2.13}, {5.355, -2.05}, {5.4264, -1.97}, {5.4978, -1.895}, {5.5692, -1.81}, {5.6406, -1.73}, {5.712, -1.6}, {5.7834, -1.42}, {5.8548, -1.13}, {5.9262, -0.95}, {5.9976, -0.93}, {6.069, -0.95}, {6.1404, -1}, {6.2118, -0.92}, {6.283185307, -0.69}}, 
    A = 0.004, qvr = 0.144, Hr = 30, rho_r(displayUnit = "g/cm3") = 1, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {262, -230.80000000000004}, extent = {{10, -10}, {-10, 10}})));
  TYThermoFluidSys.Machines.Generator generator(motorType = TYThermoFluidSys.Utilities.Types.MotorType.ConstantRotatinngSpeed) 
    annotation(Placement(transformation(origin = {231, -210.8}, extent = {{10, -10}, {-10, 10}})));
  TYThermoFluidSys.Volumes.OnephaseVolume volume8(initFromEnthalpy = true, p_start = 50000, h_start = 196e3, V = 1, redeclare package Medium = Modelica.Media.Water.StandardWater, redeclare model volume_type = TYThermoFluidSys.PartialLib.Volumes.Volumes.Volume) 
    annotation(Placement(transformation(origin = {291, -200.8}, extent = {{10, 10}, {-10, -10}}, rotation = 90)));
  TYThermoFluidSys.Machines.SteamTurbine steamTurbine3(p_in_0 = 4.2e6, p_out_0(displayUnit = "bar") = 20000, m_flow_0 = 6, eta_0 = 0.8, h_in_0 = 2925.95e3, redeclare model TurbineEta = TYThermoFluidSys.Machines.Basic.TurbineEffectiveness.EllipticalEfficiency, p_in0 = 3.14e6, p_out0 = 27000, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {140, -1.59999999999998}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Valves.SimpleControlValve controlValve3(p_start = 3.2e6, m_flow_start = 4.5, dp_nominal = 70000, dp_start = 300, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {72, -0.799999999999983}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Boundaries.BoundarySpeed boundarySpeed1(w(displayUnit = "rpm") = 314.159265358979) 
    annotation(Placement(transformation(origin = {114, 23.199999999999974}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume volume3(V = 1, p_start = 3.14e6, T_start = 589.15, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {106, -0.7999999999999758}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume volume4(V = 0.1, p_start = 3.14e6, T_start = 589.15, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {106, -46.80000000000001}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression7(y = 1) 
    annotation(Placement(transformation(origin = {46, 23.199999999999974}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Machines.SteamTurbine steamTurbine2(p_in_0 = 4.2e6, p_out_0(displayUnit = "bar") = 20000, m_flow_0 = 92, eta_0 = 0.8, h_in_0 = 2925.95e3, redeclare model TurbineEta = TYThermoFluidSys.Machines.Basic.TurbineEffectiveness.EllipticalEfficiency, p_in0 = 3.12e6, p_out0 = 30000, CF_eta = 1.2, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {140, 54.39999999999999}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Valves.SimpleControlValve controlValve2(p_start = 3.2e6, m_flow_start = 68.5152, dp_nominal = 21700, dp_start = 21700, m_flow_nominal = 68.5, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {72, 55.19999999999999}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Boundaries.BoundarySpeed boundarySpeed(w(displayUnit = "rpm") = 314.159265358979) 
    annotation(Placement(transformation(origin = {108.00000000000001, 81.19999999999999}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume volume2(V = 2, p_start = 3.12e6, T_start = 589.15, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {108.5, 55.19999999999999}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression8(y = 1) 
    annotation(Placement(transformation(origin = {46, 81.19999999999999}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Machines.SteamTurbine steamTurbine1(p_in_0 = 4.2e6, p_out_0(displayUnit = "bar") = 20000, m_flow_0 = 6, eta_0 = 0.8, h_in_0 = 2925.95e3, redeclare model TurbineEta = TYThermoFluidSys.Machines.Basic.TurbineEffectiveness.EllipticalEfficiency, p_in0 = 3.14e6, p_out0 = 30000, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {140, 107.19999999999999}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Valves.SimpleControlValve controlValve1(p_start = 4.5e6, m_flow_start = 4.5, dp_nominal = 70000, dp_start = 300, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {72, 108}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Boundaries.BoundarySpeed boundarySpeed3(w(displayUnit = "rpm") = 314.159265358979) 
    annotation(Placement(transformation(origin = {108, 144}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume volume1(V = 1, p_start = 3.14e6, T_start = 589.15, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {108, 108}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression9(y = 1) 
    annotation(Placement(transformation(origin = {46, 129.2}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume volume6(V = 2, p_start = 30000, T_start = 341.15, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {236, 55.2}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Valves.ControlValve controlValve7(p_start = 80000, m_flow_start = 68.5, d = 2, dp_start = 2300, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {274.00000000000006, 55.2}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression10(y = 1) 
    annotation(Placement(transformation(origin = {244, 81.19999999999999}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Machines.SteamTurbine steamTurbine5(flange_a(phi(start = 1)), p_in_0 = 4.2e6, p_out_0(displayUnit = "bar") = 20000, m_flow_0 = 1.1, eta_0 = 0.8, h_in_0 = 2925.95e3, redeclare model TurbineEta = TYThermoFluidSys.Machines.Basic.TurbineEffectiveness.EllipticalEfficiency, p_in0 = 3.14e6, p_out0 = 27000, CF_eta = 1, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {-4, -121.60000000000002}, 
    extent = {{-10, 10}, {10, -10}})));
  TYThermoFluidSys.Valves.SimpleControlValve controlValve5(p_start = 3.14e6, m_flow_start = 0.82, dp_nominal = 70000, dp_start = 800, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {-86.99999999999989, -64.80000000000001}, extent = {{-10, 10}, {10, -10}}, rotation = -90)));
  TYThermoFluidSys.Machines.SuterPump suterPump2(qv(start = 0.144), A = 0.04, qvr = 0.144, Hr = 450, table_beta = {{0, -1.42}, {0.0714, -1.328}, {0.1428, -1.211}, {0.2142, -1.056}, {0.2856, -0.87}, {0.357, -0.677}, {0.4284, -0.573}, {0.4998, -0.518}, {0.5712, -0.38}, {0.6426, -0.232}, {0.714, -0.16}, {0.7854, 0}, {0.8568, 0.118}, {0.9282, 0.308}, {0.9996, 0.442}, {1.071, 0.574}, {1.1424, 0.739}, {1.2138, 0.929}, {1.2852, 1.147}, {1.3566, 1.37}, {1.428, 1.599}, {1.4994, 1.839}, {1.5708, 2.08}, {1.6422, 2.3}, {1.7136, 2.48}, {1.785, 2.63}, {1.8564, 2.724}, {1.9278, 2.687}, {1.9992, 2.715}, {2.0706, 2.688}, {2.142, 2.555}, {2.2134, 2.434}, {2.2848, 2.288}, {2.3562, 2.11}, {2.4276, 1.948}, {2.499, 1.825}, {2.5704, 1.732}, {2.6418, 1.644}, {2.7132, 1.576}, {2.7846, 1.533}, {2.856, 1.522}, {2.9274, 1.519}, {2.9988, 1.523}, {3.0702, 1.523}, {3.1416, 1.49}, {3.213, 1.386}, {3.2844, 1.223}, {3.3558, 1.048}, {3.4272, 0.909}, {3.4986, 0.814}, {3.57, 0.766}, {3.6414, 0.734}, {3.7128, 0.678}, {3.7842, 0.624}, {3.8556, 0.57}, {3.927, 0.5}, {3.9984, 0.407}, 
    {4.0698, 0.278}, {4.1412, 0.146}, {4.2126, 0.023}, {4.284, -0.175}, {4.3554, -0.379}, {4.4268, -0.585}, {4.4982, -0.778}, {4.5696, -1.008}, {4.641, -1.277}, {4.7124, -1.56}, {4.7838, -2.07}, {4.8552, -2.48}, {4.9266, -2.7}, {4.998, -2.77}, {5.0694, -2.8}, {5.1408, -2.8}, {5.2122, -2.76}, {5.2836, -2.71}, {5.355, -2.64}, {5.4264, -2.54}, {5.4978, -2.44}, {5.5692, -2.34}, {5.6406, -2.24}, {5.712, -2.12}, {5.7834, -2}, {5.8548, -1.94}, {5.9262, -1.9}, {5.9976, -1.9}, {6.069, -1.85}, {6.1404, -1.75}, {6.2118, -1.63}, {6.283185307, -1.42}}, table_h = {{0, -0.69}, {0.0714, -0.599}, {0.1428, -0.512}, {0.2142, -0.418}, {0.2856, -0.304}, {0.357, -0.181}, {0.4284, -0.078}, {0.4998, -0.011}, {0.5712, 0.032}, {0.6426, 0.074}, {0.714, 0.13}, {0.7854, 0.19}, {0.8568, 0.265}, {0.9282, 0.363}, {0.9996, 0.461}, {1.071, 0.553}, {1.1424, 0.674}, {1.2138, 0.848}, {1.2852, 1.075}, {1.3566, 1.337}, {1.428, 1.629}, {1.4994, 1.929}, {1.5708, 2.18}, {1.6422, 2.334}, {1.7136, 2.518}, {1.785, 2.736}, {1.8564, 2.863}, 
    {1.9278, 2.948}, {1.9992, 3.026}, {2.0706, 3.015}, {2.142, 2.927}, {2.2134, 2.873}, {2.2848, 2.771}, {2.3562, 2.64}, {2.4276, 2.497}, {2.499, 2.441}, {2.5704, 2.378}, {2.6418, 2.336}, {2.7132, 2.288}, {2.7846, 2.209}, {2.856, 2.162}, {2.9274, 2.14}, {2.9988, 2.109}, {3.0702, 2.054}, {3.1416, 1.97}, {3.213, 1.86}, {3.2844, 1.735}, {3.3558, 1.571}, {3.4272, 1.357}, {3.4986, 1.157}, {3.57, 1.106}, {3.6414, 0.927}, {3.7128, 0.846}, {3.7842, 0.744}, {3.8556, 0.64}, {3.927, 0.5}, {3.9984, 0.374}, {4.0698, 0.191}, {4.1412, 0.001}, {4.2126, -0.19}, {4.284, -0.384}, {4.3554, -0.585}, {4.4268, -0.786}, {4.4982, -0.972}, {4.5696, -1.185}, {4.641, -1.372}, {4.7124, -1.5}, {4.7838, -1.94}, {4.8552, -2.16}, {4.9266, -2.29}, {4.998, -2.35}, {5.0694, -2.35}, {5.1408, -2.23}, {5.2122, -2.2}, {5.2836, -2.13}, {5.355, -2.05}, {5.4264, -1.97}, {5.4978, -1.895}, {5.5692, -1.81}, {5.6406, -1.73}, {5.712, -1.6}, {5.7834, -1.42}, {5.8548, -1.13}, {5.9262, -0.95}, {5.9976, -0.93}, {6.069, -0.95}, {6.1404, -1}, 
    {6.2118, -0.92}, {6.283185307, -0.69}}, rho_r = 1, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {88, -200.8}, 
    extent = {{10, -10}, {-10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume volume9(V = 0.5, initFromEnthalpy = true, h_start = 196e3, p_start = 3e5, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {204.25, -230.80000000000004}, extent = {{10, -10}, {-10, 10}})));
  TYThermoFluidSys.Machines.Shaft shaft1(J = 100, N_start = 314.159265358979, If_Speed_Initial = true) 
    annotation(Placement(transformation(origin = {46, -176}, 
    extent = {{10, 10}, {-10, -10}}, 
    rotation = -180)));
  Modelica.Blocks.Sources.RealExpression realExpression11(y = 1) 
    annotation(Placement(transformation(origin = {-122.99999999999994, -64.80000000000001}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume volume5(V = 5, p_start = 3.14e6, T_start = 589.15, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {-58.00000000000003, -121.60000000000004}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume volume(port_b(m_flow(start = -78.5)), V = 2, p_start = 3.14e6, initFromEnthalpy = true, h_start = 3e6, initOpt = TYThermoFluidSys.Utilities.Types.InitOptions.initialValues, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {-122, 175.2}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Valves.SimpleControlValve controlValve(p_start = 3.23e6, m_flow_start = 78.5, dp_start = 90000, dp_nominal = 100000, m_flow_nominal = 80, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {-162, 175.20000000000005}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression12(y = 0.5) 
    annotation(Placement(transformation(origin = {-180, 200.40000000000003}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Valves.SimpleControlValve controlValve6(p_start = 3.1e6, m_flow_start = 0.0006, dp_nominal = 3e6, m_flow_nominal = 0.0005, dp_start = 3.12e6, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {170, 175.2}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression13(y = 1) 
    annotation(Placement(transformation(origin = {140, 200.40000000000003}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Boundaries.BoundaryMdot boundaryMdot2(redeclare package Medium = Modelica.Media.Water.StandardWater, m_flow = 750, energyDefinition = "T", T = 593.15) 
    annotation(Placement(transformation(origin = {-312, -8}, 
    extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Boundaries.BoundaryPressure boundaryPressure5(redeclare package Medium = Modelica.Media.Water.StandardWater, p = 1.5e7, energyDefinition = "h", h = 1300e3) 
    annotation(Placement(transformation(origin = {-312, 81.19999999999999}, 
    extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume volume0(V = 5, initFromEnthalpy = true, h_start = 3e6, initOpt = TYThermoFluidSys.Utilities.Types.InitOptions.initialValues, p_start = 3.23e6, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {-204.00000000000009, 136.0487675663064}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYThermoFluidSys.Volumes.TwophaseVolume volume7(V = 0.5, initFromEnthalpy = true, h_start = 105e3, p_start = 1.12e5, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {254.5, -150.8}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.HeatExchangers.GenericDoublePipeHeatExchanger DoublePipeHEX(n = 5, T_start_in_Prim = 593.15, T_start_out_Prim = 529.15, m_flow_start_Prim = 750, p_start_in_Sec = 4.1e6, p_start_out_Sec = 3.23e6, m_flow_start_Sec = 78.5, useEnthalpy_Sec = true, h_start_in_Sec = 1.6e6, h_start_out_Sec = 3e6, from_dp_Prim = false, L_Prim = 11, L_Sec = 11, r_outer(displayUnit = "m") = 0.018, r_inner(displayUnit = "m") = 0.016, energyDynamics_Wall = Modelica.Fluid.Types.Dynamics.DynamicFreeInitial, 
  redeclare model PressureLoss_Prim = TYThermoFluidSys.Pipelines.Basic.DP_OnePhase.DarcyWeisbach, redeclare model PressureLoss_Sec = TYThermoFluidSys.Pipelines.Basic.DP_OnePhase.DarcyWeisbach, 
  redeclare model HeatTransfer_Prim = TYThermoFluidSys.Pipelines.Basic.HT_OnePhase.DittusBoelter, redeclare model HeatTransfer_Sec = TYThermoFluidSys.Pipelines.Basic.HT_OnePhase.DittusBoelter, L_Wall = 11 * 1400, staticHead_Prim = true, staticHead_Sec = true, height_Sec = 10, height_Prim = 11, D_Prim(displayUnit = "m") = 0.2 / sqrt(1400), D_Sec(displayUnit = "m") = 0.13 / sqrt(1400), p_start_out_Prim = 1.5e7, p_start_in_Prim = 1.51e7, FlowType = TYThermoFluidSys.Utilities.Choices.FlowType.counter_current, CF_HeatTransfer_Prim = 0.5, CF_HeatTransfer_Sec = 1, counterFlow(counterCurrent = TYThermoFluidSys.Utilities.Choices.FlowType.counter_current), T_start_Wall = 529.15, Wall(energyDynamics = TYThermoFluidSys.Utilities.Types.Dynamics.DynamicFreeInitial), CF_PressureLoss_Prim = 1, CF_PressureLoss_Sec = 0.4, initOpt_Sec = TYThermoFluidSys.Utilities.Choices.InitOptions.initialValues, initOpt_Prim = TYThermoFluidSys.Utilities.Choices.InitOptions.initialValues, pipe_Prim(n_channels = fill(1400, 5)), pipe_Sec(n_channels = fill(1400, 5)), dp_State_Sec = false, from_dp_Sec = true, exposeState_b_Wall = true, redeclare package Solid = TYMedia.Solid.Steel_constant, T_reference_Wall = 548.15, exposeState_a_Wall = true, redeclare package Medium_Prim = Modelica.Media.Water.StandardWater, redeclare package Medium_Sec = Modelica.Media.Water.StandardWater, frictionDistribution_Sec = TYThermoFluidSys.Utilities.Choices.FrictionDistribution.FricFric) 
    annotation(Placement(transformation(origin = {-292, 30.048767566306374}, 
    extent = {{30, 10}, {-30, -10}})));
equation
  connect(condenser.Water_out, boundaryPressure.fluidPort) 
    annotation(Line(origin = {317, -79.80000000000001}, points = {{-42.5, -0.29999999999999716}, {-42.5, 15}, {-78, 15}}, color = {0, 178, 226}));
  connect(condenser.Liquid_out, controlValve9.port_a) 
    annotation(Line(origin = {281, -146.8}, points = {{9.699999999999989, 49}, {9.699999999999989, -4}, {10, -4}}, color = {0, 178, 226}));
  connect(realExpression6.y, controlValve8.opening) 
    annotation(Line(origin = {199.5, -137.8}, points = {{15.75, 32.19999999999999}, {18.5, 32.19999999999999}, {18.5, -6}}, color = {0, 0, 127}));
  connect(controlValve8.port_a, suterPump.port_b) 
    annotation(Line(origin = {190.5, -162.8}, points = {{17.5, 12}, {-9.349999999999994, 12}, {-9.349999999999994, 11.999999999999972}}, color = {0, 178, 226}));
  connect(boundaryPressure2.fluidPort, suterPump.port_a) 
    annotation(Line(origin = {147.5, -150.8}, points = {{-13.999999999999972, -2.842170943040401e-14}, {14.050000000000011, -2.842170943040401e-14}}, color = {0, 178, 226}));
  connect(realExpression4.y, controlValve4.opening) 
    annotation(Line(origin = {65, -35.60000000000001}, points = {{-8, 8.799999999999997}, {7.000000000000014, 8.799999999999997}, {7.000000000000014, -4.200000000000003}}, color = {0, 0, 127}));
  connect(shaft.flange_b, suterPump.flange_a) 
    annotation(Line(origin = {145.5, -136.8}, points = {{16.5, 46}, {25.049999999999983, 46}, {25.049999999999983, -5.000000000000028}}, color = {0, 0, 0}));
  connect(steamTurbine4.flange_a, shaft.flange_a) 
    annotation(Line(origin = {124, -94.00000000000004}, points = {{17, 39.400000000000034}, {17, 3.2000000000000313}, {18, 3.2000000000000313}}, color = {0, 0, 0}));
  connect(steamTurbine4.port_out, condenser.Steam_in) 
    annotation(Line(origin = {225, -70.80000000000001}, points = {{-74.80000000000001, 23.200000000000003}, {107, 23.200000000000003}, {107, 0}, {76.5, 0}, {76.5, -4.5}}, color = {0, 178, 226}));
  connect(realExpression5.y, controlValve9.opening) 
    annotation(Line(origin = {284, -149.60000000000002}, points = {{29.5, -11.199999999999989}, {14, -11.199999999999989}}, color = {0, 0, 127}));
  connect(generator.flange_a, suterPump1.flange_a) 
    annotation(Line(origin = {251, -215.8}, points = {{-11.600000000000023, 5}, {11.199999999999989, 5}, {11.199999999999989, -6.000000000000028}}, color = {0, 0, 0}));
  connect(controlValve9.port_b, volume8.port_a) 
    annotation(Line(origin = {291, -180.8}, points = {{0, 10}, {0, -9.599999999999994}}, color = {0, 178, 226}));
  connect(volume8.port_b, suterPump1.port_a) 
    annotation(Line(origin = {281, -220.8}, points = {{10, 10}, {10, -10.000000000000028}, {-9.800000000000011, -10.000000000000028}}, color = {0, 178, 226}));
  connect(boundarySpeed1.flange, steamTurbine3.flange_a) 
    annotation(Line(origin = {132, 18.19999999999999}, points = {{-8, 4.999999999999986}, {9, 4.999999999999986}, {9, -11.999999999999972}}, color = {0, 0, 0}));
  connect(steamTurbine3.port_out, condenser.Steam_in) 
    annotation(Line(origin = {226, -37.80000000000001}, points = {{-75.80000000000001, 37.00000000000003}, {106, 37.00000000000003}, {106, -33}, {75.5, -33}, {75.5, -37.5}}, color = {0, 178, 226}));
  connect(controlValve3.port_b, volume3.port_a) 
    annotation(Line(origin = {89, -0.8000000000000114}, points = {{-7, 2.842170943040401e-14}, {6.599999999999994, 2.842170943040401e-14}, {6.599999999999994, 3.552713678800501e-14}}, color = {0, 178, 226}));
  connect(volume3.port_b, steamTurbine3.port_in) 
    annotation(Line(origin = {125, -0.8000000000000114}, points = {{-9, 3.552713678800501e-14}, {8, 3.552713678800501e-14}, {8, 3.1530333899354446e-14}}, color = {0, 178, 226}));
  connect(controlValve4.port_b, volume4.port_a) 
    annotation(Line(origin = {89, -46.80000000000001}, points = {{-6.999999999999986, 0}, {6.599999999999994, 0}}, color = {0, 178, 226}));
  connect(volume4.port_b, steamTurbine4.port_in) 
    annotation(Line(origin = {125, -46.80000000000001}, points = {{-9, 0}, {8, 0}, {8, -0.7999999999999972}}, color = {0, 178, 226}));
  connect(realExpression7.y, controlValve3.opening) 
    annotation(Line(origin = {65, 44.19999999999999}, points = {{-8, -21.000000000000014}, {7, -21.000000000000014}, {7, -37.99999999999997}}, color = {0, 0, 127}));
  connect(boundarySpeed.flange, steamTurbine2.flange_a) 
    annotation(Line(origin={130,75.2}, 
points={{-12,6},{11,6},{11,-13}}, 
color={0,0,0}));
  connect(steamTurbine2.port_in, volume2.port_b) 
    annotation(Line(origin={126,56.2}, 
points={{7,-1},{-7.5,-1}}, 
color={0,178,226}));
  connect(controlValve2.port_b, volume2.port_a) 
    annotation(Line(origin = {88, 56.19999999999999}, points = {{-6, -1}, {10.099999999999994, -1}}, color = {0, 178, 226}));
  connect(realExpression8.y, controlValve2.opening) 
    annotation(Line(origin = {65, 76.19999999999999}, points = {{-8, 5}, {7, 5}, {7, -14}}, color = {0, 0, 127}));
  connect(controlValve1.port_b, volume1.port_a) 
    annotation(Line(origin = {90, 108.19999999999999}, points = {{-8, -0.19999999999998863}, {7.599999999999994, -0.19999999999998863}}, color = {0, 178, 226}));
  connect(volume1.port_b, steamTurbine1.port_in) 
    annotation(Line(origin = {126, 108.19999999999999}, points = {{-8, -0.19999999999998863}, {7, -0.19999999999998863}, {7, -0.20000000000000284}}, color = {0, 178, 226}));
  connect(realExpression9.y, controlValve1.opening) 
    annotation(Line(origin = {65, 127.19999999999999}, points = {{-8, 2}, {7, 2}, {7, -12.199999999999989}}, color = {0, 0, 127}));
  connect(boundarySpeed3.flange, steamTurbine1.flange_a) 
    annotation(Line(origin = {130, 130.2}, points = {{-12, 13.800000000000011}, {11, 13.800000000000011}, {11, -15.199999999999989}}, color = {0, 0, 0}));
  connect(steamTurbine1.port_out, condenser.Steam_in) 
    annotation(Line(origin = {226, 16.19999999999999}, points = {{-75.80000000000001, 91.8}, {106, 91.8}, {106, -87}, {75.5, -87}, {75.5, -91.5}}, color = {0, 178, 226}));
  connect(steamTurbine2.port_out, volume6.port_a) 
    annotation(Line(origin={185,56.2}, 
points={{-34.8,-1},{40.6,-1},{40.6,-1}}, 
color={0,178,226}));
  connect(volume6.port_b, controlValve7.port_a) 
    annotation(Line(origin = {253, 56.19999999999999}, points = {{-7, -0.9999999999999858}, {11.000000000000057, -0.9999999999999858}}, color = {0, 178, 226}));
  connect(controlValve7.port_b, condenser.Steam_in) 
    annotation(Line(origin = {308, -9.800000000000011}, points = {{-23.999999999999943, 65.00000000000001}, {24, 65.00000000000001}, {24, -61}, {-6.5, -61}, {-6.5, -65.5}}, color = {0, 178, 226}));
  connect(realExpression10.y, controlValve7.opening) 
    annotation(Line(origin = {265, 72.19999999999999}, points = {{-10, 9}, {9.000000000000057, 9}, {9.000000000000057, -9.999999999999986}}, color = {0, 0, 127}));
  connect(volume9.port_b, suterPump2.port_a) 
    annotation(Line(origin = {-2.000000000000057, -186}, 
    points = {{196.25000000000006, -44.80000000000004}, {142, -44.80000000000004}, {142, -14.800000000000011}, {99.20000000000006, -14.800000000000011}}, 
    color = {0, 178, 226}));
  connect(suterPump2.flange_a, shaft1.flange_b) 
    annotation(Line(origin = {-18.000000000000057, -171}, 
    points = {{106.20000000000006, -20.80000000000001}, {106.20000000000006, -5}, {74.00000000000006, -5}}, 
    color = {0, 0, 0}));
  connect(controlValve5.port_b, volume5.port_a) 
    annotation(Line(origin = {-52.99999999999997, -121.80000000000004}, points = {{-33.999999999999915, 47.00000000000003}, {-33.999999999999915, 0.20000000000000284}, {-15.400000000000063, 0.20000000000000284}}, color = {0, 178, 226}));
  connect(volume5.port_b, steamTurbine5.port_in) 
    annotation(Line(origin = {30.000000000000057, -121.80000000000003}, 
    points = {{-78.00000000000009, 0.19999999999998863}, {-41.00000000000006, 0.19999999999998863}, {-41.00000000000006, -0.5999999999999943}}, 
    color = {0, 178, 226}));
  connect(volume9.port_a, suterPump1.port_b) 
    annotation(Line(origin = {228, -230.8}, points = {{-13.349999999999994, -2.842170943040401e-14}, {23.599999999999994, -2.842170943040401e-14}}, color = {0, 178, 226}));
  connect(realExpression11.y, controlValve5.opening) 
    annotation(Line(origin = {-98.99999999999989, -76.60000000000002}, points = {{-13.000000000000057, 11.800000000000011}, {5, 11.800000000000011}}, color = {0, 0, 127}));
  connect(steamTurbine5.flange_a, shaft1.flange_a) 
    annotation(Line(origin = {55, -143.8}, 
    points = {{-58, 14.399999999999977}, {-58, -32.19999999999999}, {-19, -32.19999999999999}}, 
    color = {0, 0, 0}));
  connect(realExpression12.y, controlValve.opening) 
    annotation(Line(origin = {-147, 191.39999999999998}, points = {{-22, 9.000000000000057}, {-15, 9.000000000000057}, {-15, -9.199999999999932}}, color = {0, 0, 127}));
  connect(controlValve.port_b, volume.port_a) 
    annotation(Line(origin = {-123, 175.39999999999998}, points = {{-29, -0.1999999999999318}, {-9.400000000000006, -0.1999999999999318}, {-9.400000000000006, -0.19999999999998863}}, color = {0, 178, 226}));
  connect(volume.port_b, controlValve1.port_a) 
    annotation(Line(origin = {5, 126.19999999999999}, points = {{-117, 49}, {-18, 49}, {-18, -18.19999999999999}, {57, -18.19999999999999}}, color = {0, 178, 226}));
  connect(volume.port_b, controlValve2.port_a) 
    annotation(Line(origin = {5, 100.19999999999999}, points = {{-117, 75}, {-18, 75}, {-18, -45}, {57, -45}}, color = {0, 178, 226}));
  connect(controlValve3.port_a, volume.port_b) 
    annotation(Line(origin = {5, 72.19999999999999}, points = {{57, -72.99999999999997}, {-18, -72.99999999999997}, {-18, 103}, {-117, 103}}, color = {0, 178, 226}));
  connect(controlValve4.port_a, volume.port_b) 
    annotation(Line(origin = {5, 49.19999999999999}, points = {{57.000000000000014, -96}, {-18, -96}, {-18, 126}, {-117, 126}}, color = {0, 178, 226}));
  connect(controlValve5.port_a, volume.port_b) 
    annotation(Line(origin = {-100, 50.199999999999974}, points = {{13.000000000000114, -104.99999999999999}, {13.000000000000114, 125.00000000000001}, {-12, 125.00000000000001}}, color = {0, 178, 226}));
  connect(volume.port_b, controlValve6.port_a) 
    annotation(Line(origin = {51, 175.2}, points = {{-163, 0}, {109, 0}}, color = {0, 178, 226}));
  connect(controlValve6.port_b, volume6.port_a) 
    annotation(Line(origin = {203, 116.19999999999999}, points = {{-23, 59}, {6, 59}, {6, -60.999999999999986}, {22.599999999999994, -60.999999999999986}}, color = {0, 178, 226}));
  connect(realExpression13.y, controlValve6.opening) 
    annotation(Line(origin = {163, 187.2}, points = {{-12, 13.200000000000045}, {7, 13.200000000000045}, {7, -5}}, color = {0, 0, 127}));
  connect(controlValve.port_a, volume0.port_b) 
    annotation(Line(origin = {-187, 146.2}, 
    points = {{15, 29.000000000000057}, {-17.000000000000085, 29.000000000000057}, {-17.000000000000085, -0.1512324336935933}}, 
    color = {0, 178, 226}));
  connect(condenser.Water_in, volume7.port_b) 
    annotation(Line(origin = {270, -134.8}, points = {{4.5, 46}, {4.5, -16}, {-5.5, -16}}, color = {0, 178, 226}));
  connect(volume7.port_a, controlValve8.port_b) 
    annotation(Line(origin = {236, -150.8}, points = {{8.099999999999994, 0}, {-8, 0}}, color = {0, 127, 255}));
  connect(steamTurbine5.port_out, condenser.Steam_in) 
    annotation(Line(origin = {179, -81}, 
    points = {{-172.8, -41.40000000000002}, {138, -41.40000000000002}, {138, 5.699999999999989}, {122.5, 5.699999999999989}}, 
    color = {0, 178, 226}));
  connect(boundaryPressure5.fluidPort, DoublePipeHEX.PortBPrimary) 
    annotation(Line(origin = {-297, 58.048767566306395}, 
    points = {{-7, 23.151232433693593}, {19.587199999999996, 23.151232433693593}, {19.587199999999996, -17.800000000000026}}, 
    color = {0, 178, 226}));
  connect(boundaryMdot2.fluidPort, DoublePipeHEX.PortA_Primary) 
    annotation(Line(origin = {-297, 6.048767566306388}, 
    points = {{-7, -14.048767566306388}, {19.04731257524253, -14.048767566306388}, {19.04731257524253, 13.866302585478628}}, 
    color = {0, 178, 226}));
  connect(volume0.port_a, DoublePipeHEX.PortB_Secondary) 
    annotation(Line(origin = {-221.00000000000003, 81.0487675663064}, 
    points = {{16.999999999999943, 44.599999999999994}, {16.999999999999943, -45.09909250443506}, {-49.15330000000003, -45.09909250443506}}, 
    color = {0, 178, 226}));
  connect(DoublePipeHEX.PortA_Secondary, suterPump2.port_b) 
    annotation(Line(origin = {-84.00000000000003, -84.9512324336936}, 
    points = {{-186.13899081355814, 108.9512324336936}, {-115.99999999999997, 108.9512324336936}, {-115.99999999999997, -115.8487675663064}, {161.60000000000002, -115.8487675663064}}, 
    color = {0, 178, 226}));
  annotation(Documentation(link = "modelica://TYThermoFluidSys/Resources/HTML/SecondLoopSys.html"), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {2, 27}, 
    lineColor = {0, 94, 138}, 
    fillColor = {0, 94, 138}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {2, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5), Line(origin = {2, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5)}), Diagram(coordinateSystem(extent={{-380,-280},{360,240}}, 
grid={2,2}),graphics = {Text(origin={112.686,-332}, 
lineColor={255,0,0}, 
extent={{-357.314,132},{357.314,-132}}, 
textString="在仿真设置的模型翻译页面下，必须开启“参数估值以便优化模型（改善仿真效率）”才能运行", 
textStyle={TextStyle.None}, 
textColor={255,0,0})}), experiment(Algorithm=Dassl,Interval=0.5,StartTime=0,StopTime=5000,Tolerance=1e-05,InlineIntegrator=false,InlineStepSize=false), Protection(access = Access.nonPackageDuplicate), __MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=2500,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="Result", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="质量流量/[kg/s]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 5000), zoom_y_l=(50, 90)), 
Plot(legend=["汽轮机质量流量 [kg/s]"], y=["steamTurbine2.port_in.m_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 5000), zoom_y_l=(240, 320)), 
Plot(legend=["DoublePipeHEX.pipe_Sec.T[5](出口温度) [degC]"], y=["DoublePipeHEX.pipe_Sec.T[5]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 5000), zoom_y_l=(170, 240)), 
Plot(legend=[" DoublePipeHEX.pipe_Sec.T[1](进口温度) [degC]"], y=["DoublePipeHEX.pipe_Sec.T[1]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="汽轮机功率/kW", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5000), zoom_y_l=(35000, 65000)), 
Plot(legend=["汽轮机功率[kW]"], y=["steamTurbine2.P_t"], colors=["4278190335"])})
})));
end SecondLoopSys;