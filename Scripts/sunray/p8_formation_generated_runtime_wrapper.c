#include "MoSim_P8_FormationControl_CFunction_Sysblock.h"
#include "MoSim_P8_FormationControl_CFunction_Sysblock_private.h"

static int initialized;

void mosim_p8_generated_init(void) {
    Init();
    initialized = 1;
}

int mosim_p8_generated_step(const double *in, double *out) {
    int i = 0;
    if (!in || !out) return -1;
    if (!initialized) mosim_p8_generated_init();
    function_sysblockGbIn.mode_id_in=in[i++]; function_sysblockGbIn.dt_in=in[i++];
    function_sysblockGbIn.leader_x_in=in[i++]; function_sysblockGbIn.leader_y_in=in[i++]; function_sysblockGbIn.leader_z_in=in[i++];
    function_sysblockGbIn.leader_vx_in=in[i++]; function_sysblockGbIn.leader_vy_in=in[i++]; function_sysblockGbIn.leader_vz_in=in[i++]; function_sysblockGbIn.leader_yaw_in=in[i++];
    function_sysblockGbIn.position_1_x_in=in[i++]; function_sysblockGbIn.position_1_y_in=in[i++]; function_sysblockGbIn.position_1_z_in=in[i++];
    function_sysblockGbIn.position_2_x_in=in[i++]; function_sysblockGbIn.position_2_y_in=in[i++]; function_sysblockGbIn.position_2_z_in=in[i++];
    function_sysblockGbIn.position_3_x_in=in[i++]; function_sysblockGbIn.position_3_y_in=in[i++]; function_sysblockGbIn.position_3_z_in=in[i++];
    function_sysblockGbIn.velocity_1_x_in=in[i++]; function_sysblockGbIn.velocity_1_y_in=in[i++]; function_sysblockGbIn.velocity_1_z_in=in[i++];
    function_sysblockGbIn.velocity_2_x_in=in[i++]; function_sysblockGbIn.velocity_2_y_in=in[i++]; function_sysblockGbIn.velocity_2_z_in=in[i++];
    function_sysblockGbIn.velocity_3_x_in=in[i++]; function_sysblockGbIn.velocity_3_y_in=in[i++]; function_sysblockGbIn.velocity_3_z_in=in[i++];
    function_sysblockGbIn.healthy_1_in=in[i++]; function_sysblockGbIn.healthy_2_in=in[i++]; function_sysblockGbIn.healthy_3_in=in[i++];
    function_sysblockGbIn.reconfigure_in=in[i++]; function_sysblockGbIn.enable_in=in[i++]; function_sysblockGbIn.reset_in=in[i++];
    Step(); i=0;
    out[i++]=cfunction_sysblockGbOut.desired_position_1_x_out; out[i++]=cfunction_sysblockGbOut.desired_position_1_y_out; out[i++]=cfunction_sysblockGbOut.desired_position_1_z_out;
    out[i++]=cfunction_sysblockGbOut.desired_position_2_x_out; out[i++]=cfunction_sysblockGbOut.desired_position_2_y_out; out[i++]=cfunction_sysblockGbOut.desired_position_2_z_out;
    out[i++]=cfunction_sysblockGbOut.desired_position_3_x_out; out[i++]=cfunction_sysblockGbOut.desired_position_3_y_out; out[i++]=cfunction_sysblockGbOut.desired_position_3_z_out;
    out[i++]=cfunction_sysblockGbOut.desired_velocity_1_x_out; out[i++]=cfunction_sysblockGbOut.desired_velocity_1_y_out; out[i++]=cfunction_sysblockGbOut.desired_velocity_1_z_out;
    out[i++]=cfunction_sysblockGbOut.desired_velocity_2_x_out; out[i++]=cfunction_sysblockGbOut.desired_velocity_2_y_out; out[i++]=cfunction_sysblockGbOut.desired_velocity_2_z_out;
    out[i++]=cfunction_sysblockGbOut.desired_velocity_3_x_out; out[i++]=cfunction_sysblockGbOut.desired_velocity_3_y_out; out[i++]=cfunction_sysblockGbOut.desired_velocity_3_z_out;
    out[i++]=cfunction_sysblockGbOut.minimum_pair_distance_out; out[i++]=cfunction_sysblockGbOut.formation_rmse_out;
    out[i++]=cfunction_sysblockGbOut.active_agents_out; out[i++]=cfunction_sysblockGbOut.failed_mask_out;
    out[i++]=cfunction_sysblockGbOut.safety_corrections_out; out[i++]=cfunction_sysblockGbOut.status_code_out;
    return 0;
}
