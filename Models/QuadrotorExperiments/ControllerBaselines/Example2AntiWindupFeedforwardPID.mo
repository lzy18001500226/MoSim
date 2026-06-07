within QuadrotorExperiments.ControllerBaselines;
model Example2AntiWindupFeedforwardPID
  "Example2 with project-owned anti-windup and reference-feedforward controller"
  extends Example2ProjectControllerBase;
  annotation(__MWORKS(hide=true));
end Example2AntiWindupFeedforwardPID;
