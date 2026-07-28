within ;
model SevenScenarioAB_OfficialPid_WindDisturbance
  "Ephemeral evidence harness for official_pid/wind_disturbance"

  extends MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner(
    redeclare model Trajectory = MoSimQuadrotorModel.Guidance.Trajectories.WindDisturbance(gust_force = {0.25, 0, 0}, gust_start_s = 0, gust_duration_s = 50),
    gust_force = {0.25, 0, 0},
    gust_start_s = 0,
    gust_duration_s = 50,
    mass_scale = 1,
    inertia_scale = {1, 1, 1},
    rotor_effectiveness = {1, 1, 1, 1},
    fault_start_s = 1000000000,
    fault_rotor_index = 1,
    fault_rotor_effectiveness = 1);

  // Export internal Plant state used to validate the profile injection.
  Real injection_gust_force_N[3](each unit = "N");
  Real injection_plant_mass_kg(unit = "kg");
  Real injection_controller_nominal_mass_kg(unit = "kg");
  Real injection_fault_effectiveness[4];

equation
  injection_gust_force_N = plant.gust.force;
  injection_plant_mass_kg = plant.physical.wrapper.dynamics.mass_kg;
  injection_controller_nominal_mass_kg = controller.profile.takeoff_mass_kg;
  injection_fault_effectiveness = plant.physical.wrapper.dynamics.fault_effectiveness;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end SevenScenarioAB_OfficialPid_WindDisturbance;
