#include <stdio.h>
#include <string.h>
#include "safety_supervisor_core.h"
static void run_case(int id) {
    MosimSafetyParams p; MosimSafetyState s; MosimSafetyInput in; MosimSafetyOutput out;
    int rc; memset(&in,0,sizeof(in)); mosim_safety_default_params(&p); mosim_safety_reset(&s);
    in.dt=0.01; in.position[2]=1.0; in.reference_position[0]=12.0; in.reference_position[2]=1.0;
    in.candidate_acceleration[0]=8.0; in.candidate_thrust=1.2; in.candidate_tilt_rad=0.8;
    in.obstacle_distance=5.0; in.state_valid=1; in.offboard_valid=1; in.enable=1; in.reset=1;
    if(id==2) in.obstacle_distance=0.4;
    if(id==5) in.emergency_request=1;
    if(id==6) in.return_request=1;
    if(id==7) in.command_age_s=1.0;
    rc=mosim_safety_step(id,&p,&s,&in,&out);
    printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d,%u,%d,%d\n",
      id,rc,out.safe_acceleration[0],out.safe_acceleration[1],out.safe_acceleration[2],
      out.safe_thrust,out.safe_reference[0],out.safe_reference[1],out.safe_reference[2],
      out.action,out.state,out.active_constraints,out.modified,out.status_code);
}
int main(void) { int id; for(id=1;id<=7;++id) run_case(id); return 0; }
