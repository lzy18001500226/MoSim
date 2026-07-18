within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfflineBodyRateThrustController
  "Deterministic fixture for the offline BODY_RATE_THRUST boundary"

  extends MoSimQuadrotorModel.ExperimentRunner.Interfaces.PartialBodyRateThrustController;
equation
  body_rate_ref[1] = -0.20 * (position_ref[2] - position_mea[2]) - 0.8 * attitude_mea[1];
  body_rate_ref[2] = 0.20 * (position_ref[1] - position_mea[1]) - 0.8 * attitude_mea[2];
  body_rate_ref[3] = -0.8 * attitude_mea[3];
  collective_thrust_delta = 0.20 * (position_ref[3] - position_mea[3]);
end OfflineBodyRateThrustController;
