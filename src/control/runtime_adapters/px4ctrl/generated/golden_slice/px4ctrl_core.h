#ifndef MOSIM_PX4CTRL_GOLDEN_SLICE_CORE_H
#define MOSIM_PX4CTRL_GOLDEN_SLICE_CORE_H

#include <cmath>
#include <string>

namespace mosim_px4ctrl
{

struct Vec3
{
    double x{0.0};
    double y{0.0};
    double z{0.0};

    Vec3() = default;
    Vec3(double x_in, double y_in, double z_in)
        : x(x_in), y(y_in), z(z_in)
    {
    }
};

struct Quat
{
    double w{1.0};
    double x{0.0};
    double y{0.0};
    double z{0.0};

    Quat() = default;
    Quat(double w_in, double x_in, double y_in, double z_in)
        : w(w_in), x(x_in), y(y_in), z(z_in)
    {
    }
};

struct CoreParams
{
    double kp[3]{1.5, 1.5, 1.5};
    double kv[3]{1.5, 1.5, 1.5};
    double ki[3]{0.0, 0.0, 0.0};
    double smc_lambda[3]{2.0, 2.0, 2.0};
    double smc_eta[3]{0.1, 0.1, 0.05};
    double smc_phi[3]{0.4, 0.4, 0.35};
    double smc_surface_limit[3]{3.0, 3.0, 2.5};
    double indi_gain[3]{0.12, 0.12, 0.08};
    double indi_increment_limit[3]{0.35, 0.35, 0.20};
    double indi_measured_accel_limit[3]{6.0, 6.0, 4.0};
    double indi_accel_lpf_alpha{0.25};
    double nmpc_horizon_s{0.25};
    double nmpc_position_weight[3]{1.0, 1.0, 1.0};
    double nmpc_velocity_weight[3]{0.05, 0.05, 0.05};
    double nmpc_control_weight[3]{0.001, 0.001, 0.001};
    double nmpc_accel_limit[3]{4.0, 4.0, 2.5};
    double nmpc_increment_limit[3]{4.0, 4.0, 2.5};
    double high_order_body_rate_limit[3]{6.0, 6.0, 3.0};
    double high_order_body_accel_limit[3]{60.0, 60.0, 30.0};
    double smooth_feedback_gain[3]{1.2, 1.2, 1.0};
    double smooth_feedback_bound[3]{1.5, 1.5, 1.0};
    double disturbance_observer_gain[3]{0.4, 0.4, 0.3};
    double disturbance_compensation_limit[3]{1.0, 1.0, 0.8};
    double l1_model_decay{1.25};
    double l1_filter_T{0.20};
    double l1_gain[3]{0.32, 0.32, 0.35};
    double l1_comp_limit[3]{2.0, 2.0, 2.0};
    double drag_feedforward_gain[3]{0.0, 0.0, 0.0};
    double safety_accel_limit[3]{50.0, 50.0, 50.0};
    double fault_rotor_efficiency[4]{1.0, 1.0, 1.0, 1.0};
    double fault_allocation_blend{0.52};
    double fault_min_efficiency{0.50};
    double fault_thrust_comp_limit{0.25};
    double integral_limit[3]{0.5, 0.5, 0.3};
    double mass{1.0};
    double gravity{9.80665};
    double hover_percentage{0.37};
    double min_normalized_thrust{0.0};
    double max_normalized_thrust{1.0};
    double tilt_limit_rad{0.5235987755982988};
};

struct CoreState
{
    double thr2acc{9.80665 / 0.37};
    double covariance{1.0e6};
    Vec3 integral_position_error;
    Vec3 previous_velocity;
    Vec3 measured_acceleration_lpf;
    Vec3 previous_command_acceleration;
    Vec3 disturbance_estimate;
    double previous_measurement_stamp_s{0.0};
    bool has_previous_velocity{false};
    bool has_previous_measurement_stamp{false};
};

struct ControllerInput
{
    double dt{0.01};
    Vec3 position;
    Vec3 velocity;
    Quat attitude;
    Vec3 angular_velocity;
    Vec3 reference_position;
    Vec3 reference_velocity;
    Vec3 reference_acceleration;
    Vec3 reference_jerk;
    Vec3 reference_snap;
    double reference_yaw{0.0};
    double reference_yaw_rate{0.0};
    double reference_yaw_acceleration{0.0};
    double measurement_stamp_s{0.0};
    Quat imu_attitude;
    Vec3 imu_angular_velocity;
    bool enable{true};
    bool reset{false};
    bool measurement_stamp_valid{false};
    bool enable_disturbance_observer{true};
};

struct ControllerOutput
{
    Quat desired_attitude;
    double normalized_thrust{0.0};
    double collective_thrust_n{0.0};
    Vec3 position_error;
    Vec3 velocity_error;
    Vec3 sliding_surface;
    Vec3 desired_acceleration;
    Vec3 desired_body_rate;
    Vec3 desired_body_acceleration;
    Vec3 disturbance_estimate;
    Vec3 desired_force_n;
    bool saturated{false};
    int status_code{0};
    std::string status_text{"ok"};
};

inline Quat normalize(const Quat &q)
{
    const double n = std::sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (n <= 0.0)
    {
        return Quat{};
    }
    return Quat{q.w / n, q.x / n, q.y / n, q.z / n};
}

inline Quat conjugate(const Quat &q)
{
    return Quat{q.w, -q.x, -q.y, -q.z};
}

inline Quat multiply(const Quat &a, const Quat &b)
{
    return normalize(Quat{
        a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
        a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
        a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
        a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w,
    });
}

inline Quat inverse(const Quat &q)
{
    return conjugate(normalize(q));
}

inline Quat angle_axis(double angle, const Vec3 &axis)
{
    const double half = 0.5 * angle;
    const double s = std::sin(half);
    return normalize(Quat{std::cos(half), axis.x * s, axis.y * s, axis.z * s});
}

inline double yaw_from_quat(const Quat &q_raw)
{
    const Quat q = normalize(q_raw);
    return std::atan2(
        2.0 * (q.x * q.y + q.w * q.z),
        q.w * q.w + q.x * q.x - q.y * q.y - q.z * q.z);
}

inline Vec3 add(const Vec3 &a, const Vec3 &b)
{
    return Vec3{a.x + b.x, a.y + b.y, a.z + b.z};
}

inline Vec3 subtract(const Vec3 &a, const Vec3 &b)
{
    return Vec3{a.x - b.x, a.y - b.y, a.z - b.z};
}

inline Vec3 scale(const Vec3 &v, double s)
{
    return Vec3{v.x * s, v.y * s, v.z * s};
}

inline double dot(const Vec3 &a, const Vec3 &b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

inline Vec3 cross(const Vec3 &a, const Vec3 &b)
{
    return Vec3{
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x,
    };
}

inline double norm(const Vec3 &v)
{
    return std::sqrt(dot(v, v));
}

inline Vec3 normalize_vec3(const Vec3 &v, const Vec3 &fallback = Vec3{0.0, 0.0, 0.0})
{
    const double n = norm(v);
    if (n <= 1.0e-12)
    {
        return fallback;
    }
    return scale(v, 1.0 / n);
}

inline void reset_thrust_mapping(const CoreParams &params, CoreState &state)
{
    state.thr2acc = params.gravity / params.hover_percentage;
    state.covariance = 1.0e6;
    state.integral_position_error = Vec3{};
    state.previous_velocity = Vec3{};
    state.measured_acceleration_lpf = Vec3{};
    state.previous_command_acceleration = Vec3{};
    state.disturbance_estimate = Vec3{};
    state.previous_measurement_stamp_s = 0.0;
    state.has_previous_velocity = false;
    state.has_previous_measurement_stamp = false;
}

ControllerOutput calculate_px4ctrl_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_official_pid_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_se3_basic_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_dfbc_basic_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_dfbc_high_order_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_dfbc_smooth_robust_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_dfbc_smooth_robust_indi_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_smc_boundary_layer_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_pid_indi_bounded_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_nmpc_outer_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_l1_awff_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_safety_filter_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

ControllerOutput calculate_fault_allocation_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

} // namespace mosim_px4ctrl

#endif
