#include <stdio.h>
#include "MoSim_P2_LinearRobust_CFunction_Sysblock.h"
#include "MoSim_P2_LinearRobust_CFunction_Sysblock_private.h"

static void print_case(int id)
{
    tion_sysblockGbIn.controller_id_in = (double)id;
    tion_sysblockGbIn.dt_in = 0.02;
    tion_sysblockGbIn.position_x_in = 0.20000000000000001;
    tion_sysblockGbIn.position_y_in = -0.10000000000000001;
    tion_sysblockGbIn.position_z_in = 0.69999999999999996;
    tion_sysblockGbIn.velocity_x_in = -0.29999999999999999;
    tion_sysblockGbIn.velocity_y_in = 0.20000000000000001;
    tion_sysblockGbIn.velocity_z_in = -0.10000000000000001;
    tion_sysblockGbIn.reference_position_x_in = 1;
    tion_sysblockGbIn.reference_position_y_in = 0.5;
    tion_sysblockGbIn.reference_position_z_in = 1.2;
    tion_sysblockGbIn.reference_velocity_x_in = 0.10000000000000001;
    tion_sysblockGbIn.reference_velocity_y_in = -0.20000000000000001;
    tion_sysblockGbIn.reference_velocity_z_in = 0;
    tion_sysblockGbIn.reference_acceleration_x_in = 0.050000000000000003;
    tion_sysblockGbIn.reference_acceleration_y_in = -0.040000000000000001;
    tion_sysblockGbIn.reference_acceleration_z_in = 0.02;
    tion_sysblockGbIn.reference_yaw_in = 0.29999999999999999;
    tion_sysblockGbIn.mass_kg_in = 0.67000000000000004;
    tion_sysblockGbIn.gravity_mps2_in = 9.8066499999999994;
    tion_sysblockGbIn.hover_percentage_in = 0.29099999999999998;
    tion_sysblockGbIn.max_tilt_rad_in = 0.52359877559829882;
    tion_sysblockGbIn.min_collective_thrust_n_in = 0;
    tion_sysblockGbIn.max_collective_thrust_n_in = 16;
    tion_sysblockGbIn.enable_in = 1;
    tion_sysblockGbIn.reset_in = 1;
    Init();
    Step();
    printf("%d,0,"
        "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
        "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
        "%.17g,%.17g,%.17g\n",
        id,
        ction_sysblockGbOut.desired_acceleration_x_out,
        ction_sysblockGbOut.desired_acceleration_y_out,
        ction_sysblockGbOut.desired_acceleration_z_out,
        ction_sysblockGbOut.desired_attitude_w_out,
        ction_sysblockGbOut.desired_attitude_x_out,
        ction_sysblockGbOut.desired_attitude_y_out,
        ction_sysblockGbOut.desired_attitude_z_out,
        ction_sysblockGbOut.normalized_thrust_out,
        ction_sysblockGbOut.collective_thrust_n_out,
        ction_sysblockGbOut.estimated_position_x_out,
        ction_sysblockGbOut.estimated_position_y_out,
        ction_sysblockGbOut.estimated_position_z_out,
        ction_sysblockGbOut.estimated_velocity_x_out,
        ction_sysblockGbOut.estimated_velocity_y_out,
        ction_sysblockGbOut.estimated_velocity_z_out,
        ction_sysblockGbOut.adaptive_disturbance_x_out,
        ction_sysblockGbOut.adaptive_disturbance_y_out,
        ction_sysblockGbOut.adaptive_disturbance_z_out,
        ction_sysblockGbOut.storage_function_out,
        ction_sysblockGbOut.saturated_out,
        ction_sysblockGbOut.status_code_out);
}

int main(void)
{
    print_case(1); print_case(2); print_case(3); print_case(4);
    return 0;
}
