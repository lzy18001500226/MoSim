within MoSimQuadrotorModel.Formation;
package Scenarios
  "多机编队场景（后续扩展入口）"
  extends Modelica.Icons.Package;

  model TriangleFigure8LinearMPC
    "三机三角编队 8 字：线性 MPC 闭环"
    extends MoSimQuadrotorModel.Formation.Scenarios.FormationTriangleFigure8LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end TriangleFigure8LinearMPC;
  annotation(__MWORKS(version="26.3.0"));

end Scenarios;