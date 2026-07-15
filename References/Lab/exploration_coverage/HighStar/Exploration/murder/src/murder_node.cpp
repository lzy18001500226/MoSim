#include <ros/ros.h>
#include <stdio.h>
#include <string>
#include <exception>
#include<murder/murderFSM.h>

// #include <glog/logging.h>

int main(int argc, char** argv){
    ros::init(argc, argv, "murder_node");
    ros::NodeHandle nh, nh_private("~");

    google::InitGoogleLogging(argv[0]);
    google::ParseCommandLineFlags(&argc, &argv, true);
    google::InstallFailureSignalHandler();

    try{
        MurderFSM M_FSM;
        M_FSM.init(nh, nh_private);
        ros::spin();
    }
    catch(const std::bad_alloc &e){
        ROS_FATAL("HighStar murder_node caught bad_alloc during startup: %s", e.what());
        return 2;
    }
    catch(const std::exception &e){
        ROS_FATAL("HighStar murder_node caught exception during startup: %s", e.what());
        return 3;
    }
    catch(...){
        ROS_FATAL("HighStar murder_node caught unknown exception during startup");
        return 4;
    }
    return 0;
}
