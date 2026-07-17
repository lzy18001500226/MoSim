#include <stdio.h>
#include "MoSim_Classic_CFunction_Sysblock.h"
#include "MoSim_Classic_CFunction_Sysblock_private.h"

int main(void)
{
    int id;
    Init();
    for (id = 1; id <= 5; ++id) {
        int step;
    blockGbIn.dt_in = 0.01;
    blockGbIn.position_x_in = 0.10000000000000001;
    blockGbIn.position_y_in = -0.050000000000000003;
    blockGbIn.position_z_in = 0.80000000000000004;
    blockGbIn.velocity_x_in = 0.02;
    blockGbIn.velocity_y_in = -0.01;
    blockGbIn.velocity_z_in = 0.01;
    blockGbIn.reference_position_x_in = 0.25;
    blockGbIn.reference_position_y_in = 0.10000000000000001;
    blockGbIn.reference_position_z_in = 1;
    blockGbIn.reference_velocity_x_in = 0;
    blockGbIn.reference_velocity_y_in = 0;
    blockGbIn.reference_velocity_z_in = 0;
    blockGbIn.reference_acceleration_x_in = 0.01;
    blockGbIn.reference_acceleration_y_in = -0.02;
    blockGbIn.reference_acceleration_z_in = 0;
    blockGbIn.reference_yaw_in = 0.14999999999999999;
    blockGbIn.enable_in = 1;
    blockGbIn.enable_in = 1.0;
        blockGbIn.controller_id_in = (double)id;
        for (step = 0; step < 4; ++step) {
            blockGbIn.reset_in = step == 0 ? 1.0 : 0.0;
            Step();
            printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n", id, step,
            sblockGbOut.desired_acceleration_x_out,
            sblockGbOut.desired_acceleration_y_out,
            sblockGbOut.desired_acceleration_z_out,
            sblockGbOut.desired_attitude_w_out,
            sblockGbOut.desired_attitude_x_out,
            sblockGbOut.desired_attitude_y_out,
            sblockGbOut.desired_attitude_z_out,
            sblockGbOut.observer_position_x_out,
            sblockGbOut.observer_position_y_out,
            sblockGbOut.observer_position_z_out,
            sblockGbOut.observer_velocity_x_out,
            sblockGbOut.observer_velocity_y_out,
            sblockGbOut.observer_velocity_z_out,
            sblockGbOut.reference_model_position_x_out,
            sblockGbOut.reference_model_position_y_out,
            sblockGbOut.reference_model_position_z_out,
            sblockGbOut.reference_model_velocity_x_out,
            sblockGbOut.reference_model_velocity_y_out,
            sblockGbOut.reference_model_velocity_z_out,
            sblockGbOut.adaptive_position_delta_x_out,
            sblockGbOut.adaptive_position_delta_y_out,
            sblockGbOut.adaptive_position_delta_z_out,
            sblockGbOut.adaptive_velocity_delta_x_out,
            sblockGbOut.adaptive_velocity_delta_y_out,
            sblockGbOut.adaptive_velocity_delta_z_out,
            sblockGbOut.fractional_integral_x_out,
            sblockGbOut.fractional_integral_y_out,
            sblockGbOut.fractional_integral_z_out,
            sblockGbOut.fractional_derivative_x_out,
            sblockGbOut.fractional_derivative_y_out,
            sblockGbOut.fractional_derivative_z_out,
            sblockGbOut.normalized_thrust_out,
            sblockGbOut.collective_thrust_n_out,
            sblockGbOut.saturated_out,
            sblockGbOut.status_code_out);
        }
    }
    return 0;
}
