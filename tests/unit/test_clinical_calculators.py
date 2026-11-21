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
    calculate_meld_na_score,
    calculate_glasgow_blatchford_score,
    calculate_ascvd_risk_acc_aha,
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

    # ------------------------------------------------------------------
    # MELD-Na (OPTN/UNOS 2016)
    # ------------------------------------------------------------------
    def test_meld_na_normal_values(self):
        # All labs at their OPTN lower bounds: 9.57*ln(1) + 3.78*ln(1) + 11.2*ln(1) + 6.43 = 6.43 -> 6.4
        # Initial MELD 6.4 <= 11, so no sodium correction applies; floor bound of 6 applies.
        res = calculate_meld_na_score(
            serum_bilirubin_mg_dl=1.0,
            inr=1.0,
            serum_creatinine_mg_dl=1.0,
            serum_sodium_meq_l=140.0
        )
        self.assertEqual(res.score, 6.0)
        self.assertEqual(res.raw_inputs["initial_meld"], 6.4)
        self.assertIn("Low Risk", res.interpretation_band)
        self.assertTrue(any("Sodium correction is not applied" in w for w in res.warnings))

    def test_meld_na_sodium_effect_above_eleven(self):
        # Bili 2.0, INR 1.5, Cr 1.5:
        # 9.57*ln(1.5) + 3.78*ln(2.0) + 11.2*ln(1.5) + 6.43
        # = 3.879 + 2.620 + 4.541 + 6.43 = 17.47 -> initial MELD 17.5 (> 11, so Na applies)
        # Na 130 -> 137-130 = 7; MELD-Na = 17.5 + 1.32*7 - 0.033*17.5*7 = 17.5 + 9.24 - 4.0425 = 22.6975 -> 23
        res = calculate_meld_na_score(
            serum_bilirubin_mg_dl=2.0,
            inr=1.5,
            serum_creatinine_mg_dl=1.5,
            serum_sodium_meq_l=130.0
        )
        self.assertEqual(res.raw_inputs["initial_meld"], 17.5)
        self.assertEqual(res.score, 23.0)
        self.assertIn("High Risk", res.interpretation_band)

        # Same labs but normal sodium (140) clamps to 137 -> no correction, MELD-Na = MELD = 17.5 -> 18
        res_normal_na = calculate_meld_na_score(
            serum_bilirubin_mg_dl=2.0,
            inr=1.5,
            serum_creatinine_mg_dl=1.5,
            serum_sodium_meq_l=140.0
        )
        self.assertEqual(res_normal_na.score, 18.0)
        self.assertTrue(any("clamped to 137" in w for w in res_normal_na.warnings))
        self.assertGreater(res.score, res_normal_na.score)

    def test_meld_na_exact_eleven_boundary(self):
        # Cr 1.0, Bili 1.0, INR 1.5: 0 + 0 + 11.2*ln(1.5) + 6.43 = 4.541 + 6.43 = 10.971 -> 11.0
        # The sodium correction applies only when initial MELD is strictly > 11, so 11.0 must NOT trigger it.
        res = calculate_meld_na_score(
            serum_bilirubin_mg_dl=1.0,
            inr=1.5,
            serum_creatinine_mg_dl=1.0,
            serum_sodium_meq_l=120.0
        )
        self.assertEqual(res.raw_inputs["initial_meld"], 11.0)
        self.assertEqual(res.score, 11.0)
        self.assertTrue(any("initial MELD is <= 11" in w for w in res.warnings))

    def test_meld_na_dialysis_caps_creatinine(self):
        # Dialysis forces creatinine to 4.0 regardless of the reported value.
        # Cr 4.0: 9.57*ln(4) = 13.267; Bili 2.0: 2.620; INR 1.5: 4.541; + 6.43 = 26.858 -> 26.9
        # Na 135 -> 137-135 = 2; 26.9 + 2.64 - 0.033*26.9*2 = 26.9 + 2.64 - 1.7754 = 27.7646 -> 28
        res = calculate_meld_na_score(
            serum_bilirubin_mg_dl=2.0,
            inr=1.5,
            serum_creatinine_mg_dl=2.5,
            serum_sodium_meq_l=135.0,
            dialysis_within_7_days=True
        )
        self.assertEqual(res.raw_inputs["creatinine_used_mg_dl"], 4.0)
        self.assertEqual(res.raw_inputs["initial_meld"], 26.9)
        self.assertEqual(res.score, 28.0)
        self.assertTrue(any("Dialysis within the preceding 7 days" in w for w in res.warnings))

    def test_meld_na_upper_bound_and_bands(self):
        # Critically deranged labs must saturate the OPTN ceiling of 40 rather than exceeding it.
        res = calculate_meld_na_score(
            serum_bilirubin_mg_dl=10.0,
            inr=5.0,
            serum_creatinine_mg_dl=8.0,
            serum_sodium_meq_l=110.0,
            dialysis_within_7_days=True
        )
        self.assertEqual(res.score, 40.0)
        self.assertIn("Imminent Liver Failure", res.interpretation_band)

    def test_meld_na_refusals(self):
        # Non-positive bilirubin
        with self.assertRaises(SafeCalculationRefusal):
            calculate_meld_na_score(serum_bilirubin_mg_dl=0.0, inr=1.0, serum_creatinine_mg_dl=1.0, serum_sodium_meq_l=135.0)
        # Negative INR
        with self.assertRaises(SafeCalculationRefusal):
            calculate_meld_na_score(serum_bilirubin_mg_dl=1.5, inr=-1.2, serum_creatinine_mg_dl=1.0, serum_sodium_meq_l=135.0)
        # Negative creatinine
        with self.assertRaises(SafeCalculationRefusal):
            calculate_meld_na_score(serum_bilirubin_mg_dl=1.5, inr=1.2, serum_creatinine_mg_dl=-0.4, serum_sodium_meq_l=135.0)
        # Sodium below plausible range
        with self.assertRaises(SafeCalculationRefusal):
            calculate_meld_na_score(serum_bilirubin_mg_dl=1.5, inr=1.2, serum_creatinine_mg_dl=1.0, serum_sodium_meq_l=95.0)
        # Sodium above plausible range
        with self.assertRaises(SafeCalculationRefusal):
            calculate_meld_na_score(serum_bilirubin_mg_dl=1.5, inr=1.2, serum_creatinine_mg_dl=1.0, serum_sodium_meq_l=190.0)

    # ------------------------------------------------------------------
    # Glasgow-Blatchford Score
    # ------------------------------------------------------------------
    def test_glasgow_blatchford_zero_is_very_low_risk(self):
        # BUN 10 (< 18.2), Hgb 14.5 (no points), SBP 120, pulse 70, no history -> 0 points
        res = calculate_glasgow_blatchford_score(
            blood_urea_nitrogen_mg_dl=10.0,
            hemoglobin_g_dl=14.5,
            systolic_bp_mmhg=120,
            pulse_bpm=70
        )
        self.assertEqual(res.score, 0.0)
        self.assertIn("Very Low Risk", res.interpretation_band)
        self.assertIn("outpatient", res.clinical_recommendation)

    def test_glasgow_blatchford_hemoglobin_sex_thresholds(self):
        # Hgb 12.5: MALE scores +1 (12.0 - 13.0 band); FEMALE scores 0 (>= 12.0).
        male = calculate_glasgow_blatchford_score(
            blood_urea_nitrogen_mg_dl=10.0,
            hemoglobin_g_dl=12.5,
            systolic_bp_mmhg=120,
            pulse_bpm=70,
            biological_sex="MALE"
        )
        female = calculate_glasgow_blatchford_score(
            blood_urea_nitrogen_mg_dl=10.0,
            hemoglobin_g_dl=12.5,
            systolic_bp_mmhg=120,
            pulse_bpm=70,
            biological_sex="FEMALE"
        )
        self.assertEqual(male.score, 1.0)
        self.assertEqual(female.score, 0.0)
        self.assertIn("Low Risk", male.interpretation_band)

        # Hgb 11.0: MALE +3 (10.0 - 12.0), FEMALE +1 (10.0 - 12.0)
        male_low = calculate_glasgow_blatchford_score(
            blood_urea_nitrogen_mg_dl=10.0, hemoglobin_g_dl=11.0,
            systolic_bp_mmhg=120, pulse_bpm=70, biological_sex="MALE"
        )
        female_low = calculate_glasgow_blatchford_score(
            blood_urea_nitrogen_mg_dl=10.0, hemoglobin_g_dl=11.0,
            systolic_bp_mmhg=120, pulse_bpm=70, biological_sex="FEMALE"
        )
        self.assertEqual(male_low.score, 3.0)
        self.assertEqual(female_low.score, 1.0)

    def test_glasgow_blatchford_multi_risk_accumulation(self):
        # BUN 30.0 -> +4; Hgb 9.5 (FEMALE) -> +6; SBP 95 -> +2; pulse 105 -> +1;
        # melena +1, syncope +2, hepatic +2, cardiac +2 = 20
        res = calculate_glasgow_blatchford_score(
            blood_urea_nitrogen_mg_dl=30.0,
            hemoglobin_g_dl=9.5,
            systolic_bp_mmhg=95,
            pulse_bpm=105,
            hx_melena=True,
            hx_syncope=True,
            hx_hepatic_disease=True,
            hx_cardiac_failure=True,
            biological_sex="FEMALE"
        )
        self.assertEqual(res.score, 20.0)
        self.assertIn("High Risk", res.interpretation_band)
        self.assertIn("Inpatient admission", res.clinical_recommendation)

        # Maximum severity path: BUN >= 70 (+6), Hgb < 10 male (+6), SBP < 90 (+3),
        # pulse >= 100 (+1), all history flags (+7) = 23 (the documented ceiling)
        max_res = calculate_glasgow_blatchford_score(
            blood_urea_nitrogen_mg_dl=85.0,
            hemoglobin_g_dl=8.0,
            systolic_bp_mmhg=80,
            pulse_bpm=120,
            hx_melena=True,
            hx_syncope=True,
            hx_hepatic_disease=True,
            hx_cardiac_failure=True,
            biological_sex="MALE"
        )
        self.assertEqual(max_res.score, 23.0)

    def test_glasgow_blatchford_refusals(self):
        with self.assertRaises(SafeCalculationRefusal):
            calculate_glasgow_blatchford_score(
                blood_urea_nitrogen_mg_dl=0.0, hemoglobin_g_dl=13.0,
                systolic_bp_mmhg=120, pulse_bpm=70
            )
        with self.assertRaises(SafeCalculationRefusal):
            calculate_glasgow_blatchford_score(
                blood_urea_nitrogen_mg_dl=20.0, hemoglobin_g_dl=-1.0,
                systolic_bp_mmhg=120, pulse_bpm=70
            )
        with self.assertRaises(SafeCalculationRefusal):
            calculate_glasgow_blatchford_score(
                blood_urea_nitrogen_mg_dl=20.0, hemoglobin_g_dl=13.0,
                systolic_bp_mmhg=400, pulse_bpm=70
            )
        with self.assertRaises(SafeCalculationRefusal):
            calculate_glasgow_blatchford_score(
                blood_urea_nitrogen_mg_dl=20.0, hemoglobin_g_dl=13.0,
                systolic_bp_mmhg=120, pulse_bpm=70, biological_sex="UNKNOWN"
            )

    # ------------------------------------------------------------------
    # ACC/AHA Pooled Cohort Equations (10-year ASCVD)
    # ------------------------------------------------------------------
    def test_ascvd_low_risk(self):
        # 45-year-old White male, TC 180, HDL 60, SBP 120, untreated, non-smoker, no diabetes -> 1.2%
        res = calculate_ascvd_risk_acc_aha(
            age_years=45,
            biological_sex="MALE",
            race="WHITE",
            total_cholesterol_mg_dl=180.0,
            hdl_cholesterol_mg_dl=60.0,
            systolic_bp_mmhg=120,
            on_hypertension_meds=False,
            has_diabetes=False,
            is_current_smoker=False
        )
        self.assertAlmostEqual(res.score, 1.2, delta=0.1)
        self.assertIn("Low Risk", res.interpretation_band)

    def test_ascvd_intermediate_risk(self):
        # 55-year-old White male, TC 213, HDL 50, SBP 130 treated, diabetic, non-smoker -> 13.4%
        res = calculate_ascvd_risk_acc_aha(
            age_years=55,
            biological_sex="MALE",
            race="WHITE",
            total_cholesterol_mg_dl=213.0,
            hdl_cholesterol_mg_dl=50.0,
            systolic_bp_mmhg=130,
            on_hypertension_meds=True,
            has_diabetes=True,
            is_current_smoker=False
        )
        self.assertAlmostEqual(res.score, 13.4, delta=0.1)
        self.assertIn("Intermediate Risk", res.interpretation_band)
        self.assertIn("Moderate-intensity statin", res.clinical_recommendation)

    def test_ascvd_high_risk(self):
        # 65-year-old White male, TC 280, HDL 38, SBP 150 treated, smoker, diabetic -> 58.2%
        res = calculate_ascvd_risk_acc_aha(
            age_years=65,
            biological_sex="MALE",
            race="WHITE",
            total_cholesterol_mg_dl=280.0,
            hdl_cholesterol_mg_dl=38.0,
            systolic_bp_mmhg=150,
            on_hypertension_meds=True,
            has_diabetes=True,
            is_current_smoker=True
        )
        self.assertAlmostEqual(res.score, 58.2, delta=0.1)
        self.assertIn("High Risk", res.interpretation_band)
        self.assertIn("High-intensity statin", res.clinical_recommendation)

    def test_ascvd_race_and_sex_specific_coefficients(self):
        # African American male coefficients differ from White male for identical inputs.
        aa = calculate_ascvd_risk_acc_aha(
            age_years=60, biological_sex="MALE", race="AFRICAN_AMERICAN",
            total_cholesterol_mg_dl=220.0, hdl_cholesterol_mg_dl=45.0,
            systolic_bp_mmhg=140, on_hypertension_meds=True,
            has_diabetes=False, is_current_smoker=True
        )
        white = calculate_ascvd_risk_acc_aha(
            age_years=60, biological_sex="MALE", race="WHITE",
            total_cholesterol_mg_dl=220.0, hdl_cholesterol_mg_dl=45.0,
            systolic_bp_mmhg=140, on_hypertension_meds=True,
            has_diabetes=False, is_current_smoker=True
        )
        self.assertAlmostEqual(aa.score, 26.9, delta=0.1)
        self.assertNotEqual(aa.score, white.score)

        # 'OTHER' maps to the White coefficient set per AHA guidance.
        other = calculate_ascvd_risk_acc_aha(
            age_years=55, biological_sex="MALE", race="OTHER",
            total_cholesterol_mg_dl=213.0, hdl_cholesterol_mg_dl=50.0,
            systolic_bp_mmhg=130, on_hypertension_meds=True,
            has_diabetes=True, is_current_smoker=False
        )
        self.assertEqual(other.score, 13.4)
        self.assertTrue(any("'OTHER' was mapped to the White" in w for w in other.warnings))

    def test_ascvd_refuses_age_outside_validated_range(self):
        with self.assertRaises(SafeCalculationRefusal):
            calculate_ascvd_risk_acc_aha(
                age_years=39, biological_sex="MALE", race="WHITE",
                total_cholesterol_mg_dl=200.0, hdl_cholesterol_mg_dl=50.0,
                systolic_bp_mmhg=120, on_hypertension_meds=False,
                has_diabetes=False, is_current_smoker=False
            )
        with self.assertRaises(SafeCalculationRefusal):
            calculate_ascvd_risk_acc_aha(
                age_years=80, biological_sex="FEMALE", race="WHITE",
                total_cholesterol_mg_dl=200.0, hdl_cholesterol_mg_dl=50.0,
                systolic_bp_mmhg=120, on_hypertension_meds=False,
                has_diabetes=False, is_current_smoker=False
            )

    def test_ascvd_refuses_out_of_range_labs(self):
        with self.assertRaises(SafeCalculationRefusal):
            calculate_ascvd_risk_acc_aha(
                age_years=55, biological_sex="MALE", race="WHITE",
                total_cholesterol_mg_dl=100.0, hdl_cholesterol_mg_dl=50.0,
                systolic_bp_mmhg=130, on_hypertension_meds=False,
                has_diabetes=False, is_current_smoker=False
            )
        with self.assertRaises(SafeCalculationRefusal):
            calculate_ascvd_risk_acc_aha(
                age_years=55, biological_sex="MALE", race="WHITE",
                total_cholesterol_mg_dl=200.0, hdl_cholesterol_mg_dl=10.0,
                systolic_bp_mmhg=130, on_hypertension_meds=False,
                has_diabetes=False, is_current_smoker=False
            )
        with self.assertRaises(SafeCalculationRefusal):
            calculate_ascvd_risk_acc_aha(
                age_years=55, biological_sex="MALE", race="WHITE",
                total_cholesterol_mg_dl=200.0, hdl_cholesterol_mg_dl=50.0,
                systolic_bp_mmhg=220, on_hypertension_meds=False,
                has_diabetes=False, is_current_smoker=False
            )
        with self.assertRaises(SafeCalculationRefusal):
            calculate_ascvd_risk_acc_aha(
                age_years=55, biological_sex="MALE", race="ASIAN",
                total_cholesterol_mg_dl=200.0, hdl_cholesterol_mg_dl=50.0,
                systolic_bp_mmhg=130, on_hypertension_meds=False,
                has_diabetes=False, is_current_smoker=False
            )


if __name__ == "__main__":
    unittest.main()

