#ifndef MOSIM_MWORKS_LIVE_TELEMETRY_SCOPE_H
#define MOSIM_MWORKS_LIVE_TELEMETRY_SCOPE_H

#ifndef _WIN32
#error "The telemetry Scope bridge targets the Windows-hosted MWORKS runtime."
#endif

#include <math.h>
#include <stdint.h>
#include <string.h>
#include <winsock2.h>
#include <windows.h>

#define MOSIM_TS_MAGIC 0x4D545331u
#define MOSIM_TS_ACK_MAGIC 0x4D544131u
#define MOSIM_TS_VERSION 1u
#define MOSIM_TS_PORT 49020u
#define MOSIM_TS_RUN_ID_SIZE 64u
#define MOSIM_TS_VALUE_COUNT 32
#define MOSIM_TS_MAX_DRAIN 512

#if defined(_MSC_VER)
#define MOSIM_TS_ISFINITE(value) _finite(value)
#else
#define MOSIM_TS_ISFINITE(value) isfinite(value)
#endif

#pragma pack(push, 1)
typedef struct MosimTsHeader {
    uint32_t magic;
    uint16_t version;
    uint16_t flags;
    uint32_t sequence;
    uint32_t related_sequence;
    uint64_t source_stamp_ns;
    uint64_t produced_monotonic_ns;
    uint64_t valid_until_ns;
    char run_id[MOSIM_TS_RUN_ID_SIZE];
} MosimTsHeader;

typedef struct MosimTsFrame {
    MosimTsHeader header;
    double values[MOSIM_TS_VALUE_COUNT];
} MosimTsFrame;

typedef struct MosimTsAck {
    MosimTsHeader header;
    uint64_t echoed_sender_monotonic_ns;
} MosimTsAck;
#pragma pack(pop)

static SOCKET mosim_ts_socket = INVALID_SOCKET;
static int mosim_ts_initialized = 0;
static LARGE_INTEGER mosim_ts_counter_frequency;
static uint32_t mosim_ts_ack_sequence = 0u;
static int mosim_ts_socket_init_status = 0;
static int mosim_ts_socket_error_code = 0;
static MosimTsFrame mosim_ts_latest;

static uint64_t mosim_ts_monotonic_ns(void) {
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    return (uint64_t)((counter.QuadPart * 1000000000ULL) /
                      (uint64_t)mosim_ts_counter_frequency.QuadPart);
}

static int mosim_ts_initialize(void) {
    WSADATA data;
    struct sockaddr_in address;
    u_long nonblocking = 1;

    if (mosim_ts_initialized) {
        return mosim_ts_socket != INVALID_SOCKET;
    }
    mosim_ts_initialized = 1;
    mosim_ts_socket_init_status = 10;
    QueryPerformanceFrequency(&mosim_ts_counter_frequency);
    mosim_ts_socket_error_code = WSAStartup(MAKEWORD(2, 2), &data);
    if (mosim_ts_socket_error_code != 0) return 0;
    mosim_ts_socket_init_status = 20;
    mosim_ts_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (mosim_ts_socket == INVALID_SOCKET) {
        mosim_ts_socket_error_code = WSAGetLastError();
        return 0;
    }
    if (ioctlsocket(mosim_ts_socket, FIONBIO, &nonblocking) != 0) {
        mosim_ts_socket_error_code = WSAGetLastError();
        closesocket(mosim_ts_socket);
        mosim_ts_socket = INVALID_SOCKET;
        return 0;
    }
    mosim_ts_socket_init_status = 30;
    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_ANY);
    address.sin_port = htons((u_short)MOSIM_TS_PORT);
    if (bind(mosim_ts_socket, (struct sockaddr *)&address, sizeof(address)) != 0) {
        mosim_ts_socket_error_code = WSAGetLastError();
        closesocket(mosim_ts_socket);
        mosim_ts_socket = INVALID_SOCKET;
        return 0;
    }
    mosim_ts_socket_init_status = 40;
    mosim_ts_socket_error_code = 0;
    memset(&mosim_ts_latest, 0, sizeof(mosim_ts_latest));
    return 1;
}

static int mosim_mworks_live_telemetry_scope_receive(
    int *sequence,
    double *source_stamp_ns,
    double *sender_monotonic_ns,
    int *flags,
    int *frame_valid,
    int *socket_init_status,
    int *socket_error_code,
    double *values) {
    int processed = 0;
    int index;
    struct sockaddr_in latest_peer;
    int latest_peer_size = 0;

    *frame_valid = 0;
    if (!mosim_ts_initialize()) {
        *socket_init_status = mosim_ts_socket_init_status;
        *socket_error_code = mosim_ts_socket_error_code;
        return -1;
    }
    for (index = 0; index < MOSIM_TS_MAX_DRAIN; ++index) {
        MosimTsFrame candidate;
        struct sockaddr_in peer;
        int peer_size = (int)sizeof(peer);
        int received = recvfrom(
            mosim_ts_socket, (char *)&candidate, (int)sizeof(candidate), 0,
            (struct sockaddr *)&peer, &peer_size);
        if (received == SOCKET_ERROR) {
            int error = WSAGetLastError();
            if (error == WSAEWOULDBLOCK) break;
            mosim_ts_socket_error_code = error;
            *socket_init_status = mosim_ts_socket_init_status;
            *socket_error_code = mosim_ts_socket_error_code;
            return -2;
        }
        if (received != (int)sizeof(candidate) ||
            candidate.header.magic != MOSIM_TS_MAGIC ||
            candidate.header.version != MOSIM_TS_VERSION) {
            continue;
        }
        mosim_ts_latest = candidate;
        latest_peer = peer;
        latest_peer_size = peer_size;
        ++processed;
    }
    if (processed > 0) {
        MosimTsAck ack;
        memset(&ack, 0, sizeof(ack));
        ack.header.magic = MOSIM_TS_ACK_MAGIC;
        ack.header.version = MOSIM_TS_VERSION;
        ack.header.sequence = mosim_ts_ack_sequence++;
        ack.header.related_sequence = mosim_ts_latest.header.sequence;
        ack.header.source_stamp_ns = mosim_ts_monotonic_ns();
        ack.header.produced_monotonic_ns = ack.header.source_stamp_ns;
        memcpy(ack.header.run_id, mosim_ts_latest.header.run_id, MOSIM_TS_RUN_ID_SIZE);
        ack.echoed_sender_monotonic_ns = mosim_ts_latest.header.produced_monotonic_ns;
        if (latest_peer_size > 0) {
            sendto(mosim_ts_socket, (const char *)&ack, (int)sizeof(ack), 0,
                   (const struct sockaddr *)&latest_peer, latest_peer_size);
        }
    }
    if (processed <= 0) {
        *socket_init_status = mosim_ts_socket_init_status;
        *socket_error_code = mosim_ts_socket_error_code;
        return 0;
    }
    *sequence = (int)mosim_ts_latest.header.sequence;
    *source_stamp_ns = (double)mosim_ts_latest.header.source_stamp_ns;
    *sender_monotonic_ns = (double)mosim_ts_latest.header.produced_monotonic_ns;
    *flags = (int)mosim_ts_latest.header.flags;
    *frame_valid = 1;
    for (index = 0; index < MOSIM_TS_VALUE_COUNT; ++index) {
        values[index] = mosim_ts_latest.values[index];
        if (!MOSIM_TS_ISFINITE(values[index])) *frame_valid = 0;
    }
    *socket_init_status = mosim_ts_socket_init_status;
    *socket_error_code = mosim_ts_socket_error_code;
    return processed;
}

#endif
