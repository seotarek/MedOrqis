/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: vitals_acq.c
 * Description: Acquisition engine, deterministic scoring pipeline, and IPC/socket publisher.
 * Standards: IEC 62304 Class C (failsafe non-blocking telemetry emitter).
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "../include/vitals_acq.h"
#include "../include/qnx_compat.h"

static int g_client_fd = -1;

int vitals_acq_engine_init(vitals_acq_engine_t *engine, int port) {
    if (!engine) return -1;
    memset(engine, 0, sizeof(vitals_acq_engine_t));

    engine->sampling_interval_ms = 100; /* 10 Hz */
    engine->running = true;

    /* Create non-blocking server socket */
    int sfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sfd < 0) {
        perror("vitals_acq: socket creation failed");
        return -1;
    }

    int opt = 1;
    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    /* Set non-blocking so listener accept() does not stall the RTOS loop */
    int flags = fcntl(sfd, F_GETFL, 0);
    fcntl(sfd, F_SETFL, flags | O_NONBLOCK);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons((uint16_t)port);

    if (bind(sfd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("vitals_acq: bind failed");
        close(sfd);
        return -1;
    }

    if (listen(sfd, 2) < 0) {
        perror("vitals_acq: listen failed");
        close(sfd);
        return -1;
    }

    engine->socket_fd = sfd;
    g_client_fd = -1;

    return 0;
}

int vitals_acq_process_sample(
    vitals_acq_engine_t *engine,
    vitals_telemetry_packet_t *packet,
    news2_breakdown_t *breakdown
) {
    if (!engine || !packet || !breakdown) return -1;

    /* Measure hard real-time execution latency */
    uint64_t t_start = qnx_get_monotonic_time_ns();

    news2_status_t status = news2_calculate(
        packet->respiratory_rate_bpm,
        packet->spo2_percent,
        (oxygen_status_t)packet->on_supplemental_oxygen,
        packet->systolic_bp_mmhg,
        packet->heart_rate_bpm,
        (consciousness_level_t)packet->consciousness,
        packet->temperature_celsius,
        breakdown
    );

    uint64_t t_end = qnx_get_monotonic_time_ns();
    uint32_t latency_ns = (uint32_t)(t_end - t_start);

    if (status != NEWS2_OK) {
        return (int)status;
    }

    /* Populate packet with computed deterministic scores */
    packet->news2_score = breakdown->total_score;
    packet->alert_level = (uint8_t)breakdown->alert_level;
    packet->red_flags_mask = breakdown->red_flags_mask;
    packet->calculation_latency_ns = latency_ns;

    /* Compute CRC32 over packet bytes excluding the crc32 field itself */
    size_t crc_len = sizeof(vitals_telemetry_packet_t) - sizeof(uint32_t);
    packet->crc32_checksum = medorqis_crc32((const uint8_t*)packet, crc_len);

    /* Update engine stats */
    engine->packets_sent++;
    if (breakdown->alert_level == ALERT_LEVEL_CRITICAL) {
        engine->emergency_alarms_triggered++;
    }
    if (latency_ns > engine->max_latency_ns) {
        engine->max_latency_ns = latency_ns;
    }
    engine->avg_latency_ns = (engine->avg_latency_ns * 7 + latency_ns) / 8;

    /* Try to accept connection if not connected */
    if (engine->socket_fd >= 0 && g_client_fd < 0) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int cfd = accept(engine->socket_fd, (struct sockaddr*)&client_addr, &client_len);
        if (cfd >= 0) {
            /* Make client socket non-blocking to prevent backpressure */
            int cflags = fcntl(cfd, F_GETFL, 0);
            fcntl(cfd, F_SETFL, cflags | O_NONBLOCK);
            g_client_fd = cfd;
        }
    }

    /* Transmit packet if client is connected */
    if (g_client_fd >= 0) {
        ssize_t sent = send(g_client_fd, packet, sizeof(vitals_telemetry_packet_t), MSG_NOSIGNAL);
        if (sent < 0 && (errno == EPIPE || errno == ECONNRESET)) {
            close(g_client_fd);
            g_client_fd = -1;
        }
    }

    return 0;
}

void vitals_acq_engine_shutdown(vitals_acq_engine_t *engine) {
    if (!engine) return;
    engine->running = false;
    if (g_client_fd >= 0) {
        close(g_client_fd);
        g_client_fd = -1;
    }
    if (engine->socket_fd >= 0) {
        close(engine->socket_fd);
        engine->socket_fd = -1;
    }
}
