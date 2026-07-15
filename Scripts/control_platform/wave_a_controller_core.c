#include "wave_a_controller_core.h"

#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static void normalize_quaternion(const double in[4], double out[4])
{
    const double n = sqrt(in[0] * in[0] + in[1] * in[1] + in[2] * in[2] + in[3] * in[3]);
    if (n <= 1.0e-12) {
        out[0] = 1.0; out[1] = 0.0; out[2] = 0.0; out[3] = 0.0;
        return;
    }
    out[0] = in[0] / n; out[1] = in[1] / n; out[2] = in[2] / n; out[3] = in[3] / n;
}

static void attitude_from_acceleration(
    const MosimWaveAParams *params,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output)
{
    double roll = -output->desired_acceleration[1] / params->gravity;
    double pitch = output->desired_acceleration[0] / params->gravity;
    const double unclamped_roll = roll;
    const double unclamped_pitch = pitch;
    roll = clamp_value(roll, -params->tilt_limit_rad, params->tilt_limit_rad);
    pitch = clamp_value(pitch, -params->tilt_limit_rad, params->tilt_limit_rad);
    if (fabs(roll - unclamped_roll) > 1.0e-12 || fabs(pitch - unclamped_pitch) > 1.0e-12) {
        output->saturated = 1;
    }

    {
        const double cy = cos(0.5 * input->reference_yaw);
        const double sy = sin(0.5 * input->reference_yaw);
        const double cp = cos(0.5 * pitch);
        const double sp = sin(0.5 * pitch);
        const double cr = cos(0.5 * roll);
        const double sr = sin(0.5 * roll);
        const double q[4] = {
            cy * cp * cr + sy * sp * sr,
            cy * cp * sr - sy * sp * cr,
            sy * cp * sr + cy * sp * cr,
            sy * cp * cr - cy * sp * sr
        };
        normalize_quaternion(q, output->desired_attitude_wxyz);
    }

    output->normalized_thrust = output->desired_acceleration[2] / (params->gravity / params->hover_percentage);
    {
        const double unclamped = output->normalized_thrust;
        output->normalized_thrust = clamp_value(output->normalized_thrust, 0.0, 1.0);
        if (fabs(unclamped - output->normalized_thrust) > 1.0e-12) output->saturated = 1;
    }
    output->collective_thrust_n = output->normalized_thrust * params->mass * params->gravity / params->hover_percentage;
    output->command_variant = 1;
}

static void outer_loop_step(
    int controller_id,
    const MosimWaveAParams *params,
    MosimWaveAState *state,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output)
{
    int i;
    const double dt = input->dt > 0.0 ? input->dt : 0.01;
    for (i = 0; i < 3; ++i) {
        const double ep = input->reference_position[i] - input->position[i];
        const double ev = input->reference_velocity[i] - input->velocity[i];
        double feedback;
        if (controller_id == MOSIM_WAVE_A_LQI) {
            state->integral_position_error[i] = clamp_value(
                state->integral_position_error[i] + ep * dt,
                -params->integral_limit[i],
                params->integral_limit[i]);
        }
        if (controller_id == MOSIM_WAVE_A_BACKSTEPPING) {
            const double virtual_velocity_error = ev + params->backstepping_k1[i] * ep;
            feedback = params->backstepping_k1[i] * ev + params->backstepping_k2[i] * virtual_velocity_error;
        } else {
            feedback = params->kp[i] * ep + params->kv[i] * ev;
            if (controller_id == MOSIM_WAVE_A_LQI) feedback += params->ki[i] * state->integral_position_error[i];
        }
        output->desired_acceleration[i] = input->reference_acceleration[i] + feedback;
    }
    output->desired_acceleration[2] += params->gravity;
    attitude_from_acceleration(params, input, output);
}

static void so3_step(
    const MosimWaveAParams *params,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output)
{
    double q[4];
    double qd[4];
    double qe[4];
    int i;
    normalize_quaternion(input->attitude_wxyz, q);
    normalize_quaternion(input->reference_attitude_wxyz, qd);
    /* qe = conjugate(q) * qd, shortest-arc sign below. */
    qe[0] = q[0] * qd[0] + q[1] * qd[1] + q[2] * qd[2] + q[3] * qd[3];
    qe[1] = q[0] * qd[1] - q[1] * qd[0] - q[2] * qd[3] + q[3] * qd[2];
    qe[2] = q[0] * qd[2] + q[1] * qd[3] - q[2] * qd[0] - q[3] * qd[1];
    qe[3] = q[0] * qd[3] - q[1] * qd[2] + q[2] * qd[1] - q[3] * qd[0];
    {
        const double sign = qe[0] < 0.0 ? -1.0 : 1.0;
        for (i = 0; i < 3; ++i) {
            const double raw = input->reference_body_rate[i] + 2.0 * params->so3_attitude_gain[i] * sign * qe[i + 1];
            output->desired_body_rate[i] = clamp_value(raw, -params->body_rate_limit[i], params->body_rate_limit[i]);
            if (fabs(raw - output->desired_body_rate[i]) > 1.0e-12) output->saturated = 1;
        }
    }
    memcpy(output->desired_attitude_wxyz, qd, sizeof(qd));
    output->collective_thrust_n = input->collective_thrust_n;
    output->normalized_thrust = clamp_value(
        input->collective_thrust_n / (params->mass * params->gravity / params->hover_percentage),
        0.0,
        1.0);
    output->command_variant = 2;
}

void mosim_wave_a_default_params(MosimWaveAParams *params)
{
    const MosimWaveAParams defaults = {
        {1.6, 1.6, 2.2}, {1.8, 1.8, 2.0}, {0.20, 0.20, 0.30}, {0.50, 0.50, 0.35},
        {1.1, 1.1, 1.3}, {1.8, 1.8, 2.0}, {3.0, 3.0, 1.8}, {5.0, 5.0, 3.0},
        0.67, 9.8, 0.37, 0.5235987755982988
    };
    if (params != NULL) *params = defaults;
}

void mosim_wave_a_reset(MosimWaveAState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

int mosim_wave_a_step(
    int controller_id,
    const MosimWaveAParams *params,
    MosimWaveAState *state,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output)
{
    if (params == NULL || state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_wxyz[0] = 1.0;
    if (input->reset) mosim_wave_a_reset(state);
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    if (controller_id == MOSIM_WAVE_A_LQR || controller_id == MOSIM_WAVE_A_LQI ||
        controller_id == MOSIM_WAVE_A_BACKSTEPPING) {
        outer_loop_step(controller_id, params, state, input, output);
        return 0;
    }
    if (controller_id == MOSIM_WAVE_A_SO3) {
        so3_step(params, input, output);
        return 0;
    }
    output->status_code = -2;
    return -2;
}
