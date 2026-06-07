within MoSimQuadrotorModel;
package LegacyCompatibility
  "历史兼容入口（旧QuadrotorExperiments全量别名，禁止作为新模型主入口）"

  extends QuadrotorExperiments;

  package LegacyExperimentPool
    "旧 QuadrotorExperiments 全量入口聚合；仅用于历史脚本和证据兼容"
    extends QuadrotorExperiments;
    annotation(__MWORKS(hide=false));
  end LegacyExperimentPool;
end LegacyCompatibility;
