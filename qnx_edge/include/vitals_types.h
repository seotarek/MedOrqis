/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: vitals_types.h
 * Description: Memory-aligned packed data structures, telemetry packet contracts,
 *              and clinical alert classification enums for QNX Neutrino RTOS 8.0 & POSIX.
 * Standards: IEC 62304 Class C compliant / C99 standard.
 */

#ifndef MEDORQIS_VITALS_TYPES_H
#define MEDORQIS_VITALS_TYPES_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MEDORQIS_MAGIC_HEADER    0x4D454451U /* ASCII "MEDQ" */
#define MEDORQIS_PROTOCOL_VERSION 1U
#define MEDORQIS_DEFAULT_PORT     5055

/* Alert Priority Levels (Royal College of Physicians NEWS2 Escalation Grid) */
typedef enum {
    ALERT_LEVEL_ROUTINE  = 0, /* NEWS2 0-4: Ward monitoring (4-6 hourly) */
    ALERT_LEVEL_MEDIUM   = 1, /* NEWS2 5-6: Urgent bedside clinician review (hourly) */
    ALERT_LEVEL_CRITICAL = 2  /* NEWS2 >= 7 OR single parameter red flag: Immediate RRT / ICU */
} alert_level_t;

/* Consciousness Classification (AVPU / CVPU scale) */
typedef enum {
    CONSCIOUSNESS_ALERT = 0, /* Alert (A) */
    CONSCIOUSNESS_CVPU  = 1  /* Confusion (New), Voice (V), Pain (P), Unresponsive (U) */
} consciousness_level_t;

/* Supplemental Oxygen Status */
typedef enum {
    OXYGEN_ROOM_AIR     = 0, /* Breathing ambient room air */
    OXYGEN_SUPPLEMENTAL = 1  /* On prescribed supplemental oxygen */
} oxygen_status_t;

/* Extreme Single-Parameter Red Flag Bitmask (Immediate Escalation Trigger) */
#define RED_FLAG_NONE             0x0000U
#define RED_FLAG_SEVERE_BRADY     (1U << 0) /* Pulse <= 40 bpm */
#define RED_FLAG_SEVERE_TACHY     (1U << 1) /* Pulse >= 131 bpm */
#define RED_FLAG_SEVERE_HYPOTEN   (1U << 2) /* Systolic BP <= 90 mmHg */
#define RED_FLAG_SEVERE_BRADYPNEA (1U << 3) /* Resp Rate <= 8 bpm */
#define RED_FLAG_SEVERE_TACHYPNEA (1U << 4) /* Resp Rate >= 25 bpm */
#define RED_FLAG_SEVERE_HYPOXIA   (1U << 5) /* SpO2 <= 91% */
#define RED_FLAG_SEVERE_HYPOTHERM (1U << 6) /* Temp <= 35.0 C */
#define RED_FLAG_ACUTE_NEURO_DROP (1U << 7) /* New Confusion / CVPU */

/* Packed Telemetry Packet - Fixed 72 bytes layout */
#pragma pack(push, 1)
typedef struct {
    uint32_t magic_header;             /* Must equal MEDORQIS_MAGIC_HEADER (0x4D454451) */
    uint16_t version;                  /* Protocol version */
    uint32_t sequence_id;              /* Monotonically increasing packet sequence */
    uint64_t timestamp_us;             /* Microsecond timestamp (CLOCK_MONOTONIC or REALTIME) */
    char     patient_id[16];           /* Pseudonymized identifier, e.g. "PAT-ICU-084" */

    /* Raw Physiological Parameters */
    uint16_t heart_rate_bpm;           /* 0 - 300 bpm */
    uint16_t systolic_bp_mmhg;         /* 0 - 350 mmHg */
    uint16_t diastolic_bp_mmhg;        /* 0 - 250 mmHg */
    uint16_t respiratory_rate_bpm;     /* 0 - 100 bpm */
    float    spo2_percent;             /* 0.0 - 100.0 % */
    float    temperature_celsius;      /* 25.0 - 45.0 C */
    uint8_t  on_supplemental_oxygen;   /* oxygen_status_t */
    uint8_t  consciousness;            /* consciousness_level_t */

    /* QNX Edge Deterministic Output */
    uint8_t  news2_score;              /* Computed aggregate NEWS2 (0 - 20) */
    uint8_t  alert_level;              /* alert_level_t */
    uint16_t red_flags_mask;           /* Bitmask of triggered extreme parameter limits */
    uint32_t calculation_latency_ns;   /* QNX execution latency in nanoseconds */
    uint32_t crc32_checksum;           /* CRC32 integrity check of bytes 0..67 */
} vitals_telemetry_packet_t;
#pragma pack(pop)

/* Deterministic CRC-32 for packet integrity verification */
uint32_t medorqis_crc32(const uint8_t *data, size_t length);

#ifdef __cplusplus
}
#endif

#endif /* MEDORQIS_VITALS_TYPES_H */
