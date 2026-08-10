within MoSimQuadrotorModel.Experiment.Runners.Golden;
package NativeSysblockScenarios
  "Package-local profile runners for the native Official PID Sysblock route"

  extends Modelica.Icons.Package;

  model Hover
    "Native Sysblock Official PID under the authorized Hover profile"

    extends OfficialPidSysblockSingleUavRunner(
      redeclare model Trajectory =
        MoSimQuadrotorModel.Guidance.Trajectories.HoverHold(
          target_altitude_m = 2,
          takeoff_duration_s = 5,
          hold_duration_s = 30),
      gust_force = {0, 0, 0},
      gust_start_s = 0,
      gust_duration_s = 0,
      mass_scale = 1,
      inertia_scale = {1, 1, 1},
      rotor_effectiveness = {1, 1, 1, 1},
      fault_start_s = 1000000000,
      fault_rotor_index = 1,
      fault_rotor_effectiveness = 1);

    Real injection_gust_force_N[3](each unit = "N");
    Real injection_plant_mass_kg(unit = "kg");
    Real injection_plant_inertia_diagonal_kg_m2[3](each unit = "kg.m2");
    Real injection_fault_effectiveness[4];

  equation
    injection_gust_force_N = plant.gust.force;
    injection_plant_mass_kg = plant.physical.wrapper.dynamics.mass_kg;
    injection_plant_inertia_diagonal_kg_m2 = {
      plant.physical.body.I_11,
      plant.physical.body.I_22,
      plant.physical.body.I_33};
    injection_fault_effectiveness = plant.physical.wrapper.dynamics.fault_effectiveness;

    annotation(
      experiment(Algorithm = Dassl, StartTime = 0, StopTime = 35,
        Tolerance = 0.0001, Interval = 0.01),
      __MWORKS(version = "26.3.0"));
  end Hover;
end NativeSysblockScenarios;