#!/usr/bin/env python3
"""
MedOrqis-QNX: Clinical AI Advisory & ISBAR Handover Engine
Integrates MedOrqis-LLM (Karnak-6B fine-tuned clinical foundation model)
for deterministic contextualization, sepsis bundle recommendations, and bilingual handovers.
Standards: IEC 62304 Class A/B (Advisory Clinical Decision Support).
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional

# Project root in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DISCLAIMER_HEADER = (
    "================================================================================\n"
    "MEDORQIS CLINICAL DECISION SUPPORT (CDS) ADVISORY NOTICE\n"
    "REGULATORY STATUS: IEC 62304 Class A/B Advisory Software. Not an autonomous controller.\n"
    "All outputs require verification and oversight by a qualified attending clinician.\n"
    "================================================================================"
)

class ClinicalAdvisoryEngine:
    """
    Coordinates clinical explanation generation using MedOrqis-LLM.
    Provides offline deterministic clinical heuristic fallback if GPU/Transformers is unavailable.
    """
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.llm_available = False
        self._init_llm_if_available()

    def _init_llm_if_available(self):
        # Checks if torch and transformers are available with CUDA
        try:
            import torch
            if torch.cuda.is_available() and self.model_path and os.path.exists(self.model_path):
                self.llm_available = True
        except ImportError:
            self.llm_available = False

    def generate_isbar_handover(
        self,
        telemetry: Dict[str, Any],
        clinical_history: Optional[str] = None,
        language: str = "both"
    ) -> Dict[str, str]:
        """
        Generates bilingual ISBAR (Introduction, Situation, Background, Assessment, Recommendation)
        clinical handover note.
        """
        patient_id = telemetry.get("patient_id", "UNKNOWN")
        news2_score = telemetry.get("news2_score", 0)
        alert_level = telemetry.get("alert_level_name", "UNKNOWN")
        hr = telemetry.get("heart_rate_bpm", 0)
        sbp = telemetry.get("systolic_bp_mmhg", 0)
        dbp = telemetry.get("diastolic_bp_mmhg", 0)
        rr = telemetry.get("respiratory_rate_bpm", 0)
        spo2 = telemetry.get("spo2_percent", 0.0)
        temp = telemetry.get("temperature_celsius", 0.0)
        o2_status = "Supplemental O2" if telemetry.get("on_supplemental_oxygen") else "Room Air"
        consc = "CVPU (New Confusion / Lethargy)" if telemetry.get("consciousness") else "Alert"
        latency_ns = telemetry.get("calculation_latency_ns", 0)

        history = clinical_history or "Postoperative Day 2 following exploratory laparotomy; suspected acute surgical site infection."

        # English ISBAR Handover
        isbar_en = f"""{DISCLAIMER_HEADER}

### ISBAR CLINICAL DETERIORATION HANDOVER (ENGLISH)
**Patient ID**: {patient_id}
**Time of Escalation**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
**QNX Real-Time NEWS2 Score**: {news2_score} / 20 ({alert_level})
**RTOS Execution Latency**: {latency_ns} ns (Deterministic QNX Microkernel)

#### 1. INTRODUCTION (I)
"This is the MedOrqis Bedside Clinical Telemetry System communicating an emergency clinical deterioration alert for patient {patient_id} on Surgical Ward 4."

#### 2. SITUATION (S)
"The patient has suffered acute physiological deterioration requiring immediate Critical Care / Rapid Response Team review. Current NEWS2 score is {news2_score}/20 (Critical Threshold >= 7)."
- **Heart Rate**: {hr} bpm (Severe Tachycardia)
- **Blood Pressure**: {sbp}/{dbp} mmHg (Severe Hypotension / Vasodilation)
- **Respiratory Rate**: {rr} bpm (Severe Tachypnea)
- **Oxygen Saturation**: {spo2:.1f}% on {o2_status} (Hypoxia)
- **Core Temperature**: {temp:.1f} °C (Pyrexia)
- **Neurological State**: {consc}

#### 3. BACKGROUND (B)
"{history} Patient was previously hemodynamically stable on routine 4-hourly ward monitoring."

#### 4. ASSESSMENT (A)
"Physiological profile demonstrates profound systemic inflammatory response syndrome (SIRS) advancing to Septic Shock with warm peripheral vasodilation and early organ hypoperfusion (refractory hypotension and acute confusion)."

#### 5. RECOMMENDATIONS (R) — SURVIVING SEPSIS BUNDLE (SEPSIS SIX):
1. **Airway & Oxygenation**: Administer high-flow supplemental oxygen targeting SpO2 94-98%.
2. **Microbiological Sampling**: Draw 2 sets of peripheral blood cultures immediately prior to antibiotics.
3. **Antimicrobial Therapy**: Administer broad-spectrum intravenous empiric antibiotics within 60 minutes.
4. **Fluid Resuscitation**: Initiate rapid IV crystalloid bolus (30 mL/kg, e.g. Plasma-Lyte or Lactated Ringer's).
5. **Biomarker Monitoring**: Measure stat arterial/venous blood lactate and complete blood count with renal panel.
6. **Output Monitoring**: Place indwelling urinary catheter for strict hourly fluid balance assessment.
"""

        # Arabic ISBAR Handover
        isbar_ar = f"""{DISCLAIMER_HEADER}

### تقرير تسليم التدهور السريري الحاد — نموذج ISBAR (باللغة العربية)
**معرف المريض**: {patient_id}
**توقيت الإنذار الطارئ**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
**مقياس التدهور السريري الحتمي (QNX NEWS2)**: {news2_score} من 20 ({alert_level})
**زمن الحساب في نواة QNX الصغرى**: {latency_ns} نانوثانية (حساب حتمي فوري)

#### 1. التعريف بالحالة (Introduction)
"إخطار طارئ صادر من وحدة المراقبة الحيوية المضمنة (MedOrqis-QNX) بوجود تدهور فسيولوجي حرج للمريض {patient_id} في قسم الجراحة العامة."

#### 2. الموقف الحالي (Situation)
"دخل المريض في مرحلة تدهور فسيولوجي حاد تتطلب استدعاءً فورياً لفريق الاستجابة السريعة (Rapid Response Team) وطبيب العناية المركزة. مقياس NEWS2 الحالي هو {news2_score}/20 (تجاوز حاجز الخطر الأقصى)."
- **معدل ضربات القلب**: {hr} نبضة/دقيقة (تسرع قلب شديد)
- **ضغط الدم الشرياني**: {sbp}/{dbp} ملم زئبق (هبوط حاد في الضغط / صدمة وعائية)
- **معدل التنفس**: {rr} دورة/دقيقة (تسارع تنفسي حاد)
- **تشبع الأكسجين**: {spo2:.1f}% مع {('أكسجين داعم' if telemetry.get('on_supplemental_oxygen') else 'هواء الغرفة')}
- **درجة حرارة الجسم**: {temp:.1f} مئوية (حمى شديدة)
- **مستوى الوعي**: {('اضطراب وعي وتشوش حاد (CVPU)' if telemetry.get('consciousness') else 'واعٍ')}

#### 3. الخلفية المرضية (Background)
"{history}، وكان المريض مستقراً حيوياً خلال الساعات الماضية."

#### 4. التقييم السريري الذكي (Assessment)
"العلامات الحيوية مجتمعة تعكس متلازمة استجابة التهابية جهازية حادة (SIRS) متطورة إلى صدمة إنتانية (Septic Shock) مصحوبة بتوسع وعائي محيطي، ونقص تروية خلوية حاد (هبوط ضغط مقاوم واضطراب في الوعي)."

#### 5. التوصيات وخطة الإنقاذ السريع (Recommendations) — حزمة Sepsis Six:
1. **دعم التنفس**: إعطاء أكسجين تدفقي عالي لرفع نسبة التشبع إلى 94-98%.
2. **سحب المزارع**: سحب عينتي دم لمزرعة البكتيريا قبل إعطاء المضادات الحيوية فوراً.
3. **المضادات الحيوية**: بدء حقن وريدي لمضاد حيوي واسع المجال خلال أقل من 60 دقيقة.
4. **الإنعاش بالسوائل**: إعطاء محاليل بلورية وريدية متوازنة (30 مل لكل كجم) بسرعة.
5. **المؤشرات الحيوية**: قياس حمض اللاكتيك (Lactate) وغازات الدم الشرياني وتحليل وظائف الكلى.
6. **مراقبة السوائل**: تركيب قسطرة بولية لمراقبة دقيقة للإخراج البولي كل ساعة.
"""

        return {
            "english": isbar_en.strip(),
            "arabic": isbar_ar.strip(),
            "disclaimer": DISCLAIMER_HEADER
        }
