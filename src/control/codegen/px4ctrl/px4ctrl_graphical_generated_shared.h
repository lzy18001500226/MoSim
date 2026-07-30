#ifndef MOSIM_PX4CTRL_GRAPHICAL_GENERATED_SHARED_H
#define MOSIM_PX4CTRL_GRAPHICAL_GENERATED_SHARED_H

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Scalar C ABI for the generated 100 Hz px4ctrl graphical outer loop.
 * Every output pointer must reference writable storage.
 */
void MosimPx4ctrlGeneratedGraphStepScalar(
  double ref_px,
  double px,
  double ref_vx,
  double vx,
  double ref_ax,
  double ref_py,
  double py,
  double ref_vy,
  double vy,
  double ref_ay,
  double ref_pz,
  double pz,
  double ref_vz,
  double vz,
  double ref_az,
  double yaw_mea,
  double ref_yaw,
  double *desired_acc_x,
  double *desired_acc_y,
  double *desired_acc_z,
  double *roll_cmd,
  double *pitch_cmd,
  double *yaw_cmd,
  double *collective_thrust_n,
  double *normalized_thrust);

#ifdef __cplusplus
}
#endif

#endif
