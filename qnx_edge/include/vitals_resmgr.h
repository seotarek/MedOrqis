/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: vitals_resmgr.h
 * Description: Native QNX Neutrino RTOS 8.0 Resource Manager (/dev/vitals) interface
 *              and POSIX character driver abstraction.
 * Standards: QNX 8.0 Microkernel Driver Architecture / IEC 62304 Class C.
 */

#ifndef MEDORQIS_VITALS_RESMGR_H
#define MEDORQIS_VITALS_RESMGR_H

#include "vitals_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define VITALS_DEVICE_PATH_QNX   "/dev/vitals"
#define VITALS_DEVICE_PATH_POSIX "/tmp/dev_vitals"

/* Driver Telemetry Statistics */
typedef struct {
    uint32_t total_samples_read;
    uint32_t emergency_pulses_sent;
    uint32_t client_connections;
    uint64_t uptime_us;
} vitals_driver_stats_t;

/* QNX Custom devctl() Command Definitions */
#if defined(__QNX__) || defined(__QNXNTO__)
#include <devctl.h>
#define DCMD_VITALS_GET_PACKET  __DIOF('V', 1, vitals_telemetry_packet_t)
#define DCMD_VITALS_GET_STATS   __DIOF('V', 2, vitals_driver_stats_t)
#else
#define DCMD_VITALS_GET_PACKET  0x5601U
#define DCMD_VITALS_GET_STATS   0x5602U
#endif

/**
 * Initializes and starts the QNX /dev/vitals resource manager thread.
 */
int vitals_resmgr_start(const char *device_path);

/**
 * Publishes a new vital signs telemetry packet to the driver buffer.
 */
void vitals_resmgr_publish(const vitals_telemetry_packet_t *packet);

/**
 * Stops the resource manager.
 */
void vitals_resmgr_stop(void);

#ifdef __cplusplus
}
#endif

#endif /* MEDORQIS_VITALS_RESMGR_H */
