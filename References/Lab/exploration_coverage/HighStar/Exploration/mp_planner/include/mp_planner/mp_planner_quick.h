#ifndef MP_PLANNER_QUICK_H_
#define MP_PLANNER_QUICK_H_
#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/Dense>
#include <vector>
#include <fstream>
#include <iostream>
#include <ros/ros.h>
#include <list>
#include <tr1/unordered_map>
#include <memory>
#include <math.h>

#include <block_map/block_map.h>
#include <lowres_map/lowres_map.h>
#include <kdtree/kdtree.h>

#include <visualization_msgs/MarkerArray.h>
#include <nav_msgs/Odometry.h>
using namespace std;
using namespace lowres;

struct FM{
    Eigen::Vector3d pe_, ve_;
    int parent_;
    uint8_t flag_layer_; // 00(1 = checked)(1 = feasible, 0 = infeasible)[flags] 0000[layer]
    uint16_t aid_;
};

struct MotionStateF{
    Eigen::Vector3d p_;
    Eigen::Vector3d v_;
    Eigen::Vector3d a_;

    int id_;
    int parent_id_;
    list<int> path_;
    uint8_t layer_;                 
};

class FastMotion{
public:
    FastMotion(){};
    ~FastMotion(){
        // ROS_WARN("")
        for(auto &tree : kdTrees_){
            kd_free(tree);
        }
    };
    
    void init(ros::NodeHandle &nh, ros::NodeHandle &nh_private);

    void SetLowResMap(lowres::LowResMap *lrm){LRM_ = lrm;}
    void InitMotion(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as, double &max_t, list<int> &covered_nodes, vector<MotionStateF> &MSl);
    void RetrieveTraj(vector<MotionStateF> &MSl, list<Eigen::Vector3d> &path, const int &m_id);
    void VisMotions(vector<MotionStateF> &MSl);

    void SampleVis();
    inline bool MotionCheck(Eigen::Matrix3d &param);
    inline bool MotionCheck(Eigen::Matrix3d &param, list<pair<int, double>> &traj_ids, bool debug = false);

    vector<vector<FM>> motions_;

private:

    void VisMotionDebug(const int id, const int m_id, list<Eigen::Vector3d> &path, Eigen::Vector3d p0, Eigen::Matrix3d R);


    void inline SetTrajCost(list<pair<int, double>> &traj_ids, list<int> &covered_nodes, const int &m_id, const int &layer);


    /**
     * @brief check if the input is feasible
     * 
     * @param vs        start velocity 
     * @param a_inp     acc input
     * @param max_v   max_v_/max_dy_
     * @param max_da    da_/max_dddy_
     * @param ve        end velocity
     * @return true     
     * @return false 
     */
    inline bool FeasibleInput(const double &vs, const double &a_inp);
    inline bool GetInput(const MotionStateF &s, const int &input_dir, const int dim, double &input);

    // void PreSample(int id, Eigen::Vector3d v0, Eigen::Vector3d a0); 
    inline bool TrajCheck(const int &id, const int &m_id, const Eigen::Vector3d &p0, const Eigen::Matrix3d &R, list<int> &checked_list);
    lowres::LowResMap *LRM_;

    vector<kdtree*> kdTrees_;
    vector<Eigen::Vector3d> acc_samp_;
    vector<pair<double, Eigen::Vector3d>> vas_; // vel: (v, 0, 0), acc(ax, ay, az)
    vector<int> vids_, aids_, dids_;

    Eigen::Vector3d origin_a_, acc_max_;
    Eigen::Vector3i acc_num3_;
    bool vis_motion_;
    double dt_;
    double max_a_, max_v_, da_, dv_;//, dpsi_;
    int vel_num_, acc_num_, dir_num_, sample_depth_;

    // double vel_fac_;
    ros::Publisher debug_pub_, debug_pub2_;
};

void inline FastMotion::SetTrajCost(list<pair<int, double>> &traj_ids, list<int> &covered_nodes, const int &m_id, const int &layer){
    shared_ptr<LR_node> lr_node;
    for(auto &tr : traj_ids){
        lr_node = LRM_->GetNode(tr.first);
        // cout<<"lr_node:"<<(lr_node == NULL)<<endl;
        if(lr_node->topo_sch_ == NULL){
            lr_node->topo_sch_ = make_shared<sch_node>();
            lr_node->topo_sch_->g_score_ = tr.second + layer * dt_;
            LRM_->PostoId3(LRM_->IdtoPos(tr.first), lr_node->topo_sch_->pos_);
            lr_node->topo_sch_->parent_ = NULL;
            lr_node->topo_sch_->motion_state_ = 1;
            lr_node->topo_sch_->m_id_ = m_id;
            if(m_id == 0) lr_node->topo_sch_->me_id_ = 0; // initial motion
            else lr_node->topo_sch_->me_id_ = -1;
            covered_nodes.emplace_back(tr.first);
        }
        else{
            if(lr_node->topo_sch_->g_score_ > tr.second + layer * dt_ + 1e-3){
                lr_node->topo_sch_->m_id_ = m_id;
                lr_node->topo_sch_->g_score_ = tr.second + layer * dt_;
            }
        }
    }
}

inline bool FastMotion::TrajCheck(const int &id, const int &m_id, const Eigen::Vector3d &p0, const Eigen::Matrix3d &R, list<int> &checked_list){
    int c_id = m_id;
    Eigen::Vector3d p, v, a;
    Eigen::Matrix3d param;
    while(c_id != -1){
        if(motions_[id][c_id].flag_layer_ & 32 && motions_[id][c_id].flag_layer_ & 16){
            // continue;
        }
        else if(motions_[id][c_id].flag_layer_ & 32){
            // cout<<"1c_id:"<<c_id<<endl;
            return false;
        }
        else{
            a = acc_samp_[motions_[id][c_id].aid_];
            v = motions_[id][c_id].ve_ - dt_ * a;
            p = motions_[id][c_id].pe_ - dt_ * v - 0.5 * dt_ * dt_ * a;
            param.col(2) = R * a * 0.5;
            param.col(1) = R * v;
            param.col(0) = R * p + p0;
            checked_list.emplace_back(c_id);
            if(MotionCheck(param)){
                motions_[id][c_id].flag_layer_ |= 48;
            }
            else{
                motions_[id][c_id].flag_layer_ |= 32;
                // cout<<"2c_id:"<<c_id<<endl;
                return false;
            }
        }
        // cout<<"c_id1:"<<c_id<<endl;
        c_id = motions_[id][c_id].parent_;
        // cout<<"c_id2:"<<c_id<<endl;
    }
    return true;
}

inline bool FastMotion::MotionCheck(Eigen::Matrix3d &param){
    double t = 0;
    Eigen::MatrixXd bd;
    Eigen::Vector3d ts, p, a1_2;
    list<double> t_debug;
    for(int dim = 0; dim < 3; dim++) a1_2(dim) = param(dim, 1)*param(dim, 1);
    bool debug_flag = false;

    while(t < dt_){
        // double tc = dt_;
        p = param.col(0) + param.col(1) * t + param.col(2) * t * t;
        t_debug.emplace_back(t);

        if(!LRM_->IsFeasible(p)) {
            // cout<<"p:"<<p.transpose()<<endl;
            return false;
        }

        /* get the t of crossing bound */
        LRM_->GetBound(p, bd);
        bd.col(0) += p - param.col(0);
        bd.col(1) += p - param.col(0);
        int max_dim = 0;
        double max_t = 0;
        for(int dim = 0; dim < 3; dim++){
            ts(dim) = dt_ + 1e-5;
            for(int i = 0; i < 2; i++){
                if(abs(param(dim, 2)) > 1e-5){
                    double delta = a1_2(dim) + 4*param(dim, 2)*bd(dim, i);
                    if(delta < 0) continue;
                    else{
                        double t1, t2;
                        double s_delta = sqrt(delta);
                        t1 = (-param(dim, 1) - sqrt(delta)) / (2 * param(dim, 2));
                        t2 = (-param(dim, 1) + sqrt(delta)) / (2 * param(dim, 2));
                        if(t1 > t && t1 < ts(dim)) ts(dim) = t1;
                        if(t2 > t && t2 < ts(dim)) ts(dim) = t2;
                    }
                }
                else{
                    if(abs(param(dim, 1)) < 1e-3) continue;
                    double t1 = bd(dim, i) / param(dim, 1);
                    if(t1 > t && t1 < dt_) ts(dim) = t1;
                }
            }
            if(ts(dim) > max_t) {
                max_t = ts(dim);
                max_dim = dim;
            }
        }

        /* update t */
        t = 0;
        for(int dim = 0; dim < 3; dim++){
            if(dim == max_dim) continue;
            t += ts(dim) / 2;
        }
    }
    return true;
}

inline bool FastMotion::MotionCheck(Eigen::Matrix3d &param, list<pair<int, double>> &traj_ids, bool debug){
    traj_ids.clear();
    double t = 0;
    double tc = 0;
    Eigen::MatrixXd bd;
    Eigen::Vector3d ts, p, a1_2;
    // list<double> t_debug;
    for(int dim = 0; dim < 3; dim++) a1_2(dim) = param(dim, 1)*param(dim, 1);
    Eigen::Vector3d pe = param.col(0) + param.col(1) * dt_ + param.col(2) * dt_ * dt_;

    if(!LRM_->IsFeasible(pe)) {
        // cout<<"pe:"<<pe.transpose()<<endl;
        return false;
    }
    int e_id = LRM_->PostoId(pe);

    while(t < dt_){
        // double tc = dt_;
        p = param.col(0) + param.col(1) * t + param.col(2) * t * t;
        // t_debug.emplace_back(t);

        if(!LRM_->IsFeasible(p)) {
            // cout<<"p:"<<p.transpose()<<endl;
            // cout<<"t:"<<t<<endl;
            return false;
        }
        int p_id = LRM_->PostoId(p);
        traj_ids.push_back({p_id, t});
        /* get the t of crossing bound */
        LRM_->GetBound(p, bd);
        bd.col(0) += p - param.col(0);
        bd.col(1) += p - param.col(0);
        int max_dim = 0;
        double max_t = 0, min_t = 999;
        for(int dim = 0; dim < 3; dim++){
            ts(dim) = dt_ + 1e-5;
            for(int i = 0; i < 2; i++){
                if(abs(param(dim, 2)) > 1e-5){
                    double delta = a1_2(dim) + 4*param(dim, 2)*bd(dim, i);
                    if(delta < 0) continue;
                    else{
                        double t1, t2;
                        double s_delta = sqrt(delta);
                        t1 = (-param(dim, 1) - sqrt(delta)) / (2 * param(dim, 2));
                        t2 = (-param(dim, 1) + sqrt(delta)) / (2 * param(dim, 2));
                        if(t1 > t && t1 < ts(dim)) ts(dim) = t1;
                        if(t2 > t && t2 < ts(dim)) ts(dim) = t2;
                    }
                }
                else{
                    if(abs(param(dim, 1)) < 1e-3) continue;
                    double t1 = bd(dim, i) / param(dim, 1);
                    if(t1 > t && t1 < dt_) ts(dim) = t1;
                }
            }
            if(ts(dim) < min_t) {
                min_t = ts(dim);
                // max_dim = dim;
            }
            if(tc < ts(dim)){
                tc = ts(dim) + 1e-5;
            }
        }

        /* update t */
        t = min_t + 1e-5;
        // for(int dim = 0; dim < 3; dim++){
        //     if(dim == max_dim) continue;
        //     t += ts(dim) / 2;
        // }
    }
    if(traj_ids.back().first != e_id){
        traj_ids.push_back({e_id, dt_});
    }
    return true;
}

inline bool FastMotion::GetInput(const MotionStateF &s, const int &input_dir, const int dim, double &input){
    if(input_dir == 0){
        input = s.a_(dim);
        return FeasibleInput(s.v_(dim), s.a_(dim));
    }
    bool success = false;
    double inp_temp = s.a_(dim) + da_ * input_dir;
    inp_temp = min(max(inp_temp, -max_a_), max_a_);
    double d_inp = inp_temp - s.a_(dim);
    for(double i = 10; i > 4.9; i -= 1.0){
        input = i / 10.0 * d_inp + s.a_(dim);
        if(FeasibleInput(s.v_(dim), input)){
            success = true;
            break;
        }
    }
    return success;
}

inline bool FastMotion::FeasibleInput(const double &vs, const double &a_inp){
    double ve = vs + a_inp * dt_;
    if(abs(ve) > max_v_) return false;
    int dec_n = floor(abs(a_inp) / da_);
    if(ve * a_inp < 0) return true;
    double ve_f = abs(ve) + (abs(a_inp) * 2 - (dec_n + 1) * da_) * dt_ * (dec_n) / 2;// ve future
    if(abs(ve_f) > max_v_) return false;
    return true;
}

#endif