within MoSimQuadrotorModel.Dynamics;
model ActuatorCommandMapper
  "Formal source surface for normalized actuator commands to signed visual rotor speed"
  extends QuadrotorExperiments.DynamicsUpgrade.ActuatorCommandMapper;
  annotation(__MWORKS(hide=false));
end ActuatorCommandMapper;
