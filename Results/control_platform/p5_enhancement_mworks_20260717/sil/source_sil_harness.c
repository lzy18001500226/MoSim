#include <stdio.h>
#include <string.h>
#include "enhancement_attitude_thrust_core.h"
static void print_case(int id) {
    MosimEnhancementParams p; MosimEnhancementState s; MosimEnhancementInput in;
    MosimEnhancementOutput out; int i;
    memset(&in,0,sizeof(in)); mosim_enhancement_default_params(&p); mosim_enhancement_reset(&s);
    in.dt=0.01; in.position[0]=0.2; in.position[1]=-0.1; in.position[2]=0.7;
    in.velocity[0]=-0.3; in.velocity[1]=0.2; in.velocity[2]=-0.1;
    in.measured_acceleration[0]=0.1; in.measured_acceleration[1]=-0.05; in.measured_acceleration[2]=0.02;
    in.reference_position[0]=1.0; in.reference_position[1]=0.5; in.reference_position[2]=1.2;
    in.reference_velocity[0]=0.1; in.reference_velocity[1]=-0.2; in.reference_velocity[2]=0.0;
    in.reference_acceleration[0]=0.05; in.reference_acceleration[1]=-0.04; in.reference_acceleration[2]=0.02;
    in.reference_yaw=0.3; in.trajectory_phase_bin=7; in.enable=1; in.reset=1;
    p.max_collective_thrust_n=16.0;
    i=mosim_enhancement_step(id,&p,&s,&in,&out);
    printf("%d,%d," "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
           "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
           id,i,out.desired_attitude_wxyz[0],out.desired_attitude_wxyz[1],out.desired_attitude_wxyz[2],out.desired_attitude_wxyz[3],out.normalized_thrust,out.collective_thrust_n,out.desired_acceleration[0],out.desired_acceleration[1],out.desired_acceleration[2],out.nominal_acceleration[0],out.nominal_acceleration[1],out.nominal_acceleration[2],out.compensation[0],out.compensation[1],out.compensation[2],out.observer_state[0],out.observer_state[1],out.observer_state[2],out.effective_gain_scale,(double)out.saturated,(double)out.status_code);
}
int main(void) { int id; for(id=1;id<=6;++id) print_case(id); return 0; }
