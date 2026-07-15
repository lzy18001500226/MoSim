#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/PoseWithCovarianceStamped.h>
#include <trajectory_msgs/MultiDOFJointTrajectory.h>
#include <mav_msgs/conversions.h>
#include <mav_msgs/default_topics.h>
#include <visualization_msgs/MarkerArray.h>
#include <std_msgs/Empty.h>
#include <mavros_msgs/PositionTarget.h>
#include <lowres_map/lowres_map.h>

#include<block_map/block_map.h>
#include<murder/murder.h>

#include <glog/logging.h>

#include <message_filters/subscriber.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <message_filters/sync_policies/exact_time.h>
#include <message_filters/time_synchronizer.h>

ros::Publisher debug_pub_;

void Debug(list<Eigen::Vector3d> &pts, int id){
    visualization_msgs::Marker mk;// mkr1, mkr2;
    mk.header.frame_id = "world";
    mk.header.stamp = ros::Time::now();
    mk.id = id;
    if(id == 0){
        mk.pose.position.z = 0.0;
        mk.color.g = 1.0;
    }
    else{
        mk.color.b = 1.0;
        mk.pose.position.z = 0.0;
    }
    // scan_count_++;
    mk.action = visualization_msgs::Marker::ADD;
    mk.type = visualization_msgs::Marker::LINE_STRIP;
    mk.scale.x = 0.03;
    mk.scale.y = 0.03;
    mk.scale.z = 0.03;
    mk.color.a = 1.0;
    mk.pose.position.x = 0;
    mk.pose.position.y = 0;
    mk.pose.orientation.x = 0;
    mk.pose.orientation.y = 0;
    mk.pose.orientation.z = 0;
    mk.pose.orientation.w = 1;

    geometry_msgs::Point pt;
    for(auto &p : pts){
        // cout<<p.transpose()<<endl;
        pt.x = p.x();
        pt.y = p.y();
        pt.z = p.z();
        mk.points.push_back(pt);
    }
    debug_pub_.publish(mk);
}


int main(int argc, char** argv){
    ros::init(argc, argv, "frontier_test");
    ros::NodeHandle nh, nh_private("~");

    string ns = ros::this_node::getName(), occ_path, free_path;
    google::InitGoogleLogging(argv[0]);
    google::ParseCommandLineFlags(&argc, &argv, true);
    google::InstallFailureSignalHandler();

    debug_pub_ = nh.advertise<visualization_msgs::Marker>("/DebugVis", 10);

    Eigen::Vector3d ps, pe;

    nh_private.param(ns + "/block_map/OccPath", 
        occ_path, occ_path);
    nh_private.param(ns + "/block_map/FreePath", 
        free_path, free_path);
    nh_private.param(ns + "/Test/StartX", 
        ps(0), 7.5);
    nh_private.param(ns + "/Test/StartY", 
        ps(1), 7.5);
    nh_private.param(ns + "/Test/StartZ", 
        ps(2), 1.5);
    nh_private.param(ns + "/Test/EndX", 
        pe(0), -7.5);
    nh_private.param(ns + "/Test/EndY", 
        pe(1), -7.5);
    nh_private.param(ns + "/Test/EndZ", 
        pe(2), 1.5);

    Murder M_planner_;
    M_planner_.init(nh, nh_private);
    BlockMap *BM;
    M_planner_.GetBlockMapPtr(BM);

    cout<<"occ_path:"<<occ_path<<endl;
    cout<<"free_path:"<<free_path<<endl;

    BM->LoadRawMap(occ_path, free_path, 1, true);
    ROS_WARN("finish loading");
    ros::Duration(1.2).sleep();
    for(int i = 0; i < 10; i++){
        ros::spinOnce();
        ros::Duration(0.2).sleep();
    }
    // BM.GetExplorableVolume(Eigen::Vector3d(0.05,0.05,4.05));

    vector<Eigen::Vector4d> constraints;
    constraints.emplace_back(Eigen::Vector4d(-0.707106781, 0.707106781, 0, -4.0));
    constraints.emplace_back(Eigen::Vector4d(0.707106781, -0.707106781, 0, -2.0));
    // constraints.emplace_back(Eigen::Vector4d(0.707106781, 0.707106781, 0, -50));
    // constraints.emplace_back(Eigen::Vector4d(-0.707106781, -0.707106781, 0, -50));
    BM->BlineMap(constraints);
    ROS_WARN("blined");
    ros::Duration(1.2).sleep();
    for(int i = 0; i < 3; i++){
        ros::spinOnce();
        ros::Duration(0.2).sleep();
    }

    lowres::LowResMap *LRM;
    M_planner_.GetLowresMapPtr(LRM);
    Eigen::Matrix4d m;
    pair<Eigen::Vector3d, Eigen::Vector3d> bbx;
    bbx.first = Eigen::Vector3d(10.0, 10.0, 5.0);
    bbx.second = Eigen::Vector3d(-10.0, -10.0, 0.0);
    LRM->UpdateLocalBBX(m, bbx);
    ROS_WARN("lowres");
    ros::Duration(1.2).sleep();

    FrontierGrid *FG;
    M_planner_.GetFrontierMapPtr(FG);
    for(int i = 0; i < 3; i++){
        ros::spinOnce();
        ros::Duration(0.2).sleep();
    }

    AtoTraj *TrajOpt;
    M_planner_.GetTrajectoryPtr(TrajOpt);

    
    list<Eigen::Vector3d> path;
    Eigen::Vector3d vs, as;
    Eigen::Vector4d tar;
    pair<Eigen::Vector4d, bool> ntar;
    double expect_t;
    double ys;
    tar.head(3) = pe;
    tar(3) = M_PI * 0.75;
    // for(int i = 0; i < 8; i++){   
        int i = 2;
        nh_private.param(ns + "/Test/I", 
            i, 1);
        cout<<"i:"<<i<<endl;

        ys = M_PI / 4 * i;
        vs = Eigen::Vector3d(2.0 * cos(ys), 3.0 * sin(ys), 0.0);
        // getchar();
        if(FG->FindMotionPath(ps, vs, as, tar, path, expect_t, ys, 0, 2.0, 2.75, 6.0, 9.0)){
            // Debug(path, 0);
            ntar.second = false;
            vector<Eigen::Vector3d> path_vec;
            for(auto &pc : path) {
                path_vec.emplace_back(pc);
            }
            M_planner_.TrajPlan(ps, vs, as, pe, vs, as, ys, 0, 0, -3*M_PI_4, 0, 0, -1, ntar, path_vec);
            cout<<"exp_t:"<<expect_t<<endl;
            cout<<"real_t:"<<TrajOpt->traj.getTotalDuration()<<endl;
            ros::Duration(0.5).sleep();
            M_planner_.traj_start_t_ = ros::WallTime::now().toSec();
            M_planner_.PublishTraj(false);
            M_planner_.volume_t_ = ros::WallTime::now().toSec() + TrajOpt->traj.getTotalDuration();
            // getchar();
        }
        else{
            ROS_ERROR("motion path failed!");
        }
        vector<Eigen::Vector3d> path_vec;
        if(FG->FindPath(ps, vs, tar, path, ys, 0, 2.0, 2.75, 6.0, expect_t)){
            // Debug(path, 1);

            // double l = 0;
            // Eigen::Vector3d p = path_vec.front();
            // for(int i = 0; i < path_vec.size(); i++){
            //     l += (p - path_vec[i]).norm() / 6.0;
            //     p = path_vec[i];
            // }
            cout<<"exp_t2:"<<expect_t/6.0<<endl;
            ros::Duration(0.01).sleep();
        }
        else{
            ROS_ERROR("path failed!");
        }
        // getchar();
    // }
    ros::spin();
    return 0;
}