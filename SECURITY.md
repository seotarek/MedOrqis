# Security & Clinical Safety Policy

## Clinical AI Risk Classification (IEC 62304 / ISO 14971)

MedOrqis implements deterministic safety guardrails across 24 risk-stratified clinical skills:
- **Class A (Low Risk)**: Medical vocabulary, terminology lookup, diacritization, clinical abbreviation normalization.
- **Class B (Moderate Risk)**: Patient triage heuristics, lab result normalization, multilingual clinical negation benchmarking.
- **Class C (High Risk)**: Zero-token deterministic clinical calculators (ESC 2024 CHA₂DS₂-VA, CKD-EPI 2021, Bedside Schwartz, NEWS2, HAS-BLED, DDI Engine).

## Reporting a Security or Clinical Safety Anomaly

If you discover an error in deterministic clinical calculator logic, medical formula boundary condition, or MCP security vulnerability:
1. **Direct Communication**: Email `seotarek@gmail.com` with `[CLINICAL-SAFETY / SECURITY] MedOrqis Anomaly Report`.
2. **Include**:
   - The affected calculator or skill name.
   - Patient input vectors and observed output vs. official guideline formula result (e.g., ESC, KDIGO).
   - Expected behavior backed by authoritative clinical literature citations.
3. **Review Protocol**: Clinical and safety issues are prioritized with a response within 24 hours.
