within MoSimQuadrotorModel.Control.Implementations.ClassicRobust;
model MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL "LQR outer-loop direct graphical core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, dt, enable), Right(position_error_x_out, position_error_y_out, position_error_z_out, velocity_error_x_out, velocity_error_y_out, velocity_error_z_out, desired_acceleration_x_out, desired_acceleration_y_out, desired_acceleration_z_out, desired_roll_rad_out, desired_pitch_rad_out, normalized_thrust_out, collective_thrust_n_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
  SysplorerEmbeddedCoder.Port.Inport position_x
    annotation (Placement(transformation(origin = {-650, 350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport position_y
    annotation (Placement(transformation(origin = {-650, 324}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport position_z
    annotation (Placement(transformation(origin = {-650, 298}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_x
    annotation (Placement(transformation(origin = {-650, 240}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_y
    annotation (Placement(transformation(origin = {-650, 214}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_z
    annotation (Placement(transformation(origin = {-650, 188}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x
    annotation (Placement(transformation(origin = {-650, 130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y
    annotation (Placement(transformation(origin = {-650, 104}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z
    annotation (Placement(transformation(origin = {-650, 78}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x
    annotation (Placement(transformation(origin = {-650, 20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y
    annotation (Placement(transformation(origin = {-650, -6}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z
    annotation (Placement(transformation(origin = {-650, -32}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x
    annotation (Placement(transformation(origin = {-650, -90}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y
    annotation (Placement(transformation(origin = {-650, -116}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z
    annotation (Placement(transformation(origin = {-650, -142}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport dt
    annotation (Placement(transformation(origin = {-650, -245}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport enable
    annotation (Placement(transformation(origin = {-650, -285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant disabled_command(k=0.0)
    annotation (Placement(transformation(origin = {510, -270}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_x(inputs="+-")
    annotation (Placement(transformation(origin = {-510, 297}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_x(inputs="+-")
    annotation (Placement(transformation(origin = {-510, 213}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_gain_x(k=1.6)
    annotation (Placement(transformation(origin = {-400, 297}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_gain_x(k=1.8)
    annotation (Placement(transformation(origin = {-400, 213}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pv_feedback_x(inputs="++")
    annotation (Placement(transformation(origin = {-300, 255}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_pre_gravity_x(inputs="++")
    annotation (Placement(transformation(origin = {35, 255}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_x(k=1.0)
    annotation (Placement(transformation(origin = {125, 255}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_y(inputs="+-")
    annotation (Placement(transformation(origin = {-510, 87}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_y(inputs="+-")
    annotation (Placement(transformation(origin = {-510, 3}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_gain_y(k=1.6)
    annotation (Placement(transformation(origin = {-400, 87}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_gain_y(k=1.8)
    annotation (Placement(transformation(origin = {-400, 3}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pv_feedback_y(inputs="++")
    annotation (Placement(transformation(origin = {-300, 45}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_pre_gravity_y(inputs="++")
    annotation (Placement(transformation(origin = {35, 45}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_y(k=1.0)
    annotation (Placement(transformation(origin = {125, 45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_z(inputs="+-")
    annotation (Placement(transformation(origin = {-510, -123}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_z(inputs="+-")
    annotation (Placement(transformation(origin = {-510, -207}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_gain_z(k=2.2)
    annotation (Placement(transformation(origin = {-400, -123}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_gain_z(k=2.0)
    annotation (Placement(transformation(origin = {-400, -207}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pv_feedback_z(inputs="++")
    annotation (Placement(transformation(origin = {-300, -165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_pre_gravity_z(inputs="++")
    annotation (Placement(transformation(origin = {35, -165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity_compensation(k=9.80665)
    annotation (Placement(transformation(origin = {35, -95}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_z(inputs="++")
    annotation (Placement(transformation(origin = {125, -165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_from_lateral_acceleration(k=-0.10197162129779283)
    annotation (Placement(transformation(origin = {240, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_tilt_limit(lowLimit=-0.5235987755982988,upLimit=0.5235987755982988)
    "Attitude adapter roll limit from lateral acceleration" annotation (Placement(transformation(origin = {325, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_from_lateral_acceleration(k=0.10197162129779283)
    annotation (Placement(transformation(origin = {240, 120}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_tilt_limit(lowLimit=-0.5235987755982988,upLimit=0.5235987755982988)
    "Attitude adapter pitch limit from lateral acceleration" annotation (Placement(transformation(origin = {325, 120}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain normalized_thrust_pre_limit(k=0.03772949988018335)
    annotation (Placement(transformation(origin = {240, -55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation normalized_thrust_limit(lowLimit=0.0,upLimit=1.0)
    "Normalized thrust saturation [0, 1]" annotation (Placement(transformation(origin = {325, -55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain collective_thrust_from_normalized(k=17.745945945945948)
    "Collective thrust allocation from normalized thrust" annotation (Placement(transformation(origin = {410, -55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_x(threshold=0.5)
    annotation (Placement(transformation(origin = {525, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_x_out
    annotation (Placement(transformation(origin = {675, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_y(threshold=0.5)
    annotation (Placement(transformation(origin = {525, 292}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_y_out
    annotation (Placement(transformation(origin = {675, 292}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_z(threshold=0.5)
    annotation (Placement(transformation(origin = {525, 254}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_z_out
    annotation (Placement(transformation(origin = {675, 254}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_x(threshold=0.5)
    annotation (Placement(transformation(origin = {525, 216}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_x_out
    annotation (Placement(transformation(origin = {675, 216}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_y(threshold=0.5)
    annotation (Placement(transformation(origin = {525, 178}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_y_out
    annotation (Placement(transformation(origin = {675, 178}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_z(threshold=0.5)
    annotation (Placement(transformation(origin = {525, 140}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_z_out
    annotation (Placement(transformation(origin = {675, 140}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_x(threshold=0.5)
    annotation (Placement(transformation(origin = {525, 102}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out
    annotation (Placement(transformation(origin = {675, 102}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_y(threshold=0.5)
    annotation (Placement(transformation(origin = {525, 64}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out
    annotation (Placement(transformation(origin = {675, 64}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_z(threshold=0.5)
    annotation (Placement(transformation(origin = {525, 26}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out
    annotation (Placement(transformation(origin = {675, 26}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_roll_rad(threshold=0.5)
    annotation (Placement(transformation(origin = {525, -12}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_roll_rad_out
    annotation (Placement(transformation(origin = {675, -12}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_pitch_rad(threshold=0.5)
    annotation (Placement(transformation(origin = {525, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_pitch_rad_out
    annotation (Placement(transformation(origin = {675, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_normalized_thrust(threshold=0.5)
    annotation (Placement(transformation(origin = {525, -88}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out
    annotation (Placement(transformation(origin = {675, -88}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_collective_thrust_n(threshold=0.5)
    annotation (Placement(transformation(origin = {525, -126}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n_out
    annotation (Placement(transformation(origin = {675, -126}, extent = {{-14, -11}, {14, 11}})));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(reference_position_x, position_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_x, position_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_x, velocity_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_x, velocity_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, position_gain_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, velocity_gain_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_gain_x.y, pv_feedback_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_gain_x.y, pv_feedback_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_x, desired_acceleration_pre_gravity_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pv_feedback_x.y, desired_acceleration_pre_gravity_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_pre_gravity_x.y, desired_acceleration_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_y, position_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_y, position_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_y, velocity_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_y, velocity_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, position_gain_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, velocity_gain_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_gain_y.y, pv_feedback_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_gain_y.y, pv_feedback_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_y, desired_acceleration_pre_gravity_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pv_feedback_y.y, desired_acceleration_pre_gravity_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_pre_gravity_y.y, desired_acceleration_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_z, position_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_z, position_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_z, velocity_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_z, velocity_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, position_gain_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, velocity_gain_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_gain_z.y, pv_feedback_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_gain_z.y, pv_feedback_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_z, desired_acceleration_pre_gravity_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pv_feedback_z.y, desired_acceleration_pre_gravity_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_pre_gravity_z.y, desired_acceleration_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gravity_compensation.y, desired_acceleration_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_y.y, roll_from_lateral_acceleration.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_from_lateral_acceleration.y, roll_tilt_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_x.y, pitch_from_lateral_acceleration.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_from_lateral_acceleration.y, pitch_tilt_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_z.y, normalized_thrust_pre_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(normalized_thrust_pre_limit.y, normalized_thrust_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(normalized_thrust_limit.y, collective_thrust_from_normalized.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, enable_position_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_position_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_position_error_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_position_error_x.y, position_error_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, enable_position_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_position_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_position_error_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_position_error_y.y, position_error_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, enable_position_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_position_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_position_error_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_position_error_z.y, position_error_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, enable_velocity_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_velocity_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_velocity_error_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_velocity_error_x.y, velocity_error_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, enable_velocity_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_velocity_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_velocity_error_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_velocity_error_y.y, velocity_error_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, enable_velocity_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_velocity_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_velocity_error_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_velocity_error_z.y, velocity_error_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_x.y, enable_desired_acceleration_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_acceleration_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_y.y, enable_desired_acceleration_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_acceleration_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_z.y, enable_desired_acceleration_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_acceleration_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_acceleration_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_acceleration_z.y, desired_acceleration_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_tilt_limit.y, enable_desired_roll_rad.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_roll_rad.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_roll_rad.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_roll_rad.y, desired_roll_rad_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_tilt_limit.y, enable_desired_pitch_rad.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_pitch_rad.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_pitch_rad.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_pitch_rad.y, desired_pitch_rad_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(normalized_thrust_limit.y, enable_normalized_thrust.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_normalized_thrust.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_normalized_thrust.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_normalized_thrust.y, normalized_thrust_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(collective_thrust_from_normalized.y, enable_collective_thrust_n.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_collective_thrust_n.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_collective_thrust_n.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_collective_thrust_n.y, collective_thrust_n_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));

end MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL;
