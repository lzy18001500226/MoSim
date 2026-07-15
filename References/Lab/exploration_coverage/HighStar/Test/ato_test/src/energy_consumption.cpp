#include <ros/ros.h>
#include <stdio.h>
#include <string>
#include <glog/logging.h>
#include <mav_msgs/Actuators.h>
using namespace std;
ros::Subscriber rotor_sub_;
ros::Timer e_timer_;
double e = 0;
double kw = 0.00000854858 * 0.016;
double tl;
bool first_v = true;
void Energy(const mav_msgs::Actuators &msg){
    if(first_v){
        tl = msg.header.stamp.toSec();
        first_v = false;
        return;
    }
    double dt = msg.header.stamp.toSec() - tl;
    for(int i = 0; i < msg.angular_velocities.size(); i++){
        e += abs(pow(msg.angular_velocities[i], 3)) * kw*dt;
    }
    tl = msg.header.stamp.toSec();
}

void EnergyTimer(const ros::TimerEvent &te){
    cout<<"energy:"<<e<<endl;
}

int main(int argc, char** argv){
    ros::init(argc, argv, "murder_node");
    ros::NodeHandle nh, nh_private("~");

    google::InitGoogleLogging(argv[0]);
    google::ParseCommandLineFlags(&argc, &argv, true);
    google::InstallFailureSignalHandler();

    rotor_sub_ = nh.subscribe("/firefly/motor_speed", 1, &Energy);
    e_timer_ = nh.createTimer(ros::Duration(0.5), &EnergyTimer);
    // MurderFSM M_FSM;
    // M_FSM.init(nh, nh_private);

    ros::spin();
    cout<<"energy total:"<<e<<endl;
    return 0;
}