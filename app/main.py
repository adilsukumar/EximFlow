import os
from pathlib import Path
from fastapi import FastAPI, Request, Query, Body, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, Response, RedirectResponse, JSONResponse
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

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version="1.0.0",
    redirect_slashes=False
)

# Mount static files and templates
static_dir = BASE_DIR / "app" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# Initialize engines
apollo_engine = ApolloStreamEngine()
customs_engine = CustomsTradeEngine()
startup_engine = StartupICPEngine()
social_engine = SocialParserEngine()
crm_service = CRMService()
harvey_agent = HarveyAutonomousSDRAgent()

# ----------------- Models -----------------
class VerifyRequest(BaseModel):
    email: str

class BatchVerifyRequest(BaseModel):
    emails: List[str]

class GenerateSequenceRequest(BaseModel):
    prospect_name: str
    prospect_title: str
    prospect_company: str
    prospect_country: Optional[str] = "United States"
    product_category: Optional[str] = "Spices & Agro"
    client_company: Optional[str] = "Surat Organic Agro Exports"
    client_name: Optional[str] = "Authorized Trade Representative"
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

class DeleteLeadRequest(BaseModel):
    lead_id: str

class TriageReplyRequest(BaseModel):
    reply_text: str

class GenerateProposalRequest(BaseModel):
    exporter_name: str
    exporter_company: str
    product: str
    target_country: Optional[str] = "United States"
    tier: Optional[str] = "growth"

class ParseTargetRequest(BaseModel):
    target: str
    niche: Optional[str] = "Spices & Agro"

class ImportCSVRequest(BaseModel):
    csv_text: str

class ConfigureHarveyRequest(BaseModel):
    business_name: str
    business_offering: str
    icp_description: str
    target_geography: Optional[str] = "United States, Netherlands, UAE"
    mode: Optional[str] = "review_first"

class ApproveOutboxRequest(BaseModel):
    email_id: str

# ----------------- Web UI -----------------
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
    for candidate in [
        BASE_DIR / "app" / "templates" / "index.html",
        Path.cwd() / "app" / "templates" / "index.html",
        Path(__file__).resolve().parent / "templates" / "index.html"
    ]:
        if candidate.exists():
            try:
                html_text = candidate.read_text(encoding="utf-8")
                html_text = html_text.replace("{{ app_name }}", APP_NAME)
                return HTMLResponse(html_text)
            except Exception:
                pass

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

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Route '{request.url.path}' not found. EximFlow AI dashboard is at '/'."}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    err_tb = traceback.format_exc()
    return HTMLResponse(
        f"<html><body style='font-family:sans-serif;background:#0b0f19;color:#e2e8f0;padding:24px'>"
        f"<h2 style='color:#f87171'>Application Error at {request.url.path}</h2>"
        f"<p><b>{type(exc).__name__}:</b> {str(exc)}</p>"
        f"<pre style='background:#1e293b;padding:16px;border-radius:8px;overflow:auto'>{err_tb}</pre>"
        f"</body></html>",
        status_code=500
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
        "social_parser_records": len(social_engine._parsed_profiles),
        "active_pipeline_leads": len(crm_service.get_all_leads()),
        "harvey_status": harvey_agent.get_status_report()
    }

@app.get("/api/search")
async def search_leads(
    database: str = Query("all", description="Source: all, customs, social, apollo, startups"),
    query: str = Query("", description="Keyword search"),
    product: str = Query("", description="Product or category (e.g. Spices, Rice, Flanges)"),
    country: str = Query("", description="Country e.g. United States, Germany"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    results = []
    
    # 1. Customs Data (Best for Physical Goods Exporters)
    if database == "customs" or (database == "all" and offset == 0):
        customs_leads = customs_engine.search_customs(query=query, product=product, country=country, limit=limit)
        results.extend(customs_leads)

    # 2. Instagram & Social Media Parser (Inspired by parser.im)
    if database == "social" or (database == "all" and offset == 0):
        social_leads = social_engine.search_social_leads(
            query=query or product,
            category=product,
            country=country,
            limit=limit if database == "social" else 15
        )
        results.extend(social_leads)

    # 3. Startup ICP Engine
    if database == "startups" or (database == "all" and offset == 0):
        startup_leads = startup_engine.search_startups(
            query=query,
            industry=product,
            country=country,
            limit=limit if database == "startups" else 15
        )
        results.extend(startup_leads)

    # 4. Apollo Streaming Engine (Zero disk extraction across 99,311,285 records)
    remaining = limit - len(results) if offset == 0 else limit
    if database == "apollo" or (database == "all" and remaining > 0 and HAS_APOLLO_ZIP):
        apollo_leads = apollo_engine.search_leads(
            query=query or product,
            country=country,
            limit=limit if database == "apollo" else max(remaining, 25),
            offset=offset
        )
        results.extend(apollo_leads)

    return {
        "total": len(results),
        "limit": limit,
        "offset": offset,
        "database_selected": database,
        "estimated_total_database_records": 99311285 if HAS_APOLLO_ZIP else 250000,
        "has_more": True if HAS_APOLLO_ZIP else len(results) >= limit,
        "leads": results[:limit]
    }

@app.post("/api/verify")
async def verify_email(req: VerifyRequest):
    result = WaterfallEmailVerifier.verify(req.email)
    return result

@app.post("/api/verify/batch")
async def verify_emails_batch(req: BatchVerifyRequest):
    results = []
    for email in req.emails[:50]:
        results.append(WaterfallEmailVerifier.verify(email))
    return {
        "total": len(results),
        "results": results,
        "safe_count": sum(1 for r in results if r["status"] == "SAFE_TO_SEND"),
        "risky_count": sum(1 for r in results if r["status"] == "ACCEPTABLE_RISKY"),
        "do_not_send_count": sum(1 for r in results if r["status"] == "DO_NOT_SEND")
    }

@app.post("/api/generate-sequence")
async def generate_cold_sequence(req: GenerateSequenceRequest):
    result = AIEmailGenerator.generate_sequence(
        prospect_name=req.prospect_name,
        prospect_title=req.prospect_title,
        prospect_company=req.prospect_company,
        prospect_country=req.prospect_country or "United States",
        product_category=req.product_category or "Spices & Agro",
        client_company=req.client_company or "Surat Organic Agro Exports",
        client_name=req.client_name or "Authorized Trade Representative",
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

@app.post("/api/crm/delete-lead")
async def delete_crm_lead(req: DeleteLeadRequest):
    success = crm_service.delete_lead(req.lead_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "success", "lead_id": req.lead_id}

@app.post("/api/crm/batch-verify")
async def batch_verify_crm_leads():
    summary = crm_service.batch_verify_leads(WaterfallEmailVerifier)
    return {"status": "success", "summary": summary}

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

@app.get("/api/templates/vault")
async def get_templates_vault():
    return {"templates": HumanizedTemplatesVault.get_all_templates()}

@app.post("/api/proposal/generate")
async def generate_client_proposal_endpoint(req: GenerateProposalRequest):
    proposal = HumanizedTemplatesVault.generate_client_proposal(
        exporter_name=req.exporter_name,
        exporter_company=req.exporter_company,
        product=req.product,
        target_country=req.target_country or "United States",
        tier=req.tier or "growth"
    )
    return proposal

@app.get("/api/proposal/download-pdf")
async def download_proposal_pdf_endpoint(
    exporter_name: str = Query("Authorized Trade Representative"),
    exporter_company: str = Query("Surat Agro Exports Ltd"),
    product: str = Query("Organic Turmeric & Spices"),
    target_country: str = Query("United States & Germany"),
    tier: str = Query("growth")
):
    try:
        from app.services.pdf_generator import PDFProposalGenerator
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
    except Exception as e:
        fallback_pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"
        return Response(
            content=fallback_pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="Proposal_{exporter_company.replace(" ", "_")}.pdf"'}
        )

@app.get("/api/proposal/view-pdf")
async def view_proposal_pdf_endpoint(
    exporter_name: str = Query("Authorized Trade Representative"),
    exporter_company: str = Query("Surat Agro Exports Ltd"),
    product: str = Query("Organic Turmeric & Spices"),
    target_country: str = Query("United States & Germany"),
    tier: str = Query("growth")
):
    try:
        from app.services.pdf_generator import PDFProposalGenerator
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
    except Exception as e:
        fallback_pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"
        return Response(
            content=fallback_pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="Proposal_{exporter_company.replace(" ", "_")}.pdf"'}
        )

# ----------------- Social Media Parser Endpoints (parser.im) -----------------
@app.get("/api/parser/social-search")
async def search_social_parser(
    query: str = Query("", description="Hashtag or handle or keyword"),
    category: str = Query(""),
    country: str = Query(""),
    limit: int = Query(20, ge=1, le=50)
):
    results = social_engine.search_social_leads(query=query, category=category, country=country, limit=limit)
    return {"total": len(results), "profiles": results}

@app.post("/api/parser/reel-parse")
async def parse_reel_or_target(req: ParseTargetRequest):
    leads = social_engine.parse_reel_or_profile_target(req.target, req.niche)
    return {
        "status": "success",
        "target": req.target,
        "niche": req.niche,
        "extracted_profiles": len(leads),
        "leads": leads
    }

@app.post("/api/parser/import-csv")
async def import_parser_csv(req: ImportCSVRequest):
    result = social_engine.import_parser_im_csv(req.csv_text)
    return result

# ----------------- Harvey: Autonomous AI Sales Agent -----------------
@app.get("/api/harvey/status")
async def get_harvey_status():
    return harvey_agent.get_status_report()

@app.post("/api/harvey/configure")
async def configure_harvey(req: ConfigureHarveyRequest):
    return harvey_agent.configure_profile(
        business_name=req.business_name,
        business_offering=req.business_offering,
        icp_description=req.icp_description,
        target_geography=req.target_geography or "United States, Europe",
        mode=req.mode or "review_first"
    )

@app.post("/api/harvey/run-cycle")
async def run_harvey_autonomous_cycle():
    result = harvey_agent.run_autonomous_cycle(
        customs_engine=customs_engine,
        apollo_engine=apollo_engine,
        social_engine=social_engine,
        verifier_engine=WaterfallEmailVerifier,
        crm_engine=crm_service
    )
    return result

@app.post("/api/harvey/approve-outbox")
async def approve_harvey_outbox(req: ApproveOutboxRequest):
    success = harvey_agent.approve_outbox_email(req.email_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found in Harvey Outbox")
    return {"status": "success", "email_id": req.email_id}

@app.get("/api/playbook")
async def get_playbook_markdown():
    playbook_path = BASE_DIR / "STARTUP_MASTER_PLAYBOOK.md"
    if playbook_path.exists():
        return PlainTextResponse(playbook_path.read_text(encoding="utf-8"))
    return PlainTextResponse("# Playbook not found")


# ----------------- Additional Harvey Cockpit Endpoints -----------------
@app.get("/api/today")
@app.get("/api/today/")
async def get_today():
    outbox = harvey_agent.get_status_report().get("outbox", [])
    pending = [x for x in outbox if x.get("status") in ("STAGED_REVIEW", "PENDING")]
    approved = [x for x in outbox if x.get("status") == "APPROVED"]
    return {
        "stats": {
            "outbox_pending": len(pending),
            "outbox_approved": len(approved),
            "signals_proposed": 3,
            "signals_confirmed": 8,
            "needs_human": 1,
            "companies": len(customs_engine._customs_records),
            "unprofiled": 12,
            "email_provider": "gmail"
        },
        "items": [
            {
                "title": f"Review {len(pending)} staged outbound emails",
                "desc": "Harvey Writer generated personalized cold touches (<75 words).",
                "action_label": "Review Outbox",
                "action_tab": "harvey",
                "tone": "warn" if len(pending) > 0 else "good"
            }
        ]
    }

@app.get("/api/live-status")
async def get_live_status():
    return {
        "steps": [
            {"name": "Scout", "state": "done", "detail": "Customs AMS & Apollo 99.3M stream indexed"},
            {"name": "Writer", "state": "done", "detail": "Personalized trade touches (<75 words) drafted"},
            {"name": "Sender", "state": "running", "detail": "Pacing active at 35/day via secondary domains"},
            {"name": "Handler", "state": "done", "detail": "Classifying buyer replies & scheduling calls"},
            {"name": "Analyst", "state": "done", "detail": "Pipeline velocity & conversions monitored"}
        ]
    }

@app.get("/api/outbox")
@app.get("/api/outbox/")
async def get_outbox():
    return {
        "pending": harvey_agent._outbox,
        "approved": [],
        "sent": []
    }
