within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorFullFeedbackZeroReferenceYawInvertedSmoke
  "Diagnostic only: invert yaw feedback sign while preserving roll/pitch allocation"

  extends AllocatorFullFeedbackZeroReferenceSmoke(
    allocator(kp_yaw = -5));

  annotation(__MWORKS(version = "26.3.0"));
end AllocatorFullFeedbackZeroReferenceYawInvertedSmoke;
