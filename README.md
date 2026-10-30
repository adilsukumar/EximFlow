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

### 3. 🚀 B2B Tech Startup ICP Discovery
* Discovers founders, CTOs, and revenue leaders across tech companies categorized by tech stack, headcount, and funding stage (Seed to Series B).

### 4. 🛡️ Multi-Stage Waterfall Email Verifier
* RFC 5322 regex syntax validation.
* Real-time disposable domain detection (500+ disposable domains).
* Role-based account detection (`info@`, `sales@`, `support@`).
* Live MX and DNS routing checks with deliverability safety scoring (< 1.5% bounce target).

### 5. 🤖 AI 3-Touch Cold Sequence Generator
* Generates hyper-personalized, 3-touch cold email sequences customized for:
  * **Touch 1 (Day 1):** Direct Hook & Value Proposition (no fluff, ~65 words).
  * **Touch 2 (Day 4):** Social Proof, Lab Certificates (SGS/FDA/BRC), or Free Product Sample Offer.
  * **Touch 3 (Day 8):** Respectful Low-Friction Breakup.
* Includes **Spam Word Detector** and mobile readability scoring.

### 6. 🌐 Secondary Domain Deliverability & Warmup Hub
* Generates copy-paste DNS records (SPF, DKIM, DMARC, CNAME Custom Tracking Domain).
* Automated 21-day warmup ramping calendar (complies with Google & Microsoft spam thresholds).
* Mailbox capacity planner based on target monthly volume.

### 7. 📊 Sales Pipeline & AI Reply Triage Simulator
* Real-time lead CRM (`Discovered` → `Verified` → `Outreached` → `Replied` → `Call Booked`).
* Inbound reply classifier: Automatically identifies **Discovery Call Requests**, **Price/Spec Inquiries**, or **Unsubscribes**, and drafts recommended next actions.
* One-click CSV export ready for direct import into **Smartlead.ai** or **Instantly.ai**.

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
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Open in browser:**
   ```
   http://localhost:8000
   ```

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
