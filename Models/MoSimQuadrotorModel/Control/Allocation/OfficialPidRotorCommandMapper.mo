within MoSimQuadrotorModel.Control.Allocation;
model OfficialPidRotorCommandMapper
  "Expandable Official PID mixer-to-rotor command mapping"

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / 13.985413115099604;
  parameter Real yaw_authority_scale =
    0.016 / profile.moment_constant_ratio_m;
  parameter Real yaw_pattern[4] = {
    -profile.mworks_yaw_direction[1],
    -profile.mworks_yaw_direction[2],
    -profile.mworks_yaw_direction[3],
    -profile.mworks_yaw_direction[4]};

  Modelica.Blocks.Interfaces.RealInput amplitude_command[4]
    "Signed mixer amplitudes from the graphical Official PID core" 
    annotation(Placement(
      transformation(origin = {-250, 0}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, 0}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4](each unit = "rad/s")
    "Signed visual rotor-speed command sent to the plant boundary" 
    annotation(Placement(
      transformation(origin = {250, 110}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, 43}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput direct_control_bus[10]
    "[yaw, non-yaw(2:5), mapped(6:9), collective error(10)]" 
    annotation(Placement(
      transformation(origin = {250, -90}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, -60}, extent = {{-8, -8}, {8, 8}})));
  Real yaw_amplitude;
  Real non_yaw_amplitude[4];
  Real mapped_amplitude[4];
  Real mapped_collective_amplitude_error;

  Modelica.Blocks.Math.Gain yaw_projection_1(k = yaw_pattern[1] / 4) 
    annotation(Placement(transformation(origin = {-180, 150}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_projection_2(k = yaw_pattern[2] / 4) 
    annotation(Placement(transformation(origin = {-180, 100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_projection_3(k = yaw_pattern[3] / 4) 
    annotation(Placement(transformation(origin = {-180, 50}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_projection_4(k = yaw_pattern[4] / 4) 
    annotation(Placement(transformation(origin = {-180, 0}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add3 yaw_sum_first3(k1 = 1, k2 = 1, k3 = 1) 
    annotation(Placement(transformation(origin = {-105, 100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add yaw_sum(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {-35, 85}, extent = {{-18, -12}, {18, 12}})));

  Modelica.Blocks.Math.Gain yaw_component_1(k = yaw_pattern[1]) 
    annotation(Placement(transformation(origin = {5, 150}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_component_2(k = yaw_pattern[2]) 
    annotation(Placement(transformation(origin = {5, 100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_component_3(k = yaw_pattern[3]) 
    annotation(Placement(transformation(origin = {5, 50}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_component_4(k = yaw_pattern[4]) 
    annotation(Placement(transformation(origin = {5, 0}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add non_yaw_1(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {65, 150}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add non_yaw_2(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {65, 100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add non_yaw_3(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {65, 50}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add non_yaw_4(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {65, 0}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_authority_1(k = yaw_pattern[1] * yaw_authority_scale) 
    annotation(Placement(transformation(origin = {115, 150}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_authority_2(k = yaw_pattern[2] * yaw_authority_scale) 
    annotation(Placement(transformation(origin = {115, 100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_authority_3(k = yaw_pattern[3] * yaw_authority_scale) 
    annotation(Placement(transformation(origin = {115, 50}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_authority_4(k = yaw_pattern[4] * yaw_authority_scale) 
    annotation(Placement(transformation(origin = {115, 0}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add mapped_1(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {165, 150}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add mapped_2(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {165, 100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add mapped_3(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {165, 50}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add mapped_4(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {165, 0}, extent = {{-18, -12}, {18, 12}})));

  Modelica.Blocks.Math.Gain command_scale_1(k = command_scale) 
    annotation(Placement(transformation(origin = {210, 150}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Gain command_scale_2(k = command_scale) 
    annotation(Placement(transformation(origin = {210, 100}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Gain command_scale_3(k = command_scale) 
    annotation(Placement(transformation(origin = {210, 50}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Gain command_scale_4(k = command_scale) 
    annotation(Placement(transformation(origin = {210, 0}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Sources.Constant hover_1(k = hover_speed) 
    annotation(Placement(transformation(origin = {165, 185}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Sources.Constant hover_2(k = hover_speed) 
    annotation(Placement(transformation(origin = {165, 135}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Sources.Constant hover_3(k = hover_speed) 
    annotation(Placement(transformation(origin = {165, 85}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Sources.Constant hover_4(k = hover_speed) 
    annotation(Placement(transformation(origin = {165, 35}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Add hover_plus_1(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {235, 150}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Add hover_plus_2(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {235, 100}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Add hover_plus_3(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {235, 50}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Add hover_plus_4(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {235, 0}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Gain spin_sign_1(k = profile.mworks_spin_command_sign[1]) 
    annotation(Placement(transformation(origin = {285, 150}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Gain spin_sign_2(k = profile.mworks_spin_command_sign[2]) 
    annotation(Placement(transformation(origin = {285, 100}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Gain spin_sign_3(k = profile.mworks_spin_command_sign[3]) 
    annotation(Placement(transformation(origin = {285, 50}, extent = {{-12, -10}, {12, 10}})));
  Modelica.Blocks.Math.Gain spin_sign_4(k = profile.mworks_spin_command_sign[4]) 
    annotation(Placement(transformation(origin = {285, 0}, extent = {{-12, -10}, {12, 10}})));

  Modelica.Blocks.Math.Add3 mapped_sum_first3(k1 = 1, k2 = 1, k3 = 1) 
    annotation(Placement(transformation(origin = {75, -100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add mapped_sum(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {145, -100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add3 amplitude_sum_first3(k1 = 1, k2 = 1, k3 = 1) 
    annotation(Placement(transformation(origin = {75, -150}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add amplitude_sum(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {145, -150}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add collective_error(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {205, -125}, extent = {{-18, -12}, {18, 12}})));
equation
  connect(amplitude_command[1], yaw_projection_1.u) 
    annotation(Line(points = {{-250, 0}, {-215, 0}, {-215, 150}, {-198, 150}}, color = {0, 0, 127}));
  connect(amplitude_command[2], yaw_projection_2.u) 
    annotation(Line(points = {{-250, 0}, {-220, 0}, {-220, 100}, {-198, 100}}, color = {0, 0, 127}));
  connect(amplitude_command[3], yaw_projection_3.u) 
    annotation(Line(points = {{-250, 0}, {-225, 0}, {-225, 50}, {-198, 50}}, color = {0, 0, 127}));
  connect(amplitude_command[4], yaw_projection_4.u) 
    annotation(Line(points = {{-250, 0}, {-230, 0}, {-230, 0}, {-198, 0}}, color = {0, 0, 127}));
  connect(yaw_projection_1.y, yaw_sum_first3.u1) 
    annotation(Line(points = {{-162, 150}, {-140, 150}, {-140, 112}, {-123, 112}}, color = {0, 0, 127}));
  connect(yaw_projection_2.y, yaw_sum_first3.u2) 
    annotation(Line(points = {{-162, 100}, {-123, 100}}, color = {0, 0, 127}));
  connect(yaw_projection_3.y, yaw_sum_first3.u3) 
    annotation(Line(points = {{-162, 50}, {-140, 50}, {-140, 88}, {-123, 88}}, color = {0, 0, 127}));
  connect(yaw_sum_first3.y, yaw_sum.u1) 
    annotation(Line(points = {{-87, 100}, {-70, 100}, {-70, 97}, {-53, 97}}, color = {0, 0, 127}));
  connect(yaw_projection_4.y, yaw_sum.u2) 
    annotation(Line(points = {{-162, 0}, {-70, 0}, {-70, 73}, {-53, 73}}, color = {0, 0, 127}));
  yaw_amplitude = yaw_sum.y;

  connect(yaw_sum.y, yaw_component_1.u) 
    annotation(Line(points = {{-17, 85}, {-5, 85}, {-5, 150}, {-13, 150}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_component_2.u) 
    annotation(Line(points = {{-17, 85}, {-5, 85}, {-5, 100}, {-13, 100}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_component_3.u) 
    annotation(Line(points = {{-17, 85}, {-5, 85}, {-5, 50}, {-13, 50}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_component_4.u) 
    annotation(Line(points = {{-17, 85}, {-5, 85}, {-5, 0}, {-13, 0}}, color = {0, 0, 127}));
  connect(amplitude_command[1], non_yaw_1.u1) 
    annotation(Line(points = {{-250, 0}, {-230, 0}, {-230, 162}, {47, 162}}, color = {0, 0, 127}));
  connect(yaw_component_1.y, non_yaw_1.u2) 
    annotation(Line(points = {{23, 150}, {47, 138}}, color = {0, 0, 127}));
  connect(amplitude_command[2], non_yaw_2.u1) 
    annotation(Line(points = {{-250, 0}, {-225, 0}, {-225, 112}, {47, 112}}, color = {0, 0, 127}));
  connect(yaw_component_2.y, non_yaw_2.u2) 
    annotation(Line(points = {{23, 100}, {47, 88}}, color = {0, 0, 127}));
  connect(amplitude_command[3], non_yaw_3.u1) 
    annotation(Line(points = {{-250, 0}, {-220, 0}, {-220, 62}, {47, 62}}, color = {0, 0, 127}));
  connect(yaw_component_3.y, non_yaw_3.u2) 
    annotation(Line(points = {{23, 50}, {47, 38}}, color = {0, 0, 127}));
  connect(amplitude_command[4], non_yaw_4.u1) 
    annotation(Line(points = {{-250, 0}, {-215, 0}, {-215, 12}, {47, 12}}, color = {0, 0, 127}));
  connect(yaw_component_4.y, non_yaw_4.u2) 
    annotation(Line(points = {{23, 0}, {47, -12}}, color = {0, 0, 127}));
  non_yaw_amplitude[1] = non_yaw_1.y;
  non_yaw_amplitude[2] = non_yaw_2.y;
  non_yaw_amplitude[3] = non_yaw_3.y;
  non_yaw_amplitude[4] = non_yaw_4.y;

  connect(yaw_sum.y, yaw_authority_1.u) 
    annotation(Line(points = {{-17, 85}, {25, 85}, {25, 150}, {97, 150}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_2.u) 
    annotation(Line(points = {{-17, 85}, {30, 85}, {30, 100}, {97, 100}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_3.u) 
    annotation(Line(points = {{-17, 85}, {35, 85}, {35, 50}, {97, 50}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_4.u) 
    annotation(Line(points = {{-17, 85}, {40, 85}, {40, 0}, {97, 0}}, color = {0, 0, 127}));
  connect(non_yaw_1.y, mapped_1.u1) 
    annotation(Line(points = {{83, 150}, {147, 162}}, color = {0, 0, 127}));
  connect(yaw_authority_1.y, mapped_1.u2) 
    annotation(Line(points = {{133, 150}, {147, 138}}, color = {0, 0, 127}));
  connect(non_yaw_2.y, mapped_2.u1) 
    annotation(Line(points = {{83, 100}, {147, 112}}, color = {0, 0, 127}));
  connect(yaw_authority_2.y, mapped_2.u2) 
    annotation(Line(points = {{133, 100}, {147, 88}}, color = {0, 0, 127}));
  connect(non_yaw_3.y, mapped_3.u1) 
    annotation(Line(points = {{83, 50}, {147, 62}}, color = {0, 0, 127}));
  connect(yaw_authority_3.y, mapped_3.u2) 
    annotation(Line(points = {{133, 50}, {147, 38}}, color = {0, 0, 127}));
  connect(non_yaw_4.y, mapped_4.u1) 
    annotation(Line(points = {{83, 0}, {147, 12}}, color = {0, 0, 127}));
  connect(yaw_authority_4.y, mapped_4.u2) 
    annotation(Line(points = {{133, 0}, {147, -12}}, color = {0, 0, 127}));
  mapped_amplitude[1] = mapped_1.y;
  mapped_amplitude[2] = mapped_2.y;
  mapped_amplitude[3] = mapped_3.y;
  mapped_amplitude[4] = mapped_4.y;

  connect(mapped_1.y, command_scale_1.u) 
    annotation(Line(points = {{183, 150}, {198, 150}}, color = {0, 0, 127}));
  connect(mapped_2.y, command_scale_2.u) 
    annotation(Line(points = {{183, 100}, {198, 100}}, color = {0, 0, 127}));
  connect(mapped_3.y, command_scale_3.u) 
    annotation(Line(points = {{183, 50}, {198, 50}}, color = {0, 0, 127}));
  connect(mapped_4.y, command_scale_4.u) 
    annotation(Line(points = {{183, 0}, {198, 0}}, color = {0, 0, 127}));
  connect(command_scale_1.y, hover_plus_1.u1) 
    annotation(Line(points = {{222, 150}, {223, 150}}, color = {0, 0, 127}));
  connect(command_scale_2.y, hover_plus_2.u1) 
    annotation(Line(points = {{222, 100}, {223, 100}}, color = {0, 0, 127}));
  connect(command_scale_3.y, hover_plus_3.u1) 
    annotation(Line(points = {{222, 50}, {223, 50}}, color = {0, 0, 127}));
  connect(command_scale_4.y, hover_plus_4.u1) 
    annotation(Line(points = {{222, 0}, {223, 0}}, color = {0, 0, 127}));
  connect(hover_1.y, hover_plus_1.u2) 
    annotation(Line(points = {{177, 185}, {200, 185}, {200, 150}, {223, 150}}, color = {0, 0, 127}));
  connect(hover_2.y, hover_plus_2.u2) 
    annotation(Line(points = {{177, 135}, {205, 135}, {205, 100}, {223, 100}}, color = {0, 0, 127}));
  connect(hover_3.y, hover_plus_3.u2) 
    annotation(Line(points = {{177, 85}, {210, 85}, {210, 50}, {223, 50}}, color = {0, 0, 127}));
  connect(hover_4.y, hover_plus_4.u2) 
    annotation(Line(points = {{177, 35}, {215, 35}, {215, 0}, {223, 0}}, color = {0, 0, 127}));
  connect(hover_plus_1.y, spin_sign_1.u) 
    annotation(Line(points = {{247, 150}, {273, 150}}, color = {0, 0, 127}));
  connect(hover_plus_2.y, spin_sign_2.u) 
    annotation(Line(points = {{247, 100}, {273, 100}}, color = {0, 0, 127}));
  connect(hover_plus_3.y, spin_sign_3.u) 
    annotation(Line(points = {{247, 50}, {273, 50}}, color = {0, 0, 127}));
  connect(hover_plus_4.y, spin_sign_4.u) 
    annotation(Line(points = {{247, 0}, {273, 0}}, color = {0, 0, 127}));
  connect(spin_sign_1.y, rotor_command[1]) 
    annotation(Line(points = {{297, 150}, {320, 150}, {320, 110}, {250, 110}}, color = {0, 0, 127}));
  connect(spin_sign_2.y, rotor_command[2]) 
    annotation(Line(points = {{297, 100}, {330, 100}, {330, 110}, {250, 110}}, color = {0, 0, 127}));
  connect(spin_sign_3.y, rotor_command[3]) 
    annotation(Line(points = {{297, 50}, {340, 50}, {340, 110}, {250, 110}}, color = {0, 0, 127}));
  connect(spin_sign_4.y, rotor_command[4]) 
    annotation(Line(points = {{297, 0}, {350, 0}, {350, 110}, {250, 110}}, color = {0, 0, 127}));

  connect(mapped_1.y, mapped_sum_first3.u1) 
    annotation(Line(points = {{183, 150}, {50, 150}, {50, -88}, {57, -88}}, color = {0, 0, 127}));
  connect(mapped_2.y, mapped_sum_first3.u2) 
    annotation(Line(points = {{183, 100}, {45, 100}, {45, -100}, {57, -100}}, color = {0, 0, 127}));
  connect(mapped_3.y, mapped_sum_first3.u3) 
    annotation(Line(points = {{183, 50}, {40, 50}, {40, -112}, {57, -112}}, color = {0, 0, 127}));
  connect(mapped_sum_first3.y, mapped_sum.u1) 
    annotation(Line(points = {{93, -100}, {110, -100}, {110, -88}, {127, -88}}, color = {0, 0, 127}));
  connect(mapped_4.y, mapped_sum.u2) 
    annotation(Line(points = {{183, 0}, {115, 0}, {115, -112}, {127, -112}}, color = {0, 0, 127}));
  connect(amplitude_command[1], amplitude_sum_first3.u1) 
    annotation(Line(points = {{-250, 0}, {-240, 0}, {-240, -138}, {57, -138}}, color = {0, 0, 127}));
  connect(amplitude_command[2], amplitude_sum_first3.u2) 
    annotation(Line(points = {{-250, 0}, {-235, 0}, {-235, -150}, {57, -150}}, color = {0, 0, 127}));
  connect(amplitude_command[3], amplitude_sum_first3.u3) 
    annotation(Line(points = {{-250, 0}, {-230, 0}, {-230, -162}, {57, -162}}, color = {0, 0, 127}));
  connect(amplitude_sum_first3.y, amplitude_sum.u1) 
    annotation(Line(points = {{93, -150}, {110, -150}, {110, -138}, {127, -138}}, color = {0, 0, 127}));
  connect(amplitude_command[4], amplitude_sum.u2) 
    annotation(Line(points = {{-250, 0}, {-225, 0}, {-225, -175}, {110, -175}, {110, -162}, {127, -162}}, color = {0, 0, 127}));
  connect(mapped_sum.y, collective_error.u1) 
    annotation(Line(points = {{163, -100}, {170, -100}, {170, -113}, {187, -113}}, color = {0, 0, 127}));
  connect(amplitude_sum.y, collective_error.u2) 
    annotation(Line(points = {{163, -150}, {175, -150}, {175, -137}, {187, -137}}, color = {0, 0, 127}));
  mapped_collective_amplitude_error = collective_error.y;
  direct_control_bus[1] = yaw_amplitude;
  direct_control_bus[2:5] = non_yaw_amplitude;
  direct_control_bus[6:9] = mapped_amplitude;
  direct_control_bus[10] = mapped_collective_amplitude_error;

  annotation(
    Icon(coordinateSystem(extent = {{-100, 100}, {100, -100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 100, 130},
        fillColor = {238, 250, 255}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 25}, extent = {{-85, 18}, {85, -18}},
        textString = "YAW", textColor = {0, 100, 130}),
      Text(origin = {0, -18}, extent = {{-92, 18}, {92, -18}},
        textString = "ROTOR MAP", textColor = {0, 100, 130})}),
    Diagram(coordinateSystem(extent = {{-270, -180}, {310, 205}}, grid = {5, 5})),
    __MWORKS(version = "26.3.0"));
end OfficialPidRotorCommandMapper;