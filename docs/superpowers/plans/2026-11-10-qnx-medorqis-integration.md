# MedOrqis – QNX Global Hackathon 2026 Integration: Implementation Plan

> **For agentic workers:** Implementation plan for QNX Neutrino RTOS 8.0 & MedOrqis integration.
> **Goal:** Build, verify, and demonstrate a production-grade, zero-allocation embedded QNX Neutrino RTOS 8.0 integration layer for MedOrqis, enabling real-time detection of acute patient deterioration with deterministic safety alarms and bilingual AI clinical explanation.
> **Architecture:** Pure C99 embedded deterministic edge (QNX microkernel / POSIX PSE54) decoupled from Python clinical AI advisory (MedOrqis Core + MedOrqis-LLM).
> **Tech Stack:** C99, POSIX, QNX Neutrino RTOS 8.0 APIs, Python 3, PyTorch/Transformers (Karnak-6B QLoRA), Sockets/JSON-RPC.

## Global Constraints
- Target QNX Neutrino RTOS 8.0 while preserving 100% Linux host POSIX buildability.
- Royal College of Physicians NEWS2 (2017) clinical formula; no invented numbers.
- Zero dynamic memory allocation in the embedded C inner loops.
- Strict IEC 62304 / ISO 14971 separation: Class C deterministic alarms vs Class A/B AI advisory.
- Never claim QNX compatibility without automated tests and verified build targets.

---

## Tasks Overview
1. Create `qnx_edge/include/` headers (`vitals_types.h`, `qnx_compat.h`, `news2_deterministic.h`, `vitals_acq.h`, `patient_simulator.h`).
2. Implement `qnx_edge/src/news2_deterministic.c` with zero dynamic allocation and extreme red-flag bitmasks.
3. Create `qnx_edge/tests/test_news2_deterministic.c` and standalone `Makefile`. Compile and execute C unit tests.
4. Implement `qnx_edge/src/patient_simulator.c` (multi-scenario physiological state machine).
5. Implement `qnx_edge/src/vitals_acq.c` (timer-driven acquisition, QNX channels/pulses & POSIX socket emission).
6. Implement `qnx_edge/src/qnx_monitor_main.c` (interactive bedside TUI with ANSI color telemetry and alarm indicators).
7. Implement `qnx_edge/bridge/qnx_medorqis_bridge.py` (binary packet deserialization, CRC verification, PHI scrubbing, double-check validation with `core/clinical_calculators.py`).
8. Implement `qnx_edge/bridge/clinical_advisory.py` (MedOrqis-LLM prompt orchestration, Sepsis Six clinical bundles, bilingual English/Arabic ISBAR handover report generator).
9. Create `qnx_edge/tests/test_qnx_bridge.py` and run end-to-end socket bridge test suite.
10. Build `qnx_edge/scripts/run_qnx_demo.sh` for one-click demonstration of the acute septic shock decompensation scenario.
11. Build `qnx_edge/scripts/run_tests.sh` and verify all C and Python tests pass with 100% success rate.
12. Author `qnx_edge/README.md`, `qnx_edge/SAFETY_AND_REGULATORY_MAPPING.md`, and `qnx_edge/HACKATHON_SUBMISSION.md`.
13. Execute end-to-end verification, verify git cleanliness, and document complete results in `walkthrough.md`.
