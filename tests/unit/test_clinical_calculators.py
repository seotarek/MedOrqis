"""
Unit tests for deterministic clinical calculators in core/clinical_calculators.py.
Verifies numerical precision, guideline versioning differences, and boundary refusals.
"""

import unittest
from core.clinical_calculators import (
    calculate_cha2ds2_va_esc2024,
    calculate_cha2ds2_vasc_aha2023,
    calculate_ckd_epi_2021_egfr,
    calculate_cockcroft_gault_crcl,
    calculate_pediatric_weight_dose,
    calculate_mosteller_bsa,
    calculate_curb65_score,
    calculate_wells_dvt_score,
    calculate_wells_pe_score,
    calculate_bedside_schwartz_egfr,
    calculate_has_bled_score,
    calculate_news2_score,
    SafeCalculationRefusal
)



class TestClinicalCalculators(unittest.TestCase):

    def test_cha2ds2_esc_vs_aha_sex_difference(self):
        # Case 1: 70-year old female with hypertension and diabetes
        # Under ESC 2024: Age 65-74 (+1), HTN (+1), DM (+1) = 3 points (Sex is not included)
        res_esc = calculate_cha2ds2_va_esc2024(
            age_years=70,
            hx_heart_failure=False,
            hx_hypertension=True,
            hx_diabetes=True,
            hx_stroke_tia_thromboembolism=False,
            hx_vascular_disease=False
        )
        self.assertEqual(res_esc.score, 3.0)

        # Under AHA 2023: Same female gets +1 for female sex = 4 points
        res_aha = calculate_cha2ds2_vasc_aha2023(
            age_years=70,
            biological_sex="FEMALE",
            hx_heart_failure=False,
            hx_hypertension=True,
            hx_diabetes=True,
            hx_stroke_tia_thromboembolism=False,
            hx_vascular_disease=False
        )
        self.assertEqual(res_aha.score, 4.0)

        # Under ESC 2024: A 70yo MALE with same conditions has identical score (3.0)
        res_esc_male = calculate_cha2ds2_va_esc2024(
            age_years=70,
            hx_heart_failure=False,
            hx_hypertension=True,
            hx_diabetes=True,
            hx_stroke_tia_thromboembolism=False,
            hx_vascular_disease=False
        )
        self.assertEqual(res_esc_male.score, 3.0)

    def test_cha2ds2_pediatric_refusal(self):
        with self.assertRaises(SafeCalculationRefusal):
            calculate_cha2ds2_va_esc2024(
                age_years=15,
                hx_heart_failure=False,
                hx_hypertension=False,
                hx_diabetes=False,
                hx_stroke_tia_thromboembolism=False,
                hx_vascular_disease=False
            )

    def test_ckd_epi_2021_egfr_precision_and_stages(self):
        # 60-year old female, serum creatinine 1.0 mg/dL
        # Inker 2021: kappa=0.7, alpha=-0.241, mult=1.012
        # Scr/kappa = 1.0/0.7 = 1.42857 > 1 -> (1.42857)^(-1.200) = 0.6521
        # 142 * 0.6521 * (0.9938^60) * 1.012 = 142 * 0.6521 * 0.6883 * 1.012 ~ 64.5 mL/min/1.73m2
        res = calculate_ckd_epi_2021_egfr(
            serum_creatinine=1.0,
            age_years=60,
            biological_sex="FEMALE",
            unit="mg/dL"
        )
        self.assertAlmostEqual(res.score, 64.5, delta=0.5)
        self.assertIn("KDIGO Stage G2", res.interpretation_band)

        # Test unit conversion from umol/L (88.42 umol/L = 1.0 mg/dL)
        res_umol = calculate_ckd_epi_2021_egfr(
            serum_creatinine=88.42,
            age_years=60,
            biological_sex="FEMALE",
            unit="umol/L"
        )
        self.assertAlmostEqual(res_umol.score, res.score, places=1)

    def test_ckd_epi_refuses_pediatric_and_invalid_unit(self):
        # Age < 18 refusal
        with self.assertRaises(SafeCalculationRefusal):
            calculate_ckd_epi_2021_egfr(serum_creatinine=1.0, age_years=14, biological_sex="MALE")

        # Invalid unit refusal
        with self.assertRaises(SafeCalculationRefusal):
            calculate_ckd_epi_2021_egfr(serum_creatinine=1.0, age_years=45, biological_sex="MALE", unit="stone")

    def test_cockcroft_gault_crcl_obesity_adjustment(self):
        # 55-year old male, height 170 cm (67 in, 7 in over 5ft), actual weight 110 kg (obese)
        # IBW = 50 + 2.3 * 7 = 66.1 kg
        # Actual (110 kg) > 1.2 * IBW (79.3 kg) -> AdjBW = 66.1 + 0.4*(110 - 66.1) = 83.66 kg
        # CrCl with Scr 1.2 mg/dL: ((140-55)*83.66)/(72*1.2) = 7111.1 / 86.4 ~ 82.3 mL/min
        res = calculate_cockcroft_gault_crcl(
            serum_creatinine_mg_dl=1.2,
            age_years=55,
            actual_weight_kg=110.0,
            biological_sex="MALE",
            height_cm=170.0
        )
        self.assertAlmostEqual(res.score, 82.3, delta=1.0)
        self.assertTrue(any("Adjusted Body Weight" in w for w in res.warnings))

    def test_pediatric_dose_hard_cap(self):
        # 12-year old child, weight 60 kg, dose 10 mg/kg -> calculated uncapped = 600 mg
        # Max adult single dose is 500 mg (e.g. Paracetamol single cap)
        res = calculate_pediatric_weight_dose(
            age_years=12.0,
            weight_kg=60.0,
            dose_per_kg=10.0,
            max_single_adult_dose_mg=500.0,
            dose_unit="mg"
        )
        # Dose must be strictly capped at 500.0 mg
        self.assertEqual(res.score, 500.0)
        self.assertTrue(any("DOSE CAPPED" in w for w in res.warnings))

    def test_curb65_normalization(self):
        # 70-year old with Urea 8.0 mmol/L (> 7.0) and RR 32 (>=30) -> Score = 3 (Age, Urea, RR)
        res = calculate_curb65_score(
            confusion=False,
            urea_mmol_l=8.0,
            respiratory_rate_bpm=32,
            systolic_bp_mmhg=120,
            diastolic_bp_mmhg=80,
            age_years=70
        )
        self.assertEqual(res.score, 3.0)
        self.assertIn("High Risk", res.interpretation_band)

    def test_wells_dvt_and_pe(self):
        # Wells DVT: Active cancer (+1), calf swelling > 3cm (+1), alt dx more likely (-2) = 0 (Low)
        res_dvt = calculate_wells_dvt_score(
            active_cancer=True,
            paralysis_or_plaster_cast=False,
            bedridden_gt_3days_or_major_surgery=False,
            localized_tenderness_deep_veins=False,
            entire_leg_swollen=False,
            calf_swelling_gt_3cm_diff=True,
            pitting_edema_symptomatic_leg=False,
            collateral_superficial_veins=False,
            previous_documented_dvt=False,
            alternative_diagnosis_more_likely=True
        )
        self.assertEqual(res_dvt.score, 0.0)
        self.assertIn("DVT Unlikely", res_dvt.interpretation_band)

        # Wells PE: Signs of DVT (+3), PE most likely (+3), HR > 100 (+1.5) = 7.5 (High / PE Likely)
        res_pe = calculate_wells_pe_score(
            clinical_signs_symptoms_dvt=True,
            pe_most_likely_or_equal_to_alt=True,
            heart_rate_gt_100=True,
            immobilization_or_surgery_past_4wks=False,
            previous_pe_or_dvt=False,
            hemoptysis=False,
            active_malignancy=False
        )
        self.assertEqual(res_pe.score, 7.5)
        self.assertIn("PE Likely", res_pe.interpretation_band)

    def test_bedside_schwartz_egfr(self):
        # 8-year old, height 120 cm, creatinine 0.6 mg/dL -> 0.413 * 120 / 0.6 = 82.6 mL/min/1.73m2
        res = calculate_bedside_schwartz_egfr(height_cm=120.0, serum_creatinine_mg_dl=0.6, age_years=8.0)
        self.assertAlmostEqual(res.score, 82.6, places=1)
        self.assertIn("Mildly Decreased", res.interpretation_band)

        # Refuse adult (age >= 18)
        with self.assertRaises(SafeCalculationRefusal):
            calculate_bedside_schwartz_egfr(height_cm=170.0, serum_creatinine_mg_dl=1.0, age_years=18.0)

        # Refuse non-positive values
        with self.assertRaises(SafeCalculationRefusal):
            calculate_bedside_schwartz_egfr(height_cm=-10.0, serum_creatinine_mg_dl=0.6, age_years=5.0)

    def test_has_bled_score(self):
        # Uncontrolled HTN (1), Abnormal renal (1), Stroke (1), Bleed history (1), Labile INR (1) = 5
        res = calculate_has_bled_score(
            hypertension_uncontrolled=True,
            abnormal_renal_function=True,
            abnormal_liver_function=False,
            prior_stroke=True,
            bleeding_history_or_predisposition=True,
            labile_inr=True,
            elderly_age_gt_65=False,
            drugs_antiplatelet_or_nsaid=False,
            alcohol_excess=False,
            age_years=60.0
        )
        self.assertEqual(res.score, 5.0)
        self.assertIn("High Bleeding Risk", res.interpretation_band)

        # Pediatric refusal
        with self.assertRaises(SafeCalculationRefusal):
            calculate_has_bled_score(
                hypertension_uncontrolled=False,
                abnormal_renal_function=False,
                abnormal_liver_function=False,
                prior_stroke=False,
                bleeding_history_or_predisposition=False,
                labile_inr=False,
                age_years=14.0
            )

    def test_news2_score(self):
        # Severe deterioration: RR 28 (+3), SpO2 91% (+3), on oxygen (+2), SBP 85 (+3), Pulse 135 (+3), Alert (0), Temp 35.0 (+3) = 17
        res = calculate_news2_score(
            respiration_rate_bpm=28,
            spo2_percent=91.0,
            air_or_oxygen="OXYGEN",
            systolic_bp_mmhg=85,
            pulse_bpm=135,
            consciousness="ALERT",
            temperature_celsius=35.0,
            age_years=68.0
        )
        self.assertGreaterEqual(res.score, 14.0)
        self.assertIn("High Clinical Risk", res.interpretation_band)

        # Pediatric refusal (age < 16)
        with self.assertRaises(SafeCalculationRefusal):
            calculate_news2_score(
                respiration_rate_bpm=20,
                spo2_percent=98.0,
                air_or_oxygen="AIR",
                systolic_bp_mmhg=110,
                pulse_bpm=75,
                consciousness="ALERT",
                temperature_celsius=36.8,
                age_years=12.0
            )


    def test_curb65_boundary_refusals(self):
        # Pediatric refusal
        with self.assertRaises(SafeCalculationRefusal):
            calculate_curb65_score(
                confusion=False,
                urea_mmol_l=5.0,
                respiratory_rate_bpm=20,
                systolic_bp_mmhg=110,
                diastolic_bp_mmhg=70,
                age_years=15
            )

        # Non-physiological RR (> 100)
        with self.assertRaises(SafeCalculationRefusal):
            calculate_curb65_score(
                confusion=False,
                urea_mmol_l=5.0,
                respiratory_rate_bpm=120,
                systolic_bp_mmhg=110,
                diastolic_bp_mmhg=70,
                age_years=50
            )

        # Non-physiological SBP (<= 20)
        with self.assertRaises(SafeCalculationRefusal):
            calculate_curb65_score(
                confusion=False,
                urea_mmol_l=5.0,
                respiratory_rate_bpm=20,
                systolic_bp_mmhg=15,
                diastolic_bp_mmhg=10,
                age_years=50
            )


if __name__ == "__main__":
    unittest.main()

