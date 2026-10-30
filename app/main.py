import os
from pathlib import Path
from fastapi import FastAPI, Request, Query, Body, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.config import APP_NAME, APP_DESCRIPTION, HAS_APOLLO_ZIP, APOLLO_ZIP_FILENAME, APOLLO_ZIP_PATH
from app.data_engines.apollo_streamer import ApolloStreamEngine
from app.data_engines.customs_engine import CustomsTradeEngine
from app.data_engines.startup_icp_engine import StartupICPEngine
from app.services.verifier import WaterfallEmailVerifier
from app.services.ai_generator import AIEmailGenerator
from app.services.deliverability import DeliverabilityService
from app.services.crm import CRMService

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# Initialize engines
apollo_engine = ApolloStreamEngine()
customs_engine = CustomsTradeEngine()
startup_engine = StartupICPEngine()
crm_service = CRMService()

# ----------------- Models -----------------
class VerifyRequest(BaseModel):
    email: str

class GenerateSequenceRequest(BaseModel):
    prospect_name: str
    prospect_title: str
    prospect_company: str
    prospect_country: Optional[str] = "United States"
    product_category: Optional[str] = "Spices & Agro"
    client_company: Optional[str] = "Surat Organic Agro Exports"
    client_name: Optional[str] = "Rajesh Patel"
    client_title: Optional[str] = "Head of International Trade"
    certifications: Optional[str] = "BRC, FDA, USDA Organic"

class AddLeadRequest(BaseModel):
    name: str
    email: str
    title: Optional[str] = ""
    company: Optional[str] = ""
    country: Optional[str] = "United States"
    product: Optional[str] = "Export Commodities"
    notes: Optional[str] = ""

class UpdateStageRequest(BaseModel):
    lead_id: str
    stage: str

class TriageReplyRequest(BaseModel):
    reply_text: str

# ----------------- Web UI -----------------
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    apollo_stats = apollo_engine.get_stats()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": APP_NAME,
            "has_apollo_zip": HAS_APOLLO_ZIP,
            "apollo_stats": apollo_stats
        }
    )

# ----------------- API Endpoints -----------------
@app.get("/api/status")
async def system_status():
    return {
        "status": "online",
        "app_name": APP_NAME,
        "apollo_zip_detected": HAS_APOLLO_ZIP,
        "apollo_stats": apollo_engine.get_stats(),
        "customs_database_records": len(customs_engine._customs_records),
        "startup_icp_records": len(startup_engine._tech_records),
        "active_pipeline_leads": len(crm_service.get_all_leads())
    }

@app.get("/api/search")
async def search_leads(
    database: str = Query("all", description="Source: all, customs, apollo, startups"),
    query: str = Query("", description="Keyword search"),
    product: str = Query("", description="Product or category (e.g. Spices, Rice, Flanges)"),
    country: str = Query("", description="Country e.g. United States, Germany"),
    limit: int = Query(25, ge=1, le=100)
):
    results = []
    
    # 1. Customs Data (Best for Indian Exporters)
    if database in ["all", "customs"]:
        customs_leads = customs_engine.search_customs(query=query, product=product, country=country, limit=limit)
        results.extend(customs_leads)

    # 2. Apollo Streaming Engine (Zero disk extraction)
    remaining = limit - len(results)
    if database == "apollo" or (database == "all" and remaining > 0 and HAS_APOLLO_ZIP):
        apollo_leads = apollo_engine.search_leads(
            query=query or product,
            country=country,
            limit=limit if database == "apollo" else min(remaining, 10)
        )
        results.extend(apollo_leads)

    # 3. Startup ICP Engine
    remaining = limit - len(results)
    if database == "startups" or (database == "all" and remaining > 0):
        startup_leads = startup_engine.search_startups(
            query=query,
            industry=product,
            limit=limit if database == "startups" else min(remaining, 10)
        )
        results.extend(startup_leads)

    return {
        "total": len(results),
        "database_selected": database,
        "leads": results[:limit]
    }

@app.post("/api/verify")
async def verify_email(req: VerifyRequest):
    result = WaterfallEmailVerifier.verify(req.email)
    return result

@app.post("/api/generate-sequence")
async def generate_cold_sequence(req: GenerateSequenceRequest):
    result = AIEmailGenerator.generate_sequence(
        prospect_name=req.prospect_name,
        prospect_title=req.prospect_title,
        prospect_company=req.prospect_company,
        prospect_country=req.prospect_country or "United States",
        product_category=req.product_category or "Spices & Agro",
        client_company=req.client_company or "Surat Organic Agro Exports",
        client_name=req.client_name or "Rajesh Patel",
        client_title=req.client_title or "Head of International Trade",
        certifications=req.certifications or "BRC, FDA, USDA Organic"
    )
    return result

@app.get("/api/deliverability/dns")
async def get_dns_records(domain: str = Query("example-exports.com")):
    return DeliverabilityService.generate_dns_records(domain)

@app.get("/api/deliverability/warmup")
async def get_warmup_schedule(target_daily: int = Query(100, ge=10, le=1000)):
    return DeliverabilityService.calculate_warmup_schedule(target_daily)

@app.get("/api/deliverability/capacity")
async def get_inbox_capacity(target_monthly: int = Query(3000, ge=500, le=50000)):
    return DeliverabilityService.calculate_inbox_capacity(target_monthly)

@app.get("/api/crm/leads")
async def get_crm_leads():
    leads = crm_service.get_all_leads()
    metrics = {
        "total": len(leads),
        "verified": sum(1 for l in leads if l["stage"] == "verified"),
        "outreached": sum(1 for l in leads if l["stage"] == "outreached"),
        "replied": sum(1 for l in leads if l["stage"] == "replied"),
        "call_booked": sum(1 for l in leads if l["stage"] == "call_booked")
    }
    return {"metrics": metrics, "leads": leads}

@app.post("/api/crm/lead")
async def add_crm_lead(req: AddLeadRequest):
    new_lead = crm_service.add_lead(req.dict())
    return {"status": "success", "lead": new_lead}

@app.post("/api/crm/update-stage")
async def update_crm_stage(req: UpdateStageRequest):
    success = crm_service.update_lead_stage(req.lead_id, req.stage)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "success"}

@app.post("/api/crm/triage-reply")
async def triage_incoming_reply(req: TriageReplyRequest):
    result = crm_service.classify_email_reply(req.reply_text)
    return result

@app.get("/api/crm/export-csv")
async def export_crm_csv():
    csv_data = crm_service.export_csv_smartlead()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=eximflow_smartlead_leads.csv"}
    )

@app.get("/api/playbook")
async def get_playbook_markdown():
    playbook_path = BASE_DIR / "STARTUP_MASTER_PLAYBOOK.md"
    if playbook_path.exists():
        return PlainTextResponse(playbook_path.read_text(encoding="utf-8"))
    return PlainTextResponse("# Playbook not found")
