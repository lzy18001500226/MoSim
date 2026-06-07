within QuadrotorExperiments.ControllerBaselines;
model Example1AntiWindupFeedforwardPID
  "Example1 with project-owned anti-windup and reference-feedforward controller"
  extends Example1ProjectControllerBase;
  annotation(__MWORKS(hide=true));
end Example1AntiWindupFeedforwardPID;
