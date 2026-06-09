within MoSimQuadrotorModel.Dynamics;
model PhysicalWrenchAdapter
  "Formal source surface for physical force/torque application at the external wrench boundary"
  extends QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchAdapter;
  annotation(__MWORKS(hide=false));
end PhysicalWrenchAdapter;
