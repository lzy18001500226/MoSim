#include <stdio.h>
#include "mpc_attitude_thrust_core.h"
static void print_case(int id) {
    int step;
    MosimMpcParams p; MosimMpcState s; MosimMpcOutput output;
    MosimMpcInput in = {0.01, {0.2,-0.1,0.7}, {-0.3,0.2,-0.1},
        {1.0,0.5,1.2}, {0.1,-0.2,0.0}, {0.05,-0.04,0.02}, 0.3, 1, 0};
    mosim_mpc_default_params(&p); mosim_mpc_reset(&s);
    p.mass_kg = 0.67; p.gravity_mps2 = 9.80665; p.hover_percentage = 0.291;
    p.max_tilt_rad = 0.5235987755982988;
    p.min_collective_thrust_n = 0.0; p.max_collective_thrust_n = 16.0;
    for (step=0; step<3; ++step) (void)mosim_mpc_step(id, &p, &s, &in, &output);
    printf("%d," "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
           "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
           id, output.desired_attitude_wxyz[0],
        output.desired_attitude_wxyz[1],
        output.desired_attitude_wxyz[2],
        output.desired_attitude_wxyz[3],
        output.normalized_thrust,
        output.collective_thrust_n,
        output.desired_acceleration[0],
        output.desired_acceleration[1],
        output.desired_acceleration[2],
        output.unconstrained_acceleration[0],
        output.unconstrained_acceleration[1],
        output.unconstrained_acceleration[2],
        output.auxiliary[0],
        output.auxiliary[1],
        output.auxiliary[2],
        output.solver_cost,
        (double)output.solver_iterations,
        (double)output.saturated,
        (double)output.status_code);
}
int main(void) { int id; for (id=1; id<=7; ++id) print_case(id); return 0; }
