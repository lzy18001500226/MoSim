within MoSimQuadrotorModel;
package SceneTrace
  "UE场景trace与显示隔离（Factory、Derelict、trace隔离模型）"

  package AcceptedScenes
    "已接入UE场景的闭环或烟测入口"
    extends QuadrotorExperiments.SceneTraceScenarios;
  end AcceptedScenes;

  package Isolation
    "trace隔离与逐层接线诊断入口"
    extends QuadrotorExperiments.TraceIsolation;
  end Isolation;
end SceneTrace;
