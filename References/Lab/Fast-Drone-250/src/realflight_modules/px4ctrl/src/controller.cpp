#include "controller.h"

extern "C" {
#include "PX4CTRL_Core_CFunction_Sysblock_private.h"
}

using namespace std;



double LinearControl::fromQuaternion2yaw(Eigen::Quaterniond q)
{
  double yaw = atan2(2 * (q.x()*q.y() + q.w()*q.z()), q.w()*q.w() + q.x()*q.x() - q.y()*q.y() - q.z()*q.z());
  return yaw;
}

LinearControl::LinearControl(Parameter_t &param) : param_(param),
                                                   use_mosim_generated_core_(false),
                                                   generated_core_reset_pending_(true)
{
  std::string core_mode;
  ros::param::param<std::string>("~mosim_generated_core_mode", core_mode, "original");
  use_mosim_generated_core_ = (core_mode == "mworks_generated" ||
                               core_mode == "generated_c" ||
                               core_mode == "mworks_generated_c");
  Init();
  resetThrustMapping();
  ROS_INFO_STREAM("[px4ctrl] mosim_generated_core_mode=" << core_mode
                  << " use_mosim_generated_core=" << (use_mosim_generated_core_ ? "true" : "false"));
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

quadrotor_msgs::Px4ctrlDebug
LinearControl::calculateGeneratedCoreControl(const Desired_State_t &des,
    const Odom_Data_t &odom,
    const Imu_Data_t &imu,
    Controller_Output_t &u)
{
  const double effective_hover_percentage = param_.gra / thr2acc_;
  const double dt = 0.01;

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
  lockGbIn.reset_in = 1.0;
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
  u.thrust = blockGbOut.normalized_thrust_out;

  debug_msg_.des_v_x = des.v(0);
  debug_msg_.des_v_y = des.v(1);
  debug_msg_.des_v_z = des.v(2);
  debug_msg_.des_a_x = blockGbOut.desired_acceleration_x_out;
  debug_msg_.des_a_y = blockGbOut.desired_acceleration_y_out;
  debug_msg_.des_a_z = blockGbOut.desired_acceleration_z_out;
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
}





