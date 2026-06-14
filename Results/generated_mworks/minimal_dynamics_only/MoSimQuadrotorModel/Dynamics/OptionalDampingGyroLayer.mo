within MoSimQuadrotorModel.Dynamics;
model OptionalDampingGyroLayer
  "Formal source surface for default-disabled optional rotor gyro, body drag, and angular damping"
  extends QuadrotorExperiments.DynamicsUpgrade.OptionalDampingGyroLayer;
  annotation(__MWORKS(hide=false));
end OptionalDampingGyroLayer;
