within MoSimQuadrotorModel.Control.Implementations.Graphical.ProjectOwned;
model MoSim_OptimizedSSGraphicalController "Optimized pure graphical ss controller"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(x_error, y_error, z_error, z_ref_rate, roll_mea, pitch_mea, yaw_mea, yaw_ref), Right(y, y1, y2, y3)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.02),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1));
  SysplorerEmbeddedCoder.Port.Inport x_error 
    annotation (Placement(transformation(origin = {-720, 270}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Inport y_error 
    annotation (Placement(transformation(origin = {-720, 220}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Inport z_error 
    annotation (Placement(transformation(origin = {-720, 170}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate 
    annotation (Placement(transformation(origin = {-720, 120}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Inport roll_mea 
    annotation (Placement(transformation(origin = {-720, 45}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea 
    annotation (Placement(transformation(origin = {-720, 0}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea 
    annotation (Placement(transformation(origin = {-720, -45}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref 
    annotation (Placement(transformation(origin = {-720, -90}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Outport y 
    annotation (Placement(transformation(origin = {720, 190}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Outport y1 
    annotation (Placement(transformation(origin = {720, 70}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Outport y2 
    annotation (Placement(transformation(origin = {720, -50}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Port.Outport y3 
    annotation (Placement(transformation(origin = {720, -170}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Discrete.DiscreteStateSpace x_outer_ss(A={{0.82, 0}, {0, 0.55}},B={{0.18}, {0.45}},C={{0.08, 0.04}},D={{0.06}})
    "x-error to pitch-reference discrete ss compensator" annotation (Placement(transformation(origin = {-560, 260}, extent = {{-39, -23}, {39, 23}})));
  SysplorerEmbeddedCoder.Discrete.DiscreteStateSpace y_outer_ss(A={{0.82, 0}, {0, 0.55}},B={{0.18}, {0.45}},C={{0.08, 0.04}},D={{0.06}})
    "y-error to roll-reference discrete ss compensator" annotation (Placement(transformation(origin = {-560, 210}, extent = {{-39, -23}, {39, 23}})));
  SysplorerEmbeddedCoder.Discrete.DiscreteStateSpace z_outer_ss(A={{0.93, 0}, {0, 0.60}},B={{0.07}, {0.40}},C={{7.0, 2.0}},D={{1.5}})
    "z-error to collective-thrust discrete ss compensator" annotation (Placement(transformation(origin = {-560, 160}, extent = {{-39, -23}, {39, 23}})));
  SysplorerEmbeddedCoder.Discrete.DiscreteStateSpace roll_inner_ss(A={{0.74, 0}, {0, 0.50}},B={{0.26}, {0.50}},C={{2.0, 1.2}},D={{3.0}})
    "roll-error attitude discrete ss compensator" annotation (Placement(transformation(origin = {-270, 70}, extent = {{-39, -23}, {39, 23}})));
  SysplorerEmbeddedCoder.Discrete.DiscreteStateSpace pitch_inner_ss(A={{0.74, 0}, {0, 0.50}},B={{0.26}, {0.50}},C={{2.0, 1.2}},D={{3.0}})
    "pitch-error attitude discrete ss compensator" annotation (Placement(transformation(origin = {-270, 15}, extent = {{-39, -23}, {39, 23}})));
  SysplorerEmbeddedCoder.Discrete.DiscreteStateSpace yaw_inner_ss(A={{0.70, 0}, {0, 0.45}},B={{0.30}, {0.55}},C={{1.0, 0.4}},D={{3.6}})
    "yaw-error attitude discrete ss compensator" annotation (Placement(transformation(origin = {-270, -40}, extent = {{-39, -23}, {39, 23}})));
  SysplorerEmbeddedCoder.MathOperation.Gain z_feedforward(k=0.35) 
    annotation (Placement(transformation(origin = {-560, 115}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum thrust_command_sum(inputs="++")
    "State-space collective channel plus explicit vertical feed-forward" annotation (Placement(transformation(origin = {-370, 145}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_ref_limit(upLimit=0.2617801047,lowLimit=-0.2617801047)
    "Outer-loop pitch reference safety limit" annotation (Placement(transformation(origin = {-370, 260}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_ref_limit(upLimit=0.2617801047,lowLimit=-0.2617801047)
    "Outer-loop roll reference safety limit" annotation (Placement(transformation(origin = {-370, 210}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_error(inputs="+-") 
    annotation (Placement(transformation(origin = {-430, 70}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_error(inputs="+-") 
    annotation (Placement(transformation(origin = {-430, 15}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_error(inputs="+-") 
    annotation (Placement(transformation(origin = {-430, -40}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation thrust_limit(upLimit=20.0,lowLimit=-20.0)
    "Collective command safety limit" annotation (Placement(transformation(origin = {-270, 145}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_limit(upLimit=6.5,lowLimit=-6.5)
    "Roll torque command safety limit" annotation (Placement(transformation(origin = {-80, 70}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_limit(upLimit=6.5,lowLimit=-6.5)
    "Pitch torque command safety limit" annotation (Placement(transformation(origin = {-80, 15}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation yaw_limit(upLimit=6.5,lowLimit=-6.5)
    "Yaw torque command safety limit" annotation (Placement(transformation(origin = {-80, -40}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m1_roll_gain(k=0.707) 
    annotation (Placement(transformation(origin = {80, 210}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m1_pitch_gain(k=-0.707) 
    annotation (Placement(transformation(origin = {80, 190}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m1_yaw_gain(k=-0.707) 
    annotation (Placement(transformation(origin = {80, 170}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum m1_thrust_roll_sum(inputs="++") 
    annotation (Placement(transformation(origin = {180, 202}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum m1_pitch_yaw_sum(inputs="++") 
    annotation (Placement(transformation(origin = {180, 178}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum m1_mix_sum(inputs="++") 
    annotation (Placement(transformation(origin = {260, 190}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation m1_limit(upLimit=20.0,lowLimit=-20.0) 
    annotation (Placement(transformation(origin = {360, 190}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m2_roll_gain(k=-0.707) 
    annotation (Placement(transformation(origin = {80, 90}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m2_pitch_gain(k=-0.707) 
    annotation (Placement(transformation(origin = {80, 70}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m2_yaw_gain(k=0.707) 
    annotation (Placement(transformation(origin = {80, 50}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum m2_thrust_roll_sum(inputs="++") 
    annotation (Placement(transformation(origin = {180, 82}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum m2_pitch_yaw_sum(inputs="++") 
    annotation (Placement(transformation(origin = {180, 58}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum m2_mix_sum(inputs="++") 
    annotation (Placement(transformation(origin = {260, 70}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation m2_limit(upLimit=20.0,lowLimit=-20.0) 
    annotation (Placement(transformation(origin = {360, 70}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m3_roll_gain(k=-0.707) 
    annotation (Placement(transformation(origin = {80, -30}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m3_pitch_gain(k=0.707) 
    annotation (Placement(transformation(origin = {80, -50}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m3_yaw_gain(k=-0.707) 
    annotation (Placement(transformation(origin = {80, -70}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum m3_thrust_roll_sum(inputs="++") 
    annotation (Placement(transformation(origin = {180, -38}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum m3_pitch_yaw_sum(inputs="++") 
    annotation (Placement(transformation(origin = {180, -62}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum m3_mix_sum(inputs="++") 
    annotation (Placement(transformation(origin = {260, -50}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation m3_limit(upLimit=20.0,lowLimit=-20.0) 
    annotation (Placement(transformation(origin = {360, -50}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m4_roll_gain(k=0.707) 
    annotation (Placement(transformation(origin = {80, -150}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m4_pitch_gain(k=0.707) 
    annotation (Placement(transformation(origin = {80, -170}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain m4_yaw_gain(k=0.707) 
    annotation (Placement(transformation(origin = {80, -190}, extent = {{-21, -15}, {21, 15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum m4_thrust_roll_sum(inputs="++") 
    annotation (Placement(transformation(origin = {180, -158}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum m4_pitch_yaw_sum(inputs="++") 
    annotation (Placement(transformation(origin = {180, -182}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum m4_mix_sum(inputs="++") 
    annotation (Placement(transformation(origin = {260, -170}, extent = {{-21, -15}, {21, 15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation m4_limit(upLimit=20.0,lowLimit=-20.0) 
    annotation (Placement(transformation(origin = {360, -170}, extent = {{-21, -15}, {21, 15}})));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(x_error, x_outer_ss.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_error, y_outer_ss.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_error, z_outer_ss.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_outer_ss.y, thrust_command_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_ref_rate, z_feedforward.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_feedforward.y, thrust_command_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_ref_limit.y, roll_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_mea, roll_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_ref_limit.y, pitch_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_mea, pitch_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_ref, yaw_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_mea, yaw_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_error.y, roll_inner_ss.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_error.y, pitch_inner_ss.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_error.y, yaw_inner_ss.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(x_outer_ss.y, pitch_ref_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_outer_ss.y, roll_ref_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(thrust_command_sum.y, thrust_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_inner_ss.y, roll_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_inner_ss.y, pitch_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_inner_ss.y, yaw_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(thrust_limit.y, m1_thrust_roll_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_limit.y, m1_roll_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m1_roll_gain.y, m1_thrust_roll_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_limit.y, m1_pitch_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m1_pitch_gain.y, m1_pitch_yaw_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_limit.y, m1_yaw_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m1_yaw_gain.y, m1_pitch_yaw_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m1_thrust_roll_sum.y, m1_mix_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m1_pitch_yaw_sum.y, m1_mix_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m1_mix_sum.y, m1_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(thrust_limit.y, m2_thrust_roll_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_limit.y, m2_roll_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m2_roll_gain.y, m2_thrust_roll_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_limit.y, m2_pitch_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m2_pitch_gain.y, m2_pitch_yaw_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_limit.y, m2_yaw_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m2_yaw_gain.y, m2_pitch_yaw_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m2_thrust_roll_sum.y, m2_mix_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m2_pitch_yaw_sum.y, m2_mix_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m2_mix_sum.y, m2_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(thrust_limit.y, m3_thrust_roll_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_limit.y, m3_roll_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m3_roll_gain.y, m3_thrust_roll_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_limit.y, m3_pitch_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m3_pitch_gain.y, m3_pitch_yaw_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_limit.y, m3_yaw_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m3_yaw_gain.y, m3_pitch_yaw_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m3_thrust_roll_sum.y, m3_mix_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m3_pitch_yaw_sum.y, m3_mix_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m3_mix_sum.y, m3_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(thrust_limit.y, m4_thrust_roll_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_limit.y, m4_roll_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m4_roll_gain.y, m4_thrust_roll_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_limit.y, m4_pitch_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m4_pitch_gain.y, m4_pitch_yaw_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_limit.y, m4_yaw_gain.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m4_yaw_gain.y, m4_pitch_yaw_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m4_thrust_roll_sum.y, m4_mix_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m4_pitch_yaw_sum.y, m4_mix_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m4_mix_sum.y, m4_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m1_limit.y, y) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m2_limit.y, y1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m3_limit.y, y2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(m4_limit.y, y3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));

end MoSim_OptimizedSSGraphicalController;