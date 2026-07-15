#include <mp_planner/mp_planner.h>

void MotionPrimitivePlanner::init(ros::NodeHandle &nh, ros::NodeHandle &nh_private){
    std::string ns = ros::this_node::getName();

    nh_private.param(ns + "/Motion/MaxVel", 
        max_v_, 5.0);
    nh_private.param(ns + "/Motion/MaxAcc", 
        max_a_, 5.0);
    nh_private.param(ns + "/Motion/MaxDacc", 
        max_da_, 1.0);
    nh_private.param(ns + "/Motion/MaxDyaw", 
        max_dy_, 2.0);
    nh_private.param(ns + "/Motion/MaxDdyaw", 
        max_ddy_, 2.0);
    nh_private.param(ns + "/Motion/MaxDddyaw", 
        max_dddy_, 1.0);
    nh_private.param(ns + "/Motion/DentaT", 
        dt_, 0.3);
    nh_private.param(ns + "/Motion/MaxSteps", 
        max_step_, 5);
    nh_private.param(ns + "/Motion/SafeSteps", 
        safe_step_, 2);
    nh_private.param(ns + "/Motion/VoxScaleX", 
        vox_scale_(0), 0.3);
    nh_private.param(ns + "/Motion/VoxScaleY", 
        vox_scale_(1), 0.3);
    nh_private.param(ns + "/Motion/VoxScaleZ", 
        vox_scale_(2), 0.3);
    nh_private.param(ns + "/Motion/MaxPlanT", 
        max_plan_t_, 0.025);
    nh_private.param(ns + "/Motion/CloseRange",
        close_range_, 0.5);


    double q3 = 1;
    // max_v_ /= q3;
    // max_a_ /= q3;
    // max_da_ = q3;
    dt2_ = dt_ * dt_;

    v_n_(0) = 5;
    v_n_(1) = 25;
    v_n_(2) = 125;
    dv_ = max_v_ / 5 * 2.0;

    a_n_(0) = ceil((2*max_a_+1e-3) / max_da_);
    a_n_(1) = a_n_(0) * a_n_(0);
    a_n_(2) = a_n_(0) * a_n_(0) * a_n_(0);
    da_ = max_a_ / a_n_(0) * 2.0;

    vis_pub_ = nh.advertise<visualization_msgs::MarkerArray>("/motion_plan/vis", 100);
    debug_pub_ = nh.advertise<visualization_msgs::Marker>("/motion_plan/debug", 100);
    // kdTree_ = kd_create(3);

}

void MotionPrimitivePlanner::Reset(MotionState &ms){
    searched_m_.clear();
    // kd_free(kdTree_);
    reached_pts_.clear();
    // kdTree_ = kd_create(3);
    MotionState ims;

    cur_id_ = 0;
    ims = ms;
    ims.id_ = cur_id_;
    ims.parent_id_ = -1;
    ims.layer_ = 0;
    cur_id_++;
    bbx_max_ = ims.p_;
    bbx_min_ = ims.p_;
    for(int dim = 0; dim < 3; dim++) {
        origin_(dim) = ims.p_(dim) - max_v_ * max_step_ * dt_ - 1.0;
        vox_n_(dim) = ceil(ims.p_(dim) + max_v_ * max_step_ * dt_ + 1.0 - origin_(dim));
    }
    vox_n_(1) = vox_n_(1) * vox_n_(0);
    vox_n_(2) = vox_n_(2) * vox_n_(1);

    if(ims.v_.norm() > 1e-3) ims.v_ = ims.v_.normalized() * min(ims.v_.norm(), max_v_-1e-3);
    if(ims.a_.norm() > 1e-3) ims.a_ = ims.a_.normalized() * min(ims.a_.norm(), max_a_-1e-3);
    for(int dim = 0; dim < 3; dim++){
        double ve;
        while(!FeasibleInput(ims.v_(dim), ims.a_(dim), max_v_, max_da_, ve)){
            ims.a_(dim) *= 0.9;
            if(abs(ims.a_(dim)) < 1e-3){
                ROS_WARN("error dim: %d, vs: %lf, set zero", dim, ims.v_(dim));
                ims.a_(dim) *= 0.0;
                break;
            }
        }
    }

    ims.yaw_down_ = ims.yaw_up_;

    ims.yawd_up_ = (ims.yawd_up_ + ims.yawd_down_)/2;
    ims.yawd_up_ = max(min(ims.yawd_up_, max_dy_-1e-3), -max_dy_+1e-3);
    ims.yawd_down_ = ims.yawd_up_;
    
    ims.yawdd_up_ = (ims.yawdd_up_ + ims.yawdd_down_)/2;
    ims.yawdd_up_ = max(min(ims.yawdd_up_, max_ddy_-1e-3), -max_ddy_+1e-3);
    ims.yawdd_down_ = ims.yawdd_up_;
    
    double ve;
    while(!FeasibleInput(ims.yawd_up_, ims.yawdd_up_, max_dy_, max_dddy_, ve)){
        ims.yawdd_up_ *= 0.9;
        if(abs(ims.yawdd_up_) < 1e-3){
            ROS_WARN("error yawds: %lf, set zero", ims.yawdd_up_);
            ims.yawdd_up_ *= 0.0;
            break;
        }
    }

    ims.flags_ = 0;
    ims.flags_ |= 2;
    searched_m_.emplace_back(ims);
}

void MotionPrimitivePlanner::Plan(){
    int expand_count = 0;
    MotionState mc, me;
    list<int> cl, el; //expanding list, next expand list
    list<double> inpx, inpy, inpz;
    list<Eigen::Vector3d> inpl;// input list
    tr1::unordered_map<int, int> searched_states_;
    cl.emplace_back(0);
    me.flags_ = 2;

    // cout<<"start:"<<searched_m_[0].p_.transpose()<<endl;
    // cout<<"start:"<<searched_m_[0].v_.transpose()<<endl;
    // cout<<"start a:"<<searched_m_[0].a_.transpose()<<endl;
    // cout<<"start y:"<<searched_m_[0].yaw_up_<<endl;
    // cout<<"start yd:"<<searched_m_[0].yawd_up_<<endl;
    // cout<<"start ydd:"<<searched_m_[0].yawdd_up_<<endl;


    double start_t = ros::WallTime::now().toSec();
    ros::WallTime T;
    bool stop_flag = false;
    int total_count = 0;
    while(expand_count < max_step_ && !stop_flag){
        int success_num = 0;
        for(auto &c_id : cl){
            if(success_num % 100 == 0 && T.now().toSec() - start_t > max_plan_t_){
                stop_flag = true;
                break;
            }
            mc = searched_m_[c_id];
            me.layer_ = expand_count+1;
            me.parent_id_ = mc.id_;
            /* init space inputs */
            inpx.clear();
            inpy.clear();
            inpz.clear();
            inpx.emplace_back(mc.a_(0));
            inpy.emplace_back(mc.a_(1));
            inpz.emplace_back(mc.a_(2));
            if(max_a_ - mc.a_(0) > 0.1) inpx.push_back(min(max_a_, mc.a_(0) + max_da_));//max_v_-->max_a_
            if(max_a_ - mc.a_(1) > 0.1) inpy.push_back(min(max_a_, mc.a_(1) + max_da_));
            if(max_a_ - mc.a_(2) > 0.1) inpz.push_back(min(max_a_, mc.a_(2) + max_da_));
            if(max_a_ + mc.a_(0) > 0.1) inpx.push_back(max(-max_a_, mc.a_(0) - max_da_));
            if(max_a_ + mc.a_(1) > 0.1) inpy.push_back(max(-max_a_, mc.a_(1) - max_da_));
            if(max_a_ + mc.a_(2) > 0.1) inpz.push_back(max(-max_a_, mc.a_(2) - max_da_));
            inpl.clear();
            for(auto &ax: inpx)
                for(auto &ay: inpy)
                    for(auto &az: inpz){
                        inpl.emplace_back(ax, ay, az);
                    }
            // ROS_WARN("Plan0");
            /* init yaw range */
            int y = YawMotionForward(mc, me);

            if(y == 2 || y == 3) {
                ROS_ERROR("infeasible yaw!");                
                cout<<"cur_id_:"<<cur_id_<<endl;
                cout<<"y:"<<y<<endl;
                cout<<"yaw_down:"<<mc.yaw_down_<<endl;
                cout<<"yawd_down:"<<mc.yawd_down_<<endl;
                cout<<"yawdd_down:"<<mc.yawdd_down_<<endl;
                cout<<"yaw_up:"<<mc.yaw_up_<<endl;
                cout<<"yawd_up:"<<mc.yawd_up_<<endl;
                cout<<"yawdd_up:"<<mc.yawdd_up_<<endl;
                if(y == 2){
                    me.yawdd_down_ = min(max(mc.yawdd_down_ - max_dddy_, -max_ddy_+1e-3), max_ddy_-1e-3);
                    if(!FeasibleInputDebug(mc.yawd_down_, me.yawdd_down_, max_dy_, max_dddy_, me.yawd_down_)){
                        me.yawdd_down_ = min(max(mc.yawdd_down_, -max_ddy_+1e-3), max_ddy_-1e-3);
                        if(!FeasibleInputDebug(mc.yawd_down_, me.yawdd_down_, max_dy_, max_dddy_, me.yawd_down_)){
                            me.yawdd_down_ = min(max(mc.yawdd_down_ + max_dddy_, -max_ddy_+1e-3), max_ddy_-1e-3);
                            if(!FeasibleInputDebug(mc.yawd_down_, me.yawdd_down_, max_dy_, max_dddy_, me.yawd_down_)){
                            }
                        }
                    }
                }
                else{
                    me.yawdd_up_ = min(max(mc.yawdd_up_ + max_dddy_, -max_ddy_+1e-3), max_ddy_-1e-3);
                    if(!FeasibleInputDebug(mc.yawd_up_, me.yawdd_up_, max_dy_, max_dddy_, me.yawd_up_)){
                        me.yawdd_up_ = min(max(mc.yawdd_up_, -max_ddy_+1e-3), max_ddy_-1e-3);
                        if(!FeasibleInputDebug(mc.yawd_up_, me.yawdd_up_, max_dy_, max_dddy_, me.yawd_up_)){
                            me.yawdd_up_ = min(max(mc.yawdd_up_ - max_dddy_, -max_ddy_+1e-3), max_ddy_-1e-3);
                            if(!FeasibleInputDebug(mc.yawd_up_, me.yawdd_up_, max_dy_, max_dddy_, me.yawd_up_)){
                            }
                        }
                    }
                }
                return;
            }
            // ROS_WARN("Plan1");

            /* expand */
            total_count += inpl.size();
            for(auto &inp : inpl){
                if(MotionForward(mc, me, inp)){
                    int m_key = Motion2Key(me);
                    auto h = searched_states_.find(m_key);
                    // cout<<"key:"<<m_key<<endl;
                    if(h != searched_states_.end()){
                        searched_m_[h->second].co_parents_.emplace_back(mc.id_);
                        continue;
                    }
                    else{
                        searched_states_.insert({m_key, cur_id_});
                        success_num++;
                        for(int dim = 0; dim < 3; dim++){
                            bbx_max_(dim) = max(bbx_max_(dim), me.p_(dim));
                            bbx_min_(dim) = min(bbx_min_(dim), me.p_(dim));
                        }                        
                        me.id_ = cur_id_;
                        el.emplace_back(cur_id_);
                        searched_m_.emplace_back(me);
                        searched_m_.back().co_parents_.emplace_back(mc.id_);
                        searched_m_[c_id].flags_ &= 253;
                        cur_id_++;
                    }
                }
            }
        }
        cl.swap(el);
        el.clear();
        expand_count++;
    }

    ROS_WARN("motion sample end!");
    for(auto &p : reached_pts_){
        int k = Position2Key(p.second.first);
        auto ph = searched_dict_.find(k);
        if(ph == searched_dict_.end()){
            searched_dict_.insert({k, {{p.first, p.second.second}}});
        }
        else{
            ph->second.push_back({p.first, p.second.second});
        }
    }

    for(auto &m : searched_m_){
        m.flags_ |= 4;
    }
    cout<<"expand_count:"<<expand_count<<" stop_flag:"<<stop_flag<<"--"<<T.now().toSec() - start_t<<endl;
    cout<<"total_count:"<<total_count<<endl;
    ROS_WARN("Plan4");
}

bool MotionPrimitivePlanner::DepthFirstCheck(MotionState &mc, int layer){
    list<double> inpx, inpy, inpz;
    list<Eigen::Vector3d> inpl;// input list
    inpx.emplace_back(mc.a_(0));
    inpy.emplace_back(mc.a_(1));
    inpz.emplace_back(mc.a_(2));
    if(max_a_ - mc.a_(0) > 0.1) inpx.push_back(min(max_a_, mc.a_(0) + max_da_));
    if(max_a_ - mc.a_(1) > 0.1) inpy.push_back(min(max_a_, mc.a_(1) + max_da_));
    if(max_a_ - mc.a_(2) > 0.1) inpz.push_back(min(max_a_, mc.a_(2) + max_da_));
    if(max_a_ + mc.a_(0) > 0.1) inpx.push_back(max(-max_a_, mc.a_(0) - max_da_));
    if(max_a_ + mc.a_(1) > 0.1) inpy.push_back(max(-max_a_, mc.a_(1) - max_da_));
    if(max_a_ + mc.a_(2) > 0.1) inpz.push_back(max(-max_a_, mc.a_(2) - max_da_));
    inpl.clear();
    for(auto &ax: inpx)
        for(auto &ay: inpy)
            for(auto &az: inpz)
                inpl.emplace_back(ax, ay, az);

    MotionState me;
    for(auto &inp : inpl){
        if(!MotionForward(mc, me, inp)) continue;
        if(layer >= safe_step_) return true;
        if(DepthFirstCheck(me, layer+1)) return true;
    }
    return false;
}

int MotionPrimitivePlanner::GetCost(list<Eigen::Vector3d> &path, const double &yaw_up, const double &yaw_down, double &cost, bool yaw_require){
    // ROS_WARN("GetCost0");
    if(path.size() == 0) return 2;
    double pl = 0;
    Eigen::Vector3d p1;
    // ROS_WARN("GetCost0.1");
    // cout<<"path size:"<<path.size()<<endl;
    p1 = path.back();
    auto p2 = path.rbegin();
    // ROS_WARN("GetCost1");

    while (p2 != path.rend())
    {
        int k = Position2Key(*p2);
        auto ph = searched_dict_.find(k);
        if(ph != searched_dict_.end()){
            double min_c = 99999.0;
            for(auto &i_d : ph->second){
                // cout<<"i_d.first:"<<i_d.first<<endl;
                if(i_d.second < min_c){
                    if(yaw_require || YawIntersect(searched_m_[i_d.first], yaw_up, yaw_down)) min_c = i_d.second;
                }
            }
            if(min_c < 99998){
                if(p2 == path.rbegin()){
                    cost = min_c;
                    // ROS_WARN("GetCost2");
                    return 0;
                }
                else{
                    cost = pl / max_v_ + dt_ * max_step_;
                    // ROS_WARN("GetCost3");
                    return 1;
                }
            }
        }
        pl += (p1 - *p2).norm();
        p1 = *p2;
        p2++;

    }
    cost = pl / max_v_ + dt_ * max_step_;
    // ROS_WARN("GetCost4");
    return 1;    
}

void MotionPrimitivePlanner::Show(){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(max_step_);
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].pose.orientation.w = 1.0;
    mka.markers[0].type = visualization_msgs::Marker::SPHERE_LIST;      //nodes
    mka.markers[0].scale.x = 0.05;
    mka.markers[0].scale.y = 0.05;
    mka.markers[0].scale.z = 0.05;
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = 0;
    mka.markers[0].color.a = 1.0;
    mka.markers[0].color.r = 0.8 * (max_step_ + 1.0) / (max_step_ + 1.0);
    mka.markers[0].color.g = 0.9 * 0 / (max_step_ + 1.0);
    mka.markers[0].color.b = 0.7 * 0 / (max_step_ + 1.0);
    for(int i = 1; i < max_step_; i++){
        // int j = i;
        mka.markers[i] = mka.markers[0];
        mka.markers[i].id = i;
        mka.markers[i].color.r = 0.8 * double(max_step_ + 1.0 - i) / (max_step_ + 1.0);
        mka.markers[i].color.g = 0.9 * double(i) / (max_step_ + 1.0);
        mka.markers[i].color.b = 0.7 * double(i) / (max_step_ + 1.0);
        // cout<<"i:"<<i<<endl;
        // cout<<"r:"<<mka.markers[i].color.r<<endl;
        // cout<<"g:"<<mka.markers[i].color.g<<endl;
        // cout<<"b:"<<mka.markers[i].color.b<<endl;
    }

    // double max_x = -1000;
    // MotionState mmx;    //debug
    for(auto &m : searched_m_){
        // cout<<"m.layer_-1:"<<m.layer_-1<<endl;
        // cout<<"mka.markers:"<<mka.markers.size()<<endl;
        if(m.flags_ & 4 && m.parent_id_ != -1) {
            // cout<<"layer:"<<m.layer_<<endl;
            // if(m.layer_ == 5){
                // if(max_x < m.p_(0)){
                //     mmx = m;
                // }
                // if(m.layer_ == 1){
                //     cout<<"1layer"<<endl;
                //     cout<<m.v_.transpose()<<endl;
                //     cout<<m.a_.transpose()<<endl;
                //     cout<<m.v_ - m.a_*dt_<<endl;
                // }
                int i = m.layer_-1;
                if(m.flags_ & 1) i = 4;
                else i = 0;
                LoadMotionVis(m.id_, mka.markers[i]);
            // }
        }
    }
    // ROS_WARN("mmx");
    // cout<<mmx.layer_<<endl;
    // cout<<mmx.p_.transpose()<<endl;
    // cout<<mmx.v_.transpose()<<endl;
    // cout<<mmx.a_.transpose()<<endl;

    int i = 0;
    for(auto &mk : mka.markers){
        if(mk.points.size() == 0){
            // cout<<"i:"<<mk.id<<endl;
            mk.action = visualization_msgs::Marker::DELETE;
        }
    }
    vis_pub_.publish(mka);
}

void MotionPrimitivePlanner::LoadMotionVis(const int &id, visualization_msgs::Marker &mk){
    geometry_msgs::Point pt;
    if(id < 0 || id > searched_m_.size()){
        ROS_ERROR("LoadMotionVis");
        return;
    }
    Eigen::Matrix3d param;
    param.row(0) = searched_m_[id].p_.transpose();
    param.row(1) = -searched_m_[id].v_.transpose();
    param.row(2) = 0.5 * searched_m_[id].a_.transpose();
    // if(searched_m_[id].layer_ == 1){
    //     cout<<"p:"<<searched_m_[id].p_.transpose()<<endl;
    // }
    for(double t = 0; t < dt_ + 1e-3; t += 0.05){
        pt.x = param(0, 0) + param(1, 0) * t + param(2, 0) * t * t;
        pt.y = param(0, 1) + param(1, 1) * t + param(2, 1) * t * t;
        pt.z = param(0, 2) + param(1, 2) * t + param(2, 2) * t * t;
        mk.points.emplace_back(pt);
    }
    // pt.x = searched_m_[id].p_(0);
    // pt.y = searched_m_[id].p_(1);
    // pt.z = searched_m_[id].p_(2);
    // mk.points.emplace_back(pt);

}
