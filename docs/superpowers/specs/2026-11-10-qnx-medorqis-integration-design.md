# MedOrqis – QNX Global Hackathon 2026 Integration Design Specification

**Document Identifier**: `SPEC-MEDORQIS-QNX-2026-V1`  
**Date**: November 10, 2026  
**Status**: APPROVED by User ("ابدا")  
**Authors**: Senior QNX Systems Architect, Medical AI Engineer, Embedded Developer, Healthcare Safety Specialist  
**Target Platform**: QNX Neutrino RTOS 8.0 / POSIX PSE54 & Linux Host Simulation  
**Repository Location**: `docs/superpowers/specs/2026-11-10-qnx-medorqis-integration-design.md`

---

## 1. Executive Summary & Problem Definition

During acute inpatient hospitalization, unexpected clinical deterioration (such as developing **Septic Shock**, **Acute Respiratory Failure**, or **Postoperative Hemorrhagic Shock**) remains a leading cause of preventable mortality and unplanned ICU admissions. 

While bedside physiological sensors (ECG, pulse oximeters, non-invasive blood pressure cuffs) sample patient vital signs continuously, contemporary hospital systems suffer from two systemic failures:
1. **Alarm Fatigue & Siloed Thresholds**: Standard monitors alarm on individual parameter limits without composite clinical context, leading clinicians to desensitize to frequent false alarms.
2. **Delayed Intervention**: Subtle multisystem deterioration patterns are frequently recognized hours after the therapeutic window for early fluid resuscitation or antimicrobial therapy has elapsed.

**MedOrqis-QNX** solves this challenge by bridging **hard real-time deterministic embedded computing (QNX Neutrino RTOS 8.0)** with **clinical-grade medical AI intelligence (MedOrqis Core & MedOrqis-LLM)**.

---

## 2. Core Philosophy: Strict Deterministic & Probabilistic Separation

Under **IEC 62304** (Medical Device Software Life Cycle) and **ISO 14971** (Application of Risk Management to Medical Devices), medical software is classified according to hazard severity:
- **Class C (Life-Safety / Potential Death or Serious Injury)**: Real-time physiological signal acquisition, deterministic scoring, and local emergency alert generation.
- **Class A/B (Clinical Decision Support / Non-controlling Advisory)**: Secondary clinical narrative synthesis, diagnostic explanation, and handover documentation.

```
+===================================================================================+
| CLASS C: HARD REAL-TIME DETERMINISTIC EDGE (QNX NEUTRINO RTOS 8.0)                |
| - Zero Dynamic Memory Allocation (malloc/free prohibited in inner loop)           |
| - Hard Latency: < 1 millisecond execution budget                                   |
| - Pure C99 Implementation of Royal College of Physicians NEWS2 Guidelines         |
| - Autonomous Fail-Safe: Functions 100% reliably even if network/cloud is severed   |
+===================================================================================+
                                     │
                        Asynchronous Telemetry Stream 
                        (Non-blocking Decoupled Queue)
                                     ▼
+===================================================================================+
| CLASS A/B: CLINICAL DECISION SUPPORT TIER (MEDORQIS CORE + MEDORQIS-LLM)          |
| - HIPAA / GDPR Automated PHI De-identification                                    |
| - Deterministic Safety Guardrails & Emergency Escalation Checks                   |
| - MedOrqis-LLM (Karnak-6B QLoRA) Bilingual Narrative Interpretation & Handover    |
| - Immutable Audit Logging & Epistemic Attribution                                 |
+===================================================================================+
```

---

## 3. Directory Layout & Repository Structure

All embedded QNX assets reside in a dedicated, first-class subsystem `qnx_edge/` within the root repository:

```
MedOrqis — Medical AI Skills Ecosystem/
├── qnx_edge/                                 # [NEW] QNX 8.0 Integration Layer
│   ├── Makefile                             # Standalone build for Linux & QNX qcc
│   ├── CMakeLists.txt                       # Modern CMake build configuration
│   ├── include/                             # Embedded C/C++ Header Files
│   │   ├── vitals_types.h                   # Packed structs, telemetry protocols, enums
│   │   ├── news2_deterministic.h            # Pure C NEWS2 calculation interface
│   │   ├── vitals_acq.h                     # High-res acquisition & QNX IPC wrappers
│   │   ├── patient_simulator.h              # Clinical trajectory state machine
│   │   └── qnx_compat.h                     # POSIX PSE54 / QNX Neutrino dual-target macros
│   ├── src/                                 # Embedded C Implementations
│   │   ├── news2_deterministic.c            # Zero-allocation NEWS2 scoring engine
│   │   ├── vitals_acq.c                     # POSIX timer_create & QNX pulse/channel logic
│   │   ├── patient_simulator.c              # Sepsis, PE, and baseline physiology generators
│   │   └── qnx_monitor_main.c               # Live TUI/CLI bed-side monitor console
│   ├── bridge/                              # Edge-to-Host Communication Gateway
│   │   ├── __init__.py
│   │   ├── qnx_medorqis_bridge.py           # Socket listener, JSON serializer, MCP client
│   │   └── clinical_advisory.py             # MedOrqis-LLM interpretation & ISBAR reporter
│   ├── tests/                               # Embedded C & Bridge Automated Tests
│   │   ├── test_news2_deterministic.c       # Boundary, fuzzing, and conformance tests (C)
│   │   └── test_qnx_bridge.py               # Python end-to-end integration tests
│   └── scripts/
│       ├── run_qnx_demo.sh                  # Interactive one-click demonstration
│       └── build_qnx_package.sh             # QNX 8.0 cross-compilation packager
├── core/                                    # Existing MedOrqis Deterministic Core
│   └── clinical_calculators.py              # Contains verified calculate_news2_score
├── mcp_server/                              # Existing MedOrqis MCP Server
└── docs/superpowers/specs/                  # Design Specifications
```

---

## 4. Detailed Component Engineering

### 4.1 Data Contracts & Memory Model (`vitals_types.h`)

All data structures are fixed-size, memory-aligned, and endian-safe:

```c
typedef enum {
    ALERT_LEVEL_ROUTINE  = 0,  /* NEWS2 0-4: Ward monitoring (4-6 hourly) */
    ALERT_LEVEL_MEDIUM   = 1,  /* NEWS2 5-6: Urgent bedside review (hourly) */
    ALERT_LEVEL_CRITICAL = 2   /* NEWS2 >= 7 or single red-flag: Immediate ICU/RRT */
} alert_level_t;

typedef enum {
    CONSCIOUSNESS_ALERT = 0,
    CONSCIOUSNESS_CVPU  = 1   /* Confused, Voice, Pain, Unresponsive */
} consciousness_level_t;

typedef struct __attribute__((__packed__)) {
    uint32_t magic_header;             /* 0x4D454451 ("MEDQ") */
    uint32_t sequence_id;              /* Monotonically increasing packet ID */
    uint64_t timestamp_us;             /* POSIX CLOCK_MONOTONIC epoch in microseconds */
    char     patient_id[32];           /* Pseudonymized patient identifier */
    
    /* Physiological Vital Signs */
    uint16_t heart_rate_bpm;           /* 0 - 300 bpm */
    uint16_t systolic_bp_mmhg;         /* 0 - 350 mmHg */
    uint16_t diastolic_bp_mmhg;        /* 0 - 250 mmHg */
    uint16_t respiratory_rate_bpm;     /* 0 - 100 bpm */
    float    spo2_percent;             /* 0.0 - 100.0 % */
    float    temperature_celsius;      /* 25.0 - 45.0 C */
    uint8_t  on_supplemental_oxygen;   /* 0: Room Air, 1: Supplemental O2 */
    uint8_t  consciousness;            /* 0: Alert, 1: CVPU */
    
    /* Computed Scores (Calculated in QNX Edge) */
    uint8_t  news2_score;              /* 0 - 20 */
    uint8_t  alert_level;              /* alert_level_t */
    uint16_t red_flags_mask;           /* Bitmask of triggered extreme parameter limits */
    uint32_t crc32_checksum;           /* Data integrity verification */
} vitals_telemetry_packet_t;
```

### 4.2 Deterministic NEWS2 Engine (`news2_deterministic.c`)

- **Standard**: Royal College of Physicians (RCP) National Early Warning Score 2 (2017).
- **Guarantees**:
  1. No heap allocation (`malloc`, `calloc`, `free` are forbidden).
  2. Pure static lookup and deterministic branching.
  3. Execution latency under 500 nanoseconds per evaluation.
  4. Extreme Red Flag bitmask detection:
     - `BIT_0`: Severe Bradycardia (Pulse <= 40 bpm)
     - `BIT_1`: Severe Tachycardia (Pulse >= 131 bpm)
     - `BIT_2`: Severe Hypotension (Systolic BP <= 90 mmHg)
     - `BIT_3`: Severe Bradypnea (Resp Rate <= 8 bpm)
     - `BIT_4`: Severe Tachypnea (Resp Rate >= 25 bpm)
     - `BIT_5`: Severe Hypoxemia (SpO2 <= 91%)
     - `BIT_6`: Hypothermia (Temp <= 35.0 C)
     - `BIT_7`: Acute Neurological Deterioration (CVPU)

### 4.3 Real-Time Acquisition & IPC (`vitals_acq.c`)

- **POSIX Standard Core**:
  - Uses `timer_create(CLOCK_MONOTONIC)` with an interval of 100 ms (10 Hz sampling rate).
  - Fires POSIX signals / non-blocking signals to wake up the deterministic processing loop.
- **QNX Neutrino 8.0 Native Microkernel Extensions**:
  - On actual QNX (`#ifdef __QNXNTO__`):
    * `ChannelCreate(_NTO_CHF_UNBLOCK)` creates the synchronous IPC channel.
    * `SIGEV_PULSE_INIT` associates high-resolution hardware/kernel timer ticks directly with a QNX pulse (`MsgSendPulse`).
    * The acquisition thread calls `MsgReceivePulse()`, avoiding all thread context thrashing and ensuring deterministic wakeups.
  - On Linux Simulation Host:
    * Equivalent POSIX `timer_create` + `sigwaitinfo()` / `signalfd` abstraction delivering identical tick determinism.

### 4.4 Physiological Deterioration Simulator (`patient_simulator.c`)

Simulates realistic, clinically validated inpatient trajectories:
1. **Scenario 1: Acute Septic Shock Progression**:
   - *Phase 1 (Normal)*: HR 72, BP 120/80, RR 14, SpO2 98%, Temp 37.0°C (NEWS2 = 0).
   - *Phase 2 (SIRS / Early Sepsis)*: HR 102, BP 106/68, RR 22, SpO2 94%, Temp 38.6°C (NEWS2 = 5, Urgent Alert).
   - *Phase 3 (Septic Shock / Multi-organ dysfunction)*: HR 138, BP 78/44, RR 30, SpO2 88%, Temp 39.5°C, Confused (NEWS2 = 15, Critical Emergency Alert).
2. **Scenario 2: Acute Pulmonary Embolism**:
   - Sudden catastrophic drop in SpO2 with acute compensatory tachypnea and tachycardia.
3. **Scenario 3: Stable Post-Operative Baseline**:
   - Physiological fluctuations within safe homeostatic boundaries.

### 4.5 QNX-to-MedOrqis Bridge (`qnx_medorqis_bridge.py`)

- Listens on a local IPC socket (UNIX domain socket or TCP port 5055).
- Reads binary packets, validates CRC32 and magic header `MEDQ`.
- Translates to structured JSON telemetry.
- Invokes MedOrqis Core:
  * Runs `phi_deidentifier.py` to ensure zero patient names or hospital identifiers escape the perimeter.
  * Cross-verifies the C-computed NEWS2 score with `core/clinical_calculators.py:calculate_news2_score` (Double-Check Protocol).
- When `alert_level >= ALERT_LEVEL_MEDIUM`, forwards telemetry packet to `clinical_advisory.py`.

### 4.6 Clinical Advisory & AI Handover Engine (`clinical_advisory.py`)

- Connects to **MedOrqis-LLM** (via local Transformers / Hugging Face pipeline or lightweight fallback server).
- Ingests:
  * Baseline demographics (e.g. 68yo female, post-op day 2, bowel resection).
  * 10-minute vital sign trend vector.
  * Triggered red flags and NEWS2 score.
- Generates:
  * **Clinical Etiology Assessment**: Differential diagnosis ranked by likelihood (Septic Shock vs Acute Pulmonary Embolism vs Hypovolemia).
  * **Guideline Action Protocol**: e.g., "Surviving Sepsis Campaign 2024 / Sepsis Six Bundle":
    1. Deliver high-flow oxygen.
    2. Draw blood cultures prior to antibiotics.
    3. Administer broad-spectrum empiric IV antimicrobials.
    4. Start 30 mL/kg IV crystalloid fluid resuscitation.
    5. Check serum lactate and serial blood gas.
    6. Monitor urine output hourly.
  * **Structured ISBAR Handover Note** in bilingual English and Arabic for immediate transfer to ICU / Rapid Response Team.

---

## 5. Medical Safety & Clinical Governance Boundaries

1. **Autonomous Operation**: The QNX embedded monitor's local alarms (visual terminal strobe, console buzzer signal) trigger independently of whether the AI bridge is active or disconnected.
2. **Advisory Watermark**: All AI-generated text is watermarked:
   > `[MEDORQIS ADVISORY CDS - NOT AN AUTONOMOUS CONTROLLER - CLINICAL REVIEW REQUIRED]`
3. **No Retraining Required**: MedOrqis-LLM (Karnak-6B) remains untouched; its prompt instructions leverage the existing QLoRA weights.

---

## 6. Verification & Automated Test Plan

1. **C Unit Tests (`test_news2_deterministic.c`)**:
   - Validates all 20 NEWS2 score categories.
   - Tests boundary conditions (Pulse 40 vs 41, SBP 90 vs 91, Temp 35.0 vs 35.1).
   - Tests physiological bounds clipping (negative numbers, extreme outliers).
   - Confirms zero dynamic memory allocation.
2. **Python Bridge Tests (`test_qnx_bridge.py`)**:
   - Tests socket serialization and deserialization.
   - Tests CRC32 error detection and packet corruption drop.
   - Tests PHI de-identification and MCP server connectivity.
3. **End-to-End System Integration Test (`run_qnx_demo.sh`)**:
   - Compiles C components with `gcc -Wall -Wextra -O2`.
   - Spawns QNX monitor process and patient simulator.
   - Spawns Bridge daemon.
   - Runs full 60-second septic shock progression.
   - Asserts that:
     1. T=0s: NEWS2 is 0, alert is ROUTINE.
     2. T=15s: NEWS2 is 5, alert transitions to MEDIUM.
     3. T=30s: NEWS2 reaches >= 12, alert transitions to CRITICAL.
     4. AI handover report is synthesized and saved to `reports/qnx_clinical_handover.md`.

---

## 7. QNX Global Hackathon 2026 Submission Artifacts

1. **Devpost Pitch**: "MedOrqis-QNX: Real-Time Life-Critical Vital Monitoring & Edge AI Clinical Deterioration Advisory for QNX 8.0".
2. **Architecture Visualizations**: Embedded SVG / Mermaid diagrams in documentation.
3. **Reproducible Demo**: Self-contained script running on standard Linux environments and ready for deployment on QNX SDP 8.0 target hardware.
