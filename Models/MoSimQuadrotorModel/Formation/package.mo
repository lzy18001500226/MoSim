within MoSimQuadrotorModel;
package Formation
  "编队场景（后续P2多机扩展入口）"

  extends Modelica.Icons.Package;

  model TriangleFigure8LinearMPC
    "三机三角编队 8 字：线性 MPC 闭环"
    extends QuadrotorExperiments.FormationScenarios.TriangleFigure8LinearMPC;
    annotation(__MWORKS(hide=false));
  end TriangleFigure8LinearMPC;
end Formation;
