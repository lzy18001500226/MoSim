within MoSimQuadrotorModel.Common;
package Models
  "支撑模型、表格引用与 echo 状态烟测"
  extends Modelica.Icons.Package;

  model TraceInline
    "内联轨迹引用"
    extends MoSimQuadrotorModel.Common.Models.TraceInlineReference;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end TraceInline;

  model TraceTable
    "轨迹表引用"
    extends MoSimQuadrotorModel.Common.Models.TraceTableReference;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end TraceTable;

  model TraceLookupStandalone
    "轨迹查表独立烟测"
    extends MoSimQuadrotorModel.Common.Models.TraceLookupStandaloneSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end TraceLookupStandalone;

  model EchoMcpState
    "MWORKS MCP echo 状态烟测"
    extends MoSimQuadrotorModel.Common.Models.EchoMcpStateSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end EchoMcpState;
  annotation(__MWORKS(version="26.3.0"));

end Models;
