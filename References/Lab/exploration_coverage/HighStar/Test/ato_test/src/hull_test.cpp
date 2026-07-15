// #include <geometry_msgs/PoseStamped.h>
// #include <geometry_msgs/PoseWithCovarianceStamped.h>
// #include <trajectory_msgs/MultiDOFJointTrajectory.h>
// #include <mav_msgs/conversions.h>
// #include <mav_msgs/default_topics.h>
#include <visualization_msgs/MarkerArray.h>
// #include <swarm_exp_msgs/LocalTraj.h>
// #include <swarm_exp_msgs/SwarmTraj.h>
// #include <std_msgs/Empty.h>
// #include <mavros_msgs/PositionTarget.h>

#include <gcopter/traj_opt.h>
// #include <yaw_planner/yaw_planner.h>

#include <glog/logging.h>

#include <message_filters/subscriber.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <message_filters/sync_policies/exact_time.h>
#include <message_filters/time_synchronizer.h>
typedef Eigen::Matrix3Xd PolyhedronV;
typedef Eigen::MatrixX4d PolyhedronH;
typedef std::vector<PolyhedronV> PolyhedraV;
typedef std::vector<PolyhedronH> PolyhedraH;

ros::Publisher result_vis_pub_;
Eigen::MatrixX4d velC_, velB_;

// inline bool processCorridor(const PolyhedraH &hPs,
//                                            PolyhedraV &vPs)
// {
//     const int sizeCorridor = hPs.size() - 1;

//     vPs.clear();
//     vPs.reserve(2 * sizeCorridor + 1);

//     int nv;
//     PolyhedronH curIH;
//     PolyhedronV curIV, curIOB;
//     for (int i = 0; i < sizeCorridor; i++)
//     {
//         if (!geo_utils::enumerateVs(hPs[i], curIV))
//         {
//             return false;
//         }
//         nv = curIV.cols();
//         curIOB.resize(3, nv);
//         curIOB.col(0) = curIV.col(0);
//         curIOB.rightCols(nv - 1) = curIV.rightCols(nv - 1).colwise() - curIV.col(0);
//         vPs.push_back(curIOB);

//         curIH.resize(hPs[i].rows() + hPs[i + 1].rows(), 4);
//         curIH.topRows(hPs[i].rows()) = hPs[i];
//         curIH.bottomRows(hPs[i + 1].rows()) = hPs[i + 1];
//         if (!geo_utils::enumerateVs(curIH, curIV))
//         {
//             return false;
//         }
//         nv = curIV.cols();
//         curIOB.resize(3, nv);
//         curIOB.col(0) = curIV.col(0);
//         curIOB.rightCols(nv - 1) = curIV.rightCols(nv - 1).colwise() - curIV.col(0);
//         vPs.push_back(curIOB);
//     }

//     if (!geo_utils::enumerateVs(hPs.back(), curIV))
//     {
//         return false;
//     }
//     nv = curIV.cols();
//     curIOB.resize(3, nv);
//     curIOB.col(0) = curIV.col(0);
//     curIOB.rightCols(nv - 1) = curIV.rightCols(nv - 1).colwise() - curIV.col(0);
//     vPs.push_back(curIOB);

//     return true;
// }



void ShowHull(PolyhedronV curIV, Eigen::Vector3d dir){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(3);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = 0;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::POINTS;
    mka.markers[0].scale.x = 0.05;
    mka.markers[0].scale.y = 0.05;
    mka.markers[0].scale.z = 0.05;
    mka.markers[0].color.a = 1.0;
    mka.markers[0].color.r = 0.9;
    mka.markers[0].color.g = 0.9;
    mka.markers[0].color.b = 0.0;
    mka.markers[1] = mka.markers[0];
    mka.markers[1].type = visualization_msgs::Marker::CUBE;
    mka.markers[1].id = 1;
    mka.markers[1].color.g = 0.9;
    mka.markers[1].color.a = 0.3;
    mka.markers[1].color.r = 0.0;
    mka.markers[1].scale.x = 6.0;
    mka.markers[1].scale.y = 6.0;
    mka.markers[1].scale.z = 6.0;
    mka.markers[2] = mka.markers[0];
    mka.markers[2].type = visualization_msgs::Marker::ARROW;
    mka.markers[2].id = 2;
    mka.markers[2].color.g = 0.0;
    mka.markers[2].color.a = 1.0;
    mka.markers[2].color.r = 1.0;
    mka.markers[2].scale.x = 0.2;
    mka.markers[2].scale.y = 0.5;
    mka.markers[2].scale.z = 0.0;

    geometry_msgs::Point pt;
    for(int i = 0; i < curIV.cols(); i++){
        pt.x = curIV(0, i);
        pt.y = curIV(1, i);
        pt.z = curIV(2, i);
        mka.markers[0].points.emplace_back(pt);
    }
    pt.x = 0.0;
    pt.y = 0.0;
    pt.z = 0.0;
    mka.markers[2].points.emplace_back(pt);
    pt.x = dir(0) * 3;
    pt.y = dir(1) * 3;
    pt.z = dir(2) * 3;
    mka.markers[2].points.emplace_back(pt);

    result_vis_pub_.publish(mka);

}

int main(int argc, char** argv){
    ros::init(argc, argv, "frontier_test");
    ros::NodeHandle nh, nh_private("~");

    result_vis_pub_ = nh.advertise<visualization_msgs::MarkerArray>("vis_pub", 10);
    int edge_num = 5;
    double endtheta = 0.3;

    velB_.resize(6, 4);
    velB_.setZero();
    velB_(0, 0) = 1.0;
    velB_(1, 0) = -1.0;
    velB_(2, 1) = 1.0;
    velB_(3, 1) = -1.0;
    velB_(4, 2) = 1.0;
    velB_(5, 2) = -1.0;
    velB_.col(3).array() = -3.0;

    velC_.resize(edge_num+1, 4);
    velC_.setZero();
    Eigen::Vector3d dir0(-sin(endtheta), 0.0, cos(endtheta));
    Eigen::Quaterniond q;
    for(int i = 0; i < edge_num; i++){
        q.x() = sin(M_PI / edge_num * i);
        q.y() = 0.0;
        q.z() = 0.0;
        q.w() = cos(M_PI / edge_num * i);
        velC_.block<1, 3>(i, 0) = (q.toRotationMatrix() * dir0).transpose();
        cout<<"velC_:\n"<<velC_<<endl;
    }
    velC_(5, 0) = 1.0;
    velC_(5, 3) = -5.0;
    cout<<"velC_:\n"<<velC_<<endl;


    google::InitGoogleLogging(argv[0]);
    google::ParseCommandLineFlags(&argc, &argv, true);
    google::InstallFailureSignalHandler();
    while(ros::ok()){
        PolyhedronV curIV;
        PolyhedronH curIH;
        double theta, phi;
        theta = double(rand()) / RAND_MAX * M_PI * 2;
        phi = double(rand()) / RAND_MAX * M_PI * 2;
        // theta = -M_PI*0.5;
        // phi = -M_PI*0.5;

        cout<<"theta:"<<theta<<endl;
        cout<<"phi:"<<phi<<endl;
        Eigen::Vector3d dir(1, 0, 0);
        Eigen::Quaterniond q1, q2;
        q1.x() = 0.0;
        q1.y() = 0.0;
        q1.z() = sin(theta * 0.5);
        q1.w() = cos(theta * 0.5);
        q2.x() = 0.0;
        q2.y() = sin(phi * 0.5);
        q2.z() = 0.0;
        q2.w() = cos(phi * 0.5);
        cout<<"q1:"<<q1.coeffs().transpose()<<endl;
        cout<<"q1:\n"<<q1.toRotationMatrix()<<endl;
        cout<<"q2:"<<q2.coeffs().transpose()<<endl;
        cout<<"q2:\n"<<q2.toRotationMatrix()<<endl;
        Eigen::Matrix3d R;
        R = q1*q2;
        dir = R * dir;
        cout<<"dir:"<<dir<<endl;        
        cout<<"R:\n"<<R<<endl;        
        curIH.resize(12, 4);
        curIH.setZero();
        // curIH.topRows(6) = velC_;
        for(int i = 0; i < 6; i++){
            cout<<"r:"<<(R * (velC_.row(i).leftCols(3).transpose())).transpose()<<endl;        
            curIH.row(i).leftCols(3) = (R * (velC_.row(i).leftCols(3).transpose())).transpose();
            curIH(i, 3) = velC_(i, 3);
        }
        cout<<"curIH0:\n"<<curIH<<endl;
        curIH.bottomRows(6) = velB_;
        cout<<"curIH1:\n"<<curIH<<endl;

        if (!geo_utils::enumerateVs(curIH, curIV))
        {
            ROS_ERROR("hull failed");
        }
        else{
            ROS_WARN("hull success");
            ShowHull(curIV, dir);
        }
        ros::spinOnce();
        getchar();
    }

    // ros::spin();
    return 0;
}