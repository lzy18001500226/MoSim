within QuadrotorExperiments.ControllerBaselines;
model Example2HelixTunedAntiWindupFeedforwardPID
  "Example2 AWFF PID with helix-specific lateral command authority"
  extends Example2ProjectControllerBase(
    controller3_2(
      roll_pitch_cmd_limit = 15 / 57.3,
      attitude_cmd_limit = 7.0,
      yaw_cmd_limit = 7.0));
  annotation(__MWORKS(hide=true));
end Example2HelixTunedAntiWindupFeedforwardPID;
