#ifndef MOSIM_MWORKS_LIVE_RT0_BRIDGE_H
#define MOSIM_MWORKS_LIVE_RT0_BRIDGE_H

#ifndef _WIN32
#error "The RT0 bridge currently targets the Windows-hosted MWORKS runtime."
#endif

#include <math.h>
#include <stdint.h>
#include <string.h>
#include <winsock2.h>
#include <windows.h>

#define MOSIM_RT0_REQUEST_MAGIC 0x4D525451u
#define MOSIM_RT0_RESPONSE_MAGIC 0x4D525452u
#define MOSIM_RT0_VERSION 1u
#define MOSIM_RT0_PORT 49010u
#define MOSIM_RT0_MAX_DRAIN 16

#if defined(_MSC_VER)
#define MOSIM_RT0_ISFINITE(value) _finite(value)
#else
#define MOSIM_RT0_ISFINITE(value) isfinite(value)
#endif

#pragma pack(push, 1)
typedef struct MosimRt0Request {
    uint32_t magic;
    uint16_t version;
    uint16_t reserved;
    uint32_t sequence;
    uint64_t source_stamp_ns;
    uint64_t input_sent_monotonic_ns;
    double position_x_m;
    double velocity_x_mps;
    double reference_x_m;
    double reference_velocity_x_mps;
} MosimRt0Request;

typedef struct MosimRt0Response {
    uint32_t magic;
    uint16_t version;
    uint16_t status;
    uint32_t sequence;
    uint64_t source_stamp_ns;
    uint64_t compute_started_monotonic_ns;
    uint64_t compute_finished_monotonic_ns;
    double desired_qz;
    double desired_qw;
    double collective_thrust_n;
    double controller_output;
    int32_t output_valid;
} MosimRt0Response;
#pragma pack(pop)

static SOCKET mosim_rt0_socket = INVALID_SOCKET;
static int mosim_rt0_initialized = 0;
static LARGE_INTEGER mosim_rt0_counter_frequency;

static uint64_t mosim_rt0_monotonic_ns(void) {
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    return (uint64_t)((counter.QuadPart * 1000000000ULL) /
                      (uint64_t)mosim_rt0_counter_frequency.QuadPart);
}

static int mosim_rt0_initialize(void) {
    WSADATA data;
    struct sockaddr_in address;
    u_long nonblocking = 1;

    if (mosim_rt0_initialized) {
        return mosim_rt0_socket != INVALID_SOCKET;
    }
    mosim_rt0_initialized = 1;
    QueryPerformanceFrequency(&mosim_rt0_counter_frequency);
    if (WSAStartup(MAKEWORD(2, 2), &data) != 0) {
        return 0;
    }
    mosim_rt0_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (mosim_rt0_socket == INVALID_SOCKET) {
        return 0;
    }
    if (ioctlsocket(mosim_rt0_socket, FIONBIO, &nonblocking) != 0) {
        closesocket(mosim_rt0_socket);
        mosim_rt0_socket = INVALID_SOCKET;
        return 0;
    }
    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = htons((u_short)MOSIM_RT0_PORT);
    if (bind(mosim_rt0_socket, (struct sockaddr *)&address, sizeof(address)) != 0) {
        closesocket(mosim_rt0_socket);
        mosim_rt0_socket = INVALID_SOCKET;
        return 0;
    }
    return 1;
}

static int mosim_mworks_live_rt0_exchange(
    double simulation_time,
    int *last_sequence,
    double *source_stamp_ns,
    double *compute_started_ns,
    double *compute_finished_ns,
    double *desired_qz,
    double *desired_qw,
    double *collective_thrust_n,
    int *output_valid) {
    int processed = 0;
    int index;

    (void)simulation_time;
    *output_valid = 0;
    if (!mosim_rt0_initialize()) {
        return -1;
    }

    for (index = 0; index < MOSIM_RT0_MAX_DRAIN; ++index) {
        MosimRt0Request request;
        MosimRt0Response response;
        struct sockaddr_in peer;
        int peer_size = (int)sizeof(peer);
        int received = recvfrom(
            mosim_rt0_socket,
            (char *)&request,
            (int)sizeof(request),
            0,
            (struct sockaddr *)&peer,
            &peer_size);
        uint64_t compute_started;
        uint64_t compute_finished;
        double position_error;
        double velocity_error;
        double controller_output;
        double yaw;

        if (received == SOCKET_ERROR) {
            int error = WSAGetLastError();
            if (error == WSAEWOULDBLOCK) {
                break;
            }
            return -2;
        }
        if (received != (int)sizeof(request) ||
            request.magic != MOSIM_RT0_REQUEST_MAGIC ||
            request.version != MOSIM_RT0_VERSION) {
            continue;
        }

        compute_started = mosim_rt0_monotonic_ns();
        position_error = request.reference_x_m - request.position_x_m;
        velocity_error = request.reference_velocity_x_mps - request.velocity_x_mps;
        controller_output = 1.2 * position_error + 0.35 * velocity_error;
        yaw = 0.02 * controller_output;
        *desired_qz = sin(0.5 * yaw);
        *desired_qw = cos(0.5 * yaw);
        *collective_thrust_n = 14.715 + controller_output;
        *output_valid =
            MOSIM_RT0_ISFINITE(*desired_qz) && MOSIM_RT0_ISFINITE(*desired_qw) &&
            MOSIM_RT0_ISFINITE(*collective_thrust_n) && *collective_thrust_n > 0.0;
        compute_finished = mosim_rt0_monotonic_ns();

        memset(&response, 0, sizeof(response));
        response.magic = MOSIM_RT0_RESPONSE_MAGIC;
        response.version = MOSIM_RT0_VERSION;
        response.status = *output_valid ? 0u : 1u;
        response.sequence = request.sequence;
        response.source_stamp_ns = request.source_stamp_ns;
        response.compute_started_monotonic_ns = compute_started;
        response.compute_finished_monotonic_ns = compute_finished;
        response.desired_qz = *desired_qz;
        response.desired_qw = *desired_qw;
        response.collective_thrust_n = *collective_thrust_n;
        response.controller_output = controller_output;
        response.output_valid = *output_valid;
        sendto(
            mosim_rt0_socket,
            (const char *)&response,
            (int)sizeof(response),
            0,
            (const struct sockaddr *)&peer,
            peer_size);

        *last_sequence = (int)request.sequence;
        *source_stamp_ns = (double)request.source_stamp_ns;
        *compute_started_ns = (double)compute_started;
        *compute_finished_ns = (double)compute_finished;
        ++processed;
    }
    return processed;
}

#endif
