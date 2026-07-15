#include <murder/murderFSM.h>

namespace {
    ros::NodeHandle *g_fsm_node_handle = nullptr;
}

void MurderFSM::init(const ros::NodeHandle &nh, const ros::NodeHandle &nh_private){
    delete g_fsm_node_handle;
    g_fsm_node_handle = new ros::NodeHandle(nh);
    M_planner_.init(nh, nh_private);
    trigger_sub_ = g_fsm_node_handle->subscribe("/start_trigger", 1, &MurderFSM::TriggerCallback, this);
    fsm_timer_ = g_fsm_node_handle->createTimer(ros::Duration(0.01), &MurderFSM::FSMCallback, this);
    exploring_ = false;
    state_ = M_State::SLEEP;
    t0_ = ros::WallTime::now().toSec();
}

void MurderFSM::ChangeState(const M_State &state){
    // ROS_WARN("FSM from %d to %d", state_, state);
    std::cout << "from  \033[0;46m"<<state_names[state_]<<"\033[0m to \033[0;46m" <<state_names[state]<<"\033[0m" << std::endl;
    state_ = state;
}

void MurderFSM::TriggerCallback(const std_msgs::EmptyConstPtr &msg){
    start_trigger_ = true;
    exploring_ = true;
}

void MurderFSM::FSMCallback(const ros::TimerEvent &e){
    bool exc_plan;
    int ap = M_planner_.AllowPlan(ros::WallTime::now().toSec());
    ROS_WARN_THROTTLE(
        1.0,
        "HighStar FSM diagnostic: state=%s ap=%d exploring=%d start_trigger=%d",
        state_names[state_].c_str(),
        ap,
        exploring_ ? 1 : 0,
        start_trigger_ ? 1 : 0);
    
    if(ap == 0) exc_plan = true;                                                                            
    else if(ap == 1) exc_plan = false;                    
    else if(ap == 2) exc_plan = true;                              //current pos infeasible
    else if(ap == 3 /*&& (state_ == M_State::EXCUTE || state_ == M_State::LOCALPLAN)*/) exc_plan = true; //only allow check viewpoints and check the traj feasibility
    else if(ap == 3) exc_plan = false;
    else if(ap == 4 && state_ == M_State::LOCALPLAN) exc_plan = true;
    else if(ap == 5) exc_plan = true;

    // cout<<"ap1:"<<ap<<endl;
    switch (state_)
    {
        case M_State::EXCUTE :{
            /* trajectory check */
            if(!M_planner_.TrajCheck()){     
                if(ap == 2){                 // current pos is infeasible
                    M_planner_.SetPlanInterval(0.009);
                    break;
                }
                else{   //try to replan
                    ROS_WARN("traj occ or relpan");
                    ChangeState(M_State::LOCALPLAN);
                    M_planner_.SetPlanInterval(0.009);
                    break;
                }
            }

            /* viewpoints check */
            int vp_st = M_planner_.ViewPointsCheck(0.005);
            if(vp_st == 1 || ap == 5){        //if viewpoint is explored or exceeds replan duration, local plan
                if(ap == 5) ROS_WARN("traj time out");
                if(vp_st == 1) ROS_WARN("target explored");
                ChangeState(M_State::LOCALPLAN);
                M_planner_.SetPlanInterval(0.009);
                break;
            }
            
            /* still EXCUTE */
            M_planner_.SetPlanInterval(0.05);
            break;
        }
        // case M_State::FINISH :{
        //     M_planner_.SetPlanInterval(0.009);
        //     break;
        // }
        case M_State::LOCALPLAN :{
            if(ap == 2){               // current position is not feasible, hold on                        
                M_planner_.SetPlanInterval(0.009);
                // ChangeState(M_State::LOCALPLAN);
                break;
            }

            if(M_planner_.LocalPlan()){                 //plan success, execute trajectory
                M_planner_.SetPlanInterval(0.009);
                ChangeState(M_State::EXCUTE);
                break;
            }
            else{ // plan failed, replan imedately
                M_planner_.SetPlanInterval(0.009);
                break;
            }
        }
        case M_State::SLEEP :{
            if(!exploring_){ // wait for the trigger
                if(start_trigger_)
                M_planner_.SetPlanInterval(0.009);
            }
            else{ // trigger, then start
                ChangeState(M_State::LOCALPLAN);
                M_planner_.SetPlanInterval(0.009);
            }
            break;
        }
    }
}

void MurderFSM::Test(){
    M_planner_.Test();
}
