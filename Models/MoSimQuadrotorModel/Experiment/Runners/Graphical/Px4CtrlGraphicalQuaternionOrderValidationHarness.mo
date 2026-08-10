within MoSimQuadrotorModel.Experiment.Runners.Graphical;
model Px4CtrlGraphicalQuaternionOrderValidationHarness
  "Isolated 7.2d validation of the QuatMea {x,y,z,w} to graphical yaw boundary"

  parameter Real quaternion_domain_margin(min = 0, max = 0.01) = 1e-7;

  MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlGraphicalRealStateFormalRunner graphical_formal(
    quaternion_domain_margin = quaternion_domain_margin) 
    annotation(Placement(transformation(origin = {0, 0}, extent = {{-70, -70}, {70, 70}})));

  Real quat_xyzw[4]
    "Raw Modelica MultiBody quaternion from Sunray150Assembly.QuatMea";
  Real quat_wxyz[4]
    "Explicit PX4/Eigen order used at the graphical yaw boundary";
  Real reorder_identity_error[4]
    "Must remain zero for wxyz = {xyzw[4], xyzw[1], xyzw[2], xyzw[3]}";
  Real attitude_from_reordered_quat[3]
    "Modelica {1,2,3} angles reconstructed from the reordered quaternion";
  Real legacy_angle_mea[3]
    "Sunray150Assembly attitude surface from AbsoluteAngles";
  Real quat_to_euler_error[3]
    "Reconstructed angles minus the legacy AngleMea surface";
  Real quaternion_norm;
  Real quaternion_norm_error;
  Real yaw_before_sample
    "Quaternion-reconstructed yaw before the controller sample boundary";
  Real yaw_to_graphical_sysblock
    "Sampled scalar yaw connected to PX4CTRL_Original_OuterLoop_Graphical_Sysblock";

equation
  quat_xyzw = graphical_formal.quat_xyzw;
  quat_wxyz = graphical_formal.quat_wxyz;
  reorder_identity_error = quat_wxyz - {quat_xyzw[4], quat_xyzw[1], quat_xyzw[2], quat_xyzw[3]};
  attitude_from_reordered_quat = graphical_formal.attitude_mea_from_quat;
  legacy_angle_mea = graphical_formal.plant.attitude;
  quat_to_euler_error = graphical_formal.quat_to_euler_error;
  quaternion_norm = graphical_formal.quat_norm;
  quaternion_norm_error = graphical_formal.quaternion_norm_error;
  yaw_before_sample = attitude_from_reordered_quat[3];
  yaw_to_graphical_sysblock = graphical_formal.sampled_attitude[3].y;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-150, -120}, {150, 120}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end Px4CtrlGraphicalQuaternionOrderValidationHarness;