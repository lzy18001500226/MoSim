#include "ros_msg_utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ros/package.h>

#define FLIP_ANGLE M_PI/3
#define RC_DEADZONE 0.2
#define MAX_DATA_SIZE 2000

class Gazebo_model
{
private:
    std::string node_name;  // 节点名称
    int uav_id;             // 【参数】无人机ID
    std::string uav_name;   // 【参数】无人机名称

    double mission_time{0.0};

    // 定义数据结构体
    struct DataPoint{
        double time;        // 时间（秒）
        double x;           // x位置（米）
        double y;           // y位置（米）
        double z;           // z位置（米）
        double yaw;         // 偏航角（弧度）
    };

    struct DataSet{
        DataPoint points[MAX_DATA_SIZE];
        int count{0};
    };


    DataSet uav1_data;
    DataSet uav2_data;
    DataSet uav3_data;

    DataSet ugv1_data;
    DataSet ugv2_data;
    DataSet ugv3_data;

    DataSet solider1_data;
    DataSet solider2_data;
    DataSet solider3_data;

    // 无人机飞行相关参数
    struct Gazebomodel
    {
        string model_name;
        Eigen::Vector3d init_pos{0.0, 0.0, 0.0};     
        double init_yaw{0.0};
        bool get_init_pose{false};
        Eigen::Vector3d model_pos{0.0, 0.0, 0.0};  
        double model_yaw{0.0}; 
        Eigen::Vector3d model_vel{0.0, 0.0, 0.0};     
        double yaw_vel{0.0};
        Eigen::Vector3d set_pos{0.0, 0.0, 0.0};  
        double set_yaw{0.0}; 
    };
    Gazebomodel uav1;
    Gazebomodel uav2;
    Gazebomodel uav3;

    Gazebomodel ugv1;
    Gazebomodel ugv2;
    Gazebomodel ugv3;

    Gazebomodel solider1;
    Gazebomodel solider2;
    Gazebomodel solider3;


    // 订阅句柄
    ros::Subscriber uav1_gazebo_pose_sub;
    ros::Subscriber uav2_gazebo_pose_sub;
    ros::Subscriber uav3_gazebo_pose_sub;
    void uav1_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg);  
    void uav2_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg);  
    void uav3_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg);  

    // 订阅句柄
    ros::Subscriber ugv1_gazebo_pose_sub;
    ros::Subscriber ugv2_gazebo_pose_sub;
    ros::Subscriber ugv3_gazebo_pose_sub;
    void ugv1_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg);  
    void ugv2_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg);  
    void ugv3_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg); 

    // 订阅句柄
    ros::Subscriber solider1_gazebo_pose_sub;
    ros::Subscriber solider2_gazebo_pose_sub;
    ros::Subscriber solider3_gazebo_pose_sub;
    void solider1_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg);  
    void solider2_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg);  
    void solider3_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg); 

    void set_uav1_vel(double vel_x, double vel_y, double vel_z, double vel_yaw);
    void set_uav2_vel(double vel_x, double vel_y, double vel_z, double vel_yaw);
    void set_uav3_vel(double vel_x, double vel_y, double vel_z, double vel_yaw);
    void set_ugv1_vel(double vel_x, double vel_y, double vel_z, double vel_yaw);
    void set_ugv2_vel(double vel_x, double vel_y, double vel_z, double vel_yaw);
    void set_ugv3_vel(double vel_x, double vel_y, double vel_z, double vel_yaw);

    void read_point_data();
    void read_data_from_file(const char* filename, DataSet* data);
    int find_nearest_time_index(const DataSet* dataset, double target_time);

    ros::Publisher model_state_pub;    // 【订阅】控制指令订阅


public:
    Gazebo_model() {};
    ~Gazebo_model() {};

    void init(ros::NodeHandle &nh); 
    void debug();
    void main_loop_with_point();
    void main_loop_with_cmd();

    void set_model_state(string model_name, double x, double y, double z, double yaw);


};