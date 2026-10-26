# MedOrqis — Automated Verification Report (v2.1.1)

**Execution Timestamp**: `2026-10-26T22:57:27.229344+00:00`  
**Release Tag**: `v2.1.1`  
**Base Commit**: `40fd05d5150850ad67fe3ca2f6254f86c3965d1d`  
**Overall Automated Status**: **ALL_TESTS_PASSED (100.0% Pass Rate)**  
**Total Tests**: `36/36` passed  
**Clinical Review Status**: `PENDING_INSTITUTIONAL_CLINICAL_SIGN_OFF` (Decoupled Governance Policy)

> [!IMPORTANT]
> **Regulatory & Clinical Safety Separation Statement**:
> 100% automated software verification proves mathematical fidelity, boundary condition enforcement, and syntactic invariance against specified unit tests. It **DOES NOT** constitute human clinical certification, medical device clearance (SaMD), or IRB-approved clinical efficacy. Bedside deployment strictly requires licensed institutional clinician review and site-specific clinical governance approval.

> [!NOTE]
> **Git Merkle DAG Provenance Notice**:
> In Git, a tracked file within a commit cannot record the hash of the commit that contains it prior to its creation. MedOrqis canonically pins releases via Git Release Tags (`v2.1.1`). Continuous Integration dynamically executes this test suite on every git push, verifying the exact runtime commit SHA and logging evidence directly in [GitHub Actions CI](https://github.com/seotarek/MedOrqis/actions/workflows/ci.yml).

---

## 1. Automated Test Suite Summary Matrix (Programmatic CI)

| Test Suite | Target Module | Scope & Scenarios Verified | Tests Run | Pass Rate | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Deterministic Clinical Engine & Boundary Tests** | `core/clinical_calculators.py` | CHA2DS2-VA (ESC 2024 sex neutrality vs AHA 2023), CKD-EPI 2021 (adult vs pediatric refusal), Bedside Schwartz pediatric eGFR, Cockcroft-Gault (IBW/AdjBW in obesity), Pediatric Dose Capping, HAS-BLED, NEWS2, CURB-65 physiological bounds, Wells DVT & PE. | 12 | 100.0% | **PASSED** |
| **2. Clinical Safety Guardrails & Epistemic Provenance Tests** | `core/safety_guardrails.py & core/context_validator.py` | Epistemic provenance lockdown (hypothesis dosing refusal, empty provenance refusal), missing age gatekeeper, sentinel emergency triggers (Stroke FAST, ACS crushing chest pain, anaphylaxis, match_mode ANY), red-flag female atypical MI, anticoagulation + GI bleed conflict, critical DDI screening (Warfarin + NSAID, Apixaban + Diclofenac, Sildenafil + Nitroglycerin), negated symptom filtering. | 11 | 100.0% | **PASSED** |
| **3. Multilingual Semantic Invariance & Dialect Benchmark** | `core/terminology_normalizer.py` | Negation preservation with clause-stop boundaries across 126 curated test cases (MSA, Egyptian, Gulf, Levantine, Maghrebi, EN, FR, ES), BiDi numeric/unit fidelity (mg, mcg, g), regional trade brand-to-INN mapping. | 3 | 100.0% | **PASSED** |
| **4. Security, PHI Redaction, Citation & Platform Adapter Tests** | `core/ & mcp_server/ & adapters/ & skills/` | SHA-256 cryptographic file integrity manifest (45 files: 24 skills, 11 core modules, dictionaries), PHI scrubbing (Egypt NID 14d, Saudi Iqama 10d, MRN), prompt injection defense, 2-stage citation entailment & population mismatch, live stdio MCP JSON-RPC contract, OpenAI strict parameters, scalar allowed-tools frontmatter in all 24 skills. | 10 | 100.0% | **PASSED** |
| **TOTAL** | **Entire Ecosystem** | **End-to-End Automated Verification** | **36** | **100.0%** | **ALL_TESTS_PASSED** |

---

## 2. Two-Axis Governance & Clinical Status Separation

In accordance with ISO 14971 Risk Management and IEC 62304 Medical Device Software Architecture:

| Governance Axis | Current Status | Verification Authority | Clinical Impact & Next Steps |
| :--- | :--- | :--- | :--- |
| **Axis 1: Algorithmic & Deterministic Code Verification** | **100% COMPLETE & PASSING** | Automated Master Test Runner (`tests/run_all_tests.py`) & GitHub Actions CI | Confirms zero calculation hallucinations, proper boundary refusals, deterministic unit preservation, and zero token runtime overhead. |
| **Axis 2: Human Institutional Clinical Review** | **PENDING_INSTITUTIONAL_SIGN_OFF** | Licensed Clinical Specialists & Institutional Ethics Board (IRB) | Clinical deployment at bedside requires institutional clinician sign-off, local formulary calibration, and simulated clinical station testing. Registered in `governance/clinical_review_registry.json`. |

---

## 3. Cryptographic File Integrity & Provenance Manifest

To detect unauthorized tampering, silent code corruption, or unrecorded skill changes:
- All 24 skill specifications (`skills/*/SKILL.md`), 11 core engine modules (`core/*.py`), 5 clinical dictionaries, and schemas are hashed using **SHA-256**.
- Verified dynamically by `core/integrity_manifest.py --verify` and covered in Test Suite 4.
- Official cryptographic manifest: [`governance/file_integrity_manifest.json`](../../governance/file_integrity_manifest.json).

---

## 4. Medical Disclaimer & Non-Device Status
MedOrqis is an open-source clinical reference architecture and research framework. It is **NOT** a certified Medical Device (SaMD) and does not autonomously diagnose, triage, or prescribe. Clinical Decision Support outputs must always be reviewed by a licensed healthcare professional. See [MEDICAL_DISCLAIMER.md](../../MEDICAL_DISCLAIMER.md) and [SAFETY_AND_GOVERNANCE.md](../../SAFETY_AND_GOVERNANCE.md).
