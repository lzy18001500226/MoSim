within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorFullFeedbackZeroReferenceYawDisabledSmoke
  "Diagnostic only: remove yaw correction while retaining shared roll/pitch feedback"

  extends AllocatorFullFeedbackZeroReferenceSmoke(
    allocator(kp_yaw = 0));

  annotation(__MWORKS(version = "26.3.0"));
end AllocatorFullFeedbackZeroReferenceYawDisabledSmoke;
