within MoSimQuadrotorModel.Guidance.Trajectories;
model MotorFault
  "ClimbPath reference with one rotor reduced to 50 percent effectiveness"

  extends MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath;
  parameter Integer failed_rotor_index(min = 1, max = 4) = 1;
  parameter Real failed_rotor_effectiveness(min = 0, max = 1) = 0.5;
  parameter Real rotor_effectiveness[4] = {
    if failed_rotor_index == 1 then failed_rotor_effectiveness else 1,
    if failed_rotor_index == 2 then failed_rotor_effectiveness else 1,
    if failed_rotor_index == 3 then failed_rotor_effectiveness else 1,
    if failed_rotor_index == 4 then failed_rotor_effectiveness else 1}
    "Effectiveness vector read by a Runner when this scenario is bound";

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end MotorFault;
