within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorOfficialPidDynamicParityOfficialDerivativeProbe
  "Dynamic parity probe with the official PID derivative time constant"

  extends AllocatorOfficialPidDynamicParityProbe(
    offline_derivative_time_constant_s = 0.01);

  annotation(__MWORKS(version = "26.3.0"));
end AllocatorOfficialPidDynamicParityOfficialDerivativeProbe;
