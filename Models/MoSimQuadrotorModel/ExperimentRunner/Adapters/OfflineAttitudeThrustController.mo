within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfflineAttitudeThrustController
  "Deterministic fixture for the offline ATTITUDE_THRUST boundary"

  extends MoSimQuadrotorModel.ExperimentRunner.Interfaces.PartialAttitudeThrustController;
  parameter Real k_xy = 0.08;
  parameter Real k_z = 0.20;
equation
  attitude_ref[1] = -k_xy * (position_ref[2] - position_mea[2]);
  attitude_ref[2] = k_xy * (position_ref[1] - position_mea[1]);
  attitude_ref[3] = 0;
  collective_thrust_delta = k_z * (position_ref[3] - position_mea[3]);
end OfflineAttitudeThrustController;
