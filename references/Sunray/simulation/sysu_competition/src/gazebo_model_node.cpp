#include "gazebo_model.h"

// 中断信号
void mySigintHandler(int sig)
{
    ROS_INFO("[gazebo_model_node] exit...");
    ros::shutdown();
    exit(0);
}

int main(int argc, char **argv)
{
    // 设置日志
    Logger::init_default();
 
    Logger::setPrintToFile(false);
    Logger::setFilename("~/Documents/Sunray_log.txt");

    ros::init(argc, argv, "gazebo_model_node");
    ros::NodeHandle nh("~");
    ros::Rate rate(20.0);

    // 中断信号注册 
    signal(SIGINT, mySigintHandler);

    // 读取参数
    bool flag_printf; // 是否打印状态
    nh.param<bool>("flag_printf", flag_printf, true); 


    sleep(5.0);          

    // 初始化外部估计类
    Gazebo_model gazebo_model;
    gazebo_model.init(nh);

    ros::Time last_time = ros::Time::now();
    // 主循环
    while (ros::ok)
    {
        ros::spinOnce();

        // 定时主循环更新
        gazebo_model.main_loop_with_point();

        // 定时打印状态
        if (ros::Time::now() - last_time > ros::Duration(1.0) && flag_printf)
        {
            gazebo_model.debug();
            last_time = ros::Time::now();
        }

        rate.sleep();
    }

    return 0;
}