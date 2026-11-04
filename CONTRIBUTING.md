# Contributing to MedOrqis

Thank you for your interest in contributing to **MedOrqis** — the evidence-grounded, zero-token medical AI skills ecosystem!

MedOrqis is engineered under strict clinical risk management principles informed by **IEC 62304** (Medical device software life cycle processes) and **ISO 14971** (Application of risk management to health software). To maintain mathematical invariance and patient safety, all contributions must adhere to the engineering standards detailed below.

---

## 🏛️ Core Architectural Principles

1. **The Zero-Token Arithmetic Rule**:
   - **Clinical arithmetic, dosing formulas, and risk stratification scores MUST NEVER be computed by LLM prompt generation or chain-of-thought heuristics.**
   - All calculations must reside in pure, transparent Python functions in `core/clinical_calculators.py` with zero external API token overhead.

2. **The Epistemic Provenance Rule**:
   - Data in MedOrqis carries an explicit epistemic status: `DOCUMENTED_CLINICAL_RECORD`, `DETERMINISTIC_CALCULATION`, `PATIENT_REPORTED`, or `MODEL_INFERRED_HYPOTHESIS`.
   - High-risk clinical interventions or dosing adjustments are **strictly prohibited** from acting upon `MODEL_INFERRED_HYPOTHESIS` without human clinician verification.

3. **Fail-Closed Safe Abstention**:
   - Missing mandatory variables (such as patient age or weight) or out-of-bounds parameters must raise a typed `SafeCalculationRefusal` resulting in a `SAFE_ABSTENTION_DATA_DEFICIT` payload.
   - The engine must **never** assume default placeholder values (e.g., assuming an adult age of 30).

4. **Two-Axis Governance Separation**:
   - Automated unit and benchmark tests prove **algorithmic code invariance (100%)**, NOT real-world bedside clinical safety.
   - Institutional clinical trial validation remains formally decoupled until human hospital ethics board sign-off.

---

## 🧮 Contributing a New Clinical Calculator

When adding a clinical equation (e.g., MELD-Na, TIMI, GCS, APACHE) to `core/clinical_calculators.py`:

### 1. Function Contract Requirements
Every calculator function must return a `CalculationResult` dataclass and enforce:
- **Guideline Citation & Year**: Include primary peer-reviewed literature with DOI or PubMed ID.
- **Population Boundary Checks**: If an equation is adult-only, enforce `age < 18` refusal; if pediatric, enforce `age >= 18` refusal.
- **Physiological Sanity Limits**: Define hard lower and upper bounds (e.g., serum creatinine, heart rate, blood pressure).
- **Missing Parameter Handling**: Reject incomplete calls via `SafeCalculationRefusal`.

### 2. Unit Testing Requirement
Add rigorous test cases to `tests/unit/test_clinical_calculators.py` covering:
- Standard known clinical baseline (hand-calculated fixture).
- Boundary conditions (exact cutoffs for risk tiers).
- Extreme physiological out-of-bounds inputs.
- Safe refusal triggers (missing parameter or wrong age group).

---

## 🛠️ Verification Workflow (Mandatory Before PR)

Before opening a Pull Request, execute the two verification commands locally:

```bash
# 1. Verify SHA-256 cryptographic file integrity manifest
python3 core/integrity_manifest.py --verify

# 2. Run the harmonized clinical test suite (all 36 tests must pass 100%)
python3 tests/run_all_tests.py
```

If you modified or added core clinical files or dictionaries, regenerate the cryptographic manifest:
```bash
python3 core/integrity_manifest.py --generate
```

---

## 📋 Pull Request Checklist

When submitting a PR, ensure your submission includes:
- [ ] Clear description of the clinical rationale and guideline authority.
- [ ] Pure deterministic implementation (zero LLM token math).
- [ ] Comprehensive automated unit tests with physiological boundaries.
- [ ] Updated `SKILLS.md` and `skills.sh.json` if a new skill was introduced.
- [ ] Successful execution of `python3 tests/run_all_tests.py` (100% pass rate).
- [ ] Updated cryptographic manifest via `python3 core/integrity_manifest.py --verify`.
- [ ] Zero API keys, proprietary tokens, or private medical records (PHI) included.

---

## 💬 Community & Clinical Safety Inquiries
- For urgent patient safety or guideline discrepancy inquiries, open an issue using the **Clinical Safety Incident** template.
- For feature discussions and clinical architecture ideas, participate in [GitHub Discussions](https://github.com/seotarek/MedOrqis/discussions).
