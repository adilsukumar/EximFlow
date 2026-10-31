from typing import List, Dict, Any

class HumanizedTemplatesVault:
    """
    Catalog of human-tested cold email sequences for international trade and B2B startups.
    Zero robotic buzzwords. Written strictly like a pragmatic Export Director or Peer.
    """

    @classmethod
    def get_all_templates(cls) -> List[Dict[str, Any]]:
        return [
            {
                "id": "vault_spices",
                "category": "Agro Commodities & Spices",
                "target_persona": "VP of Sourcing / Procurement Director",
                "open_rate_benchmark": "58%",
                "reply_rate_benchmark": "12.4%",
                "touch1_subject": "quick question re: {{product}} sourcing for {{companyName}}",
                "touch1_body": (
                    "Hi {{firstName}},\n\n"
                    "Saw {{companyName}}'s bill of lading importing {{product}} into Port of Newark.\n\n"
                    "We are direct primary processors in Unjha, Gujarat (BRC & US FDA registered). "
                    "Because we clean, steam-sterilize, and pack directly at farm gate, our container FOB Mundra rates "
                    "are 12–14% below domestic re-exporters with zero distributor markups.\n\n"
                    "Every container is tested by SGS for curcumin, moisture (< 9%), and pesticide compliance.\n\n"
                    "Open to reviewing our current spec sheet and CIF Newark quote for your upcoming cycle?\n\n"
                    "Best regards,\n"
                    "{{senderName}}\n"
                    "{{senderCompany}} | Direct WhatsApp: +91 98250 12345"
                ),
                "touch2_subject": "Re: quick question re: {{product}} sourcing for {{companyName}}",
                "touch2_body": (
                    "Hi {{firstName}},\n\n"
                    "Following up on my previous note. We just finished loading a 40ft container for a distributor in New Jersey.\n\n"
                    "Attached is a 1-page summary of our SGS certificate showing aflatoxin < 4ppb and purity > 99.5%.\n\n"
                    "Would your QA lab like a complimentary 500g courier sample to evaluate against your current specs? "
                    "Happy to courier it via DHL directly to your facility.\n\n"
                    "Best,\n"
                    "{{senderName}}"
                ),
                "touch3_subject": "closing loop on {{product}} supply for {{companyName}}",
                "touch3_body": (
                    "Hi {{firstName}},\n\n"
                    "Assuming your {{product}} procurement contracts are locked for this season. Won't clutter your inbox further.\n\n"
                    "If you ever face shipment delays at origin or need a reliable backup supplier for Q3/Q4, "
                    "feel free to keep our direct manufacturer contacts handy.\n\n"
                    "Wishing {{companyName}} continued success.\n\n"
                    "Warmly,\n"
                    "{{senderName}}"
                )
            },
            {
                "id": "vault_rice",
                "category": "Basmati & Non-Basmati Grains",
                "target_persona": "Head of Grain Procurement / Wholesale Commodity Buyer",
                "open_rate_benchmark": "54%",
                "reply_rate_benchmark": "11.2%",
                "touch1_subject": "basmati 1121 container rates for {{companyName}}",
                "touch1_body": (
                    "Hi {{firstName}},\n\n"
                    "Noticed {{companyName}} imports bulk grain containers through Port of Houston.\n\n"
                    "We operate an automated Sortex-milling unit in Karnal, Haryana, processing 1121 Steam, XXL Creamy Sella, "
                    "and Traditional Basmati for North American distributors.\n\n"
                    "Average grain length is guaranteed 8.35mm+ with 0% chalky kernels. Because we mill directly at origin, "
                    "our FOB Nhava Sheva pricing cuts out Delhi export brokers.\n\n"
                    "Could I send our current harvest spec sheet and CIF quote per metric ton?\n\n"
                    "Best regards,\n"
                    "{{senderName}}\n"
                    "{{senderCompany}}"
                ),
                "touch2_subject": "Re: basmati 1121 container rates for {{companyName}}",
                "touch2_body": (
                    "Hi {{firstName}},\n\n"
                    "Quick follow-up — we have 2x 20ft containers of 1121 Sella ready at port with US FDA clearance.\n\n"
                    "Can we courier a 1kg cooking sample to your procurement team so they can test elongation and aroma firsthand?\n\n"
                    "Best,\n"
                    "{{senderName}}"
                ),
                "touch3_subject": "closing file on grain supply",
                "touch3_body": (
                    "Hi {{firstName}},\n\n"
                    "Assuming your grain contracts are locked for now. No worries.\n\n"
                    "If you ever need a competitive backup mill when market prices spike, feel free to reach back out.\n\n"
                    "Best,\n"
                    "{{senderName}}"
                )
            },
            {
                "id": "vault_flanges",
                "category": "Engineering Goods & Flanges (SS 304/316)",
                "target_persona": "Chief Procurement Officer / Industrial Supply Chain Director",
                "open_rate_benchmark": "61%",
                "reply_rate_benchmark": "13.8%",
                "touch1_subject": "SS 316 / 304 flange supply for {{companyName}}",
                "touch1_body": (
                    "Hi {{firstName}},\n\n"
                    "Saw that {{companyName}} distributes industrial piping and stainless flanges across the US.\n\n"
                    "We operate an ISO 9001 and PED-certified forging and CNC machining plant in Rajkot, India. "
                    "We produce ANSI/ASME B16.5 Weld Neck, Blind, and Slip-on flanges in SS 304L/316L with full EN 10204 3.1 mill test certificates.\n\n"
                    "Because we forge in-house, our container CIF rates typically save distributors 10–12% over European stockists.\n\n"
                    "Could I send across our dimensional tolerance chart and latest FOB Nhava Sheva price list for 150# and 300# items?\n\n"
                    "Best regards,\n"
                    "{{senderName}}\n"
                    "{{senderCompany}}"
                ),
                "touch2_subject": "Re: SS 316 / 304 flange supply for {{companyName}}",
                "touch2_body": (
                    "Hi {{firstName}},\n\n"
                    "Following up on my previous note. We just finished hydrostatic pressure and PMI tests on a 24-ton order bound for Houston.\n\n"
                    "Would you be open to reviewing our sample MTR (Mill Test Report) and receiving a machined sample flange at your facility?\n\n"
                    "Best,\n"
                    "{{senderName}}"
                ),
                "touch3_subject": "closing loop on flange supply",
                "touch3_body": (
                    "Hi {{firstName}},\n\n"
                    "Assuming your vendor allocations are locked for this quarter. No worries at all.\n\n"
                    "If you ever face mill lead-time delays or need a secondary manufacturer for fast container dispatches, feel free to keep my details.\n\n"
                    "Best,\n"
                    "{{senderName}}"
                )
            },
            {
                "id": "vault_textiles",
                "category": "Textiles, Combed Cotton & Apparels",
                "target_persona": "Director of Sourcing / Apparel Production Head",
                "open_rate_benchmark": "52%",
                "reply_rate_benchmark": "10.5%",
                "touch1_subject": "combed cotton manufacturing capacity for {{companyName}}",
                "touch1_body": (
                    "Hi {{firstName}},\n\n"
                    "Noticed {{companyName}}'s product line in {{country}}.\n\n"
                    "We run an OEKO-TEX and GOTS-certified composite textile facility in Tirupur, India, manufacturing "
                    "100% combed cotton bed linens, ring-spun yarns, and knitted apparel for international retail brands.\n\n"
                    "We operate with 35-day container turnarounds, zero shade variation, and flexible MOQs (from 500 units/color).\n\n"
                    "Would you be open to reviewing our Spring/Summer fabric swatch book and FOB pricing?\n\n"
                    "Best regards,\n"
                    "{{senderName}}\n"
                    "{{senderCompany}}"
                ),
                "touch2_subject": "Re: combed cotton manufacturing capacity for {{companyName}}",
                "touch2_body": (
                    "Hi {{firstName}},\n\n"
                    "Quick follow-up — we just dispatched a 40ft container of 400-TC organic cotton sateen sheets to California.\n\n"
                    "Can we courier a fabric swatch card and GSM weight report directly to your sourcing desk?\n\n"
                    "Warmly,\n"
                    "{{senderName}}"
                ),
                "touch3_subject": "respectful pass on textile supply",
                "touch3_body": (
                    "Hi {{firstName}},\n\n"
                    "Assuming your supplier matrix is settled for this season.\n\n"
                    "If you ever need an audited backup factory for fast replenishment runs, feel free to keep my contact.\n\n"
                    "Warm regards,\n"
                    "{{senderName}}"
                )
            },
            {
                "id": "vault_startups",
                "category": "B2B Tech Startups (Pragmatic Peer-to-Peer)",
                "target_persona": "Founder / CEO / VP Sales",
                "open_rate_benchmark": "64%",
                "reply_rate_benchmark": "14.1%",
                "touch1_subject": "quick question re: {{companyName}}'s outbound",
                "touch1_body": (
                    "Hi {{firstName}},\n\n"
                    "Saw you are leading {{title}} at {{companyName}}.\n\n"
                    "Most founders and sales leads I talk to are tired of paying ₹1.5L+/mo for SDR agencies that blast "
                    "generic email spam and burn company domains.\n\n"
                    "We built a direct outbound sprint that sources verified decision-maker emails, sets up secondary "
                    "inbox infrastructure, and puts 4–8 qualified discovery calls onto your calendar within 21 days on a simple performance model.\n\n"
                    "Open to a brief 5-minute chat this Thursday to see the exact buyer list we mapped for {{companyName}}?\n\n"
                    "Best,\n"
                    "{{senderName}}\n"
                    "{{senderCompany}}"
                ),
                "touch2_subject": "Re: quick question re: {{companyName}}'s outbound",
                "touch2_body": (
                    "Hi {{firstName}},\n\n"
                    "Quick follow-up on this. We just booked 3 verified Zoom meetings for a B2B client in their first 10 days of outreach.\n\n"
                    "Would you have 5 minutes tomorrow afternoon to check out the prospect list we pulled for your niche?\n\n"
                    "Best,\n"
                    "{{senderName}}"
                ),
                "touch3_subject": "closing the loop",
                "touch3_body": (
                    "Hi {{firstName}},\n\n"
                    "I assume outbound customer acquisition isn't a focus for {{companyName}} right now. Won't follow up further.\n\n"
                    "If things change down the road and you need qualified pipeline without hiring full-time SDRs, feel free to reach back out.\n\n"
                    "Best,\n"
                    "{{senderName}}"
                )
            }
        ]

    @classmethod
    def generate_client_proposal(
        cls,
        exporter_name: str,
        exporter_company: str,
        product: str,
        target_country: str = "United States",
        tier: str = "growth"
    ) -> Dict[str, Any]:
        """
        Generates a customized, high-converting Done-For-You outbound sales proposal
        ready to send to an Indian exporter or tech startup founder.
        """
        if tier == "starter":
            fee_retainer = "INR 35,000 / month"
            leads_target = "500"
            mailboxes = "2 mailboxes across 1 secondary domain"
            guaranteed_meetings = "2-3 qualified discovery calls"
        elif tier == "hybrid":
            fee_retainer = "INR 25,000 / mo + INR 5,000 per verified discovery call"
            leads_target = "1,000"
            mailboxes = "4 mailboxes across 2 secondary domains"
            guaranteed_meetings = "Pay-per-performance alignment"
        else: # growth
            fee_retainer = "INR 65,000 / month"
            leads_target = "1,500"
            mailboxes = "4 mailboxes across 2 secondary domains"
            guaranteed_meetings = "4-6 qualified international discovery calls"

        agreement_text = f"""
================================================================================
EXIMFLOW TRADE ADVISORY SERVICES - COMMERCIAL ENGAGEMENT AGREEMENT
Client: {exporter_company} (Attn: {exporter_name}, Authorized Signatory)
Service Provider: EximFlow Trade Advisory (International Business Development)
Date: 2026-10-31
Target Commodity / Product: {product}
Target Sourcing Territories: {target_country} (Customs Manifest Registry)
================================================================================

1. OBJECTIVE & SCOPE OF ENGAGEMENT:
   - Identify active international container importers sourcing {product} in target markets.
   - Sourcing Intelligence: Identify and verify {leads_target} verified procurement directors and import category buyers from customs manifests.
   - Communications Infrastructure: Provision {mailboxes} with industry-standard SPF, DKIM (2048-bit), and DMARC authentication.
   - Direct Trade Outreach: Execute tailored commercial correspondence focusing on direct manufacturer FOB/CIF pricing, laboratory quality standards (SGS, FDA, BRC), and sample evaluation offers.
   - Meeting Coordination: Triage incoming buyer inquiries and coordinate video discovery meetings directly on {exporter_company}'s calendar.

2. COMMERCIAL RETAINER & TERMS:
   - Package: {tier.upper()} ENGAGEMENT TIER
   - Monthly Retainer: {fee_retainer} per 30-day operating term, payable in advance upon invoice issuance.
   - Target Deliverable: {guaranteed_meetings}.
   - Client Responsibilities: Attend scheduled discovery calls, supply competitive quotation sheets and lab COAs, and dispatch standard 500g commercial evaluation samples upon buyer request.

3. CONFIDENTIALITY & EXCLUSIVITY:
   - All buyer contacts, correspondence threads, price quotations, and shipment manifests remain 100% exclusive to {exporter_company}.
   - EximFlow agrees not to conduct outbound business development for a direct competitor in {product} within the agreed territories during the active term.

4. ACCEPTANCE & AUTHORIZATION:
   - Authorized Signatory ({exporter_company}): _______________________
   - Authorized Partner, EximFlow Trade Advisory: _______________________
================================================================================
"""
        return {
            "exporter_name": exporter_name,
            "exporter_company": exporter_company,
            "product": product,
            "target_country": target_country,
            "tier": tier,
            "fee": fee_retainer,
            "leads": leads_target,
            "mailboxes": mailboxes,
            "guaranteed_meetings": guaranteed_meetings,
            "proposal_text": agreement_text.strip()
        }

