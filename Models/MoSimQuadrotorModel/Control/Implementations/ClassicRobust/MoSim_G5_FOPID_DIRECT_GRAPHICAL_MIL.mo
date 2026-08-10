within MoSimQuadrotorModel.Control.Implementations.ClassicRobust;
model MoSim_G5_FOPID_DIRECT_GRAPHICAL_MIL "FOPID direct graphical core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, dt, enable), Right(position_error_x_out, fractional_integral_x_out, fractional_derivative_x_out, desired_acceleration_x_out, position_error_y_out, fractional_integral_y_out, fractional_derivative_y_out, desired_acceleration_y_out, position_error_z_out, fractional_integral_z_out, fractional_derivative_z_out, desired_acceleration_z_out, desired_roll_rad_out, desired_pitch_rad_out, collective_thrust_n_out, normalized_thrust_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
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
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(reference_position_x, fopid_position_error_x.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_x, fopid_position_error_x.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_x.y, fopid_history_x_01.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_01.y, fopid_history_x_02.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_02.y, fopid_history_x_03.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_03.y, fopid_history_x_04.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_04.y, fopid_history_x_05.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_05.y, fopid_history_x_06.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_06.y, fopid_history_x_07.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_07.y, fopid_history_x_08.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_08.y, fopid_history_x_09.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_09.y, fopid_history_x_10.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_10.y, fopid_history_x_11.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_11.y, fopid_history_x_12.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_12.y, fopid_history_x_13.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_13.y, fopid_history_x_14.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_14.y, fopid_history_x_15.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_x.y, fopid_integral_weight_x_00.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_01.y, fopid_integral_weight_x_01.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_02.y, fopid_integral_weight_x_02.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_03.y, fopid_integral_weight_x_03.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_04.y, fopid_integral_weight_x_04.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_05.y, fopid_integral_weight_x_05.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_06.y, fopid_integral_weight_x_06.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_07.y, fopid_integral_weight_x_07.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_08.y, fopid_integral_weight_x_08.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_09.y, fopid_integral_weight_x_09.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_10.y, fopid_integral_weight_x_10.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_11.y, fopid_integral_weight_x_11.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_12.y, fopid_integral_weight_x_12.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_13.y, fopid_integral_weight_x_13.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_14.y, fopid_integral_weight_x_14.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_15.y, fopid_integral_weight_x_15.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_x.y, fopid_derivative_weight_x_00.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_01.y, fopid_derivative_weight_x_01.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_02.y, fopid_derivative_weight_x_02.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_03.y, fopid_derivative_weight_x_03.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_04.y, fopid_derivative_weight_x_04.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_05.y, fopid_derivative_weight_x_05.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_06.y, fopid_derivative_weight_x_06.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_07.y, fopid_derivative_weight_x_07.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_08.y, fopid_derivative_weight_x_08.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_09.y, fopid_derivative_weight_x_09.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_10.y, fopid_derivative_weight_x_10.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_11.y, fopid_derivative_weight_x_11.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_12.y, fopid_derivative_weight_x_12.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_13.y, fopid_derivative_weight_x_13.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_14.y, fopid_derivative_weight_x_14.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_x_15.y, fopid_derivative_weight_x_15.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_00.y, fopid_fractional_integral_x_stage_2.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_01.y, fopid_fractional_integral_x_stage_2.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_2.y, fopid_fractional_integral_x_stage_3.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_02.y, fopid_fractional_integral_x_stage_3.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_3.y, fopid_fractional_integral_x_stage_4.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_03.y, fopid_fractional_integral_x_stage_4.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_4.y, fopid_fractional_integral_x_stage_5.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_04.y, fopid_fractional_integral_x_stage_5.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_5.y, fopid_fractional_integral_x_stage_6.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_05.y, fopid_fractional_integral_x_stage_6.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_6.y, fopid_fractional_integral_x_stage_7.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_06.y, fopid_fractional_integral_x_stage_7.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_7.y, fopid_fractional_integral_x_stage_8.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_07.y, fopid_fractional_integral_x_stage_8.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_8.y, fopid_fractional_integral_x_stage_9.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_08.y, fopid_fractional_integral_x_stage_9.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_9.y, fopid_fractional_integral_x_stage_10.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_09.y, fopid_fractional_integral_x_stage_10.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_10.y, fopid_fractional_integral_x_stage_11.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_10.y, fopid_fractional_integral_x_stage_11.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_11.y, fopid_fractional_integral_x_stage_12.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_11.y, fopid_fractional_integral_x_stage_12.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_12.y, fopid_fractional_integral_x_stage_13.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_12.y, fopid_fractional_integral_x_stage_13.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_13.y, fopid_fractional_integral_x_stage_14.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_13.y, fopid_fractional_integral_x_stage_14.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_14.y, fopid_fractional_integral_x_stage_15.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_14.y, fopid_fractional_integral_x_stage_15.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x_stage_15.y, fopid_fractional_integral_x.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_x_15.y, fopid_fractional_integral_x.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_00.y, fopid_fractional_derivative_x_stage_2.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_01.y, fopid_fractional_derivative_x_stage_2.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_2.y, fopid_fractional_derivative_x_stage_3.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_02.y, fopid_fractional_derivative_x_stage_3.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_3.y, fopid_fractional_derivative_x_stage_4.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_03.y, fopid_fractional_derivative_x_stage_4.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_4.y, fopid_fractional_derivative_x_stage_5.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_04.y, fopid_fractional_derivative_x_stage_5.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_5.y, fopid_fractional_derivative_x_stage_6.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_05.y, fopid_fractional_derivative_x_stage_6.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_6.y, fopid_fractional_derivative_x_stage_7.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_06.y, fopid_fractional_derivative_x_stage_7.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_7.y, fopid_fractional_derivative_x_stage_8.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_07.y, fopid_fractional_derivative_x_stage_8.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_8.y, fopid_fractional_derivative_x_stage_9.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_08.y, fopid_fractional_derivative_x_stage_9.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_9.y, fopid_fractional_derivative_x_stage_10.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_09.y, fopid_fractional_derivative_x_stage_10.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_10.y, fopid_fractional_derivative_x_stage_11.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_10.y, fopid_fractional_derivative_x_stage_11.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_11.y, fopid_fractional_derivative_x_stage_12.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_11.y, fopid_fractional_derivative_x_stage_12.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_12.y, fopid_fractional_derivative_x_stage_13.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_12.y, fopid_fractional_derivative_x_stage_13.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_13.y, fopid_fractional_derivative_x_stage_14.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_13.y, fopid_fractional_derivative_x_stage_14.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_14.y, fopid_fractional_derivative_x_stage_15.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_14.y, fopid_fractional_derivative_x_stage_15.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x_stage_15.y, fopid_fractional_derivative_x.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_x_15.y, fopid_fractional_derivative_x.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_x.y, fopid_proportional_x.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x.y, fopid_integral_feedback_x.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x.y, fopid_derivative_feedback_x.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_x, fopid_desired_acceleration_pre_gravity_x_stage_2.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_proportional_x.y, fopid_desired_acceleration_pre_gravity_x_stage_2.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_desired_acceleration_pre_gravity_x_stage_2.y, fopid_desired_acceleration_pre_gravity_x_stage_3.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_feedback_x.y, fopid_desired_acceleration_pre_gravity_x_stage_3.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_desired_acceleration_pre_gravity_x_stage_3.y, fopid_desired_acceleration_pre_gravity_x.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_feedback_x.y, fopid_desired_acceleration_pre_gravity_x.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_desired_acceleration_pre_gravity_x.y, desired_acceleration_x.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_y, fopid_position_error_y.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_y, fopid_position_error_y.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_y.y, fopid_history_y_01.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_01.y, fopid_history_y_02.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_02.y, fopid_history_y_03.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_03.y, fopid_history_y_04.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_04.y, fopid_history_y_05.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_05.y, fopid_history_y_06.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_06.y, fopid_history_y_07.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_07.y, fopid_history_y_08.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_08.y, fopid_history_y_09.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_09.y, fopid_history_y_10.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_10.y, fopid_history_y_11.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_11.y, fopid_history_y_12.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_12.y, fopid_history_y_13.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_13.y, fopid_history_y_14.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_14.y, fopid_history_y_15.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_y.y, fopid_integral_weight_y_00.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_01.y, fopid_integral_weight_y_01.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_02.y, fopid_integral_weight_y_02.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_03.y, fopid_integral_weight_y_03.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_04.y, fopid_integral_weight_y_04.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_05.y, fopid_integral_weight_y_05.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_06.y, fopid_integral_weight_y_06.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_07.y, fopid_integral_weight_y_07.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_08.y, fopid_integral_weight_y_08.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_09.y, fopid_integral_weight_y_09.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_10.y, fopid_integral_weight_y_10.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_11.y, fopid_integral_weight_y_11.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_12.y, fopid_integral_weight_y_12.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_13.y, fopid_integral_weight_y_13.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_14.y, fopid_integral_weight_y_14.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_15.y, fopid_integral_weight_y_15.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_y.y, fopid_derivative_weight_y_00.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_01.y, fopid_derivative_weight_y_01.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_02.y, fopid_derivative_weight_y_02.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_03.y, fopid_derivative_weight_y_03.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_04.y, fopid_derivative_weight_y_04.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_05.y, fopid_derivative_weight_y_05.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_06.y, fopid_derivative_weight_y_06.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_07.y, fopid_derivative_weight_y_07.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_08.y, fopid_derivative_weight_y_08.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_09.y, fopid_derivative_weight_y_09.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_10.y, fopid_derivative_weight_y_10.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_11.y, fopid_derivative_weight_y_11.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_12.y, fopid_derivative_weight_y_12.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_13.y, fopid_derivative_weight_y_13.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_14.y, fopid_derivative_weight_y_14.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_y_15.y, fopid_derivative_weight_y_15.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_00.y, fopid_fractional_integral_y_stage_2.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_01.y, fopid_fractional_integral_y_stage_2.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_2.y, fopid_fractional_integral_y_stage_3.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_02.y, fopid_fractional_integral_y_stage_3.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_3.y, fopid_fractional_integral_y_stage_4.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_03.y, fopid_fractional_integral_y_stage_4.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_4.y, fopid_fractional_integral_y_stage_5.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_04.y, fopid_fractional_integral_y_stage_5.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_5.y, fopid_fractional_integral_y_stage_6.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_05.y, fopid_fractional_integral_y_stage_6.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_6.y, fopid_fractional_integral_y_stage_7.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_06.y, fopid_fractional_integral_y_stage_7.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_7.y, fopid_fractional_integral_y_stage_8.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_07.y, fopid_fractional_integral_y_stage_8.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_8.y, fopid_fractional_integral_y_stage_9.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_08.y, fopid_fractional_integral_y_stage_9.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_9.y, fopid_fractional_integral_y_stage_10.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_09.y, fopid_fractional_integral_y_stage_10.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_10.y, fopid_fractional_integral_y_stage_11.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_10.y, fopid_fractional_integral_y_stage_11.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_11.y, fopid_fractional_integral_y_stage_12.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_11.y, fopid_fractional_integral_y_stage_12.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_12.y, fopid_fractional_integral_y_stage_13.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_12.y, fopid_fractional_integral_y_stage_13.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_13.y, fopid_fractional_integral_y_stage_14.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_13.y, fopid_fractional_integral_y_stage_14.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_14.y, fopid_fractional_integral_y_stage_15.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_14.y, fopid_fractional_integral_y_stage_15.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y_stage_15.y, fopid_fractional_integral_y.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_y_15.y, fopid_fractional_integral_y.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_00.y, fopid_fractional_derivative_y_stage_2.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_01.y, fopid_fractional_derivative_y_stage_2.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_2.y, fopid_fractional_derivative_y_stage_3.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_02.y, fopid_fractional_derivative_y_stage_3.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_3.y, fopid_fractional_derivative_y_stage_4.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_03.y, fopid_fractional_derivative_y_stage_4.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_4.y, fopid_fractional_derivative_y_stage_5.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_04.y, fopid_fractional_derivative_y_stage_5.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_5.y, fopid_fractional_derivative_y_stage_6.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_05.y, fopid_fractional_derivative_y_stage_6.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_6.y, fopid_fractional_derivative_y_stage_7.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_06.y, fopid_fractional_derivative_y_stage_7.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_7.y, fopid_fractional_derivative_y_stage_8.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_07.y, fopid_fractional_derivative_y_stage_8.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_8.y, fopid_fractional_derivative_y_stage_9.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_08.y, fopid_fractional_derivative_y_stage_9.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_9.y, fopid_fractional_derivative_y_stage_10.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_09.y, fopid_fractional_derivative_y_stage_10.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_10.y, fopid_fractional_derivative_y_stage_11.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_10.y, fopid_fractional_derivative_y_stage_11.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_11.y, fopid_fractional_derivative_y_stage_12.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_11.y, fopid_fractional_derivative_y_stage_12.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_12.y, fopid_fractional_derivative_y_stage_13.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_12.y, fopid_fractional_derivative_y_stage_13.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_13.y, fopid_fractional_derivative_y_stage_14.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_13.y, fopid_fractional_derivative_y_stage_14.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_14.y, fopid_fractional_derivative_y_stage_15.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_14.y, fopid_fractional_derivative_y_stage_15.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y_stage_15.y, fopid_fractional_derivative_y.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_y_15.y, fopid_fractional_derivative_y.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_y.y, fopid_proportional_y.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y.y, fopid_integral_feedback_y.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y.y, fopid_derivative_feedback_y.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_y, fopid_desired_acceleration_pre_gravity_y_stage_2.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_proportional_y.y, fopid_desired_acceleration_pre_gravity_y_stage_2.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_desired_acceleration_pre_gravity_y_stage_2.y, fopid_desired_acceleration_pre_gravity_y_stage_3.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_feedback_y.y, fopid_desired_acceleration_pre_gravity_y_stage_3.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_desired_acceleration_pre_gravity_y_stage_3.y, fopid_desired_acceleration_pre_gravity_y.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_feedback_y.y, fopid_desired_acceleration_pre_gravity_y.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_desired_acceleration_pre_gravity_y.y, desired_acceleration_y.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_z, fopid_position_error_z.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_z, fopid_position_error_z.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_z.y, fopid_history_z_01.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_01.y, fopid_history_z_02.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_02.y, fopid_history_z_03.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_03.y, fopid_history_z_04.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_04.y, fopid_history_z_05.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_05.y, fopid_history_z_06.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_06.y, fopid_history_z_07.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_07.y, fopid_history_z_08.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_08.y, fopid_history_z_09.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_09.y, fopid_history_z_10.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_10.y, fopid_history_z_11.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_11.y, fopid_history_z_12.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_12.y, fopid_history_z_13.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_13.y, fopid_history_z_14.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_14.y, fopid_history_z_15.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_z.y, fopid_integral_weight_z_00.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_01.y, fopid_integral_weight_z_01.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_02.y, fopid_integral_weight_z_02.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_03.y, fopid_integral_weight_z_03.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_04.y, fopid_integral_weight_z_04.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_05.y, fopid_integral_weight_z_05.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_06.y, fopid_integral_weight_z_06.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_07.y, fopid_integral_weight_z_07.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_08.y, fopid_integral_weight_z_08.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_09.y, fopid_integral_weight_z_09.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_10.y, fopid_integral_weight_z_10.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_11.y, fopid_integral_weight_z_11.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_12.y, fopid_integral_weight_z_12.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_13.y, fopid_integral_weight_z_13.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_14.y, fopid_integral_weight_z_14.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_15.y, fopid_integral_weight_z_15.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_z.y, fopid_derivative_weight_z_00.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_01.y, fopid_derivative_weight_z_01.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_02.y, fopid_derivative_weight_z_02.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_03.y, fopid_derivative_weight_z_03.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_04.y, fopid_derivative_weight_z_04.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_05.y, fopid_derivative_weight_z_05.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_06.y, fopid_derivative_weight_z_06.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_07.y, fopid_derivative_weight_z_07.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_08.y, fopid_derivative_weight_z_08.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_09.y, fopid_derivative_weight_z_09.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_10.y, fopid_derivative_weight_z_10.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_11.y, fopid_derivative_weight_z_11.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_12.y, fopid_derivative_weight_z_12.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_13.y, fopid_derivative_weight_z_13.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_14.y, fopid_derivative_weight_z_14.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_history_z_15.y, fopid_derivative_weight_z_15.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_00.y, fopid_fractional_integral_z_stage_2.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_01.y, fopid_fractional_integral_z_stage_2.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_2.y, fopid_fractional_integral_z_stage_3.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_02.y, fopid_fractional_integral_z_stage_3.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_3.y, fopid_fractional_integral_z_stage_4.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_03.y, fopid_fractional_integral_z_stage_4.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_4.y, fopid_fractional_integral_z_stage_5.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_04.y, fopid_fractional_integral_z_stage_5.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_5.y, fopid_fractional_integral_z_stage_6.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_05.y, fopid_fractional_integral_z_stage_6.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_6.y, fopid_fractional_integral_z_stage_7.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_06.y, fopid_fractional_integral_z_stage_7.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_7.y, fopid_fractional_integral_z_stage_8.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_07.y, fopid_fractional_integral_z_stage_8.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_8.y, fopid_fractional_integral_z_stage_9.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_08.y, fopid_fractional_integral_z_stage_9.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_9.y, fopid_fractional_integral_z_stage_10.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_09.y, fopid_fractional_integral_z_stage_10.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_10.y, fopid_fractional_integral_z_stage_11.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_10.y, fopid_fractional_integral_z_stage_11.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_11.y, fopid_fractional_integral_z_stage_12.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_11.y, fopid_fractional_integral_z_stage_12.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_12.y, fopid_fractional_integral_z_stage_13.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_12.y, fopid_fractional_integral_z_stage_13.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_13.y, fopid_fractional_integral_z_stage_14.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_13.y, fopid_fractional_integral_z_stage_14.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_14.y, fopid_fractional_integral_z_stage_15.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_14.y, fopid_fractional_integral_z_stage_15.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z_stage_15.y, fopid_fractional_integral_z.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_weight_z_15.y, fopid_fractional_integral_z.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_00.y, fopid_fractional_derivative_z_stage_2.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_01.y, fopid_fractional_derivative_z_stage_2.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_2.y, fopid_fractional_derivative_z_stage_3.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_02.y, fopid_fractional_derivative_z_stage_3.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_3.y, fopid_fractional_derivative_z_stage_4.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_03.y, fopid_fractional_derivative_z_stage_4.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_4.y, fopid_fractional_derivative_z_stage_5.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_04.y, fopid_fractional_derivative_z_stage_5.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_5.y, fopid_fractional_derivative_z_stage_6.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_05.y, fopid_fractional_derivative_z_stage_6.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_6.y, fopid_fractional_derivative_z_stage_7.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_06.y, fopid_fractional_derivative_z_stage_7.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_7.y, fopid_fractional_derivative_z_stage_8.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_07.y, fopid_fractional_derivative_z_stage_8.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_8.y, fopid_fractional_derivative_z_stage_9.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_08.y, fopid_fractional_derivative_z_stage_9.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_9.y, fopid_fractional_derivative_z_stage_10.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_09.y, fopid_fractional_derivative_z_stage_10.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_10.y, fopid_fractional_derivative_z_stage_11.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_10.y, fopid_fractional_derivative_z_stage_11.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_11.y, fopid_fractional_derivative_z_stage_12.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_11.y, fopid_fractional_derivative_z_stage_12.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_12.y, fopid_fractional_derivative_z_stage_13.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_12.y, fopid_fractional_derivative_z_stage_13.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_13.y, fopid_fractional_derivative_z_stage_14.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_13.y, fopid_fractional_derivative_z_stage_14.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_14.y, fopid_fractional_derivative_z_stage_15.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_14.y, fopid_fractional_derivative_z_stage_15.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z_stage_15.y, fopid_fractional_derivative_z.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_weight_z_15.y, fopid_fractional_derivative_z.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_z.y, fopid_proportional_z.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z.y, fopid_integral_feedback_z.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z.y, fopid_derivative_feedback_z.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_z, fopid_desired_acceleration_pre_gravity_z_stage_2.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_proportional_z.y, fopid_desired_acceleration_pre_gravity_z_stage_2.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_desired_acceleration_pre_gravity_z_stage_2.y, fopid_desired_acceleration_pre_gravity_z_stage_3.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_integral_feedback_z.y, fopid_desired_acceleration_pre_gravity_z_stage_3.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_desired_acceleration_pre_gravity_z_stage_3.y, fopid_desired_acceleration_pre_gravity_z.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_derivative_feedback_z.y, fopid_desired_acceleration_pre_gravity_z.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_desired_acceleration_pre_gravity_z.y, desired_acceleration_z.u1) 
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
  connect(fopid_position_error_x.y, enable_position_error_x.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_position_error_x.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_position_error_x.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_position_error_x.y, position_error_x_out) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_x.y, enable_fractional_integral_x.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_fractional_integral_x.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_fractional_integral_x.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_fractional_integral_x.y, fractional_integral_x_out) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_x.y, enable_fractional_derivative_x.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_fractional_derivative_x.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_fractional_derivative_x.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_fractional_derivative_x.y, fractional_derivative_x_out) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_x.y, enable_desired_acceleration_x.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_acceleration_x.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_y.y, enable_position_error_y.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_position_error_y.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_position_error_y.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_position_error_y.y, position_error_y_out) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_y.y, enable_fractional_integral_y.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_fractional_integral_y.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_fractional_integral_y.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_fractional_integral_y.y, fractional_integral_y_out) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_y.y, enable_fractional_derivative_y.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_fractional_derivative_y.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_fractional_derivative_y.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_fractional_derivative_y.y, fractional_derivative_y_out) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(desired_acceleration_y.y, enable_desired_acceleration_y.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_acceleration_y.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_position_error_z.y, enable_position_error_z.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_position_error_z.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_position_error_z.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_position_error_z.y, position_error_z_out) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_integral_z.y, enable_fractional_integral_z.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_fractional_integral_z.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_fractional_integral_z.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_fractional_integral_z.y, fractional_integral_z_out) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fopid_fractional_derivative_z.y, enable_fractional_derivative_z.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_fractional_derivative_z.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_fractional_derivative_z.u3) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_fractional_derivative_z.y, fractional_derivative_z_out) 
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

end MoSim_G5_FOPID_DIRECT_GRAPHICAL_MIL;