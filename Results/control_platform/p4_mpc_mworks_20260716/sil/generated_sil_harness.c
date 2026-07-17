#include <stdio.h>
#include "MoSim_P4_Mpc_CFunction_Sysblock.h"
#include "MoSim_P4_Mpc_CFunction_Sysblock_private.h"
static void print_case(int id) {
    int step;
    lockGbIn.controller_id_in = (double)id;
    lockGbIn.dt_in = 0.01;
    lockGbIn.position_x_in = 0.20000000000000001;
    lockGbIn.position_y_in = -0.10000000000000001;
    lockGbIn.position_z_in = 0.69999999999999996;
    lockGbIn.velocity_x_in = -0.29999999999999999;
    lockGbIn.velocity_y_in = 0.20000000000000001;
    lockGbIn.velocity_z_in = -0.10000000000000001;
    lockGbIn.reference_position_x_in = 1;
    lockGbIn.reference_position_y_in = 0.5;
    lockGbIn.reference_position_z_in = 1.2;
    lockGbIn.reference_velocity_x_in = 0.10000000000000001;
    lockGbIn.reference_velocity_y_in = -0.20000000000000001;
    lockGbIn.reference_velocity_z_in = 0;
    lockGbIn.reference_acceleration_x_in = 0.050000000000000003;
    lockGbIn.reference_acceleration_y_in = -0.040000000000000001;
    lockGbIn.reference_acceleration_z_in = 0.02;
    lockGbIn.reference_yaw_in = 0.29999999999999999;
    lockGbIn.mass_kg_in = 0.67000000000000004;
    lockGbIn.gravity_mps2_in = 9.8066499999999994;
    lockGbIn.hover_percentage_in = 0.29099999999999998;
    lockGbIn.max_tilt_rad_in = 0.52359877559829882;
    lockGbIn.min_collective_thrust_n_in = 0;
    lockGbIn.max_collective_thrust_n_in = 16;
    lockGbIn.enable_in = 1;
    lockGbIn.reset_in = 0;
    Init();
    for (step=0; step<3; ++step) Step();
    printf("%d," "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
           "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
           id, blockGbOut.desired_attitude_w_out,
        blockGbOut.desired_attitude_x_out,
        blockGbOut.desired_attitude_y_out,
        blockGbOut.desired_attitude_z_out,
        blockGbOut.normalized_thrust_out,
        blockGbOut.collective_thrust_n_out,
        blockGbOut.desired_acceleration_x_out,
        blockGbOut.desired_acceleration_y_out,
        blockGbOut.desired_acceleration_z_out,
        blockGbOut.unconstrained_acceleration_x_out,
        blockGbOut.unconstrained_acceleration_y_out,
        blockGbOut.unconstrained_acceleration_z_out,
        blockGbOut.auxiliary_x_out,
        blockGbOut.auxiliary_y_out,
        blockGbOut.auxiliary_z_out,
        blockGbOut.solver_cost_out,
        blockGbOut.solver_iterations_out,
        blockGbOut.saturated_out,
        blockGbOut.status_code_out);
}
int main(void) { int id; for (id=1; id<=7; ++id) print_case(id); return 0; }
