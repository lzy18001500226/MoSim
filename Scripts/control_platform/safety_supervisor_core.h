#ifndef MOSIM_SAFETY_SUPERVISOR_CORE_H
#define MOSIM_SAFETY_SUPERVISOR_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

enum {
    MOSIM_SAFETY_FILTER = 1,
    MOSIM_SAFETY_CBF = 2,
    MOSIM_SAFETY_REFERENCE_GOVERNOR = 3,
    MOSIM_SAFETY_GEOFENCE = 4,
    MOSIM_SAFETY_EMERGENCY_STOP = 5,
    MOSIM_SAFETY_RETURN_AND_LAND = 6,
    MOSIM_SAFETY_FAILSAFE = 7
};

enum {
    MOSIM_SAFETY_ACTION_PASS = 0,
    MOSIM_SAFETY_ACTION_MODIFY = 1,
    MOSIM_SAFETY_ACTION_HOLD = 2,
    MOSIM_SAFETY_ACTION_RETURN = 3,
    MOSIM_SAFETY_ACTION_LAND = 4,
    MOSIM_SAFETY_ACTION_STOP = 5
};

enum {
    MOSIM_SAFETY_STATE_NOMINAL = 0,
    MOSIM_SAFETY_STATE_HOLD = 1,
    MOSIM_SAFETY_STATE_RETURN = 2,
    MOSIM_SAFETY_STATE_LAND = 3,
    MOSIM_SAFETY_STATE_STOP = 4
};

typedef struct {
    double max_acceleration[3];
    double max_speed[3];
    double max_tilt_rad;
    double min_thrust;
    double max_thrust;
    double geofence_min[3];
    double geofence_max[3];
    double geofence_margin;
    double cbf_alpha;
    double obstacle_min_distance;
    double governor_rate[3];
    double command_timeout_s;
    double return_altitude;
    double land_speed;
} MosimSafetyParams;

typedef struct {
    int state;
    double governed_reference[3];
} MosimSafetyState;

typedef struct {
    double dt;
    double position[3];
    double velocity[3];
    double candidate_acceleration[3];
    double candidate_thrust;
    double candidate_tilt_rad;
    double reference_position[3];
    double home_position[3];
    double obstacle_distance;
    double command_age_s;
    int state_valid;
    int offboard_valid;
    int emergency_request;
    int return_request;
    int land_request;
    int enable;
    int reset;
} MosimSafetyInput;

typedef struct {
    double safe_acceleration[3];
    double safe_thrust;
    double safe_reference[3];
    int action;
    int state;
    unsigned int active_constraints;
    int modified;
    int status_code;
} MosimSafetyOutput;

void mosim_safety_default_params(MosimSafetyParams *params);
void mosim_safety_reset(MosimSafetyState *state);
int mosim_safety_step(int mode, const MosimSafetyParams *params,
                      MosimSafetyState *state, const MosimSafetyInput *input,
                      MosimSafetyOutput *output);

#ifdef __cplusplus
}
#endif

#endif
