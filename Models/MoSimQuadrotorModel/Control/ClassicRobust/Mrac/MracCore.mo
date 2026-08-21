within MoSimQuadrotorModel.Control.ClassicRobust.Mrac;
model MracCore "MRAC direct graphical core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, dt, enable), Right(reference_model_position_x_out, reference_model_velocity_x_out, adaptive_position_delta_x_out, adaptive_velocity_delta_x_out, sliding_surface_x_out, desired_acceleration_x_out, reference_model_position_y_out, reference_model_velocity_y_out, adaptive_position_delta_y_out, adaptive_velocity_delta_y_out, sliding_surface_y_out, desired_acceleration_y_out, reference_model_position_z_out, reference_model_velocity_z_out, adaptive_position_delta_z_out, adaptive_velocity_delta_z_out, sliding_surface_z_out, desired_acceleration_z_out, desired_roll_rad_out, desired_pitch_rad_out, collective_thrust_n_out, normalized_thrust_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
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
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_position_adaptation_gain_x(k=0.03) 
    annotation (Placement(transformation(origin = {140, 115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_position_delta_pre_x(inputs="++") 
    annotation (Placement(transformation(origin = {235, 115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation mrac_position_delta_limit_x(lowLimit=-1.5,upLimit=1.5) 
    annotation (Placement(transformation(origin = {335, 115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_drive_x(inputs="**") 
    annotation (Placement(transformation(origin = {-40, 73}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_dt_x(inputs="**") 
    annotation (Placement(transformation(origin = {50, 73}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_velocity_adaptation_gain_x(k=0.03) 
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
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_position_adaptation_gain_y(k=0.03) 
    annotation (Placement(transformation(origin = {140, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_position_delta_pre_y(inputs="++") 
    annotation (Placement(transformation(origin = {235, -110}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation mrac_position_delta_limit_y(lowLimit=-1.5,upLimit=1.5) 
    annotation (Placement(transformation(origin = {335, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_drive_y(inputs="**") 
    annotation (Placement(transformation(origin = {-40, -152}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_dt_y(inputs="**") 
    annotation (Placement(transformation(origin = {50, -152}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_velocity_adaptation_gain_y(k=0.03) 
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
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_position_adaptation_gain_z(k=0.04) 
    annotation (Placement(transformation(origin = {140, -335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mrac_position_delta_pre_z(inputs="++") 
    annotation (Placement(transformation(origin = {235, -335}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation mrac_position_delta_limit_z(lowLimit=-1.5,upLimit=1.5) 
    annotation (Placement(transformation(origin = {335, -335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_drive_z(inputs="**") 
    annotation (Placement(transformation(origin = {-40, -377}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mrac_velocity_adaptation_dt_z(inputs="**") 
    annotation (Placement(transformation(origin = {50, -377}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mrac_velocity_adaptation_gain_z(k=0.04) 
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
equation
  connect(reference_position_x, reference_model_position_error_x.u1) 
    annotation(Line(points = {{-680, 137}, {-680, 233}, {-555, 233}, {-555, 329}}, color = {0, 0, 127}));
  connect(reference_model_position_state_x.y, reference_model_position_error_x.u2) 
    annotation(Line(points = {{-444, 340}, {-541, 340}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_x.y, reference_model_velocity_error_x.u1) 
    annotation(Line(points = {{-444, 300}, {-541, 300}}, color = {0, 0, 127}));
  connect(reference_velocity_x, reference_model_velocity_error_x.u2) 
    annotation(Line(points = {{-680, 25}, {-680, 157}, {-555, 157}, {-555, 289}}, color = {0, 0, 127}));
  connect(reference_model_position_error_x.y, reference_model_position_term_x.u) 
    annotation(Line(points = {{-541, 340}, {-442.5, 340}, {-442.5, 350}, {-344, 350}}, color = {0, 0, 127}));
  connect(reference_model_velocity_error_x.y, reference_model_damping_term_x.u) 
    annotation(Line(points = {{-541, 300}, {-344, 300}}, color = {0, 0, 127}));
  connect(reference_acceleration_x, reference_model_acceleration_x_stage_2.u1) 
    annotation(Line(points = {{-666, -98}, {-464, -98}, {-464, 325}, {-262, 325}}, color = {0, 0, 127}));
  connect(reference_model_position_term_x.y, reference_model_acceleration_x_stage_2.u2) 
    annotation(Line(points = {{-316, 350}, {-289, 350}, {-289, 325}, {-262, 325}}, color = {0, 0, 127}));
  connect(reference_model_acceleration_x_stage_2.y, reference_model_acceleration_x.u1) 
    annotation(Line(points = {{-234, 325}, {-194, 325}}, color = {0, 0, 127}));
  connect(reference_model_damping_term_x.y, reference_model_acceleration_x.u2) 
    annotation(Line(points = {{-316, 300}, {-255, 300}, {-255, 325}, {-194, 325}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_x.y, reference_model_position_increment_x.u1) 
    annotation(Line(points = {{-416, 300}, {-250, 300}, {-250, 340}, {-84, 340}}, color = {0, 0, 127}));
  connect(dt, reference_model_position_increment_x.u2) 
    annotation(Line(points = {{-666, -245}, {-375, -245}, {-375, 340}, {-84, 340}}, color = {0, 0, 127}));
  connect(reference_model_position_state_x.y, reference_model_position_next_x.u1) 
    annotation(Line(points = {{-416, 340}, {16, 340}}, color = {0, 0, 127}));
  connect(reference_model_position_increment_x.y, reference_model_position_next_x.u2) 
    annotation(Line(points = {{-56, 340}, {16, 340}}, color = {0, 0, 127}));
  connect(reference_model_position_next_x.y, reference_model_position_state_x.u1) 
    annotation(Line(points = {{16, 340}, {-416, 340}}, color = {0, 0, 127}));
  connect(reference_model_acceleration_x.y, reference_model_velocity_increment_x.u1) 
    annotation(Line(points = {{-166, 325}, {-125, 325}, {-125, 300}, {-84, 300}}, color = {0, 0, 127}));
  connect(dt, reference_model_velocity_increment_x.u2) 
    annotation(Line(points = {{-666, -245}, {-375, -245}, {-375, 300}, {-84, 300}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_x.y, reference_model_velocity_next_x.u1) 
    annotation(Line(points = {{-416, 300}, {16, 300}}, color = {0, 0, 127}));
  connect(reference_model_velocity_increment_x.y, reference_model_velocity_next_x.u2) 
    annotation(Line(points = {{-56, 300}, {16, 300}}, color = {0, 0, 127}));
  connect(reference_model_velocity_next_x.y, reference_model_velocity_state_x.u1) 
    annotation(Line(points = {{16, 300}, {-416, 300}}, color = {0, 0, 127}));
  connect(reference_model_position_state_x.y, mrac_position_error_x.u1) 
    annotation(Line(points = {{-416, 340}, {-380, 340}, {-380, 240}, {-344, 240}}, color = {0, 0, 127}));
  connect(position_x, mrac_position_error_x.u2) 
    annotation(Line(points = {{-666, 350}, {-505, 350}, {-505, 240}, {-344, 240}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_x.y, mrac_velocity_error_x.u1) 
    annotation(Line(points = {{-416, 300}, {-380, 300}, {-380, 200}, {-344, 200}}, color = {0, 0, 127}));
  connect(velocity_x, mrac_velocity_error_x.u2) 
    annotation(Line(points = {{-666, 238}, {-505, 238}, {-505, 200}, {-344, 200}}, color = {0, 0, 127}));
  connect(mrac_position_error_x.y, mrac_sliding_position_component_x.u) 
    annotation(Line(points = {{-316, 240}, {-219, 240}}, color = {0, 0, 127}));
  connect(mrac_velocity_error_x.y, mrac_sliding_surface_x.u1) 
    annotation(Line(points = {{-316, 200}, {-205, 200}, {-205, 220}, {-94, 220}}, color = {0, 0, 127}));
  connect(mrac_sliding_position_component_x.y, mrac_sliding_surface_x.u2) 
    annotation(Line(points = {{-191, 240}, {-142.5, 240}, {-142.5, 220}, {-94, 220}}, color = {0, 0, 127}));
  connect(mrac_sliding_surface_x.y, mrac_position_adaptation_drive_x.u1) 
    annotation(Line(points = {{-80, 209}, {-80, 167.5}, {-40, 167.5}, {-40, 126}}, color = {0, 0, 127}));
  connect(mrac_position_error_x.y, mrac_position_adaptation_drive_x.u2) 
    annotation(Line(points = {{-316, 240}, {-185, 240}, {-185, 115}, {-54, 115}}, color = {0, 0, 127}));
  connect(mrac_position_adaptation_drive_x.y, mrac_position_adaptation_dt_x.u1) 
    annotation(Line(points = {{-26, 115}, {36, 115}}, color = {0, 0, 127}));
  connect(dt, mrac_position_adaptation_dt_x.u2) 
    annotation(Line(points = {{-666, -245}, {-315, -245}, {-315, 115}, {36, 115}}, color = {0, 0, 127}));
  connect(mrac_position_adaptation_dt_x.y, mrac_position_adaptation_gain_x.u) 
    annotation(Line(points = {{64, 115}, {126, 115}}, color = {0, 0, 127}));
  connect(adaptive_position_delta_state_x.y, mrac_position_delta_pre_x.u1) 
    annotation(Line(points = {{-146, 115}, {221, 115}}, color = {0, 0, 127}));
  connect(mrac_position_adaptation_gain_x.y, mrac_position_delta_pre_x.u2) 
    annotation(Line(points = {{154, 115}, {221, 115}}, color = {0, 0, 127}));
  connect(mrac_position_delta_pre_x.y, mrac_position_delta_limit_x.u) 
    annotation(Line(points = {{249, 115}, {321, 115}}, color = {0, 0, 127}));
  connect(mrac_position_delta_limit_x.y, adaptive_position_delta_state_x.u1) 
    annotation(Line(points = {{321, 115}, {-146, 115}}, color = {0, 0, 127}));
  connect(mrac_sliding_surface_x.y, mrac_velocity_adaptation_drive_x.u1) 
    annotation(Line(points = {{-80, 209}, {-80, 146.5}, {-40, 146.5}, {-40, 84}}, color = {0, 0, 127}));
  connect(mrac_velocity_error_x.y, mrac_velocity_adaptation_drive_x.u2) 
    annotation(Line(points = {{-316, 200}, {-185, 200}, {-185, 73}, {-54, 73}}, color = {0, 0, 127}));
  connect(mrac_velocity_adaptation_drive_x.y, mrac_velocity_adaptation_dt_x.u1) 
    annotation(Line(points = {{-26, 73}, {36, 73}}, color = {0, 0, 127}));
  connect(dt, mrac_velocity_adaptation_dt_x.u2) 
    annotation(Line(points = {{-666, -245}, {-315, -245}, {-315, 73}, {36, 73}}, color = {0, 0, 127}));
  connect(mrac_velocity_adaptation_dt_x.y, mrac_velocity_adaptation_gain_x.u) 
    annotation(Line(points = {{64, 73}, {126, 73}}, color = {0, 0, 127}));
  connect(adaptive_velocity_delta_state_x.y, mrac_velocity_delta_pre_x.u1) 
    annotation(Line(points = {{-146, 73}, {221, 73}}, color = {0, 0, 127}));
  connect(mrac_velocity_adaptation_gain_x.y, mrac_velocity_delta_pre_x.u2) 
    annotation(Line(points = {{154, 73}, {221, 73}}, color = {0, 0, 127}));
  connect(mrac_velocity_delta_pre_x.y, mrac_velocity_delta_limit_x.u) 
    annotation(Line(points = {{249, 73}, {321, 73}}, color = {0, 0, 127}));
  connect(mrac_velocity_delta_limit_x.y, adaptive_velocity_delta_state_x.u1) 
    annotation(Line(points = {{321, 73}, {-146, 73}}, color = {0, 0, 127}));
  connect(mrac_base_position_gain_x.y, mrac_effective_position_gain_x.u1) 
    annotation(Line(points = {{34, 175}, {106, 175}}, color = {0, 0, 127}));
  connect(adaptive_position_delta_state_x.y, mrac_effective_position_gain_x.u2) 
    annotation(Line(points = {{-146, 115}, {-20, 115}, {-20, 175}, {106, 175}}, color = {0, 0, 127}));
  connect(mrac_base_velocity_gain_x.y, mrac_effective_velocity_gain_x.u1) 
    annotation(Line(points = {{34, 145}, {106, 145}}, color = {0, 0, 127}));
  connect(adaptive_velocity_delta_state_x.y, mrac_effective_velocity_gain_x.u2) 
    annotation(Line(points = {{-146, 73}, {-20, 73}, {-20, 145}, {106, 145}}, color = {0, 0, 127}));
  connect(mrac_effective_position_gain_x.y, mrac_position_feedback_x.u1) 
    annotation(Line(points = {{134, 175}, {236, 175}}, color = {0, 0, 127}));
  connect(mrac_position_error_x.y, mrac_position_feedback_x.u2) 
    annotation(Line(points = {{-316, 240}, {-40, 240}, {-40, 175}, {236, 175}}, color = {0, 0, 127}));
  connect(mrac_effective_velocity_gain_x.y, mrac_velocity_feedback_x.u1) 
    annotation(Line(points = {{134, 145}, {236, 145}}, color = {0, 0, 127}));
  connect(mrac_velocity_error_x.y, mrac_velocity_feedback_x.u2) 
    annotation(Line(points = {{-316, 200}, {-40, 200}, {-40, 145}, {236, 145}}, color = {0, 0, 127}));
  connect(reference_model_acceleration_x.y, mrac_desired_acceleration_pre_gravity_x_stage_2.u1) 
    annotation(Line(points = {{-166, 325}, {71, 325}, {71, 165}, {308, 165}}, color = {0, 0, 127}));
  connect(mrac_position_feedback_x.y, mrac_desired_acceleration_pre_gravity_x_stage_2.u2) 
    annotation(Line(points = {{264, 175}, {286, 175}, {286, 165}, {308, 165}}, color = {0, 0, 127}));
  connect(mrac_desired_acceleration_pre_gravity_x_stage_2.y, mrac_desired_acceleration_pre_gravity_x.u1) 
    annotation(Line(points = {{336, 165}, {376, 165}}, color = {0, 0, 127}));
  connect(mrac_velocity_feedback_x.y, mrac_desired_acceleration_pre_gravity_x.u2) 
    annotation(Line(points = {{264, 145}, {320, 145}, {320, 165}, {376, 165}}, color = {0, 0, 127}));
  connect(mrac_desired_acceleration_pre_gravity_x.y, desired_acceleration_x.u) 
    annotation(Line(points = {{376, 165}, {154, 165}}, color = {0, 0, 127}));
  connect(reference_position_y, reference_model_position_error_y.u1) 
    annotation(Line(points = {{-666, 100}, {-617.5, 100}, {-617.5, 115}, {-569, 115}}, color = {0, 0, 127}));
  connect(reference_model_position_state_y.y, reference_model_position_error_y.u2) 
    annotation(Line(points = {{-444, 115}, {-541, 115}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_y.y, reference_model_velocity_error_y.u1) 
    annotation(Line(points = {{-444, 75}, {-541, 75}}, color = {0, 0, 127}));
  connect(reference_velocity_y, reference_model_velocity_error_y.u2) 
    annotation(Line(points = {{-666, -12}, {-617.5, -12}, {-617.5, 75}, {-569, 75}}, color = {0, 0, 127}));
  connect(reference_model_position_error_y.y, reference_model_position_term_y.u) 
    annotation(Line(points = {{-541, 115}, {-442.5, 115}, {-442.5, 125}, {-344, 125}}, color = {0, 0, 127}));
  connect(reference_model_velocity_error_y.y, reference_model_damping_term_y.u) 
    annotation(Line(points = {{-541, 75}, {-344, 75}}, color = {0, 0, 127}));
  connect(reference_acceleration_y, reference_model_acceleration_y_stage_2.u1) 
    annotation(Line(points = {{-666, -124}, {-464, -124}, {-464, 100}, {-262, 100}}, color = {0, 0, 127}));
  connect(reference_model_position_term_y.y, reference_model_acceleration_y_stage_2.u2) 
    annotation(Line(points = {{-316, 125}, {-289, 125}, {-289, 100}, {-262, 100}}, color = {0, 0, 127}));
  connect(reference_model_acceleration_y_stage_2.y, reference_model_acceleration_y.u1) 
    annotation(Line(points = {{-234, 100}, {-194, 100}}, color = {0, 0, 127}));
  connect(reference_model_damping_term_y.y, reference_model_acceleration_y.u2) 
    annotation(Line(points = {{-316, 75}, {-255, 75}, {-255, 100}, {-194, 100}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_y.y, reference_model_position_increment_y.u1) 
    annotation(Line(points = {{-416, 75}, {-250, 75}, {-250, 115}, {-84, 115}}, color = {0, 0, 127}));
  connect(dt, reference_model_position_increment_y.u2) 
    annotation(Line(points = {{-666, -245}, {-375, -245}, {-375, 115}, {-84, 115}}, color = {0, 0, 127}));
  connect(reference_model_position_state_y.y, reference_model_position_next_y.u1) 
    annotation(Line(points = {{-416, 115}, {16, 115}}, color = {0, 0, 127}));
  connect(reference_model_position_increment_y.y, reference_model_position_next_y.u2) 
    annotation(Line(points = {{-56, 115}, {16, 115}}, color = {0, 0, 127}));
  connect(reference_model_position_next_y.y, reference_model_position_state_y.u1) 
    annotation(Line(points = {{16, 115}, {-416, 115}}, color = {0, 0, 127}));
  connect(reference_model_acceleration_y.y, reference_model_velocity_increment_y.u1) 
    annotation(Line(points = {{-166, 100}, {-125, 100}, {-125, 75}, {-84, 75}}, color = {0, 0, 127}));
  connect(dt, reference_model_velocity_increment_y.u2) 
    annotation(Line(points = {{-666, -245}, {-375, -245}, {-375, 75}, {-84, 75}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_y.y, reference_model_velocity_next_y.u1) 
    annotation(Line(points = {{-416, 75}, {16, 75}}, color = {0, 0, 127}));
  connect(reference_model_velocity_increment_y.y, reference_model_velocity_next_y.u2) 
    annotation(Line(points = {{-56, 75}, {16, 75}}, color = {0, 0, 127}));
  connect(reference_model_velocity_next_y.y, reference_model_velocity_state_y.u1) 
    annotation(Line(points = {{16, 75}, {-416, 75}}, color = {0, 0, 127}));
  connect(reference_model_position_state_y.y, mrac_position_error_y.u1) 
    annotation(Line(points = {{-416, 115}, {-380, 115}, {-380, 15}, {-344, 15}}, color = {0, 0, 127}));
  connect(position_y, mrac_position_error_y.u2) 
    annotation(Line(points = {{-666, 324}, {-505, 324}, {-505, 15}, {-344, 15}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_y.y, mrac_velocity_error_y.u1) 
    annotation(Line(points = {{-416, 75}, {-380, 75}, {-380, -25}, {-344, -25}}, color = {0, 0, 127}));
  connect(velocity_y, mrac_velocity_error_y.u2) 
    annotation(Line(points = {{-666, 212}, {-505, 212}, {-505, -25}, {-344, -25}}, color = {0, 0, 127}));
  connect(mrac_position_error_y.y, mrac_sliding_position_component_y.u) 
    annotation(Line(points = {{-316, 15}, {-219, 15}}, color = {0, 0, 127}));
  connect(mrac_velocity_error_y.y, mrac_sliding_surface_y.u1) 
    annotation(Line(points = {{-316, -25}, {-205, -25}, {-205, -5}, {-94, -5}}, color = {0, 0, 127}));
  connect(mrac_sliding_position_component_y.y, mrac_sliding_surface_y.u2) 
    annotation(Line(points = {{-191, 15}, {-142.5, 15}, {-142.5, -5}, {-94, -5}}, color = {0, 0, 127}));
  connect(mrac_sliding_surface_y.y, mrac_position_adaptation_drive_y.u1) 
    annotation(Line(points = {{-80, -16}, {-80, -57.5}, {-40, -57.5}, {-40, -99}}, color = {0, 0, 127}));
  connect(mrac_position_error_y.y, mrac_position_adaptation_drive_y.u2) 
    annotation(Line(points = {{-316, 15}, {-185, 15}, {-185, -110}, {-54, -110}}, color = {0, 0, 127}));
  connect(mrac_position_adaptation_drive_y.y, mrac_position_adaptation_dt_y.u1) 
    annotation(Line(points = {{-26, -110}, {36, -110}}, color = {0, 0, 127}));
  connect(dt, mrac_position_adaptation_dt_y.u2) 
    annotation(Line(points = {{-666, -245}, {-315, -245}, {-315, -110}, {36, -110}}, color = {0, 0, 127}));
  connect(mrac_position_adaptation_dt_y.y, mrac_position_adaptation_gain_y.u) 
    annotation(Line(points = {{64, -110}, {126, -110}}, color = {0, 0, 127}));
  connect(adaptive_position_delta_state_y.y, mrac_position_delta_pre_y.u1) 
    annotation(Line(points = {{-146, -110}, {221, -110}}, color = {0, 0, 127}));
  connect(mrac_position_adaptation_gain_y.y, mrac_position_delta_pre_y.u2) 
    annotation(Line(points = {{154, -110}, {221, -110}}, color = {0, 0, 127}));
  connect(mrac_position_delta_pre_y.y, mrac_position_delta_limit_y.u) 
    annotation(Line(points = {{249, -110}, {321, -110}}, color = {0, 0, 127}));
  connect(mrac_position_delta_limit_y.y, adaptive_position_delta_state_y.u1) 
    annotation(Line(points = {{321, -110}, {-146, -110}}, color = {0, 0, 127}));
  connect(mrac_sliding_surface_y.y, mrac_velocity_adaptation_drive_y.u1) 
    annotation(Line(points = {{-80, -16}, {-80, -78.5}, {-40, -78.5}, {-40, -141}}, color = {0, 0, 127}));
  connect(mrac_velocity_error_y.y, mrac_velocity_adaptation_drive_y.u2) 
    annotation(Line(points = {{-316, -25}, {-185, -25}, {-185, -152}, {-54, -152}}, color = {0, 0, 127}));
  connect(mrac_velocity_adaptation_drive_y.y, mrac_velocity_adaptation_dt_y.u1) 
    annotation(Line(points = {{-26, -152}, {36, -152}}, color = {0, 0, 127}));
  connect(dt, mrac_velocity_adaptation_dt_y.u2) 
    annotation(Line(points = {{-666, -245}, {-315, -245}, {-315, -152}, {36, -152}}, color = {0, 0, 127}));
  connect(mrac_velocity_adaptation_dt_y.y, mrac_velocity_adaptation_gain_y.u) 
    annotation(Line(points = {{64, -152}, {126, -152}}, color = {0, 0, 127}));
  connect(adaptive_velocity_delta_state_y.y, mrac_velocity_delta_pre_y.u1) 
    annotation(Line(points = {{-146, -152}, {221, -152}}, color = {0, 0, 127}));
  connect(mrac_velocity_adaptation_gain_y.y, mrac_velocity_delta_pre_y.u2) 
    annotation(Line(points = {{154, -152}, {221, -152}}, color = {0, 0, 127}));
  connect(mrac_velocity_delta_pre_y.y, mrac_velocity_delta_limit_y.u) 
    annotation(Line(points = {{249, -152}, {321, -152}}, color = {0, 0, 127}));
  connect(mrac_velocity_delta_limit_y.y, adaptive_velocity_delta_state_y.u1) 
    annotation(Line(points = {{321, -152}, {-146, -152}}, color = {0, 0, 127}));
  connect(mrac_base_position_gain_y.y, mrac_effective_position_gain_y.u1) 
    annotation(Line(points = {{34, -50}, {106, -50}}, color = {0, 0, 127}));
  connect(adaptive_position_delta_state_y.y, mrac_effective_position_gain_y.u2) 
    annotation(Line(points = {{-146, -110}, {-20, -110}, {-20, -50}, {106, -50}}, color = {0, 0, 127}));
  connect(mrac_base_velocity_gain_y.y, mrac_effective_velocity_gain_y.u1) 
    annotation(Line(points = {{34, -80}, {106, -80}}, color = {0, 0, 127}));
  connect(adaptive_velocity_delta_state_y.y, mrac_effective_velocity_gain_y.u2) 
    annotation(Line(points = {{-146, -152}, {-20, -152}, {-20, -80}, {106, -80}}, color = {0, 0, 127}));
  connect(mrac_effective_position_gain_y.y, mrac_position_feedback_y.u1) 
    annotation(Line(points = {{134, -50}, {236, -50}}, color = {0, 0, 127}));
  connect(mrac_position_error_y.y, mrac_position_feedback_y.u2) 
    annotation(Line(points = {{-316, 15}, {-40, 15}, {-40, -50}, {236, -50}}, color = {0, 0, 127}));
  connect(mrac_effective_velocity_gain_y.y, mrac_velocity_feedback_y.u1) 
    annotation(Line(points = {{134, -80}, {236, -80}}, color = {0, 0, 127}));
  connect(mrac_velocity_error_y.y, mrac_velocity_feedback_y.u2) 
    annotation(Line(points = {{-316, -25}, {-40, -25}, {-40, -80}, {236, -80}}, color = {0, 0, 127}));
  connect(reference_model_acceleration_y.y, mrac_desired_acceleration_pre_gravity_y_stage_2.u1) 
    annotation(Line(points = {{-166, 100}, {71, 100}, {71, -60}, {308, -60}}, color = {0, 0, 127}));
  connect(mrac_position_feedback_y.y, mrac_desired_acceleration_pre_gravity_y_stage_2.u2) 
    annotation(Line(points = {{264, -50}, {286, -50}, {286, -60}, {308, -60}}, color = {0, 0, 127}));
  connect(mrac_desired_acceleration_pre_gravity_y_stage_2.y, mrac_desired_acceleration_pre_gravity_y.u1) 
    annotation(Line(points = {{336, -60}, {376, -60}}, color = {0, 0, 127}));
  connect(mrac_velocity_feedback_y.y, mrac_desired_acceleration_pre_gravity_y.u2) 
    annotation(Line(points = {{264, -80}, {320, -80}, {320, -60}, {376, -60}}, color = {0, 0, 127}));
  connect(mrac_desired_acceleration_pre_gravity_y.y, desired_acceleration_y.u) 
    annotation(Line(points = {{376, -60}, {154, -60}}, color = {0, 0, 127}));
  connect(reference_position_z, reference_model_position_error_z.u1) 
    annotation(Line(points = {{-680, 63}, {-680, -18}, {-555, -18}, {-555, -99}}, color = {0, 0, 127}));
  connect(reference_model_position_state_z.y, reference_model_position_error_z.u2) 
    annotation(Line(points = {{-444, -110}, {-541, -110}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_z.y, reference_model_velocity_error_z.u1) 
    annotation(Line(points = {{-444, -150}, {-541, -150}}, color = {0, 0, 127}));
  connect(reference_velocity_z, reference_model_velocity_error_z.u2) 
    annotation(Line(points = {{-666, -38}, {-617.5, -38}, {-617.5, -150}, {-569, -150}}, color = {0, 0, 127}));
  connect(reference_model_position_error_z.y, reference_model_position_term_z.u) 
    annotation(Line(points = {{-541, -110}, {-442.5, -110}, {-442.5, -100}, {-344, -100}}, color = {0, 0, 127}));
  connect(reference_model_velocity_error_z.y, reference_model_damping_term_z.u) 
    annotation(Line(points = {{-541, -150}, {-344, -150}}, color = {0, 0, 127}));
  connect(reference_acceleration_z, reference_model_acceleration_z_stage_2.u1) 
    annotation(Line(points = {{-666, -150}, {-464, -150}, {-464, -125}, {-262, -125}}, color = {0, 0, 127}));
  connect(reference_model_position_term_z.y, reference_model_acceleration_z_stage_2.u2) 
    annotation(Line(points = {{-316, -100}, {-289, -100}, {-289, -125}, {-262, -125}}, color = {0, 0, 127}));
  connect(reference_model_acceleration_z_stage_2.y, reference_model_acceleration_z.u1) 
    annotation(Line(points = {{-234, -125}, {-194, -125}}, color = {0, 0, 127}));
  connect(reference_model_damping_term_z.y, reference_model_acceleration_z.u2) 
    annotation(Line(points = {{-316, -150}, {-255, -150}, {-255, -125}, {-194, -125}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_z.y, reference_model_position_increment_z.u1) 
    annotation(Line(points = {{-416, -150}, {-250, -150}, {-250, -110}, {-84, -110}}, color = {0, 0, 127}));
  connect(dt, reference_model_position_increment_z.u2) 
    annotation(Line(points = {{-666, -245}, {-375, -245}, {-375, -110}, {-84, -110}}, color = {0, 0, 127}));
  connect(reference_model_position_state_z.y, reference_model_position_next_z.u1) 
    annotation(Line(points = {{-416, -110}, {16, -110}}, color = {0, 0, 127}));
  connect(reference_model_position_increment_z.y, reference_model_position_next_z.u2) 
    annotation(Line(points = {{-56, -110}, {16, -110}}, color = {0, 0, 127}));
  connect(reference_model_position_next_z.y, reference_model_position_state_z.u1) 
    annotation(Line(points = {{16, -110}, {-416, -110}}, color = {0, 0, 127}));
  connect(reference_model_acceleration_z.y, reference_model_velocity_increment_z.u1) 
    annotation(Line(points = {{-166, -125}, {-125, -125}, {-125, -150}, {-84, -150}}, color = {0, 0, 127}));
  connect(dt, reference_model_velocity_increment_z.u2) 
    annotation(Line(points = {{-666, -245}, {-375, -245}, {-375, -150}, {-84, -150}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_z.y, reference_model_velocity_next_z.u1) 
    annotation(Line(points = {{-416, -150}, {16, -150}}, color = {0, 0, 127}));
  connect(reference_model_velocity_increment_z.y, reference_model_velocity_next_z.u2) 
    annotation(Line(points = {{-56, -150}, {16, -150}}, color = {0, 0, 127}));
  connect(reference_model_velocity_next_z.y, reference_model_velocity_state_z.u1) 
    annotation(Line(points = {{16, -150}, {-416, -150}}, color = {0, 0, 127}));
  connect(reference_model_position_state_z.y, mrac_position_error_z.u1) 
    annotation(Line(points = {{-416, -110}, {-380, -110}, {-380, -210}, {-344, -210}}, color = {0, 0, 127}));
  connect(position_z, mrac_position_error_z.u2) 
    annotation(Line(points = {{-680, 287}, {-680, 44}, {-330, 44}, {-330, -199}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_z.y, mrac_velocity_error_z.u1) 
    annotation(Line(points = {{-416, -150}, {-380, -150}, {-380, -250}, {-344, -250}}, color = {0, 0, 127}));
  connect(velocity_z, mrac_velocity_error_z.u2) 
    annotation(Line(points = {{-680, 175}, {-680, -32}, {-330, -32}, {-330, -239}}, color = {0, 0, 127}));
  connect(mrac_position_error_z.y, mrac_sliding_position_component_z.u) 
    annotation(Line(points = {{-316, -210}, {-219, -210}}, color = {0, 0, 127}));
  connect(mrac_velocity_error_z.y, mrac_sliding_surface_z.u1) 
    annotation(Line(points = {{-316, -250}, {-205, -250}, {-205, -230}, {-94, -230}}, color = {0, 0, 127}));
  connect(mrac_sliding_position_component_z.y, mrac_sliding_surface_z.u2) 
    annotation(Line(points = {{-191, -210}, {-142.5, -210}, {-142.5, -230}, {-94, -230}}, color = {0, 0, 127}));
  connect(mrac_sliding_surface_z.y, mrac_position_adaptation_drive_z.u1) 
    annotation(Line(points = {{-80, -241}, {-80, -282.5}, {-40, -282.5}, {-40, -324}}, color = {0, 0, 127}));
  connect(mrac_position_error_z.y, mrac_position_adaptation_drive_z.u2) 
    annotation(Line(points = {{-316, -210}, {-185, -210}, {-185, -335}, {-54, -335}}, color = {0, 0, 127}));
  connect(mrac_position_adaptation_drive_z.y, mrac_position_adaptation_dt_z.u1) 
    annotation(Line(points = {{-26, -335}, {36, -335}}, color = {0, 0, 127}));
  connect(dt, mrac_position_adaptation_dt_z.u2) 
    annotation(Line(points = {{-666, -245}, {-315, -245}, {-315, -335}, {36, -335}}, color = {0, 0, 127}));
  connect(mrac_position_adaptation_dt_z.y, mrac_position_adaptation_gain_z.u) 
    annotation(Line(points = {{64, -335}, {126, -335}}, color = {0, 0, 127}));
  connect(adaptive_position_delta_state_z.y, mrac_position_delta_pre_z.u1) 
    annotation(Line(points = {{-146, -335}, {221, -335}}, color = {0, 0, 127}));
  connect(mrac_position_adaptation_gain_z.y, mrac_position_delta_pre_z.u2) 
    annotation(Line(points = {{154, -335}, {221, -335}}, color = {0, 0, 127}));
  connect(mrac_position_delta_pre_z.y, mrac_position_delta_limit_z.u) 
    annotation(Line(points = {{249, -335}, {321, -335}}, color = {0, 0, 127}));
  connect(mrac_position_delta_limit_z.y, adaptive_position_delta_state_z.u1) 
    annotation(Line(points = {{321, -335}, {-146, -335}}, color = {0, 0, 127}));
  connect(mrac_sliding_surface_z.y, mrac_velocity_adaptation_drive_z.u1) 
    annotation(Line(points = {{-80, -241}, {-80, -303.5}, {-40, -303.5}, {-40, -366}}, color = {0, 0, 127}));
  connect(mrac_velocity_error_z.y, mrac_velocity_adaptation_drive_z.u2) 
    annotation(Line(points = {{-316, -250}, {-185, -250}, {-185, -377}, {-54, -377}}, color = {0, 0, 127}));
  connect(mrac_velocity_adaptation_drive_z.y, mrac_velocity_adaptation_dt_z.u1) 
    annotation(Line(points = {{-26, -377}, {36, -377}}, color = {0, 0, 127}));
  connect(dt, mrac_velocity_adaptation_dt_z.u2) 
    annotation(Line(points = {{-666, -245}, {-315, -245}, {-315, -377}, {36, -377}}, color = {0, 0, 127}));
  connect(mrac_velocity_adaptation_dt_z.y, mrac_velocity_adaptation_gain_z.u) 
    annotation(Line(points = {{64, -377}, {126, -377}}, color = {0, 0, 127}));
  connect(adaptive_velocity_delta_state_z.y, mrac_velocity_delta_pre_z.u1) 
    annotation(Line(points = {{-146, -377}, {221, -377}}, color = {0, 0, 127}));
  connect(mrac_velocity_adaptation_gain_z.y, mrac_velocity_delta_pre_z.u2) 
    annotation(Line(points = {{154, -377}, {221, -377}}, color = {0, 0, 127}));
  connect(mrac_velocity_delta_pre_z.y, mrac_velocity_delta_limit_z.u) 
    annotation(Line(points = {{249, -377}, {321, -377}}, color = {0, 0, 127}));
  connect(mrac_velocity_delta_limit_z.y, adaptive_velocity_delta_state_z.u1) 
    annotation(Line(points = {{321, -377}, {-146, -377}}, color = {0, 0, 127}));
  connect(mrac_base_position_gain_z.y, mrac_effective_position_gain_z.u1) 
    annotation(Line(points = {{34, -275}, {106, -275}}, color = {0, 0, 127}));
  connect(adaptive_position_delta_state_z.y, mrac_effective_position_gain_z.u2) 
    annotation(Line(points = {{-146, -335}, {-20, -335}, {-20, -275}, {106, -275}}, color = {0, 0, 127}));
  connect(mrac_base_velocity_gain_z.y, mrac_effective_velocity_gain_z.u1) 
    annotation(Line(points = {{34, -305}, {106, -305}}, color = {0, 0, 127}));
  connect(adaptive_velocity_delta_state_z.y, mrac_effective_velocity_gain_z.u2) 
    annotation(Line(points = {{-146, -377}, {-20, -377}, {-20, -305}, {106, -305}}, color = {0, 0, 127}));
  connect(mrac_effective_position_gain_z.y, mrac_position_feedback_z.u1) 
    annotation(Line(points = {{134, -275}, {236, -275}}, color = {0, 0, 127}));
  connect(mrac_position_error_z.y, mrac_position_feedback_z.u2) 
    annotation(Line(points = {{-316, -210}, {-40, -210}, {-40, -275}, {236, -275}}, color = {0, 0, 127}));
  connect(mrac_effective_velocity_gain_z.y, mrac_velocity_feedback_z.u1) 
    annotation(Line(points = {{134, -305}, {236, -305}}, color = {0, 0, 127}));
  connect(mrac_velocity_error_z.y, mrac_velocity_feedback_z.u2) 
    annotation(Line(points = {{-316, -250}, {-40, -250}, {-40, -305}, {236, -305}}, color = {0, 0, 127}));
  connect(reference_model_acceleration_z.y, mrac_desired_acceleration_pre_gravity_z_stage_2.u1) 
    annotation(Line(points = {{-166, -125}, {71, -125}, {71, -285}, {308, -285}}, color = {0, 0, 127}));
  connect(mrac_position_feedback_z.y, mrac_desired_acceleration_pre_gravity_z_stage_2.u2) 
    annotation(Line(points = {{264, -275}, {286, -275}, {286, -285}, {308, -285}}, color = {0, 0, 127}));
  connect(mrac_desired_acceleration_pre_gravity_z_stage_2.y, mrac_desired_acceleration_pre_gravity_z.u1) 
    annotation(Line(points = {{336, -285}, {376, -285}}, color = {0, 0, 127}));
  connect(mrac_velocity_feedback_z.y, mrac_desired_acceleration_pre_gravity_z.u2) 
    annotation(Line(points = {{264, -305}, {320, -305}, {320, -285}, {376, -285}}, color = {0, 0, 127}));
  connect(mrac_desired_acceleration_pre_gravity_z.y, desired_acceleration_z.u1) 
    annotation(Line(points = {{376, -285}, {154, -285}}, color = {0, 0, 127}));
  connect(gravity_compensation.y, desired_acceleration_z.u2) 
    annotation(Line(points = {{69, -213}, {97.5, -213}, {97.5, -285}, {126, -285}}, color = {0, 0, 127}));
  connect(desired_acceleration_y.y, roll_from_lateral_acceleration.u) 
    annotation(Line(points = {{140, -49}, {140, 7.5}, {230, 7.5}, {230, 64}}, color = {0, 0, 127}));
  connect(roll_from_lateral_acceleration.y, roll_tilt_limit.u) 
    annotation(Line(points = {{244, 75}, {306, 75}}, color = {0, 0, 127}));
  connect(desired_acceleration_x.y, pitch_from_lateral_acceleration.u) 
    annotation(Line(points = {{154, 165}, {185, 165}, {185, 130}, {216, 130}}, color = {0, 0, 127}));
  connect(pitch_from_lateral_acceleration.y, pitch_tilt_limit.u) 
    annotation(Line(points = {{244, 130}, {306, 130}}, color = {0, 0, 127}));
  connect(desired_acceleration_z.y, vertical_force_allocation.u) 
    annotation(Line(points = {{140, -274}, {140, -165}, {230, -165}, {230, -56}}, color = {0, 0, 127}));
  connect(vertical_force_allocation.y, collective_thrust_limit.u) 
    annotation(Line(points = {{244, -45}, {306, -45}}, color = {0, 0, 127}));
  connect(collective_thrust_limit.y, normalized_thrust_from_collective.u) 
    annotation(Line(points = {{334, -45}, {396, -45}}, color = {0, 0, 127}));
  connect(normalized_thrust_from_collective.y, normalized_thrust_limit.u) 
    annotation(Line(points = {{424, -45}, {486, -45}}, color = {0, 0, 127}));
  connect(reference_model_position_state_x.y, enable_reference_model_position_x.u1) 
    annotation(Line(points = {{-416, 340}, {52.5, 340}, {52.5, 350}, {521, 350}}, color = {0, 0, 127}));
  connect(enable, enable_reference_model_position_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 350}, {521, 350}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_reference_model_position_x.u3) 
    annotation(Line(points = {{500, -299}, {500, 20}, {535, 20}, {535, 339}}, color = {0, 0, 127}));
  connect(enable_reference_model_position_x.y, reference_model_position_x_out) 
    annotation(Line(points = {{549, 350}, {681, 350}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_x.y, enable_reference_model_velocity_x.u1) 
    annotation(Line(points = {{-416, 300}, {52.5, 300}, {52.5, 312}, {521, 312}}, color = {0, 0, 127}));
  connect(enable, enable_reference_model_velocity_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 312}, {521, 312}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_reference_model_velocity_x.u3) 
    annotation(Line(points = {{500, -299}, {500, 1}, {535, 1}, {535, 301}}, color = {0, 0, 127}));
  connect(enable_reference_model_velocity_x.y, reference_model_velocity_x_out) 
    annotation(Line(points = {{549, 312}, {681, 312}}, color = {0, 0, 127}));
  connect(adaptive_position_delta_state_x.y, enable_adaptive_position_delta_x.u1) 
    annotation(Line(points = {{-146, 115}, {187.5, 115}, {187.5, 274}, {521, 274}}, color = {0, 0, 127}));
  connect(enable, enable_adaptive_position_delta_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 274}, {521, 274}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_adaptive_position_delta_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -18}, {535, -18}, {535, 263}}, color = {0, 0, 127}));
  connect(enable_adaptive_position_delta_x.y, adaptive_position_delta_x_out) 
    annotation(Line(points = {{549, 274}, {681, 274}}, color = {0, 0, 127}));
  connect(adaptive_velocity_delta_state_x.y, enable_adaptive_velocity_delta_x.u1) 
    annotation(Line(points = {{-146, 73}, {187.5, 73}, {187.5, 236}, {521, 236}}, color = {0, 0, 127}));
  connect(enable, enable_adaptive_velocity_delta_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 236}, {521, 236}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_adaptive_velocity_delta_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -37}, {535, -37}, {535, 225}}, color = {0, 0, 127}));
  connect(enable_adaptive_velocity_delta_x.y, adaptive_velocity_delta_x_out) 
    annotation(Line(points = {{549, 236}, {681, 236}}, color = {0, 0, 127}));
  connect(mrac_sliding_surface_x.y, enable_sliding_surface_x.u1) 
    annotation(Line(points = {{-66, 220}, {227.5, 220}, {227.5, 198}, {521, 198}}, color = {0, 0, 127}));
  connect(enable, enable_sliding_surface_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 198}, {521, 198}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_sliding_surface_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -56}, {535, -56}, {535, 187}}, color = {0, 0, 127}));
  connect(enable_sliding_surface_x.y, sliding_surface_x_out) 
    annotation(Line(points = {{549, 198}, {681, 198}}, color = {0, 0, 127}));
  connect(desired_acceleration_x.y, enable_desired_acceleration_x.u1) 
    annotation(Line(points = {{154, 165}, {337.5, 165}, {337.5, 160}, {521, 160}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 160}, {521, 160}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -75}, {535, -75}, {535, 149}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out) 
    annotation(Line(points = {{549, 160}, {681, 160}}, color = {0, 0, 127}));
  connect(reference_model_position_state_y.y, enable_reference_model_position_y.u1) 
    annotation(Line(points = {{-416, 115}, {52.5, 115}, {52.5, 122}, {521, 122}}, color = {0, 0, 127}));
  connect(enable, enable_reference_model_position_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 122}, {521, 122}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_reference_model_position_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -94}, {535, -94}, {535, 111}}, color = {0, 0, 127}));
  connect(enable_reference_model_position_y.y, reference_model_position_y_out) 
    annotation(Line(points = {{549, 122}, {681, 122}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_y.y, enable_reference_model_velocity_y.u1) 
    annotation(Line(points = {{-416, 75}, {52.5, 75}, {52.5, 84}, {521, 84}}, color = {0, 0, 127}));
  connect(enable, enable_reference_model_velocity_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 84}, {521, 84}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_reference_model_velocity_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -113}, {535, -113}, {535, 73}}, color = {0, 0, 127}));
  connect(enable_reference_model_velocity_y.y, reference_model_velocity_y_out) 
    annotation(Line(points = {{549, 84}, {681, 84}}, color = {0, 0, 127}));
  connect(adaptive_position_delta_state_y.y, enable_adaptive_position_delta_y.u1) 
    annotation(Line(points = {{-146, -110}, {187.5, -110}, {187.5, 46}, {521, 46}}, color = {0, 0, 127}));
  connect(enable, enable_adaptive_position_delta_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 46}, {521, 46}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_adaptive_position_delta_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -132}, {535, -132}, {535, 35}}, color = {0, 0, 127}));
  connect(enable_adaptive_position_delta_y.y, adaptive_position_delta_y_out) 
    annotation(Line(points = {{549, 46}, {681, 46}}, color = {0, 0, 127}));
  connect(adaptive_velocity_delta_state_y.y, enable_adaptive_velocity_delta_y.u1) 
    annotation(Line(points = {{-146, -152}, {187.5, -152}, {187.5, 8}, {521, 8}}, color = {0, 0, 127}));
  connect(enable, enable_adaptive_velocity_delta_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 8}, {521, 8}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_adaptive_velocity_delta_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -151}, {535, -151}, {535, -3}}, color = {0, 0, 127}));
  connect(enable_adaptive_velocity_delta_y.y, adaptive_velocity_delta_y_out) 
    annotation(Line(points = {{549, 8}, {681, 8}}, color = {0, 0, 127}));
  connect(mrac_sliding_surface_y.y, enable_sliding_surface_y.u1) 
    annotation(Line(points = {{-66, -5}, {227.5, -5}, {227.5, -30}, {521, -30}}, color = {0, 0, 127}));
  connect(enable, enable_sliding_surface_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -30}, {521, -30}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_sliding_surface_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -170}, {535, -170}, {535, -41}}, color = {0, 0, 127}));
  connect(enable_sliding_surface_y.y, sliding_surface_y_out) 
    annotation(Line(points = {{549, -30}, {681, -30}}, color = {0, 0, 127}));
  connect(desired_acceleration_y.y, enable_desired_acceleration_y.u1) 
    annotation(Line(points = {{154, -60}, {337.5, -60}, {337.5, -68}, {521, -68}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -68}, {521, -68}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -189}, {535, -189}, {535, -79}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out) 
    annotation(Line(points = {{549, -68}, {681, -68}}, color = {0, 0, 127}));
  connect(reference_model_position_state_z.y, enable_reference_model_position_z.u1) 
    annotation(Line(points = {{-416, -110}, {52.5, -110}, {52.5, -106}, {521, -106}}, color = {0, 0, 127}));
  connect(enable, enable_reference_model_position_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -106}, {521, -106}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_reference_model_position_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -208}, {535, -208}, {535, -117}}, color = {0, 0, 127}));
  connect(enable_reference_model_position_z.y, reference_model_position_z_out) 
    annotation(Line(points = {{549, -106}, {681, -106}}, color = {0, 0, 127}));
  connect(reference_model_velocity_state_z.y, enable_reference_model_velocity_z.u1) 
    annotation(Line(points = {{-416, -150}, {52.5, -150}, {52.5, -144}, {521, -144}}, color = {0, 0, 127}));
  connect(enable, enable_reference_model_velocity_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -144}, {521, -144}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_reference_model_velocity_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -227}, {535, -227}, {535, -155}}, color = {0, 0, 127}));
  connect(enable_reference_model_velocity_z.y, reference_model_velocity_z_out) 
    annotation(Line(points = {{549, -144}, {681, -144}}, color = {0, 0, 127}));
  connect(adaptive_position_delta_state_z.y, enable_adaptive_position_delta_z.u1) 
    annotation(Line(points = {{-146, -335}, {187.5, -335}, {187.5, -182}, {521, -182}}, color = {0, 0, 127}));
  connect(enable, enable_adaptive_position_delta_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -182}, {521, -182}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_adaptive_position_delta_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -246}, {535, -246}, {535, -193}}, color = {0, 0, 127}));
  connect(enable_adaptive_position_delta_z.y, adaptive_position_delta_z_out) 
    annotation(Line(points = {{549, -182}, {681, -182}}, color = {0, 0, 127}));
  connect(adaptive_velocity_delta_state_z.y, enable_adaptive_velocity_delta_z.u1) 
    annotation(Line(points = {{-146, -377}, {187.5, -377}, {187.5, -220}, {521, -220}}, color = {0, 0, 127}));
  connect(enable, enable_adaptive_velocity_delta_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -220}, {521, -220}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_adaptive_velocity_delta_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -265}, {535, -265}, {535, -231}}, color = {0, 0, 127}));
  connect(enable_adaptive_velocity_delta_z.y, adaptive_velocity_delta_z_out) 
    annotation(Line(points = {{549, -220}, {681, -220}}, color = {0, 0, 127}));
  connect(mrac_sliding_surface_z.y, enable_sliding_surface_z.u1) 
    annotation(Line(points = {{-66, -230}, {227.5, -230}, {227.5, -258}, {521, -258}}, color = {0, 0, 127}));
  connect(enable, enable_sliding_surface_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -258}, {521, -258}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_sliding_surface_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -284}, {535, -284}, {535, -269}}, color = {0, 0, 127}));
  connect(enable_sliding_surface_z.y, sliding_surface_z_out) 
    annotation(Line(points = {{549, -258}, {681, -258}}, color = {0, 0, 127}));
  connect(desired_acceleration_z.y, enable_desired_acceleration_z.u1) 
    annotation(Line(points = {{154, -285}, {337.5, -285}, {337.5, -296}, {521, -296}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -296}, {521, -296}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_z.u3) 
    annotation(Line(points = {{514, -310}, {517.5, -310}, {517.5, -296}, {521, -296}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_z.y, desired_acceleration_z_out) 
    annotation(Line(points = {{549, -296}, {681, -296}}, color = {0, 0, 127}));
  connect(roll_tilt_limit.y, enable_desired_roll_rad.u1) 
    annotation(Line(points = {{320, 64}, {320, -129.5}, {535, -129.5}, {535, -323}}, color = {0, 0, 127}));
  connect(enable, enable_desired_roll_rad.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -334}, {521, -334}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_roll_rad.u3) 
    annotation(Line(points = {{514, -310}, {517.5, -310}, {517.5, -334}, {521, -334}}, color = {0, 0, 127}));
  connect(enable_desired_roll_rad.y, desired_roll_rad_out) 
    annotation(Line(points = {{549, -334}, {681, -334}}, color = {0, 0, 127}));
  connect(pitch_tilt_limit.y, enable_desired_pitch_rad.u1) 
    annotation(Line(points = {{320, 119}, {320, -121}, {535, -121}, {535, -361}}, color = {0, 0, 127}));
  connect(enable, enable_desired_pitch_rad.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -372}, {521, -372}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_pitch_rad.u3) 
    annotation(Line(points = {{500, -321}, {500, -341}, {535, -341}, {535, -361}}, color = {0, 0, 127}));
  connect(enable_desired_pitch_rad.y, desired_pitch_rad_out) 
    annotation(Line(points = {{549, -372}, {681, -372}}, color = {0, 0, 127}));
  connect(collective_thrust_limit.y, enable_collective_thrust_n.u1) 
    annotation(Line(points = {{320, -56}, {320, -227.5}, {535, -227.5}, {535, -399}}, color = {0, 0, 127}));
  connect(enable, enable_collective_thrust_n.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -410}, {521, -410}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_collective_thrust_n.u3) 
    annotation(Line(points = {{500, -321}, {500, -360}, {535, -360}, {535, -399}}, color = {0, 0, 127}));
  connect(enable_collective_thrust_n.y, collective_thrust_n_out) 
    annotation(Line(points = {{549, -410}, {681, -410}}, color = {0, 0, 127}));
  connect(normalized_thrust_limit.y, enable_normalized_thrust.u1) 
    annotation(Line(points = {{500, -56}, {500, -246.5}, {535, -246.5}, {535, -437}}, color = {0, 0, 127}));
  connect(enable, enable_normalized_thrust.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -448}, {521, -448}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_normalized_thrust.u3) 
    annotation(Line(points = {{500, -321}, {500, -379}, {535, -379}, {535, -437}}, color = {0, 0, 127}));
  connect(enable_normalized_thrust.y, normalized_thrust_out) 
    annotation(Line(points = {{549, -448}, {681, -448}}, color = {0, 0, 127}));
end MracCore;