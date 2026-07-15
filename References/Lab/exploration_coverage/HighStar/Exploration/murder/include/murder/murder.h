#ifndef MURDER_H_
#define MURDER_H_

#include <ros/ros.h>
#include <thread>
#include <Eigen/Eigen>
#include <vector>
#include <list>
#include <visualization_msgs/MarkerArray.h>
#include <tr1/unordered_map>

// #include <multiDTG/dtg_structures.h>
// #include <multiDTG/multiDTG.h>
#include <block_map/color_manager.h>
#include <block_map/block_map.h>
#include <lowres_map/lowres_map.h>
#include <swarm_data/swarm_data.h>
#include <gcopter/traj_opt.h>
#include <frontier_grid/frontier_grid.h>
#include <yaw_planner/yaw_planner.h>
#include <data_statistics/computation_statistician.h>
#include <mp_planner/mp_planner_quick.h>
#include <exp_yaw_plan/exp_yaw_plan.h>
#include <quick_hull2d/quick_hull2d.h>

#include <visualization_msgs/MarkerArray.h>
#include <swarm_exp_msgs/SwarmTraj.h>
#include <nav_msgs/Odometry.h>
#include <sensor_msgs/Image.h>
#include <sensor_msgs/PointCloud2.h>

#include <message_filters/subscriber.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <message_filters/sync_policies/exact_time.h>
#include <message_filters/time_synchronizer.h>

class Murder{
typedef message_filters::sync_policies::ApproximateTime<sensor_msgs::Image, nav_msgs::Odometry>
      SyncPolicyImageOdom;
typedef shared_ptr<message_filters::Synchronizer<SyncPolicyImageOdom>> SynchronizerImageOdom;
typedef message_filters::sync_policies::ApproximateTime<sensor_msgs::PointCloud2, nav_msgs::Odometry>
      SyncPolicyPclOdom;
typedef shared_ptr<message_filters::Synchronizer<SyncPolicyPclOdom>> SynchronizerPclOdom;
public: 
    Murder(){};
    ~Murder(){cout<<"------==========v_mean:"<<v_total_ / max(v_num_, 1)<<endl;};
    void init(const ros::NodeHandle &nh, const ros::NodeHandle &nh_private);

    void GetBlockMapPtr(BlockMap *&BM){BM = &BM_;};
    void GetLowresMapPtr(lowres::LowResMap *&LRM){LRM = &LRM_;};
    void GetFrontierMapPtr(FrontierGrid *&FG){FG = &FG_;};
    void GetTrajectoryPtr(AtoTraj *&traj){traj = &TrajOpt_;};

    /**
     * @brief 
     * 
     * @param T current time 
     * @return int allow: 0; not allow: 1(time fail), 2(pos infeasible), 3(sensor not update); may allow: 4(viewpoint not sampled)
     */
    int AllowPlan(const double &T);

    /**
     * @brief set allow plan flags, and set the plan interval
     * 
     * @param intv interval
     */
    void SetPlanInterval(const double &intv);

    bool GoHome();

    bool LocalPlan();

    bool TrajCheck();

    void Test();

    int ViewPointsCheck(const double &t);
    void ImgOdomCallback(const sensor_msgs::ImageConstPtr& img,
                               const nav_msgs::OdometryConstPtr& odom);
    void PclOdomCallback(const sensor_msgs::PointCloud2ConstPtr& pcl,
                               const nav_msgs::OdometryConstPtr& odom);
    
    // for test
    bool PlanTraj(Eigen::Vector3d &pos, double &yaw);
    void BodyOdomCallback(const nav_msgs::OdometryConstPtr& odom);
    void ShowTraj(vector<Eigen::Vector3d> &path, vector<Eigen::MatrixX4d> &h);
    void ShowTrajCover(vector<double> &Cts, /*vector<int> &trajCoverIdx,*/ vector<vector<Eigen::Vector3d>> &hullPts, vector<vector<Eigen::Vector3d>> &coverPts);
    void ShowPath(list<Eigen::Vector3d> &path, int id);
    bool TestFunc(const Eigen::Matrix<double, 4, 3> &startpva, const Eigen::Matrix<double, 4, 3> &endpva, 
                            const vector<Eigen::MatrixX4d> &h, const vector<Eigen::Matrix3Xd> &p);
    void GetExpTarget(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as, pair<int, int> &target, Eigen::Vector4d &target_vp, 
                            Eigen::Vector4d &sec_target, list<Eigen::Vector3d> &path, double &expect_t, 
                            double yaws, double yawds, double yawv, double yawa, double vel, double acc, int exclude_f, bool &ans1, bool &ans2);
    bool TrajPlan(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as,
            const Eigen::Vector3d &pe, const Eigen::Vector3d &ve, const Eigen::Vector3d &ae, const double &yps, 
            const double &yds, const double &ydds, const double &ype, const double &yde, const double &ydde, 
            const int &target_id, pair<Eigen::Vector4d, bool> &next_tar, vector<Eigen::Vector3d> &path);
    void PublishTraj(bool recover);

    Eigen::Vector4d init_pose_;
    double plan_t_, replan_t_;
    double traj_start_t_, traj_end_t_;
    double volume_t_;

private:

    bool TrajPlanB(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as,
            const Eigen::Vector3d &pe, const Eigen::Vector3d &ve, const Eigen::Vector3d &ae, const double &yps, 
            const double &yds, const double &ydds, const double &ype, const double &yde, const double &ydde, const Eigen::Vector3d &gazept);
    bool CoverTrajPlan(const Eigen::Matrix<double, 4, 3> &startpva, const Eigen::Matrix<double, 4, 3> &endpva, 
                            const vector<Eigen::MatrixX4d> &h, const vector<Eigen::Matrix3Xd> &p, const int &tar_id, 
                            const pair<Eigen::Vector4d, bool> &next_tar, double min_t);
    // void PlanYaw(const double &yps, const double &yds, const double &ydds, const double &ype, 
    //         const double &yde, const double &ydde, const Eigen::Vector3d &gazept,bool gaze = false);
    void PublishSecondFOV(const Eigen::Vector4d &vp, const bool &add);
    void Debug(const Eigen::Vector3d &pt1, const Eigen::Vector3d &pt2);
    void Debug(list<Eigen::Vector3d> &pts);
    void Debug(vector<Eigen::Vector3d> &pts);
    inline void DrawFOVs(const vector<Eigen::Vector3d> &p, const vector<Eigen::Quaterniond> &R, 
        visualization_msgs::Marker &mk, double factor = 1.0);
    inline void GetHull(const vector<Eigen::Vector3d> &pts, const Eigen::Vector3d &p, const Eigen::Vector3d &a, const double &yaw, 
        Eigen::Matrix3Xd &hull, Eigen::Matrix3Xd &hull_vis);
    BlockMap BM_;
//     DTG::MultiDTG MDTG_;
    // YawPlanner YawP_;
    lowres::LowResMap LRM_;
    AtoTraj TrajOpt_;
    FrontierGrid FG_;
    ColorManager CM_;
    FastMotion FM_;
    ExpYawPlan EYP_;

    ros::Publisher show_pub_, traj_pub_;
    ros::Subscriber odom_sub_;
    ros::NodeHandle nh_, nh_private_;

    shared_ptr<message_filters::Subscriber<nav_msgs::Odometry>> vi_odom_sub_;
    shared_ptr<message_filters::Subscriber<sensor_msgs::Image>> depth_sub_;
    shared_ptr<message_filters::Subscriber<sensor_msgs::PointCloud2>> pcl_sub_;
    SynchronizerImageOdom sync_image_odom_;
    SynchronizerPclOdom sync_pcl_odom_;

    Eigen::Vector3d p_, v_, home_p_;
    Eigen::Vector3d last_safe_, last_vi_pos_;
    Eigen::Vector4d target_, recover_pose_;
    int target_f_id_, target_v_id_; // -1: no target now, -2: go home
    Eigen::Matrix4d robot_pose_;
    Eigen::Matrix4d FOV_; //row: a(0-2), b(3), a^t*x <= b
    vector<Eigen::Vector3d> fov_line_pts_;
    list<double> cts_; // cover time
    double dyaw_max_, ddyaw_max_;
    double yaw_, yaw_v_;
    bool sensor_flag_, have_odom_, replan_img_flag_;
    bool use_motion_, use_terminal_corridor_, use_dir_corridor_, use_cover_trajectory_;
    bool use_fg_vp_;
    bool volume_test_;
    double update_interval_;
    int v_num_;
    double v_total_;
    double last_map_update_t_;    //blockmap & DTG
    double reach_out_t_;
    double traj_length_;
    double exc_duration_, replan_duration_, check_duration_;
    double strong_check_interval_;
    int local_max_search_iter_;
    int global_max_search_iter_;
    bool stat_;
    bool first_odom_;
};


inline void Murder::DrawFOVs(const vector<Eigen::Vector3d> &p, const vector<Eigen::Quaterniond> &R,
        visualization_msgs::Marker &mk, double factor){
    geometry_msgs::Point gpt;
    Eigen::Vector3d ept;
    for(int i = 0; i < p.size(); i++){
        for(auto &pfov : fov_line_pts_){
            ept = R[i].toRotationMatrix() * (pfov * factor) + p[i];
            gpt.x = ept(0);
            gpt.y = ept(1);
            gpt.z = ept(2);
            mk.points.emplace_back(gpt);
        }
    }
    if(mk.points.size() == 0) mk.action = visualization_msgs::Marker::DELETE;
}

inline void Murder::GetHull(const vector<Eigen::Vector3d> &pts, const Eigen::Vector3d &p, const Eigen::Vector3d &a, const double &yaw, 
        Eigen::Matrix3Xd &hull, Eigen::Matrix3Xd &hull_vis){
    double yaw2 = yaw / 2;
    double siny2 = sin(yaw2);
    double cosy2 = cos(yaw2);
    Eigen::Vector3d z = a + Eigen::Vector3d(0, 0, 9.8);
    z.normalize();
    Eigen::Quaterniond q;
    q.x() = -z(1)*cosy2 + z(0)*siny2;
    q.y() = z(0)*cosy2 + z(1)*siny2;
    q.z() = (1 + z(2))*siny2;
    q.w() = (1 + z(2))*cosy2;
    q.coeffs() /= sqrt(2*(1 + z(2)));
    Eigen::Matrix3d R = q.toRotationMatrix().transpose();
    // cout<<"R0:"<<R<<endl;

    vector<Eigen::Vector2d> pjPts;
    vector<Eigen::Vector3d> Pts;
    Eigen::Vector3d itp;
    Eigen::Vector2d itp2;
    for(auto &pt : pts){
        itp = R*(pt - p);
        if(itp(0) <= 0) {
            ROS_ERROR("error pt!");
            cout<<itp.transpose()<<"   "<<pt.transpose()<<endl;
            continue;
        }
        itp2(0) = itp(1) / itp(0) * 0.5;
        itp2(1) = itp(2) / itp(0) * 0.5;
        pjPts.emplace_back(itp2);
        Pts.emplace_back(pt);
    }

    vector<pair<Eigen::Vector2d, int>> hull2;
    QuickHull(pjPts, hull2);
    hull_vis.resize(3, hull2.size());
    Eigen::Matrix3d Rt = R.transpose();
    // cout<<"R1:"<<R<<endl;
    // cout<<"z:"<<z.transpose()<<endl;
    for(int i = 0; i < hull2.size(); i++){
        hull_vis.col(i) = Pts[hull2[i].second];
        // itp(0) = 0.5;
        // itp(1) = hull2[i].first(0);
        // itp(2) = hull2[i].first(1);
        // hull_vis.col(i) = Rt*itp + p;
    } 

    int samp_n = 0;
    double d;
    Eigen::Vector3d itp_last, dp, samp_p;
    itp_last(0) = 0.5;
    itp_last(1) = hull2[0].first(0);
    itp_last(2) = hull2[0].first(1);
    vector<Eigen::Vector3d> pl;
    for(int i = 1; i < hull2.size(); i++){
        itp(0) = 0.5;
        itp(1) = hull2[i].first(0);
        itp(2) = hull2[i].first(1);
        dp = itp - itp_last;
        d = dp.norm();
        samp_n = ceil(d * 6.0);
        for(int i = 0; i < samp_n; i++){
            samp_p = itp_last + dp * (i+1)/ samp_n;
            pl.emplace_back(samp_p);
        }
        itp_last = itp;
    }
    itp_last(0) = 0.5;
    itp_last(1) = hull2.back().first(0);
    itp_last(2) = hull2.back().first(1);
    itp_last(0) = 0.5;
    itp_last(1) = hull2[0].first(0);
    itp_last(2) = hull2[0].first(1);
    dp = itp - itp_last;
    d = dp.norm();
    samp_n = ceil(d * 6.0);
    for(int i = 0; i < samp_n; i++){
        samp_p = itp_last + dp * (i+1)/ samp_n;
        pl.emplace_back(samp_p);
    }
    hull.resize(3, pl.size());
    for(int i = 0; i < pl.size(); i++){
        hull.col(i) = Rt*pl[i] + p;
    }
}


#endif
