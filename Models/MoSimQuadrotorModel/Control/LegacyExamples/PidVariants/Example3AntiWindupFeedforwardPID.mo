within MoSimQuadrotorModel.Control.LegacyExamples.PidVariants;
model Example3AntiWindupFeedforwardPID
  "Example3 with project-owned anti-windup and reference-feedforward controller"
  extends Example3ProjectControllerBase;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Example3AntiWindupFeedforwardPID;
