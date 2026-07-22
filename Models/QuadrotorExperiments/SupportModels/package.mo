within QuadrotorExperiments;
package SupportModels
  // Deprecated compatibility facade; active implementation lives under MoSimQuadrotorModel.
  "支撑模型、表格引用与 echo 状态烟测"
  extends Modelica.Icons.Package;

  model TraceInline
    "内联轨迹引用"
    extends MoSimQuadrotorModel.Support.Models.TraceInlineReference;
    annotation(__MWORKS(hide=true));
  end TraceInline;

  model TraceTable
    "轨迹表引用"
    extends MoSimQuadrotorModel.Support.Models.TraceTableReference;
    annotation(__MWORKS(hide=true));
  end TraceTable;

  model TraceLookupStandalone
    "轨迹查表独立烟测"
    extends MoSimQuadrotorModel.Support.Models.TraceLookupStandaloneSmoke;
    annotation(__MWORKS(hide=true));
  end TraceLookupStandalone;

  model EchoMcpState
    "MWORKS MCP echo 状态烟测"
    extends MoSimQuadrotorModel.Support.Models.EchoMcpStateSmoke;
    annotation(__MWORKS(hide=true));
  end EchoMcpState;
  annotation(__MWORKS(hide=true));

end SupportModels;