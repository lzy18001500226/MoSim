#ifndef MOSIM_MWORKS_LIVE_RT1_BRIDGE_H
#define MOSIM_MWORKS_LIVE_RT1_BRIDGE_H

#ifndef _WIN32
#error "The RT1 bridge targets the Windows-hosted MWORKS runtime."
#endif

#include <math.h>
#include <stdint.h>
#include <string.h>
#include <winsock2.h>
#include <windows.h>

#define MOSIM_RT1_STATE_MAGIC 0x4D525431u
#define MOSIM_RT1_COMMAND_MAGIC 0x4D524331u
#define MOSIM_RT1_VERSION 1u
#define MOSIM_RT1_PORT 49020u
#define MOSIM_RT1_RUN_ID_SIZE 64u
#define MOSIM_RT1_MAX_DRAIN 512
#define MOSIM_RT1_FLAG_ARMED (1u << 0)
#define MOSIM_RT1_FLAG_STATE_VALID (1u << 1)
#define MOSIM_RT1_FLAG_REFERENCE_VALID (1u << 2)
#define MOSIM_RT1_FLAG_OUTPUT_VALID (1u << 3)

#if defined(_MSC_VER)
#define MOSIM_RT1_ISFINITE(value) _finite(value)
#else
#define MOSIM_RT1_ISFINITE(value) isfinite(value)
#endif

#pragma pack(push, 1)
typedef struct MosimRt1Header {
    uint32_t magic;
    uint16_t version;
    uint16_t flags;
    uint32_t sequence;
    uint32_t related_sequence;
    uint64_t source_stamp_ns;
    uint64_t produced_or_receive_monotonic_ns;
    uint64_t valid_until_ns;
    char run_id[MOSIM_RT1_RUN_ID_SIZE];
} MosimRt1Header;

typedef struct MosimRt1StateReference {
    MosimRt1Header header;
    double values[24];
} MosimRt1StateReference;

typedef struct MosimRt1Command {
    MosimRt1Header header;
    double qx;
    double qy;
    double qz;
    double qw;
    double collective_thrust_n;
    uint32_t saturation_mask;
    uint32_t controller_status;
} MosimRt1Command;
#pragma pack(pop)

static SOCKET mosim_rt1_socket = INVALID_SOCKET;
static int mosim_rt1_initialized = 0;
static LARGE_INTEGER mosim_rt1_counter_frequency;
static struct sockaddr_in mosim_rt1_peer;
static int mosim_rt1_peer_size = 0;
static MosimRt1StateReference mosim_rt1_latest;
static uint32_t mosim_rt1_command_sequence = 0u;
static int mosim_rt1_socket_init_status = 0;
static int mosim_rt1_socket_error_code = 0;
static int mosim_rt1_socket_local_port = 0;
static int mosim_rt1_last_receive_datagrams = 0;
static int mosim_rt1_last_receive_rejected = 0;
static int mosim_rt1_last_receive_bytes = 0;
static int mosim_rt1_last_receive_error = 0;

static uint64_t mosim_rt1_monotonic_ns(void) {
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    return (uint64_t)((counter.QuadPart * 1000000000ULL) /
                      (uint64_t)mosim_rt1_counter_frequency.QuadPart);
}

static int mosim_rt1_initialize(void) {
    WSADATA data;
    struct sockaddr_in address;
    u_long nonblocking = 1;

    if (mosim_rt1_initialized) {
        return mosim_rt1_socket != INVALID_SOCKET;
    }
    mosim_rt1_initialized = 1;
    mosim_rt1_socket_init_status = 10;
    mosim_rt1_socket_error_code = 0;
    mosim_rt1_socket_local_port = 0;
    QueryPerformanceFrequency(&mosim_rt1_counter_frequency);
    mosim_rt1_socket_error_code = WSAStartup(MAKEWORD(2, 2), &data);
    if (mosim_rt1_socket_error_code != 0) {
        return 0;
    }
    mosim_rt1_socket_init_status = 20;
    mosim_rt1_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (mosim_rt1_socket == INVALID_SOCKET) {
        mosim_rt1_socket_error_code = WSAGetLastError();
        return 0;
    }
    mosim_rt1_socket_init_status = 30;
    if (ioctlsocket(mosim_rt1_socket, FIONBIO, &nonblocking) != 0) {
        mosim_rt1_socket_error_code = WSAGetLastError();
        closesocket(mosim_rt1_socket);
        mosim_rt1_socket = INVALID_SOCKET;
        return 0;
    }
    mosim_rt1_socket_init_status = 40;
    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_ANY);
    address.sin_port = htons((u_short)MOSIM_RT1_PORT);
    if (bind(mosim_rt1_socket, (struct sockaddr *)&address, sizeof(address)) != 0) {
        mosim_rt1_socket_error_code = WSAGetLastError();
        closesocket(mosim_rt1_socket);
        mosim_rt1_socket = INVALID_SOCKET;
        return 0;
    }
    mosim_rt1_socket_init_status = 50;
    mosim_rt1_socket_error_code = 0;
    mosim_rt1_socket_local_port = (int)MOSIM_RT1_PORT;
    memset(&mosim_rt1_latest, 0, sizeof(mosim_rt1_latest));
    return 1;
}

static int mosim_mworks_live_rt1_receive(
    int *sequence,
    double *source_stamp_ns,
    double *adapter_receive_monotonic_ns,
    int *armed,
    int *frame_valid,
    double *values) {
    int processed = 0;
    int index;

    mosim_rt1_last_receive_datagrams = 0;
    mosim_rt1_last_receive_rejected = 0;
    mosim_rt1_last_receive_bytes = 0;
    mosim_rt1_last_receive_error = 0;
    *sequence = -1;
    *source_stamp_ns = 0.0;
    *adapter_receive_monotonic_ns = 0.0;
    *armed = 0;
    *frame_valid = 0;
    for (index = 0; index < 24; ++index) {
        values[index] = 0.0;
    }
    if (!mosim_rt1_initialize()) {
        mosim_rt1_last_receive_error = mosim_rt1_socket_error_code;
        return -1;
    }
    for (index = 0; index < MOSIM_RT1_MAX_DRAIN; ++index) {
        MosimRt1StateReference candidate;
        struct sockaddr_in peer;
        int peer_size = (int)sizeof(peer);
        int received = recvfrom(
            mosim_rt1_socket,
            (char *)&candidate,
            (int)sizeof(candidate),
            0,
            (struct sockaddr *)&peer,
            &peer_size);
        if (received == SOCKET_ERROR) {
            int error = WSAGetLastError();
            if (error == WSAEWOULDBLOCK) {
                break;
            }
            mosim_rt1_last_receive_error = error;
            return -2;
        }
        ++mosim_rt1_last_receive_datagrams;
        mosim_rt1_last_receive_bytes = received;
        if (received != (int)sizeof(candidate) ||
            candidate.header.magic != MOSIM_RT1_STATE_MAGIC ||
            candidate.header.version != MOSIM_RT1_VERSION) {
            ++mosim_rt1_last_receive_rejected;
            continue;
        }
        mosim_rt1_latest = candidate;
        mosim_rt1_peer = peer;
        mosim_rt1_peer_size = peer_size;
        ++processed;
    }
    if (processed <= 0) {
        return 0;
    }
    *sequence = (int)mosim_rt1_latest.header.sequence;
    *source_stamp_ns = (double)mosim_rt1_latest.header.source_stamp_ns;
    *adapter_receive_monotonic_ns =
        (double)mosim_rt1_latest.header.produced_or_receive_monotonic_ns;
    *armed = (mosim_rt1_latest.header.flags & MOSIM_RT1_FLAG_ARMED) != 0u;
    *frame_valid =
        (mosim_rt1_latest.header.flags & MOSIM_RT1_FLAG_STATE_VALID) != 0u &&
        (mosim_rt1_latest.header.flags & MOSIM_RT1_FLAG_REFERENCE_VALID) != 0u;
    for (index = 0; index < 24; ++index) {
        values[index] = mosim_rt1_latest.values[index];
        if (!MOSIM_RT1_ISFINITE(values[index])) {
            *frame_valid = 0;
        }
    }
    return processed;
}

static int mosim_mworks_live_rt1_send(
    int state_sequence,
    double adapter_receive_monotonic_ns,
    double qx,
    double qy,
    double qz,
    double qw,
    double collective_thrust_n,
    int saturation_mask,
    int controller_status,
    int output_valid) {
    MosimRt1Command command;
    uint64_t adapter_stamp;
    int valid;

    if (!mosim_rt1_initialize() || mosim_rt1_peer_size <= 0) {
        return -1;
    }
    adapter_stamp = (uint64_t)adapter_receive_monotonic_ns;
    valid = output_valid &&
        MOSIM_RT1_ISFINITE(qx) && MOSIM_RT1_ISFINITE(qy) &&
        MOSIM_RT1_ISFINITE(qz) && MOSIM_RT1_ISFINITE(qw) &&
        MOSIM_RT1_ISFINITE(collective_thrust_n) && collective_thrust_n > 0.0;
    memset(&command, 0, sizeof(command));
    command.header.magic = MOSIM_RT1_COMMAND_MAGIC;
    command.header.version = MOSIM_RT1_VERSION;
    command.header.flags = valid ? MOSIM_RT1_FLAG_OUTPUT_VALID : 0u;
    command.header.sequence = mosim_rt1_command_sequence++;
    command.header.related_sequence = (uint32_t)state_sequence;
    command.header.source_stamp_ns = adapter_stamp;
    command.header.produced_or_receive_monotonic_ns = mosim_rt1_monotonic_ns();
    command.header.valid_until_ns = adapter_stamp + 50000000ULL;
    memcpy(command.header.run_id, mosim_rt1_latest.header.run_id, MOSIM_RT1_RUN_ID_SIZE);
    command.qx = qx;
    command.qy = qy;
    command.qz = qz;
    command.qw = qw;
    command.collective_thrust_n = collective_thrust_n;
    command.saturation_mask = (uint32_t)saturation_mask;
    command.controller_status = (uint32_t)controller_status;
    return sendto(
        mosim_rt1_socket,
        (const char *)&command,
        (int)sizeof(command),
        0,
        (const struct sockaddr *)&mosim_rt1_peer,
        mosim_rt1_peer_size) == (int)sizeof(command) ? 1 : -2;
}

static int mosim_mworks_live_rt1_socket_status(
    int *socket_init_status,
    int *socket_error_code,
    int *socket_local_port) {
    *socket_init_status = mosim_rt1_socket_init_status;
    *socket_error_code = mosim_rt1_socket_error_code;
    *socket_local_port = mosim_rt1_socket_local_port;
    return mosim_rt1_socket != INVALID_SOCKET ? 1 : 0;
}

#endif
