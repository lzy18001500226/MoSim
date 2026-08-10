within MoSimQuadrotorModel.Control.LegacyExamples.PidVariants;
model Example2AntiWindupFeedforwardPID
  "Example2 with project-owned anti-windup and reference-feedforward controller"
  extends Example2ProjectControllerBase;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Example2AntiWindupFeedforwardPID;