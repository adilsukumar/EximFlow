import csv
import io
from typing import List, Dict, Any
from datetime import datetime

class CRMService:
    """
    Manages the sales pipeline, lead status transitions,
    Smartlead/Instantly CSV exports, and AI response classification.
    """
    def __init__(self):
        self._leads: List[Dict[str, Any]] = [
            {
                "id": "crm_01",
                "name": "Marcus Vance",
                "email": "m.vance@americanspiceimports.com",
                "title": "VP of Sourcing",
                "company": "American Spice Imports LLC",
                "country": "United States",
                "product": "Organic Turmeric & Pepper",
                "status": "Discovery Call Booked",
                "stage": "call_booked",
                "call_date": "2026-11-04 15:30 EST",
                "last_touch": "Day 4 Follow-up sent",
                "notes": "Reviewed SGS lab report. Interested in 2x 20ft containers CIF Newark."
            },
            {
                "id": "crm_02",
                "name": "Jennifer Sterling",
                "email": "jsterling@goldengrainimports.com",
                "title": "Director of Sourcing",
                "company": "Golden Grain Wholesalers Inc",
                "country": "United States",
                "product": "Basmati Rice 1121",
                "status": "Positive Reply",
                "stage": "replied",
                "call_date": None,
                "last_touch": "Day 1 Initial Email",
                "notes": "Asked: 'What is your current MOQ and FOB Mundra price per metric ton?'"
            },
            {
                "id": "crm_03",
                "name": "Arthur Pendelton",
                "email": "apendelton@titanpipingusa.com",
                "title": "Chief Procurement Officer",
                "company": "Titan Piping Corp",
                "country": "United States",
                "product": "SS 316 Flanges",
                "status": "Outreach Active",
                "stage": "outreached",
                "call_date": None,
                "last_touch": "Day 1 Initial Email",
                "notes": "Delivered to primary inbox. Awaiting response."
            },
            {
                "id": "crm_04",
                "name": "Dirk Van Houten",
                "email": "d.vanhouten@euronordicfoods.nl",
                "title": "Head of Raw Materials",
                "company": "EuroNordic Food Ingredients BV",
                "country": "Netherlands",
                "product": "Dehydrated Onion Flakes",
                "status": "Verified",
                "stage": "verified",
                "call_date": None,
                "last_touch": "Waterfall verification passed",
                "notes": "Safety score 95/100. Ready for campaign launch."
            }
        ]

    def get_all_leads(self) -> List[Dict[str, Any]]:
        return self._leads

    def add_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        lead_id = f"crm_{len(self._leads) + 1:02d}"
        new_lead = {
            "id": lead_id,
            "name": lead_data.get("name", "Unknown Contact"),
            "email": lead_data.get("email", ""),
            "title": lead_data.get("title", ""),
            "company": lead_data.get("company", ""),
            "country": lead_data.get("country", "United States"),
            "product": lead_data.get("product", "Export Goods"),
            "status": lead_data.get("status", "Verified"),
            "stage": lead_data.get("stage", "verified"),
            "call_date": lead_data.get("call_date", None),
            "last_touch": lead_data.get("last_touch", "Added to pipeline"),
            "notes": lead_data.get("notes", "Discovered via EximFlow AI")
        }
        self._leads.append(new_lead)
        return new_lead

    def update_lead_stage(self, lead_id: str, new_stage: str) -> bool:
        stage_map = {
            "verified": "Verified",
            "outreached": "Outreach Active",
            "replied": "Positive Reply",
            "call_booked": "Discovery Call Booked",
            "unsubscribed": "Unsubscribed"
        }
        for lead in self._leads:
            if lead["id"] == lead_id:
                lead["stage"] = new_stage
                lead["status"] = stage_map.get(new_stage, new_stage)
                return True
        return False

    def classify_email_reply(self, reply_text: str) -> Dict[str, Any]:
        """
        AI Reply Triage Engine:
        Categorizes inbound buyer responses and generates next actions.
        """
        text_lower = reply_text.lower()

        # 1. Unsubscribe / Negative
        if any(w in text_lower for w in ["unsubscribe", "remove me", "not interested", "stop emailing", "wrong person"]):
            return {
                "classification": "UNSUBSCRIBE / NOT INTERESTED",
                "sentiment": "negative",
                "intent": "Remove from campaign immediately",
                "recommended_action": "Mark lead as Unsubscribed in Smartlead to prevent future emails.",
                "draft_response": None
            }

        # 2. Out of Office
        if any(w in text_lower for w in ["out of office", "on leave", "away from my desk", "returning on", "maternity leave"]):
            return {
                "classification": "OUT OF OFFICE",
                "sentiment": "neutral",
                "intent": "Snooze campaign touchpoints",
                "recommended_action": "Snooze sequence until prospect returns to office.",
                "draft_response": None
            }

        # 3. High Intent / Discovery Call Request
        if any(w in text_lower for w in ["call", "zoom", "calendly", "time to chat", "meet", "discuss", "phone", "availability", "schedule"]):
            return {
                "classification": "HIGH INTENT: DISCOVERY CALL",
                "sentiment": "positive",
                "intent": "Buyer wants to get on a call",
                "recommended_action": "ALERT CLIENT IMMEDIATELY: Hot lead ready for meeting booking.",
                "draft_response": (
                    "Hi [First Name],\n\n"
                    "Glad to connect! I would be delighted to coordinate a brief 15-minute call between your team "
                    "and our Export Director to discuss specs and logistics.\n\n"
                    "Here is a direct calendar link to pick a time convenient for your timezone: [Insert Calendly Link]\n\n"
                    "Looking forward to speaking soon!"
                )
            }

        # 4. Question / Request for Pricing / Spec Sheet
        return {
            "classification": "POSITIVE: PRODUCT INQUIRY",
            "sentiment": "positive",
            "intent": "Buyer requesting spec sheet, MOQ, or FOB pricing",
            "recommended_action": "Forward spec sheet and price quotation within 2 business hours.",
            "draft_response": (
                "Hi [First Name],\n\n"
                "Thank you for your response! Attached is our comprehensive product specification sheet along with "
                "our current FOB Mundra and CIF rates for standard 20ft/40ft containers.\n\n"
                "Could you let us know your required packaging specs (e.g. 25kg PP bags, vacuum packs) so we can provide an exact formal proforma quote?\n\n"
                "Best regards,\n[Client Name]"
            )
        }

    def export_csv_smartlead(self) -> str:
        """
        Exports pipeline leads to Smartlead / Instantly compatible CSV string.
        """
        output = io.StringIO()
        fieldnames = ["First Name", "Last Name", "Email", "Company", "Title", "Country", "Product", "Custom Notes"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for lead in self._leads:
            name_parts = lead["name"].split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            writer.writerow({
                "First Name": first_name,
                "Last Name": last_name,
                "Email": lead["email"],
                "Company": lead["company"],
                "Title": lead["title"],
                "Country": lead["country"],
                "Product": lead["product"],
                "Custom Notes": lead["notes"]
            })

        return output.getvalue()
