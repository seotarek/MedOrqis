/**
 * MedOrqis-QNX: Automated Test Suite for Deterministic NEWS2 Engine
 * File: test_news2_deterministic.c
 * Standards: IEC 62304 verification of Class C deterministic algorithms.
 */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include "../include/news2_deterministic.h"

static int g_tests_run = 0;
static int g_tests_passed = 0;

#define TEST_ASSERT(cond, msg) do { \
    g_tests_run++; \
    if (!(cond)) { \
        printf("[FAIL] Line %d: %s\n", __LINE__, msg); \
        assert(cond); \
    } else { \
        g_tests_passed++; \
    } \
} while(0)

void test_baseline_normal_patient(void) {
    news2_breakdown_t b;
    news2_status_t status = news2_calculate(
        15,           /* RR 15 bpm (0) */
        98.0f,        /* SpO2 98% (0) */
        OXYGEN_ROOM_AIR, /* Air (0) */
        120,          /* SBP 120 mmHg (0) */
        72,           /* HR 72 bpm (0) */
        CONSCIOUSNESS_ALERT, /* Alert (0) */
        37.0f,        /* Temp 37.0 C (0) */
        &b
    );

    TEST_ASSERT(status == NEWS2_OK, "Baseline calculation must return NEWS2_OK");
    TEST_ASSERT(b.total_score == 0, "Normal vitals must yield score 0");
    TEST_ASSERT(b.alert_level == ALERT_LEVEL_ROUTINE, "Score 0 must be ALERT_LEVEL_ROUTINE");
    TEST_ASSERT(b.red_flags_mask == RED_FLAG_NONE, "Normal vitals must have no red flags");
}

void test_early_deterioration_medium_risk(void) {
    news2_breakdown_t b;
    news2_status_t status = news2_calculate(
        22,           /* RR 22 bpm (2) */
        94.0f,        /* SpO2 94% (1) */
        OXYGEN_ROOM_AIR, /* Air (0) */
        105,          /* SBP 105 mmHg (1) */
        102,          /* HR 102 bpm (1) */
        CONSCIOUSNESS_ALERT, /* Alert (0) */
        38.5f,        /* Temp 38.5 C (1) */
        &b
    );

    TEST_ASSERT(status == NEWS2_OK, "Calculation must succeed");
    TEST_ASSERT(b.total_score == 6, "Sum 2+1+0+1+1+0+1 must equal 6");
    TEST_ASSERT(b.alert_level == ALERT_LEVEL_MEDIUM, "Score 6 must trigger ALERT_LEVEL_MEDIUM");
    TEST_ASSERT(b.red_flags_mask == RED_FLAG_NONE, "No single extreme >= 3 in this profile");
}

void test_fulminant_septic_shock_critical(void) {
    news2_breakdown_t b;
    news2_status_t status = news2_calculate(
        28,           /* RR 28 bpm (3) -> RED_FLAG_SEVERE_TACHYPNEA */
        88.0f,        /* SpO2 88% (3) -> RED_FLAG_SEVERE_HYPOXIA */
        OXYGEN_SUPPLEMENTAL, /* Supplemental O2 (2) */
        82,           /* SBP 82 mmHg (3) -> RED_FLAG_SEVERE_HYPOTEN */
        136,          /* HR 136 bpm (3) -> RED_FLAG_SEVERE_TACHY */
        CONSCIOUSNESS_CVPU,  /* CVPU (3) -> RED_FLAG_ACUTE_NEURO_DROP */
        39.5f,        /* Temp 39.5 C (2) */
        &b
    );

    TEST_ASSERT(status == NEWS2_OK, "Septic shock calculation must succeed");
    TEST_ASSERT(b.total_score == 19, "Sum 3+3+2+3+3+3+2 must equal 19");
    TEST_ASSERT(b.alert_level == ALERT_LEVEL_CRITICAL, "Score 19 must trigger ALERT_LEVEL_CRITICAL");
    TEST_ASSERT((b.red_flags_mask & RED_FLAG_SEVERE_TACHYPNEA) != 0, "Tachypnea flag must be set");
    TEST_ASSERT((b.red_flags_mask & RED_FLAG_SEVERE_HYPOXIA) != 0, "Hypoxia flag must be set");
    TEST_ASSERT((b.red_flags_mask & RED_FLAG_SEVERE_HYPOTEN) != 0, "Hypotension flag must be set");
    TEST_ASSERT((b.red_flags_mask & RED_FLAG_SEVERE_TACHY) != 0, "Tachycardia flag must be set");
    TEST_ASSERT((b.red_flags_mask & RED_FLAG_ACUTE_NEURO_DROP) != 0, "Neuro drop flag must be set");
}

void test_single_parameter_extreme_red_flag_escalation(void) {
    /* Patient is normal on everything EXCEPT severe bradycardia (HR 38 bpm) */
    news2_breakdown_t b;
    news2_status_t status = news2_calculate(
        16,           /* RR 16 bpm (0) */
        98.0f,        /* SpO2 98% (0) */
        OXYGEN_ROOM_AIR, /* Air (0) */
        125,          /* SBP 125 mmHg (0) */
        38,           /* HR 38 bpm (3) -> Extreme Bradycardia */
        CONSCIOUSNESS_ALERT, /* Alert (0) */
        36.8f,        /* Temp 36.8 C (0) */
        &b
    );

    TEST_ASSERT(status == NEWS2_OK, "Calculation must succeed");
    TEST_ASSERT(b.total_score == 3, "Total score is 3");
    TEST_ASSERT(b.alert_level == ALERT_LEVEL_CRITICAL, "Single score of 3 MUST trigger ALERT_LEVEL_CRITICAL per RCP rules");
    TEST_ASSERT((b.red_flags_mask & RED_FLAG_SEVERE_BRADY) != 0, "Severe bradycardia flag must be set");
}

void test_exact_boundary_thresholds(void) {
    news2_breakdown_t b;

    /* Pulse 40 (score 3) vs 41 (score 1) */
    news2_calculate(16, 98.0f, OXYGEN_ROOM_AIR, 120, 40, CONSCIOUSNESS_ALERT, 37.0f, &b);
    TEST_ASSERT(b.pulse_score == 3, "HR 40 must score 3");

    news2_calculate(16, 98.0f, OXYGEN_ROOM_AIR, 120, 41, CONSCIOUSNESS_ALERT, 37.0f, &b);
    TEST_ASSERT(b.pulse_score == 1, "HR 41 must score 1");

    /* Systolic BP 90 (score 3) vs 91 (score 2) */
    news2_calculate(16, 98.0f, OXYGEN_ROOM_AIR, 90, 75, CONSCIOUSNESS_ALERT, 37.0f, &b);
    TEST_ASSERT(b.systolic_bp_score == 3, "SBP 90 must score 3");

    news2_calculate(16, 98.0f, OXYGEN_ROOM_AIR, 91, 75, CONSCIOUSNESS_ALERT, 37.0f, &b);
    TEST_ASSERT(b.systolic_bp_score == 2, "SBP 91 must score 2");

    /* Temp 35.0 (score 3) vs 35.1 (score 1) */
    news2_calculate(16, 98.0f, OXYGEN_ROOM_AIR, 120, 75, CONSCIOUSNESS_ALERT, 35.0f, &b);
    TEST_ASSERT(b.temperature_score == 3, "Temp 35.0 must score 3");

    news2_calculate(16, 98.0f, OXYGEN_ROOM_AIR, 120, 75, CONSCIOUSNESS_ALERT, 35.1f, &b);
    TEST_ASSERT(b.temperature_score == 1, "Temp 35.1 must score 1");
}

void test_physiological_bounds_rejection(void) {
    news2_breakdown_t b;

    /* SBP 10 mmHg (impossible/detached lead) */
    news2_status_t s1 = news2_calculate(16, 98.0f, OXYGEN_ROOM_AIR, 10, 75, CONSCIOUSNESS_ALERT, 37.0f, &b);
    TEST_ASSERT(s1 == NEWS2_ERR_PHYSIOLOGICAL_OUT_OF_BOUNDS, "SBP 10 must be rejected");

    /* SpO2 105% (impossible percentage) */
    news2_status_t s2 = news2_calculate(16, 105.0f, OXYGEN_ROOM_AIR, 120, 75, CONSCIOUSNESS_ALERT, 37.0f, &b);
    TEST_ASSERT(s2 == NEWS2_ERR_PHYSIOLOGICAL_OUT_OF_BOUNDS, "SpO2 > 100 must be rejected");

    /* Heart rate 350 bpm */
    news2_status_t s3 = news2_calculate(16, 98.0f, OXYGEN_ROOM_AIR, 120, 350, CONSCIOUSNESS_ALERT, 37.0f, &b);
    TEST_ASSERT(s3 == NEWS2_ERR_PHYSIOLOGICAL_OUT_OF_BOUNDS, "HR > 300 must be rejected");
}

void test_crc32_checksum(void) {
    const char *test_str = "MEDORQIS_QNX_8_0_SAFETY_ENGINE";
    uint32_t crc = medorqis_crc32((const uint8_t*)test_str, strlen(test_str));
    TEST_ASSERT(crc != 0, "CRC32 must calculate non-zero value");

    /* Verify deterministic property: same input gives exact same CRC */
    uint32_t crc2 = medorqis_crc32((const uint8_t*)test_str, strlen(test_str));
    TEST_ASSERT(crc == crc2, "CRC32 must be strictly deterministic");
}

int main(void) {
    printf("======================================================================\n");
    printf("MEDORQIS-QNX DETERMINISTIC NEWS2 & SAFETY ENGINE UNIT TEST SUITE\n");
    printf("Standard: Royal College of Physicians (RCP 2017) / IEC 62304 Class C\n");
    printf("======================================================================\n");

    test_baseline_normal_patient();
    test_early_deterioration_medium_risk();
    test_fulminant_septic_shock_critical();
    test_single_parameter_extreme_red_flag_escalation();
    test_exact_boundary_thresholds();
    test_physiological_bounds_rejection();
    test_crc32_checksum();

    printf("\nAll Tests Complete: %d/%d passed (100.0%%)\n", g_tests_passed, g_tests_run);
    printf("======================================================================\n");

    return 0;
}
