#include "MoSim_Classic_CFunction_Sysblock.h"
/*** Current Block Name: cFunction ***/
#define MOSIM_CLASSIC_FOPID_MEMORY 16

enum MosimClassicControllerId {
    MOSIM_CLASSIC_POLE_PLACEMENT_LUENBERGER = 1,
    MOSIM_CLASSIC_MRAC = 2,
    MOSIM_CLASSIC_NDI = 3,
    MOSIM_CLASSIC_FOPID = 4,
    MOSIM_CLASSIC_H2_STATE_FEEDBACK = 5
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
} MosimClassicInput;

typedef struct {
    double pole_position_gain[3];
    double pole_velocity_gain[3];
    double observer_position_gain[3];
    double observer_velocity_gain[3];
    double mrac_reference_omega[3];
    double mrac_reference_zeta[3];
    double mrac_position_gain[3];
    double mrac_velocity_gain[3];
    double mrac_adaptation_gain[3];
    double mrac_parameter_limit[3];
    double ndi_position_gain[3];
    double ndi_velocity_gain[3];
    double ndi_linear_drag[3];
    double fopid_kp[3];
    double fopid_ki[3];
    double fopid_kd[3];
    double fopid_lambda;
    double fopid_mu;
    double h2_position_gain[3];
    double h2_velocity_gain[3];
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimClassicParams;

typedef struct {
    double observer_position[3];
    double observer_velocity[3];
    double previous_virtual_acceleration[3];
    int observer_initialized;
    double reference_model_position[3];
    double reference_model_velocity[3];
    double mrac_position_delta[3];
    double mrac_velocity_delta[3];
    int reference_model_initialized;
    double fopid_error_history[3][MOSIM_CLASSIC_FOPID_MEMORY];
    int fopid_sample_count;
} MosimClassicState;

typedef struct {
    double desired_acceleration[3];
    double desired_attitude_wxyz[4];
    double normalized_thrust;
    double collective_thrust_n;
    double observer_position[3];
    double observer_velocity[3];
    double reference_model_position[3];
    double reference_model_velocity[3];
    double adaptive_position_delta[3];
    double adaptive_velocity_delta[3];
    double fractional_integral[3];
    double fractional_derivative[3];
    int saturated;
    int status_code;
} MosimClassicOutput;

void mosim_classic_default_params(MosimClassicParams *params);
void mosim_classic_reset(MosimClassicState *state);
int mosim_classic_step(
    int controller_id,
    const MosimClassicParams *params,
    MosimClassicState *state,
    const MosimClassicInput *input,
    MosimClassicOutput *output);





#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static int finite3(const double value[3])
{
    return isfinite(value[0]) && isfinite(value[1]) && isfinite(value[2]);
}

static double norm3(const double value[3])
{
    return sqrt(value[0] * value[0] + value[1] * value[1] + value[2] * value[2]);
}

static void cross3(const double a[3], const double b[3], double output[3])
{
    output[0] = a[1] * b[2] - a[2] * b[1];
    output[1] = a[2] * b[0] - a[0] * b[2];
    output[2] = a[0] * b[1] - a[1] * b[0];
}

static int normalize3(double value[3])
{
    const double length = norm3(value);
    int axis;
    if (length <= 1.0e-12) return -1;
    for (axis = 0; axis < 3; ++axis) value[axis] /= length;
    return 0;
}

static void quaternion_from_rotation(const double rotation[3][3], double q[4])
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

static int params_valid(const MosimClassicParams *params)
{
    int axis;
    if (!isfinite(params->mass_kg) || params->mass_kg <= 0.0 ||
        !isfinite(params->gravity_mps2) || params->gravity_mps2 <= 0.0 ||
        !isfinite(params->hover_percentage) || params->hover_percentage <= 0.0 ||
        params->hover_percentage > 1.0 ||
        !isfinite(params->fopid_lambda) || params->fopid_lambda <= 0.0 || params->fopid_lambda > 1.0 ||
        !isfinite(params->fopid_mu) || params->fopid_mu <= 0.0 || params->fopid_mu > 1.0 ||
        !isfinite(params->max_tilt_rad) || params->max_tilt_rad <= 0.0 ||
        params->max_tilt_rad >= 1.5707963267948966 ||
        params->min_collective_thrust_n < 0.0 ||
        params->max_collective_thrust_n <= params->min_collective_thrust_n) return 0;
    for (axis = 0; axis < 3; ++axis) {
        if (params->pole_position_gain[axis] < 0.0 || params->pole_velocity_gain[axis] < 0.0 ||
            params->observer_position_gain[axis] < 0.0 || params->observer_velocity_gain[axis] < 0.0 ||
            params->mrac_reference_omega[axis] <= 0.0 || params->mrac_reference_zeta[axis] <= 0.0 ||
            params->mrac_adaptation_gain[axis] < 0.0 || params->mrac_parameter_limit[axis] < 0.0 ||
            params->ndi_position_gain[axis] < 0.0 || params->ndi_velocity_gain[axis] < 0.0 ||
            params->ndi_linear_drag[axis] < 0.0 || params->fopid_kp[axis] < 0.0 ||
            params->fopid_ki[axis] < 0.0 || params->fopid_kd[axis] < 0.0 ||
            params->h2_position_gain[axis] < 0.0 || params->h2_velocity_gain[axis] < 0.0) return 0;
    }
    return 1;
}

static int command_from_acceleration(
    const MosimClassicParams *params,
    const MosimClassicInput *input,
    MosimClassicOutput *output)
{
    double force[3];
    double b1_reference[3];
    double b1[3];
    double b2[3];
    double b3[3];
    double rotation[3][3];
    double force_norm;
    double horizontal;
    double horizontal_limit;
    int axis;

    horizontal = hypot(output->desired_acceleration[0], output->desired_acceleration[1]);
    horizontal_limit = fmax(0.0, output->desired_acceleration[2]) * tan(params->max_tilt_rad);
    if (horizontal > horizontal_limit && horizontal > 1.0e-12) {
        const double scale = horizontal_limit / horizontal;
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
    output->collective_thrust_n = clamp_value(
        force_norm, params->min_collective_thrust_n, params->max_collective_thrust_n);
    if (fabs(output->collective_thrust_n - force_norm) > 1.0e-12) output->saturated = 1;
    output->normalized_thrust = clamp_value(
        output->collective_thrust_n /
            (params->mass_kg * params->gravity_mps2 / params->hover_percentage),
        0.0, 1.0);
    return 0;
}

void mosim_classic_default_params(MosimClassicParams *params)
{
    const MosimClassicParams defaults = {
        {9.0, 9.0, 6.25}, {6.0, 6.0, 5.0},
        {8.0, 8.0, 9.0}, {16.0, 16.0, 20.25},
        {2.2, 2.2, 2.5}, {0.85, 0.85, 0.90},
        {6.0, 6.0, 4.5}, {4.5, 4.5, 4.0},
        {0.08, 0.08, 0.10}, {1.5, 1.5, 1.5},
        {8.0, 8.0, 5.0}, {5.0, 5.0, 4.0}, {0.12, 0.12, 0.18},
        {6.5, 6.5, 4.5}, {0.8, 0.8, 0.7}, {1.2, 1.2, 1.0},
        0.85, 0.65,
        {7.4, 7.4, 5.3}, {4.9, 4.9, 4.2},
        0.67, 9.80665, 0.291, 0.5235987755982988, 0.0, 16.0
    };
    if (params != NULL) *params = defaults;
}

void mosim_classic_reset(MosimClassicState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

static void pole_placement_step(
    const MosimClassicParams *params,
    MosimClassicState *state,
    const MosimClassicInput *input,
    MosimClassicOutput *output)
{
    int axis;
    if (!state->observer_initialized) {
        memcpy(state->observer_position, input->position, sizeof(state->observer_position));
        memcpy(state->observer_velocity, input->velocity, sizeof(state->observer_velocity));
        state->observer_initialized = 1;
    }
    for (axis = 0; axis < 3; ++axis) {
        const double residual = input->position[axis] - state->observer_position[axis];
        const double position_dot = state->observer_velocity[axis] +
            params->observer_position_gain[axis] * residual;
        const double velocity_dot = state->previous_virtual_acceleration[axis] +
            params->observer_velocity_gain[axis] * residual;
        state->observer_position[axis] += input->dt * position_dot;
        state->observer_velocity[axis] += input->dt * velocity_dot;
        output->desired_acceleration[axis] = input->reference_acceleration[axis] +
            params->pole_position_gain[axis] *
                (input->reference_position[axis] - state->observer_position[axis]) +
            params->pole_velocity_gain[axis] *
                (input->reference_velocity[axis] - state->observer_velocity[axis]);
        state->previous_virtual_acceleration[axis] = output->desired_acceleration[axis];
        output->observer_position[axis] = state->observer_position[axis];
        output->observer_velocity[axis] = state->observer_velocity[axis];
    }
}

static void mrac_step(
    const MosimClassicParams *params,
    MosimClassicState *state,
    const MosimClassicInput *input,
    MosimClassicOutput *output)
{
    int axis;
    if (!state->reference_model_initialized) {
        memcpy(state->reference_model_position, input->position, sizeof(state->reference_model_position));
        memcpy(state->reference_model_velocity, input->velocity, sizeof(state->reference_model_velocity));
        state->reference_model_initialized = 1;
    }
    for (axis = 0; axis < 3; ++axis) {
        const double omega = params->mrac_reference_omega[axis];
        const double model_acceleration = omega * omega *
            (input->reference_position[axis] - state->reference_model_position[axis]) -
            2.0 * params->mrac_reference_zeta[axis] * omega *
            (state->reference_model_velocity[axis] - input->reference_velocity[axis]) +
            input->reference_acceleration[axis];
        double position_error;
        double velocity_error;
        double sliding;
        state->reference_model_position[axis] +=
            input->dt * state->reference_model_velocity[axis];
        state->reference_model_velocity[axis] += input->dt * model_acceleration;
        position_error = state->reference_model_position[axis] - input->position[axis];
        velocity_error = state->reference_model_velocity[axis] - input->velocity[axis];
        sliding = velocity_error + 0.5 * params->mrac_position_gain[axis] * position_error;
        state->mrac_position_delta[axis] = clamp_value(
            state->mrac_position_delta[axis] + input->dt * params->mrac_adaptation_gain[axis] *
                sliding * position_error,
            -params->mrac_parameter_limit[axis], params->mrac_parameter_limit[axis]);
        state->mrac_velocity_delta[axis] = clamp_value(
            state->mrac_velocity_delta[axis] + input->dt * params->mrac_adaptation_gain[axis] *
                sliding * velocity_error,
            -params->mrac_parameter_limit[axis], params->mrac_parameter_limit[axis]);
        output->desired_acceleration[axis] = model_acceleration +
            (params->mrac_position_gain[axis] + state->mrac_position_delta[axis]) * position_error +
            (params->mrac_velocity_gain[axis] + state->mrac_velocity_delta[axis]) * velocity_error;
        output->reference_model_position[axis] = state->reference_model_position[axis];
        output->reference_model_velocity[axis] = state->reference_model_velocity[axis];
        output->adaptive_position_delta[axis] = state->mrac_position_delta[axis];
        output->adaptive_velocity_delta[axis] = state->mrac_velocity_delta[axis];
    }
}

static void ndi_step(
    const MosimClassicParams *params,
    const MosimClassicInput *input,
    MosimClassicOutput *output)
{
    int axis;
    for (axis = 0; axis < 3; ++axis) {
        const double virtual_acceleration = input->reference_acceleration[axis] +
            params->ndi_position_gain[axis] *
                (input->reference_position[axis] - input->position[axis]) +
            params->ndi_velocity_gain[axis] *
                (input->reference_velocity[axis] - input->velocity[axis]);
        output->desired_acceleration[axis] = virtual_acceleration +
            params->ndi_linear_drag[axis] * input->velocity[axis] / params->mass_kg;
    }
}

static double fractional_gl(
    const double history[MOSIM_CLASSIC_FOPID_MEMORY],
    int sample_count,
    double alpha,
    double dt)
{
    const int count = sample_count < MOSIM_CLASSIC_FOPID_MEMORY ?
        sample_count : MOSIM_CLASSIC_FOPID_MEMORY;
    double coefficient = 1.0;
    double sum = 0.0;
    int index;
    for (index = 0; index < count; ++index) {
        if (index > 0) coefficient *= -((alpha - (double)index + 1.0) / (double)index);
        sum += coefficient * history[index];
    }
    return pow(dt, -alpha) * sum;
}

static void fopid_step(
    const MosimClassicParams *params,
    MosimClassicState *state,
    const MosimClassicInput *input,
    MosimClassicOutput *output)
{
    int axis;
    int index;
    for (axis = 0; axis < 3; ++axis) {
        const double error = input->reference_position[axis] - input->position[axis];
        for (index = MOSIM_CLASSIC_FOPID_MEMORY - 1; index > 0; --index) {
            state->fopid_error_history[axis][index] = state->fopid_error_history[axis][index - 1];
        }
        state->fopid_error_history[axis][0] = error;
    }
    if (state->fopid_sample_count < MOSIM_CLASSIC_FOPID_MEMORY) ++state->fopid_sample_count;
    for (axis = 0; axis < 3; ++axis) {
        const double integral = fractional_gl(
            state->fopid_error_history[axis], state->fopid_sample_count,
            -params->fopid_lambda, input->dt);
        const double derivative = fractional_gl(
            state->fopid_error_history[axis], state->fopid_sample_count,
            params->fopid_mu, input->dt);
        output->fractional_integral[axis] = integral;
        output->fractional_derivative[axis] = derivative;
        output->desired_acceleration[axis] = input->reference_acceleration[axis] +
            params->fopid_kp[axis] * state->fopid_error_history[axis][0] +
            params->fopid_ki[axis] * integral + params->fopid_kd[axis] * derivative;
    }
}

static void h2_step(
    const MosimClassicParams *params,
    const MosimClassicInput *input,
    MosimClassicOutput *output)
{
    int axis;
    for (axis = 0; axis < 3; ++axis) {
        output->desired_acceleration[axis] = input->reference_acceleration[axis] +
            params->h2_position_gain[axis] *
                (input->reference_position[axis] - input->position[axis]) +
            params->h2_velocity_gain[axis] *
                (input->reference_velocity[axis] - input->velocity[axis]);
    }
}

int mosim_classic_step(
    int controller_id,
    const MosimClassicParams *params,
    MosimClassicState *state,
    const MosimClassicInput *input,
    MosimClassicOutput *output)
{
    int rc;
    if (params == NULL || state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_wxyz[0] = 1.0;
    if (input->reset) mosim_classic_reset(state);
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

    if (controller_id == MOSIM_CLASSIC_POLE_PLACEMENT_LUENBERGER) {
        pole_placement_step(params, state, input, output);
    } else if (controller_id == MOSIM_CLASSIC_MRAC) {
        mrac_step(params, state, input, output);
    } else if (controller_id == MOSIM_CLASSIC_NDI) {
        ndi_step(params, input, output);
    } else if (controller_id == MOSIM_CLASSIC_FOPID) {
        fopid_step(params, state, input, output);
    } else if (controller_id == MOSIM_CLASSIC_H2_STATE_FEEDBACK) {
        h2_step(params, input, output);
    } else {
        output->status_code = -2;
        return -2;
    }

    output->desired_acceleration[2] += params->gravity_mps2;
    rc = command_from_acceleration(params, input, output);
    if (rc != 0) {
        output->status_code = rc;
        return rc;
    }
    output->status_code = 0;
    return 0;
}

void MosimClassicStepScalar(
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
    double enable,
    double reset,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *observer_position_x,
    double *observer_position_y,
    double *observer_position_z,
    double *observer_velocity_x,
    double *observer_velocity_y,
    double *observer_velocity_z,
    double *reference_model_position_x,
    double *reference_model_position_y,
    double *reference_model_position_z,
    double *reference_model_velocity_x,
    double *reference_model_velocity_y,
    double *reference_model_velocity_z,
    double *adaptive_position_delta_x,
    double *adaptive_position_delta_y,
    double *adaptive_position_delta_z,
    double *adaptive_velocity_delta_x,
    double *adaptive_velocity_delta_y,
    double *adaptive_velocity_delta_z,
    double *fractional_integral_x,
    double *fractional_integral_y,
    double *fractional_integral_z,
    double *fractional_derivative_x,
    double *fractional_derivative_y,
    double *fractional_derivative_z,
    double *normalized_thrust,
    double *collective_thrust_n,
    double *saturated,
    double *status_code)
{
    static MosimClassicState states[6];
    static int initialized[6] = {0};
    MosimClassicParams params;
    MosimClassicInput in;
    MosimClassicOutput out;
    int id=(int)controller_id;
    mosim_classic_default_params(&params);
    memset(&in,0,sizeof(in));
    in.dt=dt;
    in.position[0]=position_x; in.position[1]=position_y; in.position[2]=position_z;
    in.velocity[0]=velocity_x; in.velocity[1]=velocity_y; in.velocity[2]=velocity_z;
    in.reference_position[0]=reference_position_x; in.reference_position[1]=reference_position_y; in.reference_position[2]=reference_position_z;
    in.reference_velocity[0]=reference_velocity_x; in.reference_velocity[1]=reference_velocity_y; in.reference_velocity[2]=reference_velocity_z;
    in.reference_acceleration[0]=reference_acceleration_x; in.reference_acceleration[1]=reference_acceleration_y; in.reference_acceleration[2]=reference_acceleration_z;
    in.reference_yaw=reference_yaw; in.enable=enable!=0.0; in.reset=reset!=0.0;
    if(id<1 || id>5) id=0;
    if(!initialized[id]) { mosim_classic_reset(&states[id]); initialized[id]=1; }
    mosim_classic_step(id,&params,&states[id],&in,&out);
    *desired_acceleration_x=out.desired_acceleration[0]; *desired_acceleration_y=out.desired_acceleration[1]; *desired_acceleration_z=out.desired_acceleration[2];
    *desired_attitude_w=out.desired_attitude_wxyz[0]; *desired_attitude_x=out.desired_attitude_wxyz[1]; *desired_attitude_y=out.desired_attitude_wxyz[2]; *desired_attitude_z=out.desired_attitude_wxyz[3];
    *normalized_thrust=out.normalized_thrust; *collective_thrust_n=out.collective_thrust_n;
    *observer_position_x=out.observer_position[0]; *observer_position_y=out.observer_position[1]; *observer_position_z=out.observer_position[2];
    *observer_velocity_x=out.observer_velocity[0]; *observer_velocity_y=out.observer_velocity[1]; *observer_velocity_z=out.observer_velocity[2];
    *reference_model_position_x=out.reference_model_position[0]; *reference_model_position_y=out.reference_model_position[1]; *reference_model_position_z=out.reference_model_position[2];
    *reference_model_velocity_x=out.reference_model_velocity[0]; *reference_model_velocity_y=out.reference_model_velocity[1]; *reference_model_velocity_z=out.reference_model_velocity[2];
    *adaptive_position_delta_x=out.adaptive_position_delta[0]; *adaptive_position_delta_y=out.adaptive_position_delta[1]; *adaptive_position_delta_z=out.adaptive_position_delta[2];
    *adaptive_velocity_delta_x=out.adaptive_velocity_delta[0]; *adaptive_velocity_delta_y=out.adaptive_velocity_delta[1]; *adaptive_velocity_delta_z=out.adaptive_velocity_delta[2];
    *fractional_integral_x=out.fractional_integral[0]; *fractional_integral_y=out.fractional_integral[1]; *fractional_integral_z=out.fractional_integral[2];
    *fractional_derivative_x=out.fractional_derivative[0]; *fractional_derivative_y=out.fractional_derivative[1]; *fractional_derivative_z=out.fractional_derivative[2];
    *saturated=(double)out.saturated; *status_code=(double)out.status_code;
}
