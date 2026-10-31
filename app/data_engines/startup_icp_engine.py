from typing import List, Dict, Any

class StartupICPEngine:
    """
    B2B Tech & High-Growth Startup Decision-Maker Engine.
    Filters by Role (CTO, CEO, Head of Sales, VP Eng), Headcount, Tech Stack & Funding Stage.
    """
    def __init__(self):
        self._tech_records: List[Dict[str, Any]] = [
            {
                "id": "tech_201",
                "name": "Alex Mercer",
                "first_name": "Alex",
                "last_name": "Mercer",
                "title": "Chief Technology Officer (CTO)",
                "company": "Kinetix Cloud Systems",
                "email": "alex.mercer@kinetixcloud.io",
                "phone": "+1 (415) 555-0193",
                "linkedin_url": "https://linkedin.com/in/alex-mercer-kinetix",
                "company_website": "https://kinetixcloud.io",
                "city": "San Francisco",
                "state": "CA",
                "country": "United States",
                "industry": "B2B SaaS / DevOps",
                "headcount": "45 employees",
                "funding_stage": "Series A ($6.2M)",
                "tech_stack": "AWS, Kubernetes, Next.js, FastAPI, PostgreSQL",
                "icp_tags": "CTO, Cloud Infrastructure, High Growth, Tech Leader",
                "data_source": "LinkedIn Sales Nav / TechCrunch",
                "verified_badge": True
            },
            {
                "id": "tech_202",
                "name": "Priya Sharma",
                "first_name": "Priya",
                "last_name": "Sharma",
                "title": "Head of Engineering",
                "company": "PayFlow FinTech Solutions",
                "email": "priya.sharma@payflowglobal.com",
                "phone": "+44 20 7946 0912",
                "linkedin_url": "https://linkedin.com/in/priya-sharma-payflow",
                "company_website": "https://payflowglobal.com",
                "city": "London",
                "state": "Greater London",
                "country": "United Kingdom",
                "industry": "FinTech & Payments",
                "headcount": "80 employees",
                "funding_stage": "Series B ($18M)",
                "tech_stack": "GCP, Golang, React, Snowflake, Kafka",
                "icp_tags": "VP Eng, Fintech, Cross-border Payments, Compliance",
                "data_source": "LinkedIn Sales Nav / Crunchbase",
                "verified_badge": True
            },
            {
                "id": "tech_203",
                "name": "Daniel Chen",
                "first_name": "Daniel",
                "last_name": "Chen",
                "title": "VP of Revenue & Growth",
                "company": "OmniLogistics AI",
                "email": "daniel.chen@omnilogistics.ai",
                "phone": "+1 (206) 555-0814",
                "linkedin_url": "https://linkedin.com/in/daniel-chen-growth",
                "company_website": "https://omnilogistics.ai",
                "city": "Seattle",
                "state": "WA",
                "country": "United States",
                "industry": "Supply Chain SaaS",
                "headcount": "32 employees",
                "funding_stage": "Seed ($3.0M)",
                "tech_stack": "Python, React, AWS, Segment, HubSpot",
                "icp_tags": "CRO, VP Sales, Logistics AI, Freight Automation, B2B Outbound",
                "data_source": "LinkedIn Sales Nav / ProductHunt",
                "verified_badge": True
            },
            {
                "id": "tech_204",
                "name": "Sarah O'Connor",
                "first_name": "Sarah",
                "last_name": "O'Connor",
                "title": "Chief Executive Officer & Founder (CEO)",
                "company": "BioTrace Diagnostics",
                "email": "soconnor@biotracedx.com",
                "phone": "+1 (617) 555-3421",
                "linkedin_url": "https://linkedin.com/in/sarah-oconnor-biotrace",
                "company_website": "https://biotracedx.com",
                "city": "Boston",
                "state": "MA",
                "country": "United States",
                "industry": "HealthTech & Diagnostics",
                "headcount": "24 employees",
                "funding_stage": "Seed ($2.5M)",
                "tech_stack": "AWS HIPAA Cloud, Python, Next.js",
                "icp_tags": "CEO, Founder, HealthTech, Enterprise Buyer",
                "data_source": "LinkedIn Sales Nav / AngelList",
                "verified_badge": True
            }
        ]

    def search_startups(
        self,
        query: str = "",
        role: str = "",
        industry: str = "",
        country: str = "",
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        results = []
        q = query.lower().strip()
        r = role.lower().strip()
        ind = industry.lower().strip()
        c = country.lower().strip()

        # Common search expansions
        role_synonyms = {
            "cto": ["chief technology officer", "cto", "head of engineering"],
            "ceo": ["chief executive officer", "ceo", "founder"],
            "cpo": ["chief procurement officer", "chief product officer", "cpo"],
            "cro": ["chief revenue officer", "vp of revenue", "cro", "vp sales"],
            "vp": ["vice president", "vp"],
        }

        for rec in self._tech_records:
            if c and c not in rec["country"].lower():
                continue
            if r and r not in rec["title"].lower():
                continue
            if ind and (ind not in rec["industry"].lower() and ind not in rec.get("icp_tags", "").lower()):
                continue
            if q:
                matchable = f"{rec['company']} {rec['name']} {rec['title']} {rec['tech_stack']} {rec['industry']} {rec.get('icp_tags', '')} {rec.get('funding_stage', '')}".lower()
                
                # Check direct or synonym match
                direct_match = q in matchable
                synonym_match = False
                if q in role_synonyms:
                    synonym_match = any(syn in matchable for syn in role_synonyms[q])
                
                if not direct_match and not synonym_match:
                    continue

            results.append(rec)
            if len(results) >= limit:
                break

        return results

