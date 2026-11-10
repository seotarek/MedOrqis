/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: patient_simulator.c
 * Description: Clinically-grounded physiological patient deterioration simulator.
 * Standards: Simulates verified physiological trajectories (Sepsis-3, PE, Homeostasis).
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "../include/patient_simulator.h"
#include "../include/qnx_compat.h"

void patient_simulator_init(
    patient_simulator_t *sim,
    const char *patient_id,
    clinical_scenario_t scenario,
    uint32_t duration_steps
) {
    if (!sim) return;
    memset(sim, 0, sizeof(patient_simulator_t));
    if (patient_id) {
        snprintf(sim->patient_id, sizeof(sim->patient_id), "%s", patient_id);
    } else {
        snprintf(sim->patient_id, sizeof(sim->patient_id), "%s", "PAT-ICU-084");
    }
    sim->scenario = scenario;
    sim->current_step = 0;
    sim->total_steps = (duration_steps > 0) ? duration_steps : 60;
    sim->is_completed = false;
}

const char* patient_simulator_get_scenario_name(clinical_scenario_t scenario) {
    switch (scenario) {
        case SCENARIO_SEPTIC_SHOCK:
            return "Acute Postoperative Sepsis Progression to Septic Shock";
        case SCENARIO_PULMONARY_EMBOLISM:
            return "Acute Massive Pulmonary Embolism (Sudden Cardiopulmonary Strain)";
        case SCENARIO_STABLE_POSTOP:
        default:
            return "Stable Postoperative Ward Patient (Baseline Homeostasis)";
    }
}

bool patient_simulator_step(patient_simulator_t *sim, vitals_telemetry_packet_t *out_packet) {
    if (!sim || !out_packet || sim->is_completed) return false;

    memset(out_packet, 0, sizeof(vitals_telemetry_packet_t));
    out_packet->magic_header = MEDORQIS_MAGIC_HEADER;
    out_packet->version = MEDORQIS_PROTOCOL_VERSION;
    out_packet->sequence_id = sim->current_step;
    out_packet->timestamp_us = qnx_get_monotonic_time_us();
    snprintf(out_packet->patient_id, sizeof(out_packet->patient_id), "%s", sim->patient_id);

    uint32_t step = sim->current_step;
    uint32_t max_s = sim->total_steps;
    float progress = (float)step / (float)max_s;

    if (sim->scenario == SCENARIO_SEPTIC_SHOCK) {
        if (progress < 0.25f) {
            /* Phase 1: Baseline Homeostasis (NEWS2 ~ 0) */
            out_packet->heart_rate_bpm = 72 + (step % 5) - 2;
            out_packet->systolic_bp_mmhg = 122 + (step % 4) - 2;
            out_packet->diastolic_bp_mmhg = 78 + (step % 3) - 1;
            out_packet->respiratory_rate_bpm = 15;
            out_packet->spo2_percent = 98.0f;
            out_packet->temperature_celsius = 36.9f;
            out_packet->on_supplemental_oxygen = (uint8_t)OXYGEN_ROOM_AIR;
            out_packet->consciousness = (uint8_t)CONSCIOUSNESS_ALERT;
        } else if (progress < 0.55f) {
            /* Phase 2: SIRS / Early Sepsis (NEWS2 ~ 5-6, Alert Medium) */
            float p2 = (progress - 0.25f) / 0.30f;
            out_packet->heart_rate_bpm = (uint16_t)(76 + (p2 * 28.0f) + (step % 3));
            out_packet->systolic_bp_mmhg = (uint16_t)(120 - (p2 * 14.0f) - (step % 3));
            out_packet->diastolic_bp_mmhg = (uint16_t)(76 - (p2 * 10.0f));
            out_packet->respiratory_rate_bpm = (uint16_t)(16 + (p2 * 6.0f));
            out_packet->spo2_percent = (float)((int)(97.0f - (p2 * 3.0f)));
            out_packet->temperature_celsius = (float)((int)((37.0f + (p2 * 1.5f)) * 10.0f)) / 10.0f;
            out_packet->on_supplemental_oxygen = (uint8_t)OXYGEN_ROOM_AIR;
            out_packet->consciousness = (uint8_t)CONSCIOUSNESS_ALERT;
        } else {
            /* Phase 3: Fulminant Septic Shock (NEWS2 ~ 14-19, Alert Critical) */
            float p3 = (progress - 0.55f) / 0.45f;
            out_packet->heart_rate_bpm = (uint16_t)(106 + (p3 * 32.0f) + (step % 4));
            out_packet->systolic_bp_mmhg = (uint16_t)(104 - (p3 * 26.0f) - (step % 4));
            out_packet->diastolic_bp_mmhg = (uint16_t)(64 - (p3 * 18.0f));
            out_packet->respiratory_rate_bpm = (uint16_t)(22 + (p3 * 7.0f));
            out_packet->spo2_percent = (float)((int)(93.0f - (p3 * 5.0f)));
            out_packet->temperature_celsius = (float)((int)((38.6f + (p3 * 0.9f)) * 10.0f)) / 10.0f;
            out_packet->on_supplemental_oxygen = (uint8_t)OXYGEN_SUPPLEMENTAL;
            out_packet->consciousness = (p3 > 0.4f) ? (uint8_t)CONSCIOUSNESS_CVPU : (uint8_t)CONSCIOUSNESS_ALERT;
        }
    } else if (sim->scenario == SCENARIO_PULMONARY_EMBOLISM) {
        if (progress < 0.35f) {
            /* Baseline */
            out_packet->heart_rate_bpm = 74;
            out_packet->systolic_bp_mmhg = 126;
            out_packet->diastolic_bp_mmhg = 80;
            out_packet->respiratory_rate_bpm = 14;
            out_packet->spo2_percent = 98.0f;
            out_packet->temperature_celsius = 36.8f;
            out_packet->on_supplemental_oxygen = (uint8_t)OXYGEN_ROOM_AIR;
            out_packet->consciousness = (uint8_t)CONSCIOUSNESS_ALERT;
        } else {
            /* Sudden Embolic Event */
            out_packet->heart_rate_bpm = 124 + (step % 6);
            out_packet->systolic_bp_mmhg = 96 - (step % 4);
            out_packet->diastolic_bp_mmhg = 62;
            out_packet->respiratory_rate_bpm = 32 + (step % 3);
            out_packet->spo2_percent = 86.0f;
            out_packet->temperature_celsius = 37.1f;
            out_packet->on_supplemental_oxygen = (uint8_t)OXYGEN_SUPPLEMENTAL;
            out_packet->consciousness = (uint8_t)CONSCIOUSNESS_CVPU;
        }
    } else {
        /* Stable Post-Op Baseline */
        out_packet->heart_rate_bpm = 70 + (step % 6) - 3;
        out_packet->systolic_bp_mmhg = 120 + (step % 8) - 4;
        out_packet->diastolic_bp_mmhg = 78 + (step % 4) - 2;
        out_packet->respiratory_rate_bpm = 15;
        out_packet->spo2_percent = 98.0f + (0.1f * (float)(step % 3));
        out_packet->temperature_celsius = 36.8f + (0.05f * (float)(step % 3));
        out_packet->on_supplemental_oxygen = (uint8_t)OXYGEN_ROOM_AIR;
        out_packet->consciousness = (uint8_t)CONSCIOUSNESS_ALERT;
    }

    sim->current_step++;
    if (sim->current_step >= sim->total_steps) {
        sim->is_completed = true;
    }

    return true;
}
