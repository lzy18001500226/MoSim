#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/PoseWithCovarianceStamped.h>
#include <trajectory_msgs/MultiDOFJointTrajectory.h>
#include <mav_msgs/conversions.h>
#include <mav_msgs/default_topics.h>
#include <visualization_msgs/MarkerArray.h>
#include <std_msgs/Empty.h>
#include <mavros_msgs/PositionTarget.h>

#include<block_map/block_map.h>

#include <glog/logging.h>

#include <message_filters/subscriber.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <message_filters/sync_policies/exact_time.h>
#include <message_filters/time_synchronizer.h>


int main(int argc, char** argv){
    ros::init(argc, argv, "frontier_test");
    ros::NodeHandle nh, nh_private("~");

    string ns = ros::this_node::getName(), occ_path, free_path;
    google::InitGoogleLogging(argv[0]);
    google::ParseCommandLineFlags(&argc, &argv, true);
    google::InstallFailureSignalHandler();

    nh_private.param(ns + "/block_map/OccPath", 
        occ_path, occ_path);
    nh_private.param(ns + "/block_map/FreePath", 
        free_path, free_path);
    BlockMap BM;
    BM.init(nh, nh_private);

    cout<<"occ_path:"<<occ_path<<endl;
    cout<<"free_path:"<<free_path<<endl;

    BM.LoadRawMap(occ_path, free_path, 0, true);
    ROS_WARN("finish loading");
    for(int i = 0; i < 10; i++){
        ros::spinOnce();
        ros::Duration(0.2).sleep();
    }
    // BM.GetExplorableVolume(Eigen::Vector3d(0.05,0.05,4.05));


    ros::spin();
    return 0;
}