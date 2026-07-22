within MoSimQuadrotorModel.Controllers.Baselines;
model Example3AntiWindupFeedforwardPID
  "Example3 with project-owned anti-windup and reference-feedforward controller"
  extends Example3ProjectControllerBase;
  annotation(__MWORKS(hide=true));
end Example3AntiWindupFeedforwardPID;
