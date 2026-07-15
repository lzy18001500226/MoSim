#include <mp_planner/mp_planner_quick.h>

void FastMotion::init(ros::NodeHandle &nh, ros::NodeHandle &nh_private){
    std::string ns = ros::this_node::getName();
    nh_private.param(ns + "/opt/MaxVel", 
        max_v_, 5.0);
    nh_private.param(ns + "/opt/MaxAcc", 
        max_a_, 9.0);
    nh_private.param(ns + "/MotionQ/VelNum", 
        vel_num_, 3);
    nh_private.param(ns + "/MotionQ/AccNum", 
        acc_num_, 3);
    nh_private.param(ns + "/MotionQ/Dt", 
        dt_, 0.5);
    nh_private.param(ns + "/MotionQ/VisMotion", 
        vis_motion_, false);
    // nh_private.param(ns + "/MotionQ/AngleNum", 
    //     dir_num_, 6);
    nh_private.param(ns + "/MotionQ/SampleDepth", 
        sample_depth_, 3);
    // nh_private.param(ns + "/MotionQ/VelFactor", 
    //     vel_fac_, 0.35);
    

    max_a_ /= sqrt(3) * 0.9;
    max_v_ /= sqrt(3);

    debug_pub_ = nh.advertise<visualization_msgs::MarkerArray>("MotionQ/debug", 100);
    debug_pub2_ = nh.advertise<nav_msgs::Odometry>("MotionQ/pose", 100);

    dv_ = max_v_ / (vel_num_ - 0.5);
    da_ = max_a_ / (acc_num_ - 0.5);
    // dpsi_ = M_PI / (dir_num_-1);
    acc_num3_ = Eigen::Vector3i::Ones() * (acc_num_ * 2 - 1);
    // acc_num3_(2) = acc_num_;
    acc_max_ = Eigen::Vector3d(da_*(acc_num_ - 0.5)-1e-5, da_*(acc_num_ - 0.5)-1e-5, da_*(acc_num_ - 0.5)-1e-5);
    origin_a_ = Eigen::Vector3d(-da_*(acc_num_ - 0.5),-da_*(acc_num_ - 0.5), -da_*(acc_num_ - 0.5));

    cout<<"dv:"<<dv_<<endl;
    cout<<"da:"<<da_<<endl;
    // cout<<"dpsi_:"<<dpsi_<<endl;
    cout<<"acc_num3_:"<<acc_num3_.transpose()<<endl;
    cout<<"origin_a_:"<<origin_a_.transpose()<<endl;
    cout<<"acc_max_:"<<acc_max_.transpose()<<endl;

    Eigen::Vector3d inp_samp;
    for(int z = 0; z < acc_num3_(2); z++){
        inp_samp(2) = (z - (acc_num_ - 1)) * da_;
        for(int y = 0; y < acc_num3_(1); y++){
            inp_samp(1) = (y - (acc_num_ - 1)) * da_;
            for(int x = 0; x < acc_num3_(0); x++){
                inp_samp(0) = (x - (acc_num_ - 1)) * da_;
                // cout<<"inp_samp:"<<inp_samp.transpose()<<endl;
                acc_samp_.emplace_back(inp_samp);
            }
        }
    }

    // kdTrees_.resize((vel_num_ + acc_num_ - 1) + (vel_num_ - 1) * (acc_num_ - 1) * dir_num_);
    // // cout<<"vel_num_:"<<vel_num_<<endl;
    // // cout<<"acc_num_:"<<acc_num_<<endl;
    // // cout<<"dir_num_:"<<dir_num_<<endl;
    // int AtD = (acc_num_ - 1) * (dir_num_ - 1);
    // double psi;
    // for(int i = 0; i < kdTrees_.size(); i++){
    //     kdTrees_[i] = kd_create(3);
    //     motions_.push_back({});
    //     if(i < vel_num_ + acc_num_ - 1){
    //         if(i < acc_num_){
    //             vids_.emplace_back(0);
    //             aids_.emplace_back(i);
    //             dids_.emplace_back(0);
    //             vas_.push_back({0.0, Eigen::Vector3d(da_*i, 0.0, 0.0)});
    //         }
    //         else{
    //             vids_.emplace_back(i-acc_num_+1);
    //             aids_.emplace_back(0);
    //             dids_.emplace_back(0);
    //             vas_.push_back({(i-acc_num_+1) * dv_, Eigen::Vector3d(0.0, 0.0, 0.0)});
    //         }
    //         psi = 0;
    //         cout<<"vid:"<<vids_.back()<<endl;
    //         cout<<"aid:"<<aids_.back()<<endl;
    //         cout<<"did:"<<dids_.back()<<endl;
    //     }
    //     else{
    //         int j = i - (vel_num_ + acc_num_ - 1);
    //         int vid, aid, did;
    //         did = j % dir_num_;
    //         aid = ((j - did) / dir_num_) % (acc_num_ - 1);
    //         vid = ((j - did) - aid*dir_num_) / dir_num_ / (acc_num_ - 1); 
    //         Eigen::Vector3d a((aid + 1) * da_, 0.0, 0.0);
    //         double v = (vid+1) * dv_;
    //         psi = dpsi_ * (did);
    //         a(1) = a(0) * sin(psi);
    //         a(0) = a(0) * cos(psi);
    //         vas_.push_back({v, a});
    //         vids_.emplace_back(vid+1);
    //         aids_.emplace_back(aid+1);
    //         dids_.emplace_back(did);
    //         cout<<"psi:"<<psi<<endl;
    //         cout<<"vid:"<<vid+1<<endl;
    //         cout<<"aid:"<<aid+1<<endl;
    //         cout<<"did:"<<did<<endl;
    //     }
    //     // cout<<"init"<<endl;
    //     cout<<"vas_.back().first:"<<vas_.back().first<<" vas_.back().second:"<<vas_.back().second.transpose()<<endl;

    //     SampleInit(i, vas_.back().first, vas_.back().second.norm(), psi);
    //     cout<<"id:"<<i<<" size:"<<motions_.back().size()<<endl;
    // }

}

void FastMotion::InitMotion(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as, 
        double &max_t, list<int> &covered_nodes, vector<MotionStateF> &MSl){
    int sample_layer = 0;
    max_t = dt_ * sample_depth_;
    vector<int> eidl, nidl;
    list<pair<int, double>> traj_ids;

    MSl.clear();
    MSl.resize(1);
    if(!LRM_->IsFeasible(ps)) return;
    int ps_id = LRM_->PostoId(ps);
    eidl.resize(1);
    eidl[0] = 0;
    MSl[0].p_ = ps;
    MSl[0].v_ = vs;
    if(MSl[0].v_.norm() + dt_ * da_ > max_v_)  MSl[0].v_ = vs.normalized() * (max_v_ - dt_ * da_ - 1e-3);

    MSl[0].a_ = as;
    if(MSl[0].a_.norm() > max_a_)  MSl[0].a_ = as.normalized() * max_a_;

    MSl[0].id_ = 0;
    MSl[0].parent_id_ = -1;
    MSl[0].path_.emplace_back(ps_id);
    MSl[0].layer_ = 0;    
    traj_ids.push_back({ps_id, 0.0});
    SetTrajCost(traj_ids, covered_nodes, 0, 0); // initial cost

    shared_ptr<LR_node> lr_node;
    Eigen::Vector3d inp, da, pp, pv, pa;
    Eigen::Matrix3d param;
    list<Eigen::Vector3d> inpts;
    list<int> end_motion_ids;
    int cid;
    MotionStateF ms;
    bool inp_val;
    bool end_motion;

    while(sample_layer < sample_depth_){
        sample_layer++;
        while(!eidl.empty()){
            end_motion = true;
            int mit = eidl.back();
            eidl.pop_back();
            inpts.clear();
            pp = MSl[mit].p_;
            pv = MSl[mit].v_;
            pa = MSl[mit].a_;
            
            for(int jx = -1; jx <= 1; jx++){ // sample inputs
                da(0) = jx * da_;
                for(int jy = -1; jy <= 1; jy++){
                    da(1) = jy * da_;
                    for(int jz = -1; jz <= 1; jz++){
                        da(2) = jz * da_;

                        // feasibility check
                        for(int i = 10; i > 5; i--){
                            inp_val = true;
                            inp = da * 0.1 * i + MSl[mit].a_;
                            for(int dim = 0; dim < 3; dim++){
                                if(!FeasibleInput(MSl[mit].v_(dim), inp(dim))){
                                    inp_val = false;
                                    break;
                                }
                            }
                            if(inp_val) break;
                        }

                        if(inp_val) inpts.emplace_back(inp);
                    }
                }
            }   

            for(auto &in : inpts){ // generate motions
                param.col(0) = pp;
                param.col(1) = pv;
                param.col(2) = in * 0.5;
                if(!MotionCheck(param, traj_ids, false)) continue;
                end_motion = false;
                ms.p_ = pp + pv * dt_ + dt_ * dt_ * in * 0.5;
                ms.v_ = pv + in * dt_;
                ms.a_ = in;
                ms.id_ = MSl.size();
                ms.parent_id_ = mit;
                ms.path_.clear();
                for(auto &tr : traj_ids) {
                    ms.path_.emplace_back(tr.first);
                }

                SetTrajCost(traj_ids, covered_nodes, ms.id_, sample_layer - 1);
                nidl.push_back(ms.id_);
                MSl.emplace_back(ms);
                // if(ms.id_ + 1 != MSl.size()){ // debug
                //     ROS_ERROR("error id!");
                //     ros::shutdown();
                // }
            }
            if(end_motion) end_motion_ids.emplace_back(mit);
        }
        eidl.swap(nidl);

    }
    if(sample_layer >= sample_depth_){
        for(auto &em: eidl){
            lr_node = LRM_->GetNode(MSl[em].p_);
            if(lr_node->topo_sch_->motion_state_ != 2){
                lr_node->topo_sch_->motion_state_ = 2;
                lr_node->topo_sch_->me_id_ = em;
            }
        }
    }
    if(vis_motion_) VisMotions(MSl);
}

void FastMotion::RetrieveTraj(vector<MotionStateF> &MSl, list<Eigen::Vector3d> &path, const int &m_id){
    // cout<<"m_id:"<<m_id<<endl;
    if(m_id < 0 || m_id >= MSl.size()){
        cout<<"MSl.size():"<<MSl.size()<<endl;
        ROS_ERROR("error RetrieveTraj");
        ros::shutdown();
        return;
    }
    Eigen::Vector3d p0 = path.front();
    int c;
    int r_id = m_id;
    bool find_traj = false;
    while(MSl[r_id].parent_id_ >= 0 && r_id >= 0){
        // cout<<"r_id:"<<r_id<<endl;
        for(list<int>::reverse_iterator it = MSl[r_id].path_.rbegin(); it != MSl[r_id].path_.rend(); it++){
            c = LRM_->PostoId(path.front());
            if(!find_traj){
                if(c == *it) find_traj = true;
            }
            if(*it == c || !find_traj) continue;
            path.push_front(LRM_->IdtoPos(*it));
            // cout<<"path:"<<path.front().transpose()<<endl;
            // cout<<"r_id:"<<r_id<<endl;
        }
        if(!find_traj){
            for(auto p : MSl[r_id].path_){
                cout<<p<<endl;
            }
            cout<<"c:"<<c<<endl;
            cout<<"p0:"<<p0.transpose()<<"   id:"<<LRM_->PostoId(p0)<<endl;
            ROS_ERROR("RetrieveTraj m error!");
            ros::shutdown();
        }
        // cout<<"traj_begin:"<<LRM_->IdtoPos(MSl[r_id].path_.front()).transpose()<<endl;
        r_id = MSl[r_id].parent_id_;
        // cout<<"r_id:"<<r_id<<endl;

    }
    p0 = LRM_->IdtoPos(MSl[0].path_.front());
    // if((path.front() - p0).norm() > 1e-3){
    //     cout<<"pd:"<<(path.front() - p0).norm()<<endl;
    //     cout<<"p0:"<<p0.transpose()<<endl;
    //     cout<<"p1:"<<path.front().transpose()<<endl;
    //     getchar();
    // }
}

void FastMotion::VisMotions(vector<MotionStateF> &MSl){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(1);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = -2;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::LINE_LIST;
    mka.markers[0].scale.x = 0.02;
    mka.markers[0].scale.y = 0.02;
    mka.markers[0].scale.z = 0.02;
    mka.markers[0].color.a = 0.15;
    mka.markers[0].color.r = 0.9;
    mka.markers[0].color.g = 0.9;
    mka.markers[0].color.b = 0.0;
    Eigen::Matrix3d param;
    Eigen::Vector3d p;
    geometry_msgs::Point pt;
    for(auto &m : MSl){
        if(m.id_ == 0) continue;
        double dt = dt_ / 5 - 1e-4;
        param.col(2) = m.a_ * 0.5;
        param.col(1) = m.v_ - m.a_ * dt_;
        param.col(0) = m.p_ - dt_ * param.col(1) - 0.5 * dt_ * dt_ * m.a_;
        pt.x = param(0, 0);
        pt.y = param(1, 0);
        pt.z = param(2, 0);
        mka.markers[0].points.emplace_back(pt);
        for(double t = dt; t < dt_; t += dt){
            p = param.col(0) + param.col(1) * t + param.col(2) * t * t;
            pt.x = p(0);
            pt.y = p(1);
            pt.z = p(2);
            mka.markers[0].points.emplace_back(pt);
            mka.markers[0].points.emplace_back(pt);
        }
        mka.markers[0].points.pop_back();
    }
    debug_pub_.publish(mka);
}

void FastMotion::SampleVis(){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(1);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = -1;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::SPHERE_LIST;
    mka.markers[0].scale.x = 0.1;
    mka.markers[0].scale.y = 0.1;
    mka.markers[0].scale.z = 0.1;
    mka.markers[0].color.a = 1.0;
    mka.markers[0].color.r = 0.9;
    mka.markers[0].color.g = 0.9;
    mka.markers[0].color.b = 0.0;
    geometry_msgs::Point pt;
    for(int i = 0; i < motions_.size(); i++){
        for(auto &m : motions_[i]){
            pt.x = m.pe_(0);
            pt.y = m.pe_(1);
            pt.z = m.pe_(2);
            mka.markers[0].points.emplace_back(pt);
        }
        debug_pub_.publish(mka);
        cout<<vas_[i].first<<"  "<<vas_[i].second.transpose()<<endl;
        ROS_WARN("pub!");
        mka.markers[0].points.clear();
        // ros::Duration(1.0).sleep();
        // getchar();
    }
}

void FastMotion::VisMotionDebug(const int id, const int m_id, list<Eigen::Vector3d> &path, Eigen::Vector3d p0, Eigen::Matrix3d R){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(1);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = 1;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::LINE_STRIP;
    mka.markers[0].scale.x = 0.05;
    mka.markers[0].scale.y = 0.05;
    mka.markers[0].scale.z = 0.05;
    mka.markers[0].color.a = 0.8;
    mka.markers[0].color.r = 0.9;
    mka.markers[0].color.g = 0.9;
    mka.markers[0].color.b = 0.3;

    // cout<<"R:\n"<<R<<endl;

    list<Eigen::Vector3d> pts;
    int c_id = m_id;
    while(motions_[id][c_id].parent_ != -1){
        Eigen::Vector3d p, v, a;
        a = acc_samp_[motions_[id][c_id].aid_];
        v = motions_[id][c_id].ve_ - dt_ * a;
        p = motions_[id][c_id].pe_ - dt_ * v - 0.5 * dt_ * dt_ * a;
        // cout<<"p:"<<p.transpose()<<endl;
        // cout<<"v:"<<v.transpose()<<endl;
        // cout<<"a:"<<a.transpose()<<endl;

        for(int i = 0; i < 5; i++){
            double t = (4 - i) * dt_ / 4;
            Eigen::Vector3d pit = R * (p + t * v + 0.5 * t * t * a) + p0;
            // cout<<"pit:"<<pit.transpose()<<endl;
            pts.emplace_front(pit);
        }
        c_id = motions_[id][c_id].parent_;
    }

    geometry_msgs::Point pg;
    for(auto p : pts){
        pg.x = p(0);
        pg.y = p(1);
        pg.z = p(2);
        mka.markers[0].points.emplace_back(pg);
    }
    for(auto p : path){
        pg.x = p(0);
        pg.y = p(1);
        pg.z = p(2);
        // cout<<"p:"<<p.transpose()<<endl;
        mka.markers[0].points.emplace_back(pg);
    }
    debug_pub_.publish(mka);
}