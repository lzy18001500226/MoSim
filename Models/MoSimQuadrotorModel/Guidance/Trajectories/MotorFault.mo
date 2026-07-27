within MoSimQuadrotorModel.Guidance.Trajectories;
model MotorFault
  "ClimbPath reference with one rotor reduced to 50 percent effectiveness"

  extends MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath;
  parameter Real fault_start_s(unit = "s") = 15
    "The Runner binds this scheduled fault time into the physical plant";
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 0.5;

  // This reference model deliberately does not expose a static effectiveness
  // vector. The Runner passes the scheduled values to RotorActuatorCore so the
  // selected rotor remains nominal before t = fault_start_s.

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end MotorFault;
