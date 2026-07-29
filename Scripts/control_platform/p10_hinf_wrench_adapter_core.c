#include "p10_hinf_wrench_adapter_core.h"

#include "wave_b_hinf_core.h"

#include <math.h>
#include <string.h>

static double adapter_clamp_value(double value, double lower, double upper, int *saturated)
{
    if (value < lower) {
        *saturated = 1;
        return lower;
    }
    if (value > upper) {
        *saturated = 1;
        return upper;
    }
    return value;
}

static int params_valid(const MosimP10HinfAdapterParams *params)
{
    int axis;
    if (params == NULL || !isfinite(params->mass) || params->mass <= 0.0 ||
        !isfinite(params->gravity) || params->gravity <= 0.0 ||
        params->force_max_n < params->force_min_n || params->torque_limit_nm <= 0.0 ||
        params->hover_percentage <= 0.0 || params->max_normalized_thrust < params->min_normalized_thrust ||
        params->tilt_limit_rad <= 0.0 || params->yaw_correction_limit_rad <= 0.0) {
        return 0;
    }
    for (axis = 0; axis < 3; ++axis) {
        if (!isfinite(params->attitude_stiffness[axis]) || params->attitude_stiffness[axis] <= 0.0) {
            return 0;
        }
    }
    return 1;
}

static void euler_to_quaternion(double roll, double pitch, double yaw, double quaternion[4])
{
    const double cr = cos(0.5 * roll);
    const double sr = sin(0.5 * roll);
    const double cp = cos(0.5 * pitch);
    const double sp = sin(0.5 * pitch);
    const double cy = cos(0.5 * yaw);
    const double sy = sin(0.5 * yaw);
    quaternion[0] = cr * cp * cy + sr * sp * sy;
    quaternion[1] = sr * cp * cy - cr * sp * sy;
    quaternion[2] = cr * sp * cy + sr * cp * sy;
    quaternion[3] = cr * cp * sy - sr * sp * cy;
}

void mosim_p10_hinf_adapter_default_params(MosimP10HinfAdapterParams *params)
{
    if (params == NULL) return;
    memset(params, 0, sizeof(*params));
    params->mass = 1.0;
    params->gravity = 9.80665;
    params->force_min_n = 0.0;
    params->force_max_n = 25.0;
    params->torque_limit_nm = 8.0;
    params->attitude_stiffness[0] = 30.0;
    params->attitude_stiffness[1] = 30.0;
    params->attitude_stiffness[2] = 40.0;
    params->hover_percentage = 0.37;
    params->tilt_limit_rad = 0.35;
    params->yaw_correction_limit_rad = 0.20;
    params->min_normalized_thrust = 0.0;
    params->max_normalized_thrust = 0.62;
}

int mosim_p10_hinf_adapter_step(
    const MosimP10HinfAdapterParams *params,
    const MosimP10HinfAdapterInput *input,
    MosimP10HinfAdapterOutput *output)
{
    MosimWaveBHinfParams hinf_params;
    MosimWaveBHinfInput hinf_input;
    MosimWaveBHinfOutput hinf_output;
    double thrust_scale;
    int axis;
    int return_code;
    if (params == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->source_command_variant = 3;
    output->adapted_command_variant = 1;
    if (!params_valid(params)) {
        output->status_code = 2;
        return -2;
    }
    memset(&hinf_input, 0, sizeof(hinf_input));
    for (axis = 0; axis < 12; ++axis) {
        hinf_input.state[axis] = input->state[axis];
        hinf_input.reference[axis] = input->reference[axis];
    }
    hinf_input.enable = input->enable;
    hinf_input.reset = input->reset;
    mosim_wave_b_hinf_default_params(&hinf_params);
    hinf_params.mass = params->mass;
    hinf_params.gravity = params->gravity;
    hinf_params.force_min_n = params->force_min_n;
    hinf_params.force_max_n = params->force_max_n;
    hinf_params.torque_limit_nm = params->torque_limit_nm;
    return_code = mosim_wave_b_hinf_step(&hinf_params, &hinf_input, &hinf_output);
    if (return_code != 0 || hinf_output.status_code != 0) {
        output->status_code = hinf_output.status_code;
        return return_code;
    }
    for (axis = 0; axis < 4; ++axis) output->wrench[axis] = hinf_output.wrench[axis];
    output->saturated = hinf_output.saturated;
    output->collective_thrust_n = hinf_output.wrench[0];
    thrust_scale = params->mass * params->gravity / params->hover_percentage;
    output->normalized_thrust = adapter_clamp_value(
        output->collective_thrust_n / thrust_scale,
        params->min_normalized_thrust,
        params->max_normalized_thrust,
        &output->saturated);
    output->adapted_euler[0] = adapter_clamp_value(
        input->reference[0] + output->wrench[1] / params->attitude_stiffness[0],
        -params->tilt_limit_rad,
        params->tilt_limit_rad,
        &output->saturated);
    output->adapted_euler[1] = adapter_clamp_value(
        input->reference[1] + output->wrench[2] / params->attitude_stiffness[1],
        -params->tilt_limit_rad,
        params->tilt_limit_rad,
        &output->saturated);
    output->adapted_euler[2] = input->reference[2] + adapter_clamp_value(
        output->wrench[3] / params->attitude_stiffness[2],
        -params->yaw_correction_limit_rad,
        params->yaw_correction_limit_rad,
        &output->saturated);
    euler_to_quaternion(
        output->adapted_euler[0], output->adapted_euler[1], output->adapted_euler[2],
        output->desired_attitude);
    output->status_code = 0;
    return 0;
}

void MosimP10HinfWrenchAdapterStepScalar(
    double state_roll, double state_pitch, double state_yaw,
    double state_p, double state_q, double state_r,
    double state_u, double state_v, double state_w,
    double state_x, double state_y, double state_z,
    double reference_roll, double reference_pitch, double reference_yaw,
    double reference_p, double reference_q, double reference_r,
    double reference_u, double reference_v, double reference_w,
    double reference_x, double reference_y, double reference_z,
    double enable, double reset, double mass, double gravity,
    double force_min_n, double force_max_n, double torque_limit_nm,
    double roll_stiffness_nm_per_rad, double pitch_stiffness_nm_per_rad,
    double yaw_stiffness_nm_per_rad, double hover_percentage,
    double tilt_limit_rad, double yaw_correction_limit_rad,
    double min_normalized_thrust, double max_normalized_thrust,
    double *wrench_force_n, double *wrench_tau_x_nm, double *wrench_tau_y_nm,
    double *wrench_tau_z_nm, double *desired_attitude_w, double *desired_attitude_x,
    double *desired_attitude_y, double *desired_attitude_z, double *normalized_thrust,
    double *collective_thrust_n, double *adapted_roll_rad, double *adapted_pitch_rad,
    double *adapted_yaw_rad, double *saturated, double *status_code,
    double *source_command_variant, double *adapted_command_variant)
{
    const double state[12] = {state_roll, state_pitch, state_yaw, state_p, state_q, state_r,
                              state_u, state_v, state_w, state_x, state_y, state_z};
    const double reference[12] = {reference_roll, reference_pitch, reference_yaw,
                                  reference_p, reference_q, reference_r, reference_u,
                                  reference_v, reference_w, reference_x, reference_y, reference_z};
    MosimP10HinfAdapterParams params;
    MosimP10HinfAdapterInput input;
    MosimP10HinfAdapterOutput output;
    int index;
    mosim_p10_hinf_adapter_default_params(&params);
    params.mass = mass;
    params.gravity = gravity;
    params.force_min_n = force_min_n;
    params.force_max_n = force_max_n;
    params.torque_limit_nm = torque_limit_nm;
    params.attitude_stiffness[0] = roll_stiffness_nm_per_rad;
    params.attitude_stiffness[1] = pitch_stiffness_nm_per_rad;
    params.attitude_stiffness[2] = yaw_stiffness_nm_per_rad;
    params.hover_percentage = hover_percentage;
    params.tilt_limit_rad = tilt_limit_rad;
    params.yaw_correction_limit_rad = yaw_correction_limit_rad;
    params.min_normalized_thrust = min_normalized_thrust;
    params.max_normalized_thrust = max_normalized_thrust;
    memset(&input, 0, sizeof(input));
    for (index = 0; index < 12; ++index) {
        input.state[index] = state[index];
        input.reference[index] = reference[index];
    }
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    (void)mosim_p10_hinf_adapter_step(&params, &input, &output);
    *wrench_force_n = output.wrench[0];
    *wrench_tau_x_nm = output.wrench[1];
    *wrench_tau_y_nm = output.wrench[2];
    *wrench_tau_z_nm = output.wrench[3];
    *desired_attitude_w = output.desired_attitude[0];
    *desired_attitude_x = output.desired_attitude[1];
    *desired_attitude_y = output.desired_attitude[2];
    *desired_attitude_z = output.desired_attitude[3];
    *normalized_thrust = output.normalized_thrust;
    *collective_thrust_n = output.collective_thrust_n;
    *adapted_roll_rad = output.adapted_euler[0];
    *adapted_pitch_rad = output.adapted_euler[1];
    *adapted_yaw_rad = output.adapted_euler[2];
    *saturated = (double)output.saturated;
    *status_code = (double)output.status_code;
    *source_command_variant = (double)output.source_command_variant;
    *adapted_command_variant = (double)output.adapted_command_variant;
}
