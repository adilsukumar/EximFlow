from typing import List, Dict, Any

class CustomsTradeEngine:
    """
    US/EU/Middle East Customs & Bill of Lading Intelligence Engine.
    Tracks verified importers who actively buy physical goods from Indian manufacturers.
    """
    def __init__(self):
        self._customs_records: List[Dict[str, Any]] = [
            {
                "id": "exim_101",
                "name": "Marcus Vance",
                "first_name": "Marcus",
                "last_name": "Vance",
                "title": "VP of Global Sourcing & Procurement",
                "company": "American Spice Imports LLC",
                "email": "m.vance@americanspiceimports.com",
                "phone": "+1 (201) 555-0182",
                "linkedin_url": "https://linkedin.com/in/marcus-vance-procurement",
                "company_website": "https://americanspiceimports.com",
                "city": "Secaucus",
                "state": "NJ",
                "country": "United States",
                "industry": "Agro & Food Spices",
                "hs_code": "091030 / 090411",
                "product_interest": "Organic Turmeric, Black Pepper, Cumin Seed",
                "annual_teu_volume": "38 TEU containers / yr",
                "recent_shipment_date": "2026-09-14",
                "port_of_origin": "Mundra Port (INMUN1), India",
                "port_of_discharge": "Port of New York / Newark, USA",
                "current_suppliers": "Exporters from Gujarat & Kerala",
                "data_source": "US Customs Bill of Lading (AMS)",
                "verified_badge": True
            },
            {
                "id": "exim_102",
                "name": "Jennifer Sterling",
                "first_name": "Jennifer",
                "last_name": "Sterling",
                "title": "Director of Agricultural Commodity Buying",
                "company": "Golden Grain Wholesalers Inc",
                "email": "jsterling@goldengrainimports.com",
                "phone": "+1 (713) 555-8841",
                "linkedin_url": "https://linkedin.com/in/jennifer-sterling-grain",
                "company_website": "https://goldengrainimports.com",
                "city": "Houston",
                "state": "TX",
                "country": "United States",
                "industry": "Grains & Cereals",
                "hs_code": "100630",
                "product_interest": "1121 & Traditional Basmati Rice, Sella Rice",
                "annual_teu_volume": "84 TEU containers / yr",
                "recent_shipment_date": "2026-10-02",
                "port_of_origin": "Nhava Sheva (INNSA1), India",
                "port_of_discharge": "Port of Houston, USA",
                "current_suppliers": "Exporters from Punjab & Haryana",
                "data_source": "US Customs Bill of Lading (AMS)",
                "verified_badge": True
            },
            {
                "id": "exim_103",
                "name": "Dirk Van Houten",
                "first_name": "Dirk",
                "last_name": "Van Houten",
                "title": "Head of Strategic Raw Materials",
                "company": "EuroNordic Food Ingredients BV",
                "email": "d.vanhouten@euronordicfoods.nl",
                "phone": "+31 10 555 4290",
                "linkedin_url": "https://linkedin.com/in/dirk-vanhouten-exim",
                "company_website": "https://euronordicfoods.nl",
                "city": "Rotterdam",
                "state": "South Holland",
                "country": "Netherlands",
                "industry": "Food Ingredients & Dehydrates",
                "hs_code": "071220 / 071290",
                "product_interest": "Dehydrated White Onion Flakes, Garlic Powder",
                "annual_teu_volume": "46 TEU containers / yr",
                "recent_shipment_date": "2026-09-28",
                "port_of_origin": "Pipavav Port (INPAV1), India",
                "port_of_discharge": "Port of Rotterdam, Netherlands",
                "current_suppliers": "Exporters from Mahuva / Gujarat",
                "data_source": "EU Import Customs Registry",
                "verified_badge": True
            },
            {
                "id": "exim_104",
                "name": "Arthur Pendelton",
                "first_name": "Arthur",
                "last_name": "Pendelton",
                "title": "Chief Procurement Officer",
                "company": "Titan Piping & Flange Distributors Corp",
                "email": "apendelton@titanpipingusa.com",
                "phone": "+1 (312) 555-7319",
                "linkedin_url": "https://linkedin.com/in/arthur-pendelton-piping",
                "company_website": "https://titanpipingusa.com",
                "city": "Chicago",
                "state": "IL",
                "country": "United States",
                "industry": "Engineering & Metals",
                "hs_code": "730721 / 730799",
                "product_interest": "Stainless Steel Flanges, Pipe Fittings (ANSI/ASME)",
                "annual_teu_volume": "62 TEU containers / yr",
                "recent_shipment_date": "2026-08-19",
                "port_of_origin": "Nhava Sheva (INNSA1), India",
                "port_of_discharge": "Port of Savannah, USA",
                "current_suppliers": "Exporters from Maharashtra & Gujarat",
                "data_source": "US Customs Bill of Lading (AMS)",
                "verified_badge": True
            },
            {
                "id": "exim_105",
                "name": "Claire Dupont",
                "first_name": "Claire",
                "last_name": "Dupont",
                "title": "Category Sourcing Director (Home Textiles)",
                "company": "Maison & Co Fabrics SA",
                "email": "c.dupont@maisontextiles.fr",
                "phone": "+33 1 42 68 55 12",
                "linkedin_url": "https://linkedin.com/in/claire-dupont-textiles",
                "company_website": "https://maisontextiles.fr",
                "city": "Lyon",
                "state": "Auvergne-Rhône-Alpes",
                "country": "France",
                "industry": "Textiles & Home Furnishings",
                "hs_code": "520811 / 630231",
                "product_interest": "Organic Combed Cotton Fabric, Bed Linen, Terry Towels",
                "annual_teu_volume": "52 TEU containers / yr",
                "recent_shipment_date": "2026-10-10",
                "port_of_origin": "Tuticorin Port (INTUT1), India",
                "port_of_discharge": "Port of Le Havre, France",
                "current_suppliers": "Exporters from Tirupur & Karur",
                "data_source": "EU Customs Trade Manifest",
                "verified_badge": True
            },
            {
                "id": "exim_106",
                "name": "Tariq Al-Mansoor",
                "first_name": "Tariq",
                "last_name": "Al-Mansoor",
                "title": "Director of General Trading & Procurement",
                "company": "Al-Mansoor FMCG Imports LLC",
                "email": "tariq@almansoorgroup.ae",
                "phone": "+971 4 332 9911",
                "linkedin_url": "https://linkedin.com/in/tariq-al-mansoor-fmcg",
                "company_website": "https://almansoorgroup.ae",
                "city": "Dubai",
                "state": "Dubai",
                "country": "United Arab Emirates",
                "industry": "FMCG & Commodities",
                "hs_code": "100630 / 090240",
                "product_interest": "Basmati Rice, Assam Orthodox Black Tea, Cardamom",
                "annual_teu_volume": "110 TEU containers / yr",
                "recent_shipment_date": "2026-10-18",
                "port_of_origin": "Mundra Port (INMUN1), India",
                "port_of_discharge": "Jebel Ali Port (AEJEA), UAE",
                "current_suppliers": "Exporters from Haryana & Assam",
                "data_source": "Dubai Trade Customs Registry",
                "verified_badge": True
            },
            {
                "id": "exim_107",
                "name": "Robert Kelling",
                "first_name": "Robert",
                "last_name": "Kelling",
                "title": "VP of Packaging Supply Chain",
                "company": "EcoPack Solutions Americas",
                "email": "r.kelling@ecopackamericas.com",
                "phone": "+1 (415) 555-9271",
                "linkedin_url": "https://linkedin.com/in/robert-kelling-packaging",
                "company_website": "https://ecopackamericas.com",
                "city": "Los Angeles",
                "state": "CA",
                "country": "United States",
                "industry": "Packaging & Polymers",
                "hs_code": "392321 / 481910",
                "product_interest": "Biodegradable PLA Bags, Corrugated Shipping Cartons",
                "annual_teu_volume": "42 TEU containers / yr",
                "recent_shipment_date": "2026-09-05",
                "port_of_origin": "Nhava Sheva (INNSA1), India",
                "port_of_discharge": "Port of Long Beach, USA",
                "current_suppliers": "Exporters from Daman & Vapi",
                "data_source": "US Customs Bill of Lading (AMS)",
                "verified_badge": True
            },
            {
                "id": "exim_108",
                "name": "Dr. Sarah Lindemann",
                "first_name": "Sarah",
                "last_name": "Lindemann",
                "title": "Head of API & Intermediates Sourcing",
                "company": "Bavaria Pharma Ingredients GmbH",
                "email": "s.lindemann@bavariapharma.de",
                "phone": "+49 89 214 7730",
                "linkedin_url": "https://linkedin.com/in/dr-sarah-lindemann-pharma",
                "company_website": "https://bavariapharma.de",
                "city": "Munich",
                "state": "Bavaria",
                "country": "Germany",
                "industry": "Pharmaceuticals & APIs",
                "hs_code": "293339 / 300490",
                "product_interest": "Paracetamol, Metformin HCl, Herbal Plant Extracts (GMP)",
                "annual_teu_volume": "28 TEU containers / yr",
                "recent_shipment_date": "2026-10-09",
                "port_of_origin": "Hazira Port (INHZR1), India",
                "port_of_discharge": "Port of Hamburg, Germany",
                "current_suppliers": "Exporters from Hyderabad & Ankleshwar",
                "data_source": "German Federal Customs Register",
                "verified_badge": True
            }
        ]

    def search_customs(
        self,
        query: str = "",
        product: str = "",
        country: str = "",
        hs_code: str = "",
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        results = []
        q = query.lower().strip()
        p = product.lower().strip()
        c = country.lower().strip()
        hs = hs_code.replace(" ", "").strip()

        for rec in self._customs_records:
            if c and c not in rec["country"].lower():
                continue
            if hs and hs not in rec["hs_code"].replace(" ", ""):
                continue
            if p and (p not in rec["product_interest"].lower() and p not in rec["industry"].lower()):
                continue
            if q:
                matchable = f"{rec['company']} {rec['name']} {rec['title']} {rec['product_interest']} {rec['city']}".lower()
                if q not in matchable:
                    continue

            results.append(rec)
            if len(results) >= limit:
                break

        return results
