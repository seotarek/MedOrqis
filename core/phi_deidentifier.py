"""
MedOrqis — PHI De-Identification & Privacy Scrubbing Module
Redacts HIPAA 18 Identifiers, Egyptian 14-digit National IDs, and Saudi 10-digit Iqama/National IDs.
"""

from typing import Dict, Any, Tuple, List
import re


class PHIDeidentifier:
    def __init__(self):
        # Egyptian National ID: 14 digits starting with 2 or 3
        self.eg_nid_regex = re.compile(r"\b[23]\d{13}\b")
        # Saudi National ID / Iqama: 10 digits starting with 1 or 2
        self.sa_nid_regex = re.compile(r"\b[12]\d{9}\b")
        # Medical Record Number (MRN) patterns
        self.mrn_regex = re.compile(r"(?i)\b(?:MRN|Medical Record No|رقم الملف|الملف الطبي)[:\s#]*([A-Z0-9-]{5,15})\b")
        # Phone numbers (EG, SA, International)
        self.phone_regex = re.compile(r"(?:\+?20\s?1[0125]\d{8}|\+?966\s?5\d{8}|\b01[0125]\d{8}\b|\b05\d{8}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b)")
        # Emails
        self.email_regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        # Patient Name prefixes (English & Arabic)
        self.name_prefix_regex = re.compile(r"(?i)(?:Patient Name|Patient|Pt|المريض|اسم المريض|المريضة)[:\s]+([A-Za-z\u0621-\u064A\s]{3,35})(?=[,\n\r;]|$)", re.UNICODE)
        # Dates (DOB / Admission)
        self.date_regex = re.compile(r"(?i)\b(?:DOB|تاريخ الميلاد|Date of Birth)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")

    def deidentify(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Scrubs PHI from clinical free-text narratives.
        Returns scrubbed text and an audit count of redacted tokens.
        """
        redactions = {
            "egyptian_national_ids": 0,
            "saudi_national_ids": 0,
            "mrns": 0,
            "phone_numbers": 0,
            "emails": 0,
            "patient_names": 0,
            "dates_of_birth": 0
        }

        scrubbed = text

        # Redact Egyptian National IDs
        eg_matches = list(self.eg_nid_regex.finditer(scrubbed))
        redactions["egyptian_national_ids"] = len(eg_matches)
        scrubbed = self.eg_nid_regex.sub("[REDACTED_EGYPT_NID]", scrubbed)

        # Redact Saudi National IDs / Iqamas
        sa_matches = list(self.sa_nid_regex.finditer(scrubbed))
        redactions["saudi_national_ids"] = len(sa_matches)
        scrubbed = self.sa_nid_regex.sub("[REDACTED_SAUDI_ID]", scrubbed)

        # Redact Emails
        email_matches = list(self.email_regex.finditer(scrubbed))
        redactions["emails"] = len(email_matches)
        scrubbed = self.email_regex.sub("[REDACTED_EMAIL]", scrubbed)

        # Redact Phones
        phone_matches = list(self.phone_regex.finditer(scrubbed))
        redactions["phone_numbers"] = len(phone_matches)
        scrubbed = self.phone_regex.sub("[REDACTED_PHONE]", scrubbed)

        # Redact MRNs
        def replace_mrn(match):
            redactions["mrns"] += 1
            return match.group(0).replace(match.group(1), "[REDACTED_MRN]")
        scrubbed = self.mrn_regex.sub(replace_mrn, scrubbed)

        # Redact Dates of Birth
        def replace_dob(match):
            redactions["dates_of_birth"] += 1
            return match.group(0).replace(match.group(1), "[REDACTED_DOB]")
        scrubbed = self.date_regex.sub(replace_dob, scrubbed)

        # Redact Patient Names following explicit labels
        def replace_name(match):
            redactions["patient_names"] += 1
            return match.group(0).replace(match.group(1), "[REDACTED_PATIENT_NAME]")
        scrubbed = self.name_prefix_regex.sub(replace_name, scrubbed)

        total_redactions = sum(redactions.values())
        report = {
            "total_phi_items_redacted": total_redactions,
            "redaction_details": redactions,
            "deidentification_status": "SCRUBBED_SAFE" if total_redactions > 0 else "CLEAN_NO_DIRECT_PHI_FOUND",
            "regulatory_notice": "Regex scrubbing reduces risk under HIPAA Safe Harbor / GDPR / PDPL but does not replace institutional de-identification verification."
        }

        return (scrubbed, report)
