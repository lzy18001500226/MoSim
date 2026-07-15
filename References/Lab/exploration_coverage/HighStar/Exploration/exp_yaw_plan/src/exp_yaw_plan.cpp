#include <exp_yaw_plan/exp_yaw_plan.h>

void ExpYawPlan::init(ros::NodeHandle &nh, ros::NodeHandle &nh_private){
    std::string ns = ros::this_node::getName();
    nh_private.param(ns + "/exp_yaw/labda", lambda_, 0.5);
    nh_private.param(ns + "/exp_yaw/MinDt", min_dt_, 1.0);
    nh_private.param(ns + "/exp_yaw/DSampleDir", dsr_, 0.10);
    // nh_private.param(ns + "/exp_yaw/DSampleLength", dd_, 0.07);
    nh_private.param(ns + "/exp_yaw/GainFactor", exp_gf_, 3.0);
    nh_private.param(ns + "/exp_yaw/SampleNumMax", sample_num_max_, 20);
    nh_private.param(ns + "/exp_yaw/StableNumMax", stable_num_max_, 5);
    nh_private.param(ns + "/exp_yaw/PlanTMax", plan_t_max_, 0.005);
    nh_private.param(ns + "/Frontier/cam_hor", FOV_h_, 1.5);
    nh_private.param(ns + "/Frontier/cam_ver", FOV_v_, 0.9);
    nh_private.param(ns + "/block_map/sensor_max_range", sr_, 5.0);
    nh_private.param(ns + "/opt/YawVel", dy_, 2.5);
    nh_private.param(ns + "/opt/YawAcc", ddy_, 2.5);
    nh_private.param(ns + "/exp_yaw/DownResX", node_scale_.x(), 0.4);
    nh_private.param(ns + "/exp_yaw/DownResY", node_scale_.y(), 0.4);
    nh_private.param(ns + "/exp_yaw/DownResZ", node_scale_.z(), 0.4);
    nh_private.param(ns + "/Exp/maxX", mapscale_.x(), 10.0);
    nh_private.param(ns + "/Exp/maxY", mapscale_.y(), 10.0);
    nh_private.param(ns + "/Exp/maxZ", mapscale_.z(), 0.0);
    nh_private.param(ns + "/Exp/minX", origin_.x(), -10.0);
    nh_private.param(ns + "/Exp/minY", origin_.y(), -10.0);
    nh_private.param(ns + "/Exp/minZ", origin_.z(), 0.0);

    mapscale_.x() = ceil((mapscale_.x() - origin_.x())/node_scale_(0)) * node_scale_(0);
    mapscale_.y() = ceil((mapscale_.y() - origin_.y())/node_scale_(1)) * node_scale_(1);
    mapscale_.z() = ceil((mapscale_.z() - origin_.z())/node_scale_(2)) * node_scale_(2);
    double dx = origin_.x() - (floor((origin_.x())/node_scale_(0))) * node_scale_(0);
    double dy = origin_.y() - (floor((origin_.y())/node_scale_(1))) * node_scale_(1);
    double dz = origin_.z() - (floor((origin_.z())/node_scale_(2))) * node_scale_(2);
    origin_.x() -= dx;
    origin_.y() -= dy;
    origin_.z() -= dz;
    voxel_num_.x() = ceil((mapscale_.x())/node_scale_(0));
    voxel_num_.y() = ceil((mapscale_.y())/node_scale_(1));
    voxel_num_.z() = ceil((mapscale_.z())/node_scale_(2));
    v_n_.x() = voxel_num_.x();
    v_n_.y() = voxel_num_.y() * voxel_num_.x();
    v_n_.z() = voxel_num_.z() * voxel_num_.y() * voxel_num_.x();
    map_upbd_ = origin_+mapscale_ - Eigen::Vector3d(1e-4, 1e-4, 1e-4);
    map_lowbd_ = origin_ + Eigen::Vector3d(1e-4, 1e-4, 1e-4);

    FOV_h_ *= 0.8;
    dr_ = dsr_*2;
    dr_ = 2 * M_PI / ceil(2 * M_PI / dr_);
    fov_sample_h_num_ = ceil(2 * M_PI / dr_);
    fov_slice_num_ = floor(FOV_h_ / dr_);
    FOV_h_ = fov_slice_num_ * dr_;
    FOV_v_ *= 0.8;
    eng_ = default_random_engine(rd_());
    // ddy_ *= 0.85;
    cout<<"dr:"<<dr_<<endl;
    dy_ *= 1.0;
    // cout<<"fov_sample_h_num_:"<<fov_sample_h_num_<<endl;
    // cout<<"fov_slice_num_:"<<fov_slice_num_<<endl;
    vis_pub_ = nh.advertise<visualization_msgs::MarkerArray>("/exp_yaw_plan/Vis", 10);
    debug_pub_ = nh.advertise<visualization_msgs::Marker>("/exp_yaw_plan/Debug", 10);
}

bool ExpYawPlan::YawPlan(vector<pair<Eigen::Vector4d, double>> &path_pts, const double &total_t, const double &ys, const double &ye, int Fid){
    double ts0 = ros::WallTime::now().toSec();
    if(!CreateGraphs(total_t, path_pts, ys, ye, Fid)){
        ROS_WARN("create graph failed!");
        return false;
    }
    vector<pair<int, int>> layer_id_ans;
    for(int i = 0; i < path_pts.size(); i++){
        layer_id_ans.emplace_back(i, GetYawIdx(0, path_pts[i].first(3)));
    }
    tr1::unordered_map<int, int> cd;
    vector<bool> check_list;
    vector<double> info_list;
    double gain_motion, gain_exp;
    InitSubModGain(layer_id_ans, cd, info_list, gain_motion, gain_exp, ys, ye);
    int sample_count = 0;
    int stable_count = 0;
    int last_idx = -1, sample_idx;
    double ts = ros::WallTime::now().toSec();
    if(layer_id_ans.size() > 0){
        rand_idx_ = uniform_int_distribution<int>(0, layer_id_ans.size()-1);
        while(1){
            if(sample_count > sample_num_max_ || ros::WallTime::now().toSec() - ts > plan_t_max_ || stable_count > stable_num_max_) break;
            sample_idx = rand_idx_(eng_);
            if(last_idx == sample_idx) continue;
            last_idx = sample_idx;
            sample_count++;
            if(SubModGainSample(layer_id_ans, cd, info_list, check_list, gain_motion, gain_exp, sample_idx, ys, ye)){
                stable_count = 0;
                if(layer_id_ans.size() == 1) break;
            }
            else{
                stable_count++;
            }
        }
    }
    cout<<"Yaw Exp Plan T:"<<ros::WallTime::now().toSec() - ts0<<endl;
    cout<<"sample_count:"<<sample_count<<endl;
    
    SetAnswer(layer_id_ans, cd);
    covered_dict_.clear();
    for(auto &a : ans_){
        if(a.covered_targets_.size() > 0) return true;        
    }
    ROS_WARN("Zero gain");
    return false;
}

void ExpYawPlan::SetAnswer(vector<pair<int, int>> &layer_id_ans, tr1::unordered_map<int, int> &cd){
    ans_.clear();
    Eigen::Vector3d up_exp, do_exp;
    // up_exp = FG_->f_grid_[fid_].up_;
    // do_exp = FG_->f_grid_[fid_].down_;
    for(auto &i : layer_id_ans){
        ans_.push_back(nodes_[i.first][i.second]);
        for(auto j : cd){
            if(j.second == i.first){
                Eigen::Vector3d p = IdtoPos(j.first);
                // Eigen::Vector3d p = LRM_->IdtoPos(j.first);
                // if(p(0) > up_exp(0) || p(1) > up_exp(1) || p(2) > up_exp(2) || p(0) < do_exp(0) || 
                //         p(1) < do_exp(1) || p(2) < do_exp(2)){
                //     ans_.back().covered_unknown_.emplace_back(p);
                // }
                // else ans_.back().covered_key_.emplace_back(p);
                ans_.back().covered_targets_.emplace_back(p);
            }
        }
        // cout<<"layer:"<<i.first<<" id:"<<i.second<<endl;
        // cout<<"node pos:"<<ans_.back().pos_.transpose()<<endl;
    }
}

bool ExpYawPlan::CreateGraphs(double total_t, vector<pair<Eigen::Vector4d, double>> &path_pts, double ys, double ye, int Fid){
    nodes_.clear();
    hash_n_.clear();
    cross_thresh_.clear();
    t_l_.clear();
    fid_ = Fid;
    // ROS_WARN("CreateGraphs0");

    //sample
    // int graph_layer = total_t / min_dt_ - 1;
    // graph_layer = min(graph_layer, 8);
    if(path_pts.size() <= 0 || path_pts.size() >= 30) return false;
    // double next_t = total_t / (graph_layer + 1);
    double last_t = 0.0;
    double dt;
    double dyaw,dyaw2;// yup, ydown;
    double yaw_last = ys;
    // yup = ys;
    // ydown = ys;
    layer_num_ = 0;
    // ROS_WARN("CreateGraphs1");

    // dyaw = CalYdist(path_pts[0].second);
    for(int i = 0; i < path_pts.size(); i++){
        // if(path_pts[i].second > next_t){
        dt = path_pts[i].second - last_t;
        tdm_l_.emplace_back(dt);
        // yup += dyaw;
        // ydown -= dyaw;
        // if(yup - ydown > M_PI * 2){
        //     ydown = 0;
        //     yup = M_PI * 2;
        // }
        // cout<<path_pts.size()<<endl;
        InitNodes(layer_num_, /*yup, ydown,*/ path_pts[i].first.head(3), i, path_pts[i].second);
        dyaw = CalYdist(dt);
        dyaw2 = abs(YawDiff(path_pts[i].first(3), yaw_last));
        // dyaw2 = 0.0;

        yaw_last = path_pts[i].first(3);
        layer_num_++;
        last_t = path_pts[i].second;
        // next_t = path_pts[i].second + total_t / (graph_layer + 1);

        // cross_thresh_.emplace_back(max(dyaw, dyaw2));
        double g = 1.0;
        if(path_pts[i].second < 0.75 || total_t - last_t < 0.75) g = 0.5;
        cross_thresh_.emplace_back(max(dt * dy_ * g, dyaw2));
        // cout<<"cross:"<<cross_thresh_.back()<<"  dt:"<<dt<<" dyaw2:"<<dyaw2<<endl;
        t_l_.emplace_back(path_pts[i].second);
        // }
    }
    // ROS_WARN("CreateGraphs2");

    dt = total_t - last_t;
    tdm_l_.emplace_back(dt);

    dyaw = CalYdist(dt);
    dyaw2 = abs(YawDiff(ye, yaw_last));
    // dyaw2 = 0.0;
    // cross_thresh_.emplace_back(max(dyaw, dyaw2));
    // cross_thresh_.emplace_back(max(dyaw, dyaw2));
    double g = 1.0;
    if(last_t < 0.75 || total_t - last_t < 0.75) g = 0.5;

    cross_thresh_.emplace_back(max(dt * dy_ * g, dyaw2));
    cout<<"cross:"<<cross_thresh_.back()<<"  dt:"<<dt<<" dyaw2:"<<dyaw2<<endl;
    // cross_thresh_.emplace_back(dyaw);

    // eval gain
    gains_.clear();
    gains_.resize(layer_num_);
    double y;
    double fov_h_v = FOV_v_ * 0.5;
    double dsr_h = dsr_ * 0.5;
    Eigen::Vector3d p0, dir, pt, pc;
    VoxelState vs;
    // list<pair<int, double>> el;
    double sin_2_dphi = sin(dsr_ / 2);
    // int hs, he;
    int ynum;
    int hor_idx;
    // double pena, t;
    Eigen::Vector3d up_exp, do_exp, rs, re;
    list<Eigen::Vector3d> line;
    vector<Eigen::Vector3d> debug_pts;
    if(Fid >= 0 && Fid < FG_->f_grid_.size()){
        up_exp = FG_->f_grid_[Fid].up_;
        do_exp = FG_->f_grid_[Fid].down_;
    }
    else{
        up_exp(0) = -1.0;
        do_exp(0) = 1.0;
    }
    // vector<vector<int>> 
    // ROS_WARN("CreateGraphs3");

    for(int i = 0; i < layer_num_; i++){
        // pena = exp(-t_l_[i] * lambda_);
        // yup = nodes_[i].back().pos_(3) + FOV_h_ * 0.5;
        // ydown = nodes_[i].front().pos_(3) - FOV_h_ * 0.5;
        // ynum = fov_slice_num_ + nodes_[i].size() - 1;
        // he = nodes_[i].back().ce_;
        // dyaw = yup - ydown;
        // if(dyaw > M_PI * 2){
        //     // yup = ydown + M_PI * 2;
        //     ynum = ceil(M_PI * 2 / dr_);
        // }
        // ROS_WARN("CreateGraphs3.1");

        p0 = nodes_[i].front().pos_.head(3);
        // ydown += dsr_h;
        gains_[i].resize(fov_sample_h_num_);
        // yup += dsr_h;
        // y = ydown + dsr_h;
        // ROS_WARN("CreateGraphs3.2");

        for(int yi = 0; yi < fov_sample_h_num_; yi++){
            y = (yi + 0.5) * dr_;

            for(double v = -fov_h_v + dsr_h; v < fov_h_v; v += dsr_){
                // ROS_WARN("CreateGraphs3.3");
                double cos_phi = cos(v);
                dir(0) = cos_phi * cos(y);
                dir(1) = cos_phi * sin(y);
                dir(2) = sin(v);
                rs = p0;
                re = p0 + dir * sr_;
                // BM_->GetCastLine()
                // LRM_->GetCastLine(rs, re, line);
                // for(auto &p_low : line){
                //     if(LRM_->IsFeasible(p_low)) {
                //         debug_pts.emplace_back(p_low);
                //         rs = p_low;
                //         continue;
                //     }
                //     else break;
                // }
                BM_->GetCastLine(rs, re, line);
                for(auto p_high : line){
                    // debug_pts.emplace_back(p_high);

                    if(!FG_->InsideMap(p_high)) break;
                    // ROS_WARN("CreateGraphs3.4");

                    vs = BM_->GetVoxState(p_high);
                    if(vs == VoxelState::free){
                        continue;
                    }
                    else if(vs == VoxelState::occupied){
                        break;
                    }
                    else if(vs == VoxelState::unknown){
                        // ROS_WARN("CreateGraphs3.41");
                        int id = PostoId(p_high);
                        // int id = LRM_->PostoId(pt);
                        pt = IdtoPos(id);

                        pc = IdtoPos(id) - p0;
                        // pt = LRM_->IdtoPos(id) - p0;
                        double gain = 1.0;// * pena;//2*dsr_*pow(d, 2)*sin_2_dphi*cos_phi ;
                        if(pt(0) < up_exp(0) && pt(1) < up_exp(1) && pt(2) < up_exp(2) &&
                            pt(0) > do_exp(0) && pt(1) > do_exp(1) && pt(2) > do_exp(2)) gain *= exp_gf_;
                        if(pc.norm() > sr_) break;
                        // ROS_WARN("CreateGraphs3.42");

                        auto h = covered_dict_.find(id);
                        if(h == covered_dict_.end()){
                            // ROS_WARN("CreateGraphs3.43");
                            int f;
                            f = 1 << i;
                            covered_dict_.insert({id, {f, gain}});
                            hor_idx = GetYawIdx(0, atan2(pc(1), pc(0)));
                            gains_[i][hor_idx].push_back({id, gain});
                        }
                        else if(!(h->second.first | (1<<i))){
                            // ROS_WARN("CreateGraphs3.45");
                            h->second.first |= 1 << i;
                            hor_idx = GetYawIdx(0, atan2(pc(1), pc(0)));
                            gains_[i][hor_idx].push_back({id, gain});
                            // ROS_WARN("CreateGraphs3.46");
                        }
                        else{
                            // cout<<"i:"<<i<<"  flag:"<<int(h->second.first )<<endl;
                            // ROS_ERROR("impossible");
                            // getchar();
                        }
                        // ROS_WARN("CreateGraphs3.47");
                        // break;
                    }
                    else {
                        break;
                    }
                    // ROS_WARN("CreateGraphs3.5");
                }
                // Debug(debug_pts);
                // getchar();
            }
        }
    }
    // ROS_WARN("CreateGraphs4");
    return true;
}

bool ExpYawPlan::Search(double ys, double ye, vector<pair<int, int>> &layer_id_ans){
    // cout<<"nodes_.size():"<<nodes_.size()<<endl;
    if(nodes_.size() < 1) return false;

    bool find_ans = false;
    // ans_.clear();
    ;
    priority_queue<shared_ptr<YawSearchNode>, vector<shared_ptr<YawSearchNode>>, YCompare> open_set;
    shared_ptr<YawSearchNode> yns, yne, c_node, r_node, e_node;
    yns = make_shared<YawSearchNode>();
    yne = make_shared<YawSearchNode>();

    yns->id_ = -1;
    yns->parent_ = -1;
    yns->gain_ = 0.0;
    yns->status_ = in_open;
    yns->yaw_ = ys;
    yns->layer_ = -1;
    yne->yaw_ = ye;
    yne->gain_ = 999999.0;
    yne->id_ = 9999999;
    yne->parent_ = -1;
    int layer;
    int layer_max = nodes_.size();
    double dyaw;

    open_set.push(yns);

    while(!open_set.empty()){
        c_node = open_set.top();
        open_set.pop();
        if(c_node->status_ == in_close) continue;/**/
        c_node->status_ = in_close;
        // ROS_WARN("it");
        // cout<<"c layer:"<<c_node->layer_<<endl;

        if(c_node->id_ == 9999999){
            // cout<<"c_node->parent_:"<<c_node->parent_<<endl;
            // cout<<"nodes_.back():"<<nodes_.back().size()<<endl;
            r_node = nodes_.back()[c_node->parent_].ysn_;
            // cout<<"null:"<<(r_node == NULL)<<endl;
            // cout<<"r_node->layer_:"<<r_node->layer_<<endl;
            layer_id_ans.push_back({r_node->layer_, r_node->id_});
            while(r_node->layer_ != 0){

                layer = r_node->layer_ - 1;
                r_node = nodes_[layer][r_node->parent_].ysn_;
                layer_id_ans.push_back({r_node->layer_, r_node->id_});
                // ans_.push_back(nodes_[layer][r_node->parent_]);
            }
            // ROS_WARN("???");
            // layer_id_ans.pop_back(); // pop start pt
            reverse(layer_id_ans.begin(), layer_id_ans.end());
            // reverse(ans_.begin(), ans_.end());
            find_ans = true;
            break;
        }
        // cout<<"c id:"<<c_node->id_<<endl;
        // cout<<"yaw:"<<c_node->yaw_<<endl;
        // cout<<"gain:"<<c_node->gain_<<endl;
        layer = c_node->layer_ + 1;
        if(layer < layer_max){
            // cout<<"cross_thresh_[layer]:"<<cross_thresh_[layer]<<endl;
            for(auto &y : nodes_[layer]){
                dyaw = abs(YawDiff(c_node->yaw_, y.pos_(3)));
                if(dyaw > cross_thresh_[layer]) continue;
                // cout<<"dyaw:"<<dyaw<<endl;
                dyaw *= 0.02;
                e_node = y.ysn_;
                if(e_node == NULL){
                    e_node = make_shared<YawSearchNode>();
                    e_node->gain_ = dyaw + c_node->gain_;
                    e_node->id_ = y.id_;
                    e_node->layer_ = layer;
                    e_node->parent_ = c_node->id_;
                    e_node->status_ = in_open;
                    e_node->yaw_ = y.pos_(3);
                    y.ysn_ = e_node;
                    open_set.push(e_node);
                }
                else{
                    if(e_node->status_ == in_close) continue;
                    double g_tmp = c_node->gain_ + dyaw + 1e-4;
                    if(e_node->gain_ > g_tmp){
                        e_node->status_ = in_close;
                        e_node = make_shared<YawSearchNode>();
                        y.ysn_ = e_node;
                        e_node->gain_ = dyaw + c_node->gain_;
                        e_node->id_ = y.id_;
                        e_node->layer_ = layer;
                        e_node->parent_ = c_node->id_;
                        e_node->status_ = in_open;
                        e_node->yaw_ = y.pos_(3);
                        open_set.push(e_node);
                    }
                }
            }
        }
        else{
            dyaw = abs(YawDiff(c_node->yaw_, ye));
            // cout<<"dyaw:"<<dyaw<<endl;
            // cout<<"end th:"<<cross_thresh_[layer]<<endl;
            if(dyaw > cross_thresh_[layer]) continue;
            dyaw *= 0.02;

            double g_tmp = c_node->gain_ + dyaw + 1e-4;
            if(yne->gain_ > g_tmp){
                yne->status_ = in_close;
                yne = make_shared<YawSearchNode>();
                yne->gain_ = dyaw + c_node->gain_;
                yne->id_ = 9999999;
                yne->layer_ = layer;
                yne->parent_ = c_node->id_;
                yne->status_ = in_open;
                yne->yaw_ = ye;
                open_set.push(yne);
            }
        }
    }

    if(!find_ans) return false;
    return true;
}

void ExpYawPlan::InitSubModGain(vector<pair<int, int>> &layer_id_ans, tr1::unordered_map<int, int> &cd, vector<double> &info_list,
                                    double &gain_motion, double &gain_exp, double ys, double ye){
    int y_min_idx, y_max_idx, layer, id;
    int hnum = FOV_v_ / dsr_;
    double g;
    double yaws = ys;
    gain_motion = 0;
    gain_exp = 0;
    list<int> cl;

    vector<double> yl, pl;
    yl.emplace_back(ys);
    for(auto &ans : layer_id_ans){
        yl.emplace_back(nodes_[ans.first][ans.second].pos_(3));
    }
    yl.emplace_back(ye);
    GetTimePenalties(yl, pl);

    for(auto &li : layer_id_ans){
        layer = li.first;
        id = li.second;
        y_min_idx = id;
        y_max_idx = id + hnum;
        g = 0;
        GetCoverIds(nodes_[layer][id].pos_(3), cl);
        for(auto &i : cl){
            for(auto &p : gains_[layer][i]){
                auto h = cd.find(p.first);
                if(h == cd.end()){
                    cd.insert({p.first, layer});
                    g += p.second;
                }
            }
        }
        info_list.emplace_back(g);
        gain_exp += pl[layer] * g;
        gain_motion -= abs(YawDiff(yaws, nodes_[layer][id].pos_(3)))*0.02;
        yaws = nodes_[layer][id].pos_(3);
    }
    gain_motion -= abs(YawDiff(ye, yaws))*0.02;
}



// bool ExpYawPlan::SubModGainIter(vector<pair<int, int>> &layer_id_ans, tr1::unordered_map<int, uint8_t> &cd, 
                                    // vector<bool> &check_list, double &gain_motion, double &gain_exp, double ys, double ye){
    // double ydif1, ydif2;
//     double y1, y2, y3;
//     // double y_fov_s, y_fov_e;
//     double yns, y;
//     int hash_id, cur_yaw_id, layer_n;
//     vector<pair<int, int>> temp_ans;
//     vector<int> de_sl, ad_sl;
//     tr1::unordered_map<int, uint8_t>::iterator cit;
//     double dg;

//     for(int i = 0; i < nodes_.size(); i++){
//         temp_ans = layer_id_ans;
//         if(i == 0) y1 = ys;
//         else y1 = nodes_[i - 1][temp_ans[i - 1].first].pos_(3);

//         if(i + 1 == nodes_.size()) y3 = ye;
//         else y3 = nodes_[i + 1][temp_ans[i + 1].first].pos_(3);

//         yns = nodes_[i].front().pos_(3) - FOV_h_ * 0.5 + 1e-3;
//         cur_yaw_id = temp_ans[i].second;

//         // y_fov_s = nodes_[i][cur_yaw_id].pos_(0) - FOV_h_ * 0.5 + 1e-3;
//         // y_fov_e = nodes_[i][cur_yaw_id].pos_(0) + FOV_h_ * 0.5 - 1e-3;
//         // covered_slices.clear();
//         // for(double y = y_fov_s; y < y_fov_e; y += dr_){
//         //     int y_id = GetYawIdx(yns, y);
//         //     if(y_id >= gains_[i].size() || y_id < 0){
//         //         ROS_ERROR("error y_id! %d, %lf, %lf, %ld", y_id, yns, y, gains_[i].size());
//         //         ros::shutdown();
//         //     }
//         //     covered_slices.push_back(y_id);
//         // }

//         // cur_slices
//         layer_n = gains_[i].size();
//         for(int idx = 0; idx < nodes_[i].size(); idx++){
//             temp_ans[i].second = idx;
//             hash_id = GetHash(temp_ans);
//             if(check_list[hash_id]) continue;
//             ydif1 = abs(YawDiff(y1, y2));
//             ydif2 = abs(YawDiff(y2, y3));
//             if(ydif1 > cross_thresh_[i] || ydif2 > cross_thresh_[i]) continue;
//             GetSliceDiff(cur_yaw_id, idx, layer_n, de_sl, ad_sl);

//             dg = 0.0;
//             for(auto &de : de_sl){

//                 for(auto &g : gains_[i][de]){
//                     // cit = cd.find(de);
//                     // if(cit == cd.end()){
//                     //     ROS_ERROR("how ??? error de cd dict!");
//                     // }
//                     // dg -= g.second;
//                 }

//             }


        
//         }
        


//     }
// }

bool ExpYawPlan::SubModGainSample(vector<pair<int, int>> &layer_id_ans, tr1::unordered_map<int, int> &cd, vector<double> &info_list,
    vector<bool> &check_list, double &gain_motion, double &gain_exp, int s_idx, double ys, double ye){
    double y0, y1, y2, dyaw, motion_cost;
    int c_id = layer_id_ans[s_idx].second;

    if(s_idx == 0) y0 = ys;
    else y0 = nodes_[s_idx - 1][layer_id_ans[s_idx - 1].second].pos_(3);

    y1 = nodes_[s_idx][layer_id_ans[s_idx].second].pos_(3);
    if(s_idx + 1 == layer_id_ans.size()) y2 = ye;
    else y2 = nodes_[s_idx + 1][layer_id_ans[s_idx + 1].second].pos_(3);

    // vector<pair<int, int>> 
    vector<int> candidates;
    for(int i = 0; i < nodes_[s_idx].size(); i++){
        if(i == c_id) continue;
        auto &n = nodes_[s_idx][i];
        motion_cost = 0.0;

        dyaw = abs(YawDiff(n.pos_(3), y2));
        if(dyaw > cross_thresh_[s_idx]) continue;
        dyaw = abs(YawDiff(n.pos_(3), y1));
        if(dyaw > cross_thresh_[s_idx]) continue;
        candidates.emplace_back(i);
    }

    vector<int> slice_delete, slice_add;
    // vector<int> delete_lists, add_lists;
    // vector<pair<int, int>> change_lists;
    vector<vector<int>> add_L, delete_L;
    vector<vector<pair<int, int>>> change_L; //key, change to
    vector<Eigen::Vector3d> debug_list;
    vector<double> pl, yl;
    int layer_n = nodes_.size(), best_id = c_id;
    vector<double> info_list_cur, info_list_best;
    // double gain_best = gain_motion + gain_exp;
    double cover_gain_cur, motion_gain_cur;
    double cover_gain_cur_best = gain_exp, motion_gain_cur_best = gain_motion;
    // double gain_c = 0, best_c = 0;
    // double gain_m = 0, best_m = -0.2 * (abs(YawDiff(y0, y1)) + abs(YawDiff(y1, y2)));
    // double pena = exp(-lambda_ * t_l_[s_idx]);
    int slice_id;
    Eigen::Vector3d tar;
    double y;
    int it_id = -1, best_it;
    add_L.resize(candidates.size());
    delete_L.resize(candidates.size());
    change_L.resize(candidates.size());

    yl.emplace_back(ys);
    for(auto &ans : layer_id_ans){
        yl.emplace_back(nodes_[ans.first][ans.second].pos_(3));
    }
    yl.emplace_back(ye);

    for(auto &v : candidates){
        it_id++;
        // gain_c = 0;
        // gain_m = 0;
        info_list_cur = info_list;
        yl[s_idx] = nodes_[s_idx][v].pos_(3);
        GetTimePenalties(yl, pl);
        GetSliceDiff(v, c_id, s_idx, slice_delete, slice_add);
        // delete_lists.clear();
        y = nodes_[s_idx][v].pos_(3);

        // DrawFov(nodes_[s_idx][v].pos_);
        // ROS_WARN("draw fov");

        // gain_m = -0.2 * (abs(YawDiff(y0, y)) + abs(YawDiff(y, y2)));
        // cout<<"it_id:"<<it_id<<"  d:"<<slice_delete.size()<<endl;
        for(auto &d : slice_delete){
            for(auto &p : gains_[s_idx][d]){
                auto cd_i = cd.find(p.first);               // covered pt in current sequence
                auto cp_i = covered_dict_.find(p.first);    // covered point
                tar = IdtoPos(p.first);
                debug_list.emplace_back(tar);
                debug_list.back().z() += 0.2;
                // tar = LRM_->IdtoPos(p.first);

                if(cd_i == cd.end()){ //debug
                    double yd = y - dr_ * floor(fov_slice_num_ / 2);
                    double yu = yd + dr_ * fov_slice_num_;
                    y = atan2(tar(1) - nodes_[s_idx].front().pos_(1), tar(0) - nodes_[s_idx].front().pos_(0));
                    if(yd < y && y < yu) cout<<"ok!"<<endl;
                    ROS_ERROR("error d idx");
                    ros::shutdown();
                }
                else{
                    if(cp_i == covered_dict_.end()){ //debug
                        ROS_ERROR("error d cp idx");
                        ros::shutdown();
                    }
                    if(cd_i->second < s_idx) {
                        // ROS_WARN("???????");
                        continue;
                    }
                    if(cd_i->second > s_idx) { //debug
                        cout<<"cd_i->second:"<<cd_i->second <<" s_idx:"<<s_idx<<endl;
                        ROS_ERROR("error > s_idx");
                        getchar();
                        ros::shutdown();
                    }

                    bool delete_g = true;
                    for(int i = s_idx + 1; i < layer_n; i++){ //delete in submo way
                        y = atan2(tar(1) - nodes_[i].front().pos_(1), tar(0) - nodes_[i].front().pos_(0));
                        // slice_id = floor((y - nodes_[i].front().pos_(3) + FOV_h_ * 0.5) / dr_);
                        slice_id = GetYawIdx(0, y);
                        if(cp_i->second.first & (1 << i) && CoverSlice(i, layer_id_ans[i].second, slice_id)) { // find later cover fov
                            info_list_cur[s_idx] -= cp_i->second.second;
                            info_list_cur[i] += cp_i->second.second;
                            // gain_c -= pena * cp_i->second.second;
                            // gain_c += exp(-lambda_ * t_l_[i]) * cp_i->second.second;

                            delete_g = false;
                            cd_i->second = i;
                            change_L[it_id].push_back({p.first, i});
                            break;
                        }
                    }
                    if(delete_g) {
                        info_list_cur[s_idx] -= cp_i->second.second;
                        // gain_c -= pena * cp_i->second.second;
                        delete_L[it_id].emplace_back(p.first);
                        // delete_lists.emplace_back(p.first);
                    }
                }
            }
        }

        for(auto &a : slice_add){
            for(auto &p : gains_[s_idx][a]){
                auto cd_i = cd.find(p.first);               // covered pt in current sequence
                auto cp_i = covered_dict_.find(p.first);    // covered point
                tar = IdtoPos(p.first);
                // tar = LRM_->IdtoPos(p.first);
                debug_list.emplace_back(tar);
                debug_list.back().z() += 0.2;

                if(cd_i == cd.end()){ //debug
                    info_list_cur[s_idx] += cp_i->second.second;
                    // gain_c += pena * cp_i->second.second;
                    add_L[it_id].emplace_back(p.first);
                    // add_lists.emplace_back(p.first);
                }
                else{
                    if(cp_i == covered_dict_.end()){ //debug
                        ROS_ERROR("error d cp idx");
                        ros::shutdown();
                    }

                    if(cd_i->second < s_idx) continue;
                    info_list_cur[s_idx] += cp_i->second.second;
                    info_list_cur[cd_i->second] -= cp_i->second.second;

                    // gain_c += pena * cp_i->second.second;
                    // gain_c -= exp(-lambda_ * t_l_[cd_i->second]) * cp_i->second.second;
                    cd_i->second = s_idx;
                    change_L[it_id].push_back({p.first, s_idx});
                }
            }
        }

        cover_gain_cur = 0;
        motion_gain_cur = 0;
        for(int i = 0; i < layer_id_ans.size() + 1; i++){
            motion_gain_cur -= 0.02*abs(YawDiff(yl[i], yl[i + 1]));
        }
        for(int i = 0; i < info_list_cur.size(); i++){
            cover_gain_cur += info_list_cur[i] * pl[i];
        }

        if(cover_gain_cur + motion_gain_cur > cover_gain_cur_best + motion_gain_cur_best){
            cover_gain_cur_best = cover_gain_cur;
            motion_gain_cur_best = motion_gain_cur;
            best_id = v;
            best_it = it_id;
        }
    }

    if(best_id != c_id){
        // cout<<"best_it:"<<best_it<<endl;
        for(auto &d : delete_L[best_it]) cd.erase(d);
        for(auto &a : add_L[best_it]) cd.insert({a, s_idx});
        // cout<<"delet num:"<<delete_L[best_it].size()<<endl;
        for(auto &c : change_L[best_it]) {
            auto cd_it = cd.find(c.first);
            cd_it->second = c.second;
        }
        // for(auto &a : add_lists) cd.insert({a, s_idx});
        // for(auto &d : delete_lists) cd.erase(d);
    }
    gain_exp = cover_gain_cur_best;
    gain_motion = motion_gain_cur_best;
    layer_id_ans[s_idx].second = best_id;
    if(best_id == c_id) return false;
    else return true;
}

void ExpYawPlan::SampleTimes(double &total, vector<double> &tl, const double &ys, const double &ye){
    tl.clear();
    if(total < min_dt_ * 2) return;
    int sample_seg_num = min(floor(total / min_dt_), 9.0);
    int sample_pt_num = sample_seg_num - 1;
    double dt = total / sample_seg_num;
    // cout<<"ym:"<<sample_seg_num * CalYdist(dt)<<endl;
    // cout<<"dy:"<<YawDiff(ys, ye)<<endl;
    if(sample_seg_num * CalYdist(dt) < abs(YawDiff(ys, ye))) return;
    for(double i = 0; i < sample_pt_num; i++) tl.push_back((i + 1) * dt);
}

void ExpYawPlan::FovShow(){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(7); // fov circle, large fov, fov center, pts, tar pts, pts lines, tar box
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = 0;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::LINE_LIST;
    mka.markers[0].scale.x = 0.07;
    mka.markers[0].scale.y = 0.07;
    mka.markers[0].scale.z = 0.07;
    mka.markers[0].color.a = 0.6;
    mka.markers[0].color.r = 0.5;
    mka.markers[0].color.g = 0.5;
    mka.markers[0].color.b = 0.5;
    // mka.markers[0].lifetime = ros::Duration(3.0);

    mka.markers[1] = mka.markers[0];
    mka.markers[1].id = 1;
    mka.markers[1].scale.x = 0.1;
    mka.markers[1].scale.y = 0.1;
    mka.markers[1].scale.z = 0.1;
    mka.markers[1].color.a = 1.0;
    mka.markers[1].color.r = 0.3;
    mka.markers[1].color.g = 0.9;
    mka.markers[1].color.b = 0.2;

    mka.markers[2] = mka.markers[0];
    mka.markers[2].type = visualization_msgs::Marker::SPHERE_LIST;
    mka.markers[2].id = 2;
    mka.markers[2].scale.x = 0.15;
    mka.markers[2].scale.y = 0.15;
    mka.markers[2].scale.z = 0.15;
    mka.markers[2].color.a = 0.3;
    mka.markers[2].color.r = 1.0;
    mka.markers[2].color.g = 0.3;
    mka.markers[2].color.b = 0.4;

    mka.markers[3] = mka.markers[2];
    mka.markers[3].id = 3;
    mka.markers[3].scale.x = 0.25;
    mka.markers[3].scale.y = 0.25;
    mka.markers[3].scale.z = 0.25;
    mka.markers[3].color.a = 0.3;
    mka.markers[3].color.r = 0.2;
    mka.markers[3].color.g = 0.8;
    mka.markers[3].color.b = 0.8;

    mka.markers[4] = mka.markers[2];
    mka.markers[4].id = 4;
    mka.markers[4].color.a = 1.0;
    mka.markers[4].color.r = 0.8;
    mka.markers[4].color.g = 0.8;
    mka.markers[4].color.b = 0.2;

    mka.markers[5] = mka.markers[0];
    mka.markers[5].id = 5;
    mka.markers[5].scale.x = 0.03;
    mka.markers[5].scale.y = 0.03;
    mka.markers[5].scale.z = 0.03;
    mka.markers[5].color.a = 1.0;
    mka.markers[5].color.r = 0.3;
    mka.markers[5].color.g = 0.6;
    mka.markers[5].color.b = 0.2;

    // mka.markers[6] = mka.markers[0];
    // mka.markers[6].id = 6;
    // mka.markers[6].type = visualization_msgs::Marker::CUBE;
    // mka.markers[6].color.a = 0.5;
    // mka.markers[6].color.r = 0.9;
    // mka.markers[6].color.g = 0.6;
    // mka.markers[6].color.b = 0.2;
    // mka.markers[6].pose.position.x = FG_->f_grid_[fid_].center_(0);
    // mka.markers[6].pose.position.y = FG_->f_grid_[fid_].center_(1);
    // mka.markers[6].pose.position.z = FG_->f_grid_[fid_].center_(2);
    // mka.markers[6].scale.x = FG_->f_grid_[fid_].up_(0) - FG_->f_grid_[fid_].down_(0);
    // mka.markers[6].scale.y = FG_->f_grid_[fid_].up_(1) - FG_->f_grid_[fid_].down_(1);
    // mka.markers[6].scale.z = FG_->f_grid_[fid_].up_(2) - FG_->f_grid_[fid_].down_(2);

    geometry_msgs::Point pt1, pt2, pt3, pt4, pt5;
    double y, cy, sy, cv, sv;

    cv = cos(FOV_v_ / 2);
    sv = sin(FOV_v_ / 2);
    for(int i = 0; i < ans_.size(); i++){
        //0
        for(int j = 0; j < fov_sample_h_num_; j++){
            y = j * dr_;
            cy = cos(y);
            sy = sin(y);
            pt1.x = ans_[i].pos_(0);
            pt1.y = ans_[i].pos_(1);
            pt1.z = ans_[i].pos_(2);
            mka.markers[0].points.emplace_back(pt1);
            pt2.x = pt1.x + cv*cy*0.3;
            pt2.y = pt1.y + cv*sy*0.3;
            pt2.z = pt1.z + sv*0.3;
            mka.markers[0].points.emplace_back(pt2);

            mka.markers[0].points.emplace_back(pt2);
            pt2.z = pt1.z - sv*0.3;
            mka.markers[0].points.emplace_back(pt2);

            mka.markers[0].points.emplace_back(pt2);
            mka.markers[0].points.emplace_back(pt1);
        }

        //1
        int ys = GetYawIdx(0, ans_[i].pos_(3)) - floor(fov_slice_num_ / 2);
        int ye = ys + fov_slice_num_;
        y = ys * dr_;
        sy = sin(y);
        cy = cos(y);
        pt1.x = ans_[i].pos_(0);
        pt1.y = ans_[i].pos_(1);
        pt1.z = ans_[i].pos_(2);
        pt2.x = pt1.x + 1.0 * cv * cy;
        pt2.y = pt1.y + 1.0 * cv * sy;
        pt2.z = pt1.z + 1.0 * sv;
        pt3.x = pt2.x;
        pt3.y = pt2.y;
        pt3.z = pt1.z - 1.0 * sv;
        y = ye * dr_;
        sy = sin(y);
        cy = cos(y);
        pt4.x = pt1.x + 1.0 * cv * cy;
        pt4.y = pt1.y + 1.0 * cv * sy;
        pt4.z = pt1.z + 1.0 * sv;
        pt5.x = pt4.x;
        pt5.y = pt4.y;
        pt5.z = pt1.z - 1.0 * sv;
        mka.markers[1].points.emplace_back(pt2);
        mka.markers[1].points.emplace_back(pt1);
        mka.markers[1].points.emplace_back(pt3);
        mka.markers[1].points.emplace_back(pt1);
        mka.markers[1].points.emplace_back(pt4);
        mka.markers[1].points.emplace_back(pt1);
        mka.markers[1].points.emplace_back(pt5);
        mka.markers[1].points.emplace_back(pt1);
        mka.markers[1].points.emplace_back(pt2);
        mka.markers[1].points.emplace_back(pt3);
        mka.markers[1].points.emplace_back(pt3);
        mka.markers[1].points.emplace_back(pt5);
        mka.markers[1].points.emplace_back(pt5);
        mka.markers[1].points.emplace_back(pt4);
        mka.markers[1].points.emplace_back(pt4);
        mka.markers[1].points.emplace_back(pt2);

        //2
        y = ans_[i].pos_(3);
        sy = sin(y);
        cy = cos(y);
        pt2.x = ans_[i].pos_(0) + 2.0 * cy;
        pt2.y = ans_[i].pos_(1) + 2.0 * sy;
        pt2.z = ans_[i].pos_(2);
        mka.markers[2].points.emplace_back(pt2);
    }

    //3
    Eigen::Vector3d cpt;
    for(auto &cp : covered_dict_){
        cpt = IdtoPos(cp.first);
        // cpt = LRM_->IdtoPos(cp.first);
        pt1.x = cpt(0);
        pt1.y = cpt(1);
        pt1.z = cpt(2);
        mka.markers[3].points.emplace_back(pt1);
    }

    //4
    // Eigen::Vector3d fu, fd, tpt, p0;
    // fu = FG_->f_grid_[fid_].up_;
    // fd = FG_->f_grid_[fid_].down_;
    // p0 = fd + Eigen::Vector3d::Ones() * 1e-3;
    // for(cpt(0) = p0(0); cpt(0) < fu(0); cpt(0) += node_scale_(0)){
    //     for(cpt(1) = p0(1); cpt(1) < fu(1); cpt(1) += node_scale_(1)){
    //         for(cpt(2) = p0(2); cpt(2) < fu(2); cpt(2) += node_scale_(2)){
    //             int id = PostoId(cpt);
    //             if(covered_dict_.find(id) == covered_dict_.end()) continue;
    //             tpt = GetStdPos(cpt);
    //             // tpt = cpt;

    //             // tpt = LRM_->GetStdPos(cpt);
    //             pt1.x = tpt(0);
    //             pt1.y = tpt(1);
    //             pt1.z = tpt(2);
    //             mka.markers[4].points.emplace_back(pt1);
    //         }
    //     }
    // }

    //5
    // for(int i = 0; i < ans_.size(); i++){
    //     y = ans_[i].pos_(3);
    //     sy = sin(y);
    //     cy = cos(y);
    //     pt1.x = ans_[i].pos_(0) + 2.0 * cy;
    //     pt1.y = ans_[i].pos_(1) + 2.0 * sy;
    //     pt1.z = ans_[i].pos_(2);

    //     for(auto &j : ans_[i].covered_key_){
    //         // cpt = IdtoPos(j);
    //         // // cpt = LRM_->IdtoPos(j);
    //         // pt2.x = cpt(0);
    //         // pt2.y = cpt(1);
    //         // pt2.z = cpt(2);
    //         pt2.x = j(0);
    //         pt2.y = j(1);
    //         pt2.z = j(2);
    //         mka.markers[5].points.emplace_back(pt1);
    //         mka.markers[5].points.emplace_back(pt2);
    //     }

    //     for(auto &j : ans_[i].covered_unknown_){
    //         // cpt = IdtoPos(j);
    //         // // cpt = LRM_->IdtoPos(j);
    //         // pt2.x = cpt(0);
    //         // pt2.y = cpt(1);
    //         // pt2.z = cpt(2);
    //         pt2.x = j(0);
    //         pt2.y = j(1);
    //         pt2.z = j(2);
    //         mka.markers[5].points.emplace_back(pt1);
    //         mka.markers[5].points.emplace_back(pt2);
    //     }
    // }
    vis_pub_.publish(mka);
}

void ExpYawPlan::FovClearShow(){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(6); // fov circle, large fov, fov center, pts, tar pts, pts lines
    for(auto &m : mka.markers) m.action = visualization_msgs::Marker::DELETE;
    vis_pub_.publish(mka);
}

void ExpYawPlan::Debug(vector<Eigen::Vector3d> &pts){
    visualization_msgs::Marker mk;
    
    mk.header.frame_id = "world";
    mk.header.stamp = ros::Time::now();
    mk.id = 0;
    mk.action = visualization_msgs::Marker::ADD;
    mk.type = visualization_msgs::Marker::POINTS;
    mk.scale.x = 0.15;
    mk.scale.y = 0.15;
    mk.scale.z = 0.15;
    mk.color.a = 0.6;
    mk.color.r = 1.0;
    geometry_msgs::Point pt;
    for(auto &p : pts){
        pt.x = p(0);
        pt.y = p(1);
        pt.z = p(2);
        mk.points.emplace_back(pt);
    }
    debug_pub_.publish(mk);
}

void ExpYawPlan::DrawFov(Eigen::Vector4d &pose){
    visualization_msgs::Marker mk;
    
    mk.header.frame_id = "world";
    mk.header.stamp = ros::Time::now();
    mk.id = 1;
    mk.action = visualization_msgs::Marker::ADD;
    mk.type = visualization_msgs::Marker::LINE_LIST;
    mk.scale.x = 0.04;
    mk.scale.y = 0.04;
    mk.scale.z = 0.04;
    mk.color.a = 0.6;
    mk.color.r = 1.0;
    double y, cy, sy, cv, sv;

    cv = cos(FOV_v_ / 2);
    sv = sin(FOV_v_ / 2);

    geometry_msgs::Point pt1, pt2, pt3, pt4, pt5;
    int ys = GetYawIdx(0, pose(3)) - floor(fov_slice_num_ / 2);
    int ye = ys + fov_slice_num_;
    y = ys * dr_;
    sy = sin(y);
    cy = cos(y);
    pt1.x = pose(0);
    pt1.y = pose(1);
    pt1.z = pose(2);
    pt2.x = pt1.x + 1.0 * cv * cy;
    pt2.y = pt1.y + 1.0 * cv * sy;
    pt2.z = pt1.z + 1.0 * sv;
    pt3.x = pt2.x;
    pt3.y = pt2.y;
    pt3.z = pt1.z - 1.0 * sv;
    y = ye * dr_;
    sy = sin(y);
    cy = cos(y);
    pt4.x = pt1.x + 1.0 * cv * cy;
    pt4.y = pt1.y + 1.0 * cv * sy;
    pt4.z = pt1.z + 1.0 * sv;
    pt5.x = pt4.x;
    pt5.y = pt4.y;
    pt5.z = pt1.z - 1.0 * sv;
    mk.points.emplace_back(pt2);
    mk.points.emplace_back(pt1);
    mk.points.emplace_back(pt3);
    mk.points.emplace_back(pt1);
    mk.points.emplace_back(pt4);
    mk.points.emplace_back(pt1);
    mk.points.emplace_back(pt5);
    mk.points.emplace_back(pt1);
    mk.points.emplace_back(pt2);
    mk.points.emplace_back(pt3);
    mk.points.emplace_back(pt3);
    mk.points.emplace_back(pt5);
    mk.points.emplace_back(pt5);
    mk.points.emplace_back(pt4);
    mk.points.emplace_back(pt4);
    mk.points.emplace_back(pt2);
    debug_pub_.publish(mk);
}