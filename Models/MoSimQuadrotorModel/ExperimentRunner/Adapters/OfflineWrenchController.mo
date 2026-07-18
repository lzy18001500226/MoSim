within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfflineWrenchController
  "Deterministic fixture for the offline WRENCH boundary"

  extends MoSimQuadrotorModel.ExperimentRunner.Interfaces.PartialWrenchController;
equation
  body_force = {0, 0, 0.20 * (position_ref[3] - position_mea[3])};
  body_torque = {-0.30 * attitude_mea[1], -0.30 * attitude_mea[2], -0.15 * attitude_mea[3]};
end OfflineWrenchController;
