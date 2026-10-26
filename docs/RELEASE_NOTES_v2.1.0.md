# MedOrqis v2.1.0 — Production Medical AI Skills Ecosystem

[![Verification: 100% Passed](https://img.shields.io/badge/Verification-100%25%20Passed-brightgreen.svg)](https://github.com/seotarek/MedOrqis/blob/main/tests/reports/VERIFICATION_REPORT.md)
[![Safety: IEC 62304 / ISO 14971](https://img.shields.io/badge/Safety%20Class-Class%20A%20%7C%20B%20%7C%20C-red.svg)](https://github.com/seotarek/MedOrqis/blob/main/SAFETY_AND_GOVERNANCE.md)
[![Skills: 24 Registered](https://img.shields.io/badge/Skills-24%20Medical%20Skills-teal.svg)](https://github.com/seotarek/MedOrqis/tree/main/skills)
[![Live Catalog](https://img.shields.io/badge/Catalog-GitHub%20Pages-blue.svg)](https://seotarek.github.io/MedOrqis/)

**MedOrqis v2.1.0** is an evidence-grounded, zero-token medical AI skills ecosystem designed for multi-agent workflows, clinical decision support (CDS), and real-time medical governance.

---

## ⚡ What's New in v2.1.0

### 1. Deterministic Pediatric & Risk Calculators (`core/clinical_calculators.py`)
- **Bedside Schwartz Pediatric eGFR**: Exact implementation ($0.413 \times \text{Height} / \text{SCr}$) with strict pediatric gating ($\text{age} < 18$).
- **HAS-BLED Bleeding Risk Score**: Validated score for patients with Atrial Fibrillation (0–9 points) identifying reversible risk factors.
- **NEWS2 General Inpatient Deterioration Score**: 7 vital parameter scoring with acute emergency threshold triggering.
- **Hardened CURB-65**: Enforces physiological plausibility bounds (RR: 0–100 bpm, SBP: 21–350 mmHg) and rejects pediatric patients.

### 2. Critical Drug-Drug Interaction (DDI) Engine (`core/safety_guardrails.py`)
- Real-time deterministic detection of fatal contraindications:
  - Warfarin + NSAID (synergistic gastrointestinal hemorrhage hazard)
  - DOAC (Apixaban) + NSAID (Diclofenac)
  - Sildenafil + Nitroglycerin (catastrophic refractory hypotension)
  - Spironolactone + ACE-Inhibitor (fatal hyperkalemia)
  - Pregnancy Category X Teratogens
- Regional trade brand name mapping to INN across Egyptian, Saudi/Gulf, Levantine, Maghrebi, and International markets.

### 3. Clause-Boundary Negation Polarity Engine (`core/terminology_normalizer.py`)
- Prevents false negation propagation to affirmed symptoms using bounded clause stoppers (`لكن`, `إلا`, `بينما`, `بل`, `but`, `however`, `mais`, `pero`) with a 5-word scope window.
- 100% negation preservation verified across 34 clinical benchmark cases in 8 languages and dialects (MSA, Egyptian, Gulf, Levantine, Maghrebi, English, French, Spanish).

### 4. Epistemic Provenance Rule Enforcement
- Architectural block against dosing or irreversible treatment recommendations based on AI hypotheses (`MODEL_INFERRED_HYPOTHESIS`) or empty provenance. High-risk interventions strictly require confirmed `DOCUMENTED_CLINICAL_RECORD` provenance.

### 5. Multi-Platform Adapters & Standards Compliance
- **Skills CLI (`npx skills`)**: Fully registered 24 skills with scalar `allowed-tools: bash`.
- **OpenAI Structured Outputs**: Function tools enforce `"strict": true` and `"additionalProperties": false`.
- **Model Context Protocol (MCP)**: Live JSON-RPC 2.0 stdio server (`mcp_server/medorqis_mcp_server.py`) exposing deterministic calculators, DDI screening, and prompt defense tools.
- **Gemini CLI Extension**: Manifests and custom slash commands configured.
- **Interactive Web Catalog**: Live on [https://seotarek.github.io/MedOrqis/](https://seotarek.github.io/MedOrqis/).

---

## 📦 Quick Installation

### Skills CLI (`npx skills`)
```bash
# Install the entire ecosystem
npx skills add seotarek/MedOrqis

# Or install specific specialized skills
npx skills add seotarek/MedOrqis --skill emergency-triage-redflags
npx skills add seotarek/MedOrqis --skill pharmacology-dosing-interactions
npx skills add seotarek/MedOrqis --skill pediatrics-neonatology
```

### Model Context Protocol (MCP) Server
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "medorqis": {
      "command": "python3",
      "args": ["/path/to/MedOrqis/mcp_server/medorqis_mcp_server.py"]
    }
  }
}
```

---

## 🧪 Automated Verification Evidence
- **Total Tests**: `31/31 passed` (**100.0% Pass Rate** in 0.1s).
- **Clinical Governance**: ISO 14971 / IEC 62304 compliant registry with SHA-256 integrity hashing.
