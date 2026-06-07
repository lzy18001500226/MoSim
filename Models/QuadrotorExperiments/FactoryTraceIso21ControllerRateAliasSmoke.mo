model FactoryTraceIso21ControllerRateAliasSmoke
  "Rate isolation 21: expose project-owned attitude-derived and controller internal rate aliases"
  extends FactoryTraceIso20RollPitchYawEstimatorSmoke;

  Real roll_rate_from_extraction;
  Real pitch_rate_from_extraction;
  Real yaw_rate_from_extraction;
  Real controller_roll_rate_probe;
  Real controller_pitch_rate_probe;
  Real controller_yaw_rate_probe;
  Real controller_roll_accel_probe;
  Real controller_pitch_accel_probe;
  Real controller_yaw_accel_probe;

equation
  roll_rate_from_extraction = (sensors1_1.AngleMea[1] - roll_est_state) / attitude_extraction_T;
  pitch_rate_from_extraction = (sensors1_1.AngleMea[2] - pitch_est_state) / attitude_extraction_T;
  yaw_rate_from_extraction = (sensors1_1.AngleMea[3] - yaw_est_state) / attitude_extraction_T;
  controller_roll_rate_probe = controller3_2.roll_rate;
  controller_pitch_rate_probe = controller3_2.pitch_rate;
  controller_yaw_rate_probe = controller3_2.yaw_rate;
  controller_roll_accel_probe = controller3_2.roll_accel_hat;
  controller_pitch_accel_probe = controller3_2.pitch_accel_hat;
  controller_yaw_accel_probe = controller3_2.yaw_accel_hat;
end FactoryTraceIso21ControllerRateAliasSmoke;
