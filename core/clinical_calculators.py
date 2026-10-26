"""
MedOrqis — Deterministic Clinical Calculators Module
Evidence-Grounded, Version-Attributed, Pure Deterministic Functions.
"""

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import math
from typing import Optional, List, Dict, Any


class SafeCalculationRefusal(ValueError):
    """Raised when calculation cannot safely proceed due to out-of-bounds or missing data."""
    def __init__(self, reason: str, missing_or_invalid_parameter: str, recommendation: str):
        super().__init__(f"Calculation Refused: {reason} (Param: {missing_or_invalid_parameter}). {recommendation}")
        self.reason = reason
        self.parameter = missing_or_invalid_parameter
        self.recommendation = recommendation


@dataclass(frozen=True)
class CalculationResult:
    calculator_id: str
    calculator_name: str
    score: float
    unit: str
    interpretation_band: str
    clinical_recommendation: str
    guideline_citation: str
    guideline_year: int
    applicable_population: str
    raw_inputs: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)


def calculate_cha2ds2_va_esc2024(
    age_years: int,
    hx_heart_failure: bool,
    hx_hypertension: bool,
    hx_diabetes: bool,
    hx_stroke_tia_thromboembolism: bool,
    hx_vascular_disease: bool
) -> CalculationResult:
    """
    CHA2DS2-VA Score according to 2024 ESC Guidelines for the management of Atrial Fibrillation.
    Guideline: Van Gelder IC, et al. Eur Heart J 2024 (DOI: 10.1093/eurheartj/ehae176).
    NOTE: Biological sex category is REMOVED in the 2024 ESC update (score range 0-8).
    """
    if age_years < 18:
        raise SafeCalculationRefusal(
            reason="CHA2DS2-VA is validated only for adult patients with atrial fibrillation.",
            missing_or_invalid_parameter="age_years",
            recommendation="Refer to pediatric cardiology guidelines for pediatric arrhythmias."
        )

    score = 0
    if hx_heart_failure:
        score += 1
    if hx_hypertension:
        score += 1
    if age_years >= 75:
        score += 2
    elif age_years >= 65:
        score += 1
    if hx_diabetes:
        score += 1
    if hx_stroke_tia_thromboembolism:
        score += 2
    if hx_vascular_disease:
        score += 1

    if score == 0:
        band = "Low Risk (0 points)"
        rec = "Oral anticoagulation (OAC) is generally NOT recommended. Re-evaluate periodically."
    elif score == 1:
        band = "Intermediate Risk (1 point)"
        rec = "Oral anticoagulation SHOULD BE CONSIDERED (Class IIa). Weigh bleeding risk and patient preference."
    else:
        band = f"High Risk ({score} points)"
        rec = "Oral anticoagulation IS RECOMMENDED (Class I), preferably DOAC over VKA unless mechanical valve or moderate-severe mitral stenosis. Assess HAS-BLED bleeding risk."

    warnings = [
        "2024 ESC Guideline update removes female sex modifier from score.",
        "Must verify renal function (eGFR/CrCl) before selecting DOAC agent and dosing.",
        "Check for active pathological bleeding and contraindications."
    ]

    return CalculationResult(
        calculator_id="cha2ds2_va_esc2024",
        calculator_name="CHA2DS2-VA Stroke Risk in Atrial Fibrillation (ESC 2024)",
        score=float(score),
        unit="points",
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Van Gelder IC, et al. 2024 ESC Guidelines for the management of atrial fibrillation. Eur Heart J 2024;45(39):4177–4254.",
        guideline_year=2024,
        applicable_population="Adults (>=18y) with documented non-valvular atrial fibrillation",
        raw_inputs={
            "age_years": age_years,
            "hx_heart_failure": hx_heart_failure,
            "hx_hypertension": hx_hypertension,
            "hx_diabetes": hx_diabetes,
            "hx_stroke_tia_thromboembolism": hx_stroke_tia_thromboembolism,
            "hx_vascular_disease": hx_vascular_disease
        },
        warnings=warnings
    )


def calculate_cha2ds2_vasc_aha2023(
    age_years: int,
    biological_sex: str,
    hx_heart_failure: bool,
    hx_hypertension: bool,
    hx_diabetes: bool,
    hx_stroke_tia_thromboembolism: bool,
    hx_vascular_disease: bool
) -> CalculationResult:
    """
    CHA2DS2-VASc Score according to 2023 ACC/AHA/ACCP/HRS Guideline.
    Guideline: Joglar JA, et al. Circulation 2024;149:e1-e156.
    Biological sex: Female adds 1 point (range 0-9).
    """
    if age_years < 18:
        raise SafeCalculationRefusal(
            reason="CHA2DS2-VASc is validated only for adult patients with atrial fibrillation.",
            missing_or_invalid_parameter="age_years",
            recommendation="Refer to pediatric cardiology guidelines."
        )

    sex_upper = biological_sex.upper().strip()
    if sex_upper not in ["MALE", "FEMALE", "M", "F"]:
        raise SafeCalculationRefusal(
            reason="Biological sex is required for AHA/ACC CHA2DS2-VASc calculation.",
            missing_or_invalid_parameter="biological_sex",
            recommendation="Specify 'MALE' or 'FEMALE', or use cha2ds2_va_esc2024 (which is sex-neutral)."
        )

    is_female = sex_upper in ["FEMALE", "F"]

    score = 0
    if hx_heart_failure:
        score += 1
    if hx_hypertension:
        score += 1
    if age_years >= 75:
        score += 2
    elif age_years >= 65:
        score += 1
    if hx_diabetes:
        score += 1
    if hx_stroke_tia_thromboembolism:
        score += 2
    if hx_vascular_disease:
        score += 1
    if is_female:
        score += 1

    # AHA thresholds: Men (low: 0, int: 1, high: >=2); Women (low: 1, int: 2, high: >=3)
    non_sex_score = score - (1 if is_female else 0)
    if non_sex_score == 0:
        band = f"Low Thromboembolic Risk ({score} pts)"
        rec = "Oral anticoagulation is NOT recommended."
    elif non_sex_score == 1:
        band = f"Intermediate Thromboembolic Risk ({score} pts)"
        rec = "Oral anticoagulation may be considered based on shared decision-making."
    else:
        band = f"High Thromboembolic Risk ({score} pts)"
        rec = "Oral anticoagulation is recommended (DOAC preferred over Warfarin). Assess bleeding risk."

    return CalculationResult(
        calculator_id="cha2ds2_vasc_aha2023",
        calculator_name="CHA2DS2-VASc Stroke Risk in Atrial Fibrillation (ACC/AHA 2023)",
        score=float(score),
        unit="points",
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Joglar JA, et al. 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation. Circulation 2024;149:e1-e156.",
        guideline_year=2023,
        applicable_population="Adults (>=18y) with atrial fibrillation",
        raw_inputs={
            "age_years": age_years,
            "biological_sex": sex_upper,
            "hx_heart_failure": hx_heart_failure,
            "hx_hypertension": hx_hypertension,
            "hx_diabetes": hx_diabetes,
            "hx_stroke_tia_thromboembolism": hx_stroke_tia_thromboembolism,
            "hx_vascular_disease": hx_vascular_disease
        },
        warnings=["Female sex alone in the absence of other risk factors does not confer increased stroke risk."]
    )


def calculate_ckd_epi_2021_egfr(
    serum_creatinine: float,
    age_years: int,
    biological_sex: str,
    unit: str = "mg/dL"
) -> CalculationResult:
    """
    2021 CKD-EPI Creatinine Equation (Race-Free).
    Guideline: Inker LA, Eneanya ND, et al. N Engl J Med 2021;385:1737-1749.
    Output: mL/min/1.73 m2.
    """
    if age_years < 18:
        raise SafeCalculationRefusal(
            reason="CKD-EPI 2021 equation is strictly validated for adults >= 18 years.",
            missing_or_invalid_parameter="age_years",
            recommendation="For patients < 18 years, use the Bedside Schwartz equation."
        )

    unit_norm = unit.strip().lower()
    if unit_norm in ["mg/dl", "mg_dl", "mg%"]:
        scr = float(serum_creatinine)
    elif unit_norm in ["umol/l", "µmol/l", "micromol/l"]:
        # 1 mg/dL = 88.42 umol/L
        scr = float(serum_creatinine) / 88.42
    else:
        raise SafeCalculationRefusal(
            reason=f"Unrecognized serum creatinine unit: '{unit}'.",
            missing_or_invalid_parameter="unit",
            recommendation="Specify unit as 'mg/dL' or 'umol/L'."
        )

    if scr < 0.1 or scr > 35.0:
        raise SafeCalculationRefusal(
            reason=f"Serum creatinine value {scr:.2f} mg/dL is outside physiologically plausible range (0.1 - 35.0).",
            missing_or_invalid_parameter="serum_creatinine",
            recommendation="Verify lab measurement and unit calibration."
        )

    sex_upper = biological_sex.upper().strip()
    if sex_upper in ["FEMALE", "F"]:
        kappa = 0.7
        alpha = -0.241
        sex_multiplier = 1.012
    elif sex_upper in ["MALE", "M"]:
        kappa = 0.9
        alpha = -0.302
        sex_multiplier = 1.000
    else:
        raise SafeCalculationRefusal(
            reason="Biological sex is required for CKD-EPI 2021 calculation.",
            missing_or_invalid_parameter="biological_sex",
            recommendation="Specify 'MALE' or 'FEMALE'."
        )

    ratio = scr / kappa
    egfr = 142.0 * (min(ratio, 1.0) ** alpha) * (max(ratio, 1.0) ** -1.200) * (0.9938 ** age_years) * sex_multiplier
    egfr_val = round(egfr, 1)

    if egfr_val >= 90.0:
        band = "KDIGO Stage G1: Normal or high kidney function"
        rec = "eGFR >= 90 mL/min/1.73m2. If proteinuria or kidney damage markers present, manage underlying disease."
    elif egfr_val >= 60.0:
        band = "KDIGO Stage G2: Mildly decreased kidney function"
        rec = "eGFR 60-89 mL/min/1.73m2. Monitor renal function annually; adjust renally cleared drugs if needed."
    elif egfr_val >= 45.0:
        band = "KDIGO Stage G3a: Mildly to moderately decreased"
        rec = "eGFR 45-59 mL/min/1.73m2. Check urinary albumin-to-creatinine ratio (uACR); evaluate nephrotoxic drugs."
    elif egfr_val >= 30.0:
        band = "KDIGO Stage G3b: Moderately to severely decreased"
        rec = "eGFR 30-44 mL/min/1.73m2. Mandatory renal drug dose adjustments; consider nephrology referral."
    elif egfr_val >= 15.0:
        band = "KDIGO Stage G4: Severely decreased kidney function"
        rec = "eGFR 15-29 mL/min/1.73m2. Nephrology consultation recommended; prepare for kidney replacement therapy."
    else:
        band = "KDIGO Stage G5: Kidney Failure"
        rec = "eGFR < 15 mL/min/1.73m2. Immediate nephrology evaluation and kidney replacement therapy management."

    return CalculationResult(
        calculator_id="ckd_epi_2021_egfr",
        calculator_name="CKD-EPI 2021 Race-Free eGFR",
        score=egfr_val,
        unit="mL/min/1.73m2",
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Inker LA, Eneanya ND, et al. New Creatinine- and Cystatin C–Based Equations to Estimate GFR without Race. N Engl J Med 2021;385:1737-1749.",
        guideline_year=2021,
        applicable_population="Adults (>=18y) without acute kidney injury or unstable creatinine",
        raw_inputs={
            "serum_creatinine_input": serum_creatinine,
            "unit_input": unit,
            "serum_creatinine_mg_dl": round(scr, 3),
            "age_years": age_years,
            "biological_sex": sex_upper
        },
        warnings=[
            "Equation assumes stable serum creatinine; unreliable in acute kidney injury (AKI).",
            "Not standardized for extreme muscle mass (amputees, bodybuilders) or vegetarian diets."
        ]
    )


def calculate_cockcroft_gault_crcl(
    serum_creatinine_mg_dl: float,
    age_years: int,
    actual_weight_kg: float,
    biological_sex: str,
    height_cm: Optional[float] = None
) -> CalculationResult:
    """
    Cockcroft-Gault Creatinine Clearance (CrCl) Equation (1976).
    Standard metric used in FDA drug package inserts for renal dose adjustments.
    Includes Ideal Body Weight (IBW) and Adjusted Body Weight (AdjBW) in obesity.
    """
    if age_years < 18:
        raise SafeCalculationRefusal(
            reason="Cockcroft-Gault is validated only for adults >= 18 years.",
            missing_or_invalid_parameter="age_years",
            recommendation="Use pediatric Schwartz equation for pediatric renal estimation."
        )
    if serum_creatinine_mg_dl <= 0:
        raise SafeCalculationRefusal(
            reason="Serum creatinine must be positive.",
            missing_or_invalid_parameter="serum_creatinine_mg_dl",
            recommendation="Enter valid serum creatinine."
        )

    sex_upper = biological_sex.upper().strip()
    is_female = sex_upper in ["FEMALE", "F"]

    # Calculate IBW if height is provided
    weight_used = actual_weight_kg
    warnings = []
    if height_cm and height_cm > 100:
        height_inches = height_cm / 2.54
        inches_over_5ft = max(0.0, height_inches - 60.0)
        ibw = (45.5 if is_female else 50.0) + (2.3 * inches_over_5ft)

        # Check for obesity: Actual weight > 120% of IBW
        if actual_weight_kg > (1.2 * ibw):
            adj_bw = ibw + 0.4 * (actual_weight_kg - ibw)
            weight_used = adj_bw
            warnings.append(f"Patient actual weight exceeds 120% of IBW. Using Adjusted Body Weight (AdjBW: {adj_bw:.1f} kg) to avoid overestimating clearance in obesity.")
        elif actual_weight_kg < ibw:
            weight_used = actual_weight_kg
            warnings.append("Patient actual weight is less than IBW. Actual body weight used.")

    crcl = ((140 - age_years) * weight_used) / (72.0 * serum_creatinine_mg_dl)
    if is_female:
        crcl *= 0.85

    crcl_val = round(crcl, 1)

    if crcl_val >= 90:
        band = "Normal Renal Clearance (>= 90 mL/min)"
        rec = "Standard drug dosing usually appropriate unless drug package insert specifies otherwise."
    elif crcl_val >= 60:
        band = "Mild Renal Impairment (60-89 mL/min)"
        rec = "Check package insert for dose adjustments (e.g. some cephalosporins, metformin)."
    elif crcl_val >= 30:
        band = "Moderate Renal Impairment (30-59 mL/min)"
        rec = "Mandatory dose adjustments required for renally excreted medications (DOACs, SGLT2i, enoxaparin)."
    elif crcl_val >= 15:
        band = "Severe Renal Impairment (15-29 mL/min)"
        rec = "Significant dose reductions or drug contraindications apply. Nephrology consultation recommended."
    else:
        band = "End-Stage Renal Impairment (< 15 mL/min)"
        rec = "Extreme dose adjustment or dialysis dosing rules apply. Avoid nephrotoxic agents."

    return CalculationResult(
        calculator_id="cockcroft_gault_crcl",
        calculator_name="Cockcroft-Gault Creatinine Clearance (CrCl)",
        score=crcl_val,
        unit="mL/min",
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Cockcroft DW, Gault MH. Prediction of creatinine clearance from serum creatinine. Nephron 1976;16(1):31-41.",
        guideline_year=1976,
        applicable_population="Adults (>=18y) for FDA-labeled medication dose adjustments",
        raw_inputs={
            "serum_creatinine_mg_dl": serum_creatinine_mg_dl,
            "age_years": age_years,
            "actual_weight_kg": actual_weight_kg,
            "biological_sex": sex_upper,
            "height_cm": height_cm,
            "weight_used_kg": round(weight_used, 1)
        },
        warnings=warnings
    )


def calculate_pediatric_weight_dose(
    age_years: float,
    weight_kg: float,
    dose_per_kg: float,
    max_single_adult_dose_mg: float,
    dose_unit: str = "mg"
) -> CalculationResult:
    """
    Pediatric Weight-Based Dose Calculator with Physiological Plausibility Checks & Hard Capping.
    Enforces maximum adult single dose capping (Zero Overdose Policy).
    """
    if age_years < 0 or age_years > 18:
        raise SafeCalculationRefusal(
            reason="Pediatric dose calculator applies only to ages 0 to 18 years.",
            missing_or_invalid_parameter="age_years",
            recommendation="For patients > 18 years, use standard adult dosing protocols."
        )

    if weight_kg <= 0.3 or weight_kg > 150:
        raise SafeCalculationRefusal(
            reason=f"Weight {weight_kg} kg is outside plausible pediatric range.",
            missing_or_invalid_parameter="weight_kg",
            recommendation="Confirm scale measurement and unit (kg vs lbs)."
        )

    # Check for likely lb vs kg entry error
    # Rough median weights: 1y ~ 10kg, 5y ~ 18kg, 10y ~ 32kg
    warnings = []
    if age_years >= 1.0:
        expected_min = max(3.0, (age_years * 1.5))
        expected_max = min(120.0, (age_years * 6.5) + 15)
        if weight_kg > expected_max:
            warnings.append(
                f"POTENTIAL UNIT ERROR: Weight {weight_kg} kg is unusually high for age {age_years:.1f}y. "
                f"Verify patient was not weighed in pounds (lbs) (e.g., {weight_kg} lbs = {weight_kg*0.453592:.1f} kg)."
            )

    uncapped_dose = weight_kg * dose_per_kg
    capped = False
    final_dose = uncapped_dose

    if uncapped_dose > max_single_adult_dose_mg:
        final_dose = max_single_adult_dose_mg
        capped = True
        warnings.append(
            f"DOSE CAPPED: Uncapped weight-based calculation ({uncapped_dose:.2f} {dose_unit}) "
            f"exceeded maximum adult single dose ({max_single_adult_dose_mg} {dose_unit}). "
            f"Final dose capped at {max_single_adult_dose_mg} {dose_unit} to prevent pediatric overdose."
        )

    band = f"Calculated Single Dose: {final_dose:.2f} {dose_unit}" + (" (CAPPED AT ADULT MAX)" if capped else "")
    rec = f"Administer {final_dose:.2f} {dose_unit}. Verify frequency, route, renal/hepatic adjustments, and liquid concentration."

    return CalculationResult(
        calculator_id="pediatric_dose_calculator",
        calculator_name="Pediatric Weight-Based Dose with Maximum Dose Capping",
        score=round(final_dose, 2),
        unit=dose_unit,
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Nelson Textbook of Pediatrics / AAP Pediatric Formulary Guidelines (2024).",
        guideline_year=2024,
        applicable_population="Pediatric patients (0-18y)",
        raw_inputs={
            "age_years": age_years,
            "weight_kg": weight_kg,
            "dose_per_kg": dose_per_kg,
            "max_single_adult_dose_mg": max_single_adult_dose_mg,
            "uncapped_calculated_dose": round(uncapped_dose, 2)
        },
        warnings=warnings
    )


def calculate_mosteller_bsa(height_cm: float, weight_kg: float) -> CalculationResult:
    """
    Mosteller formula for Body Surface Area (BSA): sqrt((height * weight) / 3600).
    Output: m2.
    """
    if height_cm <= 20 or height_cm > 260:
        raise SafeCalculationRefusal(
            reason=f"Height {height_cm} cm is outside human physiological range.",
            missing_or_invalid_parameter="height_cm",
            recommendation="Confirm height measurement in centimeters."
        )
    if weight_kg <= 0.3 or weight_kg > 400:
        raise SafeCalculationRefusal(
            reason=f"Weight {weight_kg} kg is outside human physiological range.",
            missing_or_invalid_parameter="weight_kg",
            recommendation="Confirm weight measurement in kilograms."
        )

    bsa = math.sqrt((height_cm * weight_kg) / 3600.0)
    bsa_val = round(bsa, 2)

    return CalculationResult(
        calculator_id="mosteller_bsa",
        calculator_name="Mosteller Body Surface Area (BSA)",
        score=bsa_val,
        unit="m2",
        interpretation_band=f"Body Surface Area: {bsa_val} m2",
        clinical_recommendation="Use BSA for chemotherapy, cardiac index, and burn surface assessments.",
        guideline_citation="Mosteller RD. Simplified calculation of body-surface area. N Engl J Med 1987;317(17):1098.",
        guideline_year=1987,
        applicable_population="Pediatric and adult patients",
        raw_inputs={"height_cm": height_cm, "weight_kg": weight_kg},
        warnings=[]
    )


def calculate_curb65_score(
    confusion: bool,
    bun_mg_dl: Optional[float] = None,
    urea_mmol_l: Optional[float] = None,
    respiratory_rate_bpm: Optional[int] = None,
    systolic_bp_mmhg: Optional[int] = None,
    diastolic_bp_mmhg: Optional[int] = None,
    age_years: Optional[int] = None
) -> CalculationResult:
    """
    CURB-65 Pneumonia Severity Score.
    Guideline: Lim WS, et al. Thorax 2003;58:377-382 (BTS Guidelines).
    Includes unit normalization: BUN > 19 mg/dL is equivalent to Urea > 7.0 mmol/L.
    """
    if age_years is None:
        raise SafeCalculationRefusal(
            reason="Age is a mandatory component of CURB-65.",
            missing_or_invalid_parameter="age_years",
            recommendation="Provide patient age."
        )

    if age_years < 18:
        raise SafeCalculationRefusal(
            reason="CURB-65 pneumonia severity score is validated exclusively for adult patients >= 18 years.",
            missing_or_invalid_parameter="age_years",
            recommendation="For pediatric patients (< 18 years), apply pediatric community-acquired pneumonia criteria (BTS Pediatric / IDSA/PIDS)."
        )

    if respiratory_rate_bpm is not None and (respiratory_rate_bpm < 0 or respiratory_rate_bpm > 100):
        raise SafeCalculationRefusal(
            reason=f"Respiratory rate {respiratory_rate_bpm} bpm is outside physiologically possible human limits (0 - 100 bpm).",
            missing_or_invalid_parameter="respiratory_rate_bpm",
            recommendation="Verify and enter an accurate vital signs measurement."
        )

    if systolic_bp_mmhg is not None and (systolic_bp_mmhg <= 20 or systolic_bp_mmhg > 350):
        raise SafeCalculationRefusal(
            reason=f"Systolic blood pressure {systolic_bp_mmhg} mmHg is outside physiologically possible limits (21 - 350 mmHg).",
            missing_or_invalid_parameter="systolic_bp_mmhg",
            recommendation="Confirm blood pressure measurement."
        )

    if diastolic_bp_mmhg is not None and (diastolic_bp_mmhg < 10 or diastolic_bp_mmhg > 250):
        raise SafeCalculationRefusal(
            reason=f"Diastolic blood pressure {diastolic_bp_mmhg} mmHg is outside physiologically possible limits (10 - 250 mmHg).",
            missing_or_invalid_parameter="diastolic_bp_mmhg",
            recommendation="Confirm blood pressure measurement."
        )

    score = 0
    warnings = []

    # C: Confusion
    if confusion:
        score += 1

    # U: Urea / BUN
    if bun_mg_dl is not None:
        if bun_mg_dl > 19.0:
            score += 1
    elif urea_mmol_l is not None:
        if urea_mmol_l > 7.0:
            score += 1
    else:
        warnings.append("BUN/Urea measurement missing: calculating partial CRB-65 score.")

    # R: Respiratory rate >= 30
    if respiratory_rate_bpm is not None:
        if respiratory_rate_bpm >= 30:
            score += 1
    else:
        warnings.append("Respiratory rate missing: score may underestimate pneumonia severity.")

    # B: Blood pressure (SBP < 90 or DBP <= 60)
    if systolic_bp_mmhg is not None and diastolic_bp_mmhg is not None:
        if systolic_bp_mmhg < 90 or diastolic_bp_mmhg <= 60:
            score += 1
    elif systolic_bp_mmhg is not None or diastolic_bp_mmhg is not None:
        warnings.append("Incomplete blood pressure readings.")

    # 65: Age >= 65
    if age_years >= 65:
        score += 1

    if score <= 1:
        band = f"CURB-65 Score {score}: Low Risk (30-day mortality < 3%)"
        rec = "Consider outpatient management. Verify adequate oxygenation (SpO2 >= 92%) and social support."
    elif score == 2:
        band = f"CURB-65 Score {score}: Moderate Risk (30-day mortality ~ 9%)"
        rec = "Consider short hospital stay or closely monitored outpatient care."
    else:
        band = f"CURB-65 Score {score}: High Risk (30-day mortality 15-40%)"
        rec = "Urgent hospital admission required; assess for ICU / high-dependency unit placement."

    warnings.append("CURB-65 does not evaluate hypoxia (SpO2 < 90%), sepsis, or uncompensated comorbidities.")

    return CalculationResult(
        calculator_id="curb65_score",
        calculator_name="CURB-65 Community-Acquired Pneumonia Severity Score",
        score=float(score),
        unit="points",
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Lim WS, et al. Defining community acquired pneumonia severity on presentation to hospital. Thorax 2003;58:377-382.",
        guideline_year=2003,
        applicable_population="Adults (>=18y) presenting with community-acquired pneumonia",
        raw_inputs={
            "confusion": confusion,
            "bun_mg_dl": bun_mg_dl,
            "urea_mmol_l": urea_mmol_l,
            "respiratory_rate_bpm": respiratory_rate_bpm,
            "systolic_bp_mmhg": systolic_bp_mmhg,
            "diastolic_bp_mmhg": diastolic_bp_mmhg,
            "age_years": age_years
        },
        warnings=warnings
    )


def calculate_wells_dvt_score(
    active_cancer: bool,
    paralysis_or_plaster_cast: bool,
    bedridden_gt_3days_or_major_surgery: bool,
    localized_tenderness_deep_veins: bool,
    entire_leg_swollen: bool,
    calf_swelling_gt_3cm_diff: bool,
    pitting_edema_symptomatic_leg: bool,
    collateral_superficial_veins: bool,
    previous_documented_dvt: bool,
    alternative_diagnosis_more_likely: bool
) -> CalculationResult:
    """
    Wells Criteria for Deep Vein Thrombosis (DVT).
    Guideline: Wells PS, et al. Thromb Haemost 2000;83:416-420.
    Range: -2 to 8 points. Returns 2-tier and 3-tier probability.
    """
    score = 0
    if active_cancer: score += 1
    if paralysis_or_plaster_cast: score += 1
    if bedridden_gt_3days_or_major_surgery: score += 1
    if localized_tenderness_deep_veins: score += 1
    if entire_leg_swollen: score += 1
    if calf_swelling_gt_3cm_diff: score += 1
    if pitting_edema_symptomatic_leg: score += 1
    if collateral_superficial_veins: score += 1
    if previous_documented_dvt: score += 1
    if alternative_diagnosis_more_likely: score -= 2

    if score <= 0:
        band = f"Wells DVT Score {score}: Low Probability (3-tier) / DVT Unlikely (2-tier)"
        rec = "DVT Unlikely: Obtain high-sensitivity D-dimer. If negative, DVT can be safely ruled out without ultrasound."
    elif score in [1, 2]:
        band = f"Wells DVT Score {score}: Moderate Probability (3-tier) / DVT Likely (2-tier if >=2)"
        rec = "Obtain D-dimer or proceed directly to compression duplex ultrasonography."
    else:
        band = f"Wells DVT Score {score}: High Probability (3-tier) / DVT Likely (2-tier)"
        rec = "DVT Likely: Perform compression duplex ultrasonography immediately. Consider empiric anticoagulation if delay."

    warnings = [
        "Pre-test probability MUST be paired with objective testing (D-dimer or duplex ultrasound). Never use as standalone diagnosis."
    ]

    return CalculationResult(
        calculator_id="wells_dvt_score",
        calculator_name="Wells Criteria for Deep Vein Thrombosis (DVT)",
        score=float(score),
        unit="points",
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Wells PS, et al. Derivation of a simple clinical model to categorize patients' probability of pulmonary embolism or DVT. Thromb Haemost 2000;83:416-420.",
        guideline_year=2000,
        applicable_population="Adults suspected of acute lower extremity DVT",
        raw_inputs={
            "active_cancer": active_cancer,
            "paralysis_or_plaster_cast": paralysis_or_plaster_cast,
            "bedridden_gt_3days_or_major_surgery": bedridden_gt_3days_or_major_surgery,
            "localized_tenderness_deep_veins": localized_tenderness_deep_veins,
            "entire_leg_swollen": entire_leg_swollen,
            "calf_swelling_gt_3cm_diff": calf_swelling_gt_3cm_diff,
            "pitting_edema_symptomatic_leg": pitting_edema_symptomatic_leg,
            "collateral_superficial_veins": collateral_superficial_veins,
            "previous_documented_dvt": previous_documented_dvt,
            "alternative_diagnosis_more_likely": alternative_diagnosis_more_likely
        },
        warnings=warnings
    )


def calculate_wells_pe_score(
    clinical_signs_symptoms_dvt: bool,
    pe_most_likely_or_equal_to_alt: bool,
    heart_rate_gt_100: bool,
    immobilization_or_surgery_past_4wks: bool,
    previous_pe_or_dvt: bool,
    hemoptysis: bool,
    active_malignancy: bool
) -> CalculationResult:
    """
    Wells Criteria for Pulmonary Embolism (PE).
    Guideline: Wells PS, et al. Lancet 1997;350:1795-1798 / Thromb Haemost 2000.
    """
    score = 0.0
    if clinical_signs_symptoms_dvt: score += 3.0
    if pe_most_likely_or_equal_to_alt: score += 3.0
    if heart_rate_gt_100: score += 1.5
    if immobilization_or_surgery_past_4wks: score += 1.5
    if previous_pe_or_dvt: score += 1.5
    if hemoptysis: score += 1.0
    if active_malignancy: score += 1.0

    score_val = round(score, 1)

    # 2-tier: <= 4.0 PE Unlikely, > 4.0 PE Likely
    if score_val <= 4.0:
        band = f"Wells PE Score {score_val}: PE Unlikely (2-tier)"
        rec = "PE Unlikely: Order high-sensitivity age-adjusted D-dimer. If negative, PE is ruled out without CTPA."
    else:
        band = f"Wells PE Score {score_val}: PE Likely (2-tier)"
        rec = "PE Likely: Proceed immediately to CT Pulmonary Angiography (CTPA). Consider therapeutic anticoagulation while awaiting imaging if no bleeding contraindications."

    warnings = [
        "Pre-test probability must be combined with age-adjusted D-dimer or CTPA imaging.",
        "Assess hemodynamic stability (massive PE with shock requires immediate bedside echo and thrombolysis assessment)."
    ]

    return CalculationResult(
        calculator_id="wells_pe_score",
        calculator_name="Wells Criteria for Pulmonary Embolism (PE)",
        score=score_val,
        unit="points",
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Wells PS, et al. Use of a clinical model for safe management of patients with suspected pulmonary embolism. Ann Intern Med 2001;135:98-107.",
        guideline_year=2001,
        applicable_population="Adults suspected of acute pulmonary embolism",
        raw_inputs={
            "clinical_signs_symptoms_dvt": clinical_signs_symptoms_dvt,
            "pe_most_likely_or_equal_to_alt": pe_most_likely_or_equal_to_alt,
            "heart_rate_gt_100": heart_rate_gt_100,
            "immobilization_or_surgery_past_4wks": immobilization_or_surgery_past_4wks,
            "previous_pe_or_dvt": previous_pe_or_dvt,
            "hemoptysis": hemoptysis,
            "active_malignancy": active_malignancy
        },
        warnings=warnings
    )


def calculate_bedside_schwartz_egfr(
    height_cm: float,
    serum_creatinine_mg_dl: float,
    age_years: float
) -> CalculationResult:
    """
    Bedside Schwartz Equation for Pediatric Estimated GFR (eGFR).
    Formula: eGFR (mL/min/1.73m2) = 0.413 * height_cm / serum_creatinine_mg_dl
    Citation: Schwartz GJ, Muñoz A, Schneider MF, et al. J Am Soc Nephrol 2009;20(3):629-637.
    Strictly applicable to pediatric patients < 18 years.
    """
    if age_years >= 18:
        raise SafeCalculationRefusal(
            reason="Bedside Schwartz equation is strictly validated for pediatric patients (< 18 years).",
            missing_or_invalid_parameter="age_years",
            recommendation="For adult patients >= 18 years, use the CKD-EPI 2021 race-free equation."
        )

    if height_cm < 30.0 or height_cm > 230.0:
        raise SafeCalculationRefusal(
            reason=f"Height {height_cm} cm is outside plausible pediatric range (30 - 230 cm).",
            missing_or_invalid_parameter="height_cm",
            recommendation="Confirm height in centimeters."
        )

    if serum_creatinine_mg_dl <= 0.05 or serum_creatinine_mg_dl > 25.0:
        raise SafeCalculationRefusal(
            reason=f"Serum creatinine {serum_creatinine_mg_dl} mg/dL is outside plausible range (0.06 - 25.0 mg/dL).",
            missing_or_invalid_parameter="serum_creatinine_mg_dl",
            recommendation="Verify creatinine value and units."
        )

    egfr = (0.413 * height_cm) / serum_creatinine_mg_dl
    egfr_val = round(egfr, 1)

    if egfr_val >= 90.0:
        band = f"Pediatric eGFR {egfr_val} mL/min/1.73m2: Normal or High (Stage G1)"
        rec = "Normal renal filtration rate for age. Maintain age-appropriate hydration."
    elif egfr_val >= 60.0:
        band = f"Pediatric eGFR {egfr_val} mL/min/1.73m2: Mildly Decreased (Stage G2)"
        rec = "Mild reduction. Monitor renal markers and avoid nephrotoxic medications."
    elif egfr_val >= 30.0:
        band = f"Pediatric eGFR {egfr_val} mL/min/1.73m2: Moderate to Severe (Stage G3a/G3b)"
        rec = "Significant pediatric renal impairment. Urgent pediatric nephrology referral; adjust all renally cleared drugs."
    elif egfr_val >= 15.0:
        band = f"Pediatric eGFR {egfr_val} mL/min/1.73m2: Severely Decreased (Stage G4)"
        rec = "Severe renal dysfunction. Prepare for kidney replacement therapy / dialysis."
    else:
        band = f"Pediatric eGFR {egfr_val} mL/min/1.73m2: Kidney Failure (Stage G5)"
        rec = "End-stage renal disease (ESRD). Immediate emergency pediatric nephrology admission."

    return CalculationResult(
        calculator_id="bedside_schwartz_egfr",
        calculator_name="Bedside Schwartz Pediatric eGFR (2009)",
        score=egfr_val,
        unit="mL/min/1.73m2",
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Schwartz GJ, Muñoz A, Schneider MF, et al. New equations to estimate GFR in children with CKD. J Am Soc Nephrol 2009;20(3):629-637.",
        guideline_year=2009,
        applicable_population="Pediatric patients (< 18 years)",
        raw_inputs={
            "height_cm": height_cm,
            "serum_creatinine_mg_dl": serum_creatinine_mg_dl,
            "age_years": age_years
        },
        warnings=[]
    )


def calculate_has_bled_score(
    hypertension_uncontrolled: bool,
    abnormal_renal_function: bool,
    abnormal_liver_function: bool,
    prior_stroke: bool,
    bleeding_history_or_predisposition: bool,
    labile_inr: bool = False,
    elderly_age_gt_65: bool = False,
    drugs_antiplatelet_or_nsaid: bool = False,
    alcohol_excess: bool = False,
    age_years: Optional[float] = None
) -> CalculationResult:
    """
    HAS-BLED Bleeding Risk Score for Patients with Atrial Fibrillation.
    Citation: Pisters R, et al. Chest 2010;138(5):1093-1100.
    Score: 0 to 9 points. High risk threshold: >= 3 points.
    """
    if age_years is not None:
        if age_years < 18:
            raise SafeCalculationRefusal(
                reason="HAS-BLED score is validated strictly for adults (age >= 18 years).",
                missing_or_invalid_parameter="age_years",
                recommendation="Use pediatric bleeding risk assessment tools for patients < 18 years."
            )
        if age_years > 65:
            elderly_age_gt_65 = True

    score = 0
    if hypertension_uncontrolled: score += 1
    if abnormal_renal_function: score += 1
    if abnormal_liver_function: score += 1
    if prior_stroke: score += 1
    if bleeding_history_or_predisposition: score += 1
    if labile_inr: score += 1
    if elderly_age_gt_65: score += 1
    if drugs_antiplatelet_or_nsaid: score += 1
    if alcohol_excess: score += 1

    if score >= 3:
        band = f"HAS-BLED Score {score}: High Bleeding Risk (>= 3 points)"
        rec = "High bleeding risk. Anticoagulation is NOT automatically contraindicated, but modifiable risk factors must be actively corrected and frequent clinical follow-up scheduled."
    elif score >= 1:
        band = f"HAS-BLED Score {score}: Moderate Bleeding Risk (1 - 2 points)"
        rec = "Moderate risk. Standard anticoagulation monitoring with periodic reassessment of bleeding risks."
    else:
        band = f"HAS-BLED Score {score}: Low Bleeding Risk (0 points)"
        rec = "Low bleeding risk. Proceed with guideline-directed anticoagulation if indicated."

    return CalculationResult(
        calculator_id="has_bled_score",
        calculator_name="HAS-BLED Bleeding Risk Score",
        score=score,
        unit="points",
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Pisters R, Lane DA, Nieuwlaat R, et al. A novel user-friendly score (HAS-BLED) to assess 1-year risk of major bleeding in patients with atrial fibrillation: the Euro Heart Survey. Chest 2010;138(5):1093-1100.",
        guideline_year=2010,
        applicable_population="Adults with atrial fibrillation receiving or considering anticoagulation",
        raw_inputs={
            "hypertension_uncontrolled": hypertension_uncontrolled,
            "abnormal_renal_function": abnormal_renal_function,
            "abnormal_liver_function": abnormal_liver_function,
            "prior_stroke": prior_stroke,
            "bleeding_history_or_predisposition": bleeding_history_or_predisposition,
            "labile_inr": labile_inr,
            "elderly_age_gt_65": elderly_age_gt_65,
            "drugs_antiplatelet_or_nsaid": drugs_antiplatelet_or_nsaid,
            "alcohol_excess": alcohol_excess
        },
        warnings=[
            "HAS-BLED should be used to identify and address reversible bleeding risk factors, not to withhold oral anticoagulation."
        ]
    )


def calculate_news2_score(
    respiration_rate_bpm: int,
    spo2_percent: float,
    air_or_oxygen: str,
    systolic_bp_mmhg: int,
    pulse_bpm: int,
    consciousness: str,
    temperature_celsius: float,
    age_years: Optional[float] = None
) -> CalculationResult:
    """
    National Early Warning Score 2 (NEWS2).
    Citation: Royal College of Physicians. National Early Warning Score (NEWS) 2. London: RCP, 2017.
    Assesses acute illness severity and risk of clinical deterioration.
    """
    if age_years is not None and age_years < 16:
        raise SafeCalculationRefusal(
            reason="NEWS2 is validated for non-pregnant adults aged 16 years and older.",
            missing_or_invalid_parameter="age_years",
            recommendation="Use Paediatric Early Warning System (PEWS) for patients under 16 years."
        )

    if respiration_rate_bpm < 0 or respiration_rate_bpm > 100:
        raise SafeCalculationRefusal(
            reason=f"Respiration rate {respiration_rate_bpm} bpm is outside physiological bounds (0 - 100 bpm).",
            missing_or_invalid_parameter="respiration_rate_bpm",
            recommendation="Confirm counted respiratory rate."
        )

    if systolic_bp_mmhg <= 20 or systolic_bp_mmhg > 350:
        raise SafeCalculationRefusal(
            reason=f"Systolic BP {systolic_bp_mmhg} mmHg is outside physiological bounds (21 - 350 mmHg).",
            missing_or_invalid_parameter="systolic_bp_mmhg",
            recommendation="Confirm blood pressure measurement."
        )

    score = 0
    warnings = []


    # 1. Respiration Rate
    if respiration_rate_bpm <= 8:
        score += 3
    elif 9 <= respiration_rate_bpm <= 11:
        score += 1
    elif 12 <= respiration_rate_bpm <= 20:
        score += 0
    elif 21 <= respiration_rate_bpm <= 24:
        score += 2
    else:  # >= 25
        score += 3

    # 2. SpO2 (Scale 1)
    if spo2_percent <= 91.0:
        score += 3
    elif 92.0 <= spo2_percent <= 93.0:
        score += 2
    elif 94.0 <= spo2_percent <= 95.0:
        score += 1
    else:  # >= 96
        score += 0

    # 3. Supplemental Oxygen
    sup_ox = air_or_oxygen.strip().upper()
    if sup_ox in ["OXYGEN", "O2", "SUPPLEMENTAL"]:
        score += 2
    elif sup_ox in ["AIR", "ROOM_AIR"]:
        score += 0
    else:
        warnings.append(f"Unrecognized oxygen status '{air_or_oxygen}', defaulting to AIR.")

    # 4. Systolic BP
    if systolic_bp_mmhg <= 90:
        score += 3
    elif 91 <= systolic_bp_mmhg <= 100:
        score += 2
    elif 101 <= systolic_bp_mmhg <= 110:
        score += 1
    elif 111 <= systolic_bp_mmhg <= 219:
        score += 0
    else:  # >= 220
        score += 3

    # 5. Pulse rate
    if pulse_bpm <= 40:
        score += 3
    elif 41 <= pulse_bpm <= 50:
        score += 1
    elif 51 <= pulse_bpm <= 90:
        score += 0
    elif 91 <= pulse_bpm <= 110:
        score += 1
    elif 111 <= pulse_bpm <= 130:
        score += 2
    else:  # >= 131
        score += 3

    # 6. Consciousness (Alert vs CVPU: Confusion, Voice, Pain, Unresponsive)
    cons_upper = consciousness.strip().upper()
    if cons_upper in ["ALERT", "A"]:
        score += 0
    elif cons_upper in ["CVPU", "CONFUSED", "VOICE", "PAIN", "UNRESPONSIVE", "V", "P", "U"]:
        score += 3
    else:
        score += 3
        warnings.append(f"Non-alert or unrecognized consciousness '{consciousness}', scored 3.")

    # 7. Temperature
    if temperature_celsius <= 35.0:
        score += 3
    elif 35.1 <= temperature_celsius <= 36.0:
        score += 1
    elif 36.1 <= temperature_celsius <= 38.0:
        score += 0
    elif 38.1 <= temperature_celsius <= 39.0:
        score += 1
    else:  # >= 39.1
        score += 2

    # Clinical risk classification
    if score >= 7:
        band = f"NEWS2 Score {score}: High Clinical Risk"
        rec = "Emergency response: Immediate assessment by rapid response / critical care team with continuous vital sign monitoring. Consider ICU escalation."
    elif score >= 5:
        band = f"NEWS2 Score {score}: Medium Clinical Risk"
        rec = "Urgent response: Urgent bedside clinical review by a clinician competent in acute assessment. Increase observation frequency to at least hourly."
    else:
        band = f"NEWS2 Score {score}: Low Clinical Risk"
        rec = "Ward-based response: Continue routine clinical observations (every 4 to 6 hours)."

    return CalculationResult(
        calculator_id="news2_score",
        calculator_name="National Early Warning Score 2 (NEWS2)",
        score=score,
        unit="points",
        interpretation_band=band,
        clinical_recommendation=rec,
        guideline_citation="Royal College of Physicians. National Early Warning Score (NEWS) 2: Standardising the assessment of acute-illness severity in the NHS. London: RCP, 2017.",
        guideline_year=2017,
        applicable_population="Adult inpatient clinical deterioration assessment",
        raw_inputs={
            "respiration_rate_bpm": respiration_rate_bpm,
            "spo2_percent": spo2_percent,
            "air_or_oxygen": air_or_oxygen,
            "systolic_bp_mmhg": systolic_bp_mmhg,
            "pulse_bpm": pulse_bpm,
            "consciousness": consciousness,
            "temperature_celsius": temperature_celsius
        },
        warnings=warnings
    )

