/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: vitals_resmgr.c
 * Description: Native QNX Neutrino RTOS 8.0 Resource Manager (/dev/vitals) implementation
 *              with dual-target POSIX PSE54 driver emulation for Linux host testing.
 * Standards: QNX Neutrino Microkernel Architecture (procnto-64) / IEC 62304 Class C.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <pthread.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "../include/vitals_resmgr.h"
#include "../include/qnx_compat.h"

static vitals_telemetry_packet_t g_latest_packet;
static pthread_mutex_t g_driver_mutex = PTHREAD_MUTEX_INITIALIZER;
static vitals_driver_stats_t g_driver_stats;
static volatile bool g_resmgr_running = false;
static int g_fifo_fd = -1;
static char g_device_path[128];

#if defined(__QNX__) || defined(__QNXNTO__)
#include <sys/iofunc.h>
#include <sys/dispatch.h>

static resmgr_connect_funcs_t  g_connect_funcs;
static resmgr_io_funcs_t       g_io_funcs;
static iofunc_attr_t           g_attr;
static dispatch_t             *g_dpp = NULL;

static int vitals_io_read(resmgr_context_t *ctp, io_read_t *msg, RESMGR_OCB_T *ocb) {
    int status;
    if ((status = iofunc_read_verify(ctp, msg, ocb, NULL)) != EOK) {
        return status;
    }
    if ((msg->i.xtype & _IO_XTYPE_MASK) != _IO_XTYPE_NONE) {
        return ENOSYS;
    }

    pthread_mutex_lock(&g_driver_mutex);
    size_t packet_size = sizeof(vitals_telemetry_packet_t);
    size_t bytes_to_read = msg->i.nbytes < packet_size ? msg->i.nbytes : packet_size;

    MsgReply(ctp->rcvid, bytes_to_read, &g_latest_packet, bytes_to_read);
    g_driver_stats.total_samples_read++;
    pthread_mutex_unlock(&g_driver_mutex);

    return _RESMGR_NOREPLY;
}

static int vitals_io_devctl(resmgr_context_t *ctp, io_devctl_t *msg, RESMGR_OCB_T *ocb) {
    int status;
    if ((status = iofunc_devctl_verify(ctp, msg, ocb, NULL)) != EOK) {
        return status;
    }

    pthread_mutex_lock(&g_driver_mutex);
    switch (msg->i.dcmd) {
        case DCMD_VITALS_GET_PACKET:
            memcpy(_DEVCTL_DATA(msg->i), &g_latest_packet, sizeof(vitals_telemetry_packet_t));
            MsgReply(ctp->rcvid, EOK, msg, sizeof(io_devctl_t) + sizeof(vitals_telemetry_packet_t));
            status = _RESMGR_NOREPLY;
            break;
        case DCMD_VITALS_GET_STATS:
            memcpy(_DEVCTL_DATA(msg->i), &g_driver_stats, sizeof(vitals_driver_stats_t));
            MsgReply(ctp->rcvid, EOK, msg, sizeof(io_devctl_t) + sizeof(vitals_driver_stats_t));
            status = _RESMGR_NOREPLY;
            break;
        default:
            status = ENOSYS;
            break;
    }
    pthread_mutex_unlock(&g_driver_mutex);
    return status;
}

static void* qnx_resmgr_thread(void *arg) {
    (void)arg;
    resmgr_attr_t resmgr_attr;
    memset(&resmgr_attr, 0, sizeof(resmgr_attr));
    resmgr_attr.nparts_max = 1;
    resmgr_attr.msg_max_size = 2048;

    iofunc_func_init(_RESMGR_CONNECT_NFUNCS, &g_connect_funcs,
                     _RESMGR_IO_NFUNCS, &g_io_funcs);
    g_io_funcs.read = vitals_io_read;
    g_io_funcs.devctl = vitals_io_devctl;

    iofunc_attr_init(&g_attr, S_IFCHR | 0666, 0, 0);

    g_dpp = dispatch_create();
    if (!g_dpp) {
        perror("vitals_resmgr: dispatch_create failed");
        return NULL;
    }

    int id = resmgr_attach(g_dpp, &resmgr_attr, g_device_path, _FTYPE_ANY, 0,
                           &g_connect_funcs, &g_io_funcs, &g_attr);
    if (id == -1) {
        perror("vitals_resmgr: resmgr_attach failed");
        return NULL;
    }

    dispatch_context_t *ctp = dispatch_context_alloc(g_dpp);
    while (g_resmgr_running) {
        if ((ctp = dispatch_block(ctp)) == NULL) {
            break;
        }
        dispatch_handler(ctp);
    }
    dispatch_context_free(ctp);
    return NULL;
}
#else
/* Linux / POSIX Emulation of /dev/vitals via POSIX FIFO */
static void* posix_resmgr_thread(void *arg) {
    (void)arg;
    mkfifo(g_device_path, 0666);

    while (g_resmgr_running) {
        /* Open in non-blocking mode to prevent freeze if no readers */
        int fd = open(g_device_path, O_RDWR | O_NONBLOCK);
        if (fd >= 0) {
            pthread_mutex_lock(&g_driver_mutex);
            write(fd, &g_latest_packet, sizeof(vitals_telemetry_packet_t));
            g_driver_stats.total_samples_read++;
            pthread_mutex_unlock(&g_driver_mutex);
            close(fd);
        }
        qnx_sleep_ms(100);
    }
    unlink(g_device_path);
    return NULL;
}
#endif

int vitals_resmgr_start(const char *device_path) {
    if (g_resmgr_running) return 0;

    memset(&g_driver_stats, 0, sizeof(g_driver_stats));
    g_resmgr_running = true;

#if defined(__QNX__) || defined(__QNXNTO__)
    strncpy(g_device_path, device_path ? device_path : VITALS_DEVICE_PATH_QNX, sizeof(g_device_path) - 1);
    pthread_t tid;
    return pthread_create(&tid, NULL, qnx_resmgr_thread, NULL);
#else
    strncpy(g_device_path, device_path ? device_path : VITALS_DEVICE_PATH_POSIX, sizeof(g_device_path) - 1);
    pthread_t tid;
    return pthread_create(&tid, NULL, posix_resmgr_thread, NULL);
#endif
}

void vitals_resmgr_publish(const vitals_telemetry_packet_t *packet) {
    if (!packet) return;
    pthread_mutex_lock(&g_driver_mutex);
    memcpy(&g_latest_packet, packet, sizeof(vitals_telemetry_packet_t));
    if (packet->alert_level == ALERT_LEVEL_CRITICAL) {
        g_driver_stats.emergency_pulses_sent++;
    }
    pthread_mutex_unlock(&g_driver_mutex);
}

void vitals_resmgr_stop(void) {
    g_resmgr_running = false;
    if (g_fifo_fd >= 0) {
        close(g_fifo_fd);
        g_fifo_fd = -1;
    }
}
