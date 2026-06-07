within QuadrotorExperiments;
package SupportModels
  "支撑模型、表格引用与 echo 状态烟测"
  extends Modelica.Icons.Package;

  model TraceInline
    "内联轨迹引用"
    extends QuadrotorExperiments.SupportModels.TraceInlineReference;
    annotation(__MWORKS(hide=false));
  end TraceInline;

  model TraceTable
    "轨迹表引用"
    extends QuadrotorExperiments.SupportModels.TraceTableReference;
    annotation(__MWORKS(hide=false));
  end TraceTable;

  model TraceLookupStandalone
    "轨迹查表独立烟测"
    extends QuadrotorExperiments.SupportModels.TraceLookupStandaloneSmoke;
    annotation(__MWORKS(hide=false));
  end TraceLookupStandalone;

  model EchoMcpState
    "MWORKS MCP echo 状态烟测"
    extends QuadrotorExperiments.SupportModels.EchoMcpStateSmoke;
    annotation(__MWORKS(hide=false));
  end EchoMcpState;

end SupportModels;
