#include "MoSim_P4_Mpc_CFunction_Sysblock.h"
/*** Current Block Name: cFunction ***/
enum MosimMpcControllerId {
    MOSIM_MPC_LINEAR = 1,
    MOSIM_MPC_ROBUST = 2,
    MOSIM_MPC_ADAPTIVE = 3,
    MOSIM_MPC_TUBE = 4,
    MOSIM_MPC_EXPLICIT_GAIN_SCHEDULED = 5,
    MOSIM_MPC_ILQR = 6,
    MOSIM_MPC_MPPI = 7
};

typedef struct {
    double dt;
    double position[3];
    double velocity[3];
    double reference_position[3];
    double reference_velocity[3];
    double reference_acceleration[3];
    double reference_yaw;
    int enable;
    int reset;
} MosimMpcInput;

typedef struct {
    double horizon_s;
    double position_weight[3];
    double velocity_weight[3];
    double control_weight[3];
    double acceleration_limit[3];
    double increment_limit[3];
    double robust_bound[3];
    double tube_position_gain[3];
    double tube_velocity_gain[3];
    double adaptive_rate;
    double adaptive_scale_min;
    double adaptive_scale_max;
    double schedule_error_threshold;
    double ilqr_step_size;
    double mppi_temperature;
    double mppi_noise_scale[3];
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimMpcParams;

typedef struct {
    double previous_acceleration[3];
    double adaptive_scale;
    unsigned long step_count;
} MosimMpcState;

typedef struct {
    double desired_acceleration[3];
    double desired_attitude_wxyz[4];
    double normalized_thrust;
    double collective_thrust_n;
    double unconstrained_acceleration[3];
    double auxiliary[3];
    double solver_cost;
    int solver_iterations;
    int saturated;
    int status_code;
} MosimMpcOutput;

void mosim_mpc_default_params(MosimMpcParams *params);
void mosim_mpc_reset(MosimMpcState *state);
int mosim_mpc_step(
    int controller_id,
    const MosimMpcParams *params,
    MosimMpcState *state,
    const MosimMpcInput *input,
    MosimMpcOutput *output);




#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static double norm3(const double value[3])
{
    return sqrt(value[0] * value[0] + value[1] * value[1] + value[2] * value[2]);
}

static int finite3(const double value[3])
{
    return isfinite(value[0]) && isfinite(value[1]) && isfinite(value[2]);
}

static void cross3(const double a[3], const double b[3], double out[3])
{
    out[0] = a[1] * b[2] - a[2] * b[1];
    out[1] = a[2] * b[0] - a[0] * b[2];
    out[2] = a[0] * b[1] - a[1] * b[0];
}

static int normalize3(double value[3])
{
    const double length = norm3(value);
    int axis;
    if (length <= 1.0e-12) return -1;
    for (axis = 0; axis < 3; ++axis) value[axis] /= length;
    return 0;
}

static void quaternion_from_rotation(double rotation[3][3], double q[4])
{
    const double trace = rotation[0][0] + rotation[1][1] + rotation[2][2];
    if (trace > 0.0) {
        const double scale = 2.0 * sqrt(trace + 1.0);
        q[0] = 0.25 * scale;
        q[1] = (rotation[2][1] - rotation[1][2]) / scale;
        q[2] = (rotation[0][2] - rotation[2][0]) / scale;
        q[3] = (rotation[1][0] - rotation[0][1]) / scale;
    } else if (rotation[0][0] > rotation[1][1] && rotation[0][0] > rotation[2][2]) {
        const double scale = 2.0 * sqrt(1.0 + rotation[0][0] - rotation[1][1] - rotation[2][2]);
        q[0] = (rotation[2][1] - rotation[1][2]) / scale;
        q[1] = 0.25 * scale;
        q[2] = (rotation[0][1] + rotation[1][0]) / scale;
        q[3] = (rotation[0][2] + rotation[2][0]) / scale;
    } else if (rotation[1][1] > rotation[2][2]) {
        const double scale = 2.0 * sqrt(1.0 + rotation[1][1] - rotation[0][0] - rotation[2][2]);
        q[0] = (rotation[0][2] - rotation[2][0]) / scale;
        q[1] = (rotation[0][1] + rotation[1][0]) / scale;
        q[2] = 0.25 * scale;
        q[3] = (rotation[1][2] + rotation[2][1]) / scale;
    } else {
        const double scale = 2.0 * sqrt(1.0 + rotation[2][2] - rotation[0][0] - rotation[1][1]);
        q[0] = (rotation[1][0] - rotation[0][1]) / scale;
        q[1] = (rotation[0][2] + rotation[2][0]) / scale;
        q[2] = (rotation[1][2] + rotation[2][1]) / scale;
        q[3] = 0.25 * scale;
    }
    if (q[0] < 0.0) {
        q[0] = -q[0]; q[1] = -q[1]; q[2] = -q[2]; q[3] = -q[3];
    }
}

static int params_valid(const MosimMpcParams *params)
{
    int axis;
    if (!isfinite(params->horizon_s) || params->horizon_s <= 0.0 || params->horizon_s > 2.0 ||
        !isfinite(params->adaptive_rate) || params->adaptive_rate < 0.0 ||
        !isfinite(params->adaptive_scale_min) || !isfinite(params->adaptive_scale_max) ||
        params->adaptive_scale_min <= 0.0 || params->adaptive_scale_max < params->adaptive_scale_min ||
        !isfinite(params->schedule_error_threshold) || params->schedule_error_threshold <= 0.0 ||
        !isfinite(params->ilqr_step_size) || params->ilqr_step_size <= 0.0 ||
        !isfinite(params->mppi_temperature) || params->mppi_temperature <= 0.0 ||
        !isfinite(params->mass_kg) || params->mass_kg <= 0.0 ||
        !isfinite(params->gravity_mps2) || params->gravity_mps2 <= 0.0 ||
        !isfinite(params->hover_percentage) || params->hover_percentage <= 0.0 || params->hover_percentage > 1.0 ||
        !isfinite(params->max_tilt_rad) || params->max_tilt_rad <= 0.0 ||
        params->max_tilt_rad >= 1.5707963267948966 ||
        !isfinite(params->min_collective_thrust_n) || !isfinite(params->max_collective_thrust_n) ||
        params->min_collective_thrust_n < 0.0 || params->max_collective_thrust_n <= params->min_collective_thrust_n) return 0;
    for (axis = 0; axis < 3; ++axis) {
        if (!isfinite(params->position_weight[axis]) || params->position_weight[axis] <= 0.0 ||
            !isfinite(params->velocity_weight[axis]) || params->velocity_weight[axis] < 0.0 ||
            !isfinite(params->control_weight[axis]) || params->control_weight[axis] <= 0.0 ||
            !isfinite(params->acceleration_limit[axis]) || params->acceleration_limit[axis] <= 0.0 ||
            !isfinite(params->increment_limit[axis]) || params->increment_limit[axis] <= 0.0 ||
            !isfinite(params->robust_bound[axis]) || params->robust_bound[axis] < 0.0 ||
            !isfinite(params->tube_position_gain[axis]) || params->tube_position_gain[axis] < 0.0 ||
            !isfinite(params->tube_velocity_gain[axis]) || params->tube_velocity_gain[axis] < 0.0 ||
            !isfinite(params->mppi_noise_scale[axis]) || params->mppi_noise_scale[axis] < 0.0) return 0;
    }
    return 1;
}

static double stage_cost(double ep, double ev, double acceleration, const MosimMpcParams *params, int axis)
{
    const double horizon = params->horizon_s;
    const double predicted_position_error = ep + horizon * ev - 0.5 * horizon * horizon * acceleration;
    const double predicted_velocity_error = ev - horizon * acceleration;
    return params->position_weight[axis] * predicted_position_error * predicted_position_error +
        params->velocity_weight[axis] * predicted_velocity_error * predicted_velocity_error +
        params->control_weight[axis] * acceleration * acceleration;
}

static double linear_solution(double ep, double ev, double previous, const MosimMpcParams *params, int axis)
{
    const double horizon = params->horizon_s;
    const double horizon_sq = horizon * horizon;
    const double numerator = params->position_weight[axis] * horizon_sq * ep +
        2.0 * params->velocity_weight[axis] * horizon * ev +
        2.0 * params->control_weight[axis] * previous;
    const double denominator = 0.5 * params->position_weight[axis] * horizon_sq * horizon_sq +
        2.0 * params->velocity_weight[axis] * horizon_sq + 2.0 * params->control_weight[axis];
    return numerator / fmax(denominator, 1.0e-9);
}

static double ilqr_solution(double ep, double ev, double initial, const MosimMpcParams *params, int axis)
{
    double acceleration = initial;
    const double h = params->horizon_s;
    const double hessian = 0.5 * params->position_weight[axis] * h * h * h * h +
        2.0 * params->velocity_weight[axis] * h * h + 2.0 * params->control_weight[axis];
    int iteration;
    for (iteration = 0; iteration < 5; ++iteration) {
        const double pe = ep + h * ev - 0.5 * h * h * acceleration;
        const double ve = ev - h * acceleration;
        const double gradient = -params->position_weight[axis] * h * h * pe -
            2.0 * params->velocity_weight[axis] * h * ve +
            2.0 * params->control_weight[axis] * acceleration;
        acceleration -= params->ilqr_step_size * gradient / fmax(hessian, 1.0e-9);
    }
    return acceleration;
}

static double mppi_solution(double ep, double ev, double initial, const MosimMpcParams *params, int axis, double *cost_out)
{
    static const double samples[7] = {-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5};
    double weighted = 0.0;
    double weight_sum = 0.0;
    double min_cost = HUGE_VAL;
    double costs[7];
    double candidates[7];
    int sample;
    for (sample = 0; sample < 7; ++sample) {
        candidates[sample] = initial + samples[sample] * params->mppi_noise_scale[axis];
        costs[sample] = stage_cost(ep, ev, candidates[sample], params, axis);
        if (costs[sample] < min_cost) min_cost = costs[sample];
    }
    for (sample = 0; sample < 7; ++sample) {
        const double weight = exp(-(costs[sample] - min_cost) / params->mppi_temperature);
        weighted += weight * candidates[sample];
        weight_sum += weight;
    }
    if (cost_out != NULL) *cost_out = min_cost;
    return weighted / fmax(weight_sum, 1.0e-12);
}

static int command_from_acceleration(
    const MosimMpcParams *params,
    const MosimMpcInput *input,
    MosimMpcOutput *output)
{
    double force[3];
    double b1_reference[3];
    double b1[3];
    double b2[3];
    double b3[3];
    double rotation[3][3];
    double force_norm;
    double horizontal_acceleration = hypot(output->desired_acceleration[0], output->desired_acceleration[1]);
    double horizontal_limit = fmax(0.0, output->desired_acceleration[2]) * tan(params->max_tilt_rad);
    int axis;
    if (horizontal_acceleration > horizontal_limit && horizontal_acceleration > 1.0e-12) {
        const double scale = horizontal_limit / horizontal_acceleration;
        output->desired_acceleration[0] *= scale;
        output->desired_acceleration[1] *= scale;
        output->saturated = 1;
    }
    for (axis = 0; axis < 3; ++axis) {
        force[axis] = params->mass_kg * output->desired_acceleration[axis];
        b3[axis] = force[axis];
    }
    force_norm = norm3(force);
    if (normalize3(b3) != 0) return -4;
    b1_reference[0] = cos(input->reference_yaw);
    b1_reference[1] = sin(input->reference_yaw);
    b1_reference[2] = 0.0;
    cross3(b3, b1_reference, b2);
    if (normalize3(b2) != 0) return -4;
    cross3(b2, b3, b1);
    for (axis = 0; axis < 3; ++axis) {
        rotation[axis][0] = b1[axis];
        rotation[axis][1] = b2[axis];
        rotation[axis][2] = b3[axis];
    }
    quaternion_from_rotation(rotation, output->desired_attitude_wxyz);
    output->collective_thrust_n = clamp_value(force_norm, params->min_collective_thrust_n, params->max_collective_thrust_n);
    if (fabs(output->collective_thrust_n - force_norm) > 1.0e-12) output->saturated = 1;
    output->normalized_thrust = clamp_value(
        output->collective_thrust_n / (params->mass_kg * params->gravity_mps2 / params->hover_percentage), 0.0, 1.0);
    return 0;
}

void mosim_mpc_default_params(MosimMpcParams *params)
{
    const MosimMpcParams defaults = {
        0.25,
        {1.0, 1.0, 1.2}, {0.08, 0.08, 0.10}, {0.002, 0.002, 0.003},
        {4.0, 4.0, 2.5}, {1.2, 1.2, 0.8}, {0.25, 0.25, 0.20},
        {0.35, 0.35, 0.45}, {0.18, 0.18, 0.25},
        0.08, 0.75, 1.25, 0.75, 0.65, 0.30, {0.35, 0.35, 0.25},
        0.67, 9.80665, 0.291, 0.5235987755982988, 0.0, 16.0
    };
    if (params != NULL) *params = defaults;
}

void mosim_mpc_reset(MosimMpcState *state)
{
    if (state == NULL) return;
    memset(state, 0, sizeof(*state));
    state->adaptive_scale = 1.0;
}

int mosim_mpc_step(
    int controller_id,
    const MosimMpcParams *params,
    MosimMpcState *state,
    const MosimMpcInput *input,
    MosimMpcOutput *output)
{
    int axis;
    int rc;
    if (params == NULL || state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_wxyz[0] = 1.0;
    if (input->reset) mosim_mpc_reset(state);
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    if (!params_valid(params)) {
        output->status_code = -5;
        return -5;
    }
    if (!isfinite(input->dt) || input->dt <= 0.0 || input->dt > 0.1 ||
        !finite3(input->position) || !finite3(input->velocity) ||
        !finite3(input->reference_position) || !finite3(input->reference_velocity) ||
        !finite3(input->reference_acceleration) || !isfinite(input->reference_yaw)) {
        output->status_code = -3;
        return -3;
    }
    if (controller_id < MOSIM_MPC_LINEAR || controller_id > MOSIM_MPC_MPPI) {
        output->status_code = -2;
        return -2;
    }
    if (controller_id == MOSIM_MPC_ADAPTIVE) {
        double adaptation_signal = 0.0;
        for (axis = 0; axis < 3; ++axis) {
            adaptation_signal += (input->reference_position[axis] - input->position[axis]) *
                (input->reference_velocity[axis] - input->velocity[axis]);
        }
        state->adaptive_scale = clamp_value(
            state->adaptive_scale + params->adaptive_rate * adaptation_signal * input->dt / 3.0,
            params->adaptive_scale_min, params->adaptive_scale_max);
    }
    for (axis = 0; axis < 3; ++axis) {
        const double ep = input->reference_position[axis] - input->position[axis];
        const double ev = input->reference_velocity[axis] - input->velocity[axis];
        double acceleration = linear_solution(ep, ev, state->previous_acceleration[axis], params, axis);
        double limit = params->acceleration_limit[axis];
        if (controller_id == MOSIM_MPC_ROBUST) {
            acceleration += params->robust_bound[axis] * tanh(4.0 * (ep + params->horizon_s * ev));
            output->auxiliary[axis] = params->robust_bound[axis];
        } else if (controller_id == MOSIM_MPC_ADAPTIVE) {
            acceleration *= state->adaptive_scale;
            output->auxiliary[axis] = state->adaptive_scale;
        } else if (controller_id == MOSIM_MPC_TUBE) {
            acceleration += params->tube_position_gain[axis] * ep + params->tube_velocity_gain[axis] * ev;
            limit = fmax(0.1, limit - params->robust_bound[axis]);
            output->auxiliary[axis] = limit;
        } else if (controller_id == MOSIM_MPC_EXPLICIT_GAIN_SCHEDULED) {
            const double schedule = clamp_value(fabs(ep) / params->schedule_error_threshold, 0.0, 1.0);
            acceleration += schedule * (params->tube_position_gain[axis] * ep + params->tube_velocity_gain[axis] * ev);
            output->auxiliary[axis] = schedule;
        } else if (controller_id == MOSIM_MPC_ILQR) {
            acceleration = ilqr_solution(ep, ev, acceleration, params, axis);
            output->solver_iterations = 5;
        } else if (controller_id == MOSIM_MPC_MPPI) {
            double cost = 0.0;
            acceleration = mppi_solution(ep, ev, acceleration, params, axis, &cost);
            output->solver_cost += cost;
            output->solver_iterations = 7;
        }
        acceleration += input->reference_acceleration[axis];
        output->unconstrained_acceleration[axis] = acceleration;
        acceleration = clamp_value(acceleration, -limit, limit);
        acceleration = clamp_value(acceleration,
            state->previous_acceleration[axis] - params->increment_limit[axis],
            state->previous_acceleration[axis] + params->increment_limit[axis]);
        if (fabs(acceleration - output->unconstrained_acceleration[axis]) > 1.0e-12) output->saturated = 1;
        state->previous_acceleration[axis] = acceleration;
        output->desired_acceleration[axis] = acceleration;
        if (controller_id != MOSIM_MPC_MPPI) output->solver_cost += stage_cost(ep, ev, acceleration, params, axis);
    }
    output->desired_acceleration[2] += params->gravity_mps2;
    state->step_count += 1UL;
    rc = command_from_acceleration(params, input, output);
    if (rc != 0) {
        output->status_code = rc;
        return rc;
    }
    return 0;
}
void MosimMpcStepScalar(
    double controller_id,
    double dt,
    double position_x,
    double position_y,
    double position_z,
    double velocity_x,
    double velocity_y,
    double velocity_z,
    double reference_position_x,
    double reference_position_y,
    double reference_position_z,
    double reference_velocity_x,
    double reference_velocity_y,
    double reference_velocity_z,
    double reference_acceleration_x,
    double reference_acceleration_y,
    double reference_acceleration_z,
    double reference_yaw,
    double mass_kg,
    double gravity_mps2,
    double hover_percentage,
    double max_tilt_rad,
    double min_collective_thrust_n,
    double max_collective_thrust_n,
    double enable,
    double reset,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *normalized_thrust,
    double *collective_thrust_n,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *unconstrained_acceleration_x,
    double *unconstrained_acceleration_y,
    double *unconstrained_acceleration_z,
    double *auxiliary_x,
    double *auxiliary_y,
    double *auxiliary_z,
    double *solver_cost,
    double *solver_iterations,
    double *saturated,
    double *status_code)
{
    static MosimMpcState states[8];
    static unsigned char initialized[8];
    MosimMpcParams params;
    MosimMpcInput input;
    MosimMpcOutput output;
    int id = (int)controller_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.position[0] = position_x; input.position[1] = position_y; input.position[2] = position_z;
    input.velocity[0] = velocity_x; input.velocity[1] = velocity_y; input.velocity[2] = velocity_z;
    input.reference_position[0] = reference_position_x;
    input.reference_position[1] = reference_position_y;
    input.reference_position[2] = reference_position_z;
    input.reference_velocity[0] = reference_velocity_x;
    input.reference_velocity[1] = reference_velocity_y;
    input.reference_velocity[2] = reference_velocity_z;
    input.reference_acceleration[0] = reference_acceleration_x;
    input.reference_acceleration[1] = reference_acceleration_y;
    input.reference_acceleration[2] = reference_acceleration_z;
    input.reference_yaw = reference_yaw;
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    mosim_mpc_default_params(&params);
    params.mass_kg = mass_kg;
    params.gravity_mps2 = gravity_mps2;
    params.hover_percentage = hover_percentage;
    params.max_tilt_rad = max_tilt_rad;
    params.min_collective_thrust_n = min_collective_thrust_n;
    params.max_collective_thrust_n = max_collective_thrust_n;
    if (id < 1 || id > 7) id = 0;
    if (id != 0 && !initialized[id]) {
        mosim_mpc_reset(&states[id]);
        initialized[id] = 1;
    }
    result = mosim_mpc_step(id, &params, &states[id], &input, &output);
    if (result != 0) {
        memset(&output, 0, sizeof(output));
        output.desired_attitude_wxyz[0] = 1.0;
        output.status_code = result;
    }
    *desired_attitude_w = output.desired_attitude_wxyz[0];
    *desired_attitude_x = output.desired_attitude_wxyz[1];
    *desired_attitude_y = output.desired_attitude_wxyz[2];
    *desired_attitude_z = output.desired_attitude_wxyz[3];
    *normalized_thrust = output.normalized_thrust;
    *collective_thrust_n = output.collective_thrust_n;
    *desired_acceleration_x = output.desired_acceleration[0];
    *desired_acceleration_y = output.desired_acceleration[1];
    *desired_acceleration_z = output.desired_acceleration[2];
    *unconstrained_acceleration_x = output.unconstrained_acceleration[0];
    *unconstrained_acceleration_y = output.unconstrained_acceleration[1];
    *unconstrained_acceleration_z = output.unconstrained_acceleration[2];
    *auxiliary_x = output.auxiliary[0];
    *auxiliary_y = output.auxiliary[1];
    *auxiliary_z = output.auxiliary[2];
    *solver_cost = output.solver_cost;
    *solver_iterations = (double)output.solver_iterations;
    *saturated = (double)output.saturated;
    *status_code = (double)output.status_code;
}
