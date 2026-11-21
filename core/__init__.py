"""
MedOrqis — Medical AI Skills Ecosystem
Core Deterministic Engines & Clinical Safety Layer.
"""

__version__ = "2.1.2"

from core.clinical_documenter import (
    ClinicalDocumenter,
    ClinicalDocumentInput,
    VitalsInput,
    LabValue,
    PanicAlert,
    PanicValueEngine,
    GeneratedDocument
)

from core.clinical_calculators import (
    SafeCalculationRefusal,
    CalculationResult,
    calculate_meld_na_score,
    calculate_glasgow_blatchford_score,
    calculate_ascvd_risk_acc_aha,
)

__all__ = [
    "ClinicalDocumenter",
    "ClinicalDocumentInput",
    "VitalsInput",
    "LabValue",
    "PanicAlert",
    "PanicValueEngine",
    "GeneratedDocument",
    "SafeCalculationRefusal",
    "CalculationResult",
    "calculate_meld_na_score",
    "calculate_glasgow_blatchford_score",
    "calculate_ascvd_risk_acc_aha",
    "__version__"
]
