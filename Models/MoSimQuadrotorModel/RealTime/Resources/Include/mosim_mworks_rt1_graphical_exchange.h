#ifndef MOSIM_MWORKS_RT1_GRAPHICAL_EXCHANGE_H
#define MOSIM_MWORKS_RT1_GRAPHICAL_EXCHANGE_H

#include "mosim_mworks_live_rt1_bridge.h"

/* Keep the production RT1 transport state in one generated C translation unit. */
static int mosim_rt1_graphical_exchange_call_count = 0;

static int mosim_mworks_rt1_graphical_exchange(
    int send_requested,
    int command_state_sequence,
    double command_adapter_receive_monotonic_ns,
    double command_qx,
    double command_qy,
    double command_qz,
    double command_qw,
    double command_collective_thrust_n,
    int command_saturation_mask,
    int command_controller_status,
    int command_output_valid,
    int transport_pace_ms,
    int *exchange_call_count,
    int *send_status,
    int *socket_ready,
    int *socket_init_status,
    int *socket_error_code,
    int *socket_local_port,
    int *received_datagrams,
    int *rejected_datagrams,
    int *last_received_bytes,
    int *receive_error_code,
    int *state_sequence,
    double *source_stamp_ns,
    double *adapter_receive_monotonic_ns,
    int *armed,
    int *frame_valid,
    double *values) {
    int processed;

    ++mosim_rt1_graphical_exchange_call_count;
    *exchange_call_count = mosim_rt1_graphical_exchange_call_count;
    *send_status = 0;
    if (transport_pace_ms > 0) {
        Sleep((DWORD)transport_pace_ms);
    }
    processed = mosim_mworks_live_rt1_receive(
        state_sequence,
        source_stamp_ns,
        adapter_receive_monotonic_ns,
        armed,
        frame_valid,
        values);
    *received_datagrams = mosim_rt1_last_receive_datagrams;
    *rejected_datagrams = mosim_rt1_last_receive_rejected;
    *last_received_bytes = mosim_rt1_last_receive_bytes;
    *receive_error_code = mosim_rt1_last_receive_error;
    if (send_requested && command_state_sequence >= 0) {
        *send_status = mosim_mworks_live_rt1_send(
            command_state_sequence,
            command_adapter_receive_monotonic_ns,
            command_qx,
            command_qy,
            command_qz,
            command_qw,
            command_collective_thrust_n,
            command_saturation_mask,
            command_controller_status,
            command_output_valid);
    }
    *socket_ready = mosim_mworks_live_rt1_socket_status(
        socket_init_status, socket_error_code, socket_local_port);
    return processed;
}

#endif
