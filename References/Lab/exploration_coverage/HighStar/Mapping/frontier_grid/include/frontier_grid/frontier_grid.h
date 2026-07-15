#ifndef FRONTIER_GRID_H_
#define FRONTIER_GRID_H_

#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/Dense>
#include <vector>
#include <fstream>
#include <iostream>
#include <ros/ros.h>
#include <list>
#include <memory>
#include <math.h>
#include <random>
// #include <octomap_world/octomap_manager.h>
#include <tr1/unordered_map>
#include <visualization_msgs/Marker.h>
#include <visualization_msgs/MarkerArray.h>
#include <frontier_grid/frontier_struct.h>
#include <block_map/color_manager.h>
#include <block_map/block_map.h>
#include <lowres_map/lowres_map.h>
#include <mp_planner/mp_planner_quick.h>
using namespace std;
using namespace Eigen;
using namespace FrontierGridStruct;

class FrontierGrid{
public: 
    FrontierGrid(){};
    ~FrontierGrid(){};
    void init(ros::NodeHandle &nh, ros::NodeHandle &nh_private);
    
    void SetColorManager(ColorManager &CM){CM_ = &CM;}
    void SetLowresMap(lowres::LowResMap &LRM){LRM_ = &LRM;}
    void SetMap(BlockMap &BM){BM_ = &BM;}
    void SetMotion(FastMotion &FM){FM_ = &FM;}

    void InitialVpDict();

    /**
     * @brief sample viewpoints of frontiers in exploring 
     * 
     */
    bool SampleVps();

    /**
     * @brief remove a viewpoint 
     * 
     * @param f_id frontier id  
     * @param v_id viewpoint id
     */
    inline void RemoveVp(const int &f_id, const int &v_id);

    /**
     * @brief pos to idx
     * 
     * @param pos 
     * @return -1: invalid; else: valid idx
     */
    inline int Pos2Idx(Eigen::Vector3d &pos);

    /**
     * @brief idx to pos
     * 
     * @param idx  
     * @param pos the center position corresponding to the f_grid
     * @return true valid idx
     * @return false invalid idx
     */
    inline bool Idx2Pos(const int &idx, Eigen::Vector3d &pos);

    /**
     * @brief pos to idx
     * 
     * @param pos 
     * @return -1: invalid; else: valid idx
     */
    inline int Posi2Idx(Eigen::Vector3i &pos);

    /**
     * @brief idx to pos3i
     * 
     * @param idx 
     * @param pos 
     * @return true valid idx
     * @return false invalid idx
     */
    inline bool Idx2Posi(const int &idx, Eigen::Vector3i &pos);

    /**
     * @brief Get the viewpoint position
     * 
     * @param f_idx frontier index
     * @param v_id  viewpoint id 
     * @param v_pos  viewpoint pos (xyz)
     * @return true 
     * @return false 
     */
    inline bool GetVpPos(const int &f_idx, const int &v_id, Eigen::Vector3d &v_pos, bool force_valid = true, bool apply_z_gate = true);

    /**
     * @brief Get the viewpoint
     * 
     * @param f_idx frontier index
     * @param v_id  viewpoint id 
     * @param v_pose  viewpoint pose (xyz_yaw)
     * 
     * @return true alive viewpoint
     * @return false dead viewpoint
     */
    inline bool GetVp(const int &f_idx, const int &v_id, Eigen::Vector4d &v_pose, bool force_valid = true);

    /**
     * @brief Get the Vp object
     * 
     * @param f_center frontier center
     * @param v_id      viewpoint id 
     * @param v_pose    viewpoint pose (xyz_yaw)
     * @return true 
     * @return false 
     */
    inline bool GetVp(const Eigen::Vector3d &f_center, const int &v_id, Eigen::Vector4d &v_pose, bool apply_z_gate = true);

    /**
     * @brief sample viewpoints for exploration
     * 
     * @param poses the poses of tagets to be covered by the viewpoints
     */
    bool SampleVps(list<Eigen::Vector3d> &poses);
    bool SampleVps(list<int> &idxs, const double &tm = 0.05);

    /**
     * @brief Set the corresponding frontier explored
     * 
     * @param id id of the target frontier
     */
    inline void SetExplored(const int &id);

    /**
     * @brief Set the exploring frontier
     * 
     * @param dirs_state samplable dirs 
     * @param id         frontier id
     */
    inline void SetExploring(const vector<uint8_t> &dirs_states, const int &id);

    /**
     * @brief update frontier and viewpoints
     * 
     * @param pts newly registered points
     */
    void UpdateFrontier(const vector<Eigen::Vector3d> &pts);
    
    /**
     * @brief Get the grids inside a bounding box 
     * 
     * @param center 
     * @param box_scale 
     * @param f_list     
     */
    void GetWildGridsBBX(const Eigen::Vector3d &center, const Eigen::Vector3d &box_scale, list<pair<int, list<pair<int, Eigen::Vector3d>>>> &f_list);

    /**
     * @brief check if a viewpoint is blocked or has little gain. This func is time-consuming, only for exploring viewpoint.
     * 
     * @param f_id          frontier id
     * @param v_id          viewpoint id
     * @param allow_unknown allow the viewpoint in unknown space
     * @return true         not blocked, has enough gain
     * @return false        blocked or has little gain
     */
    bool StrongCheckViewpoint(const int &f_id, const int &v_id, const bool &allow_unknown);
    bool StrongCheckViewpoint(Eigen::Vector4d &vp_pose, const bool &allow_unknown);

    /**
     * @brief Get the covered volume
     * 
     * @param f_id          frontier id
     * @param v_id          viewpoint id
     * @return double 
     */
    double GetVGain(const int &f_id, const int &v_id, bool debug = false);
    double GetVGain(const int &f_id, const int &v_id, vector<vector<double>> &gain_depth, Eigen::Vector3d &u_center);
    double GetVGainSubmod(const int &f_id, const int &v_id, const vector<vector<double>> &gain_depth, const Eigen::Vector4d vp_pr);

    /**
     * @brief 
     * 
     * @param ps        
     * @param target 
     * @param path
     * @return * int 0: fail, 1: success
     */
    int FindExpTarget(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, pair<int, int> &target, 
                                    list<Eigen::Vector3d> &path, double yaws, double yawvs,
                                    double yawv, double yawa, double vel, int exclude_f, double max_range);
    int FindPath(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector4d &target_pose, 
                                    list<Eigen::Vector3d> &path, double yaws, double yawvs,
                                    double yawv, double yawa, double vel, double &expect_t);

                    
    // 0: find nothing, 1: find target out of motion, 2: find target inside motion, 3: extra vp
    int FindExpTargetM(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as, pair<int, int> &target, Eigen::Vector4d &tar_vp,
                            list<Eigen::Vector3d> &path, double &expect_t, double yaws, double yawvs, double yawv, double yawa, double vel, double acc,
                            int exclude_f, double max_range = 999999.0, double t_thresh = 999.0);
    int FindMotionPath(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as, const Eigen::Vector4d &target_pose, 
                            list<Eigen::Vector3d> &path, double &expect_t, double yaws, double yawvs, double yawv, 
                            double yawa, double vel, double acc, double max_range = 999999.0, double t_thresh = 999.0);
                            
    bool FindSecondTarget(const int &f_id, const int &v_id, const double &v, const double &dy, Eigen::Vector4d &sec_vp);
    
    int GetClosestFid(Eigen::Vector3d p);
    void ExpandFrontier(const int &idx);
    void SampleFrontierNeighbours(const int &idx, const Eigen::Vector3d &cur_p);

    void MotionInitDijkstraDebug(Eigen::Vector3d p);

    inline int Pos2Idx(const Eigen::Vector3d &pos);
    inline bool InsideMap(Eigen::Vector3d &pos);

    inline int IdCompress(const int &f_id, const int &v_id); 
    inline bool IdDecompress(const int &c_id, int &f_id, int &v_id); 
    inline void YawNorm(double &yaw);
    inline double YawDiff(const double &yaw1, const double &yaw2);
    inline double YtEva(const double dy, double yv0, double yvm, double yam);
    inline double YawDiffCover(const double &yawc, const pair<double, double> yawd, const double &yaws);
    inline bool ViewpointZAllowed(const Eigen::Vector3d &pos) const;

    void ShowGainDebug();
    void DebugShowAll();
    Eigen::Vector3d Robot_pos_; //for lazy sample
    bool sample_flag_;          

    vector<CoarseFrontier> f_grid_;
    tr1::unordered_map<int, list<pair<int, int>>> vp_dict_; //<lr node idx, <f_id, vp_id>>

private:
    inline bool InsideMap(Eigen::Vector3i &pos);
    inline bool InsideMap(const Eigen::Vector3d &pos);
    inline bool GetImgIdx(const Eigen::Vector4d &vp, const Eigen::Vector3d &p, int &v, int &h, double &rc);
    void GetDiagnalConnection(list<Eigen::Vector3d> &comp_seg, Eigen::Vector3i ps, Eigen::Vector3i dir);
    void InitGainRays();
    void InitGmax();
    void InitGmaxNear();
    double SampleBestYawSubmod(const vector<vector<double>> &gain_depth, const Eigen::Vector3d &pos, 
                                    double &best_yaw, const Eigen::Vector4d vp_pr, const double &vel, const double &dy);
    double SampleBestYaw(const Eigen::Vector3d &pos, double &best_yaw, const double &y0, const double &yaw_thresh);
    bool SampleVps(list<Eigen::Vector3i> &posis);
    /**
     * @brief get frontier gain, dg_u_d.first+yaw = gain up, dg_u_d.second+yaw = gain down
     * 
     * @param f_id 
     * @param vp_id 
     * @param dg_u_d  gain up down
     * @return double 
     */
    double GetGain(const int &f_id, const int &vp_id, pair<double, double> &dg_u_d);
    double GetGainRange(const int &f_id, const Eigen::Vector3d &tar_vp);
    // double GetGain(const int &f_id, const int &vp_id);
    void RetrieveExpPath(const Eigen::Vector3d &ps, const Eigen::Vector3d &pe, list<Eigen::Vector3d> &path, list<Eigen::Vector3d> &path_debug, shared_ptr<lowres::sch_node> &end_node);
    void RetrieveExpPath(list<Eigen::Vector3d> &path, list<Eigen::Vector3d> &path_debug, shared_ptr<lowres::sch_node> &end_node, shared_ptr<lowres::sch_node> &root_node);
    
    void ClearSearched(vector<shared_ptr<lowres::sch_node>> &node_list);
    void LoadVpLines(visualization_msgs::Marker &mk, Eigen::Vector4d &vp);
    void SampleExtraVps(const Eigen::Vector3d &ps, const Eigen::Vector3d &vs, const Eigen::Vector3d &as, const double vel, const double acc,
                            const double yaws, const double yawvs, const double yawv, const double yawa, 
                                tr1::unordered_map<int, pair<Eigen::Vector4d, double>> &vp_dict);
    void SampleVpsCallback(const ros::TimerEvent &e);
    void LazySampleCallback(const ros::TimerEvent &e);
    void LazyVgainEvaluate(const ros::TimerEvent &e);
    void ShowVpsCallback(const ros::TimerEvent &e);
    void Debug(list<Eigen::Vector3d> &pts, int id);
    void Debug(Eigen::Vector3d &pt, int id);
    void Debug(list<int> &v_ids);
    void DrawFOVs(list<Eigen::Vector4d> &vps);
    inline void GetRayEndInsideMap(const Eigen::Vector3d &start, Eigen::Vector3d &end);
    inline int Pos2DirIdx(const Eigen::Vector3d &pos, const Eigen::Vector3d &center);

    Eigen::Vector3d Robot_size_;
    Eigen::Vector3i node_num_;
    Eigen::Vector3d origin_, up_bd_;
    double resolution_, node_scale_, obs_thresh_;
    double vp_thresh_, resample_duration_, eval_duration_, sensor_range_, sample_max_range_;

    int samp_h_dir_num_, samp_v_dir_num_, samp_dist_num_;
    double samp_h_dir_;
    int samp_dir_num_; //samp_h_dir_num_ * samp_dist_num_
    int samp_num_; //samp_h_dir_num_ * samp_v_dir_num_ * samp_dist_num_
    // int samp_free_thresh_;
    
    int scan_count_;
    ros::Publisher show_pub_, debug_pub_;
    ros::Timer sample_timer_, show_timer_, lazy_samp_timer_, lazy_eva_timer_;
    //FOV down sample
    SensorType sensor_type_;
    int FOV_h_num_, FOV_v_num_; 
    double cam_hor_, cam_ver_;
    double livox_ver_low_, livox_ver_up_;
    double ray_samp_dist1_, ray_samp_dist2_;
    double lambda_;
    double second_gain_thresh_, second_dist_thresh_, second_distmin_thresh_, second_yaw_thresh_;
    double gain_min_, v_gain_thresh_;
    double gmax_, g_factor_;
    double w_dir_;
    bool use_near_gain_;
    bool viewpoint_z_gate_enable_;
    double viewpoint_min_z_, viewpoint_max_z_;
    int g_hor_num_, g_ver_num_;

    vector<double> sample_dists_, sample_h_dirs_, sample_v_dirs_;
    vector<double> sample_vdir_sins_, sample_vdir_coses_;
    vector<double> sample_hdir_sins_, sample_hdir_coses_;
    vector<list<pair<list<Eigen::Vector3d>, list<pair<Eigen::Vector3d, double>>>>> gain_rays_;
    vector<list<pair<Eigen::Vector3d, double>>> gain_dirs_; //<<end pt of rays, raw gain>
    
    //to be shown
    list<int> explored_frontiers_show_;
    list<int> exploring_frontiers_show_;

    //for viewpoints sampling
    list<int> exploring_frontiers_;

    ros::NodeHandle nh_, nh_private_;
    ColorManager *CM_;
    lowres::LowResMap *LRM_;
    BlockMap *BM_;
    FastMotion *FM_;

};

inline void FrontierGrid::RemoveVp(const int &f_id, const int &v_id){
    if(f_id < 0 || f_id >= f_grid_.size() || v_id < 0 || v_id >= samp_num_) return;
    if(f_grid_[f_id].local_vps_[v_id] == 2) return;
    // cout<<"remove:"<<f_id<<" "<<v_id<<endl;
    f_grid_[f_id].local_vps_[v_id] = 2;
    bool kill_frontier = true;
    for(auto &v : f_grid_[f_id].local_vps_){
        if(v != 2) {
            kill_frontier = false;
            break;
        }
    }
    if(kill_frontier){
        f_grid_[f_id].f_state_ = 2;
    }
    if(!f_grid_[f_id].flags_[2]){
        f_grid_[f_id].flags_.set(2);
        exploring_frontiers_show_.emplace_back(f_id);
    }
    if(!kill_frontier && !f_grid_[f_id].flags_[1]){
        f_grid_[f_id].flags_.set(1);
        exploring_frontiers_.emplace_back(f_id);
    }
    if(kill_frontier)
        ExpandFrontier(f_id);
}

inline bool FrontierGrid::InsideMap(Eigen::Vector3i &pos){
    if(pos(0) < 0 || pos(1) < 0 || pos(2) < 0 ||
        pos(0) >=  node_num_(0) || pos(1) >= node_num_(1) || pos(2) >= node_num_(2) )
        return false;
    return true;
}

inline bool FrontierGrid::InsideMap(Eigen::Vector3d &pos){
    if(pos(0) < origin_(0) || pos(1) < origin_(1) || pos(2) < origin_(2) ||
        pos(0) >  up_bd_(0) || pos(1) > up_bd_(1) || pos(2) > up_bd_(2) )
        return false;
    return true;
}

inline bool FrontierGrid::InsideMap(const Eigen::Vector3d &pos){
    if(pos(0) < origin_(0) || pos(1) < origin_(1) || pos(2) < origin_(2) ||
        pos(0) >  up_bd_(0) || pos(1) > up_bd_(1) || pos(2) > up_bd_(2) )
        return false;
    return true;
}

inline int FrontierGrid::Pos2Idx(Eigen::Vector3d &pos){
    if(InsideMap(pos)){
        Eigen::Vector3d dpos = pos - origin_;
        Eigen::Vector3i posid;
        posid.x() = floor(dpos.x() / node_scale_);
        posid.y() = floor(dpos.y() / node_scale_);
        posid.z() = floor(dpos.z() / node_scale_);
        return posid(2)*node_num_(0)*node_num_(1) + posid(1)*node_num_(0) + posid(0);
    }
    else{
        return -1;
    }
}


inline int FrontierGrid::Pos2Idx(const Eigen::Vector3d &pos){
    if(InsideMap(pos)){
        Eigen::Vector3d dpos = pos - origin_;
        Eigen::Vector3i posid;
        posid.x() = floor(dpos.x() / node_scale_);
        posid.y() = floor(dpos.y() / node_scale_);
        posid.z() = floor(dpos.z() / node_scale_);
        return posid(2)*node_num_(0)*node_num_(1) + posid(1)*node_num_(0) + posid(0);
    }
    else{
        return -1;
    }
}

inline int FrontierGrid::Pos2DirIdx(const Eigen::Vector3d &pos, const Eigen::Vector3d &center){
    double dir = atan2(pos(1) - center(1), pos(0) - center(0));
    return int((dir + M_PI + 0.5 * samp_h_dir_) / (samp_h_dir_)) % samp_h_dir_num_;
}


inline bool FrontierGrid::Idx2Pos(const int &idx, Eigen::Vector3d &pos){
    if(idx >= 0 && idx < f_grid_.size()){
        int x = idx % node_num_(0);
        int y = ((idx - x)/node_num_(0)) % node_num_(1);
        int z = ((idx - x) - y*node_num_(0))/node_num_(1)/node_num_(0);
        pos(0) = (double(x)+0.5)*node_scale_;
        pos(1) = (double(y)+0.5)*node_scale_;
        pos(2) = (double(z)+0.5)*node_scale_;
        return true;
    }
    else return false;
}

inline int FrontierGrid::Posi2Idx(Eigen::Vector3i &pos){
    if(InsideMap(pos)){
        return pos(0) + pos(1) * node_num_(0) + pos(2) * node_num_(0) * node_num_(1); 
    }
    else{
        return -1; 
    }
}

inline bool FrontierGrid::Idx2Posi(const int &idx, Eigen::Vector3i &pos){
    if(idx >= 0 && idx < f_grid_.size()){
        int x = idx % node_num_(0);
        int y = ((idx - x)/node_num_(0)) % node_num_(1);
        int z = ((idx - x) - y*node_num_(0))/node_num_(1)/node_num_(0);
        pos(0) = x;
        pos(1) = y;
        pos(2) = z;
        return true;
    }
    else return false;
}

inline bool FrontierGrid::GetVpPos(const int &f_idx, const int &v_id, Eigen::Vector3d &v_pos, bool force_valid, bool apply_z_gate){
    if(f_idx < 0 || f_idx >= f_grid_.size() || v_id < 0 || v_id >= samp_num_) return false;
    if(force_valid && f_grid_[f_idx].f_state_ != 1) {
        // cout<<int(force_valid)<<"  "<<int(f_grid_[f_idx].f_state_)<<endl;
        return false;
    }
    // if(!f_grid_[f_idx].dirs_state_[v_id]) return false;
    int h_idx = (v_id + 0.1) / samp_dir_num_;

    // if((f_grid_[f_idx].dirs_state_[h_idx] == 1)){
        int d_idx = v_id % samp_dist_num_;
        int v_idx = (v_id - samp_dir_num_ * h_idx + 0.1) / samp_dist_num_;
        double length = sample_dists_[d_idx];
        double vdir_sin = sample_vdir_sins_[v_idx];
        double vdir_cos = sample_vdir_coses_[v_idx];
        double hdir_sin = sample_hdir_sins_[h_idx];
        double hdir_cos = sample_hdir_coses_[h_idx];
        v_pos(2) = length * vdir_sin + f_grid_[f_idx].center_(2);
        v_pos(1) = length * vdir_cos * hdir_sin + f_grid_[f_idx].center_(1);
        v_pos(0) = length * vdir_cos * hdir_cos + f_grid_[f_idx].center_(0);
        if(LRM_ != NULL && LRM_->InsideMap(v_pos)){
            v_pos = LRM_->GetStdPos(v_pos);
        }
        if(apply_z_gate && !ViewpointZAllowed(v_pos)) return false;
        return true;
}


inline bool FrontierGrid::GetVp(const int &f_idx, const int &v_id, Eigen::Vector4d &v_pose, bool force_valid){
    if(f_idx < 0 || f_idx >= f_grid_.size() || v_id < 0 || v_id >= samp_num_) return false;
    if(force_valid && f_grid_[f_idx].f_state_ != 1) return false;
    // if(!f_grid_[f_idx].dirs_state_[v_id]) return false;
    int h_idx = (v_id + 0.1) / samp_dir_num_;

    // if((f_grid_[f_idx].dirs_state_[h_idx] == 1)){
        int d_idx = v_id % samp_dist_num_;
        int v_idx = (v_id - samp_dir_num_ * h_idx + 0.1) / samp_dist_num_;
        double length = sample_dists_[d_idx];
        double vdir_sin = sample_vdir_sins_[v_idx];
        double vdir_cos = sample_vdir_coses_[v_idx];
        double hdir_sin = sample_hdir_sins_[h_idx];
        double hdir_cos = sample_hdir_coses_[h_idx];
        v_pose(3) = M_PI + sample_h_dirs_[h_idx];
        v_pose(2) = length * vdir_sin + f_grid_[f_idx].center_(2);
        v_pose(1) = length * vdir_cos * hdir_sin + f_grid_[f_idx].center_(1);
        v_pose(0) = length * vdir_cos * hdir_cos + f_grid_[f_idx].center_(0);
        Eigen::Vector3d vp_pos(v_pose(0), v_pose(1), v_pose(2));
        if(LRM_ != NULL && LRM_->InsideMap(vp_pos)){
            v_pose.block(0, 0, 3, 1) = LRM_->GetStdPos(vp_pos);
        }
        if(!ViewpointZAllowed(v_pose.head(3))) return false;
        return true;
    // }
    // else return false;
}

inline bool FrontierGrid::GetVp(const Eigen::Vector3d &f_center, const int &v_id, Eigen::Vector4d &v_pose, bool apply_z_gate){
    if(v_id < 0 || v_id >= samp_num_) return false;
    int h_idx = (v_id + 0.1) / samp_dir_num_;
    int d_idx = v_id % samp_dist_num_;
    int v_idx = (v_id - samp_dir_num_ * h_idx + 0.1) / samp_dist_num_;

    double length = sample_dists_[d_idx];
    double vdir_sin = sample_vdir_sins_[v_idx];
    double vdir_cos = sample_vdir_coses_[v_idx];
    double hdir_sin = sample_hdir_sins_[h_idx];
    double hdir_cos = sample_hdir_coses_[h_idx];
    v_pose(3) = sample_h_dirs_[h_idx] + M_PI;

    v_pose(2) = length * vdir_sin + f_center(2);
    v_pose(1) = length * vdir_cos * hdir_sin + f_center(1);
    v_pose(0) = length * vdir_cos * hdir_cos + f_center(0);
    Eigen::Vector3d vp_pos(v_pose(0), v_pose(1), v_pose(2));
    if(LRM_ != NULL && LRM_->InsideMap(vp_pos)){
        v_pose.block(0, 0, 3, 1) = LRM_->GetStdPos(vp_pos);
    }
    if(apply_z_gate && !ViewpointZAllowed(v_pose.head(3))) return false;
    return true;
}

inline void FrontierGrid::SetExplored(const int &id){
    f_grid_[id].f_state_ = 2;
}

inline void FrontierGrid::SetExploring(const vector<uint8_t> &dirs_states, const int &id){

}

inline int FrontierGrid::IdCompress(const int &f_id, const int &v_id){
    if(f_id < 0 || f_id >= f_grid_.size() || v_id < 0 || v_id >= samp_num_) return -1;
    return f_id * samp_num_ + v_id;
}

inline bool FrontierGrid::IdDecompress(const int &c_id, int &f_id, int &v_id){
    v_id = c_id % samp_num_;
    f_id = (c_id + 0.1) / samp_num_;
    if(f_id < 0 || f_id >= f_grid_.size()) return false;
    return true;
}


inline void FrontierGrid::YawNorm(double &yaw){
    double yawn;
    int c = yaw / M_PI / 2;
    yawn = yaw - c * M_PI * 2;
    
    if(yawn < -M_PI) yawn += M_PI * 2;
    if(yawn > M_PI) yawn -= M_PI * 2;
    yaw = yawn;
    return;
}

inline double FrontierGrid::YawDiff(const double &yaw1, const double &yaw2){
    double dy = yaw1 - yaw2;
    YawNorm(dy);
    return dy;
}

inline bool FrontierGrid::GetImgIdx(const Eigen::Vector4d &vp, const Eigen::Vector3d &p, int &v, int &h, double &rc){
    Eigen::Vector3d dir = p - vp.head(3);
    rc = dir.norm();
    if(rc < 1e-3 || rc > sensor_range_) return false;
    double ver = atan(dir(2) / rc);
    double half_v = cam_ver_ * 0.5;
    if(ver - 1e-3 < -half_v || ver + 1e-3 > half_v) return false;
    double dv = ver + half_v;
    double hor = atan2(dir(1), dir(0));
    double dh = YawDiff(hor, vp(3));
    double half_h = cam_hor_ * 0.5;
    if(dh - 1e-3 < -half_h || dh + 1e-3 > half_h) return false;
    double dtheta = cam_hor_ / FOV_h_num_;
    double dphi = cam_ver_ / FOV_v_num_;
    v = floor(dv / dphi);
    h = floor((dh+half_h) / dtheta);
    return true;
}


inline double FrontierGrid::YtEva(const double dy, double yv0, double yvm, double yam){
    double t0, t1;
    // double y1 = dy, y2;
    double yvt;
    double ya;
    double ta;
    int dir;
    // if(y1 > 0) y2 = y1 - M_PI*2;
    // else y2 = y1 + M_PI*2;
    if(abs(yv0) > yvm) yv0 = yv0 * yvm / abs(yv0);
    if(dy > 0) ya = yam, yvt = yvm, dir = 1;
    else ya = -yam, yvt = -yvm, dir = -1;
    ta = (yvt - yv0)/ya;
    if(0.5*ta*ta*ya + ta*yv0 < dy && dir == -1 || 0.5*ta*ta*ya + ta*yv0 > dy && dir == 1){
        t1 = (-yv0+sqrt(yv0*yv0+2*ya*dy))/ya;
        if(t1 < 0) t1 = 99999999.0;
        t0 = (-yv0-sqrt(yv0*yv0+2*ya*dy))/ya;
        if(t0 < 0) t0 = 99999999.0;
        // if(t0 > 9999.0 && t1 > 99999.0){//debug
        //     cout<<"dir:"<<dir<<" yv0:"<<yv0<<" yvm:"<<yvm<<" yam:"<<yam<<endl;
        //     cout<<"ta:"<<ta<<" ya:"<<ya<<endl;
        //     cout<<"0.5*ta*ta*ya + ta*yv0:"<<0.5*ta*ta*ya + ta*yv0<<endl;
        //     cout<<"t0:"<<(-yv0+sqrt(yv0*yv0+2*ya*dy))/ya<<endl;
        //     cout<<"t1:"<<(-yv0-sqrt(yv0*yv0+2*ya*dy))/ya<<endl;
        //     ROS_ERROR("YtEva1");
        //     getchar();
        // }
        return min(t1, t0); 
    }
    else{
        double da = yv0*ta+0.5*ta*ta*ya;
        if((dy - da)/yvt < 0){//debug
            ROS_ERROR("YtEva2");
            getchar();
        }
        return (dy - da)/yvt;
    }
}

inline double FrontierGrid::YawDiffCover(const double &yawc, const pair<double, double> yawd, const double &yaws){
    double yaw_up = yawc + yawd.second + cam_hor_*0.5;
    double yaw_down = yawc + yawd.first - cam_hor_*0.5;
    if(yaw_down > yaw_up){
        ROS_ERROR("YawDiffCover error!");
        getchar();
    }
    double du, dd;
    du = YawDiff(yaw_up, yaws);
    dd = YawDiff(yaw_up, yaws);
    if(du * dd < 0) return 0;
    else {
        return std::min(abs(du), abs(dd));
    }
}

inline bool FrontierGrid::ViewpointZAllowed(const Eigen::Vector3d &pos) const{
    if(!viewpoint_z_gate_enable_) return true;
    return pos(2) >= viewpoint_min_z_ && pos(2) <= viewpoint_max_z_;
}

inline void FrontierGrid::GetRayEndInsideMap(const Eigen::Vector3d &start, Eigen::Vector3d &end){
    double lx, ly, lz;
    if(end(0) > up_bd_(0)){
        lx = (up_bd_(0) - start(0)) / (end(0) - start(0)) - 1e-4;
    }    
    else if(end(0) < origin_(0)){
        lx = (start(0) - origin_(0)) / (start(0) - end(0)) - 1e-4;
    }    
    else lx = 1.0;

    if(end(1) > up_bd_(1)){
        ly = (up_bd_(1) - start(1)) / (end(1) - start(1)) - 1e-4;
    }    
    else if(end(1) < origin_(1)){
        ly = (start(1) - origin_(1)) / (start(1) - end(1)) - 1e-4;
    }    
    else ly = 1.0;

    if(end(2) > up_bd_(2)){
        lz = (up_bd_(2) - start(2)) / (end(2) - start(2)) - 1e-4;
    }    
    else if(end(2) < origin_(2)){
        lz = (start(2) - origin_(2)) / (start(2) - end(2)) - 1e-4;
    }    
    else lz = 1.0;

    end = (end - start) * min(lx, min(ly, lz)) + start;
}

#endif
