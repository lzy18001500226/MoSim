#include <ros/ros.h>
#include <stdio.h>
#include <string>
#include <murder/murderFSM.h>
#include <geometry_msgs/PoseStamped.h>
#include <glog/logging.h>

Murder *M_planner_;
ros::Subscriber tar_sub_;


void PlanTraj(const geometry_msgs::PoseStamped &msg){
    Eigen::Vector3d p;
    double y;
    p(0) = msg.pose.position.x;
    p(1) = msg.pose.position.y;
    p(2) = rand() / RAND_MAX * 1.0 + 1.0;
    y = asin(msg.pose.orientation.z) * 2;
    if(M_planner_->PlanTraj(p, y)){
        ROS_WARN("plan success!");
    }
    else{
        ROS_ERROR("plan fail");
    }
}





int main(int argc, char** argv){
    ros::init(argc, argv, "murder_node");
    ros::NodeHandle nh, nh_private("~");

    google::InitGoogleLogging(argv[0]);
    google::ParseCommandLineFlags(&argc, &argv, true);
    google::InstallFailureSignalHandler();

    tar_sub_ = nh.subscribe("/move_base_simple/goal", 1, &PlanTraj);
    // MurderFSM M_FSM;
    // M_FSM.init(nh, nh_private);
    Murder M_planner;
    M_planner_ = &M_planner;
    M_planner_->init(nh, nh_private);

    ros::spin();
    return 0;
}