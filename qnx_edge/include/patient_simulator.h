/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: patient_simulator.h
 * Description: Clinically-grounded physiological patient deterioration simulator
 *              for QNX 8.0 demonstration and verification scenarios.
 */

#ifndef MEDORQIS_PATIENT_SIMULATOR_H
#define MEDORQIS_PATIENT_SIMULATOR_H

#include "vitals_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SCENARIO_SEPTIC_SHOCK       = 0, /* Sepsis progression: Normal -> SIRS -> Septic Shock */
    SCENARIO_PULMONARY_EMBOLISM = 1, /* Sudden desaturation and acute cardiopulmonary strain */
    SCENARIO_STABLE_POSTOP      = 2  /* Stable postoperative patient baseline */
} clinical_scenario_t;

typedef struct {
    char patient_id[16];
    clinical_scenario_t scenario;
    uint32_t current_step;
    uint32_t total_steps;
    bool is_completed;
} patient_simulator_t;

/**
 * Initializes the patient simulator with a selected clinical scenario.
 */
void patient_simulator_init(patient_simulator_t *sim, const char *patient_id, clinical_scenario_t scenario, uint32_t duration_steps);

/**
 * Generates the next physiological vital signs reading for the given trajectory step.
 */
bool patient_simulator_step(patient_simulator_t *sim, vitals_telemetry_packet_t *out_packet);

/**
 * Returns a human-readable description of the current scenario.
 */
const char* patient_simulator_get_scenario_name(clinical_scenario_t scenario);

#ifdef __cplusplus
}
#endif

#endif /* MEDORQIS_PATIENT_SIMULATOR_H */
