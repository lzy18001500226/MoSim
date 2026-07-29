#include "px4ctrl_core.h"

namespace mosim_px4ctrl
{

namespace
{

double clamp(double value, double lower, double upper)
{
    if (value < lower)
    {
        return lower;
    }
    if (value > upper)
    {
        return upper;
    }
    return value;
}

Vec3 clamp_vec3(const Vec3 &value, const double limit[3])
{
    return Vec3{
        clamp(value.x, -limit[0], limit[0]),
        clamp(value.y, -limit[1], limit[1]),
        clamp(value.z, -limit[2], limit[2]),
    };
}

bool vec3_components_equal(const Vec3 &a, const Vec3 &b, double tol = 1.0e-12)
{
    return std::fabs(a.x - b.x) <= tol &&
        std::fabs(a.y - b.y) <= tol &&
        std::fabs(a.z - b.z) <= tol;
}

Vec3 clamp_delta_vec3(const Vec3 &value, const Vec3 &previous, const double limit[3])
{
    const Vec3 delta = clamp_vec3(subtract(value, previous), limit);
    return add(previous, delta);
}

double sat(double value)
{
    return clamp(value, -1.0, 1.0);
}

double safe_positive(double value, double fallback)
{
    return value > 1.0e-9 ? value : fallback;
}

double safe_nonnegative(double value)
{
    return value > 0.0 ? value : 0.0;
}

void fill_common_error_state(const ControllerInput &input, ControllerOutput &out)
{
    out.position_error = subtract(input.reference_position, input.position);
    out.velocity_error = subtract(input.reference_velocity, input.velocity);
}

Vec3 pid_acceleration_no_gravity(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input,
    ControllerOutput &out)
{
    out.position_error = subtract(input.reference_position, input.position);
    out.velocity_error = subtract(input.reference_velocity, input.velocity);

    const double dt = input.dt > 0.0 ? input.dt : 0.01;
    state.integral_position_error = clamp_vec3(
        Vec3{
            state.integral_position_error.x + out.position_error.x * dt,
            state.integral_position_error.y + out.position_error.y * dt,
            state.integral_position_error.z + out.position_error.z * dt,
        },
        params.integral_limit);

    return Vec3{
        input.reference_acceleration.x + params.kv[0] * out.velocity_error.x + params.kp[0] * out.position_error.x + params.ki[0] * state.integral_position_error.x,
        input.reference_acceleration.y + params.kv[1] * out.velocity_error.y + params.kp[1] * out.position_error.y + params.ki[1] * state.integral_position_error.y,
        input.reference_acceleration.z + params.kv[2] * out.velocity_error.z + params.kp[2] * out.position_error.z + params.ki[2] * state.integral_position_error.z,
    };
}

Vec3 measured_acceleration_from_velocity(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input,
    double dt)
{
    dt = safe_positive(dt, 0.01);
    Vec3 measured_acceleration;
    if (state.has_previous_velocity)
    {
        measured_acceleration = scale(subtract(input.velocity, state.previous_velocity), 1.0 / dt);
    }
    else
    {
        measured_acceleration = state.previous_command_acceleration;
    }

    measured_acceleration = clamp_vec3(measured_acceleration, params.indi_measured_accel_limit);
    const double alpha = clamp(params.indi_accel_lpf_alpha, 0.0, 1.0);
    if (state.has_previous_velocity)
    {
        state.measured_acceleration_lpf = add(
            scale(measured_acceleration, alpha),
            scale(state.measured_acceleration_lpf, 1.0 - alpha));
    }
    else
    {
        state.measured_acceleration_lpf = measured_acceleration;
    }

    state.previous_velocity = input.velocity;
    state.has_previous_velocity = true;
    return state.measured_acceleration_lpf;
}

bool consume_new_measurement_sample(
    CoreState &state,
    const ControllerInput &input,
    double &dt)
{
    dt = safe_positive(input.dt, 0.01);
    if (!input.measurement_stamp_valid)
    {
        return true;
    }

    if (!state.has_previous_measurement_stamp)
    {
        state.previous_measurement_stamp_s = input.measurement_stamp_s;
        state.has_previous_measurement_stamp = true;
        return true;
    }

    const double measurement_dt = input.measurement_stamp_s - state.previous_measurement_stamp_s;
    if (measurement_dt <= 1.0e-6)
    {
        return false;
    }

    state.previous_measurement_stamp_s = input.measurement_stamp_s;
    dt = measurement_dt;
    return true;
}

Vec3 smooth_bounded_feedback(
    const CoreParams &params,
    const ControllerOutput &out)
{
    return Vec3{
        params.smooth_feedback_bound[0] * std::tanh(
            (params.kp[0] * out.position_error.x + params.kv[0] * out.velocity_error.x) /
            safe_positive(params.smooth_feedback_bound[0], 1.0)),
        params.smooth_feedback_bound[1] * std::tanh(
            (params.kp[1] * out.position_error.y + params.kv[1] * out.velocity_error.y) /
            safe_positive(params.smooth_feedback_bound[1], 1.0)),
        params.smooth_feedback_bound[2] * std::tanh(
            (params.kp[2] * out.position_error.z + params.kv[2] * out.velocity_error.z) /
            safe_positive(params.smooth_feedback_bound[2], 1.0)),
    };
}

ControllerOutput disabled_output(const ControllerInput &input)
{
    ControllerOutput out;
    out.status_code = 1;
    out.status_text = "disabled";
    out.desired_attitude = normalize(input.imu_attitude);
    out.normalized_thrust = 0.0;
    out.collective_thrust_n = 0.0;
    return out;
}

Quat quat_from_rotation_matrix_columns(const Vec3 &b1, const Vec3 &b2, const Vec3 &b3)
{
    const double m00 = b1.x;
    const double m01 = b2.x;
    const double m02 = b3.x;
    const double m10 = b1.y;
    const double m11 = b2.y;
    const double m12 = b3.y;
    const double m20 = b1.z;
    const double m21 = b2.z;
    const double m22 = b3.z;

    const double trace = m00 + m11 + m22;
    if (trace > 0.0)
    {
        const double s = std::sqrt(trace + 1.0) * 2.0;
        return normalize(Quat{
            0.25 * s,
            (m21 - m12) / s,
            (m02 - m20) / s,
            (m10 - m01) / s,
        });
    }
    if (m00 > m11 && m00 > m22)
    {
        const double s = std::sqrt(1.0 + m00 - m11 - m22) * 2.0;
        return normalize(Quat{
            (m21 - m12) / s,
            0.25 * s,
            (m01 + m10) / s,
            (m02 + m20) / s,
        });
    }
    if (m11 > m22)
    {
        const double s = std::sqrt(1.0 + m11 - m00 - m22) * 2.0;
        return normalize(Quat{
            (m02 - m20) / s,
            (m01 + m10) / s,
            0.25 * s,
            (m12 + m21) / s,
        });
    }
    const double s = std::sqrt(1.0 + m22 - m00 - m11) * 2.0;
    return normalize(Quat{
        (m10 - m01) / s,
        (m02 + m20) / s,
        (m12 + m21) / s,
        0.25 * s,
    });
}

void fill_attitude_thrust_output(
    const CoreParams &params,
    const CoreState &state,
    const ControllerInput &input,
    ControllerOutput &out,
    bool enforce_limits)
{
    out.normalized_thrust = out.desired_acceleration.z / state.thr2acc;
    if (enforce_limits)
    {
        const double unclamped_normalized_thrust = out.normalized_thrust;
        out.normalized_thrust = clamp(
            out.normalized_thrust,
            params.min_normalized_thrust,
            params.max_normalized_thrust);
        out.saturated = out.saturated ||
            std::fabs(out.normalized_thrust - unclamped_normalized_thrust) > 1.0e-12;
    }

    const double full_thrust_n = params.mass * params.gravity / params.hover_percentage;
    out.collective_thrust_n = out.normalized_thrust * full_thrust_n;

    out.desired_force_n = Vec3{
        params.mass * out.desired_acceleration.x,
        params.mass * out.desired_acceleration.y,
        params.mass * out.desired_acceleration.z,
    };

    const double yaw_odom = yaw_from_quat(input.attitude);
    const double sin_yaw = std::sin(yaw_odom);
    const double cos_yaw = std::cos(yaw_odom);

    double roll = (out.desired_acceleration.x * sin_yaw - out.desired_acceleration.y * cos_yaw) / params.gravity;
    double pitch = (out.desired_acceleration.x * cos_yaw + out.desired_acceleration.y * sin_yaw) / params.gravity;
    if (enforce_limits)
    {
        const double unclamped_roll = roll;
        const double unclamped_pitch = pitch;
        roll = clamp(roll, -params.tilt_limit_rad, params.tilt_limit_rad);
        pitch = clamp(pitch, -params.tilt_limit_rad, params.tilt_limit_rad);
        out.saturated = out.saturated ||
            std::fabs(roll - unclamped_roll) > 1.0e-12 ||
            std::fabs(pitch - unclamped_pitch) > 1.0e-12;
    }

    const Quat q_yaw = angle_axis(input.reference_yaw, Vec3{0.0, 0.0, 1.0});
    const Quat q_pitch = angle_axis(pitch, Vec3{0.0, 1.0, 0.0});
    const Quat q_roll = angle_axis(roll, Vec3{1.0, 0.0, 0.0});
    const Quat q_des_world = multiply(multiply(q_yaw, q_pitch), q_roll);

    out.desired_attitude = multiply(multiply(input.imu_attitude, inverse(input.attitude)), q_des_world);
}

void fill_flatness_attitude_output(
    const CoreParams &params,
    const CoreState &state,
    const ControllerInput &input,
    ControllerOutput &out,
    const Vec3 &force,
    bool enforce_limits)
{
    Vec3 limited_force = force;
    const double force_norm = norm(limited_force);
    Vec3 b3c = normalize_vec3(limited_force, Vec3{0.0, 0.0, 1.0});

    constexpr double kHalfPi = 1.57079632679489661923;
    if (enforce_limits && params.tilt_limit_rad > 0.0 && params.tilt_limit_rad < kHalfPi)
    {
        const double min_b3_z = std::cos(params.tilt_limit_rad);
        if (b3c.z < min_b3_z)
        {
            const double xy_norm = std::sqrt(b3c.x * b3c.x + b3c.y * b3c.y);
            const double xy_limited = std::sin(params.tilt_limit_rad);
            if (xy_norm > 1.0e-12)
            {
                b3c.x = b3c.x / xy_norm * xy_limited;
                b3c.y = b3c.y / xy_norm * xy_limited;
            }
            else
            {
                b3c.x = 0.0;
                b3c.y = 0.0;
            }
            b3c.z = min_b3_z;
            b3c = normalize_vec3(b3c, Vec3{0.0, 0.0, 1.0});
            limited_force = scale(b3c, force_norm);
            out.saturated = true;
        }
    }

    const Vec3 b1d{std::cos(input.reference_yaw), std::sin(input.reference_yaw), 0.0};
    Vec3 b2c = cross(b3c, b1d);
    if (norm(b2c) <= 1.0e-9)
    {
        b2c = cross(b3c, Vec3{0.0, 1.0, 0.0});
    }
    b2c = normalize_vec3(b2c, Vec3{0.0, 1.0, 0.0});
    const Vec3 b1c = normalize_vec3(cross(b2c, b3c), b1d);

    out.desired_attitude = multiply(
        multiply(input.imu_attitude, inverse(input.attitude)),
        quat_from_rotation_matrix_columns(b1c, b2c, b3c));

    out.desired_force_n = limited_force;
    out.desired_acceleration = Vec3{
        limited_force.x / params.mass,
        limited_force.y / params.mass,
        limited_force.z / params.mass,
    };

    out.normalized_thrust = dot(limited_force, b3c) / (params.mass * state.thr2acc);
    const double unclamped_normalized_thrust = out.normalized_thrust;
    if (enforce_limits)
    {
        out.normalized_thrust = clamp(
            out.normalized_thrust,
            params.min_normalized_thrust,
            params.max_normalized_thrust);
        out.saturated = out.saturated ||
            std::fabs(out.normalized_thrust - unclamped_normalized_thrust) > 1.0e-12;
    }

    const double full_thrust_n = params.mass * params.gravity / params.hover_percentage;
    out.collective_thrust_n = out.normalized_thrust * full_thrust_n;
}

Vec3 body_rate_from_jerk(
    const CoreParams &params,
    const Vec3 &desired_force,
    const Vec3 &reference_jerk,
    double reference_yaw_rate)
{
    const double thrust_n = safe_positive(norm(desired_force), params.mass * params.gravity);
    const Vec3 b3c = normalize_vec3(desired_force, Vec3{0.0, 0.0, 1.0});
    const Vec3 h_omega = scale(cross(b3c, scale(reference_jerk, params.mass)), 1.0 / thrust_n);
    return clamp_vec3(
        Vec3{
            -h_omega.y,
            h_omega.x,
            reference_yaw_rate * b3c.z,
        },
        params.high_order_body_rate_limit);
}

Vec3 body_acceleration_from_snap(
    const CoreParams &params,
    const Vec3 &desired_force,
    const Vec3 &reference_snap,
    double reference_yaw_acceleration)
{
    const double thrust_n = safe_positive(norm(desired_force), params.mass * params.gravity);
    const Vec3 b3c = normalize_vec3(desired_force, Vec3{0.0, 0.0, 1.0});
    const Vec3 h_acc = scale(cross(b3c, scale(reference_snap, params.mass)), 1.0 / thrust_n);
    return clamp_vec3(
        Vec3{
            -h_acc.y,
            h_acc.x,
            reference_yaw_acceleration * b3c.z,
        },
        params.high_order_body_accel_limit);
}

} // namespace

ControllerOutput calculate_px4ctrl_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    out.position_error = Vec3{
        input.reference_position.x - input.position.x,
        input.reference_position.y - input.position.y,
        input.reference_position.z - input.position.z,
    };
    out.velocity_error = Vec3{
        input.reference_velocity.x - input.velocity.x,
        input.reference_velocity.y - input.velocity.y,
        input.reference_velocity.z - input.velocity.z,
    };

    out.desired_acceleration = Vec3{
        input.reference_acceleration.x + params.kv[0] * out.velocity_error.x + params.kp[0] * out.position_error.x,
        input.reference_acceleration.y + params.kv[1] * out.velocity_error.y + params.kp[1] * out.position_error.y,
        input.reference_acceleration.z + params.kv[2] * out.velocity_error.z + params.kp[2] * out.position_error.z + params.gravity,
    };

    fill_attitude_thrust_output(params, state, input, out, false);
    return out;
}

ControllerOutput calculate_official_pid_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    out.position_error = Vec3{
        input.reference_position.x - input.position.x,
        input.reference_position.y - input.position.y,
        input.reference_position.z - input.position.z,
    };
    out.velocity_error = Vec3{
        input.reference_velocity.x - input.velocity.x,
        input.reference_velocity.y - input.velocity.y,
        input.reference_velocity.z - input.velocity.z,
    };

    const double dt = input.dt > 0.0 ? input.dt : 0.01;
    state.integral_position_error = clamp_vec3(
        Vec3{
            state.integral_position_error.x + out.position_error.x * dt,
            state.integral_position_error.y + out.position_error.y * dt,
            state.integral_position_error.z + out.position_error.z * dt,
        },
        params.integral_limit);

    out.desired_acceleration = Vec3{
        input.reference_acceleration.x + params.kv[0] * out.velocity_error.x + params.kp[0] * out.position_error.x + params.ki[0] * state.integral_position_error.x,
        input.reference_acceleration.y + params.kv[1] * out.velocity_error.y + params.kp[1] * out.position_error.y + params.ki[1] * state.integral_position_error.y,
        input.reference_acceleration.z + params.kv[2] * out.velocity_error.z + params.kp[2] * out.position_error.z + params.ki[2] * state.integral_position_error.z + params.gravity,
    };

    fill_attitude_thrust_output(params, state, input, out, true);
    out.status_text = "official_pid_attitude_thrust";
    return out;
}

ControllerOutput calculate_se3_basic_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    out.position_error = subtract(input.reference_position, input.position);
    out.velocity_error = subtract(input.reference_velocity, input.velocity);

    Vec3 desired_acc_no_gravity{
        input.reference_acceleration.x + params.kp[0] * out.position_error.x + params.kv[0] * out.velocity_error.x,
        input.reference_acceleration.y + params.kp[1] * out.position_error.y + params.kv[1] * out.velocity_error.y,
        input.reference_acceleration.z + params.kp[2] * out.position_error.z + params.kv[2] * out.velocity_error.z,
    };

    Vec3 force = add(
        scale(desired_acc_no_gravity, params.mass),
        Vec3{0.0, 0.0, params.mass * params.gravity});

    const double force_norm = norm(force);
    Vec3 b3c = normalize_vec3(force, Vec3{0.0, 0.0, 1.0});

    constexpr double kHalfPi = 1.57079632679489661923;
    if (params.tilt_limit_rad > 0.0 && params.tilt_limit_rad < kHalfPi)
    {
        const double min_b3_z = std::cos(params.tilt_limit_rad);
        if (b3c.z < min_b3_z)
        {
            const double xy_norm = std::sqrt(b3c.x * b3c.x + b3c.y * b3c.y);
            const double xy_limited = std::sin(params.tilt_limit_rad);
            if (xy_norm > 1.0e-12)
            {
                b3c.x = b3c.x / xy_norm * xy_limited;
                b3c.y = b3c.y / xy_norm * xy_limited;
            }
            else
            {
                b3c.x = 0.0;
                b3c.y = 0.0;
            }
            b3c.z = min_b3_z;
            b3c = normalize_vec3(b3c, Vec3{0.0, 0.0, 1.0});
            force = scale(b3c, force_norm);
            out.saturated = true;
        }
    }

    const Vec3 b1d{std::cos(input.reference_yaw), std::sin(input.reference_yaw), 0.0};
    Vec3 b2c = cross(b3c, b1d);
    if (norm(b2c) <= 1.0e-9)
    {
        b2c = cross(b3c, Vec3{0.0, 1.0, 0.0});
    }
    b2c = normalize_vec3(b2c, Vec3{0.0, 1.0, 0.0});
    Vec3 b1c = normalize_vec3(cross(b2c, b3c), b1d);

    out.desired_attitude = multiply(
        multiply(input.imu_attitude, inverse(input.attitude)),
        quat_from_rotation_matrix_columns(b1c, b2c, b3c));

    out.desired_acceleration = Vec3{
        force.x / params.mass,
        force.y / params.mass,
        force.z / params.mass,
    };
    out.desired_force_n = force;

    out.normalized_thrust = dot(force, b3c) / (params.mass * state.thr2acc);
    const double unclamped_normalized_thrust = out.normalized_thrust;
    out.normalized_thrust = clamp(
        out.normalized_thrust,
        params.min_normalized_thrust,
        params.max_normalized_thrust);
    out.saturated = out.saturated ||
        std::fabs(out.normalized_thrust - unclamped_normalized_thrust) > 1.0e-12;

    const double full_thrust_n = params.mass * params.gravity / params.hover_percentage;
    out.collective_thrust_n = out.normalized_thrust * full_thrust_n;
    out.status_text = "se3_basic_attitude_thrust";
    return out;
}

ControllerOutput calculate_dfbc_basic_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    out.position_error = subtract(input.reference_position, input.position);
    out.velocity_error = subtract(input.reference_velocity, input.velocity);

    const Vec3 flat_output_acceleration{
        input.reference_acceleration.x + params.kp[0] * out.position_error.x + params.kv[0] * out.velocity_error.x,
        input.reference_acceleration.y + params.kp[1] * out.position_error.y + params.kv[1] * out.velocity_error.y,
        input.reference_acceleration.z + params.kp[2] * out.position_error.z + params.kv[2] * out.velocity_error.z,
    };

    Vec3 force = Vec3{
        params.mass * flat_output_acceleration.x,
        params.mass * flat_output_acceleration.y,
        params.mass * (flat_output_acceleration.z + params.gravity),
    };

    const double force_norm = norm(force);
    Vec3 b3c = normalize_vec3(force, Vec3{0.0, 0.0, 1.0});

    constexpr double kHalfPi = 1.57079632679489661923;
    if (params.tilt_limit_rad > 0.0 && params.tilt_limit_rad < kHalfPi)
    {
        const double min_b3_z = std::cos(params.tilt_limit_rad);
        if (b3c.z < min_b3_z)
        {
            const double xy_norm = std::sqrt(b3c.x * b3c.x + b3c.y * b3c.y);
            const double xy_limited = std::sin(params.tilt_limit_rad);
            if (xy_norm > 1.0e-12)
            {
                b3c.x = b3c.x / xy_norm * xy_limited;
                b3c.y = b3c.y / xy_norm * xy_limited;
            }
            else
            {
                b3c.x = 0.0;
                b3c.y = 0.0;
            }
            b3c.z = min_b3_z;
            b3c = normalize_vec3(b3c, Vec3{0.0, 0.0, 1.0});
            force = scale(b3c, force_norm);
            out.saturated = true;
        }
    }

    const Vec3 b1d{std::cos(input.reference_yaw), std::sin(input.reference_yaw), 0.0};
    Vec3 b2c = cross(b3c, b1d);
    if (norm(b2c) <= 1.0e-9)
    {
        b2c = cross(b3c, Vec3{0.0, 1.0, 0.0});
    }
    b2c = normalize_vec3(b2c, Vec3{0.0, 1.0, 0.0});
    const Vec3 b1c = normalize_vec3(cross(b2c, b3c), b1d);

    out.desired_attitude = multiply(
        multiply(input.imu_attitude, inverse(input.attitude)),
        quat_from_rotation_matrix_columns(b1c, b2c, b3c));

    out.desired_acceleration = Vec3{
        force.x / params.mass,
        force.y / params.mass,
        force.z / params.mass,
    };
    out.desired_force_n = force;

    out.normalized_thrust = dot(force, b3c) / (params.mass * state.thr2acc);
    const double unclamped_normalized_thrust = out.normalized_thrust;
    out.normalized_thrust = clamp(
        out.normalized_thrust,
        params.min_normalized_thrust,
        params.max_normalized_thrust);
    out.saturated = out.saturated ||
        std::fabs(out.normalized_thrust - unclamped_normalized_thrust) > 1.0e-12;

    const double full_thrust_n = params.mass * params.gravity / params.hover_percentage;
    out.collective_thrust_n = out.normalized_thrust * full_thrust_n;
    out.status_text = "dfbc_basic_attitude_thrust";
    return out;
}

ControllerOutput calculate_dfbc_high_order_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    out.position_error = subtract(input.reference_position, input.position);
    out.velocity_error = subtract(input.reference_velocity, input.velocity);

    const Vec3 flat_output_acceleration{
        input.reference_acceleration.x + params.kp[0] * out.position_error.x + params.kv[0] * out.velocity_error.x,
        input.reference_acceleration.y + params.kp[1] * out.position_error.y + params.kv[1] * out.velocity_error.y,
        input.reference_acceleration.z + params.kp[2] * out.position_error.z + params.kv[2] * out.velocity_error.z,
    };

    const Vec3 force{
        params.mass * flat_output_acceleration.x,
        params.mass * flat_output_acceleration.y,
        params.mass * (flat_output_acceleration.z + params.gravity),
    };

    fill_flatness_attitude_output(params, state, input, out, force, true);
    out.desired_body_rate = body_rate_from_jerk(
        params,
        out.desired_force_n,
        input.reference_jerk,
        input.reference_yaw_rate);
    out.desired_body_acceleration = body_acceleration_from_snap(
        params,
        out.desired_force_n,
        input.reference_snap,
        input.reference_yaw_acceleration);
    out.status_text = "dfbc_high_order_attitude_thrust_with_bodyrate_feedforward";
    return out;
}

ControllerOutput calculate_dfbc_smooth_robust_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    out.position_error = subtract(input.reference_position, input.position);
    out.velocity_error = subtract(input.reference_velocity, input.velocity);

    const Vec3 bounded_feedback = smooth_bounded_feedback(params, out);
    const Vec3 model_acceleration{
        input.reference_acceleration.x + bounded_feedback.x,
        input.reference_acceleration.y + bounded_feedback.y,
        input.reference_acceleration.z + bounded_feedback.z,
    };

    double measurement_dt = input.dt;
    Vec3 residual{};
    if (input.enable_disturbance_observer &&
        consume_new_measurement_sample(state, input, measurement_dt))
    {
        const Vec3 measured_acceleration =
            measured_acceleration_from_velocity(params, state, input, measurement_dt);
        residual = subtract(measured_acceleration, state.previous_command_acceleration);
        state.disturbance_estimate = clamp_vec3(
            Vec3{
                (1.0 - params.disturbance_observer_gain[0]) * state.disturbance_estimate.x + params.disturbance_observer_gain[0] * residual.x,
                (1.0 - params.disturbance_observer_gain[1]) * state.disturbance_estimate.y + params.disturbance_observer_gain[1] * residual.y,
                (1.0 - params.disturbance_observer_gain[2]) * state.disturbance_estimate.z + params.disturbance_observer_gain[2] * residual.z,
            },
            params.disturbance_compensation_limit);
    }

    const Vec3 compensated_acceleration = input.enable_disturbance_observer
        ? subtract(model_acceleration, state.disturbance_estimate)
        : model_acceleration;
    state.previous_command_acceleration = compensated_acceleration;

    const Vec3 force{
        params.mass * compensated_acceleration.x,
        params.mass * compensated_acceleration.y,
        params.mass * (compensated_acceleration.z + params.gravity),
    };

    fill_flatness_attitude_output(params, state, input, out, force, true);
    out.desired_body_rate = body_rate_from_jerk(
        params,
        out.desired_force_n,
        input.reference_jerk,
        input.reference_yaw_rate);
    out.desired_body_acceleration = body_acceleration_from_snap(
        params,
        out.desired_force_n,
        input.reference_snap,
        input.reference_yaw_acceleration);
    out.sliding_surface = residual;
    out.disturbance_estimate = state.disturbance_estimate;
    out.status_text = input.enable_disturbance_observer
        ? "dfbc_smooth_robust_attitude_thrust_dob"
        : "dfbc_smooth_robust_attitude_thrust_no_dob";
    return out;
}

ControllerOutput calculate_dfbc_smooth_robust_indi_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    out.position_error = subtract(input.reference_position, input.position);
    out.velocity_error = subtract(input.reference_velocity, input.velocity);

    const Vec3 bounded_feedback = smooth_bounded_feedback(params, out);
    const Vec3 model_acceleration{
        input.reference_acceleration.x + bounded_feedback.x,
        input.reference_acceleration.y + bounded_feedback.y,
        input.reference_acceleration.z + bounded_feedback.z,
    };

    double measurement_dt = input.dt;
    const bool update_measurement = consume_new_measurement_sample(state, input, measurement_dt);
    const bool had_previous_velocity = state.has_previous_velocity;
    Vec3 measured_acceleration = state.measured_acceleration_lpf;
    if (update_measurement)
    {
        measured_acceleration = measured_acceleration_from_velocity(params, state, input, measurement_dt);
    }

    Vec3 residual{};
    Vec3 indi_increment{};
    if (update_measurement)
    {
        residual = subtract(measured_acceleration, state.previous_command_acceleration);
        state.disturbance_estimate = clamp_vec3(
            Vec3{
                (1.0 - params.disturbance_observer_gain[0]) * state.disturbance_estimate.x + params.disturbance_observer_gain[0] * residual.x,
                (1.0 - params.disturbance_observer_gain[1]) * state.disturbance_estimate.y + params.disturbance_observer_gain[1] * residual.y,
                (1.0 - params.disturbance_observer_gain[2]) * state.disturbance_estimate.z + params.disturbance_observer_gain[2] * residual.z,
            },
            params.disturbance_compensation_limit);
    }

    if (update_measurement && had_previous_velocity)
    {
        const Vec3 high_frequency_residual = subtract(residual, state.disturbance_estimate);
        indi_increment = clamp_vec3(
            Vec3{
                params.indi_gain[0] * high_frequency_residual.x,
                params.indi_gain[1] * high_frequency_residual.y,
                params.indi_gain[2] * high_frequency_residual.z,
            },
            params.indi_increment_limit);
        out.sliding_surface = high_frequency_residual;
    }
    else
    {
        out.sliding_surface = Vec3{};
    }

    const Vec3 compensated_acceleration =
        subtract(model_acceleration, state.disturbance_estimate);
    const Vec3 corrected_acceleration = add(compensated_acceleration, indi_increment);
    state.previous_command_acceleration = corrected_acceleration;

    const Vec3 force{
        params.mass * corrected_acceleration.x,
        params.mass * corrected_acceleration.y,
        params.mass * (corrected_acceleration.z + params.gravity),
    };

    fill_flatness_attitude_output(params, state, input, out, force, true);
    out.desired_body_rate = body_rate_from_jerk(
        params,
        out.desired_force_n,
        input.reference_jerk,
        input.reference_yaw_rate);
    out.desired_body_acceleration = body_acceleration_from_snap(
        params,
        out.desired_force_n,
        input.reference_snap,
        input.reference_yaw_acceleration);
    out.disturbance_estimate = state.disturbance_estimate;
    out.status_text = "dfbc_smooth_robust_dob_indi_attitude_thrust";
    return out;
}

ControllerOutput calculate_smc_boundary_layer_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    out.position_error = subtract(input.reference_position, input.position);
    out.velocity_error = subtract(input.reference_velocity, input.velocity);

    out.sliding_surface = clamp_vec3(
        Vec3{
            out.velocity_error.x + params.smc_lambda[0] * out.position_error.x,
            out.velocity_error.y + params.smc_lambda[1] * out.position_error.y,
            out.velocity_error.z + params.smc_lambda[2] * out.position_error.z,
        },
        params.smc_surface_limit);

    const double phi_x = std::fabs(params.smc_phi[0]) > 1.0e-9 ? std::fabs(params.smc_phi[0]) : 1.0e-9;
    const double phi_y = std::fabs(params.smc_phi[1]) > 1.0e-9 ? std::fabs(params.smc_phi[1]) : 1.0e-9;
    const double phi_z = std::fabs(params.smc_phi[2]) > 1.0e-9 ? std::fabs(params.smc_phi[2]) : 1.0e-9;

    const Vec3 switching_acceleration{
        params.smc_eta[0] * sat(out.sliding_surface.x / phi_x),
        params.smc_eta[1] * sat(out.sliding_surface.y / phi_y),
        params.smc_eta[2] * sat(out.sliding_surface.z / phi_z),
    };

    const Vec3 outer_acceleration{
        input.reference_acceleration.x + params.kp[0] * out.position_error.x + params.kv[0] * out.velocity_error.x + switching_acceleration.x,
        input.reference_acceleration.y + params.kp[1] * out.position_error.y + params.kv[1] * out.velocity_error.y + switching_acceleration.y,
        input.reference_acceleration.z + params.kp[2] * out.position_error.z + params.kv[2] * out.velocity_error.z + switching_acceleration.z,
    };

    Vec3 force = Vec3{
        params.mass * outer_acceleration.x,
        params.mass * outer_acceleration.y,
        params.mass * (outer_acceleration.z + params.gravity),
    };

    const double force_norm = norm(force);
    Vec3 b3c = normalize_vec3(force, Vec3{0.0, 0.0, 1.0});

    constexpr double kHalfPi = 1.57079632679489661923;
    if (params.tilt_limit_rad > 0.0 && params.tilt_limit_rad < kHalfPi)
    {
        const double min_b3_z = std::cos(params.tilt_limit_rad);
        if (b3c.z < min_b3_z)
        {
            const double xy_norm = std::sqrt(b3c.x * b3c.x + b3c.y * b3c.y);
            const double xy_limited = std::sin(params.tilt_limit_rad);
            if (xy_norm > 1.0e-12)
            {
                b3c.x = b3c.x / xy_norm * xy_limited;
                b3c.y = b3c.y / xy_norm * xy_limited;
            }
            else
            {
                b3c.x = 0.0;
                b3c.y = 0.0;
            }
            b3c.z = min_b3_z;
            b3c = normalize_vec3(b3c, Vec3{0.0, 0.0, 1.0});
            force = scale(b3c, force_norm);
            out.saturated = true;
        }
    }

    const Vec3 b1d{std::cos(input.reference_yaw), std::sin(input.reference_yaw), 0.0};
    Vec3 b2c = cross(b3c, b1d);
    if (norm(b2c) <= 1.0e-9)
    {
        b2c = cross(b3c, Vec3{0.0, 1.0, 0.0});
    }
    b2c = normalize_vec3(b2c, Vec3{0.0, 1.0, 0.0});
    const Vec3 b1c = normalize_vec3(cross(b2c, b3c), b1d);

    out.desired_attitude = multiply(
        multiply(input.imu_attitude, inverse(input.attitude)),
        quat_from_rotation_matrix_columns(b1c, b2c, b3c));

    out.desired_acceleration = Vec3{
        force.x / params.mass,
        force.y / params.mass,
        force.z / params.mass,
    };
    out.desired_force_n = force;

    out.normalized_thrust = dot(force, b3c) / (params.mass * state.thr2acc);
    const double unclamped_normalized_thrust = out.normalized_thrust;
    out.normalized_thrust = clamp(
        out.normalized_thrust,
        params.min_normalized_thrust,
        params.max_normalized_thrust);
    out.saturated = out.saturated ||
        std::fabs(out.normalized_thrust - unclamped_normalized_thrust) > 1.0e-12;

    const double full_thrust_n = params.mass * params.gravity / params.hover_percentage;
    out.collective_thrust_n = out.normalized_thrust * full_thrust_n;
    out.status_text = "smc_boundary_layer_attitude_thrust";
    return out;
}

ControllerOutput calculate_pid_indi_bounded_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    const Vec3 base_acceleration_no_gravity =
        pid_acceleration_no_gravity(params, state, input, out);
    double measurement_dt = input.dt;
    const bool update_measurement = consume_new_measurement_sample(state, input, measurement_dt);
    const bool had_previous_velocity = state.has_previous_velocity;
    Vec3 measured_acceleration = state.measured_acceleration_lpf;
    if (update_measurement)
    {
        measured_acceleration = measured_acceleration_from_velocity(params, state, input, measurement_dt);
    }

    Vec3 indi_increment;
    if (update_measurement && had_previous_velocity)
    {
        const Vec3 acceleration_residual =
            subtract(state.previous_command_acceleration, measured_acceleration);
        indi_increment = clamp_vec3(
            Vec3{
                params.indi_gain[0] * acceleration_residual.x,
                params.indi_gain[1] * acceleration_residual.y,
                params.indi_gain[2] * acceleration_residual.z,
            },
            params.indi_increment_limit);
        out.sliding_surface = acceleration_residual;
    }
    else
    {
        indi_increment = Vec3{};
        out.sliding_surface = Vec3{};
    }

    const Vec3 corrected_acceleration_no_gravity =
        add(base_acceleration_no_gravity, indi_increment);
    state.previous_command_acceleration = corrected_acceleration_no_gravity;

    out.desired_acceleration = Vec3{
        corrected_acceleration_no_gravity.x,
        corrected_acceleration_no_gravity.y,
        corrected_acceleration_no_gravity.z + params.gravity,
    };

    fill_attitude_thrust_output(params, state, input, out, true);
    out.status_text = "pid_indi_bounded_attitude_thrust";
    return out;
}

ControllerOutput calculate_nmpc_outer_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    out.position_error = subtract(input.reference_position, input.position);
    out.velocity_error = subtract(input.reference_velocity, input.velocity);

    const double horizon = clamp(params.nmpc_horizon_s, 0.05, 2.0);
    const double half_horizon_sq = 0.5 * horizon * horizon;
    const double horizon_sq = horizon * horizon;
    const double horizon_fourth = horizon_sq * horizon_sq;

    const Vec3 reference_position_horizon{
        input.reference_position.x + input.reference_velocity.x * horizon + half_horizon_sq * input.reference_acceleration.x,
        input.reference_position.y + input.reference_velocity.y * horizon + half_horizon_sq * input.reference_acceleration.y,
        input.reference_position.z + input.reference_velocity.z * horizon + half_horizon_sq * input.reference_acceleration.z,
    };
    const Vec3 reference_velocity_horizon{
        input.reference_velocity.x + input.reference_acceleration.x * horizon,
        input.reference_velocity.y + input.reference_acceleration.y * horizon,
        input.reference_velocity.z + input.reference_acceleration.z * horizon,
    };
    const Vec3 predicted_position_open_loop{
        input.position.x + input.velocity.x * horizon,
        input.position.y + input.velocity.y * horizon,
        input.position.z + input.velocity.z * horizon,
    };

    const Vec3 horizon_position_error =
        subtract(reference_position_horizon, predicted_position_open_loop);
    const Vec3 horizon_velocity_error =
        subtract(reference_velocity_horizon, input.velocity);

    const double wp[3]{
        safe_nonnegative(params.nmpc_position_weight[0]),
        safe_nonnegative(params.nmpc_position_weight[1]),
        safe_nonnegative(params.nmpc_position_weight[2]),
    };
    const double wv[3]{
        safe_nonnegative(params.nmpc_velocity_weight[0]),
        safe_nonnegative(params.nmpc_velocity_weight[1]),
        safe_nonnegative(params.nmpc_velocity_weight[2]),
    };
    const double wu[3]{
        safe_nonnegative(params.nmpc_control_weight[0]),
        safe_nonnegative(params.nmpc_control_weight[1]),
        safe_nonnegative(params.nmpc_control_weight[2]),
    };

    Vec3 unconstrained_acceleration;
    const double numerator_x =
        wp[0] * horizon_sq * horizon_position_error.x +
        2.0 * wv[0] * horizon * horizon_velocity_error.x +
        2.0 * wu[0] * state.previous_command_acceleration.x;
    const double denominator_x =
        0.5 * wp[0] * horizon_fourth + 2.0 * wv[0] * horizon_sq + 2.0 * wu[0];
    unconstrained_acceleration.x = numerator_x / safe_positive(denominator_x, 1.0e-6);

    const double numerator_y =
        wp[1] * horizon_sq * horizon_position_error.y +
        2.0 * wv[1] * horizon * horizon_velocity_error.y +
        2.0 * wu[1] * state.previous_command_acceleration.y;
    const double denominator_y =
        0.5 * wp[1] * horizon_fourth + 2.0 * wv[1] * horizon_sq + 2.0 * wu[1];
    unconstrained_acceleration.y = numerator_y / safe_positive(denominator_y, 1.0e-6);

    const double numerator_z =
        wp[2] * horizon_sq * horizon_position_error.z +
        2.0 * wv[2] * horizon * horizon_velocity_error.z +
        2.0 * wu[2] * state.previous_command_acceleration.z;
    const double denominator_z =
        0.5 * wp[2] * horizon_fourth + 2.0 * wv[2] * horizon_sq + 2.0 * wu[2];
    unconstrained_acceleration.z = numerator_z / safe_positive(denominator_z, 1.0e-6);

    Vec3 constrained_acceleration =
        clamp_vec3(unconstrained_acceleration, params.nmpc_accel_limit);
    constrained_acceleration =
        clamp_delta_vec3(constrained_acceleration, state.previous_command_acceleration, params.nmpc_increment_limit);
    state.previous_command_acceleration = constrained_acceleration;

    out.desired_acceleration = Vec3{
        constrained_acceleration.x,
        constrained_acceleration.y,
        constrained_acceleration.z + params.gravity,
    };
    out.sliding_surface = subtract(unconstrained_acceleration, constrained_acceleration);
    out.saturated = norm(out.sliding_surface) > 1.0e-12;

    fill_attitude_thrust_output(params, state, input, out, true);
    out.status_text = "nmpc_outer_attitude_thrust";
    return out;
}

ControllerOutput calculate_l1_awff_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    fill_common_error_state(input, out);
    const Vec3 nominal_acceleration_no_gravity = pid_acceleration_no_gravity(params, state, input, out);

    double measurement_dt = input.dt;
    const bool update_measurement = consume_new_measurement_sample(state, input, measurement_dt);
    const bool had_previous_velocity = state.has_previous_velocity;
    Vec3 measured_acceleration = state.measured_acceleration_lpf;
    if (update_measurement)
    {
        measured_acceleration = measured_acceleration_from_velocity(params, state, input, measurement_dt);
    }

    Vec3 residual{};
    if (update_measurement && had_previous_velocity)
    {
        residual = subtract(measured_acceleration, state.previous_command_acceleration);
        const double filter_T = std::fabs(params.l1_filter_T);
        const double alpha = filter_T > 1.0e-9
            ? clamp(measurement_dt / (filter_T + measurement_dt), 0.0, 1.0)
            : 1.0;
        const double model_decay = safe_nonnegative(params.l1_model_decay);
        const Vec3 adaptive_update{
            -params.l1_gain[0] * residual.x - model_decay * state.disturbance_estimate.x,
            -params.l1_gain[1] * residual.y - model_decay * state.disturbance_estimate.y,
            -params.l1_gain[2] * residual.z - model_decay * state.disturbance_estimate.z,
        };
        state.disturbance_estimate = clamp_vec3(
            add(
                scale(state.disturbance_estimate, 1.0 - alpha),
                scale(add(state.disturbance_estimate, scale(adaptive_update, measurement_dt)), alpha)),
            params.l1_comp_limit);
    }

    const Vec3 drag_feedforward{
        -params.drag_feedforward_gain[0] * input.reference_velocity.x,
        -params.drag_feedforward_gain[1] * input.reference_velocity.y,
        -params.drag_feedforward_gain[2] * input.reference_velocity.z,
    };
    const Vec3 compensated_acceleration_no_gravity =
        add(add(nominal_acceleration_no_gravity, state.disturbance_estimate), drag_feedforward);
    state.previous_command_acceleration = compensated_acceleration_no_gravity;

    out.desired_acceleration = Vec3{
        compensated_acceleration_no_gravity.x,
        compensated_acceleration_no_gravity.y,
        compensated_acceleration_no_gravity.z + params.gravity,
    };
    fill_attitude_thrust_output(params, state, input, out, true);
    out.sliding_surface = residual;
    out.disturbance_estimate = state.disturbance_estimate;
    out.status_text = "l1_awff_attitude_thrust_minimal";
    return out;
}

ControllerOutput calculate_safety_filter_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    const Vec3 nominal_acceleration_no_gravity = pid_acceleration_no_gravity(params, state, input, out);
    const Vec3 limited_acceleration_no_gravity =
        clamp_vec3(nominal_acceleration_no_gravity, params.safety_accel_limit);
    out.saturated = !vec3_components_equal(nominal_acceleration_no_gravity, limited_acceleration_no_gravity);
    out.sliding_surface = subtract(nominal_acceleration_no_gravity, limited_acceleration_no_gravity);
    state.previous_command_acceleration = limited_acceleration_no_gravity;

    out.desired_acceleration = Vec3{
        limited_acceleration_no_gravity.x,
        limited_acceleration_no_gravity.y,
        limited_acceleration_no_gravity.z + params.gravity,
    };
    const bool saturated_before_attitude = out.saturated;
    fill_attitude_thrust_output(params, state, input, out, true);
    out.saturated = out.saturated || saturated_before_attitude;
    out.status_code = out.saturated ? 2 : 0;
    out.status_text = out.saturated
        ? "safety_filter_attitude_thrust_limited"
        : "safety_filter_attitude_thrust_passthrough";
    return out;
}

ControllerOutput calculate_fault_allocation_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        return disabled_output(input);
    }

    const Vec3 nominal_acceleration_no_gravity = pid_acceleration_no_gravity(params, state, input, out);
    state.previous_command_acceleration = nominal_acceleration_no_gravity;
    out.desired_acceleration = Vec3{
        nominal_acceleration_no_gravity.x,
        nominal_acceleration_no_gravity.y,
        nominal_acceleration_no_gravity.z + params.gravity,
    };
    fill_attitude_thrust_output(params, state, input, out, true);

    double min_efficiency = 1.0;
    double mean_efficiency = 0.0;
    for (int i = 0; i < 4; ++i)
    {
        const double eta = clamp(
            params.fault_rotor_efficiency[i],
            safe_positive(params.fault_min_efficiency, 0.01),
            1.0);
        min_efficiency = std::min(min_efficiency, eta);
        mean_efficiency += eta;
    }
    mean_efficiency *= 0.25;

    const double missing_authority = clamp(1.0 - mean_efficiency, 0.0, 1.0);
    const double requested_multiplier = 1.0 + clamp(params.fault_allocation_blend, 0.0, 1.0) * missing_authority;
    const double bounded_multiplier = clamp(
        requested_multiplier,
        1.0,
        1.0 + safe_nonnegative(params.fault_thrust_comp_limit));
    const double uncompensated_thrust = out.normalized_thrust;
    out.normalized_thrust = clamp(
        uncompensated_thrust * bounded_multiplier,
        params.min_normalized_thrust,
        params.max_normalized_thrust);
    const double full_thrust_n = params.mass * params.gravity / params.hover_percentage;
    out.collective_thrust_n = out.normalized_thrust * full_thrust_n;
    out.desired_force_n = Vec3{
        out.desired_force_n.x,
        out.desired_force_n.y,
        out.desired_force_n.z * bounded_multiplier,
    };
    out.saturated = out.saturated ||
        missing_authority > 1.0e-12 ||
        std::fabs(out.normalized_thrust - uncompensated_thrust * bounded_multiplier) > 1.0e-12;
    out.disturbance_estimate = Vec3{
        missing_authority,
        min_efficiency,
        bounded_multiplier - 1.0,
    };
    out.sliding_surface = Vec3{
        params.fault_rotor_efficiency[0],
        params.fault_rotor_efficiency[1],
        params.fault_rotor_efficiency[2],
    };
    out.status_code = missing_authority > 1.0e-12 ? 3 : 0;
    out.status_text = "fault_allocation_attitude_thrust_degraded_compensation";
    return out;
}

} // namespace mosim_px4ctrl
