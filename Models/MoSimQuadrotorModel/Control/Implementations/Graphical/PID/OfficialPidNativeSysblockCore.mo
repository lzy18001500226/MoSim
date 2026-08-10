within MoSimQuadrotorModel.Control.Implementations.Graphical.PID;
model OfficialPidNativeSysblockCore
  "Native Sysblock reconstruction of the original six-DOF Official PID law"

  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(
    __MWORKS(version = "26.3.0",modelType = Control,PortArrangement(Left(x_ref, y_ref, z_ref, x_mea, y_mea, z_mea, roll_mea, pitch_mea, yaw_mea), Right(y, y1, y2, y3)),BlockSystem(blockKind = BlockKind.userModel,SampleTime(auto=true,group = "")=0.01,OutputInterval=0.01),SysblockVersion = "1.0"),
    experiment(Algorithm = Euler, StartTime = 0, StopTime = 50, Interval = 0.01));

  SysplorerEmbeddedCoder.Port.Inport x_ref annotation(Placement(transformation(origin = {-520, 310}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Inport y_ref annotation(Placement(transformation(origin = {-520, 250}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Inport z_ref annotation(Placement(transformation(origin = {-520, 120}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Inport x_mea annotation(Placement(transformation(origin = {-520, 270}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Inport y_mea annotation(Placement(transformation(origin = {-520, 210}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Inport z_mea annotation(Placement(transformation(origin = {-520, 80}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin = {-520, -80}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin = {-520, -145}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin = {-520, -230}, extent = {{-12, -12}, {12, 12}})));

  SysplorerEmbeddedCoder.MathOperation.Sum x_error(inputs = "+-") annotation(Placement(transformation(origin = {-445, 290}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum y_error(inputs = "+-") annotation(Placement(transformation(origin = {-445, 230}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum z_error(inputs = "+-") annotation(Placement(transformation(origin = {-445, 100}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain x_p(k = 1.5) annotation(Placement(transformation(origin = {-365, 315}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain y_p(k = 1.5) annotation(Placement(transformation(origin = {-365, 255}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Continuous.Derivative x_derivative annotation(Placement(transformation(origin = {-365, 280}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Continuous.Derivative y_derivative annotation(Placement(transformation(origin = {-365, 220}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain x_d(k = 1) annotation(Placement(transformation(origin = {-285, 280}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain y_d(k = 1) annotation(Placement(transformation(origin = {-285, 220}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum x_pd annotation(Placement(transformation(origin = {-205, 300}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum y_pd annotation(Placement(transformation(origin = {-205, 240}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_ref_scale(k = 0.1) annotation(Placement(transformation(origin = {-125, 300}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_ref_scale(k = 0.1) annotation(Placement(transformation(origin = {-125, 240}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_ref_limit(lowLimit = -0.2617801047120419, upLimit = 0.2617801047120419) annotation(Placement(transformation(origin = {-45, 300}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_ref_limit(lowLimit = -0.2617801047120419, upLimit = 0.2617801047120419) annotation(Placement(transformation(origin = {-45, 240}, extent = {{-14, -12}, {14, 12}})));

  SysplorerEmbeddedCoder.MathOperation.Gain z_p(k = 8) annotation(Placement(transformation(origin = {-365, 145}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Continuous.Integrator z_integral annotation(Placement(transformation(origin = {-365, 100}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Continuous.Derivative z_derivative annotation(Placement(transformation(origin = {-365, 55}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain z_i(k = 6) annotation(Placement(transformation(origin = {-285, 100}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain z_d(k = 4) annotation(Placement(transformation(origin = {-285, 55}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum z_pi annotation(Placement(transformation(origin = {-205, 125}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum thrust_command annotation(Placement(transformation(origin = {-125, 105}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));

  SysplorerEmbeddedCoder.MathOperation.Sum pitch_error(inputs = "+-") annotation(Placement(transformation(origin = {-365, -125}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_error(inputs = "+-") annotation(Placement(transformation(origin = {-365, -60}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Sources.Constant yaw_ref(k = 0) annotation(Placement(transformation(origin = {-445, -250}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_error(inputs = "+-") annotation(Placement(transformation(origin = {-365, -230}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_p(k = 14.142) annotation(Placement(transformation(origin = {-285, -100}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_p(k = 14.142) annotation(Placement(transformation(origin = {-285, -35}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_p(k = 5) annotation(Placement(transformation(origin = {-285, -230}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Continuous.Derivative pitch_derivative annotation(Placement(transformation(origin = {-285, -145}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Continuous.Derivative roll_derivative annotation(Placement(transformation(origin = {-285, -80}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_d(k = 1.414) annotation(Placement(transformation(origin = {-205, -145}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_d(k = 1.414) annotation(Placement(transformation(origin = {-205, -80}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_pd annotation(Placement(transformation(origin = {-125, -110}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_pd annotation(Placement(transformation(origin = {-125, -45}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_limit(lowLimit = -7, upLimit = 7) annotation(Placement(transformation(origin = {-45, -110}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_limit(lowLimit = -7, upLimit = 7) annotation(Placement(transformation(origin = {-45, -45}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation yaw_limit(lowLimit = -7, upLimit = 7) annotation(Placement(transformation(origin = {-125, -230}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_mix(k = 0.707) annotation(Placement(transformation(origin = {35, -110}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_mix(k = 0.707) annotation(Placement(transformation(origin = {35, -45}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_mix(k = 0.707) annotation(Placement(transformation(origin = {-45, -230}, extent = {{-14, -12}, {14, 12}})));

  SysplorerEmbeddedCoder.MathOperation.Sum mixer_1(inputs = "--++") annotation(Placement(transformation(origin = {145, 185}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2, u3, u4)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_2(inputs = "+--+") annotation(Placement(transformation(origin = {145, 65}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2, u3, u4)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_3(inputs = "-+-+") annotation(Placement(transformation(origin = {145, -65}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2, u3, u4)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_4(inputs = "++++") annotation(Placement(transformation(origin = {145, -185}, extent = {{-14, -12}, {14, 12}})), __MWORKS(BlockSystem(Instance(u(u1, u2, u3, u4)))));
  SysplorerEmbeddedCoder.MathOperation.Gain rotor_2_sign(k = -1) annotation(Placement(transformation(origin = {230, 65}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain rotor_4_sign(k = -1) annotation(Placement(transformation(origin = {230, -185}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin = {320, 185}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin = {320, 65}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin = {320, -65}, extent = {{-12, -12}, {12, 12}})));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin = {320, -185}, extent = {{-12, -12}, {12, 12}})));

  model ModelWorkspace
    annotation(__MWORKS(hide = true, BlockSystem(blockKind = BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(x_ref, x_error.u1) 
    annotation(Line(points = {{-508, 310}, {-483.5, 310}, {-483.5, 290}, {-459, 290}}, color = {0, 0, 127}));
  connect(x_mea, x_error.u2) 
    annotation(Line(points = {{-508, 270}, {-483.5, 270}, {-483.5, 290}, {-459, 290}}, color = {0, 0, 127}));
  connect(y_ref, y_error.u1) 
    annotation(Line(points = {{-508, 250}, {-483.5, 250}, {-483.5, 230}, {-459, 230}}, color = {0, 0, 127}));
  connect(y_mea, y_error.u2) 
    annotation(Line(points = {{-508, 210}, {-483.5, 210}, {-483.5, 230}, {-459, 230}}, color = {0, 0, 127}));
  connect(z_ref, z_error.u1) 
    annotation(Line(points = {{-508, 120}, {-483.5, 120}, {-483.5, 100}, {-459, 100}}, color = {0, 0, 127}));
  connect(z_mea, z_error.u2) 
    annotation(Line(points = {{-508, 80}, {-483.5, 80}, {-483.5, 100}, {-459, 100}}, color = {0, 0, 127}));
  connect(x_error.y, x_p.u) 
    annotation(Line(points = {{-431, 290}, {-405, 290}, {-405, 315}, {-379, 315}}, color = {0, 0, 127}));
  connect(x_error.y, x_derivative.u) 
    annotation(Line(points = {{-431, 290}, {-405, 290}, {-405, 280}, {-379, 280}}, color = {0, 0, 127}));
  connect(x_derivative.y, x_d.u) 
    annotation(Line(points = {{-351, 280}, {-299, 280}}, color = {0, 0, 127}));
  connect(x_p.y, x_pd.u1) 
    annotation(Line(points = {{-351, 315}, {-285, 315}, {-285, 300}, {-219, 300}}, color = {0, 0, 127}));
  connect(x_d.y, x_pd.u2) 
    annotation(Line(points = {{-271, 280}, {-245, 280}, {-245, 300}, {-219, 300}}, color = {0, 0, 127}));
  connect(x_pd.y, pitch_ref_scale.u) 
    annotation(Line(points = {{-191, 300}, {-139, 300}}, color = {0, 0, 127}));
  connect(pitch_ref_scale.y, pitch_ref_limit.u) 
    annotation(Line(points = {{-111, 300}, {-59, 300}}, color = {0, 0, 127}));
  connect(y_error.y, y_p.u) 
    annotation(Line(points = {{-431, 230}, {-405, 230}, {-405, 255}, {-379, 255}}, color = {0, 0, 127}));
  connect(y_error.y, y_derivative.u) 
    annotation(Line(points = {{-431, 230}, {-405, 230}, {-405, 220}, {-379, 220}}, color = {0, 0, 127}));
  connect(y_derivative.y, y_d.u) 
    annotation(Line(points = {{-351, 220}, {-299, 220}}, color = {0, 0, 127}));
  connect(y_p.y, y_pd.u1) 
    annotation(Line(points = {{-351, 255}, {-285, 255}, {-285, 240}, {-219, 240}}, color = {0, 0, 127}));
  connect(y_d.y, y_pd.u2) 
    annotation(Line(points = {{-271, 220}, {-245, 220}, {-245, 240}, {-219, 240}}, color = {0, 0, 127}));
  connect(y_pd.y, roll_ref_scale.u) 
    annotation(Line(points = {{-191, 240}, {-139, 240}}, color = {0, 0, 127}));
  connect(roll_ref_scale.y, roll_ref_limit.u) 
    annotation(Line(points = {{-111, 240}, {-59, 240}}, color = {0, 0, 127}));
  connect(z_error.y, z_p.u) 
    annotation(Line(points = {{-431, 100}, {-405, 100}, {-405, 145}, {-379, 145}}, color = {0, 0, 127}));
  connect(z_error.y, z_integral.u1) 
    annotation(Line(points = {{-431, 100}, {-379, 100}}, color = {0, 0, 127}));
  connect(z_error.y, z_derivative.u) 
    annotation(Line(points = {{-431, 100}, {-405, 100}, {-405, 55}, {-379, 55}}, color = {0, 0, 127}));
  connect(z_integral.y, z_i.u) 
    annotation(Line(points = {{-351, 100}, {-299, 100}}, color = {0, 0, 127}));
  connect(z_derivative.y, z_d.u) 
    annotation(Line(points = {{-351, 55}, {-299, 55}}, color = {0, 0, 127}));
  connect(z_p.y, z_pi.u1) 
    annotation(Line(points = {{-351, 145}, {-285, 145}, {-285, 125}, {-219, 125}}, color = {0, 0, 127}));
  connect(z_i.y, z_pi.u2) 
    annotation(Line(points = {{-271, 100}, {-245, 100}, {-245, 125}, {-219, 125}}, color = {0, 0, 127}));
  connect(z_pi.y, thrust_command.u1) 
    annotation(Line(points = {{-191, 125}, {-165, 125}, {-165, 105}, {-139, 105}}, color = {0, 0, 127}));
  connect(z_d.y, thrust_command.u2) 
    annotation(Line(points = {{-271, 55}, {-205, 55}, {-205, 105}, {-139, 105}}, color = {0, 0, 127}));
  connect(pitch_ref_limit.y, pitch_error.u1) 
    annotation(Line(points = {{-45, 288}, {-45, 87.5}, {-365, 87.5}, {-365, -113}}, color = {0, 0, 127}));
  connect(pitch_mea, pitch_error.u2) 
    annotation(Line(points = {{-508, -145}, {-443.5, -145}, {-443.5, -125}, {-379, -125}}, color = {0, 0, 127}));
  connect(roll_ref_limit.y, roll_error.u1) 
    annotation(Line(points = {{-59, 240}, {-205, 240}, {-205, -60}, {-351, -60}}, color = {0, 0, 127}));
  connect(roll_mea, roll_error.u2) 
    annotation(Line(points = {{-508, -80}, {-443.5, -80}, {-443.5, -60}, {-379, -60}}, color = {0, 0, 127}));
  connect(yaw_ref.y, yaw_error.u1) 
    annotation(Line(points = {{-431, -250}, {-405, -250}, {-405, -230}, {-379, -230}}, color = {0, 0, 127}));
  connect(yaw_mea, yaw_error.u2) 
    annotation(Line(points = {{-508, -230}, {-379, -230}}, color = {0, 0, 127}));
  connect(pitch_error.y, pitch_p.u) 
    annotation(Line(points = {{-351, -125}, {-325, -125}, {-325, -100}, {-299, -100}}, color = {0, 0, 127}));
  connect(pitch_error.y, pitch_derivative.u) 
    annotation(Line(points = {{-351, -125}, {-325, -125}, {-325, -145}, {-299, -145}}, color = {0, 0, 127}));
  connect(pitch_derivative.y, pitch_d.u) 
    annotation(Line(points = {{-271, -145}, {-219, -145}}, color = {0, 0, 127}));
  connect(pitch_p.y, pitch_pd.u1) 
    annotation(Line(points = {{-271, -100}, {-205, -100}, {-205, -110}, {-139, -110}}, color = {0, 0, 127}));
  connect(pitch_d.y, pitch_pd.u2) 
    annotation(Line(points = {{-191, -145}, {-165, -145}, {-165, -110}, {-139, -110}}, color = {0, 0, 127}));
  connect(pitch_pd.y, pitch_limit.u) 
    annotation(Line(points = {{-111, -110}, {-59, -110}}, color = {0, 0, 127}));
  connect(roll_error.y, roll_p.u) 
    annotation(Line(points = {{-351, -60}, {-325, -60}, {-325, -35}, {-299, -35}}, color = {0, 0, 127}));
  connect(roll_error.y, roll_derivative.u) 
    annotation(Line(points = {{-351, -60}, {-325, -60}, {-325, -80}, {-299, -80}}, color = {0, 0, 127}));
  connect(roll_derivative.y, roll_d.u) 
    annotation(Line(points = {{-271, -80}, {-219, -80}}, color = {0, 0, 127}));
  connect(roll_p.y, roll_pd.u1) 
    annotation(Line(points = {{-271, -35}, {-205, -35}, {-205, -45}, {-139, -45}}, color = {0, 0, 127}));
  connect(roll_d.y, roll_pd.u2) 
    annotation(Line(points = {{-191, -80}, {-165, -80}, {-165, -45}, {-139, -45}}, color = {0, 0, 127}));
  connect(roll_pd.y, roll_limit.u) 
    annotation(Line(points = {{-111, -45}, {-59, -45}}, color = {0, 0, 127}));
  connect(yaw_error.y, yaw_p.u) 
    annotation(Line(points = {{-351, -230}, {-299, -230}}, color = {0, 0, 127}));
  connect(yaw_p.y, yaw_limit.u) 
    annotation(Line(points = {{-271, -230}, {-139, -230}}, color = {0, 0, 127}));
  connect(pitch_limit.y, pitch_mix.u) 
    annotation(Line(points = {{-31, -110}, {21, -110}}, color = {0, 0, 127}));
  connect(roll_limit.y, roll_mix.u) 
    annotation(Line(points = {{-31, -45}, {21, -45}}, color = {0, 0, 127}));
  connect(yaw_limit.y, yaw_mix.u) 
    annotation(Line(points = {{-111, -230}, {-59, -230}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_1.u1) 
    annotation(Line(points = {{-45, -218}, {-45, -22.5}, {145, -22.5}, {145, 173}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_1.u2) 
    annotation(Line(points = {{35, -98}, {35, 37.5}, {145, 37.5}, {145, 173}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_1.u3) 
    annotation(Line(points = {{35, -33}, {35, 70}, {145, 70}, {145, 173}}, color = {0, 0, 127}));
  connect(thrust_command.y, mixer_1.u4) 
    annotation(Line(points = {{-111, 105}, {10, 105}, {10, 185}, {131, 185}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_2.u1) 
    annotation(Line(points = {{-45, -218}, {-45, -82.5}, {145, -82.5}, {145, 53}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_2.u2) 
    annotation(Line(points = {{35, -98}, {35, -22.5}, {145, -22.5}, {145, 53}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_2.u3) 
    annotation(Line(points = {{49, -45}, {90, -45}, {90, 65}, {131, 65}}, color = {0, 0, 127}));
  connect(thrust_command.y, mixer_2.u4) 
    annotation(Line(points = {{-111, 105}, {10, 105}, {10, 65}, {131, 65}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_3.u1) 
    annotation(Line(points = {{-31, -230}, {50, -230}, {50, -65}, {131, -65}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_3.u2) 
    annotation(Line(points = {{49, -110}, {90, -110}, {90, -65}, {131, -65}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_3.u3) 
    annotation(Line(points = {{49, -45}, {90, -45}, {90, -65}, {131, -65}}, color = {0, 0, 127}));
  connect(thrust_command.y, mixer_3.u4) 
    annotation(Line(points = {{-111, 105}, {10, 105}, {10, -65}, {131, -65}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_4.u1) 
    annotation(Line(points = {{-31, -230}, {50, -230}, {50, -185}, {131, -185}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_4.u2) 
    annotation(Line(points = {{49, -110}, {90, -110}, {90, -185}, {131, -185}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_4.u3) 
    annotation(Line(points = {{35, -57}, {35, -115}, {145, -115}, {145, -173}}, color = {0, 0, 127}));
  connect(thrust_command.y, mixer_4.u4) 
    annotation(Line(points = {{-125, 93}, {-125, -40}, {145, -40}, {145, -173}}, color = {0, 0, 127}));
  connect(mixer_1.y, y) 
    annotation(Line(points = {{159, 185}, {308, 185}}, color = {0, 0, 127}));
  connect(mixer_2.y, rotor_2_sign.u) 
    annotation(Line(points = {{159, 65}, {216, 65}}, color = {0, 0, 127}));
  connect(rotor_2_sign.y, y1) 
    annotation(Line(points = {{244, 65}, {308, 65}}, color = {0, 0, 127}));
  connect(mixer_3.y, y2) 
    annotation(Line(points = {{159, -65}, {308, -65}}, color = {0, 0, 127}));
  connect(mixer_4.y, rotor_4_sign.u) 
    annotation(Line(points = {{159, -185}, {216, -185}}, color = {0, 0, 127}));
  connect(rotor_4_sign.y, y3) 
    annotation(Line(points = {{244, -185}, {308, -185}}, color = {0, 0, 127}));
end OfficialPidNativeSysblockCore;