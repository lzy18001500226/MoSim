#include <stdio.h>
#include "MoSim_P8_FormationControl_CFunction_Sysblock.h"
#include "MoSim_P8_FormationControl_CFunction_Sysblock_private.h"
static void run_case(int id) {
  int step;
  function_sysblockGbIn.mode_id_in=(double)id;
  function_sysblockGbIn.dt_in=0.02;
  function_sysblockGbIn.leader_x_in=2.0;
  function_sysblockGbIn.leader_y_in=1.0;
  function_sysblockGbIn.leader_z_in=1.2;
  function_sysblockGbIn.leader_vx_in=0.35;
  function_sysblockGbIn.leader_vy_in=0.0;
  function_sysblockGbIn.leader_vz_in=0.0;
  function_sysblockGbIn.leader_yaw_in=0.4;
  function_sysblockGbIn.position_1_x_in=0;
  function_sysblockGbIn.position_1_y_in=-0;
  function_sysblockGbIn.position_1_z_in=1.0;
  function_sysblockGbIn.velocity_1_x_in=0.0;
  function_sysblockGbIn.velocity_1_y_in=0.0;
  function_sysblockGbIn.velocity_1_z_in=0.0;
  function_sysblockGbIn.healthy_1_in=1.0;
  function_sysblockGbIn.position_2_x_in=0.14999999999999999;
  function_sysblockGbIn.position_2_y_in=-0.20000000000000001;
  function_sysblockGbIn.position_2_z_in=1.0;
  function_sysblockGbIn.velocity_2_x_in=0.0;
  function_sysblockGbIn.velocity_2_y_in=0.0;
  function_sysblockGbIn.velocity_2_z_in=0.0;
  function_sysblockGbIn.healthy_2_in=1.0;
  function_sysblockGbIn.position_3_x_in=0.29999999999999999;
  function_sysblockGbIn.position_3_y_in=-0.40000000000000002;
  function_sysblockGbIn.position_3_z_in=1.0;
  function_sysblockGbIn.velocity_3_x_in=0.0;
  function_sysblockGbIn.velocity_3_y_in=0.0;
  function_sysblockGbIn.velocity_3_z_in=0.0;
  function_sysblockGbIn.healthy_3_in=1.0;
  function_sysblockGbIn.reconfigure_in=1.0;
  function_sysblockGbIn.enable_in=1.0;
  function_sysblockGbIn.reset_in=1.0;
  if(id==7) function_sysblockGbIn.healthy_2_in=0.0;
  Init();
  for(step=0;step<20;++step) { Step(); function_sysblockGbIn.reset_in=0.0; }
  printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",id,0,cfunction_sysblockGbOut.desired_position_1_x_out,cfunction_sysblockGbOut.desired_position_1_y_out,cfunction_sysblockGbOut.desired_position_1_z_out,cfunction_sysblockGbOut.desired_position_2_x_out,cfunction_sysblockGbOut.desired_position_2_y_out,cfunction_sysblockGbOut.desired_position_2_z_out,cfunction_sysblockGbOut.desired_position_3_x_out,cfunction_sysblockGbOut.desired_position_3_y_out,cfunction_sysblockGbOut.desired_position_3_z_out,cfunction_sysblockGbOut.desired_velocity_1_x_out,cfunction_sysblockGbOut.desired_velocity_1_y_out,cfunction_sysblockGbOut.desired_velocity_1_z_out,cfunction_sysblockGbOut.desired_velocity_2_x_out,cfunction_sysblockGbOut.desired_velocity_2_y_out,cfunction_sysblockGbOut.desired_velocity_2_z_out,cfunction_sysblockGbOut.desired_velocity_3_x_out,cfunction_sysblockGbOut.desired_velocity_3_y_out,cfunction_sysblockGbOut.desired_velocity_3_z_out,cfunction_sysblockGbOut.minimum_pair_distance_out,cfunction_sysblockGbOut.formation_rmse_out,cfunction_sysblockGbOut.active_agents_out,cfunction_sysblockGbOut.failed_mask_out,cfunction_sysblockGbOut.safety_corrections_out,cfunction_sysblockGbOut.status_code_out);
}
int main(void) { int id; for(id=1;id<=9;++id) run_case(id); return 0; }
