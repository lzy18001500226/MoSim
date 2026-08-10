within MoSimQuadrotorModel.Control.Implementations.Graphical.ProjectOwned;
model AWFFCoreSysblock
  "Strict graphical AWFF controller matching the Formal equation-core parameters"

  parameter Real kp_x = 1.65;
  parameter Real kd_x = 1.0;
  parameter Real kp_y = 1.65;
  parameter Real kd_y = 1.0;
  parameter Real kp_z = 8.0;
  parameter Real ki_z = 6.0;
  parameter Real kd_z = 4.0;
  parameter Real kff_z = 0.35;
  parameter Real kp_roll = 14.142;
  parameter Real kd_roll = 1.70;
  parameter Real kp_pitch = 14.142;
  parameter Real kd_pitch = 1.70;
  parameter Real kp_yaw = 5.0;
  parameter Real roll_pitch_cmd_limit = 12 / 57.3;
  parameter Real attitude_cmd_limit = 6.5;
  parameter Real yaw_cmd_limit = 6.5;
  parameter Real output_limit = 20.0;
  parameter Real position_derivative_filter_T = 0.05;
  parameter Real altitude_derivative_filter_T = 0.08;
  parameter Real attitude_derivative_filter_T = 0.03;

  Modelica.Blocks.Interfaces.RealInput x_error 
    annotation(Placement(transformation(origin = {-370, 250}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealInput y_error 
    annotation(Placement(transformation(origin = {-370, 190}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealInput z_error 
    annotation(Placement(transformation(origin = {-370, 100}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealInput z_ref_rate 
    annotation(Placement(transformation(origin = {-370, 25}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealInput roll_mea 
    annotation(Placement(transformation(origin = {-370, -55}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealInput pitch_mea 
    annotation(Placement(transformation(origin = {-370, -125}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealInput yaw_mea 
    annotation(Placement(transformation(origin = {-370, -195}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealInput yaw_ref 
    annotation(Placement(transformation(origin = {-370, -260}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealOutput y 
    annotation(Placement(transformation(origin = {370, 190}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealOutput y1 
    annotation(Placement(transformation(origin = {370, 65}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealOutput y2 
    annotation(Placement(transformation(origin = {370, -65}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealOutput y3 
    annotation(Placement(transformation(origin = {370, -190}, extent = {{-14, -14}, {14, 14}})));

  Modelica.Blocks.Continuous.FirstOrder x_filter(k = 1, T = position_derivative_filter_T,
    initType = Modelica.Blocks.Types.Init.InitialOutput, y_start = 0) 
    annotation(Placement(transformation(origin = {-300, 265}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Continuous.FirstOrder y_filter(k = 1, T = position_derivative_filter_T,
    initType = Modelica.Blocks.Types.Init.InitialOutput, y_start = 0) 
    annotation(Placement(transformation(origin = {-300, 205}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add x_delta(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {-245, 250}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add y_delta(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {-245, 190}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain x_rate(k = 1 / position_derivative_filter_T) 
    annotation(Placement(transformation(origin = {-190, 250}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain y_rate(k = 1 / position_derivative_filter_T) 
    annotation(Placement(transformation(origin = {-190, 190}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain x_p(k = kp_x) 
    annotation(Placement(transformation(origin = {-190, 280}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain x_d(k = kd_x) 
    annotation(Placement(transformation(origin = {-135, 250}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain y_p(k = kp_y) 
    annotation(Placement(transformation(origin = {-190, 220}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain y_d(k = kd_y) 
    annotation(Placement(transformation(origin = {-135, 190}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add x_pd(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {-80, 265}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add y_pd(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {-80, 205}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain pitch_ref_scale(k = 0.1) 
    annotation(Placement(transformation(origin = {-25, 265}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain roll_ref_scale(k = 0.1) 
    annotation(Placement(transformation(origin = {-25, 205}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Nonlinear.Limiter pitch_ref_limit(uMax = roll_pitch_cmd_limit, uMin = -roll_pitch_cmd_limit) 
    annotation(Placement(transformation(origin = {30, 265}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Nonlinear.Limiter roll_ref_limit(uMax = roll_pitch_cmd_limit, uMin = -roll_pitch_cmd_limit) 
    annotation(Placement(transformation(origin = {30, 205}, extent = {{-18, -12}, {18, 12}})));

  Modelica.Blocks.Continuous.FirstOrder z_filter(k = 1, T = altitude_derivative_filter_T,
    initType = Modelica.Blocks.Types.Init.InitialOutput, y_start = 0) 
    annotation(Placement(transformation(origin = {-300, 115}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add z_delta(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {-245, 100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain z_rate(k = 1 / altitude_derivative_filter_T) 
    annotation(Placement(transformation(origin = {-190, 100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain z_p(k = kp_z) 
    annotation(Placement(transformation(origin = {-190, 145}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain z_d(k = kd_z) 
    annotation(Placement(transformation(origin = {-135, 100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain z_ff(k = kff_z) 
    annotation(Placement(transformation(origin = {-190, 30}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Logical.LessThreshold unsaturated(threshold = output_limit) 
    annotation(Placement(transformation(origin = {30, 90}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Abs thrust_abs 
    annotation(Placement(transformation(origin = {-25, 90}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Product recovery_product 
    annotation(Placement(transformation(origin = {-25, 35}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Logical.LessThreshold recovery_required(threshold = 0) 
    annotation(Placement(transformation(origin = {30, 35}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Logical.Or integral_enabled 
    annotation(Placement(transformation(origin = {85, 60}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Sources.Constant zero(k = 0) 
    annotation(Placement(transformation(origin = {85, 20}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Logical.Switch z_integral_input 
    annotation(Placement(transformation(origin = {140, 80}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Continuous.Integrator z_integral(
    initType = Modelica.Blocks.Types.Init.InitialOutput, y_start = 0) 
    annotation(Placement(transformation(origin = {195, 80}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain z_i(k = ki_z) 
    annotation(Placement(transformation(origin = {250, 80}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add z_sum_1(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {85, 145}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add z_sum_2(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {140, 145}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add z_sum_3(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {195, 145}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Nonlinear.Limiter thrust_limit(uMax = output_limit, uMin = -output_limit) 
    annotation(Placement(transformation(origin = {250, 145}, extent = {{-18, -12}, {18, 12}})));

  Modelica.Blocks.Math.Add roll_error(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {-245, -40}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add pitch_error(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {-245, -110}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add yaw_error(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {-245, -200}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Continuous.FirstOrder roll_filter(k = 1, T = attitude_derivative_filter_T,
    initType = Modelica.Blocks.Types.Init.InitialOutput, y_start = 0) 
    annotation(Placement(transformation(origin = {-190, -25}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Continuous.FirstOrder pitch_filter(k = 1, T = attitude_derivative_filter_T,
    initType = Modelica.Blocks.Types.Init.InitialOutput, y_start = 0) 
    annotation(Placement(transformation(origin = {-190, -95}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add roll_delta(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {-135, -40}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add pitch_delta(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {-135, -110}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain roll_rate(k = 1 / attitude_derivative_filter_T) 
    annotation(Placement(transformation(origin = {-80, -40}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain pitch_rate(k = 1 / attitude_derivative_filter_T) 
    annotation(Placement(transformation(origin = {-80, -110}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain roll_p(k = kp_roll) 
    annotation(Placement(transformation(origin = {-80, -15}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain roll_d(k = kd_roll) 
    annotation(Placement(transformation(origin = {-25, -40}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain pitch_p(k = kp_pitch) 
    annotation(Placement(transformation(origin = {-80, -85}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain pitch_d(k = kd_pitch) 
    annotation(Placement(transformation(origin = {-25, -110}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add roll_sum(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {30, -30}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add pitch_sum(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {30, -100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_p(k = kp_yaw) 
    annotation(Placement(transformation(origin = {-190, -200}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Nonlinear.Limiter roll_limit(uMax = attitude_cmd_limit, uMin = -attitude_cmd_limit) 
    annotation(Placement(transformation(origin = {85, -30}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Nonlinear.Limiter pitch_limit(uMax = attitude_cmd_limit, uMin = -attitude_cmd_limit) 
    annotation(Placement(transformation(origin = {85, -100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Nonlinear.Limiter yaw_limit(uMax = yaw_cmd_limit, uMin = -yaw_cmd_limit) 
    annotation(Placement(transformation(origin = {-135, -200}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain roll_mix(k = 0.707) 
    annotation(Placement(transformation(origin = {140, -30}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain neg_roll_mix(k = -0.707) 
    annotation(Placement(transformation(origin = {140, -55}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain pitch_mix(k = 0.707) 
    annotation(Placement(transformation(origin = {140, -100}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain neg_pitch_mix(k = -0.707) 
    annotation(Placement(transformation(origin = {140, -125}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain yaw_mix(k = 0.707) 
    annotation(Placement(transformation(origin = {-80, -185}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain neg_yaw_mix(k = -0.707) 
    annotation(Placement(transformation(origin = {-80, -215}, extent = {{-18, -12}, {18, 12}})));

  Modelica.Blocks.Math.Add3 motor_1_base(k1 = 1, k2 = -1, k3 = -1) 
    annotation(Placement(transformation(origin = {195, 260}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add motor_1_sum(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {250, 260}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add3 motor_2_base(k1 = 1, k2 = 1, k3 = -1) 
    annotation(Placement(transformation(origin = {195, 220}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add motor_2_pre_sign(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {250, 220}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain motor_2_sign(k = -1) 
    annotation(Placement(transformation(origin = {305, 220}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add3 motor_3_base(k1 = 1, k2 = -1, k3 = 1) 
    annotation(Placement(transformation(origin = {195, -220}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add motor_3_sum(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {250, -220}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add3 motor_4_base(k1 = 1, k2 = 1, k3 = 1) 
    annotation(Placement(transformation(origin = {195, -260}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add motor_4_pre_sign(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {250, -260}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain motor_4_sign(k = -1) 
    annotation(Placement(transformation(origin = {305, -260}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Nonlinear.Limiter motor_1_limit(uMax = output_limit, uMin = -output_limit) 
    annotation(Placement(transformation(origin = {305, 260}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Nonlinear.Limiter motor_2_limit(uMax = output_limit, uMin = -output_limit) 
    annotation(Placement(transformation(origin = {325, 190}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Nonlinear.Limiter motor_3_limit(uMax = output_limit, uMin = -output_limit) 
    annotation(Placement(transformation(origin = {305, -220}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Nonlinear.Limiter motor_4_limit(uMax = output_limit, uMin = -output_limit) 
    annotation(Placement(transformation(origin = {325, -190}, extent = {{-18, -12}, {18, 12}})));

equation
  connect(x_error, x_filter.u);
  connect(y_error, y_filter.u);
  connect(x_error, x_delta.u1);
  connect(x_filter.y, x_delta.u2);
  connect(y_error, y_delta.u1);
  connect(y_filter.y, y_delta.u2);
  connect(x_delta.y, x_rate.u);
  connect(y_delta.y, y_rate.u);
  connect(x_error, x_p.u);
  connect(x_rate.y, x_d.u);
  connect(y_error, y_p.u);
  connect(y_rate.y, y_d.u);
  connect(x_p.y, x_pd.u1);
  connect(x_d.y, x_pd.u2);
  connect(y_p.y, y_pd.u1);
  connect(y_d.y, y_pd.u2);
  connect(x_pd.y, pitch_ref_scale.u);
  connect(y_pd.y, roll_ref_scale.u);
  connect(pitch_ref_scale.y, pitch_ref_limit.u);
  connect(roll_ref_scale.y, roll_ref_limit.u);

  connect(z_error, z_filter.u);
  connect(z_error, z_delta.u1);
  connect(z_filter.y, z_delta.u2);
  connect(z_delta.y, z_rate.u);
  connect(z_error, z_p.u);
  connect(z_rate.y, z_d.u);
  connect(z_ref_rate, z_ff.u);
  connect(z_p.y, z_sum_1.u1);
  connect(z_i.y, z_sum_1.u2);
  connect(z_sum_1.y, z_sum_2.u1);
  connect(z_d.y, z_sum_2.u2);
  connect(z_sum_2.y, z_sum_3.u1);
  connect(z_ff.y, z_sum_3.u2);
  connect(z_sum_3.y, thrust_limit.u);
  connect(z_sum_3.y, thrust_abs.u);
  connect(thrust_abs.y, unsaturated.u);
  connect(z_error, recovery_product.u1);
  connect(z_sum_3.y, recovery_product.u2);
  connect(recovery_product.y, recovery_required.u);
  connect(unsaturated.y, integral_enabled.u1);
  connect(recovery_required.y, integral_enabled.u2);
  connect(z_error, z_integral_input.u1);
  connect(integral_enabled.y, z_integral_input.u2);
  connect(zero.y, z_integral_input.u3);
  connect(z_integral_input.y, z_integral.u);
  connect(z_integral.y, z_i.u);

  connect(roll_ref_limit.y, roll_error.u1);
  connect(roll_mea, roll_error.u2);
  connect(pitch_ref_limit.y, pitch_error.u1);
  connect(pitch_mea, pitch_error.u2);
  connect(yaw_ref, yaw_error.u1);
  connect(yaw_mea, yaw_error.u2);
  connect(roll_error.y, roll_filter.u);
  connect(pitch_error.y, pitch_filter.u);
  connect(roll_error.y, roll_delta.u1);
  connect(roll_filter.y, roll_delta.u2);
  connect(pitch_error.y, pitch_delta.u1);
  connect(pitch_filter.y, pitch_delta.u2);
  connect(roll_delta.y, roll_rate.u);
  connect(pitch_delta.y, pitch_rate.u);
  connect(roll_error.y, roll_p.u);
  connect(roll_rate.y, roll_d.u);
  connect(pitch_error.y, pitch_p.u);
  connect(pitch_rate.y, pitch_d.u);
  connect(roll_p.y, roll_sum.u1);
  connect(roll_d.y, roll_sum.u2);
  connect(pitch_p.y, pitch_sum.u1);
  connect(pitch_d.y, pitch_sum.u2);
  connect(roll_sum.y, roll_limit.u);
  connect(pitch_sum.y, pitch_limit.u);
  connect(yaw_error.y, yaw_p.u);
  connect(yaw_p.y, yaw_limit.u);
  connect(roll_limit.y, roll_mix.u);
  connect(roll_limit.y, neg_roll_mix.u);
  connect(pitch_limit.y, pitch_mix.u);
  connect(pitch_limit.y, neg_pitch_mix.u);
  connect(yaw_limit.y, yaw_mix.u);
  connect(yaw_limit.y, neg_yaw_mix.u);

  connect(thrust_limit.y, motor_1_base.u1);
  connect(neg_yaw_mix.y, motor_1_base.u2);
  connect(neg_pitch_mix.y, motor_1_base.u3);
  connect(motor_1_base.y, motor_1_sum.u1);
  connect(roll_mix.y, motor_1_sum.u2);
  connect(motor_1_sum.y, motor_1_limit.u);
  connect(motor_1_limit.y, y);

  connect(thrust_limit.y, motor_2_base.u1);
  connect(yaw_mix.y, motor_2_base.u2);
  connect(neg_pitch_mix.y, motor_2_base.u3);
  connect(motor_2_base.y, motor_2_pre_sign.u1);
  connect(neg_roll_mix.y, motor_2_pre_sign.u2);
  connect(motor_2_pre_sign.y, motor_2_sign.u);
  connect(motor_2_sign.y, motor_2_limit.u);
  connect(motor_2_limit.y, y1);

  connect(thrust_limit.y, motor_3_base.u1);
  connect(neg_yaw_mix.y, motor_3_base.u2);
  connect(pitch_mix.y, motor_3_base.u3);
  connect(motor_3_base.y, motor_3_sum.u1);
  connect(neg_roll_mix.y, motor_3_sum.u2);
  connect(motor_3_sum.y, motor_3_limit.u);
  connect(motor_3_limit.y, y2);

  connect(thrust_limit.y, motor_4_base.u1);
  connect(yaw_mix.y, motor_4_base.u2);
  connect(pitch_mix.y, motor_4_base.u3);
  connect(motor_4_base.y, motor_4_pre_sign.u1);
  connect(roll_mix.y, motor_4_pre_sign.u2);
  connect(motor_4_pre_sign.y, motor_4_sign.u);
  connect(motor_4_sign.y, motor_4_limit.u);
  connect(motor_4_limit.y, y3);

  annotation(
    Diagram(coordinateSystem(extent = {{-390, -295}, {390, 305}}, grid = {2, 2})),
    __MWORKS(
      version="26.3.0",
      modelType=Control,
      BlockSystem(
        blockKind=BlockKind.userModel,
        SampleTime(auto=true),
        OutputInterval=0.01),
      SysblockVersion="1.0"),
    experiment(
      Algorithm=Euler,
      Interval=0.01,
      IntegratorStep=0.01,
      StartTime=0,
      StopTime=50,
      StoreEventValue=0));
end AWFFCoreSysblock;