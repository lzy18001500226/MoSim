package MoSimQuadrotorModel
  "MoSim正式四旋翼模型包（Sunray150主线、基线适配、动力学升级和实验迁移入口）"

  extends Modelica.Icons.Package;
  annotation(uses(
    Modelica(version = "4.0.0.TY.1"),
    QuadrotorModel,
    QuadrotorExperiments,
    QuadrotorControllerBlocks));
end MoSimQuadrotorModel;
