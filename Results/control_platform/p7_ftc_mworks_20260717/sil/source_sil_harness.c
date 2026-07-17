#include <stdio.h>
#include <string.h>
#include "fault_tolerant_control_core.h"
static void run_case(int id) {
    MosimFtcParams p; MosimFtcState s; MosimFtcInput in; MosimFtcOutput out;
    int step, rc=0; memset(&in,0,sizeof(in)); mosim_ftc_default_params(&p); mosim_ftc_reset(&s);
    in.dt=0.01; in.desired_wrench[0]=2.4; in.desired_wrench[1]=0.04;
    in.desired_wrench[2]=-0.03; in.desired_wrench[3]=0.02;
    in.measured_motor_response[0]=0.57; in.measured_motor_response[1]=0.60;
    in.measured_motor_response[2]=0.64; in.measured_motor_response[3]=0.59;
    in.airborne=1; in.altitude=1.2; in.enable=1;
    if(id==1) in.measured_motor_response[0]=0.3135;
    if(id==2) in.measured_motor_response[0]=0.4275;
    if(id==3) in.measured_motor_response[1]=0.33;
    if(id==4) in.measured_motor_response[2]=0.352;
    if(id==5) in.measured_motor_response[3]=0.118;
    if(id==6) { in.measured_motor_response[0]=0.3135; in.measured_motor_response[2]=0.384; }
    for(step=0;step<80;++step) rc=mosim_ftc_step(id,&p,&s,&in,&out);
    printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%u,%d,%d,%d,%d\n",
      id,rc,out.motor_command[0],out.motor_command[1],out.motor_command[2],out.motor_command[3],
      out.effectiveness_estimate[0],out.effectiveness_estimate[1],out.effectiveness_estimate[2],out.effectiveness_estimate[3],
      out.achieved_wrench[0],out.achieved_wrench[1],out.achieved_wrench[2],out.achieved_wrench[3],out.residual_norm,
      out.isolated_mask,out.fault_count,out.action,out.allocation_saturated,out.status_code);
}
int main(void) { int id; for(id=1;id<=6;++id) run_case(id); return 0; }
