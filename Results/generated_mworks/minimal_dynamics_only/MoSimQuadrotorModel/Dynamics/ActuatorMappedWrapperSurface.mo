within MoSimQuadrotorModel.Dynamics;
model ActuatorMappedWrapperSurface
  "Formal source surface for normalized actuator commands feeding the dynamics wrapper"
  extends QuadrotorExperiments.DynamicsUpgrade.ActuatorMappedWrapperSurface;
  annotation(__MWORKS(hide=false));
end ActuatorMappedWrapperSurface;
