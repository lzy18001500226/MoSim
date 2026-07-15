#ifndef MURDER_FSM_H_
#define MURDER_FSM_H_
#include <ros/ros.h>
#include <thread>
#include <Eigen/Eigen>
#include <vector>
#include <list>
#include <visualization_msgs/MarkerArray.h>
#include <std_msgs/Empty.h>
#include <murder/murder.h>

class MurderFSM{
public:
    /**
     * EXCUTE: excute traj, strongcheck several viewpoints, check the feasibility of the traj
     * SLEEP: before exploratin
     * RECOVER: if traj is infeasible and replan fails, slowly fly to the free pos
     * FINISH: no explorable viewpoint, return start place 
     * LOCALPLAN: to the closest local viewpoint
     * GLOBALPLAN: to the closest global viewpoint
     */
    enum M_State{EXCUTE, SLEEP, RECOVER, FINISH, LOCALPLAN };
    vector<string> state_names = {"EXCUTE", "SLEEP", "RECOVER", "FINISH", "LOCALPLAN"};
    MurderFSM(){};
    ~MurderFSM(){};
    void init(const ros::NodeHandle &nh, const ros::NodeHandle &nh_private);
    void Test();
private:
    void FSMCallback(const ros::TimerEvent &e);
    void TriggerCallback(const std_msgs::EmptyConstPtr &msg);
    void ChangeState(const M_State &state);
    double fsm_min_duration_;
    bool exploring_, start_trigger_;
    ros::Subscriber trigger_sub_;
    Murder M_planner_;
    ros::Timer fsm_timer_;
    M_State state_;
    double t0_;

};
#endif
