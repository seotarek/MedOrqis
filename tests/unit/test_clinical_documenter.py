"""
Unit Tests for MedOrqis Smart Clinical Documenter & Structured Reporting Engine
Verifies deterministic SOAP & ISBAR generation, Panic Values, and PHI protection.
"""

import unittest
from core.clinical_documenter import (
    ClinicalDocumenter,
    ClinicalDocumentInput,
    VitalsInput,
    LabValue,
    PanicValueEngine
)


class TestClinicalDocumenter(unittest.TestCase):

    def setUp(self):
        self.doc = ClinicalDocumenter()

    def test_soap_generation_english_with_news2(self):
        vitals = VitalsInput(
            respiration_rate_bpm=26,
            spo2_percent=91.0,
            air_or_oxygen="Oxygen",
            systolic_bp_mmhg=92,
            diastolic_bp_mmhg=58,
            pulse_bpm=115,
            consciousness="Alert",
            temperature_celsius=38.8
        )
        data = ClinicalDocumentInput(
            patient_identifier="PT-10023",
            age_years=62,
            biological_sex="male",
            chief_complaint="Severe shortness of breath and high fever for 3 days.",
            hpi="Patient developed productive cough with purulent sputum, worsening dyspnea, and rigors.",
            medical_history=["Type 2 Diabetes Mellitus", "Hypertension"],
            allergies=["Penicillin"],
            current_medications=["Metformin 500mg BID", "Amlodipine 5mg OD"],
            vitals=vitals,
            primary_diagnosis="Community-Acquired Pneumonia (Severe)",
            differential_diagnoses=["Acute Exacerbation of COPD", "Pulmonary Embolism"],
            planned_diagnostics=["Chest X-Ray AP/Lat", "Sputum Culture", "Blood Cultures x2"],
            planned_medications=["IV Levofloxacin 750mg OD (Penicillin-allergic)", "IV Paracetamol 1g Q8H"],
            monitoring_instructions=["Continuous pulse oximetry", "Hourly NEWS2 scoring", "Notify RRT if NEWS2 >= 5"]
        )

        res = self.doc.generate_soap(data, language="en")
        self.assertEqual(res.document_type, "SOAP")
        self.assertEqual(res.language, "en")
        self.assertIn("S — Subjective", res.structured_sections)
        self.assertIn("O — Objective", res.structured_sections)
        self.assertIn("A — Assessment", res.structured_sections)
        self.assertIn("P — Plan", res.structured_sections)
        
        # Verify NEWS2 score was automatically calculated
        self.assertEqual(len(res.calculated_scores), 1)
        self.assertEqual(res.calculated_scores[0].calculator_id, "news2_score")
        self.assertGreaterEqual(res.calculated_scores[0].score, 7)  # High clinical risk
        self.assertIn("NEWS2 Score:", res.structured_sections["A — Assessment"])

    def test_soap_generation_arabic(self):
        data = ClinicalDocumentInput(
            patient_identifier="MRN-44910",
            age_years=54,
            biological_sex="female",
            chief_complaint="ألم حاد في الصدر يمتد إلى الذراع الأيسر مع تعرق بارد.",
            hpi="بدأ الألم فجأة منذ ساعتين أثناء الراحة، مع ضيق في التنفس وغثيان.",
            medical_history=["ارتفاع ضغط الدم", "قصور الشريان التاجي"],
            vitals=VitalsInput(
                respiration_rate_bpm=20,
                spo2_percent=96.0,
                systolic_bp_mmhg=150,
                diastolic_bp_mmhg=95,
                pulse_bpm=88,
                temperature_celsius=37.0
            ),
            primary_diagnosis="اشتباه متلازمة الشريان التاجي الحادة (ACS)",
            planned_diagnostics=["رسم قلب 12-lead فوري", "تحليل إنزيمات القلب (hs-cTnI)"],
            planned_medications=["أسبرين 300 مجم مضغ", "كلوبيدوجريل 300 مجم"]
        )

        res = self.doc.generate_soap(data, language="ar")
        self.assertEqual(res.language, "ar")
        self.assertIn("S — الجزء الذاتي (Subjective)", res.structured_sections)
        self.assertIn("O — الجزء الموضوعي (Objective)", res.structured_sections)
        self.assertIn("A — التقييم السريري (Assessment)", res.structured_sections)
        self.assertIn("P — الخطة العلاجية (Plan)", res.structured_sections)
        self.assertIn("متلازمة الشريان التاجي الحادة", res.formatted_markdown)

    def test_panic_value_detection(self):
        labs = [
            LabValue(test_name="Serum Potassium", value=6.8, unit="mmol/L"),
            LabValue(test_name="Hemoglobin", value=6.2, unit="g/dL"),
            LabValue(test_name="Platelets", value=15.0, unit="10^3/uL")
        ]
        alerts = PanicValueEngine.evaluate(labs)
        self.assertEqual(len(alerts), 3)

        potassium_alert = next(a for a in alerts if "potassium" in a.test_name.lower())
        self.assertEqual(potassium_alert.severity, "CRITICAL_HIGH")
        self.assertIn("Calcium Gluconate", potassium_alert.immediate_action_en)
        self.assertIn("كالسيوم جلوكونات", potassium_alert.immediate_action_ar)

        hgb_alert = next(a for a in alerts if "hemoglobin" in a.test_name.lower())
        self.assertEqual(hgb_alert.severity, "CRITICAL_LOW")
        self.assertIn("PRBCs", hgb_alert.immediate_action_en)

    def test_phi_deidentification_in_clinical_notes(self):
        # Patient notes containing an Egyptian 14-digit National ID and name
        data = ClinicalDocumentInput(
            patient_identifier="MRN-TEST-1",
            age_years=45,
            biological_sex="male",
            chief_complaint="Patient Name: Mohamed Mahmoud, National ID 29810151200123 presents with acute abdominal pain.",
            hpi="Patient phone is 01012345678, reported fever and vomiting."
        )

        res = self.doc.generate_soap(data, language="en")
        # Ensure raw national ID and phone are not present in the generated markdown
        self.assertNotIn("29810151200123", res.formatted_markdown)
        self.assertNotIn("01012345678", res.formatted_markdown)
        self.assertIn("[REDACTED_EGYPT_NID]", res.formatted_markdown)
        self.assertIn("[REDACTED_PHONE]", res.formatted_markdown)

    def test_soap_generation_with_ckd_epi_integration(self):
        data = ClinicalDocumentInput(
            patient_identifier="PT-RENAL-01",
            age_years=65,
            biological_sex="male",
            chief_complaint="Follow-up chronic kidney disease and hypertension.",
            hpi="Patient asymptomatic, routine lab review.",
            labs=[
                LabValue(test_name="Serum Creatinine", value=2.0, unit="mg/dL")
            ]
        )
        res = self.doc.generate_soap(data, language="en")
        self.assertEqual(len(res.calculated_scores), 1)
        self.assertEqual(res.calculated_scores[0].calculator_id, "ckd_epi_2021_egfr")
        self.assertIn("eGFR (CKD-EPI 2021):", res.structured_sections["A — Assessment"])

    def test_isbar_handover_generation(self):
        data = ClinicalDocumentInput(
            patient_identifier="BED-ICU-04",
            age_years=70,
            biological_sex="female",
            chief_complaint="Septic Shock",
            hpi="Admitted for urosepsis, refractory hypotension on vasopressors.",
            vitals=VitalsInput(
                respiration_rate_bpm=24,
                spo2_percent=94.0,
                air_or_oxygen="Oxygen",
                systolic_bp_mmhg=85,
                diastolic_bp_mmhg=50,
                pulse_bpm=120,
                temperature_celsius=38.9
            ),
            primary_diagnosis="Severe Sepsis secondary to Pyelonephritis"
        )

        res = self.doc.generate_isbar(
            data=data,
            situation="Patient experienced sudden drop in MAP < 65 mmHg despite 2L fluid resuscitation.",
            recommendation="Titrate Noradrenaline infusion, obtain stat arterial blood gas, and review by ICU fellow.",
            language="en"
        )

        self.assertEqual(res.document_type, "ISBAR")
        self.assertIn("I — Identification", res.structured_sections)
        self.assertIn("S — Situation", res.structured_sections)
        self.assertIn("B — Background", res.structured_sections)
        self.assertIn("A — Assessment", res.structured_sections)
        self.assertIn("R — Recommendation", res.structured_sections)
        self.assertIn("Rapid Response Team (RRT)", res.formatted_markdown)


if __name__ == "__main__":
    unittest.main()
