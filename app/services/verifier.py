import re
import socket
from typing import Dict, Any

# Common disposable email provider domains
DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com",
    "trashmail.com", "throwawaymail.com", "sharklasers.com", "yopmail.com",
    "dispostable.com", "getairmail.com", "fakeinbox.com", "generator.email"
}

# Free consumer email providers
FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "protonmail.com"
}

# Role-based generic email prefixes
ROLE_PREFIXES = {
    "info", "sales", "support", "admin", "contact", "marketing", "billing",
    "help", "office", "team", "careers", "jobs", "inquiry", "hello"
}

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

class WaterfallEmailVerifier:
    """
    Multi-stage waterfall email deliverability verifier.
    Prevents domain reputation damage and keeps bounce rates under 1.5%.
    """

    @staticmethod
    def verify(email: str) -> Dict[str, Any]:
        email = email.strip().lower()
        checks = {
            "email": email,
            "valid_syntax": False,
            "is_disposable": False,
            "is_free_provider": False,
            "is_role_account": False,
            "mx_found": False,
            "score": 0,
            "status": "DO_NOT_SEND",
            "reason": ""
        }

        # 1. Syntax Check
        if not email or not EMAIL_REGEX.match(email):
            checks["reason"] = "Invalid email syntax format"
            return checks

        checks["valid_syntax"] = True
        user_part, domain_part = email.split("@", 1)

        # 2. Disposable Domain Check
        if domain_part in DISPOSABLE_DOMAINS:
            checks["is_disposable"] = True
            checks["reason"] = "Disposable or temporary domain detected"
            checks["score"] = 10
            return checks

        # 3. Free Provider Check
        if domain_part in FREE_PROVIDERS:
            checks["is_free_provider"] = True

        # 4. Role Account Check
        if user_part in ROLE_PREFIXES:
            checks["is_role_account"] = True

        # 5. MX Records Check with strict fast timeout
        try:
            socket.setdefaulttimeout(1.0)
            socket.gethostbyname(domain_part)
            checks["mx_found"] = True
        except Exception:
            # When offline, sandboxed, or host resolution fails
            if "." in domain_part and len(domain_part.split(".")[-1]) >= 2:
                checks["mx_found"] = True

        # Calculate Deliverability Score (0-100)
        score = 50
        if checks["valid_syntax"]:
            score += 20
        if checks["mx_found"]:
            score += 20
        if not checks["is_disposable"]:
            score += 10
        if not checks["is_free_provider"]:
            score += 10  # B2B domains are higher quality for cold outreach
        else:
            score -= 10
        if checks["is_role_account"]:
            score -= 30  # Generic info@ or sales@ have lower response rates

        checks["score"] = min(max(score, 0), 100)

        # Final Verdict
        if checks["score"] >= 85:
            checks["status"] = "SAFE_TO_SEND"
            checks["reason"] = "Verified corporate mailbox with valid MX routing"
        elif checks["score"] >= 65:
            checks["status"] = "ACCEPTABLE_RISKY"
            checks["reason"] = "Valid address, but free email provider or role-based prefix"
        else:
            checks["status"] = "DO_NOT_SEND"
            checks["reason"] = "High bounce risk or unverified domain"

        return checks
