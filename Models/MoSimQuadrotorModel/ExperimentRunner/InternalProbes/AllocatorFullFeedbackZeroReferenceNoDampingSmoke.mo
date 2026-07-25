within MoSimQuadrotorModel.ExperimentRunner.InternalProbes;
model AllocatorFullFeedbackZeroReferenceNoDampingSmoke
  "Diagnostic only: remove roll/pitch derivative action from the shared allocator"

  extends AllocatorFullFeedbackZeroReferenceSmoke(
    allocator(kd_attitude = 0));

  annotation(__MWORKS(version = "26.3.0"));
end AllocatorFullFeedbackZeroReferenceNoDampingSmoke;
