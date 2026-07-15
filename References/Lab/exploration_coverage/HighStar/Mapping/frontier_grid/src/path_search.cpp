#include <frontier_grid/frontier_grid.h>
using namespace std;
using namespace lowres;

void FrontierGrid::ClearSearched(vector<shared_ptr<sch_node>> &node_list){
    for(vector<shared_ptr<sch_node>>::iterator node_it = node_list.begin(); node_it != node_list.end(); node_it++){
        shared_ptr<LR_node> node = LRM_->GetNode(LRM_->IdtoPos((*node_it)->pos_));
        if(node != LRM_->Outnode_ && node != NULL){
            node->topo_sch_ = NULL;
        }
        else{//debug
            cout<<(*node_it)->pos_.transpose()<<endl;
            cout<<(*node_it)->g_score_<<endl;
            ROS_WARN("ERROR FreeWorker");
        }
    }
}

void FrontierGrid::GetDiagnalConnection(list<Eigen::Vector3d> &comp_seg, Eigen::Vector3i ps, Eigen::Vector3i dir){
    comp_seg.clear();
    // comp_seg.push_back(LRM_->IdtoPos(ps));
    int move_count = dir.cwiseAbs().sum();
    if(move_count == 1){
        comp_seg.push_back(LRM_->IdtoPos(ps + dir));
    }
    else if(move_count == 2){
        for(int dim = 0; dim < 3; dim++) {
            if(dir(dim) != 0){
                Eigen::Vector3i p = ps;
                p(dim) += dir(dim);
                if(LRM_->IsFeasible(p)) {
                    comp_seg.push_back(LRM_->IdtoPos(p));
                    comp_seg.push_back(LRM_->IdtoPos(ps + dir));
                    return;
                }
            }
        } 
        ROS_ERROR("error GetDiagnalConnection2");
        ros::shutdown();
        return;
    }
    else if(move_count == 3){
        Eigen::Vector3i pe = ps + dir;
        Eigen::Vector3i p, p1, p2;
        vector<bool> m2(3, false);
        // vector<bool> checked(3, false);
        p1 = ps;
        p1(0) = ps(0) + dir(0);
        
        if(LRM_->IsFeasible(p1)){
            p2 = pe;
            p2(1) = pe(1) - dir(1);    //x-->z-->y
            if(LRM_->IsFeasible(p2)){  
                comp_seg.push_back(LRM_->IdtoPos(p1));
                comp_seg.push_back(LRM_->IdtoPos(p2));
                comp_seg.push_back(LRM_->IdtoPos(pe));
                return;
            }
            p2 = pe;
            p2(2) = pe(2) - dir(2);    //x-->y-->z
            if(LRM_->IsFeasible(p2)){
                comp_seg.push_back(LRM_->IdtoPos(p1));
                comp_seg.push_back(LRM_->IdtoPos(p2));
                comp_seg.push_back(LRM_->IdtoPos(pe));
                return;
            }
        }
        else{
            p2 = pe;
            p2(1) = pe(1) - dir(1);
            if(LRM_->IsFeasible(p2)) m2[1] = true;
            p2 = pe;
            p2(2) = pe(2) - dir(2);
            if(LRM_->IsFeasible(p2)) m2[2] = true;
        }

        p1 = ps;
        p1(1) = ps(1) + dir(1);
        if(LRM_->IsFeasible(p1)){
            if(m2[2]) {
                // p2 = pe;
                p2(2) = pe(2) - dir(2);
                comp_seg.push_back(LRM_->IdtoPos(p1));
                comp_seg.push_back(LRM_->IdtoPos(p2));
                comp_seg.push_back(LRM_->IdtoPos(pe));
                return; //y-->x-->z
            }

            p2 = pe;
            p2(0) = pe(0) - dir(0);    //y-->z-->x
            if(LRM_->IsFeasible(p2)) {
                comp_seg.push_back(LRM_->IdtoPos(p1));
                comp_seg.push_back(LRM_->IdtoPos(p2));
                comp_seg.push_back(LRM_->IdtoPos(pe));
                return;
            }
            else{
                p = pe;
                p(0) = pe(0) - dir(0);    //x-->z-->x
                if(LRM_->IsFeasible(p)) m2[0] = true;
            }
        }
        else{
            p2 = pe;
            p2(0) = pe(0) - dir(0);
            if(LRM_->IsFeasible(p2)) m2[0] = true;
        }

        p1 = ps;
        p1(2) = ps(2) + dir(2);
        if(LRM_->IsFeasible(p1)){
            if(m2[0]) {
                p2 = pe;
                p2(0) = pe(0) - dir(0);    //z-->x-->y
                comp_seg.push_back(LRM_->IdtoPos(p1));
                comp_seg.push_back(LRM_->IdtoPos(p2));
                comp_seg.push_back(LRM_->IdtoPos(pe));
                return;
            }

            if(m2[1]){
                p2 = pe;
                p2(1) = pe(1) - dir(1);    //z-->y-->x
                comp_seg.push_back(LRM_->IdtoPos(p1));
                comp_seg.push_back(LRM_->IdtoPos(p2));
                comp_seg.push_back(LRM_->IdtoPos(pe));
                return; //z-->x-->y
            }
        }
        //to debug
        cout<<"ps:"<<ps.transpose()<<endl;
        cout<<"pe:"<<pe.transpose()<<endl;
        cout<<"dir:"<<dir.transpose()<<endl;
        for(int dim = 0; dim < 3; dim++){
            p = ps;
            p(dim) += dir(dim);
            cout<<p.transpose()<<endl;
            cout<<LRM_->IsFeasible(p)<<endl;
            p = pe;
            p(dim) -= dir(dim);
            cout<<p.transpose()<<endl;
            cout<<LRM_->IsFeasible(p)<<endl;
        }
        ROS_ERROR("error GetDiagnalConnection3");
        ros::shutdown();
        return;
    }
    else{
        ROS_ERROR("error GetDiagnalConnection4");
        cout<<dir.transpose()<<endl;
        ros::shutdown();
        return;
    }
}

void FrontierGrid::RetrieveExpPath(const Eigen::Vector3d &ps, const Eigen::Vector3d &pe, list<Eigen::Vector3d> &path, list<Eigen::Vector3d> &path_debug, shared_ptr<lowres::sch_node> &end_node){
    path.clear();
    path_debug.clear();
    path.emplace_front(pe);
    path_debug.emplace_front(pe);
    Eigen::Vector3i p1, p2;
    list<Eigen::Vector3d> path_seg;
    shared_ptr<sch_node> c_node = end_node;
    path.push_front(LRM_->IdtoPos(c_node->pos_));
    path_debug.push_front(LRM_->IdtoPos(c_node->pos_));
    while(c_node->parent_ != NULL){
        GetDiagnalConnection(path_seg, c_node->pos_, c_node->parent_->pos_ - c_node->pos_);
        // cout<<"path_seg:"<<path_seg.size()<<endl;
        // cout<<"s:" <<c_node->pos_.transpose()<<" dir:"<<(c_node->parent_->pos_ - c_node->pos_).transpose()<<endl;
        for(auto &p : path_seg) {
            // cout<<p.transpose()<<endl;
            path.push_front(p);
        }
        c_node = c_node->parent_;
        path_debug.push_front(LRM_->IdtoPos(c_node->pos_));
    }
    // path.push_front(LRM_->IdtoPos(c_node->pos_));
    path.emplace_front(ps);
    path_debug.emplace_front(ps);
}

void FrontierGrid::RetrieveExpPath(list<Eigen::Vector3d> &path, list<Eigen::Vector3d> &path_debug, shared_ptr<lowres::sch_node> &end_node, shared_ptr<lowres::sch_node> &root_node){
    path.clear();
    path_debug.clear();
    Eigen::Vector3i p1, p2;
    list<Eigen::Vector3d> path_seg;
    shared_ptr<sch_node> c_node = end_node;
    path.push_front(LRM_->IdtoPos(c_node->pos_));
    path_debug.push_front(LRM_->IdtoPos(c_node->pos_));
    while(c_node->parent_ != NULL){
        GetDiagnalConnection(path_seg, c_node->pos_, c_node->parent_->pos_ - c_node->pos_);
        // cout<<"s:" <<c_node->pos_.transpose()<<" dir:"<<(c_node->parent_->pos_ - c_node->pos_).transpose()<<endl;

        for(auto &p : path_seg) {
            // cout<<p.transpose()<<endl;
            path.push_front(p);
        }
        c_node = c_node->parent_;
        // cout<<"motion_state:"<<int(c_node->motion_state_)<<endl;
        // cout<<"cost:"<<c_node->g_score_<<endl;

        path_debug.push_front(LRM_->IdtoPos(c_node->pos_));
    }
    root_node = c_node;
    // path.push_front(LRM_->IdtoPos(c_node->pos_));
}

int FrontierGrid::FindExpTarget(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, pair<int, int> &target, 
                                    list<Eigen::Vector3d> &path, double yaws, double yawvs,
                                    double yawv, double yawa, double vel, int exclude_f, double max_range){
    vector<shared_ptr<sch_node>> node_list; //to maintain nodes 
    bool find_target = false;
    if(!LRM_->IsFeasible(ps)){
        // FreeWorker(workid, node_list);
        cout<<LRM_->IsFeasible(ps)<<endl;
        ROS_WARN("error IsFeasible");
        return find_target;
    }
    list<Eigen::Vector3d> debug_pts;
    vector<pair<double, double>> g_searched;
    priority_queue<shared_ptr<sch_node>, vector<shared_ptr<sch_node>>, DCompare> open_set;
    shared_ptr<sch_node> c_node, ep_node, best_node;
    shared_ptr<LR_node> lr_node;
    double max_g_score = 9999999.0;
    double best_gain = 0.0;
    double best_dyaw;
    Eigen::Vector3d vp_pos;
    Eigen::Vector3i std_start;
    Vector3d vdir = vs.normalized();
    Eigen::Vector3d ns = LRM_->node_scale_;
    LRM_->PostoId3(ps, std_start);
    c_node = make_shared<sch_node>();
    c_node->pos_ = std_start;
    c_node->g_score_ = 0;
    node_list.push_back(c_node);
    lr_node = LRM_->GetNode(LRM_->IdtoPos(c_node->pos_));
    if(lr_node == NULL || lr_node == LRM_->Outnode_) ROS_WARN("ERROR Search"); //debug
    lr_node->topo_sch_ = c_node;
    open_set.push(c_node);
    // cout<<"vp_dict_:"<<vp_dict_.size()<<endl;
    while(!open_set.empty()){
        c_node = open_set.top();
        open_set.pop();
        if(c_node->status_ == in_close) continue;/**/
        c_node->status_ = in_close;

        if(c_node->g_score_ > max_range){
            break;
        }

        // check if the vp is the best
        int n_id = LRM_->Id3toId(c_node->pos_);
        auto vp_it = vp_dict_.find(n_id);
        if(vp_it != vp_dict_.end()){
            for(auto &f_v : vp_it->second){
                if(f_grid_[f_v.first].f_state_ != 1 || f_grid_[f_v.first].local_vps_[f_v.second] != 1 || f_v.first == exclude_f) continue;
                // double gain = f_grid_[f_v.first].gains_[f_v.second];
                double gain;
                Eigen::Vector4d vp_pose;
                if(!GetVp(f_v.first, f_v.second, vp_pose, false)) continue;
                vp_pos = vp_pose.head(3);
                if(use_near_gain_) {
                    gain = GetGainRange(f_v.first, vp_pos);
                }
                else gain = f_grid_[f_v.first].gains_[f_v.second];

                double yd = abs(YawDiff(yaws, vp_pose(3)));
                if((ps - vp_pos).norm() < 1.0 && yd < 0.5 && LRM_->FeasibleLine(ps, vp_pos)){
                    RemoveVp(f_v.first, f_v.second);
                    continue;
                }
                // double t_cost = max(c_node->g_score_ / vel, yd / yawv);
                double yt = YtEva(YawDiff(vp_pose(3), yaws), yawvs, yawv, yawa);



                double t_cost = max(c_node->g_score_, yt/*yd / yawv*/);

                Vector3d dir = (vp_pos - ps).normalized();
                double diff = acos(vdir.dot(dir));
                t_cost += w_dir_ * diff;

                gain *= exp(-lambda_ * t_cost);
                // gain *= exp(-lambda_ * t_cost);
                g_searched.push_back({c_node->g_score_, f_grid_[f_v.first].gains_[f_v.second]});
                Eigen::Vector3d debug_p;
                GetVpPos(f_v.first, f_v.second, debug_p);
                // debug_pts.emplace_back(debug_p);
                g_searched.push_back({c_node->g_score_, f_grid_[f_v.first].gains_[f_v.second]});

                if(gain > best_gain){
                    if(!StrongCheckViewpoint(f_v.first, f_v.second, true)){   //dead vp, erase
                        RemoveVp(f_v.first, f_v.second);
                        continue;
                    }
                    best_gain = gain;
                    target = f_v;
                    find_target = true;
                    max_g_score = -log(best_gain / gmax_) / lambda_;
                    best_node = c_node;
                    // cout<<"got best:"<<f_v.first<<"  "<<f_v.second<<endl;
                }
            }
        }

        if(c_node->g_score_ > max_g_score){
            break;
        }

        //expand
        Eigen::Vector3i diff(0, 0, 0);
        for(diff(0) = -1; diff(0) < 2; diff(0)++){
            for(diff(1) = -1; diff(1) < 2; diff(1)++){
                for(diff(2) = -1; diff(2) < 2; diff(2)++){
                    if(diff(0) == 0 && diff(1) == 0 && diff(2) == 0) continue;    //the same node
                    if(!LRM_->FeasibleMove(c_node->pos_, diff)) continue;
                    // if(lr_node == NULL || lr_node == LRM_->Outnode_) continue;    //bad lrnode
                    // if(lr_node->flags_[0]) continue;
                    lr_node = LRM_->GetNode(LRM_->IdtoPos(diff+c_node->pos_));
                    ep_node = lr_node->topo_sch_;
                    
                    if(ep_node == NULL){                         //create a new node
                        ep_node = make_shared<sch_node>();
                        ep_node->pos_ = c_node->pos_ + diff;
                        ep_node->g_score_ = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm();// + LRM_->GetDist(diff(0), diff(1), diff(2));
                        ep_node->parent_ = c_node;
                        ep_node->status_ = in_open;
                        lr_node->topo_sch_ = ep_node;
                        node_list.push_back(ep_node);
                        open_set.push(ep_node);
                    }
                    else{                                       //new parent?
                        if(ep_node->status_ == in_close) continue;

                        double g_tmp = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm() + 0.0001;// + GetDist(diff(0), diff(1), diff(2));
                        // double f_tmp = g_tmp + GetHue(c_node->pos_, std_end)*lambda_heu_*1.001;
                        if(g_tmp < ep_node->g_score_){
                            ep_node->status_ = in_close;
                            ep_node = make_shared<sch_node>();/**/
                            lr_node->topo_sch_ = ep_node; /**/
                            ep_node->status_ = in_open;  /**/
                            ep_node->pos_ = c_node->pos_ + diff;/**/
                            // c_node->f_score_ = g_tmp + GetHue(c_node->pos_, std_end)*lambda_heu_;
                            ep_node->g_score_ = g_tmp;
                            ep_node->parent_ = c_node;
                            open_set.push(ep_node); /**/
                        }
                    }
                }
            }
        }
    }
    if(find_target){
        Eigen::Vector3d pe;
        list<Eigen::Vector3d> path_debug;
        cout<<int(f_grid_[target.first].local_vps_[target.second])<<endl;

        cout<<int(GetVpPos(target.first, target.second, pe))<<endl;
        RetrieveExpPath(ps, pe, path, path_debug, best_node);
        // Debug(debug_pts, 1);

        // Debug(path_debug, 0);
        cout<<"ps:"<<ps.transpose()<<endl;
        cout<<"pe:"<<pe.transpose()<<endl;
        std::cout <<"\033[0;32mFind target:\033[0m" << std::endl;
        cout<<"  f:"<<target.first<<endl;
        cout<<"  v:"<<target.second<<endl;
        cout<<"  max_g_score:"<<max_g_score<<endl;
        cout<<"  exp gain:"<<best_gain<<endl;
        cout<<"  vp gain:"<<f_grid_[target.first].gains_[target.second]<<endl;
        cout<<"  length:"<<best_node->g_score_<<endl;
        // for(auto g : g_searched){
        //     cout<<"dist:"<<g.first<<endl;
        //     cout<<"vp gain:"<<g.second<<endl;
        //     cout<<"exp gain:"<<exp(-lambda_ * g.first) * g.second<<endl;
        // }
    }
    else{
        ROS_WARN("no target");
    }
    
    ClearSearched(node_list);
    return find_target;
}


int FrontierGrid::FindExpTargetM(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as, pair<int, int> &target, Eigen::Vector4d &tar_vp,
                            list<Eigen::Vector3d> &path, double &expect_t, double yaws, double yawvs, double yawv, double yawa, double vel, double acc,
                             int exclude_f, double max_range, double t_thresh){
    if(!LRM_->IsFeasible(ps)){
        cout<<LRM_->IsFeasible(ps)<<endl;
        ROS_WARN("error IsFeasible");
        return 0;
    }
    list<int> init_list;
    vector<MotionStateF> MSl;
    double mt;
    double ts = ros::WallTime::now().toSec();
    double dect = vs.norm() / acc;
    double best_cost;
    bool use_ex_vp = false;
    FM_->InitMotion(ps, vs, as, mt, init_list, MSl); // sample motion primitives
    tr1::unordered_map<int, pair<Eigen::Vector4d, double>> vpex_dict;
    SampleExtraVps(ps, vs, as, vel, acc, yaws, yawvs, yawv, yawa, vpex_dict);// sample some viewpoits around the UAV
    vector<pair<double, double>> g_searched;
    vector<shared_ptr<sch_node>> node_list; //to maintain nodes 
    Eigen::Vector3d ns = LRM_->node_scale_;

    priority_queue<shared_ptr<sch_node>, vector<shared_ptr<sch_node>>, DCompare> open_set;
    shared_ptr<sch_node> c_node, ep_node, best_node, r_node;
    shared_ptr<LR_node> lr_node;
    double v_inv = 1.0 / vel;
    int find_target = 0;
    double max_g_score = 9999999.0;
    double best_gain = 0.0;
    double g = 0;
    int iter = 0;
    int vp_node_hits = 0;
    int vp_ref_count = 0;
    int vp_state_filtered = 0;
    int vp_positive_gain = 0;
    int vp_strong_rejected = 0;
    int extra_vp_hits = 0;
    list<Eigen::Vector3d> debug_pts;

    for(auto &i : init_list){ // search from the motion primitives
        lr_node = LRM_->GetNode(i);
        open_set.push(lr_node->topo_sch_);
        node_list.push_back(lr_node->topo_sch_);
    }

    while(!open_set.empty()){ // Dijkstra search
        c_node = open_set.top();
        open_set.pop();
        if(c_node->status_ == in_close) continue;/**/
        c_node->status_ = in_close;

        if(c_node->g_score_ > max_range){
            break;
        }

        // check if the vp is the best
        int n_id = LRM_->Id3toId(c_node->pos_);
        auto vp_it = vp_dict_.find(n_id);
        if(vp_it != vp_dict_.end()){ // find a viewpoint
            vp_node_hits++;
            for(auto &f_v : vp_it->second){
                vp_ref_count++;
                if(f_grid_[f_v.first].f_state_ != 1 || f_grid_[f_v.first].local_vps_[f_v.second] != 1 || f_v.first == exclude_f){
                    vp_state_filtered++;
                    continue;
                }
                Eigen::Vector4d vp_pose;
                Eigen::Vector3d vp_pos;
                if(!GetVp(f_v.first, f_v.second, vp_pose, false)) continue;
                vp_pos = vp_pose.head(3);
                double yd = abs(YawDiff(yaws, vp_pose(3)));
                if((ps - vp_pos).norm() < 1.0 && yd < 0.5 && LRM_->FeasibleLine(ps, vp_pos)){ // too close, remove it
                    RemoveVp(f_v.first, f_v.second);
                    continue;
                }

                double gain;
                if(use_near_gain_) gain = GetGainRange(f_v.first, vp_pos);
                else gain = f_grid_[f_v.first].gains_[f_v.second];
                if(gain > 0.0) vp_positive_gain++;

                double yt = YtEva(/*dyaw*/ YawDiff(vp_pose(3), yaws), yawvs, yawv, yawa);
                double pt = c_node->g_score_;
                if(pt * vel < 1.0) pt += 1.0;

                double t_cost = max(pt, yt/*yd / yawv*/);
                gain *= exp(-lambda_ * t_cost);

                if(gain > best_gain){
                    if(!StrongCheckViewpoint(f_v.first, f_v.second, true)){   //dead vp, erase
                        vp_strong_rejected++;
                        RemoveVp(f_v.first, f_v.second);
                        continue;
                    }
                    best_gain = gain;
                    target = f_v;
                    find_target = 1;
                    use_ex_vp = false;
                    max_g_score = -log(best_gain / gmax_) / lambda_;
                    g = f_grid_[f_v.first].gains_[f_v.second];
                    best_node = c_node;
                    best_cost = t_cost;
                }
            }
        }
        auto vpex_it = vpex_dict.find(n_id);
        if(vpex_it != vpex_dict.end()){
            extra_vp_hits++;
            double gain = vpex_it->second.second;
            double yt = YtEva(/*dyaw*/ YawDiff(vpex_it->second.first(3), yaws), yawvs, yawv, yawa);
            double pt = c_node->g_score_;
            if(pt * vel < 1.0) pt += 1.0;

            double t_cost = max(pt, yt/*yd / yawv*/);
            gain *= exp(-lambda_ * t_cost);
            if(gain > best_gain){
                best_gain = gain;
                target.first = -10;
                target.second = -10;
                find_target = 1;
                use_ex_vp = true;
                max_g_score = -log(best_gain / gmax_) / lambda_;
                best_node = c_node;
                best_cost = t_cost;
                tar_vp = vpex_it->second.first;
                g = vpex_it->second.second;
            }
            cout<<"reach exra:"<<vpex_it->second.first.transpose()<<endl;
            cout<<"exra g:"<<vpex_it->second.second<<endl;
            cout<<"exra t:"<<t_cost<<"  l t:"<<c_node->g_score_<<"  mn?:"<<int(c_node->motion_state_)<<endl;
        }

        iter++;
        // cout<<"tn:"<<ros::WallTime::now().toSec() - ts<<endl;
        // cout<<"t_thresh:"<<t_thresh<<endl;
        // cout<<"iter % 10:"<<iter % 10<<endl;
        // cout<<"find_target:"<<find_target<<endl;
        if(find_target && iter % 10 == 0 && ros::WallTime::now().toSec() - ts > t_thresh){ // search too long, not used most of time
            cout<<"search cost:"<<ros::WallTime::now().toSec() - ts<<endl;
            cout<<"t_thresh:"<<t_thresh<<endl;
            break;
        }

        if(c_node->g_score_ > max_g_score){ // no better target will be found
            break;
        }

        //expand
        Eigen::Vector3i diff(0, 0, 0);
        for(diff(0) = -1; diff(0) < 2; diff(0)++){
            for(diff(1) = -1; diff(1) < 2; diff(1)++){
                for(diff(2) = -1; diff(2) < 2; diff(2)++){
                    if(diff(0) == 0 && diff(1) == 0 && diff(2) == 0) continue;    //the same node
                    if(!LRM_->FeasibleMove(c_node->pos_, diff)) continue;
                    // if(lr_node == NULL || lr_node == LRM_->Outnode_) continue;    //bad lrnode
                    // if(lr_node->flags_[0]) continue;
                    lr_node = LRM_->GetNode(LRM_->IdtoPos(diff+c_node->pos_));
                    ep_node = lr_node->topo_sch_;
                    
                    if(ep_node == NULL){                         //create a new node
                        ep_node = make_shared<sch_node>();
                        ep_node->pos_ = c_node->pos_ + diff;
                        if(c_node->motion_state_ == 1) ep_node->g_score_ = c_node->g_score_ + diff.cast<double>().norm() * v_inv + mt + dect;
                        else if(c_node->motion_state_ == 2) ep_node->g_score_ = mt + diff.cast<double>().norm() * v_inv;
                        else ep_node->g_score_ = c_node->g_score_ + diff.cast<double>().norm() * v_inv;
                        ep_node->parent_ = c_node;
                        ep_node->status_ = in_open;
                        lr_node->topo_sch_ = ep_node;
                        node_list.push_back(ep_node);
                        open_set.push(ep_node);
                    }
                    else{                                       //new parent?
                        if(ep_node->status_ == in_close) continue;

                        double g_tmp;
                        if(c_node->motion_state_ == 1) g_tmp = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm() * v_inv + mt + dect + 1e-3;
                        else if(c_node->motion_state_ == 2) g_tmp = mt + diff.cast<double>().cwiseProduct(ns).norm() * v_inv + 1e-3;
                        else g_tmp = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm() * v_inv + 1e-3;

                        if(g_tmp < ep_node->g_score_){
                            ep_node->status_ = in_close;
                            ep_node = make_shared<sch_node>();/**/
                            lr_node->topo_sch_ = ep_node; /**/
                            ep_node->status_ = in_open;  /**/
                            ep_node->pos_ = c_node->pos_ + diff;/**/
                            // c_node->f_score_ = g_tmp + GetHue(c_node->pos_, std_end)*lambda_heu_;
                            if(c_node->motion_state_ == 1) ep_node->g_score_ = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm() * v_inv + mt + dect;
                            else if(c_node->motion_state_ == 2) ep_node->g_score_ = mt + diff.cast<double>().cwiseProduct(ns).norm() * v_inv;
                            else ep_node->g_score_ = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm() * v_inv;
                            ep_node->parent_ = c_node;
                            open_set.push(ep_node); /**/
                        }
                    }
                }
            }
        }
    }

    if(find_target){
        Eigen::Vector3d pe;
        list<Eigen::Vector3d> path_debug;
        if(!use_ex_vp){
            cout<<int(f_grid_[target.first].local_vps_[target.second])<<endl;
            cout<<int(GetVpPos(target.first, target.second, pe))<<endl;
            GetVp(target.first, target.second, tar_vp);
            if(best_node->motion_state_ != 0) find_target = 2;
        }
        else{
            std::cout << "\033[0;41m USE EXTRA \033[0m" << std::endl;
            find_target = 3;
        }

        RetrieveExpPath(path, path_debug, best_node, r_node);
        expect_t = best_cost;
        // Debug(path, 1);
        if(best_node->motion_state_ != 0 && r_node != best_node){ //debug
            ROS_ERROR("Error dj!");
            ros::shutdown();
        }

        
        if(MSl.size() != 0 && best_node->motion_state_ == 0) {
            if(r_node->motion_state_ == 2)
                FM_->RetrieveTraj(MSl, path, r_node->me_id_); // bug exists
            else{
                FM_->RetrieveTraj(MSl, path, r_node->m_id_); // bug exists
            }
        }
        else if(MSl.size() != 0) FM_->RetrieveTraj(MSl, path, r_node->m_id_);
        cout<<"ps:"<<ps.transpose()<<endl;
        cout<<"pe:"<<pe.transpose()<<endl;
        std::cout <<"\033[0;32mFind target:\033[0m" << std::endl;
    }
    else{
        int frontier_active = 0;
        int frontier_total_vps = 0;
        int frontier_unsampled_vps = 0;
        int frontier_alive_vps = 0;
        int frontier_dead_vps = 0;
        int active_total_vps = 0;
        int active_unsampled_vps = 0;
        int active_alive_vps = 0;
        int active_dead_vps = 0;
        for(auto &fg : f_grid_){
            const bool active = fg.f_state_ == 1;
            if(active) frontier_active++;
            frontier_total_vps += fg.local_vps_.size();
            if(active) active_total_vps += fg.local_vps_.size();
            for(auto &vp_state : fg.local_vps_){
                if(vp_state == 0){
                    frontier_unsampled_vps++;
                    if(active) active_unsampled_vps++;
                }
                else if(vp_state == 1){
                    frontier_alive_vps++;
                    if(active) active_alive_vps++;
                }
                else if(vp_state == 2){
                    frontier_dead_vps++;
                    if(active) active_dead_vps++;
                }
            }
        }
        ROS_WARN(
            "no target diag: iter=%d init=%zu motion=%zu vp_dict=%zu vp_node_hits=%d vp_refs=%d state_filtered=%d positive_gain=%d strong_rejected=%d extra_hits=%d frontier_active=%d total_vps=%d all_vps[pending=%d alive=%d dead=%d] active_vps[total=%d pending=%d alive=%d dead=%d]",
            iter, init_list.size(), MSl.size(), vp_dict_.size(), vp_node_hits, vp_ref_count,
            vp_state_filtered, vp_positive_gain, vp_strong_rejected, extra_vp_hits,
            frontier_active, frontier_total_vps,
            frontier_unsampled_vps, frontier_alive_vps, frontier_dead_vps,
            active_total_vps, active_unsampled_vps, active_alive_vps, active_dead_vps);
        ROS_WARN("no target");
    }
    ClearSearched(node_list);
    return find_target;
}


int FrontierGrid::FindPath(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector4d &target_pose, 
                                    list<Eigen::Vector3d> &path, double yaws, double yawvs,
                                    double yawv, double yawa, double vel, double &expect_t){
    vector<shared_ptr<sch_node>> node_list; //to maintain nodes 
    bool find_target = false;
    if(!LRM_->IsFeasible(ps)){
        // FreeWorker(workid, node_list);
        cout<<LRM_->IsFeasible(ps)<<endl;
        ROS_WARN("error IsFeasible");
        return find_target;
    }
    list<Eigen::Vector3d> debug_pts;
    vector<pair<double, double>> g_searched;
    priority_queue<shared_ptr<sch_node>, vector<shared_ptr<sch_node>>, DCompare> open_set;
    shared_ptr<sch_node> c_node, ep_node, best_node;
    shared_ptr<LR_node> lr_node;
    double max_g_score = 9999999.0;
    double best_gain = 0.0;
    double best_dyaw;
    Eigen::Vector3d vp_pos;
    Eigen::Vector3i std_start;
    Vector3d vdir = vs.normalized();
    LRM_->PostoId3(ps, std_start);
    int target_id = LRM_->PostoId(target_pose.head(3));
    Eigen::Vector3d ns = LRM_->node_scale_;

    c_node = make_shared<sch_node>();
    c_node->pos_ = std_start;
    c_node->g_score_ = 0;
    node_list.push_back(c_node);
    lr_node = LRM_->GetNode(LRM_->IdtoPos(c_node->pos_));
    if(lr_node == NULL || lr_node == LRM_->Outnode_) ROS_WARN("ERROR Search"); //debug
    lr_node->topo_sch_ = c_node;
    open_set.push(c_node);
    // cout<<"vp_dict_:"<<vp_dict_.size()<<endl;
    while(!open_set.empty()){
        c_node = open_set.top();
        open_set.pop();
        if(c_node->status_ == in_close) continue;/**/
        c_node->status_ = in_close;

        // check if the vp is the best
        int n_id = LRM_->Id3toId(c_node->pos_);
        if(target_id == n_id){

            Eigen::Vector3d pe = target_pose.head(3);
            list<Eigen::Vector3d> path_debug;

            RetrieveExpPath(ps, pe, path, path_debug, c_node);
            expect_t = c_node->g_score_;
            find_target = 1;
            break;
        }
        //expand
        Eigen::Vector3i diff(0, 0, 0);
        for(diff(0) = -1; diff(0) < 2; diff(0)++){
            for(diff(1) = -1; diff(1) < 2; diff(1)++){
                for(diff(2) = -1; diff(2) < 2; diff(2)++){
                    if(diff(0) == 0 && diff(1) == 0 && diff(2) == 0) continue;    //the same node
                    if(!LRM_->FeasibleMove(c_node->pos_, diff)) continue;
                    // if(lr_node == NULL || lr_node == LRM_->Outnode_) continue;    //bad lrnode
                    // if(lr_node->flags_[0]) continue;
                    lr_node = LRM_->GetNode(LRM_->IdtoPos(diff+c_node->pos_));
                    ep_node = lr_node->topo_sch_;
                    
                    if(ep_node == NULL){                         //create a new node
                        ep_node = make_shared<sch_node>();
                        ep_node->pos_ = c_node->pos_ + diff;
                        ep_node->g_score_ = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm() ;// + LRM_->GetDist(diff(0), diff(1), diff(2));
                        ep_node->parent_ = c_node;
                        ep_node->status_ = in_open;
                        lr_node->topo_sch_ = ep_node;
                        node_list.push_back(ep_node);
                        open_set.push(ep_node);
                    }
                    else{                                       //new parent?
                        if(ep_node->status_ == in_close) continue;

                        double g_tmp = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm()  + 0.0001;// + GetDist(diff(0), diff(1), diff(2));
                        // double f_tmp = g_tmp + GetHue(c_node->pos_, std_end)*lambda_heu_*1.001;
                        if(g_tmp < ep_node->g_score_){
                            ep_node->status_ = in_close;
                            ep_node = make_shared<sch_node>();/**/
                            lr_node->topo_sch_ = ep_node; /**/
                            ep_node->status_ = in_open;  /**/
                            ep_node->pos_ = c_node->pos_ + diff;/**/
                            // c_node->f_score_ = g_tmp + GetHue(c_node->pos_, std_end)*lambda_heu_;
                            ep_node->g_score_ = g_tmp;
                            ep_node->parent_ = c_node;
                            open_set.push(ep_node); /**/
                        }
                    }
                }
            }
        }
    }
    
    
    ClearSearched(node_list);
    return find_target;
}

int FrontierGrid::FindMotionPath(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as, 
                        const Eigen::Vector4d &target_pose, 
                        list<Eigen::Vector3d> &path, double &expect_t, double yaws, double yawvs, double yawv, 
                        double yawa, double vel, double acc, double max_range, double t_thresh){
    if(!LRM_->IsFeasible(ps)){
        // FreeWorker(workid, node_list);
        cout<<LRM_->IsFeasible(ps)<<endl;
        ROS_WARN("error IsFeasible");
        return 0;
    }
    list<int> init_list;
    vector<MotionStateF> MSl;
    double mt;
    double ts = ros::WallTime::now().toSec();
    double dect = vs.norm() / acc;
    double best_cost;
    FM_->InitMotion(ps, vs, as, mt, init_list, MSl);
    vector<pair<double, double>> g_searched;
    vector<shared_ptr<sch_node>> node_list; //to maintain nodes 

    priority_queue<shared_ptr<sch_node>, vector<shared_ptr<sch_node>>, DCompare> open_set;
    shared_ptr<sch_node> c_node, ep_node, best_node, r_node;
    shared_ptr<LR_node> lr_node;
    double v_inv = 1.0 / vel;
    int find_target = 0;
    // bool out_motion;
    double max_g_score = 9999999.0;
    double best_gain = 0.0;
    int iter = 0;
    list<Eigen::Vector3d> debug_pts;
    Eigen::Vector3d ns = LRM_->node_scale_;
    int target_id = LRM_->PostoId(target_pose.head(3));
    // cout<<"init_list num:"<<init_list.size()<<endl;
    for(auto &i : init_list){
        lr_node = LRM_->GetNode(i);
        open_set.push(lr_node->topo_sch_);
        node_list.push_back(lr_node->topo_sch_);
    }

    while(!open_set.empty()){
        c_node = open_set.top();
        open_set.pop();
        if(c_node->status_ == in_close) continue;/**/
        c_node->status_ = in_close;

        if(c_node->g_score_ > max_range){
            break;
        }

        // check if the vp is the best
        int n_id = LRM_->Id3toId(c_node->pos_);
        if(target_id == n_id){
            list<Eigen::Vector3d> path_debug;
            // cout<<"iter:"<<iter<<endl;
            // cout<<"mt:"<<mt<<endl;
            expect_t = c_node->g_score_;
            best_node = c_node;
            RetrieveExpPath(path, path_debug, best_node, r_node);
            if(MSl.size() != 0 && best_node->motion_state_ == 0) {
                if(r_node->motion_state_ == 2)
                    FM_->RetrieveTraj(MSl, path, r_node->me_id_); // bug exists
                else{
                    FM_->RetrieveTraj(MSl, path, r_node->m_id_); // bug exists
                }
            }
            else if(MSl.size() != 0) FM_->RetrieveTraj(MSl, path, r_node->m_id_);
            find_target = 1;
            break;
        }


        iter++;
        //expand
        Eigen::Vector3i diff(0, 0, 0);
        for(diff(0) = -1; diff(0) < 2; diff(0)++){
            for(diff(1) = -1; diff(1) < 2; diff(1)++){
                for(diff(2) = -1; diff(2) < 2; diff(2)++){
                    if(diff(0) == 0 && diff(1) == 0 && diff(2) == 0) continue;    //the same node
                    if(!LRM_->FeasibleMove(c_node->pos_, diff)) continue;
                    // if(lr_node == NULL || lr_node == LRM_->Outnode_) continue;    //bad lrnode
                    // if(lr_node->flags_[0]) continue;
                    lr_node = LRM_->GetNode(LRM_->IdtoPos(diff+c_node->pos_));
                    ep_node = lr_node->topo_sch_;
                    
                    if(ep_node == NULL){                         //create a new node
                        ep_node = make_shared<sch_node>();
                        ep_node->pos_ = c_node->pos_ + diff;
                        if(c_node->motion_state_ == 1) ep_node->g_score_ = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm() * v_inv + mt + dect;
                        else if(c_node->motion_state_ == 2) ep_node->g_score_ = mt + diff.cast<double>().cwiseProduct(ns).norm() * v_inv;
                        else ep_node->g_score_ = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm() * v_inv;
                        ep_node->parent_ = c_node;
                        ep_node->status_ = in_open;
                        lr_node->topo_sch_ = ep_node;
                        node_list.push_back(ep_node);
                        open_set.push(ep_node);
                    }
                    else{                                       //new parent?
                        if(ep_node->status_ == in_close) continue;

                        double g_tmp;
                        if(c_node->motion_state_ == 1) g_tmp = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm() * v_inv + mt + dect + 1e-3;
                        else if(c_node->motion_state_ == 2) g_tmp = mt + diff.cast<double>().cwiseProduct(ns).norm() * v_inv + 1e-3;
                        else g_tmp = c_node->g_score_ + diff.cast<double>().cwiseProduct(ns).norm() * v_inv + 1e-3;

                        if(g_tmp < ep_node->g_score_){
                            ep_node->status_ = in_close;
                            ep_node = make_shared<sch_node>();/**/
                            lr_node->topo_sch_ = ep_node; /**/
                            ep_node->status_ = in_open;  /**/
                            ep_node->pos_ = c_node->pos_ + diff;/**/
                            // c_node->f_score_ = g_tmp + GetHue(c_node->pos_, std_end)*lambda_heu_;
                            if(c_node->motion_state_ == 1) ep_node->g_score_ = c_node->g_score_ + diff.cast<double>().norm() * v_inv + mt + dect;
                            else if(c_node->motion_state_ == 2) ep_node->g_score_ = mt + diff.cast<double>().norm() * v_inv;
                            else ep_node->g_score_ = c_node->g_score_ + diff.cast<double>().norm() * v_inv;
                            ep_node->parent_ = c_node;
                            open_set.push(ep_node); /**/
                        }
                    }
                }
            }
        }
    }
    
    ClearSearched(node_list);
    return find_target;
}

bool FrontierGrid::FindSecondTarget(const int &f_id, const int &v_id, const double &v, const double &dy, Eigen::Vector4d &sec_vp){
    Eigen::Vector4d fir_vp;
    if(!GetVp(f_id, v_id, fir_vp) || f_grid_[f_id].local_vps_[v_id] != 1){
        ROS_ERROR("error get vp FindSecondTarget!");
        ros::shutdown();
        return false;
    }
    vector<vector<double>> dist_img;
    Eigen::Vector3d uc;
    // ROS_WARN("FindSecondTarget0");
    GetVGain(f_id, v_id, dist_img, uc);
    // Debug(uc, -2);

    // if((uc - fir_vp.head(3)).norm() > 5.0){
    //     ROS_ERROR("error uc");
    //     cout<<"d:"<<(uc - fir_vp.head(3)).norm()<<endl;
    //     cout<<"uc:"<<uc.transpose()<<endl;
    //     cout<<"fir_vp:"<<fir_vp.transpose()<<endl;
    //     getchar();
    // }
    // ROS_WARN("FindSecondTarget1");

    list<Eigen::Vector3d> line;
    list<Eigen::Vector3d> debug_pts;
    bool find_second = false;
    double best_gain = 0.0;

    /* get vp in the first target EROI */
    Eigen::Vector3d fir_vp_pos = LRM_->GetStdPos(fir_vp.head(3)), last_feasible = LRM_->GetStdPos(fir_vp.head(3));
    fir_vp.head(3) = fir_vp_pos;
    bool uvp = false;
    VoxelState vs;
    LRM_->GetCastLine(fir_vp_pos, uc, line);// to most promising space
    while(!line.empty()){
        // vs = BM_->GetVoxState(line.front());
        // if(vs == VoxelState::unknown || vs == VoxelState::occupied || vs == VoxelState::out || (fir_vp_pos - line.front()).norm() > second_dist_thresh_){
        if(!LRM_->IsFeasible(line.front()) || (fir_vp_pos - line.front()).norm() > second_dist_thresh_){
            break;
        }
        uvp = true;
        last_feasible = line.front();
        line.pop_front();
    }
    // Debug(last_feasible, -3);

    double best_yaw, g_0;
    double dist_cost, yaw_cost;
    if(uvp && (last_feasible - fir_vp_pos).norm() > second_distmin_thresh_){
        g_0 = SampleBestYawSubmod(dist_img, last_feasible, best_yaw, fir_vp, v, dy);
        // cout<<"g_0:"<<g_0<<endl;
        if(g_0 > 1e-3){
            // yaw_cost = abs(YawDiff(best_yaw, fir_vp(3))) / dy;
            // dist_cost = (last_feasible - fir_vp_pos).norm() / v;
            best_gain = g_0;// * exp(-lambda_ * max(yaw_cost, dist_cost));
            sec_vp(3) = best_yaw;
            sec_vp.head(3) = last_feasible;
            debug_pts.emplace_back(last_feasible);
            // cout<<"sec_vp1:"<<sec_vp.transpose()<<endl;
            // cout<<"best_gain:"<<best_gain<<endl;
            find_second = true;
        }
    }

    /* Get near exist vp gain */
    int it;
    Eigen::Vector3i n(1, node_num_(0), node_num_(0) * node_num_(1)), it3;
    Eigen::Vector4d vp_pose;
    Eigen::Vector3d y_norm(cos(vp_pose(3)), sin(vp_pose(3)), 0);
    n(0) = f_id % node_num_(0);
    n(1) = ((f_id - n(0))/node_num_(0)) % node_num_(1);
    n(2) = ((f_id - n(0)) - n(1)*node_num_(0))/node_num_(1)/node_num_(0);
    // it3(0) = 
    for(int x = -1; x < 2; x++){
        it3(0) = n(0) + x;
        if(it3(0) < 0 || it3(0) >= node_num_(0)) continue;
        for(int y = -1; y < 2; y++){
            it3(1) = n(1) + y;
            if(it3(1) < 0 || it3(1) >= node_num_(1)) continue;
            for(int z = -1; z < 2; z++){
                it3(2) = n(2) + z;
                if(it3(2) < 0 || it3(2) >= node_num_(2)) continue;
                it = it3(2)*node_num_(0)*node_num_(1) + it3(1)*node_num_(0) + it3(0);
                for(int vi = 0; vi < samp_num_; vi++){
                    if(!GetVp(it, vi, vp_pose, true) || f_grid_[it].local_vps_[vi] != 1) continue;
                    dist_cost = (vp_pose.head(3) - fir_vp_pos).norm();
                    if(y_norm.dot((vp_pose.head(3) - fir_vp_pos).normalized()) < 0.3) continue;
                    // double y = atan2(fir_vp(1) - vp_pose(1), fir_vp(0) - vp_pose(0));
                    // if(abs(YawDiff(vp_pose(3), y)) > 0.75) continue;
                    yaw_cost = abs(YawDiff(vp_pose(3), fir_vp(3)));
                    if(dist_cost > second_distmin_thresh_ && dist_cost < second_dist_thresh_ && yaw_cost < second_yaw_thresh_ && f_grid_[it].gains_[vi] > second_gain_thresh_){
                        if(!LRM_->FeasibleLine(fir_vp_pos, vp_pose.head(3))) continue;

                        debug_pts.emplace_back(vp_pose.head(3));
                        g_0 = GetVGainSubmod(it, vi, dist_img, fir_vp);
                        
                        if(g_0 < second_gain_thresh_) continue;
                        g_0 = g_0 * exp(-lambda_ * max(yaw_cost/dy, dist_cost/v));
                        if(g_0 > best_gain){
                            best_gain = g_0;
                            sec_vp = vp_pose;
                            // cout<<"sec_vp2:"<<sec_vp.transpose()<<endl;
                            // cout<<"best_gain:"<<best_gain<<endl;
                            find_second = true;
                        }
                    }
                    // else{
                    //     cout<<"it:"<<it<<"   vi:"<<vi<<endl;
                    //     cout<<"dist_cost:"<<dist_cost<<"   second_dist_thresh_:"<<second_dist_thresh_<<endl;
                    //     cout<<"yaw_cost:"<<yaw_cost<<"   second_yaw_thresh_:"<<second_yaw_thresh_<<endl;
                    //     cout<<"gain:"<<f_grid_[it].gains_[vi]<<"   second_gain_thresh_:"<<second_gain_thresh_<<endl;
                    // }
                }
            }
        }
    }
    // cout<<"checked num:"<<debug_pts.size()<<endl;
    // Debug(debug_pts, -1);
    // if(find_second) getchar();
    return find_second;

    // for(int dim = 0; dim < 3; dim++){
    //     for(int dir = -1; dir < 3; dir +=2){
    //         int it = f_id + dir*n(dim);
    //         if(it < f_grid_.size() && it >= 0 && f_grid_[it].f_state_ != 2){
    //             if(f_grid_[it].f_state_ == 0) gain += f_grid_[it].unknown_num_ * g_factor_ * v;
    //             else if(f_grid_[it].f_state_ == 1){
    //                 for(auto &v : f_grid_[it].local_vps_){
    //                     if(!GetVpPos(it, v, vp)) continue;
    //                     if(LRM_->FeasibleLine(tar_vp, vp)){
    //                         gain += f_grid_[it].unknown_num_ * g_factor_ * v;
    //                         break;
    //                     }
    //                 }
    //             }
    //         }
    //     }
    // }

}


void FrontierGrid::MotionInitDijkstraDebug(Eigen::Vector3d p){
    Eigen::Matrix3d W2S, S2W; // world to sample 
    int id;
    Eigen::Vector3d vs, as;
    vs.setZero();
    as.setZero();
    // FM_->GetTansMatrix(vs, as, S2W, id);
    tr1::unordered_map<int, bool> motion_states;
    priority_queue<shared_ptr<sch_node>, vector<shared_ptr<sch_node>>, DCompare> open_set;
    vector<shared_ptr<sch_node>> node_list; //to maintain nodes 
    

}

void FrontierGrid::SampleExtraVps(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as, const double vel, const double acc,
                        const double yaws, const double yawvs, const double yawv, const double yawa, 
                            tr1::unordered_map<int, pair<Eigen::Vector4d, double>> &vp_dict){
    if(vs.norm() < vel * 0.01) return;
    double t0 = ros::WallTime::now().toSec();
    Eigen::Vector3d vn = vs.normalized();
    list<Eigen::Vector3d> samples;
    // samples.emplace_back(vn);
    Eigen::Vector3d perpen_dir = vn + Eigen::Vector3d(1,0,0);
    perpen_dir = perpen_dir - vn * perpen_dir.dot(vn);
    Eigen::Vector3d d_it;
    for(double dir = -M_PI; dir < M_PI; dir += M_PI*0.35){
        d_it(0) = cos(dir);
        d_it(1) = sin(dir);
        d_it(2) = 0;
        samples.emplace_back(d_it);
    }
    for(int x = 0; x < 2; x++){
        for(int y = 0; y < 2; y++){
        }
    }

    Eigen::Vector3d vp_pos;
    list<Eigen::Vector4d> vps;
    while(ros::WallTime::now().toSec() - t0 < 0.005 && !samples.empty()){
        Eigen::Vector3d samp_p = samples.front().normalized() * sensor_range_ * 0.75 + ps;
        list<Eigen::Vector3d> ray;
        samples.pop_front();
        BM_->GetCastLine(ps, samp_p, ray);
        for(auto &p : ray){
            if(LRM_->IsFeasible(p)){
                vp_pos = p;
                vp_pos = LRM_->GetStdPos(vp_pos);
            }
            else{
                break;
            }
        }
        if(!ViewpointZAllowed(vp_pos)) continue;
        int id = LRM_->PostoId(vp_pos);
        if(vp_dict.find(id) != vp_dict.end() || (vp_pos - ps).norm() < 1.0) continue;
        double dy_thresh = (vp_pos - ps).norm() / (vel + vs.norm()) * 2 * yawv;
        double best_yaw;
        double gain = SampleBestYaw(vp_pos, best_yaw, yaws, dy_thresh);
        if(gain < second_gain_thresh_) continue; // gain too low
        else{
            Eigen::Vector4d vp(vp_pos(0), vp_pos(1), vp_pos(2), best_yaw);
            vps.emplace_back(vp);
            vp_dict.insert({id,{vp, gain}});
        }
    }
    DrawFOVs(vps);
    
}
