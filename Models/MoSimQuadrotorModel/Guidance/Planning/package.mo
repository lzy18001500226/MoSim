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
