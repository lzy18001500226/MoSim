#include <stdio.h>
#include "sliding_mode_attitude_thrust_core.h"
static void print_case(int id) {
    MosimSlidingModeParams p; MosimSlidingModeState s; MosimSlidingModeOutput output;
    MosimSlidingModeInput in = {0.02, {0.2,-0.1,0.7}, {-0.3,0.2,-0.1},
        {1.0,0.5,1.2}, {0.1,-0.2,0.0}, {0.05,-0.04,0.02}, 0.3, 1, 1};
    mosim_sliding_mode_default_params(&p); mosim_sliding_mode_reset(&p, &s);
    (void)mosim_sliding_mode_step(id, &p, &s, &in, &output);
    printf("%d," "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
           "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
           id, output.desired_acceleration[0],
        output.desired_acceleration[1],
        output.desired_acceleration[2],
        output.sliding_surface[0],
        output.sliding_surface[1],
        output.sliding_surface[2],
        output.auxiliary_state[0],
        output.auxiliary_state[1],
        output.auxiliary_state[2],
        output.effective_reaching_gain[0],
        output.effective_reaching_gain[1],
        output.effective_reaching_gain[2],
        output.desired_attitude_wxyz[0],
        output.desired_attitude_wxyz[1],
        output.desired_attitude_wxyz[2],
        output.desired_attitude_wxyz[3],
        output.normalized_thrust,
        output.collective_thrust_n,
        (double)output.saturated,
        (double)output.status_code);
}
int main(void) { int id; for (id=1; id<=6; ++id) print_case(id); return 0; }
