## Description of Changes
<!-- Provide a clear summary of what this PR introduces or fixes. -->

## Clinical & Safety Justification
<!-- If modifying or adding clinical equations, cite the peer-reviewed guideline DOI/PMID and explain the target population boundaries. -->

## Regulatory & Quality Checklist (IEC 62304 / ISO 14971)
Please verify that your pull request satisfies all MedOrqis quality gates:
- [ ] **Zero-Token Rule**: All clinical calculations are pure deterministic Python functions (no LLM arithmetic or prompt token overhead).
- [ ] **Hard Refusal Gates**: Missing mandatory inputs or out-of-bounds parameters raise `SafeCalculationRefusal`.
- [ ] **Unit Tests Added**: New test cases added in `tests/` covering normal, boundary, and out-of-bounds scenarios.
- [ ] **File Integrity Verified**: Ran `python3 core/integrity_manifest.py --verify` and SHA-256 manifest matches.
- [ ] **Harmonized Test Suite Passes**: Ran `python3 tests/run_all_tests.py` with 100% pass rate.
- [ ] **Zero PHI or Secrets**: No patient data, unredacted identifiers, or API keys are committed.
