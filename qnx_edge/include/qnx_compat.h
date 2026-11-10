/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: qnx_compat.h
 * Description: Abstraction layer between QNX Neutrino RTOS 8.0 native microkernel
 *              primitives (ChannelCreate, MsgSend, MsgReceivePulse) and POSIX PSE54.
 */

#ifndef MEDORQIS_QNX_COMPAT_H
#define MEDORQIS_QNX_COMPAT_H

#include <time.h>
#include <errno.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>

#if defined(__QNX__) || defined(__QNXNTO__)
#define QNX_TARGET_REAL_RTOS 1
#include <sys/neutrino.h>
#include <sys/netmgr.h>
#include <sys/dispatch.h>
#else
#define QNX_TARGET_REAL_RTOS 0
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Monotonic timestamp in microseconds */
static inline uint64_t qnx_get_monotonic_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ((uint64_t)ts.tv_sec * 1000000ULL) + ((uint64_t)ts.tv_nsec / 1000ULL);
}

/* Monotonic timestamp in nanoseconds */
static inline uint64_t qnx_get_monotonic_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ((uint64_t)ts.tv_sec * 1000000000ULL) + (uint64_t)ts.tv_nsec;
}

/* Sleep high-resolution milliseconds */
static inline void qnx_sleep_ms(uint32_t ms) {
    struct timespec req;
    req.tv_sec = ms / 1000;
    req.tv_nsec = (ms % 1000) * 1000000L;
    nanosleep(&req, NULL);
}

#ifdef __cplusplus
}
#endif

#endif /* MEDORQIS_QNX_COMPAT_H */
