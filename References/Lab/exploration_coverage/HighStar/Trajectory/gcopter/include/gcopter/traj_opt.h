#ifndef TRAJ_OPT_H_
#define TRAJ_OPT_H_
#include "gcopter/trajectory.hpp"
#include "gcopter/gcopter.hpp"
#include "gcopter/gcopter_cover.hpp"

#include <ros/ros.h>

using namespace std;
class AtoTraj{
public:
    void Init(ros::NodeHandle &nh, ros::NodeHandle &nh_private);
    bool Optimize(  const vector<Eigen::Vector3d> &path, 
                    const vector<Eigen::MatrixX4d> &corridors,
                    const vector<Eigen::Matrix3Xd> &corridorVs,
                    // const double &min_t,
                    const Eigen::Matrix<double, 4, 3> &initState,
                    const Eigen::Matrix<double, 4, 3> &endState,
                    const pair<Eigen::Vector4d, bool> &next_tar,
                    double min_t = 0.0,
                    bool use_terminal_corridor = true);
                                             
    bool OptimizeCover(// const vector<Eigen::Vector3d> &path,
                    const vector<Eigen::MatrixX4d> &corridors,
                    const vector<Eigen::Matrix3Xd> &corridorVs,
                    // const vector<pair<Eigen::Vector4d, int>> &midPts,
                    // const Eigen::VectorXd &midTs,
                    const vector<Eigen::Matrix3Xd> &targets,
                    const Eigen::MatrixX4d &camerafov,
                    // const double &min_t,
                    const Eigen::Matrix<double, 4, 3> &initState,
                    const Eigen::Matrix<double, 4, 3> &endState,
                    const pair<Eigen::Vector4d, bool> &next_tar,
                    std::vector<Eigen::Vector3d> &debug_pts,
                    double min_t = 0.0,
                    bool use_terminal_corridor = true);
    Trajectory4<5> traj;    
    vector<double> weightVec_; //[pos, vel, acc, avoidT]
    vector<double> upboundVec_; //[maxvel, maxacc]
    Eigen::VectorXi trajCorridorIdx_;
    Eigen::VectorXi hCorridorIdx_, vCorridorIdx_;
    Eigen::VectorXd vep_, dyp_;
private:
    inline void SetEndVelCorridor(const Eigen::Vector3d &dir, Eigen::MatrixX4d &c);
    ros::NodeHandle nh_, nh_private_;
    Eigen::MatrixX4d velC_;
    double smoothingEps_;
    double weightT_;// weight_minT_;
    double adopt_cover_thresh_;
    int integralIntervs_;

    double trajlength_;

    double relCostTol_;

    double trajStamp;



};

inline void AtoTraj::SetEndVelCorridor(const Eigen::Vector3d &dir, Eigen::MatrixX4d &c){
    double yaw, psi;
    yaw = atan2(dir(1), dir(0));
    psi = -atan2(dir(2), sqrt(pow(dir(0), 2) + pow(dir(1), 2)));
    Eigen::Quaterniond q1, q2;
    Eigen::Matrix3d R;
    q1.x() = 0;
    q1.y() = 0;
    q1.z() = sin(yaw * 0.5);
    q1.w() = cos(yaw * 0.5);
    q2.x() = 0;
    q2.y() = sin(psi * 0.5);
    q2.z() = 0;
    q2.w() = cos(psi * 0.5);
    R = q1.toRotationMatrix() * q2.toRotationMatrix();
    c = velC_;
    for(int i = 0; i < velC_.rows(); i++){
        c.block<1, 3>(i, 0) = (R * velC_.block<1, 3>(i, 0).transpose()).transpose();
    }
    // cout<<"R:\n"<<R<<endl;
    // cout<<"dir:\n"<<dir<<endl;
}


#endif