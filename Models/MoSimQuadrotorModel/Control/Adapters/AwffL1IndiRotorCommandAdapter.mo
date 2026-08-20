within MoSimQuadrotorModel.Control.Adapters;
model AwffL1IndiRotorCommandAdapter
  "Adapter for AWFF+L1+INDI Sysblock controller outputting ROTOR_COMMAND boundary"
  extends MoSimQuadrotorModel.Control.Adapters.Base.RotorCommandAdapterBase;
  MoSimQuadrotorModel.Control.Implementations.Graphical.AWFF.AwffL1IndiControllerCoreSysblock controller_core;
  Modelica.Blocks.Math.Feedback x_error;
  Modelica.Blocks.Math.Feedback y_error;
  Modelica.Blocks.Math.Feedback z_error;
  Modelica.Blocks.Sources.Constant z_ref_rate(k = 0);
  Modelica.Blocks.Sources.Constant yaw_ref(k = 0);
equation
  connect(position_command[1], x_error.u1);
  connect(position_measurement[1], x_error.u2);
  connect(position_command[2], y_error.u1);
  connect(position_measurement[2], y_error.u2);
  connect(position_command[3], z_error.u1);
  connect(position_measurement[3], z_error.u2);
  connect(x_error.y, controller_core.x_error);
  connect(y_error.y, controller_core.y_error);
  connect(z_error.y, controller_core.z_error);
  connect(z_ref_rate.y, controller_core.z_ref_rate);
  connect(attitude_measurement[1], controller_core.roll_mea);
  connect(attitude_measurement[2], controller_core.pitch_mea);
  connect(attitude_measurement[3], controller_core.yaw_mea);
  connect(yaw_ref.y, controller_core.yaw_ref);
  connect(controller_core.y, motor_speed_command[1]);
  connect(controller_core.y1, motor_speed_command[2]);
  connect(controller_core.y2, motor_speed_command[3]);
  connect(controller_core.y3, motor_speed_command[4]);
  annotation(__MWORKS(hide = false, version = "26.3.0"));
end AwffL1IndiRotorCommandAdapter;