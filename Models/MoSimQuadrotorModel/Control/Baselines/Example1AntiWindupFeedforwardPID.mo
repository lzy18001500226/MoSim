within MoSimQuadrotorModel.Control.Baselines;
model Example1AntiWindupFeedforwardPID
  "Example1 with project-owned anti-windup and reference-feedforward controller"
  extends Example1ProjectControllerBase;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Example1AntiWindupFeedforwardPID;