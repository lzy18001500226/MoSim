within MoSimQuadrotorModel.Control.Px4Ctrl;
model Px4CtrlAttitudeThrustSysblockAdapter
  "px4ctrl graphical outer loop bridged to attitude and collective thrust"

  parameter MoSimQuadrotorModel.Parameters.Sunray150Parameters profile;
  parameter Real hover_collective_thrust_n = 4
    * profile.mworks_visual_thrust_coefficient
    * profile.mworks_hover_visual_rotor_speed_rad_s ^ 2;
  parameter Real controller_mass = 1.0;
  parameter Real gravity = 9.80665;
  parameter Real hover_percentage = 0.37;
  parameter Real quaternion_epsilon = 1e-12;
  parameter Real reference_yaw = 0;

  Modelica.Blocks.Interfaces.RealInput position_ref[3];
  Modelica.Blocks.Interfaces.RealInput velocity_ref[3];
  Modelica.Blocks.Interfaces.RealInput acceleration_ref[3];
  Modelica.Blocks.Interfaces.RealInput position_mea[3];
  Modelica.Blocks.Interfaces.RealInput velocity_mea[3];
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3];
  Modelica.Blocks.Interfaces.RealOutput attitude_ref[3];
  Modelica.Blocks.Interfaces.RealOutput collective_thrust_delta(unit="N");
  Modelica.Blocks.Interfaces.RealOutput desired_acceleration[3](each unit="m/s2");

  // Keep the PD/feed-forward law in a visible graphical Sysblock. This wrapper
  // only maps its acceleration command to the unchanged PX4 attitude boundary.
  Px4CtrlOuterLoopGraphicalSysblock outer_loop 
    annotation(__MWORKS(SECInstance=true, PortLabels(labelType="PortName")));

  Modelica.Blocks.Interfaces.RealInput graphical_desired_acceleration[3](each unit="m/s2");

  Real roll_mea;
  Real pitch_mea;
  Real yaw_mea;
  Real q_w;
  Real q_x;
  Real q_y;
  Real q_z;
  Real desired_quaternion[4];
  Real normalized_thrust;
  Real collective_thrust_n(unit="N");
  Real roll_ref;
  Real pitch_ref;
  Real yaw_ref;
  Real pitch_argument;
  Real q_norm;
  Real iq_norm;
  Real nq_w;
  Real nq_x;
  Real nq_y;
  Real nq_z;
  Real niq_w;
  Real niq_x;
  Real niq_y;
  Real niq_z;
  Real sin_yaw;
  Real cos_yaw;
  Real roll_cmd;
  Real pitch_cmd;
  Real cy;
  Real sy;
  Real cp;
  Real sp;
  Real cr;
  Real sr;
  Real qyp_w;
  Real qyp_x;
  Real qyp_y;
  Real qyp_z;
  Real qdes_w;
  Real qdes_x;
  Real qdes_y;
  Real qdes_z;
  Real qdes_norm;
  Real rel_w;
  Real rel_x;
  Real rel_y;
  Real rel_z;
  Real rel_norm;
  Real out_w;
  Real out_x;
  Real out_y;
  Real out_z;
  Real out_norm;

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

  connect(position_ref[1], outer_loop.ref_p_x);
  connect(position_mea[1], outer_loop.mea_p_x);
  connect(velocity_ref[1], outer_loop.ref_v_x);
  connect(velocity_mea[1], outer_loop.mea_v_x);
  connect(acceleration_ref[1], outer_loop.ref_a_x);
  connect(position_ref[2], outer_loop.ref_p_y);
  connect(position_mea[2], outer_loop.mea_p_y);
  connect(velocity_ref[2], outer_loop.ref_v_y);
  connect(velocity_mea[2], outer_loop.mea_v_y);
  connect(acceleration_ref[2], outer_loop.ref_a_y);
  connect(position_ref[3], outer_loop.ref_p_z);
  connect(position_mea[3], outer_loop.mea_p_z);
  connect(velocity_ref[3], outer_loop.ref_v_z);
  connect(velocity_mea[3], outer_loop.mea_v_z);
  connect(acceleration_ref[3], outer_loop.ref_a_z);
  connect(outer_loop.desired_acc_x, graphical_desired_acceleration[1]);
  connect(outer_loop.desired_acc_y, graphical_desired_acceleration[2]);
  connect(outer_loop.desired_acc_z, graphical_desired_acceleration[3]);

  // Only the nested graphical Sysblock computes the acceleration command.
  // RT1 holds outbound transport until the graphical core has seen two valid
  // state samples, so no equation-form startup command is needed here.
  desired_acceleration[1] = graphical_desired_acceleration[1];
  desired_acceleration[2] = graphical_desired_acceleration[2];
  desired_acceleration[3] = graphical_desired_acceleration[3];

  normalized_thrust = desired_acceleration[3] / (gravity / hover_percentage);
  collective_thrust_n = normalized_thrust
    * (controller_mass * gravity / hover_percentage);
  q_norm = max(quaternion_epsilon, sqrt(q_w * q_w + q_x * q_x + q_y * q_y + q_z * q_z));
  iq_norm = max(quaternion_epsilon, sqrt(q_w * q_w + q_x * q_x + q_y * q_y + q_z * q_z));
  nq_w = q_w / q_norm;
  nq_x = q_x / q_norm;
  nq_y = q_y / q_norm;
  nq_z = q_z / q_norm;
  niq_w = q_w / iq_norm;
  niq_x = q_x / iq_norm;
  niq_y = q_y / iq_norm;
  niq_z = q_z / iq_norm;
  sin_yaw = sin(yaw_mea);
  cos_yaw = cos(yaw_mea);
  roll_cmd = (desired_acceleration[1] * sin_yaw
    - desired_acceleration[2] * cos_yaw) / gravity;
  pitch_cmd = (desired_acceleration[1] * cos_yaw
    + desired_acceleration[2] * sin_yaw) / gravity;
  cy = cos(0.5 * reference_yaw);
  sy = sin(0.5 * reference_yaw);
  cp = cos(0.5 * pitch_cmd);
  sp = sin(0.5 * pitch_cmd);
  cr = cos(0.5 * roll_cmd);
  sr = sin(0.5 * roll_cmd);
  qyp_w = cy * cp;
  qyp_x = -sy * sp;
  qyp_y = cy * sp;
  qyp_z = sy * cp;
  qdes_w = qyp_w * cr - qyp_x * sr;
  qdes_x = qyp_w * sr + qyp_x * cr;
  qdes_y = qyp_y * cr + qyp_z * sr;
  qdes_z = -qyp_y * sr + qyp_z * cr;
  qdes_norm = max(quaternion_epsilon, sqrt(qdes_w * qdes_w + qdes_x * qdes_x
    + qdes_y * qdes_y + qdes_z * qdes_z));
  rel_w = niq_w * nq_w + niq_x * nq_x + niq_y * nq_y + niq_z * nq_z;
  rel_x = -niq_w * nq_x + niq_x * nq_w - niq_y * nq_z + niq_z * nq_y;
  rel_y = -niq_w * nq_y + niq_x * nq_z + niq_y * nq_w - niq_z * nq_x;
  rel_z = -niq_w * nq_z - niq_x * nq_y + niq_y * nq_x + niq_z * nq_w;
  rel_norm = max(quaternion_epsilon, sqrt(rel_w * rel_w + rel_x * rel_x
    + rel_y * rel_y + rel_z * rel_z));
  out_w = (rel_w / rel_norm) * (qdes_w / qdes_norm)
    - (rel_x / rel_norm) * (qdes_x / qdes_norm)
    - (rel_y / rel_norm) * (qdes_y / qdes_norm)
    - (rel_z / rel_norm) * (qdes_z / qdes_norm);
  out_x = (rel_w / rel_norm) * (qdes_x / qdes_norm)
    + (rel_x / rel_norm) * (qdes_w / qdes_norm)
    + (rel_y / rel_norm) * (qdes_z / qdes_norm)
    - (rel_z / rel_norm) * (qdes_y / qdes_norm);
  out_y = (rel_w / rel_norm) * (qdes_y / qdes_norm)
    - (rel_x / rel_norm) * (qdes_z / qdes_norm)
    + (rel_y / rel_norm) * (qdes_w / qdes_norm)
    + (rel_z / rel_norm) * (qdes_x / qdes_norm);
  out_z = (rel_w / rel_norm) * (qdes_z / qdes_norm)
    + (rel_x / rel_norm) * (qdes_y / qdes_norm)
    - (rel_y / rel_norm) * (qdes_x / qdes_norm)
    + (rel_z / rel_norm) * (qdes_w / qdes_norm);
  out_norm = max(quaternion_epsilon, sqrt(out_w * out_w + out_x * out_x
    + out_y * out_y + out_z * out_z));
  desired_quaternion[1] = out_w / out_norm;
  desired_quaternion[2] = out_x / out_norm;
  desired_quaternion[3] = out_y / out_norm;
  desired_quaternion[4] = out_z / out_norm;

  roll_ref = atan2(2 * (desired_quaternion[1] * desired_quaternion[2]
    + desired_quaternion[3] * desired_quaternion[4]),
    1 - 2 * (desired_quaternion[2] ^ 2 + desired_quaternion[3] ^ 2));
  pitch_argument = 2 * (desired_quaternion[1] * desired_quaternion[3]
    - desired_quaternion[4] * desired_quaternion[2]);
  pitch_ref = if pitch_argument >= 1 then Modelica.Constants.pi / 2 
    else if pitch_argument <= -1 then -Modelica.Constants.pi / 2 else asin(pitch_argument);
  yaw_ref = atan2(2 * (desired_quaternion[1] * desired_quaternion[4]
    + desired_quaternion[2] * desired_quaternion[3]),
    1 - 2 * (desired_quaternion[3] ^ 2 + desired_quaternion[4] ^ 2));
  attitude_ref[1] = -roll_ref;
  attitude_ref[2] = pitch_ref;
  attitude_ref[3] = yaw_ref;
  collective_thrust_delta = collective_thrust_n - hover_collective_thrust_n;

  annotation(
    Icon(coordinateSystem(extent={{-100,-100},{100,100}}), graphics={
      Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,100,150},
        fillColor={240,255,240}, fillPattern=FillPattern.Solid),
      Text(origin={0,22}, extent={{-90,18},{90,-18}}, textString="PX4CTRL"),
      Text(origin={0,-20}, extent={{-90,18},{90,-18}}, textString="GRAPHICAL OUTER LOOP")} ),
    __MWORKS(version="26.3.0"));
end Px4CtrlAttitudeThrustSysblockAdapter;