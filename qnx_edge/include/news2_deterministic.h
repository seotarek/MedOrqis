/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: news2_deterministic.h
 * Description: Pure C deterministic implementation of the Royal College of Physicians (RCP)
 *              National Early Warning Score 2 (NEWS2).
 * Guarantee: Zero dynamic memory allocation, execution latency < 500 ns.
 */

#ifndef MEDORQIS_NEWS2_DETERMINISTIC_H
#define MEDORQIS_NEWS2_DETERMINISTIC_H

#include "vitals_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEWS2_OK = 0,
    NEWS2_ERR_PHYSIOLOGICAL_OUT_OF_BOUNDS = -1,
    NEWS2_ERR_NULL_POINTER = -2
} news2_status_t;

/* Detailed sub-score breakdown for clinical auditability */
typedef struct {
    uint8_t respiration_score;   /* 0, 1, 2, or 3 */
    uint8_t spo2_score;          /* 0, 1, 2, or 3 */
    uint8_t oxygen_score;        /* 0 or 2 */
    uint8_t systolic_bp_score;   /* 0, 1, 2, or 3 */
    uint8_t pulse_score;         /* 0, 1, 2, or 3 */
    uint8_t consciousness_score; /* 0 or 3 */
    uint8_t temperature_score;   /* 0, 1, 2, or 3 */
    uint8_t total_score;         /* Sum: 0 - 20 */
    alert_level_t alert_level;   /* ROUTINE, MEDIUM, CRITICAL */
    uint16_t red_flags_mask;     /* Extreme parameter triggers */
} news2_breakdown_t;

/**
 * Validates whether raw vitals fall within human physiological bounds.
 * Prevents garbage arithmetic caused by detached leads or sensor artifacts.
 */
news2_status_t news2_validate_physiological_bounds(
    uint16_t heart_rate_bpm,
    uint16_t systolic_bp_mmhg,
    uint16_t respiratory_rate_bpm,
    float spo2_percent,
    float temperature_celsius
);

/**
 * Calculates NEWS2 aggregate score, sub-scores, and alert priority.
 * Pure deterministic function: No heap allocation, no static mutable state.
 */
news2_status_t news2_calculate(
    uint16_t respiratory_rate_bpm,
    float spo2_percent,
    oxygen_status_t oxygen_status,
    uint16_t systolic_bp_mmhg,
    uint16_t pulse_bpm,
    consciousness_level_t consciousness,
    float temperature_celsius,
    news2_breakdown_t *out_breakdown
);

/**
 * Returns clinical recommendation guideline string matching RCP 2017.
 */
const char* news2_get_escalation_protocol(alert_level_t level);

#ifdef __cplusplus
}
#endif

#endif /* MEDORQIS_NEWS2_DETERMINISTIC_H */
