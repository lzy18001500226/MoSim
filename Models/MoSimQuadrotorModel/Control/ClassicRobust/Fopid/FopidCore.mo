within MoSimQuadrotorModel.Control.ClassicRobust.Fopid;
model FopidCore "FOPID direct graphical core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, dt, enable), Right(position_error_x_out, fractional_integral_x_out, fractional_derivative_x_out, desired_acceleration_x_out, position_error_y_out, fractional_integral_y_out, fractional_derivative_y_out, desired_acceleration_y_out, position_error_z_out, fractional_integral_z_out, fractional_derivative_z_out, desired_acceleration_z_out, desired_roll_rad_out, desired_pitch_rad_out, collective_thrust_n_out, normalized_thrust_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
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
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_position_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-590, 260}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_01(initCond=0.0) 
    annotation (Placement(transformation(origin = {-458, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_02(initCond=0.0) 
    annotation (Placement(transformation(origin = {-416, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_03(initCond=0.0) 
    annotation (Placement(transformation(origin = {-374, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_04(initCond=0.0) 
    annotation (Placement(transformation(origin = {-332, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_05(initCond=0.0) 
    annotation (Placement(transformation(origin = {-290, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_06(initCond=0.0) 
    annotation (Placement(transformation(origin = {-248, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_07(initCond=0.0) 
    annotation (Placement(transformation(origin = {-206, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_08(initCond=0.0) 
    annotation (Placement(transformation(origin = {-164, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_09(initCond=0.0) 
    annotation (Placement(transformation(origin = {-122, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_10(initCond=0.0) 
    annotation (Placement(transformation(origin = {-80, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_11(initCond=0.0) 
    annotation (Placement(transformation(origin = {-38, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_12(initCond=0.0) 
    annotation (Placement(transformation(origin = {4, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_13(initCond=0.0) 
    annotation (Placement(transformation(origin = {46, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_14(initCond=0.0) 
    annotation (Placement(transformation(origin = {88, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_x_15(initCond=0.0) 
    annotation (Placement(transformation(origin = {130, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_00(k=0.0199526231496888) 
    annotation (Placement(transformation(origin = {-500, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_01(k=0.01695972967723548) 
    annotation (Placement(transformation(origin = {-458, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_02(k=0.01568774995144282) 
    annotation (Placement(transformation(origin = {-416, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_03(k=0.01490336245387068) 
    annotation (Placement(transformation(origin = {-374, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_04(k=0.014344486361850529) 
    annotation (Placement(transformation(origin = {-332, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_05(k=0.013914151770995012) 
    annotation (Placement(transformation(origin = {-290, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_06(k=0.013566297976720137) 
    annotation (Placement(transformation(origin = {-248, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_07(k=0.013275591591504704) 
    annotation (Placement(transformation(origin = {-206, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_08(k=0.01302667424916399) 
    annotation (Placement(transformation(origin = {-164, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_09(k=0.012809563011677922) 
    annotation (Placement(transformation(origin = {-122, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_10(k=0.012617419566502754) 
    annotation (Placement(transformation(origin = {-80, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_11(k=0.012445363845141354) 
    annotation (Placement(transformation(origin = {-38, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_12(k=0.012289796797077085) 
    annotation (Placement(transformation(origin = {4, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_13(k=0.012147991449418503) 
    annotation (Placement(transformation(origin = {46, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_14(k=0.01201783439817473) 
    annotation (Placement(transformation(origin = {88, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_x_15(k=0.011897656054192983) 
    annotation (Placement(transformation(origin = {130, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_00(k=19.952623149688797) 
    annotation (Placement(transformation(origin = {-500, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_01(k=-12.969205047297718) 
    annotation (Placement(transformation(origin = {-458, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_02(k=-2.2696108832771014) 
    annotation (Placement(transformation(origin = {-416, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_03(k=-1.0213248974746956) 
    annotation (Placement(transformation(origin = {-374, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_04(k=-0.6000283772663837) 
    annotation (Placement(transformation(origin = {-332, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_05(k=-0.402019012768477) 
    annotation (Placement(transformation(origin = {-290, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_06(k=-0.29146378425714586) 
    annotation (Placement(transformation(origin = {-248, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_07(k=-0.22276160653939003) 
    annotation (Placement(transformation(origin = {-206, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_08(k=-0.17681702519064083) 
    annotation (Placement(transformation(origin = {-164, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_09(k=-0.14440057057235667) 
    annotation (Placement(transformation(origin = {-122, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_10(k=-0.12057447642791781) 
    annotation (Placement(transformation(origin = {-80, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_11(k=-0.10248830496373014) 
    annotation (Placement(transformation(origin = {-38, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_12(k=-0.08839616303121725) 
    annotation (Placement(transformation(origin = {4, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_13(k=-0.07717665003110122) 
    annotation (Placement(transformation(origin = {46, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_14(k=-0.06808083056315) 
    annotation (Placement(transformation(origin = {88, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_x_15(k=-0.060591939201203496) 
    annotation (Placement(transformation(origin = {130, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_2 
    annotation (Placement(transformation(origin = {-787, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_3 
    annotation (Placement(transformation(origin = {-719, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_4 
    annotation (Placement(transformation(origin = {-651, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_5 
    annotation (Placement(transformation(origin = {-583, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_6 
    annotation (Placement(transformation(origin = {-515, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_7 
    annotation (Placement(transformation(origin = {-447, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_8 
    annotation (Placement(transformation(origin = {-379, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_9 
    annotation (Placement(transformation(origin = {-311, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_10 
    annotation (Placement(transformation(origin = {-243, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_11 
    annotation (Placement(transformation(origin = {-175, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_12 
    annotation (Placement(transformation(origin = {-107, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_13 
    annotation (Placement(transformation(origin = {-39, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_14 
    annotation (Placement(transformation(origin = {29, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x_stage_15 
    annotation (Placement(transformation(origin = {97, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_x 
    annotation (Placement(transformation(origin = {165, 202}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_2 
    annotation (Placement(transformation(origin = {-787, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_3 
    annotation (Placement(transformation(origin = {-719, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_4 
    annotation (Placement(transformation(origin = {-651, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_5 
    annotation (Placement(transformation(origin = {-583, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_6 
    annotation (Placement(transformation(origin = {-515, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_7 
    annotation (Placement(transformation(origin = {-447, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_8 
    annotation (Placement(transformation(origin = {-379, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_9 
    annotation (Placement(transformation(origin = {-311, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_10 
    annotation (Placement(transformation(origin = {-243, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_11 
    annotation (Placement(transformation(origin = {-175, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_12 
    annotation (Placement(transformation(origin = {-107, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_13 
    annotation (Placement(transformation(origin = {-39, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_14 
    annotation (Placement(transformation(origin = {29, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x_stage_15 
    annotation (Placement(transformation(origin = {97, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_x 
    annotation (Placement(transformation(origin = {165, 158}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_proportional_x(k=6.5) 
    annotation (Placement(transformation(origin = {-150, 300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_feedback_x(k=0.8) 
    annotation (Placement(transformation(origin = {265, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_feedback_x(k=1.2) 
    annotation (Placement(transformation(origin = {265, 158}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_desired_acceleration_pre_gravity_x_stage_2 
    annotation (Placement(transformation(origin = {239, 260}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_desired_acceleration_pre_gravity_x_stage_3 
    annotation (Placement(transformation(origin = {307, 260}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_desired_acceleration_pre_gravity_x 
    annotation (Placement(transformation(origin = {375, 260}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_x(k=1.0) 
    annotation (Placement(transformation(origin = {140, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_position_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-590, 25}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_01(initCond=0.0) 
    annotation (Placement(transformation(origin = {-458, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_02(initCond=0.0) 
    annotation (Placement(transformation(origin = {-416, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_03(initCond=0.0) 
    annotation (Placement(transformation(origin = {-374, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_04(initCond=0.0) 
    annotation (Placement(transformation(origin = {-332, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_05(initCond=0.0) 
    annotation (Placement(transformation(origin = {-290, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_06(initCond=0.0) 
    annotation (Placement(transformation(origin = {-248, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_07(initCond=0.0) 
    annotation (Placement(transformation(origin = {-206, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_08(initCond=0.0) 
    annotation (Placement(transformation(origin = {-164, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_09(initCond=0.0) 
    annotation (Placement(transformation(origin = {-122, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_10(initCond=0.0) 
    annotation (Placement(transformation(origin = {-80, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_11(initCond=0.0) 
    annotation (Placement(transformation(origin = {-38, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_12(initCond=0.0) 
    annotation (Placement(transformation(origin = {4, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_13(initCond=0.0) 
    annotation (Placement(transformation(origin = {46, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_14(initCond=0.0) 
    annotation (Placement(transformation(origin = {88, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_y_15(initCond=0.0) 
    annotation (Placement(transformation(origin = {130, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_00(k=0.0199526231496888) 
    annotation (Placement(transformation(origin = {-500, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_01(k=0.01695972967723548) 
    annotation (Placement(transformation(origin = {-458, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_02(k=0.01568774995144282) 
    annotation (Placement(transformation(origin = {-416, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_03(k=0.01490336245387068) 
    annotation (Placement(transformation(origin = {-374, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_04(k=0.014344486361850529) 
    annotation (Placement(transformation(origin = {-332, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_05(k=0.013914151770995012) 
    annotation (Placement(transformation(origin = {-290, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_06(k=0.013566297976720137) 
    annotation (Placement(transformation(origin = {-248, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_07(k=0.013275591591504704) 
    annotation (Placement(transformation(origin = {-206, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_08(k=0.01302667424916399) 
    annotation (Placement(transformation(origin = {-164, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_09(k=0.012809563011677922) 
    annotation (Placement(transformation(origin = {-122, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_10(k=0.012617419566502754) 
    annotation (Placement(transformation(origin = {-80, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_11(k=0.012445363845141354) 
    annotation (Placement(transformation(origin = {-38, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_12(k=0.012289796797077085) 
    annotation (Placement(transformation(origin = {4, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_13(k=0.012147991449418503) 
    annotation (Placement(transformation(origin = {46, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_14(k=0.01201783439817473) 
    annotation (Placement(transformation(origin = {88, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_y_15(k=0.011897656054192983) 
    annotation (Placement(transformation(origin = {130, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_00(k=19.952623149688797) 
    annotation (Placement(transformation(origin = {-500, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_01(k=-12.969205047297718) 
    annotation (Placement(transformation(origin = {-458, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_02(k=-2.2696108832771014) 
    annotation (Placement(transformation(origin = {-416, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_03(k=-1.0213248974746956) 
    annotation (Placement(transformation(origin = {-374, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_04(k=-0.6000283772663837) 
    annotation (Placement(transformation(origin = {-332, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_05(k=-0.402019012768477) 
    annotation (Placement(transformation(origin = {-290, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_06(k=-0.29146378425714586) 
    annotation (Placement(transformation(origin = {-248, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_07(k=-0.22276160653939003) 
    annotation (Placement(transformation(origin = {-206, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_08(k=-0.17681702519064083) 
    annotation (Placement(transformation(origin = {-164, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_09(k=-0.14440057057235667) 
    annotation (Placement(transformation(origin = {-122, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_10(k=-0.12057447642791781) 
    annotation (Placement(transformation(origin = {-80, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_11(k=-0.10248830496373014) 
    annotation (Placement(transformation(origin = {-38, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_12(k=-0.08839616303121725) 
    annotation (Placement(transformation(origin = {4, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_13(k=-0.07717665003110122) 
    annotation (Placement(transformation(origin = {46, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_14(k=-0.06808083056315) 
    annotation (Placement(transformation(origin = {88, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_y_15(k=-0.060591939201203496) 
    annotation (Placement(transformation(origin = {130, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_2 
    annotation (Placement(transformation(origin = {-787, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_3 
    annotation (Placement(transformation(origin = {-719, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_4 
    annotation (Placement(transformation(origin = {-651, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_5 
    annotation (Placement(transformation(origin = {-583, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_6 
    annotation (Placement(transformation(origin = {-515, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_7 
    annotation (Placement(transformation(origin = {-447, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_8 
    annotation (Placement(transformation(origin = {-379, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_9 
    annotation (Placement(transformation(origin = {-311, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_10 
    annotation (Placement(transformation(origin = {-243, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_11 
    annotation (Placement(transformation(origin = {-175, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_12 
    annotation (Placement(transformation(origin = {-107, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_13 
    annotation (Placement(transformation(origin = {-39, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_14 
    annotation (Placement(transformation(origin = {29, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y_stage_15 
    annotation (Placement(transformation(origin = {97, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_y 
    annotation (Placement(transformation(origin = {165, -33}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_2 
    annotation (Placement(transformation(origin = {-787, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_3 
    annotation (Placement(transformation(origin = {-719, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_4 
    annotation (Placement(transformation(origin = {-651, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_5 
    annotation (Placement(transformation(origin = {-583, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_6 
    annotation (Placement(transformation(origin = {-515, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_7 
    annotation (Placement(transformation(origin = {-447, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_8 
    annotation (Placement(transformation(origin = {-379, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_9 
    annotation (Placement(transformation(origin = {-311, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_10 
    annotation (Placement(transformation(origin = {-243, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_11 
    annotation (Placement(transformation(origin = {-175, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_12 
    annotation (Placement(transformation(origin = {-107, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_13 
    annotation (Placement(transformation(origin = {-39, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_14 
    annotation (Placement(transformation(origin = {29, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y_stage_15 
    annotation (Placement(transformation(origin = {97, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_y 
    annotation (Placement(transformation(origin = {165, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_proportional_y(k=6.5) 
    annotation (Placement(transformation(origin = {-150, 65}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_feedback_y(k=0.8) 
    annotation (Placement(transformation(origin = {265, -33}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_feedback_y(k=1.2) 
    annotation (Placement(transformation(origin = {265, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_desired_acceleration_pre_gravity_y_stage_2 
    annotation (Placement(transformation(origin = {239, 25}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_desired_acceleration_pre_gravity_y_stage_3 
    annotation (Placement(transformation(origin = {307, 25}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_desired_acceleration_pre_gravity_y 
    annotation (Placement(transformation(origin = {375, 25}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_y(k=1.0) 
    annotation (Placement(transformation(origin = {140, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_position_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-590, -210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_01(initCond=0.0) 
    annotation (Placement(transformation(origin = {-458, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_02(initCond=0.0) 
    annotation (Placement(transformation(origin = {-416, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_03(initCond=0.0) 
    annotation (Placement(transformation(origin = {-374, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_04(initCond=0.0) 
    annotation (Placement(transformation(origin = {-332, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_05(initCond=0.0) 
    annotation (Placement(transformation(origin = {-290, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_06(initCond=0.0) 
    annotation (Placement(transformation(origin = {-248, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_07(initCond=0.0) 
    annotation (Placement(transformation(origin = {-206, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_08(initCond=0.0) 
    annotation (Placement(transformation(origin = {-164, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_09(initCond=0.0) 
    annotation (Placement(transformation(origin = {-122, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_10(initCond=0.0) 
    annotation (Placement(transformation(origin = {-80, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_11(initCond=0.0) 
    annotation (Placement(transformation(origin = {-38, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_12(initCond=0.0) 
    annotation (Placement(transformation(origin = {4, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_13(initCond=0.0) 
    annotation (Placement(transformation(origin = {46, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_14(initCond=0.0) 
    annotation (Placement(transformation(origin = {88, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay fopid_history_z_15(initCond=0.0) 
    annotation (Placement(transformation(origin = {130, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_00(k=0.0199526231496888) 
    annotation (Placement(transformation(origin = {-500, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_01(k=0.01695972967723548) 
    annotation (Placement(transformation(origin = {-458, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_02(k=0.01568774995144282) 
    annotation (Placement(transformation(origin = {-416, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_03(k=0.01490336245387068) 
    annotation (Placement(transformation(origin = {-374, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_04(k=0.014344486361850529) 
    annotation (Placement(transformation(origin = {-332, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_05(k=0.013914151770995012) 
    annotation (Placement(transformation(origin = {-290, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_06(k=0.013566297976720137) 
    annotation (Placement(transformation(origin = {-248, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_07(k=0.013275591591504704) 
    annotation (Placement(transformation(origin = {-206, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_08(k=0.01302667424916399) 
    annotation (Placement(transformation(origin = {-164, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_09(k=0.012809563011677922) 
    annotation (Placement(transformation(origin = {-122, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_10(k=0.012617419566502754) 
    annotation (Placement(transformation(origin = {-80, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_11(k=0.012445363845141354) 
    annotation (Placement(transformation(origin = {-38, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_12(k=0.012289796797077085) 
    annotation (Placement(transformation(origin = {4, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_13(k=0.012147991449418503) 
    annotation (Placement(transformation(origin = {46, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_14(k=0.01201783439817473) 
    annotation (Placement(transformation(origin = {88, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_weight_z_15(k=0.011897656054192983) 
    annotation (Placement(transformation(origin = {130, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_00(k=19.952623149688797) 
    annotation (Placement(transformation(origin = {-500, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_01(k=-12.969205047297718) 
    annotation (Placement(transformation(origin = {-458, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_02(k=-2.2696108832771014) 
    annotation (Placement(transformation(origin = {-416, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_03(k=-1.0213248974746956) 
    annotation (Placement(transformation(origin = {-374, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_04(k=-0.6000283772663837) 
    annotation (Placement(transformation(origin = {-332, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_05(k=-0.402019012768477) 
    annotation (Placement(transformation(origin = {-290, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_06(k=-0.29146378425714586) 
    annotation (Placement(transformation(origin = {-248, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_07(k=-0.22276160653939003) 
    annotation (Placement(transformation(origin = {-206, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_08(k=-0.17681702519064083) 
    annotation (Placement(transformation(origin = {-164, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_09(k=-0.14440057057235667) 
    annotation (Placement(transformation(origin = {-122, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_10(k=-0.12057447642791781) 
    annotation (Placement(transformation(origin = {-80, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_11(k=-0.10248830496373014) 
    annotation (Placement(transformation(origin = {-38, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_12(k=-0.08839616303121725) 
    annotation (Placement(transformation(origin = {4, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_13(k=-0.07717665003110122) 
    annotation (Placement(transformation(origin = {46, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_14(k=-0.06808083056315) 
    annotation (Placement(transformation(origin = {88, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_weight_z_15(k=-0.060591939201203496) 
    annotation (Placement(transformation(origin = {130, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_2 
    annotation (Placement(transformation(origin = {-787, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_3 
    annotation (Placement(transformation(origin = {-719, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_4 
    annotation (Placement(transformation(origin = {-651, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_5 
    annotation (Placement(transformation(origin = {-583, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_6 
    annotation (Placement(transformation(origin = {-515, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_7 
    annotation (Placement(transformation(origin = {-447, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_8 
    annotation (Placement(transformation(origin = {-379, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_9 
    annotation (Placement(transformation(origin = {-311, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_10 
    annotation (Placement(transformation(origin = {-243, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_11 
    annotation (Placement(transformation(origin = {-175, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_12 
    annotation (Placement(transformation(origin = {-107, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_13 
    annotation (Placement(transformation(origin = {-39, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_14 
    annotation (Placement(transformation(origin = {29, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z_stage_15 
    annotation (Placement(transformation(origin = {97, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_integral_z 
    annotation (Placement(transformation(origin = {165, -268}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_2 
    annotation (Placement(transformation(origin = {-787, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_3 
    annotation (Placement(transformation(origin = {-719, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_4 
    annotation (Placement(transformation(origin = {-651, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_5 
    annotation (Placement(transformation(origin = {-583, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_6 
    annotation (Placement(transformation(origin = {-515, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_7 
    annotation (Placement(transformation(origin = {-447, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_8 
    annotation (Placement(transformation(origin = {-379, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_9 
    annotation (Placement(transformation(origin = {-311, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_10 
    annotation (Placement(transformation(origin = {-243, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_11 
    annotation (Placement(transformation(origin = {-175, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_12 
    annotation (Placement(transformation(origin = {-107, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_13 
    annotation (Placement(transformation(origin = {-39, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_14 
    annotation (Placement(transformation(origin = {29, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z_stage_15 
    annotation (Placement(transformation(origin = {97, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_fractional_derivative_z 
    annotation (Placement(transformation(origin = {165, -312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_proportional_z(k=4.5) 
    annotation (Placement(transformation(origin = {-150, -170}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_integral_feedback_z(k=0.7) 
    annotation (Placement(transformation(origin = {265, -268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fopid_derivative_feedback_z(k=1.0) 
    annotation (Placement(transformation(origin = {265, -312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_desired_acceleration_pre_gravity_z_stage_2 
    annotation (Placement(transformation(origin = {239, -210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_desired_acceleration_pre_gravity_z_stage_3 
    annotation (Placement(transformation(origin = {307, -210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum fopid_desired_acceleration_pre_gravity_z 
    annotation (Placement(transformation(origin = {375, -210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity_compensation(k=9.80665) 
    annotation (Placement(transformation(origin = {55, -138}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_z 
    annotation (Placement(transformation(origin = {140, -210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 345}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_x_out 
    annotation (Placement(transformation(origin = {695, 345}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_fractional_integral_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 307}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport fractional_integral_x_out 
    annotation (Placement(transformation(origin = {695, 307}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_fractional_derivative_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 269}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport fractional_derivative_x_out 
    annotation (Placement(transformation(origin = {695, 269}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 231}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out 
    annotation (Placement(transformation(origin = {695, 231}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 193}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_y_out 
    annotation (Placement(transformation(origin = {695, 193}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_fractional_integral_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport fractional_integral_y_out 
    annotation (Placement(transformation(origin = {695, 155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_fractional_derivative_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 117}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport fractional_derivative_y_out 
    annotation (Placement(transformation(origin = {695, 117}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 79}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out 
    annotation (Placement(transformation(origin = {695, 79}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 41}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_z_out 
    annotation (Placement(transformation(origin = {695, 41}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_fractional_integral_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 3}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport fractional_integral_z_out 
    annotation (Placement(transformation(origin = {695, 3}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_fractional_derivative_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -35}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport fractional_derivative_z_out 
    annotation (Placement(transformation(origin = {695, -35}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -73}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out 
    annotation (Placement(transformation(origin = {695, -73}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_roll_rad(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -111}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_roll_rad_out 
    annotation (Placement(transformation(origin = {695, -111}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_pitch_rad(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -149}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_pitch_rad_out 
    annotation (Placement(transformation(origin = {695, -149}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_collective_thrust_n(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -187}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n_out 
    annotation (Placement(transformation(origin = {695, -187}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_normalized_thrust(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -225}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out 
    annotation (Placement(transformation(origin = {695, -225}, extent = {{-14, -11}, {14, 11}})));
equation
  connect(reference_position_x, fopid_position_error_x.u1) 
    annotation(Line(points = {{-680, 137}, {-680, 193}, {-590, 193}, {-590, 249}}, color = {0, 0, 127}));
  connect(position_x, fopid_position_error_x.u2) 
    annotation(Line(points = {{-666, 350}, {-635, 350}, {-635, 260}, {-604, 260}}, color = {0, 0, 127}));
  connect(fopid_position_error_x.y, fopid_history_x_01.u1) 
    annotation(Line(points = {{-576, 260}, {-472, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_01.y, fopid_history_x_02.u1) 
    annotation(Line(points = {{-444, 260}, {-430, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_02.y, fopid_history_x_03.u1) 
    annotation(Line(points = {{-402, 260}, {-388, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_03.y, fopid_history_x_04.u1) 
    annotation(Line(points = {{-360, 260}, {-346, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_04.y, fopid_history_x_05.u1) 
    annotation(Line(points = {{-318, 260}, {-304, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_05.y, fopid_history_x_06.u1) 
    annotation(Line(points = {{-276, 260}, {-262, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_06.y, fopid_history_x_07.u1) 
    annotation(Line(points = {{-234, 260}, {-220, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_07.y, fopid_history_x_08.u1) 
    annotation(Line(points = {{-192, 260}, {-178, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_08.y, fopid_history_x_09.u1) 
    annotation(Line(points = {{-150, 260}, {-136, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_09.y, fopid_history_x_10.u1) 
    annotation(Line(points = {{-108, 260}, {-94, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_10.y, fopid_history_x_11.u1) 
    annotation(Line(points = {{-66, 260}, {-52, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_11.y, fopid_history_x_12.u1) 
    annotation(Line(points = {{-24, 260}, {-10, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_12.y, fopid_history_x_13.u1) 
    annotation(Line(points = {{18, 260}, {32, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_13.y, fopid_history_x_14.u1) 
    annotation(Line(points = {{60, 260}, {74, 260}}, color = {0, 0, 127}));
  connect(fopid_history_x_14.y, fopid_history_x_15.u1) 
    annotation(Line(points = {{102, 260}, {116, 260}}, color = {0, 0, 127}));
  connect(fopid_position_error_x.y, fopid_integral_weight_x_00.u) 
    annotation(Line(points = {{-576, 260}, {-545, 260}, {-545, 202}, {-514, 202}}, color = {0, 0, 127}));
  connect(fopid_history_x_01.y, fopid_integral_weight_x_01.u) 
    annotation(Line(points = {{-458, 249}, {-458, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_02.y, fopid_integral_weight_x_02.u) 
    annotation(Line(points = {{-416, 249}, {-416, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_03.y, fopid_integral_weight_x_03.u) 
    annotation(Line(points = {{-374, 249}, {-374, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_04.y, fopid_integral_weight_x_04.u) 
    annotation(Line(points = {{-332, 249}, {-332, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_05.y, fopid_integral_weight_x_05.u) 
    annotation(Line(points = {{-290, 249}, {-290, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_06.y, fopid_integral_weight_x_06.u) 
    annotation(Line(points = {{-248, 249}, {-248, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_07.y, fopid_integral_weight_x_07.u) 
    annotation(Line(points = {{-206, 249}, {-206, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_08.y, fopid_integral_weight_x_08.u) 
    annotation(Line(points = {{-164, 249}, {-164, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_09.y, fopid_integral_weight_x_09.u) 
    annotation(Line(points = {{-122, 249}, {-122, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_10.y, fopid_integral_weight_x_10.u) 
    annotation(Line(points = {{-80, 249}, {-80, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_11.y, fopid_integral_weight_x_11.u) 
    annotation(Line(points = {{-38, 249}, {-38, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_12.y, fopid_integral_weight_x_12.u) 
    annotation(Line(points = {{4, 249}, {4, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_13.y, fopid_integral_weight_x_13.u) 
    annotation(Line(points = {{46, 249}, {46, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_14.y, fopid_integral_weight_x_14.u) 
    annotation(Line(points = {{88, 249}, {88, 213}}, color = {0, 0, 127}));
  connect(fopid_history_x_15.y, fopid_integral_weight_x_15.u) 
    annotation(Line(points = {{130, 249}, {130, 213}}, color = {0, 0, 127}));
  connect(fopid_position_error_x.y, fopid_derivative_weight_x_00.u) 
    annotation(Line(points = {{-590, 249}, {-590, 209}, {-500, 209}, {-500, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_01.y, fopid_derivative_weight_x_01.u) 
    annotation(Line(points = {{-458, 249}, {-458, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_02.y, fopid_derivative_weight_x_02.u) 
    annotation(Line(points = {{-416, 249}, {-416, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_03.y, fopid_derivative_weight_x_03.u) 
    annotation(Line(points = {{-374, 249}, {-374, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_04.y, fopid_derivative_weight_x_04.u) 
    annotation(Line(points = {{-332, 249}, {-332, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_05.y, fopid_derivative_weight_x_05.u) 
    annotation(Line(points = {{-290, 249}, {-290, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_06.y, fopid_derivative_weight_x_06.u) 
    annotation(Line(points = {{-248, 249}, {-248, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_07.y, fopid_derivative_weight_x_07.u) 
    annotation(Line(points = {{-206, 249}, {-206, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_08.y, fopid_derivative_weight_x_08.u) 
    annotation(Line(points = {{-164, 249}, {-164, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_09.y, fopid_derivative_weight_x_09.u) 
    annotation(Line(points = {{-122, 249}, {-122, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_10.y, fopid_derivative_weight_x_10.u) 
    annotation(Line(points = {{-80, 249}, {-80, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_11.y, fopid_derivative_weight_x_11.u) 
    annotation(Line(points = {{-38, 249}, {-38, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_12.y, fopid_derivative_weight_x_12.u) 
    annotation(Line(points = {{4, 249}, {4, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_13.y, fopid_derivative_weight_x_13.u) 
    annotation(Line(points = {{46, 249}, {46, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_14.y, fopid_derivative_weight_x_14.u) 
    annotation(Line(points = {{88, 249}, {88, 169}}, color = {0, 0, 127}));
  connect(fopid_history_x_15.y, fopid_derivative_weight_x_15.u) 
    annotation(Line(points = {{130, 249}, {130, 169}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_00.y, fopid_fractional_integral_x_stage_2.u1) 
    annotation(Line(points = {{-514, 202}, {-773, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_01.y, fopid_fractional_integral_x_stage_2.u2) 
    annotation(Line(points = {{-472, 202}, {-773, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_2.y, fopid_fractional_integral_x_stage_3.u1) 
    annotation(Line(points = {{-773, 202}, {-733, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_02.y, fopid_fractional_integral_x_stage_3.u2) 
    annotation(Line(points = {{-430, 202}, {-705, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_3.y, fopid_fractional_integral_x_stage_4.u1) 
    annotation(Line(points = {{-705, 202}, {-665, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_03.y, fopid_fractional_integral_x_stage_4.u2) 
    annotation(Line(points = {{-388, 202}, {-637, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_4.y, fopid_fractional_integral_x_stage_5.u1) 
    annotation(Line(points = {{-637, 202}, {-597, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_04.y, fopid_fractional_integral_x_stage_5.u2) 
    annotation(Line(points = {{-346, 202}, {-569, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_5.y, fopid_fractional_integral_x_stage_6.u1) 
    annotation(Line(points = {{-569, 202}, {-529, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_05.y, fopid_fractional_integral_x_stage_6.u2) 
    annotation(Line(points = {{-304, 202}, {-501, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_6.y, fopid_fractional_integral_x_stage_7.u1) 
    annotation(Line(points = {{-501, 202}, {-461, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_06.y, fopid_fractional_integral_x_stage_7.u2) 
    annotation(Line(points = {{-262, 202}, {-433, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_7.y, fopid_fractional_integral_x_stage_8.u1) 
    annotation(Line(points = {{-433, 202}, {-393, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_07.y, fopid_fractional_integral_x_stage_8.u2) 
    annotation(Line(points = {{-220, 202}, {-365, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_8.y, fopid_fractional_integral_x_stage_9.u1) 
    annotation(Line(points = {{-365, 202}, {-325, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_08.y, fopid_fractional_integral_x_stage_9.u2) 
    annotation(Line(points = {{-178, 202}, {-297, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_9.y, fopid_fractional_integral_x_stage_10.u1) 
    annotation(Line(points = {{-297, 202}, {-257, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_09.y, fopid_fractional_integral_x_stage_10.u2) 
    annotation(Line(points = {{-136, 202}, {-229, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_10.y, fopid_fractional_integral_x_stage_11.u1) 
    annotation(Line(points = {{-229, 202}, {-189, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_10.y, fopid_fractional_integral_x_stage_11.u2) 
    annotation(Line(points = {{-94, 202}, {-161, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_11.y, fopid_fractional_integral_x_stage_12.u1) 
    annotation(Line(points = {{-161, 202}, {-121, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_11.y, fopid_fractional_integral_x_stage_12.u2) 
    annotation(Line(points = {{-52, 202}, {-93, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_12.y, fopid_fractional_integral_x_stage_13.u1) 
    annotation(Line(points = {{-93, 202}, {-53, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_12.y, fopid_fractional_integral_x_stage_13.u2) 
    annotation(Line(points = {{-10, 202}, {-25, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_13.y, fopid_fractional_integral_x_stage_14.u1) 
    annotation(Line(points = {{-25, 202}, {15, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_13.y, fopid_fractional_integral_x_stage_14.u2) 
    annotation(Line(points = {{32, 202}, {43, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_14.y, fopid_fractional_integral_x_stage_15.u1) 
    annotation(Line(points = {{43, 202}, {83, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_14.y, fopid_fractional_integral_x_stage_15.u2) 
    annotation(Line(points = {{102, 202}, {83, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x_stage_15.y, fopid_fractional_integral_x.u1) 
    annotation(Line(points = {{111, 202}, {151, 202}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_x_15.y, fopid_fractional_integral_x.u2) 
    annotation(Line(points = {{144, 202}, {151, 202}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_00.y, fopid_fractional_derivative_x_stage_2.u1) 
    annotation(Line(points = {{-514, 158}, {-773, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_01.y, fopid_fractional_derivative_x_stage_2.u2) 
    annotation(Line(points = {{-472, 158}, {-773, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_2.y, fopid_fractional_derivative_x_stage_3.u1) 
    annotation(Line(points = {{-773, 158}, {-733, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_02.y, fopid_fractional_derivative_x_stage_3.u2) 
    annotation(Line(points = {{-430, 158}, {-705, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_3.y, fopid_fractional_derivative_x_stage_4.u1) 
    annotation(Line(points = {{-705, 158}, {-665, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_03.y, fopid_fractional_derivative_x_stage_4.u2) 
    annotation(Line(points = {{-388, 158}, {-637, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_4.y, fopid_fractional_derivative_x_stage_5.u1) 
    annotation(Line(points = {{-637, 158}, {-597, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_04.y, fopid_fractional_derivative_x_stage_5.u2) 
    annotation(Line(points = {{-346, 158}, {-569, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_5.y, fopid_fractional_derivative_x_stage_6.u1) 
    annotation(Line(points = {{-569, 158}, {-529, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_05.y, fopid_fractional_derivative_x_stage_6.u2) 
    annotation(Line(points = {{-304, 158}, {-501, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_6.y, fopid_fractional_derivative_x_stage_7.u1) 
    annotation(Line(points = {{-501, 158}, {-461, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_06.y, fopid_fractional_derivative_x_stage_7.u2) 
    annotation(Line(points = {{-262, 158}, {-433, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_7.y, fopid_fractional_derivative_x_stage_8.u1) 
    annotation(Line(points = {{-433, 158}, {-393, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_07.y, fopid_fractional_derivative_x_stage_8.u2) 
    annotation(Line(points = {{-220, 158}, {-365, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_8.y, fopid_fractional_derivative_x_stage_9.u1) 
    annotation(Line(points = {{-365, 158}, {-325, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_08.y, fopid_fractional_derivative_x_stage_9.u2) 
    annotation(Line(points = {{-178, 158}, {-297, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_9.y, fopid_fractional_derivative_x_stage_10.u1) 
    annotation(Line(points = {{-297, 158}, {-257, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_09.y, fopid_fractional_derivative_x_stage_10.u2) 
    annotation(Line(points = {{-136, 158}, {-229, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_10.y, fopid_fractional_derivative_x_stage_11.u1) 
    annotation(Line(points = {{-229, 158}, {-189, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_10.y, fopid_fractional_derivative_x_stage_11.u2) 
    annotation(Line(points = {{-94, 158}, {-161, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_11.y, fopid_fractional_derivative_x_stage_12.u1) 
    annotation(Line(points = {{-161, 158}, {-121, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_11.y, fopid_fractional_derivative_x_stage_12.u2) 
    annotation(Line(points = {{-52, 158}, {-93, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_12.y, fopid_fractional_derivative_x_stage_13.u1) 
    annotation(Line(points = {{-93, 158}, {-53, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_12.y, fopid_fractional_derivative_x_stage_13.u2) 
    annotation(Line(points = {{-10, 158}, {-25, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_13.y, fopid_fractional_derivative_x_stage_14.u1) 
    annotation(Line(points = {{-25, 158}, {15, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_13.y, fopid_fractional_derivative_x_stage_14.u2) 
    annotation(Line(points = {{32, 158}, {43, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_14.y, fopid_fractional_derivative_x_stage_15.u1) 
    annotation(Line(points = {{43, 158}, {83, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_14.y, fopid_fractional_derivative_x_stage_15.u2) 
    annotation(Line(points = {{102, 158}, {83, 158}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x_stage_15.y, fopid_fractional_derivative_x.u1) 
    annotation(Line(points = {{111, 158}, {151, 158}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_x_15.y, fopid_fractional_derivative_x.u2) 
    annotation(Line(points = {{144, 158}, {151, 158}}, color = {0, 0, 127}));
  connect(fopid_position_error_x.y, fopid_proportional_x.u) 
    annotation(Line(points = {{-576, 260}, {-370, 260}, {-370, 300}, {-164, 300}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x.y, fopid_integral_feedback_x.u) 
    annotation(Line(points = {{179, 202}, {251, 202}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x.y, fopid_derivative_feedback_x.u) 
    annotation(Line(points = {{179, 158}, {251, 158}}, color = {0, 0, 127}));
  connect(reference_acceleration_x, fopid_desired_acceleration_pre_gravity_x_stage_2.u1) 
    annotation(Line(points = {{-666, -98}, {-220.5, -98}, {-220.5, 260}, {225, 260}}, color = {0, 0, 127}));
  connect(fopid_proportional_x.y, fopid_desired_acceleration_pre_gravity_x_stage_2.u2) 
    annotation(Line(points = {{-136, 300}, {44.5, 300}, {44.5, 260}, {225, 260}}, color = {0, 0, 127}));
  connect(fopid_desired_acceleration_pre_gravity_x_stage_2.y, fopid_desired_acceleration_pre_gravity_x_stage_3.u1) 
    annotation(Line(points = {{253, 260}, {293, 260}}, color = {0, 0, 127}));
  connect(fopid_integral_feedback_x.y, fopid_desired_acceleration_pre_gravity_x_stage_3.u2) 
    annotation(Line(points = {{265, 213}, {265, 231}, {307, 231}, {307, 249}}, color = {0, 0, 127}));
  connect(fopid_desired_acceleration_pre_gravity_x_stage_3.y, fopid_desired_acceleration_pre_gravity_x.u1) 
    annotation(Line(points = {{321, 260}, {361, 260}}, color = {0, 0, 127}));
  connect(fopid_derivative_feedback_x.y, fopid_desired_acceleration_pre_gravity_x.u2) 
    annotation(Line(points = {{279, 158}, {320, 158}, {320, 260}, {361, 260}}, color = {0, 0, 127}));
  connect(fopid_desired_acceleration_pre_gravity_x.y, desired_acceleration_x.u) 
    annotation(Line(points = {{361, 260}, {154, 260}}, color = {0, 0, 127}));
  connect(reference_position_y, fopid_position_error_y.u1) 
    annotation(Line(points = {{-666, 100}, {-635, 100}, {-635, 25}, {-604, 25}}, color = {0, 0, 127}));
  connect(position_y, fopid_position_error_y.u2) 
    annotation(Line(points = {{-680, 313}, {-680, 174.5}, {-590, 174.5}, {-590, 36}}, color = {0, 0, 127}));
  connect(fopid_position_error_y.y, fopid_history_y_01.u1) 
    annotation(Line(points = {{-576, 25}, {-472, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_01.y, fopid_history_y_02.u1) 
    annotation(Line(points = {{-444, 25}, {-430, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_02.y, fopid_history_y_03.u1) 
    annotation(Line(points = {{-402, 25}, {-388, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_03.y, fopid_history_y_04.u1) 
    annotation(Line(points = {{-360, 25}, {-346, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_04.y, fopid_history_y_05.u1) 
    annotation(Line(points = {{-318, 25}, {-304, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_05.y, fopid_history_y_06.u1) 
    annotation(Line(points = {{-276, 25}, {-262, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_06.y, fopid_history_y_07.u1) 
    annotation(Line(points = {{-234, 25}, {-220, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_07.y, fopid_history_y_08.u1) 
    annotation(Line(points = {{-192, 25}, {-178, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_08.y, fopid_history_y_09.u1) 
    annotation(Line(points = {{-150, 25}, {-136, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_09.y, fopid_history_y_10.u1) 
    annotation(Line(points = {{-108, 25}, {-94, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_10.y, fopid_history_y_11.u1) 
    annotation(Line(points = {{-66, 25}, {-52, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_11.y, fopid_history_y_12.u1) 
    annotation(Line(points = {{-24, 25}, {-10, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_12.y, fopid_history_y_13.u1) 
    annotation(Line(points = {{18, 25}, {32, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_13.y, fopid_history_y_14.u1) 
    annotation(Line(points = {{60, 25}, {74, 25}}, color = {0, 0, 127}));
  connect(fopid_history_y_14.y, fopid_history_y_15.u1) 
    annotation(Line(points = {{102, 25}, {116, 25}}, color = {0, 0, 127}));
  connect(fopid_position_error_y.y, fopid_integral_weight_y_00.u) 
    annotation(Line(points = {{-576, 25}, {-545, 25}, {-545, -33}, {-514, -33}}, color = {0, 0, 127}));
  connect(fopid_history_y_01.y, fopid_integral_weight_y_01.u) 
    annotation(Line(points = {{-458, 14}, {-458, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_02.y, fopid_integral_weight_y_02.u) 
    annotation(Line(points = {{-416, 14}, {-416, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_03.y, fopid_integral_weight_y_03.u) 
    annotation(Line(points = {{-374, 14}, {-374, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_04.y, fopid_integral_weight_y_04.u) 
    annotation(Line(points = {{-332, 14}, {-332, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_05.y, fopid_integral_weight_y_05.u) 
    annotation(Line(points = {{-290, 14}, {-290, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_06.y, fopid_integral_weight_y_06.u) 
    annotation(Line(points = {{-248, 14}, {-248, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_07.y, fopid_integral_weight_y_07.u) 
    annotation(Line(points = {{-206, 14}, {-206, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_08.y, fopid_integral_weight_y_08.u) 
    annotation(Line(points = {{-164, 14}, {-164, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_09.y, fopid_integral_weight_y_09.u) 
    annotation(Line(points = {{-122, 14}, {-122, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_10.y, fopid_integral_weight_y_10.u) 
    annotation(Line(points = {{-80, 14}, {-80, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_11.y, fopid_integral_weight_y_11.u) 
    annotation(Line(points = {{-38, 14}, {-38, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_12.y, fopid_integral_weight_y_12.u) 
    annotation(Line(points = {{4, 14}, {4, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_13.y, fopid_integral_weight_y_13.u) 
    annotation(Line(points = {{46, 14}, {46, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_14.y, fopid_integral_weight_y_14.u) 
    annotation(Line(points = {{88, 14}, {88, -22}}, color = {0, 0, 127}));
  connect(fopid_history_y_15.y, fopid_integral_weight_y_15.u) 
    annotation(Line(points = {{130, 14}, {130, -22}}, color = {0, 0, 127}));
  connect(fopid_position_error_y.y, fopid_derivative_weight_y_00.u) 
    annotation(Line(points = {{-590, 14}, {-590, -26}, {-500, -26}, {-500, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_01.y, fopid_derivative_weight_y_01.u) 
    annotation(Line(points = {{-458, 14}, {-458, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_02.y, fopid_derivative_weight_y_02.u) 
    annotation(Line(points = {{-416, 14}, {-416, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_03.y, fopid_derivative_weight_y_03.u) 
    annotation(Line(points = {{-374, 14}, {-374, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_04.y, fopid_derivative_weight_y_04.u) 
    annotation(Line(points = {{-332, 14}, {-332, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_05.y, fopid_derivative_weight_y_05.u) 
    annotation(Line(points = {{-290, 14}, {-290, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_06.y, fopid_derivative_weight_y_06.u) 
    annotation(Line(points = {{-248, 14}, {-248, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_07.y, fopid_derivative_weight_y_07.u) 
    annotation(Line(points = {{-206, 14}, {-206, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_08.y, fopid_derivative_weight_y_08.u) 
    annotation(Line(points = {{-164, 14}, {-164, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_09.y, fopid_derivative_weight_y_09.u) 
    annotation(Line(points = {{-122, 14}, {-122, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_10.y, fopid_derivative_weight_y_10.u) 
    annotation(Line(points = {{-80, 14}, {-80, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_11.y, fopid_derivative_weight_y_11.u) 
    annotation(Line(points = {{-38, 14}, {-38, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_12.y, fopid_derivative_weight_y_12.u) 
    annotation(Line(points = {{4, 14}, {4, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_13.y, fopid_derivative_weight_y_13.u) 
    annotation(Line(points = {{46, 14}, {46, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_14.y, fopid_derivative_weight_y_14.u) 
    annotation(Line(points = {{88, 14}, {88, -66}}, color = {0, 0, 127}));
  connect(fopid_history_y_15.y, fopid_derivative_weight_y_15.u) 
    annotation(Line(points = {{130, 14}, {130, -66}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_00.y, fopid_fractional_integral_y_stage_2.u1) 
    annotation(Line(points = {{-514, -33}, {-773, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_01.y, fopid_fractional_integral_y_stage_2.u2) 
    annotation(Line(points = {{-472, -33}, {-773, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_2.y, fopid_fractional_integral_y_stage_3.u1) 
    annotation(Line(points = {{-773, -33}, {-733, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_02.y, fopid_fractional_integral_y_stage_3.u2) 
    annotation(Line(points = {{-430, -33}, {-705, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_3.y, fopid_fractional_integral_y_stage_4.u1) 
    annotation(Line(points = {{-705, -33}, {-665, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_03.y, fopid_fractional_integral_y_stage_4.u2) 
    annotation(Line(points = {{-388, -33}, {-637, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_4.y, fopid_fractional_integral_y_stage_5.u1) 
    annotation(Line(points = {{-637, -33}, {-597, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_04.y, fopid_fractional_integral_y_stage_5.u2) 
    annotation(Line(points = {{-346, -33}, {-569, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_5.y, fopid_fractional_integral_y_stage_6.u1) 
    annotation(Line(points = {{-569, -33}, {-529, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_05.y, fopid_fractional_integral_y_stage_6.u2) 
    annotation(Line(points = {{-304, -33}, {-501, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_6.y, fopid_fractional_integral_y_stage_7.u1) 
    annotation(Line(points = {{-501, -33}, {-461, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_06.y, fopid_fractional_integral_y_stage_7.u2) 
    annotation(Line(points = {{-262, -33}, {-433, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_7.y, fopid_fractional_integral_y_stage_8.u1) 
    annotation(Line(points = {{-433, -33}, {-393, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_07.y, fopid_fractional_integral_y_stage_8.u2) 
    annotation(Line(points = {{-220, -33}, {-365, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_8.y, fopid_fractional_integral_y_stage_9.u1) 
    annotation(Line(points = {{-365, -33}, {-325, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_08.y, fopid_fractional_integral_y_stage_9.u2) 
    annotation(Line(points = {{-178, -33}, {-297, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_9.y, fopid_fractional_integral_y_stage_10.u1) 
    annotation(Line(points = {{-297, -33}, {-257, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_09.y, fopid_fractional_integral_y_stage_10.u2) 
    annotation(Line(points = {{-136, -33}, {-229, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_10.y, fopid_fractional_integral_y_stage_11.u1) 
    annotation(Line(points = {{-229, -33}, {-189, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_10.y, fopid_fractional_integral_y_stage_11.u2) 
    annotation(Line(points = {{-94, -33}, {-161, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_11.y, fopid_fractional_integral_y_stage_12.u1) 
    annotation(Line(points = {{-161, -33}, {-121, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_11.y, fopid_fractional_integral_y_stage_12.u2) 
    annotation(Line(points = {{-52, -33}, {-93, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_12.y, fopid_fractional_integral_y_stage_13.u1) 
    annotation(Line(points = {{-93, -33}, {-53, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_12.y, fopid_fractional_integral_y_stage_13.u2) 
    annotation(Line(points = {{-10, -33}, {-25, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_13.y, fopid_fractional_integral_y_stage_14.u1) 
    annotation(Line(points = {{-25, -33}, {15, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_13.y, fopid_fractional_integral_y_stage_14.u2) 
    annotation(Line(points = {{32, -33}, {43, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_14.y, fopid_fractional_integral_y_stage_15.u1) 
    annotation(Line(points = {{43, -33}, {83, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_14.y, fopid_fractional_integral_y_stage_15.u2) 
    annotation(Line(points = {{102, -33}, {83, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y_stage_15.y, fopid_fractional_integral_y.u1) 
    annotation(Line(points = {{111, -33}, {151, -33}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_y_15.y, fopid_fractional_integral_y.u2) 
    annotation(Line(points = {{144, -33}, {151, -33}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_00.y, fopid_fractional_derivative_y_stage_2.u1) 
    annotation(Line(points = {{-514, -77}, {-773, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_01.y, fopid_fractional_derivative_y_stage_2.u2) 
    annotation(Line(points = {{-472, -77}, {-773, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_2.y, fopid_fractional_derivative_y_stage_3.u1) 
    annotation(Line(points = {{-773, -77}, {-733, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_02.y, fopid_fractional_derivative_y_stage_3.u2) 
    annotation(Line(points = {{-430, -77}, {-705, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_3.y, fopid_fractional_derivative_y_stage_4.u1) 
    annotation(Line(points = {{-705, -77}, {-665, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_03.y, fopid_fractional_derivative_y_stage_4.u2) 
    annotation(Line(points = {{-388, -77}, {-637, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_4.y, fopid_fractional_derivative_y_stage_5.u1) 
    annotation(Line(points = {{-637, -77}, {-597, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_04.y, fopid_fractional_derivative_y_stage_5.u2) 
    annotation(Line(points = {{-346, -77}, {-569, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_5.y, fopid_fractional_derivative_y_stage_6.u1) 
    annotation(Line(points = {{-569, -77}, {-529, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_05.y, fopid_fractional_derivative_y_stage_6.u2) 
    annotation(Line(points = {{-304, -77}, {-501, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_6.y, fopid_fractional_derivative_y_stage_7.u1) 
    annotation(Line(points = {{-501, -77}, {-461, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_06.y, fopid_fractional_derivative_y_stage_7.u2) 
    annotation(Line(points = {{-262, -77}, {-433, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_7.y, fopid_fractional_derivative_y_stage_8.u1) 
    annotation(Line(points = {{-433, -77}, {-393, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_07.y, fopid_fractional_derivative_y_stage_8.u2) 
    annotation(Line(points = {{-220, -77}, {-365, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_8.y, fopid_fractional_derivative_y_stage_9.u1) 
    annotation(Line(points = {{-365, -77}, {-325, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_08.y, fopid_fractional_derivative_y_stage_9.u2) 
    annotation(Line(points = {{-178, -77}, {-297, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_9.y, fopid_fractional_derivative_y_stage_10.u1) 
    annotation(Line(points = {{-297, -77}, {-257, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_09.y, fopid_fractional_derivative_y_stage_10.u2) 
    annotation(Line(points = {{-136, -77}, {-229, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_10.y, fopid_fractional_derivative_y_stage_11.u1) 
    annotation(Line(points = {{-229, -77}, {-189, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_10.y, fopid_fractional_derivative_y_stage_11.u2) 
    annotation(Line(points = {{-94, -77}, {-161, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_11.y, fopid_fractional_derivative_y_stage_12.u1) 
    annotation(Line(points = {{-161, -77}, {-121, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_11.y, fopid_fractional_derivative_y_stage_12.u2) 
    annotation(Line(points = {{-52, -77}, {-93, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_12.y, fopid_fractional_derivative_y_stage_13.u1) 
    annotation(Line(points = {{-93, -77}, {-53, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_12.y, fopid_fractional_derivative_y_stage_13.u2) 
    annotation(Line(points = {{-10, -77}, {-25, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_13.y, fopid_fractional_derivative_y_stage_14.u1) 
    annotation(Line(points = {{-25, -77}, {15, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_13.y, fopid_fractional_derivative_y_stage_14.u2) 
    annotation(Line(points = {{32, -77}, {43, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_14.y, fopid_fractional_derivative_y_stage_15.u1) 
    annotation(Line(points = {{43, -77}, {83, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_14.y, fopid_fractional_derivative_y_stage_15.u2) 
    annotation(Line(points = {{102, -77}, {83, -77}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y_stage_15.y, fopid_fractional_derivative_y.u1) 
    annotation(Line(points = {{111, -77}, {151, -77}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_y_15.y, fopid_fractional_derivative_y.u2) 
    annotation(Line(points = {{144, -77}, {151, -77}}, color = {0, 0, 127}));
  connect(fopid_position_error_y.y, fopid_proportional_y.u) 
    annotation(Line(points = {{-576, 25}, {-370, 25}, {-370, 65}, {-164, 65}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y.y, fopid_integral_feedback_y.u) 
    annotation(Line(points = {{179, -33}, {251, -33}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y.y, fopid_derivative_feedback_y.u) 
    annotation(Line(points = {{179, -77}, {251, -77}}, color = {0, 0, 127}));
  connect(reference_acceleration_y, fopid_desired_acceleration_pre_gravity_y_stage_2.u1) 
    annotation(Line(points = {{-666, -124}, {-220.5, -124}, {-220.5, 25}, {225, 25}}, color = {0, 0, 127}));
  connect(fopid_proportional_y.y, fopid_desired_acceleration_pre_gravity_y_stage_2.u2) 
    annotation(Line(points = {{-136, 65}, {44.5, 65}, {44.5, 25}, {225, 25}}, color = {0, 0, 127}));
  connect(fopid_desired_acceleration_pre_gravity_y_stage_2.y, fopid_desired_acceleration_pre_gravity_y_stage_3.u1) 
    annotation(Line(points = {{253, 25}, {293, 25}}, color = {0, 0, 127}));
  connect(fopid_integral_feedback_y.y, fopid_desired_acceleration_pre_gravity_y_stage_3.u2) 
    annotation(Line(points = {{265, -22}, {265, -4}, {307, -4}, {307, 14}}, color = {0, 0, 127}));
  connect(fopid_desired_acceleration_pre_gravity_y_stage_3.y, fopid_desired_acceleration_pre_gravity_y.u1) 
    annotation(Line(points = {{321, 25}, {361, 25}}, color = {0, 0, 127}));
  connect(fopid_derivative_feedback_y.y, fopid_desired_acceleration_pre_gravity_y.u2) 
    annotation(Line(points = {{279, -77}, {320, -77}, {320, 25}, {361, 25}}, color = {0, 0, 127}));
  connect(fopid_desired_acceleration_pre_gravity_y.y, desired_acceleration_y.u) 
    annotation(Line(points = {{361, 25}, {154, 25}}, color = {0, 0, 127}));
  connect(reference_position_z, fopid_position_error_z.u1) 
    annotation(Line(points = {{-680, 63}, {-680, -68}, {-590, -68}, {-590, -199}}, color = {0, 0, 127}));
  connect(position_z, fopid_position_error_z.u2) 
    annotation(Line(points = {{-680, 287}, {-680, 44}, {-590, 44}, {-590, -199}}, color = {0, 0, 127}));
  connect(fopid_position_error_z.y, fopid_history_z_01.u1) 
    annotation(Line(points = {{-576, -210}, {-472, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_01.y, fopid_history_z_02.u1) 
    annotation(Line(points = {{-444, -210}, {-430, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_02.y, fopid_history_z_03.u1) 
    annotation(Line(points = {{-402, -210}, {-388, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_03.y, fopid_history_z_04.u1) 
    annotation(Line(points = {{-360, -210}, {-346, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_04.y, fopid_history_z_05.u1) 
    annotation(Line(points = {{-318, -210}, {-304, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_05.y, fopid_history_z_06.u1) 
    annotation(Line(points = {{-276, -210}, {-262, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_06.y, fopid_history_z_07.u1) 
    annotation(Line(points = {{-234, -210}, {-220, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_07.y, fopid_history_z_08.u1) 
    annotation(Line(points = {{-192, -210}, {-178, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_08.y, fopid_history_z_09.u1) 
    annotation(Line(points = {{-150, -210}, {-136, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_09.y, fopid_history_z_10.u1) 
    annotation(Line(points = {{-108, -210}, {-94, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_10.y, fopid_history_z_11.u1) 
    annotation(Line(points = {{-66, -210}, {-52, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_11.y, fopid_history_z_12.u1) 
    annotation(Line(points = {{-24, -210}, {-10, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_12.y, fopid_history_z_13.u1) 
    annotation(Line(points = {{18, -210}, {32, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_13.y, fopid_history_z_14.u1) 
    annotation(Line(points = {{60, -210}, {74, -210}}, color = {0, 0, 127}));
  connect(fopid_history_z_14.y, fopid_history_z_15.u1) 
    annotation(Line(points = {{102, -210}, {116, -210}}, color = {0, 0, 127}));
  connect(fopid_position_error_z.y, fopid_integral_weight_z_00.u) 
    annotation(Line(points = {{-576, -210}, {-545, -210}, {-545, -268}, {-514, -268}}, color = {0, 0, 127}));
  connect(fopid_history_z_01.y, fopid_integral_weight_z_01.u) 
    annotation(Line(points = {{-458, -221}, {-458, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_02.y, fopid_integral_weight_z_02.u) 
    annotation(Line(points = {{-416, -221}, {-416, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_03.y, fopid_integral_weight_z_03.u) 
    annotation(Line(points = {{-374, -221}, {-374, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_04.y, fopid_integral_weight_z_04.u) 
    annotation(Line(points = {{-332, -221}, {-332, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_05.y, fopid_integral_weight_z_05.u) 
    annotation(Line(points = {{-290, -221}, {-290, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_06.y, fopid_integral_weight_z_06.u) 
    annotation(Line(points = {{-248, -221}, {-248, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_07.y, fopid_integral_weight_z_07.u) 
    annotation(Line(points = {{-206, -221}, {-206, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_08.y, fopid_integral_weight_z_08.u) 
    annotation(Line(points = {{-164, -221}, {-164, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_09.y, fopid_integral_weight_z_09.u) 
    annotation(Line(points = {{-122, -221}, {-122, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_10.y, fopid_integral_weight_z_10.u) 
    annotation(Line(points = {{-80, -221}, {-80, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_11.y, fopid_integral_weight_z_11.u) 
    annotation(Line(points = {{-38, -221}, {-38, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_12.y, fopid_integral_weight_z_12.u) 
    annotation(Line(points = {{4, -221}, {4, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_13.y, fopid_integral_weight_z_13.u) 
    annotation(Line(points = {{46, -221}, {46, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_14.y, fopid_integral_weight_z_14.u) 
    annotation(Line(points = {{88, -221}, {88, -257}}, color = {0, 0, 127}));
  connect(fopid_history_z_15.y, fopid_integral_weight_z_15.u) 
    annotation(Line(points = {{130, -221}, {130, -257}}, color = {0, 0, 127}));
  connect(fopid_position_error_z.y, fopid_derivative_weight_z_00.u) 
    annotation(Line(points = {{-590, -221}, {-590, -261}, {-500, -261}, {-500, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_01.y, fopid_derivative_weight_z_01.u) 
    annotation(Line(points = {{-458, -221}, {-458, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_02.y, fopid_derivative_weight_z_02.u) 
    annotation(Line(points = {{-416, -221}, {-416, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_03.y, fopid_derivative_weight_z_03.u) 
    annotation(Line(points = {{-374, -221}, {-374, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_04.y, fopid_derivative_weight_z_04.u) 
    annotation(Line(points = {{-332, -221}, {-332, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_05.y, fopid_derivative_weight_z_05.u) 
    annotation(Line(points = {{-290, -221}, {-290, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_06.y, fopid_derivative_weight_z_06.u) 
    annotation(Line(points = {{-248, -221}, {-248, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_07.y, fopid_derivative_weight_z_07.u) 
    annotation(Line(points = {{-206, -221}, {-206, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_08.y, fopid_derivative_weight_z_08.u) 
    annotation(Line(points = {{-164, -221}, {-164, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_09.y, fopid_derivative_weight_z_09.u) 
    annotation(Line(points = {{-122, -221}, {-122, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_10.y, fopid_derivative_weight_z_10.u) 
    annotation(Line(points = {{-80, -221}, {-80, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_11.y, fopid_derivative_weight_z_11.u) 
    annotation(Line(points = {{-38, -221}, {-38, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_12.y, fopid_derivative_weight_z_12.u) 
    annotation(Line(points = {{4, -221}, {4, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_13.y, fopid_derivative_weight_z_13.u) 
    annotation(Line(points = {{46, -221}, {46, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_14.y, fopid_derivative_weight_z_14.u) 
    annotation(Line(points = {{88, -221}, {88, -301}}, color = {0, 0, 127}));
  connect(fopid_history_z_15.y, fopid_derivative_weight_z_15.u) 
    annotation(Line(points = {{130, -221}, {130, -301}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_00.y, fopid_fractional_integral_z_stage_2.u1) 
    annotation(Line(points = {{-514, -268}, {-773, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_01.y, fopid_fractional_integral_z_stage_2.u2) 
    annotation(Line(points = {{-472, -268}, {-773, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_2.y, fopid_fractional_integral_z_stage_3.u1) 
    annotation(Line(points = {{-773, -268}, {-733, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_02.y, fopid_fractional_integral_z_stage_3.u2) 
    annotation(Line(points = {{-430, -268}, {-705, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_3.y, fopid_fractional_integral_z_stage_4.u1) 
    annotation(Line(points = {{-705, -268}, {-665, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_03.y, fopid_fractional_integral_z_stage_4.u2) 
    annotation(Line(points = {{-388, -268}, {-637, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_4.y, fopid_fractional_integral_z_stage_5.u1) 
    annotation(Line(points = {{-637, -268}, {-597, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_04.y, fopid_fractional_integral_z_stage_5.u2) 
    annotation(Line(points = {{-346, -268}, {-569, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_5.y, fopid_fractional_integral_z_stage_6.u1) 
    annotation(Line(points = {{-569, -268}, {-529, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_05.y, fopid_fractional_integral_z_stage_6.u2) 
    annotation(Line(points = {{-304, -268}, {-501, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_6.y, fopid_fractional_integral_z_stage_7.u1) 
    annotation(Line(points = {{-501, -268}, {-461, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_06.y, fopid_fractional_integral_z_stage_7.u2) 
    annotation(Line(points = {{-262, -268}, {-433, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_7.y, fopid_fractional_integral_z_stage_8.u1) 
    annotation(Line(points = {{-433, -268}, {-393, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_07.y, fopid_fractional_integral_z_stage_8.u2) 
    annotation(Line(points = {{-220, -268}, {-365, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_8.y, fopid_fractional_integral_z_stage_9.u1) 
    annotation(Line(points = {{-365, -268}, {-325, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_08.y, fopid_fractional_integral_z_stage_9.u2) 
    annotation(Line(points = {{-178, -268}, {-297, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_9.y, fopid_fractional_integral_z_stage_10.u1) 
    annotation(Line(points = {{-297, -268}, {-257, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_09.y, fopid_fractional_integral_z_stage_10.u2) 
    annotation(Line(points = {{-136, -268}, {-229, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_10.y, fopid_fractional_integral_z_stage_11.u1) 
    annotation(Line(points = {{-229, -268}, {-189, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_10.y, fopid_fractional_integral_z_stage_11.u2) 
    annotation(Line(points = {{-94, -268}, {-161, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_11.y, fopid_fractional_integral_z_stage_12.u1) 
    annotation(Line(points = {{-161, -268}, {-121, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_11.y, fopid_fractional_integral_z_stage_12.u2) 
    annotation(Line(points = {{-52, -268}, {-93, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_12.y, fopid_fractional_integral_z_stage_13.u1) 
    annotation(Line(points = {{-93, -268}, {-53, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_12.y, fopid_fractional_integral_z_stage_13.u2) 
    annotation(Line(points = {{-10, -268}, {-25, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_13.y, fopid_fractional_integral_z_stage_14.u1) 
    annotation(Line(points = {{-25, -268}, {15, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_13.y, fopid_fractional_integral_z_stage_14.u2) 
    annotation(Line(points = {{32, -268}, {43, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_14.y, fopid_fractional_integral_z_stage_15.u1) 
    annotation(Line(points = {{43, -268}, {83, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_14.y, fopid_fractional_integral_z_stage_15.u2) 
    annotation(Line(points = {{102, -268}, {83, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z_stage_15.y, fopid_fractional_integral_z.u1) 
    annotation(Line(points = {{111, -268}, {151, -268}}, color = {0, 0, 127}));
  connect(fopid_integral_weight_z_15.y, fopid_fractional_integral_z.u2) 
    annotation(Line(points = {{144, -268}, {151, -268}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_00.y, fopid_fractional_derivative_z_stage_2.u1) 
    annotation(Line(points = {{-514, -312}, {-773, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_01.y, fopid_fractional_derivative_z_stage_2.u2) 
    annotation(Line(points = {{-472, -312}, {-773, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_2.y, fopid_fractional_derivative_z_stage_3.u1) 
    annotation(Line(points = {{-773, -312}, {-733, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_02.y, fopid_fractional_derivative_z_stage_3.u2) 
    annotation(Line(points = {{-430, -312}, {-705, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_3.y, fopid_fractional_derivative_z_stage_4.u1) 
    annotation(Line(points = {{-705, -312}, {-665, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_03.y, fopid_fractional_derivative_z_stage_4.u2) 
    annotation(Line(points = {{-388, -312}, {-637, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_4.y, fopid_fractional_derivative_z_stage_5.u1) 
    annotation(Line(points = {{-637, -312}, {-597, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_04.y, fopid_fractional_derivative_z_stage_5.u2) 
    annotation(Line(points = {{-346, -312}, {-569, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_5.y, fopid_fractional_derivative_z_stage_6.u1) 
    annotation(Line(points = {{-569, -312}, {-529, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_05.y, fopid_fractional_derivative_z_stage_6.u2) 
    annotation(Line(points = {{-304, -312}, {-501, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_6.y, fopid_fractional_derivative_z_stage_7.u1) 
    annotation(Line(points = {{-501, -312}, {-461, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_06.y, fopid_fractional_derivative_z_stage_7.u2) 
    annotation(Line(points = {{-262, -312}, {-433, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_7.y, fopid_fractional_derivative_z_stage_8.u1) 
    annotation(Line(points = {{-433, -312}, {-393, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_07.y, fopid_fractional_derivative_z_stage_8.u2) 
    annotation(Line(points = {{-220, -312}, {-365, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_8.y, fopid_fractional_derivative_z_stage_9.u1) 
    annotation(Line(points = {{-365, -312}, {-325, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_08.y, fopid_fractional_derivative_z_stage_9.u2) 
    annotation(Line(points = {{-178, -312}, {-297, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_9.y, fopid_fractional_derivative_z_stage_10.u1) 
    annotation(Line(points = {{-297, -312}, {-257, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_09.y, fopid_fractional_derivative_z_stage_10.u2) 
    annotation(Line(points = {{-136, -312}, {-229, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_10.y, fopid_fractional_derivative_z_stage_11.u1) 
    annotation(Line(points = {{-229, -312}, {-189, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_10.y, fopid_fractional_derivative_z_stage_11.u2) 
    annotation(Line(points = {{-94, -312}, {-161, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_11.y, fopid_fractional_derivative_z_stage_12.u1) 
    annotation(Line(points = {{-161, -312}, {-121, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_11.y, fopid_fractional_derivative_z_stage_12.u2) 
    annotation(Line(points = {{-52, -312}, {-93, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_12.y, fopid_fractional_derivative_z_stage_13.u1) 
    annotation(Line(points = {{-93, -312}, {-53, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_12.y, fopid_fractional_derivative_z_stage_13.u2) 
    annotation(Line(points = {{-10, -312}, {-25, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_13.y, fopid_fractional_derivative_z_stage_14.u1) 
    annotation(Line(points = {{-25, -312}, {15, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_13.y, fopid_fractional_derivative_z_stage_14.u2) 
    annotation(Line(points = {{32, -312}, {43, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_14.y, fopid_fractional_derivative_z_stage_15.u1) 
    annotation(Line(points = {{43, -312}, {83, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_14.y, fopid_fractional_derivative_z_stage_15.u2) 
    annotation(Line(points = {{102, -312}, {83, -312}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z_stage_15.y, fopid_fractional_derivative_z.u1) 
    annotation(Line(points = {{111, -312}, {151, -312}}, color = {0, 0, 127}));
  connect(fopid_derivative_weight_z_15.y, fopid_fractional_derivative_z.u2) 
    annotation(Line(points = {{144, -312}, {151, -312}}, color = {0, 0, 127}));
  connect(fopid_position_error_z.y, fopid_proportional_z.u) 
    annotation(Line(points = {{-576, -210}, {-370, -210}, {-370, -170}, {-164, -170}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z.y, fopid_integral_feedback_z.u) 
    annotation(Line(points = {{179, -268}, {251, -268}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z.y, fopid_derivative_feedback_z.u) 
    annotation(Line(points = {{179, -312}, {251, -312}}, color = {0, 0, 127}));
  connect(reference_acceleration_z, fopid_desired_acceleration_pre_gravity_z_stage_2.u1) 
    annotation(Line(points = {{-666, -150}, {-220.5, -150}, {-220.5, -210}, {225, -210}}, color = {0, 0, 127}));
  connect(fopid_proportional_z.y, fopid_desired_acceleration_pre_gravity_z_stage_2.u2) 
    annotation(Line(points = {{-136, -170}, {44.5, -170}, {44.5, -210}, {225, -210}}, color = {0, 0, 127}));
  connect(fopid_desired_acceleration_pre_gravity_z_stage_2.y, fopid_desired_acceleration_pre_gravity_z_stage_3.u1) 
    annotation(Line(points = {{253, -210}, {293, -210}}, color = {0, 0, 127}));
  connect(fopid_integral_feedback_z.y, fopid_desired_acceleration_pre_gravity_z_stage_3.u2) 
    annotation(Line(points = {{265, -257}, {265, -239}, {307, -239}, {307, -221}}, color = {0, 0, 127}));
  connect(fopid_desired_acceleration_pre_gravity_z_stage_3.y, fopid_desired_acceleration_pre_gravity_z.u1) 
    annotation(Line(points = {{321, -210}, {361, -210}}, color = {0, 0, 127}));
  connect(fopid_derivative_feedback_z.y, fopid_desired_acceleration_pre_gravity_z.u2) 
    annotation(Line(points = {{279, -312}, {320, -312}, {320, -210}, {361, -210}}, color = {0, 0, 127}));
  connect(fopid_desired_acceleration_pre_gravity_z.y, desired_acceleration_z.u1) 
    annotation(Line(points = {{361, -210}, {154, -210}}, color = {0, 0, 127}));
  connect(gravity_compensation.y, desired_acceleration_z.u2) 
    annotation(Line(points = {{69, -138}, {97.5, -138}, {97.5, -210}, {126, -210}}, color = {0, 0, 127}));
  connect(desired_acceleration_y.y, roll_from_lateral_acceleration.u) 
    annotation(Line(points = {{154, 25}, {185, 25}, {185, 75}, {216, 75}}, color = {0, 0, 127}));
  connect(roll_from_lateral_acceleration.y, roll_tilt_limit.u) 
    annotation(Line(points = {{244, 75}, {306, 75}}, color = {0, 0, 127}));
  connect(desired_acceleration_x.y, pitch_from_lateral_acceleration.u) 
    annotation(Line(points = {{140, 249}, {140, 195}, {230, 195}, {230, 141}}, color = {0, 0, 127}));
  connect(pitch_from_lateral_acceleration.y, pitch_tilt_limit.u) 
    annotation(Line(points = {{244, 130}, {306, 130}}, color = {0, 0, 127}));
  connect(desired_acceleration_z.y, vertical_force_allocation.u) 
    annotation(Line(points = {{140, -199}, {140, -127.5}, {230, -127.5}, {230, -56}}, color = {0, 0, 127}));
  connect(vertical_force_allocation.y, collective_thrust_limit.u) 
    annotation(Line(points = {{244, -45}, {306, -45}}, color = {0, 0, 127}));
  connect(collective_thrust_limit.y, normalized_thrust_from_collective.u) 
    annotation(Line(points = {{334, -45}, {396, -45}}, color = {0, 0, 127}));
  connect(normalized_thrust_from_collective.y, normalized_thrust_limit.u) 
    annotation(Line(points = {{424, -45}, {486, -45}}, color = {0, 0, 127}));
  connect(fopid_position_error_x.y, enable_position_error_x.u1) 
    annotation(Line(points = {{-576, 260}, {-27.5, 260}, {-27.5, 345}, {521, 345}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 345}, {521, 345}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_x.u3) 
    annotation(Line(points = {{500, -299}, {500, 17.5}, {535, 17.5}, {535, 334}}, color = {0, 0, 127}));
  connect(enable_position_error_x.y, position_error_x_out) 
    annotation(Line(points = {{549, 345}, {681, 345}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_x.y, enable_fractional_integral_x.u1) 
    annotation(Line(points = {{179, 202}, {350, 202}, {350, 307}, {521, 307}}, color = {0, 0, 127}));
  connect(enable, enable_fractional_integral_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 307}, {521, 307}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_fractional_integral_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -1.5}, {535, -1.5}, {535, 296}}, color = {0, 0, 127}));
  connect(enable_fractional_integral_x.y, fractional_integral_x_out) 
    annotation(Line(points = {{549, 307}, {681, 307}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_x.y, enable_fractional_derivative_x.u1) 
    annotation(Line(points = {{179, 158}, {350, 158}, {350, 269}, {521, 269}}, color = {0, 0, 127}));
  connect(enable, enable_fractional_derivative_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 269}, {521, 269}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_fractional_derivative_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -20.5}, {535, -20.5}, {535, 258}}, color = {0, 0, 127}));
  connect(enable_fractional_derivative_x.y, fractional_derivative_x_out) 
    annotation(Line(points = {{549, 269}, {681, 269}}, color = {0, 0, 127}));
  connect(desired_acceleration_x.y, enable_desired_acceleration_x.u1) 
    annotation(Line(points = {{154, 260}, {337.5, 260}, {337.5, 231}, {521, 231}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 231}, {521, 231}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -39.5}, {535, -39.5}, {535, 220}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out) 
    annotation(Line(points = {{549, 231}, {681, 231}}, color = {0, 0, 127}));
  connect(fopid_position_error_y.y, enable_position_error_y.u1) 
    annotation(Line(points = {{-576, 25}, {-27.5, 25}, {-27.5, 193}, {521, 193}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 193}, {521, 193}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -58.5}, {535, -58.5}, {535, 182}}, color = {0, 0, 127}));
  connect(enable_position_error_y.y, position_error_y_out) 
    annotation(Line(points = {{549, 193}, {681, 193}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_y.y, enable_fractional_integral_y.u1) 
    annotation(Line(points = {{179, -33}, {350, -33}, {350, 155}, {521, 155}}, color = {0, 0, 127}));
  connect(enable, enable_fractional_integral_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 155}, {521, 155}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_fractional_integral_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -77.5}, {535, -77.5}, {535, 144}}, color = {0, 0, 127}));
  connect(enable_fractional_integral_y.y, fractional_integral_y_out) 
    annotation(Line(points = {{549, 155}, {681, 155}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_y.y, enable_fractional_derivative_y.u1) 
    annotation(Line(points = {{179, -77}, {350, -77}, {350, 117}, {521, 117}}, color = {0, 0, 127}));
  connect(enable, enable_fractional_derivative_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 117}, {521, 117}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_fractional_derivative_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -96.5}, {535, -96.5}, {535, 106}}, color = {0, 0, 127}));
  connect(enable_fractional_derivative_y.y, fractional_derivative_y_out) 
    annotation(Line(points = {{549, 117}, {681, 117}}, color = {0, 0, 127}));
  connect(desired_acceleration_y.y, enable_desired_acceleration_y.u1) 
    annotation(Line(points = {{154, 25}, {337.5, 25}, {337.5, 79}, {521, 79}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 79}, {521, 79}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -115.5}, {535, -115.5}, {535, 68}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out) 
    annotation(Line(points = {{549, 79}, {681, 79}}, color = {0, 0, 127}));
  connect(fopid_position_error_z.y, enable_position_error_z.u1) 
    annotation(Line(points = {{-576, -210}, {-27.5, -210}, {-27.5, 41}, {521, 41}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 41}, {521, 41}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -134.5}, {535, -134.5}, {535, 30}}, color = {0, 0, 127}));
  connect(enable_position_error_z.y, position_error_z_out) 
    annotation(Line(points = {{549, 41}, {681, 41}}, color = {0, 0, 127}));
  connect(fopid_fractional_integral_z.y, enable_fractional_integral_z.u1) 
    annotation(Line(points = {{179, -268}, {350, -268}, {350, 3}, {521, 3}}, color = {0, 0, 127}));
  connect(enable, enable_fractional_integral_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 3}, {521, 3}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_fractional_integral_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -153.5}, {535, -153.5}, {535, -8}}, color = {0, 0, 127}));
  connect(enable_fractional_integral_z.y, fractional_integral_z_out) 
    annotation(Line(points = {{549, 3}, {681, 3}}, color = {0, 0, 127}));
  connect(fopid_fractional_derivative_z.y, enable_fractional_derivative_z.u1) 
    annotation(Line(points = {{179, -312}, {350, -312}, {350, -35}, {521, -35}}, color = {0, 0, 127}));
  connect(enable, enable_fractional_derivative_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -35}, {521, -35}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_fractional_derivative_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -172.5}, {535, -172.5}, {535, -46}}, color = {0, 0, 127}));
  connect(enable_fractional_derivative_z.y, fractional_derivative_z_out) 
    annotation(Line(points = {{549, -35}, {681, -35}}, color = {0, 0, 127}));
  connect(desired_acceleration_z.y, enable_desired_acceleration_z.u1) 
    annotation(Line(points = {{154, -210}, {337.5, -210}, {337.5, -73}, {521, -73}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -73}, {521, -73}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -191.5}, {535, -191.5}, {535, -84}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_z.y, desired_acceleration_z_out) 
    annotation(Line(points = {{549, -73}, {681, -73}}, color = {0, 0, 127}));
  connect(roll_tilt_limit.y, enable_desired_roll_rad.u1) 
    annotation(Line(points = {{334, 75}, {427.5, 75}, {427.5, -111}, {521, -111}}, color = {0, 0, 127}));
  connect(enable, enable_desired_roll_rad.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -111}, {521, -111}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_roll_rad.u3) 
    annotation(Line(points = {{500, -299}, {500, -210.5}, {535, -210.5}, {535, -122}}, color = {0, 0, 127}));
  connect(enable_desired_roll_rad.y, desired_roll_rad_out) 
    annotation(Line(points = {{549, -111}, {681, -111}}, color = {0, 0, 127}));
  connect(pitch_tilt_limit.y, enable_desired_pitch_rad.u1) 
    annotation(Line(points = {{320, 119}, {320, -9.5}, {535, -9.5}, {535, -138}}, color = {0, 0, 127}));
  connect(enable, enable_desired_pitch_rad.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -149}, {521, -149}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_pitch_rad.u3) 
    annotation(Line(points = {{500, -299}, {500, -229.5}, {535, -229.5}, {535, -160}}, color = {0, 0, 127}));
  connect(enable_desired_pitch_rad.y, desired_pitch_rad_out) 
    annotation(Line(points = {{549, -149}, {681, -149}}, color = {0, 0, 127}));
  connect(collective_thrust_limit.y, enable_collective_thrust_n.u1) 
    annotation(Line(points = {{334, -45}, {427.5, -45}, {427.5, -187}, {521, -187}}, color = {0, 0, 127}));
  connect(enable, enable_collective_thrust_n.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -187}, {521, -187}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_collective_thrust_n.u3) 
    annotation(Line(points = {{500, -299}, {500, -248.5}, {535, -248.5}, {535, -198}}, color = {0, 0, 127}));
  connect(enable_collective_thrust_n.y, collective_thrust_n_out) 
    annotation(Line(points = {{549, -187}, {681, -187}}, color = {0, 0, 127}));
  connect(normalized_thrust_limit.y, enable_normalized_thrust.u1) 
    annotation(Line(points = {{500, -56}, {500, -135}, {535, -135}, {535, -214}}, color = {0, 0, 127}));
  connect(enable, enable_normalized_thrust.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -225}, {521, -225}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_normalized_thrust.u3) 
    annotation(Line(points = {{500, -299}, {500, -267.5}, {535, -267.5}, {535, -236}}, color = {0, 0, 127}));
  connect(enable_normalized_thrust.y, normalized_thrust_out) 
    annotation(Line(points = {{549, -225}, {681, -225}}, color = {0, 0, 127}));

end FopidCore;
