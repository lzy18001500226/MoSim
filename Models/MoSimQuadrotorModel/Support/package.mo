within MoSimQuadrotorModel;
package Support
  "支撑模型（trace引用、查询、MCP回声和共享工具模型）"

  extends Modelica.Icons.Package;

  model TraceInline
    "内联轨迹引用"
    extends QuadrotorExperiments.SupportModels.TraceInline;
    annotation(__MWORKS(hide=false));
  end TraceInline;

  model TraceTable
    "轨迹表引用"
    extends QuadrotorExperiments.SupportModels.TraceTable;
    annotation(__MWORKS(hide=false));
  end TraceTable;

  model TraceLookupStandalone
    "轨迹查表独立烟测"
    extends QuadrotorExperiments.SupportModels.TraceLookupStandalone;
    annotation(__MWORKS(hide=false));
  end TraceLookupStandalone;

  model EchoMcpState
    "MWORKS MCP echo 状态烟测"
    extends QuadrotorExperiments.SupportModels.EchoMcpState;
    annotation(__MWORKS(hide=false));
  end EchoMcpState;
end Support;
