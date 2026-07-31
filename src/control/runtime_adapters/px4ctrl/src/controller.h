/*************************************************************/
/* Acknowledgement: github.com/uzh-rpg/rpg_quadrotor_control */
/*************************************************************/

#ifndef __CONTROLLER_H
#define __CONTROLLER_H

#include <mavros_msgs/AttitudeTarget.h>
#include <quadrotor_msgs/Px4ctrlDebug.h>
#include <queue>

#include "input.h"
#include <Eigen/Dense>
#include "px4ctrl_core.h"

struct Desired_State_t
{
	Eigen::Vector3d p;
	Eigen::Vector3d v;
	Eigen::Vector3d a;
	Eigen::Vector3d j;
	Eigen::Quaterniond q;
	double yaw;
	double yaw_rate;

	Desired_State_t(){};

	Desired_State_t(Odom_Data_t &odom)
		: p(odom.p),
		  v(Eigen::Vector3d::Zero()),
		  a(Eigen::Vector3d::Zero()),
		  j(Eigen::Vector3d::Zero()),
		  q(odom.q),
		  yaw(uav_utils::get_yaw_from_quaternion(odom.q)),
		  yaw_rate(0){};
};

struct Controller_Output_t
{

	// Orientation of the body frame with respect to the world frame
	Eigen::Quaterniond q;

	// Body rates in body frame
	Eigen::Vector3d bodyrates; // [rad/s]

	// Collective mass normalized thrust
	double thrust;

	//Eigen::Vector3d des_v_real;
};


class LinearControl
{
public:
  LinearControl(Parameter_t &);
  quadrotor_msgs::Px4ctrlDebug calculateControl(const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu, 
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateOriginalControl(const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  bool estimateThrustModel(const Eigen::Vector3d &est_v,
      const Parameter_t &param);
  void resetThrustMapping(void);
  bool usingGeneratedCore(void) const;
  bool usingMosimWrapperOwnedLandingCore(void) const;

  EIGEN_MAKE_ALIGNED_OPERATOR_NEW

private:
  Parameter_t param_;
  quadrotor_msgs::Px4ctrlDebug debug_msg_;
  std::queue<std::pair<ros::Time, double>> timed_thrust_;
  static constexpr double kMinNormalizedCollectiveThrust_ = 3.0;
  bool use_mosim_generated_core_;
  bool use_graphical_c99_core_;
  bool use_official_pid_core_;
  bool use_se3_basic_core_;
  bool use_dfbc_basic_core_;
  bool use_smc_boundary_layer_core_;
  bool use_pid_indi_core_;
  bool use_nmpc_outer_core_;
  bool use_dfbc_high_order_core_;
  bool use_dfbc_smooth_robust_core_;
  bool use_dfbc_smooth_robust_dob_;
  bool use_dfbc_smooth_robust_indi_core_;
  bool use_l1_awff_core_;
  bool use_safety_filter_core_;
  bool use_fault_allocation_core_;
  bool generated_core_reset_pending_;
  int generated_family_controller_id_;
  bool enhancement_acceleration_initialized_;
  Eigen::Vector3d enhancement_previous_velocity_;
  Eigen::Vector3d enhancement_measured_acceleration_;
  mosim_px4ctrl::CoreState official_pid_core_state_;
  mosim_px4ctrl::CoreState se3_basic_core_state_;
  mosim_px4ctrl::CoreState dfbc_basic_core_state_;
  mosim_px4ctrl::CoreState smc_boundary_layer_core_state_;
  mosim_px4ctrl::CoreState pid_indi_core_state_;
  mosim_px4ctrl::CoreState nmpc_outer_core_state_;
  mosim_px4ctrl::CoreState dfbc_high_order_core_state_;
  mosim_px4ctrl::CoreState dfbc_smooth_robust_core_state_;
  mosim_px4ctrl::CoreState dfbc_smooth_robust_indi_core_state_;
  mosim_px4ctrl::CoreState l1_awff_core_state_;
  mosim_px4ctrl::CoreState safety_filter_core_state_;
  mosim_px4ctrl::CoreState fault_allocation_core_state_;
  double smc_lambda_[3];
  double smc_eta_[3];
  double smc_phi_[3];
  double smc_surface_limit_[3];
  double indi_gain_[3];
  double indi_increment_limit_[3];
  double indi_measured_accel_limit_[3];
  double indi_accel_lpf_alpha_;
  double nmpc_horizon_s_;
  double nmpc_position_weight_[3];
  double nmpc_velocity_weight_[3];
  double nmpc_control_weight_[3];
  double nmpc_accel_limit_[3];
  double nmpc_increment_limit_[3];
  double high_order_body_rate_limit_[3];
  double bodyrate_attitude_gain_[3];
  double high_order_body_accel_limit_[3];
  double smooth_feedback_gain_[3];
  double smooth_feedback_bound_[3];
  double disturbance_observer_gain_[3];
  double disturbance_compensation_limit_[3];
  double l1_model_decay_;
  double l1_filter_T_;
  double l1_gain_[3];
  double l1_comp_limit_[3];
  double drag_feedforward_gain_[3];
  double safety_accel_limit_[3];
  double fault_rotor_efficiency_[4];
  double fault_allocation_blend_;
  double fault_min_efficiency_;
  double fault_thrust_comp_limit_;

  // Thrust-accel mapping params
  const double rho2_ = 0.998; // do not change
  double thr2acc_;
  double P_;

  double computeDesiredCollectiveThrustSignal(const Eigen::Vector3d &des_acc);
  Eigen::Vector3d bodyrateAttitudeFeedback(
      const Eigen::Quaterniond &desired_attitude,
      const Eigen::Quaterniond &current_attitude,
      const Eigen::Vector3d &feedforward_bodyrates) const;
  quadrotor_msgs::Px4ctrlDebug calculateGeneratedCoreControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateGraphicalC99Control(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateOfficialPidControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateSe3BasicControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateDfbcBasicControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateSmcBoundaryLayerControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculatePidIndiControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateNmpcOuterControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateDfbcHighOrderControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateDfbcSmoothRobustControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateDfbcSmoothRobustIndiControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateL1AwffControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateSafetyFilterControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  quadrotor_msgs::Px4ctrlDebug calculateFaultAllocationControl(
      const Desired_State_t &des,
      const Odom_Data_t &odom,
      const Imu_Data_t &imu,
      Controller_Output_t &u);
  double fromQuaternion2yaw(Eigen::Quaterniond q);
};


#endif
