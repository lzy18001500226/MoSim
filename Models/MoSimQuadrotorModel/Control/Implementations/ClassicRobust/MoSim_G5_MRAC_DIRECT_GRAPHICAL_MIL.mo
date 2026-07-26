within MoSimQuadrotorModel.Control.Implementations.ClassicRobust;
model MoSim_G5_MRAC_DIRECT_GRAPHICAL_MIL "MRAC direct graphical core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, dt, enable), Right(reference_model_position_x_out, reference_model_velocity_x_out, adaptive_position_delta_x_out, adaptive_velocity_delta_x_out, sliding_surface_x_out, desired_acceleration_x_out, reference_model_position_y_out, reference_model_velocity_y_out, adaptive_position_delta_y_out, adaptive_velocity_delta_y_out, sliding_surface_y_out, desired_acceleration_y_out, reference_model_position_z_out, reference_model_velocity_z_out, adaptive_position_delta_z_out, adaptive_velocity_delta_z_out, sliding_surface_z_out, desired_acceleration_z_out, desired_roll_rad_out, desired_pitch_rad_out, collective_thrust_n_out, normalized_thrust_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
  SysplorerEmbeddedCoder.Port.Inport position_x
    annotation (Placement(transformation(origin = {-680, 350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport position_y
    annotation (Placement(transformation(origin = {-680, 324}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport position_z
    annotation (Placement(transformation(origin = {-680, 298}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_x
    annotation (Placement(transformation(origin = {-680, 238}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_y
    annotation (Placement(transformation(origin = {-680, 212}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_z
    annotation (Placement(transformation(origin = {-680, 186}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x
    annotation (Placement(transformation(origin = {-680, 126}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y
    annotation (Placement(transformation(origin = {-680, 100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z
    annotation (Placement(transformation(origin = {-680, 74}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x
    annotation (Placement(transformation(origin = {-680, 14}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y
    annotation (Placement(transformation(origin = {-680, -12}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z
    annotation (Placement(transformation(origin = {-680, -38}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x
    annotation (Placement(transformation(origin = {-680, -98}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y
    annotation (Placement(transformation(origin = {-680, -124}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z
    annotation (Placement(transformation(origin = {-680, -150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport dt
    annotation (Placement(transformation(origin = {-680, -245}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport enable
    annotation (Placement(transformation(origin = {-680, -285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant disabled_command(k=0.0)
    annotation (Placement(transformation(origin = {500, -310}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay reference_model_position_state_x(initCond=0.0)
    annotation (Placement(transformation(origin = {-430, 340}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay reference_model_velocity_state_x(initCond=0.0)
    annotation (Placement(transformation(origin = {-430, 300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay adaptive_position_delta_state_x(initCond=0.0)
    annotation (Placement(transformation(origin = {-160, 115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay adaptive_velocity_delta_state_x(initCond=0.0)
    annotation (Placement(transformation(origin = {-160, 73}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_position_error_x(inputs="+-")
    annotation (Placement(transformation(origin = {-555, 340}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_velocity_error_x(inputs="+-")
    annotation (Placement(transformation(origin = {-555, 300}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain reference_model_position_term_x(k=4.840000000000001)
    annotation (Placement(transformation(origin = {-330, 350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain reference_model_damping_term_x(k=-3.74)
    annotation (Placement(transformation(origin = {-330, 300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_acceleration_x_stage_2(inputs="++")
    annotation (Placement(transformation(origin = {-248, 325}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_acceleration_x(inputs="++")
    annotation (Placement(transformation(origin = {-180, 325}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product reference_model_position_increment_x(inputs="**")
    annotation (Placement(transformation(origin = {-70, 340}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_position_next_x(inputs="++")
    annotation (Placement(transformation(origin = {30, 340}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product reference_model_velocity_increment_x(inputs="**")
    annotation (Placement(transformation(origin = {-70, 300}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_velocity_next_x(inputs="++")
    annotation (Placement(transformation(origin = {30, 300}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_position_error_x(inputs="+-")
    annotation (Placement(transformation(origin = {-330, 240}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_velocity_error_x(inputs="+-")
    annotation (Placement(transformation(origin = {-330, 200}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_sliding_position_component_x(k=3.0)
    annotation (Placement(transformation(origin = {-205, 240}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_sliding_surface_x(inputs="++")
    annotation (Placement(transformation(origin = {-80, 220}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_position_adaptation_drive_x(inputs="**")
    annotation (Placement(transformation(origin = {-40, 115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_position_adaptation_dt_x(inputs="**")
    annotation (Placement(transformation(origin = {50, 115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_position_adaptation_gain_x(k=0.08)
    annotation (Placement(transformation(origin = {140, 115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_position_delta_pre_x(inputs="++")
    annotation (Placement(transformation(origin = {235, 115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation mrac_position_delta_limit_x(lowLimit=-1.5,upLimit=1.5)
    annotation (Placement(transformation(origin = {335, 115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_drive_x(inputs="**")
    annotation (Placement(transformation(origin = {-40, 73}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_dt_x(inputs="**")
    annotation (Placement(transformation(origin = {50, 73}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_velocity_adaptation_gain_x(k=0.08)
    annotation (Placement(transformation(origin = {140, 73}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_velocity_delta_pre_x(inputs="++")
    annotation (Placement(transformation(origin = {235, 73}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation mrac_velocity_delta_limit_x(lowLimit=-1.5,upLimit=1.5)
    annotation (Placement(transformation(origin = {335, 73}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant mrac_base_position_gain_x(k=6.0)
    annotation (Placement(transformation(origin = {20, 175}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant mrac_base_velocity_gain_x(k=4.5)
    annotation (Placement(transformation(origin = {20, 145}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_effective_position_gain_x(inputs="++")
    annotation (Placement(transformation(origin = {120, 175}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_effective_velocity_gain_x(inputs="++")
    annotation (Placement(transformation(origin = {120, 145}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_position_feedback_x(inputs="**")
    annotation (Placement(transformation(origin = {250, 175}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_feedback_x(inputs="**")
    annotation (Placement(transformation(origin = {250, 145}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_desired_acceleration_pre_gravity_x_stage_2(inputs="++")
    annotation (Placement(transformation(origin = {322, 165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_desired_acceleration_pre_gravity_x(inputs="++")
    annotation (Placement(transformation(origin = {390, 165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_x(k=1.0)
    annotation (Placement(transformation(origin = {140, 165}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay reference_model_position_state_y(initCond=0.0)
    annotation (Placement(transformation(origin = {-430, 115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay reference_model_velocity_state_y(initCond=0.0)
    annotation (Placement(transformation(origin = {-430, 75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay adaptive_position_delta_state_y(initCond=0.0)
    annotation (Placement(transformation(origin = {-160, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay adaptive_velocity_delta_state_y(initCond=0.0)
    annotation (Placement(transformation(origin = {-160, -152}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_position_error_y(inputs="+-")
    annotation (Placement(transformation(origin = {-555, 115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_velocity_error_y(inputs="+-")
    annotation (Placement(transformation(origin = {-555, 75}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain reference_model_position_term_y(k=4.840000000000001)
    annotation (Placement(transformation(origin = {-330, 125}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain reference_model_damping_term_y(k=-3.74)
    annotation (Placement(transformation(origin = {-330, 75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_acceleration_y_stage_2(inputs="++")
    annotation (Placement(transformation(origin = {-248, 100}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_acceleration_y(inputs="++")
    annotation (Placement(transformation(origin = {-180, 100}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product reference_model_position_increment_y(inputs="**")
    annotation (Placement(transformation(origin = {-70, 115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_position_next_y(inputs="++")
    annotation (Placement(transformation(origin = {30, 115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product reference_model_velocity_increment_y(inputs="**")
    annotation (Placement(transformation(origin = {-70, 75}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_velocity_next_y(inputs="++")
    annotation (Placement(transformation(origin = {30, 75}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_position_error_y(inputs="+-")
    annotation (Placement(transformation(origin = {-330, 15}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_velocity_error_y(inputs="+-")
    annotation (Placement(transformation(origin = {-330, -25}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_sliding_position_component_y(k=3.0)
    annotation (Placement(transformation(origin = {-205, 15}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_sliding_surface_y(inputs="++")
    annotation (Placement(transformation(origin = {-80, -5}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_position_adaptation_drive_y(inputs="**")
    annotation (Placement(transformation(origin = {-40, -110}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_position_adaptation_dt_y(inputs="**")
    annotation (Placement(transformation(origin = {50, -110}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_position_adaptation_gain_y(k=0.08)
    annotation (Placement(transformation(origin = {140, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_position_delta_pre_y(inputs="++")
    annotation (Placement(transformation(origin = {235, -110}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation mrac_position_delta_limit_y(lowLimit=-1.5,upLimit=1.5)
    annotation (Placement(transformation(origin = {335, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_drive_y(inputs="**")
    annotation (Placement(transformation(origin = {-40, -152}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_dt_y(inputs="**")
    annotation (Placement(transformation(origin = {50, -152}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_velocity_adaptation_gain_y(k=0.08)
    annotation (Placement(transformation(origin = {140, -152}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_velocity_delta_pre_y(inputs="++")
    annotation (Placement(transformation(origin = {235, -152}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation mrac_velocity_delta_limit_y(lowLimit=-1.5,upLimit=1.5)
    annotation (Placement(transformation(origin = {335, -152}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant mrac_base_position_gain_y(k=6.0)
    annotation (Placement(transformation(origin = {20, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant mrac_base_velocity_gain_y(k=4.5)
    annotation (Placement(transformation(origin = {20, -80}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_effective_position_gain_y(inputs="++")
    annotation (Placement(transformation(origin = {120, -50}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_effective_velocity_gain_y(inputs="++")
    annotation (Placement(transformation(origin = {120, -80}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_position_feedback_y(inputs="**")
    annotation (Placement(transformation(origin = {250, -50}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_feedback_y(inputs="**")
    annotation (Placement(transformation(origin = {250, -80}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_desired_acceleration_pre_gravity_y_stage_2(inputs="++")
    annotation (Placement(transformation(origin = {322, -60}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_desired_acceleration_pre_gravity_y(inputs="++")
    annotation (Placement(transformation(origin = {390, -60}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_y(k=1.0)
    annotation (Placement(transformation(origin = {140, -60}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay reference_model_position_state_z(initCond=0.0)
    annotation (Placement(transformation(origin = {-430, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay reference_model_velocity_state_z(initCond=0.0)
    annotation (Placement(transformation(origin = {-430, -150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay adaptive_position_delta_state_z(initCond=0.0)
    annotation (Placement(transformation(origin = {-160, -335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay adaptive_velocity_delta_state_z(initCond=0.0)
    annotation (Placement(transformation(origin = {-160, -377}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_position_error_z(inputs="+-")
    annotation (Placement(transformation(origin = {-555, -110}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_velocity_error_z(inputs="+-")
    annotation (Placement(transformation(origin = {-555, -150}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain reference_model_position_term_z(k=6.25)
    annotation (Placement(transformation(origin = {-330, -100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain reference_model_damping_term_z(k=-4.5)
    annotation (Placement(transformation(origin = {-330, -150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_acceleration_z_stage_2(inputs="++")
    annotation (Placement(transformation(origin = {-248, -125}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_acceleration_z(inputs="++")
    annotation (Placement(transformation(origin = {-180, -125}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product reference_model_position_increment_z(inputs="**")
    annotation (Placement(transformation(origin = {-70, -110}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_position_next_z(inputs="++")
    annotation (Placement(transformation(origin = {30, -110}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product reference_model_velocity_increment_z(inputs="**")
    annotation (Placement(transformation(origin = {-70, -150}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum reference_model_velocity_next_z(inputs="++")
    annotation (Placement(transformation(origin = {30, -150}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_position_error_z(inputs="+-")
    annotation (Placement(transformation(origin = {-330, -210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_velocity_error_z(inputs="+-")
    annotation (Placement(transformation(origin = {-330, -250}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_sliding_position_component_z(k=2.25)
    annotation (Placement(transformation(origin = {-205, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_sliding_surface_z(inputs="++")
    annotation (Placement(transformation(origin = {-80, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_position_adaptation_drive_z(inputs="**")
    annotation (Placement(transformation(origin = {-40, -335}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_position_adaptation_dt_z(inputs="**")
    annotation (Placement(transformation(origin = {50, -335}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_position_adaptation_gain_z(k=0.1)
    annotation (Placement(transformation(origin = {140, -335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_position_delta_pre_z(inputs="++")
    annotation (Placement(transformation(origin = {235, -335}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation mrac_position_delta_limit_z(lowLimit=-1.5,upLimit=1.5)
    annotation (Placement(transformation(origin = {335, -335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_drive_z(inputs="**")
    annotation (Placement(transformation(origin = {-40, -377}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_dt_z(inputs="**")
    annotation (Placement(transformation(origin = {50, -377}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_velocity_adaptation_gain_z(k=0.1)
    annotation (Placement(transformation(origin = {140, -377}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_velocity_delta_pre_z(inputs="++")
    annotation (Placement(transformation(origin = {235, -377}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation mrac_velocity_delta_limit_z(lowLimit=-1.5,upLimit=1.5)
    annotation (Placement(transformation(origin = {335, -377}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant mrac_base_position_gain_z(k=4.5)
    annotation (Placement(transformation(origin = {20, -275}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant mrac_base_velocity_gain_z(k=4.0)
    annotation (Placement(transformation(origin = {20, -305}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_effective_position_gain_z(inputs="++")
    annotation (Placement(transformation(origin = {120, -275}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_effective_velocity_gain_z(inputs="++")
    annotation (Placement(transformation(origin = {120, -305}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_position_feedback_z(inputs="**")
    annotation (Placement(transformation(origin = {250, -275}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_feedback_z(inputs="**")
    annotation (Placement(transformation(origin = {250, -305}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_desired_acceleration_pre_gravity_z_stage_2(inputs="++")
    annotation (Placement(transformation(origin = {322, -285}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_desired_acceleration_pre_gravity_z(inputs="++")
    annotation (Placement(transformation(origin = {390, -285}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity_compensation(k=9.80665)
    annotation (Placement(transformation(origin = {55, -213}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_z(inputs="++")
    annotation (Placement(transformation(origin = {140, -285}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_from_lateral_acceleration(k=-0.10197162129779283)
    annotation (Placement(transformation(origin = {230, 75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_tilt_limit(lowLimit=-0.5235987755982988,upLimit=0.5235987755982988)
    annotation (Placement(transformation(origin = {320, 75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_from_lateral_acceleration(k=0.10197162129779283)
    annotation (Placement(transformation(origin = {230, 130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_tilt_limit(lowLimit=-0.5235987755982988,upLimit=0.5235987755982988)
    annotation (Placement(transformation(origin = {320, 130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain vertical_force_allocation(k=1.0)
    annotation (Placement(transformation(origin = {230, -45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation collective_thrust_limit(lowLimit=0.0,upLimit=16.0)
    annotation (Placement(transformation(origin = {320, -45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain normalized_thrust_from_collective(k=0.04428916686217568)
    annotation (Placement(transformation(origin = {410, -45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation normalized_thrust_limit(lowLimit=0.0,upLimit=1.0)
    annotation (Placement(transformation(origin = {500, -45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_reference_model_position_x(threshold=0.5)
    annotation (Placement(transformation(origin = {535, 350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport reference_model_position_x_out
    annotation (Placement(transformation(origin = {695, 350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_reference_model_velocity_x(threshold=0.5)
    annotation (Placement(transformation(origin = {535, 312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport reference_model_velocity_x_out
    annotation (Placement(transformation(origin = {695, 312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_adaptive_position_delta_x(threshold=0.5)
    annotation (Placement(transformation(origin = {535, 274}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_position_delta_x_out
    annotation (Placement(transformation(origin = {695, 274}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_adaptive_velocity_delta_x(threshold=0.5)
    annotation (Placement(transformation(origin = {535, 236}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_velocity_delta_x_out
    annotation (Placement(transformation(origin = {695, 236}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_sliding_surface_x(threshold=0.5)
    annotation (Placement(transformation(origin = {535, 198}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_x_out
    annotation (Placement(transformation(origin = {695, 198}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_x(threshold=0.5)
    annotation (Placement(transformation(origin = {535, 160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out
    annotation (Placement(transformation(origin = {695, 160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_reference_model_position_y(threshold=0.5)
    annotation (Placement(transformation(origin = {535, 122}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport reference_model_position_y_out
    annotation (Placement(transformation(origin = {695, 122}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_reference_model_velocity_y(threshold=0.5)
    annotation (Placement(transformation(origin = {535, 84}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport reference_model_velocity_y_out
    annotation (Placement(transformation(origin = {695, 84}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_adaptive_position_delta_y(threshold=0.5)
    annotation (Placement(transformation(origin = {535, 46}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_position_delta_y_out
    annotation (Placement(transformation(origin = {695, 46}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_adaptive_velocity_delta_y(threshold=0.5)
    annotation (Placement(transformation(origin = {535, 8}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_velocity_delta_y_out
    annotation (Placement(transformation(origin = {695, 8}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_sliding_surface_y(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -30}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_y_out
    annotation (Placement(transformation(origin = {695, -30}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_y(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -68}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out
    annotation (Placement(transformation(origin = {695, -68}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_reference_model_position_z(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -106}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport reference_model_position_z_out
    annotation (Placement(transformation(origin = {695, -106}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_reference_model_velocity_z(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -144}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport reference_model_velocity_z_out
    annotation (Placement(transformation(origin = {695, -144}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_adaptive_position_delta_z(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -182}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_position_delta_z_out
    annotation (Placement(transformation(origin = {695, -182}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_adaptive_velocity_delta_z(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -220}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_velocity_delta_z_out
    annotation (Placement(transformation(origin = {695, -220}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_sliding_surface_z(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -258}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_z_out
    annotation (Placement(transformation(origin = {695, -258}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_z(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -296}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out
    annotation (Placement(transformation(origin = {695, -296}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_roll_rad(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -334}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_roll_rad_out
    annotation (Placement(transformation(origin = {695, -334}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_pitch_rad(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -372}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_pitch_rad_out
    annotation (Placement(transformation(origin = {695, -372}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_collective_thrust_n(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -410}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n_out
    annotation (Placement(transformation(origin = {695, -410}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_normalized_thrust(threshold=0.5)
    annotation (Placement(transformation(origin = {535, -448}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out
    annotation (Placement(transformation(origin = {695, -448}, extent = {{-14, -11}, {14, 11}})));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(reference_position_x, reference_model_position_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_x.y, reference_model_position_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_x.y, reference_model_velocity_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_x, reference_model_velocity_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_error_x.y, reference_model_position_term_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_error_x.y, reference_model_damping_term_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_x, reference_model_acceleration_x_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_term_x.y, reference_model_acceleration_x_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_acceleration_x_stage_2.y, reference_model_acceleration_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_damping_term_x.y, reference_model_acceleration_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_x.y, reference_model_position_increment_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, reference_model_position_increment_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_x.y, reference_model_position_next_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_increment_x.y, reference_model_position_next_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_next_x.y, reference_model_position_state_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_acceleration_x.y, reference_model_velocity_increment_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, reference_model_velocity_increment_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_x.y, reference_model_velocity_next_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_increment_x.y, reference_model_velocity_next_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_next_x.y, reference_model_velocity_state_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_x.y, mrac_position_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_x, mrac_position_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_x.y, mrac_velocity_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_x, mrac_velocity_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_error_x.y, mrac_sliding_position_component_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_error_x.y, mrac_sliding_surface_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_position_component_x.y, mrac_sliding_surface_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_surface_x.y, mrac_position_adaptation_drive_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_error_x.y, mrac_position_adaptation_drive_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_adaptation_drive_x.y, mrac_position_adaptation_dt_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, mrac_position_adaptation_dt_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_adaptation_dt_x.y, mrac_position_adaptation_gain_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_position_delta_state_x.y, mrac_position_delta_pre_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_adaptation_gain_x.y, mrac_position_delta_pre_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_delta_pre_x.y, mrac_position_delta_limit_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_delta_limit_x.y, adaptive_position_delta_state_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_surface_x.y, mrac_velocity_adaptation_drive_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_error_x.y, mrac_velocity_adaptation_drive_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_adaptation_drive_x.y, mrac_velocity_adaptation_dt_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, mrac_velocity_adaptation_dt_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_adaptation_dt_x.y, mrac_velocity_adaptation_gain_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_velocity_delta_state_x.y, mrac_velocity_delta_pre_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_adaptation_gain_x.y, mrac_velocity_delta_pre_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_delta_pre_x.y, mrac_velocity_delta_limit_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_delta_limit_x.y, adaptive_velocity_delta_state_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_base_position_gain_x.y, mrac_effective_position_gain_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_position_delta_state_x.y, mrac_effective_position_gain_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_base_velocity_gain_x.y, mrac_effective_velocity_gain_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_velocity_delta_state_x.y, mrac_effective_velocity_gain_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_effective_position_gain_x.y, mrac_position_feedback_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_error_x.y, mrac_position_feedback_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_effective_velocity_gain_x.y, mrac_velocity_feedback_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_error_x.y, mrac_velocity_feedback_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_acceleration_x.y, mrac_desired_acceleration_pre_gravity_x_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_feedback_x.y, mrac_desired_acceleration_pre_gravity_x_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_desired_acceleration_pre_gravity_x_stage_2.y, mrac_desired_acceleration_pre_gravity_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_feedback_x.y, mrac_desired_acceleration_pre_gravity_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_desired_acceleration_pre_gravity_x.y, desired_acceleration_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_y, reference_model_position_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_y.y, reference_model_position_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_y.y, reference_model_velocity_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_y, reference_model_velocity_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_error_y.y, reference_model_position_term_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_error_y.y, reference_model_damping_term_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_y, reference_model_acceleration_y_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_term_y.y, reference_model_acceleration_y_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_acceleration_y_stage_2.y, reference_model_acceleration_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_damping_term_y.y, reference_model_acceleration_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_y.y, reference_model_position_increment_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, reference_model_position_increment_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_y.y, reference_model_position_next_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_increment_y.y, reference_model_position_next_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_next_y.y, reference_model_position_state_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_acceleration_y.y, reference_model_velocity_increment_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, reference_model_velocity_increment_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_y.y, reference_model_velocity_next_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_increment_y.y, reference_model_velocity_next_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_next_y.y, reference_model_velocity_state_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_y.y, mrac_position_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_y, mrac_position_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_y.y, mrac_velocity_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_y, mrac_velocity_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_error_y.y, mrac_sliding_position_component_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_error_y.y, mrac_sliding_surface_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_position_component_y.y, mrac_sliding_surface_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_surface_y.y, mrac_position_adaptation_drive_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_error_y.y, mrac_position_adaptation_drive_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_adaptation_drive_y.y, mrac_position_adaptation_dt_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, mrac_position_adaptation_dt_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_adaptation_dt_y.y, mrac_position_adaptation_gain_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_position_delta_state_y.y, mrac_position_delta_pre_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_adaptation_gain_y.y, mrac_position_delta_pre_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_delta_pre_y.y, mrac_position_delta_limit_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_delta_limit_y.y, adaptive_position_delta_state_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_surface_y.y, mrac_velocity_adaptation_drive_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_error_y.y, mrac_velocity_adaptation_drive_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_adaptation_drive_y.y, mrac_velocity_adaptation_dt_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, mrac_velocity_adaptation_dt_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_adaptation_dt_y.y, mrac_velocity_adaptation_gain_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_velocity_delta_state_y.y, mrac_velocity_delta_pre_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_adaptation_gain_y.y, mrac_velocity_delta_pre_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_delta_pre_y.y, mrac_velocity_delta_limit_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_delta_limit_y.y, adaptive_velocity_delta_state_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_base_position_gain_y.y, mrac_effective_position_gain_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_position_delta_state_y.y, mrac_effective_position_gain_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_base_velocity_gain_y.y, mrac_effective_velocity_gain_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_velocity_delta_state_y.y, mrac_effective_velocity_gain_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_effective_position_gain_y.y, mrac_position_feedback_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_error_y.y, mrac_position_feedback_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_effective_velocity_gain_y.y, mrac_velocity_feedback_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_error_y.y, mrac_velocity_feedback_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_acceleration_y.y, mrac_desired_acceleration_pre_gravity_y_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_feedback_y.y, mrac_desired_acceleration_pre_gravity_y_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_desired_acceleration_pre_gravity_y_stage_2.y, mrac_desired_acceleration_pre_gravity_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_feedback_y.y, mrac_desired_acceleration_pre_gravity_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_desired_acceleration_pre_gravity_y.y, desired_acceleration_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_z, reference_model_position_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_z.y, reference_model_position_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_z.y, reference_model_velocity_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_z, reference_model_velocity_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_error_z.y, reference_model_position_term_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_error_z.y, reference_model_damping_term_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_z, reference_model_acceleration_z_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_term_z.y, reference_model_acceleration_z_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_acceleration_z_stage_2.y, reference_model_acceleration_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_damping_term_z.y, reference_model_acceleration_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_z.y, reference_model_position_increment_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, reference_model_position_increment_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_z.y, reference_model_position_next_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_increment_z.y, reference_model_position_next_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_next_z.y, reference_model_position_state_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_acceleration_z.y, reference_model_velocity_increment_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, reference_model_velocity_increment_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_z.y, reference_model_velocity_next_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_increment_z.y, reference_model_velocity_next_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_next_z.y, reference_model_velocity_state_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_z.y, mrac_position_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_z, mrac_position_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_z.y, mrac_velocity_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_z, mrac_velocity_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_error_z.y, mrac_sliding_position_component_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_error_z.y, mrac_sliding_surface_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_position_component_z.y, mrac_sliding_surface_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_surface_z.y, mrac_position_adaptation_drive_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_error_z.y, mrac_position_adaptation_drive_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_adaptation_drive_z.y, mrac_position_adaptation_dt_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, mrac_position_adaptation_dt_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_adaptation_dt_z.y, mrac_position_adaptation_gain_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_position_delta_state_z.y, mrac_position_delta_pre_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_adaptation_gain_z.y, mrac_position_delta_pre_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_delta_pre_z.y, mrac_position_delta_limit_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_delta_limit_z.y, adaptive_position_delta_state_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_surface_z.y, mrac_velocity_adaptation_drive_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_error_z.y, mrac_velocity_adaptation_drive_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_adaptation_drive_z.y, mrac_velocity_adaptation_dt_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(dt, mrac_velocity_adaptation_dt_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_adaptation_dt_z.y, mrac_velocity_adaptation_gain_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_velocity_delta_state_z.y, mrac_velocity_delta_pre_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_adaptation_gain_z.y, mrac_velocity_delta_pre_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_delta_pre_z.y, mrac_velocity_delta_limit_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_delta_limit_z.y, adaptive_velocity_delta_state_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_base_position_gain_z.y, mrac_effective_position_gain_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_position_delta_state_z.y, mrac_effective_position_gain_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_base_velocity_gain_z.y, mrac_effective_velocity_gain_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_velocity_delta_state_z.y, mrac_effective_velocity_gain_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_effective_position_gain_z.y, mrac_position_feedback_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_error_z.y, mrac_position_feedback_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_effective_velocity_gain_z.y, mrac_velocity_feedback_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_error_z.y, mrac_velocity_feedback_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_acceleration_z.y, mrac_desired_acceleration_pre_gravity_z_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_position_feedback_z.y, mrac_desired_acceleration_pre_gravity_z_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_desired_acceleration_pre_gravity_z_stage_2.y, mrac_desired_acceleration_pre_gravity_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_velocity_feedback_z.y, mrac_desired_acceleration_pre_gravity_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_desired_acceleration_pre_gravity_z.y, desired_acceleration_z.u1)
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
  connect(desired_acceleration_z.y, vertical_force_allocation.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(vertical_force_allocation.y, collective_thrust_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(collective_thrust_limit.y, normalized_thrust_from_collective.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(normalized_thrust_from_collective.y, normalized_thrust_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_x.y, enable_reference_model_position_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_reference_model_position_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_reference_model_position_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_reference_model_position_x.y, reference_model_position_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_x.y, enable_reference_model_velocity_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_reference_model_velocity_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_reference_model_velocity_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_reference_model_velocity_x.y, reference_model_velocity_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_position_delta_state_x.y, enable_adaptive_position_delta_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_adaptive_position_delta_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_adaptive_position_delta_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_adaptive_position_delta_x.y, adaptive_position_delta_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_velocity_delta_state_x.y, enable_adaptive_velocity_delta_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_adaptive_velocity_delta_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_adaptive_velocity_delta_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_adaptive_velocity_delta_x.y, adaptive_velocity_delta_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_surface_x.y, enable_sliding_surface_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_sliding_surface_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_sliding_surface_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_sliding_surface_x.y, sliding_surface_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_x.y, enable_desired_acceleration_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_acceleration_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_y.y, enable_reference_model_position_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_reference_model_position_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_reference_model_position_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_reference_model_position_y.y, reference_model_position_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_y.y, enable_reference_model_velocity_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_reference_model_velocity_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_reference_model_velocity_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_reference_model_velocity_y.y, reference_model_velocity_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_position_delta_state_y.y, enable_adaptive_position_delta_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_adaptive_position_delta_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_adaptive_position_delta_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_adaptive_position_delta_y.y, adaptive_position_delta_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_velocity_delta_state_y.y, enable_adaptive_velocity_delta_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_adaptive_velocity_delta_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_adaptive_velocity_delta_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_adaptive_velocity_delta_y.y, adaptive_velocity_delta_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_surface_y.y, enable_sliding_surface_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_sliding_surface_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_sliding_surface_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_sliding_surface_y.y, sliding_surface_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_y.y, enable_desired_acceleration_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_acceleration_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_position_state_z.y, enable_reference_model_position_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_reference_model_position_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_reference_model_position_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_reference_model_position_z.y, reference_model_position_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_model_velocity_state_z.y, enable_reference_model_velocity_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_reference_model_velocity_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_reference_model_velocity_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_reference_model_velocity_z.y, reference_model_velocity_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_position_delta_state_z.y, enable_adaptive_position_delta_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_adaptive_position_delta_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_adaptive_position_delta_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_adaptive_position_delta_z.y, adaptive_position_delta_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(adaptive_velocity_delta_state_z.y, enable_adaptive_velocity_delta_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_adaptive_velocity_delta_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_adaptive_velocity_delta_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_adaptive_velocity_delta_z.y, adaptive_velocity_delta_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mrac_sliding_surface_z.y, enable_sliding_surface_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_sliding_surface_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_sliding_surface_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_sliding_surface_z.y, sliding_surface_z_out)
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
  connect(collective_thrust_limit.y, enable_collective_thrust_n.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_collective_thrust_n.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_collective_thrust_n.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_collective_thrust_n.y, collective_thrust_n_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(normalized_thrust_limit.y, enable_normalized_thrust.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_normalized_thrust.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_normalized_thrust.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_normalized_thrust.y, normalized_thrust_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));

end MoSim_G5_MRAC_DIRECT_GRAPHICAL_MIL;
