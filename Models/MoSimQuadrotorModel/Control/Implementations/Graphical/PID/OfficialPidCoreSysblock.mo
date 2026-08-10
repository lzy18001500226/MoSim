within MoSimQuadrotorModel.Control.Implementations.Graphical.PID;
model OfficialPidCoreSysblock
  "Strict graphical registration of the verified Official PID block network"

  extends MoSimQuadrotorModel.Vehicle.Blocks.Controller.Controller;
  extends ModelWorkspace;

  annotation(
    __MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),
    experiment(
      Algorithm=Euler,
      Interval=0.01,
      IntegratorStep=0.01,
      StartTime=0,
      StopTime=50,
      StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
end OfficialPidCoreSysblock;