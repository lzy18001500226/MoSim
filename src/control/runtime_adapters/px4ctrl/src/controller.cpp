#include "controller.h"

#include <algorithm>
#include <cmath>

extern "C" {
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_GRAPHICAL_PX4CTRL_C99)
#include "px4ctrl_graphical_generated_shared.h"
// In graphical-C99 builds the legacy CFunction declarations remain available
// only for inactive compatibility methods compiled into this ROS adapter.
#include "PX4CTRL_Core_CFunction_Sysblock_private.h"
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY)
#include "G9_Family_CFunction_Sysblock_private.h"
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G10_BDE_FAMILY)
#include "G10_BDE_Family_CFunction_Sysblock_StateIso_private.h"
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST)
#include "MoSim_PID_AttitudeThrust_CFunction_Sysblock_private.h"
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST)
#include "MoSim_WaveA_CFunction_Sysblock_private.h"
#define MOSIM_ATTITUDE_THRUST_GB_IN ockGbIn
#define MOSIM_ATTITUDE_THRUST_GB_OUT lockGbOut
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST)
#include "MoSim_P2_LinearRobust_CFunction_Sysblock_private.h"
#define MOSIM_ATTITUDE_THRUST_GB_IN tion_sysblockGbIn
#define MOSIM_ATTITUDE_THRUST_GB_OUT ction_sysblockGbOut
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST)
#include "MoSim_Classic_CFunction_Sysblock_private.h"
#define MOSIM_ATTITUDE_THRUST_GB_IN blockGbIn
#define MOSIM_ATTITUDE_THRUST_GB_OUT sblockGbOut
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST)
#include "MoSim_P3_SlidingMode_CFunction_Sysblock_private.h"
#define MOSIM_ATTITUDE_THRUST_GB_IN ion_sysblockGbIn
#define MOSIM_ATTITUDE_THRUST_GB_OUT tion_sysblockGbOut
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST)
#include "MoSim_P4_Mpc_CFunction_Sysblock_private.h"
#define MOSIM_ATTITUDE_THRUST_GB_IN lockGbIn
#define MOSIM_ATTITUDE_THRUST_GB_OUT blockGbOut
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST)
#include "MoSim_P5_Enhancement_CFunction_Sysblock_private.h"
#define MOSIM_ATTITUDE_THRUST_GB_IN ion_sysblockGbIn
#define MOSIM_ATTITUDE_THRUST_GB_OUT tion_sysblockGbOut
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
#include "MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock_private.h"
#define MOSIM_LEARNING_GB_IN hrust_cfunction_sysblockGbIn
#define MOSIM_LEARNING_GB_OUT thrust_cfunction_sysblockGbOut
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SAFETY_SUPERVISOR)
#include "MoSim_P6_SafetySupervisor_CFunction_Sysblock_private.h"
#define MOSIM_SAFETY_GB_IN function_sysblockGbIn
#define MOSIM_SAFETY_GB_OUT cfunction_sysblockGbOut
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_L1_AWFF)
#include "MoSim_P10_G10_BDE_CFunction_Sysblock_private.h"
#define MOSIM_P10_BDE_GB_IN asysblockGbIn
#define MOSIM_P10_BDE_GB_OUT n_sysblockGbOut
#define sblock_stateisoGbIn MOSIM_P10_BDE_GB_IN
#define ysblock_stateisoGbOut MOSIM_P10_BDE_GB_OUT
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY)
#include "MoSim_P10_DFBC_Family_CFunction_Sysblock_private.h"
#define MOSIM_P10_BDE_GB_IN tion_sysblockGbIn
#define MOSIM_P10_BDE_GB_OUT ction_sysblockGbOut
#define sblock_stateisoGbIn MOSIM_P10_BDE_GB_IN
#define ysblock_stateisoGbOut MOSIM_P10_BDE_GB_OUT
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_HINF_WRENCH)
#include "MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock_private.h"
#define MOSIM_P10_HINF_GB_IN r_cfunction_sysblockGbIn
#define MOSIM_P10_HINF_GB_OUT er_cfunction_sysblockGbOut
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
constexpr int kP10DfbcHighOrder = 10;
constexpr int kP10DfbcSmoothRobust = 11;

int p10_dfbc_controller_id_from_mode(const std::string &core_mode)
{
  if (core_mode == "dfbc_high_order_attitude" ||
      core_mode == "dfbc_high_order_bodyrate") return kP10DfbcHighOrder;
  return kP10DfbcSmoothRobust;
}

const char *p10_dfbc_controller_name_from_mode(const std::string &core_mode)
{
  if (core_mode == "dfbc_high_order_attitude") return "dfbc_high_order_attitude";
  if (core_mode == "dfbc_high_order_bodyrate") return "dfbc_high_order_bodyrate";
  if (core_mode == "dfbc_smooth_robust_bodyrate") return "dfbc_smooth_robust_bodyrate";
  if (core_mode == "dfbc_dob_eso_disabled") return "dfbc_dob_eso_disabled";
  if (core_mode == "dfbc_dob_eso") return "dfbc_dob_eso";
  return "dfbc_smooth_robust_attitude";
}

constexpr int kPidCascade = 1;
constexpr int kPidGainScheduled = 2;
constexpr int kPidFuzzy = 3;
constexpr int kPidNeural = 4;
constexpr int kPidAntiWindup = 5;
constexpr int kPidFeedforwardProfile = 6;

constexpr int kWaveALqr = 1;
constexpr int kWaveALqi = 2;
constexpr int kWaveASo3 = 3;
constexpr int kWaveABackstepping = 4;

int wave_a_controller_id_from_mode(const std::string &core_mode)
{
  if (core_mode == "lqi_baseline") return kWaveALqi;
  if (core_mode == "so3_attitude") return kWaveASo3;
  if (core_mode == "backstepping_baseline") return kWaveABackstepping;
  return kWaveALqr;
}

const char *wave_a_controller_name_from_id(const int controller_id)
{
  switch (controller_id)
  {
    case kWaveALqr: return "lqr_baseline";
    case kWaveALqi: return "lqi_baseline";
    case kWaveASo3: return "so3_attitude";
    case kWaveABackstepping: return "backstepping_baseline";
    default: return "unknown";
  }
}

constexpr int kLinearRobustLqg = 1;
constexpr int kLinearRobustFeedbackLinearization = 2;
constexpr int kLinearRobustPassivity = 3;
constexpr int kLinearRobustAdaptiveBackstepping = 4;

constexpr int kClassicPolePlacementLuenberger = 1;
constexpr int kClassicMrac = 2;
constexpr int kClassicNdi = 3;
constexpr int kClassicFopid = 4;
constexpr int kClassicH2StateFeedback = 5;

int classic_controller_id_from_mode(const std::string &core_mode)
{
  if (core_mode == "mrac") return kClassicMrac;
  if (core_mode == "ndi") return kClassicNdi;
  if (core_mode == "fopid") return kClassicFopid;
  if (core_mode == "h2_state_feedback") return kClassicH2StateFeedback;
  return kClassicPolePlacementLuenberger;
}

const char *classic_controller_name_from_id(const int controller_id)
{
  switch (controller_id)
  {
    case kClassicPolePlacementLuenberger: return "pole_placement_luenberger";
    case kClassicMrac: return "mrac";
    case kClassicNdi: return "ndi";
    case kClassicFopid: return "fopid";
    case kClassicH2StateFeedback: return "h2_state_feedback";
    default: return "unknown";
  }
}

int linear_robust_controller_id_from_mode(const std::string &core_mode)
{
  if (core_mode == "feedback_linearization") return kLinearRobustFeedbackLinearization;
  if (core_mode == "passivity_based_control") return kLinearRobustPassivity;
  if (core_mode == "adaptive_backstepping") return kLinearRobustAdaptiveBackstepping;
  return kLinearRobustLqg;
}

const char *linear_robust_controller_name_from_id(const int controller_id)
{
  switch (controller_id)
  {
    case kLinearRobustLqg: return "lqg";
    case kLinearRobustFeedbackLinearization: return "feedback_linearization";
    case kLinearRobustPassivity: return "passivity_based_control";
    case kLinearRobustAdaptiveBackstepping: return "adaptive_backstepping";
    default: return "unknown";
  }
}

constexpr int kSlidingIntegral = 1;
constexpr int kSlidingTerminal = 2;
constexpr int kSlidingNonsingularTerminal = 3;
constexpr int kSlidingSuperTwisting = 4;
constexpr int kSlidingAdaptive = 5;
constexpr int kSlidingFuzzy = 6;

int sliding_mode_controller_id_from_mode(const std::string &core_mode)
{
  if (core_mode == "terminal_smc") return kSlidingTerminal;
  if (core_mode == "nonsingular_terminal_smc") return kSlidingNonsingularTerminal;
  if (core_mode == "super_twisting_smc") return kSlidingSuperTwisting;
  if (core_mode == "adaptive_smc") return kSlidingAdaptive;
  if (core_mode == "fuzzy_smc") return kSlidingFuzzy;
  return kSlidingIntegral;
}

const char *sliding_mode_controller_name_from_id(const int controller_id)
{
  switch (controller_id)
  {
    case kSlidingIntegral: return "integral_smc";
    case kSlidingTerminal: return "terminal_smc";
    case kSlidingNonsingularTerminal: return "nonsingular_terminal_smc";
    case kSlidingSuperTwisting: return "super_twisting_smc";
    case kSlidingAdaptive: return "adaptive_smc";
    case kSlidingFuzzy: return "fuzzy_smc";
    default: return "unknown";
  }
}

constexpr int kMpcLinear = 1;
constexpr int kMpcRobust = 2;
constexpr int kMpcAdaptive = 3;
constexpr int kMpcTube = 4;
constexpr int kMpcExplicitGainScheduled = 5;
constexpr int kMpcIlqr = 6;
constexpr int kMpcMppi = 7;

int mpc_controller_id_from_mode(const std::string &core_mode)
{
  if (core_mode == "robust_mpc") return kMpcRobust;
  if (core_mode == "adaptive_mpc") return kMpcAdaptive;
  if (core_mode == "tube_mpc") return kMpcTube;
  if (core_mode == "explicit_gain_scheduled_mpc") return kMpcExplicitGainScheduled;
  if (core_mode == "ilqr") return kMpcIlqr;
  if (core_mode == "mppi") return kMpcMppi;
  return kMpcLinear;
}

const char *mpc_controller_name_from_id(const int controller_id)
{
  switch (controller_id)
  {
    case kMpcLinear: return "linear_mpc";
    case kMpcRobust: return "robust_mpc";
    case kMpcAdaptive: return "adaptive_mpc";
    case kMpcTube: return "tube_mpc";
    case kMpcExplicitGainScheduled: return "explicit_gain_scheduled_mpc";
    case kMpcIlqr: return "ilqr";
    case kMpcMppi: return "mppi";
    default: return "unknown";
  }
}

constexpr int kEnhancementL1Adaptive = 1;
constexpr int kEnhancementAwff = 2;
constexpr int kEnhancementCompleteAdrc = 3;
constexpr int kEnhancementStandardizedIndi = 4;
constexpr int kEnhancementParameterScheduling = 5;
constexpr int kEnhancementIlc = 6;

int enhancement_controller_id_from_mode(const std::string &core_mode)
{
  if (core_mode == "awff") return kEnhancementAwff;
  if (core_mode == "complete_adrc") return kEnhancementCompleteAdrc;
  if (core_mode == "standardized_indi") return kEnhancementStandardizedIndi;
  if (core_mode == "parameter_scheduling") return kEnhancementParameterScheduling;
  if (core_mode == "ilc") return kEnhancementIlc;
  return kEnhancementL1Adaptive;
}

const char *enhancement_controller_name_from_id(const int controller_id)
{
  switch (controller_id)
  {
    case kEnhancementL1Adaptive: return "l1_adaptive";
    case kEnhancementAwff: return "awff";
    case kEnhancementCompleteAdrc: return "complete_adrc";
    case kEnhancementStandardizedIndi: return "standardized_indi";
    case kEnhancementParameterScheduling: return "parameter_scheduling";
    case kEnhancementIlc: return "ilc";
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

int safety_mode_id_from_mode(const std::string &core_mode)
{
  if (core_mode == "cbf") return 2;
  if (core_mode == "reference_governor") return 3;
  if (core_mode == "geofence") return 4;
  if (core_mode == "emergency_stop") return 5;
  if (core_mode == "return_and_land") return 6;
  if (core_mode == "failsafe_state_machine") return 7;
  return 1;
}

const char *safety_mode_name_from_id(const int mode_id)
{
  static const char *const names[] = {
      "unknown", "safety_filter", "cbf", "reference_governor", "geofence",
      "emergency_stop", "return_and_land", "failsafe_state_machine"};
  return mode_id >= 1 && mode_id <= 7 ? names[mode_id] : names[0];
}

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
                                                   use_graphical_c99_core_(false),
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
                                                   generated_family_controller_id_(kG9OfficialPid),
                                                   enhancement_acceleration_initialized_(false),
                                                   enhancement_previous_velocity_(Eigen::Vector3d::Zero()),
                                                   enhancement_measured_acceleration_(Eigen::Vector3d::Zero())
{
  std::string core_mode;
  ros::param::param<std::string>("~mosim_generated_core_mode", core_mode, "original");
  use_mosim_generated_core_ = (core_mode == "mworks_generated" ||
                               core_mode == "generated_c" ||
                               core_mode == "mworks_generated_c");
  use_graphical_c99_core_ = (core_mode == "graphical_c99");
  use_official_pid_core_ = (core_mode == "official_pid");
  use_se3_basic_core_ = (core_mode == "se3_basic");
  use_dfbc_basic_core_ = (core_mode == "dfbc_basic");
  use_smc_boundary_layer_core_ = (core_mode == "smc_boundary_layer");
  use_pid_indi_core_ = (core_mode == "pid_indi");
  use_nmpc_outer_core_ = (core_mode == "nmpc_outer");
  use_dfbc_high_order_core_ = (core_mode == "dfbc_high_order" ||
                               core_mode == "dfbc_jerk_snap" ||
                               core_mode == "dfbc_high_order_attitude" ||
                               core_mode == "dfbc_high_order_bodyrate");
  use_dfbc_smooth_robust_core_ = (core_mode == "dfbc_smooth_robust" ||
                                  core_mode == "dfbc_smooth_robust_dob" ||
                                  core_mode == "dfbc_wind_robust" ||
                                  core_mode == "dfbc_smooth_robust_attitude" ||
                                  core_mode == "dfbc_smooth_robust_bodyrate" ||
                                  core_mode == "dfbc_dob_eso_disabled" ||
                                  core_mode == "dfbc_dob_eso");
  use_dfbc_smooth_robust_dob_ = (core_mode == "dfbc_smooth_robust_dob" ||
                                 core_mode == "dfbc_wind_robust" ||
                                 core_mode == "dfbc_dob_eso");
  use_dfbc_smooth_robust_indi_core_ = (core_mode == "dfbc_smooth_robust_indi");
  use_l1_awff_core_ = (core_mode == "l1_awff" ||
                       core_mode == "l1_residual" ||
                       core_mode == "awff_l1" ||
                       core_mode == "l1_awff_minimal");
  use_safety_filter_core_ = (core_mode == "safety_filter");
  use_fault_allocation_core_ = (core_mode == "fault_allocation");
  generated_family_controller_id_ = g9_controller_id_from_mode(core_mode);
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST)
  generated_family_controller_id_ = pid_controller_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST)
  generated_family_controller_id_ = wave_a_controller_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST)
  generated_family_controller_id_ = linear_robust_controller_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST)
  generated_family_controller_id_ = classic_controller_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST)
  generated_family_controller_id_ = sliding_mode_controller_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST)
  generated_family_controller_id_ = mpc_controller_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST)
  generated_family_controller_id_ = enhancement_controller_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
  generated_family_controller_id_ = learning_controller_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SAFETY_SUPERVISOR)
  generated_family_controller_id_ = safety_mode_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_L1_AWFF)
  generated_family_controller_id_ = kG10L1Awff;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY)
  generated_family_controller_id_ = p10_dfbc_controller_id_from_mode(core_mode);
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_HINF_WRENCH)
  generated_family_controller_id_ = 1;
#endif
  ros::param::param<int>("~mosim_generated_family_controller_id",
                         generated_family_controller_id_,
                         generated_family_controller_id_);
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G10_BDE_FAMILY)
  const int max_generated_family_controller_id = kG10FaultAllocation;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST)
  const int max_generated_family_controller_id = kPidFeedforwardProfile;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST)
  const int max_generated_family_controller_id = kWaveABackstepping;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST)
  const int max_generated_family_controller_id = kLinearRobustAdaptiveBackstepping;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST)
  const int max_generated_family_controller_id = kClassicH2StateFeedback;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST)
  const int max_generated_family_controller_id = kSlidingFuzzy;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST)
  const int max_generated_family_controller_id = kMpcMppi;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST)
  const int max_generated_family_controller_id = kEnhancementIlc;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
  const int max_generated_family_controller_id = kLearningRlGainScheduler;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SAFETY_SUPERVISOR)
  const int max_generated_family_controller_id = 7;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_L1_AWFF)
  const int max_generated_family_controller_id = kG10L1Awff;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY)
  const int max_generated_family_controller_id = kP10DfbcSmoothRobust;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_HINF_WRENCH)
  const int max_generated_family_controller_id = 1;
#else
  const int max_generated_family_controller_id = kG9NmpcOuter;
#endif
  generated_family_controller_id_ = static_cast<int>(clamp_double(
      static_cast<double>(generated_family_controller_id_),
      static_cast<double>(kG9OfficialPid),
      static_cast<double>(max_generated_family_controller_id)));
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_GRAPHICAL_PX4CTRL_C99)
  if (use_graphical_c99_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_graphical_c99"
                    << " build_backend=graphical_px4ctrl_c99"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_GRAPHICAL_PX4CTRL_C99"
                    << " generated_model_name=PX4CTRL_Original_OuterLoop_Graphical_Sysblock"
                    << " runtime_loaded_symbol=MosimPx4ctrlGeneratedGraphStepScalar"
                    << " controller_id=px4ctrl_graphical_c99"
                    << " output_interface=ATTITUDE_THRUST"
                    << " thrust_mapping=runtime_hover_percentage");
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY)
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
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "lqr_baseline" ||
                               core_mode == "lqi_baseline" ||
                               core_mode == "so3_attitude" ||
                               core_mode == "backstepping_baseline";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "lqg" ||
                               core_mode == "feedback_linearization" ||
                               core_mode == "passivity_based_control" ||
                               core_mode == "adaptive_backstepping";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "pole_placement_luenberger" ||
                               core_mode == "mrac" ||
                               core_mode == "ndi" ||
                               core_mode == "fopid" ||
                               core_mode == "h2_state_feedback";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "integral_smc" ||
                               core_mode == "terminal_smc" ||
                               core_mode == "nonsingular_terminal_smc" ||
                               core_mode == "super_twisting_smc" ||
                               core_mode == "adaptive_smc" ||
                               core_mode == "fuzzy_smc";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "linear_mpc" ||
                               core_mode == "robust_mpc" ||
                               core_mode == "adaptive_mpc" ||
                               core_mode == "tube_mpc" ||
                               core_mode == "explicit_gain_scheduled_mpc" ||
                               core_mode == "ilqr" ||
                               core_mode == "mppi";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "l1_adaptive" ||
                               core_mode == "awff" ||
                               core_mode == "complete_adrc" ||
                               core_mode == "standardized_indi" ||
                               core_mode == "parameter_scheduling" ||
                               core_mode == "ilc";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "trained_neural_residual" ||
                               core_mode == "rl_gain_scheduler";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SAFETY_SUPERVISOR)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "safety_filter" ||
                               core_mode == "cbf" ||
                               core_mode == "reference_governor" ||
                               core_mode == "geofence" ||
                               core_mode == "emergency_stop" ||
                               core_mode == "return_and_land" ||
                               core_mode == "failsafe_state_machine";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_L1_AWFF)
  use_mosim_generated_core_ = use_mosim_generated_core_ || core_mode == "l1_awff_minimal";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY)
  use_mosim_generated_core_ = use_mosim_generated_core_ ||
                               core_mode == "dfbc_high_order_attitude" ||
                               core_mode == "dfbc_high_order_bodyrate" ||
                               core_mode == "dfbc_smooth_robust_attitude" ||
                               core_mode == "dfbc_smooth_robust_bodyrate" ||
                               core_mode == "dfbc_dob_eso_disabled" ||
                               core_mode == "dfbc_dob_eso";
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_HINF_WRENCH)
  use_mosim_generated_core_ = use_mosim_generated_core_ || core_mode == "hinf_hover_wrench";
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
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=wave_a_attitude_thrust"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST"
                    << " generated_model_name=MoSim_WaveA_CFunction_Sysblock"
                    << " generated_source_sha256=ec7dc5730b02bb4701c9f30ef78177b851a2ee8bc080575d8aedb5239fc492b7"
                    << " runtime_loaded_symbol=MoSim_WaveA_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << wave_a_controller_name_from_id(generated_family_controller_id_));
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=linear_robust_attitude_thrust"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST"
                    << " generated_model_name=MoSim_P2_LinearRobust_CFunction_Sysblock"
                    << " runtime_loaded_symbol=MoSim_P2_LinearRobust_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << linear_robust_controller_name_from_id(generated_family_controller_id_));
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=classic_controller_attitude_thrust"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST"
                    << " generated_model_name=MoSim_Classic_CFunction_Sysblock"
                    << " generated_source_sha256=0f44c05a4d36ed4a2040989ff48a47b9b1033f24ced152da1c5eb38428da7772"
                    << " runtime_loaded_symbol=MoSim_Classic_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << classic_controller_name_from_id(generated_family_controller_id_));
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=sliding_mode_attitude_thrust"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST"
                    << " generated_model_name=MoSim_P3_SlidingMode_CFunction_Sysblock"
                    << " runtime_loaded_symbol=MoSim_P3_SlidingMode_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << sliding_mode_controller_name_from_id(generated_family_controller_id_));
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=mpc_attitude_thrust"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST"
                    << " generated_model_name=MoSim_P4_Mpc_CFunction_Sysblock"
                    << " runtime_loaded_symbol=MoSim_P4_Mpc_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << mpc_controller_name_from_id(generated_family_controller_id_));
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=enhancement_attitude_thrust"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST"
                    << " generated_model_name=MoSim_P5_Enhancement_CFunction_Sysblock"
                    << " runtime_loaded_symbol=MoSim_P5_Enhancement_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << enhancement_controller_name_from_id(generated_family_controller_id_));
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
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SAFETY_SUPERVISOR)
  if (use_mosim_generated_core_)
  {
    Init();
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=safety_supervisor"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_SAFETY_SUPERVISOR"
                    << " generated_model_name=MoSim_P6_SafetySupervisor_CFunction_Sysblock"
                    << " runtime_loaded_symbol=MoSim_P6_SafetySupervisor_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << safety_mode_name_from_id(generated_family_controller_id_));
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_L1_AWFF)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=p10_l1_awff"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_P10_L1_AWFF"
                    << " generated_model_name=MoSim_P10_G10_BDE_CFunction_Sysblock"
                    << " generated_source_sha256=358ba0446938e83519d7f29e9800237495cfe074a4be2f8a134cad47e13c53a4"
                    << " runtime_loaded_symbol=MoSim_P10_G10_BDE_CFunction_Sysblock::Step"
                    << " controller_id=7 controller_name=l1_awff_minimal");
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=p10_dfbc_family"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY"
                    << " generated_model_name=MoSim_P10_DFBC_Family_CFunction_Sysblock"
                    << " generated_source_sha256=287f68f7e676f96ed59c996fab147cf82780f52b69037c99750930772e683fd2"
                    << " runtime_loaded_symbol=MoSim_P10_DFBC_Family_CFunction_Sysblock::Step"
                    << " controller_id=" << generated_family_controller_id_
                    << " controller_name=" << p10_dfbc_controller_name_from_mode(core_mode)
                    << " output_interface=" << (param_.use_bodyrate_ctrl ? "BODY_RATE_THRUST" : "ATTITUDE_THRUST")
                    << " disturbance_observer=" << (use_dfbc_smooth_robust_dob_ ? "enabled" : "disabled"));
  }
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_HINF_WRENCH)
  if (use_mosim_generated_core_)
  {
    ROS_INFO_STREAM("[mosim_generated_runtime] backend=mworks_generated_c"
                    << " build_backend=p10_hinf_wrench"
                    << " build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_P10_HINF_WRENCH"
                    << " generated_model_name=MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock"
                    << " generated_source_sha256=1a1743d722d03678fc9d78da9fcb24d7da33fe7bc6b180c26b1f357480a7587b"
                    << " runtime_loaded_symbol=MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock::Step"
                    << " controller_id=1 controller_name=hinf_hover_wrench"
                    << " adapter_contract=frozen_hover_quasi_static_wrench_to_attitude_thrust");
  }
#endif
  ROS_INFO_STREAM("[px4ctrl] mosim_generated_core_mode=" << core_mode
                  << " use_mosim_generated_core=" << (use_mosim_generated_core_ ? "true" : "false")
                  << " use_graphical_c99_core=" << (use_graphical_c99_core_ ? "true" : "false")
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
  if (use_graphical_c99_core_)
  {
    return calculateGraphicalC99Control(des, odom, imu, u);
  }
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

      // The original outer loop expresses lateral acceleration as a small-angle
      // roll/pitch command below. Bound that command with the configured
      // max_angle before publishing an unrecoverable attitude request.
      if (param_.max_angle > 0.0)
      {
        const double horizontal_acceleration = std::hypot(des_acc(0), des_acc(1));
        const double max_horizontal_acceleration = param_.gra * param_.max_angle;
        if (horizontal_acceleration > max_horizontal_acceleration)
        {
          const double scale = max_horizontal_acceleration / horizontal_acceleration;
          des_acc(0) *= scale;
          des_acc(1) *= scale;
        }
      }

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

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateGraphicalC99Control(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
#if !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_GRAPHICAL_PX4CTRL_C99)
  ROS_ERROR_THROTTLE(1.0,
      "graphical_c99 was selected, but px4ctrl was not built with graphical_px4ctrl_c99");
  return calculateOriginalControl(des, odom, imu, u);
#else
  double desired_acc_x = 0.0;
  double desired_acc_y = 0.0;
  double desired_acc_z = 0.0;
  double roll_cmd = 0.0;
  double pitch_cmd = 0.0;
  double yaw_cmd = 0.0;
  double collective_thrust_n = 0.0;
  double generated_normalized_thrust = 0.0;

  // Bind the generated graphical model to the exact ROS runtime Profile. The
  // wrapper only writes exported block parameters; it does not replace the
  // MWORKS-generated control equations.
  MosimPx4ctrlGeneratedGraphConfigure(
      param_.gain.Kp0, param_.gain.Kv0,
      param_.gain.Kp1, param_.gain.Kv1,
      param_.gain.Kp2, param_.gain.Kv2,
      param_.mass, param_.gra, param_.thr_map.hover_percentage);

  MosimPx4ctrlGeneratedGraphStepScalar(
      des.p(0), odom.p(0), des.v(0), odom.v(0), des.a(0),
      des.p(1), odom.p(1), des.v(1), odom.v(1), des.a(1),
      des.p(2), odom.p(2), des.v(2), odom.v(2), des.a(2),
      fromQuaternion2yaw(odom.q), des.yaw,
      &desired_acc_x, &desired_acc_y, &desired_acc_z,
      &roll_cmd, &pitch_cmd, &yaw_cmd,
      &collective_thrust_n, &generated_normalized_thrust);

  if (!std::isfinite(desired_acc_x) || !std::isfinite(desired_acc_y) ||
      !std::isfinite(desired_acc_z) || !std::isfinite(roll_cmd) ||
      !std::isfinite(pitch_cmd) || !std::isfinite(yaw_cmd) ||
      !std::isfinite(collective_thrust_n) ||
      !std::isfinite(generated_normalized_thrust))
  {
    ROS_ERROR_THROTTLE(1.0,
        "MWORKS graphical px4ctrl C99 returned a non-finite output; using the original adapter for this cycle");
    return calculateOriginalControl(des, odom, imu, u);
  }

  if (param_.max_angle > 0.0)
  {
    const double generated_tilt = std::hypot(roll_cmd, pitch_cmd);
    if (generated_tilt > param_.max_angle)
    {
      const double scale = param_.max_angle / generated_tilt;
      roll_cmd *= scale;
      pitch_cmd *= scale;
    }
  }

  const Eigen::Vector3d generated_des_acc(
      desired_acc_x, desired_acc_y, desired_acc_z);
  // The graphical model's 0.37 is a frozen model output.  Runtime throttle
  // remains calibrated through the current Gazebo hover map (0.456), so only
  // its physical desired acceleration is passed into the MAVROS adapter.
  u.thrust = computeDesiredCollectiveThrustSignal(generated_des_acc);
  const Eigen::Quaterniond q =
      Eigen::AngleAxisd(yaw_cmd, Eigen::Vector3d::UnitZ()) *
      Eigen::AngleAxisd(pitch_cmd, Eigen::Vector3d::UnitY()) *
      Eigen::AngleAxisd(roll_cmd, Eigen::Vector3d::UnitX());
  u.q = (imu.q * odom.q.inverse() * q).normalized();
  u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = generated_des_acc(0);
  debug_msg_.des_a_y = generated_des_acc(1);
  debug_msg_.des_a_z = generated_des_acc(2);
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
#endif
}

bool
LinearControl::usingGeneratedCore(void) const
{
  return use_mosim_generated_core_ || use_graphical_c99_core_;
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
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SAFETY_SUPERVISOR)
  const double dt = 0.01;
  Eigen::Vector3d kp(param_.gain.Kp0, param_.gain.Kp1, param_.gain.Kp2);
  Eigen::Vector3d kv(param_.gain.Kv0, param_.gain.Kv1, param_.gain.Kv2);
  Eigen::Vector3d candidate_acceleration =
      des.a + kv.asDiagonal() * (des.v - odom.v) + kp.asDiagonal() * (des.p - odom.p);
  Eigen::Vector3d candidate_reference = des.p;
  bool test_event = false;
  bool emergency_request = false;
  bool return_request = false;
  bool land_request = false;
  double obstacle_distance = 100.0;
  double command_age_s = 0.0;
  ros::param::param<bool>("~mosim_safety_test_event", test_event, false);
  ros::param::param<bool>("~mosim_safety_emergency_request", emergency_request, false);
  ros::param::param<bool>("~mosim_safety_return_request", return_request, false);
  ros::param::param<bool>("~mosim_safety_land_request", land_request, false);
  ros::param::param<double>("~mosim_safety_obstacle_distance", obstacle_distance, 100.0);
  ros::param::param<double>("~mosim_safety_command_age_s", command_age_s, 0.0);
  if (test_event)
  {
    if (generated_family_controller_id_ == 1) candidate_acceleration(0) = 8.0;
    if (generated_family_controller_id_ == 2) obstacle_distance = 0.4;
    if (generated_family_controller_id_ == 3 || generated_family_controller_id_ == 4)
      candidate_reference(0) = 12.0;
    if (generated_family_controller_id_ == 5) emergency_request = true;
    if (generated_family_controller_id_ == 6) return_request = true;
    if (generated_family_controller_id_ == 7) command_age_s = 1.0;
  }

  MOSIM_SAFETY_GB_IN.mode_id_in = static_cast<double>(generated_family_controller_id_);
  MOSIM_SAFETY_GB_IN.dt_in = dt;
  MOSIM_SAFETY_GB_IN.position_x_in = odom.p(0);
  MOSIM_SAFETY_GB_IN.position_y_in = odom.p(1);
  MOSIM_SAFETY_GB_IN.position_z_in = odom.p(2);
  MOSIM_SAFETY_GB_IN.velocity_x_in = odom.v(0);
  MOSIM_SAFETY_GB_IN.velocity_y_in = odom.v(1);
  MOSIM_SAFETY_GB_IN.velocity_z_in = odom.v(2);
  MOSIM_SAFETY_GB_IN.candidate_acceleration_x_in = candidate_acceleration(0);
  MOSIM_SAFETY_GB_IN.candidate_acceleration_y_in = candidate_acceleration(1);
  MOSIM_SAFETY_GB_IN.candidate_acceleration_z_in = candidate_acceleration(2);
  MOSIM_SAFETY_GB_IN.candidate_thrust_in =
      clamp_double((candidate_acceleration(2) + param_.gra) / thr2acc_, 0.0, 1.0);
  MOSIM_SAFETY_GB_IN.candidate_tilt_rad_in = 0.0;
  MOSIM_SAFETY_GB_IN.reference_position_x_in = candidate_reference(0);
  MOSIM_SAFETY_GB_IN.reference_position_y_in = candidate_reference(1);
  MOSIM_SAFETY_GB_IN.reference_position_z_in = candidate_reference(2);
  MOSIM_SAFETY_GB_IN.home_position_x_in = 0.0;
  MOSIM_SAFETY_GB_IN.home_position_y_in = 0.0;
  MOSIM_SAFETY_GB_IN.home_position_z_in = 0.0;
  MOSIM_SAFETY_GB_IN.obstacle_distance_in = obstacle_distance;
  MOSIM_SAFETY_GB_IN.command_age_s_in = command_age_s;
  MOSIM_SAFETY_GB_IN.state_valid_in = 1.0;
  MOSIM_SAFETY_GB_IN.offboard_valid_in = 1.0;
  MOSIM_SAFETY_GB_IN.emergency_request_in = emergency_request ? 1.0 : 0.0;
  MOSIM_SAFETY_GB_IN.return_request_in = return_request ? 1.0 : 0.0;
  MOSIM_SAFETY_GB_IN.land_request_in = land_request ? 1.0 : 0.0;
  MOSIM_SAFETY_GB_IN.enable_in = 1.0;
  MOSIM_SAFETY_GB_IN.reset_in = generated_core_reset_pending_ ? 1.0 : 0.0;
  Step();
  generated_core_reset_pending_ = false;

  const bool output_valid = MOSIM_SAFETY_GB_OUT.status_code_out == 1.0 &&
      std::isfinite(MOSIM_SAFETY_GB_OUT.safe_thrust_out) &&
      std::isfinite(MOSIM_SAFETY_GB_OUT.safe_reference_x_out) &&
      std::isfinite(MOSIM_SAFETY_GB_OUT.safe_acceleration_x_out);
  if (!output_valid)
  {
    ROS_ERROR_THROTTLE(1.0, "SafetySupervisor generated backend returned invalid output");
    u.q = imu.q;
    u.bodyrates = Eigen::Vector3d::Zero();
    u.thrust = 0.0;
    return debug_msg_;
  }

  Desired_State_t safe_des = des;
  if (generated_family_controller_id_ <= 2)
  {
    const Eigen::Vector3d safe_acceleration(
        MOSIM_SAFETY_GB_OUT.safe_acceleration_x_out,
        MOSIM_SAFETY_GB_OUT.safe_acceleration_y_out,
        MOSIM_SAFETY_GB_OUT.safe_acceleration_z_out);
    safe_des.a = safe_acceleration -
        kv.asDiagonal() * (des.v - odom.v) - kp.asDiagonal() * (des.p - odom.p);
  }
  else
  {
    safe_des.p = Eigen::Vector3d(
        MOSIM_SAFETY_GB_OUT.safe_reference_x_out,
        MOSIM_SAFETY_GB_OUT.safe_reference_y_out,
        MOSIM_SAFETY_GB_OUT.safe_reference_z_out);
  }
  quadrotor_msgs::Px4ctrlDebug debug = calculateOriginalControl(safe_des, odom, imu, u);
  if (static_cast<int>(MOSIM_SAFETY_GB_OUT.action_out) == 5)
    u.thrust = 0.0;
  else
    u.thrust = std::min(u.thrust, clamp_double(MOSIM_SAFETY_GB_OUT.safe_thrust_out, 0.0, 1.0));
  debug.des_thr = u.thrust;
  ROS_INFO_STREAM_THROTTLE(1.0, "[px4ctrl] safety_event"
      << " mode=" << safety_mode_name_from_id(generated_family_controller_id_)
      << " action=" << static_cast<int>(MOSIM_SAFETY_GB_OUT.action_out)
      << " state=" << static_cast<int>(MOSIM_SAFETY_GB_OUT.state_out)
      << " active_constraints=" << static_cast<unsigned int>(MOSIM_SAFETY_GB_OUT.active_constraints_out)
      << " test_event=" << (test_event ? "true" : "false")
      << " safe_thrust=" << u.thrust);
  return debug;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_HINF_WRENCH)
  const double effective_hover_percentage = param_.gra / thr2acc_;
  const double full_collective_thrust_n = std::max(param_.mass * thr2acc_, 1.0e-6);
  const Eigen::Vector3d kp(param_.gain.Kp0, param_.gain.Kp1, param_.gain.Kp2);
  const Eigen::Vector3d kv(param_.gain.Kv0, param_.gain.Kv1, param_.gain.Kv2);
  Eigen::Vector3d reference_acceleration = des.a;
  reference_acceleration += kv.asDiagonal() * (des.v - odom.v);
  reference_acceleration += kp.asDiagonal() * (des.p - odom.p);
  reference_acceleration += Eigen::Vector3d(0.0, 0.0, param_.gra);
  const double reference_yaw = des.yaw;
  const double reference_roll =
      (reference_acceleration(0) * std::sin(reference_yaw) -
       reference_acceleration(1) * std::cos(reference_yaw)) / param_.gra;
  const double reference_pitch =
      (reference_acceleration(0) * std::cos(reference_yaw) +
       reference_acceleration(1) * std::sin(reference_yaw)) / param_.gra;
  const Eigen::Vector3d state_euler = odom.q.toRotationMatrix().eulerAngles(0, 1, 2);

  MOSIM_P10_HINF_GB_IN.state_roll_in = state_euler(0);
  MOSIM_P10_HINF_GB_IN.state_pitch_in = state_euler(1);
  MOSIM_P10_HINF_GB_IN.state_yaw_in = state_euler(2);
  MOSIM_P10_HINF_GB_IN.state_p_in = imu.w(0);
  MOSIM_P10_HINF_GB_IN.state_q_in = imu.w(1);
  MOSIM_P10_HINF_GB_IN.state_r_in = imu.w(2);
  MOSIM_P10_HINF_GB_IN.state_u_in = odom.v(0);
  MOSIM_P10_HINF_GB_IN.state_v_in = odom.v(1);
  MOSIM_P10_HINF_GB_IN.state_w_in = odom.v(2);
  MOSIM_P10_HINF_GB_IN.state_x_in = odom.p(0);
  MOSIM_P10_HINF_GB_IN.state_y_in = odom.p(1);
  MOSIM_P10_HINF_GB_IN.state_z_in = odom.p(2);
  MOSIM_P10_HINF_GB_IN.reference_roll_in = reference_roll;
  MOSIM_P10_HINF_GB_IN.reference_pitch_in = reference_pitch;
  MOSIM_P10_HINF_GB_IN.reference_yaw_in = reference_yaw;
  MOSIM_P10_HINF_GB_IN.reference_p_in = 0.0;
  MOSIM_P10_HINF_GB_IN.reference_q_in = 0.0;
  MOSIM_P10_HINF_GB_IN.reference_r_in = des.yaw_rate;
  MOSIM_P10_HINF_GB_IN.reference_u_in = des.v(0);
  MOSIM_P10_HINF_GB_IN.reference_v_in = des.v(1);
  MOSIM_P10_HINF_GB_IN.reference_w_in = des.v(2);
  MOSIM_P10_HINF_GB_IN.reference_x_in = des.p(0);
  MOSIM_P10_HINF_GB_IN.reference_y_in = des.p(1);
  MOSIM_P10_HINF_GB_IN.reference_z_in = des.p(2);
  MOSIM_P10_HINF_GB_IN.enable_in = 1.0;
  MOSIM_P10_HINF_GB_IN.reset_in = generated_core_reset_pending_ ? 1.0 : 0.0;
  MOSIM_P10_HINF_GB_IN.mass_in = param_.mass;
  MOSIM_P10_HINF_GB_IN.gravity_in = param_.gra;
  MOSIM_P10_HINF_GB_IN.force_min_n_in = 0.0;
  MOSIM_P10_HINF_GB_IN.force_max_n_in = full_collective_thrust_n;
  MOSIM_P10_HINF_GB_IN.torque_limit_nm_in = 8.0;
  MOSIM_P10_HINF_GB_IN.roll_stiffness_nm_per_rad_in = 30.0;
  MOSIM_P10_HINF_GB_IN.pitch_stiffness_nm_per_rad_in = 30.0;
  MOSIM_P10_HINF_GB_IN.yaw_stiffness_nm_per_rad_in = 40.0;
  MOSIM_P10_HINF_GB_IN.hover_percentage_in = effective_hover_percentage;
  MOSIM_P10_HINF_GB_IN.tilt_limit_rad_in = param_.max_angle > 0.0 ? param_.max_angle : 0.35;
  MOSIM_P10_HINF_GB_IN.yaw_correction_limit_rad_in = 0.20;
  MOSIM_P10_HINF_GB_IN.min_normalized_thrust_in = 0.0;
  MOSIM_P10_HINF_GB_IN.max_normalized_thrust_in = 1.0;
  Step();
  generated_core_reset_pending_ = false;

  const bool output_valid = MOSIM_P10_HINF_GB_OUT.status_code_out == 0.0 &&
      MOSIM_P10_HINF_GB_OUT.source_command_variant_out == 3.0 &&
      MOSIM_P10_HINF_GB_OUT.adapted_command_variant_out == 1.0 &&
      std::isfinite(MOSIM_P10_HINF_GB_OUT.normalized_thrust_out) &&
      std::isfinite(MOSIM_P10_HINF_GB_OUT.desired_attitude_w_out);
  if (!output_valid)
  {
    ROS_ERROR_THROTTLE(1.0, "P10 H-infinity generated backend returned invalid output");
    u.q = imu.q;
    u.bodyrates = Eigen::Vector3d::Zero();
    u.thrust = 0.0;
  }
  else
  {
    u.q = Eigen::Quaterniond(
        MOSIM_P10_HINF_GB_OUT.desired_attitude_w_out,
        MOSIM_P10_HINF_GB_OUT.desired_attitude_x_out,
        MOSIM_P10_HINF_GB_OUT.desired_attitude_y_out,
        MOSIM_P10_HINF_GB_OUT.desired_attitude_z_out).normalized();
    u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
    u.thrust = clamp_double(MOSIM_P10_HINF_GB_OUT.normalized_thrust_out, 0.0, 1.0);
  }
  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = des.a(0);
  debug_msg_.des_a_y = des.a(1);
  debug_msg_.des_a_z = des.a(2);
#else
#if !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST) && \
    !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST) && \
    !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST) && \
    !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST) && \
    !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST) && \
    !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST) && \
    !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST) && \
    !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
  const double effective_hover_percentage = param_.gra / thr2acc_;
#endif
  const double dt = 0.01;
  const bool reset_this_cycle = generated_core_reset_pending_;

#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST) || \
    defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST) || \
    defined(MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST) || \
    defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST) || \
    defined(MOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST) || \
    defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST)
  const double effective_hover_percentage = param_.gra / thr2acc_;
  const double full_collective_thrust_n = std::max(param_.mass * thr2acc_, 1.0e-6);
  MOSIM_ATTITUDE_THRUST_GB_IN.controller_id_in = static_cast<double>(generated_family_controller_id_);
  MOSIM_ATTITUDE_THRUST_GB_IN.dt_in = dt;
  MOSIM_ATTITUDE_THRUST_GB_IN.position_x_in = odom.p(0);
  MOSIM_ATTITUDE_THRUST_GB_IN.position_y_in = odom.p(1);
  MOSIM_ATTITUDE_THRUST_GB_IN.position_z_in = odom.p(2);
  MOSIM_ATTITUDE_THRUST_GB_IN.velocity_x_in = odom.v(0);
  MOSIM_ATTITUDE_THRUST_GB_IN.velocity_y_in = odom.v(1);
  MOSIM_ATTITUDE_THRUST_GB_IN.velocity_z_in = odom.v(2);
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST)
  MOSIM_ATTITUDE_THRUST_GB_IN.attitude_w_in = imu.q.w();
  MOSIM_ATTITUDE_THRUST_GB_IN.attitude_x_in = imu.q.x();
  MOSIM_ATTITUDE_THRUST_GB_IN.attitude_y_in = imu.q.y();
  MOSIM_ATTITUDE_THRUST_GB_IN.attitude_z_in = imu.q.z();
#endif
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST)
  if (!enhancement_acceleration_initialized_ || reset_this_cycle)
  {
    enhancement_previous_velocity_ = odom.v;
    enhancement_measured_acceleration_.setZero();
    enhancement_acceleration_initialized_ = true;
  }
  else
  {
    const Eigen::Vector3d raw_acceleration = (odom.v - enhancement_previous_velocity_) / dt;
    enhancement_measured_acceleration_ =
        0.15 * raw_acceleration.cwiseMax(-8.0).cwiseMin(8.0) +
        0.85 * enhancement_measured_acceleration_;
    enhancement_previous_velocity_ = odom.v;
  }
  MOSIM_ATTITUDE_THRUST_GB_IN.measured_acceleration_x_in = enhancement_measured_acceleration_(0);
  MOSIM_ATTITUDE_THRUST_GB_IN.measured_acceleration_y_in = enhancement_measured_acceleration_(1);
  MOSIM_ATTITUDE_THRUST_GB_IN.measured_acceleration_z_in = enhancement_measured_acceleration_(2);
#endif
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_position_x_in = des.p(0);
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_position_y_in = des.p(1);
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_position_z_in = des.p(2);
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_velocity_x_in = des.v(0);
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_velocity_y_in = des.v(1);
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_velocity_z_in = des.v(2);
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_acceleration_x_in = des.a(0);
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_acceleration_y_in = des.a(1);
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_acceleration_z_in = des.a(2);
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_yaw_in = des.yaw;
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST)
  const Eigen::Vector3d wave_a_kp(
      param_.gain.Kp0, param_.gain.Kp1, param_.gain.Kp2);
  const Eigen::Vector3d wave_a_kv(
      param_.gain.Kv0, param_.gain.Kv1, param_.gain.Kv2);
  Eigen::Vector3d wave_a_outer_acceleration = des.a;
  wave_a_outer_acceleration += wave_a_kv.asDiagonal() * (des.v - odom.v);
  wave_a_outer_acceleration += wave_a_kp.asDiagonal() * (des.p - odom.p);
  wave_a_outer_acceleration += Eigen::Vector3d(0.0, 0.0, param_.gra);
  const double wave_a_reference_thrust = computeDesiredCollectiveThrustSignal(
      wave_a_outer_acceleration);
  const double wave_a_yaw_odom = fromQuaternion2yaw(odom.q);
  const double wave_a_roll = (wave_a_outer_acceleration(0) * std::sin(wave_a_yaw_odom) -
                              wave_a_outer_acceleration(1) * std::cos(wave_a_yaw_odom)) /
                             param_.gra;
  const double wave_a_pitch = (wave_a_outer_acceleration(0) * std::cos(wave_a_yaw_odom) +
                               wave_a_outer_acceleration(1) * std::sin(wave_a_yaw_odom)) /
                              param_.gra;
  const Eigen::Quaterniond wave_a_reference_world =
      Eigen::AngleAxisd(des.yaw, Eigen::Vector3d::UnitZ()) *
      Eigen::AngleAxisd(wave_a_pitch, Eigen::Vector3d::UnitY()) *
      Eigen::AngleAxisd(wave_a_roll, Eigen::Vector3d::UnitX());
  const Eigen::Quaterniond wave_a_reference_attitude =
      (imu.q * odom.q.inverse() * wave_a_reference_world).normalized();
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_attitude_w_in = wave_a_reference_attitude.w();
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_attitude_x_in = wave_a_reference_attitude.x();
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_attitude_y_in = wave_a_reference_attitude.y();
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_attitude_z_in = wave_a_reference_attitude.z();
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_body_rate_x_in = 0.0;
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_body_rate_y_in = 0.0;
  MOSIM_ATTITUDE_THRUST_GB_IN.reference_body_rate_z_in = 0.0;
  MOSIM_ATTITUDE_THRUST_GB_IN.collective_thrust_n_in =
      wave_a_reference_thrust * full_collective_thrust_n;
#endif
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST)
  MOSIM_ATTITUDE_THRUST_GB_IN.trajectory_phase_bin_in = 0.0;
  MOSIM_ATTITUDE_THRUST_GB_IN.repeat_complete_in = 0.0;
#endif
#if !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST) && \
    !defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST)
  MOSIM_ATTITUDE_THRUST_GB_IN.mass_kg_in = param_.mass;
  MOSIM_ATTITUDE_THRUST_GB_IN.gravity_mps2_in = param_.gra;
  MOSIM_ATTITUDE_THRUST_GB_IN.hover_percentage_in = effective_hover_percentage;
  MOSIM_ATTITUDE_THRUST_GB_IN.max_tilt_rad_in = param_.max_angle > 0.0 ? param_.max_angle : M_PI / 2.0 - 1.0e-6;
  MOSIM_ATTITUDE_THRUST_GB_IN.min_collective_thrust_n_in = 0.0;
  MOSIM_ATTITUDE_THRUST_GB_IN.max_collective_thrust_n_in = full_collective_thrust_n;
#endif
  MOSIM_ATTITUDE_THRUST_GB_IN.enable_in = 1.0;
  MOSIM_ATTITUDE_THRUST_GB_IN.reset_in = reset_this_cycle ? 1.0 : 0.0;

  Step();
  generated_core_reset_pending_ = false;

  const bool generated_output_valid =
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST)
      MOSIM_ATTITUDE_THRUST_GB_OUT.status_code_out == 1.0 &&
#else
      MOSIM_ATTITUDE_THRUST_GB_OUT.status_code_out == 0.0 &&
#endif
      std::isfinite(MOSIM_ATTITUDE_THRUST_GB_OUT.normalized_thrust_out) &&
      std::isfinite(MOSIM_ATTITUDE_THRUST_GB_OUT.desired_attitude_w_out) &&
      std::isfinite(MOSIM_ATTITUDE_THRUST_GB_OUT.desired_attitude_x_out) &&
      std::isfinite(MOSIM_ATTITUDE_THRUST_GB_OUT.desired_attitude_y_out) &&
      std::isfinite(MOSIM_ATTITUDE_THRUST_GB_OUT.desired_attitude_z_out);
  if (!generated_output_valid)
  {
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST)
    ROS_ERROR_THROTTLE(1.0, "Linear/robust ATTITUDE_THRUST generated backend returned invalid output");
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST)
    ROS_ERROR_THROTTLE(1.0, "Wave A generated backend returned invalid output");
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST)
    ROS_ERROR_THROTTLE(1.0, "Classic-controller ATTITUDE_THRUST generated backend returned invalid output");
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST)
    ROS_ERROR_THROTTLE(1.0, "Sliding-mode ATTITUDE_THRUST generated backend returned invalid output");
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST)
    ROS_ERROR_THROTTLE(1.0, "Enhancement ATTITUDE_THRUST generated backend returned invalid output");
#else
    ROS_ERROR_THROTTLE(1.0, "MPC ATTITUDE_THRUST generated backend returned invalid output");
#endif
    u.q = imu.q;
    u.bodyrates = Eigen::Vector3d::Zero();
    u.thrust = 0.0;
  }
  else
  {
    u.q = Eigen::Quaterniond(
        MOSIM_ATTITUDE_THRUST_GB_OUT.desired_attitude_w_out,
        MOSIM_ATTITUDE_THRUST_GB_OUT.desired_attitude_x_out,
        MOSIM_ATTITUDE_THRUST_GB_OUT.desired_attitude_y_out,
        MOSIM_ATTITUDE_THRUST_GB_OUT.desired_attitude_z_out);
    u.q.normalize();
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST)
    if (generated_family_controller_id_ == kWaveASo3)
    {
      u.bodyrates = Eigen::Vector3d(
          MOSIM_ATTITUDE_THRUST_GB_OUT.desired_body_rate_x_out,
          MOSIM_ATTITUDE_THRUST_GB_OUT.desired_body_rate_y_out,
          MOSIM_ATTITUDE_THRUST_GB_OUT.desired_body_rate_z_out);
    }
    else
    {
      u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
    }
#else
    u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
#endif
    u.thrust = clamp_double(MOSIM_ATTITUDE_THRUST_GB_OUT.normalized_thrust_out, 0.0, 1.0);
  }

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = MOSIM_ATTITUDE_THRUST_GB_OUT.desired_acceleration_x_out;
  debug_msg_.des_a_y = MOSIM_ATTITUDE_THRUST_GB_OUT.desired_acceleration_y_out;
  debug_msg_.des_a_z = MOSIM_ATTITUDE_THRUST_GB_OUT.desired_acceleration_z_out;
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST)
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
#elif defined(MOSIM_PX4CTRL_GENERATED_BACKEND_G10_BDE_FAMILY) || \
      defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_L1_AWFF) || \
      defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY)
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
  sblock_stateisoGbIn.enable_disturbance_observer_in =
      use_dfbc_smooth_robust_dob_ ? 1.0 : 0.0;
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
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY)
  sblock_stateisoGbIn.high_order_body_rate_limit_x_in = high_order_body_rate_limit_[0];
  sblock_stateisoGbIn.high_order_body_rate_limit_y_in = high_order_body_rate_limit_[1];
  sblock_stateisoGbIn.high_order_body_rate_limit_z_in = high_order_body_rate_limit_[2];
  sblock_stateisoGbIn.high_order_body_accel_limit_x_in = high_order_body_accel_limit_[0];
  sblock_stateisoGbIn.high_order_body_accel_limit_y_in = high_order_body_accel_limit_[1];
  sblock_stateisoGbIn.high_order_body_accel_limit_z_in = high_order_body_accel_limit_[2];
  sblock_stateisoGbIn.smooth_feedback_gain_x_in = smooth_feedback_gain_[0];
  sblock_stateisoGbIn.smooth_feedback_gain_y_in = smooth_feedback_gain_[1];
  sblock_stateisoGbIn.smooth_feedback_gain_z_in = smooth_feedback_gain_[2];
  sblock_stateisoGbIn.smooth_feedback_bound_x_in = smooth_feedback_bound_[0];
  sblock_stateisoGbIn.smooth_feedback_bound_y_in = smooth_feedback_bound_[1];
  sblock_stateisoGbIn.smooth_feedback_bound_z_in = smooth_feedback_bound_[2];
  sblock_stateisoGbIn.disturbance_observer_gain_x_in = disturbance_observer_gain_[0];
  sblock_stateisoGbIn.disturbance_observer_gain_y_in = disturbance_observer_gain_[1];
  sblock_stateisoGbIn.disturbance_observer_gain_z_in = disturbance_observer_gain_[2];
  sblock_stateisoGbIn.disturbance_compensation_limit_x_in = disturbance_compensation_limit_[0];
  sblock_stateisoGbIn.disturbance_compensation_limit_y_in = disturbance_compensation_limit_[1];
  sblock_stateisoGbIn.disturbance_compensation_limit_z_in = disturbance_compensation_limit_[2];
#endif
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

  const bool p10_generated_output_valid =
      ysblock_stateisoGbOut.status_code_out == 0.0 &&
      std::isfinite(ysblock_stateisoGbOut.normalized_thrust_out) &&
      std::isfinite(ysblock_stateisoGbOut.desired_attitude_w_out);
  if (!p10_generated_output_valid)
  {
    ROS_ERROR_THROTTLE(1.0, "G10/P10 BDE generated backend returned invalid output");
    u.q = imu.q;
    u.bodyrates = Eigen::Vector3d::Zero();
    u.thrust = 0.0;
  }
  else
  {
    u.q = Eigen::Quaterniond(
        ysblock_stateisoGbOut.desired_attitude_w_out,
        ysblock_stateisoGbOut.desired_attitude_x_out,
        ysblock_stateisoGbOut.desired_attitude_y_out,
        ysblock_stateisoGbOut.desired_attitude_z_out).normalized();
#if defined(MOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY)
    if (param_.use_bodyrate_ctrl)
    {
      u.bodyrates = Eigen::Vector3d(
          ysblock_stateisoGbOut.desired_body_rate_x_out,
          ysblock_stateisoGbOut.desired_body_rate_y_out,
          ysblock_stateisoGbOut.desired_body_rate_z_out);
    }
    else
    {
      u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
    }
#else
    u.bodyrates = bodyrateAttitudeFeedback(u.q, imu.q, Eigen::Vector3d::Zero());
#endif
    u.thrust = clamp_double(ysblock_stateisoGbOut.normalized_thrust_out, 0.0, 1.0);
  }

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
#endif
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
