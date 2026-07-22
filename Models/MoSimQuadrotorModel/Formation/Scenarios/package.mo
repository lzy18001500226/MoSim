within MoSimQuadrotorModel.Formation;
package Scenarios
  "多机编队场景（后续扩展入口）"
  extends Modelica.Icons.Package;

  model TriangleFigure8LinearMPC
    "三机三角编队 8 字：线性 MPC 闭环"
    extends MoSimQuadrotorModel.Formation.Scenarios.FormationTriangleFigure8LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false));
  end TriangleFigure8LinearMPC;

end Scenarios;
