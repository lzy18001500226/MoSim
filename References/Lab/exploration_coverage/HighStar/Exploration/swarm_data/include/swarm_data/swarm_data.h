#ifndef SWARM_DATA_HPP_
#define SWARM_DATA_HPP_
#include <ros/ros.h>
#include <thread>
#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/Dense>
#include <vector>
#include <list>
#include <tr1/unordered_map>
#include <visualization_msgs/MarkerArray.h>
#include <nav_msgs/Odometry.h>

#include "gcopter/trajectory.hpp"

using namespace std;
struct Swarm_Data{
    uint8_t drones_num_;
    uint8_t self_id_;
    uint8_t ground_id_;
    vector<uint8_t> Exp_map_;              //0: unexplored; 255: explored; 00(300-360)(240-300) (180-240)(120-180)(60-120)(0-60)deg;
    vector<Trajectory<5>> trajs_;    
    vector<nav_msgs::Odometry> Odoms_;
    list<uint8_t> mining_queue_;           //the planning sequence of robots in current group
    vector<uint8_t> swarm_root_;             //the root hnode of each robot
     
};

#endif