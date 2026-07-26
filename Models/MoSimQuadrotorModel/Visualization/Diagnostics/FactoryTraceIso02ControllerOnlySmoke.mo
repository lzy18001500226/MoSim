within MoSimQuadrotorModel.Visualization.Diagnostics;
model FactoryTraceIso02ControllerOnlySmoke
  "Incremental trace isolation 02: Iso01 plus controller math group only"
  extends FactoryTraceIso01FullDisplaySmoke;

  Modelica.Blocks.Math.Feedback x_error;
  Modelica.Blocks.Math.Feedback y_error;
  Modelica.Blocks.Math.Feedback z_error;
  Modelica.Blocks.Sources.Constant zero_roll(k = 0.0);
  Modelica.Blocks.Sources.Constant zero_pitch(k = 0.0);
  Modelica.Blocks.Sources.Constant zero_yaw(k = 0.0);
  AWFF_LinearMPCOuterLoopControllerEquation_Sysblock controller3_2;
  Real motor_delta_1;
  Real motor_delta_2;
  Real motor_delta_3;
  Real motor_delta_4;

equation
  connect(planningReference.position_command[1], x_error.u1);
  connect(planningReference.position_command[1], x_error.u2);
  connect(planningReference.position_command[2], y_error.u1);
  connect(planningReference.position_command[2], y_error.u2);
  connect(planningReference.position_command[3], z_error.u1);
  connect(planningReference.position_command[3], z_error.u2);

  connect(x_error.y, controller3_2.x_error);
  connect(y_error.y, controller3_2.y_error);
  connect(z_error.y, controller3_2.z_error);
  connect(planningReference.z_ref_rate, controller3_2.z_ref_rate);
  connect(zero_roll.y, controller3_2.roll_mea);
  connect(zero_pitch.y, controller3_2.pitch_mea);
  connect(zero_yaw.y, controller3_2.yaw_mea);
  connect(planningReference.yaw_ref, controller3_2.yaw_ref);

  motor_delta_1 = controller3_2.y;
  motor_delta_2 = controller3_2.y1;
  motor_delta_3 = controller3_2.y2;
  motor_delta_4 = controller3_2.y3;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end FactoryTraceIso02ControllerOnlySmoke;