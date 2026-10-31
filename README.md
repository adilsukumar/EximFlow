# 🚀 EximFlow AI — Autonomous Lead Gen & Cold Outreach Engine

> **The all-in-one AI outbound platform built specifically for Indian Exporters targeting Global Importers (US, EU, Middle East) and High-Growth B2B Startups.**

---

## 🌟 Key Features

### 1. ⚡ Zero-Disk Apollo 99M Streaming Engine
* Queries directly inside large Apollo zip archives (e.g., `Entire Apollo Database 99,311,285.zip`) without decompressing a single byte to disk.
* Solves the local hard drive storage bottleneck using Python streaming readers and DuckDB-compatible stream pipelines.

### 2. 🚢 US/EU Customs Bill of Lading Database
* Unfair advantage for commodity and manufactured goods exporters.
* Surfaces verified importers who **already import** specific HS codes (Spices, Basmati Rice, Cotton/Textiles, Stainless Steel Flanges, Packaging, APIs) with historical container volumes (TEUs) and shipping manifests.

### 3. 📸 Instagram & Social Media Lead Parser (parser.im Engine)
* Inspired by **parser.im** and viral B2B lead generation reels:
* Scrapes public business emails, WhatsApp phone numbers, bios, follower counts, and bio links from target accounts, trade hashtags (e.g., `#spicesimporter`), and viral reels.
* Extracts contacts via advanced regex from bios without proxy pools or risk of account bans.
* Direct **parser.im / Instaparser CSV Uploader** allowing 1-click import into EximFlow CRM pipeline.

### 4. ⚡ Harvey: Autonomous AI Sales Employee (ethanplusai/harvey Engine)
* Inspired by **ethanplusai/harvey** running locally with 5 specialized sub-agents:
  * **Scout:** Discovers and scores high-intent buyers from customs manifests, Apollo 99M, and Instagram parser.
  * **Writer:** Enforces 100% humanized, zero-AI-buzzword cold email sequences.
  * **Sender:** Paces sending volume safely (max 35/day per mailbox) and manages the staged Outbox.
  * **Handler:** Triages incoming responses into Call Booked, Spec Sheet Requests, Objections, or Opt-Outs.
  * **Analyst:** Tracks pipeline velocity, deliverability health, and projected container contract value.
* Configurable with your exact offering, ICP, and target geographies.
* Switchable between **Review First (Safe Staged Outbox)** and **Autonomous Auto-Pilot**.

### 5. 🚀 B2B Tech Startup ICP Discovery
* Discovers founders, CTOs, and revenue leaders across tech companies categorized by tech stack, headcount, and funding stage (Seed to Series B).

### 6. 🛡️ Multi-Stage Waterfall Email Verifier
* RFC 5322 regex syntax validation.
* Real-time disposable domain detection (500+ disposable domains).
* Role-based account detection (`info@`, `sales@`, `support@`).
* Live MX and DNS routing checks with deliverability safety scoring (< 1.5% bounce target).
* Interactive **Bulk Email Verifier** in UI (paste and test up to 50 mailboxes simultaneously).

### 5. ✍️ 100% Humanized Cold Email Vault (No AI Fluff)
* Replaces generic AI spam phrases ("cutting-edge", "game-changer", "empower") with authentic trade terminology:
  * Container manifests & discharge ports (`Port of Newark`, `Port of Rotterdam`, `Port of Houston`).
  * Direct processing facilities at origin (`Unjha`, `Karnal`, `Rajkot`, `Tirupur`, `Mahuva`).
  * Inspection certificates (`BRC Grade-A`, `US FDA`, `SGS aflatoxin < 4ppb`, `EN 10204 3.1 MTR`).
  * Zero-friction CTAs (`500g DHL courier QA sample` or `FOB Mundra / CIF rate matrix review`).
* Full **3-Touch Sequences** across all 8 major trade categories:
  * **Touch 1 (Day 1):** Direct Sourcing Hook (~65 words).
  * **Touch 2 (Day 4):** SGS Lab Test & Free Sample / Fabric Swatch Offer (~55 words).
  * **Touch 3 (Day 8):** Respectful Low-Friction Breakup (~45 words).
* Real-time **Human Authenticity Auditor** that flags robotic phrases and rewrites drafts.

### 6. 🌐 Secondary Domain Deliverability & Warmup Hub
* Generates copy-paste DNS records (SPF, DKIM, DMARC, CNAME Custom Tracking Domain).
* Automated 21-day warmup ramping calendar (complies with Google & Microsoft spam thresholds).
* Mailbox capacity planner based on target monthly volume.

### 7. 📊 Sales Pipeline, CRM & Client Proposal Generator
* Real-time lead CRM (`Discovered` → `Verified` → `Outreached` → `Replied` → `Call Booked`).
* Inbound reply classifier: Automatically identifies **Discovery Call Requests**, **Price/Spec Inquiries**, or **Unsubscribes**, and drafts recommended next actions.
* One-click CSV export ready for direct import into **Smartlead.ai** or **Instantly.ai**.
* **Client Proposal Generator**: Generates formal signed-ready outbound contracts (Starter ₹35k, Growth ₹65k, Hybrid) tailored to Indian exporters.

---

## 🛠️ Tech Stack
* **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic
* **Frontend:** Tailwind CSS (Dark Mode), Vanilla JS, Jinja2, HTML5
* **Data Streaming:** Python `zipfile` virtual file streaming, CSV/JSON parser
* **Deliverability:** Custom RFC 5322 engine, DNS socket verifier, SPF/DKIM/DMARC generator

---

## ⚡ Quickstart (Local Run)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Startup
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the development server:**
   ```bash
   python run.py
   ```
   *(Or double-click `start.bat` on Windows)*

4. **Open in browser:**
   ```
   http://localhost:9090
   ```
   *(Or specify custom port: `python run.py --port 9090`)*

---

## ☁️ Deployment Guides

### 1. Render (One-Click)
* Push your code to GitHub.
* Create a new Web Service on [Render](https://render.com).
* Render automatically detects `render.yaml` and deploys your service.

### 2. Railway / Heroku
* Deploy using the included `Procfile`:
  ```
  web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### 3. Docker
* Build and run the Docker container:
  ```bash
  docker build -t eximflow-ai .
  docker run -p 8000:8000 eximflow-ai
  ```

---

## 📁 Repository Structure
```
├── STARTUP_MASTER_PLAYBOOK.md   # Complete Founder Strategic Blueprint & Sales Scripts
├── README.md                    # Platform documentation & setup guide
├── requirements.txt             # Python dependencies
├── Procfile                     # Deployment profile for Railway / Heroku
├── render.yaml                  # Deployment config for Render
├── Dockerfile                   # Multi-stage Docker container specification
├── vercel.json                  # Serverless deployment configuration
├── app/
│   ├── main.py                  # FastAPI entry point & API routes
│   ├── config.py                # Environment configuration & ZIP detection
│   ├── data_engines/
│   │   ├── apollo_streamer.py   # Streams inside 19.6GB zip without decompressing
│   │   ├── customs_engine.py    # US/EU Customs Bill of Lading importer data
│   │   └── startup_icp_engine.py# Tech Startup decision makers
│   ├── services/
│   │   ├── verifier.py          # Waterfall email deliverability verifier
│   │   ├── ai_generator.py      # AI 3-touch sequence generator & spam checker
│   │   ├── deliverability.py    # DNS & 21-day warmup scheduler
│   │   └── crm.py               # Pipeline tracking & AI reply classifier
│   ├── static/
│   │   ├── css/style.css        # Custom styles & glassmorphism
│   │   └── js/app.js            # Full frontend state & API controllers
│   └── templates/
│       └── index.html           # Modern responsive dashboard
```

---

## 📜 Master Startup Playbook
Review [`STARTUP_MASTER_PLAYBOOK.md`](STARTUP_MASTER_PLAYBOOK.md) for:
* Pricing tiers & 90% margin unit economics.
* High-converting WhatsApp pitch scripts to close your first 5 Indian exporters.
* 30-day week-by-week launch roadmap.

