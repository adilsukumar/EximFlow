"""
EximFlow AI - Autonomous Lead Gen & Cold Outreach Engine for B2B Exporters & Startups
"""
import sys

# Strip any external editable finders from sys.meta_path to avoid namespace collisions
for finder in list(sys.meta_path):
    finder_repr = repr(finder).lower()
    if "lightsense" in finder_repr or "nifty" in finder_repr:
        sys.meta_path.remove(finder)

__version__ = "1.0.0"

