// EximFlow AI - Frontend Engine
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  loadSystemStatus();
  searchLeads();
  loadCRMLeads();
  initDeliverabilityTools();
});

// Current Active Lead for AI Generation Modal
let activeLead = null;
let currentSequenceData = null;

// Tab Switching
function initTabs() {
  const tabButtons = document.querySelectorAll(".nav-tab-btn");
  const tabSections = document.querySelectorAll(".tab-section");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");
      
      tabButtons.forEach(b => b.classList.remove("tab-active", "text-blue-400"));
      btn.classList.add("tab-active", "text-blue-400");

      tabSections.forEach(sec => {
        if (sec.id === `tab-${target}`) {
          sec.classList.remove("hidden");
        } else {
          sec.classList.add("hidden");
        }
      });

      if (target === "playbook") {
        loadPlaybookContent();
      }
    });
  });
}

// Fetch System Status (Apollo ZIP check, metrics)
async function loadSystemStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    
    const zipStatusEl = document.getElementById("apollo-zip-badge");
    if (zipStatusEl) {
      if (data.apollo_zip_detected) {
        zipStatusEl.innerHTML = `
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            Apollo 99M Zip Stream: Active (Zero-Disk Mode)
          </span>
        `;
      } else {
        zipStatusEl.innerHTML = `
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            Cloud Mode: Customs & Startup Datasets Active
          </span>
        `;
      }
    }
  } catch (err) {
    console.error("Failed to load status:", err);
  }
}

// Search Leads
async function searchLeads() {
  const searchInput = document.getElementById("search-query");
  const dbSelect = document.getElementById("search-database");
  const productInput = document.getElementById("search-product");
  const countryInput = document.getElementById("search-country");
  const leadsContainer = document.getElementById("leads-container");
  const leadsCountEl = document.getElementById("leads-count");

  const query = searchInput ? searchInput.value : "";
  const database = dbSelect ? dbSelect.value : "all";
  const product = productInput ? productInput.value : "";
  const country = countryInput ? countryInput.value : "";

  leadsContainer.innerHTML = `
    <div class="col-span-full py-16 text-center text-gray-400">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
      <p class="text-sm font-medium">Scanning trade manifests & contact streams...</p>
    </div>
  `;

  try {
    const params = new URLSearchParams({
      database: database,
      query: query,
      product: product,
      country: country,
      limit: "30"
    });

    const res = await fetch(`/api/search?${params.toString()}`);
    const data = await res.json();

    if (leadsCountEl) {
      leadsCountEl.textContent = `${data.total} Verified Prospects Found`;
    }

    if (!data.leads || data.leads.length === 0) {
      leadsContainer.innerHTML = `
        <div class="col-span-full py-16 text-center bg-gray-900/40 rounded-xl border border-gray-800">
          <p class="text-gray-400 text-sm">No matching leads found for these filters.</p>
          <button onclick="clearSearchFilters()" class="mt-3 px-4 py-1.5 text-xs bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-medium">Reset Filters</button>
        </div>
      `;
      return;
    }

    leadsContainer.innerHTML = data.leads.map(lead => renderLeadCard(lead)).join("");
  } catch (err) {
    console.error("Search error:", err);
    leadsContainer.innerHTML = `<div class="col-span-full py-10 text-center text-red-400">Failed to load leads. Please retry.</div>`;
  }
}

// Render Lead Card
function renderLeadCard(lead) {
  const isCustoms = lead.data_source && lead.data_source.includes("Customs");
  const isApollo = lead.data_source && lead.data_source.includes("Apollo");
  
  let sourceBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30">Startup ICP</span>`;
  if (isCustoms) {
    sourceBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">🚢 Customs Bill of Lading</span>`;
  } else if (isApollo) {
    sourceBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-blue-500/20 text-blue-300 border border-blue-500/30">⚡ Apollo 99M Stream</span>`;
  }

  const extraMeta = isCustoms ? `
    <div class="mt-3 pt-3 border-t border-gray-800/80 text-xs grid grid-cols-2 gap-2 text-gray-400">
      <div><span class="text-gray-500">Volume:</span> <span class="text-gray-200 font-medium">${lead.annual_teu_volume || 'N/A'}</span></div>
      <div><span class="text-gray-500">Port:</span> <span class="text-gray-200 font-medium">${lead.port_of_discharge || 'US Port'}</span></div>
      <div class="col-span-2 truncate"><span class="text-gray-500">Imports:</span> <span class="text-emerald-400 font-medium">${lead.product_interest || lead.industry}</span></div>
    </div>
  ` : `
    <div class="mt-3 pt-3 border-t border-gray-800/80 text-xs text-gray-400">
      <span class="text-gray-500">Industry:</span> <span class="text-gray-200 font-medium">${lead.industry || 'B2B'}</span>
      ${lead.tech_stack ? `<div class="truncate mt-1 text-[11px] text-gray-400"><span class="text-gray-500">Stack:</span> ${lead.tech_stack}</div>` : ''}
    </div>
  `;

  return `
    <div class="glass-panel glass-panel-hover rounded-xl p-5 flex flex-col justify-between border border-gray-800/80">
      <div>
        <div class="flex items-start justify-between gap-2">
          <div>
            <h4 class="font-semibold text-base text-white tracking-tight">${lead.name || 'Decision Maker'}</h4>
            <p class="text-xs text-blue-400 font-medium">${lead.title || 'Executive'}</p>
          </div>
          ${sourceBadge}
        </div>

        <div class="mt-2.5 flex items-center gap-1.5 text-xs text-gray-300">
          <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
          <span class="font-medium text-gray-100">${lead.company}</span>
          <span class="text-gray-500">•</span>
          <span class="text-gray-400">${lead.city ? lead.city + ', ' : ''}${lead.country || 'USA'}</span>
        </div>

        <div class="mt-2 text-xs flex items-center justify-between bg-gray-900/60 px-2.5 py-1.5 rounded-lg border border-gray-800">
          <span class="font-mono text-gray-300 truncate">${lead.email}</span>
          <button onclick="verifyEmailDirect('${lead.email}', this)" class="text-[11px] font-semibold text-blue-400 hover:text-blue-300 hover:underline shrink-0 ml-2">Verify MX</button>
        </div>

        ${extraMeta}
      </div>

      <div class="mt-4 pt-3 flex items-center gap-2">
        <button onclick="openSequenceModal('${encodeURIComponent(JSON.stringify(lead))}')" class="flex-1 py-2 px-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold rounded-lg shadow-sm flex items-center justify-center gap-1.5 transition">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          Generate AI Sequence
        </button>
        <button onclick="addToCRM('${encodeURIComponent(JSON.stringify(lead))}')" title="Save to Sales Pipeline" class="p-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg border border-gray-700 transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
        </button>
      </div>
    </div>
  `;
}

// Clear Search Filters
function clearSearchFilters() {
  document.getElementById("search-query").value = "";
  document.getElementById("search-product").value = "";
  document.getElementById("search-country").value = "";
  document.getElementById("search-database").value = "all";
  searchLeads();
}

// Direct Email Verification Check
async function verifyEmailDirect(email, btnEl) {
  btnEl.textContent = "...";
  try {
    const res = await fetch("/api/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });
    const result = await res.json();
    if (result.status === "SAFE_TO_SEND") {
      btnEl.outerHTML = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">✓ 95% Safe</span>`;
    } else if (result.status === "ACCEPTABLE_RISKY") {
      btnEl.outerHTML = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">⚠ Acceptable</span>`;
    } else {
      btnEl.outerHTML = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/40">✕ Risky</span>`;
    }
  } catch (err) {
    btnEl.textContent = "Error";
  }
}

// Open AI Sequence Generator Modal
function openSequenceModal(leadStr) {
  activeLead = JSON.parse(decodeURIComponent(leadStr));
  const modal = document.getElementById("sequence-modal");
  
  document.getElementById("modal-lead-name").textContent = `${activeLead.name} (${activeLead.company})`;
  document.getElementById("modal-lead-title").textContent = activeLead.title || "Procurement";
  
  // Set default product category
  const prodInput = document.getElementById("modal-product-cat");
  if (activeLead.product_interest) {
    prodInput.value = activeLead.product_interest;
  } else if (activeLead.industry) {
    prodInput.value = activeLead.industry;
  } else {
    prodInput.value = "Organic Spices & Commodities";
  }

  modal.classList.remove("hidden");
  generateModalSequence();
}

function closeSequenceModal() {
  document.getElementById("sequence-modal").classList.add("hidden");
}

// Generate sequence inside modal
async function generateModalSequence() {
  if (!activeLead) return;

  const sequenceOutput = document.getElementById("sequence-output");
  const productCat = document.getElementById("modal-product-cat").value;
  const clientCompany = document.getElementById("modal-client-company").value || "Surat Organic Agro Exports";
  const clientName = document.getElementById("modal-client-name").value || "Rajesh Patel";
  const certifications = document.getElementById("modal-certs").value || "BRC, FDA, USDA Organic";

  sequenceOutput.innerHTML = `
    <div class="py-16 text-center text-gray-400">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mb-3"></div>
      <p class="text-sm">Synthesizing personalized 3-touch sequence & running spam word analysis...</p>
    </div>
  `;

  try {
    const res = await fetch("/api/generate-sequence", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prospect_name: activeLead.name,
        prospect_title: activeLead.title,
        prospect_company: activeLead.company,
        prospect_country: activeLead.country,
        product_category: productCat,
        client_company: clientCompany,
        client_name: clientName,
        certifications: certifications
      })
    });

    currentSequenceData = await res.json();
    renderSequenceOutput(currentSequenceData);
  } catch (err) {
    sequenceOutput.innerHTML = `<p class="text-red-400 text-center py-8">Failed to generate email sequence.</p>`;
  }
}

// Render generated sequence
function renderSequenceOutput(data) {
  const container = document.getElementById("sequence-output");
  const spam = data.spam_analysis;

  container.innerHTML = `
    <div class="mb-5 p-3.5 rounded-xl bg-gray-900/80 border border-gray-800 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${spam.score >= 80 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'}">
          ${spam.score}
        </div>
        <div>
          <h5 class="text-xs font-semibold text-white">Deliverability & Spam Score: ${spam.score >= 80 ? 'Excellent' : 'Moderate'}</h5>
          <p class="text-[11px] text-gray-400">${spam.is_clean ? '✓ Zero spam triggers detected. 100% Primary Inbox optimized.' : 'Triggers found: ' + spam.detected_triggers.join(', ')}</p>
        </div>
      </div>
      <div class="text-right">
        <span class="text-[11px] px-2.5 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/30 rounded-full font-medium">
          Mobile Readability: Grade 6
        </span>
      </div>
    </div>

    <!-- Sequence Tabs -->
    <div class="flex border-b border-gray-800 gap-2 mb-4">
      ${data.sequences.map((s, idx) => `
        <button onclick="switchSequenceStep(${idx})" id="seq-step-btn-${idx}" class="seq-step-btn py-2 px-3 text-xs font-medium rounded-t-lg transition ${idx === 0 ? 'text-blue-400 border-b-2 border-blue-500 bg-gray-900/60' : 'text-gray-400 hover:text-gray-200'}">
          ${s.day} (${s.step === 1 ? 'Initial Hook' : s.step === 2 ? 'Social Proof' : 'Breakup'})
        </button>
      `).join("")}
    </div>

    <!-- Sequence Content Area -->
    <div id="sequence-steps-container">
      ${data.sequences.map((s, idx) => `
        <div id="seq-step-content-${idx}" class="seq-step-content ${idx === 0 ? '' : 'hidden'} space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-400">Subject Line:</span>
            <button onclick="copyToClipboard('${encodeURIComponent(s.subject)}', this)" class="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
              Copy Subject
            </button>
          </div>
          <div class="p-2.5 bg-gray-900 rounded-lg border border-gray-800 text-sm font-mono text-gray-100">
            ${s.subject}
          </div>

          <div class="flex items-center justify-between mt-2">
            <span class="text-xs text-gray-400">Email Body (${s.word_count} words):</span>
            <button onclick="copyToClipboard('${encodeURIComponent(s.body)}', this)" class="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
              Copy Body
            </button>
          </div>
          <div class="p-3 bg-gray-900 rounded-lg border border-gray-800 text-xs font-mono text-gray-200 whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto">
${s.body}
          </div>
        </div>
      `).join("")}
    </div>
  `;
}

function switchSequenceStep(stepIndex) {
  document.querySelectorAll(".seq-step-btn").forEach((btn, idx) => {
    if (idx === stepIndex) {
      btn.classList.add("text-blue-400", "border-b-2", "border-blue-500", "bg-gray-900/60");
      btn.classList.remove("text-gray-400");
    } else {
      btn.classList.remove("text-blue-400", "border-b-2", "border-blue-500", "bg-gray-900/60");
      btn.classList.add("text-gray-400");
    }
  });

  document.querySelectorAll(".seq-step-content").forEach((sec, idx) => {
    if (idx === stepIndex) {
      sec.classList.remove("hidden");
    } else {
      sec.classList.add("hidden");
    }
  });
}

function copyToClipboard(encodedText, btnEl) {
  const text = decodeURIComponent(encodedText);
  navigator.clipboard.writeText(text);
  const orig = btnEl.innerHTML;
  btnEl.innerHTML = `<span class="text-emerald-400 font-semibold">✓ Copied!</span>`;
  setTimeout(() => { btnEl.innerHTML = orig; }, 1500);
}

// Add lead to CRM
async function addToCRM(leadStr) {
  const lead = JSON.parse(decodeURIComponent(leadStr));
  try {
    const res = await fetch("/api/crm/lead", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: lead.name,
        email: lead.email,
        title: lead.title,
        company: lead.company,
        country: lead.country,
        product: lead.product_interest || lead.industry || "General Commodity",
        notes: `Discovered from ${lead.data_source}`
      })
    });
    alert(`✓ Added ${lead.name} (${lead.company}) to Sales Pipeline!`);
    loadCRMLeads();
  } catch (err) {
    alert("Failed to add to CRM");
  }
}

// Load CRM Pipeline Leads
async function loadCRMLeads() {
  const tbody = document.getElementById("crm-leads-table-body");
  if (!tbody) return;

  try {
    const res = await fetch("/api/crm/leads");
    const data = await res.json();

    // Update KPI badges
    const m = data.metrics;
    if (document.getElementById("kpi-total-leads")) document.getElementById("kpi-total-leads").textContent = m.total;
    if (document.getElementById("kpi-verified")) document.getElementById("kpi-verified").textContent = m.verified;
    if (document.getElementById("kpi-outreached")) document.getElementById("kpi-outreached").textContent = m.outreached;
    if (document.getElementById("kpi-replied")) document.getElementById("kpi-replied").textContent = m.replied;
    if (document.getElementById("kpi-calls")) document.getElementById("kpi-calls").textContent = m.call_booked;

    tbody.innerHTML = data.leads.map(lead => {
      let stageBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-700/50 text-gray-300">Verified</span>`;
      if (lead.stage === "outreached") stageBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-400 border border-blue-500/30">Outreach Active</span>`;
      if (lead.stage === "replied") stageBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-400 border border-amber-500/30">Positive Reply</span>`;
      if (lead.stage === "call_booked") stageBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">🎉 Call Booked</span>`;

      return `
        <tr class="border-b border-gray-800/60 hover:bg-gray-800/30">
          <td class="py-3 px-4">
            <div class="font-semibold text-white text-sm">${lead.name}</div>
            <div class="text-xs text-gray-400">${lead.title} @ ${lead.company}</div>
          </td>
          <td class="py-3 px-4 text-xs font-mono text-gray-300">${lead.email}</td>
          <td class="py-3 px-4 text-xs text-gray-300">${lead.product}</td>
          <td class="py-3 px-4">${stageBadge}</td>
          <td class="py-3 px-4 text-xs text-gray-400 max-w-xs truncate">${lead.notes}</td>
          <td class="py-3 px-4 text-right">
            <select onchange="updateCRMStage('${lead.id}', this.value)" class="text-xs bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-300 focus:outline-none focus:border-blue-500">
              <option value="verified" ${lead.stage === 'verified' ? 'selected' : ''}>Verified</option>
              <option value="outreached" ${lead.stage === 'outreached' ? 'selected' : ''}>Outreached</option>
              <option value="replied" ${lead.stage === 'replied' ? 'selected' : ''}>Positive Reply</option>
              <option value="call_booked" ${lead.stage === 'call_booked' ? 'selected' : ''}>Call Booked</option>
            </select>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    console.error("Failed to load CRM leads:", err);
  }
}

async function updateCRMStage(leadId, stage) {
  try {
    await fetch("/api/crm/update-stage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lead_id: leadId, stage: stage })
    });
    loadCRMLeads();
  } catch (err) {
    alert("Failed to update status");
  }
}

// Simulate Inbound Email Reply Triage
async function triageReplySim() {
  const textInput = document.getElementById("triage-reply-input");
  const outputEl = document.getElementById("triage-output");
  const text = textInput ? textInput.value : "";

  if (!text.trim()) {
    alert("Please enter sample reply text");
    return;
  }

  outputEl.innerHTML = `<p class="text-xs text-gray-400">Classifying reply intent...</p>`;

  try {
    const res = await fetch("/api/crm/triage-reply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reply_text: text })
    });
    const result = await res.json();

    outputEl.innerHTML = `
      <div class="p-4 rounded-xl bg-gray-900 border border-gray-800 space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold px-2.5 py-1 rounded-full ${result.sentiment === 'positive' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : result.sentiment === 'negative' ? 'bg-red-500/20 text-red-400' : 'bg-gray-800 text-gray-300'}">
            ${result.classification}
          </span>
          <span class="text-xs text-gray-400 font-medium">${result.intent}</span>
        </div>

        <div class="text-xs text-gray-300">
          <strong class="text-blue-400">Recommended Action:</strong> ${result.recommended_action}
        </div>

        ${result.draft_response ? `
          <div class="pt-2 border-t border-gray-800">
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-xs text-gray-400 font-semibold">Suggested Quick Response:</span>
              <button onclick="copyToClipboard('${encodeURIComponent(result.draft_response)}', this)" class="text-xs text-blue-400 hover:underline">Copy Response</button>
            </div>
            <pre class="p-3 bg-black/50 rounded-lg text-xs font-mono text-gray-200 whitespace-pre-wrap">${result.draft_response}</pre>
          </div>
        ` : ''}
      </div>
    `;
  } catch (err) {
    outputEl.innerHTML = `<p class="text-red-400 text-xs">Error parsing reply.</p>`;
  }
}

// Deliverability Tools: DNS, Warmup & Capacity
function initDeliverabilityTools() {
  generateDNS();
  calculateCapacity();
  calculateWarmup();
}

async function generateDNS() {
  const domainInput = document.getElementById("dns-domain-input");
  const tableBody = document.getElementById("dns-table-body");
  const domain = domainInput ? domainInput.value : "example-exports.com";

  try {
    const res = await fetch(`/api/deliverability/dns?domain=${encodeURIComponent(domain)}`);
    const data = await res.json();

    if (tableBody) {
      tableBody.innerHTML = data.records.map(rec => `
        <tr class="border-b border-gray-800/60 font-mono text-xs">
          <td class="py-2.5 px-3 font-bold text-blue-400">${rec.type}</td>
          <td class="py-2.5 px-3 text-gray-300">${rec.host}</td>
          <td class="py-2.5 px-3 text-gray-200 break-all">${rec.value}</td>
          <td class="py-2.5 px-3 font-sans text-gray-400 text-[11px]">${rec.purpose}</td>
        </tr>
      `).join("");
    }
  } catch (err) {
    console.error("DNS generation failed", err);
  }
}

async function calculateCapacity() {
  const volInput = document.getElementById("capacity-target-volume");
  const target = volInput ? parseInt(volInput.value) || 3000 : 3000;

  try {
    const res = await fetch(`/api/deliverability/capacity?target_monthly=${target}`);
    const data = await res.json();

    document.getElementById("cap-domains").textContent = data.required_secondary_domains;
    document.getElementById("cap-inboxes").textContent = data.required_mailboxes;
    document.getElementById("cap-daily").textContent = `${data.daily_emails_capacity} / day`;
    document.getElementById("cap-cost").textContent = `₹${data.estimated_infra_cost_inr} / mo`;
  } catch (err) {
    console.error("Capacity calc failed", err);
  }
}

async function calculateWarmup() {
  const container = document.getElementById("warmup-schedule-container");
  if (!container) return;

  try {
    const res = await fetch("/api/deliverability/warmup?target_daily=100");
    const data = await res.json();

    container.innerHTML = data.slice(0, 14).map(w => `
      <div class="p-2.5 rounded-lg bg-gray-900 border border-gray-800 flex items-center justify-between text-xs">
        <div>
          <span class="font-bold text-white">${w.day}</span>
          <span class="text-gray-500 text-[11px] ml-2">${w.phase}</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-blue-400 font-semibold">${w.cold_emails} Cold</span>
          <span class="text-emerald-400 font-semibold">${w.warmup_emails} Warm</span>
          <span class="text-gray-400 font-mono font-bold">${w.total_emails} Total</span>
        </div>
      </div>
    `).join("");
  } catch (err) {
    console.error("Warmup calc failed", err);
  }
}

// Load Playbook Markdown
async function loadPlaybookContent() {
  const el = document.getElementById("playbook-content");
  if (!el || el.getAttribute("data-loaded") === "true") return;

  try {
    const res = await fetch("/api/playbook");
    const markdown = await res.text();
    el.textContent = markdown;
    el.setAttribute("data-loaded", "true");
  } catch (err) {
    el.textContent = "Failed to load playbook.";
  }
}
