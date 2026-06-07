within QuadrotorExperiments.OfficialScenarios;
model Example2HelixTunedAWFFSysblockClosedLoop
  "Example2 plant with helix-tuned project AWFF Sysblock controller"
  extends Example2AWFFSysblockClosedLoop(
    controller3_2(
      roll_pitch_cmd_limit = 15 / 57.3,
      attitude_cmd_limit = 7.0,
      yaw_cmd_limit = 7.0));
  annotation(__MWORKS(hide=true));
end Example2HelixTunedAWFFSysblockClosedLoop;
