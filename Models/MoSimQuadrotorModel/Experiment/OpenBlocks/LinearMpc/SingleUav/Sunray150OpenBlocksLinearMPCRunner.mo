within MoSimQuadrotorModel.Experiment.OpenBlocks.LinearMpc.SingleUav;
model Sunray150OpenBlocksLinearMPCRunner
  "Single-UAV LinearMPC runner using the frozen OpenBlocks reference"
  extends MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;
  annotation(__MWORKS(version="26.3.0"));
end Sunray150OpenBlocksLinearMPCRunner;