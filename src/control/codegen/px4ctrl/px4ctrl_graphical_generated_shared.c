/*
 * MWORKS exports generic Init/Step symbols.  The ROS adapter still links its
 * dormant legacy CFunction implementation for compatibility with existing
 * non-graphical profiles, so give this graphical instance private symbols.
 */
#define Init MosimPx4ctrlGraphicalGeneratedInit
#define Step MosimPx4ctrlGraphicalGeneratedStep
#include "mwb_types.h"
#include "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.h"
#include "PX4CTRL_Original_OuterLoop_Graphical_Sysblock_private.h"
#include "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.c"
#undef Step
#undef Init

#if defined(_WIN32)
#define MOSIM_PX4CTRL_EXPORT __declspec(dllexport)
#else
#define MOSIM_PX4CTRL_EXPORT __attribute__((visibility("default")))
#endif

MOSIM_PX4CTRL_EXPORT void MosimPx4ctrlGeneratedGraphStepScalar(
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
  double *normalized_thrust)
{
  static int mosim_px4ctrl_generated_initialized = 0;
  if (!mosim_px4ctrl_generated_initialized) {
    MosimPx4ctrlGraphicalGeneratedInit();
    mosim_px4ctrl_generated_initialized = 1;
  }
  graphical_sysblockGbIn.ref_px = ref_px;
  graphical_sysblockGbIn.px = px;
  graphical_sysblockGbIn.ref_vx = ref_vx;
  graphical_sysblockGbIn.vx = vx;
  graphical_sysblockGbIn.ref_ax = ref_ax;
  graphical_sysblockGbIn.ref_py = ref_py;
  graphical_sysblockGbIn.py = py;
  graphical_sysblockGbIn.ref_vy = ref_vy;
  graphical_sysblockGbIn.vy = vy;
  graphical_sysblockGbIn.ref_ay = ref_ay;
  graphical_sysblockGbIn.ref_pz = ref_pz;
  graphical_sysblockGbIn.pz = pz;
  graphical_sysblockGbIn.ref_vz = ref_vz;
  graphical_sysblockGbIn.vz = vz;
  graphical_sysblockGbIn.ref_az = ref_az;
  graphical_sysblockGbIn.yaw_mea = yaw_mea;
  graphical_sysblockGbIn.ref_yaw = ref_yaw;
  MosimPx4ctrlGraphicalGeneratedStep();
  *desired_acc_x = agraphical_sysblockGbOut.desired_acc_x;
  *desired_acc_y = agraphical_sysblockGbOut.desired_acc_y;
  *desired_acc_z = agraphical_sysblockGbOut.desired_acc_z;
  *roll_cmd = agraphical_sysblockGbOut.roll_cmd;
  *pitch_cmd = agraphical_sysblockGbOut.pitch_cmd;
  *yaw_cmd = agraphical_sysblockGbOut.yaw_cmd;
  *collective_thrust_n = agraphical_sysblockGbOut.collective_thrust_n;
  *normalized_thrust = agraphical_sysblockGbOut.normalized_thrust;
}
