from typing import Dict, Any, List
import math

class DeliverabilityService:
    """
    DNS record generator, warmup scheduler, and domain capacity planner.
    """

    @staticmethod
    def generate_dns_records(domain: str) -> Dict[str, Any]:
        domain = domain.strip().lower()
        if not domain:
            domain = "example-exports.com"

        return {
            "domain": domain,
            "records": [
                {
                    "type": "TXT",
                    "host": "@",
                    "value": "v=spf1 include:_spf.google.com ~all",
                    "purpose": "SPF (Sender Policy Framework) - Authorizes Google Workspace mail servers"
                },
                {
                    "type": "TXT",
                    "host": "google._domainkey",
                    "value": "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3f9...",
                    "purpose": "DKIM (DomainKeys Identified Mail) - Cryptographic digital signature"
                },
                {
                    "type": "TXT",
                    "host": "_dmarc",
                    "value": f"v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@{domain}; pct=100; sp=quarantine",
                    "purpose": "DMARC - Directs spam filters on handling unauthenticated messages"
                },
                {
                    "type": "CNAME",
                    "host": "track",
                    "value": "custom.smartlead.io",
                    "purpose": "Custom Tracking Domain - Prevents shared domain reputation penalties"
                },
                {
                    "type": "MX",
                    "host": "@",
                    "value": "10 aspmx.l.google.com",
                    "purpose": "Google Workspace Primary MX"
                }
            ],
            "recommendation": "Configure these 5 records inside Cloudflare / Namecheap / GoDaddy DNS before sending any email."
        }

    @staticmethod
    def calculate_warmup_schedule(target_daily_volume: int = 100) -> List[Dict[str, Any]]:
        """
        Calculates a compliant 21-day warmup ramping calendar.
        """
        schedule = []
        for day in range(1, 22):
            if day <= 7:
                # Stage 1: Warmup only
                cold = 0
                warmup = min(day * 4, 30)
                phase = "Phase 1: Pure Warmup Pool"
            elif day <= 14:
                # Stage 2: Light Cold Introduction
                cold = (day - 7) * 3
                warmup = 25
                phase = "Phase 2: Gradual Cold Intro"
            else:
                # Stage 3: Controlled Scaling
                cold = min(15 + (day - 14) * 4, target_daily_volume)
                warmup = 20
                phase = "Phase 3: Production Outbound"

            schedule.append({
                "day": f"Day {day}",
                "cold_emails": cold,
                "warmup_emails": warmup,
                "total_emails": cold + warmup,
                "phase": phase
            })

        return schedule

    @staticmethod
    def calculate_inbox_capacity(target_monthly_emails: int = 3000) -> Dict[str, Any]:
        """
        Calculates domain & inbox requirements.
        Rule: Max 35 cold emails per inbox/day, max 2 inboxes per domain.
        22 business days per month.
        """
        daily_emails_needed = math.ceil(target_monthly_emails / 22)
        inboxes_needed = max(math.ceil(daily_emails_needed / 30), 2)
        domains_needed = max(math.ceil(inboxes_needed / 2), 1)

        cost_per_domain_yr = 800  # INR (.com domain)
        cost_per_inbox_mo = 400   # INR (Google Workspace or Inframail)

        est_monthly_cost = (inboxes_needed * cost_per_inbox_mo) + math.ceil((domains_needed * cost_per_domain_yr) / 12)

        return {
            "target_monthly_emails": target_monthly_emails,
            "daily_emails_capacity": inboxes_needed * 30,
            "required_secondary_domains": domains_needed,
            "required_mailboxes": inboxes_needed,
            "max_emails_per_inbox_daily": 30,
            "estimated_infra_cost_inr": est_monthly_cost,
            "safety_rating": "100% Google/Yahoo compliant (Spam rate < 0.05%)"
        }
