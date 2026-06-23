#pragma once

#include <cmath>

namespace mosim_sunray_runtime_adapters {

struct Vec3 {
  double x{0.0};
  double y{0.0};
  double z{0.0};
};

struct Quat {
  double x{0.0};
  double y{0.0};
  double z{0.0};
  double w{1.0};
};

struct Pose3 {
  Vec3 p{};
  Quat q{};
};

inline Vec3 vec_add(const Vec3& a, const Vec3& b) {
  return Vec3{a.x + b.x, a.y + b.y, a.z + b.z};
}

inline Quat quat_norm(const Quat& q) {
  const double n = std::sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w);
  if (n <= 0.0) {
    return Quat{};
  }
  return Quat{q.x / n, q.y / n, q.z / n, q.w / n};
}

inline Quat quat_mul(const Quat& a_raw, const Quat& b_raw) {
  const Quat a = quat_norm(a_raw);
  const Quat b = quat_norm(b_raw);
  return quat_norm(Quat{
      a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
      a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
      a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w,
      a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
  });
}

inline Quat quat_inv(const Quat& q_raw) {
  const Quat q = quat_norm(q_raw);
  return Quat{-q.x, -q.y, -q.z, q.w};
}

inline Vec3 rotate(const Quat& q_raw, const Vec3& v) {
  const Quat q = quat_norm(q_raw);
  const double tx = 2.0 * (q.y * v.z - q.z * v.y);
  const double ty = 2.0 * (q.z * v.x - q.x * v.z);
  const double tz = 2.0 * (q.x * v.y - q.y * v.x);
  return Vec3{
      v.x + q.w * tx + (q.y * tz - q.z * ty),
      v.y + q.w * ty + (q.z * tx - q.x * tz),
      v.z + q.w * tz + (q.x * ty - q.y * tx),
  };
}

inline Quat quat_from_rpy(double roll, double pitch, double yaw) {
  const double cr = std::cos(roll * 0.5);
  const double sr = std::sin(roll * 0.5);
  const double cp = std::cos(pitch * 0.5);
  const double sp = std::sin(pitch * 0.5);
  const double cy = std::cos(yaw * 0.5);
  const double sy = std::sin(yaw * 0.5);
  return quat_norm(Quat{
      sr * cp * cy - cr * sp * sy,
      cr * sp * cy + sr * cp * sy,
      cr * cp * sy - sr * sp * cy,
      cr * cp * cy + sr * sp * sy,
  });
}

inline double yaw_from_quat(const Quat& q_raw) {
  const Quat q = quat_norm(q_raw);
  return std::atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z));
}

inline Pose3 pose_inv(const Pose3& t_ab) {
  const Quat q_ba = quat_inv(t_ab.q);
  return Pose3{rotate(q_ba, Vec3{-t_ab.p.x, -t_ab.p.y, -t_ab.p.z}), q_ba};
}

inline Pose3 pose_mul(const Pose3& t_ab, const Pose3& t_bc) {
  return Pose3{vec_add(t_ab.p, rotate(t_ab.q, t_bc.p)), quat_mul(t_ab.q, t_bc.q)};
}

inline Pose3 livox_pose_to_base_pose(const Pose3& t_ref_livox, const Pose3& t_base_livox) {
  return pose_mul(t_ref_livox, pose_inv(t_base_livox));
}

inline Pose3 make_alignment(const Pose3& t_local_base0, const Pose3& t_fast_base0) {
  return pose_mul(t_local_base0, pose_inv(t_fast_base0));
}

inline Vec3 transform_velocity(const Quat& q_local_fast, const Vec3& v_fast) {
  return rotate(q_local_fast, v_fast);
}

}  // namespace mosim_sunray_runtime_adapters
