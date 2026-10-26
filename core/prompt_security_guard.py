"""
MedOrqis — Prompt Security & Adversarial Injection Defense
Guards against instruction override attacks, dosing boundary bypasses, and system prompt extraction.
"""

from typing import Dict, Any, Tuple, List
import re


class SecurityViolationError(ValueError):
    """Raised when an adversarial instruction override or dosing bypass attack is detected."""
    pass


class PromptSecurityGuard:
    def __init__(self):
        # Override and jailbreak indicators (English and Arabic)
        self.injection_patterns = [
            (re.compile(r"(?i)\b(?:ignore|disregard|bypass|override)\s+(?:all\s+)?(?:(?:previous|prior|system|safety)\s+)+(?:instructions|rules|prompts|limits)\b"), "INSTRUCTION_OVERRIDE"),
            (re.compile(r"(?i)\b(?:ignore|bypass|remove)\s+(?:dose|dosing|toxicity|maximum)\s+(?:caps?|limits?|boundaries?)\b"), "DOSING_SAFETY_BYPASS"),
            (re.compile(r"(?i)\b(?:repeat|print|dump|show|reveal)\s+(?:your\s+)?(?:system\s+prompt|developer\s+mode|internal\s+instructions)\b"), "SYSTEM_PROMPT_EXTRACTION"),
            (re.compile(r"(?i)\b(?:act as|pretend to be|roleplay as)\s+(?:an unrestricted|DAN|jailbroken|godmode)\b"), "JAILBREAK_ROLEPLAY"),
            (re.compile(r"(?:تجاهل|تجاوز|احذف|الغي)\s+(?:التعليمات|الضوابط|الحدود|الأمان|القواعد)\s+(?:السابقة|الطبية|القصوى)"), "ARABIC_INSTRUCTION_OVERRIDE"),
            (re.compile(r"(?:اطبع|اظهر|استخرج|اكشف)\s+(?:البرومبت|التعليمات الداخلية|النظام الداخلي)"), "ARABIC_SYSTEM_PROMPT_EXTRACTION")
        ]

    def scan_input(self, untrusted_text: str) -> Tuple[bool, List[str], str]:
        """
        Scans untrusted clinical input (e.g. pasted lab reports, OCR texts).
        Returns:
            (is_safe: bool, detected_threats: list[str], sanitized_text: str)
        """
        detected_threats = []
        for pattern, threat_type in self.injection_patterns:
            if pattern.search(untrusted_text):
                detected_threats.append(threat_type)

        is_safe = len(detected_threats) == 0
        sanitized_text = untrusted_text

        if not is_safe:
            # Strip offending patterns
            for pattern, _ in self.injection_patterns:
                sanitized_text = pattern.sub("[BLOCKED_UNTRUSTED_INSTRUCTION]", sanitized_text)

        return (is_safe, detected_threats, sanitized_text)
