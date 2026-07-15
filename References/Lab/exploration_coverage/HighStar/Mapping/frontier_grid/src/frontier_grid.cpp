#include <frontier_grid/frontier_grid.h>
void FrontierGrid::init(ros::NodeHandle &nh, ros::NodeHandle &nh_private){
    nh_ = nh;
    nh_private_ = nh_private;
    std::string ns = ros::this_node::getName();
    string sensor;
    bool show_frontier;
    nh_private_.param(ns + "/Exp/minX", 
        origin_.x(), -10.0);
    nh_private_.param(ns + "/Exp/minY", 
        origin_.y(), -10.0);
    nh_private_.param(ns + "/Exp/minZ", 
        origin_.z(), 0.0);
    nh_private_.param(ns + "/Exp/maxX", 
        up_bd_.x(), 10.0);
    nh_private_.param(ns + "/Exp/maxY", 
        up_bd_.y(), 10.0);
    nh_private_.param(ns + "/Exp/maxZ", 
        up_bd_.z(), 5.0);
    nh_private_.param(ns + "/block_map/resolution", 
        resolution_, 0.1);
    nh_private_.param(ns + "/block_map/sensor_max_range", 
        sensor_range_, 5.0);
    nh_private_.param(ns + "/Frontier/sample_max_range", 
        sample_max_range_, 4.5);
    nh_private_.param(ns + "/Frontier/grid_scale", 
        node_scale_, 5.0);
    nh_private_.param(ns + "/Frontier/viewpoint_thresh", 
        vp_thresh_, 2.0);
    nh_private_.param(ns + "/Frontier/viewpoint_z_gate_enable",
        viewpoint_z_gate_enable_, false);
    nh_private_.param(ns + "/Frontier/viewpoint_min_z",
        viewpoint_min_z_, origin_.z());
    nh_private_.param(ns + "/Frontier/viewpoint_max_z",
        viewpoint_max_z_, up_bd_.z());
    nh_private_.param(ns + "/Frontier/observe_thresh", 
        obs_thresh_, 0.85);
    nh_private_.param(ns + "/Frontier/resample_duration", 
        resample_duration_, 1.0);
    nh_private_.param(ns + "/Frontier/eval_duration", 
        eval_duration_, 1.0);
    nh_private_.param(ns + "/Frontier/sample_hor_dir_num", 
        samp_h_dir_num_, 10);
    nh_private_.param(ns + "/Frontier/sample_ver_dir_num", 
        samp_v_dir_num_, 3);
    nh_private_.param(ns + "/Frontier/sample_dist_num", 
        samp_dist_num_, 3);
    nh_private_.param(ns + "/Frontier/sensor_type", 
        sensor, string("Depth_Camera"));
    nh_private_.param(ns + "/Frontier/FOV_hor_num", 
        FOV_h_num_, 15);
    nh_private_.param(ns + "/Frontier/FOV_ver_num", 
        FOV_v_num_, 10); 
    nh_private_.param(ns + "/Frontier/cam_hor", 
        cam_hor_, 0.5 * M_PI);
    nh_private_.param(ns + "/Frontier/cam_ver", 
        cam_ver_, 0.5 * M_PI);    
    nh_private_.param(ns + "/Frontier/livox_ver_low", 
        livox_ver_low_, -10/180 * M_PI);
    nh_private_.param(ns + "/Frontier/livox_ver_up", 
        livox_ver_up_, 75/180 * M_PI);    
    nh_private_.param(ns + "/Frontier/ray_samp_dist1", 
        ray_samp_dist1_, 0.2);
    // nh_private_.param(ns + "/Frontier/samp_free_thresh", 
    //     samp_free_thresh_, 25);
    nh_private_.param(ns + "/Frontier/ray_samp_dist2", 
        ray_samp_dist2_, 0.1);    
    nh_private_.param(ns + "/Frontier/show_frontier", 
        show_frontier, true);
    nh_private_.param(ns + "/Exp/robot_sizeX", 
        Robot_size_(0), 0.5);    
    nh_private_.param(ns + "/Exp/robot_sizeY", 
        Robot_size_(1), 0.5);    
    nh_private_.param(ns + "/Exp/robot_sizeZ", 
        Robot_size_(2), 0.4);    
    nh_private_.param(ns + "/Exp/lambda", 
        lambda_, 0.4);    
    nh_private_.param(ns + "/Exp/GainFactor", 
        g_factor_, 0.3);    
    nh_private_.param(ns + "/Exp/WeightDir", 
        w_dir_, 0.0);    

    nh_private_.param(ns + "/Exp/UseNearGain", 
        use_near_gain_, true);    
    nh_private_.param(ns + "/Exp/SecondGainThresh", 
        second_gain_thresh_, 5.0);    
    nh_private_.param(ns + "/Exp/SecondDistThresh", 
        second_dist_thresh_, 2.5);    
    nh_private_.param(ns + "/Exp/SecondDistMinThresh", 
        second_distmin_thresh_, 0.3);    
    nh_private_.param(ns + "/Exp/SecondYawThresh", 
        second_yaw_thresh_, 0.75);    
    nh_private_.param(ns + "/Exp/GainMin", 
        gain_min_, 0.0);    
    nh_private_.param(ns + "/Frontier/vgain_thresh", 
        v_gain_thresh_, 0.5);    
    node_scale_ = ceil(node_scale_ / resolution_) * resolution_;
    for(int dim = 0; dim < 3; dim++){
        node_num_(dim) = ceil((up_bd_(dim) - origin_(dim)) / node_scale_);
    }
    scan_count_ = 0;
    cout<<"node_scale_:"<<node_scale_<<endl;
    cout<<"up_bd_:"<<up_bd_.transpose()<<endl;
    cout<<"origin_:"<<origin_.transpose()<<endl;
    cout<<"node_num_:"<<node_num_.transpose()<<endl;

    sample_flag_ = false;

    Eigen::Vector3i v_it;
    samp_dir_num_ = samp_v_dir_num_ * samp_dist_num_;
    samp_num_ = samp_h_dir_num_ * samp_v_dir_num_ * samp_dist_num_;
    samp_h_dir_ = M_PI * 2 / samp_h_dir_num_;
    for(v_it(2) = 0; v_it(2) < node_num_(2); v_it(2)++){
        for(v_it(1) = 0; v_it(1) < node_num_(1); v_it(1)++){
            for(v_it(0) = 0; v_it(0) < node_num_(0); v_it(0)++){
                CoarseFrontier CF;
                Eigen::Vector3i vox_num;
                for(int dim = 0; dim < 3; dim++){
                    vox_num(dim) = floor(node_scale_ / resolution_);
                    double remain_d = up_bd_(dim) - origin_(dim) - v_it(dim) * node_scale_;
                    CF.down_(dim) = v_it(dim) * node_scale_ + origin_(dim);
                    CF.up_(dim) = v_it(dim) * node_scale_ + node_scale_ + origin_(dim);
                    CF.center_(dim) = CF.down_(dim) / 2 + CF.up_(dim) / 2;
                    if(remain_d < node_scale_){
                        CF.center_(dim) = remain_d * 0.5 + v_it(dim) * node_scale_ + origin_(dim);
                        CF.up_(dim) = remain_d + v_it(dim) * node_scale_ + origin_(dim);
                        vox_num(dim) = floor((CF.up_(dim) - CF.down_(dim)) / resolution_);
                    }
                    CF.last_sample_ = ros::WallTime::now().toSec();
                    CF.last_strong_check_ = ros::WallTime::now().toSec();
                    CF.last_vgain_eval_ = ros::WallTime::now().toSec();
                }
                CF.unknown_num_ = vox_num(0) * vox_num(1) * vox_num(2);
                CF.thresh_num_ = floor((1.0 - obs_thresh_) * CF.unknown_num_);
                CF.f_state_ = 0;
                
                // CF.dirs_state_.resize(samp_h_dir_num_, 0);
                // CF.dirs_free_num_.resize(samp_h_dir_num_, 0);
                CF.local_vps_.resize(samp_num_, 0);
                CF.gains_.resize(samp_num_, 0);
                CF.gain_dir_ranges_.resize(samp_num_);
                // CF.public_vps_.resize(samp_num_, 0);
                CF.flags_.reset();
                f_grid_.emplace_back(CF);                
            }
        }
    }
    sample_timer_ = nh.createTimer(ros::Duration(0.1), &FrontierGrid::SampleVpsCallback, this);
    lazy_samp_timer_ = nh.createTimer(ros::Duration(0.2), &FrontierGrid::LazySampleCallback, this);
    lazy_eva_timer_ = nh.createTimer(ros::Duration(0.1), &FrontierGrid::LazyVgainEvaluate, this);

    if(show_frontier)
        show_timer_ = nh.createTimer(ros::Duration(0.5), &FrontierGrid::ShowVpsCallback, this);
    show_pub_ = nh.advertise<visualization_msgs::MarkerArray>("/Frontier/grid", 1);
    debug_pub_ = nh.advertise<visualization_msgs::Marker>("/Frontier/debug", 10);
    // //FOV down sample
    if(sensor == "Depth_Camera"){
        sensor_type_ = CAMERA;
    }
    else if(sensor == "Livox"){
        sensor_type_ = LIVOX;
    }
    else{
        ROS_ERROR("error sensor type!");
        ros::shutdown();
        return;
    }

    for(int i = 0; i < samp_dist_num_; i++){
        // sample_dists_.push_back((sample_max_range_ - sqrt(3) * node_scale_) / max(1, samp_dist_num_) * i + sqrt(3)/2 * node_scale_ - 1e-3);
        // sample_dists_.push_back((sample_max_range_ - node_scale_) / max(1, samp_dist_num_-1) * i + node_scale_ - 1e-3);
        sample_dists_.push_back(sample_max_range_ + (node_scale_ - sample_max_range_) / max(1, samp_dist_num_-1) * i);
        cout<<i<<"samp d:"<<sample_dists_.back()<<endl;
    }
    for(int i = 0; i < samp_v_dir_num_; i++){
        if(sensor_type_ == CAMERA){
            sample_vdir_sins_.push_back(sin(M_PI * 0.25 / max(samp_v_dir_num_ - 1, 1) * i - M_PI * 0.25 / 2));
            sample_vdir_coses_.push_back(cos(M_PI * 0.25 / max(samp_v_dir_num_ - 1, 1) * i - M_PI * 0.25 / 2));
            sample_v_dirs_.push_back(M_PI * 0.25 / max(samp_v_dir_num_ - 1, 1) * i - M_PI * 0.25 / 2);
        }
        else if(sensor_type_ == LIVOX){
            sample_vdir_sins_.push_back(sin(M_PI * 0.2 / max(samp_v_dir_num_ - 1, 1) * i - M_PI * 0.3 / 2));
            sample_vdir_coses_.push_back(cos(M_PI * 0.2 / max(samp_v_dir_num_ - 1, 1) * i - M_PI * 0.3 / 2));
            sample_v_dirs_.push_back(M_PI * 0.2 / max(samp_v_dir_num_ - 1, 1) * i - M_PI * 0.3 / 2);
        }
    }
    for(int i = 0; i < samp_h_dir_num_; i++){
        sample_hdir_sins_.push_back(sin(M_PI * 2.0 / max(samp_h_dir_num_, 1) * i - M_PI));
        sample_hdir_coses_.push_back(cos(M_PI * 2.0 / max(samp_h_dir_num_, 1) * i - M_PI));
        sample_h_dirs_.push_back(M_PI * 2.0 / max(samp_h_dir_num_, 1) * i - M_PI);
    }
    gain_rays_.resize(samp_num_);
    gain_dirs_.resize(samp_num_);
    Robot_pos_.setZero();
    InitGainRays();
    if(use_near_gain_){
        InitGmaxNear();
    }
    else InitGmax();
    InitialVpDict();
    cout<<"samp_h_dir_num_:"<<samp_h_dir_num_<<endl;
    cout<<"samp_v_dir_num_:"<<samp_v_dir_num_<<endl;
    cout<<"samp_dist_num_:"<<samp_dist_num_<<endl;
    cout<<"samp_num_:"<<samp_num_<<endl;
    // g_hor_num_ = 
}

void FrontierGrid::InitialVpDict(){
    Eigen::Vector4d vp_pose;
    Eigen::Vector3d vp_pos;
    int p_id;
    for(int f = 0; f < f_grid_.size(); f++){
        for(int v = 0; v < f_grid_[f].local_vps_.size(); v++){
            if(!GetVp(f, v, vp_pose, false)) continue;
            vp_pos = vp_pose.head(3);
            if(!LRM_->InsideMap(vp_pos) || LRM_->StrangePoint(vp_pos)) continue;
            p_id = LRM_->PostoId(vp_pos);
            auto vp_it = vp_dict_.find(p_id);
            if(vp_it == vp_dict_.end()){
                pair<int, list<pair<int, int>>> i;
                i.first = p_id;
                i.second.push_back({f, v});
                vp_dict_.insert(i);
            }
            else{
                vp_it->second.push_back({f, v});
            }
        }
    }
}

bool FrontierGrid::SampleVps(list<Eigen::Vector3i> &posis){
    list<int> idxs;
    for(auto &p : posis){
        int idx = Posi2Idx(p);
        if(idx != -1) idxs.push_back(idx);
    }
    return SampleVps(idxs);
}

bool FrontierGrid::SampleVps(list<Eigen::Vector3d> &poses){
    list<int> idxs;
    for(auto &p : poses){
        int idx = Pos2Idx(p);
        if(idx != -1) idxs.push_back(idx);
    }
    return SampleVps(idxs);
}

bool FrontierGrid::SampleVps(list<int> &idxs, const double &tm){
    double gain;
    Eigen::Vector4d vp_pose;
    Eigen::Vector3d vp_pos;
    list<Eigen::Vector3d> debug_pts;
    int vp_id;
    bool flag = false;
    int visited_frontiers = 0;
    int skipped_stale = 0;
    int skipped_invalid_idx = 0;
    int sampled_vps = 0;
    int rejected_infeasible = 0;
    int rejected_strange = 0;
    int rejected_lowres = 0;
    int rejected_lowres_outside = 0;
    int rejected_lowres_block_null = 0;
    int rejected_lowres_node_null = 0;
    int rejected_lowres_outnode = 0;
    int rejected_lowres_obstacle = 0;
    int rejected_lowres_unknown_reason = 0;
    int lowres_stats_nodes = 0;
    int lowres_stats_total_voxels = 0;
    int lowres_stats_free_voxels = 0;
    int lowres_stats_unknown_voxels = 0;
    int lowres_stats_occupied_voxels = 0;
    int lowres_stats_out_voxels = 0;
    double lowres_stats_occupied_ratio_sum = 0.0;
    double lowres_stats_occupied_ratio_max = 0.0;
    double lowres_stats_out_ratio_sum = 0.0;
    double lowres_stats_out_ratio_max = 0.0;
    int rejected_occupied = 0;
    int rejected_z = 0;
    int rejected_gain = 0;
    int rejected_vgain = 0;
    int alive_vps = 0;
    double cur_t = ros::WallTime::now().toSec();
    Eigen::Vector3d r_size;
    r_size = LRM_->GetRobotSize();
    int idx;
    while(!idxs.empty() && ros::WallTime::now().toSec() - cur_t < tm){
        idx = idxs.front();
        idxs.pop_front();
        if(idx < 0 || idx  >= f_grid_.size()){
            skipped_invalid_idx++;
            continue;
        }
        visited_frontiers++;
        f_grid_[idx].flags_.reset(1);
        if(cur_t - f_grid_[idx].last_sample_ < resample_duration_){
            skipped_stale++;
            continue;
        }
        f_grid_[idx].last_sample_ = cur_t;
        for(int h_id = 0; h_id < samp_h_dir_num_; h_id++){
            for(int dir_id = 0; dir_id < samp_dir_num_; dir_id++){
                vp_id = h_id * samp_dir_num_ + dir_id;
                if(!GetVp(idx, vp_id, vp_pose)){
                    Eigen::Vector3d vp_pos_probe;
                    if(GetVpPos(idx, vp_id, vp_pos_probe, false, false) && !ViewpointZAllowed(vp_pos_probe)){
                        f_grid_[idx].local_vps_[vp_id] = 2;
                        rejected_z++;
                    }
                    continue;
                }
                if(f_grid_[idx].local_vps_[vp_id] == 2) continue;
                sampled_vps++;
                vp_pos = vp_pose.block(0,0,3,1);

                bool strange = LRM_->StrangePoint(vp_pos);
                bool lowres_infeasible = !strange && !LRM_->IsFeasible(vp_pos);
                bool occupied = false;
                if(strange || lowres_infeasible){
                    occupied = BM_->PosBBXOccupied(vp_pos, Robot_size_ * 2);
                    if(occupied) f_grid_[idx].local_vps_[vp_id] = 2;
                    if(strange) rejected_strange++;
                    if(lowres_infeasible) {
                        rejected_lowres++;
                        int reason = LRM_->DebugFeasibilityReason(vp_pos);
                        if(reason == 1) rejected_lowres_outside++;
                        else if(reason == 2) rejected_lowres_block_null++;
                        else if(reason == 3) rejected_lowres_node_null++;
                        else if(reason == 4) rejected_lowres_outnode++;
                        else if(reason == 5) {
                            rejected_lowres_obstacle++;
                            lowres::NodeVoxelStats stats = LRM_->DebugNodeVoxelStats(vp_pos);
                            if(stats.total > 0){
                                double occ_ratio = double(stats.occupied) / double(stats.total);
                                double out_ratio = double(stats.out) / double(stats.total);
                                lowres_stats_nodes++;
                                lowres_stats_total_voxels += stats.total;
                                lowres_stats_free_voxels += stats.free;
                                lowres_stats_unknown_voxels += stats.unknown;
                                lowres_stats_occupied_voxels += stats.occupied;
                                lowres_stats_out_voxels += stats.out;
                                lowres_stats_occupied_ratio_sum += occ_ratio;
                                lowres_stats_occupied_ratio_max = max(lowres_stats_occupied_ratio_max, occ_ratio);
                                lowres_stats_out_ratio_sum += out_ratio;
                                lowres_stats_out_ratio_max = max(lowres_stats_out_ratio_max, out_ratio);
                            }
                        }
                        else rejected_lowres_unknown_reason++;
                    }
                    if(occupied) rejected_occupied++;
                    rejected_infeasible++;
                    continue;
                }
                if(GetGain(idx, vp_id, f_grid_[idx].gain_dir_ranges_[vp_id]) < vp_thresh_) {
                    f_grid_[idx].local_vps_[vp_id] = 2;
                    rejected_gain++;
                }
                else{
                    if(LRM_->IsLocalFeasible(vp_pos)) flag = true;
                    f_grid_[idx].local_vps_[vp_id] = 1;
                    alive_vps++;
                    // if(cur_t - f_grid_[idx].last_vgain_eval_ > eval_duration_) {
                    //     f_grid_[idx].last_vgain_eval_ = cur_t;
                    double v_gain = max(gain_min_, GetVGain(idx, vp_id));
                    // debug_pts.emplace_back(vp_pos);
                    // if(v_gain < 1e-4) {
                    //     ROS_ERROR("error gain!");
                    //     getchar();
                    // }
                    // if(v_gain < 1e-3){
                    //     // GetVGain(idx, vp_id, true);
                    //     cout<<"fg:"<<GetGain(idx, vp_id)<<endl;
                    //     cout<<"vg:"<<v_gain<<endl;
                    //     // ros::shutdown();
                    //     // return false;
                    // }
                    // cout<<"v_gain:"<<v_gain<<endl;
                    f_grid_[idx].gains_[vp_id] = v_gain;
                    if(v_gain < v_gain_thresh_){
                        f_grid_[idx].local_vps_[vp_id] = 2;
                        alive_vps--;
                        rejected_vgain++;
                    }
                    // }
                }
            }
        }
        bool vp_explored = true;
        for(int h_id = 0; h_id < samp_num_; h_id++){
            if(f_grid_[idx].local_vps_[h_id] != 2){
                vp_explored = false;
                break;
            }
        }
        if(vp_explored){
            f_grid_[idx].f_state_ = 2;
            if(!f_grid_[idx].flags_[2]){
                explored_frontiers_show_.push_back(idx);
                f_grid_[idx].flags_.set(2);
            }
        }
    }
    ROS_WARN_THROTTLE(
        1.0,
        "HighStar SampleVps diag: visited_frontiers=%d skipped_invalid=%d skipped_stale=%d sampled_vps=%d alive=%d rejected[infeasible=%d strange=%d lowres=%d occupied=%d z=%d gain=%d vgain=%d] lowres_reason[outside=%d block_null=%d node_null=%d outnode=%d obstacle=%d other=%d] lowres_obstacle_stats[nodes=%d avg_occ_ratio=%.4f max_occ_ratio=%.4f avg_out_ratio=%.4f max_out_ratio=%.4f vox_total=%d free=%d unknown=%d occupied=%d out=%d] flag=%d",
        visited_frontiers,
        skipped_invalid_idx,
        skipped_stale,
        sampled_vps,
        alive_vps,
        rejected_infeasible,
        rejected_strange,
        rejected_lowres,
        rejected_occupied,
        rejected_z,
        rejected_gain,
        rejected_vgain,
        rejected_lowres_outside,
        rejected_lowres_block_null,
        rejected_lowres_node_null,
        rejected_lowres_outnode,
        rejected_lowres_obstacle,
        rejected_lowres_unknown_reason,
        lowres_stats_nodes,
        lowres_stats_nodes > 0 ? lowres_stats_occupied_ratio_sum / double(lowres_stats_nodes) : 0.0,
        lowres_stats_occupied_ratio_max,
        lowres_stats_nodes > 0 ? lowres_stats_out_ratio_sum / double(lowres_stats_nodes) : 0.0,
        lowres_stats_out_ratio_max,
        lowres_stats_total_voxels,
        lowres_stats_free_voxels,
        lowres_stats_unknown_voxels,
        lowres_stats_occupied_voxels,
        lowres_stats_out_voxels,
        flag ? 1 : 0);
    // Debug(debug_pts, 0);
    return flag;
}

void FrontierGrid::UpdateFrontier(const vector<Eigen::Vector3d> &pts){
    int idx;
    list<int> idx_list;

    for(auto &p : pts){
        idx = Pos2Idx(p);
        if(idx == -1) continue;
        f_grid_[idx].unknown_num_--;

        
        if(!f_grid_[idx].flags_[0]){
            f_grid_[idx].flags_.set(0);
            idx_list.push_back(idx);
        }
    }

    for(auto &it_idx : idx_list){
        f_grid_[it_idx].flags_.reset(0);
        if(f_grid_[it_idx].f_state_ == 0) f_grid_[it_idx].f_state_ = 1;

        if(f_grid_[it_idx].f_state_ == 1){
            if(f_grid_[it_idx].unknown_num_ < f_grid_[it_idx].thresh_num_){
                ExpandFrontier(it_idx);
                f_grid_[it_idx].f_state_ = 2;
            }

            //show
            if(!f_grid_[it_idx].flags_[2] && f_grid_[it_idx].f_state_ == 1){
                exploring_frontiers_show_.push_back(it_idx);
                f_grid_[it_idx].flags_.set(2);
            }
            else if(!f_grid_[it_idx].flags_[2] && f_grid_[it_idx].f_state_ == 2){
                explored_frontiers_show_.push_back(it_idx);
                f_grid_[it_idx].flags_.set(2);
            }

            if(!f_grid_[it_idx].flags_[1] && f_grid_[it_idx].f_state_ == 1){
                f_grid_[it_idx].flags_.set(1);
                exploring_frontiers_.push_back(it_idx);
            }
        }
    }


}

double FrontierGrid::GetGain(const int &f_id, const int &vp_id, pair<double, double> &dg_u_d){
    bool vis_free;
    double gain = 0;
    auto &rays = gain_rays_[vp_id];
    double yaw, dyaw;
    VoxelState state;
    Eigen::Vector3d chk_pt;
    Eigen::Vector4d v_pose;
    // cout<<"gain vp id:"<<vp_id<<endl;
    dg_u_d.first = -cam_hor_ * 0.5;
    dg_u_d.second = cam_hor_ * 0.5;
    if(!GetVp(f_id, vp_id, v_pose)){
        ROS_ERROR("GetGain: error vp id%d", int(vp_id));
        ros::shutdown();
        return -1;
    }
    for(auto &ray : rays){
        vis_free = true;
        for(auto &vox : ray.first){
            chk_pt = vox + f_grid_[f_id].center_;
            state = BM_->GetVoxState(chk_pt);
            if(state == VoxelState::occupied || state == VoxelState::out){
                vis_free = false;
                break;
            }
        }
        if(!vis_free) continue;

        for(auto &v_g : ray.second){
            chk_pt = v_g.first + f_grid_[f_id].center_;
            state = BM_->GetVoxState(chk_pt);
            if(state == VoxelState::free){
                continue;
            }
            else if(state == VoxelState::occupied || state == VoxelState::out){
                break;
            }
            else{
                gain += v_g.second;
                yaw = atan2(chk_pt(1) - v_pose(1), chk_pt(0) - v_pose(0));
                dyaw = YawDiff(yaw, v_pose(3));
                dg_u_d.first = max(dyaw, dg_u_d.first);
                dg_u_d.second = min(dyaw, dg_u_d.second);
                if(gain > vp_thresh_) return gain;
                break;
            }
        }
    }
    // cout<<"gain:"<<gain<<endl;
    return gain;
}

double FrontierGrid::GetGainRange(const int &f_id, const Eigen::Vector3d &tar_vp){
    double cur_t = ros::WallTime::now().toSec();
    if(f_id >= f_grid_.size() || f_id < 0 ) return -1.0;
    int it;
    Eigen::Vector3i n(1, node_num_(0), node_num_(0) * node_num_(1));
    Eigen::Vector3d vp;
    double v = pow(BM_->resolution_, 3);
    double gain = f_grid_[f_id].unknown_num_ * v;
    for(int dim = 0; dim < 3; dim++){
        for(int dir = -1; dir < 3; dir +=2){
            int it = f_id + dir*n(dim);
            if(it < f_grid_.size() && it >= 0 && f_grid_[it].f_state_ != 2){
                if(f_grid_[it].f_state_ == 0) gain += f_grid_[it].unknown_num_ * g_factor_ * v;
                else if(f_grid_[it].f_state_ == 1){
                    for(auto &v : f_grid_[it].local_vps_){
                        if(!GetVpPos(it, v, vp)) continue;
                        if(LRM_->FeasibleLine(tar_vp, vp)){
                            gain += f_grid_[it].unknown_num_ * g_factor_ * v;
                            break;
                        }
                    }
                }
            }
        }
    }
    return gain * v;
}


void FrontierGrid::InitGainRays(){
    Eigen::Vector3d f = Eigen::Vector3d::Zero();
    Eigen::Vector4d vp;
    double dtheta = cam_hor_ / FOV_h_num_;
    double dphi = cam_ver_ / FOV_v_num_;
    double cos_phi;
    double sin_2_dphi = sin(dphi / 2);

    for(int v_id = 0; v_id < samp_num_; v_id++){
        if(!GetVp(f, v_id, vp, false)){
            ROS_ERROR("InitGainRays0");
            ros::shutdown();
        }
        if(sensor_type_ == SensorType::CAMERA){
            for(int h = 0; h < FOV_h_num_; h++){
                double h_dir = vp(3) + double(h) / FOV_h_num_ * cam_hor_ - cam_hor_ / 2;
                for(int v = 0; v < FOV_v_num_; v++){
                    bool valid_ray = false;
                    double v_dir = double(v) / double(FOV_v_num_) * cam_ver_ - cam_ver_ / 2;
                    tr1::unordered_map<int, double> l1;
                    list<Eigen::Vector3d> ray1;
                    list<pair<Eigen::Vector3d, double>> ray2;
                    Eigen::Vector3d dir;
                    cos_phi = cos(v_dir);
                    dir(0) = cos(h_dir) * cos(v_dir);
                    dir(1) = sin(h_dir) * cos(v_dir);
                    dir(2) = sin(v_dir);
                    double l_gain = 0;
                    for(double l = 0; l < sensor_range_; l += ray_samp_dist1_){
                        Eigen::Vector3d p = dir * l;
                        Eigen::Vector3d pm = p + vp.block(0, 0, 3, 1);
                        int id = BM_->PostoId(p);
                        if(abs(pm.x()) < node_scale_ / 2 && abs(pm.y()) < node_scale_ / 2
                             && abs(pm.z()) < node_scale_ / 2){
                            valid_ray = true;
                            l_gain = l;
                            break;
                        }
                        if(l1.find(id) == l1.end()){
                            l1.insert(pair<int, double>{id, l});
                            ray1.push_back(pm);
                        }
                    }
                    tr1::unordered_map<int, double> l2;
                    for(; l_gain < sensor_range_; l_gain += ray_samp_dist2_){
                        Eigen::Vector3d p = dir * l_gain;
                        Eigen::Vector3d pm = p + vp.block(0, 0, 3, 1);
                        if(abs(pm.x()) > node_scale_ / 2 || abs(pm.y()) > node_scale_ / 2
                             || abs(pm.z()) > node_scale_ / 2){
                            break;
                        }
                        int id = BM_->PostoId(pm);
                        if(l2.find(id) == l2.end()){
                            l2.insert(pair<int, double>{id, l_gain});
                            double gain = 2*dtheta*pow(l_gain, 2)*sin_2_dphi*cos_phi;
                            ray2.push_back({pm, gain});
                        }
                    }
                    if(valid_ray && ray2.size() > 0){
                        gain_rays_[v_id].push_back({ray1, ray2});
                        gain_dirs_[v_id].push_back({dir * l_gain + vp.block(0, 0, 3, 1), 2*dtheta*sin_2_dphi*cos_phi});
                    }
                }
            }
        }
        else if(sensor_type_ == SensorType::LIVOX){
            dtheta = M_PI * 2 / FOV_h_num_;
            dphi = (livox_ver_up_ - livox_ver_low_) / FOV_v_num_;
            sin_2_dphi = sin(dphi / 2);
            for(int h = 0; h < FOV_h_num_; h++){
                double h_dir = vp(3) + double(h) / FOV_h_num_ * M_PI * 2 - M_PI;
                for(int v = 0; v < FOV_v_num_; v++){
                    bool valid_ray = false;
                    double v_dir = double(v) / FOV_v_num_ * (livox_ver_up_ - livox_ver_low_) + livox_ver_low_;
                    tr1::unordered_map<int, double> l1;
                    list<Eigen::Vector3d> ray1;
                    list<pair<Eigen::Vector3d, double>> ray2;
                    Eigen::Vector3d dir;
                    cos_phi = cos(v_dir);
                    dir(0) = cos(h_dir) * cos(v_dir);
                    dir(1) = sin(h_dir) * cos(v_dir);
                    dir(2) = sin(v_dir);
                    double l_gain = 0;
                    for(double l = 0; l < sensor_range_; l += ray_samp_dist1_){
                        Eigen::Vector3d p = dir * l;
                        Eigen::Vector3d pm = p + vp.block(0, 0, 3, 1);
                        int id = BM_->PostoId(p);
                        if(abs(pm.x()) < node_scale_ / 2 && abs(pm.y()) < node_scale_ / 2
                             && abs(pm.z()) < node_scale_ / 2){
                            valid_ray = true;
                            l_gain = l;
                            break;
                        }
                        if(l1.find(id) == l1.end()){
                            l1.insert(pair<int, double>{id, l});
                            ray1.push_back(pm);
                        }
                    }
                    tr1::unordered_map<int, double> l2;
                    for(; l_gain < sensor_range_; l_gain += ray_samp_dist2_){
                        Eigen::Vector3d p = dir * l_gain;
                        Eigen::Vector3d pm = p + vp.block(0, 0, 3, 1);
                        if(abs(pm.x()) > node_scale_ / 2 || abs(pm.y()) > node_scale_ / 2
                             || abs(pm.z()) > node_scale_ / 2){
                            break;
                        }
                        int id = BM_->PostoId(pm);
                        if(l2.find(id) == l2.end()){
                            l2.insert(pair<int, double>{id, l_gain});
                            double gain = 2*dtheta*pow(l_gain, 2)*sin_2_dphi*cos_phi;
                            ray2.push_back({pm, gain});
                        }
                    }
                if(valid_ray && ray2.size() > 0){
                    gain_rays_[v_id].push_back({ray1, ray2});
                    gain_dirs_[v_id].push_back({dir * l_gain + vp.block(0, 0, 3, 1), 2*dtheta*sin_2_dphi*cos_phi});
                }
            }
        }
        }
        else{
            ROS_ERROR("InitGainRays1");
            ros::shutdown();
            return;
        }
    }
}

void FrontierGrid::InitGmaxNear(){
    gmax_ = 0.0;
    gmax_ = node_scale_ * node_scale_ * node_scale_;
    gmax_ += node_scale_ * node_scale_ * node_scale_ * g_factor_ * 6;
}

void FrontierGrid::InitGmax(){
    gmax_ = 0.0;
    list<Eigen::Vector3d> ray;
    VoxelState state;
    
    double dtheta = cam_hor_ / FOV_h_num_;
    double dphi = cam_ver_ / FOV_v_num_;
    double cos_phi;
    double sin_2_dphi = sin(dphi / 2);
    double dr = ray_samp_dist1_;
    Eigen::Vector3d vs(0, 0, 0);
    for(double theta = - (cam_hor_ - dtheta) / 2; theta < (cam_hor_ + dtheta) / 2; theta += dtheta){
        for(double phi = -(cam_ver_ - dphi) / 2; phi < cam_ver_ / 2; phi += dphi){
            Eigen::Vector3d dir;
            dir(0) += cos(theta) * cos(phi);
            dir(1) += sin(theta) * cos(phi);
            dir(2) += sin(phi);
            cos_phi = cos(phi);
            for(double r = dr / 2; r < sensor_range_; r += dr){
                gmax_ += (2 * pow(r, 2) * dr + 1/6 * pow(dr, 3)) * dtheta*sin_2_dphi*cos_phi; //d_l.second * pow((p - pos).norm(), 2);
            }
        }
    }

}

bool FrontierGrid::SampleVps(){
    bool flag = SampleVps(exploring_frontiers_);
    // exploring_frontiers_.clear();
    sample_flag_ = true;
    return flag;
}

void FrontierGrid::SampleVpsCallback(const ros::TimerEvent &e){
    // cout<<"sample num:"<<exploring_frontiers_.size()<<endl;
    SampleVps(exploring_frontiers_);
    // exploring_frontiers_.clear();
    sample_flag_ = true;
}

void FrontierGrid::ExpandFrontier(const int &idx){
    Eigen::Vector3i n(1, node_num_(0), node_num_(0) * node_num_(1));
    Eigen::Vector3i id3;
    double cur_t = ros::WallTime::now().toSec();
    if(!Idx2Posi(idx, id3)) return;
    for(int x = id3(0) - 1; x < id3(0) + 2; x++){
        if(x < 0 || x >= node_num_(0)) continue;
        for(int y = id3(1) - 1; y < id3(1) + 2; y++){
            if(y < 0 || y >= node_num_(1)) continue;
            for(int z = id3(2) - 1; z < id3(2) + 2; z++){
                if(z < 0 || z >= node_num_(2)) continue;
                int n1_idx = x + y * n(1)+ z * n(2);
                if(n1_idx < f_grid_.size() && n1_idx >= 0 && f_grid_[n1_idx].f_state_ == 0){
                    f_grid_[n1_idx].f_state_ = 1;
                    f_grid_[n1_idx].last_sample_ = cur_t - 100.0;
                    if(f_grid_[n1_idx].unknown_num_ < f_grid_[n1_idx].thresh_num_) f_grid_[n1_idx].f_state_ = 2;

                    if(!f_grid_[n1_idx].flags_[2]){
                        exploring_frontiers_show_.push_back(n1_idx);
                        f_grid_[n1_idx].flags_.set(2);
                    }
                    if(!f_grid_[n1_idx].flags_[1] && f_grid_[n1_idx].f_state_ == 1){
                        f_grid_[n1_idx].flags_.set(1);
                        exploring_frontiers_.push_back(n1_idx);
                    }
                }
                else if(n1_idx < f_grid_.size() && n1_idx >= 0 && f_grid_[n1_idx].f_state_ == 1){
                    f_grid_[n1_idx].last_sample_ = cur_t - 100.0;
                    if(!f_grid_[n1_idx].flags_[1]){
                        exploring_frontiers_.push_back(n1_idx);
                        f_grid_[n1_idx].flags_.set(1);
                    }
                }
            }
        }
    }


    // for(int dim = 0; dim < 3; dim++){
    //     if(id3(dim) != 0){
    //         int n1_idx = idx - n(dim);
    //         if(n1_idx < f_grid_.size() && n1_idx >= 0 && f_grid_[n1_idx].f_state_ == 0){
    //             f_grid_[n1_idx].f_state_ = 1;
    //             f_grid_[n1_idx].last_sample_ = cur_t - 100.0;
    //             if(f_grid_[n1_idx].unknown_num_ < f_grid_[n1_idx].thresh_num_) f_grid_[n1_idx].f_state_ = 2;

    //             if(!f_grid_[n1_idx].flags_[2]){
    //                 exploring_frontiers_show_.push_back(n1_idx);
    //                 f_grid_[n1_idx].flags_.set(2);
    //             }

    //             // if(!f_grid_[n1_idx].flags_[2] && f_grid_[n1_idx].f_state_ == 1){
    //             //     exploring_frontiers_show_.push_back(n1_idx);
    //             //     f_grid_[n1_idx].flags_.set(2);
    //             // }
    //             // else if(!f_grid_[n1_idx].flags_[2] && f_grid_[n1_idx].f_state_ == 2){
    //             //     explored_frontiers_show_.push_back(n1_idx);
    //             //     f_grid_[n1_idx].flags_.set(2);
    //             // }

    //             if(!f_grid_[n1_idx].flags_[1] && f_grid_[n1_idx].f_state_ == 1){
    //                 f_grid_[n1_idx].flags_.set(1);
    //                 exploring_frontiers_.push_back(n1_idx);
    //             }
    //         }
    //         else if(n1_idx < f_grid_.size() && n1_idx >= 0 && f_grid_[n1_idx].f_state_ == 1){
    //             f_grid_[n1_idx].last_sample_ = cur_t - 100.0;
    //             if(!f_grid_[n1_idx].flags_[1]){
    //                 exploring_frontiers_.push_back(n1_idx);
    //                 f_grid_[n1_idx].flags_.set(1);
    //             }
    //         }
    //     }
    //     if(id3(dim) != node_num_(dim) - 1){
    //         int n2_idx = idx + n(dim);
    //         if(n2_idx < f_grid_.size() && n2_idx >= 0 && f_grid_[n2_idx].f_state_ == 0){
    //             f_grid_[n2_idx].f_state_ = 1;
    //             f_grid_[n2_idx].last_sample_ = cur_t - 100.0;
    //             if(f_grid_[n2_idx].unknown_num_ < f_grid_[n2_idx].thresh_num_) f_grid_[n2_idx].f_state_ = 2;

    //             if(!f_grid_[n2_idx].flags_[2]){
    //                 exploring_frontiers_show_.push_back(n2_idx);
    //                 f_grid_[n2_idx].flags_.set(2);
    //             }

    //             // if(!f_grid_[n2_idx].flags_[2] && f_grid_[n2_idx].f_state_ == 1){
    //             //     exploring_frontiers_show_.push_back(n2_idx);
    //             //     f_grid_[n2_idx].flags_.set(2);
    //             // }
    //             // else if(!f_grid_[n2_idx].flags_[2] && f_grid_[n2_idx].f_state_ == 2){
    //             //     explored_frontiers_show_.push_back(n2_idx);
    //             //     f_grid_[n2_idx].flags_.set(2);
    //             // }

    //             if(!f_grid_[n2_idx].flags_[1] && f_grid_[n2_idx].f_state_ == 1){
    //                 f_grid_[n2_idx].flags_.set(1);
    //                 exploring_frontiers_.push_back(n2_idx);
    //             }
    //         }
    //         else if(n2_idx < f_grid_.size() && n2_idx >= 0 && f_grid_[n2_idx].f_state_ == 1){
    //             f_grid_[n2_idx].last_sample_ = cur_t - 100.0;
    //             if(!f_grid_[n2_idx].flags_[1]){
    //                 exploring_frontiers_.push_back(n2_idx);
    //                 f_grid_[n2_idx].flags_.set(1);
    //             }
    //         }
    //     }
    // }
}

void FrontierGrid::SampleFrontierNeighbours(const int &idx, const Eigen::Vector3d &cur_p){
    list<int> ids;
    Eigen::Vector3i n(1, node_num_(0), node_num_(0) * node_num_(1));
    Eigen::Vector3i id3;
    double cur_t = ros::WallTime::now().toSec();
    if(!Idx2Posi(idx, id3)) return;
    Eigen::Vector3d dir = (f_grid_[idx].center_ - cur_p).normalized();
    for(int x = id3(0) - 2; x < id3(0) + 3; x++){
        if(x < 0 || x >= node_num_(0)) continue;
        for(int y = id3(1) - 2; y < id3(1) + 3; y++){
            if(y < 0 || y >= node_num_(1)) continue;
            for(int z = id3(2) - 1; z < id3(2) + 2; z++){
                if(z < 0 || z >= node_num_(2)) continue;
                int n1_idx = x + y * n(1)+ z * n(2);
                if(n1_idx < 0 || n1_idx >= f_grid_.size()) continue;
                // if(dir.dot(f_grid_[n1_idx].center_ - cur_p) < 0.0) continue;
                if(f_grid_[n1_idx].f_state_ == 0){
                    f_grid_[n1_idx].f_state_ = 1;
                    f_grid_[n1_idx].last_sample_ = cur_t - 100.0;
                    if(f_grid_[n1_idx].unknown_num_ < f_grid_[n1_idx].thresh_num_) f_grid_[n1_idx].f_state_ = 2;

                    if(!f_grid_[n1_idx].flags_[2]){
                        exploring_frontiers_show_.push_back(n1_idx);
                        f_grid_[n1_idx].flags_.set(2);
                    }
                    if(!f_grid_[n1_idx].flags_[1] && f_grid_[n1_idx].f_state_ == 1){
                        f_grid_[n1_idx].flags_.set(1);
                        ids.push_back(n1_idx);
                    }
                }
                else if(f_grid_[n1_idx].f_state_ == 1){
                    f_grid_[n1_idx].last_sample_ = cur_t - 100.0;
                    if(!f_grid_[n1_idx].flags_[1]){
                        ids.push_back(n1_idx);
                        f_grid_[n1_idx].flags_.set(1);
                    }
                }
            }
        }
    }
    SampleVps(ids, 0.05);
    for(auto i : ids){
        f_grid_[i].flags_.reset(1);
    }
}

void FrontierGrid::GetWildGridsBBX(const Eigen::Vector3d &center, const Eigen::Vector3d &box_scale, list<pair<int, list<pair<int, Eigen::Vector3d>>>> &f_list){
    Eigen::Vector3d upbd, lowbd;
    Eigen::Vector3i upid, lowid, it;
    int f_id;
    // list<int> debug_list;
    upbd = center + box_scale / 2;
    lowbd = center - box_scale / 2;

    for(int dim = 0; dim < 3; dim++){
        upbd(dim) = min(upbd(dim), up_bd_(dim) - 1e-3);
        upbd(dim) = max(upbd(dim), origin_(dim) + 1e-3);
        lowbd(dim) = min(lowbd(dim), up_bd_(dim) - 1e-3);
        lowbd(dim) = max(lowbd(dim), origin_(dim) + 1e-3);
        upid(dim) = (upbd(dim) - origin_(dim)) / node_scale_;
        lowid(dim) = (lowbd(dim) - origin_(dim)) / node_scale_;
    }
    for(it(0) = lowid(0); it(0) <= upid(0); it(0)++){
        for(it(1) = lowid(1); it(1) <= upid(1); it(1)++){
            for(it(2) = lowid(2); it(2) <= upid(2); it(2)++){
                f_id = Posi2Idx(it);
                if(f_id == -1) continue;
                list<pair<int, Eigen::Vector3d>> vps;
                Eigen::Vector4d vp_pose;
                Eigen::Vector3d vp_pos;
                for(int v_id = 0; v_id < samp_num_; v_id++){
                    if(f_grid_[f_id].local_vps_[v_id] == 1 && GetVp(f_id, v_id, vp_pose)){
                        vp_pos = vp_pose.block(0, 0, 3, 1);
                        vps.push_back({v_id, vp_pos});
                    }
                }
                if(vps.size() > 0){
                    f_list.push_back({f_id, vps});
                    // debug_list.emplace_back(f_id);
                }
            }   
        }   
    }
    // Debug(debug_list);
}

void FrontierGrid::LazySampleCallback(const ros::TimerEvent &e){
    Eigen::Vector3d up, low;
    Eigen::Vector3i up_id3, low_id3, it;
    int f_id;
    double cur_t = ros::WallTime::now().toSec();
    up = Robot_pos_ + Eigen::Vector3d::Ones() * sensor_range_ * 0.5;
    low = Robot_pos_ - Eigen::Vector3d::Ones() * sensor_range_ * 0.5;
    for(int dim = 0; dim < 3; dim++){
        up_id3(dim) = min(node_num_(dim) - 1, int(floor((up(dim) - origin_(dim))/node_scale_)));
        low_id3(dim) = max(0, int(floor((low(dim) - origin_(dim))/node_scale_)));
    }
    for(it(0) = low_id3(0); it(0) <= up_id3(0); it(0)++){
        for(it(1) = low_id3(1); it(1) <= up_id3(1); it(1)++){
            for(it(2) = low_id3(2); it(2) <= up_id3(2); it(2)++){
                f_id = Posi2Idx(it);
                if(f_id == -1) continue;
                if(f_grid_[f_id].f_state_ == 1 && !f_grid_[f_id].flags_[1]){
                    f_grid_[f_id].last_sample_ = cur_t - 999;
                    f_grid_[f_id].flags_.set(1);
                    exploring_frontiers_.push_back(f_id);
                }
            }   
        }   
    }
}


// bool FrontierGrid::SampleVps(list<int> &idxs){
//     double gain;
//     Eigen::Vector4d vp_pose;
//     Eigen::Vector3d vp_pos;
//     int vp_id;
//     bool flag = false;
//     double cur_t = ros::WallTime::now().toSec();
//     for(auto &idx : idxs){
//         if(idx < 0 || idx  >= f_grid_.size()) continue;
//         f_grid_[idx].flags_.reset(1);
//         if(cur_t - f_grid_[idx].last_sample_ < resample_duration_) continue;
//         f_grid_[idx].last_sample_ = cur_t;
//         for(int h_id = 0; h_id < samp_h_dir_num_; h_id++){
//             for(int dir_id = 0; dir_id < samp_dir_num_; dir_id++){
//                 vp_id = h_id * samp_dir_num_ + dir_id;
//                 if(!GetVp(idx, vp_id, vp_pose) ||  f_grid_[idx].local_vps_[vp_id] == 2) continue;
//                 vp_pos = vp_pose.block(0,0,3,1);
//                 if(!LRM_->IsFeasible(vp_pos) || LRM_->StrangePoint(vp_pos)){
//                     if(BM_->PosBBXOccupied(vp_pos, Robot_size_)) f_grid_[idx].local_vps_[vp_id] = 2;
//                     continue;
//                 }
//                 if(GetGain(idx, vp_id) < vp_thresh_) {
//                     f_grid_[idx].local_vps_[vp_id] = 2;
//                 }
//                 else{
//                     if(LRM_->IsLocalFeasible(vp_pos)) flag = true;
//                     f_grid_[idx].local_vps_[vp_id] = 1;
//                 }
//             }
//         }
//         bool vp_explored = true;
//         for(int h_id = 0; h_id < samp_num_; h_id++){
//             if(f_grid_[idx].local_vps_[h_id] != 2){
//                 vp_explored = false;
//                 break;
//             }
//         }
//         if(vp_explored){
//             f_grid_[idx].f_state_ = 2;
//             if(!f_grid_[idx].flags_[2]){
//                 explored_frontiers_show_.push_back(idx);
//                 f_grid_[idx].flags_.set(2);
//             }
//         }
//     }
//     return flag;
// }

void FrontierGrid::LazyVgainEvaluate(const ros::TimerEvent &e){
    Eigen::Vector4d vp_pose;
    Eigen::Vector3d vp_pos;
    int vp_id;
    bool flag = false;
    double cur_t = ros::WallTime::now().toSec();
    // for(auto &idx : exploring_frontiers_){
    //     if(ros::WallTime::now().toSec() - cur_t > 0.05) break;
    //     if(idx < 0 || idx  >= f_grid_.size()) continue;
    //     if(cur_t - f_grid_[idx].last_vgain_eval_ < eval_duration_) continue;
    //     f_grid_[idx].last_vgain_eval_ = cur_t;
    //     for(int h_id = 0; h_id < samp_h_dir_num_; h_id++){
    //         for(int dir_id = 0; dir_id < samp_dir_num_; dir_id++){
    //             vp_id = h_id * samp_dir_num_ + dir_id;
    //             if(!GetVp(idx, vp_id, vp_pose) ||  f_grid_[idx].local_vps_[vp_id] == 2 || f_grid_[idx].local_vps_[vp_id] == 0) continue;
    //             f_grid_[idx].gains_[vp_id] = GetVGain(idx, vp_id);
    //         }
    //     }
    // }
}

bool FrontierGrid::StrongCheckViewpoint(const int &f_id, const int &v_id, const bool &allow_unknown){
    Eigen::Vector4d vp_pose;
    static int diag_getvp_failed = 0;
    static int diag_state_not_alive = 0;
    static int diag_block_occupied = 0;
    static int diag_block_not_free = 0;
    static int diag_gain_below = 0;
    static int diag_pass = 0;

    if(!GetVp(f_id, v_id, vp_pose)){
        diag_getvp_failed++;
        ROS_WARN_THROTTLE(
            1.0,
            "HighStar StrongCheck(f,v) reject diag: getvp=%d state=%d block_occ=%d block_not_free=%d gain_below=%d pass=%d last_f=%d last_v=%d",
            diag_getvp_failed, diag_state_not_alive, diag_block_occupied,
            diag_block_not_free, diag_gain_below, diag_pass, f_id, v_id);
        return false;
    }
    if(f_grid_[f_id].local_vps_[v_id] != 1){
        diag_state_not_alive++;
        ROS_WARN_THROTTLE(
            1.0,
            "HighStar StrongCheck(f,v) reject diag: getvp=%d state=%d block_occ=%d block_not_free=%d gain_below=%d pass=%d last_state=%d last_f=%d last_v=%d pos=(%.2f,%.2f,%.2f)",
            diag_getvp_failed, diag_state_not_alive, diag_block_occupied,
            diag_block_not_free, diag_gain_below, diag_pass,
            int(f_grid_[f_id].local_vps_[v_id]), f_id, v_id,
            vp_pose(0), vp_pose(1), vp_pose(2));
        return false;
    }
    auto &frontier = f_grid_[f_id];

    // block check
    Eigen::Vector3d pos = vp_pose.block(0, 0, 3, 1);
    if(allow_unknown && BM_->PosBBXOccupied(pos, Robot_size_*2)) {
        // cout<<"colli"<<endl;
        diag_block_occupied++;
        ROS_WARN_THROTTLE(
            1.0,
            "HighStar StrongCheck(f,v) reject diag: getvp=%d state=%d block_occ=%d block_not_free=%d gain_below=%d pass=%d reason=block_occ last_f=%d last_v=%d pos=(%.2f,%.2f,%.2f)",
            diag_getvp_failed, diag_state_not_alive, diag_block_occupied,
            diag_block_not_free, diag_gain_below, diag_pass,
            f_id, v_id, pos(0), pos(1), pos(2));
        return false;
    }
    else if(!allow_unknown && !BM_->PosBBXFree(pos, Robot_size_*2)) {
        // cout<<"colli"<<endl;
        diag_block_not_free++;
        ROS_WARN_THROTTLE(
            1.0,
            "HighStar StrongCheck(f,v) reject diag: getvp=%d state=%d block_occ=%d block_not_free=%d gain_below=%d pass=%d reason=block_not_free last_f=%d last_v=%d pos=(%.2f,%.2f,%.2f)",
            diag_getvp_failed, diag_state_not_alive, diag_block_occupied,
            diag_block_not_free, diag_gain_below, diag_pass,
            f_id, v_id, pos(0), pos(1), pos(2));
        return false;
    }

    //gain check
    Eigen::Vector3d f_scale = (frontier.up_ - frontier.down_) / 2;

    list<Eigen::Vector3d> ray;
    double gain = 0;
    bool inside_f;
    VoxelState state;
    for(auto &d_l : gain_dirs_[v_id]){
        BM_->GetCastLine(pos, d_l.first + f_grid_[f_id].center_, ray);
        for(auto &p : ray){
            inside_f = false;
            for(int dim = 0; dim < 3; dim++){
                if(abs(frontier.center_(dim) - p(dim)) < f_scale(dim)){
                    inside_f = true;
                    break;
                }
            }
            state = BM_->GetVoxState(p);
            if(!inside_f){
                if(state == VoxelState::occupied || state == VoxelState::out){
                    break;
                }
            }
            else{
                if(state == VoxelState::free){
                    continue;
                }
                else if(state == VoxelState::occupied || state == VoxelState::out){
                    break;
                }
                else{
                    gain += d_l.second * pow((p - pos).norm(), 2);
                    break;
                }
            }
        }
    }
    if(gain < vp_thresh_) {
        diag_gain_below++;
        ROS_WARN_THROTTLE(
            1.0,
            "HighStar StrongCheck(f,v) reject diag: getvp=%d state=%d block_occ=%d block_not_free=%d gain_below=%d pass=%d reason=gain last_gain=%.4f thresh=%.4f last_f=%d last_v=%d pos=(%.2f,%.2f,%.2f)",
            diag_getvp_failed, diag_state_not_alive, diag_block_occupied,
            diag_block_not_free, diag_gain_below, diag_pass,
            gain, vp_thresh_, f_id, v_id, pos(0), pos(1), pos(2));
        return false;
    }
    diag_pass++;
    ROS_WARN_THROTTLE(
        2.0,
        "HighStar StrongCheck(f,v) pass diag: getvp=%d state=%d block_occ=%d block_not_free=%d gain_below=%d pass=%d last_gain=%.4f thresh=%.4f last_f=%d last_v=%d pos=(%.2f,%.2f,%.2f)",
        diag_getvp_failed, diag_state_not_alive, diag_block_occupied,
        diag_block_not_free, diag_gain_below, diag_pass,
        gain, vp_thresh_, f_id, v_id, pos(0), pos(1), pos(2));
    return true;
}

bool FrontierGrid::StrongCheckViewpoint(Eigen::Vector4d &vp_pose, const bool &allow_unknown){
    static int diag_block_occupied = 0;
    static int diag_block_not_free = 0;
    static int diag_gain_below = 0;
    static int diag_pass = 0;

    // block check
    Eigen::Vector3d pos = vp_pose.block(0, 0, 3, 1);
    if(allow_unknown && BM_->PosBBXOccupied(pos, Robot_size_*2)) {
        // cout<<"colli"<<endl;
        diag_block_occupied++;
        ROS_WARN_THROTTLE(
            1.0,
            "HighStar StrongCheck(pose) reject diag: block_occ=%d block_not_free=%d gain_below=%d pass=%d reason=block_occ pos=(%.2f,%.2f,%.2f)",
            diag_block_occupied, diag_block_not_free, diag_gain_below, diag_pass,
            pos(0), pos(1), pos(2));
        return false;
    }
    else if(!allow_unknown && !BM_->PosBBXFree(pos, Robot_size_*2)) {
        // cout<<"colli"<<endl;
        diag_block_not_free++;
        ROS_WARN_THROTTLE(
            1.0,
            "HighStar StrongCheck(pose) reject diag: block_occ=%d block_not_free=%d gain_below=%d pass=%d reason=block_not_free pos=(%.2f,%.2f,%.2f)",
            diag_block_occupied, diag_block_not_free, diag_gain_below, diag_pass,
            pos(0), pos(1), pos(2));
        return false;
    }

    double gain = 0;
    double dtheta = cam_hor_ / FOV_h_num_;
    double dphi = cam_ver_ / FOV_v_num_;
    double phi, theta;
    double rc;
    double cos_phi;
    double sin_2_dphi = sin(dphi / 2);
    double dr = ray_samp_dist2_, ray_range;
    double g;
    VoxelState state;
    int v = 0, h = 0;
    Eigen::Vector3d endp, dir, ray_end;

    for(int i = 0; i < FOV_h_num_; i++){
        theta = (-FOV_h_num_ * 0.5 + i + 0.5) * dtheta + vp_pose(3);
        for(int j = 0; j < FOV_v_num_; j++){
            phi = (-FOV_v_num_ * 0.5 + j + 0.5) * dphi;
            dir(0) = cos(theta) * cos(phi);
            dir(1) = sin(theta) * cos(phi);
            dir(2) = sin(phi);
            cos_phi = cos(phi);
            g = dtheta*sin_2_dphi*cos_phi;
            ray_end = pos + dir * sensor_range_;
            GetRayEndInsideMap(pos, ray_end);
            ray_range = (pos - ray_end).norm();
            for(double r = dr / 2; r < ray_range; r += dr){
                endp = pos + dir * r;
                state = BM_->GetVoxState(endp);
                if(state == VoxelState::free){
                    continue;
                }
                else if(state == VoxelState::occupied || state == VoxelState::out){
                    break;
                }
                else{
                    gain += (2 * pow(r, 2) * dr + 1/6 * pow(dr, 3)) * g; //d_l.second * pow((p - pos).norm(), 2);
                }
            }
        }
    }
    // cout<<"gain:"<<gain<<endl;
    if(gain < second_gain_thresh_) {
        diag_gain_below++;
        ROS_WARN_THROTTLE(
            1.0,
            "HighStar StrongCheck(pose) reject diag: block_occ=%d block_not_free=%d gain_below=%d pass=%d reason=second_gain gain=%.4f thresh=%.4f pos=(%.2f,%.2f,%.2f)",
            diag_block_occupied, diag_block_not_free, diag_gain_below, diag_pass,
            gain, second_gain_thresh_, pos(0), pos(1), pos(2));
        return false;
    }
    diag_pass++;
    ROS_WARN_THROTTLE(
        2.0,
        "HighStar StrongCheck(pose) pass diag: block_occ=%d block_not_free=%d gain_below=%d pass=%d gain=%.4f thresh=%.4f pos=(%.2f,%.2f,%.2f)",
        diag_block_occupied, diag_block_not_free, diag_gain_below, diag_pass,
        gain, second_gain_thresh_, pos(0), pos(1), pos(2));
    return true;
}

double FrontierGrid::GetVGain(const int &f_id, const int &v_id, bool debug){
    Eigen::Vector4d vp_pose;
    double gain = 0.0;
    if(!GetVp(f_id, v_id, vp_pose)) {
        // ROS_WARN("vp failed!");
        return gain;
    }
    Eigen::Vector3d vp_pos, ray_end;
    list<Eigen::Vector3d> ray;
    list<Eigen::Vector3d> debug_pts;
    VoxelState state;
    double dtheta = cam_hor_ / FOV_h_num_*1.5;
    double dphi = cam_ver_ / FOV_v_num_*1.5;
    double cos_phi;
    double sin_2_dphi = sin(dphi / 2);
    double dr = ray_samp_dist1_, ray_range;
    vp_pos = vp_pose.head(3);
    for(double theta = vp_pose(3) - (cam_hor_ - dtheta) / 2; theta < vp_pose(3) + (cam_hor_ + dtheta) / 2; theta += dtheta){
        for(double phi = -(cam_ver_ - dphi) / 2; phi < cam_ver_ / 2; phi += dphi){
            Eigen::Vector3d endp;// = vp_pose.head(3);
            Eigen::Vector3d dir;
            dir(0) = cos(theta) * cos(phi);
            dir(1) = sin(theta) * cos(phi);
            dir(2) = sin(phi);
            cos_phi = cos(phi);
            ray_end = vp_pose.head(3) + dir * sensor_range_;
            GetRayEndInsideMap(vp_pos, ray_end);
            ray_range = (vp_pos - ray_end).norm();
            for(double r = dr / 2; r < ray_range; r += dr){
                endp = vp_pose.head(3) + dir * r;
                state = BM_->GetVoxState(endp);
                // debug_pts.emplace_back(endp);
                if(state == VoxelState::free){
                    continue;
                }
                else if(state == VoxelState::occupied || state == VoxelState::out){
                    break;
                }
                else{
                    gain += (2 * pow(r, 2) * dr + 1/6 * pow(dr, 3)) * dtheta*sin_2_dphi*cos_phi; //d_l.second * pow((p - pos).norm(), 2);
                    // if(gain >= 50.0)
                    // return 50.0;
                }
            }
        }
    }
    // if(debug) Debug(debug_pts, 100);
    // if(gain < 1e-4) {
        // Debug(debug_pts, 100);
        // cout<<"vp:"<<vp_pose.transpose()<<endl;
    // }

    return gain;
}


double FrontierGrid::GetVGain(const int &f_id, const int &v_id, vector<vector<double>> &gain_depth, Eigen::Vector3d &u_center){
    Eigen::Vector4d vp_pose;
    double gain = 0.0;
    if(!GetVp(f_id, v_id, vp_pose)) return gain;
    Eigen::Vector3d vp_pos, ray_end;//, debug_pt;
    int debug_count = 0;
    vp_pos = vp_pose.head(3);
    list<Eigen::Vector3d> ray;
    // list<Eigen::Vector3d> debug_pts;
    VoxelState state;
    // Eigen::Vector3d ray_end;
    double dtheta = cam_hor_ / FOV_h_num_;
    double dphi = cam_ver_ / FOV_v_num_;
    double cos_phi, sin_phi, sin_dphi, sin_theta, cos_theta;
    double sin_2_dphi = sin(dphi / 2);
    double sin_2_dtheta = sin(dtheta / 2);
    double dr = ray_samp_dist1_;
    double g;
    double ray_range;
    int i = 0, j = 0;
    double phi, theta;
    double dr4, s2d, sd, cd, c2d;

    gain_depth.resize(FOV_h_num_);
    sin_dphi = sin(dphi);
    u_center.setZero();
    for(i = 0; i < FOV_h_num_; i++){
        theta = (-FOV_h_num_ * 0.5 + i + 0.5) * dtheta + vp_pose(3);
        gain_depth[i].resize(FOV_v_num_);
        sin_theta = sin(theta);
        cos_theta = cos(theta);
        sd = 2*cos_theta*sin_2_dtheta;
        cd = 2*sin_theta*sin_2_dtheta;
        for(j = 0; j < FOV_v_num_; j++){
            phi = (-FOV_v_num_ * 0.5 + j + 0.5) * dphi;
            gain_depth[i][j] = sensor_range_;
            Eigen::Vector3d endp;// = vp_pose.head(3);
            Eigen::Vector3d dir;
            cos_phi = cos(phi);
            sin_phi = sin(phi);

            dir(0) = cos_theta * cos_phi;
            dir(1) = sin_theta * cos_phi;
            dir(2) = sin_phi;

            s2d = 0.5*(dphi + (cos_phi - sin_phi)*(cos_phi + sin_phi)*sin_dphi);
            c2d = cos_phi*sin_phi*sin_dphi;
            g = dtheta*sin_2_dphi*cos_phi;
            ray_end = vp_pos + dir * sensor_range_;
            GetRayEndInsideMap(vp_pos, ray_end);
            ray_range = (vp_pos - ray_end).norm();
            for(double r = dr / 2; r < ray_range; r += dr){
                endp = vp_pos + dir * r;
                state = BM_->GetVoxState(endp);
                if(state == VoxelState::free){
                    continue;
                }
                else if(state == VoxelState::occupied || state == VoxelState::out){
                    gain_depth[i][j] = r;
                    break;
                }
                else{
                    gain += (2 * pow(r, 2) * dr + 1/6 * pow(dr, 3)) * g; //d_l.second * pow((p - pos).norm(), 2);
                    dr4 = 0.25*(4*pow(r, 3) + r * dr*dr) * dr;
                    u_center(0) += dr4*s2d*sd;
                    u_center(1) += dr4*s2d*cd;
                    u_center(2) += dr4*c2d*dtheta;
                    // debug_pt += endp;
                    // debug_count++;
                }
            }
        }
    }
    // debug_pt = debug_pt/debug_count;
    // cout<<"debug pt:"<<debug_pt.transpose()<<endl;
    // cout<<"debug_count:"<<debug_count<<endl;
    if(gain > 1e-3) u_center = u_center/gain + vp_pos;
    return gain;
}

double FrontierGrid::GetVGainSubmod(const int &f_id, const int &v_id, const vector<vector<double>> &gain_depth, const Eigen::Vector4d vp_pr){
    Eigen::Vector4d vp_pose;
    double gain = 0.0;
    if(!GetVp(f_id, v_id, vp_pose)) return gain;
    Eigen::Vector3d vp_pos, ray_end;
    list<Eigen::Vector3d> ray;
    // list<Eigen::Vector3d> debug_pts;
    VoxelState state;
    double dtheta = cam_hor_ / FOV_h_num_;
    double dphi = cam_ver_ / FOV_v_num_;
    double cos_phi;
    double sin_2_dphi = sin(dphi / 2);
    double dr = ray_samp_dist1_;
    double g;
    int i = 0, j = 0;
    int v = 0, h = 0;
    double phi, theta, ray_range;
    double rc;
    vp_pos = vp_pose.head(3);
    // gain_depth.resize(FOV_h_num_);
    for(i = 0; i < FOV_h_num_; i++){
        theta = (-FOV_h_num_ * 0.5 + i + 0.5) * dtheta + vp_pose(3);

        // gain_depth.back().resize(FOV_v_num_);
        for(j = 0; j < FOV_v_num_; j++){
            phi = (-FOV_h_num_ * 0.5 + j + 0.5) * dphi;

            Eigen::Vector3d endp;// = vp_pose.head(3);
            Eigen::Vector3d dir;
            dir(0) = cos(theta) * cos(phi);
            dir(1) = sin(theta) * cos(phi);
            dir(2) = sin(phi);
            cos_phi = cos(phi);
            g = dtheta*sin_2_dphi*cos_phi;
            ray_end = vp_pos + dir * sensor_range_;
            GetRayEndInsideMap(vp_pos, ray_end);
            ray_range = (vp_pos - ray_end).norm();
            for(double r = dr / 2; r < ray_range; r += dr){
                endp = vp_pos + dir * r;
                state = BM_->GetVoxState(endp);
                if(state == VoxelState::free){
                    continue;
                }
                else if(state == VoxelState::occupied || state == VoxelState::out){
                    break;
                }   
                else{
                    if(GetImgIdx(vp_pr, endp, v, h, rc) && rc < gain_depth[h][v]) continue;
                    gain += (2 * pow(r, 2) * dr + 1/6 * pow(dr, 3)) * g; //d_l.second * pow((p - pos).norm(), 2);
                }
            }
        }
    }
    return gain;
}

double FrontierGrid::SampleBestYawSubmod(const vector<vector<double>> &gain_depth, const Eigen::Vector3d &pos, 
                                            double &best_yaw, const Eigen::Vector4d vp_pr, const double &vel, const double &dy){
    vector<double> gains;
    double dtheta = cam_hor_ / FOV_h_num_;
    double dphi = cam_ver_ / FOV_v_num_;
    int hor_num = M_PI * 2 / dtheta;
    dtheta = M_PI * 2 / hor_num;
    gains.resize(hor_num, 0);
    double phi, theta;
    double rc;
    double cos_phi;
    double sin_2_dphi = sin(dphi / 2);
    double dr = ray_samp_dist1_, ray_range;
    double g;
    VoxelState state;
    int v = 0, h = 0;
    // Eigen::Vector3d endp;// = vp_pose.head(3);
    // ROS_WARN("SampleBestYawSubmod0");
    // cout<<"hor_num:"<<hor_num<<endl;
    Eigen::Vector3d endp, dir, ray_end;
    for(int i = 0; i < hor_num; i++){
        theta = (i + 0.5) * dtheta;
        for(int j = 0; j < FOV_v_num_; j++){
            phi = (-FOV_h_num_ * 0.5 + j + 0.5) * dphi;
            dir(0) = cos(theta) * cos(phi);
            dir(1) = sin(theta) * cos(phi);
            dir(2) = sin(phi);
            cos_phi = cos(phi);
            g = dtheta*sin_2_dphi*cos_phi;
            ray_end = pos + dir * sensor_range_;
            GetRayEndInsideMap(pos, ray_end);
            ray_range = (pos - ray_end).norm();
            for(double r = dr / 2; r < ray_range; r += dr){
                endp = pos + dir * r;
                state = BM_->GetVoxState(endp);
                if(state == VoxelState::free){
                    continue;
                }
                else if(state == VoxelState::occupied || state == VoxelState::out){
                    break;
                }
                else{
                    if(GetImgIdx(vp_pr, endp, v, h, rc) && rc < gain_depth[h][v]) continue;
                    // if(h < 0 || h >= gain_depth.size()) {
                    //     ROS_ERROR("error h");
                    //     cout<<"h:"<<h<<endl;
                    //     cout<<"gain_depth:"<<gain_depth.size()<<endl;
                    // }
                    // if(v < 0 || v >= gain_depth[h].size()) {
                    //     cout<<"v:"<<v<<endl;
                    //     cout<<"h:"<<h<<endl;
                    //     cout<<"gain_depth[h]:"<<gain_depth[h].size()<<endl;
                    //     cout<<"gain_depth:"<<gain_depth.size()<<endl;
                    //     ROS_ERROR("error v");
                    // }
                    // if(rc < gain_depth[h][v]) {
                    //     // cout<<"rc:"<<rc<<"  depth:"<<gain_depth[h][v]<<endl;
                    //     continue;
                    // }
                    // else{
                    //     cout<<"============rc:"<<rc<<"  depth:"<<gain_depth[h][v]<<" g:"<<(2 * pow(r, 2) * dr + 1/6 * pow(dr, 3)) * g<<endl;
                    // }
                    gains[i] += (2 * pow(r, 2) * dr + 1/6 * pow(dr, 3)) * g; //d_l.second * pow((p - pos).norm(), 2);
                }
            }
        }
    }

    /* init first vp gain */
    double gain = 0, gain_exp;
    double best_gain = 0;
    int vp_h_num = cam_hor_ / dtheta;
    double yaw = vp_h_num * 0.5 * dtheta;
    double dyt, dpt;
    double dyaw;
    dpt = (pos - vp_pr.head(3)).norm() / vel;
    double pena;
    for(int i = 0; i < vp_h_num; i++){
        gain += gains[i];
        // cout<<"i:"<<i<<"  g:"<<gains[i]<<endl;
    }

    dyaw = abs(YawDiff(vp_pr(3), yaw));
    dyt = dyaw / dy;
    if(dyaw < second_yaw_thresh_ && gain > second_gain_thresh_){
        best_yaw = yaw;
        best_gain = gain;
        best_gain *= exp(-lambda_ * max(dpt, dyt));
    }

    /* find best */
    int delet_idx, add_idx;


    for(int i = 1; i < hor_num; i++){
        delet_idx = i - 1;
        add_idx = delet_idx + vp_h_num;
        if(add_idx >= hor_num) add_idx -= hor_num;
        gain += gains[add_idx];
        gain -= gains[delet_idx];
        yaw = (i + vp_h_num * 0.5) * dtheta;
        dyaw = abs(YawDiff(vp_pr(3), yaw));
        dyt = dyaw / dy;
        gain_exp = gain * exp(-lambda_ * max(dpt, dyt));
        if(gain > second_gain_thresh_ && gain_exp > best_gain && dyaw < second_yaw_thresh_){
            best_gain = gain_exp;
            best_yaw = yaw;
        }
    }
    return best_gain;
}

double FrontierGrid::SampleBestYaw(const Eigen::Vector3d &pos, double &best_yaw, const double &y0, 
                                    const double &yaw_thresh){
    vector<double> gains;
    double dtheta = cam_hor_ / FOV_h_num_;
    double dphi = cam_ver_ / FOV_v_num_;
    int hor_num = M_PI * 2 / dtheta;
    dtheta = M_PI * 2 / hor_num;
    gains.resize(hor_num, 0);
    double phi, theta;
    double rc;
    double cos_phi;
    double sin_2_dphi = sin(dphi / 2);
    double dr = ray_samp_dist2_, ray_range;
    double g;
    VoxelState state;
    int v = 0, h = 0;
    Eigen::Vector3d endp, dir, ray_end;
    for(int i = 0; i < hor_num; i++){
        theta = (i + 0.5) * dtheta;
        for(int j = 0; j < FOV_v_num_; j++){
            phi = (-FOV_h_num_ * 0.5 + j + 0.5) * dphi;
            dir(0) = cos(theta) * cos(phi);
            dir(1) = sin(theta) * cos(phi);
            dir(2) = sin(phi);
            cos_phi = cos(phi);
            g = dtheta*sin_2_dphi*cos_phi;
            // 2*dtheta*pow(l_gain, 2)*sin_2_dphi*cos_phi;
            ray_end = pos + dir * sensor_range_;
            GetRayEndInsideMap(pos, ray_end);
            ray_range = (pos - ray_end).norm();
            for(double r = dr / 2; r < ray_range; r += dr){
                endp = pos + dir * r;
                state = BM_->GetVoxState(endp);
                if(state == VoxelState::free){
                    continue;
                }
                else if(state == VoxelState::occupied || state == VoxelState::out){
                    break;
                }
                else{
                    gains[i] += (2 * pow(r, 2) * dr + 1/6 * pow(dr, 3)) * g; //d_l.second * pow((p - pos).norm(), 2);
                }
            }
        }
    }
    /* init first vp gain */
    double gain = 0, gain_exp;
    double best_gain = 0;
    int vp_h_num = cam_hor_ / dtheta;
    double yaw = vp_h_num * 0.5 * dtheta;
    double dyaw;
    for(int i = 0; i < vp_h_num; i++){
        gain += gains[i];
        // cout<<"i:"<<i<<"  g:"<<gains[i]<<endl;
    }
    dyaw = abs(YawDiff(y0, yaw));
    if(dyaw < yaw_thresh){
        best_yaw = yaw;
        best_gain = gain;
    }

    /* find best */
    int delet_idx, add_idx;


    for(int i = 1; i < hor_num; i++){
        delet_idx = i - 1;
        add_idx = delet_idx + vp_h_num;
        if(add_idx >= hor_num) add_idx -= hor_num;
        gain += gains[add_idx];
        gain -= gains[delet_idx];
        yaw = (i + vp_h_num * 0.5) * dtheta;
        dyaw = abs(YawDiff(y0, yaw));
        gain_exp = gain;
        if(gain_exp > best_gain && dyaw < yaw_thresh){
            best_gain = gain_exp;
            best_yaw = yaw;
        }
    }
    return best_gain;
}

int FrontierGrid::GetClosestFid(Eigen::Vector3d p){
    if(InsideMap(p)){
        Eigen::Vector3d dpos = p - origin_;
        Eigen::Vector3i posid, pit;
        posid.x() = floor(dpos.x() / node_scale_);
        posid.y() = floor(dpos.y() / node_scale_);
        posid.z() = floor(dpos.z() / node_scale_);
        int id, best_id = 0;
        double d = 9999.0;
        for(int x = -1; x < 2; x++){
            for(int y = -1; y < 2; y++){
                for(int z = -1; z < 2; z++){
                    pit(0) = posid(0) + x;
                    pit(1) = posid(1) + y;
                    pit(2) = posid(2) + z;
                    id = pit(2)*node_num_(0)*node_num_(1) + pit(1)*node_num_(0) + pit(0);
                    if(id >= 0 && id < f_grid_.size()){
                        if((f_grid_[id].center_ - p).norm() < d){
                            d = (f_grid_[id].center_ - p).norm();
                            best_id = id;
                        }
                    }
                }
            }
        }
        return best_id;
    }
    return 0;
}

void FrontierGrid::ShowVpsCallback(const ros::TimerEvent &e){
    // cout<<"SHOW!!!!!!!!!!!!!!!!!!!!!!!"<<endl;//debug
    Eigen::Vector4d vp_pose;
    visualization_msgs::MarkerArray mka;
    visualization_msgs::Marker mk1, mk2;
    mk1.header.frame_id = "world";
    mk1.header.stamp = ros::Time::now();
    mk1.id = 1;
    mk1.action = visualization_msgs::Marker::ADD;
    mk1.type = visualization_msgs::Marker::CUBE;
    mk1.scale.x = node_scale_;
    mk1.scale.y = node_scale_;
    mk1.scale.z = node_scale_;
    mk1.color.a = 0.2;
    mk1.color.b = 0.7;
    mk1.color.g = 0.6;
    mk1.color.r = 0.6;
    mk1.pose.position.x = 0;
    mk1.pose.position.y = 0;
    mk1.pose.position.z = 0;
    mk1.pose.orientation.x = 0;
    mk1.pose.orientation.y = 0;
    mk1.pose.orientation.z = 0;
    mk1.pose.orientation.w = 1;
    mk2 = mk1;
    mk2.type = visualization_msgs::Marker::LINE_LIST;
    mk2.scale.x = 0.02;
    mk2.scale.y = 0.02;
    mk2.scale.z = 0.02;
    std_msgs::ColorRGBA cl;
    // ROS_WARN("ShowVpsCallback0");
    // for(int f = 0; f < f_grid_.size(); f++){
    for(auto &f : exploring_frontiers_show_){
        // ROS_WARN("ShowVpsCallback0.0");
        auto &frontier = f_grid_[f];
        if(frontier.f_state_ == 0)
            continue;
        // ROS_WARN("ShowVpsCallback0.1");
        if(frontier.f_state_ == 2){
            explored_frontiers_show_.push_back(f);
            continue;
        }
        // ROS_WARN("ShowVpsCallback0.2");
        frontier.flags_.reset(2);
        mk1.action = visualization_msgs::Marker::ADD;
        mk2.action = visualization_msgs::Marker::ADD;
        // mk1.points.clear();
        mk2.points.clear();
        mk1.id = f * 2;
        mk2.id = f * 2 + 1;
        cl = CM_->Id2Color(f, 0.15);
        mk1.color = cl;
        mk1.pose.position.x = frontier.center_(0);
        mk1.pose.position.y = frontier.center_(1);
        mk1.pose.position.z = frontier.center_(2);
        mk1.scale.x = frontier.up_(0) - frontier.down_(0);
        mk1.scale.y = frontier.up_(1) - frontier.down_(1);
        mk1.scale.z = frontier.up_(2) - frontier.down_(2);
        // mk2.color = cl;
        // mk2.color.a = 0.3;
        bool valid = false;
        for(int vp_id = 0; vp_id < samp_num_; vp_id++){
            if(frontier.local_vps_[vp_id] == 1 && GetVp(f, vp_id, vp_pose)){
                valid = true;
                break;
        //         LoadVpLines(mk2, vp_pose);
            }
        }
        if(valid)
            mka.markers.emplace_back(mk1);
        else
            explored_frontiers_show_.push_back(f);
        // mka.markers.emplace_back(mk2);
    }
    mk1.points.clear();
    mk2.points.clear();
    mk1.action = visualization_msgs::Marker::ADD;
    // mk1.action = visualization_msgs::Marker::DELETE;
    mk2.action = visualization_msgs::Marker::DELETE;
    mk1.color.a = 0.01;
    mk1.color.b = 0.7;
    mk1.color.g = 0.7;
    mk1.color.r = 0.7;
    for(auto &f : explored_frontiers_show_){
        auto &frontier = f_grid_[f];
        frontier.flags_.reset(2);
        mk1.id = f * 2;
        // mk2.id = f * 2 + 1;
        mk1.pose.position.x = frontier.center_(0);
        mk1.pose.position.y = frontier.center_(1);
        mk1.pose.position.z = frontier.center_(2);
        mk1.scale.x = frontier.up_(0) - frontier.down_(0);
        mk1.scale.y = frontier.up_(1) - frontier.down_(1);
        mk1.scale.z = frontier.up_(2) - frontier.down_(2);
        
        mka.markers.emplace_back(mk1);
        // mka.markers.emplace_back(mk2);
    }
    // ROS_WARN("ShowVpsCallback2");
    show_pub_.publish(mka);
    explored_frontiers_show_.clear();
    exploring_frontiers_show_.clear();
}

void FrontierGrid::ShowGainDebug(){
    visualization_msgs::Marker mk, mkr1, mkr2;
    mk.header.frame_id = "world";
    mk.header.stamp = ros::Time::now();
    mk.id = 1;
    mk.action = visualization_msgs::Marker::ADD;
    mk.type = visualization_msgs::Marker::CUBE;
    mk.scale.x = node_scale_;
    mk.scale.y = node_scale_;
    mk.scale.z = node_scale_;
    mk.color.a = 0.2;
    mk.color.b = 1.0;
    mk.pose.position.x = 0;
    mk.pose.position.y = 0;
    mk.pose.position.z = 0;
    mk.pose.orientation.x = 0;
    mk.pose.orientation.y = 0;
    mk.pose.orientation.z = 0;
    mk.pose.orientation.w = 1;

    Eigen::Vector3d z_pos = Eigen::Vector3d::Zero();
    Eigen::Vector4d v_pose;
    mk.color.b = 0;
    mkr1 = mk;
    mkr2 = mk;
    mkr1.color.r = 0.7;
    mkr2.color.g = 0.7;
    mkr1.color.a = 0.7;
    mkr2.color.a = 0.7;
    mkr1.scale.x = resolution_;
    mkr1.scale.y = resolution_;
    mkr1.scale.z = resolution_;
    mkr2.scale.x = resolution_;
    mkr2.scale.y = resolution_;
    mkr2.scale.z = resolution_;
    mkr1.type = visualization_msgs::Marker::CUBE_LIST;
    mkr2.type = visualization_msgs::Marker::CUBE_LIST;
    geometry_msgs::Point pt;
    for(int i = 0; i < gain_rays_.size(); i++){

        mkr1.id = i*2 + 2;
        mkr2.id = i*2 + 3;
        mkr1.points.clear();
        mkr2.points.clear();

        mkr1.action = visualization_msgs::Marker::ADD;
        mkr2.action = visualization_msgs::Marker::ADD;
        if(!ros::ok()) return;
        if(!GetVp(z_pos, i, v_pose)){
            ROS_ERROR("error vp id%d", int(i));
            return;
        }
        pt.x = v_pose(0);
        pt.y = v_pose(1);
        pt.z = v_pose(2);
        mkr1.points.push_back(pt);
        for(auto &rays : gain_rays_[i]){
            for(auto & p1 : rays.first){
                pt.x = p1.x();
                pt.y = p1.y();
                pt.z = p1.z();
                mkr1.points.push_back(pt);
            }
            for(auto & p2 : rays.second){
                pt.x = p2.first.x();
                pt.y = p2.first.y();
                pt.z = p2.first.z();
                mkr2.points.push_back(pt);
            }
        }
        ros::Duration(0.05).sleep();
        debug_pub_.publish(mkr2);
        debug_pub_.publish(mkr1);
        ros::Duration(0.3).sleep();
        
        mkr1.action = visualization_msgs::Marker::DELETE;
        mkr2.action = visualization_msgs::Marker::DELETE;
        debug_pub_.publish(mkr2);
        debug_pub_.publish(mkr1);
    }

}

void FrontierGrid::LoadVpLines(visualization_msgs::Marker &mk, Eigen::Vector4d &vp){
    geometry_msgs::Point pt0, pt1, pt2, pt3, pt4;
    pt0.x = vp(0);    
    pt0.y = vp(1);    
    pt0.z = vp(2);
    pt1.x = vp(0) + 0.5 * cos(vp(3) + cam_hor_/2) * cos(-cam_ver_/2);    
    pt1.y = vp(1) + 0.5 * sin(vp(3) + cam_hor_/2) * cos(-cam_ver_/2);
    pt1.z = vp(2) + sin(-cam_ver_/2) * 0.5;
    pt2.x = vp(0) + 0.5 * cos(vp(3) - cam_hor_/2) * cos(-cam_ver_/2);      
    pt2.y = vp(1) + 0.5 * sin(vp(3) - cam_hor_/2) * cos(-cam_ver_/2);    
    pt2.z = vp(2) + sin(-cam_ver_/2) * 0.5;
    pt3.x = vp(0) + 0.5 * cos(vp(3) + cam_hor_/2) * cos(cam_ver_/2);    
    pt3.y = vp(1) + 0.5 * sin(vp(3) + cam_hor_/2) * cos(cam_ver_/2);
    pt3.z = vp(2) + sin(cam_ver_/2) * 0.5;
    pt4.x = vp(0) + 0.5 * cos(vp(3) - cam_hor_/2) * cos(cam_ver_/2);    
    pt4.y = vp(1) + 0.5 * sin(vp(3) - cam_hor_/2) * cos(cam_ver_/2); 
    pt4.z = vp(2) + sin(cam_ver_/2) * 0.5;

    mk.points.push_back(pt0);
    mk.points.push_back(pt1);
    mk.points.push_back(pt0);
    mk.points.push_back(pt2);
    mk.points.push_back(pt0);
    mk.points.push_back(pt3);
    mk.points.push_back(pt0);
    mk.points.push_back(pt4);

    mk.points.push_back(pt1);
    mk.points.push_back(pt2);

    mk.points.push_back(pt2);
    mk.points.push_back(pt4);

    mk.points.push_back(pt3);
    mk.points.push_back(pt4);
    
    mk.points.push_back(pt3);
    mk.points.push_back(pt1);
}

void FrontierGrid::Debug(list<int> &v_ids){
    visualization_msgs::Marker mk;
    mk.header.frame_id = "world";
    mk.header.stamp = ros::Time::now();
    mk.id = -1;
    mk.action = visualization_msgs::Marker::ADD;
    mk.type = visualization_msgs::Marker::CUBE_LIST;
    mk.scale.x = node_scale_;
    mk.scale.y = node_scale_;
    mk.scale.z = node_scale_;
    mk.color.a = 1.0;
    mk.color.b = 1.0;
    mk.pose.position.x = 0;
    mk.pose.position.y = 0;
    mk.pose.position.z = 0;
    mk.pose.orientation.x = 0;
    mk.pose.orientation.y = 0;
    mk.pose.orientation.z = 0;
    mk.pose.orientation.w = 1;
    geometry_msgs::Point pt;
    for(auto &v_id : v_ids){
        if(v_id < 0 || v_id >= f_grid_.size()) continue;
        pt.x = f_grid_[v_id].center_(0);
        pt.y = f_grid_[v_id].center_(1);
        pt.z = f_grid_[v_id].center_(2);
        mk.points.emplace_back(pt);
    }
    debug_pub_.publish(mk);
}

void FrontierGrid::Debug(list<Eigen::Vector3d> &pts, int id){
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
    mk.type = visualization_msgs::Marker::SPHERE_LIST;
    mk.scale.x = 0.15;
    mk.scale.y = 0.15;
    mk.scale.z = 0.15;
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

void FrontierGrid::Debug(Eigen::Vector3d &pt, int id){
    visualization_msgs::Marker mk;// mkr1, mkr2;
    mk.header.frame_id = "world";
    mk.header.stamp = ros::Time::now();
    mk.id = id;
    if(id == -3){
        mk.pose.position.z = 0.2;
        mk.color.g = 1.0;
    }
    // else{
    //     mk.color.b = 1.0;
    //     mk.pose.position.z = 0.0;
    // }
    // scan_count_++;
    mk.action = visualization_msgs::Marker::ADD;
    mk.type = visualization_msgs::Marker::CUBE;
    mk.scale.x = 0.3;
    mk.scale.y = 0.3;
    mk.scale.z = 0.3;
    mk.color.a = 1.0;
    mk.color.r = 1.0;
    mk.pose.position.x = pt(0);
    mk.pose.position.y = pt(1);
    mk.pose.position.z = pt(2);
    mk.pose.orientation.x = 0;
    mk.pose.orientation.y = 0;
    mk.pose.orientation.z = 0;
    mk.pose.orientation.w = 1;

    debug_pub_.publish(mk);
}

void FrontierGrid::DebugShowAll(){
    visualization_msgs::Marker mk;
    mk.header.frame_id = "world";
    mk.header.stamp = ros::Time::now();
    mk.id = -1;
    // scan_count_++;
    mk.action = visualization_msgs::Marker::ADD;
    mk.type = visualization_msgs::Marker::CUBE_LIST;
    mk.scale.x = 0.25;
    mk.scale.y = 0.25;
    mk.scale.z = 0.25;
    mk.color.a = 0.3;
    mk.color.b = 1.0;
    mk.pose.position.x = 0;
    mk.pose.position.y = 0;
    mk.pose.position.z = 0;
    mk.pose.orientation.x = 0;
    mk.pose.orientation.y = 0;
    mk.pose.orientation.z = 0;
    mk.pose.orientation.w = 1;
    for(auto &f : f_grid_){
        if(f.f_state_ == 1){
            for(int i = 0; i < samp_num_; i++){
                if(f.local_vps_[i] == 1){
                    Eigen::Vector4d vpt;
                    GetVp(f.center_, i, vpt);
                    geometry_msgs::Point pt;
                    pt.x = vpt(0);
                    pt.y = vpt(1);
                    pt.z = vpt(2);
                    mk.points.emplace_back(pt);
                }
            }
        }
    }
    debug_pub_.publish(mk);
}

void FrontierGrid::DrawFOVs(list<Eigen::Vector4d> &vps){
    visualization_msgs::Marker mk;
    mk.header.frame_id = "world";
    mk.header.stamp = ros::Time::now();
    mk.id = -100;
    // scan_count_++;
    mk.action = visualization_msgs::Marker::ADD;
    mk.type = visualization_msgs::Marker::LINE_LIST;
    mk.scale.x = 0.05;
    mk.scale.y = 0.05;
    mk.scale.z = 0.05;
    mk.color.a = 0.8;
    mk.color.g = 1.0;
    mk.pose.position.x = 0;
    mk.pose.position.y = 0;
    mk.pose.position.z = 0;
    mk.pose.orientation.x = 0;
    mk.pose.orientation.y = 0;
    mk.pose.orientation.z = 0;
    mk.pose.orientation.w = 1;
    for(auto vp : vps){
        LoadVpLines(mk, vp);
    }
    debug_pub_.publish(mk);
}
