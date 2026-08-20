within MoSimQuadrotorModel.Control.Px4Ctrl;
model Px4CtrlCoreSysblock
  "px4ctrl outer-loop Sysblock equation bridge"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    experiment(DoublePrecision=true, Algorithm=Euler, IntegratorStep=0.01,
      Interval=0.01, StartTime=0, StopTime=0.03, StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-420,-360},{420,360}}, grid={2,2})));

  parameter Real kp_x = 1.5;
  parameter Real kp_y = 1.5;
  parameter Real kp_z = 1.5;
  parameter Real kv_x = 1.5;
  parameter Real kv_y = 1.5;
  parameter Real kv_z = 1.5;
  parameter Real mass = 1.0;
  parameter Real gravity = 9.80665;
  parameter Real hover_percentage = 0.37;
  parameter Real eps = 1e-12;

  SysplorerEmbeddedCoder.Port.Inport px annotation(Placement(transformation(origin={-400,330}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport py annotation(Placement(transformation(origin={-400,300}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pz annotation(Placement(transformation(origin={-400,270}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport vx annotation(Placement(transformation(origin={-400,240}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport vy annotation(Placement(transformation(origin={-400,210}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport vz annotation(Placement(transformation(origin={-400,180}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport qw annotation(Placement(transformation(origin={-400,140}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport qx annotation(Placement(transformation(origin={-400,110}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport qy annotation(Placement(transformation(origin={-400,80}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport qz annotation(Placement(transformation(origin={-400,50}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_qw annotation(Placement(transformation(origin={-400,10}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_qx annotation(Placement(transformation(origin={-400,-20}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_qy annotation(Placement(transformation(origin={-400,-50}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport imu_qz annotation(Placement(transformation(origin={-400,-80}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_px annotation(Placement(transformation(origin={-400,-120}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_py annotation(Placement(transformation(origin={-400,-150}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_pz annotation(Placement(transformation(origin={-400,-180}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_vx annotation(Placement(transformation(origin={-400,-210}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_vy annotation(Placement(transformation(origin={-400,-240}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_vz annotation(Placement(transformation(origin={-400,-270}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_ax annotation(Placement(transformation(origin={-400,-300}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_ay annotation(Placement(transformation(origin={-400,-330}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_az annotation(Placement(transformation(origin={-310,-350}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_yaw annotation(Placement(transformation(origin={-240,-350}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport qd_w annotation(Placement(transformation(origin={400,300}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport qd_x annotation(Placement(transformation(origin={400,270}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport qd_y annotation(Placement(transformation(origin={400,240}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport qd_z annotation(Placement(transformation(origin={400,210}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust annotation(Placement(transformation(origin={400,170}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n annotation(Placement(transformation(origin={400,140}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acc_x annotation(Placement(transformation(origin={400,90}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acc_y annotation(Placement(transformation(origin={400,60}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acc_z annotation(Placement(transformation(origin={400,30}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_force_x annotation(Placement(transformation(origin={400,-20}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_force_y annotation(Placement(transformation(origin={400,-50}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_force_z annotation(Placement(transformation(origin={400,-80}, extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(Type(inherit=InheritType.none, ref="double"), Dimension(dimensionType=DimensionType.none)=1, SampleTime(group="D1")=0.01)));

  Real pos_error_x; Real pos_error_y; Real pos_error_z;
  Real vel_error_x; Real vel_error_y; Real vel_error_z;
  Real q_norm; Real iq_norm;
  Real nq_w; Real nq_x; Real nq_y; Real nq_z;
  Real niq_w; Real niq_x; Real niq_y; Real niq_z;
  Real yaw_odom; Real sin_yaw; Real cos_yaw;
  Real roll_cmd; Real pitch_cmd;
  Real cy; Real sy; Real cp; Real sp; Real cr; Real sr;
  Real qyp_w; Real qyp_x; Real qyp_y; Real qyp_z;
  Real qdes_w; Real qdes_x; Real qdes_y; Real qdes_z;
  Real qdes_norm;
  Real rel_w; Real rel_x; Real rel_y; Real rel_z; Real rel_norm;
  Real out_w; Real out_x; Real out_y; Real out_z; Real out_norm;

  model ModelWorkspace
    annotation(__MWORKS(hide=true, BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  pos_error_x = ref_px - px;
  pos_error_y = ref_py - py;
  pos_error_z = ref_pz - pz;
  vel_error_x = ref_vx - vx;
  vel_error_y = ref_vy - vy;
  vel_error_z = ref_vz - vz;
  desired_acc_x = ref_ax + kv_x * vel_error_x + kp_x * pos_error_x;
  desired_acc_y = ref_ay + kv_y * vel_error_y + kp_y * pos_error_y;
  desired_acc_z = ref_az + kv_z * vel_error_z + kp_z * pos_error_z + gravity;
  normalized_thrust = desired_acc_z / (gravity / hover_percentage);
  collective_thrust_n = normalized_thrust * (mass * gravity / hover_percentage);
  desired_force_x = mass * desired_acc_x;
  desired_force_y = mass * desired_acc_y;
  desired_force_z = mass * desired_acc_z;
  q_norm = max(eps, sqrt(qw * qw + qx * qx + qy * qy + qz * qz));
  iq_norm = max(eps, sqrt(imu_qw * imu_qw + imu_qx * imu_qx + imu_qy * imu_qy + imu_qz * imu_qz));
  nq_w = qw / q_norm; nq_x = qx / q_norm; nq_y = qy / q_norm; nq_z = qz / q_norm;
  niq_w = imu_qw / iq_norm; niq_x = imu_qx / iq_norm; niq_y = imu_qy / iq_norm; niq_z = imu_qz / iq_norm;
  yaw_odom = atan2(2 * (nq_x * nq_y + nq_w * nq_z), nq_w * nq_w + nq_x * nq_x - nq_y * nq_y - nq_z * nq_z);
  sin_yaw = sin(yaw_odom);
  cos_yaw = cos(yaw_odom);
  roll_cmd = (desired_acc_x * sin_yaw - desired_acc_y * cos_yaw) / gravity;
  pitch_cmd = (desired_acc_x * cos_yaw + desired_acc_y * sin_yaw) / gravity;
  cy = cos(0.5 * ref_yaw); sy = sin(0.5 * ref_yaw);
  cp = cos(0.5 * pitch_cmd); sp = sin(0.5 * pitch_cmd);
  cr = cos(0.5 * roll_cmd); sr = sin(0.5 * roll_cmd);
  qyp_w = cy * cp; qyp_x = -sy * sp; qyp_y = cy * sp; qyp_z = sy * cp;
  qdes_w = qyp_w * cr - qyp_x * sr;
  qdes_x = qyp_w * sr + qyp_x * cr;
  qdes_y = qyp_y * cr + qyp_z * sr;
  qdes_z = -qyp_y * sr + qyp_z * cr;
  qdes_norm = max(eps, sqrt(qdes_w * qdes_w + qdes_x * qdes_x + qdes_y * qdes_y + qdes_z * qdes_z));
  rel_w = niq_w * nq_w + niq_x * nq_x + niq_y * nq_y + niq_z * nq_z;
  rel_x = -niq_w * nq_x + niq_x * nq_w - niq_y * nq_z + niq_z * nq_y;
  rel_y = -niq_w * nq_y + niq_x * nq_z + niq_y * nq_w - niq_z * nq_x;
  rel_z = -niq_w * nq_z - niq_x * nq_y + niq_y * nq_x + niq_z * nq_w;
  rel_norm = max(eps, sqrt(rel_w * rel_w + rel_x * rel_x + rel_y * rel_y + rel_z * rel_z));
  out_w = (rel_w / rel_norm) * (qdes_w / qdes_norm) - (rel_x / rel_norm) * (qdes_x / qdes_norm) - (rel_y / rel_norm) * (qdes_y / qdes_norm) - (rel_z / rel_norm) * (qdes_z / qdes_norm);
  out_x = (rel_w / rel_norm) * (qdes_x / qdes_norm) + (rel_x / rel_norm) * (qdes_w / qdes_norm) + (rel_y / rel_norm) * (qdes_z / qdes_norm) - (rel_z / rel_norm) * (qdes_y / qdes_norm);
  out_y = (rel_w / rel_norm) * (qdes_y / qdes_norm) - (rel_x / rel_norm) * (qdes_z / qdes_norm) + (rel_y / rel_norm) * (qdes_w / qdes_norm) + (rel_z / rel_norm) * (qdes_x / qdes_norm);
  out_z = (rel_w / rel_norm) * (qdes_z / qdes_norm) + (rel_x / rel_norm) * (qdes_y / qdes_norm) - (rel_y / rel_norm) * (qdes_x / qdes_norm) + (rel_z / rel_norm) * (qdes_w / qdes_norm);
  out_norm = max(eps, sqrt(out_w * out_w + out_x * out_x + out_y * out_y + out_z * out_z));
  qd_w = out_w / out_norm;
  qd_x = out_x / out_norm;
  qd_y = out_y / out_norm;
  qd_z = out_z / out_norm;
end Px4CtrlCoreSysblock;