#include "controller.h"

#include <algorithm>

extern "C" {
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY)
#include "G9_Family_CFunction_Sysblock_private.h"
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G10_BDE_FAMILY)
#include "G10_BDE_Family_CFunction_Sysblock_StateIso_private.h"
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST)
#include "MoSim_PID_AttitudeThrust_CFunction_Sysblock_private.h"
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
#include "MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock_private.h"
#define MOSIM_LEARNING_GB_IN hrust_cfunction_sysblockGbIn
#define MOSIM_LEARNING_GB_OUT thrust_cfunction_sysblockGbOut
#else
#include "PX4CTRL_Core_CFunction_Sysblock_private.h"
#endif
}

using namespace std;

namespace
{
constexpr int kG9OfficialPid = 1;
constexpr int kG9Se3Basic = 2;
constexpr int kG9DfbcBasic = 3;
constexpr int kG9SmcBoundaryLayer = 4;
constexpr int kG9PidIndi = 5;
constexpr int kG9NmpcOuter = 6;
constexpr int kG10L1Awff = 7;
constexpr int kG10SafetyFilter = 8;
constexpr int kG10FaultAllocation = 9;

constexpr int kPidCascade = 1;
constexpr int kPidGainScheduled = 2;
constexpr int kPidFuzzy = 3;
constexpr int kPidNeural = 4;
constexpr int kPidAntiWindup = 5;
constexpr int kPidFeedforwardProfile = 6;

int pid_controller_id_from_mode(const std::string &core_mode)
{
  if (core_mode == "gain_scheduled_pid") return kPidGainScheduled;
  if (core_mode == "fuzzy_pid") return kPidFuzzy;
  if (core_mode == "neural_pid") return kPidNeural;
  if (core_mode == "anti_windup") return kPidAntiWindup;
  if (core_mode == "feedforward_profile") return kPidFeedforwardProfile;
  return kPidCascade;
}

const char *pid_controller_name_from_id(const int controller_id)
{
  switch (controller_id)
  {
    case kPidCascade: return "cascade_pid";
    case kPidGainScheduled: return "gain_scheduled_pid";
    case kPidFuzzy: return "fuzzy_pid";
    case kPidNeural: return "neural_pid";
    case kPidAntiWindup: return "anti_windup";
    case kPidFeedforwardProfile: return "feedforward_profile";
    default: return "unknown";
  }
}

constexpr int kLearningNeuralResidual = 1;
constexpr int kLearningRlGainScheduler = 2;

int learning_controller_id_from_mode(const std::string &core_mode)
{
  return core_mode == "rl_gain_scheduler" ? kLearningRlGainScheduler : kLearningNeuralResidual;
}

const char *learning_controller_name_from_id(const int controller_id)
{
  switch (controller_id)
  {
    case kLearningNeuralResidual: return "trained_neural_residual";
    case kLearningRlGainScheduler: return "rl_gain_scheduler";
    default: return "unknown";
  }
}

int g9_controller_id_from_mode(const std::string &core_mode)
{
  if (core_mode == "se3_basic")
  {
    return kG9Se3Basic;
  }
  if (core_mode == "dfbc_basic")
  {
    return kG9DfbcBasic;
  }
  if (core_mode == "smc_boundary_layer")
  {
    return kG9SmcBoundaryLayer;
  }
  if (core_mode == "pid_indi")
  {
    return kG9PidIndi;
  }
  if (core_mode == "nmpc_outer")
  {
    return kG9NmpcOuter;
  }
  if (core_mode == "l1_awff" ||
      core_mode == "l1_residual" ||
      core_mode == "awff_l1")
  {
    return kG10L1Awff;
  }
  if (core_mode == "safety_filter")
  {
    return kG10SafetyFilter;
  }
  if (core_mode == "fault_allocation")
  {
    return kG10FaultAllocation;
  }
  return kG9OfficialPid;
}

#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY)
const char *g9_controller_name_from_id(const int controller_id)
{
  switch (controller_id)
  {
    case kG9OfficialPid: return "official_pid";
    case kG9Se3Basic: return "se3_basic";
    case kG9DfbcBasic: return "dfbc_basic";
    case kG9SmcBoundaryLayer: return "smc_boundary_layer";
    case kG9PidIndi: return "pid_indi";
    case kG9NmpcOuter: return "nmpc_outer";
    default: return "unknown";
  }
}
#endif

double clamp_double(double value, double lo, double hi)
{
  return std::max(lo, std::min(hi, value));
}
} // namespace



double LinearControl::fromQuaternion2yaw(Eigen::Quaterniond q)
{
  double yaw = atan2(2 * (q.x()*q.y() + q.w()*q.z()), q.w()*q.w() + q.x()*q.x() - q.y()*q.y() - q.z()*q.z());
  return yaw;
}

LinearControl::LinearControl(Parameter_t &param) : param_(param),
                                                   use_mosim_generated_core_(false),
                                                   use_official_pid_core_(false),
                                                   use_se3_basic_core_(false),
                                                   use_dfbc_basic_core_(false),
                                                   use_smc_boundary_layer_core_(false),
                                                   use_pid_indi_core_(false),
                                                   use_nmpc_outer_core_(false),
                                                   use_dfbc_high_order_core_(false),
                                                   use_dfbc_smooth_robust_core_(false),
                                                   use_dfbc_smooth_robust_dob_(false),
                                                   use_dfbc_smooth_robust_indi_core_(false),
                                                   use_l1_awff_core_(false),
                                                   use_safety_filter_core_(false),
                                                   use_fault_allocation_core_(false),
                                                   generated_core_reset_pending_(true),
                                                   generated_family_controller_id_(kG9OfficialPid)
{
  std::string core_mode;
  ros::param::param<std::string>("~mosim_generated_core_mode", core_mode, "original");
  use_mosim_generated_core_ = (core_mode == "mworks_generated" ||
                               core_mode == "generated_c" ||
                               core_mode == "mworks_generated_c");
  use_official_pid_core_ = (core_mode == "official_pid");
  use_se3_basic_core_ = (core_mode == "se3_basic");
  use_dfbc_basic_core_ = (core_mode == "dfbc_basic");
  use_smc_boundary_layer_core_ = (core_mode == "smc_boundary_layer");
  use_pid_indi_core_ = (core_mode == "pid_indi");
  use_nmpc_outer_core_ = (core_mode == "nmpc_outer");
  use_dfbc_high_order_core_ = (core_mode == "dfbc_high_order" ||
                               core_mode == "dfbc_jerk_snap");
  use_dfbc_smooth_robust_core_ = (core_mode == "dfbc_smooth_robust" ||
                                  core_mode == "dfbc_smooth_robust_dob" ||
                                  core_mode == "dfbc_wind_robust");
  use_dfbc_smooth_robust_dob_ = (core_mode == "dfbc_smooth_robust_dob" ||
                                 core_mode == "dfbc_wind_robust");
  use_dfbc_smooth_robust_indi_core_ = (core_mode == "dfbc_smooth_robust_indi");
  use_l1_awff_core_ = (core_mode == "l1_awff" ||
                       core_mode == "l1_residual" ||
                       core_mode == "awff_l1");
  use_safety_filter_core_ = (core_mode == "safety_filter");
  use_fault_allocation_core_ = (core_mode == "fault_allocation");
  generated_family_controller_id_ = g9_controller_id_from_mode(core_mode);
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST)
  generated_family_controller_id_ = pid_controller_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
  generated_family_controller_id_ = learning_controller_id_from_mode(core_mode);
#endif
  ros::param::param<int>("~mosim_generated_family_controller_id",
                         generated_family_controller_id_,
                         generated_family_controller_id_);
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G10_BDE_FAMILY)
  const int max_generated_family_controller_id = kG10FaultAllocation;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST)
  const int max_generated_family_controller_id = kPidFeedforwardProfile;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
  const int max_generated_family_controller_id = kLearningRlGainScheduler;
#else
  const int max_generated_family_controller_id = kG9NmpcOuter;
#endif
  generated_family_controller_id_ = static_cast<int>(clamp_double(
      static_cast<double>(generated_family_controller_id_),
      static_cast<double>(kG9OfficialPid),
      static_cast<double>(max_generated_family_controller_id)));
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               use_official_pid_core_ ||
                               use_se3_basic_core_ ||
                               use_dfbc_basic_core_ ||
                               use_smc_boundary_layer_core_ ||
                               use_pid_indi_core_ ||
                               use_nmpc_outer_core_;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G10_BDE_FAMILY)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               use_l1_awff_core_ ||
                               use_safety_filter_core_ ||
                               use_fault_allocation_core_;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "cascade_pid" ||
                               core_mode == "gain_scheduled_pid" ||
                               core_mode == "fuzzy_pid" ||
                               core_mode == "neural_pid" ||
                               core_mode == "anti_windup" ||
                               core_mode == "feedforward_profile";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "trained_neural_residual" ||
                               core_mode == "rl_gain_scheduler";
#endif
  ros::param::param<double>("~smc/lambda_x", smc_lambda_[0], 2.0);
  ros::param::param<double>("~smc/lambda_y", smc_lambda_[1], 2.0);
  ros::param::param<double>("~smc/lambda_z", smc_lambda_[2], 2.0);
  ros::param::param<double>("~smc/eta_x", smc_eta_[0], 0.1);
  ros::param::param<double>("~smc/eta_y", smc_eta_[1], 0.1);
  ros::param::param<double>("~smc/eta_z", smc_eta_[2], 0.05);
  ros::param::param<double>("~smc/phi_x", smc_phi_[0], 0.4);
  ros::param::param<double>("~smc/phi_y", smc_phi_[1], 0.4);
  ros::param::param<double>("~smc/phi_z", smc_phi_[2], 0.35);
  ros::param::param<double>("~smc/surface_limit_x", smc_surface_limit_[0], 3.0);
  ros::param::param<double>("~smc/surface_limit_y", smc_surface_limit_[1], 3.0);
  ros::param::param<double>("~smc/surface_limit_z", smc_surface_limit_[2], 2.5);
  ros::param::param<double>("~indi/gain_x", indi_gain_[0], 0.12);
  ros::param::param<double>("~indi/gain_y", indi_gain_[1], 0.12);
  ros::param::param<double>("~indi/gain_z", indi_gain_[2], 0.08);
  ros::param::param<double>("~indi/increment_limit_x", indi_increment_limit_[0], 0.35);
  ros::param::param<double>("~indi/increment_limit_y", indi_increment_limit_[1], 0.35);
  ros::param::param<double>("~indi/increment_limit_z", indi_increment_limit_[2], 0.20);
  ros::param::param<double>("~indi/measured_accel_limit_x", indi_measured_accel_limit_[0], 6.0);
  ros::param::param<double>("~indi/measured_accel_limit_y", indi_measured_accel_limit_[1], 6.0);
  ros::param::param<double>("~indi/measured_accel_limit_z", indi_measured_accel_limit_[2], 4.0);
  ros::param::param<double>("~indi/accel_lpf_alpha", indi_accel_lpf_alpha_, 0.25);
  ros::param::param<double>("~nmpc/horizon_s", nmpc_horizon_s_, 0.25);
  ros::param::param<double>("~nmpc/position_weight_x", nmpc_position_weight_[0], 1.0);
  ros::param::param<double>("~nmpc/position_weight_y", nmpc_position_weight_[1], 1.0);
  ros::param::param<double>("~nmpc/position_weight_z", nmpc_position_weight_[2], 1.0);
  ros::param::param<double>("~nmpc/velocity_weight_x", nmpc_velocity_weight_[0], 0.05);
  ros::param::param<double>("~nmpc/velocity_weight_y", nmpc_velocity_weight_[1], 0.05);
  ros::param::param<double>("~nmpc/velocity_weight_z", nmpc_velocity_weight_[2], 0.05);
  ros::param::param<double>("~nmpc/control_weight_x", nmpc_control_weight_[0], 0.001);
  ros::param::param<double>("~nmpc/control_weight_y", nmpc_control_weight_[1], 0.001);
  ros::param::param<double>("~nmpc/control_weight_z", nmpc_control_weight_[2], 0.001);
  ros::param::param<double>("~nmpc/accel_limit_x", nmpc_accel_limit_[0], 4.0);
  ros::param::param<double>("~nmpc/accel_limit_y", nmpc_accel_limit_[1], 4.0);
  ros::param::param<double>("~nmpc/accel_limit_z", nmpc_accel_limit_[2], 2.5);
  ros::param::param<double>("~nmpc/increment_limit_x", nmpc_increment_limit_[0], 4.0);
  ros::param::param<double>("~nmpc/increment_limit_y", nmpc_increment_limit_[1], 4.0);
  ros::param::param<double>("~nmpc/increment_limit_z", nmpc_increment_limit_[2], 2.5);
  ros::param::param<double>("~dfbc_high_order/body_rate_limit_x", high_order_body_rate_limit_[0], 6.0);
  ros::param::param<double>("~dfbc_high_order/body_rate_limit_y", high_order_body_rate_limit_[1], 6.0);
  ros::param::param<double>("~dfbc_high_order/body_rate_limit_z", high_order_body_rate_limit_[2], 3.0);
  ros::param::param<double>("~bodyrate_attitude/gain_x", bodyrate_attitude_gain_[0], 3.0);
  ros::param::param<double>("~bodyrate_attitude/gain_y", bodyrate_attitude_gain_[1], 3.0);
  ros::param::param<double>("~bodyrate_attitude/gain_z", bodyrate_attitude_gain_[2], 1.5);
  ros::param::param<double>("~dfbc_high_order/body_accel_limit_x", high_order_body_accel_limit_[0], 60.0);
  ros::param::param<double>("~dfbc_high_order/body_accel_limit_y", high_order_body_accel_limit_[1], 60.0);
  ros::param::param<double>("~dfbc_high_order/body_accel_limit_z", high_order_body_accel_limit_[2], 30.0);
  ros::param::param<double>("~dfbc_robust/smooth_feedback_gain_x", smooth_feedback_gain_[0], 1.2);
  ros::param::param<double>("~dfbc_robust/smooth_feedback_gain_y", smooth_feedback_gain_[1], 1.2);
  ros::param::param<double>("~dfbc_robust/smooth_feedback_gain_z", smooth_feedback_gain_[2], 1.0);
  ros::param::param<double>("~dfbc_robust/smooth_feedback_bound_x", smooth_feedback_bound_[0], 1.5);
  ros::param::param<double>("~dfbc_robust/smooth_feedback_bound_y", smooth_feedback_bound_[1], 1.5);
  ros::param::param<double>("~dfbc_robust/smooth_feedback_bound_z", smooth_feedback_bound_[2], 1.0);
  ros::param::param<double>("~dfbc_robust/disturbance_observer_gain_x", disturbance_observer_gain_[0], 0.4);
  ros::param::param<double>("~dfbc_robust/disturbance_observer_gain_y", disturbance_observer_gain_[1], 0.4);
  ros::param::param<double>("~dfbc_robust/disturbance_observer_gain_z", disturbance_observer_gain_[2], 0.3);
  ros::param::param<double>("~dfbc_robust/disturbance_compensation_limit_x", disturbance_compensation_limit_[0], 1.0);
  ros::param::param<double>("~dfbc_robust/disturbance_compensation_limit_y", disturbance_compensation_limit_[1], 1.0);
  ros::param::param<double>("~dfbc_robust/disturbance_compensation_limit_z", disturbance_compensation_limit_[2], 0.8);
  ros::param::param<double>("~l1_awff/model_decay", l1_model_decay_, 1.25);
  ros::param::param<double>("~l1_awff/filter_T", l1_filter_T_, 0.20);
  ros::param::param<double>("~l1_awff/gain_x", l1_gain_[0], 0.32);
  ros::param::param<double>("~l1_awff/gain_y", l1_gain_[1], 0.32);
  ros::param::param<double>("~l1_awff/gain_z", l1_gain_[2], 0.35);
  ros::param::param<double>("~l1_awff/comp_limit_x", l1_comp_limit_[0], 2.0);
  ros::param::param<double>("~l1_awff/comp_limit_y", l1_comp_limit_[1], 2.0);
  ros::param::param<double>("~l1_awff/comp_limit_z", l1_comp_limit_[2], 2.0);
  ros::param::param<double>("~l1_awff/drag_feedforward_gain_x", drag_feedforward_gain_[0], 0.0);
  ros::param::param<double>("~l1_awff/drag_feedforward_gain_y", drag_feedforward_gain_[1], 0.0);
  ros::param::param<double>("~l1_awff/drag_feedforward_gain_z", drag_feedforward_gain_[2], 0.0);
  ros::param::param<double>("~safety_filter/accel_limit_x", safety_accel_limit_[0], 50.0);
  ros::param::param<double>("~safety_filter/accel_limit_y", safety_accel_limit_[1], 50.0);
  ros::param::param<double>("~safety_filter/accel_limit_z", safety_accel_limit_[2], 50.0);
  ros::param::param<double>("~fault_allocation/rotor1_efficiency", fault_rotor_efficiency_[0], 1.0);
  ros::param::param<double>("~fault_allocation/rotor2_efficiency", fault_rotor_efficiency_[1], 1.0);
  ros::param::param<double>("~fault_allocation/rotor3_efficiency", fault_rotor_efficiency_[2], 1.0);
  ros::param::param<double>("~fault_allocation/rotor4_efficiency", fault_rotor_efficiency_[3], 1.0);
  ros::param::param<double>("~fault_allocation/blend", fault_allocation_blend_, 0.52);
  ros::param::param<double>("~fault_allocation/min_efficiency", fault_min_efficiency_, 0.50);
  ros::param::param<double>("~fault_allocation/thrust_comp_limit", fault_thrust_comp_limit_, 0.25);
  Init();
  resetThrustMapping();
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=g9_family"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY"
                    << " generated_model_name=G9_Family_CFunction_Sysblock"
                    << " runtime_loaded_symbol=G9_Family_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << g9_controller_name_from_id(generated_family_controller_id_));
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=pid_attitude_thrust"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST"
                    << " generated_model_name=MoSim_PID_AttitudeThrust_CFunction_Sysblock"
                    << " runtime_loaded_symbol=MoSim_PID_AttitudeThrust_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << pid_controller_name_from_id(generated_family_controller_id_)
                    << " neural_residual_source=zero_untrained");
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=learning_attitude_thrust"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST"
                    << " generated_model_name=MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock"
                    << " runtime_loaded_symbol=MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << learning_controller_name_from_id(generated_family_controller_id_)
                    << " learning_artifact_sha256=4d480c6ad4738da75b4f7bfdf824658b7878ea511a52935ed2be4fff0d043e45");
  }
#endif
  ROS_INFO_STREAM("[px4ctrl] mosim_generated_core_mode=" << core_mode
                  << " use_mosim_generated_core=" << (use_mosim_generated_core_ ? "true" : "false")
                  << " generated_family_controller_id=" << generated_family_controller_id_
                  << " use_official_pid_core=" << (use_official_pid_core_ ? "true" : "false")
                  << " use_se3_basic_core=" << (use_se3_basic_core_ ? "true" : "false")
                  << " use_dfbc_basic_core=" << (use_dfbc_basic_core_ ? "true" : "false")
                  << " use_smc_boundary_layer_core=" << (use_smc_boundary_layer_core_ ? "true" : "false")
                  << " use_pid_indi_core=" << (use_pid_indi_core_ ? "true" : "false")
                  << " use_nmpc_outer_core=" << (use_nmpc_outer_core_ ? "true" : "false")
                  << " use_dfbc_high_order_core=" << (use_dfbc_high_order_core_ ? "true" : "false")
                  << " use_dfbc_smooth_robust_core=" << (use_dfbc_smooth_robust_core_ ? "true" : "false")
                  << " use_dfbc_smooth_robust_indi_core=" << (use_dfbc_smooth_robust_indi_core_ ? "true" : "false")
                  << " use_l1_awff_core=" << (use_l1_awff_core_ ? "true" : "false")
                  << " use_safety_filter_core=" << (use_safety_filter_core_ ? "true" : "false")
                  << " use_fault_allocation_core=" << (use_fault_allocation_core_ ? "true" : "false"));
}

/* 
  compute u.thrust and u.q, controller gains and other parameters are in param_ 
*/
quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu, 
    Controller_Output_t &u)
{
  if (use_mosim_generated_core_)
  {
    return calculateGeneratedCoreControl(des, odom, imu, u);
  }
  if (use_official_pid_core_)
  {
    return calculateOfficialPidControl(des, odom, imu, u);
  }
  if (use_se3_basic_core_)
  {
    return calculateSe3BasicControl(des, odom, imu, u);
  }
  if (use_dfbc_basic_core_)
  {
    return calculateDfbcBasicControl(des, odom, imu, u);
  }
  if (use_smc_boundary_layer_core_)
  {
    return calculateSmcBoundaryLayerControl(des, odom, imu, u);
  }
  if (use_pid_indi_core_)
  {
    return calculatePidIndiControl(des, odom, imu, u);
  }
  if (use_nmpc_outer_core_)
  {
    return calculateNmpcOuterControl(des, odom, imu, u);
  }
  if (use_dfbc_high_order_core_)
  {
    return calculateDfbcHighOrderControl(des, odom, imu, u);
  }
  if (use_dfbc_smooth_robust_core_)
  {
    return calculateDfbcSmoothRobustControl(des, odom, imu, u);
  }
  if (use_dfbc_smooth_robust_indi_core_)
  {
    return calculateDfbcSmoothRobustIndiControl(des, odom, imu, u);
  }
  if (use_l1_awff_core_)
  {
    return calculateL1AwffControl(des, odom, imu, u);
  }
  if (use_safety_filter_core_)
  {
    return calculateSafetyFilterControl(des, odom, imu, u);
  }
  if (use_fault_allocation_core_)
  {
    return calculateFaultAllocationControl(des, odom, imu, u);
  }

  return calculateOriginalControl(des, odom, imu, u);
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateOriginalControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{

  /* WRITE YOUR CODE HERE */
      //compute disired acceleration
      Eigen::Vector3d des_acc(0.0, 0.0, 0.0);
      Eigen::Vector3d Kp,Kv;
      Kp << param_.gain.Kp0, param_.gain.Kp1, param_.gain.Kp2;
      Kv << param_.gain.Kv0, param_.gain.Kv1, param_.gain.Kv2;
      des_acc = des.a + Kv.asDiagonal() * (des.v - odom.v) + Kp.asDiagonal() * (des.p - odom.p);
      des_acc += Eigen::Vector3d(0,0,param_.gra);

      u.thrust = computeDesiredCollectiveThrustSignal(des_acc);
      double roll,pitch,yaw,yaw_imu;
      double yaw_odom = fromQuaternion2yaw(odom.q);
      double sin = std::sin(yaw_odom);
      double cos = std::cos(yaw_odom);
      roll = (des_acc(0) * sin - des_acc(1) * cos )/ param_.gra;
      pitch = (des_acc(0) * cos + des_acc(1) * sin )/ param_.gra;
      // yaw = fromQuaternion2yaw(des.q);
      yaw_imu = fromQuaternion2yaw(imu.q);
      // Eigen::Quaterniond q = Eigen::AngleAxisd(yaw,Eigen::Vector3d::UnitZ())
      //   * Eigen::AngleAxisd(roll,Eigen::Vector3d::UnitX())
      //   * Eigen::AngleAxisd(pitch,Eigen::Vector3d::UnitY());
      Eigen::Quaterniond q = Eigen::AngleAxisd(des.yaw,Eigen::Vector3d::UnitZ())
        * Eigen::AngleAxisd(pitch,Eigen::Vector3d::UnitY())
        * Eigen::AngleAxisd(roll,Eigen::Vector3d::UnitX());
      u.q = imu.q * odom.q.inverse() * q;
      u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());


  /* WRITE YOUR CODE HERE */

  //used for debug
  // debug_msg_.des_p_x = des.p(0);
  // debug_msg_.des_p_y = des.p(1);
  // debug_msg_.des_p_z = des.p(2);
  
  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  
  debug_msg_.des_a_x = des_acc(0);
  debug_msg_.des_a_y = des_acc(1);
  debug_msg_.des_a_z = des_acc(2);
  
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  
  debug_msg_.des_thr = u.thrust;
  
  // Used for thrust-accel mapping estimation
  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

bool
LinearControl::usingGeneratedCore(void) const
{
  return use_mosim_generated_core_;
}

bool
LinearControl::usingMosimWrapperOwnedLandingCore(void) const
{
  return use_mosim_generated_core_ || use_official_pid_core_ || use_se3_basic_core_ || use_dfbc_basic_core_ || use_smc_boundary_layer_core_ || use_pid_indi_core_ || use_nmpc_outer_core_ || use_dfbc_high_order_core_ || use_dfbc_smooth_robust_core_ || use_dfbc_smooth_robust_indi_core_ || use_l1_awff_core_ || use_safety_filter_core_ || use_fault_allocation_core_;
}

Eigen::Vector3d
LinearControl::bodyrateAttitudeFeedback(
    const Eigen::Quaterniond &desired_attitude,
    const Eigen::Quaterniond &current_attitude,
    const Eigen::Vector3d &feedforward_bodyrates) const
{
  Eigen::Quaterniond q_des = desired_attitude.normalized();
  Eigen::Quaterniond q_cur = current_attitude.normalized();
  Eigen::Quaterniond q_err = q_cur.inverse() * q_des;
  if (q_err.w() < 0.0)
  {
    q_err.coeffs() *= -1.0;
  }

  Eigen::Vector3d bodyrates = feedforward_bodyrates;
  for (int i = 0; i < 3; ++i)
  {
    bodyrates(i) += bodyrate_attitude_gain_[i] * 2.0 * q_err.vec()(i);
    bodyrates(i) = std::max(-high_order_body_rate_limit_[i],
                            std::min(high_order_body_rate_limit_[i], bodyrates(i)));
  }
  return bodyrates;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateOfficialPidControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.ki[0] = param_.gain.Kvi0;
  core_params.ki[1] = param_.gain.Kvi1;
  core_params.ki[2] = param_.gain.Kvi2;
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : M_PI / 2.0;

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_official_pid_core(core_params, official_pid_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateSe3BasicControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_se3_basic_core(core_params, se3_basic_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateDfbcBasicControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_dfbc_basic_core(core_params, dfbc_basic_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateSmcBoundaryLayerControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.smc_lambda[0] = smc_lambda_[0];
  core_params.smc_lambda[1] = smc_lambda_[1];
  core_params.smc_lambda[2] = smc_lambda_[2];
  core_params.smc_eta[0] = smc_eta_[0];
  core_params.smc_eta[1] = smc_eta_[1];
  core_params.smc_eta[2] = smc_eta_[2];
  core_params.smc_phi[0] = smc_phi_[0];
  core_params.smc_phi[1] = smc_phi_[1];
  core_params.smc_phi[2] = smc_phi_[2];
  core_params.smc_surface_limit[0] = smc_surface_limit_[0];
  core_params.smc_surface_limit[1] = smc_surface_limit_[1];
  core_params.smc_surface_limit[2] = smc_surface_limit_[2];
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_smc_boundary_layer_core(core_params, smc_boundary_layer_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = core_output.sliding_surface.x;
  debug_msg_.des_v_y = core_output.sliding_surface.y;
  debug_msg_.des_v_z = core_output.sliding_surface.z;
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculatePidIndiControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.ki[0] = param_.gain.Kvi0;
  core_params.ki[1] = param_.gain.Kvi1;
  core_params.ki[2] = param_.gain.Kvi2;
  core_params.indi_gain[0] = indi_gain_[0];
  core_params.indi_gain[1] = indi_gain_[1];
  core_params.indi_gain[2] = indi_gain_[2];
  core_params.indi_increment_limit[0] = indi_increment_limit_[0];
  core_params.indi_increment_limit[1] = indi_increment_limit_[1];
  core_params.indi_increment_limit[2] = indi_increment_limit_[2];
  core_params.indi_measured_accel_limit[0] = indi_measured_accel_limit_[0];
  core_params.indi_measured_accel_limit[1] = indi_measured_accel_limit_[1];
  core_params.indi_measured_accel_limit[2] = indi_measured_accel_limit_[2];
  core_params.indi_accel_lpf_alpha = indi_accel_lpf_alpha_;
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.measurement_stamp_s = odom.rcv_stamp.toSec();
  core_input.measurement_stamp_valid = !odom.rcv_stamp.isZero();
  core_input.enable_disturbance_observer = use_dfbc_smooth_robust_dob_;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_pid_indi_bounded_core(core_params, pid_indi_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = core_output.sliding_surface.x;
  debug_msg_.des_v_y = core_output.sliding_surface.y;
  debug_msg_.des_v_z = core_output.sliding_surface.z;
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateNmpcOuterControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.nmpc_horizon_s = nmpc_horizon_s_;
  core_params.nmpc_position_weight[0] = nmpc_position_weight_[0];
  core_params.nmpc_position_weight[1] = nmpc_position_weight_[1];
  core_params.nmpc_position_weight[2] = nmpc_position_weight_[2];
  core_params.nmpc_velocity_weight[0] = nmpc_velocity_weight_[0];
  core_params.nmpc_velocity_weight[1] = nmpc_velocity_weight_[1];
  core_params.nmpc_velocity_weight[2] = nmpc_velocity_weight_[2];
  core_params.nmpc_control_weight[0] = nmpc_control_weight_[0];
  core_params.nmpc_control_weight[1] = nmpc_control_weight_[1];
  core_params.nmpc_control_weight[2] = nmpc_control_weight_[2];
  core_params.nmpc_accel_limit[0] = nmpc_accel_limit_[0];
  core_params.nmpc_accel_limit[1] = nmpc_accel_limit_[1];
  core_params.nmpc_accel_limit[2] = nmpc_accel_limit_[2];
  core_params.nmpc_increment_limit[0] = nmpc_increment_limit_[0];
  core_params.nmpc_increment_limit[1] = nmpc_increment_limit_[1];
  core_params.nmpc_increment_limit[2] = nmpc_increment_limit_[2];
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_nmpc_outer_core(core_params, nmpc_outer_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = core_output.sliding_surface.x;
  debug_msg_.des_v_y = core_output.sliding_surface.y;
  debug_msg_.des_v_z = core_output.sliding_surface.z;
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateDfbcHighOrderControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;
  core_params.high_order_body_rate_limit[0] = high_order_body_rate_limit_[0];
  core_params.high_order_body_rate_limit[1] = high_order_body_rate_limit_[1];
  core_params.high_order_body_rate_limit[2] = high_order_body_rate_limit_[2];
  core_params.high_order_body_accel_limit[0] = high_order_body_accel_limit_[0];
  core_params.high_order_body_accel_limit[1] = high_order_body_accel_limit_[1];
  core_params.high_order_body_accel_limit[2] = high_order_body_accel_limit_[2];

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_jerk = mosim_px4ctrl::Vec3{des.j(0), des.j(1), des.j(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_dfbc_high_order_core(core_params, dfbc_high_order_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = Eigen::Vector3d(
      core_output.desired_body_rate.x,
      core_output.desired_body_rate.y,
      core_output.desired_body_rate.z);
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, u.bodyrates);
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateDfbcSmoothRobustControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;
  core_params.high_order_body_rate_limit[0] = high_order_body_rate_limit_[0];
  core_params.high_order_body_rate_limit[1] = high_order_body_rate_limit_[1];
  core_params.high_order_body_rate_limit[2] = high_order_body_rate_limit_[2];
  core_params.high_order_body_accel_limit[0] = high_order_body_accel_limit_[0];
  core_params.high_order_body_accel_limit[1] = high_order_body_accel_limit_[1];
  core_params.high_order_body_accel_limit[2] = high_order_body_accel_limit_[2];
  core_params.smooth_feedback_gain[0] = smooth_feedback_gain_[0];
  core_params.smooth_feedback_gain[1] = smooth_feedback_gain_[1];
  core_params.smooth_feedback_gain[2] = smooth_feedback_gain_[2];
  core_params.smooth_feedback_bound[0] = smooth_feedback_bound_[0];
  core_params.smooth_feedback_bound[1] = smooth_feedback_bound_[1];
  core_params.smooth_feedback_bound[2] = smooth_feedback_bound_[2];
  core_params.disturbance_observer_gain[0] = disturbance_observer_gain_[0];
  core_params.disturbance_observer_gain[1] = disturbance_observer_gain_[1];
  core_params.disturbance_observer_gain[2] = disturbance_observer_gain_[2];
  core_params.disturbance_compensation_limit[0] = disturbance_compensation_limit_[0];
  core_params.disturbance_compensation_limit[1] = disturbance_compensation_limit_[1];
  core_params.disturbance_compensation_limit[2] = disturbance_compensation_limit_[2];

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_jerk = mosim_px4ctrl::Vec3{des.j(0), des.j(1), des.j(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.measurement_stamp_s = odom.rcv_stamp.toSec();
  core_input.measurement_stamp_valid = !odom.rcv_stamp.isZero();
  core_input.enable_disturbance_observer = use_dfbc_smooth_robust_dob_;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_dfbc_smooth_robust_core(core_params, dfbc_smooth_robust_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = Eigen::Vector3d(
      core_output.desired_body_rate.x,
      core_output.desired_body_rate.y,
      core_output.desired_body_rate.z);
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, u.bodyrates);
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = u.bodyrates.x();
  debug_msg_.des_v_y = u.bodyrates.y();
  debug_msg_.des_v_z = u.bodyrates.z();
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateDfbcSmoothRobustIndiControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;
  core_params.high_order_body_rate_limit[0] = high_order_body_rate_limit_[0];
  core_params.high_order_body_rate_limit[1] = high_order_body_rate_limit_[1];
  core_params.high_order_body_rate_limit[2] = high_order_body_rate_limit_[2];
  core_params.high_order_body_accel_limit[0] = high_order_body_accel_limit_[0];
  core_params.high_order_body_accel_limit[1] = high_order_body_accel_limit_[1];
  core_params.high_order_body_accel_limit[2] = high_order_body_accel_limit_[2];
  core_params.smooth_feedback_gain[0] = smooth_feedback_gain_[0];
  core_params.smooth_feedback_gain[1] = smooth_feedback_gain_[1];
  core_params.smooth_feedback_gain[2] = smooth_feedback_gain_[2];
  core_params.smooth_feedback_bound[0] = smooth_feedback_bound_[0];
  core_params.smooth_feedback_bound[1] = smooth_feedback_bound_[1];
  core_params.smooth_feedback_bound[2] = smooth_feedback_bound_[2];
  core_params.disturbance_observer_gain[0] = disturbance_observer_gain_[0];
  core_params.disturbance_observer_gain[1] = disturbance_observer_gain_[1];
  core_params.disturbance_observer_gain[2] = disturbance_observer_gain_[2];
  core_params.disturbance_compensation_limit[0] = disturbance_compensation_limit_[0];
  core_params.disturbance_compensation_limit[1] = disturbance_compensation_limit_[1];
  core_params.disturbance_compensation_limit[2] = disturbance_compensation_limit_[2];
  core_params.indi_gain[0] = indi_gain_[0];
  core_params.indi_gain[1] = indi_gain_[1];
  core_params.indi_gain[2] = indi_gain_[2];
  core_params.indi_increment_limit[0] = indi_increment_limit_[0];
  core_params.indi_increment_limit[1] = indi_increment_limit_[1];
  core_params.indi_increment_limit[2] = indi_increment_limit_[2];
  core_params.indi_measured_accel_limit[0] = indi_measured_accel_limit_[0];
  core_params.indi_measured_accel_limit[1] = indi_measured_accel_limit_[1];
  core_params.indi_measured_accel_limit[2] = indi_measured_accel_limit_[2];
  core_params.indi_accel_lpf_alpha = indi_accel_lpf_alpha_;

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_jerk = mosim_px4ctrl::Vec3{des.j(0), des.j(1), des.j(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.measurement_stamp_s = odom.rcv_stamp.toSec();
  core_input.measurement_stamp_valid = !odom.rcv_stamp.isZero();
  core_input.enable_disturbance_observer = false;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(core_params, dfbc_smooth_robust_indi_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = Eigen::Vector3d(
      core_output.desired_body_rate.x,
      core_output.desired_body_rate.y,
      core_output.desired_body_rate.z);
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, u.bodyrates);
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = u.bodyrates.x();
  debug_msg_.des_v_y = u.bodyrates.y();
  debug_msg_.des_v_z = u.bodyrates.z();
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateL1AwffControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.ki[0] = param_.gain.Kvi0;
  core_params.ki[1] = param_.gain.Kvi1;
  core_params.ki[2] = param_.gain.Kvi2;
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;
  core_params.l1_model_decay = l1_model_decay_;
  core_params.l1_filter_T = l1_filter_T_;
  for (int i = 0; i < 3; ++i)
  {
    core_params.l1_gain[i] = l1_gain_[i];
    core_params.l1_comp_limit[i] = l1_comp_limit_[i];
    core_params.drag_feedforward_gain[i] = drag_feedforward_gain_[i];
  }

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.measurement_stamp_s = odom.rcv_stamp.toSec();
  core_input.measurement_stamp_valid = !odom.rcv_stamp.isZero();
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_l1_awff_core(core_params, l1_awff_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = core_output.disturbance_estimate.x;
  debug_msg_.des_v_y = core_output.disturbance_estimate.y;
  debug_msg_.des_v_z = core_output.disturbance_estimate.z;
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateSafetyFilterControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.ki[0] = param_.gain.Kvi0;
  core_params.ki[1] = param_.gain.Kvi1;
  core_params.ki[2] = param_.gain.Kvi2;
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;
  for (int i = 0; i < 3; ++i)
  {
    core_params.safety_accel_limit[i] = safety_accel_limit_[i];
  }

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_safety_filter_core(core_params, safety_filter_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = core_output.sliding_surface.x;
  debug_msg_.des_v_y = core_output.sliding_surface.y;
  debug_msg_.des_v_z = core_output.sliding_surface.z;
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateFaultAllocationControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  mosim_px4ctrl::CoreParams core_params;
  core_params.kp[0] = param_.gain.Kp0;
  core_params.kp[1] = param_.gain.Kp1;
  core_params.kp[2] = param_.gain.Kp2;
  core_params.kv[0] = param_.gain.Kv0;
  core_params.kv[1] = param_.gain.Kv1;
  core_params.kv[2] = param_.gain.Kv2;
  core_params.ki[0] = param_.gain.Kvi0;
  core_params.ki[1] = param_.gain.Kvi1;
  core_params.ki[2] = param_.gain.Kvi2;
  core_params.mass = param_.mass;
  core_params.gravity = param_.gra;
  core_params.hover_percentage = param_.gra / thr2acc_;
  core_params.min_normalized_thrust = 0.0;
  core_params.max_normalized_thrust = 1.0;
  core_params.tilt_limit_rad = param_.max_angle > 0.0 ? param_.max_angle : 1.5707963267948966;
  for (int i = 0; i < 4; ++i)
  {
    core_params.fault_rotor_efficiency[i] = fault_rotor_efficiency_[i];
  }
  core_params.fault_allocation_blend = fault_allocation_blend_;
  core_params.fault_min_efficiency = fault_min_efficiency_;
  core_params.fault_thrust_comp_limit = fault_thrust_comp_limit_;

  mosim_px4ctrl::ControllerInput core_input;
  core_input.dt = 0.01;
  core_input.position = mosim_px4ctrl::Vec3{odom.p(0), odom.p(1), odom.p(2)};
  core_input.velocity = mosim_px4ctrl::Vec3{odom.v(0), odom.v(1), odom.v(2)};
  core_input.attitude = mosim_px4ctrl::Quat{odom.q.w(), odom.q.x(), odom.q.y(), odom.q.z()};
  core_input.angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.reference_position = mosim_px4ctrl::Vec3{des.p(0), des.p(1), des.p(2)};
  core_input.reference_velocity = mosim_px4ctrl::Vec3{des.v(0), des.v(1), des.v(2)};
  core_input.reference_acceleration = mosim_px4ctrl::Vec3{des.a(0), des.a(1), des.a(2)};
  core_input.reference_yaw = des.yaw;
  core_input.reference_yaw_rate = des.yaw_rate;
  core_input.imu_attitude = mosim_px4ctrl::Quat{imu.q.w(), imu.q.x(), imu.q.y(), imu.q.z()};
  core_input.imu_angular_velocity = mosim_px4ctrl::Vec3{imu.w(0), imu.w(1), imu.w(2)};
  core_input.enable = true;
  core_input.reset = generated_core_reset_pending_;

  const mosim_px4ctrl::ControllerOutput core_output =
      mosim_px4ctrl::calculate_fault_allocation_core(core_params, fault_allocation_core_state_, core_input);
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      core_output.desired_attitude.w,
      core_output.desired_attitude.x,
      core_output.desired_attitude.y,
      core_output.desired_attitude.z);
  u.q.normalize();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
  u.thrust = core_output.normalized_thrust;

  debug_msg_.des_v_x = core_output.disturbance_estimate.x;
  debug_msg_.des_v_y = core_output.disturbance_estimate.y;
  debug_msg_.des_v_z = core_output.disturbance_estimate.z;
  debug_msg_.des_a_x = core_output.desired_acceleration.x;
  debug_msg_.des_a_y = core_output.desired_acceleration.y;
  debug_msg_.des_a_z = core_output.desired_acceleration.z;
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateGeneratedCoreControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
#if !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST) && \
    !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
  const double effective_hover_percentage = param_.gra / thr2acc_;
#endif
  const double dt = 0.01;
  const bool reset_this_cycle = generated_core_reset_pending_;

#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
  const double effective_hover_percentage = param_.gra / thr2acc_;
  const double full_collective_thrust_n = std::max(param_.mass * thr2acc_, 1.0e-6);
  MOSIM_LEARNING_GB_IN.mode_in = static_cast<double>(generated_family_controller_id_);
  MOSIM_LEARNING_GB_IN.dt_in = dt;
  MOSIM_LEARNING_GB_IN.position_x_in = odom.p(0);
  MOSIM_LEARNING_GB_IN.position_y_in = odom.p(1);
  MOSIM_LEARNING_GB_IN.position_z_in = odom.p(2);
  MOSIM_LEARNING_GB_IN.velocity_x_in = odom.v(0);
  MOSIM_LEARNING_GB_IN.velocity_y_in = odom.v(1);
  MOSIM_LEARNING_GB_IN.velocity_z_in = odom.v(2);
  MOSIM_LEARNING_GB_IN.attitude_w_in = odom.q.w();
  MOSIM_LEARNING_GB_IN.attitude_x_in = odom.q.x();
  MOSIM_LEARNING_GB_IN.attitude_y_in = odom.q.y();
  MOSIM_LEARNING_GB_IN.attitude_z_in = odom.q.z();
  MOSIM_LEARNING_GB_IN.angular_velocity_x_in = imu.w(0);
  MOSIM_LEARNING_GB_IN.angular_velocity_y_in = imu.w(1);
  MOSIM_LEARNING_GB_IN.angular_velocity_z_in = imu.w(2);
  MOSIM_LEARNING_GB_IN.reference_position_x_in = des.p(0);
  MOSIM_LEARNING_GB_IN.reference_position_y_in = des.p(1);
  MOSIM_LEARNING_GB_IN.reference_position_z_in = des.p(2);
  MOSIM_LEARNING_GB_IN.reference_velocity_x_in = des.v(0);
  MOSIM_LEARNING_GB_IN.reference_velocity_y_in = des.v(1);
  MOSIM_LEARNING_GB_IN.reference_velocity_z_in = des.v(2);
  MOSIM_LEARNING_GB_IN.reference_acceleration_x_in = des.a(0);
  MOSIM_LEARNING_GB_IN.reference_acceleration_y_in = des.a(1);
  MOSIM_LEARNING_GB_IN.reference_acceleration_z_in = des.a(2);
  MOSIM_LEARNING_GB_IN.reference_yaw_in = des.yaw;
  MOSIM_LEARNING_GB_IN.mass_kg_in = param_.mass;
  MOSIM_LEARNING_GB_IN.gravity_mps2_in = param_.gra;
  MOSIM_LEARNING_GB_IN.hover_percentage_in = effective_hover_percentage;
  MOSIM_LEARNING_GB_IN.max_tilt_rad_in =
      param_.max_angle > 0.0 ? param_.max_angle : M_PI / 2.0 - 1.0e-6;
  MOSIM_LEARNING_GB_IN.min_collective_thrust_n_in = 0.0;
  MOSIM_LEARNING_GB_IN.max_collective_thrust_n_in = full_collective_thrust_n;
  MOSIM_LEARNING_GB_IN.enable_in = 1.0;
  MOSIM_LEARNING_GB_IN.learning_enable_in = 1.0;
  MOSIM_LEARNING_GB_IN.reset_in = reset_this_cycle ? 1.0 : 0.0;
  Step();
  generated_core_reset_pending_ = false;
  const bool generated_output_valid =
      MOSIM_LEARNING_GB_OUT.status_code_out == 0.0 &&
      MOSIM_LEARNING_GB_OUT.fallback_active_out == 0.0 &&
      std::isfinite(MOSIM_LEARNING_GB_OUT.normalized_thrust_out) &&
      std::isfinite(MOSIM_LEARNING_GB_OUT.desired_attitude_w_out) &&
      std::isfinite(MOSIM_LEARNING_GB_OUT.desired_attitude_x_out) &&
      std::isfinite(MOSIM_LEARNING_GB_OUT.desired_attitude_y_out) &&
      std::isfinite(MOSIM_LEARNING_GB_OUT.desired_attitude_z_out);
  if (!generated_output_valid)
  {
    ROS_ERROR_THROTTLE(1.0, "Learning ATTITUDE_THRUST generated backend returned invalid output");
    u.q = imu.q;
    u.bodyrates = Eigen::Vector3d::Zero();
    u.thrust = 0.0;
  }
  else
  {
    u.q = Eigen::Quaterniond(
        MOSIM_LEARNING_GB_OUT.desired_attitude_w_out,
        MOSIM_LEARNING_GB_OUT.desired_attitude_x_out,
        MOSIM_LEARNING_GB_OUT.desired_attitude_y_out,
        MOSIM_LEARNING_GB_OUT.desired_attitude_z_out);
    u.q.normalize();
    u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
    u.thrust = clamp_double(MOSIM_LEARNING_GB_OUT.normalized_thrust_out, 0.0, 1.0);
  }
  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = MOSIM_LEARNING_GB_OUT.desired_acceleration_x_out;
  debug_msg_.des_a_y = MOSIM_LEARNING_GB_OUT.desired_acceleration_y_out;
  debug_msg_.des_a_z = MOSIM_LEARNING_GB_OUT.desired_acceleration_z_out;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST)
  const Eigen::Vector3d position_error = des.p - odom.p;
  const double full_collective_thrust_n = std::max(param_.mass * thr2acc_, 1.0e-6);
  unction_sysblockGbIn.algorithm_id_in = static_cast<double>(generated_family_controller_id_);
  unction_sysblockGbIn.dt_in = dt;
  unction_sysblockGbIn.position_x_in = odom.p(0);
  unction_sysblockGbIn.position_y_in = odom.p(1);
  unction_sysblockGbIn.position_z_in = odom.p(2);
  unction_sysblockGbIn.velocity_x_in = odom.v(0);
  unction_sysblockGbIn.velocity_y_in = odom.v(1);
  unction_sysblockGbIn.velocity_z_in = odom.v(2);
  unction_sysblockGbIn.attitude_w_in = odom.q.w();
  unction_sysblockGbIn.attitude_x_in = odom.q.x();
  unction_sysblockGbIn.attitude_y_in = odom.q.y();
  unction_sysblockGbIn.attitude_z_in = odom.q.z();
  unction_sysblockGbIn.angular_velocity_x_in = imu.w(0);
  unction_sysblockGbIn.angular_velocity_y_in = imu.w(1);
  unction_sysblockGbIn.angular_velocity_z_in = imu.w(2);
  unction_sysblockGbIn.reference_position_x_in = des.p(0);
  unction_sysblockGbIn.reference_position_y_in = des.p(1);
  unction_sysblockGbIn.reference_position_z_in = des.p(2);
  unction_sysblockGbIn.reference_velocity_x_in = des.v(0);
  unction_sysblockGbIn.reference_velocity_y_in = des.v(1);
  unction_sysblockGbIn.reference_velocity_z_in = des.v(2);
  unction_sysblockGbIn.reference_acceleration_x_in = des.a(0);
  unction_sysblockGbIn.reference_acceleration_y_in = des.a(1);
  unction_sysblockGbIn.reference_acceleration_z_in = des.a(2);
  unction_sysblockGbIn.reference_yaw_in = des.yaw;
  unction_sysblockGbIn.mass_kg_in = param_.mass;
  unction_sysblockGbIn.gravity_mps2_in = param_.gra;
  unction_sysblockGbIn.max_tilt_rad_in = param_.max_angle > 0.0 ? param_.max_angle : M_PI / 2.0 - 1.0e-6;
  unction_sysblockGbIn.min_collective_thrust_n_in = 0.0;
  unction_sysblockGbIn.max_collective_thrust_n_in = full_collective_thrust_n;
  unction_sysblockGbIn.schedule_x_in = clamp_double(std::abs(position_error(0)), 0.0, 1.0);
  unction_sysblockGbIn.schedule_y_in = clamp_double(std::abs(position_error(1)), 0.0, 1.0);
  unction_sysblockGbIn.schedule_z_in = clamp_double(std::abs(position_error(2)), 0.0, 1.0);
  unction_sysblockGbIn.fuzzy_error_x_in = clamp_double(position_error(0), -1.0, 1.0);
  unction_sysblockGbIn.fuzzy_error_y_in = clamp_double(position_error(1), -1.0, 1.0);
  unction_sysblockGbIn.fuzzy_error_z_in = clamp_double(position_error(2), -1.0, 1.0);
  unction_sysblockGbIn.neural_residual_x_in = 0.0;
  unction_sysblockGbIn.neural_residual_y_in = 0.0;
  unction_sysblockGbIn.neural_residual_z_in = 0.0;
  unction_sysblockGbIn.enable_in = 1.0;
  unction_sysblockGbIn.reset_in = reset_this_cycle ? 1.0 : 0.0;

  Step();
  generated_core_reset_pending_ = false;

  const bool generated_output_valid =
      function_sysblockGbOut.status_code_out == 0.0 &&
      static_cast<int>(function_sysblockGbOut.algorithm_id_out_out) == generated_family_controller_id_ &&
      std::isfinite(function_sysblockGbOut.desired_collective_thrust_n_out);
  if (!generated_output_valid)
  {
    ROS_ERROR_THROTTLE(1.0, "PID ATTITUDE_THRUST generated backend returned invalid status or profile id");
    u.q = imu.q;
    u.bodyrates = Eigen::Vector3d::Zero();
    u.thrust = 0.0;
  }
  else
  {
    u.q = Eigen::Quaterniond(
        function_sysblockGbOut.desired_attitude_w_out,
        function_sysblockGbOut.desired_attitude_x_out,
        function_sysblockGbOut.desired_attitude_y_out,
        function_sysblockGbOut.desired_attitude_z_out);
    u.q.normalize();
    u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
    u.thrust = clamp_double(
        function_sysblockGbOut.desired_collective_thrust_n_out / full_collective_thrust_n,
        0.0, 1.0);
  }

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = function_sysblockGbOut.desired_acceleration_x_out;
  debug_msg_.des_a_y = function_sysblockGbOut.desired_acceleration_y_out;
  debug_msg_.des_a_z = function_sysblockGbOut.desired_acceleration_z_out;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY)
  GbIn.controller_id_in = static_cast<double>(generated_family_controller_id_);
  GbIn.dt_in = dt;
  GbIn.position_x_in = odom.p(0);
  GbIn.position_y_in = odom.p(1);
  GbIn.position_z_in = odom.p(2);
  GbIn.velocity_x_in = odom.v(0);
  GbIn.velocity_y_in = odom.v(1);
  GbIn.velocity_z_in = odom.v(2);
  GbIn.attitude_w_in = odom.q.w();
  GbIn.attitude_x_in = odom.q.x();
  GbIn.attitude_y_in = odom.q.y();
  GbIn.attitude_z_in = odom.q.z();
  GbIn.angular_velocity_x_in = imu.w(0);
  GbIn.angular_velocity_y_in = imu.w(1);
  GbIn.angular_velocity_z_in = imu.w(2);
  GbIn.reference_position_x_in = des.p(0);
  GbIn.reference_position_y_in = des.p(1);
  GbIn.reference_position_z_in = des.p(2);
  GbIn.reference_velocity_x_in = des.v(0);
  GbIn.reference_velocity_y_in = des.v(1);
  GbIn.reference_velocity_z_in = des.v(2);
  GbIn.reference_acceleration_x_in = des.a(0);
  GbIn.reference_acceleration_y_in = des.a(1);
  GbIn.reference_acceleration_z_in = des.a(2);
  GbIn.reference_jerk_x_in = des.j(0);
  GbIn.reference_jerk_y_in = des.j(1);
  GbIn.reference_jerk_z_in = des.j(2);
  GbIn.reference_snap_x_in = 0.0;
  GbIn.reference_snap_y_in = 0.0;
  GbIn.reference_snap_z_in = 0.0;
  GbIn.reference_yaw_in = des.yaw;
  GbIn.reference_yaw_rate_in = des.yaw_rate;
  GbIn.reference_yaw_acceleration_in = 0.0;
  GbIn.measurement_stamp_s_in = odom.rcv_stamp.toSec();
  GbIn.imu_attitude_w_in = imu.q.w();
  GbIn.imu_attitude_x_in = imu.q.x();
  GbIn.imu_attitude_y_in = imu.q.y();
  GbIn.imu_attitude_z_in = imu.q.z();
  GbIn.imu_angular_velocity_x_in = imu.w(0);
  GbIn.imu_angular_velocity_y_in = imu.w(1);
  GbIn.imu_angular_velocity_z_in = imu.w(2);
  GbIn.enable_in = 1.0;
  GbIn.reset_in = reset_this_cycle ? 1.0 : 0.0;
  GbIn.measurement_stamp_valid_in = odom.rcv_stamp.isZero() ? 0.0 : 1.0;
  GbIn.enable_disturbance_observer_in = 0.0;
  GbIn.kp_x_in = param_.gain.Kp0;
  GbIn.kp_y_in = param_.gain.Kp1;
  GbIn.kp_z_in = param_.gain.Kp2;
  GbIn.kv_x_in = param_.gain.Kv0;
  GbIn.kv_y_in = param_.gain.Kv1;
  GbIn.kv_z_in = param_.gain.Kv2;
  GbIn.ki_x_in = param_.gain.Kvi0;
  GbIn.ki_y_in = param_.gain.Kvi1;
  GbIn.ki_z_in = param_.gain.Kvi2;
  GbIn.smc_lambda_x_in = smc_lambda_[0];
  GbIn.smc_lambda_y_in = smc_lambda_[1];
  GbIn.smc_lambda_z_in = smc_lambda_[2];
  GbIn.smc_eta_x_in = smc_eta_[0];
  GbIn.smc_eta_y_in = smc_eta_[1];
  GbIn.smc_eta_z_in = smc_eta_[2];
  GbIn.smc_phi_x_in = smc_phi_[0];
  GbIn.smc_phi_y_in = smc_phi_[1];
  GbIn.smc_phi_z_in = smc_phi_[2];
  GbIn.smc_surface_limit_x_in = smc_surface_limit_[0];
  GbIn.smc_surface_limit_y_in = smc_surface_limit_[1];
  GbIn.smc_surface_limit_z_in = smc_surface_limit_[2];
  GbIn.indi_gain_x_in = indi_gain_[0];
  GbIn.indi_gain_y_in = indi_gain_[1];
  GbIn.indi_gain_z_in = indi_gain_[2];
  GbIn.indi_increment_limit_x_in = indi_increment_limit_[0];
  GbIn.indi_increment_limit_y_in = indi_increment_limit_[1];
  GbIn.indi_increment_limit_z_in = indi_increment_limit_[2];
  GbIn.indi_measured_accel_limit_x_in = indi_measured_accel_limit_[0];
  GbIn.indi_measured_accel_limit_y_in = indi_measured_accel_limit_[1];
  GbIn.indi_measured_accel_limit_z_in = indi_measured_accel_limit_[2];
  GbIn.indi_accel_lpf_alpha_in = indi_accel_lpf_alpha_;
  GbIn.nmpc_horizon_s_in = nmpc_horizon_s_;
  GbIn.nmpc_position_weight_x_in = nmpc_position_weight_[0];
  GbIn.nmpc_position_weight_y_in = nmpc_position_weight_[1];
  GbIn.nmpc_position_weight_z_in = nmpc_position_weight_[2];
  GbIn.nmpc_velocity_weight_x_in = nmpc_velocity_weight_[0];
  GbIn.nmpc_velocity_weight_y_in = nmpc_velocity_weight_[1];
  GbIn.nmpc_velocity_weight_z_in = nmpc_velocity_weight_[2];
  GbIn.nmpc_control_weight_x_in = nmpc_control_weight_[0];
  GbIn.nmpc_control_weight_y_in = nmpc_control_weight_[1];
  GbIn.nmpc_control_weight_z_in = nmpc_control_weight_[2];
  GbIn.nmpc_accel_limit_x_in = nmpc_accel_limit_[0];
  GbIn.nmpc_accel_limit_y_in = nmpc_accel_limit_[1];
  GbIn.nmpc_accel_limit_z_in = nmpc_accel_limit_[2];
  GbIn.nmpc_increment_limit_x_in = nmpc_increment_limit_[0];
  GbIn.nmpc_increment_limit_y_in = nmpc_increment_limit_[1];
  GbIn.nmpc_increment_limit_z_in = nmpc_increment_limit_[2];
  GbIn.integral_limit_x_in = 0.5;
  GbIn.integral_limit_y_in = 0.5;
  GbIn.integral_limit_z_in = 0.3;
  GbIn.mass_in = param_.mass;
  GbIn.gravity_in = param_.gra;
  GbIn.hover_percentage_in = effective_hover_percentage;
  GbIn.min_normalized_thrust_in = 0.0;
  GbIn.max_normalized_thrust_in = 1.0;
  GbIn.tilt_limit_rad_in = param_.max_angle > 0.0 ? param_.max_angle : M_PI / 2.0;

  Step();
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      kGbOut.desired_attitude_w_out,
      kGbOut.desired_attitude_x_out,
      kGbOut.desired_attitude_y_out,
      kGbOut.desired_attitude_z_out);
  u.q.normalize();
  u.bodyrates = Eigen::Vector3d::Zero();
  u.thrust = kGbOut.normalized_thrust_out;

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = kGbOut.desired_acceleration_x_out;
  debug_msg_.des_a_y = kGbOut.desired_acceleration_y_out;
  debug_msg_.des_a_z = kGbOut.desired_acceleration_z_out;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G10_BDE_FAMILY)
  sblock_stateisoGbIn.controller_id_in = static_cast<double>(generated_family_controller_id_);
  sblock_stateisoGbIn.dt_in = dt;
  sblock_stateisoGbIn.position_x_in = odom.p(0);
  sblock_stateisoGbIn.position_y_in = odom.p(1);
  sblock_stateisoGbIn.position_z_in = odom.p(2);
  sblock_stateisoGbIn.velocity_x_in = odom.v(0);
  sblock_stateisoGbIn.velocity_y_in = odom.v(1);
  sblock_stateisoGbIn.velocity_z_in = odom.v(2);
  sblock_stateisoGbIn.attitude_w_in = odom.q.w();
  sblock_stateisoGbIn.attitude_x_in = odom.q.x();
  sblock_stateisoGbIn.attitude_y_in = odom.q.y();
  sblock_stateisoGbIn.attitude_z_in = odom.q.z();
  sblock_stateisoGbIn.angular_velocity_x_in = imu.w(0);
  sblock_stateisoGbIn.angular_velocity_y_in = imu.w(1);
  sblock_stateisoGbIn.angular_velocity_z_in = imu.w(2);
  sblock_stateisoGbIn.reference_position_x_in = des.p(0);
  sblock_stateisoGbIn.reference_position_y_in = des.p(1);
  sblock_stateisoGbIn.reference_position_z_in = des.p(2);
  sblock_stateisoGbIn.reference_velocity_x_in = des.v(0);
  sblock_stateisoGbIn.reference_velocity_y_in = des.v(1);
  sblock_stateisoGbIn.reference_velocity_z_in = des.v(2);
  sblock_stateisoGbIn.reference_acceleration_x_in = des.a(0);
  sblock_stateisoGbIn.reference_acceleration_y_in = des.a(1);
  sblock_stateisoGbIn.reference_acceleration_z_in = des.a(2);
  sblock_stateisoGbIn.reference_jerk_x_in = des.j(0);
  sblock_stateisoGbIn.reference_jerk_y_in = des.j(1);
  sblock_stateisoGbIn.reference_jerk_z_in = des.j(2);
  sblock_stateisoGbIn.reference_snap_x_in = 0.0;
  sblock_stateisoGbIn.reference_snap_y_in = 0.0;
  sblock_stateisoGbIn.reference_snap_z_in = 0.0;
  sblock_stateisoGbIn.reference_yaw_in = des.yaw;
  sblock_stateisoGbIn.reference_yaw_rate_in = des.yaw_rate;
  sblock_stateisoGbIn.reference_yaw_acceleration_in = 0.0;
  sblock_stateisoGbIn.measurement_stamp_s_in = odom.rcv_stamp.toSec();
  sblock_stateisoGbIn.imu_attitude_w_in = imu.q.w();
  sblock_stateisoGbIn.imu_attitude_x_in = imu.q.x();
  sblock_stateisoGbIn.imu_attitude_y_in = imu.q.y();
  sblock_stateisoGbIn.imu_attitude_z_in = imu.q.z();
  sblock_stateisoGbIn.imu_angular_velocity_x_in = imu.w(0);
  sblock_stateisoGbIn.imu_angular_velocity_y_in = imu.w(1);
  sblock_stateisoGbIn.imu_angular_velocity_z_in = imu.w(2);
  sblock_stateisoGbIn.enable_in = 1.0;
  sblock_stateisoGbIn.reset_in = reset_this_cycle ? 1.0 : 0.0;
  sblock_stateisoGbIn.measurement_stamp_valid_in = odom.rcv_stamp.isZero() ? 0.0 : 1.0;
  sblock_stateisoGbIn.enable_disturbance_observer_in = 0.0;
  sblock_stateisoGbIn.kp_x_in = param_.gain.Kp0;
  sblock_stateisoGbIn.kp_y_in = param_.gain.Kp1;
  sblock_stateisoGbIn.kp_z_in = param_.gain.Kp2;
  sblock_stateisoGbIn.kv_x_in = param_.gain.Kv0;
  sblock_stateisoGbIn.kv_y_in = param_.gain.Kv1;
  sblock_stateisoGbIn.kv_z_in = param_.gain.Kv2;
  sblock_stateisoGbIn.ki_x_in = param_.gain.Kvi0;
  sblock_stateisoGbIn.ki_y_in = param_.gain.Kvi1;
  sblock_stateisoGbIn.ki_z_in = param_.gain.Kvi2;
  sblock_stateisoGbIn.smc_lambda_x_in = smc_lambda_[0];
  sblock_stateisoGbIn.smc_lambda_y_in = smc_lambda_[1];
  sblock_stateisoGbIn.smc_lambda_z_in = smc_lambda_[2];
  sblock_stateisoGbIn.smc_eta_x_in = smc_eta_[0];
  sblock_stateisoGbIn.smc_eta_y_in = smc_eta_[1];
  sblock_stateisoGbIn.smc_eta_z_in = smc_eta_[2];
  sblock_stateisoGbIn.smc_phi_x_in = smc_phi_[0];
  sblock_stateisoGbIn.smc_phi_y_in = smc_phi_[1];
  sblock_stateisoGbIn.smc_phi_z_in = smc_phi_[2];
  sblock_stateisoGbIn.smc_surface_limit_x_in = smc_surface_limit_[0];
  sblock_stateisoGbIn.smc_surface_limit_y_in = smc_surface_limit_[1];
  sblock_stateisoGbIn.smc_surface_limit_z_in = smc_surface_limit_[2];
  sblock_stateisoGbIn.indi_gain_x_in = indi_gain_[0];
  sblock_stateisoGbIn.indi_gain_y_in = indi_gain_[1];
  sblock_stateisoGbIn.indi_gain_z_in = indi_gain_[2];
  sblock_stateisoGbIn.indi_increment_limit_x_in = indi_increment_limit_[0];
  sblock_stateisoGbIn.indi_increment_limit_y_in = indi_increment_limit_[1];
  sblock_stateisoGbIn.indi_increment_limit_z_in = indi_increment_limit_[2];
  sblock_stateisoGbIn.indi_measured_accel_limit_x_in = indi_measured_accel_limit_[0];
  sblock_stateisoGbIn.indi_measured_accel_limit_y_in = indi_measured_accel_limit_[1];
  sblock_stateisoGbIn.indi_measured_accel_limit_z_in = indi_measured_accel_limit_[2];
  sblock_stateisoGbIn.indi_accel_lpf_alpha_in = indi_accel_lpf_alpha_;
  sblock_stateisoGbIn.nmpc_horizon_s_in = nmpc_horizon_s_;
  sblock_stateisoGbIn.nmpc_position_weight_x_in = nmpc_position_weight_[0];
  sblock_stateisoGbIn.nmpc_position_weight_y_in = nmpc_position_weight_[1];
  sblock_stateisoGbIn.nmpc_position_weight_z_in = nmpc_position_weight_[2];
  sblock_stateisoGbIn.nmpc_velocity_weight_x_in = nmpc_velocity_weight_[0];
  sblock_stateisoGbIn.nmpc_velocity_weight_y_in = nmpc_velocity_weight_[1];
  sblock_stateisoGbIn.nmpc_velocity_weight_z_in = nmpc_velocity_weight_[2];
  sblock_stateisoGbIn.nmpc_control_weight_x_in = nmpc_control_weight_[0];
  sblock_stateisoGbIn.nmpc_control_weight_y_in = nmpc_control_weight_[1];
  sblock_stateisoGbIn.nmpc_control_weight_z_in = nmpc_control_weight_[2];
  sblock_stateisoGbIn.nmpc_accel_limit_x_in = nmpc_accel_limit_[0];
  sblock_stateisoGbIn.nmpc_accel_limit_y_in = nmpc_accel_limit_[1];
  sblock_stateisoGbIn.nmpc_accel_limit_z_in = nmpc_accel_limit_[2];
  sblock_stateisoGbIn.nmpc_increment_limit_x_in = nmpc_increment_limit_[0];
  sblock_stateisoGbIn.nmpc_increment_limit_y_in = nmpc_increment_limit_[1];
  sblock_stateisoGbIn.nmpc_increment_limit_z_in = nmpc_increment_limit_[2];
  sblock_stateisoGbIn.l1_model_decay_in = l1_model_decay_;
  sblock_stateisoGbIn.l1_filter_T_in = l1_filter_T_;
  sblock_stateisoGbIn.l1_gain_x_in = l1_gain_[0];
  sblock_stateisoGbIn.l1_gain_y_in = l1_gain_[1];
  sblock_stateisoGbIn.l1_gain_z_in = l1_gain_[2];
  sblock_stateisoGbIn.l1_comp_limit_x_in = l1_comp_limit_[0];
  sblock_stateisoGbIn.l1_comp_limit_y_in = l1_comp_limit_[1];
  sblock_stateisoGbIn.l1_comp_limit_z_in = l1_comp_limit_[2];
  sblock_stateisoGbIn.drag_feedforward_gain_x_in = drag_feedforward_gain_[0];
  sblock_stateisoGbIn.drag_feedforward_gain_y_in = drag_feedforward_gain_[1];
  sblock_stateisoGbIn.drag_feedforward_gain_z_in = drag_feedforward_gain_[2];
  sblock_stateisoGbIn.safety_accel_limit_x_in = safety_accel_limit_[0];
  sblock_stateisoGbIn.safety_accel_limit_y_in = safety_accel_limit_[1];
  sblock_stateisoGbIn.safety_accel_limit_z_in = safety_accel_limit_[2];
  sblock_stateisoGbIn.fault_rotor_efficiency_1_in = fault_rotor_efficiency_[0];
  sblock_stateisoGbIn.fault_rotor_efficiency_2_in = fault_rotor_efficiency_[1];
  sblock_stateisoGbIn.fault_rotor_efficiency_3_in = fault_rotor_efficiency_[2];
  sblock_stateisoGbIn.fault_rotor_efficiency_4_in = fault_rotor_efficiency_[3];
  sblock_stateisoGbIn.fault_allocation_blend_in = fault_allocation_blend_;
  sblock_stateisoGbIn.fault_min_efficiency_in = fault_min_efficiency_;
  sblock_stateisoGbIn.fault_thrust_comp_limit_in = fault_thrust_comp_limit_;
  sblock_stateisoGbIn.integral_limit_x_in = 0.5;
  sblock_stateisoGbIn.integral_limit_y_in = 0.5;
  sblock_stateisoGbIn.integral_limit_z_in = 0.3;
  sblock_stateisoGbIn.mass_in = param_.mass;
  sblock_stateisoGbIn.gravity_in = param_.gra;
  sblock_stateisoGbIn.hover_percentage_in = effective_hover_percentage;
  sblock_stateisoGbIn.min_normalized_thrust_in = 0.0;
  sblock_stateisoGbIn.max_normalized_thrust_in = 1.0;
  sblock_stateisoGbIn.tilt_limit_rad_in = param_.max_angle > 0.0 ? param_.max_angle : M_PI / 2.0;

  Step();
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      ysblock_stateisoGbOut.desired_attitude_w_out,
      ysblock_stateisoGbOut.desired_attitude_x_out,
      ysblock_stateisoGbOut.desired_attitude_y_out,
      ysblock_stateisoGbOut.desired_attitude_z_out);
  u.q.normalize();
  u.bodyrates = Eigen::Vector3d::Zero();
  u.thrust = ysblock_stateisoGbOut.normalized_thrust_out;

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = ysblock_stateisoGbOut.desired_acceleration_x_out;
  debug_msg_.des_a_y = ysblock_stateisoGbOut.desired_acceleration_y_out;
  debug_msg_.des_a_z = ysblock_stateisoGbOut.desired_acceleration_z_out;
#else
  lockGbIn.dt_in = dt;
  lockGbIn.position_x_in = odom.p(0);
  lockGbIn.position_y_in = odom.p(1);
  lockGbIn.position_z_in = odom.p(2);
  lockGbIn.velocity_x_in = odom.v(0);
  lockGbIn.velocity_y_in = odom.v(1);
  lockGbIn.velocity_z_in = odom.v(2);
  lockGbIn.attitude_w_in = odom.q.w();
  lockGbIn.attitude_x_in = odom.q.x();
  lockGbIn.attitude_y_in = odom.q.y();
  lockGbIn.attitude_z_in = odom.q.z();
  lockGbIn.angular_velocity_x_in = imu.w(0);
  lockGbIn.angular_velocity_y_in = imu.w(1);
  lockGbIn.angular_velocity_z_in = imu.w(2);
  lockGbIn.reference_position_x_in = des.p(0);
  lockGbIn.reference_position_y_in = des.p(1);
  lockGbIn.reference_position_z_in = des.p(2);
  lockGbIn.reference_velocity_x_in = des.v(0);
  lockGbIn.reference_velocity_y_in = des.v(1);
  lockGbIn.reference_velocity_z_in = des.v(2);
  lockGbIn.reference_acceleration_x_in = des.a(0);
  lockGbIn.reference_acceleration_y_in = des.a(1);
  lockGbIn.reference_acceleration_z_in = des.a(2);
  lockGbIn.reference_yaw_in = des.yaw;
  lockGbIn.reference_yaw_rate_in = des.yaw_rate;
  lockGbIn.imu_attitude_w_in = imu.q.w();
  lockGbIn.imu_attitude_x_in = imu.q.x();
  lockGbIn.imu_attitude_y_in = imu.q.y();
  lockGbIn.imu_attitude_z_in = imu.q.z();
  lockGbIn.imu_angular_velocity_x_in = imu.w(0);
  lockGbIn.imu_angular_velocity_y_in = imu.w(1);
  lockGbIn.imu_angular_velocity_z_in = imu.w(2);
  lockGbIn.enable_in = 1.0;
  lockGbIn.reset_in = reset_this_cycle ? 1.0 : 0.0;
  lockGbIn.kp_x_in = param_.gain.Kp0;
  lockGbIn.kp_y_in = param_.gain.Kp1;
  lockGbIn.kp_z_in = param_.gain.Kp2;
  lockGbIn.kv_x_in = param_.gain.Kv0;
  lockGbIn.kv_y_in = param_.gain.Kv1;
  lockGbIn.kv_z_in = param_.gain.Kv2;
  lockGbIn.mass_in = param_.mass;
  lockGbIn.gravity_in = param_.gra;
  lockGbIn.hover_percentage_in = effective_hover_percentage;

  Step();
  generated_core_reset_pending_ = false;

  u.q = Eigen::Quaterniond(
      blockGbOut.desired_attitude_w_out,
      blockGbOut.desired_attitude_x_out,
      blockGbOut.desired_attitude_y_out,
      blockGbOut.desired_attitude_z_out);
  u.q.normalize();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
  u.thrust = blockGbOut.normalized_thrust_out;

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = blockGbOut.desired_acceleration_x_out;
  debug_msg_.des_a_y = blockGbOut.desired_acceleration_y_out;
  debug_msg_.des_a_z = blockGbOut.desired_acceleration_z_out;
#endif
  debug_msg_.des_q_x = u.q.x();
  debug_msg_.des_q_y = u.q.y();
  debug_msg_.des_q_z = u.q.z();
  debug_msg_.des_q_w = u.q.w();
  debug_msg_.des_thr = u.thrust;

  timed_thrust_.push(std::pair<ros::Time, double>(ros::Time::now(), u.thrust));
  while (timed_thrust_.size() > 100)
  {
    timed_thrust_.pop();
  }
  return debug_msg_;
}

/*
  compute throttle percentage 
*/
double 
LinearControl::computeDesiredCollectiveThrustSignal(
    const Eigen::Vector3d &des_acc)
{
  double throttle_percentage(0.0);
  
  /* compute throttle, thr2acc has been estimated before */
  throttle_percentage = des_acc(2) / thr2acc_;

  return throttle_percentage;
}

bool 
LinearControl::estimateThrustModel(
    const Eigen::Vector3d &est_a,
    const Parameter_t &param)
{
  ros::Time t_now = ros::Time::now();
  while (timed_thrust_.size() >= 1)
  {
    // Choose data before 35~45ms ago
    std::pair<ros::Time, double> t_t = timed_thrust_.front();
    double time_passed = (t_now - t_t.first).toSec();
    if (time_passed > 0.045) // 45ms
    {
      // printf("continue, time_passed=%f\n", time_passed);
      timed_thrust_.pop();
      continue;
    }
    if (time_passed < 0.035) // 35ms
    {
      // printf("skip, time_passed=%f\n", time_passed);
      return false;
    }

    /***********************************************************/
    /* Recursive least squares algorithm with vanishing memory */
    /***********************************************************/
    double thr = t_t.second;
    timed_thrust_.pop();
    
    /***********************************/
    /* Model: est_a(2) = thr1acc_ * thr */
    /***********************************/
    double gamma = 1 / (rho2_ + thr * P_ * thr);
    double K = gamma * P_ * thr;
    thr2acc_ = thr2acc_ + K * (est_a(2) - thr * thr2acc_);
    P_ = (1 - K * thr) * P_ / rho2_;
    //printf("%6.3f,%6.3f,%6.3f,%6.3f\n", thr2acc_, gamma, K, P_);
    //fflush(stdout);

    // debug_msg_.thr2acc = thr2acc_;
    return true;
  }
  return false;
}

void 
LinearControl::resetThrustMapping(void)
{
  thr2acc_ = param_.gra / param_.thr_map.hover_percentage;
  P_ = 1e6;
  generated_core_reset_pending_ = true;
  mosim_px4ctrl::CoreParams params;
  params.gravity = param_.gra;
  params.hover_percentage = param_.thr_map.hover_percentage;
  mosim_px4ctrl::reset_thrust_mapping(params, official_pid_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, se3_basic_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, dfbc_basic_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, smc_boundary_layer_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, pid_indi_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, nmpc_outer_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, dfbc_high_order_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, dfbc_smooth_robust_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, dfbc_smooth_robust_indi_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, l1_awff_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, safety_filter_core_state_);
  mosim_px4ctrl::reset_thrust_mapping(params, fault_allocation_core_state_);
}
