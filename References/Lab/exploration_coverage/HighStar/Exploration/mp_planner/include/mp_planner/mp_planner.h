#ifndef MP_PLANNER_H_
#define MP_PLANNER_H_
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
using namespace std;
struct MotionState{
    // Eigen::Vector3d inp_a_; //input at parent state
    Eigen::Vector3d p_;
    Eigen::Vector3d v_;
    Eigen::Vector3d a_;
    // double yaw_;
    double yawd_up_, yawd_down_;
    double yawdd_up_, yawdd_down_;
    double yaw_up_, yaw_down_;    // yaw range
    int id_;
    int parent_id_;
    list<int> co_parents_;      // those whose hashes are the same
    int layer_;
    uint8_t flags_;                 //0000 0(feasible)(leaf state)(every yaw avilable)
};


class MotionPrimitivePlanner{
public:
    MotionPrimitivePlanner(){};
    ~MotionPrimitivePlanner(){};
    void init(ros::NodeHandle &nh, ros::NodeHandle &nh_private);
    void SetLowResMap(lowres::LowResMap *lrm){LRM_ = lrm;}
    /**
     * @brief clear data, perpare for a new plan
     * 
     * @param ms initial motion state
     */
    void Reset(MotionState &ms);

    /**
     * @brief sample motion
     * 
     */
    void Plan();

    /**
     * @brief show the motion
     * 
     */
    void Show();

    /**
     * @brief Get the Motion Cost of following a path 
     * 
     * @param path 
     * @param cost 
     * @param yaw_up 
     * @param yaw_down 
     * @param yaw_require if yaw required 
     * @return int 0: reach end, 1: not reach end but work, 2: path in unsearched space 
     */
    int GetCost(list<Eigen::Vector3d> &path, const double &yaw_up, const double &yaw_down, double &cost, bool yaw_require = false);

    /**
     * @brief nomalize yaw in [-pi, pi]
     * 
     * @param yaw [-oo, +oo]
     */
    inline void YawNorm(double &yaw);

    /**
     * @brief yaw1 - yaw2
     * 
     * @param yaw1 
     * @param yaw2 
     * @return double 
     */
    inline double YawDiff(const double &yaw1, const double &yaw2);
    
    inline bool YawIntersect(MotionState &ms, const double &up, const double &down);

    /**
     * @brief Get the Bbx of all motions
     * 
     * @param c     box center
     * @param box   box scale
     */
    inline void GetBbx(Eigen::Vector3d &c, Eigen::Vector3d &box);

    /**
     * @brief check if the input is feasible
     * 
     * @param vs        start velocity 
     * @param a_inp     acc input
     * @param max_v   max_v_/max_dy_
     * @param max_da    max_da_/max_dddy_
     * @param ve        end velocity
     * @return true     
     * @return false 
     */
    inline bool FeasibleInput(const double &vs, const double &a_inp, const double &max_v, const double &max_da, double &ve);
    // kdtree *kdTree_;
private:
    /**
     * @brief check if state is feasible after safe_step search using dfs 
     * 
     * @param mc start motion state
     * @param layer depth
     * @return true     safe
     * @return false    unsafe
     */
    bool DepthFirstCheck(MotionState &mc, int layer); 



    inline bool FeasibleInputDebug(const double &vs, const double &a_inp, const double &max_v, const double &max_da, double &ve);

    /**
     * @brief start + input --> end, check if the input imposed on start motion is feasible
     * 
     * @param ms    start motion state 
     * @param me    end motion state
     * @param inp3 
     * @return true 
     * @return false 
     */
    inline bool MotionForward(MotionState &ms, MotionState &me, Eigen::Vector3d &inp3, bool debug = false);

    /**
     * @brief update the yaw range
     * 
     * @param ms start motion state
     * @param me end motion state
     * @return int    0: not every yaw avilable, 1: every yaw avilable, 2: error down, 3: error up
     */
    inline int YawMotionForward(MotionState &ms, MotionState &me);

    /**
     * @brief get hash key
     * 
     * @param m 
     * @return int key
     */
    inline int Motion2Key(MotionState &m);

    inline int Position2Key(Eigen::Vector3d &p);

    // inline double 
    void LoadMotionVis(const int &id, visualization_msgs::Marker &mk);

    list<pair<int, pair<Eigen::Vector3d, double>>> reached_pts_; // <mid, <pt, t>>
    tr1::unordered_map<int, list<pair<int, double>>> searched_dict_; // <pt id, list<<mid, t>>>

    ros::Publisher vis_pub_, debug_pub_;
    vector<MotionState> searched_m_;
    lowres::LowResMap *LRM_;
    // BlockMap *BM_;
    // tr1::unordered_map<int, MotionState> m_dict_;

    // for key computation
    Eigen::Vector3d vox_scale_, origin_, vox_n_, v_n_, a_n_, bbx_max_, bbx_min_;
    double da_, dv_;

    int cur_id_;
    double dt_, dt2_; 
    int max_step_;
    int safe_step_;

    double max_v_;
    double max_a_;
    double max_da_;
    double max_dy_;
    double max_ddy_;
    double max_dddy_;

    double max_plan_t_;
    double close_range_;
};

inline bool MotionPrimitivePlanner::YawIntersect(MotionState &ms, const double &up, const double &down){
    if(ms.flags_ & 1) return true;
    double yu1 = ms.yaw_up_;
    double yd1 = ms.yaw_down_;
    double yu2 = up;
    double yd2 = down;
    YawNorm(yu1);
    yd1 = yd1 + (yu1 - ms.yaw_up_);
    YawNorm(yu2);
    yd2 = yd2 + (yu2 - up);
    if(yu1 < yd2 || yd1 > yu2) return false;
    else return true;
}

inline void MotionPrimitivePlanner::GetBbx(Eigen::Vector3d &c, Eigen::Vector3d &box){
    c = (bbx_max_ + bbx_min_) / 2;
    box = bbx_max_ - bbx_min_;
}

inline void MotionPrimitivePlanner::YawNorm(double &yaw){
    double yawn;
    int c = yaw / M_PI / 2;
    yawn = yaw - c * M_PI * 2;
    
    if(yawn < -M_PI) yawn += M_PI * 2;
    if(yawn > M_PI) yawn -= M_PI * 2;
    yaw = yawn;
    return;
}

inline double MotionPrimitivePlanner::YawDiff(const double &yaw1, const double &yaw2){
    double dy = yaw1 - yaw2;
    YawNorm(dy);
    return dy;
}

inline bool MotionPrimitivePlanner::FeasibleInput(const double &vs, const double &a_inp, const double &max_v, const double &max_da, double &ve){
    ve = vs + a_inp * dt_;
    if(abs(ve) > max_v) return false;
    int dec_n = floor(abs(a_inp) / max_da);
    if(ve * a_inp < 0) return true;
    double ve_f = abs(ve) + (abs(a_inp) * 2 - (dec_n + 1) * max_da) * dt_ * (dec_n) / 2;// ve future
    if(abs(ve_f) > max_v) return false;
    return true;
}

inline bool MotionPrimitivePlanner::FeasibleInputDebug(const double &vs, const double &a_inp, const double &max_v, const double &max_da, double &ve){
    cout<<"vs:"<<vs<<endl;
    cout<<"a_inp:"<<a_inp<<endl;
    cout<<"dt_:"<<dt_<<endl;
    ve = vs + a_inp * dt_;
    cout<<"ve:"<<ve<<endl;
    cout<<"max_v:"<<max_v<<endl;
    if(abs(ve) > max_v) return false;
    int dec_n = floor(abs(a_inp) / max_da);
    cout<<"dec_n:"<<dec_n<<endl;

    double ve_f = (ve + ve + dec_n * max_da) * (dec_n + 1) / 2;// ve future
    cout<<"ve_f:"<<ve_f<<endl;

    if(abs(ve_f) > max_v) return false;
    return true;
}


inline bool MotionPrimitivePlanner::MotionForward(MotionState &ms, MotionState &me, Eigen::Vector3d &inp3, bool debug){
    double vs, ve;
    list<double> check_list;
    Eigen::Matrix3d param;

    // EIgen::Vector3d check_d = LRM_->
    for(int dim = 0; dim < 3; dim++){
        vs = ms.v_(dim);
        if(!FeasibleInput(vs, inp3(dim), max_v_, max_da_, me.v_(dim))) return false;
        me.a_(dim) = inp3(dim);
        me.p_(dim) = ms.p_(dim) + ms.v_(dim) * dt_ + 0.5 * inp3(dim) * dt_ * dt_;
        // me.inp_a_(dim) = inp3(dim);
        param(dim, 0) = ms.p_(dim);
        param(dim, 1) = ms.v_(dim);
        param(dim, 2) = inp3(dim) * 0.5;
        // double abs_v0 = abs(ms.v_(dim));

    }
    double tc = 0;
    double tstep = dt_ / 3 + 1e-3; 
    while(1){
        tc += tstep;
        if(tc > dt_){
            check_list.emplace_back(dt_);
            break;
        }
        else{
            check_list.emplace_back(tc);
            // tstep = 0.2;
        }
    }
    Eigen::Vector3d p;
    list<pair<int, pair<Eigen::Vector3d, double>>> sp;
    for(auto &t : check_list){
        for(int dim = 0; dim < 3; dim++) p(dim) = param(dim, 0) + param(dim, 1) * t + param(dim, 2) * t*t;
        if(debug){
            cout<<p.transpose()<<"safe:"<<LRM_->IsFeasible(p)<<endl;
        }
        if(!LRM_->IsFeasible(p)) return false;
        sp.push_back({me.id_, {p, ms.layer_ * dt_ + t}});
    }

    reached_pts_.insert(reached_pts_.end(), sp.begin(), sp.end());
    return true;
}

inline int MotionPrimitivePlanner::YawMotionForward(MotionState &ms, MotionState &me){
    if(ms.flags_ & 1){
        me.flags_ |= 1;
        return 0;
    }
    else{
        me.yawdd_down_ = min(max(max(ms.yawdd_down_ - max_dddy_, (-max_dy_ - ms.yawd_down_) / dt_ + 1e-3), -max_ddy_+1e-3), max_ddy_-1e-3);
        if(!FeasibleInput(ms.yawd_down_, me.yawdd_down_, max_dy_, max_dddy_, me.yawd_down_)){
            me.yawdd_down_ = min(max(ms.yawdd_down_, -max_ddy_+1e-3), max_ddy_-1e-3);
            if(!FeasibleInput(ms.yawd_down_, me.yawdd_down_, max_dy_, max_dddy_, me.yawd_down_)){
                me.yawdd_down_ = min(max(ms.yawdd_down_ + max_dddy_, -max_ddy_+1e-3), max_ddy_-1e-3);
                if(!FeasibleInput(ms.yawd_down_, me.yawdd_down_, max_dy_, max_dddy_, me.yawd_down_)){
                    return 2;
                }
            }
        }
        me.yaw_down_ = ms.yaw_down_ + dt_ * ms.yawd_down_ + 0.5 * dt_ * dt_ * me.yawdd_down_;

        me.yawdd_up_ = min(max(min(ms.yawdd_up_ + max_dddy_, (max_dy_ - ms.yawd_up_) / dt_ - 1e-3), -max_ddy_+1e-3), max_ddy_-1e-3);
        if(!FeasibleInput(ms.yawd_up_, me.yawdd_up_, max_dy_, max_dddy_, me.yawd_up_)){
            me.yawdd_up_ = min(max(ms.yawdd_up_, -max_ddy_+1e-3), max_ddy_-1e-3);
            if(!FeasibleInput(ms.yawd_up_, me.yawdd_up_, max_dy_, max_dddy_, me.yawd_up_)){
                me.yawdd_up_ = min(max(ms.yawdd_up_ - max_dddy_, -max_ddy_+1e-3), max_ddy_-1e-3);
                if(!FeasibleInput(ms.yawd_up_, me.yawdd_up_, max_dy_, max_dddy_, me.yawd_up_)){
                    return 3;
                }
            }
        }
        me.yaw_up_ = ms.yaw_up_ + dt_ * ms.yawd_up_ + 0.5 * dt_ * dt_ * me.yawdd_up_;
        if(me.yaw_up_ - me.yaw_down_ >= 2*M_PI) me.flags_ |= 1;
        return 1;
    }
}

inline int MotionPrimitivePlanner::Motion2Key(MotionState &m){
    int i = floor((m.p_(2)-origin_(2))/vox_scale_(2))*vox_n_(1)+floor((m.p_(1)-origin_(1))/vox_scale_(1))*vox_n_(0)+floor((m.p_(0)-origin_(0))/vox_scale_(0));
    i *= floor((m.v_(2) + max_v_) / dv_)*v_n_(1)+floor((m.v_(1) + max_v_) / dv_)*v_n_(0)+floor((m.v_(0) + max_v_)/dv_);
    i *= floor((m.a_(2) + max_a_) / da_)*a_n_(1)+floor((m.a_(1) + max_a_) / da_)*a_n_(0)+floor((m.a_(0) + max_a_)/da_);
    return i;
}

inline int MotionPrimitivePlanner::Position2Key(Eigen::Vector3d &p){
    return floor((p(2)-origin_(2))/close_range_)*vox_n_(1)+floor((p(1)-origin_(1))/close_range_)*vox_n_(0)+floor((p(0)-origin_(0))/close_range_);
}
#endif