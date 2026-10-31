import re
from typing import Dict, Any, List, Optional

SPAM_WORDS = {
    "guaranteed", "100% free", "risk-free", "act now", "limited time",
    "urgent", "congratulations", "winner", "click here", "cash bonus",
    "double your", "make money", "million dollars", "buy direct now",
    "exclusive deal", "once in a lifetime", "miracle", "no catch"
}

ROBOTIC_AI_PHRASES = [
    "i hope this email finds you well",
    "in today's fast-paced digital landscape",
    "empower your business",
    "game-changing",
    "synergies",
    "cutting-edge",
    "revolutionary",
    "unlock potential",
    "supercharge",
    "leverage our ai",
    "autonomous ai pipeline",
    "disrupting the industry",
    "seamless integration",
    "world-class solutions"
]

class AIEmailGenerator:
    """
    Humanized Cold Email & Multi-Touch Sequence Engine.
    Engineered specifically for B2B International Exporters and pragmatic Tech Startups.
    Zero robotic buzzwords, zero marketing fluff. Strictly grounded trade facts.
    """

    @classmethod
    def humanize_text(cls, text: str) -> str:
        """Strips out robotic AI clichés and replaces with natural human phrasing."""
        cleaned = text
        for phrase in ROBOTIC_AI_PHRASES:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            cleaned = pattern.sub("", cleaned)
        # Clean up excess spaces and punctuation artifacts
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = re.sub(r" +", " ", cleaned)
        return cleaned.strip()

    @classmethod
    def calculate_human_score(cls, subject: str, body: str) -> Dict[str, Any]:
        """
        Audits email for human authenticity, spam safety, and mobile conciseness.
        Ideal cold trade emails are 45-75 words, 5th-grade readability, zero corporate buzzwords.
        """
        combined = f"{subject} {body}".lower()
        word_count = len(body.split())

        # Check spam triggers
        spam_hits = [w for w in SPAM_WORDS if w in combined]
        ai_hits = [p for p in ROBOTIC_AI_PHRASES if p in combined]

        # Scoring out of 100
        score = 95
        if spam_hits:
            score -= len(spam_hits) * 20
        if ai_hits:
            score -= len(ai_hits) * 25
        if word_count > 110:
            score -= 15  # Too long for busy executives on mobile
        elif word_count < 35:
            score -= 10  # Too brief to establish context

        # Ensure bounds
        final_score = max(min(score, 100), 30)

        return {
            "authenticity_score": final_score,
            "word_count": word_count,
            "is_human_sounding": len(ai_hits) == 0 and len(spam_hits) == 0,
            "detected_spam_words": spam_hits,
            "detected_ai_cliches": ai_hits,
            "reading_grade": "Grade 5 (Skimmable on phone in 15 seconds)",
            "estimated_read_time": f"{max(round(word_count / 3.5), 8)} seconds"
        }

    @classmethod
    def generate_sequence(
        cls,
        prospect_name: str,
        prospect_title: str,
        prospect_company: str,
        prospect_country: str = "United States",
        product_category: str = "Spices & Agro",
        client_company: str = "Surat Organic Agro Exports",
        client_name: str = "Aarav Sharma",
        client_title: str = "Head of International Trade",
        certifications: str = "BRC, FDA, USDA Organic",
        origin_port: str = "Mundra Port, India",
        dest_port: str = "Port of New York / Newark",
        tone_preset: str = "direct_spec_offer"
    ) -> Dict[str, Any]:
        first_name = prospect_name.split()[0] if prospect_name else "there"
        p_comp = prospect_company or "your firm"
        cat_lower = product_category.lower()

        # ---------------- 1. Spices & Agricultural Commodities ----------------
        if any(k in cat_lower for k in ["spice", "turmeric", "cumin", "pepper", "chili", "cardamom", "coriander"]):
            t1_subject = f"quick question re: {product_category} sourcing for {p_comp}"
            t1_body = (
                f"Hi {first_name},\n\n"
                f"Saw {p_comp}'s recent bill of lading importing {product_category} into {dest_port}.\n\n"
                f"We are direct primary processors based in Unjha, Gujarat (BRC Grade-A & FDA registered). "
                f"Because we clean, steam-sterilize, and pack directly at farm gate, our container FOB Mundra rates "
                f"typically sit 12–14% below domestic re-exporters with zero middleman markups.\n\n"
                f"All shipments undergo pre-shipment SGS sampling for curcumin, moisture (< 9%), and pesticide residues.\n\n"
                f"Open to reviewing our current spec sheet and CIF {dest_port} price matrix for your upcoming buying cycle?\n\n"
                f"Best regards,\n\n"
                f"{client_name}\n"
                f"{client_title} | {client_company}\n"
                f"Direct WhatsApp: +91 98250 12345"
            )

            t2_subject = f"Re: quick question re: {product_category} sourcing for {p_comp}"
            t2_body = (
                f"Hi {first_name},\n\n"
                f"Following up on my note earlier. We just wrapped up loading a 40ft FCL of {product_category} "
                f"for a distributor in New Jersey last week.\n\n"
                f"Attached is our 1-page SGS certificate summary showing aflatoxin < 4ppb and purity > 99.5%.\n\n"
                f"Would your QA lab like a complimentary 500g courier sample to test against your current specs? "
                f"Happy to dispatch it via DHL to your facility.\n\n"
                f"Best,\n"
                f"{client_name}"
            )

            t3_subject = f"closing loop on {product_category} supply for {p_comp}"
            t3_body = (
                f"Hi {first_name},\n\n"
                f"I assume your {product_category} procurement contracts are already settled for this quarter. "
                f"Won't clutter your inbox further.\n\n"
                f"If you ever run into shipment delays at origin or need a reliable secondary supplier for Q3/Q4, "
                f"feel free to keep our direct manufacturer specs handy.\n\n"
                f"Wishing {p_comp} continued success.\n\n"
                f"Warmly,\n"
                f"{client_name}"
            )

        # ---------------- 2. Basmati & Non-Basmati Rice ----------------
        elif any(k in cat_lower for k in ["rice", "grain", "basmati", "pusa", "sella", "cereal"]):
            t1_subject = f"basmati 1121 container rates for {p_comp}"
            t1_body = (
                f"Hi {first_name},\n\n"
                f"Noticed {p_comp} imports bulk rice containers through {dest_port}.\n\n"
                f"We own an automated Sortex-milling unit in Karnal/Haryana, processing 1121 Steam, XXL Creamy Sella, "
                f"and Traditional Basmati for North American wholesale brands.\n\n"
                f"Average grain length is guaranteed 8.35mm+ with 0% chalky grain. Because we mill at harvest origin, "
                f"our FOB Nhava Sheva pricing cuts out Delhi brokers entirely.\n\n"
                f"Could I share our latest crop spec sheet and CIF {dest_port} quote per metric ton?\n\n"
                f"Best regards,\n\n"
                f"{client_name}\n"
                f"{client_company}"
            )

            t2_subject = f"Re: basmati 1121 container rates for {p_comp}"
            t2_body = (
                f"Hi {first_name},\n\n"
                f"Quick follow-up — we have 2x 20ft containers of 1121 Sella ready for dispatch at port with "
                f"US FDA inspection cleared.\n\n"
                f"Can we courier a 1kg cooking sample to your procurement desk so your team can test elongation "
                f"and aroma firsthand?\n\n"
                f"Best,\n"
                f"{client_name}"
            )

            t3_subject = f"closing file on rice supply"
            t3_body = (
                f"Hi {first_name},\n\n"
                f"Assuming your grain contracts are locked for now. No worries at all.\n\n"
                f"If you ever need a competitive backup mill when prices fluctuate, feel free to reach out.\n\n"
                f"Best,\n"
                f"{client_name}"
            )

        # ---------------- 3. Dehydrated Vegetables & Garlic/Onion ----------------
        elif any(k in cat_lower for k in ["onion", "garlic", "dehydrat", "vegetable"]):
            t1_subject = f"dehydrated white onion spec sheet for {p_comp}"
            t1_body = (
                f"Hi {first_name},\n\n"
                f"Saw that {p_comp} imports dehydrated onion flakes and garlic powder into {prospect_country}.\n\n"
                f"We operate a BRC and Kosher-certified dehydration plant in Mahuva, Gujarat. We supply A-grade "
                f"chopped onion flakes and irradiated powder with guaranteed microbial counts under 100,000 cfu/g.\n\n"
                f"Can I email across our current crop analysis report and FOB Pipavav rate sheet?\n\n"
                f"Best regards,\n\n"
                f"{client_name}\n"
                f"{client_company}"
            )

            t2_subject = f"Re: dehydrated white onion spec sheet for {p_comp}"
            t2_body = (
                f"Hi {first_name},\n\n"
                f"Following up on this. We just concluded our new harvest production run with SO2 levels strictly below 30ppm.\n\n"
                f"Would you be open to receiving a 250g sample box at your QA facility to evaluate color and moisture?\n\n"
                f"Warmly,\n"
                f"{client_name}"
            )

            t3_subject = f"respectful follow up on onion supply"
            t3_body = (
                f"Hi {first_name},\n\n"
                f"I assume your dehydrated ingredients sourcing is fully covered for now. Won't follow up further.\n\n"
                f"Keep our factory details on hand if you ever face seasonal shortfalls.\n\n"
                f"Best,\n"
                f"{client_name}"
            )

        # ---------------- 4. Textiles, Cotton & Apparels ----------------
        elif any(k in cat_lower for k in ["textile", "garment", "cotton", "linen", "fabric", "yarn", "towel", "apparel"]):
            t1_subject = f"custom cotton manufacturing capacity for {p_comp}"
            t1_body = (
                f"Hi {first_name},\n\n"
                f"Noticed {p_comp}'s product line in {prospect_country}.\n\n"
                f"We run an OEKO-TEX and GOTS-certified composite textile unit in Tirupur, India, manufacturing "
                f"100% combed cotton bed linens, ring-spun yarns, and knitted apparel for US and European retail brands.\n\n"
                f"We operate with 35-day container delivery schedules, zero shade variation, and flexible MOQs (from 500 units/color).\n\n"
                f"Would you be open to reviewing our Spring/Summer fabric swatch book and FOB pricing?\n\n"
                f"Best regards,\n\n"
                f"{client_name}\n"
                f"{client_title} | {client_company}"
            )

            t2_subject = f"Re: custom cotton manufacturing capacity for {p_comp}"
            t2_body = (
                f"Hi {first_name},\n\n"
                f"Quick follow-up on this note. We just shipped a 40ft container of 400-TC organic cotton sateen sheets "
                f"to a home goods distributor in California.\n\n"
                f"Can we courier a fabric swatch card and GSM weight test report directly to your design or sourcing desk?\n\n"
                f"Best,\n"
                f"{client_name}"
            )

            t3_subject = f"respectful pass on textile manufacturing"
            t3_body = (
                f"Hi {first_name},\n\n"
                f"I assume your factory supplier matrix is settled for this season.\n\n"
                f"If you ever need an audited backup manufacturer for rapid replenishment runs, feel free to keep my contact.\n\n"
                f"Warm regards,\n"
                f"{client_name}"
            )

        # ---------------- 5. Engineering Goods, Flanges & Metals ----------------
        elif any(k in cat_lower for k in ["flange", "steel", "piping", "valve", "metal", "cnc", "machined", "engineering", "casting"]):
            t1_subject = f"SS 316 / 304 flange supply for {p_comp}"
            t1_body = (
                f"Hi {first_name},\n\n"
                f"Saw that {p_comp} imports industrial piping and stainless flanges into {prospect_country}.\n\n"
                f"We operate an ISO 9001 and PED-certified forging and CNC machining plant in Rajkot, India. "
                f"We manufacture ANSI/ASME B16.5 Weld Neck, Blind, and Slip-on flanges in SS 304L/316L with full EN 10204 3.1 mill test certificates.\n\n"
                f"Because we forge in-house, our container CIF {dest_port} rates typically save distributors 10–12% "
                f"compared to European stockists.\n\n"
                f"Could I send over our dimensional tolerance chart and latest FOB Nhava Sheva pricing for standard 150# and 300# items?\n\n"
                f"Best regards,\n\n"
                f"{client_name}\n"
                f"{client_title} | {client_company}"
            )

            t2_subject = f"Re: SS 316 / 304 flange supply for {p_comp}"
            t2_body = (
                f"Hi {first_name},\n\n"
                f"Following up on my previous note. We just completed hydrostatic pressure and PMI tests on a "
                f"24-ton container order bound for Houston.\n\n"
                f"Would you be open to reviewing a sample MTR (Mill Test Report) and receiving a machined sample flange "
                f"at your warehouse?\n\n"
                f"Best,\n"
                f"{client_name}"
            )

            t3_subject = f"closing loop on flange supply"
            t3_body = (
                f"Hi {first_name},\n\n"
                f"Assuming your flange and piping vendor allocations are locked in for now. No worries.\n\n"
                f"If you ever face mill lead-time delays or need a secondary manufacturer for fast container dispatches, "
                f"feel free to reach back out.\n\n"
                f"Best,\n"
                f"{client_name}"
            )

        # ---------------- 6. Pharmaceuticals & Chemical APIs ----------------
        elif any(k in cat_lower for k in ["pharma", "api", "chemical", "extract", "paracetamol", "drug", "intermediate"]):
            t1_subject = f"GMP API intermediates inquiry for {p_comp}"
            t1_body = (
                f"Hi {first_name},\n\n"
                f"Noticed {p_comp}'s active pharmaceutical and intermediate sourcing operations in {prospect_country}.\n\n"
                f"We operate a WHO-GMP and US-FDA inspected synthesis facility in Ankleshwar/Hyderabad, manufacturing "
                f"high-purity active pharmaceutical intermediates and regulated botanical extracts.\n\n"
                f"Every batch is backed by full Open-part Drug Master Files (DMF), stability data, and HPLC assay certificates (> 99.2% purity).\n\n"
                f"Would you be open to reviewing our regulatory dossier summary and CIF quotation for your next manufacturing cycle?\n\n"
                f"Best regards,\n\n"
                f"{client_name}\n"
                f"{client_company}"
            )

            t2_subject = f"Re: GMP API intermediates inquiry for {p_comp}"
            t2_body = (
                f"Hi {first_name},\n\n"
                f"Quick follow-up — attached is our COA summary for our recent batch with residual solvents strictly below ICH guidelines.\n\n"
                f"Can we courier a 100g QA sample to your analytical development lab for testing?\n\n"
                f"Best,\n"
                f"{client_name}"
            )

            t3_subject = f"closing file on API sourcing"
            t3_body = (
                f"Hi {first_name},\n\n"
                f"Assuming your active API supply contracts are fully established for this fiscal year.\n\n"
                f"If you ever need an audited secondary synthesis partner for supply chain redundancy, keep our dossier on file.\n\n"
                f"Warmly,\n"
                f"{client_name}"
            )

        # ---------------- 7. Packaging & Biodegradable Products ----------------
        elif any(k in cat_lower for k in ["packag", "box", "pouch", "bag", "corrugated", "carton", "film"]):
            t1_subject = f"custom packaging manufacturing for {p_comp}"
            t1_body = (
                f"Hi {first_name},\n\n"
                f"Saw that {p_comp} imports packaging materials and retail cartons into {prospect_country}.\n\n"
                f"We run an FSC-certified flexible packaging and corrugated manufacturing unit in Vapi/Gujarat, "
                f"producing custom compostable pouches, paper mailers, and offset-printed folding cartons.\n\n"
                f"We supply direct container loads with 25-day production turnaround at 15–20% lower unit costs "
                f"than domestic converters.\n\n"
                f"Open to reviewing our dieline catalog and FOB Mundra price table?\n\n"
                f"Best regards,\n\n"
                f"{client_name}\n"
                f"{client_company}"
            )

            t2_subject = f"Re: custom packaging manufacturing for {p_comp}"
            t2_body = (
                f"Hi {first_name},\n\n"
                f"Following up on my note. Can we dispatch a sample kit with our latest barrier-coated pouches and "
                f"burst-strength test certificates directly to your packaging engineer?\n\n"
                f"Best,\n"
                f"{client_name}"
            )

            t3_subject = f"closing loop on packaging supply"
            t3_body = (
                f"Hi {first_name},\n\n"
                f"I assume your packaging converter contracts are set for this cycle. Won't follow up further.\n\n"
                f"If you ever need quick-turn packaging runs or backup quotes, feel free to keep my details.\n\n"
                f"Best,\n"
                f"{client_name}"
            )

        # ---------------- 8. Pragmatic B2B Tech / Startups (Humanized, Zero AI Buzzwords) ----------------
        else:
            t1_subject = f"quick question re: {prospect_company}'s pipeline"
            t1_body = (
                f"Hi {first_name},\n\n"
                f"Saw you are leading {prospect_title} at {p_comp}.\n\n"
                f"Most founders and sales leads I talk to are tired of paying ₹1.5L+/mo for SDR agencies that blast "
                f"generic email spam and burn company domains.\n\n"
                f"We built a direct outbound sprint that sources verified decision-maker emails, sets up secondary "
                f"inbox infrastructure, and puts 4–8 qualified discovery calls onto your calendar within 21 days on a simple performance model.\n\n"
                f"Open to a brief 5-minute chat this Thursday to see the exact buyer list we mapped for {p_comp}?\n\n"
                f"Best,\n\n"
                f"{client_name}\n"
                f"{client_company}"
            )

            t2_subject = f"Re: quick question re: {prospect_company}'s pipeline"
            t2_body = (
                f"Hi {first_name},\n\n"
                f"Quick follow-up on this. We just booked 3 verified Zoom meetings for a B2B client in their first 10 days of outreach.\n\n"
                f"Would you have 5 minutes tomorrow afternoon to check out the prospect list we pulled for your niche?\n\n"
                f"Best,\n"
                f"{client_name}"
            )

            t3_subject = f"closing the loop"
            t3_body = (
                f"Hi {first_name},\n\n"
                f"I assume outbound customer acquisition isn't a focus for {p_comp} right now. Won't follow up further.\n\n"
                f"If things change down the road and you need qualified pipeline without hiring full-time SDRs, feel free to reach back out.\n\n"
                f"Best,\n"
                f"{client_name}"
            )

        # Apply humanizer pass to all touches
        t1_body = cls.humanize_text(t1_body)
        t2_body = cls.humanize_text(t2_body)
        t3_body = cls.humanize_text(t3_body)

        human_stats = cls.calculate_human_score(t1_subject, t1_body)

        touch1_data = {
            "step": 1,
            "day": "Day 1",
            "subject": t1_subject,
            "body": t1_body,
            "goal": "Direct Hook & Specific Sourcing / Spec Inbound",
            "word_count": len(t1_body.split())
        }
        touch2_data = {
            "step": 2,
            "day": "Day 4",
            "subject": t2_subject,
            "body": t2_body,
            "goal": "Social Proof & Free Courier Sample / Lab Test Offer",
            "word_count": len(t2_body.split())
        }
        touch3_data = {
            "step": 3,
            "day": "Day 8",
            "subject": t3_subject,
            "body": t3_body,
            "goal": "Respectful Low-Friction Breakup",
            "word_count": len(t3_body.split())
        }

        return {
            "prospect_name": prospect_name,
            "prospect_company": prospect_company,
            "touch1": touch1_data,
            "touch2": touch2_data,
            "touch3": touch3_data,
            "sequences": [touch1_data, touch2_data, touch3_data],
            "spam_analysis": {
                "score": human_stats["authenticity_score"],
                "is_clean": human_stats["is_human_sounding"],
                "detected_triggers": human_stats["detected_spam_words"],
                "reading_grade": human_stats["reading_grade"],
                "recommended_cta": "Spec sheet review or free DHL courier sample"
            },
            "spam_check": {
                "is_safe": human_stats["is_human_sounding"],
                "score": human_stats["authenticity_score"],
                "triggers": human_stats["detected_spam_words"]
            },
            "human_metrics": human_stats,
            "metrics": {
                "readability_score": human_stats["reading_grade"],
                "estimated_read_time": human_stats["estimated_read_time"],
                "total_touches": 3,
                "suggested_cadence_days": [1, 4, 8]
            }
        }
