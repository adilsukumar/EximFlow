import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
else:
    sys.path.remove(str(BASE_DIR))
    sys.path.insert(0, str(BASE_DIR))

# Strip external editable finders from sys.meta_path
for finder in list(sys.meta_path):
    finder_repr = repr(finder).lower()
    if "lightsense" in finder_repr or "nifty" in finder_repr:
        sys.meta_path.remove(finder)

from app.main import app

class TestAppRoutes(unittest.TestCase):
    def test_routes_registered(self):
        registered_paths = [route.path for route in app.routes if hasattr(route, "path")]
        
        # Core UI
        self.assertIn("/", registered_paths)
        self.assertIn("/api/status", registered_paths)
        self.assertIn("/api/search", registered_paths)
        
        # Social Parser (parser.im)
        self.assertIn("/api/parser/social-search", registered_paths)
        self.assertIn("/api/parser/reel-parse", registered_paths)
        self.assertIn("/api/parser/import-csv", registered_paths)
        
        # Harvey Autonomous SDR (ethanplusai/harvey)
        self.assertIn("/api/harvey/status", registered_paths)
        self.assertIn("/api/harvey/configure", registered_paths)
        self.assertIn("/api/harvey/run-cycle", registered_paths)
        self.assertIn("/api/harvey/approve-outbox", registered_paths)
        
        # Humanized Vault & Proposals
        self.assertIn("/api/templates/vault", registered_paths)
        self.assertIn("/api/proposal/generate", registered_paths)
        
        # CRM & Verification
        self.assertIn("/api/crm/leads", registered_paths)
        self.assertIn("/api/crm/batch-verify", registered_paths)
        self.assertIn("/api/crm/export-csv", registered_paths)

if __name__ == "__main__":
    unittest.main()

