/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: news2_deterministic.c
 * Description: Pure C99 deterministic implementation of Royal College of Physicians (RCP)
 *              National Early Warning Score 2 (NEWS2).
 * Guarantee: Zero dynamic memory allocation (malloc/free prohibited), execution latency < 500 ns.
 */

#include <string.h>
#include "../include/news2_deterministic.h"

/* Standard IEEE 802.3 CRC-32 polynomial */
#define CRC32_POLYNOMIAL 0xEDB88320U

uint32_t medorqis_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    if (!data) return 0;
    
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint32_t)data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 1U) {
                crc = (crc >> 1) ^ CRC32_POLYNOMIAL;
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

news2_status_t news2_validate_physiological_bounds(
    uint16_t heart_rate_bpm,
    uint16_t systolic_bp_mmhg,
    uint16_t respiratory_rate_bpm,
    float spo2_percent,
    float temperature_celsius
) {
    /* Reject physiological impossibilities indicative of disconnected leads or hardware corruption */
    if (heart_rate_bpm > 300) return NEWS2_ERR_PHYSIOLOGICAL_OUT_OF_BOUNDS;
    if (systolic_bp_mmhg < 20 || systolic_bp_mmhg > 350) return NEWS2_ERR_PHYSIOLOGICAL_OUT_OF_BOUNDS;
    if (respiratory_rate_bpm > 100) return NEWS2_ERR_PHYSIOLOGICAL_OUT_OF_BOUNDS;
    if (spo2_percent < 0.0f || spo2_percent > 100.0f) return NEWS2_ERR_PHYSIOLOGICAL_OUT_OF_BOUNDS;
    if (temperature_celsius < 20.0f || temperature_celsius > 45.0f) return NEWS2_ERR_PHYSIOLOGICAL_OUT_OF_BOUNDS;

    return NEWS2_OK;
}

news2_status_t news2_calculate(
    uint16_t respiratory_rate_bpm,
    float spo2_percent,
    oxygen_status_t oxygen_status,
    uint16_t systolic_bp_mmhg,
    uint16_t pulse_bpm,
    consciousness_level_t consciousness,
    float temperature_celsius,
    news2_breakdown_t *out_breakdown
) {
    if (!out_breakdown) {
        return NEWS2_ERR_NULL_POINTER;
    }

    news2_status_t bound_check = news2_validate_physiological_bounds(
        pulse_bpm, systolic_bp_mmhg, respiratory_rate_bpm, spo2_percent, temperature_celsius
    );
    if (bound_check != NEWS2_OK) {
        return bound_check;
    }

    memset(out_breakdown, 0, sizeof(news2_breakdown_t));
    uint16_t red_flags = RED_FLAG_NONE;

    /* 1. Respiration Rate (bpm) */
    if (respiratory_rate_bpm <= 8) {
        out_breakdown->respiration_score = 3;
        red_flags |= RED_FLAG_SEVERE_BRADYPNEA;
    } else if (respiratory_rate_bpm >= 9 && respiratory_rate_bpm <= 11) {
        out_breakdown->respiration_score = 1;
    } else if (respiratory_rate_bpm >= 12 && respiratory_rate_bpm <= 20) {
        out_breakdown->respiration_score = 0;
    } else if (respiratory_rate_bpm >= 21 && respiratory_rate_bpm <= 24) {
        out_breakdown->respiration_score = 2;
    } else { /* >= 25 */
        out_breakdown->respiration_score = 3;
        red_flags |= RED_FLAG_SEVERE_TACHYPNEA;
    }

    /* 2. SpO2 Oxygen Saturation (% - Scale 1) */
    if (spo2_percent <= 91.0f) {
        out_breakdown->spo2_score = 3;
        red_flags |= RED_FLAG_SEVERE_HYPOXIA;
    } else if (spo2_percent <= 93.0f) {
        out_breakdown->spo2_score = 2;
    } else if (spo2_percent <= 95.0f) {
        out_breakdown->spo2_score = 1;
    } else { /* >= 96.0f */
        out_breakdown->spo2_score = 0;
    }

    /* 3. Supplemental Oxygen Status */
    if (oxygen_status == OXYGEN_SUPPLEMENTAL) {
        out_breakdown->oxygen_score = 2;
    } else {
        out_breakdown->oxygen_score = 0;
    }

    /* 4. Systolic Blood Pressure (mmHg) */
    if (systolic_bp_mmhg <= 90) {
        out_breakdown->systolic_bp_score = 3;
        red_flags |= RED_FLAG_SEVERE_HYPOTEN;
    } else if (systolic_bp_mmhg <= 100) {
        out_breakdown->systolic_bp_score = 2;
    } else if (systolic_bp_mmhg <= 110) {
        out_breakdown->systolic_bp_score = 1;
    } else if (systolic_bp_mmhg <= 219) {
        out_breakdown->systolic_bp_score = 0;
    } else { /* >= 220 */
        out_breakdown->systolic_bp_score = 3;
    }

    /* 5. Heart Rate / Pulse (bpm) */
    if (pulse_bpm <= 40) {
        out_breakdown->pulse_score = 3;
        red_flags |= RED_FLAG_SEVERE_BRADY;
    } else if (pulse_bpm <= 50) {
        out_breakdown->pulse_score = 1;
    } else if (pulse_bpm <= 90) {
        out_breakdown->pulse_score = 0;
    } else if (pulse_bpm <= 110) {
        out_breakdown->pulse_score = 1;
    } else if (pulse_bpm <= 130) {
        out_breakdown->pulse_score = 2;
    } else { /* >= 131 */
        out_breakdown->pulse_score = 3;
        red_flags |= RED_FLAG_SEVERE_TACHY;
    }

    /* 6. Consciousness (Alert vs CVPU) */
    if (consciousness == CONSCIOUSNESS_ALERT) {
        out_breakdown->consciousness_score = 0;
    } else {
        out_breakdown->consciousness_score = 3;
        red_flags |= RED_FLAG_ACUTE_NEURO_DROP;
    }

    /* 7. Body Temperature (Celsius) */
    if (temperature_celsius <= 35.0f) {
        out_breakdown->temperature_score = 3;
        red_flags |= RED_FLAG_SEVERE_HYPOTHERM;
    } else if (temperature_celsius <= 36.0f) {
        out_breakdown->temperature_score = 1;
    } else if (temperature_celsius <= 38.0f) {
        out_breakdown->temperature_score = 0;
    } else if (temperature_celsius <= 39.0f) {
        out_breakdown->temperature_score = 1;
    } else { /* > 39.0f */
        out_breakdown->temperature_score = 2;
    }

    /* Total composite score (0 - 20) */
    out_breakdown->total_score = (uint8_t)(
        out_breakdown->respiration_score +
        out_breakdown->spo2_score +
        out_breakdown->oxygen_score +
        out_breakdown->systolic_bp_score +
        out_breakdown->pulse_score +
        out_breakdown->consciousness_score +
        out_breakdown->temperature_score
    );

    out_breakdown->red_flags_mask = red_flags;

    /* Determine Clinical Risk Priority Level (RCP 2017) */
    /* An extreme score of 3 in ANY individual parameter OR composite score >= 7 warrants emergency escalation */
    bool has_individual_3 = (
        out_breakdown->respiration_score == 3 ||
        out_breakdown->spo2_score == 3 ||
        out_breakdown->systolic_bp_score == 3 ||
        out_breakdown->pulse_score == 3 ||
        out_breakdown->consciousness_score == 3 ||
        out_breakdown->temperature_score == 3
    );

    if (out_breakdown->total_score >= 7 || has_individual_3) {
        out_breakdown->alert_level = ALERT_LEVEL_CRITICAL;
    } else if (out_breakdown->total_score >= 5) {
        out_breakdown->alert_level = ALERT_LEVEL_MEDIUM;
    } else {
        out_breakdown->alert_level = ALERT_LEVEL_ROUTINE;
    }

    return NEWS2_OK;
}

const char* news2_get_escalation_protocol(alert_level_t level) {
    switch (level) {
        case ALERT_LEVEL_CRITICAL:
            return "EMERGENCY: Immediate assessment by Rapid Response Team (RRT) / Critical Care Team. Continuous monitoring.";
        case ALERT_LEVEL_MEDIUM:
            return "URGENT: Urgent bedside clinical review by a clinician competent in acute assessment. Observation hourly.";
        case ALERT_LEVEL_ROUTINE:
        default:
            return "ROUTINE: Standard ward-based monitoring (every 4 to 6 hours).";
    }
}
