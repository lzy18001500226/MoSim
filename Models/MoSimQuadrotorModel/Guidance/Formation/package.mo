within MoSimQuadrotorModel.Guidance;
package Formation
  "Formation references and historical LinearMPC prototype; the formal PX4CTRL three-UAV runner is under Experiment.Runners.Formation"

  extends Modelica.Icons.Package;

  model TriangleFigure8LinearMPC
    "Three-UAV leader-follower triangle tracking a planar figure-8 with LinearMPC"
    extends MoSimQuadrotorModel.Guidance.Formation.FormationTriangleFigure8LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end TriangleFigure8LinearMPC;

  annotation(__MWORKS(version="26.3.0"));
end Formation;
