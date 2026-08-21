within MoSimQuadrotorModel.Experiment.OpenBlocks.LinearMpc.Formation;
model ThreeUavOpenBlocksLinearMPCRunner
  "Three-UAV LinearMPC runner using synchronized OpenBlocks references"
  extends MoSimQuadrotorModel.Guidance.Planning.ThreeUavOpenBlocksReconfigurableFormationLinearMPC;
  annotation(__MWORKS(version="26.3.0"));
end ThreeUavOpenBlocksLinearMPCRunner;