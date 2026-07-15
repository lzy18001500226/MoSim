#ifndef BLOCK_MAP_H_
#define BLOCK_MAP_H_

#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/Dense>
#include <vector>
#include <fstream>
#include <iostream>
#include <ros/ros.h>
#include <list>
#include <memory>
#include <math.h>
#include <tr1/unordered_map>
// #include <octomap_world/octomap_manager.h>
#include <std_msgs/Float32.h>
#include <sensor_msgs/Image.h>
#include <sensor_msgs/PointCloud2.h>
#include <sensor_msgs/CameraInfo.h>
#include <sensor_msgs/image_encodings.h>
#include <nav_msgs/Odometry.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/io/pcd_io.h>
#include <pcl/filters/filter.h>
#include <cv_bridge/cv_bridge.h>
#include <data_statistics/computation_statistician.h>
#include <mav_msgs/Actuators.h>


#include <block_map/raycast.h>
#include <pcl_conversions/pcl_conversions.h>
#include <visualization_msgs/Marker.h>
#include <visualization_msgs/MarkerArray.h>
#include <block_map/mapping_struct.h>

using namespace std;
using namespace BlockMapStruct;

class BlockMap{
public:
    BlockMap() {};
    ~BlockMap() {};

    void init(ros::NodeHandle &nh, ros::NodeHandle &nh_private);

    /**
     * @brief check if voxes inside the bbx centered at pos contains any occpied vox 
     * 
     * @param pos center
     * @param bbx boundingbox
     * @return true 
     * @return false 
     */
    bool PosBBXOccupied(const Eigen::Vector3d &pos, const Eigen::Vector3d &bbx);

    /**
     * @brief check if voxes inside the bbx are all free
     * 
     * @param pos center
     * @param bbx boudingbox
     * @return true 
     * @return false 
     */
    bool PosBBXFree(const Eigen::Vector3d &pos, const Eigen::Vector3d &bbx);
    
    /**
     * @brief Get the Vox State: unknown/occupied/free
     * 
     * @param id 
     * @return VoxelState 
     */
    inline VoxelState GetVoxState(const int &id);

    /**
     * @brief Get the Vox State: unknown/occupied/free
     * 
     * @param id 
     * @return VoxelState 
     */
    inline VoxelState GetVoxState(const Eigen::Vector3i &id);

    /**
     * @brief Get the Vox State: unknown/occupied/free
     * 
     * @param id 
     * @return VoxelState 
     */
    inline VoxelState GetVoxState(const Eigen::Vector3d &id);

    /**
     * @brief update map using pcl
     * 
     * @param pcl 
     */
    void InsertPcl(const sensor_msgs::PointCloud2ConstPtr &pcl);


    /**
     * @brief update map using depth img
     * 
     * @param depth 
     */
    void InsertImg(const sensor_msgs::ImageConstPtr &depth);

    /**
     * @brief set current robot pose
     * 
     * @param odom 
     */
    void OdomCallback(const nav_msgs::OdometryConstPtr &odom);

    /**
     * @brief load pcl
     * 
     * @param occ_path  path of occ pcd file 
     * @param free_path path of free pcd file
     * @param reset_type     0: unknown, 1: free, 2: occ
     * @param reset     reset exist map
     */
    void LoadRawMap(string occ_path, string free_path, int reset_type, bool reset);

    /**
     * @brief Get the Explorable Volume utilizing BFS
     * 
     * @param init_pt  init search position
     * @return double 
     */
    double GetExplorableVolume(Eigen::Vector3d init_pt);

    /**
     * @brief Set voxel out of constraints state unknown
     * 
     * @param constraints x*c(0)+y*c(1)+z*c(2)+c(3)<0
     */
    void BlineMap(vector<Eigen::Vector4d> constraints);

    /**
     * @brief Get the vox poses on the line
     * 
     * @param start line start pos
     * @param end   line end pos
     * @param line 
     */
    inline void GetCastLine(const Eigen::Vector3d &start, const Eigen::Vector3d &end, list<Eigen::Vector3d> &line);
    inline int PostoId(const Eigen::Vector3d &pos);//dont check in side map, carefully use
    //for low resolution map
    vector<Eigen::Vector3d> cur_pcl_;
    vector<Eigen::Vector3d> newly_register_idx_;
    double resolution_;
    pair<Eigen::Vector3d, Eigen::Vector3d> update_bbx_; // <up, down>
    // ComputationStatistician CS_;

private:
    //callback func
    void InsertPCLCallback(const sensor_msgs::PointCloud2ConstPtr &pcl);
    void InsertDepthCallback(const sensor_msgs::ImageConstPtr &img);
    void CamParamCallback(const sensor_msgs::CameraInfoConstPtr &param);

    //Timer
    void ShowMapCallback(const ros::TimerEvent &e);


    void ProjectToImg(const sensor_msgs::PointCloud2ConstPtr &pcl, vector<double> &depth_img);
    void AwakeBlocks();
    void StatisticV(const ros::TimerEvent &e);
    void StatisticE(const ros::TimerEvent &e);
    void EnergyMsgCallback(const mav_msgs::Actuators &msg);

    // inline 
    inline bool GetVox(int &block_id, int &vox_id, const Vector3i &pos);   //return true: inside map; false: outside map
    inline bool GetVox(int &block_id, int &vox_id, const Vector3d &pos);

    inline float GetVoxOdds(const Eigen::Vector3d &pos);//check if pos is in the block, dont check if pos is in the block
    inline float GetVoxOdds(const int &id);//don't check, carefully use
    inline float GetVoxOdds(const Eigen::Vector3d &pos, const shared_ptr<Grid_Block> &FG);//don't check

    inline bool GetBlock3Id(const Eigen::Vector3d &pos, Eigen::Vector3i &blkid);//check
    inline int GetBlockId(const Eigen::Vector3d &pos);//check
    inline int GetBlockId(const Eigen::Vector3i &pos);//check, pos: block id/carefully use 
    
    inline int GetVoxId(const Eigen::Vector3d &pos, const shared_ptr<Grid_Block> &GB);//don't check, pos of world
    inline int GetVoxId(const Eigen::Vector3i &pos, const shared_ptr<Grid_Block> &GB);//don't check, pos of world
    inline Eigen::Vector3d Id2LocalPos(const shared_ptr<Grid_Block> &GB, const int &id);


    inline bool InsideMap(const Eigen::Vector3i &pos);//
    inline bool InsideMap(const Eigen::Vector3d &pos);//

    inline Eigen::Vector3d IdtoPos(int id);//
    inline Eigen::Vector3i PostoId3(const Eigen::Vector3d &pos);

    inline void GetRayEndInsideMap(const Eigen::Vector3d &start, Eigen::Vector3d &end, bool &occ);

    inline void SpointToUV(const double &x, const double &y, Eigen::Vector2i &uv); //standard depth to camera vector index
    inline void UVToPoint(const int &u, const int &v, const double &depth, Eigen::Vector3d &point); //depthcamera point to 3d point 

    inline std_msgs::ColorRGBA Getcolor(const double z);
    ros::NodeHandle nh_, nh_private_;
    ros::Subscriber odom_sub_, sensor_sub_, camparam_sub_;
    ros::Publisher vox_pub_, debug_pub_;
    ros::Timer show_timer_, debug_timer_;
    vector<std_msgs::ColorRGBA> color_list_;
    double colorhsize_;
    
    Eigen::Vector3d origin_, blockscale_, edgeblock_scale_, map_upbd_, map_lowbd_;
    Eigen::Vector3i block_size_, voxel_num_, block_num_;       //block_size: size of voxels in a block, block_num_:total number of blocks
    Eigen::Vector3i edgeblock_size_;

    nav_msgs::Odometry robot_odom_;
    Eigen::Matrix4d cam2body_, cam2world_;
    //map updating params
    double pro_hit_;             //log(P(hit|occupied)/P(hit|free))
    double pro_miss_;           //log(P(miss|occupied)/P(miss|free))
    double thr_max_, thr_min_, thr_occ_;

    //sensor params
    bool bline_;
    double max_range_;
    double fx_, fy_, cx_, cy_;    
    int u_max_, v_max_, u_down_max_, v_down_max_, downsample_size_, depth_step_;
    vector<shared_ptr<Grid_Block>> GBS_;
    vector<double> void_img_;
    vector<FFD_Grid> downsampled_img_;  //FFD
    //detect frontier flag
    bool depth_;
    bool have_odom_, have_cam_param_;
    double last_update_, update_interval_, show_freq_, last_odom_;
    //blocks to be shown
    vector<int> changed_blocks_;
    //awake blocks 
    list<int> awake_blocks_; 

    //statistic
    bool stat_;
    ros::Publisher statistic_pub_;
    ros::Timer statistic_timer_;
    Eigen::Vector3d stat_upbd_, stat_lowbd_;
    int stat_n_;
    double stat_v_;

    // energy
    ros::Subscriber motor_sub_;
    ros::Timer e_statistic_timer_;
    double energy_ = 0.0;
    double kw_ = 0.00000854858 * 0.016;
    double tl_;
    bool first_v_ = true;
};

inline bool BlockMap::GetVox(int &block_id, int &vox_id, const Vector3i &pos){
    Vector3d pos3d = pos.cast<double>() * resolution_;
    return GetVox(block_id, vox_id, pos3d);
}

inline bool BlockMap::GetVox(int &block_id, int &vox_id, const Vector3d &pos){
    block_id = GetBlockId(pos);
    if(block_id != -1 && block_id >= 0 && block_id < static_cast<int>(GBS_.size())){
        shared_ptr<Grid_Block> GB_ptr = GBS_[block_id];
        if(!GB_ptr){
            return false;
        }
        if(GB_ptr->state_ == MIXED){
            vox_id = GetVoxId(pos, GB_ptr);
            const int vox_num = GB_ptr->block_size_.x() * GB_ptr->block_size_.y() * GB_ptr->block_size_.z();
            if(vox_id < 0 || vox_id >= vox_num ||
               vox_id >= static_cast<int>(GB_ptr->odds_log_.size()) ||
               vox_id >= static_cast<int>(GB_ptr->flags_.size())){
                return false;
            }
            // cout<<"blk size:"<<GB_ptr->block_size_.transpose()<<"pos:::"<<pos.transpose()<<"  B origin:"<<GB_ptr->origin_.transpose()<<" state:"<<GB_ptr->state_<<" size1:"<<GB_ptr->odds_log_.size()<<" size2:"<<GB_ptr->flags_.size()<<endl;
            return true;
        }
        else{
            return false;
        }
    }
    else{
        return false;
    }

}

inline float BlockMap::GetVoxOdds(const Eigen::Vector3d &pos){//check if pos is in the block, dont check if pos is in the block
    int blockid = GetBlockId(pos);
    if(blockid != -1){
        shared_ptr<Grid_Block> GB_ptr = GBS_[blockid];
        if(GB_ptr->state_ == MIXED){
            return GetVoxOdds(pos, GB_ptr);
        }
        else if(GB_ptr->state_ == GBSTATE::FREE){
            return thr_min_;
        }
        else if(GB_ptr->state_ == GBSTATE::OCCUPIED){
            return thr_max_;
        }
        else{
            return 0.0;
        }
    }
    else{
        return 0.0;
    }
}

inline float BlockMap::GetVoxOdds(const int &id){//don't check, carefully use
    Eigen::Vector3d pos = IdtoPos(id);
    
    int blockid = GetBlockId(pos);
    if(blockid == -1) {
        return 0.0;
    }
    else if(GBS_[blockid]->state_ == GBSTATE::MIXED){
        return GBS_[blockid]->odds_log_[GetVoxId(pos, GBS_[blockid])];
    } 
    else if(GBS_[blockid]->state_ == GBSTATE::FREE){
        return thr_min_;
    }
    else if(GBS_[blockid]->state_ == GBSTATE::OCCUPIED){
        return thr_max_;
    }
    else {
        return 0.0;
    }
}

inline float BlockMap::GetVoxOdds(const Eigen::Vector3d &pos, const shared_ptr<Grid_Block> &FG){//don't check
    return FG->odds_log_[GetVoxId(pos, FG)];
}

inline bool BlockMap::GetBlock3Id(const Eigen::Vector3d &pos, Eigen::Vector3i &blkid){//check
    // Eigen::Vector3i pos3;

    // cout<<"pos:"<<pos.transpose()<<endl;
    if(InsideMap(pos)){
        Eigen::Vector3d dpos = pos - origin_;
        blkid.x() = floor(dpos.x() / blockscale_.x());
        blkid.y() = floor(dpos.y() / blockscale_.y());
        blkid.z() = floor(dpos.z() / blockscale_.z());
        return true;
    }
    else{
        return false;
    }
}

inline int BlockMap::GetBlockId(const Eigen::Vector3d &pos){//check
    if(InsideMap(pos)){
        Eigen::Vector3d dpos = pos - origin_;
        Eigen::Vector3i posid;
        posid.x() = floor(dpos.x() / blockscale_.x());
        posid.y() = floor(dpos.y() / blockscale_.y());
        posid.z() = floor(dpos.z() / blockscale_.z());
        return posid(2)*block_num_(0)*block_num_(1) + posid(1)*block_num_(0) + posid(0);
    }
    else{
        return -1;
    }
}

inline int BlockMap::GetBlockId(const Eigen::Vector3i &pos){//check, pos: block id/carefully use 
    if(pos(0) < 0 || pos(1) < 0 || pos(2) < 0 ||
        pos(0) >=  block_num_(0) || pos(1) >= block_num_(1) || pos(2) >= block_num_(2)){
            return -1;
        }
    else{
        return pos(2)*block_num_(0)*block_num_(1) + pos(1)*block_num_(0) + pos(0);
    }
}

inline int BlockMap::GetVoxId(const Eigen::Vector3d &pos, const shared_ptr<Grid_Block> &GB){//don't check, pos of world
    Eigen::Vector3d dpos = pos - origin_ - GB->origin_.cast<double>()*resolution_;
    Eigen::Vector3i posid;
    posid.x() = floor(dpos(0) / resolution_);
    posid.y() = floor(dpos(1) / resolution_);
    posid.z() = floor(dpos(2) / resolution_);

    return posid(2) * GB->block_size_.x() * GB->block_size_.y() + posid(1) * GB->block_size_.x() + posid(0);
}

inline int BlockMap::GetVoxId(const Eigen::Vector3i &pos, const shared_ptr<Grid_Block> &GB){//don't check, pos of world
    Eigen::Vector3i dpos = pos - GB->origin_;
    return dpos(2)*(GB->block_size_.x())*(GB->block_size_.y()) + dpos(1)*(GB->block_size_.x()) + dpos(0);
}

inline Eigen::Vector3d BlockMap::Id2LocalPos(const shared_ptr<Grid_Block> &GB, const int &id){
    int x = id % GB->block_size_(0);
    int y = ((id - x)/GB->block_size_(0)) % GB->block_size_(1);
    int z = ((id - x) - y*GB->block_size_(0))/GB->block_size_(1)/GB->block_size_(0);
    return Eigen::Vector3d((double(x)+0.5)*resolution_,(double(y)+0.5)*resolution_,(double(z)+0.5)*resolution_)+origin_ + GB->origin_.cast<double>() * resolution_;
}

inline bool BlockMap::InsideMap(const Eigen::Vector3i &pos){
    // cout<<"dpos:"<<dpos.transpose()<<endl;
    if(pos(0) < 0 || pos(1) < 0 || pos(2) < 0 ||
        pos(0) >=  voxel_num_(0) || pos(1) >= voxel_num_(1) || pos(2) >= voxel_num_(2))
        return false;
    return true;
}

inline bool BlockMap::InsideMap(const Eigen::Vector3d &pos){
    if(pos(0) < map_lowbd_(0)|| pos(1) < map_lowbd_(1)|| pos(2) < map_lowbd_(2)||
        pos(0) >  map_upbd_(0) || pos(1) > map_upbd_(1) || pos(2) > map_upbd_(2) )
        return false;
    return true;
}

inline Eigen::Vector3d BlockMap::IdtoPos(int id){
    int x = id % voxel_num_(0);
    int y = ((id - x)/voxel_num_(0)) % voxel_num_(1);
    int z = ((id - x) - y*voxel_num_(0))/voxel_num_(1)/voxel_num_(0);
    return Eigen::Vector3d((double(x)+0.5)*resolution_,(double(y)+0.5)*resolution_,(double(z)+0.5)*resolution_)+origin_;
}

inline void BlockMap::GetCastLine(const Eigen::Vector3d &start, const Eigen::Vector3d &end, list<Eigen::Vector3d> &line){
    RayCaster rc;
    Eigen::Vector3d ray_iter;
    Eigen::Vector3d half_res = Eigen::Vector3d(0.5, 0.5, 0.5) * resolution_;
    line.clear();
    rc.setInput((start - origin_) / resolution_, (end - origin_) / resolution_);
    while (rc.step(ray_iter))
    {
        ray_iter = (ray_iter) * resolution_ + origin_ + half_res;
        line.emplace_back(ray_iter);
    }
}

inline int BlockMap::PostoId(const Eigen::Vector3d &pos){
    return floor((pos(2)-origin_(2))/resolution_)*voxel_num_(0)*voxel_num_(1)+
        floor((pos(1)-origin_(1))/resolution_)*voxel_num_(0)+floor((pos(0)-origin_(0))/resolution_);
}

inline Eigen::Vector3i BlockMap::PostoId3(const Eigen::Vector3d &pos){
    return Eigen::Vector3i((int)floor((pos(0) - origin_(0))/resolution_), (int)floor((pos(1) - origin_(1))/resolution_),
         (int)floor((pos(2) - origin_(2))/resolution_)); 
}


inline VoxelState BlockMap::GetVoxState(const int &id){
    Eigen::Vector3d pos = IdtoPos(id);
    
    int blockid = GetBlockId(pos);
    if(blockid == -1) {
        return VoxelState::out;
    }
    else if(GBS_[blockid]->state_ == GBSTATE::MIXED){
        float odds = GBS_[blockid]->odds_log_[GetVoxId(pos, GBS_[blockid])];
        if(odds > 0) return VoxelState::occupied;
        else if(odds < 0 && odds >= thr_min_) return VoxelState::free;
        else return VoxelState::unknown;
    } 
    else if(GBS_[blockid]->state_ == GBSTATE::FREE){
        return VoxelState::free;
    }
    else if(GBS_[blockid]->state_ == GBSTATE::OCCUPIED){
        return VoxelState::occupied;
    }
    else {
        return VoxelState::unknown;
    }
}

inline VoxelState BlockMap::GetVoxState(const Eigen::Vector3i &id){
    int voxid = id(0) + id(1) * voxel_num_(0) + id(2) * voxel_num_(0) * voxel_num_(1);
    return GetVoxState(voxid);
}

inline VoxelState BlockMap::GetVoxState(const Eigen::Vector3d &pos){
    int blockid = GetBlockId(pos);
    if(blockid != -1){
        shared_ptr<Grid_Block> GB_ptr = GBS_[blockid];
        if(GB_ptr->state_ == MIXED){
            float odds = GBS_[blockid]->odds_log_[GetVoxId(pos, GBS_[blockid])];
            // cout<<odds<<"  "<<thr_min_<<endl;
            if(odds > 0) return VoxelState::occupied;
            else if(odds < 0 && odds > thr_min_ - 1e-3) return VoxelState::free;
            else return VoxelState::unknown;
        }
        else if(GBS_[blockid]->state_ == GBSTATE::FREE){
            return VoxelState::free;
        }
        else if(GBS_[blockid]->state_ == GBSTATE::OCCUPIED){
            return VoxelState::occupied;
        }
        else{
            return VoxelState::unknown;
        }
    }
    else{
        return VoxelState::out;
    }
}

inline void BlockMap::GetRayEndInsideMap(const Eigen::Vector3d &start, Eigen::Vector3d &end, bool &occ){
    double lx, ly, lz;
    if(end(0) > map_upbd_(0)){
        lx = (map_upbd_(0) - start(0)) / (end(0) - start(0)) - 1e-4;
        occ = 0;
    }    
    else if(end(0) < map_lowbd_(0)){
        lx = (start(0) - map_lowbd_(0)) / (start(0) - end(0)) - 1e-4;
        occ = 0;
    }    
    else lx = 1.0;

    if(end(1) > map_upbd_(1)){
        ly = (map_upbd_(1) - start(1)) / (end(1) - start(1)) - 1e-4;
        occ = 0;
    }    
    else if(end(1) < map_lowbd_(1)){
        ly = (start(1) - map_lowbd_(1)) / (start(1) - end(1)) - 1e-4;
        occ = 0;
    }    
    else ly = 1.0;

    if(end(2) > map_upbd_(2)){
        lz = (map_upbd_(2) - start(2)) / (end(2) - start(2)) - 1e-4;
        occ = 0;
    }    
    else if(end(2) < map_lowbd_(2)){
        lz = (start(2) - map_lowbd_(2)) / (start(2) - end(2)) - 1e-4;
        occ = 0;
    }    
    else lz = 1.0;

    end = (end - start) * min(lx, min(ly, lz)) + start;
}

inline void BlockMap::SpointToUV(const double &x, const double &y, Eigen::Vector2i &uv){
    // return Eigen::Vector2i(fx_ * x + cx_, fy_ * y + cy_);
    uv.x() = fx_ * x + cx_;
    uv.y() = fy_ * y + cy_;
}

inline void BlockMap::UVToPoint(const int &u, const int &v, const double &depth, Eigen::Vector3d &point){
    point.x() = (u - cx_) * depth / fx_;
    point.y() = (v - cy_) * depth / fy_;
    point.z() = depth;
} 

inline std_msgs::ColorRGBA BlockMap::Getcolor(const double z){
    std_msgs::ColorRGBA color;
    double difz = z - origin_(2);
    color.a = 1.0;
    if(difz > map_upbd_(2)){
        return color_list_.back();
    }
    else if(difz < origin_(2)){
        return color_list_.front();
    }
    else{
        
        int hieghtf = floor(difz / colorhsize_);
        int hieghtc = hieghtf + 1;
        double gain = (difz - colorhsize_*hieghtf)/colorhsize_;
        color.r = color_list_[hieghtf].r*(1.0-gain) + color_list_[hieghtc].r*gain;
        color.g = color_list_[hieghtf].g*(1.0-gain) + color_list_[hieghtc].g*gain;
        color.b = color_list_[hieghtf].b*(1.0-gain) + color_list_[hieghtc].b*gain;
    }
    return color;
}

#endif
