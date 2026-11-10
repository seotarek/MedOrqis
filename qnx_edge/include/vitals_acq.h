/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: vitals_acq.h
 * Description: High-resolution acquisition loop, deterministic scoring scheduler,
 *              and IPC / socket emitter for QNX 8.0 & POSIX.
 */

#ifndef MEDORQIS_VITALS_ACQ_H
#define MEDORQIS_VITALS_ACQ_H

#include "vitals_types.h"
#include "news2_deterministic.h"
#include "patient_simulator.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int socket_fd;
    uint32_t sampling_interval_ms;
    uint32_t packets_sent;
    uint32_t emergency_alarms_triggered;
    uint64_t max_latency_ns;
    uint64_t avg_latency_ns;
    bool running;
} vitals_acq_engine_t;

/**
 * Initializes the acquisition engine and establishes socket listener/emitter.
 */
int vitals_acq_engine_init(vitals_acq_engine_t *engine, int port);

/**
 * Executes a single acquisition cycle:
 * 1. Samples/receives raw vitals
 * 2. Runs deterministic NEWS2 calculation
 * 3. Checks for extreme red flags
 * 4. Measures execution latency
 * 5. Dispatches telemetry packet to connected bridge
 */
int vitals_acq_process_sample(
    vitals_acq_engine_t *engine,
    vitals_telemetry_packet_t *packet,
    news2_breakdown_t *breakdown
);

/**
 * Shuts down acquisition engine and cleans up descriptors.
 */
void vitals_acq_engine_shutdown(vitals_acq_engine_t *engine);

#ifdef __cplusplus
}
#endif

#endif /* MEDORQIS_VITALS_ACQ_H */
