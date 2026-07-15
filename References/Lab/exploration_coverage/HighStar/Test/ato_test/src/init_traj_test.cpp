#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/PoseWithCovarianceStamped.h>
#include <trajectory_msgs/MultiDOFJointTrajectory.h>
#include <mav_msgs/conversions.h>
#include <mav_msgs/default_topics.h>
#include <visualization_msgs/MarkerArray.h>
#include <std_msgs/Empty.h>
#include <mavros_msgs/PositionTarget.h>

#include <gcopter/traj_opt.h>
#include<murder/murderFSM.h>

#include <glog/logging.h>

#include <message_filters/subscriber.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <message_filters/sync_policies/exact_time.h>
#include <message_filters/time_synchronizer.h>

ros::Subscriber trig_sub_, cmd_sub_;
ros::Publisher cmd_pub_;
MurderFSM *M_FSM_;


void trig_sub(geometry_msgs::PoseWithCovarianceStampedPtr &msg){
    M_FSM_->Test();
}

void TargetCallback(const geometry_msgs::PoseStampedPtr &msg){

    trajectory_msgs::MultiDOFJointTrajectory samples_array;
    trajectory_msgs::MultiDOFJointTrajectoryPoint trajectory_point_msg;
    mav_msgs::EigenTrajectoryPoint trajectory_point;
    trajectory_point.position_W.x() = msg->pose.position.x;
    trajectory_point.position_W.y() = msg->pose.position.y;
    trajectory_point.position_W.z() = 1.5;

    // if(!LRM_ptr_->IsFeasible(trajectory_point.position_W)) {
    //     ROS_ERROR("infeasible!!!!!");
    //     return;
    // }
    trajectory_point.orientation_W_B.w() = msg->pose.orientation.w;
    trajectory_point.orientation_W_B.x() = msg->pose.orientation.x;
    trajectory_point.orientation_W_B.y() = msg->pose.orientation.y;
    trajectory_point.orientation_W_B.z() = msg->pose.orientation.z;
    ROS_WARN("t0");
    mav_msgs::msgMultiDofJointTrajectoryPointFromEigen(trajectory_point, &trajectory_point_msg);
    samples_array.points.push_back(trajectory_point_msg);
    cmd_pub_.publish(samples_array);
}

int main(int argc, char** argv){
    ros::init(argc, argv, "frontier_test");
    ros::NodeHandle nh, nh_private("~");

    google::InitGoogleLogging(argv[0]);
    google::ParseCommandLineFlags(&argc, &argv, true);
    google::InstallFailureSignalHandler();

    cmd_pub_ = nh.advertise < trajectory_msgs::MultiDOFJointTrajectory
        > ("/command/trajectory", 5);
    cmd_sub_ = nh.subscribe("/move_base_simple/goal", 1, &TargetCallback);

    MurderFSM M_FSM;
    M_FSM.init(nh, nh_private);
    M_FSM_ = &M_FSM;

    ros::spin();
    return 0;
}