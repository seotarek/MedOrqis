/**
 * MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring System
 * File: qnx_monitor_main.c
 * Description: Interactive bedside telemetry monitor console (TUI) for QNX 8.0 & POSIX.
 * Standards: IEC 62304 Class C (Continuous determinism, high-visibility clinical status).
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include "../include/vitals_types.h"
#include "../include/news2_deterministic.h"
#include "../include/patient_simulator.h"
#include "../include/vitals_acq.h"
#include "../include/qnx_compat.h"

/* ANSI Color Escape Codes */
#define ANSI_RESET   "\033[0m"
#define ANSI_BOLD    "\033[1m"
#define ANSI_RED     "\033[1;31m"
#define ANSI_GREEN   "\033[1;32m"
#define ANSI_YELLOW  "\033[1;33m"
#define ANSI_BLUE    "\033[1;34m"
#define ANSI_MAGENTA "\033[1;35m"
#define ANSI_CYAN    "\033[1;36m"
#define ANSI_WHITE   "\033[1;37m"
#define ANSI_BG_RED  "\033[41;1;37m"

static volatile bool g_running = true;

static void sigint_handler(int sig) {
    (void)sig;
    g_running = false;
}

static void print_header(const char *scenario_name, const char *patient_id, int port) {
    printf("\033[2J\033[H"); /* Clear screen & move cursor to top-left */
    printf("%s================================================================================%s\n", ANSI_CYAN, ANSI_RESET);
    printf("%s   MEDORQIS-QNX :: Real-Time Life-Critical Bedside Telemetry Monitor%s\n", ANSI_BOLD, ANSI_RESET);
    printf("%s   Target RTOS: QNX Neutrino 8.0 / POSIX PSE54  |  Port: %d%s\n", ANSI_CYAN, port, ANSI_RESET);
    printf("%s================================================================================%s\n", ANSI_CYAN, ANSI_RESET);
    printf(" Patient ID: %s%-16s%s | Scenario: %s%s%s\n", ANSI_WHITE, patient_id, ANSI_RESET, ANSI_YELLOW, scenario_name, ANSI_RESET);
    printf(" Standard: Royal College of Physicians NEWS2 (2017) | Deterministic Hard Real-Time\n");
    printf("--------------------------------------------------------------------------------\n\n");
}

static void render_telemetry_frame(
    const vitals_telemetry_packet_t *pkt,
    const news2_breakdown_t *b,
    uint32_t step,
    uint32_t total_steps
) {
    /* Move cursor to line 7 to update telemetry smoothly */
    printf("\033[7;1H");

    /* Alert Banner */
    if (b->alert_level == ALERT_LEVEL_CRITICAL) {
        printf("%s  >>> CRITICAL EMERGENCY ALARM: RAPID RESPONSE ESCALATION REQUIRED <<<  %s\n\n", ANSI_BG_RED, ANSI_RESET);
    } else if (b->alert_level == ALERT_LEVEL_MEDIUM) {
        printf("%s  [!] URGENT CLINICAL ALERT: BEDSIDE REVIEW REQUIRED (HOURLY OBS) [!]  %s\n\n", ANSI_YELLOW, ANSI_RESET);
    } else {
        printf("%s  [OK] ROUTINE WARD MONITORING: CLINICAL VITALS STABLE (Q4-6H OBS)      %s\n\n", ANSI_GREEN, ANSI_RESET);
    }

    /* Primary Vital Signs Matrix */
    const char *hr_color = (pkt->heart_rate_bpm <= 40 || pkt->heart_rate_bpm >= 131) ? ANSI_RED :
                           (pkt->heart_rate_bpm <= 50 || pkt->heart_rate_bpm >= 91) ? ANSI_YELLOW : ANSI_GREEN;
    const char *bp_color = (pkt->systolic_bp_mmhg <= 90 || pkt->systolic_bp_mmhg >= 220) ? ANSI_RED :
                           (pkt->systolic_bp_mmhg <= 110) ? ANSI_YELLOW : ANSI_GREEN;
    const char *rr_color = (pkt->respiratory_rate_bpm <= 8 || pkt->respiratory_rate_bpm >= 25) ? ANSI_RED :
                           (pkt->respiratory_rate_bpm >= 21) ? ANSI_YELLOW : ANSI_GREEN;
    const char *ox_color = (pkt->spo2_percent <= 91.0f) ? ANSI_RED :
                           (pkt->spo2_percent <= 95.0f) ? ANSI_YELLOW : ANSI_GREEN;
    const char *temp_color = (pkt->temperature_celsius <= 35.0f || pkt->temperature_celsius >= 39.1f) ? ANSI_RED :
                             (pkt->temperature_celsius >= 38.1f) ? ANSI_YELLOW : ANSI_GREEN;

    printf("+------------------------------------------------------------------------------+\n");
    printf("| %-18s | %-16s | %-16s | %-17s |\n", "VITAL PARAMETER", "CURRENT READING", "NEWS2 POINTS", "PHYSIOLOGY STATE");
    printf("+------------------------------------------------------------------------------+\n");
    printf("| Heart Rate (HR)    | %s%3d bpm%s          | %-16d | %-17s |\n",
           hr_color, pkt->heart_rate_bpm, ANSI_RESET, b->pulse_score,
           (pkt->heart_rate_bpm >= 131) ? "Severe Tachy" : (pkt->heart_rate_bpm <= 40) ? "Severe Brady" : "Normal/Mild");

    printf("| Systolic BP (NIBP) | %s%3d/%-3d mmHg%s     | %-16d | %-17s |\n",
           bp_color, pkt->systolic_bp_mmhg, pkt->diastolic_bp_mmhg, ANSI_RESET, b->systolic_bp_score,
           (pkt->systolic_bp_mmhg <= 90) ? "Hypotension!" : (pkt->systolic_bp_mmhg >= 140) ? "Elevated" : "Adequate");

    printf("| Resp Rate (RR)     | %s%3d bpm%s          | %-16d | %-17s |\n",
           rr_color, pkt->respiratory_rate_bpm, ANSI_RESET, b->respiration_score,
           (pkt->respiratory_rate_bpm >= 25) ? "Tachypnea!" : (pkt->respiratory_rate_bpm <= 8) ? "Bradypnea!" : "Eupneic");

    printf("| Oxygen Sat (SpO2)  | %s%5.1f %% %s         | %-16d | %-17s |\n",
           ox_color, pkt->spo2_percent, ANSI_RESET, b->spo2_score,
           (pkt->spo2_percent <= 91.0f) ? "Severe Hypoxia" : (pkt->spo2_percent <= 95.0f) ? "Mild Hypoxia" : "Acceptable");

    printf("| Supplemental O2    | %-16s | %-16d | %-17s |\n",
           (pkt->on_supplemental_oxygen) ? "O2 Mask (High)" : "Room Air", b->oxygen_score,
           (pkt->on_supplemental_oxygen) ? "Prescribed" : "Ambient");

    printf("| Body Temperature   | %s%5.1f C%s          | %-16d | %-17s |\n",
           temp_color, pkt->temperature_celsius, ANSI_RESET, b->temperature_score,
           (pkt->temperature_celsius >= 39.1f) ? "Pyrexia/Fever" : (pkt->temperature_celsius <= 35.0f) ? "Hypothermia" : "Normothermic");

    printf("| Neurological/Consc | %-16s | %-16d | %-17s |\n",
           (pkt->consciousness == CONSCIOUSNESS_ALERT) ? "Alert (A)" : "CVPU (Confused)", b->consciousness_score,
           (pkt->consciousness == CONSCIOUSNESS_ALERT) ? "Intact" : "Acute Change!");
    printf("+------------------------------------------------------------------------------+\n");

    /* Summary Bar */
    const char *score_color = (b->total_score >= 7) ? ANSI_RED : (b->total_score >= 5) ? ANSI_YELLOW : ANSI_GREEN;
    const char *status_text = (b->alert_level == ALERT_LEVEL_CRITICAL) ? ANSI_RED "HIGH CLINICAL RISK (EMERGENCY)" :
                              (b->alert_level == ALERT_LEVEL_MEDIUM) ? ANSI_YELLOW "MEDIUM CLINICAL RISK (URGENT)" :
                              ANSI_GREEN "LOW CLINICAL RISK (ROUTINE)";

    printf("\n%sTOTAL NEWS2 COMPOSITE SCORE: %s%2d / 20%s  |  Status: %s%s\n",
           ANSI_BOLD, score_color, b->total_score, ANSI_RESET, status_text, ANSI_RESET);

    /* Protocol Recommendation */
    printf("Guideline Action: %s%s%s\n", ANSI_WHITE, news2_get_escalation_protocol(b->alert_level), ANSI_RESET);

    /* Telemetry Performance & Latency */
    printf("\nTelemetry Progress: Step %u / %u | Execution Latency: %s%u ns%s | CRC32: 0x%08X\n",
           step, total_steps, ANSI_CYAN, pkt->calculation_latency_ns, ANSI_RESET, pkt->crc32_checksum);

    fflush(stdout);
}

int main(int argc, char **argv) {
    signal(SIGINT, sigint_handler);
    signal(SIGTERM, sigint_handler);

    clinical_scenario_t scenario = SCENARIO_SEPTIC_SHOCK;
    uint32_t total_steps = 60;
    uint32_t step_delay_ms = 150;
    int port = MEDORQIS_DEFAULT_PORT;
    const char *patient_id = "PAT-ICU-084";

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--scenario") == 0 && i + 1 < argc) {
            if (strcmp(argv[i+1], "pe") == 0) scenario = SCENARIO_PULMONARY_EMBOLISM;
            else if (strcmp(argv[i+1], "stable") == 0) scenario = SCENARIO_STABLE_POSTOP;
            else scenario = SCENARIO_SEPTIC_SHOCK;
            i++;
        } else if (strcmp(argv[i], "--steps") == 0 && i + 1 < argc) {
            total_steps = (uint32_t)atoi(argv[++i]);
        } else if (strcmp(argv[i], "--delay") == 0 && i + 1 < argc) {
            step_delay_ms = (uint32_t)atoi(argv[++i]);
        } else if (strcmp(argv[i], "--port") == 0 && i + 1 < argc) {
            port = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--patient") == 0 && i + 1 < argc) {
            patient_id = argv[++i];
        }
    }

    patient_simulator_t sim;
    patient_simulator_init(&sim, patient_id, scenario, total_steps);

    vitals_acq_engine_t engine;
    if (vitals_acq_engine_init(&engine, port) < 0) {
        fprintf(stderr, "Failed to initialize acquisition engine\n");
        return 1;
    }

    print_header(patient_simulator_get_scenario_name(scenario), patient_id, port);

    vitals_telemetry_packet_t packet;
    news2_breakdown_t breakdown;

    while (g_running && !sim.is_completed) {
        if (!patient_simulator_step(&sim, &packet)) {
            break;
        }

        vitals_acq_process_sample(&engine, &packet, &breakdown);
        render_telemetry_frame(&packet, &breakdown, sim.current_step, total_steps);

        qnx_sleep_ms(step_delay_ms);
    }

    vitals_acq_engine_shutdown(&engine);

    printf("\n%s[MONITOR STOPPED] Acquisition terminated successfully.%s\n", ANSI_CYAN, ANSI_RESET);
    printf("Total Packets Transmitted: %u | Emergency Alarms Fired: %u | Max Latency: %lu ns\n",
           engine.packets_sent, engine.emergency_alarms_triggered, (unsigned long)engine.max_latency_ns);

    return 0;
}
