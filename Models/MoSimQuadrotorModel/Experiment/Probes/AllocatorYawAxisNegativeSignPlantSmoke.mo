within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorYawAxisNegativeSignPlantSmoke
  "Negative yaw reference response of the current shared allocator and plant"

  extends AllocatorYawAxisSignPlantSmoke(
    yaw_reference_rad = -0.08);

  annotation(__MWORKS(version = "26.3.0"));
end AllocatorYawAxisNegativeSignPlantSmoke;