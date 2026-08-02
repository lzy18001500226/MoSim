within MoSimQuadrotorModel.Experiment;
model CompleteSystemGraphical
  "Direct graphical formal entry for the px4ctrl Sunray150 whole-aircraft closure"

  extends MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlFormalRunner;

  annotation(
    Documentation(info = "<html><p>Graphical entry for the active px4ctrl FormalRunner chain. The diagram inherits the same trajectory, sampled controller boundary, offline allocator, Sunray150Assembly plant, and feedback path used by <code>Px4CtrlFormalRunner</code>.</p></html>"),
    __MWORKS(hide=false,version="26.3.0"));
end CompleteSystemGraphical;
