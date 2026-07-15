#include<murder/murder.h>

void Murder::init(const ros::NodeHandle &nh, const ros::NodeHandle &nh_private){
    std::string ns = ros::this_node::getName();
    ROS_WARN("HighStar Murder::init stage=begin ns=%s", ns.c_str());
    nh_private.param(ns + "/Exp/traj_length", traj_length_, 10.0);
    nh_private.param(ns + "/Exp/local_path_search", local_max_search_iter_, 1000);
    nh_private.param(ns + "/Exp/global_path_search", global_max_search_iter_, 3000);
    nh_private.param(ns + "/Exp/strong_check_interval", strong_check_interval_, 3.0);
    nh_private.param(ns + "/Exp/replan_duration", replan_duration_, 1.5);
    nh_private.param(ns + "/Exp/check_duration", check_duration_, 3.5);
    nh_private.param(ns + "/Exp/exc_duration", exc_duration_, 0.5);
    nh_private.param(ns + "/Exp/takeoff_x", init_pose_(0), 0.0);
    nh_private.param(ns + "/Exp/takeoff_y", init_pose_(1), 0.0);
    nh_private.param(ns + "/Exp/takeoff_z", init_pose_(2), 1.0);
    nh_private.param(ns + "/Exp/takeoff_yaw", init_pose_(3), 0.0);
    nh_private.param(ns + "/Exp/reach_out_t", reach_out_t_, 0.1);
    nh_private.param(ns + "/Exp/statistic", stat_, false);
    nh_private.param(ns + "/opt/YawVel", dyaw_max_, 2.0);
    nh_private.param(ns + "/opt/YawAcc", ddyaw_max_, 2.0);
    nh_private.param(ns + "/Exp/UseMotion", use_motion_, true);
    nh_private.param(ns + "/Exp/UseTerminalCorridor", use_terminal_corridor_, true);
    nh_private.param(ns + "/Exp/UseDirCorridor", use_dir_corridor_, true);
    nh_private.param(ns + "/Exp/UseCoverTrajectory", use_cover_trajectory_, true);
    nh_private.param(ns + "/Exp/VolumeTest", volume_test_, false);
    nh_private.param(ns + "/Exp/UpdateInterval", update_interval_, 0.2);
    std::string sensor_input;
    nh_private.param(ns + "/Exp/SensorInput", sensor_input, std::string("depth"));

    use_dir_corridor_ = use_dir_corridor_ & use_terminal_corridor_;
    cout<<"=======------"<<use_dir_corridor_<<endl;
    cout<<use_terminal_corridor_<<endl;
    cout<<use_motion_<<endl;
    ROS_WARN("HighStar Murder::init stage=params sensor_input=%s", sensor_input.c_str());
    Eigen::Vector4d fovangle;
    nh_private.param(ns + "/EXP/FovHorizontalUp", fovangle(0), 0.9);
    nh_private.param(ns + "/EXP/FovHorizontalDown", fovangle(1), -0.9);
    nh_private.param(ns + "/EXP/FovVerticalUp", fovangle(2), 0.65);
    nh_private.param(ns + "/EXP/FovVerticalDown", fovangle(3), -0.65);
    double sensor_range;
    nh_private.param(ns + "/block_map/sensor_max_range", sensor_range, 5.0);

    volume_t_ = ros::WallTime::now().toSec() - 100;


    FOV_.setZero();
    fov_line_pts_.clear();
    fov_line_pts_.reserve(16);
    FOV_(0, 0) = -sin(fovangle(0));
    FOV_(0, 1) = cos(fovangle(0));
    FOV_(1, 0) = sin(fovangle(1));
    FOV_(1, 1) = -cos(fovangle(1));
    FOV_(2, 0) = -sin(fovangle(2));
    FOV_(2, 2) = cos(fovangle(2));
    FOV_(3, 0) = sin(fovangle(3));
    FOV_(3, 2) = -cos(fovangle(3));
    Eigen::Vector3d upleft(cos(fovangle(2))*cos(fovangle(0)), cos(fovangle(2))*sin(fovangle(0)), sin(fovangle(2))), 
    upright(cos(fovangle(2))*cos(fovangle(1)), cos(fovangle(2))*sin(fovangle(1)), sin(fovangle(2))), 
    downleft(cos(fovangle(3))*cos(fovangle(0)), cos(fovangle(3))*sin(fovangle(0)), sin(fovangle(3))), 
    downright(cos(fovangle(3))*cos(fovangle(1)), cos(fovangle(3))*sin(fovangle(1)), sin(fovangle(3))), ori(0,0,0);
    double ks = sensor_range*0.2;
    fov_line_pts_.emplace_back(upleft * ks / upleft(0));
    cout<<"fov_line_pts_.back()"<<fov_line_pts_.back().transpose()<<endl;
    fov_line_pts_.emplace_back(ori);
    fov_line_pts_.emplace_back(upright * ks / upright(0));
    fov_line_pts_.emplace_back(ori);
    fov_line_pts_.emplace_back(downleft * ks / downleft(0));
    fov_line_pts_.emplace_back(ori);
    fov_line_pts_.emplace_back(downright * ks / downright(0));
    fov_line_pts_.emplace_back(ori);

    fov_line_pts_.emplace_back(upleft * ks / upleft(0));
    fov_line_pts_.emplace_back(upright * ks / upright(0));

    fov_line_pts_.emplace_back(upright * ks / upright(0));
    fov_line_pts_.emplace_back(downright * ks / downright(0));

    fov_line_pts_.emplace_back(downright * ks / downright(0));
    fov_line_pts_.emplace_back(downleft * ks / downleft(0));

    fov_line_pts_.emplace_back(downleft * ks / downleft(0));
    fov_line_pts_.emplace_back(upleft * ks / upleft(0));
    ROS_WARN("HighStar Murder::init stage=fov_ready line_pts=%zu sensor_range=%.3f", fov_line_pts_.size(), sensor_range);

    nh_ = nh;
    nh_private_ = nh_private;

    ROS_WARN("HighStar Murder::init stage=block_map_begin");
    BM_.init(nh_, nh_private_);
    ROS_WARN("HighStar Murder::init stage=block_map_done");
    ROS_WARN("HighStar Murder::init stage=color_manager_begin");
    CM_.init(nh_, nh_private_);
    ROS_WARN("HighStar Murder::init stage=color_manager_done");
    LRM_.SetColorManager(&CM_);

    LRM_.SetMap(&BM_);
    ROS_WARN("HighStar Murder::init stage=lowres_map_begin");
    LRM_.init(nh, nh_private);
    ROS_WARN("HighStar Murder::init stage=lowres_map_done");
    ROS_WARN("HighStar Murder::init stage=traj_opt_begin");
    TrajOpt_.Init(nh_, nh_private_);
    ROS_WARN("HighStar Murder::init stage=traj_opt_done");

    ROS_WARN("HighStar Murder::init stage=motion_begin");
    FM_.init(nh_, nh_private_);
    ROS_WARN("HighStar Murder::init stage=motion_done");
    FM_.SetLowResMap(&LRM_);
    // MDTG_.SetColorManager(&CM_);
    // MDTG_.SetBlockMap(&BM_);
    // MDTG_.SetLowresMap(&LRM_);
    // MDTG_.init(nh_, nh_private_);
    v_num_ = 0;
    v_total_ = 0;
    FG_.SetMap(BM_);
    FG_.SetLowresMap(LRM_);
    FG_.SetMotion(FM_);
    FG_.SetColorManager(CM_);
    ROS_WARN("HighStar Murder::init stage=frontier_grid_begin");
    FG_.init(nh_, nh_private_);
    ROS_WARN("HighStar Murder::init stage=frontier_grid_done");
    
    ROS_WARN("HighStar Murder::init stage=exp_yaw_begin");
    EYP_.init(nh_, nh_private_);
    ROS_WARN("HighStar Murder::init stage=exp_yaw_done");
    EYP_.SetLowresMap(LRM_);
    EYP_.SetMap(BM_);
    EYP_.SetFrontierGrid(FG_);
    // MDTG_.SetFrontierMap(&FG_);

    // YawP_.init(nh, nh_private);

    last_safe_ = init_pose_.head(3);
    home_p_ = init_pose_.head(3);

    last_map_update_t_ = ros::WallTime::now().toSec();
    traj_end_t_ = last_map_update_t_ - 0.1;
    replan_t_ =  last_map_update_t_ - 0.1;
    have_odom_ = false;
    target_f_id_ = -1;
    target_v_id_ = -1;
    first_odom_ = false;
    sensor_flag_ = false;
    vi_odom_sub_.reset(new message_filters::Subscriber<nav_msgs::Odometry>(nh_, "/vi_odom", 10));
    if(sensor_input == "pointcloud" || sensor_input == "pcl"){
        ROS_WARN("HighStar Murder::init stage=pcl_subscribe_begin");
        pcl_sub_.reset(new message_filters::Subscriber<sensor_msgs::PointCloud2>(nh_, "/pointcloud", 10));
        sync_pcl_odom_.reset(new message_filters::Synchronizer<SyncPolicyPclOdom>(
            SyncPolicyPclOdom(100), *pcl_sub_, *vi_odom_sub_));
        sync_pcl_odom_->registerCallback(boost::bind(&Murder::PclOdomCallback, this,  _1, _2));
        ROS_WARN("HighStar sensor input: pointcloud");
    }
    else{
        ROS_WARN("HighStar Murder::init stage=depth_subscribe_begin");
        depth_sub_.reset(new message_filters::Subscriber<sensor_msgs::Image>(nh_, "/depth", 10));
        sync_image_odom_.reset(new message_filters::Synchronizer<SyncPolicyImageOdom>(
            SyncPolicyImageOdom(100), *depth_sub_, *vi_odom_sub_));
        sync_image_odom_->registerCallback(boost::bind(&Murder::ImgOdomCallback, this,  _1, _2));
        ROS_WARN("HighStar sensor input: depth");
    }
    ROS_WARN("HighStar Murder::init stage=odom_subscribe_begin");
    odom_sub_ = nh_.subscribe("/odom", 1, &Murder::BodyOdomCallback, this);
    show_pub_ = nh_.advertise<visualization_msgs::MarkerArray>("/Murder/Show", 5);
    traj_pub_ = nh_.advertise<swarm_exp_msgs::SwarmTraj>("/Murder/Traj", 1);
    ROS_WARN("HighStar Murder::init stage=done");
}

int Murder::AllowPlan(const double &T){// to be modified

    /* not satisfy plan interval */
    if(T - plan_t_ < 0){
        return 1;
    }

    /* not in free space */
    if(!have_odom_){
        ROS_WARN_THROTTLE(2.0, "HighStar AllowPlan blocked: no body odom yet");
        return 2;
    }
    if(!LRM_.IsFeasible(p_)){
        auto node = LRM_.GetNode(p_);
        std::string node_state = "null";
        if(node == LRM_.Outnode_){
            node_state = "outnode";
        }
        else if(node != NULL){
            node_state = std::string("flags=") + node->flags_.to_string();
        }
        ROS_WARN_THROTTLE(
            2.0,
            "HighStar AllowPlan blocked: current pos infeasible p=(%.3f, %.3f, %.3f) node=%s",
            p_(0), p_(1), p_(2), node_state.c_str());
        return 2;
    }
    last_safe_ = p_;

    /* sensor not update */
    if(!sensor_flag_){
        ROS_WARN_THROTTLE(
            2.0,
            "HighStar AllowPlan: waiting for synced depth/odom map update p=(%.3f, %.3f, %.3f)",
            p_(0), p_(1), p_(2));
        return 3;
    }

    /* traj time up */
    if(T - replan_t_ > 0){
        return 5;
    }

    /* viewpoints not sampled */
    // if(!FG_.sample_flag_){
    //     return 4;
    // }


    return 0;
}

void Murder::SetPlanInterval(const double &intv){
    plan_t_ = ros::WallTime::now().toSec() + intv;
}

// bool Murder::GoHome(){
//     Eigen::Vector3d ps, vs, as, pe, ve, ae;
//     double ys, yds, ydds, ye, yde, ydde;
//     double hand_t = ros::WallTime::now().toSec() + reach_out_t_; 
//     double cur_t = ros::WallTime::now().toSec();
//     if(hand_t > traj_end_t_){
//         hand_t = cur_t;
//         ps = p_;
//         vs = v_;
//         as.setZero();
//         ve.setZero();
//         ae.setZero();
//         ys = yaw_;
//         yds = yaw_v_;
//         ydds = 0;
//         yde = 0; 
//         ydde = 0;
//         ROS_ERROR("Not Connect!!!!!!!!!!");
//     }
//     else{
//         Eigen::Vector4d p4s, v4s, a4s;
//         p4s = TrajOpt_.traj.getPos(hand_t - traj_start_t_);
//         ps = p4s.head(3);
//         while(!LRM_.IsFeasible(ps) && hand_t > cur_t){
//             hand_t -= reach_out_t_ / 10;
//             p4s = TrajOpt_.traj.getPos(hand_t - traj_start_t_);
//             ps = p4s.head(3);
//         }
//         if(!LRM_.IsFeasible(ps)){
//             hand_t = cur_t;
//             ps = p_;
//         }
//         v4s = TrajOpt_.traj.getVel(hand_t - traj_start_t_);
//         a4s = TrajOpt_.traj.getAcc(hand_t - traj_start_t_);
//         vs = v4s.head(3);
//         as = a4s.head(3);
//         ys = p4s(3);
//         yds = v4s(3);
//         ydds = a4s(3);
//         ve.setZero();
//         ae.setZero();
//         // YawP_.GetCmd(hand_t - traj_start_t_, ys, yds, ydds);
//         yde = 0; 
//         ydde = 0;
//     }
//     pe = home_p_;
//     ye = 0;
//     if(TrajPlanB(ps, vs, as, pe, ve, 
//                 ae, ys, yds, ydds, target_(3), yde, ydde, home_p_ + Eigen::Vector3d(1.0, 0, 0))){
//         traj_start_t_ = hand_t;
//         traj_end_t_ = TrajOpt_.traj.getTotalDuration() + traj_start_t_;
//         replan_t_ = min(replan_duration_, TrajOpt_.traj.getTotalDuration()) + traj_start_t_;
//         target_f_id_ = -2;
//         target_v_id_ = -2;
//         PublishTraj(false);
//         return true;
//     }
//     return false;
// }

bool Murder::LocalPlan(){
    ROS_WARN("local plan!0");
    ROS_WARN(
        "HighStar LocalPlan enter: p=(%.3f, %.3f, %.3f) v=(%.3f, %.3f, %.3f) sensor_flag=%d have_odom=%d target=(%d,%d)",
        p_(0), p_(1), p_(2),
        v_(0), v_(1), v_(2),
        sensor_flag_ ? 1 : 0,
        have_odom_ ? 1 : 0,
        target_f_id_,
        target_v_id_);
    double ts = ros::WallTime::now().toSec();
    // if(stat_) {
    //     BM_.CS_.StartTimer(1);
    //     BM_.CS_.StartTimer(0);
    // }
    pair<int, int> f_v_target;
    list<Eigen::Vector3d> path;
    Eigen::Vector3d ps, vs, as, pe, ve, ae;
    double ys, yds, ydds, ye, yde, ydde;
    double hand_t = ros::WallTime::now().toSec() + reach_out_t_; 
    double cur_t = ros::WallTime::now().toSec();
    if(hand_t > traj_end_t_){ // the trajectory is going to end within reach_out_t_
        if(cur_t - traj_end_t_ > 0.0){ // trajectory expires, use current uav state
            hand_t = ros::WallTime::now().toSec();
            ps = p_;
            vs = v_;
            as.setZero();
            ve.setZero();
            ae.setZero();
            ys = yaw_;
            yds = yaw_v_;
            ydds = 0;
            yde = 0; 
            ydde = 0;
        }
        else{   // current trajectory still not expires, , so use the terminal state as the replanning state
            Eigen::Vector4d p4s, v4s, a4s;
            hand_t = max(traj_end_t_ - 1e-3 - ts, 0.0) + ts;
            p4s = TrajOpt_.traj.getPos(traj_end_t_ - traj_start_t_ - 1e-3);
            v4s = TrajOpt_.traj.getVel(traj_end_t_ - traj_start_t_ - 1e-3);
            a4s = TrajOpt_.traj.getAcc(traj_end_t_ - traj_start_t_ - 1e-3);
            ps = p4s.head(3);
            vs = v4s.head(3);
            as = a4s.head(3);
            ys = p4s(3);
            yds = v4s(3);
            ydds = a4s(3);
            ve.setZero();
            ae.setZero();
            yde = 0; 
            ydde = 0;
        }
    }
    else{ // use the state at cur_t + reach_out_t_
        Eigen::Vector4d p4s, v4s, a4s;
        p4s = TrajOpt_.traj.getPos(hand_t - traj_start_t_);
        ps = p4s.head(3);
        while(!LRM_.IsFeasible(ps) && hand_t > cur_t){
            hand_t -= reach_out_t_ / 10;
            p4s = TrajOpt_.traj.getPos(hand_t - traj_start_t_);
            ps = p4s.head(3);
        }
        if(!LRM_.IsFeasible(ps)){
            hand_t = cur_t;
            ps = p_;
        }
        v4s = TrajOpt_.traj.getVel(hand_t - traj_start_t_);
        a4s = TrajOpt_.traj.getAcc(hand_t - traj_start_t_);
        vs = v4s.head(3);
        as = a4s.head(3);
        ys = p4s(3);
        yds = v4s(3);
        ydds = a4s(3);
        ve.setZero();
        ae.setZero();
        yde = 0; 
        ydde = 0;
    }
    FG_.SampleFrontierNeighbours(target_f_id_, ps); // sample viewpoints before planning

    Eigen::Vector4d sec_target;
    bool ans1, ans2; // ans1: find the target, ans2: find a good terminal direction 
    double input_v; // max vel
    input_v = TrajOpt_.upboundVec_[0];
    double expect_t; // expected motion cost

    // find the next target using motion-primitive-based cost evaluation
    GetExpTarget(ps, vs, as, f_v_target, target_, sec_target, path, expect_t, ys, yds, dyaw_max_, ddyaw_max_,
                    input_v, TrajOpt_.upboundVec_[1], -1, ans1, ans2);
    ROS_WARN(
        "HighStar LocalPlan target result: ans1=%d ans2=%d path_size=%zu expect_t=%.3f target=(%.3f, %.3f, %.3f, %.3f)",
        ans1 ? 1 : 0,
        ans2 ? 1 : 0,
        path.size(),
        expect_t,
        target_(0), target_(1), target_(2), target_(3));
    double exp_t = ros::WallTime::now().toSec() - ts; // exploration target planning time
    if(!ans1){ // no target found, plan fails
        target_f_id_ = -1;
        target_v_id_ = -1;
        ROS_WARN("fail find target");
        // if(stat_) BM_.CS_.EndTimer(1);
        return false;
    }
    // PublishSecondFOV(sec_target, ans2);
    pair<Eigen::Vector4d, bool> next_tar;
    next_tar.first = sec_target;
    next_tar.second = ans2;

    pe = target_.head(3);
    ye = target_(3);

    vector<Eigen::Vector3d> path_vec;
    for(auto &pc : path) {
        path_vec.emplace_back(pc);
    }

    cur_t = ros::WallTime::now().toSec();
    if(cur_t > hand_t){ // if the target plan takes too long, reculculate the initial state
        Eigen::Vector3d ps_temp, vs_temp, as_temp;
        double ys_temp, yds_temp, ydds_temp;
        double hand_t_new = cur_t + reach_out_t_ * 0.25; 
        if(hand_t_new > traj_end_t_){
            if(cur_t - traj_end_t_ > 0.0){
                hand_t_new = ros::WallTime::now().toSec();
                ps_temp = p_;
                vs_temp = v_;
                as_temp.setZero();
                ve.setZero();
                ae.setZero();
                ys_temp = yaw_;
                yds_temp = yaw_v_;
                ydds_temp = 0;
                yde = 0; 
                ydde = 0;

            }
            else{
                Eigen::Vector4d p4s, v4s, a4s;
                hand_t_new = max(traj_end_t_ - 1e-3 - cur_t, 0.0) + cur_t;
                p4s = TrajOpt_.traj.getPos(traj_end_t_ - traj_start_t_ - 1e-3);
                v4s = TrajOpt_.traj.getVel(traj_end_t_ - traj_start_t_ - 1e-3);
                a4s = TrajOpt_.traj.getAcc(traj_end_t_ - traj_start_t_ - 1e-3);
                ps_temp = p4s.head(3);
                vs_temp = v4s.head(3);
                as_temp = a4s.head(3);
                ys_temp = p4s(3);
                yds_temp = v4s(3);
                ydds_temp = a4s(3);
                ve.setZero();
                ae.setZero();
                // YawP_.GetCmd(cur_t - traj_start_t_, ys, yds, ydds);
                yde = 0; 
                ydde = 0;
            }
        }
        else{
            Eigen::Vector4d p4s, v4s, a4s;
            p4s = TrajOpt_.traj.getPos(hand_t_new - traj_start_t_);
            ps_temp = p4s.head(3);
            while(!LRM_.IsFeasible(ps_temp) && hand_t_new > cur_t){
                hand_t_new -= reach_out_t_ / 10;
                p4s = TrajOpt_.traj.getPos(hand_t_new - traj_start_t_);
                ps_temp = p4s.head(3);
            }
            if(!LRM_.IsFeasible(ps_temp)){
                hand_t_new = cur_t;
                ps_temp = p_;
            }
            v4s = TrajOpt_.traj.getVel(hand_t_new - traj_start_t_);
            a4s = TrajOpt_.traj.getAcc(hand_t_new - traj_start_t_);
            vs_temp = v4s.head(3);
            as_temp = a4s.head(3);
            ys_temp = p4s(3);
            yds_temp = v4s(3);
            ydds_temp = a4s(3);
            ve.setZero();
            ae.setZero();
            yde = 0; 
            ydde = 0;
        }
        vector<Eigen::Vector3d> path_temp;// = path_vec;
        // path_vec.clear();
        ROS_WARN("path research!!!!!!!!!");
        if(!LRM_.GetPath(ps_temp, pe, path_temp, false, 50000)){
            hand_t = hand_t_new;
            path_vec = path_temp;
            ps = ps_temp;
            vs = vs_temp;
            as = as_temp;
            ys = ys_temp;
            yds = yds_temp;
            ydds = ydds_temp;
            return false;
            // if(stat_) BM_.CS_.EndTimer(1);
        }
    }



    if(TrajPlan(ps, vs, as, pe, ve, 
            ae, ys, yds, ydds, target_(3), yde, ydde, f_v_target.first, next_tar, path_vec)){ // optimize trajectory
        PublishSecondFOV(sec_target, next_tar.second); // visualization

        target_f_id_ = f_v_target.first;
        target_v_id_ = f_v_target.second;
        traj_start_t_ = hand_t;
        for(auto &t : cts_) t += hand_t;
        double traj_du = TrajOpt_.traj.getTotalDuration();
        double replan_seg = min(replan_duration_, traj_du - reach_out_t_ * 1.9);
        if(use_motion_ &&  traj_du > expect_t * 1.3){
            replan_seg = min(replan_seg, replan_duration_ * 0.2);
            cout<<"\033[44m replan replan:"<<replan_seg<<"\033[0m"<<endl;
        }
        traj_end_t_ = traj_du + traj_start_t_;
        replan_t_ = replan_seg + /*min(replan_duration_, traj_du - reach_out_t_ * 1.9) + */traj_start_t_;
        replan_img_flag_ = true;
        cout<<"plan success!"<<endl;
        cout<<"traj_du:"<<traj_du<<endl;
        cout<<"Plan total:"<<ros::WallTime::now().toSec() - ts<<endl;
        
        PublishTraj(false); // publish the traj to the command publisher
        // if(stat_) BM_.CS_.EndTimer(0);
        return true;
    }
    else{
        ROS_WARN("LocalPlan TrajPlanB fail");
        // if(stat_) BM_.CS_.EndTimer(1);
        return false;
    }
}

bool Murder::TrajCheck(){
    double cur_t = max(ros::WallTime::now().toSec(), traj_start_t_);

    if(cur_t > traj_end_t_ - 1e-3 || cur_t > replan_t_) { // traj time out
        // sensor_flag_ = false; // need to update map
        return false;
    }

    double end_t = min(cur_t + check_duration_, traj_end_t_ - 1e-3);
    end_t -= traj_start_t_;
    Eigen::Vector3d last_p = TrajOpt_.traj.getPos(cur_t).head(3);
    Eigen::Vector3d p, r_size;
    r_size = LRM_.GetRobotSize();
    for(double t = cur_t - traj_start_t_; t < end_t; t += 0.05){
        p = TrajOpt_.traj.getPos(t).head(3);
        for(int dim = 0; dim < 3; dim ++){
            if(abs(p(dim) - last_p(dim)) > BM_.resolution_){ 
                if(!BM_.PosBBXFree(p, r_size)) { // collide
                    sensor_flag_ = false; // need to update map
                    return false;
                }
                break;
            } 
        }
    }
    return true;
}


int Murder::ViewPointsCheck(const double &t){
    if(use_fg_vp_){
        if(target_f_id_ == -1 || target_v_id_ == -1) return 1;
        Eigen::Vector4d tar_pose;
        FG_.GetVp(target_f_id_, target_v_id_, tar_pose);
        double dp, dyaw;
        dyaw = abs(FG_.YawDiff(yaw_, tar_pose(3)));
        dp = (tar_pose.head(3) - p_).norm();
        if(!FG_.StrongCheckViewpoint(target_f_id_, target_v_id_, true) || (dp < 1.25 && dyaw < 0.5)){ // close to the target, delete the viewpoint
            if(target_f_id_ >= 0 && target_f_id_ < FG_.f_grid_.size() && 0 <= target_v_id_ && target_v_id_ < FG_.f_grid_[target_f_id_].local_vps_.size())
                FG_.RemoveVp(target_f_id_, target_v_id_);
            sensor_flag_ = false; // need to update map
            return 1;
        }
    }
    else{
        double dp, dyaw;
        dyaw = abs(FG_.YawDiff(yaw_, target_(3)));
        dp = (target_.head(3) - p_).norm();
        if(!FG_.StrongCheckViewpoint(target_, true) || (dp < 1.25 && dyaw < 0.5)){ // close to the target, delete the viewpoint
            return 1;
        }
    }
    return 0;
}

bool Murder::TrajPlan(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as,
        const Eigen::Vector3d &pe, const Eigen::Vector3d &ve, const Eigen::Vector3d &ae, const double &yps, 
        const double &yds, const double &ydds, const double &ype, const double &yde, const double &ydde, 
        const int &target_id, pair<Eigen::Vector4d, bool> &next_tar, vector<Eigen::Vector3d> &path){
    vector<Eigen::Vector3d> path_pruned;
    vector<Eigen::MatrixX4d> h;
    vector<Eigen::Matrix3Xd> p;
    // if(stat_) BM_.CS_.StartTimer(3);
    if(LRM_.FindCorridors(path, h, p, path_pruned, traj_length_)){

        Eigen::Matrix<double, 4, 3> startpva, endpva;
        startpva.setZero();
        endpva.setZero();
        startpva.col(0).head(3) = ps;
        startpva.col(1).head(3) = vs;
        startpva.col(2).head(3) = as;
        startpva(3, 0) = yps;
        startpva(3, 1) = yds;
        startpva(3, 2) = ydds;
        endpva.col(0).head(3) = path_pruned.back();
        if((path.back() - path_pruned.back()).norm() > LRM_.node_scale_.norm() * 0.51){
            next_tar.second = false;
        }


        double dyaw = FG_.YawDiff(ype, yps);

        endpva(3, 0) = yps + dyaw;
        // cout<<"end p:"<<path_pruned.back().transpose()<<endl;
        // if((path_pruned.back() - path.back()).norm() < 0.3) {
        //     endpva.col(1) = ve;
        // }
        // cout<<"startpva:\n"<<startpva<<endl;
        // cout<<"path:"<<path.front()<<endl;
        // cout<<"endpva:\n"<<endpva<<endl;
        // cout<<"h size:"<<h.size()<<endl;
        // for(auto hi : h)cout<<"hi\n"<<hi<<endl;
        // ShowTraj(path, h);
        // ;
        // next_tar.second = false;
        if(TrajOpt_.Optimize(path_pruned, h, p/*, min_t*/, startpva, endpva, next_tar, reach_out_t_ * 2, use_terminal_corridor_)){ // optimize the minimum time traj 
            // if(stat_) BM_.CS_.EndTimer(3);
            ShowTraj(path, h);
            double t_test = ros::WallTime::now().toSec();
            cts_.clear();
            cout<<"real_t0:"<<TrajOpt_.traj.getTotalDuration()<<endl;
            if(use_cover_trajectory_ && CoverTrajPlan(startpva, endpva, h, p, target_id, next_tar, reach_out_t_ * 2)){ // try to generate coverage se3 traj
                ROS_WARN("Cover traj success!");
            }
            else{
                ROS_WARN("Cover traj fail, use simple traj!");
            }
            // if(TrajOpt_.traj.getTotalDuration() < reach_out_t_ * 2){
            //     ROS_WARN("Time too shot!");
            //     return false;
            // }

            // for(auto &p : path){//debug
            //     if(!LRM_.IsFeasible(p)){
            //         ROS_ERROR("path dead!");
            //         ros::shutdown();
            //         return false;
            //     }
            // }
            // double yaw_end = ype;
            // if((traj_end - path.back()).norm() < 3.5){
            //     if((traj_end - path.back()).norm() > 0.1){
            //         yaw_end = atan2(gazept(1) - traj_end(1), gazept(0) - traj_end(0));
            //     }
            //     PlanYaw(yps, yds, ydds, yaw_end, yde, ydde, gazept, true);
            // }
            // else{
            //     yaw_end = atan2(gazept(1) - traj_end(1), gazept(0) - traj_end(0));
            //     PlanYaw(yps, yds, ydds, yaw_end, yde, ydde, gazept, false);
            // }            


            // Eigen::VectorXd durations = TrajOpt_.traj.getDurations();
            // double traj_tc = 0;
            // vector<double> Cts;
            // vector<vector<Eigen::Vector3d>> hullPts, covPts;

            // for(int i = 0, m = 0; i < durations.size(); i++){
            //     traj_tc += durations(i);
            //     if(i + 1 < durations.size()){
            //         Cts.emplace_back(traj_tc);
            //         hullPts.push_back({});
            //         covPts.push_back({});
            //     }
            // }
            // ShowTrajCover(Cts, /*trajCoverIdx,*/ hullPts, covPts);
            return true;
        }
        else{
            // cout<<"min_t:"<<min_t<<"d:"<<(ps - pe).norm()<<endl;
            ROS_ERROR("opt failed");
            return false;
        }
    }
    else{
        ROS_WARN("fail");
        return false;
    }
}

// bool Murder::TrajPlanB(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as,
//             const Eigen::Vector3d &pe, const Eigen::Vector3d &ve, const Eigen::Vector3d &ae, const double &yps, 
//             const double &yds, const double &ydds, const double &ype, const double &yde, const double &ydde, const Eigen::Vector3d &gazept){
//     vector<Eigen::Vector3d> path, path_pruned;
//     vector<Eigen::MatrixX4d> h;
//     vector<Eigen::Matrix3Xd> p;
//     if(LRM_.GetPath(ps, pe, path, false, local_max_search_iter_)){

//         if(LRM_.FindCorridors(path, h, p, path_pruned, traj_length_)){
//             Eigen::Matrix<double, 4, 3> startpva, endpva;
//             // double min_t = YawP_.GetMinT(yps, ype);
//             startpva.setZero();
//             endpva.setZero();
//             startpva.col(0).head(3) = ps;
//             startpva.col(1).head(3) = vs;
//             startpva.col(2).head(3) = as;
//             startpva(3, 0) = yps;
//             startpva(3, 1) = yds;
//             startpva(3, 2) = ydds;
//             endpva.col(0).head(3) = path_pruned.back();
//             endpva(3, 0) = ype;
//             pair<Eigen::Vector4d, bool> next_tar;
//             next_tar.second = false;
//             if(TrajOpt_.Optimize(path_pruned, h, p, /*min_t,*/ startpva, endpva, next_tar)){
//                 // Eigen::Vector3d traj_end = TrajOpt_.traj.getPos(TrajOpt_.traj.getTotalDuration());
//                 ShowTraj(path, h);
//                 // for(auto &p : path){//debug
//                 //     if(!LRM_.IsFeasible(p)){
//                 //         ROS_ERROR("path dead!");
//                 //         ros::shutdown();
//                 //         return false;
//                 //     }
//                 // }
//                 // double yaw_end = ype;
//                 // if((traj_end - path.back()).norm() < 3.5){
//                 //     if((traj_end - path.back()).norm() > 0.1){
//                 //         yaw_end = atan2(gazept(1) - traj_end(1), gazept(0) - traj_end(0));
//                 //     }
//                 //     PlanYaw(yps, yds, ydds, yaw_end, yde, ydde, gazept, true);
//                 // }
//                 // else{
//                 //     yaw_end = atan2(gazept(1) - traj_end(1), gazept(0) - traj_end(0));
//                 //     PlanYaw(yps, yds, ydds, yaw_end, yde, ydde, gazept, false);

//                 // }            
//                 return true;
//             }
//             else{
//                 // cout<<"min_t:"<<min_t<<"d:"<<(ps - pe).norm()<<endl;
//                 ROS_ERROR("opt failed");
//                 return false;
//             }
//         }
//         else{
//             ROS_WARN("fail");
//             return false;
//         }
//     }
//     else{
//         cout<<"r:"<<LRM_.IsFeasible(p_)<<endl;
//         cout<<"s:"<<LRM_.IsFeasible(ps)<<endl;
//         cout<<"e:"<<LRM_.IsFeasible(pe)<<endl;
//         cout<<p_.transpose()<<"  "<<ps.transpose()<<endl;
//         ROS_ERROR("no path");
//         ros::shutdown();
//         return false;
//     }
// }

// void Murder::PlanYaw(const double &yps, const double &yds, const double &ydds, const double &ype, 
//             const double &yde, const double &ydde, const Eigen::Vector3d &gazept, bool gaze){
//     Eigen::VectorXd T, yaw_l;
//     double total_t = TrajOpt_.traj.getTotalDuration();
//     YawP_.SampleT(total_t, T);
//     yaw_l.resize(T.size()+1);
//     yaw_l(0) = yps;
//     for(int i = 0; i+1 < T.size(); i++){
//         Eigen::Vector3d v = TrajOpt_.traj.getVel(T(i)).head(3);
//         Eigen::Vector3d p = TrajOpt_.traj.getPos(T(i)).head(3);
//         double yaw = atan2(v(1), v(0));

//         double yaw_gaze = atan2(gazept(1) - p(1), gazept(0) - p(0));

//         if(i == 0 && gaze && T.size() == 2){     //gaze at the second yaw, if only have 3 yaws
//             yaw_l(i+1) = YawP_.GetClosestYaw(T(0), yaw_l(0), yds, yaw_gaze);
//         }
//         else if(i == 0)                         //dont gaze
//             yaw_l(i+1) = YawP_.GetClosestYaw(T(0), yaw_l(0), yds, yaw);
//         else if(T.size() > 2 && i == T.size() - 1){ //gaze at the last second yaw, if have more than 3 yaws 
//             yaw_l(i+1) = YawP_.GetClosestYaw(T(0), yaw_l(i-1), 0, yaw_gaze);
//         }
//         else
//             yaw_l(i+1) = yaw;
//     }

//     yaw_l.tail(1)(0) = ype;
//     YawP_.Plan(yaw_l, T, yds, 0.0, yde, 0.0);
//     double p, v, a;
//     YawP_.GetCmd(T.sum(), p, v, a);
// }

void Murder::PublishTraj(bool recover){
    // swarm_exp_msgs::SwarmTraj traj;
    // if(recover){        //recover
    //     traj.state = 1;
    //     traj.recover_pt.x = recover_pose_.x();
    //     traj.recover_pt.y = recover_pose_.y();
    //     traj.recover_pt.z = recover_pose_.z();
    // }
    // else{               //normal traj
    //     traj.state = 2;
    //     traj.start_t = traj_start_t_;
    //     traj.coef_p.resize(TrajOpt_.traj.getPieceNum() * 6);
    //     traj.t_p.resize(TrajOpt_.traj.getPieceNum());
    //     traj.order_p = 5;
    //     for(int i = 0; i < TrajOpt_.traj.getPieceNum(); i++){
    //         auto &cur_p = TrajOpt_.traj[i];
    //         Eigen::MatrixXd cM;
    //         cM = cur_p.getCoeffMat();
    //         traj.t_p[i] = cur_p.getDuration();
    //         for(int j = 0; j < cM.cols(); j++){
    //             traj.coef_p[j + i * 6].x = cM(0, j);
    //             traj.coef_p[j + i * 6].y = cM(1, j);
    //             traj.coef_p[j + i * 6].z = cM(2, j);
    //         }
    //     }

    //     traj.order_yaw = 5;
    //     traj.t_yaw.resize(YawP_.T_.size());
    //     traj.coef_yaw.resize(YawP_.A_.size());
    //     for(int i = 0; i < YawP_.A_.size(); i++){
    //         traj.coef_yaw[i] = YawP_.A_[i];
    //     }
    //     for(int i = 0; i < YawP_.T_.size(); i++){
    //         traj.t_yaw[i] = YawP_.T_[i];
    //     }
    // }
    // traj_pub_.publish(traj);
    swarm_exp_msgs::SwarmTraj traj;
    if(recover){        //recover
        traj.state = 1;
        traj.recover_pt.x = recover_pose_.x();
        traj.recover_pt.y = recover_pose_.y();
        traj.recover_pt.z = recover_pose_.z();
    }
    else{               //normal traj
        traj.state = 2;
        traj.start_t = traj_start_t_;
        traj.coef_p.resize(TrajOpt_.traj.getPieceNum() * 6);
        traj.t_p.resize(TrajOpt_.traj.getPieceNum());
        traj.order_p = 5;
        
        traj.order_yaw = 5;
        traj.t_yaw.resize(TrajOpt_.traj.getPieceNum());
        traj.coef_yaw.resize(TrajOpt_.traj.getPieceNum() * 6);

        for(int i = 0; i < TrajOpt_.traj.getPieceNum(); i++){
            auto &cur_p = TrajOpt_.traj[i];
            Eigen::MatrixXd cM;
            cM = cur_p.getCoeffMat();
            traj.t_p[i] = cur_p.getDuration();
            traj.t_yaw[i] = cur_p.getDuration();
            for(int j = 0; j < cM.cols(); j++){
                traj.coef_p[j + i * 6].x = cM(0, j);
                traj.coef_p[j + i * 6].y = cM(1, j);
                traj.coef_p[j + i * 6].z = cM(2, j);
                traj.coef_yaw[(i+1) * 6 - j - 1] = cM(3, j);
                // cout<<"coef:"<<cM(3, j)<<endl;
            }
            // cout<<"t:"<<traj.t_yaw[i]<<endl;

        }
    }
    traj_pub_.publish(traj);
}

bool Murder::PlanTraj(Eigen::Vector3d &pos, double &yaw){
    double tc = ros::WallTime::now().toSec();
    list<Eigen::Vector3d> path;
    Eigen::Vector3d ps, vs, as, pe, ve, ae;
    double ys, yds, ydds, ye, yde, ydde;
    double hand_t = ros::WallTime::now().toSec() + reach_out_t_; 
    double cur_t = ros::WallTime::now().toSec();
    if(hand_t > traj_end_t_){
        if(cur_t - traj_end_t_ > 0.0){
            hand_t = ros::WallTime::now().toSec();
            ps = p_;
            vs = v_;
            as.setZero();
            ve.setZero();
            ae.setZero();
            ys = yaw_;
            yds = yaw_v_;
            ydds = 0;
            yde = 0; 
            ydde = 0;
        }
        else{
            Eigen::Vector4d p4s, v4s, a4s;
            hand_t = max(cur_t + 1e-3, 0.0);
            p4s = TrajOpt_.traj.getPos(cur_t - traj_start_t_ - 1e-3);
            v4s = TrajOpt_.traj.getVel(cur_t - traj_start_t_ - 1e-3);
            a4s = TrajOpt_.traj.getAcc(cur_t - traj_start_t_ - 1e-3);
            ps = p4s.head(3);
            vs = v4s.head(3);
            as = a4s.head(3);
            ys = p4s(3);
            yds = v4s(3);
            ydds = a4s(3);
            ve.setZero();
            ae.setZero();
            // YawP_.GetCmd(cur_t - traj_start_t_, ys, yds, ydds);
            yde = 0; 
            ydde = 0;
        }

        // hand_t = cur_t;
        // ps = p_;
        // vs = v_;
        // as.setZero();
        // ve.setZero();
        // ae.setZero();
        // ys = yaw_;
        // yds = yaw_v_;
        // ydds = 0;
        // yde = 0; 
        // ydde = 0;
    }
    else{
        Eigen::Vector4d p4s, v4s, a4s;
        p4s = TrajOpt_.traj.getPos(hand_t - traj_start_t_);
        ps = p4s.head(3);
        while(!LRM_.IsFeasible(ps) && hand_t > cur_t){
            hand_t -= reach_out_t_ / 10;
            p4s = TrajOpt_.traj.getPos(hand_t - traj_start_t_);
            ps = p4s.head(3);
        }
        if(!LRM_.IsFeasible(ps)){
            hand_t = cur_t;
            ps = p_;
        }
        v4s = TrajOpt_.traj.getVel(hand_t - traj_start_t_);
        a4s = TrajOpt_.traj.getAcc(hand_t - traj_start_t_);
        vs = v4s.head(3);
        as = a4s.head(3);
        ys = p4s(3);
        yds = v4s(3);
        ydds = a4s(3);
        ve.setZero();
        ae.setZero();
        // YawP_.GetCmd(hand_t - traj_start_t_, ys, yds, ydds);
        yde = 0; 
        ydde = 0;
    }

    if(!LRM_.GetPath(ps, pos, path, false, 5000)) return false;

    vector<Eigen::Vector3d> path_pruned;
    vector<Eigen::MatrixX4d> h;
    vector<Eigen::Matrix3Xd> p;
    vector<Eigen::Vector3d> path_vec;
    for(auto &pc : path) {
        // cout<<"pc:"<<pc.transpose()<<endl;
        path_vec.emplace_back(pc);
    }
    if(LRM_.FindCorridors(path_vec, h, p, path_pruned, traj_length_)){

        Eigen::Matrix<double, 4, 3> startpva, endpva;
        // double min_t = YawP_.GetMinT(yps, ype);
        startpva.setZero();
        endpva.setZero();
        startpva.col(0).head(3) = ps;
        startpva.col(1).head(3) = vs;
        startpva.col(2).head(3) = as;
        startpva(3, 0) = ys;
        startpva(3, 1) = yds;
        startpva(3, 2) = ydds;
        endpva.col(0).head(3) = path_pruned.back();
        double dyaw = FG_.YawDiff(yaw, ys);

        endpva(3, 0) = ys + dyaw;
        cout<<"endpva(3, 0):"<<endpva(3, 0)<<" yaw:"<<yaw<<endl;
        // endpva(3, 0) = yaw;
        cout<<"end p:"<<path_pruned.back().transpose()<<endl;
        // if((path_pruned.back() - path.back()).norm() < 0.3) {
        //     endpva.col(1) = ve;
        // }
        pair<Eigen::Vector4d, bool> next_tar;
        next_tar.second = false;
        if(TrajOpt_.Optimize(path_pruned, h, p/*, min_t*/, startpva, endpva, next_tar)){
            // Eigen::Vector3d traj_end = TrajOpt_.traj.getPos(TrajOpt_.traj.getTotalDuration());
            ShowTraj(path_vec, h);
            traj_start_t_ = hand_t;
            traj_end_t_ = TrajOpt_.traj.getTotalDuration() + traj_start_t_;
            replan_t_ = min(replan_duration_, TrajOpt_.traj.getTotalDuration()) + traj_start_t_;
            double t_test = ros::WallTime::now().toSec();
            TestFunc(startpva, endpva, h, p);
            cout<<"test_cost:"<<ros::WallTime::now().toSec() - t_test<<endl;

            PublishTraj(false);
            // for(auto &p : path){//debug
            //     if(!LRM_.IsFeasible(p)){
            //         ROS_ERROR("path dead!");
            //         ros::shutdown();
            //         return false;
            //     }
            // }
            // double yaw_end = ype;
            // if((traj_end - path.back()).norm() < 3.5){
            //     if((traj_end - path.back()).norm() > 0.1){
            //         yaw_end = atan2(gazept(1) - traj_end(1), gazept(0) - traj_end(0));
            //     }
            //     PlanYaw(yps, yds, ydds, yaw_end, yde, ydde, gazept, true);
            // }
            // else{
            //     yaw_end = atan2(gazept(1) - traj_end(1), gazept(0) - traj_end(0));
            //     PlanYaw(yps, yds, ydds, yaw_end, yde, ydde, gazept, false);
            // }            
            return true;
        }
        else{
            // cout<<"min_t:"<<min_t<<"d:"<<(ps - pe).norm()<<endl;
            ROS_ERROR("opt failed");
            return false;
        }
    }
    else{
        ROS_WARN("fail");
        return false;
    }
}

bool Murder::TestFunc(const Eigen::Matrix<double, 4, 3> &startpva, const Eigen::Matrix<double, 4, 3> &endpva, 
                            const vector<Eigen::MatrixX4d> &h, const vector<Eigen::Matrix3Xd> &p){
    double total_t = TrajOpt_.traj.getTotalDuration();
    vector<double> tl;
    EYP_.FovClearShow();
    Eigen::VectorXd ts = TrajOpt_.traj.getDurations();
    double tt = 0, tcu = 0;
    for(int i = 0; i < ts.size(); i++){
        if(i + 1 == ts.size()) break;
        double t = ts(i) / 2;
        if(t > 0.15 && tcu > 0.7) {
            tl.emplace_back(t + tt);
            tcu = t;
        }
        else{
            tcu += ts(i);
        }
        tt += ts(i);
    }
    cout<<"total_t:"<<total_t<<endl;
    if(tl.size() == 0) {
        ROS_WARN("too short!");
        return false;
    }
    else {
        vector<pair<Eigen::Vector4d, double>> t_p_l;
        t_p_l.resize(tl.size());
        Eigen::VectorXd midTs;
        midTs.resize(tl.size());
        for(int i = 0; i < tl.size(); i++) {
            midTs(i) = tl[i];
            t_p_l[i].first = TrajOpt_.traj.getPos(tl[i]);
            t_p_l[i].second = tl[i];
        }
        
        Eigen::Vector3d pe = endpva.col(0).head(3);
        int focus = FG_.GetClosestFid(pe);
        if(EYP_.YawPlan(t_p_l, total_t, startpva(3, 0), endpva(3, 0), focus)){
            ROS_WARN("yaw plan success!");
            vector<Eigen::Matrix3Xd> targets;
            vector<pair<Eigen::Vector4d, int>> midPts;
            vector<vector<Eigen::Vector3d>> hullPts, covPts;

            double tc = 0;
            for(int i = 0; i < ts.size(); i++){
                tc += ts(i);
                ts(i) = tc;
            }
            cout<<"ts:"<<ts.transpose()<<endl;
            int count = 0;
            for(auto &a : EYP_.ans_){
                cout<<"mid p:"<<a.pos_.transpose()<<endl;
                cout<<"mid t:"<<a.t_<<endl;
                midPts.push_back({a.pos_, 0});
                for(int i = 0; i < ts.size(); i++){
                    if(a.t_ < ts(i)){
                        midPts.back().second = i;
                        break;
                    }
                }
                cout<<"mid i:"<<midPts.back().second<<endl;
                Eigen::Matrix3Xd tars, tarVis;
                int c = 0;
                tars.resize(3, a.covered_targets_.size());

                Eigen::Vector3d p, acc;
                p = a.pos_.head(3);
                acc.setZero();
                GetHull(a.covered_targets_, p, acc, a.pos_(3), tars, tarVis);
                hullPts.push_back({});
                for(int i = 0; i < tars.cols(); i++) hullPts[count].emplace_back(tars.col(i));
                cout<<"tar:\n"<<tars.transpose()<<endl;
                cout<<"tarVis:\n"<<tarVis.transpose()<<endl;
                cout<<"hullPts[i].size():"<<hullPts[count].size()<<endl;
                covPts.emplace_back(a.covered_targets_);
                targets.emplace_back(tars);
                count++;
            }
            for(int i = 0; i < midPts.size(); i++){
                if(i == 0) midPts[i].first(3) = FG_.YawDiff(midPts[i].first(3), startpva(3, 0)) + startpva(3, 0);
                else midPts[i].first(3) = FG_.YawDiff(midPts[i].first(3), midPts[i - 1].first(3)) + midPts[i - 1].first(3);
            }

            vector<Eigen::Vector3d> debug_pts;
            pair<Eigen::Vector4d, bool> next_tar;
            next_tar.second = false;
            if(TrajOpt_.OptimizeCover(h, p, /*midPts, midTs,*/ targets, FOV_, startpva, endpva, next_tar, debug_pts)){
                ROS_WARN("cover traj success!");
                Eigen::VectorXd durations = TrajOpt_.traj.getDurations();
                vector<double> Cts;
                // vector<int> trajCoverIdx;
                double traj_tc = 0;
                for(int i = 0, m = 0; i < durations.size(); i++){
                    traj_tc += durations(i);
                    if(m < midPts.size() && i == midPts[m].second){
                        Cts.emplace_back(traj_tc);
                        // trajCoverIdx.emplace_back(i);
                        m++;
                    }
                }

                cout<<"debug_pts:"<<debug_pts.size()<<endl;
                Debug(debug_pts);
                cout<<"covPts:"<<covPts.size()<<endl;
                ShowTrajCover(Cts, /*trajCoverIdx,*/ hullPts, covPts);
            }
            else{
                ROS_WARN("cover traj fail!");
            }
        }
        else{
            ROS_WARN("skip yaw plan!");
        }
    }
    return true;
}

void Murder::GetExpTarget(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as, pair<int, int> &f_v_target, Eigen::Vector4d &target_vp,
    Eigen::Vector4d &sec_target, list<Eigen::Vector3d> &path, double &expect_t, double yaws, double yawds,
        double yawv, double yawa, double vel, double acc, int exclude_f, bool &ans1, bool &ans2){
    if(use_motion_){
        // if(stat_) BM_.CS_.StartTimer(2);
        Eigen::Vector4d tar_vp;
        int ans_tar = FG_.FindExpTargetM(ps, vs, as, f_v_target, tar_vp, path, expect_t, yaws, yawds, yawv * 0.4, yawa * 0.4,
                                            vel, acc, -1, 999999.0, reach_out_t_ * 0.8); // get the optimal target
        // if(stat_) BM_.CS_.EndTimer(2);
        target_ = tar_vp;

        if(ans_tar == 0){// target not found
            ans1 = false;
            ans2 = false;
            use_fg_vp_ = true;
            return;
        }
        else if(ans_tar == 1){ // find target
            ans1 = true;
            ans2 = false;
            use_fg_vp_ = true;
            // if(stat_) BM_.CS_.StartTimer(6);

            if(use_dir_corridor_ && FG_.FindSecondTarget(f_v_target.first, f_v_target.second, vel, yawv * 0.4, sec_target)){ // find the second target
                ROS_WARN("find second!!!!!");
                ans2 = true;
            }
            // if(stat_) BM_.CS_.EndTimer(6);
            return;
        }
        else{
            if(ans_tar == 3) use_fg_vp_ = false; // target is extra viewpoint
            else use_fg_vp_ = true; // target is on a motion primitive traj
            ans1 = true;
            ans2 = false;
            return;
        }
    }
    else{  // not used, for ablation
        if(FG_.FindExpTarget(ps, vs, f_v_target, path, yaws, yawds, yawv * 0.4, yawa * 0.4, vel, -1, 999999.0)){
            ans1 = true;
            ans2 = false;
            FG_.GetVp(f_v_target.first, f_v_target.second, target_);
            use_fg_vp_ = true;
            return;
        }
        else{
            use_fg_vp_ = true;
            ans1 = false;
            ans2 = false;
        }
    }
}

bool Murder::CoverTrajPlan(const Eigen::Matrix<double, 4, 3> &startpva, const Eigen::Matrix<double, 4, 3> &endpva, 
                            const vector<Eigen::MatrixX4d> &h, const vector<Eigen::Matrix3Xd> &p, const int &tar_id,
                            const pair<Eigen::Vector4d, bool> &next_tar, double min_t){
    double total_t = TrajOpt_.traj.getTotalDuration();
    vector<double> tl;
    EYP_.FovClearShow();
    Eigen::VectorXd ts = TrajOpt_.traj.getDurations();
    double tt = 0, tcu = 0;
    for(int i = 0; i + 1 < ts.size(); i++){
        tt += ts(i);
        tl.emplace_back(tt);
    }
    if(tl.size() == 0) { // traj duration too short
        ROS_WARN("too short!");
        return false;
    }
    else {
        vector<pair<Eigen::Vector4d, double>> t_p_l;
        t_p_l.resize(tl.size());
        Eigen::VectorXd midTs;
        midTs.resize(tl.size());
        for(int i = 0; i < tl.size(); i++) {
            midTs(i) = tl[i];
            t_p_l[i].first = TrajOpt_.traj.getPos(tl[i]);
            t_p_l[i].second = tl[i];
        }
        // if(stat_) BM_.CS_.StartTimer(4);
        if(EYP_.YawPlan(t_p_l, total_t, startpva(3, 0), endpva(3, 0), tar_id)){ // sample yaws
            // if(stat_) BM_.CS_.EndTimer(4);

            ROS_WARN("yaw plan success!");
            vector<Eigen::Matrix3Xd> targets;
            vector<pair<Eigen::Vector4d, int>> midPts;
            vector<vector<Eigen::Vector3d>> hullPts, covPts;

            double tc = 0;
            for(int i = 0; i < ts.size(); i++){
                tc += ts(i);
                ts(i) = tc;
            }
            for(auto &a : EYP_.ans_){

                Eigen::Matrix3Xd tars, tarVis;
                int c = 0;

                Eigen::Vector3d p, acc;
                p = a.pos_.head(3);
                acc.setZero();
                hullPts.push_back({});
                if(a.covered_targets_.size() > 1){
                    GetHull(a.covered_targets_, p, acc, a.pos_(3), tars, tarVis);
                    for(int i = 0; i < tarVis.cols(); i++) hullPts.back().emplace_back(tarVis.col(i));
                }
                else if(a.covered_targets_.size() == 1){
                    tars.resize(3, 1);
                    tars.col(0) = a.covered_targets_[0];
                }
                else{
                    tars.resize(3, a.covered_targets_.size());
                }
                covPts.emplace_back(a.covered_targets_);
                targets.emplace_back(tars);
            }

            vector<Eigen::Vector3d> debug_pts;
            // if(stat_) BM_.CS_.StartTimer(5);
            if(TrajOpt_.OptimizeCover(h, p, /*midPts, midTs,*/ targets, FOV_, startpva, endpva, next_tar, debug_pts, min_t, use_terminal_corridor_)){
                // if(stat_) BM_.CS_.EndTimer(5);
                ROS_WARN("cover traj success!");
                Eigen::VectorXd durations = TrajOpt_.traj.getDurations();
                double traj_tc = 0;
                vector<double> Cts;
                for(int i = 0, m = 0; i < durations.size(); i++){
                    traj_tc += durations(i);
                    if(i + 1 < durations.size()){
                        cts_.emplace_back(traj_tc);
                        Cts.emplace_back(traj_tc);
                    }
                }


                ShowTrajCover(Cts, /*trajCoverIdx,*/ hullPts, covPts);
            }
            else{
                ROS_WARN("cover traj fail!");
                return false;
            }
        }
        else{
            ROS_WARN("skip yaw plan!");
            return false;
        }
    }
    return true;
}

void Murder::ImgOdomCallback(const sensor_msgs::ImageConstPtr& img,
                            const nav_msgs::OdometryConstPtr& odom){
    double tc = ros::WallTime::now().toSec();
    if(cts_.size() > 0 && tc > cts_.front()){
        cts_.pop_front();
        sensor_flag_ = false;
    }

    if(replan_img_flag_ && tc > replan_t_ - update_interval_){
        sensor_flag_ = false;
        replan_img_flag_ = false;
    }

    if(sensor_flag_ && (tc - last_map_update_t_ < update_interval_ || !have_odom_) || volume_test_ && volume_t_ < tc) return;
    last_map_update_t_ = tc; 
    // ros::WallTime t0 = ros::WallTime::now();
    BM_.OdomCallback(odom);
    BM_.InsertImg(img);
    if(!volume_test_){
        FG_.UpdateFrontier(BM_.newly_register_idx_);
        LRM_.UpdateLocalBBX(robot_pose_, BM_.update_bbx_);
    }
    // MDTG_.Update(robot_pose_);
    sensor_flag_ = true;
    // FG_.sample_flag_ = false;

    Eigen::Vector3d c_v_p;
    c_v_p(0) = odom->pose.pose.position.x;
    c_v_p(1) = odom->pose.pose.position.y;
    c_v_p(2) = odom->pose.pose.position.z;
    if(first_odom_) {
        first_odom_ = false;
    }
    else if(stat_){
        // if((c_v_p - last_vi_pos_).norm() < 100000 && !isnan(abs(last_vi_pos_(0))) && !isnan(abs(last_vi_pos_(1))) && !isnan(abs(last_vi_pos_(2))))
        //     BM_.CS_.AddVolume((c_v_p - last_vi_pos_).norm(), 1);
        Eigen::Vector3d v(odom->twist.twist.linear.x, odom->twist.twist.linear.y,odom->twist.twist.linear.z);
        v_total_ += v.norm();
        v_num_++;
        // BM_.CS_.SetVolume(v.norm(), 2);
    }
    last_vi_pos_ = c_v_p;
}

void Murder::PclOdomCallback(const sensor_msgs::PointCloud2ConstPtr& pcl,
                            const nav_msgs::OdometryConstPtr& odom){
    double tc = ros::WallTime::now().toSec();
    BodyOdomCallback(odom);
    if(cts_.size() > 0 && tc > cts_.front()){
        cts_.pop_front();
        sensor_flag_ = false;
    }

    if(replan_img_flag_ && tc > replan_t_ - update_interval_){
        sensor_flag_ = false;
        replan_img_flag_ = false;
    }

    if((sensor_flag_ && (tc - last_map_update_t_ < update_interval_ || !have_odom_)) || (volume_test_ && volume_t_ < tc)) return;
    last_map_update_t_ = tc;
    BM_.OdomCallback(odom);
    BM_.InsertPcl(pcl);
    if(!volume_test_){
        FG_.UpdateFrontier(BM_.newly_register_idx_);
        LRM_.UpdateLocalBBX(robot_pose_, BM_.update_bbx_);
    }
    sensor_flag_ = true;

    Eigen::Vector3d c_v_p;
    c_v_p(0) = odom->pose.pose.position.x;
    c_v_p(1) = odom->pose.pose.position.y;
    c_v_p(2) = odom->pose.pose.position.z;
    if(first_odom_) {
        first_odom_ = false;
    }
    else if(stat_){
        Eigen::Vector3d v(odom->twist.twist.linear.x, odom->twist.twist.linear.y,odom->twist.twist.linear.z);
        v_total_ += v.norm();
        v_num_++;
    }
    last_vi_pos_ = c_v_p;
}

void Murder::BodyOdomCallback(const nav_msgs::OdometryConstPtr& odom){

    Quaterniond qua;
    have_odom_ = true;
    robot_pose_.setZero();
    qua.x() = odom->pose.pose.orientation.x;
    qua.y() = odom->pose.pose.orientation.y;
    qua.z() = odom->pose.pose.orientation.z;
    qua.w() = odom->pose.pose.orientation.w;

    p_(0) = odom->pose.pose.position.x;
    p_(1) = odom->pose.pose.position.y;
    p_(2) = odom->pose.pose.position.z;
    FG_.Robot_pos_ = p_;
    
    robot_pose_.block(0, 0, 3, 3) = qua.toRotationMatrix();
    robot_pose_.block(0, 3, 3, 1) = p_;

    v_(0) = odom->twist.twist.linear.x;
    v_(1) = odom->twist.twist.linear.y;
    v_(2) = odom->twist.twist.linear.z;
    if(v_.norm() > 8.0) ROS_ERROR("large v!!!!!!!!!");//debug
    v_ = qua.toRotationMatrix() * v_;
    yaw_ = atan2(qua.matrix()(1, 0), qua.matrix()(0, 0));
    yaw_v_ = odom->twist.twist.angular.z * robot_pose_(2, 2) + odom->twist.twist.angular.y * robot_pose_(2, 1)
                + odom->twist.twist.angular.x * robot_pose_(2, 0);
}


void Murder::ShowTraj(vector<Eigen::Vector3d> &path, vector<Eigen::MatrixX4d> &h){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(1 + h.size());
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = -1;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::LINE_STRIP;
    mka.markers[0].scale.x = 0.07;
    mka.markers[0].scale.y = 0.07;
    mka.markers[0].scale.z = 0.07;
    mka.markers[0].color.a = 1.0;
    mka.markers[0].color.r = 0.0;
    mka.markers[0].color.g = 0.9;
    mka.markers[0].color.b = 0.0;
    

    for(double delta = 0; delta < TrajOpt_.traj.getTotalDuration(); delta += 0.025){
        Eigen::Vector3d p;
        geometry_msgs::Point pt;
        p = TrajOpt_.traj.getPos(delta).head(3);
        pt.x = p(0);
        pt.y = p(1);
        pt.z = p(2);
        mka.markers[0].points.emplace_back(pt);
    }
    // for(auto &p : path){
    //     geometry_msgs::Point pt;
    //     pt.x = p(0);
    //     pt.y = p(1);
    //     pt.z = p(2);
    //     mka.markers[0].points.emplace_back(pt);
    // }
    for(int i = 0; i < h.size(); i++){
        mka.markers[i + 1].pose.position.x = (h[i](1, 3) - h[i](0, 3)) / 2;
        mka.markers[i + 1].pose.position.y = (h[i](3, 3) - h[i](2, 3)) / 2;
        mka.markers[i + 1].pose.position.z = (h[i](5, 3) - h[i](4, 3)) / 2;
        mka.markers[i + 1].pose.orientation.w = 1.0;

        mka.markers[i + 1].scale.x = (- h[i](1, 3) - h[i](0, 3));
        mka.markers[i + 1].scale.y = (- h[i](3, 3) - h[i](2, 3));
        mka.markers[i + 1].scale.z = (- h[i](5, 3) - h[i](4, 3));
        mka.markers[i + 1].type = visualization_msgs::Marker::CUBE;
        mka.markers[i+1].header.frame_id = "world";
        mka.markers[i+1].header.stamp = ros::Time::now();
        mka.markers[i+1].id = 1+i;
        mka.markers[i+1].action = visualization_msgs::Marker::ADD;
        mka.markers[i+1].lifetime = ros::Duration(1.0);
        mka.markers[i + 1].color.a = 0.2;
        mka.markers[i + 1].color.g = 1.0;
        mka.markers[i + 1].color.b = 0.5;
        mka.markers[i + 1].lifetime = ros::Duration(1.0);
    }
    show_pub_.publish(mka);
}

void Murder::ShowTrajCover(vector<double> &Cts, /*vector<int> &trajCoverIdx,*/ vector<vector<Eigen::Vector3d>> &hullPts, vector<vector<Eigen::Vector3d>> &coverPts){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(5); //traj, pts, fov, lines, hull
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = 100;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::LINE_STRIP;
    mka.markers[0].scale.x = 0.07;
    mka.markers[0].scale.y = 0.07;
    mka.markers[0].scale.z = 0.07;
    mka.markers[0].color.a = 0.25;
    mka.markers[0].color.r = 0.0;
    mka.markers[0].color.g = 0.0;
    mka.markers[0].color.b = 1.0;
    // mka.markers[0].lifetime = ros::Duration(1.0);

    mka.markers[1] = mka.markers[0];
    mka.markers[1].id = 101;
    mka.markers[1].type = visualization_msgs::Marker::SPHERE_LIST;
    mka.markers[1].scale.x = 0.2;
    mka.markers[1].scale.y = 0.2;
    mka.markers[1].scale.z = 0.2;
    mka.markers[1].color.a = 0.2;
    mka.markers[1].color.r = 0.0;
    mka.markers[1].color.g = 1.0;
    mka.markers[1].color.b = 0.0;

    mka.markers[2] = mka.markers[0];
    mka.markers[2].id = 102;
    mka.markers[2].type = visualization_msgs::Marker::LINE_LIST;
    mka.markers[2].scale.x = 0.1;
    mka.markers[2].scale.y = 0.1;
    mka.markers[2].scale.z = 0.1;
    mka.markers[2].color.a = 0.5;
    mka.markers[2].color.r = 1.0;
    mka.markers[2].color.g = 0.0;
    mka.markers[2].color.b = 0.0;

    mka.markers[3] = mka.markers[2];
    mka.markers[3].id = 103;
    mka.markers[3].scale.x = 0.03;
    mka.markers[3].scale.y = 0.03;
    mka.markers[3].scale.z = 0.03;
    mka.markers[3].color.a = 0.1;
    mka.markers[3].color.r = 0.0;
    mka.markers[3].color.g = 1.0;
    mka.markers[3].color.b = 0.0;

    mka.markers[4] = mka.markers[3];
    mka.markers[4].id = 104;
    mka.markers[4].color.a = 1.0;
    mka.markers[4].color.r = 0.0;
    mka.markers[4].color.g = 1.0;
    mka.markers[4].color.b = 1.0;

    double t_total = TrajOpt_.traj.getTotalDuration();
    Eigen::Vector4d pt, acc;
    Eigen::Quaterniond q;
    Eigen::Vector3d z, pt3, h;
    geometry_msgs::Point p, p1;
    for(double t = 0; t < t_total; t += 0.025){
        pt = TrajOpt_.traj.getPos(t);
        p.x = pt(0);
        p.y = pt(1);
        p.z = pt(2);
        mka.markers[0].points.emplace_back(p);
    }
    vector<Eigen::Vector3d> Fovps; 
    vector<Eigen::Quaterniond> FovRs;
    double yaw, yaw2, siny2, cosy2;
    for(int i = 0; i < coverPts.size(); i++){
        pt = TrajOpt_.traj.getPos(Cts[i]);
        acc = TrajOpt_.traj.getAcc(Cts[i]);
        p1.x = pt(0);
        p1.y = pt(1);
        p1.z = pt(2);
        for(auto &pi : coverPts[i]){
            p.x = pi(0);
            p.y = pi(1);
            p.z = pi(2);
            mka.markers[1].points.emplace_back(p);
            mka.markers[3].points.emplace_back(p);
            mka.markers[3].points.emplace_back(p1);
        }    

        yaw = pt(3);
        yaw2 = yaw / 2;
        siny2 = sin(yaw2);
        cosy2 = cos(yaw2);
        z = acc.head(3) + Eigen::Vector3d(0, 0, 9.8);
        z.normalize();
        q.x() = -z(1)*cosy2 + z(0)*siny2;
        q.y() = z(0)*cosy2 + z(1)*siny2;
        q.z() = (1 + z(2))*siny2;
        q.w() = (1 + z(2))*cosy2;
        q.coeffs() /= sqrt(2*(1 + z(2)));
        Fovps.emplace_back(pt.head(3));
        FovRs.emplace_back(q);

        z = q.toRotationMatrix().col(0);
        if(hullPts[i].size() >= 2){
            pt3 = (hullPts[i].front() - pt.head(3)) / max((hullPts[i].front() - pt.head(3)).dot(z), 0.1) * 2.0;
            p1.x = pt3(0) + pt(0);
            p1.y = pt3(1) + pt(1);
            p1.z = pt3(2) + pt(2);
            mka.markers[4].points.emplace_back(p1);
            // cout<<"pt3:"<<pt3.transpose()<<endl;
            for(int j = 1; j < hullPts[i].size(); j++){
                h = hullPts[i][j];
                // cout<<"h:"<<h.transpose()<<endl;
                pt3 = (h - pt.head(3)) / max((h - pt.head(3)).dot(z), 0.1) * 2.0;
                p.x = pt3(0) + pt(0);
                p.y = pt3(1) + pt(1);
                p.z = pt3(2) + pt(2);
                mka.markers[4].points.emplace_back(p);
                mka.markers[4].points.emplace_back(p);
            }
            mka.markers[4].points.emplace_back(p1);
        }
    }
    DrawFOVs(Fovps, FovRs, mka.markers[2]);
    show_pub_.publish(mka);
}
void Murder::PublishSecondFOV(const Eigen::Vector4d &vp, const bool &add){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(2);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = 99;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::LINE_STRIP;
    mka.markers[0].scale.x = 0.07;
    mka.markers[0].scale.y = 0.07;
    mka.markers[0].scale.z = 0.07;
    mka.markers[0].color.a = 0.5;
    mka.markers[0].color.r = 1.0;
    mka.markers[0].color.g = 1.0;
    mka.markers[0].color.b = 0.0;
    mka.markers[0].lifetime = ros::Duration(2.0);
    mka.markers[1] = mka.markers[0];
    mka.markers[1].type = visualization_msgs::Marker::ARROW;
    mka.markers[1].id = 98;
    mka.markers[1].scale.x = 0.2;
    mka.markers[1].scale.y = 0.4;
    mka.markers[1].scale.z = 0.00;

    if(!add) {
        mka.markers[0].action = visualization_msgs::Marker::DELETE;
        mka.markers[1].action = visualization_msgs::Marker::DELETE;
    }
    else{
        vector<Eigen::Vector3d> Fovps; 
        vector<Eigen::Quaterniond> FovRs;
        Eigen::Quaterniond q;
        Fovps.resize(1);
        FovRs.resize(1);
        Fovps[0] = vp.head(3);
        q.x() = 0.0;
        q.y() = 0.0;
        q.z() = sin(vp(3) * 0.5);
        q.w() = cos(vp(3) * 0.5);
        FovRs[0] = q;
        // q.coeffs() /= sqrt(2*(1 + z(2)));
        DrawFOVs(Fovps, FovRs, mka.markers[0], 1.0);
    }
    double te = TrajOpt_.traj.getTotalDuration() - 1e-4;
    Eigen::Vector4d pe, ve;
    Eigen::Vector3d v;
    pe = TrajOpt_.traj.getPos(te);
    ve = TrajOpt_.traj.getVel(te);
    v = ve.head(3);
    cout<<"endv:"<<v.norm()<<endl;
    v = v.norm() / TrajOpt_.upboundVec_[0] * 1.5 * v.normalized();
    mka.markers[1].points.resize(2);
    mka.markers[1].points[0].x = pe(0);
    mka.markers[1].points[0].y = pe(1);
    mka.markers[1].points[0].z = pe(2);
    mka.markers[1].points[1].x = pe(0) + v(0);
    mka.markers[1].points[1].y = pe(1) + v(1);
    mka.markers[1].points[1].z = pe(2) + v(2);
    show_pub_.publish(mka);
}

void Murder::Debug(const Eigen::Vector3d &pt1, const Eigen::Vector3d &pt2){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(1);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = 2;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::LINE_STRIP;
    mka.markers[0].scale.x = 0.05;
    mka.markers[0].scale.y = 0.05;
    mka.markers[0].scale.z = 0.05;
    mka.markers[0].color.a = 1.0;
    mka.markers[0].color.r = 0.9;
    mka.markers[0].color.g = 0.9;
    mka.markers[0].color.b = 0.0;
    
    // for(double delta = 0; delta < TrajOpt_.traj.getTotalDuration(); delta += 0.025){
    //     Eigen::Vector3d p;
    //     geometry_msgs::Point pt;
    //     p = TrajOpt_.traj.getPos(delta);
    //     pt.x = p(0);
    //     pt.y = p(1);
    //     pt.z = p(2);
    //     mka.markers[0].points.emplace_back(pt);
    // }
    mka.markers[0].points.resize(2);
    mka.markers[0].points[0].x = pt1.x();
    mka.markers[0].points[0].y = pt1.y();
    mka.markers[0].points[0].z = pt1.z();
    mka.markers[0].points[1].x = pt2.x()*0.3 + pt1.x()*0.7;
    mka.markers[0].points[1].y = pt2.y()*0.3 + pt1.y()*0.7;
    mka.markers[0].points[1].z = pt2.z()*0.3 + pt1.z()*0.7;
    show_pub_.publish(mka);
}

void Murder::Debug(list<Eigen::Vector3d> &pts){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(1);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = -2;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::SPHERE_LIST;
    mka.markers[0].scale.x = 0.1;
    mka.markers[0].scale.y = 0.1;
    mka.markers[0].scale.z = 0.1;
    mka.markers[0].color.a = 1.0;
    mka.markers[0].color.r = 0.9;
    mka.markers[0].color.g = 0.0;
    mka.markers[0].color.b = 0.5;
    for(auto &pt : pts){
        geometry_msgs::Point p;
        p.x = pt(0);
        p.y = pt(1);
        p.z = pt(2);
        mka.markers[0].points.emplace_back(p);
    }
    show_pub_.publish(mka);
}

void Murder::Debug(vector<Eigen::Vector3d> &pts){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(1);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = -2;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::SPHERE_LIST;
    mka.markers[0].scale.x = 0.15;
    mka.markers[0].scale.y = 0.15;
    mka.markers[0].scale.z = 0.15;
    mka.markers[0].color.a = 1.0;
    mka.markers[0].color.r = 0.9;
    mka.markers[0].color.g = 0.0;
    mka.markers[0].color.b = 0.5;
    for(auto &pt : pts){
        geometry_msgs::Point p;
        p.x = pt(0);
        p.y = pt(1);
        p.z = pt(2);
        mka.markers[0].points.emplace_back(p);
    }
    show_pub_.publish(mka);
}

void Murder::ShowPath(list<Eigen::Vector3d> &path, int id){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(1);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = id;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::LINE_STRIP;
    mka.markers[0].scale.x = 0.1;
    mka.markers[0].scale.y = 0.1;
    mka.markers[0].scale.z = 0.1;
    mka.markers[0].color.a = 0.8;
    mka.markers[0].color.b = 0.8;
    if(id == -4){
        mka.markers[0].pose.position.x = 0.1;
        mka.markers[0].pose.position.y = 0.1;
        mka.markers[0].color.r = 0.9;
        mka.markers[0].color.g = 0.0;
        mka.markers[0].color.b = 0.0;
    }
    if(id == -3){
        mka.markers[0].scale.x = 0.05;
        mka.markers[0].scale.y = 0.05;
        mka.markers[0].scale.z = 0.05;
        mka.markers[0].color.r = 0.2;
        mka.markers[0].color.g = 0.4;
        mka.markers[0].color.b = 0.9;
    }
    for(auto &pt : path){
        geometry_msgs::Point p;
        p.x = pt(0);
        p.y = pt(1);
        p.z = pt(2);
        mka.markers[0].points.emplace_back(p);
    }
    show_pub_.publish(mka);
}

void Murder::Test(){
    FG_.MotionInitDijkstraDebug(p_);
}
