within MoSimQuadrotorModel.Control.Implementations.Sysblocks;
model AWFF_FaultCompensationControllerEquation_Sysblock
  "AWFF controller with known rotor-1 efficiency allocation compensation"
  extends AWFF_L1FaultAllocationControllerEquation_Sysblock(
    l1_gain_xy = 0,
    l1_gain_z = 0,
    l1_comp_limit_xy = 0,
    l1_comp_limit_z = 0,
    rotor1_efficiency = 0.85,
    rotor1_allocation_blend = 0.52);
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-320,-220},{280,220}},grid={2,2})));
end AWFF_FaultCompensationControllerEquation_Sysblock;