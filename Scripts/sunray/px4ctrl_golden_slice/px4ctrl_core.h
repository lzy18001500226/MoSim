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
    double mass{0.67};
    double gravity{9.8};
    double hover_percentage{0.37};
};

struct CoreState
{
    double thr2acc{9.8 / 0.37};
    double covariance{1.0e6};
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
    double reference_yaw{0.0};
    double reference_yaw_rate{0.0};
    Quat imu_attitude;
    Vec3 imu_angular_velocity;
    bool enable{true};
    bool reset{false};
};

struct ControllerOutput
{
    Quat desired_attitude;
    double normalized_thrust{0.0};
    double collective_thrust_n{0.0};
    Vec3 position_error;
    Vec3 velocity_error;
    Vec3 desired_acceleration;
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

inline void reset_thrust_mapping(const CoreParams &params, CoreState &state)
{
    state.thr2acc = params.gravity / params.hover_percentage;
    state.covariance = 1.0e6;
}

ControllerOutput calculate_px4ctrl_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input);

} // namespace mosim_px4ctrl

#endif
