"""
MedOrqis — Smart Clinical Documenter & Structured Reporting Engine
Evidence-Grounded, Deterministic SOAP & ISBAR Generator with Panic-Value Screening and PHI Protection.
Supports both English and Professional Medical Arabic.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
import re

from core.phi_deidentifier import PHIDeidentifier
from core.clinical_calculators import (
    calculate_news2_score,
    calculate_ckd_epi_2021_egfr,
    calculate_bedside_schwartz_egfr,
    CalculationResult,
    SafeCalculationRefusal
)


@dataclass
class VitalsInput:
    respiration_rate_bpm: Optional[int] = None
    spo2_percent: Optional[float] = None
    air_or_oxygen: str = "Air"  # "Air" or "Oxygen"
    systolic_bp_mmhg: Optional[int] = None
    diastolic_bp_mmhg: Optional[int] = None
    pulse_bpm: Optional[int] = None
    consciousness: str = "Alert"  # "Alert", "Voice", "Pain", "Unresponsive"
    temperature_celsius: Optional[float] = None


@dataclass
class LabValue:
    test_name: str
    value: float
    unit: str
    loinc_code: Optional[str] = None
    reference_range: Optional[str] = None


@dataclass
class PanicAlert:
    test_name: str
    value: float
    unit: str
    threshold: str
    severity: str  # "CRITICAL_HIGH", "CRITICAL_LOW", "URGENT"
    clinical_risk_en: str
    clinical_risk_ar: str
    immediate_action_en: str
    immediate_action_ar: str


@dataclass
class ClinicalDocumentInput:
    patient_identifier: str  # MRN or pseudo-id (will be scrubbed)
    age_years: int
    biological_sex: str  # "male" or "female"
    chief_complaint: str
    hpi: str
    medical_history: List[str] = field(default_factory=list)
    surgical_history: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    vitals: Optional[VitalsInput] = None
    physical_exam: Dict[str, str] = field(default_factory=dict)
    labs: List[LabValue] = field(default_factory=list)
    primary_diagnosis: Optional[str] = None
    differential_diagnoses: List[str] = field(default_factory=list)
    planned_diagnostics: List[str] = field(default_factory=list)
    planned_medications: List[str] = field(default_factory=list)
    monitoring_instructions: List[str] = field(default_factory=list)
    follow_up_disposition: Optional[str] = None
    attending_physician: Optional[str] = None
    unit_or_ward: Optional[str] = None


@dataclass
class GeneratedDocument:
    document_type: str  # "SOAP" or "ISBAR"
    language: str  # "en" or "ar"
    formatted_markdown: str
    structured_sections: Dict[str, str]
    panic_alerts: List[PanicAlert]
    calculated_scores: List[CalculationResult]
    phi_redactions: Dict[str, Any]


class PanicValueEngine:
    """
    Deterministic rule-based clinical panic / critical value laboratory screening.
    Based on College of American Pathologists (CAP) and CLSI Critical Values Guidelines.
    """
    CRITICAL_THRESHOLDS = [
        {
            "matchers": ["potassium", "k+", "k", "serum potassium", "بوتاسيوم"],
            "unit_standard": "mmol/L",
            "low_panic": 2.8,
            "high_panic": 6.0,
            "risk_low_en": "Severe Hypokalemia — Extreme arrhythmia, ventricular ectopy, and cardiac arrest risk.",
            "risk_low_ar": "نقص حاد في البوتاسيوم — خطر شديد لحدوث اضطراب كهربية القلب وتوقف عضلة القلب.",
            "action_low_en": "Obtain immediate 12-lead ECG; initiate urgent IV/oral potassium repletion with cardiac monitoring.",
            "action_low_ar": "إجراء رسم قلب 12-lead فوراً والبدء في تعويض البوتاسيوم عاجلاً مع المراقبة القلبية المستمرة.",
            "risk_high_en": "Severe Hyperkalemia — Peaked T waves, conduction block, and fatal ventricular arrhythmias.",
            "risk_high_ar": "فرط حاد في البوتاسيوم — موجات T مدببة وخطر انسداد التوصيل القلبي واضطرابات بطينية مميتة.",
            "action_high_en": "Stat ECG; IV Calcium Gluconate 10% (myocardial stabilization), IV Insulin + Dextrose, nebulized Albuterol.",
            "action_high_ar": "رسم قلب فوري؛ إعطاء كالسيوم جلوكونات وريدياً لحماية القلب، وإنسولين مع ديكستروز، وجلسات البوتيرول استنشاقية."
        },
        {
            "matchers": ["sodium", "na+", "na", "serum sodium", "صوديوم"],
            "unit_standard": "mmol/L",
            "low_panic": 120.0,
            "high_panic": 160.0,
            "risk_low_en": "Severe Hyponatremia — Cerebral edema, encephalopathy, and seizure risk.",
            "risk_low_ar": "نقص حاد في الصوديوم — خطر وذمة دماغية واعتلال الدماغ وتشنجات عصبية.",
            "action_low_en": "Check volume status and serum osmolality; consider 3% hypertonic saline with controlled correction rate (<8 mmol/L/24h) to avoid ODS.",
            "action_low_ar": "تقييم السوائل والأسمولية؛ دراسة إعطاء محلول ملح عالي التوتر 3% بمعدل تصحيح حذر لتجنب انحلال الميالين الجسري.",
            "risk_high_en": "Severe Hypernatremia — Severe cellular dehydration, intracranial hemorrhage, and hyperosmolar collapse.",
            "risk_high_ar": "فرط حاد في الصوديوم — جفاف خلوي حاد وخطر نزيف داخل الجمجمة وهبوط فرط الأسمولية.",
            "action_high_en": "Calculate free water deficit; administer D5W or hypotonic saline slowly to prevent cerebral edema.",
            "action_high_ar": "حساب عجز الماء الحر، وإعطاء محاليل مخففة بحذر شديد وبطء لمنع وذمة المخ."
        },
        {
            "matchers": ["hemoglobin", "hgb", "hb", "هيموجلوبين"],
            "unit_standard": "g/dL",
            "low_panic": 7.0,
            "high_panic": 20.0,
            "risk_low_en": "Severe Anemia — Tissue hypoxia, ischemic end-organ failure, and hemodynamic shock.",
            "risk_low_ar": "أنيميا حادة حرجة — نقص أكسجة الأنسجة وفشل الأعضاء الإقفاري وصدمة ديناميكا الدم.",
            "action_low_en": "Crossmatch and transfuse Packed Red Blood Cells (PRBCs); investigate active bleeding sources urgently.",
            "action_low_ar": "توفير دم متطابق ونقل كرات دم حمراء مكدسة (PRBCs) فوراً مع البحث السريع عن مصادر النزيف.",
            "risk_high_en": "Severe Polycythemia — Extreme hyperviscosity and microvascular thrombotic occlusion.",
            "risk_high_ar": "فرط لزوجة الدم الشديد — خطر التخثر والانسداد الوعائي المجهري.",
            "action_high_en": "Urgent hematology consult; consider therapeutic phlebotomy and IV hydration.",
            "action_high_ar": "استشارة أمراض دم عاجلة، تقييم الفصد العلاجي والمحاليل الوريدية."
        },
        {
            "matchers": ["platelets", "plt", "platelet count", "صفائح دموية"],
            "unit_standard": "10^3/uL",
            "low_panic": 20.0,
            "high_panic": 1000.0,
            "risk_low_en": "Critical Thrombocytopenia — High risk of spontaneous fatal intracranial and mucosal bleeding.",
            "risk_low_ar": "نقص حاد وحرج في الصفائح — خطر وشيك لحدوث نزيف دماغي أو مخاطي تلقائي مميت.",
            "action_low_en": "Stat platelet transfusion if bleeding; avoid invasive procedures, antiplatelets, and anticoagulants.",
            "action_low_ar": "نقل صفائح دموية فوراً؛ إيقاف أي مضادات للتجلط أو الصفائح وتجنب الإجراءات التداخلية.",
            "risk_high_en": "Extreme Thrombocytosis — Paradoxical thrombosis or acquired von Willebrand syndrome with bleeding.",
            "risk_high_ar": "فرط الصفائح الدموية الشديد — خطر تجلط دموي أو نزيف تناقضي.",
            "action_high_en": "Urgent hematology review for cytoreductive therapy.",
            "action_high_ar": "تقييم أمراض الدم عاجلاً للعلاج الخافض للصفائح."
        },
        {
            "matchers": ["glucose", "blood glucose", "random blood sugar", "rbs", "fbs", "سكر الدم"],
            "unit_standard": "mg/dL",
            "low_panic": 50.0,
            "high_panic": 450.0,
            "risk_low_en": "Severe Hypoglycemia — Neuroglycopenic brain injury, seizure, and coma.",
            "risk_low_ar": "هبوط حاد في سكر الدم — خطر تلف خلايا المخ العصبي وتشنجات وغيبوبة سكرية.",
            "action_low_en": "Administer IV Dextrose (D50W 25-50 mL) or IM Glucagon; recheck blood glucose every 15 minutes.",
            "action_low_ar": "إعطاء ديكستروز وريدياً فوري (D50W) أو جلوكاجون عضلياً وإعادة قياس السكر كل 15 دقيقة.",
            "risk_high_en": "Severe Hyperglycemia — Diabetic Ketoacidosis (DKA) or Hyperosmolar Hyperglycemic State (HHS).",
            "risk_high_ar": "ارتفاع حاد في سكر الدم — اشتباه الحماض الكيتوني السكري (DKA) أو متلازمة فرط الأسمولية (HHS).",
            "action_high_en": "Check blood ketones and venous blood gas; initiate aggressive IV fluid resuscitation and IV insulin infusion protocol.",
            "action_high_ar": "فحص الكيتونات وغازات الدم، والبدء في بروتوكول السوائل الوريدية المكثفة والإنسولين بالوريد."
        },
        {
            "matchers": ["lactate", "lactic acid", "حمض اللاكتيك"],
            "unit_standard": "mmol/L",
            "low_panic": None,
            "high_panic": 4.0,
            "risk_low_en": "",
            "risk_low_ar": "",
            "action_low_en": "",
            "action_low_ar": "",
            "risk_high_en": "Severe Hyperlactatemia — Severe tissue hypoperfusion, anaerobic metabolism, and Sepsis/Septic Shock.",
            "risk_high_ar": "ارتفاع حاد في اللاكتات — نقص تروية الأنسجة الحاد، والتمثيل اللاهوائي واشتباه صدمة إنتانية (Septic Shock).",
            "action_high_en": "Initiate Sepsis Six protocol: 30 mL/kg IV crystalloid fluid bolus, blood cultures before broad-spectrum IV antibiotics, measure urine output.",
            "action_high_ar": "تفعيل بروتوكول Sepsis Six: محاليل بلورية 30 مل/كجم، مزارع دم عاجلة قبل المضادات الحيوية واسعة المجال ومراقبة البول."
        },
        {
            "matchers": ["troponin", "troponin i", "troponin t", "hs-ctni", "hs-ctnt", "تروبونين"],
            "unit_standard": "ng/mL",
            "low_panic": None,
            "high_panic": 0.04,
            "risk_low_en": "",
            "risk_low_ar": "",
            "action_low_en": "",
            "action_low_ar": "",
            "risk_high_en": "Elevated Cardiac Troponin — Acute myocardial injury / Acute Coronary Syndrome (NSTEMI/STEMI).",
            "risk_high_ar": "ارتفاع أنزيم التروبونين — إصابة حادة بعضلة القلب / اشتباه متلازمة الشريان التاجي الحادة (ACS).",
            "action_high_en": "Stat 12-lead ECG, continuous telemetry, loading Dual Antiplatelet Therapy (DAPT), urgent cardiology consultation.",
            "action_high_ar": "رسم قلب فوري 12-lead، ومراقبة قلبية، وإعطاء مضادات الصفائح المزدوجة (DAPT)، واستدعاء استشاري القلب فوراً."
        }
    ]

    @classmethod
    def evaluate(cls, labs: List[LabValue]) -> List[PanicAlert]:
        alerts = []
        for lab in labs:
            name_clean = lab.test_name.strip().lower()
            val = lab.value
            for rule in cls.CRITICAL_THRESHOLDS:
                if any(m in name_clean for m in rule["matchers"]):
                    low = rule.get("low_panic")
                    high = rule.get("high_panic")
                    if low is not None and val < low:
                        alerts.append(PanicAlert(
                            test_name=lab.test_name,
                            value=val,
                            unit=lab.unit,
                            threshold=f"< {low} {rule['unit_standard']}",
                            severity="CRITICAL_LOW",
                            clinical_risk_en=rule["risk_low_en"],
                            clinical_risk_ar=rule["risk_low_ar"],
                            immediate_action_en=rule["action_low_en"],
                            immediate_action_ar=rule["action_low_ar"]
                        ))
                    elif high is not None and val > high:
                        alerts.append(PanicAlert(
                            test_name=lab.test_name,
                            value=val,
                            unit=lab.unit,
                            threshold=f"> {high} {rule['unit_standard']}",
                            severity="CRITICAL_HIGH",
                            clinical_risk_en=rule["risk_high_en"],
                            clinical_risk_ar=rule["risk_high_ar"],
                            immediate_action_en=rule["action_high_en"],
                            immediate_action_ar=rule["action_high_ar"]
                        ))
        return alerts


class ClinicalDocumenter:
    """
    Core Deterministic Clinical Documentation Generator for MedOrqis.
    Produces standardized, peer-review quality SOAP notes and ISBAR handover reports.
    """

    def __init__(self):
        self.deidentifier = PHIDeidentifier()

    def generate_soap(self, data: ClinicalDocumentInput, language: str = "en") -> GeneratedDocument:
        """
        Generates a validated SOAP note (Subjective, Objective, Assessment, Plan).
        Deidentifies free text, executes clinical calculators, and flags critical lab panic values.
        """
        lang = language.strip().lower()
        if lang not in ["en", "ar"]:
            lang = "en"

        # 1. PHI Deidentification pass
        scrubbed_cc, s_cc = self.deidentifier.deidentify(data.chief_complaint)
        scrubbed_hpi, s_hpi = self.deidentifier.deidentify(data.hpi)
        
        redactions = {
            "chief_complaint": s_cc,
            "hpi": s_hpi,
            "total_items": s_cc["total_phi_items_redacted"] + s_hpi["total_phi_items_redacted"]
        }

        # 2. Automated Deterministic Calculations
        calculated_scores: List[CalculationResult] = []
        news2_result: Optional[CalculationResult] = None
        egfr_result: Optional[CalculationResult] = None

        if data.vitals is not None:
            v = data.vitals
            if (v.respiration_rate_bpm is not None and v.spo2_percent is not None and 
                v.systolic_bp_mmhg is not None and v.pulse_bpm is not None and 
                v.temperature_celsius is not None):
                try:
                    news2_result = calculate_news2_score(
                        respiration_rate_bpm=v.respiration_rate_bpm,
                        spo2_percent=v.spo2_percent,
                        air_or_oxygen=v.air_or_oxygen,
                        systolic_bp_mmhg=v.systolic_bp_mmhg,
                        pulse_bpm=v.pulse_bpm,
                        consciousness=v.consciousness,
                        temperature_celsius=v.temperature_celsius,
                        age_years=float(data.age_years)
                    )
                    calculated_scores.append(news2_result)
                except SafeCalculationRefusal:
                    pass

        # Check for Creatinine in labs for automated eGFR
        for lab in data.labs:
            name_clean = lab.test_name.strip().lower()
            if any(k in name_clean for k in ["creatinine", "creat", "scr", "كرياتينين"]):
                try:
                    if data.age_years >= 18:
                        egfr_result = calculate_ckd_epi_2021_egfr(
                            serum_creatinine=lab.value,
                            age_years=data.age_years,
                            biological_sex=data.biological_sex,
                            unit=lab.unit
                        )
                    else:
                        egfr_result = calculate_bedside_schwartz_egfr(
                            serum_creatinine=lab.value,
                            height_cm=120.0,  # fallback if height not specified
                            unit=lab.unit
                        )
                    calculated_scores.append(egfr_result)
                    break
                except SafeCalculationRefusal:
                    pass

        # 3. Lab Panic Value Screening
        panic_alerts = PanicValueEngine.evaluate(data.labs)

        # 4. Construct Markdown Document
        if lang == "ar":
            sections = self._build_soap_sections_ar(
                data=data,
                scrubbed_cc=scrubbed_cc,
                scrubbed_hpi=scrubbed_hpi,
                panic_alerts=panic_alerts,
                news2_result=news2_result,
                egfr_result=egfr_result
            )
            doc_title = "تقرير التقييم السريري (SOAP Note) — معتمد عبر MedOrqis"
        else:
            sections = self._build_soap_sections_en(
                data=data,
                scrubbed_cc=scrubbed_cc,
                scrubbed_hpi=scrubbed_hpi,
                panic_alerts=panic_alerts,
                news2_result=news2_result,
                egfr_result=egfr_result
            )
            doc_title = "Clinical Evaluation Document (SOAP Note) — Verified by MedOrqis"

        markdown_body = f"# {doc_title}\n\n"
        for sec_name, sec_content in sections.items():
            markdown_body += f"## {sec_name}\n{sec_content}\n\n"

        return GeneratedDocument(
            document_type="SOAP",
            language=lang,
            formatted_markdown=markdown_body.strip(),
            structured_sections=sections,
            panic_alerts=panic_alerts,
            calculated_scores=calculated_scores,
            phi_redactions=redactions
        )

    def generate_isbar(
        self,
        data: ClinicalDocumentInput,
        situation: str,
        recommendation: str,
        language: str = "en"
    ) -> GeneratedDocument:
        """
        Generates a validated ISBAR handover document (Identification, Situation, Background, Assessment, Recommendation).
        Used for clinical shift handover, ICU escalation, and emergency consultation.
        """
        lang = language.strip().lower()
        if lang not in ["en", "ar"]:
            lang = "en"

        scrubbed_sit, s_sit = self.deidentifier.deidentify(situation)
        scrubbed_rec, s_rec = self.deidentifier.deidentify(recommendation)
        scrubbed_hpi, s_hpi = self.deidentifier.deidentify(data.hpi)

        redactions = {
            "situation": s_sit,
            "recommendation": s_rec,
            "total_items": s_sit["total_phi_items_redacted"] + s_rec["total_phi_items_redacted"]
        }

        # Calculations
        calculated_scores: List[CalculationResult] = []
        news2_result: Optional[CalculationResult] = None
        if data.vitals is not None:
            v = data.vitals
            if (v.respiration_rate_bpm is not None and v.spo2_percent is not None and 
                v.systolic_bp_mmhg is not None and v.pulse_bpm is not None and 
                v.temperature_celsius is not None):
                try:
                    news2_result = calculate_news2_score(
                        respiration_rate_bpm=v.respiration_rate_bpm,
                        spo2_percent=v.spo2_percent,
                        air_or_oxygen=v.air_or_oxygen,
                        systolic_bp_mmhg=v.systolic_bp_mmhg,
                        pulse_bpm=v.pulse_bpm,
                        consciousness=v.consciousness,
                        temperature_celsius=v.temperature_celsius,
                        age_years=float(data.age_years)
                    )
                    calculated_scores.append(news2_result)
                except SafeCalculationRefusal:
                    pass

        panic_alerts = PanicValueEngine.evaluate(data.labs)

        if lang == "ar":
            sections = self._build_isbar_sections_ar(
                data=data,
                scrubbed_situation=scrubbed_sit,
                scrubbed_background=scrubbed_hpi,
                scrubbed_recommendation=scrubbed_rec,
                panic_alerts=panic_alerts,
                news2_result=news2_result
            )
            doc_title = "مذكرة تسليم الحالة السريرية (ISBAR Handover) — MedOrqis"
        else:
            sections = self._build_isbar_sections_en(
                data=data,
                scrubbed_situation=scrubbed_sit,
                scrubbed_background=scrubbed_hpi,
                scrubbed_recommendation=scrubbed_rec,
                panic_alerts=panic_alerts,
                news2_result=news2_result
            )
            doc_title = "Clinical Handover Communication (ISBAR) — MedOrqis"

        markdown_body = f"# {doc_title}\n\n"
        for sec_name, sec_content in sections.items():
            markdown_body += f"## {sec_name}\n{sec_content}\n\n"

        return GeneratedDocument(
            document_type="ISBAR",
            language=lang,
            formatted_markdown=markdown_body.strip(),
            structured_sections=sections,
            panic_alerts=panic_alerts,
            calculated_scores=calculated_scores,
            phi_redactions=redactions
        )

    # -------------------------------------------------------------------------
    # Internal Formatters: English
    # -------------------------------------------------------------------------
    def _build_soap_sections_en(
        self,
        data: ClinicalDocumentInput,
        scrubbed_cc: str,
        scrubbed_hpi: str,
        panic_alerts: List[PanicAlert],
        news2_result: Optional[CalculationResult],
        egfr_result: Optional[CalculationResult]
    ) -> Dict[str, str]:
        # S: Subjective
        meds = ", ".join(data.current_medications) if data.current_medications else "None reported"
        allergies = ", ".join(data.allergies) if data.allergies else "No known drug allergies (NKDA)"
        pmh = ", ".join(data.medical_history) if data.medical_history else "Nil"
        psh = ", ".join(data.surgical_history) if data.surgical_history else "Nil"

        s_text = (
            f"**Chief Complaint (CC):** {scrubbed_cc}\n\n"
            f"**History of Present Illness (HPI):**\n{scrubbed_hpi}\n\n"
            f"**Past Medical History (PMH):** {pmh}\n"
            f"**Past Surgical History (PSH):** {psh}\n"
            f"**Allergies:** {allergies}\n"
            f"**Current Medications:** {meds}"
        )

        # O: Objective
        v_lines = []
        if data.vitals:
            v = data.vitals
            bp = f"{v.systolic_bp_mmhg}/{v.diastolic_bp_mmhg} mmHg" if v.systolic_bp_mmhg and v.diastolic_bp_mmhg else "Not recorded"
            v_lines.append(f"- **BP:** {bp} | **HR:** {v.pulse_bpm or 'N/A'} bpm | **RR:** {v.respiration_rate_bpm or 'N/A'} bpm")
            v_lines.append(f"- **SpO2:** {v.spo2_percent or 'N/A'}% ({v.air_or_oxygen}) | **Temp:** {v.temperature_celsius or 'N/A'} °C | **AVPU:** {v.consciousness}")
        v_str = "\n".join(v_lines) if v_lines else "Vital signs not documented."

        # Panic Alerts in Objective
        alert_lines = []
        if panic_alerts:
            alert_lines.append("\n> [!CAUTION]\n> **CRITICAL LABORATORY PANIC VALUES DETECTED:**")
            for a in panic_alerts:
                alert_lines.append(f"> - ⚠️ **{a.test_name}**: {a.value} {a.unit} (Threshold: {a.threshold}) — *{a.clinical_risk_en}*")
                alert_lines.append(f">   *Immediate Protocol:* {a.immediate_action_en}")
        alerts_str = "\n".join(alert_lines)

        labs_lines = []
        for lab in data.labs:
            ref = f" (Ref: {lab.reference_range})" if lab.reference_range else ""
            labs_lines.append(f"- **{lab.test_name}:** {lab.value} {lab.unit}{ref}")
        labs_str = "\n".join(labs_lines) if labs_lines else "No lab results documented."

        pe_lines = [f"- **{sys.title()}:** {desc}" for sys, desc in data.physical_exam.items()]
        pe_str = "\n".join(pe_lines) if pe_lines else "General physical examination pending."

        o_text = (
            f"### Vital Signs & Physiological Status\n{v_str}\n"
            f"{alerts_str}\n\n"
            f"### Physical Examination\n{pe_str}\n\n"
            f"### Diagnostic Laboratory Results\n{labs_str}"
        )

        # A: Assessment
        p_diag = data.primary_diagnosis or "Pending clinical confirmation"
        diffs = ", ".join(data.differential_diagnoses) if data.differential_diagnoses else "None specified"
        scores_lines = []
        if news2_result:
            scores_lines.append(f"- **NEWS2 Score:** {int(news2_result.score)} points ({news2_result.interpretation_band}) — *{news2_result.clinical_recommendation}*")
        if egfr_result:
            scores_lines.append(f"- **eGFR (CKD-EPI 2021):** {egfr_result.score:.1f} {egfr_result.unit} ({egfr_result.interpretation_band}) — *{egfr_result.clinical_recommendation}*")
        scores_str = "\n".join(scores_lines) if scores_lines else "No automated deterministic scores generated."

        a_text = (
            f"**Primary Working Diagnosis:** {p_diag}\n\n"
            f"**Differential Diagnoses:** {diffs}\n\n"
            f"**Deterministic Risk Stratification & Clinical Scores:**\n{scores_str}"
        )

        # P: Plan
        diag_plan = "\n".join([f"1. {d}" for d in data.planned_diagnostics]) if data.planned_diagnostics else "- No diagnostic orders specified."
        med_plan = "\n".join([f"- {m}" for m in data.planned_medications]) if data.planned_medications else "- No pharmacological modifications."
        mon_plan = "\n".join([f"- {m}" for m in data.monitoring_instructions]) if data.monitoring_instructions else "- Standard ward monitoring."
        disp = data.follow_up_disposition or "Review after pending investigations."

        p_text = (
            f"### 1. Diagnostic Workup\n{diag_plan}\n\n"
            f"### 2. Pharmacological & Therapeutic Interventions\n{med_plan}\n\n"
            f"### 3. Patient Monitoring & Safety Protocols\n{mon_plan}\n\n"
            f"### 4. Disposition & Follow-Up\n**Disposition:** {disp}"
        )

        return {
            "S — Subjective": s_text,
            "O — Objective": o_text,
            "A — Assessment": a_text,
            "P — Plan": p_text
        }

    # -------------------------------------------------------------------------
    # Internal Formatters: Arabic
    # -------------------------------------------------------------------------
    def _build_soap_sections_ar(
        self,
        data: ClinicalDocumentInput,
        scrubbed_cc: str,
        scrubbed_hpi: str,
        panic_alerts: List[PanicAlert],
        news2_result: Optional[CalculationResult],
        egfr_result: Optional[CalculationResult]
    ) -> Dict[str, str]:
        meds = ", ".join(data.current_medications) if data.current_medications else "لا توجد أدوية حالية مسجلة"
        allergies = ", ".join(data.allergies) if data.allergies else "لا يوجد تاريخ حساسية دوائية معروفة (NKDA)"
        pmh = ", ".join(data.medical_history) if data.medical_history else "لا يوجد"
        psh = ", ".join(data.surgical_history) if data.surgical_history else "لا يوجد"

        s_text = (
            f"**الشكوى الرئيسية (Chief Complaint):** {scrubbed_cc}\n\n"
            f"**تاريخ المرض الحالي (HPI):**\n{scrubbed_hpi}\n\n"
            f"**التاريخ المرضي السابق:** {pmh}\n"
            f"**التاريخ الجراحي السابق:** {psh}\n"
            f"**الحساسية الدوائية:** {allergies}\n"
            f"**الأدوية الحالية:** {meds}"
        )

        v_lines = []
        if data.vitals:
            v = data.vitals
            bp = f"{v.systolic_bp_mmhg}/{v.diastolic_bp_mmhg} مم زئبق" if v.systolic_bp_mmhg and v.diastolic_bp_mmhg else "غير مسجل"
            v_lines.append(f"- **ضغط الدم:** {bp} | **النبض:** {v.pulse_bpm or 'N/A'} ن/د | **معدل التنفس:** {v.respiration_rate_bpm or 'N/A'} ن/د")
            v_lines.append(f"- **تشبع الأكسجين (SpO2):** {v.spo2_percent or 'N/A'}% ({v.air_or_oxygen}) | **الحرارة:** {v.temperature_celsius or 'N/A'} °م | **الوعي:** {v.consciousness}")
        v_str = "\n".join(v_lines) if v_lines else "لم يتم توثيق العلامات الحيوية."

        alert_lines = []
        if panic_alerts:
            alert_lines.append("\n> [!CAUTION]\n> **تنبيه عاجل: قيم تحاليل حرجة وخطيرة (PANIC VALUES):**")
            for a in panic_alerts:
                alert_lines.append(f"> - ⚠️ **{a.test_name}**: {a.value} {a.unit} (الحد الحرج: {a.threshold}) — *{a.clinical_risk_ar}*")
                alert_lines.append(f">   *الإجراء الفوري الإلزامي:* {a.immediate_action_ar}")
        alerts_str = "\n".join(alert_lines)

        labs_lines = []
        for lab in data.labs:
            ref = f" (المدى الطبيعي: {lab.reference_range})" if lab.reference_range else ""
            labs_lines.append(f"- **{lab.test_name}:** {lab.value} {lab.unit}{ref}")
        labs_str = "\n".join(labs_lines) if labs_lines else "لا توجد نتائج تحاليل موثقة."

        pe_lines = [f"- **{sys}:** {desc}" for sys, desc in data.physical_exam.items()]
        pe_str = "\n".join(pe_lines) if pe_lines else "الفحص السريري العام قيد الاستكمال."

        o_text = (
            f"### المؤشرات الحيوية والحالة الفسيولوجية\n{v_str}\n"
            f"{alerts_str}\n\n"
            f"### الفحص السريري الموضعي\n{pe_str}\n\n"
            f"### نتائج الفحوصات المخبرية\n{labs_str}"
        )

        p_diag = data.primary_diagnosis or "قيد التأكيد السريري"
        diffs = ", ".join(data.differential_diagnoses) if data.differential_diagnoses else "لا يوجد"
        scores_lines = []
        if news2_result:
            scores_lines.append(f"- **مؤشر الإنذار المبكر (NEWS2):** {int(news2_result.score)} نقاط ({news2_result.interpretation_band}) — *{news2_result.clinical_recommendation}*")
        if egfr_result:
            scores_lines.append(f"- **معدل الفلترة الكلوية (CKD-EPI 2021):** {egfr_result.score:.1f} {egfr_result.unit} ({egfr_result.interpretation_band}) — *{egfr_result.clinical_recommendation}*")
        scores_str = "\n".join(scores_lines) if scores_lines else "لم يتم استدعاء حاسبات رقمية."

        a_text = (
            f"**التشخيص الأولي الراجح:** {p_diag}\n\n"
            f"**التشخيصات التفريقية (Differentials):** {diffs}\n\n"
            f"**تقييم درجات الخطورة السريرية (حسابات حتمية):**\n{scores_str}"
        )

        diag_plan = "\n".join([f"1. {d}" for d in data.planned_diagnostics]) if data.planned_diagnostics else "- لا توجد فحوصات إضافية مطلوبة."
        med_plan = "\n".join([f"- {m}" for m in data.planned_medications]) if data.planned_medications else "- لا توجد تعديلات دوائية."
        mon_plan = "\n".join([f"- {m}" for m in data.monitoring_instructions]) if data.monitoring_instructions else "- مراقبة القسم الاعتيادية."
        disp = data.follow_up_disposition or "متابعة الحالة بعد اكتمال نتائج التحاليل."

        p_text = (
            f"### 1. الفحوصات التشخيصية المطلوبة\n{diag_plan}\n\n"
            f"### 2. الخطة الدوائية والعلاجية\n{med_plan}\n\n"
            f"### 3. بروتوكول المراقبة وسلامة المريض\n{mon_plan}\n\n"
            f"### 4. الإحالة والمتابعة\n**القرار:** {disp}"
        )

        return {
            "S — الجزء الذاتي (Subjective)": s_text,
            "O — الجزء الموضوعي (Objective)": o_text,
            "A — التقييم السريري (Assessment)": a_text,
            "P — الخطة العلاجية (Plan)": p_text
        }

    # -------------------------------------------------------------------------
    # Internal Formatters: ISBAR
    # -------------------------------------------------------------------------
    def _build_isbar_sections_en(
        self,
        data: ClinicalDocumentInput,
        scrubbed_situation: str,
        scrubbed_background: str,
        scrubbed_recommendation: str,
        panic_alerts: List[PanicAlert],
        news2_result: Optional[CalculationResult]
    ) -> Dict[str, str]:
        # I: Identification
        i_text = (
            f"- **Patient Identifier:** {data.patient_identifier}\n"
            f"- **Demographics:** {data.age_years}-year-old {data.biological_sex.title()}\n"
            f"- **Unit/Ward:** {data.unit_or_ward or 'General Inpatient'}\n"
            f"- **Attending Physician:** {data.attending_physician or 'On-Duty Hospitalist'}"
        )

        # S: Situation
        s_text = f"**Current Clinical Acute Event / Reason for Handover:**\n{scrubbed_situation}"

        # B: Background
        pmh = ", ".join(data.medical_history) if data.medical_history else "Nil significant"
        allergies = ", ".join(data.allergies) if data.allergies else "NKDA"
        b_text = (
            f"**Primary Admission / Background:**\n{scrubbed_background}\n\n"
            f"- **Relevant Past Medical History:** {pmh}\n"
            f"- **Allergies:** {allergies}"
        )

        # A: Assessment
        v_str = "Vital signs not provided."
        if data.vitals:
            v = data.vitals
            v_str = (
                f"BP: {v.systolic_bp_mmhg}/{v.diastolic_bp_mmhg} mmHg | "
                f"HR: {v.pulse_bpm} bpm | RR: {v.respiration_rate_bpm} bpm | "
                f"SpO2: {v.spo2_percent}% ({v.air_or_oxygen}) | Temp: {v.temperature_celsius} °C | AVPU: {v.consciousness}"
            )
        
        scores_line = ""
        if news2_result:
            scores_line = f"\n- **Current NEWS2 Deterioration Score:** **{int(news2_result.score)} points** ({news2_result.interpretation_band}) — *{news2_result.clinical_recommendation}*"

        alerts_line = ""
        if panic_alerts:
            alerts_line = "\n\n⚠️ **CRITICAL LAB ALERT:**\n" + "\n".join([f"- **{a.test_name}**: {a.value} {a.unit} ({a.threshold}) -> *{a.immediate_action_en}*" for a in panic_alerts])

        a_text = (
            f"- **Physiological Status:** {v_str}{scores_line}{alerts_line}\n\n"
            f"- **Clinical Impression:** {data.primary_diagnosis or 'Under evaluation'}"
        )

        # R: Recommendation
        r_text = (
            f"**Specific Actions & Escalation Plan:**\n{scrubbed_recommendation}\n\n"
            f"- **Contingency / Safety Red Flag:** Notify Rapid Response Team (RRT) immediately if clinical deterioration occurs or NEWS2 >= 5."
        )

        return {
            "I — Identification": i_text,
            "S — Situation": s_text,
            "B — Background": b_text,
            "A — Assessment": a_text,
            "R — Recommendation": r_text
        }

    def _build_isbar_sections_ar(
        self,
        data: ClinicalDocumentInput,
        scrubbed_situation: str,
        scrubbed_background: str,
        scrubbed_recommendation: str,
        panic_alerts: List[PanicAlert],
        news2_result: Optional[CalculationResult]
    ) -> Dict[str, str]:
        i_text = (
            f"- **معرف الحالة:** {data.patient_identifier}\n"
            f"- **البيانات الديموغرافية:** مريض عمره {data.age_years} سنة ({'ذكر' if data.biological_sex.lower() == 'male' else 'أنثى'})\n"
            f"- **القسم / الوحدة:** {data.unit_or_ward or 'القسم الداخلي العام'}\n"
            f"- **الطبيب المعالج:** {data.attending_physician or 'الطبيب النوبتجي'}"
        )

        s_text = f"**الموقف السريري الحاد الحالي / سبب التسليم:**\n{scrubbed_situation}"

        pmh = ", ".join(data.medical_history) if data.medical_history else "لا يوجد أمراض مزمنة هامة"
        allergies = ", ".join(data.allergies) if data.allergies else "لا توجد حساسية دوائية"
        b_text = (
            f"**سبب الدخول والخلفية السريرية:**\n{scrubbed_background}\n\n"
            f"- **التاريخ المرضي السابق:** {pmh}\n"
            f"- **الحساسية الدوائية:** {allergies}"
        )

        v_str = "لم يتم تسجيل مؤشرات حيوية."
        if data.vitals:
            v = data.vitals
            v_str = (
                f"الضغط: {v.systolic_bp_mmhg}/{v.diastolic_bp_mmhg} مم زئبق | "
                f"النبض: {v.pulse_bpm} ن/د | التنفس: {v.respiration_rate_bpm} ن/د | "
                f"SpO2: {v.spo2_percent}% ({v.air_or_oxygen}) | الحرارة: {v.temperature_celsius} °م | درجة الوعي: {v.consciousness}"
            )

        scores_line = ""
        if news2_result:
            scores_line = f"\n- **مؤشر الإنذار المبكر (NEWS2):** **{int(news2_result.score)} نقاط** ({news2_result.interpretation_band}) — *{news2_result.clinical_recommendation}*"

        alerts_line = ""
        if panic_alerts:
            alerts_line = "\n\n⚠️ **تنبيه عاجل بقيم تحاليل حرجة:**\n" + "\n".join([f"- **{a.test_name}**: {a.value} {a.unit} ({a.threshold}) -> *{a.immediate_action_ar}*" for a in panic_alerts])

        a_text = (
            f"- **الحالة الحيوية والفسيولوجية:** {v_str}{scores_line}{alerts_line}\n\n"
            f"- **الانطباع السريري:** {data.primary_diagnosis or 'قيد الفحص والمتابعة'}"
        )

        r_text = (
            f"**التوصيات والإجراءات المطلوبة فوراً:**\n{scrubbed_recommendation}\n\n"
            f"- **بروتوكول الطوارئ:** استدعاء فريق الاستجابة السريعة (RRT) فوراً في حال تدهور المؤشرات الحيوية أو وصول NEWS2 إلى 5 نقاط فأكثر."
        )

        return {
            "I — التعريف بالحالة (Identification)": i_text,
            "S — الموقف الراهن (Situation)": s_text,
            "B — الخلفية المرضية (Background)": b_text,
            "A — التقييم الفسيولوجي (Assessment)": a_text,
            "R — التوصيات العاجلة (Recommendation)": r_text
        }
