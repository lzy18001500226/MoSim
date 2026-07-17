#include <stdio.h>
#include <string.h>
#include "formation_control_core.h"
static void run_case(int id) {
  MosimFormationParams p; MosimFormationState s; MosimFormationInput in; MosimFormationOutput out;
  int step,agent,axis,rc=0; memset(&in,0,sizeof(in));
  mosim_formation_default_params(&p); mosim_formation_reset(&s);
  in.dt=0.02; in.leader_position[0]=2.0; in.leader_position[1]=1.0; in.leader_position[2]=1.2;
  in.leader_velocity[0]=0.35; in.leader_yaw_rad=0.4; in.enable=1; in.reset=1; in.reconfigure=1;
  for(agent=0;agent<3;++agent) {
    in.healthy[agent]=1; in.position[agent][0]=0.15*agent;
    in.position[agent][1]=-0.20*agent; in.position[agent][2]=1.0;
    for(axis=0;axis<3;++axis) in.velocity[agent][axis]=0.0;
  }
  if(id==7) in.healthy[1]=0;
  for(step=0;step<20;++step) { rc=mosim_formation_step(id,&p,&s,&in,&out); in.reset=0; }
  printf("%d,%d",id,rc);
  for(agent=0;agent<3;++agent) for(axis=0;axis<3;++axis) printf(",%.17g",out.desired_position[agent][axis]);
  for(agent=0;agent<3;++agent) for(axis=0;axis<3;++axis) printf(",%.17g",out.desired_velocity[agent][axis]);
  printf(",%.17g,%.17g,%d,%u,%d,%d\n",out.minimum_pair_distance_m,out.formation_rmse_m,
    out.active_agents,out.failed_mask,out.safety_corrections,out.status_code);
}
int main(void) { int id; for(id=1;id<=9;++id) run_case(id); return 0; }
