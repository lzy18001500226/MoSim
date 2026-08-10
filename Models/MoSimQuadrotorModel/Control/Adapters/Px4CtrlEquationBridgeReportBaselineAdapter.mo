within MoSimQuadrotorModel.Control.Adapters;
model Px4CtrlEquationBridgeReportBaselineAdapter
  "Report-era px4ctrl EquationBridge adapter footprint"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_collective_thrust_n = 4
    * profile.mworks_visual_thrust_coefficient
    * profile.mworks_hover_visual_rotor_speed_rad_s ^ 2;

  MoSimQuadrotorModel.Control.Implementations.Sysblocks.PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock core;

  Real roll_mea;
  Real pitch_mea;
  Real yaw_mea;
  Real q_w;
  Real q_x;
  Real q_y;
  Real q_z;
  Real roll_ref;
  Real pitch_ref;
  Real yaw_ref;
  Real pitch_argument;

equation
  roll_mea = -attitude_mea[1];
  pitch_mea = attitude_mea[2];
  yaw_mea = attitude_mea[3];
  q_w = cos(roll_mea / 2) * cos(pitch_mea / 2) * cos(yaw_mea / 2)
    + sin(roll_mea / 2) * sin(pitch_mea / 2) * sin(yaw_mea / 2);
  q_x = sin(roll_mea / 2) * cos(pitch_mea / 2) * cos(yaw_mea / 2)
    - cos(roll_mea / 2) * sin(pitch_mea / 2) * sin(yaw_mea / 2);
  q_y = cos(roll_mea / 2) * sin(pitch_mea / 2) * cos(yaw_mea / 2)
    + sin(roll_mea / 2) * cos(pitch_mea / 2) * sin(yaw_mea / 2);
  q_z = cos(roll_mea / 2) * cos(pitch_mea / 2) * sin(yaw_mea / 2)
    - sin(roll_mea / 2) * sin(pitch_mea / 2) * cos(yaw_mea / 2);

  core.px = position_mea[1];
  core.py = position_mea[2];
  core.pz = position_mea[3];
  core.vx = velocity_mea[1];
  core.vy = velocity_mea[2];
  core.vz = velocity_mea[3];
  core.qw = q_w;
  core.qx = q_x;
  core.qy = q_y;
  core.qz = q_z;
  core.imu_qw = q_w;
  core.imu_qx = q_x;
  core.imu_qy = q_y;
  core.imu_qz = q_z;

  core.ref_px = position_ref[1];
  core.ref_py = position_ref[2];
  core.ref_pz = position_ref[3];
  core.ref_vx = velocity_ref[1];
  core.ref_vy = velocity_ref[2];
  core.ref_vz = velocity_ref[3];
  core.ref_ax = acceleration_ref[1];
  core.ref_ay = acceleration_ref[2];
  core.ref_az = acceleration_ref[3];
  core.ref_yaw = 0;

  roll_ref = atan2(2 * (core.qd_w * core.qd_x + core.qd_y * core.qd_z),
    1 - 2 * (core.qd_x ^ 2 + core.qd_y ^ 2));
  pitch_argument = 2 * (core.qd_w * core.qd_y - core.qd_z * core.qd_x);
  pitch_ref = if pitch_argument >= 1 then Modelica.Constants.pi / 2 
    else if pitch_argument <= -1 then -Modelica.Constants.pi / 2 else asin(pitch_argument);
  yaw_ref = atan2(2 * (core.qd_w * core.qd_z + core.qd_x * core.qd_y),
    1 - 2 * (core.qd_y ^ 2 + core.qd_z ^ 2));
  attitude_ref[1] = -roll_ref;
  attitude_ref[2] = pitch_ref;
  attitude_ref[3] = yaw_ref;
  collective_thrust_delta = core.collective_thrust_n - hover_collective_thrust_n;

  annotation(__MWORKS(version = "26.3.0"));
end Px4CtrlEquationBridgeReportBaselineAdapter;