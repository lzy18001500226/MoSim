within MoSimQuadrotorModel.Experiment.Runners.Formal;
model OfficialPidSysblockAttitudeThrustFormalRunner
  "Formal whole-aircraft runner with the native Official PID Sysblock outer loop"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller =
      MoSimQuadrotorModel.Control.Adapters.OfficialPidSysblockAttitudeThrustAdapter);

  annotation(
    Documentation(info = "<html><p>MWORKS-only formal runner for the graphical Official PID outer-loop adapter. The graphical Sysblock owns roll, pitch, and collective command generation; the existing offline inner allocator closes the physical plant at the shared <code>ATTITUDE_THRUST</code> boundary.</p><p>This proves neither RT1 takeover nor Gazebo/PX4 flight. RT1 remains shadow-only until its separate transport and runtime gates pass.</p></html>"),
    __MWORKS(version = "26.3.0"));
end OfficialPidSysblockAttitudeThrustFormalRunner;
