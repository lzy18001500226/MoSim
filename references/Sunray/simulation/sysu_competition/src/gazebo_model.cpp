#include "gazebo_model.h"

void Gazebo_model::init(ros::NodeHandle &nh)
{
    node_name = ros::this_node::getName();
    nh.param<int>("uav_id", uav_id, 1);                 // 【参数】无人机编号
    nh.param<std::string>("uav_name", uav_name, "uav"); // 【参数】无人机名字前缀
    // 无人机名字 = 无人机名字前缀 + 无人机ID
    uav_name = "/" + uav_name + std::to_string(uav_id);

    // 【订阅】Gazebo pose
    uav1_gazebo_pose_sub = nh.subscribe<nav_msgs::Odometry>("/uav_1/gazebo_pose", 10, &Gazebo_model::uav1_gazebo_pose_cb, this);
    uav2_gazebo_pose_sub = nh.subscribe<nav_msgs::Odometry>("/uav_2/gazebo_pose", 10, &Gazebo_model::uav2_gazebo_pose_cb, this);
    uav3_gazebo_pose_sub = nh.subscribe<nav_msgs::Odometry>("/uav_3/gazebo_pose", 10, &Gazebo_model::uav3_gazebo_pose_cb, this);
    ugv1_gazebo_pose_sub = nh.subscribe<nav_msgs::Odometry>("/ugv_1/gazebo_pose", 10, &Gazebo_model::ugv1_gazebo_pose_cb, this);
    ugv2_gazebo_pose_sub = nh.subscribe<nav_msgs::Odometry>("/ugv_2/gazebo_pose", 10, &Gazebo_model::ugv2_gazebo_pose_cb, this);
    ugv3_gazebo_pose_sub = nh.subscribe<nav_msgs::Odometry>("/ugv_3/gazebo_pose", 10, &Gazebo_model::ugv3_gazebo_pose_cb, this);
    solider1_gazebo_pose_sub = nh.subscribe<nav_msgs::Odometry>("/solider_1/gazebo_pose", 10, &Gazebo_model::solider1_gazebo_pose_cb, this);
    solider2_gazebo_pose_sub = nh.subscribe<nav_msgs::Odometry>("/solider_2/gazebo_pose", 10, &Gazebo_model::solider2_gazebo_pose_cb, this);
    solider3_gazebo_pose_sub = nh.subscribe<nav_msgs::Odometry>("/solider_3/gazebo_pose", 10, &Gazebo_model::solider3_gazebo_pose_cb, this);

    // 【发布】设置模型位置
    model_state_pub = nh.advertise<gazebo_msgs::ModelState>("/gazebo/set_model_state", 1);


    // 初始化位置
    while (ros::ok)
    {
        ros::spinOnce();

        if(uav1.get_init_pose && uav2.get_init_pose && uav3.get_init_pose 
            && ugv1.get_init_pose && ugv2.get_init_pose && ugv3.get_init_pose 
            && solider1.get_init_pose && solider2.get_init_pose && solider3.get_init_pose)
        {
            Logger::print_color(int(LogColor::green), node_name, "Gazebo模型初始化成功");
            break;
        }else
        {
            Logger::print_color(int(LogColor::red), node_name, "等待Gazebo模型初始化");
            sleep(2.0);
        }
    }

    // 读取预设的脚本数据点
    read_point_data();
}

void Gazebo_model::main_loop_with_point()
{
    // 仿真步长，该循环执行频率为20Hz，因此dt为0.05秒
    float dt = 0.05;

    int index;
    // 根据当前任务时间查询最近的点索引，然后设置模型位置
    index = find_nearest_time_index(&uav1_data, mission_time);
    set_model_state("uav_1", uav1_data.points[index].x, uav1_data.points[index].y, uav1_data.points[index].z, uav1_data.points[index].yaw);
    // 根据当前任务时间查询最近的点索引，然后设置模型位置
    index = find_nearest_time_index(&uav2_data, mission_time);
    set_model_state("uav_2", uav2_data.points[index].x, uav2_data.points[index].y, uav2_data.points[index].z, uav2_data.points[index].yaw);
    // 根据当前任务时间查询最近的点索引，然后设置模型位置
    index = find_nearest_time_index(&uav3_data, mission_time);
    set_model_state("uav_3", uav3_data.points[index].x, uav3_data.points[index].y, uav3_data.points[index].z+1, uav3_data.points[index].yaw);
    // 根据当前任务时间查询最近的点索引，然后设置模型位置
    index = find_nearest_time_index(&ugv1_data, mission_time);
    set_model_state("ugv_1", ugv1_data.points[index].x, ugv1_data.points[index].y, ugv1_data.points[index].z+2, ugv1_data.points[index].yaw);
    // 根据当前任务时间查询最近的点索引，然后设置模型位置
    index = find_nearest_time_index(&ugv2_data, mission_time);
    set_model_state("ugv_2", ugv2_data.points[index].x, ugv2_data.points[index].y, ugv2_data.points[index].z+3, ugv2_data.points[index].yaw);
    // 根据当前任务时间查询最近的点索引，然后设置模型位置
    index = find_nearest_time_index(&ugv3_data, mission_time);
    set_model_state("ugv_3", ugv3_data.points[index].x, ugv3_data.points[index].y, ugv3_data.points[index].z+4, ugv3_data.points[index].yaw);
    // 根据当前任务时间查询最近的点索引，然后设置模型位置
    index = find_nearest_time_index(&solider1_data, mission_time);
    set_model_state("solider_1", solider1_data.points[index].x, solider1_data.points[index].y, solider1_data.points[index].z+5, solider1_data.points[index].yaw);
    // 根据当前任务时间查询最近的点索引，然后设置模型位置
    index = find_nearest_time_index(&solider2_data, mission_time);
    set_model_state("solider_2", solider2_data.points[index].x, solider2_data.points[index].y, solider2_data.points[index].z+6, solider2_data.points[index].yaw);
    // 根据当前任务时间查询最近的点索引，然后设置模型位置
    index = find_nearest_time_index(&solider3_data, mission_time);
    set_model_state("solider_3", solider3_data.points[index].x, solider3_data.points[index].y, solider3_data.points[index].z+7, solider3_data.points[index].yaw);
    
    // 更新时间
    mission_time = mission_time + dt;
}

void Gazebo_model::main_loop_with_cmd()
{
    // 仿真步长，该循环执行频率为20Hz，因此dt为0.05秒
    float dt = 0.05;

    set_uav1_vel(0.5,0,0,0);
    
    // 根据当前位置和期望速度，更新设定位置
    uav1.set_pos[0] = uav1.model_pos[0] + uav1.model_vel[0] * dt;
    uav1.set_pos[1] = uav1.model_pos[1] + uav1.model_vel[1] * dt;
    uav1.set_pos[2] = uav1.model_pos[2] + uav1.model_vel[2] * dt;
    uav1.set_yaw = uav1.model_yaw + uav1.yaw_vel * dt;

    uav2.set_pos[0] = uav2.model_pos[0] + uav2.model_vel[0] * dt;
    uav2.set_pos[1] = uav2.model_pos[1] + uav2.model_vel[1] * dt;
    uav2.set_pos[2] = uav2.model_pos[2] + uav2.model_vel[2] * dt;
    uav2.set_yaw = uav2.model_yaw + uav2.yaw_vel * dt;

    uav3.set_pos[0] = uav3.model_pos[0] + uav3.model_vel[0] * dt;
    uav3.set_pos[1] = uav3.model_pos[1] + uav3.model_vel[1] * dt;
    uav3.set_pos[2] = uav3.model_pos[2] + uav3.model_vel[2] * dt;
    uav3.set_yaw = uav3.model_yaw + uav3.yaw_vel * dt;

    ugv1.set_pos[0] = ugv1.model_pos[0] + ugv1.model_vel[0] * dt;
    ugv1.set_pos[1] = ugv1.model_pos[1] + ugv1.model_vel[1] * dt;
    ugv1.set_pos[2] = ugv1.model_pos[2] + ugv1.model_vel[2] * dt;
    ugv1.set_yaw = ugv1.model_yaw + ugv1.yaw_vel * dt;

    ugv2.set_pos[0] = ugv2.model_pos[0] + ugv2.model_vel[0] * dt;
    ugv2.set_pos[1] = ugv2.model_pos[1] + ugv2.model_vel[1] * dt;
    ugv2.set_pos[2] = ugv2.model_pos[2] + ugv2.model_vel[2] * dt;
    ugv2.set_yaw = ugv2.model_yaw + ugv2.yaw_vel * dt;

    ugv3.set_pos[0] = ugv3.model_pos[0] + ugv3.model_vel[0] * dt;
    ugv3.set_pos[1] = ugv3.model_pos[1] + ugv3.model_vel[1] * dt;
    ugv3.set_pos[2] = ugv3.model_pos[2] + ugv3.model_vel[2] * dt;
    ugv3.set_yaw = ugv3.model_yaw + ugv3.yaw_vel * dt;

    // 设定模型位置
    set_model_state("uav_1", uav1.set_pos[0], uav1.set_pos[1], uav1.set_pos[2], uav1.set_yaw);
    set_model_state("uav_2", uav2.set_pos[0], uav2.set_pos[1], uav2.set_pos[2], uav2.set_yaw);
    set_model_state("uav_3", uav3.set_pos[0], uav3.set_pos[1], uav3.set_pos[2], uav3.set_yaw);
    set_model_state("ugv_1", ugv1.set_pos[0], ugv1.set_pos[1], ugv1.set_pos[2], ugv1.set_yaw);
    set_model_state("ugv_2", ugv2.set_pos[0], ugv2.set_pos[1], ugv2.set_pos[2], ugv2.set_yaw);
    set_model_state("ugv_3", ugv3.set_pos[0], ugv3.set_pos[1], ugv3.set_pos[2], ugv3.set_yaw);
}

void Gazebo_model::read_point_data()
{
    std::string file_name;

    // 读取TXT数据
    // TXT数据格式：第一列为时间（s）、第二列为X坐标（m）、第三列为Y坐标（m）、第四列为Z坐标（m）、第五列为偏航角（rad）
    // 时间间隔为0.05秒，

    // 1号无人机的数据点
    file_name = "/home/amov/uav1_point.txt";
    read_data_from_file(file_name.c_str(), &uav1_data);

    // 2号无人机的数据点
    file_name = "/home/amov/uav2_point.txt";
    read_data_from_file(file_name.c_str(), &uav2_data);

    // 3号无人机的数据点
    file_name = "/home/amov/uav3_point.txt";
    read_data_from_file(file_name.c_str(), &uav3_data);

    // 1号无人车的数据点
    file_name = "/home/amov/ugv1_point.txt";
    read_data_from_file(file_name.c_str(), &ugv1_data);

    // 2号无人车的数据点
    file_name = "/home/amov/ugv2_point.txt";
    read_data_from_file(file_name.c_str(), &ugv2_data);

    // 3号无人车的数据点
    file_name = "/home/amov/ugv3_point.txt";
    read_data_from_file(file_name.c_str(), &ugv3_data);

    // 1号士兵的数据点
    file_name = "/home/amov/solider1_point.txt";
    read_data_from_file(file_name.c_str(), &solider1_data);

    // 2号士兵的数据点
    file_name = "/home/amov/solider2_point.txt";
    read_data_from_file(file_name.c_str(), &solider2_data);

    // 3号士兵的数据点
    file_name = "/home/amov/solider3_point.txt";
    read_data_from_file(file_name.c_str(), &solider3_data);
}


// 设定无人机速度
void Gazebo_model::set_uav1_vel(double vel_x, double vel_y, double vel_z, double vel_yaw)
{
    uav1.model_vel[0] = vel_x;  // m/s
    uav1.model_vel[1] = vel_y;
    uav1.model_vel[2] = vel_z;
    uav1.yaw_vel = vel_yaw;     // rad/s
}
void Gazebo_model::set_uav2_vel(double vel_x, double vel_y, double vel_z, double vel_yaw)
{
    uav2.model_vel[0] = vel_x;  // m/s
    uav2.model_vel[1] = vel_y;
    uav2.model_vel[2] = vel_z;
    uav2.yaw_vel = vel_yaw;     // rad/s
}
void Gazebo_model::set_uav3_vel(double vel_x, double vel_y, double vel_z, double vel_yaw)
{
    uav3.model_vel[0] = vel_x;  // m/s
    uav3.model_vel[1] = vel_y;
    uav3.model_vel[2] = vel_z;
    uav3.yaw_vel = vel_yaw;     // rad/s
}

void Gazebo_model::set_ugv1_vel(double vel_x, double vel_y, double vel_z, double vel_yaw)
{
    ugv1.model_vel[0] = vel_x;  // m/s
    ugv1.model_vel[1] = vel_y;
    ugv1.model_vel[2] = vel_z;
    ugv1.yaw_vel = vel_yaw;     // rad/s
}
void Gazebo_model::set_ugv2_vel(double vel_x, double vel_y, double vel_z, double vel_yaw)
{
    ugv2.model_vel[0] = vel_x;  // m/s
    ugv2.model_vel[1] = vel_y;
    ugv2.model_vel[2] = vel_z;
    ugv2.yaw_vel = vel_yaw;     // rad/s
}
void Gazebo_model::set_ugv3_vel(double vel_x, double vel_y, double vel_z, double vel_yaw)
{
    ugv3.model_vel[0] = vel_x;  // m/s
    ugv3.model_vel[1] = vel_y;
    ugv3.model_vel[2] = vel_z;
    ugv3.yaw_vel = vel_yaw;     // rad/s
}


void Gazebo_model::set_model_state(string model_name, double x, double y, double z, double yaw)
{
    gazebo_msgs::ModelState model_state;

    model_state.model_name = model_name;
    model_state.pose.position.x = x;
    model_state.pose.position.y = y;
    model_state.pose.position.z = z;

    Eigen::Vector3d att;
    att << 0.0, 0.0, yaw;
    Eigen::Quaterniond q_des = quaternion_from_rpy(att);
    model_state.pose.orientation.x = q_des.x();
    model_state.pose.orientation.y = q_des.y();
    model_state.pose.orientation.z = q_des.z();
    model_state.pose.orientation.w = q_des.w();
    model_state.reference_frame = "ground_plane::link";    
    model_state_pub.publish(model_state);
}


void Gazebo_model::debug()
{
    Logger::print_color(int(LogColor::green), node_name, "----------[Debug Info]-----------", "运行时间:",
                        mission_time,
                        "[ s ]");

    Logger::print_color(int(LogColor::green), "1号飞机位置[X Y Z yaw]:",
                        uav1.model_pos[0],
                        uav1.model_pos[1],
                        uav1.model_pos[2],
                        "[ m ]",
                        uav1.model_yaw / M_PI * 180,
                        "[deg]");


    Logger::print_color(int(LogColor::green), "2号飞机位置[X Y Z yaw]:",
                        uav2.model_pos[0],
                        uav2.model_pos[1],
                        uav2.model_pos[2],
                        "[ m ]",
                        uav2.model_yaw / M_PI * 180,
                        "[deg]");

    Logger::print_color(int(LogColor::green), "3号飞机位置[X Y Z yaw]:",
                        uav3.model_pos[0],
                        uav3.model_pos[1],
                        uav3.model_pos[2],
                        "[ m ]",
                        uav3.model_yaw / M_PI * 180,
                        "[deg]");


    Logger::print_color(int(LogColor::green), "1号车辆位置[X Y Z yaw]:",
                        ugv1.model_pos[0],
                        ugv1.model_pos[1],
                        ugv1.model_pos[2],
                        "[ m ]",
                        ugv1.model_yaw / M_PI * 180,
                        "[deg]");


    Logger::print_color(int(LogColor::green), "2号车辆位置[X Y Z yaw]:",
                        ugv2.model_pos[0],
                        ugv2.model_pos[1],
                        ugv2.model_pos[2],
                        "[ m ]",
                        ugv2.model_yaw / M_PI * 180,
                        "[deg]");

    Logger::print_color(int(LogColor::green), "3号车辆位置[X Y Z yaw]:",
                        ugv3.model_pos[0],
                        ugv3.model_pos[1],
                        ugv3.model_pos[2],
                        "[ m ]",
                        ugv3.model_yaw / M_PI * 180,
                        "[deg]");
    Logger::print_color(int(LogColor::green), "1号士兵位置[X Y Z yaw]:",
                        solider1.model_pos[0],
                        solider1.model_pos[1],
                        solider1.model_pos[2],
                        "[ m ]",
                        solider1.model_yaw / M_PI * 180,
                        "[deg]");


    Logger::print_color(int(LogColor::green), "2号士兵位置[X Y Z yaw]:",
                        solider2.model_pos[0],
                        solider2.model_pos[1],
                        solider2.model_pos[2],
                        "[ m ]",
                        solider2.model_yaw / M_PI * 180,
                        "[deg]");

    Logger::print_color(int(LogColor::green), "3号士兵位置[X Y Z yaw]:",
                        solider3.model_pos[0],
                        solider3.model_pos[1],
                        solider3.model_pos[2],
                        "[ m ]",
                        solider3.model_yaw / M_PI * 180,
                        "[deg]");



}


void Gazebo_model::read_data_from_file(const char* filename, DataSet* data)
{
   FILE* file = fopen(filename, "r");  // 以只读方式打开文件:cite[2]:cite[3]
    if (file == NULL) {
        printf("错误：无法打开文件 %s\n", filename);
        return;
    }
    
    char line[256];
    data->count = 0;

    while (fgets(line, sizeof(line), file) && data->count < MAX_DATA_SIZE) {
        // 解析每行数据
        if (sscanf(line, "%lf %lf %lf %lf %lf", 
                  &data->points[data->count].time,
                  &data->points[data->count].x,
                  &data->points[data->count].y,
                  &data->points[data->count].z,
                  &data->points[data->count].yaw) == 5) {
            data->count++;
        } else {
            printf("警告：第 %d 行数据格式错误，已跳过\n", data->count + 1);
        }
    }
    printf("'%s'数据读取成功！\n", filename);
    printf("总共读取了 %d 组数据\n", data->count);
    
    if (data->count > 0) {
        printf("时间范围: %.6f - %.6f 秒\n", 
               data->points[0].time, data->points[data->count-1].time);
    }

    fclose(file);  // 关闭文件:cite[2]
}


// 辅助函数：查找最近时间的数据点索引
int Gazebo_model::find_nearest_time_index(const DataSet* dataset, double target_time) 
{
    if (dataset == NULL || dataset->count == 0) {
        return -1;
    }
    
    int nearest_index = 0;
    double min_diff = (dataset->points[0].time - target_time > 0) ? 
                      dataset->points[0].time - target_time : target_time - dataset->points[0].time;
    
    for (int i = 1; i < dataset->count; i++) {
        double diff = (dataset->points[i].time - target_time > 0) ? 
                      dataset->points[i].time - target_time : target_time - dataset->points[i].time;
        if (diff < min_diff) {
            min_diff = diff;
            nearest_index = i;
        }
    }
    
    return nearest_index;
}


void Gazebo_model::uav1_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg)
{
    if(!uav1.get_init_pose)
    {
        uav1.get_init_pose = true;
    }

    uav1.model_pos[0] = msg->pose.pose.position.x;
    uav1.model_pos[1] = msg->pose.pose.position.y;
    uav1.model_pos[2] = msg->pose.pose.position.z;

    // 转为rpy
    tf::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
    tf::Matrix3x3 m(q);
    double roll, pitch, yaw;
    m.getRPY(roll, pitch, yaw);

    uav1.model_yaw = yaw;
}
void Gazebo_model::uav2_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg)
{
    if(!uav2.get_init_pose)
    {
        uav2.get_init_pose = true;
    }

    uav2.model_pos[0] = msg->pose.pose.position.x;
    uav2.model_pos[1] = msg->pose.pose.position.y;
    uav2.model_pos[2] = msg->pose.pose.position.z;

    // 转为rpy
    tf::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
    tf::Matrix3x3 m(q);
    double roll, pitch, yaw;
    m.getRPY(roll, pitch, yaw);

    uav2.model_yaw = yaw;
}
void Gazebo_model::uav3_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg)
{
    if(!uav3.get_init_pose)
    {
        uav3.get_init_pose = true;
    }

    uav3.model_pos[0] = msg->pose.pose.position.x;
    uav3.model_pos[1] = msg->pose.pose.position.y;
    uav3.model_pos[2] = msg->pose.pose.position.z;

    // 转为rpy
    tf::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
    tf::Matrix3x3 m(q);
    double roll, pitch, yaw;
    m.getRPY(roll, pitch, yaw);

    uav3.model_yaw = yaw;
}


void Gazebo_model::ugv1_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg)
{
    if(!ugv1.get_init_pose)
    {
        ugv1.get_init_pose = true;
    }

    ugv1.model_pos[0] = msg->pose.pose.position.x;
    ugv1.model_pos[1] = msg->pose.pose.position.y;
    ugv1.model_pos[2] = msg->pose.pose.position.z;

    // 转为rpy
    tf::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
    tf::Matrix3x3 m(q);
    double roll, pitch, yaw;
    m.getRPY(roll, pitch, yaw);

    ugv1.model_yaw = yaw;
}
void Gazebo_model::ugv2_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg)
{
    if(!ugv2.get_init_pose)
    {
        ugv2.get_init_pose = true;
    }

    ugv2.model_pos[0] = msg->pose.pose.position.x;
    ugv2.model_pos[1] = msg->pose.pose.position.y;
    ugv2.model_pos[2] = msg->pose.pose.position.z;

    // 转为rpy
    tf::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
    tf::Matrix3x3 m(q);
    double roll, pitch, yaw;
    m.getRPY(roll, pitch, yaw);

    ugv2.model_yaw = yaw;
}
void Gazebo_model::ugv3_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg)
{
    if(!ugv3.get_init_pose)
    {
        ugv3.get_init_pose = true;
    }

    ugv3.model_pos[0] = msg->pose.pose.position.x;
    ugv3.model_pos[1] = msg->pose.pose.position.y;
    ugv3.model_pos[2] = msg->pose.pose.position.z;

    // 转为rpy
    tf::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
    tf::Matrix3x3 m(q);
    double roll, pitch, yaw;
    m.getRPY(roll, pitch, yaw);

    ugv3.model_yaw = yaw;
}

void Gazebo_model::solider1_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg)
{
    if(!solider1.get_init_pose)
    {
        solider1.get_init_pose = true;
    }

    solider1.model_pos[0] = msg->pose.pose.position.x;
    solider1.model_pos[1] = msg->pose.pose.position.y;
    solider1.model_pos[2] = msg->pose.pose.position.z;

    // 转为rpy
    tf::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
    tf::Matrix3x3 m(q);
    double roll, pitch, yaw;
    m.getRPY(roll, pitch, yaw);

    solider1.model_yaw = yaw;
}

void Gazebo_model::solider2_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg)
{
    if(!solider2.get_init_pose)
    {
        solider2.get_init_pose = true;
    }

    solider2.model_pos[0] = msg->pose.pose.position.x;
    solider2.model_pos[1] = msg->pose.pose.position.y;
    solider2.model_pos[2] = msg->pose.pose.position.z;

    // 转为rpy
    tf::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
    tf::Matrix3x3 m(q);
    double roll, pitch, yaw;
    m.getRPY(roll, pitch, yaw);

    solider2.model_yaw = yaw;
}

void Gazebo_model::solider3_gazebo_pose_cb(const nav_msgs::Odometry::ConstPtr &msg)
{
    if(!solider3.get_init_pose)
    {
        solider3.get_init_pose = true;
    }

    solider3.model_pos[0] = msg->pose.pose.position.x;
    solider3.model_pos[1] = msg->pose.pose.position.y;
    solider3.model_pos[2] = msg->pose.pose.position.z;

    // 转为rpy
    tf::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
    tf::Matrix3x3 m(q);
    double roll, pitch, yaw;
    m.getRPY(roll, pitch, yaw);

    solider3.model_yaw = yaw;
}


// 打印前n行数据
// void print_first_n_data(int n) {
//     printf("序号\t时间(s)\t\tX(m)\t\tY(m)\t\tZ(m)\t\tYaw(rad)\n");
//     printf("------------------------------------------------------------------------\n");
    
//     int count = (n < data_count) ? n : data_count;
//     for (int i = 0; i < count; i++) {
//         printf("%d\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\n", 
//                i+1, 
//                data[i].time, 
//                data[i].x, 
//                data[i].y, 
//                data[i].z, 
//                data[i].yaw);
//     }
// }

