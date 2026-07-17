#include <stdio.h>
#include "MoSim_P5_Enhancement_CFunction_Sysblock.h"
#include "MoSim_P5_Enhancement_CFunction_Sysblock_private.h"
static void print_case(int id) {
    ion_sysblockGbIn.controller_id_in=(double)id;
    ion_sysblockGbIn.dt_in=0.01;
    ion_sysblockGbIn.position_x_in=0.20000000000000001;
    ion_sysblockGbIn.position_y_in=-0.10000000000000001;
    ion_sysblockGbIn.position_z_in=0.69999999999999996;
    ion_sysblockGbIn.velocity_x_in=-0.29999999999999999;
    ion_sysblockGbIn.velocity_y_in=0.20000000000000001;
    ion_sysblockGbIn.velocity_z_in=-0.10000000000000001;
    ion_sysblockGbIn.measured_acceleration_x_in=0.10000000000000001;
    ion_sysblockGbIn.measured_acceleration_y_in=-0.050000000000000003;
    ion_sysblockGbIn.measured_acceleration_z_in=0.02;
    ion_sysblockGbIn.reference_position_x_in=1;
    ion_sysblockGbIn.reference_position_y_in=0.5;
    ion_sysblockGbIn.reference_position_z_in=1.2;
    ion_sysblockGbIn.reference_velocity_x_in=0.10000000000000001;
    ion_sysblockGbIn.reference_velocity_y_in=-0.20000000000000001;
    ion_sysblockGbIn.reference_velocity_z_in=0;
    ion_sysblockGbIn.reference_acceleration_x_in=0.050000000000000003;
    ion_sysblockGbIn.reference_acceleration_y_in=-0.040000000000000001;
    ion_sysblockGbIn.reference_acceleration_z_in=0.02;
    ion_sysblockGbIn.reference_yaw_in=0.29999999999999999;
    ion_sysblockGbIn.trajectory_phase_bin_in=7;
    ion_sysblockGbIn.repeat_complete_in=0;
    ion_sysblockGbIn.mass_kg_in=0.67000000000000004;
    ion_sysblockGbIn.gravity_mps2_in=9.8066499999999994;
    ion_sysblockGbIn.hover_percentage_in=0.29399999999999998;
    ion_sysblockGbIn.max_tilt_rad_in=0.65000000000000002;
    ion_sysblockGbIn.min_collective_thrust_n_in=0;
    ion_sysblockGbIn.max_collective_thrust_n_in=16;
    ion_sysblockGbIn.enable_in=1;
    ion_sysblockGbIn.reset_in=1;
    Init(); Step();
    printf("%d,%d," "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
           "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
           id,0,tion_sysblockGbOut.desired_attitude_w_out,tion_sysblockGbOut.desired_attitude_x_out,tion_sysblockGbOut.desired_attitude_y_out,tion_sysblockGbOut.desired_attitude_z_out,tion_sysblockGbOut.normalized_thrust_out,tion_sysblockGbOut.collective_thrust_n_out,tion_sysblockGbOut.desired_acceleration_x_out,tion_sysblockGbOut.desired_acceleration_y_out,tion_sysblockGbOut.desired_acceleration_z_out,tion_sysblockGbOut.nominal_acceleration_x_out,tion_sysblockGbOut.nominal_acceleration_y_out,tion_sysblockGbOut.nominal_acceleration_z_out,tion_sysblockGbOut.compensation_x_out,tion_sysblockGbOut.compensation_y_out,tion_sysblockGbOut.compensation_z_out,tion_sysblockGbOut.observer_state_x_out,tion_sysblockGbOut.observer_state_y_out,tion_sysblockGbOut.observer_state_z_out,tion_sysblockGbOut.effective_gain_scale_out,tion_sysblockGbOut.saturated_out,tion_sysblockGbOut.status_code_out);
}
int main(void) { int id; for(id=1;id<=6;++id) print_case(id); return 0; }
