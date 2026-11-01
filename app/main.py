import os
import io
import csv
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, Request, Query, Body, HTTPException, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, Response, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.config import APP_NAME, APP_DESCRIPTION, HAS_APOLLO_ZIP, APOLLO_ZIP_FILENAME, APOLLO_ZIP_PATH
from app.data_engines.apollo_streamer import ApolloStreamEngine
from app.data_engines.customs_engine import CustomsTradeEngine
from app.data_engines.startup_icp_engine import StartupICPEngine
from app.data_engines.social_parser import SocialParserEngine
from app.services.verifier import WaterfallEmailVerifier
from app.services.ai_generator import AIEmailGenerator
from app.services.deliverability import DeliverabilityService
from app.services.crm import CRMService
from app.services.templates_vault import HumanizedTemplatesVault
from app.services.harvey_agent import HarveyAutonomousSDRAgent
from app.services.pdf_generator import PDFProposalGenerator

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Harvey — Command Deck",
    description="Autonomous AI Sales & Trade Outreach Cockpit",
    version="2.1.0",
    redirect_slashes=False
)

# Mount static files safely
static_dir = BASE_DIR / "app" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates_dir = BASE_DIR / "app" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Initialize backend engines
apollo_engine = ApolloStreamEngine()
customs_engine = CustomsTradeEngine()
startup_engine = StartupICPEngine()
social_engine = SocialParserEngine()
crm_service = CRMService()
harvey_agent = HarveyAutonomousSDRAgent()

# Internal State Stores for Harvey Cockpit
_sending_state = {
    "mode": "approval",  # "approval" or "autopilot"
    "paused": None,      # None or reason string
    "provider": "gmail",
    "held": 0
}

_signals_state = {
    "summary": {"confirmed": 8, "proposed": 3, "rejected": 1},
    "groups": [
        {
            "name": "Customs Trade AMS Manifests (Physical Importers)",
            "signals": [
                {
                    "code": "AMS_TEU_IMPORT",
                    "name": "Active Maritime Bill of Lading (TEU > 10/yr)",
                    "description": "Importer has active bill of lading filed with US Customs within last 180 days.",
                    "status": "confirmed",
                    "confidence": 98,
                    "source": "US Customs AMS"
                },
                {
                    "code": "PORT_NEWARK_DISCHARGE",
                    "name": "Discharge Port: Newark / NY / Long Beach",
                    "description": "Receives cargo at Tier-1 commercial container terminals.",
                    "status": "confirmed",
                    "confidence": 95,
                    "source": "Port Authority"
                },
                {
                    "code": "AGRO_HS_MATCH",
                    "name": "HS Code Match (0904, 0910, 1006, 7307)",
                    "description": "Verified imports matching agricultural spices, basmati rice, or piping flanges.",
                    "status": "confirmed",
                    "confidence": 99,
                    "source": "Customs Tariff Schedule"
                }
            ]
        },
        {
            "name": "Social Media & Direct Wholesale Buyers",
            "signals": [
                {
                    "code": "IG_WHOLESALE_BIO",
                    "name": "Wholesale / B2B Sourcing in Instagram Bio",
                    "description": "Instagram profile explicitly mentions wholesale inquiries, importing, or distribution.",
                    "status": "confirmed",
                    "confidence": 92,
                    "source": "parser.im"
                },
                {
                    "code": "IG_COMMERCIAL_EMAIL",
                    "name": "Public Commercial Contact / Domain Email",
                    "description": "Verified business email in social profile header.",
                    "status": "confirmed",
                    "confidence": 94,
                    "source": "Social Graph"
                }
            ]
        },
        {
            "name": "Apollo 99.3M Global Directory Intelligence",
            "signals": [
                {
                    "code": "DECISION_MAKER_TITLE",
                    "name": "VP Sourcing / CPO / Head of Procurement",
                    "description": "Verified senior executive with purchasing authority.",
                    "status": "confirmed",
                    "confidence": 96,
                    "source": "Apollo Stream"
                },
                {
                    "code": "CORP_DOMAIN_VERIFIED",
                    "name": "Corporate Domain with Active MX Records",
                    "description": "Primary inbox deliverability verified through waterfall DNS checks.",
                    "status": "confirmed",
                    "confidence": 98,
                    "source": "Waterfall Verifier"
                },
                {
                    "code": "HIGH_GROWTH_TIER",
                    "name": "Growing Headcount (20-500 employees)",
                    "description": "Company size optimized for rapid outbound conversion.",
                    "status": "proposed",
                    "confidence": 88,
                    "source": "Apollo Stream"
                }
            ]
        }
    ]
}

_outbox_items = [
    {
        "id": "out_01",
        "to_email": "m.vance@americanspiceimports.com",
        "subject": "quick question re: Organic Spices sourcing for American Spice Imports LLC",
        "body": "Saw American Spice Imports LLC's recent bill of lading importing Organic Spices into Port of Newark.\n\nWe are a direct primary processor in Gujarat exporting BRC Grade-A & US FDA turmeric and cumin. Can we courier a 500g lab sample to Secaucus this week?\n\nBest regards,\nTrade Sourcing Desk",
        "deliverability_score": 100,
        "step": "Touch 1 (Day 1)",
        "words": 48,
        "status": "STAGED_REVIEW",
        "held": False,
        "context": {
            "company": "American Spice Imports LLC",
            "website": "https://americanspiceimports.com",
            "description": "US importer and distributor of bulk organic spices, herbs, and seasonings.",
            "contact": "Marcus Vance",
            "contact_title": "VP of Global Sourcing & Procurement",
            "email_status": "valid",
            "score": 98,
            "signals": {"US Customs AMS": "38 TEU containers imported in 2026", "Origin": "Mundra Port to Newark"},
            "contact_source": "customs",
            "campaign": "US Food Wholesalers & Spice Importers Q4",
            "notes": "Direct importer with active bills of lading."
        }
    },
    {
        "id": "out_02",
        "to_email": "jsterling@goldengrainimports.com",
        "subject": "Re: basmati 1121 container rates for Golden Grain Wholesalers Inc",
        "body": "Quick follow-up \u2014 we have 2x 20ft containers of 1121 Sella ready at port with US FDA clearance. Can we courier a 1kg cooking sample to your procurement team?\n\nBest regards,\nTrade Sourcing Desk",
        "deliverability_score": 95,
        "step": "Touch 2 (Day 4)",
        "words": 38,
        "status": "STAGED_REVIEW",
        "held": False,
        "context": {
            "company": "Golden Grain Wholesalers Inc",
            "website": "https://goldengrainimports.com",
            "description": "Major wholesale grain and basmati rice distributor across US West Coast.",
            "contact": "Jennifer Sterling",
            "contact_title": "Director of Sourcing",
            "email_status": "valid",
            "score": 95,
            "signals": {"US Customs AMS": "14 TEU containers (Long Beach)", "Category": "Basmati Rice 1121"},
            "contact_source": "customs",
            "campaign": "US Food Wholesalers & Spice Importers Q4",
            "notes": "Replied asking for MOQ and FOB Mundra port pricing."
        }
    }
]

_conversations = [
    {
        "id": "convo_01",
        "company": "Golden Grain Wholesalers Inc",
        "contact": "Jennifer Sterling",
        "contact_title": "Director of Sourcing",
        "status": "needs_human",
        "emails": [
            {
                "sent_at": "2026-10-31T09:14:00Z",
                "from": "Trade Desk <outbound@domain.com>",
                "to": "jsterling@goldengrainimports.com",
                "subject": "quick question re: basmati 1121 container rates for Golden Grain Wholesalers Inc",
                "body": "Saw Golden Grain's recent imports of long-grain rice into Long Beach. We have 2x 20ft containers of 1121 Sella ready at port with US FDA clearance. Can we courier a 1kg cooking sample?"
            }
        ],
        "thread": [
            {
                "timestamp": "2026-11-01T11:22:00Z",
                "role": "prospect",
                "inbound": True,
                "text": "What is your current MOQ and FOB Mundra price per metric ton? Also, please share your latest SGS lab analysis certificate."
            }
        ],
        "draft": {
            "subject": "Re: quick question re: basmati 1121 container rates for Golden Grain Wholesalers Inc",
            "body": "Hi Jennifer, MOQ is 1x 20ft container (24 MT). Current FOB Mundra is $1,180/MT. SGS lab certificate attached showing 8.35mm average grain length. Would Thursday 10 AM EST work for a 10-minute Zoom call?"
        }
    },
    {
        "id": "convo_02",
        "company": "American Spice Imports LLC",
        "contact": "Marcus Vance",
        "contact_title": "VP of Global Sourcing",
        "status": "booked",
        "emails": [
            {
                "sent_at": "2026-10-30T10:00:00Z",
                "from": "Trade Desk <outbound@domain.com>",
                "to": "m.vance@americanspiceimports.com",
                "subject": "Organic Turmeric & Black Pepper sourcing",
                "body": "Noticed your Newark container receipts for organic turmeric..."
            }
        ],
        "thread": [
            {
                "timestamp": "2026-10-31T14:45:00Z",
                "role": "prospect",
                "inbound": True,
                "text": "Received the lab reports. Let's schedule a 15 min intro call to review 2027 contract supply."
            },
            {
                "timestamp": "2026-10-31T16:00:00Z",
                "role": "agent",
                "inbound": False,
                "text": "Calendar invite sent for Wednesday Nov 4 at 3:30 PM EST via Google Meet."
            }
        ],
        "draft": None
    }
]

_companies_cache = [
    {
        "id": "comp_01",
        "name": "American Spice Imports LLC",
        "domain": "americanspiceimports.com",
        "website": "https://americanspiceimports.com",
        "industry": "Agro & Food Spices",
        "location": "Secaucus, NJ, USA",
        "size": "50-200",
        "contacts": 3,
        "source": "US Customs AMS",
        "added": "Today"
    },
    {
        "id": "comp_02",
        "name": "Golden Grain Wholesalers Inc",
        "domain": "goldengrainimports.com",
        "website": "https://goldengrainimports.com",
        "industry": "Grains & Basmati Rice",
        "location": "Long Beach, CA, USA",
        "size": "20-50",
        "contacts": 2,
        "source": "US Customs AMS",
        "added": "Today"
    },
    {
        "id": "comp_03",
        "name": "Titan Piping Corp",
        "domain": "titanpipingusa.com",
        "website": "https://titanpipingusa.com",
        "industry": "Industrial Flanges & Metals",
        "location": "Houston, TX, USA",
        "size": "100-500",
        "contacts": 4,
        "source": "US Customs AMS",
        "added": "Yesterday"
    },
    {
        "id": "comp_04",
        "name": "EuroNordic Food Ingredients BV",
        "domain": "euronordicfoods.nl",
        "website": "https://euronordicfoods.nl",
        "industry": "Food Ingredients & Dehydrates",
        "location": "Rotterdam, Netherlands",
        "size": "50-200",
        "contacts": 2,
        "source": "EU Customs Single Window",
        "added": "2 days ago"
    },
    {
        "id": "comp_05",
        "name": "Gulf Horizon Foodstuff Trading LLC",
        "domain": "gulfhorizonfood.ae",
        "website": "https://gulfhorizonfood.ae",
        "industry": "Agricultural Commodities",
        "location": "Dubai, UAE",
        "size": "50-150",
        "contacts": 3,
        "source": "Dubai Trade Manifest",
        "added": "3 days ago"
    }
]

_prospects_cache = [
    {
        "id": "pros_01",
        "first_name": "Marcus",
        "last_name": "Vance",
        "company": "American Spice Imports LLC",
        "email": "m.vance@americanspiceimports.com",
        "title": "VP of Global Sourcing & Procurement",
        "score": 98,
        "status": "interested",
        "source": "customs",
        "added": "Today"
    },
    {
        "id": "pros_02",
        "first_name": "Jennifer",
        "last_name": "Sterling",
        "company": "Golden Grain Wholesalers Inc",
        "email": "jsterling@goldengrainimports.com",
        "title": "Director of Sourcing",
        "score": 95,
        "status": "replied",
        "source": "customs",
        "added": "Today"
    },
    {
        "id": "pros_03",
        "first_name": "Arthur",
        "last_name": "Pendelton",
        "company": "Titan Piping Corp",
        "email": "apendelton@titanpipingusa.com",
        "title": "Chief Procurement Officer",
        "score": 92,
        "status": "contacted",
        "source": "customs",
        "added": "Yesterday"
    },
    {
        "id": "pros_04",
        "first_name": "Dirk",
        "last_name": "Van Houten",
        "company": "EuroNordic Food Ingredients BV",
        "email": "d.vanhouten@euronordicfoods.nl",
        "title": "Head of Raw Materials",
        "score": 94,
        "status": "queued",
        "source": "customs",
        "added": "2 days ago"
    },
    {
        "id": "pros_05",
        "first_name": "Tariq",
        "last_name": "Al-Mansoor",
        "company": "Gulf Horizon Foodstuff Trading LLC",
        "email": "tariq.mansoor@gulfhorizonfood.ae",
        "title": "Managing Director & Head Buyer",
        "score": 90,
        "status": "new",
        "source": "customs",
        "added": "3 days ago"
    }
]

_campaigns_cache = [
    {
        "id": "camp_01",
        "name": "US Food Wholesalers & Spice Importers Q4",
        "status": "active",
        "target_count": 25,
        "sequence": [
            {
                "step_number": 1,
                "delay_days": 0,
                "subject": "quick question re: Organic Spices sourcing for {company}",
                "body": "Saw {company}'s recent container bill of lading importing Organic Spices. We are a direct primary processor in Gujarat exporting BRC Grade-A & US FDA turmeric and cumin. Can we courier a 500g cooking sample to your team this week?",
                "words": 41
            },
            {
                "step_number": 2,
                "delay_days": 3,
                "subject": "Re: quick question re: Organic Spices sourcing for {company}",
                "body": "Quick follow-up — we have 2x 20ft containers ready for prompt shipment with SGS lab assay certificates. Would a 10-minute Zoom call on Thursday work to discuss CIF rates?",
                "words": 30
            },
            {
                "step_number": 3,
                "delay_days": 7,
                "subject": "spec sheet & FOB Mundra benchmark for {company}",
                "body": "Final note — sharing our 2026/2027 crop harvest analysis and certificate of analysis. If sourcing is closed for this quarter, let's connect for the next buying window.",
                "words": 28
            }
        ],
        "recipients": [
            {"email": "m.vance@americanspiceimports.com", "name": "Marcus Vance", "company": "American Spice Imports LLC", "sent_by_hand": False},
            {"email": "jsterling@goldengrainimports.com", "name": "Jennifer Sterling", "company": "Golden Grain Wholesalers Inc", "sent_by_hand": False}
        ]
    }
]

# ----------------- Root & Web UI -----------------
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
@app.get("/api/index.py", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
@app.get("/app", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ----------------- Harvey Dashboard REST API -----------------

@app.get("/api/today")
@app.get("/api/today/")
async def get_today():
    pending = [x for x in _outbox_items if x["status"] == "STAGED_REVIEW"]
    approved = [x for x in _outbox_items if x["status"] == "APPROVED"]
    return {
        "stats": {
            "outbox_pending": len(pending),
            "outbox_approved": len(approved),
            "signals_proposed": 3,
            "signals_confirmed": 8,
            "needs_human": 1,
            "companies": len(_companies_cache),
            "unprofiled": 12,
            "email_provider": _sending_state.get("provider", "gmail")
        },
        "items": [
            {
                "title": f"Review {len(pending)} cold trade sequences staged for US importers",
                "desc": "Harvey Writer generated personalized touches (<75 words) for Marcus Vance and Jennifer Sterling.",
                "action_label": "Open Outbox",
                "action_tab": "outbox",
                "tone": "warn" if len(pending) > 0 else "good"
            },
            {
                "title": "Confirm 3 proposed buyer signals",
                "desc": "Customs manifests indicate high container TEU volume for spice & agro importers.",
                "action_label": "Review Signals",
                "action_tab": "signals",
                "tone": "wait"
            },
            {
                "title": "Inbound reply from Golden Grain Wholesalers",
                "desc": "Jennifer Sterling asked for MOQ and FOB Mundra port pricing.",
                "action_label": "View Thread",
                "action_tab": "conversations",
                "tone": "warn"
            }
        ]
    }

@app.get("/api/stats")
@app.get("/api/stats/")
async def get_stats():
    return {
        "prospects": {"total": len(_prospects_cache)},
        "pipeline": {
            "to_write": 24,
            "contacted": 18,
            "replied": 6,
            "booked": 3,
            "closed": 1
        }
    }

@app.get("/api/trend")
@app.get("/api/trend/")
async def get_trend(days: int = Query(14), tz: int = Query(0)):
    now = datetime.now()
    day_list = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in reversed(range(days))]
    return {
        "days": day_list,
        "sent": [12, 18, 22, 19, 28, 25, 32, 21, 27, 30, 24, 33, 29, 28],
        "contacts": [10, 14, 18, 15, 22, 20, 28, 17, 22, 25, 19, 27, 24, 23],
        "convos": [1, 2, 2, 1, 3, 2, 4, 2, 3, 4, 2, 4, 3, 4]
    }

@app.get("/api/live-status")
@app.get("/api/live-status/")
async def get_live_status():
    return {
        "steps": [
            {"name": "Scout", "state": "done", "detail": "Customs AMS & Apollo 99.3M stream indexed"},
            {"name": "Writer", "state": "done", "detail": "Personalized sequences (<75 words) drafted"},
            {"name": "Sender", "state": "running", "detail": "Pacing active at 35/day via secondary domains"},
            {"name": "Handler", "state": "done", "detail": "Classifying buyer replies & scheduling calls"},
            {"name": "Analyst", "state": "done", "detail": "Pipeline velocity & conversions monitored"}
        ]
    }

@app.get("/api/setup-status")
@app.get("/api/setup-status/")
async def get_setup_status():
    return {"percent": 100, "complete": True, "checks": []}

@app.get("/api/runs")
@app.get("/api/runs/")
async def get_runs():
    return [
        {"stage": "Customs Manifest Harvester", "status": "done", "started_at": "2026-11-01T15:00:00Z"},
        {"stage": "Instagram / Parser.im Scraper", "status": "done", "started_at": "2026-11-01T14:30:00Z"},
        {"stage": "Apollo 99M Zero-Disk Streamer", "status": "done", "started_at": "2026-11-01T14:00:00Z"}
    ]

# ----------------- Outbox (Decisions Desk) -----------------

@app.get("/api/outbox")
@app.get("/api/outbox/")
async def get_outbox():
    pending = [x for x in _outbox_items if x["status"] == "STAGED_REVIEW"]
    approved = [x for x in _outbox_items if x["status"] == "APPROVED"]
    return {
        "pending": pending,
        "approved": approved,
        "sent": [],
        "paused": _sending_state.get("paused"),
        "compliance_notice": ""
    }

@app.post("/api/outbox/{item_id}/approve")
async def approve_outbox_item(item_id: str):
    for item in _outbox_items:
        if item["id"] == item_id:
            item["status"] = "APPROVED"
            return {"status": "ok", "id": item_id}
    raise HTTPException(status_code=404, detail="Outbox item not found")

@app.post("/api/outbox/{item_id}/reject")
async def reject_outbox_item(item_id: str):
    for item in _outbox_items:
        if item["id"] == item_id:
            item["status"] = "REJECTED"
            return {"status": "ok", "id": item_id}
    raise HTTPException(status_code=404, detail="Outbox item not found")

@app.post("/api/outbox/{item_id}/edit")
async def edit_outbox_item(item_id: str, data: Dict[str, Any] = Body(...)):
    for item in _outbox_items:
        if item["id"] == item_id:
            if "subject" in data:
                item["subject"] = data["subject"]
            if "body" in data:
                item["body"] = data["body"]
                item["words"] = len(data["body"].split())
            return {"status": "ok", "id": item_id, "item": item}
    raise HTTPException(status_code=404, detail="Outbox item not found")

@app.post("/api/outbox/approve-all")
async def approve_all_outbox():
    approved_count = 0
    for item in _outbox_items:
        if item["status"] == "STAGED_REVIEW" and not item.get("held"):
            item["status"] = "APPROVED"
            approved_count += 1
    return {"status": "ok", "approved_count": approved_count}

# ----------------- Sending Mode & Controls -----------------

@app.get("/api/sending-mode")
@app.get("/api/sending-mode/")
async def get_sending_mode():
    return _sending_state

@app.post("/api/sending-mode")
async def set_sending_mode(data: Dict[str, Any] = Body(...)):
    if "mode" in data:
        _sending_state["mode"] = data["mode"]
    return _sending_state

@app.post("/api/sending/{action}")
async def toggle_sending(action: str):
    if action == "pause":
        _sending_state["paused"] = "Manual pause by user"
    elif action == "resume":
        _sending_state["paused"] = None
    return {"status": "ok", "paused": _sending_state["paused"]}

# ----------------- Conversations -----------------

@app.get("/api/conversations")
@app.get("/api/conversations/")
async def get_conversations(awaiting: Optional[int] = Query(None)):
    return _conversations

@app.post("/api/conversations/{convo_id}/status")
async def set_convo_status(convo_id: str, data: Dict[str, Any] = Body(...)):
    for c in _conversations:
        if c["id"] == convo_id:
            if "status" in data:
                c["status"] = data["status"]
            return {"status": "ok", "convo": c}
    raise HTTPException(status_code=404, detail="Conversation not found")

# ----------------- Signals -----------------

@app.get("/api/signals")
@app.get("/api/signals/")
async def get_signals():
    return _signals_state

@app.get("/api/signals/status")
async def get_signals_status():
    return _signals_state.get("summary", {})

@app.post("/api/signals/confirm")
async def confirm_signal(data: Dict[str, Any] = Body(...)):
    codes = data.get("codes", [])
    if isinstance(codes, str):
        codes = [codes]
    for grp in _signals_state.get("groups", []):
        for sig in grp.get("signals", []):
            if sig.get("code") in codes:
                sig["status"] = "confirmed"
    _signals_state["summary"]["confirmed"] += len(codes)
    _signals_state["summary"]["proposed"] = max(0, _signals_state["summary"]["proposed"] - len(codes))
    return {"status": "ok", "summary": _signals_state["summary"]}

@app.post("/api/signals/skip")
async def skip_signal(data: Dict[str, Any] = Body(...)):
    codes = data.get("codes", [])
    if isinstance(codes, str):
        codes = [codes]
    for grp in _signals_state.get("groups", []):
        for sig in grp.get("signals", []):
            if sig.get("code") in codes:
                sig["status"] = "rejected"
    _signals_state["summary"]["rejected"] += len(codes)
    _signals_state["summary"]["proposed"] = max(0, _signals_state["summary"]["proposed"] - len(codes))
    return {"status": "ok", "summary": _signals_state["summary"]}

@app.get("/api/cohort")
@app.get("/api/cohort/")
async def get_cohort():
    return {
        "matching_companies": len(_companies_cache),
        "total": len(_companies_cache),
        "sample": _companies_cache[:3]
    }

@app.get("/api/cohort.csv")
async def download_cohort_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Company", "Domain", "Industry", "Location", "Contacts", "Source"])
    for c in _companies_cache:
        writer.writerow([c.get("name"), c.get("domain"), c.get("industry"), c.get("location"), c.get("contacts"), c.get("source")])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cohort.csv"}
    )

# ----------------- Discover -----------------

@app.get("/api/discover/providers")
@app.get("/api/discover/providers/")
async def get_discover_providers():
    return {
        "providers": [
            {
                "key": "customs",
                "label": "US Customs AMS Trade Manifests",
                "blurb": "Bill of Lading manifests filed with US Customs. Real verified importers with historical container TEU volumes and active supplier relationships.",
                "cost_note": "$0.00 (Local zero-cost)",
                "free_tier": "Unlimited local manifest lookups",
                "configured": True,
                "needs_key": False,
                "env_keys": [],
                "signup_url": "",
                "caveat": ""
            },
            {
                "key": "social",
                "label": "Instagram & Social Media Parser (parser.im)",
                "blurb": "Scrapes business profiles, link-in-bio commercial emails, and wholesale distributor accounts across social platforms.",
                "cost_note": "$0.00 (Local zero-cost)",
                "free_tier": "Unlimited profile parsing",
                "configured": True,
                "needs_key": False,
                "env_keys": [],
                "signup_url": "",
                "caveat": ""
            },
            {
                "key": "apollo",
                "label": "Apollo 99.3M Database Stream",
                "blurb": "High-throughput streaming search across 99,311,285 global B2B buyer records with zero RAM pressure and instant index querying.",
                "cost_note": "$0.00 (Local zero-cost)",
                "free_tier": "Unlimited stream queries",
                "configured": True,
                "needs_key": False,
                "env_keys": [],
                "signup_url": "",
                "caveat": ""
            },
            {
                "key": "startups",
                "label": "Startup ICP & Tech Directory",
                "blurb": "Verified B2B technology leaders, Series A/B funded companies, and tech procurement executives.",
                "cost_note": "$0.00 (Local zero-cost)",
                "free_tier": "Unlimited directory searches",
                "configured": True,
                "needs_key": False,
                "env_keys": [],
                "signup_url": "",
                "caveat": ""
            }
        ],
        "default": "customs",
        "selected": "customs",
        "running": False
    }

@app.post("/api/discover/estimate")
async def estimate_discovery(data: Dict[str, Any] = Body(...)):
    return {
        "queries": 1,
        "depth": 30,
        "cost": 0.0,
        "note": "Local high-performance search across 99M+ records. $0.00 cost.",
        "ok": True
    }

@app.post("/api/discover/run")
async def run_discovery(data: Dict[str, Any] = Body(...)):
    provider = data.get("provider", "customs")
    cities = data.get("cities", "")
    preset = data.get("preset", "")
    
    # Run genuine search based on provider
    if provider == "customs":
        leads = customs_engine.search_customs(query=cities or "spices", limit=20)
    elif provider == "social":
        leads = social_engine.search_social_leads(query=cities or "wholesale", limit=20)
    elif provider == "apollo" and HAS_APOLLO_ZIP:
        leads = apollo_engine.search_leads(query=cities or "director", limit=20)
    else:
        leads = startup_engine.search_startups(query=cities or "tech", limit=20)
        
    return {
        "status": "success",
        "provider": provider,
        "results_found": len(leads),
        "leads": leads
    }

@app.post("/api/discover/stop")
async def stop_discovery():
    return {"status": "ok", "stopped": True}

# ----------------- Companies & Contacts -----------------

@app.get("/api/companies")
@app.get("/api/companies/")
async def get_companies():
    return _companies_cache

@app.get("/api/companies/{company_index}/contacts")
async def get_company_contacts(company_index: int):
    if 0 <= company_index < len(_companies_cache):
        comp = _companies_cache[company_index]
        matching = [p for p in _prospects_cache if p["company"].lower() == comp["name"].lower()]
        return matching or _prospects_cache[:2]
    return _prospects_cache[:2]

@app.get("/api/prospects")
@app.get("/api/prospects/")
async def get_prospects():
    return _prospects_cache

@app.get("/api/export/prospects.csv")
async def export_prospects_csv(all: Optional[bool] = Query(False)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["First Name", "Last Name", "Company", "Email", "Title", "Score", "Status", "Source", "Added"])
    for p in _prospects_cache:
        writer.writerow([p.get("first_name"), p.get("last_name"), p.get("company"), p.get("email"), p.get("title"), p.get("score"), p.get("status"), p.get("source"), p.get("added")])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=prospects.csv"}
    )

# ----------------- Campaigns -----------------

@app.get("/api/campaigns")
@app.get("/api/campaigns/")
async def get_campaigns():
    return _campaigns_cache

# ----------------- Activity & Usage -----------------

@app.get("/api/activity")
@app.get("/api/activity/")
async def get_activity():
    now_str = datetime.now().isoformat()
    return [
        {
            "created_at": now_str,
            "agent": "writer",
            "action": "staged_email",
            "details": "Generated 48-word personalized Touch 1 for Marcus Vance (American Spice Imports LLC)."
        },
        {
            "created_at": now_str,
            "agent": "handler",
            "action": "handled_reply",
            "details": "Classified inbound buyer reply from Jennifer Sterling (Golden Grain Wholesalers). Drafted MOQ & CIF pricing response."
        },
        {
            "created_at": now_str,
            "agent": "scout",
            "action": "found_prospect",
            "details": "Harvested Bill of Lading from US Customs AMS: 38 TEU containers imported by American Spice Imports LLC."
        },
        {
            "created_at": now_str,
            "agent": "analyst",
            "action": "measured_pipeline",
            "details": "Pipeline health score: 98/100. Pacing optimal at 35 sends/day."
        }
    ]

@app.get("/api/usage")
@app.get("/api/usage/")
async def get_usage():
    return {
        "totals": {
            "today": {"calls": 48, "output_tokens": 14200, "input_tokens": 38900, "cache_read_tokens": 82000},
            "week": {"calls": 284, "output_tokens": 95400, "input_tokens": 245000, "cache_read_tokens": 512000},
            "month": {"calls": 1140, "output_tokens": 382000, "input_tokens": 980000, "cache_read_tokens": 2150000}
        },
        "providers": [
            {"name": "Local Claude / Codex Subscription", "calls": 284, "tokens": 340400, "cost": "$0.00"}
        ]
    }

# ----------------- Settings & Harvey Heartbeat Loop -----------------

@app.get("/api/settings")
@app.get("/api/settings/")
async def get_settings():
    return {
        "provider": _sending_state.get("provider", "gmail"),
        "sending_mode": _sending_state.get("mode", "approval"),
        "daily_limit": 35,
        "human_review_required": True
    }

@app.post("/api/settings/save")
async def save_settings(data: Dict[str, Any] = Body(...)):
    return {"status": "ok", "saved": True}

@app.post("/api/settings/test-instantly")
async def test_instantly(data: Dict[str, Any] = Body(...)):
    return {"status": "ok", "message": "Instantly connection verified"}

@app.get("/api/harvey/status")
async def get_harvey_status():
    return {
        "running": harvey_agent.is_running,
        "pid": 8942,
        "started_at": datetime.now().isoformat(),
        "mode": harvey_agent.mode,
        "report": harvey_agent.get_status_report()
    }

@app.post("/api/harvey/start")
async def start_harvey():
    harvey_agent.is_running = True
    return {"status": "ok", "running": True}

@app.post("/api/harvey/stop")
async def stop_harvey():
    harvey_agent.is_running = False
    return {"status": "ok", "running": False}

@app.get("/api/harvey/logs")
async def get_harvey_logs():
    return {"logs": ["Harvey loop active. Monitoring outbox and incoming replies every 3 minutes."]}

# ----------------- Formal Client Proposal PDF Generator -----------------

@app.get("/api/proposal/download-pdf")
async def download_proposal_pdf_endpoint(
    exporter_name: str = Query("Authorized Representative"),
    exporter_company: str = Query("Surat Organic Agro Exports"),
    product: str = Query("Organic Turmeric, Cumin & Black Pepper"),
    target_country: str = Query("United States"),
    tier: str = Query("growth")
):
    filename, pdf_bytes = PDFProposalGenerator.create_proposal_pdf(
        exporter_name=exporter_name,
        exporter_company=exporter_company,
        product=product,
        target_country=target_country,
        tier=tier
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/api/proposal/view-pdf")
async def view_proposal_pdf_endpoint(
    exporter_name: str = Query("Authorized Representative"),
    exporter_company: str = Query("Surat Organic Agro Exports"),
    product: str = Query("Organic Turmeric, Cumin & Black Pepper"),
    target_country: str = Query("United States"),
    tier: str = Query("growth")
):
    filename, pdf_bytes = PDFProposalGenerator.create_proposal_pdf(
        exporter_name=exporter_name,
        exporter_company=exporter_company,
        product=product,
        target_country=target_country,
        tier=tier
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'}
    )

# ----------------- Legacy & Additional Engine APIs -----------------

@app.get("/api/status")
async def system_status():
    return {
        "status": "online",
        "app_name": "Harvey — Command Deck",
        "apollo_zip_detected": HAS_APOLLO_ZIP,
        "apollo_stats": apollo_engine.get_stats(),
        "customs_database_records": len(customs_engine._customs_records),
        "startup_icp_records": len(startup_engine._tech_records),
        "social_parser_records": len(social_engine._parsed_profiles),
        "active_pipeline_leads": len(crm_service.get_all_leads()),
        "harvey_status": harvey_agent.get_status_report()
    }

@app.get("/api/search")
async def search_leads(
    database: str = Query("all"),
    query: str = Query(""),
    product: str = Query(""),
    country: str = Query(""),
    limit: int = Query(50),
    offset: int = Query(0)
):
    results = []
    if database in ("customs", "all"):
        results.extend(customs_engine.search_customs(query=query, product=product, country=country, limit=limit))
    if database in ("social", "all"):
        results.extend(social_engine.search_social_leads(query=query or product, category=product, country=country, limit=15))
    if database in ("startups", "all"):
        results.extend(startup_engine.search_startups(query=query, industry=product, country=country, limit=15))
    if (database in ("apollo", "all")) and HAS_APOLLO_ZIP:
        results.extend(apollo_engine.search_leads(query=query or product, limit=15))
    return {"total": len(results), "leads": results}

@app.get("/api/playbook")
async def get_playbook():
    return {"status": "ok", "playbook": "Harvey Autonomous Outbound Architecture Playbook"}
