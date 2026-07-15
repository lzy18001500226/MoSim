#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/PoseWithCovarianceStamped.h>
#include <trajectory_msgs/MultiDOFJointTrajectory.h>
#include <mav_msgs/conversions.h>
#include <mav_msgs/default_topics.h>
#include <visualization_msgs/MarkerArray.h>
#include <swarm_exp_msgs/SwarmTraj.h>
#include <std_msgs/Empty.h>
#include <mavros_msgs/PositionTarget.h>
#include <gazebo_msgs/SetModelState.h>

#include <glog/logging.h>

#include <gcopter/traj_opt.h>
#include <yaw_planner/yaw_planner.h>

// #include <glog/logging.h>

#include <message_filters/subscriber.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <message_filters/sync_policies/exact_time.h>
#include <message_filters/time_synchronizer.h>

ros::Publisher show_pub_, trigger_pub_;
ros::Subscriber takeoff_sub_;
bool auto_takeoff_;

ros::Subscriber traj_sub_;
int traj_state_;
Trajectory<5> traj_;  
Eigen::Vector3d recover_pt_;
list<swarm_exp_msgs::SwarmTraj> trajs_;
double start_t_;  
YawPlanner yaw_traj_;

bool ready_;
Eigen::Vector3d robot_pos_, takeoff_pos_;
double max_v_, max_a_, max_yawd_, max_yawdd_;

ros::Timer run_timer_;
bool TryUpdateTraj();

inline void YawNorm(double &yaw){
    double yawn;
    int c = yaw / M_PI / 2;
    yawn = yaw - c * M_PI * 2;
    
    if(yawn < -M_PI) yawn += M_PI * 2;
    if(yawn > M_PI) yawn -= M_PI * 2;
    yaw = yawn;
    return;
}

inline double YawDiff(const double &yaw1, const double &yaw2){
    double dy = yaw1 - yaw2;
    YawNorm(dy);
    return dy;
}

void GetHoufFibYaw(const Eigen::Vector3d &acc, double &yaw, Eigen::Quaterniond &q){
    double yaw2 = yaw / 2;
    double siny2 = sin(yaw2);
    double cosy2 = cos(yaw2);
    Eigen::Vector3d z = acc.head(3) + Eigen::Vector3d(0, 0, 9.8);
    z.normalize();
    q.x() = -z(1)*cosy2 + z(0)*siny2;
    q.y() = z(0)*cosy2 + z(1)*siny2;
    q.z() = (1 + z(2))*siny2;
    q.w() = (1 + z(2))*cosy2;
    q.coeffs() /= sqrt(2*(1 + z(2)));
}

void RunCallback(const ros::TimerEvent &e){
    if(!ready_) return;
    Eigen::Vector3d p, v, a, j;
    double yaw, yawd, yawdd;
    // ROS_WARN("run0");
    while (TryUpdateTraj()){}
    if(traj_state_ == 1){
        p = recover_pt_ - robot_pos_;
        p = robot_pos_ + min(p.norm(), 0.3) * p.normalized();
        v.setZero();
        a.setZero();
        yawd = 0;
        yawdd = 0;
    }
    else if(traj_state_ == 2){
        // cout<<traj_.getPieceNum()<<endl;
        double cur_t = ros::WallTime::now().toSec();
        double tt = traj_.getTotalDuration();
        if(cur_t - start_t_> tt){
            v = traj_.getVel(tt - 1e-4) * max((0.25 + tt - cur_t + start_t_) * 4.0, 0.0);
            a = traj_.getAcc(tt - 1e-4) * max((0.25 + tt - cur_t + start_t_) * 4.0, 0.0);
            j = traj_.getJer(tt - 1e-4) * max((0.25 + tt - cur_t + start_t_) * 4.0, 0.0);
            yaw_traj_.GetCmd(cur_t - start_t_, yaw, yawd, yawdd);
            yawd *= max((0.25 + tt - cur_t + start_t_) * 4.0, 0.0);
            yawdd *= max((0.25 + tt - cur_t + start_t_) * 4.0, 0.0);
            cur_t = start_t_ + tt - 1e-4;
        }
        else{
            v = traj_.getVel(cur_t - start_t_);
            a = traj_.getAcc(cur_t - start_t_);
            j = traj_.getJer(cur_t - start_t_);
            yaw_traj_.GetCmd(cur_t - start_t_, yaw, yawd, yawdd);
        }
        p = traj_.getPos(cur_t - start_t_);
        if(v.norm() > max_v_)
            v = v.normalized() * max_v_;
        if(a.norm() > max_a_)
            a = a.normalized() * max_a_;
        if(abs(yawd) > max_yawd_) yawd = yawd / abs(yawd) * max_yawd_;
        if(abs(yawdd) > max_yawdd_) yawdd = yawdd / abs(yawdd) * max_yawdd_;
    }
    else return;
    Eigen::Quaterniond q;
    GetHoufFibYaw(a, yaw, q);
    gazebo_msgs::SetModelState state_srv;
    state_srv.request.model_state.reference_frame = "world";
    state_srv.request.model_state.model_name = "firefly";
    state_srv.request.model_state.pose.position.x = p(0);
    state_srv.request.model_state.pose.position.y = p(1);
    state_srv.request.model_state.pose.position.z = p(2);
    state_srv.request.model_state.pose.orientation.w = q.w();
    state_srv.request.model_state.pose.orientation.x = q.x();
    state_srv.request.model_state.pose.orientation.y = q.y();
    state_srv.request.model_state.pose.orientation.z = q.z();
    state_srv.request.model_state.twist.linear.x = 0;
    state_srv.request.model_state.twist.linear.y = 0;
    state_srv.request.model_state.twist.linear.z = 0;
    state_srv.request.model_state.twist.angular.x = 0;
    state_srv.request.model_state.twist.angular.y = 0;
    state_srv.request.model_state.twist.angular.z = 0;
    ros::service::call("/gazebo/set_model_state", state_srv);
}

void TrajCallback(const swarm_exp_msgs::SwarmTrajConstPtr &traj){
    trajs_.push_back(*traj);
    ready_ = true;
}

bool TryUpdateTraj(){
    if(trajs_.empty()) return false;
    double cur_t = ros::WallTime::now().toSec();
    if(trajs_.front().start_t > cur_t) return false;
    if(trajs_.front().state == 1){
        traj_state_ = 1;
        recover_pt_(0) = trajs_.front().recover_pt.x;
        recover_pt_(1) = trajs_.front().recover_pt.y;
        recover_pt_(2) = trajs_.front().recover_pt.z;
    }
    else if(trajs_.front().state == 2){
        traj_state_ = 2;
        start_t_ = trajs_.front().start_t;
        int col = 0;
        int t_idx = 0;
        Eigen::MatrixXd cM(3, 6);
        traj_.clear();

        for(int i = 0; i < trajs_.front().coef_p.size(); i++, col++){
            cM(0, col) = trajs_.front().coef_p[i].x;
            cM(1, col) = trajs_.front().coef_p[i].y;
            cM(2, col) = trajs_.front().coef_p[i].z;
            if(col == 5){
                traj_.emplace_back(double(trajs_.front().t_p[t_idx]), cM);
                col = -1;
                t_idx++;
            }
        }

        t_idx = 0;
        yaw_traj_.A_.resize(trajs_.front().coef_yaw.size());
        yaw_traj_.T_.resize(trajs_.front().t_yaw.size());
        for(int i = 0; i < trajs_.front().coef_yaw.size(); i++){
            yaw_traj_.A_(i) = double(trajs_.front().coef_yaw[i]);
            if((i + 1) % 6 == 0){
                yaw_traj_.T_(t_idx) = double(trajs_.front().t_yaw[t_idx]);
                t_idx++;
            }
        }
        double p,v ,a;
        yaw_traj_.GetCmd(yaw_traj_.T_.sum(), p, v, a);
    }
    trajs_.pop_front();
    return true;
}

int main(int argc, char** argv){
    ros::init(argc, argv, "frontier_test");
    ros::NodeHandle nh, nh_private("~");

    google::InitGoogleLogging(argv[0]);
    google::ParseCommandLineFlags(&argc, &argv, true);
    google::InstallFailureSignalHandler();

    // bool auto_takeoff_;
    traj_state_ = -1;
    ready_ = false;
    string ns = ros::this_node::getName();
    show_pub_ = nh.advertise<visualization_msgs::MarkerArray>(ns + "/traj_show", 5);
    traj_sub_ = nh.subscribe("/trajectory_cmd", 1, &TrajCallback);
    // odom_sub_ = nh.subscribe("/odom", 1, &OdomCallback);
    run_timer_ = nh.createTimer(ros::Duration(0.01), &RunCallback);
    trigger_pub_ = nh.advertise<std_msgs::Empty>("/start_trigger", 5);
    nh_private.param(ns + "/Exp/AutoTakeoff", auto_takeoff_, false);
    nh_private.param(ns + "/Exp/takeoff_x", takeoff_pos_(0), 0.0);
    nh_private.param(ns + "/Exp/takeoff_y", takeoff_pos_(1), 0.0);
    nh_private.param(ns + "/Exp/takeoff_z", takeoff_pos_(2), 1.0);
    nh_private.param(ns + "/opt/MaxVel", max_v_, 1.5);
    nh_private.param(ns + "/opt/MaxAcc", max_a_, 1.5);
    nh_private.param(ns + "/opt/YawVel", max_yawd_, 1.5);
    nh_private.param(ns + "/opt/YawAcc", max_yawdd_, 1.5);

    // cout<<"auto_takeoff_----------------------:"<<auto_takeoff_<<endl;

    // if(auto_takeoff_){
    //     std_msgs::EmptyPtr e;
    //     // ros::Duration(3.0).sleep();
    //     Takeoff(e);
    // }
    // else{
    //     ROS_WARN("takeoff init");
    //     takeoff_sub_ = nh.subscribe("/takeoff", 1, &Takeoff);
    // }
    ros::spin();
    return 0;
}