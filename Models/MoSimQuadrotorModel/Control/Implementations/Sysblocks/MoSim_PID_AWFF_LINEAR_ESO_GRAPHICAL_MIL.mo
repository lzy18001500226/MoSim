within MoSimQuadrotorModel.Control.Implementations.Sysblocks;
model MoSim_PID_AWFF_LINEAR_ESO_GRAPHICAL_MIL "AWFF base controller with x/y/z third-order linear ESO and rotor mixer"
  import BaseWorkspace.*;
  import SysplorerEmbeddedCoder.Types.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(x_position_error, y_position_error, z_position_error, z_reference_rate), Right(rotor_1, rotor_2, rotor_3, rotor_4)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true)),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1));
  SysplorerEmbeddedCoder.Port.Inport x_position_error
    "x position error" annotation (Placement(transformation(origin = {-760, 330}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Port.Inport y_position_error
    "y position error" annotation (Placement(transformation(origin = {-760, 105}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Port.Inport z_position_error
    "z position error" annotation (Placement(transformation(origin = {-760, -175}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Port.Inport z_reference_rate
    "z reference velocity feedforward" annotation (Placement(transformation(origin = {-760, -260}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_x_P(k=0.165)
    "AWFF x proportional command" annotation (Placement(transformation(origin = {-585, 362}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay AWFF_x_previous_error(initCond=0.0)
    "AWFF x derivative memory" annotation (Placement(transformation(origin = {-585, 280}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum AWFF_x_error_delta(inputs="+-")
    "AWFF x error difference" annotation (Placement(transformation(origin = {-495, 280}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_x_derivative_rate(k=100.0)
    "AWFF x derivative at 100 Hz" annotation (Placement(transformation(origin = {-405, 280}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_x_D(k=0.1)
    "AWFF x derivative command" annotation (Placement(transformation(origin = {-315, 280}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum AWFF_x_base
    "AWFF x nominal base command" annotation (Placement(transformation(origin = {-225, 330}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_y_P(k=0.165)
    "AWFF y proportional command" annotation (Placement(transformation(origin = {-585, 127}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay AWFF_y_previous_error(initCond=0.0)
    "AWFF y derivative memory" annotation (Placement(transformation(origin = {-585, 45}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum AWFF_y_error_delta(inputs="+-")
    "AWFF y error difference" annotation (Placement(transformation(origin = {-495, 45}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_y_derivative_rate(k=100.0)
    "AWFF y derivative at 100 Hz" annotation (Placement(transformation(origin = {-405, 45}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_y_D(k=0.1)
    "AWFF y derivative command" annotation (Placement(transformation(origin = {-315, 45}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum AWFF_y_base
    "AWFF y nominal base command" annotation (Placement(transformation(origin = {-225, 95}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_z_P(k=8.0)
    "AWFF z proportional command" annotation (Placement(transformation(origin = {-585, -107}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay AWFF_z_previous_error(initCond=0.0)
    "AWFF z derivative memory" annotation (Placement(transformation(origin = {-585, -190}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum AWFF_z_error_delta(inputs="+-")
    "AWFF z error difference" annotation (Placement(transformation(origin = {-495, -190}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_z_derivative_rate(k=100.0)
    "AWFF z derivative at 100 Hz" annotation (Placement(transformation(origin = {-405, -190}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_z_D(k=4.0)
    "AWFF z derivative command" annotation (Placement(transformation(origin = {-315, -190}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay AWFF_z_integral_state(initCond=0.0)
    "AWFF z bounded integral memory" annotation (Placement(transformation(origin = {-405, -267}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_z_integral_increment(k=0.01)
    "AWFF z integral increment at 100 Hz" annotation (Placement(transformation(origin = {-315, -267}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum AWFF_z_integral_next
    "AWFF z integral update" annotation (Placement(transformation(origin = {-225, -267}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation AWFF_z_integral_limit(lowLimit=-2.5,upLimit=2.5)
    "AWFF z integral limit" annotation (Placement(transformation(origin = {-135, -267}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_z_I(k=6.0)
    "AWFF z integral command" annotation (Placement(transformation(origin = {-135, -227}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain AWFF_z_feedforward(k=0.35)
    "AWFF z reference-rate feedforward" annotation (Placement(transformation(origin = {-315, -67}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum AWFF_z_PI
    "AWFF z PI command" annotation (Placement(transformation(origin = {-45, -140}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum AWFF_z_PID
    "AWFF z PID command" annotation (Placement(transformation(origin = {45, -160}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum AWFF_z_base
    "AWFF z nominal base command" annotation (Placement(transformation(origin = {135, -175}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay ESO_x_z1_feedback(initCond=0.0)
    "ESO x z1 feedback tap" annotation (Placement(transformation(origin = {40, 405}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_x_innovation(inputs="+-")
    "ESO x: e - z1" annotation (Placement(transformation(origin = {-80, 415}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_x_beta1_innovation(k=9.0)
    "ESO x: 3*w_o innovation" annotation (Placement(transformation(origin = {-5, 455}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay ESO_x_z2_feedback(initCond=0.0)
    "ESO x z2 feedback tap" annotation (Placement(transformation(origin = {175, 385}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_x_z1_dot
    "ESO x: z2 + beta1 innovation" annotation (Placement(transformation(origin = {70, 425}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Continuous.Integrator ESO_x_z1_state
    "ESO x continuous state z1" annotation (Placement(transformation(origin = {145, 425}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay ESO_x_z3_feedback(initCond=0.0)
    "ESO x z3 feedback tap" annotation (Placement(transformation(origin = {310, 275}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_x_beta2_innovation(k=27.0)
    "ESO x: 3*w_o^2 innovation" annotation (Placement(transformation(origin = {-5, 335}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_x_z2_plus_z3
    "ESO x: z3 + b0*u0" annotation (Placement(transformation(origin = {70, 335}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_x_z2_dot
    "ESO x: z3 + b0*u0 + beta2 innovation" annotation (Placement(transformation(origin = {145, 335}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Continuous.Integrator ESO_x_z2_state
    "ESO x continuous state z2" annotation (Placement(transformation(origin = {220, 335}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_x_beta3_innovation(k=27.0)
    "ESO x: w_o^3 innovation" annotation (Placement(transformation(origin = {70, 200}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Continuous.Integrator ESO_x_z3_state
    "ESO x continuous state z3" annotation (Placement(transformation(origin = {145, 200}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_x_disturbance_over_b0(k=1.0)
    "ESO x: z3 / b0" annotation (Placement(transformation(origin = {300, 200}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation ESO_x_comp_limit(lowLimit=-0.06,upLimit=0.06)
    "ESO x bounded disturbance compensation" annotation (Placement(transformation(origin = {390, 200}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay ESO_y_z1_feedback(initCond=0.0)
    "ESO y z1 feedback tap" annotation (Placement(transformation(origin = {40, 150}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_y_innovation(inputs="+-")
    "ESO y: e - z1" annotation (Placement(transformation(origin = {-80, 160}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_y_beta1_innovation(k=9.0)
    "ESO y: 3*w_o innovation" annotation (Placement(transformation(origin = {-5, 200}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay ESO_y_z2_feedback(initCond=0.0)
    "ESO y z2 feedback tap" annotation (Placement(transformation(origin = {175, 130}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_y_z1_dot
    "ESO y: z2 + beta1 innovation" annotation (Placement(transformation(origin = {70, 170}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Continuous.Integrator ESO_y_z1_state
    "ESO y continuous state z1" annotation (Placement(transformation(origin = {145, 170}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay ESO_y_z3_feedback(initCond=0.0)
    "ESO y z3 feedback tap" annotation (Placement(transformation(origin = {310, 20}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_y_beta2_innovation(k=27.0)
    "ESO y: 3*w_o^2 innovation" annotation (Placement(transformation(origin = {-5, 80}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_y_z2_plus_z3
    "ESO y: z3 + b0*u0" annotation (Placement(transformation(origin = {70, 80}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_y_z2_dot
    "ESO y: z3 + b0*u0 + beta2 innovation" annotation (Placement(transformation(origin = {145, 80}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Continuous.Integrator ESO_y_z2_state
    "ESO y continuous state z2" annotation (Placement(transformation(origin = {220, 80}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_y_beta3_innovation(k=27.0)
    "ESO y: w_o^3 innovation" annotation (Placement(transformation(origin = {70, -55}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Continuous.Integrator ESO_y_z3_state
    "ESO y continuous state z3" annotation (Placement(transformation(origin = {145, -55}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_y_disturbance_over_b0(k=1.0)
    "ESO y: z3 / b0" annotation (Placement(transformation(origin = {300, -55}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation ESO_y_comp_limit(lowLimit=-0.06,upLimit=0.06)
    "ESO y bounded disturbance compensation" annotation (Placement(transformation(origin = {390, -55}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay ESO_z_z1_feedback(initCond=0.0)
    "ESO z z1 feedback tap" annotation (Placement(transformation(origin = {40, -110}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_z_innovation(inputs="+-")
    "ESO z: e - z1" annotation (Placement(transformation(origin = {-80, -100}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_z_beta1_innovation(k=6.0)
    "ESO z: 3*w_o innovation" annotation (Placement(transformation(origin = {-5, -60}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay ESO_z_z2_feedback(initCond=0.0)
    "ESO z z2 feedback tap" annotation (Placement(transformation(origin = {175, -130}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_z_z1_dot
    "ESO z: z2 + beta1 innovation" annotation (Placement(transformation(origin = {70, -90}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Continuous.Integrator ESO_z_z1_state
    "ESO z continuous state z1" annotation (Placement(transformation(origin = {145, -90}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay ESO_z_z3_feedback(initCond=0.0)
    "ESO z z3 feedback tap" annotation (Placement(transformation(origin = {310, -240}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_z_beta2_innovation(k=12.0)
    "ESO z: 3*w_o^2 innovation" annotation (Placement(transformation(origin = {-5, -180}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_z_z2_plus_z3
    "ESO z: z3 + b0*u0" annotation (Placement(transformation(origin = {70, -180}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ESO_z_z2_dot
    "ESO z: z3 + b0*u0 + beta2 innovation" annotation (Placement(transformation(origin = {145, -180}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Continuous.Integrator ESO_z_z2_state
    "ESO z continuous state z2" annotation (Placement(transformation(origin = {220, -180}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_z_beta3_innovation(k=8.0)
    "ESO z: w_o^3 innovation" annotation (Placement(transformation(origin = {70, -315}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Continuous.Integrator ESO_z_z3_state
    "ESO z continuous state z3" annotation (Placement(transformation(origin = {145, -315}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ESO_z_disturbance_over_b0(k=1.0)
    "ESO z: z3 / b0" annotation (Placement(transformation(origin = {300, -315}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation ESO_z_comp_limit(lowLimit=-1.0,upLimit=1.0)
    "ESO z bounded disturbance compensation" annotation (Placement(transformation(origin = {390, -315}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_base_minus_eso(inputs="+-")
    "pitch base command minus ESO compensation" annotation (Placement(transformation(origin = {485, 300}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_base_minus_eso(inputs="+-")
    "roll base command minus ESO compensation" annotation (Placement(transformation(origin = {485, 45}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum thrust_base_minus_eso(inputs="+-")
    "thrust base command minus ESO compensation" annotation (Placement(transformation(origin = {485, -215}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_command_limit(lowLimit=-0.2094240837696335,upLimit=0.2094240837696335)
    "pitch command limit" annotation (Placement(transformation(origin = {575, 300}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_command_limit(lowLimit=-0.2094240837696335,upLimit=0.2094240837696335)
    "roll command limit" annotation (Placement(transformation(origin = {575, 45}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation thrust_command_limit(lowLimit=-20.0,upLimit=20.0)
    "collective thrust command limit" annotation (Placement(transformation(origin = {575, -215}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant yaw_command_zero(k=0.0)
    "zero yaw command for the displayed mixer path" annotation (Placement(transformation(origin = {575, -65}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_1_stage_2
    "rotor 1: thrust + roll - pitch - yaw" annotation (Placement(transformation(origin = {564, 240}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_1_stage_3(inputs="+-")
    "rotor 1: thrust + roll - pitch - yaw" annotation (Placement(transformation(origin = {632, 240}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_1(inputs="+-")
    "rotor 1: thrust + roll - pitch - yaw" annotation (Placement(transformation(origin = {700, 240}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_2_inner_stage_2(inputs="+-")
    "rotor 2 inner mixer" annotation (Placement(transformation(origin = {564, 120}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_2_inner_stage_3(inputs="+-")
    "rotor 2 inner mixer" annotation (Placement(transformation(origin = {632, 120}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_2_inner
    "rotor 2 inner mixer" annotation (Placement(transformation(origin = {700, 120}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_rotor_2_negate(k=-1.0)
    "rotor 2 sign convention" annotation (Placement(transformation(origin = {820, 120}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_3_stage_2(inputs="+-")
    "rotor 3: thrust - roll + pitch - yaw" annotation (Placement(transformation(origin = {564, 0}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_3_stage_3
    "rotor 3: thrust - roll + pitch - yaw" annotation (Placement(transformation(origin = {632, 0}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_3(inputs="+-")
    "rotor 3: thrust - roll + pitch - yaw" annotation (Placement(transformation(origin = {700, 0}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_4_inner_stage_2
    "rotor 4 inner mixer" annotation (Placement(transformation(origin = {564, -120}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_4_inner_stage_3
    "rotor 4 inner mixer" annotation (Placement(transformation(origin = {632, -120}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_rotor_4_inner
    "rotor 4 inner mixer" annotation (Placement(transformation(origin = {700, -120}, extent = {{-16, -12}, {16, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_rotor_4_negate(k=-1.0)
    "rotor 4 sign convention" annotation (Placement(transformation(origin = {820, -120}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation rotor_1_limit(lowLimit=-20.0,upLimit=20.0)
    "rotor 1 output limit" annotation (Placement(transformation(origin = {910, 240}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation rotor_2_limit(lowLimit=-20.0,upLimit=20.0)
    "rotor 2 output limit" annotation (Placement(transformation(origin = {910, 120}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation rotor_3_limit(lowLimit=-20.0,upLimit=20.0)
    "rotor 3 output limit" annotation (Placement(transformation(origin = {910, 0}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation rotor_4_limit(lowLimit=-20.0,upLimit=20.0)
    "rotor 4 output limit" annotation (Placement(transformation(origin = {910, -120}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_1
    "rotor 1 command" annotation (Placement(transformation(origin = {1020, 240}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_2
    "rotor 2 command" annotation (Placement(transformation(origin = {1020, 120}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_3
    "rotor 3 command" annotation (Placement(transformation(origin = {1020, 0}, extent = {{-16, -12}, {16, 12}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_4
    "rotor 4 command" annotation (Placement(transformation(origin = {1020, -120}, extent = {{-16, -12}, {16, 12}})));
equation
  connect(x_position_error, AWFF_x_P.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(x_position_error, AWFF_x_error_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_x_previous_error.y, AWFF_x_error_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_x_error_delta.y, AWFF_x_derivative_rate.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_x_derivative_rate.y, AWFF_x_D.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_x_P.y, AWFF_x_base.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_x_D.y, AWFF_x_base.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(x_position_error, AWFF_x_previous_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_position_error, AWFF_y_P.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_position_error, AWFF_y_error_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_y_previous_error.y, AWFF_y_error_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_y_error_delta.y, AWFF_y_derivative_rate.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_y_derivative_rate.y, AWFF_y_D.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_y_P.y, AWFF_y_base.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_y_D.y, AWFF_y_base.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_position_error, AWFF_y_previous_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_position_error, AWFF_z_P.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_position_error, AWFF_z_error_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_previous_error.y, AWFF_z_error_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_error_delta.y, AWFF_z_derivative_rate.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_derivative_rate.y, AWFF_z_D.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_position_error, AWFF_z_integral_increment.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_integral_state.y, AWFF_z_integral_next.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_integral_increment.y, AWFF_z_integral_next.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_integral_next.y, AWFF_z_integral_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_integral_state.y, AWFF_z_I.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_reference_rate, AWFF_z_feedforward.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_P.y, AWFF_z_PI.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_I.y, AWFF_z_PI.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_PI.y, AWFF_z_PID.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_D.y, AWFF_z_PID.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_PID.y, AWFF_z_base.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_feedforward.y, AWFF_z_base.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_position_error, AWFF_z_previous_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_integral_limit.y, AWFF_z_integral_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(x_position_error, ESO_x_innovation.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_z1_feedback.y, ESO_x_innovation.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_innovation.y, ESO_x_beta1_innovation.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_z2_feedback.y, ESO_x_z1_dot.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_beta1_innovation.y, ESO_x_z1_dot.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_z1_dot.y, ESO_x_z1_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_innovation.y, ESO_x_beta2_innovation.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_z3_feedback.y, ESO_x_z2_plus_z3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_x_base.y, ESO_x_z2_plus_z3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_z2_plus_z3.y, ESO_x_z2_dot.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_beta2_innovation.y, ESO_x_z2_dot.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_z2_dot.y, ESO_x_z2_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_innovation.y, ESO_x_beta3_innovation.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_beta3_innovation.y, ESO_x_z3_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_z1_state.y, ESO_x_z1_feedback.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_z2_state.y, ESO_x_z2_feedback.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_z3_state.y, ESO_x_z3_feedback.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_z3_state.y, ESO_x_disturbance_over_b0.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_disturbance_over_b0.y, ESO_x_comp_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_position_error, ESO_y_innovation.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_z1_feedback.y, ESO_y_innovation.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_innovation.y, ESO_y_beta1_innovation.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_z2_feedback.y, ESO_y_z1_dot.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_beta1_innovation.y, ESO_y_z1_dot.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_z1_dot.y, ESO_y_z1_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_innovation.y, ESO_y_beta2_innovation.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_z3_feedback.y, ESO_y_z2_plus_z3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_y_base.y, ESO_y_z2_plus_z3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_z2_plus_z3.y, ESO_y_z2_dot.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_beta2_innovation.y, ESO_y_z2_dot.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_z2_dot.y, ESO_y_z2_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_innovation.y, ESO_y_beta3_innovation.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_beta3_innovation.y, ESO_y_z3_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_z1_state.y, ESO_y_z1_feedback.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_z2_state.y, ESO_y_z2_feedback.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_z3_state.y, ESO_y_z3_feedback.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_z3_state.y, ESO_y_disturbance_over_b0.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_disturbance_over_b0.y, ESO_y_comp_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_position_error, ESO_z_innovation.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_z1_feedback.y, ESO_z_innovation.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_innovation.y, ESO_z_beta1_innovation.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_z2_feedback.y, ESO_z_z1_dot.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_beta1_innovation.y, ESO_z_z1_dot.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_z1_dot.y, ESO_z_z1_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_innovation.y, ESO_z_beta2_innovation.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_z3_feedback.y, ESO_z_z2_plus_z3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_base.y, ESO_z_z2_plus_z3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_z2_plus_z3.y, ESO_z_z2_dot.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_beta2_innovation.y, ESO_z_z2_dot.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_z2_dot.y, ESO_z_z2_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_innovation.y, ESO_z_beta3_innovation.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_beta3_innovation.y, ESO_z_z3_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_z1_state.y, ESO_z_z1_feedback.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_z2_state.y, ESO_z_z2_feedback.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_z3_state.y, ESO_z_z3_feedback.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_z3_state.y, ESO_z_disturbance_over_b0.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_disturbance_over_b0.y, ESO_z_comp_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_x_base.y, pitch_base_minus_eso.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_x_comp_limit.y, pitch_base_minus_eso.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_y_base.y, roll_base_minus_eso.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_y_comp_limit.y, roll_base_minus_eso.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(AWFF_z_base.y, thrust_base_minus_eso.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ESO_z_comp_limit.y, thrust_base_minus_eso.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_base_minus_eso.y, pitch_command_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_base_minus_eso.y, roll_command_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(thrust_base_minus_eso.y, thrust_command_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(thrust_command_limit.y, mixer_rotor_1_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_command_limit.y, mixer_rotor_1_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_1_stage_2.y, mixer_rotor_1_stage_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_command_limit.y, mixer_rotor_1_stage_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_1_stage_3.y, mixer_rotor_1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_command_zero.y, mixer_rotor_1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(thrust_command_limit.y, mixer_rotor_2_inner_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_command_limit.y, mixer_rotor_2_inner_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_2_inner_stage_2.y, mixer_rotor_2_inner_stage_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_command_limit.y, mixer_rotor_2_inner_stage_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_2_inner_stage_3.y, mixer_rotor_2_inner.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_command_zero.y, mixer_rotor_2_inner.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_2_inner.y, mixer_rotor_2_negate.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(thrust_command_limit.y, mixer_rotor_3_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_command_limit.y, mixer_rotor_3_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_3_stage_2.y, mixer_rotor_3_stage_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_command_limit.y, mixer_rotor_3_stage_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_3_stage_3.y, mixer_rotor_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_command_zero.y, mixer_rotor_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(thrust_command_limit.y, mixer_rotor_4_inner_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_command_limit.y, mixer_rotor_4_inner_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_4_inner_stage_2.y, mixer_rotor_4_inner_stage_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_command_limit.y, mixer_rotor_4_inner_stage_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_4_inner_stage_3.y, mixer_rotor_4_inner.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_command_zero.y, mixer_rotor_4_inner.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_4_inner.y, mixer_rotor_4_negate.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_1.y, rotor_1_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_2_negate.y, rotor_2_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_3.y, rotor_3_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mixer_rotor_4_negate.y, rotor_4_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(rotor_1_limit.y, rotor_1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(rotor_2_limit.y, rotor_2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(rotor_3_limit.y, rotor_3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(rotor_4_limit.y, rotor_4)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));

end MoSim_PID_AWFF_LINEAR_ESO_GRAPHICAL_MIL;
