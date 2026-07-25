within MoSimQuadrotorModel.Controllers.GraphicalMIL.ClassicRobust;
model MoSim_P2_LQG_GRAPHICAL_MIL "P2 fixed-input graphical controller core for lqg"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Right(desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, estimated_position_x, estimated_position_y, estimated_position_z, estimated_velocity_x, estimated_velocity_y, estimated_velocity_z, adaptive_disturbance_x, adaptive_disturbance_y, adaptive_disturbance_z, storage_function)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Sources.Constant position_x(k=0.2)
    annotation (Placement(transformation(origin = {-610, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant position_y(k=-0.1)
    annotation (Placement(transformation(origin = {-555, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant position_z(k=0.7)
    annotation (Placement(transformation(origin = {-500, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_x(k=-0.3)
    annotation (Placement(transformation(origin = {-610, 268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_y(k=0.2)
    annotation (Placement(transformation(origin = {-555, 268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_z(k=-0.1)
    annotation (Placement(transformation(origin = {-500, 268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_x(k=1.0)
    annotation (Placement(transformation(origin = {-610, 206}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_y(k=0.5)
    annotation (Placement(transformation(origin = {-555, 206}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_z(k=1.2)
    annotation (Placement(transformation(origin = {-500, 206}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_x(k=0.1)
    annotation (Placement(transformation(origin = {-610, 144}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_y(k=-0.2)
    annotation (Placement(transformation(origin = {-555, 144}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_z(k=0.0)
    annotation (Placement(transformation(origin = {-500, 144}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_x(k=0.05)
    annotation (Placement(transformation(origin = {-610, 82}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_y(k=-0.04)
    annotation (Placement(transformation(origin = {-555, 82}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_z(k=0.02)
    annotation (Placement(transformation(origin = {-500, 82}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant zero(k=0.0)
    annotation (Placement(transformation(origin = {430, 340}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay estimated_position_state_x(initCond=0.2)
    "LQG observer position state" annotation (Placement(transformation(origin = {-285, 300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay estimated_velocity_state_x(initCond=-0.3)
    annotation (Placement(transformation(origin = {-285, 160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_dt_x(k=0.01)
    annotation (Placement(transformation(origin = {-210, 335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum predicted_position_x(inputs="++")
    annotation (Placement(transformation(origin = {-130, 315}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_innovation_x(inputs="+-")
    annotation (Placement(transformation(origin = {-50, 340}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_correction_x(k=0.65)
    annotation (Placement(transformation(origin = {30, 340}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum next_position_x(inputs="++")
    annotation (Placement(transformation(origin = {110, 315}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum estimated_position_error_x(inputs="+-")
    annotation (Placement(transformation(origin = {-130, 250}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum estimated_velocity_error_x(inputs="+-")
    annotation (Placement(transformation(origin = {-130, 210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain lqg_position_feedback_x(k=1.6)
    annotation (Placement(transformation(origin = {-45, 250}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain lqg_velocity_feedback_x(k=1.8)
    annotation (Placement(transformation(origin = {-45, 210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum lqg_feedback_x(inputs="++")
    annotation (Placement(transformation(origin = {40, 230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum lqg_acceleration_without_gravity_x(inputs="++")
    annotation (Placement(transformation(origin = {125, 230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_dt_x(k=0.01)
    annotation (Placement(transformation(origin = {-210, 120}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum predicted_velocity_x(inputs="++")
    annotation (Placement(transformation(origin = {-130, 135}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_innovation_x(inputs="+-")
    annotation (Placement(transformation(origin = {-50, 115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_correction_x(k=0.45)
    annotation (Placement(transformation(origin = {30, 115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum next_velocity_x(inputs="++")
    annotation (Placement(transformation(origin = {110, 135}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay estimated_position_state_y(initCond=-0.1)
    annotation (Placement(transformation(origin = {-285, 70}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay estimated_velocity_state_y(initCond=0.2)
    annotation (Placement(transformation(origin = {-285, -70}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_dt_y(k=0.01)
    annotation (Placement(transformation(origin = {-210, 105}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum predicted_position_y(inputs="++")
    annotation (Placement(transformation(origin = {-130, 85}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_innovation_y(inputs="+-")
    annotation (Placement(transformation(origin = {-50, 110}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_correction_y(k=0.65)
    annotation (Placement(transformation(origin = {30, 110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum next_position_y(inputs="++")
    annotation (Placement(transformation(origin = {110, 85}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum estimated_position_error_y(inputs="+-")
    annotation (Placement(transformation(origin = {-130, 20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum estimated_velocity_error_y(inputs="+-")
    annotation (Placement(transformation(origin = {-130, -20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain lqg_position_feedback_y(k=1.6)
    annotation (Placement(transformation(origin = {-45, 20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain lqg_velocity_feedback_y(k=1.8)
    annotation (Placement(transformation(origin = {-45, -20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum lqg_feedback_y(inputs="++")
    annotation (Placement(transformation(origin = {40, 0}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum lqg_acceleration_without_gravity_y(inputs="++")
    annotation (Placement(transformation(origin = {125, 0}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_dt_y(k=0.01)
    annotation (Placement(transformation(origin = {-210, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum predicted_velocity_y(inputs="++")
    annotation (Placement(transformation(origin = {-130, -95}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_innovation_y(inputs="+-")
    annotation (Placement(transformation(origin = {-50, -115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_correction_y(k=0.45)
    annotation (Placement(transformation(origin = {30, -115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum next_velocity_y(inputs="++")
    annotation (Placement(transformation(origin = {110, -95}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay estimated_position_state_z(initCond=0.7)
    annotation (Placement(transformation(origin = {-285, -160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay estimated_velocity_state_z(initCond=-0.1)
    annotation (Placement(transformation(origin = {-285, -300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_dt_z(k=0.01)
    annotation (Placement(transformation(origin = {-210, -125}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum predicted_position_z(inputs="++")
    annotation (Placement(transformation(origin = {-130, -145}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_innovation_z(inputs="+-")
    annotation (Placement(transformation(origin = {-50, -120}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_correction_z(k=0.7)
    annotation (Placement(transformation(origin = {30, -120}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum next_position_z(inputs="++")
    annotation (Placement(transformation(origin = {110, -145}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum estimated_position_error_z(inputs="+-")
    annotation (Placement(transformation(origin = {-130, -210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum estimated_velocity_error_z(inputs="+-")
    annotation (Placement(transformation(origin = {-130, -250}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain lqg_position_feedback_z(k=2.2)
    annotation (Placement(transformation(origin = {-45, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain lqg_velocity_feedback_z(k=2.0)
    annotation (Placement(transformation(origin = {-45, -250}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum lqg_feedback_z(inputs="++")
    annotation (Placement(transformation(origin = {40, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum lqg_acceleration_without_gravity_z(inputs="++")
    annotation (Placement(transformation(origin = {125, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_dt_z(k=0.01)
    annotation (Placement(transformation(origin = {-210, -340}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum predicted_velocity_z(inputs="++")
    annotation (Placement(transformation(origin = {-130, -325}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_innovation_z(inputs="+-")
    annotation (Placement(transformation(origin = {-50, -345}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_correction_z(k=0.5)
    annotation (Placement(transformation(origin = {30, -345}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum next_velocity_z(inputs="++")
    annotation (Placement(transformation(origin = {110, -325}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity(k=9.80665)
    annotation (Placement(transformation(origin = {125, -175}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum lqg_gravity_compensation(inputs="++")
    annotation (Placement(transformation(origin = {210, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x
    annotation (Placement(transformation(origin = {520, 325}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y
    annotation (Placement(transformation(origin = {520, 277}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z
    annotation (Placement(transformation(origin = {520, 229}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_position_x
    annotation (Placement(transformation(origin = {520, 181}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_position_y
    annotation (Placement(transformation(origin = {520, 133}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_position_z
    annotation (Placement(transformation(origin = {520, 85}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_velocity_x
    annotation (Placement(transformation(origin = {520, 37}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_velocity_y
    annotation (Placement(transformation(origin = {520, -11}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_velocity_z
    annotation (Placement(transformation(origin = {520, -59}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_disturbance_x
    annotation (Placement(transformation(origin = {520, -107}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_disturbance_y
    annotation (Placement(transformation(origin = {520, -155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_disturbance_z
    annotation (Placement(transformation(origin = {520, -203}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport storage_function
    annotation (Placement(transformation(origin = {520, -251}, extent = {{-14, -11}, {14, 11}})));
equation
  connect(estimated_velocity_state_x.y, velocity_dt_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_state_x.y, predicted_position_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_dt_x.y, predicted_position_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_x.y, position_innovation_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_position_x.y, position_innovation_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_innovation_x.y, position_correction_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_position_x.y, next_position_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_correction_x.y, next_position_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(next_position_x.y, estimated_position_state_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_x.y, estimated_position_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_state_x.y, estimated_position_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_x.y, estimated_velocity_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_x.y, estimated_velocity_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_error_x.y, lqg_position_feedback_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_error_x.y, lqg_velocity_feedback_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_position_feedback_x.y, lqg_feedback_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_velocity_feedback_x.y, lqg_feedback_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_x.y, lqg_acceleration_without_gravity_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_feedback_x.y, lqg_acceleration_without_gravity_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_acceleration_without_gravity_x.y, command_dt_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_x.y, predicted_velocity_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_dt_x.y, predicted_velocity_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_x.y, velocity_innovation_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_velocity_x.y, velocity_innovation_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_innovation_x.y, velocity_correction_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_velocity_x.y, next_velocity_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_correction_x.y, next_velocity_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(next_velocity_x.y, estimated_velocity_state_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_y.y, velocity_dt_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_state_y.y, predicted_position_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_dt_y.y, predicted_position_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_y.y, position_innovation_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_position_y.y, position_innovation_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_innovation_y.y, position_correction_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_position_y.y, next_position_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_correction_y.y, next_position_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(next_position_y.y, estimated_position_state_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_y.y, estimated_position_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_state_y.y, estimated_position_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_y.y, estimated_velocity_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_y.y, estimated_velocity_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_error_y.y, lqg_position_feedback_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_error_y.y, lqg_velocity_feedback_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_position_feedback_y.y, lqg_feedback_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_velocity_feedback_y.y, lqg_feedback_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_y.y, lqg_acceleration_without_gravity_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_feedback_y.y, lqg_acceleration_without_gravity_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_acceleration_without_gravity_y.y, command_dt_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_y.y, predicted_velocity_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_dt_y.y, predicted_velocity_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_y.y, velocity_innovation_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_velocity_y.y, velocity_innovation_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_innovation_y.y, velocity_correction_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_velocity_y.y, next_velocity_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_correction_y.y, next_velocity_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(next_velocity_y.y, estimated_velocity_state_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_z.y, velocity_dt_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_state_z.y, predicted_position_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_dt_z.y, predicted_position_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_z.y, position_innovation_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_position_z.y, position_innovation_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_innovation_z.y, position_correction_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_position_z.y, next_position_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_correction_z.y, next_position_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(next_position_z.y, estimated_position_state_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_z.y, estimated_position_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_state_z.y, estimated_position_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_z.y, estimated_velocity_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_z.y, estimated_velocity_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_error_z.y, lqg_position_feedback_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_error_z.y, lqg_velocity_feedback_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_position_feedback_z.y, lqg_feedback_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_velocity_feedback_z.y, lqg_feedback_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_z.y, lqg_acceleration_without_gravity_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_feedback_z.y, lqg_acceleration_without_gravity_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_acceleration_without_gravity_z.y, command_dt_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_z.y, predicted_velocity_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(command_dt_z.y, predicted_velocity_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_z.y, velocity_innovation_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_velocity_z.y, velocity_innovation_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_innovation_z.y, velocity_correction_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(predicted_velocity_z.y, next_velocity_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_correction_z.y, next_velocity_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(next_velocity_z.y, estimated_velocity_state_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_acceleration_without_gravity_z.y, lqg_gravity_compensation.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gravity.y, lqg_gravity_compensation.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_acceleration_without_gravity_x.y, desired_acceleration_x)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_acceleration_without_gravity_y.y, desired_acceleration_y)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(lqg_gravity_compensation.y, desired_acceleration_z)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_state_x.y, estimated_position_x)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_state_y.y, estimated_position_y)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_position_state_z.y, estimated_position_z)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_x.y, estimated_velocity_x)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_y.y, estimated_velocity_y)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(estimated_velocity_state_z.y, estimated_velocity_z)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(zero.y, adaptive_disturbance_x)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(zero.y, adaptive_disturbance_y)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(zero.y, adaptive_disturbance_z)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(zero.y, storage_function)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  end MoSim_P2_LQG_GRAPHICAL_MIL;