within MoSimQuadrotorModel.Experiment.Probes;
model OfficialPidFixedZeroInputPlantSmoke
  "Diagnostic: official PID topology with fixed zero inputs on the shared plant"

  MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter controller;
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant;
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real rotor_speed[4];

equation
  controller.position_ref = {0.0, 0.0, 0.0};
  controller.position_mea = {0.0, 0.0, 0.0};
  controller.velocity_mea = {0.0, 0.0, 0.0};
  controller.attitude_mea = {0.0, 0.0, 0.0};
  connect(controller.rotor_command, plant.rotor_command);

  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;
  rotor_speed = plant.rotor_speed;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.002, Tolerance = 0.0001,
      Interval = 0.00001),
    __MWORKS(version = "26.3.0"));
end OfficialPidFixedZeroInputPlantSmoke;