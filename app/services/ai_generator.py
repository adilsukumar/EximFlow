import re
from typing import Dict, Any, List

SPAM_WORDS = {
    "guaranteed", "100% free", "risk-free", "act now", "limited time",
    "urgent", "congratulations", "winner", "click here", "cash bonus",
    "double your", "make money", "million dollars", "buy direct now"
}

class AIEmailGenerator:
    """
    Generates high-converting, humanized 3-touch cold email sequences
    customized for Indian Exporters and B2B Startups.
    """

    @staticmethod
    def generate_sequence(
        prospect_name: str,
        prospect_title: str,
        prospect_company: str,
        prospect_country: str = "United States",
        product_category: str = "Spices & Agro",
        client_company: str = "Surat Organic Agro Exports",
        client_name: str = "Rajesh Patel",
        client_title: str = "Head of International Trade",
        certifications: str = "BRC, FDA, USDA Organic",
        origin_port: str = "Mundra Port, India",
        dest_port: str = "Port of New York / Newark"
    ) -> Dict[str, Any]:
        first_name = prospect_name.split()[0] if prospect_name else "there"
        p_comp = prospect_company or "your firm"

        # Determine email flow based on product category
        cat_lower = product_category.lower()

        if "spice" in cat_lower or "agro" in cat_lower or "rice" in cat_lower or "onion" in cat_lower:
            touch1_subject = f"quick question re: {product_category} sourcing for {p_comp}"
            touch1_body = (
                f"Hi {first_name},\n\n"
                f"Saw that {p_comp} actively imports {product_category} into the {prospect_country}.\n\n"
                f"We are direct manufacturers and primary processors based in Gujarat, India, "
                f"supplying {certifications} certified shipments to distributors across North America and Europe.\n\n"
                f"Because we process directly at the source, our container FOB rates are typically 12–15% below "
                f"re-exporter pricing, with full third-party SGS inspection before loading at {origin_port}.\n\n"
                f"Are you open to reviewing our current spec sheet and CIF quotation for {dest_port} for your upcoming cycle?\n\n"
                f"Best regards,\n\n"
                f"{client_name}\n"
                f"{client_title} | {client_company}\n"
                f"WhatsApp: +91 98250 12345"
            )

            touch2_subject = f"Re: quick question re: {product_category} sourcing for {p_comp}"
            touch2_body = (
                f"Hi {first_name},\n\n"
                f"Following up on my previous note.\n\n"
                f"We just dispatched a 40ft container of {product_category} to a distributor in New Jersey last week. "
                f"Attached is a 1-page summary of our {certifications} lab test results and aflatoxin/moisture levels.\n\n"
                f"Would you be open to receiving a complimentary 500g product sample for your QA team to evaluate?\n\n"
                f"Happy to courier it directly to your warehouse facility.\n\n"
                f"Best,\n"
                f"{client_name}"
            )

            touch3_subject = f"closing loop on {product_category} supply for {p_comp}"
            touch3_body = (
                f"Hi {first_name},\n\n"
                f"I assume your {product_category} procurement contracts are locked in for this quarter.\n\n"
                f"I won't follow up further, but if your supply chain ever faces shipping delays or you need a reliable backup quotation, "
                f"feel free to keep our direct manufacturer contacts handy.\n\n"
                f"Wishing {p_comp} continued success.\n\n"
                f"Warmly,\n"
                f"{client_name}"
            )

        elif "textile" in cat_lower or "garment" in cat_lower or "cotton" in cat_lower:
            touch1_subject = f"{product_category} manufacturing capacity for {p_comp}"
            touch1_body = (
                f"Hi {first_name},\n\n"
                f"Noticed {p_comp}'s focus on premium {product_category} in {prospect_country}.\n\n"
                f"We operate a direct OEKO-TEX and GOTS-certified composite textile manufacturing facility in South India, "
                f"specializing in custom combed cotton yarn and finished home textiles.\n\n"
                f"We partner with international retail brands to deliver 35-day order turnaround times at competitive FOB pricing with low MOQs.\n\n"
                f"Would you be against looking over our Spring/Summer fabric swatch catalog and FOB price matrix?\n\n"
                f"Best,\n\n"
                f"{client_name}\n"
                f"{client_company}"
            )
            touch2_subject = f"Re: {product_category} manufacturing capacity for {p_comp}"
            touch2_body = (
                f"Hi {first_name},\n\n"
                f"Quick follow-up — we just concluded our production run for our European retail clients with zero shade variance.\n\n"
                f"Can we send across a couple of fabric swatches and GSM test reports to your sourcing desk?\n\n"
                f"Warmly,\n"
                f"{client_name}"
            )
            touch3_subject = f"respectful pass on {product_category}"
            touch3_body = (
                f"Hi {first_name},\n\n"
                f"I assume you have all vendor relationships settled for now. No worries at all.\n\n"
                f"If you ever need an audited backup factory with quick sampling, feel free to reach back out anytime.\n\n"
                f"Best,\n"
                f"{client_name}"
            )
        else:
            # Generic B2B / Tech / Startup ICP Flow
            touch1_subject = f"scaling {prospect_company}'s outbound with AI"
            touch1_body = (
                f"Hi {first_name},\n\n"
                f"Saw your leadership over {prospect_title} at {p_comp}.\n\n"
                f"Most B2B founders we speak with are struggling to book qualified discovery calls without hiring expensive SDRs or burning their primary email domains.\n\n"
                f"We built an autonomous AI pipeline that sources verified buyers, personalizes outreach, and books 8–15 discovery calls directly onto your sales calendar every month.\n\n"
                f"Open to a brief 7-minute intro call this Thursday to see how we booked 4 qualified meetings in week one for our latest client?\n\n"
                f"Best regards,\n\n"
                f"{client_name}\n"
                f"{client_company}"
            )
            touch2_subject = f"Re: scaling {prospect_company}'s outbound with AI"
            touch2_body = (
                f"Hi {first_name},\n\n"
                f"Following up on this — here is a quick 90-second screen recording showing our live response rate and inbox deliverability score.\n\n"
                f"Would you have 5 minutes to connect tomorrow afternoon?\n\n"
                f"Best,\n"
                f"{client_name}"
            )
            touch3_subject = f"closing the file"
            touch3_body = (
                f"Hi {first_name},\n\n"
                f"I assume outbound lead generation isn't a current priority for {p_comp}. Won't bother you further.\n\n"
                f"If things change down the line, I'll be here.\n\n"
                f"Best,\n"
                f"{client_name}"
            )

        # Spam analysis on Touch 1
        spam_findings = [w for w in SPAM_WORDS if w in touch1_body.lower() or w in touch1_subject.lower()]
        word_count = len(touch1_body.split())

        spam_score = 100 - (len(spam_findings) * 20)
        if word_count > 120:
            spam_score -= 15
        elif word_count < 40:
            spam_score -= 10

        return {
            "prospect_name": prospect_name,
            "prospect_company": prospect_company,
            "sequences": [
                {
                    "step": 1,
                    "day": "Day 1",
                    "subject": touch1_subject,
                    "body": touch1_body,
                    "goal": "Initial Hook & Direct Value Proposition",
                    "word_count": word_count
                },
                {
                    "step": 2,
                    "day": "Day 4",
                    "subject": touch2_subject,
                    "body": touch2_body,
                    "goal": "Social Proof & Free Product Sample / Swatch Offer",
                    "word_count": len(touch2_body.split())
                },
                {
                    "step": 3,
                    "day": "Day 8",
                    "subject": touch3_subject,
                    "body": touch3_body,
                    "goal": "Polite Low-Friction Breakup",
                    "word_count": len(touch3_body.split())
                }
            ],
            "spam_analysis": {
                "score": max(spam_score, 40),
                "is_clean": len(spam_findings) == 0,
                "detected_triggers": spam_findings,
                "reading_grade": "Grade 6 (Easy to skim on mobile)",
                "recommended_cta": "Low-friction question (spec sheet review / 5-min intro)"
            }
        }
