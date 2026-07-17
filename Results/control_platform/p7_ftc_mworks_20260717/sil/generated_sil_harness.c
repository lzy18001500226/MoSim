#include <stdio.h>
#include "MoSim_P7_FaultTolerantControl_CFunction_Sysblock.h"
#include "MoSim_P7_FaultTolerantControl_CFunction_Sysblock_private.h"
static void run_case(int id) {
  int step;
  if(id==1) {
    ol_cfunction_sysblockGbIn.mode_id_in=1;
    ol_cfunction_sysblockGbIn.dt_in=0.01;
    ol_cfunction_sysblockGbIn.desired_thrust_in=2.3999999999999999;
    ol_cfunction_sysblockGbIn.desired_roll_in=0.040000000000000001;
    ol_cfunction_sysblockGbIn.desired_pitch_in=-0.029999999999999999;
    ol_cfunction_sysblockGbIn.desired_yaw_in=0.02;
    ol_cfunction_sysblockGbIn.response_1_in=0.3135;
    ol_cfunction_sysblockGbIn.response_2_in=0.59999999999999998;
    ol_cfunction_sysblockGbIn.response_3_in=0.64000000000000001;
    ol_cfunction_sysblockGbIn.response_4_in=0.58999999999999997;
    ol_cfunction_sysblockGbIn.airborne_in=1;
    ol_cfunction_sysblockGbIn.altitude_in=1.2;
    ol_cfunction_sysblockGbIn.enable_in=1;
    ol_cfunction_sysblockGbIn.reset_in=0;
  }
  if(id==2) {
    ol_cfunction_sysblockGbIn.mode_id_in=2;
    ol_cfunction_sysblockGbIn.dt_in=0.01;
    ol_cfunction_sysblockGbIn.desired_thrust_in=2.3999999999999999;
    ol_cfunction_sysblockGbIn.desired_roll_in=0.040000000000000001;
    ol_cfunction_sysblockGbIn.desired_pitch_in=-0.029999999999999999;
    ol_cfunction_sysblockGbIn.desired_yaw_in=0.02;
    ol_cfunction_sysblockGbIn.response_1_in=0.42749999999999999;
    ol_cfunction_sysblockGbIn.response_2_in=0.59999999999999998;
    ol_cfunction_sysblockGbIn.response_3_in=0.64000000000000001;
    ol_cfunction_sysblockGbIn.response_4_in=0.58999999999999997;
    ol_cfunction_sysblockGbIn.airborne_in=1;
    ol_cfunction_sysblockGbIn.altitude_in=1.2;
    ol_cfunction_sysblockGbIn.enable_in=1;
    ol_cfunction_sysblockGbIn.reset_in=0;
  }
  if(id==3) {
    ol_cfunction_sysblockGbIn.mode_id_in=3;
    ol_cfunction_sysblockGbIn.dt_in=0.01;
    ol_cfunction_sysblockGbIn.desired_thrust_in=2.3999999999999999;
    ol_cfunction_sysblockGbIn.desired_roll_in=0.040000000000000001;
    ol_cfunction_sysblockGbIn.desired_pitch_in=-0.029999999999999999;
    ol_cfunction_sysblockGbIn.desired_yaw_in=0.02;
    ol_cfunction_sysblockGbIn.response_1_in=0.56999999999999995;
    ol_cfunction_sysblockGbIn.response_2_in=0.33000000000000002;
    ol_cfunction_sysblockGbIn.response_3_in=0.64000000000000001;
    ol_cfunction_sysblockGbIn.response_4_in=0.58999999999999997;
    ol_cfunction_sysblockGbIn.airborne_in=1;
    ol_cfunction_sysblockGbIn.altitude_in=1.2;
    ol_cfunction_sysblockGbIn.enable_in=1;
    ol_cfunction_sysblockGbIn.reset_in=0;
  }
  if(id==4) {
    ol_cfunction_sysblockGbIn.mode_id_in=4;
    ol_cfunction_sysblockGbIn.dt_in=0.01;
    ol_cfunction_sysblockGbIn.desired_thrust_in=2.3999999999999999;
    ol_cfunction_sysblockGbIn.desired_roll_in=0.040000000000000001;
    ol_cfunction_sysblockGbIn.desired_pitch_in=-0.029999999999999999;
    ol_cfunction_sysblockGbIn.desired_yaw_in=0.02;
    ol_cfunction_sysblockGbIn.response_1_in=0.56999999999999995;
    ol_cfunction_sysblockGbIn.response_2_in=0.59999999999999998;
    ol_cfunction_sysblockGbIn.response_3_in=0.35199999999999998;
    ol_cfunction_sysblockGbIn.response_4_in=0.58999999999999997;
    ol_cfunction_sysblockGbIn.airborne_in=1;
    ol_cfunction_sysblockGbIn.altitude_in=1.2;
    ol_cfunction_sysblockGbIn.enable_in=1;
    ol_cfunction_sysblockGbIn.reset_in=0;
  }
  if(id==5) {
    ol_cfunction_sysblockGbIn.mode_id_in=5;
    ol_cfunction_sysblockGbIn.dt_in=0.01;
    ol_cfunction_sysblockGbIn.desired_thrust_in=2.3999999999999999;
    ol_cfunction_sysblockGbIn.desired_roll_in=0.040000000000000001;
    ol_cfunction_sysblockGbIn.desired_pitch_in=-0.029999999999999999;
    ol_cfunction_sysblockGbIn.desired_yaw_in=0.02;
    ol_cfunction_sysblockGbIn.response_1_in=0.56999999999999995;
    ol_cfunction_sysblockGbIn.response_2_in=0.59999999999999998;
    ol_cfunction_sysblockGbIn.response_3_in=0.64000000000000001;
    ol_cfunction_sysblockGbIn.response_4_in=0.11799999999999999;
    ol_cfunction_sysblockGbIn.airborne_in=1;
    ol_cfunction_sysblockGbIn.altitude_in=1.2;
    ol_cfunction_sysblockGbIn.enable_in=1;
    ol_cfunction_sysblockGbIn.reset_in=0;
  }
  if(id==6) {
    ol_cfunction_sysblockGbIn.mode_id_in=6;
    ol_cfunction_sysblockGbIn.dt_in=0.01;
    ol_cfunction_sysblockGbIn.desired_thrust_in=2.3999999999999999;
    ol_cfunction_sysblockGbIn.desired_roll_in=0.040000000000000001;
    ol_cfunction_sysblockGbIn.desired_pitch_in=-0.029999999999999999;
    ol_cfunction_sysblockGbIn.desired_yaw_in=0.02;
    ol_cfunction_sysblockGbIn.response_1_in=0.3135;
    ol_cfunction_sysblockGbIn.response_2_in=0.59999999999999998;
    ol_cfunction_sysblockGbIn.response_3_in=0.38400000000000001;
    ol_cfunction_sysblockGbIn.response_4_in=0.58999999999999997;
    ol_cfunction_sysblockGbIn.airborne_in=1;
    ol_cfunction_sysblockGbIn.altitude_in=1.2;
    ol_cfunction_sysblockGbIn.enable_in=1;
    ol_cfunction_sysblockGbIn.reset_in=0;
  }
  Init(); for(step=0;step<80;++step) Step();
  printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
    id,0,rol_cfunction_sysblockGbOut.motor_command_1_out,rol_cfunction_sysblockGbOut.motor_command_2_out,rol_cfunction_sysblockGbOut.motor_command_3_out,rol_cfunction_sysblockGbOut.motor_command_4_out,rol_cfunction_sysblockGbOut.eta_hat_1_out,rol_cfunction_sysblockGbOut.eta_hat_2_out,rol_cfunction_sysblockGbOut.eta_hat_3_out,rol_cfunction_sysblockGbOut.eta_hat_4_out,rol_cfunction_sysblockGbOut.achieved_thrust_out,rol_cfunction_sysblockGbOut.achieved_roll_out,rol_cfunction_sysblockGbOut.achieved_pitch_out,rol_cfunction_sysblockGbOut.achieved_yaw_out,rol_cfunction_sysblockGbOut.residual_norm_out,rol_cfunction_sysblockGbOut.isolated_mask_out,rol_cfunction_sysblockGbOut.fault_count_out,rol_cfunction_sysblockGbOut.action_out,rol_cfunction_sysblockGbOut.allocation_saturated_out,rol_cfunction_sysblockGbOut.status_code_out);
}
int main(void) { int id; for(id=1;id<=6;++id) run_case(id); return 0; }
