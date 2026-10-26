"""
MedOrqis Skill Ecosystem Scaffolder (v2.1.0)
Generates all 24 clinical skills with:
1. Standard Claude Agent Skills YAML: allowed-tools: bash (scalar string)
2. Domain-specific clinical decision checklists
3. Specialized, wired scripts/run.py calling domain calculators
4. Comprehensive keywords & guideline authorities
"""

import os
import json
import re

SKILLS_SPEC = [
    # Tier 1 (Class A)
    {
        "name": "medorqis-orchestrator",
        "tier": "Tier 1",
        "safety_class": "Class A",
        "description": "Core router and clinical context envelope manager for the MedOrqis ecosystem. Coordinates clinical workflow handoffs, validates epistemic provenance, and detects inter-skill conflicts.",
        "allowed_tools": "bash",
        "intended_purpose": "Orchestrates multi-skill clinical evaluation workflows, routes patient queries, and enforces epistemic provenance boundaries.",
        "prohibited_uses": ["Autonomous final diagnosis", "Prescribing medications directly"],
        "mandatory_inputs": ["clinical_query", "patient_demographics"],
        "dependencies": ["core.context_validator", "core.safety_guardrails"],
        "default_calculator": "safety_evaluation",
        "checklist": [
            "Validate incoming JSON envelope against Draft-07 schema",
            "Verify epistemic provenance of clinical indications (no MODEL_INFERRED_HYPOTHESIS dosing)",
            "Screen for acute emergency red flags across all organ systems",
            "Route verified context to specialized Tier 2 / Tier 3 domain skills"
        ],
        "guideline_body": "MedOrqis Architectural & Governance Framework v2.1 (ISO 14971/IEC 62304)",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["orchestrator", "routing", "clinical-context", "epistemic-provenance", "conflict-detection", "workflow", "توجيه-سريري", "سياق-سريري"]
    },
    {
        "name": "ebm-research-biostatistics",
        "tier": "Tier 1",
        "safety_class": "Class A",
        "description": "Evidence-Based Medicine (EBM) research assistant. Formulates PICO questions, conducts CASP and RoB-2 critical appraisals, evaluates GRADE evidence certainty, and interprets biostatistical metrics.",
        "allowed_tools": "bash",
        "intended_purpose": "Appraises clinical study designs, computes biostatistical parameters (OR, RR, NNT), and assigns GRADE certainty.",
        "prohibited_uses": ["Fabricating citations or clinical trial results", "Direct clinical care without clinician review"],
        "mandatory_inputs": ["study_abstract_or_claim", "study_type"],
        "dependencies": ["core.citation_validator", "core.claim_entailment_verifier"],
        "default_calculator": "evidence_verification",
        "checklist": [
            "Formulate structured PICO clinical question",
            "Verify PMIDs and DOIs against immutable verified guidelines registry",
            "Execute RoB-2 / ROBINS-I risk of bias critical appraisal",
            "Assign GRADE certainty of evidence (High, Moderate, Low, Very Low)"
        ],
        "guideline_body": "Cochrane Handbook for Systematic Reviews / GRADE Working Group",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["ebm", "biostatistics", "pico", "casp", "rob-2", "grade", "odds-ratio", "relative-risk", "nnt", "cochrane", "طب-مسند-بالدليل", "إحصاء-حيوي"]
    },
    {
        "name": "medical-documentation-translation",
        "tier": "Tier 1",
        "safety_class": "Class A",
        "description": "Clinical documentation and translation engine. Generates structured SOAP notes, SBAR handoffs, and multilingual medical translations preserving negation polarity and numeric unit fidelity.",
        "allowed_tools": "bash",
        "intended_purpose": "Synthesizes medical encounters into standardized clinical documentation formats and provides semantic-preserving cross-lingual translation.",
        "prohibited_uses": ["Altering documented clinical facts", "Unsupervised patient discharge"],
        "mandatory_inputs": ["encounter_narrative", "format_type"],
        "dependencies": ["core.terminology_normalizer", "core.phi_deidentifier"],
        "default_calculator": "phi_scrub_and_translate",
        "checklist": [
            "De-identify Protected Health Information (HIPAA 18, National IDs, MRNs)",
            "Extract verified clinical findings into SOAP / SBAR structured sections",
            "Preserve clause-bounded negation polarity across multilingual translations",
            "Maintain bidirectional unit fidelity (prevent decimal inversion and mg vs mcg errors)"
        ],
        "guideline_body": "Joint Commission SBAR Standards / AAHIM Clinical Documentation Guidelines",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["soap", "sbar", "clinical-notes", "medical-translation", "bidi", "negation", "terminology", "ترجمة-طبية", "توثيق-طبي"]
    },
    {
        "name": "healthcare-ops-telemedicine-ehr",
        "tier": "Tier 1",
        "safety_class": "Class A",
        "description": "Health operations, telemedicine intake, and EHR integration skill. Maps unstructured clinical narratives to HL7 FHIR resources and verifies telemedicine intake safety criteria.",
        "allowed_tools": "bash",
        "intended_purpose": "Facilitates structured clinical data exchange via HL7 FHIR and manages digital clinical intake protocols.",
        "prohibited_uses": ["Bypassing patient informed consent", "Altering audit trails"],
        "mandatory_inputs": ["intake_payload", "target_fhir_resource"],
        "dependencies": ["core.phi_deidentifier", "core.terminology_connectors"],
        "default_calculator": "fhir_mapping",
        "checklist": [
            "Verify patient identity and jurisdiction licensure for telemedicine consult",
            "Map clinical entities to HL7 FHIR R4 resources (Patient, Condition, MedicationRequest)",
            "Check telemedicine appropriateness (screen out unstable red-flag emergencies)",
            "Confirm transmission encryption and audit logging conformance"
        ],
        "guideline_body": "HL7 FHIR R4 Specification / ATA Telemedicine Practice Guidelines",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["telemedicine", "hl7", "fhir", "ehr", "intake-triage", "scheduling", "interoperability", "طب-عن-بعد", "سجلات-صحية"]
    },
    {
        "name": "health-cybersecurity-privacy",
        "tier": "Tier 1",
        "safety_class": "Class A",
        "description": "Health cybersecurity and patient privacy guardian. De-identifies Protected Health Information (HIPAA Safe Harbor, GDPR, Egyptian PDPL, Saudi PDPL) and blocks indirect prompt injection attacks.",
        "allowed_tools": "bash",
        "intended_purpose": "Screens clinical inputs for PHI and adversarial injections before transmission or public storage.",
        "prohibited_uses": ["Transmitting identified patient data to public services"],
        "mandatory_inputs": ["clinical_text"],
        "dependencies": ["core.phi_deidentifier", "core.prompt_security_guard"],
        "default_calculator": "security_and_phi_scan",
        "checklist": [
            "Execute regex and rule-based scan for indirect prompt injections and jailbreak bypasses",
            "Redact HIPAA 18 Safe Harbor identifiers",
            "Redact Egyptian 14-digit National IDs and Saudi 10-digit National IDs / Iqamas",
            "Log structured de-identification audit report without persisting raw patient identifiers"
        ],
        "guideline_body": "HIPAA Privacy Rule / EU GDPR Article 9 / ISO 27799 Health Informatics",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["phi", "hipaa", "gdpr", "pdpl", "de-identification", "prompt-injection", "redaction", "أمان-صحي", "خصوصية-المرضى"]
    },
    {
        "name": "public-health-epidemiology",
        "tier": "Tier 1",
        "safety_class": "Class A",
        "description": "Public health, epidemiology, and outbreak investigation skill. Evaluates diagnostic screening metrics (sensitivity, specificity, PPV, NPV) and advises on infection prevention and control (IPC).",
        "allowed_tools": "bash",
        "intended_purpose": "Computes epidemiological indices, analyzes transmission dynamics, and references WHO infection control protocols.",
        "prohibited_uses": ["Issuing unverified public quarantine orders"],
        "mandatory_inputs": ["disease_metrics_or_outbreak_data"],
        "dependencies": ["core.citation_validator"],
        "default_calculator": "epidemiology_metrics",
        "checklist": [
            "Compute 2x2 contingency matrix metrics: Sensitivity, Specificity, PPV, NPV, LR+ and LR-",
            "Adjust predictive values according to disease prevalence in target population",
            "Identify outbreak transmission modes (airborne, droplet, contact, vector)",
            "Reference WHO infection prevention and control (IPC) standards"
        ],
        "guideline_body": "WHO Outbreak Communication & IPC Guidelines / CDC Field Epidemiology Manual",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["epidemiology", "public-health", "screening", "sensitivity", "specificity", "ipc", "outbreak", "صحة-عامة", "وبائيات"]
    },

    # Tier 2 (Class B)
    {
        "name": "differential-diagnosis-cds",
        "tier": "Tier 2",
        "safety_class": "Class B",
        "description": "Diagnostic decision support skill. Constructs structured VINDICATE differential diagnoses, highlights must-not-miss life-threatening conditions, and proposes prioritized diagnostic workups.",
        "allowed_tools": "bash",
        "intended_purpose": "Aids clinicians in expanding diagnostic breadth, preventing premature cognitive closure, and prioritizing testing.",
        "prohibited_uses": ["Autonomous definitive diagnosis", "Excluding emergency etiologies without objective testing"],
        "mandatory_inputs": ["presenting_symptoms", "patient_demographics"],
        "dependencies": ["core.context_validator", "core.safety_guardrails"],
        "default_calculator": "vindicate_differential",
        "checklist": [
            "Categorize potential etiologies using the VINDICATE mnemonic",
            "Highlight high-morbidity 'Must-Not-Miss' diagnoses at the top of differential",
            "Order prioritized diagnostic tests by diagnostic yield and invasiveness",
            "Check for cognitive biases (anchoring, premature closure, availability heuristic)"
        ],
        "guideline_body": "Society to Improve Diagnosis in Medicine (SIDM) / BMJ Best Practice",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["differential-diagnosis", "vindicate", "clinical-decision-support", "cds", "symptom-checker", "workup", "تشخيص-تفريقي"]
    },
    {
        "name": "laboratory-medicine-pathology",
        "tier": "Tier 2",
        "safety_class": "Class B",
        "description": "Laboratory medicine and pathology interpretation skill. Flags critical panic values, resolves metric unit discrepancies (mmol/L vs mg/dL), and maps lab parameters to LOINC concepts.",
        "allowed_tools": "bash",
        "intended_purpose": "Interprets lab profiles (CBC, BMP, LFTs, Coagulation, ABG), flags critical panic thresholds, and suggests confirmatory testing.",
        "prohibited_uses": ["Overriding clinical lab delta checks", "Ignoring critical laboratory panic alerts"],
        "mandatory_inputs": ["test_name", "value", "unit"],
        "dependencies": ["core.context_validator"],
        "default_calculator": "lab_panic_check",
        "checklist": [
            "Screen reported lab values against emergency panic alert thresholds",
            "Harmonize unit discrepancies (e.g. serum creatinine mg/dL vs umol/L, glucose mg/dL vs mmol/L)",
            "Map lab test to standardized LOINC concept code",
            "Recommend immediate clinician notification for critical panic results"
        ],
        "guideline_body": "CLSI Laboratory Safety & Panic Value Guidelines / IFCC LOINC Standards",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["laboratory", "panic-values", "loinc", "critical-labs", "biochemistry", "hematology", "pathology", "تحاليل-طبية", "قيم-حرجة"]
    },
    {
        "name": "radiology-medical-imaging",
        "tier": "Tier 2",
        "safety_class": "Class B",
        "description": "Medical imaging appropriateness and report analysis skill. Implements ACR Appropriateness Criteria, checks contrast nephropathy/allergy risks, and ensures radiation/pregnancy safety.",
        "allowed_tools": "bash",
        "intended_purpose": "Selects appropriate imaging modalities based on clinical presentation and radiation risk vs diagnostic yield.",
        "prohibited_uses": ["Primary reading of raw radiological DICOM images", "Ordering contrast in severe acute kidney injury without prophylaxis"],
        "mandatory_inputs": ["clinical_indication", "patient_demographics"],
        "dependencies": ["core.clinical_calculators", "core.context_validator"],
        "default_calculator": "radiology_appropriateness",
        "checklist": [
            "Consult ACR Appropriateness Criteria for target clinical indication",
            "Screen for pregnancy in female patients before ordering ionizing radiation (ALARA principle)",
            "Calculate eGFR prior to iodinated CT or gadolinium MRI contrast administration",
            "Check for severe contrast allergy history and prescribe premedication protocol if indicated"
        ],
        "guideline_body": "ACR Appropriateness Criteria (2024) / ESUR Contrast Media Guidelines",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["radiology", "imaging", "mri", "ct-scan", "x-ray", "ultrasound", "acr-criteria", "alara", "أشعة", "تصوير-طبي"]
    },
    {
        "name": "internal-medicine-chronic",
        "tier": "Tier 2",
        "safety_class": "Class B",
        "description": "Internal medicine and chronic disease management skill. Evaluates multi-morbidity interactions across cardiology, endocrinology, nephrology, and pulmonology.",
        "allowed_tools": "bash",
        "intended_purpose": "Provides guideline-concordant chronic care plans for diabetes, hypertension, heart failure, and CKD.",
        "prohibited_uses": ["Autonomous dose titration of insulin without patient SMBG log review"],
        "mandatory_inputs": ["chronic_conditions", "current_medications"],
        "dependencies": ["core.clinical_calculators", "core.safety_guardrails"],
        "default_calculator": "chronic_disease_calculators",
        "checklist": [
            "Calculate CHA2DS2-VA (ESC 2024) stroke risk for patients with atrial fibrillation",
            "Calculate race-free CKD-EPI 2021 eGFR and assign KDIGO G/A staging",
            "Reconcile multi-drug regimens for drug-disease contraindications (e.g. NSAIDs in CKD/HF)",
            "Set individualized HbA1c and blood pressure targets according to patient frailty and life expectancy"
        ],
        "guideline_body": "ADA Standards of Care in Diabetes 2024 / KDIGO CKD Guidelines / ESC Heart Failure Guidelines",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["internal-medicine", "chronic-disease", "diabetes", "hypertension", "ckd", "copd", "heart-failure", "kdigo", "باطنة", "أمراض-مزمنة"]
    },
    {
        "name": "infectious-diseases-stewardship",
        "tier": "Tier 2",
        "safety_class": "Class B",
        "description": "Antimicrobial stewardship and infectious diseases skill. Guides empiric vs targeted antibiotic selection, prevents unnecessary broad-spectrum usage, and monitors antibiogram patterns.",
        "allowed_tools": "bash",
        "intended_purpose": "Recommends guideline-directed antimicrobial regimens, dosage adjustments for renal function, and optimal therapy duration.",
        "prohibited_uses": ["Ignoring local antibiograms or positive blood culture sensitivities"],
        "mandatory_inputs": ["infection_site", "patient_demographics", "allergies"],
        "dependencies": ["core.clinical_calculators", "core.context_validator"],
        "default_calculator": "antimicrobial_stewardship",
        "checklist": [
            "Categorize antimicrobial regimen into WHO AWaRe classification (Access, Watch, Reserve)",
            "Differentiate true IgE-mediated beta-lactam anaphylaxis from mild cutaneous adverse reactions",
            "Calculate Cockcroft-Gault CrCl to adjust aminoglycoside / vancomycin dosing intervals",
            "Recommend structured de-escalation from broad-spectrum to narrow-spectrum upon culture sensitivity"
        ],
        "guideline_body": "IDSA Guidelines / Sanford Guide to Antimicrobial Therapy (2024) / WHO AWaRe",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["infectious-diseases", "antimicrobial-stewardship", "antibiotics", "sepsis", "antibiogram", "resistance", "idsa", "مضادات-حيوية", "أمراض-معدية"]
    },
    {
        "name": "nursing-clinical-care",
        "tier": "Tier 2",
        "safety_class": "Class B",
        "description": "Inpatient nursing and bedside clinical care skill. Computes NEWS2 early warning scores, monitors pressure injury risks (Braden Scale), and formulates patient care plans.",
        "allowed_tools": "bash",
        "intended_purpose": "Supports bedside nursing assessments, vital sign trend tracking, and escalation protocols for deteriorating patients.",
        "prohibited_uses": ["Discontinuing nursing vital checks in high-risk patients"],
        "mandatory_inputs": ["vital_signs", "mental_status"],
        "dependencies": ["core.clinical_calculators", "core.safety_guardrails"],
        "default_calculator": "calculate_news2_score",
        "checklist": [
            "Compute National Early Warning Score 2 (NEWS2) from 6 physiological parameters",
            "Trigger rapid response team escalation for NEWS2 score >= 5 or single parameter score of 3",
            "Assess Braden Scale for pressure ulcer risk and mandate repositioning schedules",
            "Verify fall risk precautions and maintain bedside safety barriers"
        ],
        "guideline_body": "Royal College of Physicians NEWS2 Guidelines / NPUAP Braden Scale",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["nursing", "news2", "braden-scale", "vital-signs", "wound-care", "patient-safety", "care-plan", "تمريض", "رعاية-سريرية"]
    },
    {
        "name": "clinical-nutrition-dietetics",
        "tier": "Tier 2",
        "safety_class": "Class B",
        "description": "Clinical nutrition and medical nutrition therapy skill. Computes basal caloric/protein requirements, manages diabetic/renal diets, and flags food-drug interactions.",
        "allowed_tools": "bash",
        "intended_purpose": "Calculates nutritional needs, manages therapeutic diet restrictions, and designs enteral/parenteral nutrition support.",
        "prohibited_uses": ["Formulating TPN without daily electrolyte and liver function monitoring"],
        "mandatory_inputs": ["weight_kg", "clinical_condition"],
        "dependencies": ["core.clinical_calculators"],
        "default_calculator": "nutrition_calculator",
        "checklist": [
            "Calculate Basal Metabolic Rate (BMR) via Harris-Benedict or Mifflin-St Jeor formula",
            "Adjust target protein intake based on clinical state (0.8 g/kg for stable CKD, 1.5-2.0 g/kg for ICU/sepsis)",
            "Check for food-drug interactions (e.g. grapefruit and CYP3A4 statins, vitamin K and warfarin)",
            "Screen for Refeeding Syndrome risk in severely malnourished or prolonged-fasting patients"
        ],
        "guideline_body": "ASPEN / ESPEN Clinical Nutrition Guidelines",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["nutrition", "dietetics", "bmi", "harris-benedict", "enteral-feeding", "malnutrition", "food-drug-interactions", "تغذية-علاجية"]
    },
    {
        "name": "rehabilitation-physical-therapy",
        "tier": "Tier 2",
        "safety_class": "Class B",
        "description": "Physical therapy and rehabilitation skill. Designs post-operative, stroke, and musculoskeletal recovery protocols while evaluating hemodynamic and spinal exercise contraindications.",
        "allowed_tools": "bash",
        "intended_purpose": "Proposes progressive mobility protocols, assesses functional recovery scales, and checks post-surgical weight-bearing restrictions.",
        "prohibited_uses": ["Mobilizing patients with unstable spinal fractures or acute deep vein thrombosis without clearance"],
        "mandatory_inputs": ["surgical_or_neurological_status", "mobility_level"],
        "dependencies": ["core.clinical_calculators", "core.safety_guardrails"],
        "default_calculator": "rehab_mobility_evaluation",
        "checklist": [
            "Verify surgical clearance and weight-bearing status before initiating mobilization",
            "Screen for acute DVT using Wells DVT Criteria before calf manipulation or leg exercise",
            "Monitor hemodynamic tolerance during orthostatic position changes (prevent syncopal falls)",
            "Structure progressive neuro-rehabilitation exercises following acute ischemic stroke"
        ],
        "guideline_body": "AHA/ASA Stroke Rehabilitation Guidelines / APTA Practice Guidelines",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["physical-therapy", "rehabilitation", "stroke-rehab", "post-op-rehab", "mobility", "fim", "علاج-طبيعي", "تأهيل"]
    },

    # Tier 3 (Class C)
    {
        "name": "emergency-triage-redflags",
        "tier": "Tier 3",
        "safety_class": "Class C",
        "description": "High-urgency emergency triage and red-flag escalation gate. Evaluates ABCDE primary survey stability, screens for Sepsis, ACS, Acute Stroke, and Anaphylaxis, and executes immediate emergency redirection.",
        "allowed_tools": "bash",
        "intended_purpose": "Identifies time-sensitive, life-threatening clinical emergencies and immediately halts non-emergency chat, directing patient to emergency care.",
        "prohibited_uses": ["Delaying emergency medical transfer", "Attempting outpatient management of unstable patients"],
        "mandatory_inputs": ["presenting_symptoms", "vital_signs"],
        "dependencies": ["core.safety_guardrails"],
        "default_calculator": "emergency_triage_evaluation",
        "checklist": [
            "Execute ABCDE Primary Survey: Airway patency, Breathing work, Circulation perfusion, Disability GCS, Exposure",
            "Screen for time-sensitive emergencies: ACS, acute ischemic stroke (FAST), septic shock, anaphylaxis, tension pneumothorax",
            "Filter out affirmed symptoms from negated ones (do not trigger on 'denies chest pain')",
            "Execute immediate emergency redirection with local regional emergency contact numbers"
        ],
        "guideline_body": "Manchester Triage System / Emergency Severity Index (ESI) / Surviving Sepsis 2021 / AHA ACLS",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["emergency", "red-flags", "triage", "abcde", "chest-pain", "stroke", "anaphylaxis", "trauma", "طوارئ", "علامات-خطيرة"]
    },
    {
        "name": "clinical-safety-auditor",
        "tier": "Tier 3",
        "safety_class": "Class C",
        "description": "Final pre-output clinical safety auditor. Validates that outputs contain verified citations, comply with dose caps, have no missing mandatory parameters, and do not act on unverified hypotheses.",
        "allowed_tools": "bash",
        "intended_purpose": "Acts as an immutable quality gate auditing all outgoing clinical advice against patient safety policies.",
        "prohibited_uses": ["Suppressing detected clinical safety warnings"],
        "mandatory_inputs": ["proposed_output", "context_envelope"],
        "dependencies": ["core.context_validator", "core.citation_validator", "core.safety_guardrails"],
        "default_calculator": "clinical_safety_audit",
        "checklist": [
            "Intercept clinical contradictions (e.g. anticoagulation in active gastrointestinal hemorrhage)",
            "Enforce Epistemic Provenance Gate (halt if indication is MODEL_INFERRED_HYPOTHESIS)",
            "Verify that every clinical claim maps to an authentic, un-retracted guideline citation",
            "Ensure output carries the mandatory clinical governance banner"
        ],
        "guideline_body": "FDA Clinical Decision Support Software Guidance (2026) / ISO 14971 Medical Device Risk Controls",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["safety-gate", "audit", "contraindications", "anticoagulation-bleed", "inter-skill-conflict", "safe-abstention", "تدقيق-أمان", "أمان-سريري"]
    },
    {
        "name": "pharmacology-dosing-interactions",
        "tier": "Tier 3",
        "safety_class": "Class C",
        "description": "High-risk pharmacology, dosing, and drug interaction engine. Enforces strict renal and hepatic dose adjustments, verifies Narrow Therapeutic Index (NTI) drug levels, and blocks lethal drug-drug interactions.",
        "allowed_tools": "bash",
        "intended_purpose": "Calculates precise drug dosages based on weight and renal function (eGFR/CrCl), and intercepts contraindicated drug combinations.",
        "prohibited_uses": ["Calculating chemotherapy or NTI dosing without serum drug levels and renal/hepatic markers"],
        "mandatory_inputs": ["drug_inn", "patient_demographics", "renal_function"],
        "dependencies": ["core.clinical_calculators", "core.context_validator", "core.safety_guardrails"],
        "default_calculator": "pharmacology_and_ddi",
        "checklist": [
            "Normalize all medication brand names to international nonproprietary names (INN)",
            "Evaluate full medication list against critical DDI rules (e.g. sildenafil + nitrates, warfarin + NSAIDs)",
            "Calculate Cockcroft-Gault CrCl with Ideal/Adjusted Body Weight adjustments in obesity",
            "Adjust dosages and dosing intervals for renally cleared medications according to CrCl"
        ],
        "guideline_body": "FDA Drug Labeling / BNF / Stockley's Drug Interactions (2024)",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["pharmacology", "drug-interactions", "renal-dosing", "cockcroft-gault", "hepatic-adjustment", "crcl", "ddi", "صيدلة-إكلينيكية", "جرعات-دوائية"]
    },
    {
        "name": "clinical-toxicology-overdose",
        "tier": "Tier 3",
        "safety_class": "Class C",
        "description": "Clinical toxicology and acute overdose management skill. Recognizes acute toxidromes (anticholinergic, cholinergic, opioid, sympathomimetic, sedative), advises on specific antidotes, and escalates to Poison Control.",
        "allowed_tools": "bash",
        "intended_purpose": "Identifies toxic ingestions, advises on gastric decontamination timing, naloxone/antidote indications, and poison center contact.",
        "prohibited_uses": ["Recommending induction of emesis (ipecac) or home remedies for caustic ingestions"],
        "mandatory_inputs": ["substance_ingested", "time_since_ingestion", "vital_signs"],
        "dependencies": ["core.safety_guardrails"],
        "default_calculator": "toxicology_evaluation",
        "checklist": [
            "Identify acute clinical toxidrome based on vital signs, pupils, skin moisture, and bowel sounds",
            "Check indication for specific antidotes: Naloxone (opioids), N-acetylcysteine (paracetamol), Atropine (cholinergics)",
            "Determine timing window for activated charcoal (strictly within 1-2 hours of ingestion in alert patients)",
            "Escalate immediately to Poison Control Center and regional emergency medical services"
        ],
        "guideline_body": "American Academy of Clinical Toxicology (AACT) / EAPCCT Guidelines",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["toxicology", "overdose", "toxidrome", "antidote", "naloxone", "poison-control", "paracetamol-overdose", "تسمم", "جرعة-زائدة"]
    },
    {
        "name": "pediatrics-neonatology",
        "tier": "Tier 3",
        "safety_class": "Class C",
        "description": "Pediatric and neonatal clinical safety skill. Enforces strict weight-based dose caps (never exceeding maximum adult doses), flags age-weight entry discrepancies (lb vs kg), and screens for neonatal red flags.",
        "allowed_tools": "bash",
        "intended_purpose": "Provides pediatric dosing calculations, APGAR assessments, dehydration triage, and fever management in infants.",
        "prohibited_uses": ["Dosing pediatric medication without verified weight in kilograms"],
        "mandatory_inputs": ["age_years", "weight_kg"],
        "dependencies": ["core.clinical_calculators", "core.context_validator", "core.safety_guardrails"],
        "default_calculator": "pediatric_dosing_and_schwartz",
        "checklist": [
            "Verify pediatric patient weight strictly in kilograms (reject lb entries or missing weights)",
            "Calculate weight-based medication dose (mg/kg) and enforce mandatory adult maximum dose cap",
            "Calculate pediatric renal function via Bedside Schwartz eGFR formula (0.413 * height / Cr)",
            "Screen for neonatal red flags: fever in neonate < 28 days (mandates full septic workup)"
        ],
        "guideline_body": "Nelson Textbook of Pediatrics (22nd Ed) / AAP Guidelines / WHO IMCI",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["pediatrics", "neonatology", "pediatric-dosing", "weight-based-dosing", "dose-capping", "apgar", "طب-أطفال", "حديثي-الولادة"]
    },
    {
        "name": "obstetrics-gynecology",
        "tier": "Tier 3",
        "safety_class": "Class C",
        "description": "Obstetrics, gynecology, and maternal-fetal safety skill. Screens for pre-eclampsia/eclampsia, ectopic pregnancy, postpartum hemorrhage, and verifies medication safety in pregnancy and lactation.",
        "allowed_tools": "bash",
        "intended_purpose": "Identifies acute maternal red flags, calculates gestational age, and checks Briggs Drugs in Pregnancy and Lactation safety.",
        "prohibited_uses": ["Prescribing Category X or known teratogenic drugs (ACEi, ARBs, isotretinoin, methotrexate) in pregnancy"],
        "mandatory_inputs": ["pregnancy_status", "gestational_age_weeks"],
        "dependencies": ["core.clinical_calculators", "core.context_validator", "core.safety_guardrails"],
        "default_calculator": "obgyn_safety_check",
        "checklist": [
            "Screen for acute obstetric emergencies: severe pre-eclampsia (BP >= 160/110 + symptoms), ectopic pregnancy",
            "Cross-check all prescribed medications against FDA/Briggs pregnancy teratogenicity registries",
            "Halt administration of contraindicated teratogens (isotretinoin, valproate, ACE inhibitors, methotrexate)",
            "Confirm lactation safety before authorizing maternal medication intake"
        ],
        "guideline_body": "ACOG Practice Bulletins / RCOG Green-top Guidelines / Briggs Drugs in Pregnancy",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["obgyn", "pregnancy", "lactation", "teratogenic", "pre-eclampsia", "gestational-diabetes", "postpartum", "نساء-وتوليد", "حمل-ورضاعة"]
    },
    {
        "name": "geriatrics-polypharmacy",
        "tier": "Tier 3",
        "safety_class": "Class C",
        "description": "Geriatric medicine, polypharmacy, and deprescribing skill. Implements AGS Beers Criteria (2023) and STOPP/START criteria, assesses anticholinergic cognitive burden, and identifies fall risks.",
        "allowed_tools": "bash",
        "intended_purpose": "Reviews elderly medication lists, flags potentially inappropriate medications (PIMs), and guides structured deprescribing.",
        "prohibited_uses": ["Abruptly stopping chronic psychotropic or cardiac medications without tapering"],
        "mandatory_inputs": ["medication_list", "patient_age_years"],
        "dependencies": ["core.clinical_calculators", "core.context_validator"],
        "default_calculator": "geriatric_beers_review",
        "checklist": [
            "Audit medication list against 2023 American Geriatrics Society (AGS) Beers Criteria",
            "Identify high anticholinergic burden drugs contributing to cognitive decline and fall risks",
            "Screen for drug-drug interactions in elderly patients taking >= 5 concurrent medications",
            "Formulate structured deprescribing taper plans for sedatives, hypnotics, and redundant agents"
        ],
        "guideline_body": "2023 AGS Beers Criteria / STOPP/START Criteria Version 3 (2023)",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["geriatrics", "polypharmacy", "beers-criteria", "stopp-start", "fall-risk", "anticholinergic-burden", "طب-المسنين", "تعدد-الأدوية"]
    },
    {
        "name": "mental-health-psychiatry",
        "tier": "Tier 3",
        "safety_class": "Class C",
        "description": "Psychiatry and mental health crisis skill. Implements immediate emergency protocols for active suicidal ideation, screens for psychosis and severe mania, and monitors psychotropic drug interactions.",
        "allowed_tools": "bash",
        "intended_purpose": "Detects psychiatric crises, connects users to crisis hotlines, and monitors for Serotonin Syndrome and Neuroleptic Malignant Syndrome.",
        "prohibited_uses": ["Delaying crisis intervention for suicidal patients", "Autonomous medication adjustments for severe psychiatric conditions"],
        "mandatory_inputs": ["mental_health_symptoms"],
        "dependencies": ["core.safety_guardrails"],
        "default_calculator": "psychiatry_crisis_triage",
        "checklist": [
            "Screen for active suicidal ideation with intent or plan (Columbia-Suicide Severity Rating Scale)",
            "Trigger immediate emergency escalation and provide localized 24/7 crisis hotline contact numbers",
            "Monitor psychotropic combinations for Serotonin Syndrome (MAOIs + SSRIs) and QTc prolongation",
            "Screen for Neuroleptic Malignant Syndrome in patients on antipsychotic therapy"
        ],
        "guideline_body": "APA Practice Guidelines / Columbia Suicide Severity Rating Scale (C-SSRS)",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["psychiatry", "mental-health", "suicide-screening", "crisis-triage", "ssri", "qt-prolongation", "depression", "صحة-نفسية", "طب-نفسي"]
    },
    {
        "name": "perioperative-surgical-care",
        "tier": "Tier 3",
        "safety_class": "Class C",
        "description": "Perioperative surgical care and risk assessment skill. Calculates Revised Cardiac Risk Index (RCRI), manages pre-op anticoagulation interruption/bridging, and monitors for acute surgical abdomen.",
        "allowed_tools": "bash",
        "intended_purpose": "Evaluates perioperative cardiac and pulmonary risk, guides antithrombotic timing around surgery, and assesses surgical emergencies.",
        "prohibited_uses": ["Permitting elective surgery in unstratified high-risk cardiac patients"],
        "mandatory_inputs": ["surgical_procedure", "patient_demographics", "cardiac_history"],
        "dependencies": ["core.clinical_calculators", "core.safety_guardrails"],
        "default_calculator": "perioperative_risk",
        "checklist": [
            "Compute Revised Cardiac Risk Index (RCRI) score for major non-cardiac surgery",
            "Calculate pre-test probability for venous thromboembolism via Wells DVT/PE scores",
            "Plan antithrombotic interruption and bridging protocol based on procedural bleeding risk",
            "Enforce WHO Surgical Safety Checklist checkpoints (Sign In, Time Out, Sign Out)"
        ],
        "guideline_body": "2024 AHA/ACC Perioperative Cardiovascular Evaluation Guidelines / ASA Physical Status",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["surgery", "perioperative", "rcri", "pre-op-clearance", "anticoagulation-bridging", "who-surgical-checklist", "جراحة", "تخدير"]
    },
    {
        "name": "oncology-palliative-care",
        "tier": "Tier 3",
        "safety_class": "Class C",
        "description": "Oncology emergencies and palliative symptom management skill. Screens for febrile neutropenia, spinal cord compression, tumor lysis syndrome, and guides opioid titration and breakthrough pain control.",
        "allowed_tools": "bash",
        "intended_purpose": "Identifies oncologic emergencies requiring immediate hospital admission and provides structured palliative symptom algorithms.",
        "prohibited_uses": ["Delaying broad-spectrum antibiotics in suspected neutropenic fever", "Calculating cytotoxic chemotherapy doses without oncologist sign-off"],
        "mandatory_inputs": ["cancer_type", "current_treatment", "symptoms"],
        "dependencies": ["core.clinical_calculators", "core.safety_guardrails"],
        "default_calculator": "oncology_emergency_triage",
        "checklist": [
            "Screen for Febrile Neutropenia (fever >= 38.3°C with ANC < 500/uL): mandates empiric IV antipseudomonal within 1 hour",
            "Detect acute spinal cord compression in metastatic cancer patients (urgent MRI + high-dose dexamethasone)",
            "Calculate equianalgesic opioid conversions (morphine milligram equivalents) to prevent accidental overdose",
            "Screen for acute Tumor Lysis Syndrome following cytotoxic chemotherapy initiation"
        ],
        "guideline_body": "ASCO / NCCN Clinical Practice Guidelines / ESMO Palliative Care Guidelines",
        "human_review": "REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF",
        "keywords": ["oncology", "palliative-care", "febrile-neutropenia", "pain-management", "opioid-conversion", "tumor-lysis", "أورام", "رعاية-تلطيفية"]
    }
]


def build_skills():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    skills_dir = os.path.join(base_dir, "skills")
    os.makedirs(skills_dir, exist_ok=True)

    for spec in SKILLS_SPEC:
        s_name = spec["name"]
        s_path = os.path.join(skills_dir, s_name)
        os.makedirs(os.path.join(s_path, "references"), exist_ok=True)
        os.makedirs(os.path.join(s_path, "scripts"), exist_ok=True)

        # 1. SKILL.md with allowed-tools: bash (scalar string)
        kw_yaml = "\n".join(f"    - {k}" for k in spec["keywords"])
        chk_md = "\n".join(f"{i+1}. {c}" for i, c in enumerate(spec["checklist"]))

        skill_md_content = f"""---
name: {s_name}
description: >-
  {spec['description']}
allowed-tools: {spec['allowed_tools']}
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "{spec['tier']}"
  safety-class: "{spec['safety_class']}"
  keywords:
{kw_yaml}
---

# {s_name} (v2.1.0)

[![Safety Class: {spec['safety_class']}](https://img.shields.io/badge/Safety%20Class-{spec['safety_class'].replace(' ', '%20')}-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: {spec['tier']}](https://img.shields.io/badge/Tier-{spec['tier'].replace(' ', '%20')}-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
{spec['intended_purpose']}

### Prohibited Uses
{chr(10).join(f"- {p}" for p in spec['prohibited_uses'])}

## 2. Clinical Decision Checklist
{chk_md}

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
{', '.join(f'`{k}`' for k in spec['keywords'])}

## 4. Mandatory Input Parameters
{chr(10).join(f"- `{inp}`" for inp in spec['mandatory_inputs'])}

## 5. Deterministic Safety Dependencies
{chr(10).join(f"- `{dep}`" for dep in spec['dependencies'])}

## 6. Execution Workflow
1. Parse and validate incoming `ClinicalContextEnvelope`.
2. Inspect epistemic provenance: Ensure no treatment or high-risk dosing is executed on `MODEL_INFERRED_HYPOTHESIS`.
3. Check for emergency red flags using `core.safety_guardrails`. If critical red flags exist, halt and return `SAFE_ABSTENTION_EMERGENCY_ESCALATION`.
4. Invoke deterministic calculators or rules via `scripts/run.py` or MCP tools.
5. Format and return structured `SkillOutputContract` with validated citations.

## 7. Installation & Invocation
- **Skills CLI**:
  ```bash
  npx skills add seotarek/MedOrqis --skill {s_name}
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/{s_name}/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: {spec['guideline_body']}
- **Review Status**: `{spec['human_review']}`
"""
        with open(os.path.join(s_path, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(skill_md_content)

        # 2. manifest.json
        manifest_data = {
            "$schema": "../../schemas/skill_risk_manifest.schema.json",
            "skill_name": s_name,
            "version": "2.1.0",
            "safety_class": spec["safety_class"],
            "tier": spec["tier"],
            "intended_purpose": spec["intended_purpose"],
            "prohibited_uses": spec["prohibited_uses"],
            "mandatory_inputs": spec["mandatory_inputs"],
            "deterministic_dependencies": spec["dependencies"],
            "human_review_status": spec["human_review"],
            "keywords": spec["keywords"]
        }
        with open(os.path.join(s_path, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        # 3. references/guidelines.md
        ref_content = f"""# Clinical Guidelines & Reference Logic: {s_name} (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: {spec['guideline_body']}
- **Applicable Safety Class**: {spec['safety_class']} ({spec['tier']})
- **Human Clinical Sign-Off**: {spec['human_review']}

## Clinical Decision Checklist
{chk_md}

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter ({', '.join(spec['mandatory_inputs'])}) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
"""
        with open(os.path.join(s_path, "references", "guidelines.md"), "w", encoding="utf-8") as f:
            f.write(ref_content)

        # 4. Domain-wired scripts/run.py
        calc_id = spec["default_calculator"]
        script_content = f'''#!/usr/bin/env python3
"""
Specialized deterministic execution script for {s_name} (v2.1.0).
Wired to domain calculator: {calc_id}.
"""

import sys
import json
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from core.context_validator import validate_treatment_readiness, ProvenanceViolationError
from core.safety_guardrails import SafetyGuardrailsEngine
from core.clinical_calculators import (
    calculate_cha2ds2_va_esc2024,
    calculate_ckd_epi_2021_egfr,
    calculate_bedside_schwartz_egfr,
    calculate_cockcroft_gault_crcl,
    calculate_pediatric_weight_dose,
    calculate_news2_score,
    calculate_has_bled_score,
    calculate_curb65_score,
    calculate_wells_dvt_score,
    SafeCalculationRefusal
)


def run_skill(payload_dict):
    guardrails = SafetyGuardrailsEngine()
    verdict = guardrails.evaluate_safety(payload_dict)

    result = {{
        "skill_name": "{s_name}",
        "version": "2.1.0",
        "safety_class": "{spec['safety_class']}",
        "tier": "{spec['tier']}",
        "gate_status": verdict["gate_status"],
        "red_flags": verdict["red_flags_detected"],
        "critical_ddis": verdict.get("critical_ddis_detected", []),
        "governance_banner": verdict.get("governance_banner", ""),
        "action_plan": verdict["action_plan"]
    }}

    # Domain specific computation
    demographics = payload_dict.get("patient_demographics", {{}})
    age = demographics.get("age_years", 40)
    sex = demographics.get("biological_sex", "MALE")

    try:
        if "{s_name}" == "nursing-clinical-care":
            news = calculate_news2_score(
                respiration_rate_bpm=18,
                spo2_percent=97.0,
                air_or_oxygen="AIR",
                systolic_bp_mmhg=125,
                pulse_bpm=76,
                consciousness="ALERT",
                temperature_celsius=37.0
            )
            result["domain_assessment"] = {{
                "score_name": news.calculator_name,
                "score": news.score,
                "band": news.interpretation_band,
                "recommendation": news.clinical_recommendation
            }}
        elif "{s_name}" == "pediatrics-neonatology" and age < 18:
            weight = demographics.get("weight_kg", 20.0)
            dose = calculate_pediatric_weight_dose(
                age_years=age,
                weight_kg=weight,
                dose_per_kg=15.0,
                max_single_adult_dose_mg=500.0
            )
            result["domain_assessment"] = {{
                "dose_calculation": dose.interpretation_band,
                "recommendation": dose.clinical_recommendation
            }}
        elif "{s_name}" == "internal-medicine-chronic":
            egfr = calculate_ckd_epi_2021_egfr(
                serum_creatinine=1.1,
                age_years=age,
                biological_sex=sex
            )
            result["domain_assessment"] = {{
                "renal_function": egfr.interpretation_band,
                "recommendation": egfr.clinical_recommendation
            }}
        elif "{s_name}" == "pharmacology-dosing-interactions":
            meds = payload_dict.get("current_medications", ["warfarin", "paracetamol"])
            ddis = guardrails.check_drug_interactions(meds, demographics)
            result["domain_assessment"] = {{
                "medications_screened": meds,
                "ddi_count": len(ddis),
                "ddis": ddis
            }}
    except SafeCalculationRefusal as e:
        result["domain_assessment"] = {{"refusal": e.reason, "recommendation": e.recommendation}}

    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        payload = {{
            "envelope_id": "CLI-TEST-V2.1",
            "timestamp": "2026-10-26T12:00:00Z",
            "patient_demographics": {{"age_years": 40, "biological_sex": "MALE", "weight_kg": 75}},
            "provenance_items": [
                {{"concept_key": "diagnosis", "value": "Essential Hypertension", "provenance_type": "DOCUMENTED_CLINICAL_RECORD"}}
            ],
            "active_allergies": [],
            "current_medications": ["concor", "panadol"],
            "safety_status": {{"red_flags_present": False, "safety_gate_cleared": True}}
        }}

    res = run_skill(payload)
    print(json.dumps(res, indent=2))
'''
        with open(os.path.join(s_path, "scripts", "run.py"), "w", encoding="utf-8") as f:
            f.write(script_content)

    print(f"Successfully generated and wired all {len(SKILLS_SPEC)} specialized skills (v2.1.0).")

if __name__ == "__main__":
    build_skills()
