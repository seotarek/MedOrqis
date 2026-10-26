# MedOrqis — Synthetic NLP Benchmark & Dialect Regression Matrix (v2.1.1)

**Execution Timestamp**: `2026-10-26T22:39:04.992890+00:00`  
**Release Tag**: `v2.1.1`  
**Base Commit**: `d2c296f`  
**Benchmark Scope**: Automated Syntactic Unit-Test Fixtures (126 cases)  
**Governance Policy**: Two-Axis Separation (Algorithmic Invariance vs Real-World Clinical Validation)

> [!CAUTION]
> **CRITICAL TRANSPARENCY & CLINICAL NON-EQUIVALENCE ADVISORY**:
> **This matrix reports results from an automated synthetic NLP unit-test regression benchmark, NOT a clinical trial or real-world clinical validation study.**
> 
> - **Total Synthetic Test Corpus**: `126 cases` comprising:
>   - **100 Syntactic Negation Sentences**: Handcrafted grammatical fixtures designed to verify boundary detection (e.g., "ينفي وجود ألم", "no history of CAD").
>   - **10 BiDi & Unit Token Strings**: Numerical and unit strings verifying bidirectional layout preservation (e.g., Arabic RTL + English numbers/units like "500 mg").
>   - **16 Trade Brand-to-INN Mappings**: Synthetic lookup entries mapping regional commercial brand names to generic International Nonproprietary Names (e.g., Panadol -> Paracetamol).
> - **Real-World Clinical Bedside Validation**: **0.0% (UNVALIDATED IN-VIVO / PENDING MULTI-CENTER CLINICAL TRIALS)**.
> - **Linguistic Limitations**: Passing these synthetic regex fixtures proves syntactic rule compliance; it **DOES NOT** prove safety or efficacy in live clinical encounters, noisy EHR transcriptions, spoken colloquial dialect speech, or complex code-switching dialogues.

---

## 1. Dialect & Language Regression Matrix

| Language / Dialect | Dialect Code | Synthetic Negation Tests | BiDi & Unit Strings | Brand-to-INN Mappings | Automated Syntactic Pass Rate | Real-World Bedside Clinical Validation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Modern Standard Arabic (الفصحى)** | `ar-MSA` | 15/15 passed | 10/10 passed | 16/16 mapped | **100.0% (PASS)** | **0.0% (UNVALIDATED IN-VIVO)** |
| **Egyptian Arabic (العامية المصرية)** | `ar-EG` | 14/14 passed | 10/10 passed | Egyptian brands mapped | **100.0% (PASS)** | **0.0% (UNVALIDATED IN-VIVO)** |
| **Gulf Arabic (العامية الخليجية)** | `ar-GULF` | 14/14 passed | 10/10 passed | Gulf brands mapped | **100.0% (PASS)** | **0.0% (UNVALIDATED IN-VIVO)** |
| **Levantine Arabic (العامية الشامية)** | `ar-LEV` | 12/12 passed | 10/10 passed | Levantine brands mapped | **100.0% (PASS)** | **0.0% (UNVALIDATED IN-VIVO)** |
| **Maghrebi Arabic (الدارجة المغاربية)** | `ar-MAG` | 12/12 passed | 10/10 passed | Regional brands mapped | **100.0% (PASS)** | **0.0% (UNVALIDATED IN-VIVO)** |
| **English (Standard Medical)** | `en-US/GB` | 13/13 passed | 10/10 passed | International INN mapped | **100.0% (PASS)** | **0.0% (UNVALIDATED IN-VIVO)** |
| **French (Medical)** | `fr-FR` | 10/10 passed | Supported (ISO units) | Supported (International INN) | **100.0% (PASS)** | **0.0% (UNVALIDATED IN-VIVO)** |
| **Spanish (Medical)** | `es-ES` | 10/10 passed | Supported (ISO units) | Supported (International INN) | **100.0% (PASS)** | **0.0% (UNVALIDATED IN-VIVO)** |

---

## 2. Statistical Limitations & Real-World Caveats
1. **Limited Sample Size per Dialect**: The test corpus currently contains between 10 and 15 sentences per dialect (total 100 sentences). While sufficient to verify regex boundaries and clause-stop logic deterministically, this sample size is not a replacement for clinical validation against thousands of unstructured electronic health records.
2. **Code-Switching & Dialect Blending**: Clinicians and patients frequently mix Arabic dialects with English pharmacological terms or French anatomical phrases (especially in the Maghreb and Levant). Mixed-dialect linguistic parsing must always be supervised by a fluent licensed clinician.
3. **Phonetic Spelling & Typos**: Real clinical transcriptions contain typos, regional orthographic variations (e.g. ة vs ه, ي vs ى, أ vs ا), and phonetic slang. The deterministic normalizer handles common regional variants but does not extrapolate unknown idiomatic phrases.
4. **Bedside Invariance Policy**: Bedside deployment requires formal multi-center clinical trials, prospective observational validation, and local clinical governance sign-off.

---

## 3. Policy on Unverified Languages
Any language or dialect not explicitly listed in this matrix is classified as `EXPERIMENTAL_UNVERIFIED`. The system emits a mandatory clinical advisory halting automated assessments until verified inputs are provided in a supported language.
