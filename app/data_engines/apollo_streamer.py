import io
import csv
import zipfile
import logging
from typing import List, Dict, Any, Optional
from app.config import APOLLO_ZIP_PATH, HAS_APOLLO_ZIP

logger = logging.getLogger(__name__)

class ApolloStreamEngine:
    """
    Streams and queries lead records directly from inside the 19.6 GB Apollo ZIP
    without decompressing a single byte to disk.
    """
    def __init__(self, zip_path=APOLLO_ZIP_PATH):
        self.zip_path = zip_path
        self.is_available = zip_path.exists()
        self._fast_files = [
            'Entire Apollo Database 99,311,285/Agtech Apollo Database/Cleaned/Americas/americas_region_v5.csv',
            'Entire Apollo Database 99,311,285/Agtech Apollo Database/Cleaned/Americas/americas_region_v6.csv',
            'Entire Apollo Database 99,311,285/Agtech Apollo Database/Cleaned/Europe/europe_region_v5.csv',
            'Entire Apollo Database 99,311,285/Agtech Apollo Database/Cleaned/Asia/asia_region_v5.csv',
            'Entire Apollo Database 99,311,285/Agtech Apollo Database/Cleaned/cleaned-1.csv',
            'Entire Apollo Database 99,311,285/Agtech Apollo Database/Cleaned/cleaned-2.csv',
        ]

    def search_leads(
        self,
        query: str = "",
        title: str = "",
        country: str = "",
        company: str = "",
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Streaming search across the Apollo ZIP dataset with zero disk footprint.
        """
        if not self.is_available:
            return []

        results = []
        q_lower = query.lower().strip()
        t_lower = title.lower().strip()
        c_lower = country.lower().strip()
        comp_lower = company.lower().strip()

        try:
            with zipfile.ZipFile(self.zip_path, 'r') as z:
                # Search fast regional files first for lightning response
                for subfile in self._fast_files:
                    if len(results) >= limit:
                        break
                    try:
                        with z.open(subfile) as f:
                            text_stream = io.TextIOWrapper(f, encoding='utf-8', errors='ignore')
                            reader = csv.DictReader(text_stream)
                            for row in reader:
                                r_title = row.get('Title', '') or ''
                                r_comp = row.get('Company', '') or row.get('Company Name for Emails', '') or ''
                                r_country = row.get('Country', '') or ''
                                r_keywords = row.get('Keywords', '') or ''
                                r_industry = row.get('Industry', '') or ''
                                r_email = row.get('Email', '') or ''

                                if not r_email or '@' not in r_email:
                                    continue

                                # Match criteria
                                if t_lower and t_lower not in r_title.lower():
                                    continue
                                if c_lower and c_lower not in r_country.lower():
                                    continue
                                if comp_lower and comp_lower not in r_comp.lower():
                                    continue
                                if q_lower:
                                    searchable = f"{r_title} {r_comp} {r_keywords} {r_industry}".lower()
                                    if q_lower not in searchable:
                                        continue

                                results.append({
                                    "id": f"apollo_{len(results) + 1}",
                                    "first_name": row.get('First Name', '').strip(),
                                    "last_name": row.get('Last Name', '').strip(),
                                    "name": f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip(),
                                    "title": r_title.strip(),
                                    "company": r_comp.strip(),
                                    "email": r_email.strip(),
                                    "linkedin_url": row.get('Person Linkedin Url', '').strip(),
                                    "company_website": row.get('Website', '').strip(),
                                    "city": row.get('City', '').strip(),
                                    "country": r_country.strip() or "United States",
                                    "industry": r_industry.strip() or "Import & Sourcing",
                                    "keywords": r_keywords.strip(),
                                    "phone": row.get('Corporate Phone', '') or row.get('First Phone', ''),
                                    "data_source": "Apollo Database (99M Stream)",
                                    "verified_badge": True if row.get('is_deliverable') == 'true' else False
                                })

                                if len(results) >= limit:
                                    break
                    except Exception as err:
                        logger.warning(f"Error reading subfile {subfile}: {err}")
                        continue

        except Exception as e:
            logger.error(f"Error querying Apollo zip stream: {e}")

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Returns summary stats of the zip file without extracting."""
        if not self.is_available:
            return {"available": False, "total_records": 0, "size_gb": 0}
        
        file_size_gb = round(self.zip_path.stat().st_size / (1024**3), 2)
        return {
            "available": True,
            "filename": self.zip_path.name,
            "size_compressed_gb": file_size_gb,
            "estimated_people_records": 93239628,
            "estimated_company_records": 6071657,
            "streaming_mode": "Zero-Disk-Decompression Active"
        }
