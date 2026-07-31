within MoSimQuadrotorModel.Guidance;
package Planning
  "Direct planning references and obstacle-scene models"

  extends Modelica.Icons.Package;

  model QuinticReference
    "Quintic polynomial planning reference"
    extends MoSimQuadrotorModel.Guidance.Planning.PlannedQuinticReference;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end QuinticReference;

  model NavigationDisplay
    "Planning, navigation, and local-map review support"
    extends MoSimQuadrotorModel.Guidance.Planning.PlanningNavigationDisplay;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end NavigationDisplay;

  model OpenBlocksAWFF
    "Open-block obstacle field with AWFF planning closure"
    extends MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksAWFF;

  model OpenBlocksLinearMPC
    "Open-block obstacle field with linear-MPC planning closure"
    extends MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksLinearMPC;

  model OpenBlocksPx4Ctrl
    "Open-block obstacle field with PX4CTRL A* path tracking"
    extends MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksPx4Ctrl;

  model OpenBlocksSingleUavMapAudit
    "OpenBlocks 单机全局地图与局部感知叠加审查"
    extends MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningOpenBlocksSingleUavMapAudit;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksSingleUavMapAudit;

  model OpenBlocksColorMapReview
    "Open-block obstacle field color-map review"
    extends MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningOpenBlocksColorMapReview;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksColorMapReview;

  model OpenBlocksThreeUavFormation
    "Open-block obstacle field with reconfigurable three-UAV formation"
    extends MoSimQuadrotorModel.Guidance.Planning.ThreeUavOpenBlocksReconfigurableFormationLinearMPC;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksThreeUavFormation;

  model OpenBlocksThreeUavPx4CtrlFormation
    "OpenBlocks 三机 PX4CTRL 轨迹跟踪与地图审查入口"
    extends MoSimQuadrotorModel.Guidance.Planning.ThreeUavOpenBlocksReconfigurableFormationPx4Ctrl;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksThreeUavPx4CtrlFormation;

  model OpenBlocksThreeUavPx4CtrlFormationEcbfSafety
    "OpenBlocks 三机 PX4CTRL 与两两 ECBF 参考安全层对照入口"
    extends MoSimQuadrotorModel.Guidance.Planning.ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksThreeUavPx4CtrlFormationEcbfSafety;

  model CorridorGateAWFF
    "Corridor-gate obstacle field with AWFF planning closure"
    extends MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningCorridorGateAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end CorridorGateAWFF;

  model CorridorGateLinearMPC
    "Corridor-gate obstacle field with linear-MPC planning closure"
    extends MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end CorridorGateLinearMPC;

  annotation(__MWORKS(version="26.3.0"));
end Planning;
