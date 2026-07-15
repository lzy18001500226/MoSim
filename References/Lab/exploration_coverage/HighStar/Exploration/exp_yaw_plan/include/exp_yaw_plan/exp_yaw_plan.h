#ifndef EXP_YAW_PLAN_H_
#define EXP_YAW_PLAN_H_

#include <ros/ros.h>
#include <thread>
#include <Eigen/Eigen>
#include <vector>
#include <list>
#include <visualization_msgs/MarkerArray.h>
#include <tr1/unordered_map>
#include <random>

#include <lowres_map/lowres_map.h>
#include <block_map/block_map.h>
#include <frontier_grid/frontier_grid.h>


#include <visualization_msgs/MarkerArray.h>
#include <swarm_exp_msgs/SwarmTraj.h>
#include <nav_msgs/Odometry.h>
#include <sensor_msgs/Image.h>

struct YawSearchNode{
    lowres::SchState status_;
    double gain_;   // F - g; less = better
    double yaw_;
    int parent_, id_, layer_;
};

struct YawNode{
    // double gain_;   // F - g; less = better
    double t_;
    list<Eigen::Vector3d> covered_unknown_;
    list<Eigen::Vector3d> covered_key_;
    vector<Eigen::Vector3d> covered_targets_;
    int id_, parent_id_, idx_;// id: node id, parent_id: sequence parent, idx: origin path id;
    Eigen::Vector4d pos_;
    shared_ptr<YawSearchNode> ysn_;
};

class YCompare {
public:
  bool operator()(shared_ptr<YawSearchNode> &node1, shared_ptr<YawSearchNode> &node2) {
    return node1->gain_ > node2->gain_;
  }
};

class ExpYawPlan{
public:
    ExpYawPlan(){};
    ~ExpYawPlan(){};
    void init(ros::NodeHandle &nh, ros::NodeHandle &nh_private);
    void SetLowresMap(lowres::LowResMap &LRM){LRM_ = &LRM;}
    void SetMap(BlockMap &BM){BM_ = &BM;}
    void SetFrontierGrid(FrontierGrid &FG){FG_ = &FG;}
    void SampleTimes(double &total, vector<double> &tl, const double &ys, const double &ye);

    /**
     * @brief 
     * 
     * @param path_pts  intermediate pt, t
     * @param total_t 
     * @param ys 
     * @param ye 
     * @param Fid 
     * @return true 
     * @return false 
     */
    bool YawPlan(vector<pair<Eigen::Vector4d, double>> &path_pts, const double &total_t, const double &ys, const double &ye, int Fid);
    void FovClearShow();

    vector<YawNode> ans_;
private:
    bool CreateGraphs(double total_t, vector<pair<Eigen::Vector4d, double>> &path_pts, double ys, double ye, int Fid);
    bool Search(double ys, double ye, vector<pair<int, int>> &layer_id_ans);
    void InitSubModGain(vector<pair<int, int>> &layer_id_ans, tr1::unordered_map<int, int> &cd, vector<double> &info_list, 
                                double &gain_motion, double &gain_exp, double ys, double ye);
    bool SubModGainIter(vector<pair<int, int>> &layer_id_ans, tr1::unordered_map<int, int> &cd,
        vector<bool> &check_list, double &gain_motion, double &gain_exp, double ys, double ye);
    bool SubModGainSample(vector<pair<int, int>> &layer_id_ans, tr1::unordered_map<int, int> &cd, vector<double> &info_list,
        vector<bool> &check_list, double &gain_motion, double &gain_exp, int s_idx, double ys, double ye);
    void SetAnswer(vector<pair<int, int>> &layer_id_ans, tr1::unordered_map<int, int> &cd);
    void FovShow();
    void Debug(vector<Eigen::Vector3d> &pts);
    void DrawFov(Eigen::Vector4d &pose);

    inline bool InsideMap(const Eigen::Vector3d &p);
    inline Eigen::Vector3d GetStdPos(const Eigen::Vector3d &pos);
    inline Eigen::Vector3d IdtoPos(const int &id);
    inline int PostoId(const Eigen::Vector3d &p);
    inline void InitNodes(const int &layer, /*double &yup, const double &ydown, */const Eigen::Vector3d &pos, const int &idx, const double &t);
    inline double CalYdist(double &dt);
    inline void YawNorm(double &yaw);
    //yaw1 - yaw2
    inline double YawDiff(const double &yaw1, const double &yaw2);
    inline int GetHash(vector<pair<int, int>> &layer_id_ans);
    //y2 - y1
    inline int GetYawIdx(const double &y1, const double &y2);
    inline void GetSliceDiff(const int &idx1, const int &idx2, const int &layer, vector<int> &slice_delete, vector<int> &slice_add);
    inline bool CoverSlice(const int &layer, const int &vp_id, const int &slice_id);
    inline void GetCoverIds(const double &y, list<int> &cl);
    inline void GetTimePenalties(const vector<double> &ys, vector<double> &tl);
    FrontierGrid *FG_;
    lowres::LowResMap *LRM_;
    BlockMap *BM_;
    ros::Publisher vis_pub_, debug_pub_;

    int fov_sample_h_num_;
    int layer_num_, fov_slice_num_;
    double dr_, dsr_, dd_;   // yaw sample dir, ray sample dir, depth
    double min_dt_;
    double dy_, ddy_;
    double FOV_h_, FOV_v_;
    double sr_; // sensor range
    double exp_gf_; // exploration gain factor
    double lambda_;
    int sample_num_max_, stable_num_max_;
    double plan_t_max_;
    int fid_;

    Eigen::Vector3i voxel_num_, v_n_;
    Eigen::Vector3d node_scale_, origin_, mapscale_, map_upbd_, map_lowbd_;
    vector<vector<YawNode>> nodes_;
    vector<vector<list<pair<int, double>>>> gains_; //node->slice->list<target, gain>
    
    vector<double> cross_thresh_, t_l_, tdm_l_;
    vector<int> hash_n_;
    vector<bool> searched_seq_;
    tr1::unordered_map<int, pair<uint32_t, double>> covered_dict_; //<idx, <layer_flag, gain>>
    random_device rd_;
    default_random_engine eng_;
    uniform_int_distribution<int> rand_idx_;

};

inline bool ExpYawPlan::InsideMap(const Eigen::Vector3d &pos){
    if(pos(0) < map_lowbd_(0) || pos(1) < map_lowbd_(1) || pos(2) < map_lowbd_(2) ||
        pos(0) >  map_upbd_(0) || pos(1) > map_upbd_(1) || pos(2) > map_upbd_(2) )
        return false;
    return true;
}

inline Eigen::Vector3d ExpYawPlan::GetStdPos(const Eigen::Vector3d &pos){
    int id = PostoId(pos);
    return IdtoPos(id);
}

inline Eigen::Vector3d ExpYawPlan::IdtoPos(const int &id){
    int x = id % voxel_num_(0);
    int y = ((id - x)/voxel_num_(0)) % voxel_num_(1);
    int z = ((id - x) - y*voxel_num_(0))/v_n_(1);
    return Eigen::Vector3d((double(x)+0.5)*node_scale_(0),(double(y)+0.5)*node_scale_(1),(double(z)+0.5)*node_scale_(2))+origin_;
}

inline int ExpYawPlan::PostoId(const Eigen::Vector3d &p){
    return floor((p(2)-origin_(2))/node_scale_(2))*v_n_(1)+
        floor((p(1)-origin_(1))/node_scale_(1))*voxel_num_(0)+floor((p(0)-origin_(0))/node_scale_(0));
}

inline void ExpYawPlan::InitNodes(const int &layer, /*double &yup, const double &ydown,*/ const Eigen::Vector3d &pos, const int &idx, const double &t){
    int i = 1;
    for(auto &n : nodes_) i *= n.size();
    hash_n_.push_back(i);

    nodes_.push_back({});
    double PI2 = M_PI*2;
    double ang;
    int count = 0;
    int yidx, yidx0;
    // int pre_num = 0;
    // for(auto &l : nodes_) pre_num += l.size();

    // int hnum = FOV_v_ / dsr_;
    // yidx0 = GetYawIdx(0, ydown);
    for(int i = 0; i < fov_sample_h_num_; i++){
        // ang = dir + ydown;
        // yidx = GetYawIdx(0, ang);
        ang = (i + 0.5) * dr_;
        // if(yidx0 == yidx) break; // close loop
        // yup = ang;
        YawNode yn;
        yn.pos_.head(3) = pos;
        yn.pos_(3) = ang;
        yn.parent_id_ = -1;
        yn.id_ = count;// + pre_num;
        yn.idx_ = idx;
        yn.t_ = t;
        // yn.gain_ = 0.0;
        // yn.cs_ = count;
        // yn.ce_ = hnum + count;
        nodes_[layer].emplace_back(yn);
        count++;
    }
}

inline double ExpYawPlan::CalYdist(double &dt){
    double acc_t = dy_ / ddy_;
    if(dt > 2 * acc_t){
       return dy_ * (dt - acc_t);
    }
    else{
       return 0.25 * dt * dt * ddy_;
    }
}

inline void ExpYawPlan::YawNorm(double &yaw){
    double yawn;
    int c = yaw / M_PI / 2;
    yawn = yaw - c * M_PI * 2;
    
    if(yawn < -M_PI) yawn += M_PI * 2;
    if(yawn > M_PI) yawn -= M_PI * 2;
    yaw = yawn;
    return;
}

inline double ExpYawPlan::YawDiff(const double &yaw1, const double &yaw2){
    double dy = yaw1 - yaw2;
    YawNorm(dy);
    return dy;
}

inline int ExpYawPlan::GetHash(vector<pair<int, int>> &layer_id_ans){
    int h = 0;
    for(auto li : layer_id_ans){
        h += hash_n_[li.first] * li.second;
    }
    return h;
}

inline int ExpYawPlan::GetYawIdx(const double &y1, const double &y2){
    double dy = YawDiff(y2, y1);
    if(dy < 0) dy += 2 * M_PI;
    return floor(dy / dr_);
}

inline void ExpYawPlan::GetSliceDiff(const int &idx1, const int &idx2, const int &layer, vector<int> &slice_delete, vector<int> &slice_add){
    slice_delete.clear();
    slice_add.clear();
    int s1 = GetYawIdx(0, nodes_[layer][idx1].pos_(3)) - floor(fov_slice_num_ / 2);
    int s2 = GetYawIdx(0, nodes_[layer][idx2].pos_(3)) - floor(fov_slice_num_ / 2);
    if(s1 < 0) s1 += fov_sample_h_num_;
    if(s2 < 0) s2 += fov_sample_h_num_;
    // ROS_WARN("---");
    // cout<<"s1:"<<s1<<" s2:"<<s2<<endl;
    // cout<<"idx1:"<<idx1<<" idx2:"<<idx2<<endl;
    for(int i = 0, j; i < fov_slice_num_; i++){
        j = s1 + i;
        if(j >= fov_sample_h_num_) j -= fov_sample_h_num_;
        else if(j < 0) j += fov_sample_h_num_;
        // cout<<"add:"<<j<<endl;
        if(!CoverSlice(layer, idx2, j)) slice_add.emplace_back(j);

        j = s2 + i;
        if(j >= fov_sample_h_num_) j -= fov_sample_h_num_;
        else if(j < 0) j += fov_sample_h_num_;
        // cout<<"del:"<<j<<endl;
        if(!CoverSlice(layer, idx1, j)) slice_delete.emplace_back(j);
    }
}

inline bool ExpYawPlan::CoverSlice(const int &layer, const int &vp_id, const int &slice_id){
    int ys = GetYawIdx(0, nodes_[layer][vp_id].pos_(3)) - floor(fov_slice_num_ / 2);
    if(ys + fov_slice_num_ > fov_sample_h_num_){
        if(slice_id >= ys) return true;
        else if(slice_id <  fov_slice_num_ - fov_sample_h_num_ + ys) return true;
        else return false;
    }
    else if(ys < 0){
        if(slice_id >= fov_sample_h_num_ + ys) return true;
        if(slice_id < ys + fov_slice_num_) return true;
        else return false;
    }
    else{
        if(slice_id >= ys && slice_id < ys + fov_slice_num_) return true;
        else return false;
    }
}

inline void ExpYawPlan::GetCoverIds(const double &y, list<int> &cl){
    cl.clear();
    int s = GetYawIdx(0, y) - floor(fov_slice_num_ / 2);
    int j;
    for(int i = 0; i < fov_slice_num_; i++){
        j = i + s;
        if(j >= fov_sample_h_num_){
            j -= fov_sample_h_num_;
        }
        else if(j < 0){
            j += fov_sample_h_num_;
        }
        cl.emplace_back(j);
    }
}

inline void ExpYawPlan::GetTimePenalties(const vector<double> &ys, vector<double> &tl){
    int n = ys.size() - 1;
    tl.clear();
    double last_t = 0;
    for(int i = 0; i < n; i++){
        last_t = last_t + max(tdm_l_[i], abs(YawDiff(ys[i], ys[i + 1]))/dy_);
        tl.emplace_back(exp(-last_t*lambda_));
    }
}
#endif