#include "pid_attitude_thrust_core.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

static void run_case(int algorithm, int dynamic) {
  MosimPidAttitudeThrustParams p;
  MosimPidAttitudeThrustState s = {0};
  MosimPidAttitudeThrustInput i = {0};
  MosimPidAttitudeThrustOutput o;
  mosim_pid_attitude_thrust_default_params(algorithm, &p);
  i.algorithm_id = algorithm; i.dt = 0.01; i.enable = 1; i.reset = 1;
  i.attitude_enu_flu_wxyz.w = 1.0;
  if (dynamic) {
    i.reference_position_enu_m.x = 1.0; i.reference_position_enu_m.y = -0.5; i.reference_position_enu_m.z = 0.8;
    i.reference_velocity_enu_mps.x = 0.2; i.reference_velocity_enu_mps.y = -0.1;
    i.reference_acceleration_enu_mps2.x = 0.6; i.reference_acceleration_enu_mps2.y = -0.3; i.reference_acceleration_enu_mps2.z = 0.2;
    i.reference_yaw_enu_rad = 0.3;
    i.schedule.x = 0.5; i.schedule.y = 0.4; i.schedule.z = 0.3;
    i.fuzzy_error.x = 0.4; i.fuzzy_error.y = -0.3; i.fuzzy_error.z = 0.2;
    i.neural_residual.x = 0.1; i.neural_residual.y = -0.2; i.neural_residual.z = 0.3;
  }
  mosim_pid_attitude_thrust_step(&p, &s, &i, &o);
  printf("case,%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d,%.17g\n",
    algorithm, dynamic, o.desired_attitude_enu_flu_wxyz.w, o.desired_attitude_enu_flu_wxyz.x,
    o.desired_attitude_enu_flu_wxyz.y, o.desired_attitude_enu_flu_wxyz.z,
    o.desired_collective_thrust_n, o.desired_acceleration_enu_mps2.x,
    o.desired_acceleration_enu_mps2.y, o.desired_acceleration_enu_mps2.z,
    o.status_code, o.saturated, o.scheduled_gain.x);
}

int main(void) {
  int algorithm;
  MosimPidAttitudeThrustParams p;
  MosimPidAttitudeThrustState s = {0};
  MosimPidAttitudeThrustInput i = {0};
  MosimPidAttitudeThrustOutput first, second, reset, disabled, invalid, mismatch;
  for (algorithm = 1; algorithm <= 6; ++algorithm) { run_case(algorithm, 0); run_case(algorithm, 1); }
  mosim_pid_attitude_thrust_default_params(1, &p);
  i.algorithm_id=1; i.dt=0.01; i.enable=1; i.attitude_enu_flu_wxyz.w=1.0; i.reference_position_enu_m.x=1.0;
  mosim_pid_attitude_thrust_step(&p,&s,&i,&first);
  mosim_pid_attitude_thrust_step(&p,&s,&i,&second);
  i.reset=1; mosim_pid_attitude_thrust_step(&p,&s,&i,&reset);
  i.reset=0; i.enable=0; mosim_pid_attitude_thrust_step(&p,&s,&i,&disabled);
  i.enable=1; i.dt=0.0; mosim_pid_attitude_thrust_step(&p,&s,&i,&invalid);
  i.dt=0.01; p.algorithm_id=2; mosim_pid_attitude_thrust_step(&p,&s,&i,&mismatch);
  printf("lifecycle,%.17g,%.17g,%.17g,%d,%.17g,%d,%.17g,%d,%.17g\n", first.desired_collective_thrust_n,
    second.desired_collective_thrust_n, reset.desired_collective_thrust_n, disabled.status_code,
    disabled.desired_collective_thrust_n, invalid.status_code, invalid.desired_collective_thrust_n,
    mismatch.status_code, mismatch.desired_collective_thrust_n);
  return 0;
}
