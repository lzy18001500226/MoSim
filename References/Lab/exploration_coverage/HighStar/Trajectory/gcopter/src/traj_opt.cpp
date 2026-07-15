#include <gcopter/traj_opt.h>

void AtoTraj::Init(ros::NodeHandle &nh, ros::NodeHandle &nh_private){
    weightVec_.resize(9);
    upboundVec_.resize(6);
    string ns = ros::this_node::getName();
    int edge_num;
    double endtheta;
    nh_private.param(ns + "/opt/MaxVel", upboundVec_[0], 2.0);
    nh_private.param(ns + "/opt/MaxAcc", upboundVec_[1], 2.0);
    nh_private.param(ns + "/opt/MaxJer", upboundVec_[2], 20.0);
    nh_private.param(ns + "/opt/YawVel", upboundVec_[3], 20.0);
    nh_private.param(ns + "/opt/YawAcc", upboundVec_[4], 20.0);
    nh_private.param(ns + "/opt/MinCosZ", upboundVec_[5], 0.5);
    nh_private.param(ns + "/opt/WeiPos", weightVec_[0], 1000.0);
    nh_private.param(ns + "/opt/WeiVel", weightVec_[1], 100.0);
    nh_private.param(ns + "/opt/WeiAcc", weightVec_[2], 100.0);
    nh_private.param(ns + "/opt/WeiJer", weightVec_[3], 100.0);
    nh_private.param(ns + "/opt/WeiDy", weightVec_[4], 100.0);
    nh_private.param(ns + "/opt/WeiDdy", weightVec_[5], 100.0);
    nh_private.param(ns + "/opt/WeiYawReach", weightVec_[6], 10.0);
    nh_private.param(ns + "/opt/WeiCover", weightVec_[7], 10.0);
    nh_private.param(ns + "/opt/WeiMinZcos", weightVec_[8], 0.5);
    
    nh_private.param(ns + "/opt/WeiT", weightT_, 20.0);
    // nh_private.param(ns + "/opt/WeiminT", weight_minT_, 500.0);
    nh_private.param(ns + "/opt/smoothingEps", smoothingEps_, 0.01);
    nh_private.param(ns + "/opt/integralIntervs", integralIntervs_, 16);
    nh_private.param(ns + "/opt/RelCostTol", relCostTol_, 0.00001);
    nh_private.param(ns + "/opt/AdoptCoverThresh", adopt_cover_thresh_, 0.90);
    nh_private.param(ns + "/opt/VelEdgeNum", edge_num, 6);
    nh_private.param(ns + "/opt/VelEndTheta", endtheta, 0.7);
    
    cout<<"max VVV:"<<upboundVec_[0]<<endl;
    velC_.resize(edge_num + 1, 4);
    velC_.setZero();
    Eigen::Vector3d dir0(-sin(endtheta), 0.0, cos(endtheta));
    Eigen::Quaterniond q;

    for(int i = 0; i < edge_num; i++){
        q.x() = sin(M_PI / edge_num * i);
        q.y() = 0.0;
        q.z() = 0.0;
        q.w() = cos(M_PI / edge_num * i);
        velC_.block<1, 3>(i, 0) = (q.toRotationMatrix() * dir0).transpose();
        velC_(i, 3) = -1e-3;
        // cout<<"velC_:\n"<<velC_<<endl;
    }
    velC_(edge_num, 0) = 1.0;
    velC_(edge_num, 3) = -upboundVec_[0];

    // for(int i = 0; i < edge_num; i++){
    //     q.x() = cos(M_PI / edge_num);
    //     q.y() = 0.0;
    //     q.z() = 0.0;
    //     q.w() = sin(M_PI / edge_num);
    //     velC_.block<1, 3>(i, 0) = (q.toRotationMatrix().transpose() * dir0).transpose();
    // }
}

bool AtoTraj::Optimize(const vector<Eigen::Vector3d> &path,
                    const vector<Eigen::MatrixX4d> &corridors,
                    const vector<Eigen::Matrix3Xd> &corridorVs,
                    // const double &min_t,
                    const Eigen::Matrix<double, 4, 3> &initState,
                    const Eigen::Matrix<double, 4, 3> &endState,
                    const pair<Eigen::Vector4d, bool> &next_tar,
                    double min_t,
                    bool use_terminal_corridor){

    gcopter::GCOPTER_PolytopeSFC gcopter;
    
    // magnitudeBounds = [v_max, a_max]^T
    // penaltyWeights = [pos_weight, vel_weight, acc_weight]^T
    // initialize some constraint parameters

    Eigen::VectorXd magnitudeBounds(6);
    Eigen::VectorXd penaltyWeights(9);
    magnitudeBounds(0) = upboundVec_[0];
    magnitudeBounds(1) = upboundVec_[1];
    magnitudeBounds(2) = upboundVec_[2];
    magnitudeBounds(3) = upboundVec_[3];
    magnitudeBounds(4) = upboundVec_[4];
    magnitudeBounds(5) = upboundVec_[5];
    penaltyWeights(0) = weightVec_[0];
    penaltyWeights(1) = weightVec_[1];
    penaltyWeights(2) = weightVec_[2];
    penaltyWeights(3) = weightVec_[3];
    penaltyWeights(4) = weightVec_[4];
    penaltyWeights(5) = weightVec_[5];
    penaltyWeights(6) = weightVec_[6];
    penaltyWeights(7) = weightVec_[7];
    penaltyWeights(8) = weightVec_[8];

    vector<Eigen::Matrix3Xd> corridorVstemp;
    corridorVstemp.resize(corridorVs.size()*2 - 1);
    
    // Eigen::VectorXd YawPath;
    // YawPath.resize(corridorVs.size() + 1); 
    // YawPath(0) = initState(3, 0);
    // YawPath(corridorVs.size()) = endState(3, 0);

    for(int i = 0; i < int(corridorVs.size()) - 1; i++){
        corridorVstemp[i*2 + 1].resize(3, 8);
        Eigen::Vector3d up_corn, down_corn;
        for(int dim = 0; dim < 3; dim++){
            down_corn(dim) = max(corridorVs[i](dim, 7), corridorVs[i + 1](dim, 7));
            up_corn(dim) = min(corridorVs[i](dim, 0), corridorVs[i + 1](dim, 0));
        }
        for(int dim1 = 0; dim1 <= 1; dim1++){
            for(int dim2 = 0; dim2 <= 1; dim2++){
                for(int dim3 = 0; dim3 <= 1; dim3++){
                    corridorVstemp[i*2 + 1](0, 4*dim3 + 2*dim2 + dim1) = dim1 ? up_corn(0) : down_corn(0);
                    corridorVstemp[i*2 + 1](1, 4*dim3 + 2*dim2 + dim1) = dim2 ? up_corn(1) : down_corn(1);
                    corridorVstemp[i*2 + 1](2, 4*dim3 + 2*dim2 + dim1) = dim3 ? up_corn(2) : down_corn(2);
                }
            }
        }
        for(int j = 1; j < 8; j++){
            corridorVstemp[i*2 + 1].col(j) = corridorVstemp[i*2 + 1].col(j) - corridorVstemp[i*2 + 1].col(0);
        }
        // corridorVstemp[i*2 + 1].col(0) = 
    }
    for(int i = 0; i < int(corridorVs.size()); i++){
        corridorVstemp[i*2] = corridorVs[i];
        Eigen::Vector3d start_p = corridorVstemp[i*2].col(7);
        for(int j = 1; j < 7; j++){
            corridorVstemp[i*2].col(7-j) = corridorVstemp[i*2].col(7-j) - corridorVstemp[i*2].col(7);
        }
        corridorVstemp[i*2].col(7) = corridorVstemp[i*2].col(0) - corridorVstemp[i*2].col(7);
        corridorVstemp[i*2].col(0) = start_p;
    }
    const int quadratureRes = integralIntervs_;
    Trajectory4<5> traj_tempt = traj;    
    traj.clear();
    Eigen::MatrixX4d velCorridor;
    if(next_tar.second){
        Eigen::Vector3d dir = next_tar.first.head(3) - endState.col(0).head(3);
        SetEndVelCorridor(dir, velCorridor);
        // ROS_WARN("gogogo!");
    }
    // else{
    //     Eigen::Vector3d dir = Eigen::Vector3d(cos(endState.col(0)(3)), sin(endState.col(0)(3)), 0);
    //     SetEndVelCorridor(dir, velCorridor);
    // }
    // else{
    //     velCorridor.resize(6, 4);
    //     velCorridor.col(3).array() = -magnitudeBounds[0];
    //     for(int i = 0; i < 3; i++){
    //         velCorridor(i * 2, i) = 1;
    //         velCorridor(i * 2 + 1, i) = -1;
    //     }
    // }

    // cout<<"corridor:\n"<<corridors.front()<<endl;

    if (!gcopter.setup(weightT_, 
                        // weight_minT_, min_t,
                        use_terminal_corridor,
                        // true,
                        next_tar.second,
                        velCorridor,
                        initState, endState,
                        corridors, corridorVstemp,
                        INFINITY,
                        smoothingEps_,
                        quadratureRes,
                        magnitudeBounds,
                        penaltyWeights,
                        trajCorridorIdx_,
                        hCorridorIdx_, 
                        vCorridorIdx_))
    {
        return false;
    }

    if (std::isinf(gcopter.optimize(traj, relCostTol_)))
    {
        ROS_ERROR("inf");
        traj = traj_tempt;
        return false;
    }
    if(traj.getTotalDuration() < min_t){
        cout<<"mint:"<<min_t<<"  "<<traj.getTotalDuration()<<endl;
        ROS_ERROR("time too shot1");
        traj = traj_tempt;
        return false;
    }
    if (traj.getPieceNum() > 0)
    {
        trajStamp = ros::Time::now().toSec();
        vep_ = gcopter.vep;
        dyp_ = gcopter.dyp;
        cout<<"vep_:"<<vep_.size()<<endl;
        cout<<"dyp_:"<<dyp_.size()<<endl;

        return true;
    }
    else return false;
}


bool AtoTraj::OptimizeCover(// const vector<Eigen::Vector3d> &path,
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
                    std::vector<Eigen::Vector3d> &debug_pts, double min_t,
                    bool use_terminal_corridor){
    gcopter::GCOPTER_COVER_PolytopeSFC gcopter;
    
    // magnitudeBounds = [v_max, a_max]^T
    // penaltyWeights = [pos_weight, vel_weight, acc_weight]^T
    // initialize some constraint parameters

    Eigen::VectorXd magnitudeBounds(6);
    Eigen::VectorXd penaltyWeights(9);
    magnitudeBounds(0) = upboundVec_[0];
    magnitudeBounds(1) = upboundVec_[1];
    magnitudeBounds(2) = upboundVec_[2];
    magnitudeBounds(3) = upboundVec_[3];
    magnitudeBounds(4) = upboundVec_[4];
    magnitudeBounds(5) = upboundVec_[5];
    penaltyWeights(0) = weightVec_[0]*10;
    penaltyWeights(1) = weightVec_[1]*10;
    penaltyWeights(2) = weightVec_[2]*10;
    penaltyWeights(3) = weightVec_[3]*10;
    penaltyWeights(4) = weightVec_[4]*10;
    penaltyWeights(5) = weightVec_[5]*10;
    penaltyWeights(6) = weightVec_[6];
    penaltyWeights(7) = weightVec_[7];
    penaltyWeights(8) = weightVec_[8];

    vector<Eigen::Matrix3Xd> corridorVstemp;
    corridorVstemp.resize(corridorVs.size()*2 - 1);
    
    double t_total = traj.getTotalDuration();
    std::vector<std::pair<Eigen::Vector4d, double>> initPTs;
    vector<Eigen::Vector3d> origin_pts;
    Eigen::VectorXd ts = traj.getDurations();
    double t = 0;
    initPTs.resize(ts.size());
    for(int i = 0; i < ts.size(); i++) {
        t += ts(i);
        initPTs[i].first = traj.getPos(t);
        initPTs[i].second = t;
        if(i + 1 == ts.size()) continue;
        if(vCorridorIdx_(i) % 2 == 1){
            origin_pts.push_back(initPTs[i].first.head(3));
        }
        // corridorVstemp[i*2 + 1].resize(3, 8);
        // Eigen::Vector3d up_corn, down_corn;
        // for(int dim = 0; dim < 3; dim++){
        //     down_corn(dim) = initPTs[i].first(dim) - 1e-3;
        //     up_corn(dim) = initPTs[i].first(dim) + 1e-3;
        // }
        // for(int dim1 = 0; dim1 <= 1; dim1++){
        //     for(int dim2 = 0; dim2 <= 1; dim2++){
        //         for(int dim3 = 0; dim3 <= 1; dim3++){
        //             corridorVstemp[i*2 + 1](0, 4*dim3 + 2*dim2 + dim1) = dim1 ? up_corn(0) : down_corn(0);
        //             corridorVstemp[i*2 + 1](1, 4*dim3 + 2*dim2 + dim1) = dim2 ? up_corn(1) : down_corn(1);
        //             corridorVstemp[i*2 + 1](2, 4*dim3 + 2*dim2 + dim1) = dim3 ? up_corn(2) : down_corn(2);
        //         }
        //     }
        // }
        // for(int j = 1; j < 8; j++){
        //     corridorVstemp[i*2 + 1].col(j) = corridorVstemp[i*2 + 1].col(j) - corridorVstemp[i*2 + 1].col(0);
        // }
    }
    initPTs.pop_back();
    // Eigen::VectorXd YawPath;
    // YawPath.resize(corridorVs.size() + 1); 
    // YawPath(0) = initState(3, 0);
    // YawPath(corridorVs.size()) = endState(3, 0);

    for(int i = 0; i < int(corridorVs.size()) - 1; i++){
        corridorVstemp[i*2 + 1].resize(3, 8);
        Eigen::Vector3d up_corn, down_corn;
        initPTs[i].first = traj.getPos(initPTs[i].second);

        for(int dim = 0; dim < 3; dim++){
            down_corn(dim) = max(corridorVs[i](dim, 7), corridorVs[i + 1](dim, 7));
            up_corn(dim) = min(corridorVs[i](dim, 0), corridorVs[i + 1](dim, 0));
            down_corn(dim) = max(origin_pts[i](dim) - 0.005, down_corn(dim));
            up_corn(dim) = min(origin_pts[i](dim) + 0.005, up_corn(dim));            
        }
        for(int dim1 = 0; dim1 <= 1; dim1++){
            for(int dim2 = 0; dim2 <= 1; dim2++){
                for(int dim3 = 0; dim3 <= 1; dim3++){
                    corridorVstemp[i*2 + 1](0, 4*dim3 + 2*dim2 + dim1) = dim1 ? up_corn(0) : down_corn(0);
                    corridorVstemp[i*2 + 1](1, 4*dim3 + 2*dim2 + dim1) = dim2 ? up_corn(1) : down_corn(1);
                    corridorVstemp[i*2 + 1](2, 4*dim3 + 2*dim2 + dim1) = dim3 ? up_corn(2) : down_corn(2);
                }
            }
        }
        for(int j = 1; j < 8; j++){
            corridorVstemp[i*2 + 1].col(j) = corridorVstemp[i*2 + 1].col(j) - corridorVstemp[i*2 + 1].col(0);
        }
        // corridorVstemp[i*2 + 1].col(0) = 
    }
    for(int i = 0; i < int(corridorVs.size()); i++){
        corridorVstemp[i*2] = corridorVs[i];
        Eigen::Vector3d start_p = corridorVstemp[i*2].col(7);
        for(int j = 1; j < 7; j++){
            corridorVstemp[i*2].col(7-j) = corridorVstemp[i*2].col(7-j) - corridorVstemp[i*2].col(7);
        }
        corridorVstemp[i*2].col(7) = corridorVstemp[i*2].col(0) - corridorVstemp[i*2].col(7);
        corridorVstemp[i*2].col(0) = start_p;
    }
    const int quadratureRes = integralIntervs_;


    Trajectory4<5> traj_tempt = traj;    
    traj.clear();



    Eigen::MatrixX4d velCorridor;
    if(next_tar.second){
        Eigen::Vector3d dir = next_tar.first.head(3) - endState.col(0).head(3);
        SetEndVelCorridor(dir, velCorridor);
    }
    // else{
    //     Eigen::Vector3d dir = Eigen::Vector3d(cos(endState.col(0)(3)), sin(endState.col(0)(3)), 0);
    //     SetEndVelCorridor(dir, velCorridor);
    // }

    if (!gcopter.setup(weightT_ * 5.0, 
                        // weight_minT_, min_t,
                        use_terminal_corridor,
                        // true,
                        next_tar.second,
                        velCorridor,
                        initState, endState,
                        corridors, corridorVstemp,
                        INFINITY,
                        smoothingEps_,
                        quadratureRes,
                        magnitudeBounds,
                        penaltyWeights,
                        t_total,
                        // midPts, 
                        // midTs,
                        targets,
                        camerafov,
                        initPTs,
                        hCorridorIdx_,
                        vCorridorIdx_))
    {
        return false;
    }

    if (std::isinf(gcopter.optimize(traj, vep_, dyp_, relCostTol_)))
    {
        ROS_ERROR("inf2");
        traj = traj_tempt;
        return false;
    }
    double t_new = traj.getTotalDuration();
    if(t_new < min_t){
        ROS_ERROR("time too shot2");
        cout<<"mint:"<<min_t<<"  "<<traj.getTotalDuration()<<endl;
        traj = traj_tempt;
        return false;
    }
    if(t_new  * adopt_cover_thresh_> t_total){
        cout<<"tr:"<<t_total/t_new<<endl;
        ROS_ERROR("low quality trajectory, do not use it");
        traj = traj_tempt;
        return false;
    }
    cout<<"\033[42m tr:"<<t_total/t_new<<"\033[0m"<<endl;

    if (traj.getPieceNum() > 0)
    {
        debug_pts.resize(gcopter.debugpts.cols());
        for(int i = 0; i < gcopter.debugpts.cols(); i++){
            debug_pts[i] = gcopter.debugpts.col(i);
        }
        trajStamp = ros::Time::now().toSec();
        return true;
    }
    else return false;
}