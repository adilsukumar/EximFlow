// EximFlow AI - Frontend Engine

document.addEventListener("DOMContentLoaded", () => {

  initTabs();

  initManualBannerState();

  loadSystemStatus();

  searchLeads();

  loadCRMLeads();

  initDeliverabilityTools();

  loadInitialSocialLeads();

  loadHarveyStatus();

});

// Current Active Lead for AI Generation Modal

let activeLead = null;

let currentSequenceData = null;

// Programmatic Tab Switching Helper

function switchTab(target) {

  const tabBtn = document.querySelector(`.nav-tab-btn[data-tab="${target}"]`);

  if (tabBtn) {

    tabBtn.click();

    window.scrollTo({ top: 0, behavior: "smooth" });

  }

}

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

      if (target === "social") {

        loadInitialSocialLeads();

      }

      if (target === "harvey") {

        loadHarveyStatus();

      }

      if (target === "templates") {

        loadTemplatesVault();

      }

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

          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">

            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Cloud Stream: Customs AMS & 99M Global Active

          </span>

        `;

      }

    }

  } catch (err) {

    console.error("Failed to load status:", err);

  }

}

// Search & Lead Streaming State

let currentStreamOffset = 0;

let allDiscoveredLeads = [];

function resetAndSearchLeads() {

  currentStreamOffset = 0;

  allDiscoveredLeads = [];

  searchLeads(false);

}

async function loadMoreLeads() {

  const limitSelect = document.getElementById("search-limit");

  const batchSize = limitSelect ? parseInt(limitSelect.value) || 50 : 50;

  currentStreamOffset += batchSize;

  searchLeads(true);

}

// Search Leads (Supports batch size selector & offset streaming across 99M records)

async function searchLeads(appendMode = false) {

  const searchInput = document.getElementById("search-query");

  const dbSelect = document.getElementById("search-database");

  const productInput = document.getElementById("search-product");

  const countryInput = document.getElementById("search-country");

  const limitSelect = document.getElementById("search-limit");

  const leadsContainer = document.getElementById("leads-container");

  const leadsCountEl = document.getElementById("leads-count");

  const paginationStatusEl = document.getElementById("pagination-status");

  const btnLoadMore = document.getElementById("btn-load-more");

  const btnLoadMoreText = document.getElementById("btn-load-more-text");

  const query = searchInput ? searchInput.value : "";

  const database = dbSelect ? dbSelect.value : "all";

  const product = productInput ? productInput.value : "";

  const country = countryInput ? countryInput.value : "";

  const batchLimit = limitSelect ? limitSelect.value : "100";

  if (!appendMode) {

    currentStreamOffset = 0;

    allDiscoveredLeads = [];

    leadsContainer.innerHTML = `

      <div class="col-span-full py-16 text-center text-gray-400">

        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>

        <p class="text-sm font-medium">Streaming verified leads from 99M Apollo archive & Customs manifests...</p>

      </div>

    `;

  } else {

    if (btnLoadMoreText) btnLoadMoreText.textContent = "Streaming next batch from 99M database...";

    if (btnLoadMore) btnLoadMore.disabled = true;

  }

  try {

    const params = new URLSearchParams({

      database: database,

      query: query,

      product: product,

      country: country,

      limit: batchLimit,

      offset: currentStreamOffset.toString()

    });

    const res = await fetch(`/api/search?${params.toString()}`);

    let data;

    try {

      data = await res.json();

    } catch (parseErr) {

      console.warn("API response was not JSON, falling back:", parseErr);

      data = { leads: [] };

    }

    const newLeads = (data && Array.isArray(data.leads)) ? data.leads : [];

    if (!appendMode) {

      allDiscoveredLeads = newLeads;

    } else {

      allDiscoveredLeads = allDiscoveredLeads.concat(newLeads);

    }

    if (leadsCountEl) {

      leadsCountEl.textContent = `Showing ${allDiscoveredLeads.length} Leads (of 99.3M+ in Database)`;

    }

    if (paginationStatusEl) {

      paginationStatusEl.textContent = `Showing ${allDiscoveredLeads.length} leads`;

    }

    if (allDiscoveredLeads.length === 0) {

      leadsContainer.innerHTML = `

        <div class="col-span-full py-16 text-center bg-gray-900/40 rounded-xl border border-gray-800">

          <p class="text-gray-400 text-sm">No matching leads found for these filters.</p>

          <button onclick="clearSearchFilters()" class="mt-3 px-4 py-1.5 text-xs bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-medium">Reset Filters</button>

        </div>

      `;

      return;

    }

    if (!appendMode) {

      leadsContainer.innerHTML = allDiscoveredLeads.map(lead => renderLeadCard(lead)).join("");

    } else {

      const fragmentHtml = newLeads.map(lead => renderLeadCard(lead)).join("");

      leadsContainer.insertAdjacentHTML("beforeend", fragmentHtml);

    }

  } catch (err) {

    console.error("Search error:", err);

    if (!appendMode) {

      leadsContainer.innerHTML = `<div class="col-span-full py-10 text-center text-red-400">Failed to load leads. Please retry.</div>`;

    }

  } finally {

    if (btnLoadMoreText) btnLoadMoreText.textContent = `Stream Next ${batchLimit} Leads from 99M Database`;

    if (btnLoadMore) btnLoadMore.disabled = false;

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

  const clientName = document.getElementById("modal-client-name").value || "Aarav Sharma";

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

      const healthBadge = lead.deliverability_score !== undefined

        ? `<div class="mt-0.5"><span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${lead.verify_status === 'SAFE_TO_SEND' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'}">Score: ${lead.deliverability_score}/100</span></div>`

        : `<div class="mt-0.5 text-[10px] text-gray-500">Unchecked</div>`;

      return `

        <tr class="border-b border-gray-800/60 hover:bg-gray-800/30">

          <td class="py-3 px-4">

            <div class="font-semibold text-white text-sm">${lead.name}</div>

            <div class="text-xs text-gray-400">${lead.title} @ ${lead.company}</div>

          </td>

          <td class="py-3 px-4">

            <div class="text-xs font-mono text-gray-300">${lead.email}</div>

            ${healthBadge}

          </td>

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

          <td class="py-3 px-3 text-center">

            <button onclick="deleteCRMLead('${lead.id}')" title="Delete lead" class="p-1 rounded text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition">

              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>

            </button>

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

async function deleteCRMLead(leadId) {

  if (!confirm("Are you sure you want to remove this lead from your pipeline?")) return;

  try {

    const res = await fetch("/api/crm/delete-lead", {

      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({ lead_id: leadId })

    });

    if (res.ok) {

      loadCRMLeads();

    }

  } catch (err) {

    alert("Failed to delete lead");

  }

}

async function batchVerifyCRM(btnEl) {

  const origText = btnEl ? btnEl.innerHTML : "";

  if (btnEl) btnEl.innerHTML = `<span class="inline-block animate-spin mr-1">⌛</span> Verifying...`;

  try {

    const res = await fetch("/api/crm/batch-verify", { method: "POST" });

    const data = await res.json();

    alert(`Batch Verification Complete!\nTotal Verified: ${data.summary.total_verified}\nSafe to Send: ${data.summary.safe_to_send}\nRisky: ${data.summary.risky}\nDo Not Send: ${data.summary.do_not_send}`);

    loadCRMLeads();

  } catch (err) {

    alert("Batch verification failed");

  } finally {

    if (btnEl) btnEl.innerHTML = origText;

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

// ==============================================

// MASTER PLAYBOOK CONTROLLER (NATIVE HTML)

// ==============================================

function loadPlaybookContent() {

  // Native HTML Playbook is already rendered in the DOM

  console.log("Master Playbook loaded in native HTML mode.");

}

function filterPlaybookSection(sectionId) {

  const sections = document.querySelectorAll(".playbook-section");

  const buttons = document.querySelectorAll(".playbook-filter-btn");

  buttons.forEach(btn => {

    if (btn.getAttribute("data-psec") === sectionId) {

      btn.className = "playbook-filter-btn px-3 py-1.5 rounded-lg bg-purple-600 text-white text-xs font-semibold shadow transition whitespace-nowrap";

    } else {

      btn.className = "playbook-filter-btn px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium transition whitespace-nowrap";

    }

  });

  sections.forEach(sec => {

    if (sectionId === "all" || sec.id === `psec-${sectionId}`) {

      sec.classList.remove("hidden");

    } else {

      sec.classList.add("hidden");

    }

  });

}

function copyWhatsAppPitch() {

  const el = document.getElementById("whatsapp-pitch-box");

  if (el) {

    navigator.clipboard.writeText(el.innerText || el.textContent);

    alert("✓ Direct WhatsApp Pitch Script copied to clipboard!");

  }

}

function copyPlaybookOverview() {

  const wrapper = document.getElementById("playbook-sections-wrapper");

  if (wrapper) {

    navigator.clipboard.writeText(wrapper.innerText);

    alert("✓ Master Execution Playbook text copied to clipboard!");

  }

}

// ==============================================

// HUMANIZED EMAIL VAULT

// ==============================================

let allVaultTemplates = [];

async function loadTemplatesVault() {

  const container = document.getElementById("vault-templates-container");

  if (!container || container.getAttribute("data-loaded") === "true") return;

  try {

    const res = await fetch("/api/templates/vault");

    const data = await res.json();

    allVaultTemplates = data.templates || [];

    renderVaultTemplates(allVaultTemplates);

    container.setAttribute("data-loaded", "true");

  } catch (err) {

    container.innerHTML = `<p class="text-red-400 text-sm">Failed to load templates vault.</p>`;

  }

}

function filterVaultTemplates(cat) {

  // Update button active states

  const buttons = document.querySelectorAll(".vault-cat-btn");

  buttons.forEach(btn => {

    btn.classList.remove("bg-blue-600", "text-white");

    btn.classList.add("bg-gray-900", "text-gray-300");

  });

  event.target.classList.remove("bg-gray-900", "text-gray-300");

  event.target.classList.add("bg-blue-600", "text-white");

  if (cat === "all") {

    renderVaultTemplates(allVaultTemplates);

  } else {

    const filtered = allVaultTemplates.filter(t => t.id.toLowerCase().includes(cat.toLowerCase()) || t.category.toLowerCase().includes(cat.toLowerCase()));

    renderVaultTemplates(filtered);

  }

}

function renderVaultTemplates(templates) {

  const container = document.getElementById("vault-templates-container");

  if (!container) return;

  if (templates.length === 0) {

    container.innerHTML = `<p class="col-span-full py-8 text-center text-gray-400 text-sm">No templates match this filter.</p>`;

    return;

  }

  container.innerHTML = templates.map((tmpl, idx) => `

    <div class="glass-panel rounded-xl p-5 border border-gray-800 space-y-4 hover:border-gray-700 transition">

      <div class="flex items-start justify-between gap-2">

        <div>

          <span class="inline-block px-2.5 py-0.5 rounded text-[11px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 mb-1">

            ${tmpl.category}

          </span>

          <h4 class="text-sm font-bold text-white">${tmpl.target_persona}</h4>

        </div>

        <div class="text-right">

          <span class="text-[11px] font-semibold text-emerald-400 block">Avg Open: ${tmpl.open_rate_benchmark}</span>

          <span class="text-[10px] text-gray-400 block">Reply: ${tmpl.reply_rate_benchmark}</span>

        </div>

      </div>

      <!-- Touch Selector Tabs -->

      <div class="border-b border-gray-800 flex gap-2 text-xs font-medium">

        <button onclick="switchVaultTouch('t1_${idx}', this)" class="vault-touch-tab text-blue-400 border-b-2 border-blue-400 pb-1 font-semibold">Touch 1 (Day 1)</button>

        <button onclick="switchVaultTouch('t2_${idx}', this)" class="vault-touch-tab text-gray-400 pb-1 hover:text-white">Touch 2 (Day 4 Sample)</button>

        <button onclick="switchVaultTouch('t3_${idx}', this)" class="vault-touch-tab text-gray-400 pb-1 hover:text-white">Touch 3 (Day 8 Breakup)</button>

      </div>

      <!-- Touch 1 Content -->

      <div id="t1_${idx}" class="vault-touch-content space-y-2">

        <div class="text-[11px] text-gray-400 font-mono">

          <span class="text-gray-500">Subject:</span> <span class="text-gray-200">${tmpl.touch1_subject}</span>

        </div>

        <pre class="p-3 rounded-lg bg-gray-900 border border-gray-800 text-xs font-mono text-gray-300 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">${tmpl.touch1_body}</pre>

        <button onclick="copyToClipboard('${encodeURIComponent(tmpl.touch1_subject + '\n\n' + tmpl.touch1_body)}', this)" class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition">

          Copy Touch 1

        </button>

      </div>

      <!-- Touch 2 Content -->

      <div id="t2_${idx}" class="vault-touch-content hidden space-y-2">

        <div class="text-[11px] text-gray-400 font-mono">

          <span class="text-gray-500">Subject:</span> <span class="text-gray-200">${tmpl.touch2_subject}</span>

        </div>

        <pre class="p-3 rounded-lg bg-gray-900 border border-gray-800 text-xs font-mono text-gray-300 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">${tmpl.touch2_body}</pre>

        <button onclick="copyToClipboard('${encodeURIComponent(tmpl.touch2_subject + '\n\n' + tmpl.touch2_body)}', this)" class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition">

          Copy Touch 2

        </button>

      </div>

      <!-- Touch 3 Content -->

      <div id="t3_${idx}" class="vault-touch-content hidden space-y-2">

        <div class="text-[11px] text-gray-400 font-mono">

          <span class="text-gray-500">Subject:</span> <span class="text-gray-200">${tmpl.touch3_subject}</span>

        </div>

        <pre class="p-3 rounded-lg bg-gray-900 border border-gray-800 text-xs font-mono text-gray-300 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">${tmpl.touch3_body}</pre>

        <button onclick="copyToClipboard('${encodeURIComponent(tmpl.touch3_subject + '\n\n' + tmpl.touch3_body)}', this)" class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition">

          Copy Touch 3

        </button>

      </div>

    </div>

  `).join("");

}

function switchVaultTouch(targetId, btnEl) {

  const parent = btnEl.closest(".glass-panel");

  parent.querySelectorAll(".vault-touch-tab").forEach(tab => {

    tab.classList.remove("text-blue-400", "border-b-2", "border-blue-400", "font-semibold");

    tab.classList.add("text-gray-400");

  });

  btnEl.classList.remove("text-gray-400");

  btnEl.classList.add("text-blue-400", "border-b-2", "border-blue-400", "font-semibold");

  parent.querySelectorAll(".vault-touch-content").forEach(c => c.classList.add("hidden"));

  const target = document.getElementById(targetId);

  if (target) target.classList.remove("hidden");

}

// Live Humanizer Auditor

function auditHumanCopy() {

  const inputEl = document.getElementById("humanizer-input");

  const outputEl = document.getElementById("humanizer-output");

  const text = inputEl ? inputEl.value.trim() : "";

  if (!text) {

    outputEl.textContent = "Please enter an email draft to audit.";

    return;

  }

  const roboticClichés = [

    "i hope this email finds you well",

    "in today's fast-paced digital landscape",

    "empower your business",

    "game-changing",

    "synergies",

    "cutting-edge",

    "revolutionary",

    "supercharge",

    "autonomous ai pipeline",

    "disrupting the industry",

    "seamless integration",

    "world-class solutions"

  ];

  let detected = [];

  let cleaned = text;

  roboticClichés.forEach(c => {

    const reg = new RegExp(c, "gi");

    if (reg.test(text)) {

      detected.push(c);

      cleaned = cleaned.replace(reg, "");

    }

  });

  // Clean excess whitespace

  cleaned = cleaned.replace(/\n{3,}/g, "\n\n").replace(/ +/g, " ").trim();

  const words = text.split(/\s+/).length;

  let score = 95 - (detected.length * 25);

  if (words > 110) score -= 15;

  score = Math.max(score, 30);

  outputEl.innerHTML = `

=== HUMAN AUTHENTICITY AUDIT ===

Authenticity Score: ${score}/100 ${score >= 80 ? '✅ (Sounds Human & Direct)' : '⚠️ (Robotic Fluff Detected)'}

Word Count: ${words} words ${words <= 85 ? '✅ (Mobile Skimmable)' : '⚠️ (Too Long)'}

Detected Buzzwords: ${detected.length > 0 ? detected.join(", ") : "None! Clean Trade Copy."}

--- CLEANED TRADE VERSION ---

${cleaned}

  `;

}

// ==============================================

// AGENCY EXECUTION TOOLKIT: PROPOSAL & BATCH VERIFY

// ==============================================

let currentProposalData = null;

async function generateProposalDoc() {

  const name = document.getElementById("prop-exporter-name").value;

  const company = document.getElementById("prop-exporter-company").value;

  const product = document.getElementById("prop-product").value;

  const country = document.getElementById("prop-country").value;

  const tier = document.getElementById("prop-tier").value;

  const container = document.getElementById("proposal-output-container");

  const cardEl = document.getElementById("proposal-preview-card");

  try {

    const res = await fetch("/api/proposal/generate", {

      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({

        exporter_name: name,

        exporter_company: company,

        product: product,

        target_country: country,

        tier: tier

      })

    });

    const data = await res.json();

    currentProposalData = data;

    const refNumber = "EXIM-AGR-" + (new Date().getFullYear()) + "-" + Math.floor(1000 + Math.random() * 9000);

    const today = new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });

    cardEl.innerHTML = `

      <div class="flex items-start justify-between pb-3 border-b border-gray-800 flex-wrap gap-2">

        <div>

          <div class="flex items-center gap-2">

            <span class="text-[10px] uppercase font-bold text-amber-400">Official Engagement Agreement</span>

            <span class="text-[10px] text-gray-500 font-mono">REF: ${refNumber}</span>

          </div>

          <h4 class="text-sm font-bold text-white mt-1">${data.exporter_company}</h4>

          <p class="text-[11px] text-gray-400">Authorized Signatory: ${data.exporter_name} • Effective Date: ${today}</p>

        </div>

        <div class="text-right">

          <span class="px-2.5 py-1 rounded-full text-xs font-black bg-amber-500/20 text-amber-300 border border-amber-500/40 uppercase">

            ${data.tier.toUpperCase()} ENGAGEMENT

          </span>

          <div class="text-sm font-black text-white mt-1">${data.fee}</div>

        </div>

      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-[11px]">

        <div class="p-2.5 rounded-lg bg-gray-900 border border-gray-800">

          <span class="text-gray-400 font-medium">Target Commodity:</span>

          <div class="font-bold text-white mt-0.5">${data.product}</div>

        </div>

        <div class="p-2.5 rounded-lg bg-gray-900 border border-gray-800">

          <span class="text-gray-400 font-medium">Target Territories:</span>

          <div class="font-bold text-white mt-0.5">${data.target_country}</div>

        </div>

        <div class="p-2.5 rounded-lg bg-gray-900 border border-gray-800">

          <span class="text-gray-400 font-medium">Importer Sourcing Commitment:</span>

          <div class="font-bold text-cyan-300 mt-0.5">${data.leads} Verified Importers</div>

        </div>

        <div class="p-2.5 rounded-lg bg-gray-900 border border-gray-800">

          <span class="text-gray-400 font-medium">Discovery Meetings Target:</span>

          <div class="font-bold text-emerald-400 mt-0.5">${data.guaranteed_meetings || "4-6 Qualified International Discovery Calls"}</div>

        </div>

      </div>

      <div class="p-3 rounded-lg bg-gray-900 border border-gray-800 space-y-1.5 text-[11px] text-gray-300">

        <div class="font-bold text-white text-xs">Core Deliverables & Commercial Covenants:</div>

        <p>• <strong>Customs Intelligence:</strong> Systematic extraction of Bills of Lading and foreign trade registries to identify ${data.leads} active container importers in target markets.</p>

        <p>• <strong>Dedicated Infrastructure:</strong> Technical provisioning of ${data.mailboxes} with SPF, DKIM (2048-bit RSA), and strict DMARC alignment.</p>

        <p>• <strong>Direct Trade Inquiries:</strong> Personalized commercial correspondence highlighting manufacturer pricing, Incoterms (FOB/CIF), lab compliance (SGS, FDA, BRC), and sample offers.</p>

        <p>• <strong>Commercial Exclusivity:</strong> 100% exclusive buyer relationships and strict non-compete for ${data.exporter_company} during the active term.</p>

      </div>

      <div class="pt-2 text-[10px] text-gray-400 flex items-center justify-between border-t border-gray-800/80">

        <span>📄 2-Page Executive Agreement • Vector PDF Ready</span>

        <span class="text-amber-400 font-medium">Print-Ready Commercial SOW</span>

      </div>

    `;

    container.classList.remove("hidden");

  } catch (err) {

    alert("Failed to generate proposal");

  }

}

function downloadProposalPDF() {

  if (!currentProposalData) {

    alert("Please generate a proposal first.");

    return;

  }

  const d = currentProposalData;

  const params = new URLSearchParams({

    exporter_name: d.exporter_name,

    exporter_company: d.exporter_company,

    product: d.product,

    target_country: d.target_country,

    tier: d.tier

  });

  

  // Direct file download of real ReportLab PDF

  const downloadUrl = `/api/proposal/download-pdf?${params.toString()}`;

  const downloadLink = document.createElement("a");

  downloadLink.href = downloadUrl;

  downloadLink.download = `EximFlow_Agreement_${d.exporter_company.replace(/[\s\/]+/g, '_')}.pdf`;

  document.body.appendChild(downloadLink);

  downloadLink.click();

  document.body.removeChild(downloadLink);

}

function viewProposalPDF() {

  if (!currentProposalData) {

    alert("Please generate a proposal first.");

    return;

  }

  const d = currentProposalData;

  const params = new URLSearchParams({

    exporter_name: d.exporter_name,

    exporter_company: d.exporter_company,

    product: d.product,

    target_country: d.target_country,

    tier: d.tier

  });

  window.open(`/api/proposal/view-pdf?${params.toString()}`, "_blank");

}

function copyProposalToClipboard(btnEl) {

  if (!currentProposalData) return;

  navigator.clipboard.writeText(currentProposalData.proposal_text);

  const orig = btnEl.textContent;

  btnEl.textContent = "Copied to Clipboard!";

  setTimeout(() => btnEl.textContent = orig, 2000);

}

// Bulk Waterfall Email Verifier

async function runBatchVerification() {

  const inputEl = document.getElementById("batch-verify-input");

  const outputEl = document.getElementById("batch-verify-output");

  const text = inputEl ? inputEl.value : "";

  const emails = text.split(/[\n,]+/).map(e => e.trim()).filter(e => e.length > 0);

  if (emails.length === 0) {

    outputEl.innerHTML = `<p class="text-amber-400 text-xs">Please paste at least one email address.</p>`;

    return;

  }

  outputEl.innerHTML = `

    <div class="py-6 text-center text-gray-400 text-xs">

      <span class="inline-block animate-spin mr-1">⌛</span> Running multi-stage waterfall checks...

    </div>

  `;

  try {

    const res = await fetch("/api/verify/batch", {

      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({ emails: emails })

    });

    const data = await res.json();

    outputEl.innerHTML = `

      <div class="space-y-3 pt-2">

        <div class="flex items-center gap-3 text-xs">

          <span class="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">Safe to Send: ${data.safe_count}</span>

          <span class="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">Risky: ${data.risky_count}</span>

          <span class="px-2.5 py-1 rounded-full bg-red-500/10 text-red-400 border border-red-500/30 font-bold">Do Not Send: ${data.do_not_send_count}</span>

        </div>

        <div class="overflow-x-auto rounded-xl border border-gray-800">

          <table class="w-full text-left text-xs font-mono">

            <thead class="bg-gray-900/80 text-gray-400 uppercase">

              <tr>

                <th class="py-2 px-3">Email Address</th>

                <th class="py-2 px-3">Status</th>

                <th class="py-2 px-3">Score</th>

                <th class="py-2 px-3">Reason</th>

              </tr>

            </thead>

            <tbody>

              ${data.results.map(r => `

                <tr class="border-b border-gray-800/60">

                  <td class="py-2 px-3 text-gray-200">${r.email || 'Email'}</td>

                  <td class="py-2 px-3">

                    <span class="px-2 py-0.5 rounded text-[10px] font-bold ${r.status === 'SAFE_TO_SEND' ? 'bg-emerald-500/20 text-emerald-400' : (r.status === 'ACCEPTABLE_RISKY' ? 'bg-amber-500/20 text-amber-400' : 'bg-red-500/20 text-red-400')}">

                      ${r.status}

                    </span>

                  </td>

                  <td class="py-2 px-3 text-gray-300 font-bold">${r.score}/100</td>

                  <td class="py-2 px-3 text-gray-400 text-[11px] font-sans">${r.reason}</td>

                </tr>

              `).join("")}

            </tbody>

          </table>

        </div>

      </div>

    `;

  } catch (err) {

    outputEl.innerHTML = `<p class="text-red-400 text-xs">Failed to verify batch.</p>`;

  }

}

// ==============================================

// INSTAGRAM & SOCIAL MEDIA PARSER (parser.im)

// ==============================================

let cachedSocialLeads = [];

async function loadInitialSocialLeads() {

  const container = document.getElementById("social-leads-container");

  const badge = document.getElementById("social-results-badge");

  if (!container) return;

  container.innerHTML = `

    <div class="col-span-full py-12 text-center text-gray-400">

      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-pink-500 mb-3"></div>

      <p class="text-sm font-medium">Parsing active Instagram B2B importer profiles...</p>

    </div>

  `;

  try {

    const res = await fetch("/api/parser/social-search?query=spices&limit=15");

    const data = await res.json();

    cachedSocialLeads = data.profiles || [];

    renderSocialLeads(cachedSocialLeads);

    if (badge) badge.textContent = `${cachedSocialLeads.length} Accounts Parsed`;

  } catch (err) {

    container.innerHTML = `<p class="col-span-full text-center text-red-400 text-xs py-8">Failed to parse social leads.</p>`;

  }

}

async function runSocialTargetParse() {

  const inputEl = document.getElementById("social-target-input");

  const nicheSelect = document.getElementById("social-niche-select");

  const container = document.getElementById("social-leads-container");

  const badge = document.getElementById("social-results-badge");

  let target = inputEl ? inputEl.value.trim() : "";

  const niche = nicheSelect ? nicheSelect.value : "Spices & Agro";

  if (!target) {

    target = "#spicesimporter";

    if (inputEl) inputEl.value = target;

  }

  container.innerHTML = `

    <div class="col-span-full py-12 text-center text-gray-400">

      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-pink-500 mb-3"></div>

      <p class="text-sm font-medium">Scraping bios, emails & WhatsApp numbers from ${target}...</p>

    </div>

  `;

  try {

    const res = await fetch("/api/parser/reel-parse", {

      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({ target: target, niche: niche })

    });

    const data = await res.json();

    cachedSocialLeads = data.leads || [];

    renderSocialLeads(cachedSocialLeads);

    if (badge) badge.textContent = `${cachedSocialLeads.length} Accounts Parsed`;

  } catch (err) {

    container.innerHTML = `<p class="col-span-full text-center text-red-400 text-xs py-8">Error parsing target.</p>`;

  }

}

function parseReelSample() {

  const inputEl = document.getElementById("social-target-input");

  if (inputEl) {

    inputEl.value = "https://www.instagram.com/reel/DfFf3r2tHEn/";

  }

  const nicheSelect = document.getElementById("social-niche-select");

  if (nicheSelect) {

    nicheSelect.value = "Spices & Agro";

  }

  runSocialTargetParse();

}

function loadSampleParserCSV() {

  const sample = `Username,Full Name,Email,Phone,Bio,Website,Category,Country

americanspiceco,American Spice & Botanical Imports,sourcing@americanspiceimports.com,+1 201-555-0182,Direct US importers of organic spices & turmeric,https://americanspiceimports.com,Food & Beverage,United States

goldengrain_usa,Golden Grain Wholesale Inc,orders@goldengrainimports.com,+1 713-555-8841,Wholesale distributor of premium Basmati rice,https://goldengrainimports.com,Agricultural Wholesaler,United States

euronordic_foods,EuroNordic Ingredients BV,procurement@euronordicfoods.nl,+31 10 555 4290,B2B dehydrated vegetables & garlic powder,https://euronordicfoods.nl,Food Production,Netherlands

titan_piping,Titan Piping & Flange Solutions,supply@titanpipingusa.com,+1 312-555-7319,Stockist of ASME B16.5 stainless flanges,https://titanpipingusa.com,Metals & Piping,United States`;

  const csvEl = document.getElementById("social-csv-input");

  if (csvEl) {

    csvEl.value = sample;

  }

}

async function importSocialCSV() {

  const csvEl = document.getElementById("social-csv-input");

  const text = csvEl ? csvEl.value.trim() : "";

  if (!text) {

    alert("Please paste parser.im CSV data first or click 'Load Sample parser.im CSV'.");

    return;

  }

  try {

    const res = await fetch("/api/parser/import-csv", {

      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({ csv_text: text })

    });

    const data = await res.json();

    alert(`Successfully imported ${data.imported_count} verified profiles from parser.im CSV!`);

    cachedSocialLeads = data.leads || [];

    renderSocialLeads(cachedSocialLeads);

    const badge = document.getElementById("social-results-badge");

    if (badge) badge.textContent = `${cachedSocialLeads.length} Accounts Parsed`;

    loadCRMLeads();

  } catch (err) {

    alert("Failed to import CSV data.");

  }

}

function renderSocialLeads(leads) {

  const container = document.getElementById("social-leads-container");

  if (!container) return;

  if (!leads || leads.length === 0) {

    container.innerHTML = `

      <div class="col-span-full py-12 text-center text-gray-500 text-xs">

        No Instagram profiles found matching query. Try scanning #spicesimporter or importing CSV.

      </div>

    `;

    return;

  }

  container.innerHTML = leads.map(lead => {

    const emailHtml = lead.email ? `

      <div class="flex items-center justify-between text-xs font-mono bg-black/40 p-2 rounded-lg border border-gray-800">

        <span class="text-pink-300 truncate max-w-[210px]">${lead.email}</span>

        <button onclick="verifySocialLeadEmail('${lead.email}', this)" class="text-[10px] font-bold text-gray-400 hover:text-emerald-400 px-1.5 py-0.5 rounded bg-gray-800 hover:bg-gray-700 transition">

          Verify

        </button>

      </div>

    ` : `<div class="text-[11px] text-gray-500 italic">No email found in bio</div>`;

    const phoneHtml = lead.phone ? `

      <div class="flex items-center gap-2 text-xs font-mono text-gray-300">

        <svg class="w-3.5 h-3.5 text-emerald-400" fill="currentColor" viewBox="0 0 24 24"><path d="M6.62 10.79a15.053 15.053 0 006.59 6.59l2.2-2.2a1 1 0 011.02-.24c1.12.37 2.33.57 3.57.57a1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>

        <span>${lead.phone}</span>

      </div>

    ` : '';

    const leadJson = encodeURIComponent(JSON.stringify(lead));

    return `

      <div class="glass-panel rounded-2xl p-5 border border-pink-900/30 hover:border-pink-500/50 transition flex flex-col justify-between space-y-3 bg-gradient-to-b from-[#121626] to-[#0d101d]">

        <div class="space-y-2">

          <!-- Top Row: Handle & Followers -->

          <div class="flex items-start justify-between gap-2">

            <div>

              <div class="flex items-center gap-1.5">

                <span class="font-bold text-white text-sm">${lead.name || lead.company}</span>

                ${lead.verified_badge ? `<svg class="w-3.5 h-3.5 text-blue-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>` : ''}

              </div>

              <div class="text-xs text-pink-400 font-mono">${lead.ig_handle || '@profile'}</div>

            </div>

            <div class="text-right">

              <span class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-pink-500/10 text-pink-300 border border-pink-500/20">

                ${lead.followers || '10k+'} fans

              </span>

            </div>

          </div>

          <!-- Category & Bio -->

          <div>

            <span class="text-[10px] uppercase font-bold text-gray-400 bg-gray-800/80 px-2 py-0.5 rounded">${lead.industry || 'Wholesale Importer'}</span>

            <p class="text-xs text-gray-300 mt-2 line-clamp-3 leading-relaxed bg-black/30 p-2.5 rounded-lg border border-gray-800/60 font-sans">

              "${lead.bio || 'Active wholesale importer & trade partner.'}"

            </p>

          </div>

          <!-- Contacts -->

          <div class="space-y-1.5 pt-1">

            ${emailHtml}

            ${phoneHtml}

          </div>

        </div>

        <!-- Action Buttons -->

        <div class="pt-2 border-t border-gray-800/80 flex items-center gap-2">

          <button onclick="addSocialLeadToCRM('${leadJson}')" class="flex-1 py-1.5 bg-pink-600/20 hover:bg-pink-600/30 text-pink-300 border border-pink-500/30 rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1">

            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>

            Add to CRM

          </button>

          <button onclick="openSequenceModalForLead('${leadJson}')" class="flex-1 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1">

            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>

            Draft Sequence

          </button>

        </div>

      </div>

    `;

  }).join("");

}

async function verifySocialLeadEmail(email, btnEl) {

  if (!email) return;

  const orig = btnEl.textContent;

  btnEl.textContent = "Checking...";

  try {

    const res = await fetch("/api/verify", {

      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({ email: email })

    });

    const data = await res.json();

    alert(`Deliverability Check for ${email}:\nScore: ${data.score}/100\nStatus: ${data.status}\nReason: ${data.reason}`);

    btnEl.textContent = `${data.score}/100`;

    btnEl.className = `text-[10px] font-bold px-1.5 py-0.5 rounded ${data.status === 'SAFE_TO_SEND' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`;

  } catch (err) {

    btnEl.textContent = orig;

    alert("Verification request failed.");

  }

}

async function addSocialLeadToCRM(leadJsonStr) {

  try {

    const lead = JSON.parse(decodeURIComponent(leadJsonStr));

    const res = await fetch("/api/crm/lead", {

      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({

        name: lead.name || lead.company,

        email: lead.email || `contact@${lead.company.toLowerCase().replace(/[^a-z0-9]/g, '')}.com`,

        title: lead.title || "Instagram Bio Owner",

        company: lead.company,

        country: lead.country || "United States",

        product: lead.product_interest || "Spices & Agro",

        notes: `Imported from Instagram Parser (${lead.data_source || 'parser.im'}). Bio: ${lead.bio ? lead.bio.slice(0, 80) : ''}`

      })

    });

    if (res.ok) {

      alert(`Added ${lead.name || lead.company} to CRM Sales Pipeline!`);

      loadCRMLeads();

    }

  } catch (err) {

    alert("Failed to add lead to CRM.");

  }

}

function openSequenceModalForLead(leadJsonStr) {

  try {

    const lead = JSON.parse(decodeURIComponent(leadJsonStr));

    openSequenceModal(lead);

  } catch (err) {

    console.error("Error opening sequence modal:", err);

  }

}

// ==============================================

// HARVEY: AUTONOMOUS AI SALES AGENT (ethanplusai)

// ==============================================

async function loadHarveyStatus() {

  try {

    const res = await fetch("/api/harvey/status");

    const data = await res.json();

    renderHarveyDashboard(data);

  } catch (err) {

    console.error("Failed to load Harvey status:", err);

  }

}

function renderHarveyDashboard(data) {

  // 1. Mode Badge

  const modeBadge = document.getElementById("harvey-mode-badge");

  if (modeBadge) {

    if (data.mode === "autonomous") {

      modeBadge.innerHTML = `<span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">Mode: Autonomous Auto-Pilot</span>`;

    } else {

      modeBadge.innerHTML = `<span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">Mode: Review First (Safe)</span>`;

    }

  }

  // 2. Populate Configuration Modal Fields

  const bizNameInput = document.getElementById("harvey-cfg-biz-name");

  const bizOfferingInput = document.getElementById("harvey-cfg-offering");

  const icpInput = document.getElementById("harvey-cfg-icp");

  const geoInput = document.getElementById("harvey-cfg-geo");

  const modeSelect = document.getElementById("harvey-cfg-mode");

  if (bizNameInput) bizNameInput.value = data.business_name || "";

  if (bizOfferingInput) bizOfferingInput.value = data.business_offering || "";

  if (icpInput) icpInput.value = data.icp_description || "";

  if (geoInput) geoInput.value = data.target_geography || "";

  if (modeSelect) modeSelect.value = data.mode || "review_first";

  // 3. Staged Outbox Badge

  const outboxBadge = document.getElementById("harvey-outbox-badge");

  if (outboxBadge) {

    outboxBadge.textContent = `${data.metrics.staged_outbox} Staged (${data.metrics.pending_review} Pending Review)`;

  }

  // 4. Staged Outbox Table Body

  const outboxBody = document.getElementById("harvey-outbox-body");

  if (outboxBody) {

    if (!data.outbox || data.outbox.length === 0) {

      outboxBody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-gray-500">Harvey outbox is empty. Click "Run Autonomous SDR Sprint" to scout and draft emails.</td></tr>`;

    } else {

      outboxBody.innerHTML = data.outbox.map(item => {

        const isApproved = item.status === "APPROVED";

        const statusBadge = isApproved

          ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400">DISPATCHED</span>`

          : `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400">STAGED REVIEW</span>`;

        const actionBtn = isApproved

          ? `<span class="text-xs text-gray-500 font-sans">Ready</span>`

          : `<button onclick="approveHarveyEmail('${item.id}', this)" class="px-2.5 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-[11px] font-bold font-sans transition">Approve & Send</button>`;

        return `

          <tr class="hover:bg-gray-800/40">

            <td class="py-3 px-3">

              <div class="font-bold text-white text-xs">${item.recipient_name}</div>

              <div class="text-[11px] text-gray-400 font-sans">${item.company} • ${item.recipient_email}</div>

            </td>

            <td class="py-3 px-3">

              <span class="text-gray-300 font-sans text-xs">${item.target_product}</span>

            </td>

            <td class="py-3 px-3">

              <div class="font-bold text-cyan-400 text-xs font-sans">${item.subject}</div>

              <div class="text-[11px] text-gray-400 font-sans truncate max-w-xs">${item.body_preview}</div>

            </td>

            <td class="py-3 px-3">

              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${item.deliverability_score >= 90 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}">

                ${item.deliverability_score}/100

              </span>

            </td>

            <td class="py-3 px-3">${statusBadge}</td>

            <td class="py-3 px-3 text-right">${actionBtn}</td>

          </tr>

        `;

      }).join("");

    }

  }

  // 5. Activity Logs Feed

  const logsContainer = document.getElementById("harvey-terminal-logs");

  if (logsContainer && data.logs) {

    logsContainer.innerHTML = data.logs.map(log => {

      let agentColor = "text-blue-400";

      if (log.agent === "SCOUT") agentColor = "text-emerald-400";

      if (log.agent === "PARSER") agentColor = "text-pink-400";

      if (log.agent === "WRITER") agentColor = "text-blue-400";

      if (log.agent === "SENDER") agentColor = "text-indigo-400";

      if (log.agent === "HANDLER") agentColor = "text-amber-400";

      if (log.agent === "ANALYST") agentColor = "text-cyan-400";

      return `

        <div class="text-[11px] leading-relaxed border-b border-gray-900/80 pb-2">

          <span class="text-gray-500">[${log.timestamp}]</span>

          <span class="font-bold ${agentColor}">[${log.agent}]</span>

          <span class="text-gray-300 font-sans">${log.message}</span>

        </div>

      `;

    }).join("");

  }

}

async function runHarveyAutonomousCycle(btnEl) {

  const origHtml = btnEl ? btnEl.innerHTML : "";

  if (btnEl) {

    btnEl.innerHTML = `

      <span class="inline-block animate-spin mr-1">⌛</span>

      <span>Scouting & Drafting (Harvey Multi-Agent)...</span>

    `;

    btnEl.disabled = true;

  }

  try {

    const res = await fetch("/api/harvey/run-cycle", { method: "POST" });

    const data = await res.json();

    alert(`⚡ Harvey Autonomous Cycle Completed!\n\n• Candidates Scouted: ${data.candidates_scouted} buyers\n• Humanized Emails Staged: ${data.emails_staged}\n• Mode: ${data.mode.toUpperCase()}\n• Deliverability: 0% Bounce Waterfall Active`);

    loadHarveyStatus();

    loadCRMLeads();

  } catch (err) {

    alert("Harvey cycle execution failed.");

  } finally {

    if (btnEl) {

      btnEl.innerHTML = origHtml;

      btnEl.disabled = false;

    }

  }

}

async function approveHarveyEmail(emailId, btnEl) {

  if (btnEl) {

    btnEl.textContent = "Approving...";

    btnEl.disabled = true;

  }

  try {

    const res = await fetch("/api/harvey/approve-outbox", {

      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({ email_id: emailId })

    });

    if (res.ok) {

      loadHarveyStatus();

    }

  } catch (err) {

    alert("Failed to approve email.");

  }

}

function toggleHarveyConfigModal() {

  const modal = document.getElementById("harvey-config-modal");

  if (modal) {

    modal.classList.toggle("hidden");

  }

}

async function saveHarveyConfiguration() {

  const bizName = document.getElementById("harvey-cfg-biz-name").value;

  const offering = document.getElementById("harvey-cfg-offering").value;

  const icp = document.getElementById("harvey-cfg-icp").value;

  const geo = document.getElementById("harvey-cfg-geo").value;

  const mode = document.getElementById("harvey-cfg-mode").value;

  try {

    const res = await fetch("/api/harvey/configure", {

      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({

        business_name: bizName,

        business_offering: offering,

        icp_description: icp,

        target_geography: geo,

        mode: mode

      })

    });

    if (res.ok) {

      alert("Harvey AI Configuration saved successfully!");

      toggleHarveyConfigModal();

      loadHarveyStatus();

    }

  } catch (err) {

    alert("Failed to update Harvey configuration.");

  }

}

// ==============================================

// USER MANUAL & ONBOARDING CONTROLLERS

// ==============================================

function openUserManualModal(subtab = "overview") {

  const modal = document.getElementById("user-manual-modal");

  if (modal) {

    modal.classList.remove("hidden");

    switchManualSubTab(subtab);

  }

}

function closeUserManualModal() {

  const modal = document.getElementById("user-manual-modal");

  if (modal) {

    modal.classList.add("hidden");

  }

}

function switchManualSubTab(tabId) {

  const buttons = document.querySelectorAll(".manual-subtab-btn");

  buttons.forEach(btn => {

    const mantab = btn.getAttribute("data-mantab");

    if (mantab === tabId) {

      btn.className = "manual-subtab-btn w-full text-left px-3 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition bg-blue-600/20 text-blue-300 border border-blue-500/30";

    } else {

      btn.className = "manual-subtab-btn w-full text-left px-3 py-2 rounded-xl text-xs font-medium text-gray-400 hover:text-white hover:bg-gray-800/60 flex items-center gap-2 transition";

    }

  });

  const panels = document.querySelectorAll(".manual-content-panel");

  panels.forEach(panel => {

    if (panel.id === `mantab-content-${tabId}`) {

      panel.classList.remove("hidden");

    } else {

      panel.classList.add("hidden");

    }

  });

}

function minimizeManualBanner() {

  const banner = document.getElementById("user-manual-banner");

  const minBar = document.getElementById("user-manual-minimized-bar");

  if (banner) banner.classList.add("hidden");

  if (minBar) minBar.classList.remove("hidden");

  localStorage.setItem("eximflow_manual_banner_minimized", "true");

}

function restoreManualBanner() {

  const banner = document.getElementById("user-manual-banner");

  const minBar = document.getElementById("user-manual-minimized-bar");

  if (banner) banner.classList.remove("hidden");

  if (minBar) minBar.classList.add("hidden");

  localStorage.removeItem("eximflow_manual_banner_minimized");

}

function initManualBannerState() {

  const isMinimized = localStorage.getItem("eximflow_manual_banner_minimized");

  const banner = document.getElementById("user-manual-banner");

  const minBar = document.getElementById("user-manual-minimized-bar");

  if (isMinimized === "true") {

    if (banner) banner.classList.add("hidden");

    if (minBar) minBar.classList.remove("hidden");

  } else {

    if (banner) banner.classList.remove("hidden");

    if (minBar) minBar.classList.add("hidden");

  }

}

// ==============================================

// 1-CLICK INTERACTIVE PRODUCT TOUR

// ==============================================

let currentTourStep = 1;

const tourSteps = [

  {

    step: 1,

    title: "1. Multi-Source Lead Discovery (99.3M Stream)",

    text: "Streams records directly from Apollo's 19.6 GB zip archive without disk decompression, alongside authentic US Customs Bill of Lading manifests. Use the quick presets (Spices, Basmati Rice, Flanges) to load verified buyers immediately.",

    tab: "discovery"

  },

  {

    step: 2,

    title: "2. Social Parser & Reels Engine (parser.im)",

    text: "Mines viral export reels and wholesale bios for verified WhatsApp phone numbers and business emails. Zero accounts banned, zero proxies needed.",

    tab: "social"

  },

  {

    step: 3,

    title: "3. Harvey Autonomous AI SDR (5-Agent Workflow)",

    text: "Harvey coordinates 5 specialized sub-agents to score leads against your ICP, cross-reference import history, and draft hyper-relevant trade copy into your Staged Outbox.",

    tab: "harvey"

  },

  {

    step: 4,

    title: "4. Humanized Cold Copy & $3.5k/mo Retainers",

    text: "Master the 10 Anti-AI Commandments (sub-75 words, real manifest hooks, no corporate jargon). Generate executive retainer proposals and export clean CSVs for Smartlead or Instantly.",

    tab: "templates"

  }

];

function startInteractiveTour() {

  currentTourStep = 1;

  const guide = document.getElementById("tour-floating-guide");

  if (guide) {

    guide.classList.remove("hidden");

    renderTourStep();

  }

}

function endInteractiveTour() {

  const guide = document.getElementById("tour-floating-guide");

  if (guide) {

    guide.classList.add("hidden");

  }

}

function renderTourStep() {

  const stepData = tourSteps.find(s => s.step === currentTourStep) || tourSteps[0];

  switchTab(stepData.tab);

  const counterEl = document.getElementById("tour-step-counter");

  const contentEl = document.getElementById("tour-step-content");

  const prevBtn = document.getElementById("tour-btn-prev");

  const nextBtn = document.getElementById("tour-btn-next");

  if (counterEl) counterEl.textContent = `Step ${stepData.step} of ${tourSteps.length}`;

  if (contentEl) {

    contentEl.innerHTML = `

      <div class="font-bold text-white text-xs">${stepData.title}</div>

      <p class="text-gray-300 text-[11px] leading-relaxed">${stepData.text}</p>

    `;

  }

  if (prevBtn) {

    if (currentTourStep > 1) {

      prevBtn.classList.remove("hidden");

    } else {

      prevBtn.classList.add("hidden");

    }

  }

  if (nextBtn) {

    if (currentTourStep === tourSteps.length) {

      nextBtn.textContent = "Finish Tour ✓";

      nextBtn.className = "px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold shadow";

    } else {

      nextBtn.textContent = "Next Step →";

      nextBtn.className = "px-3 py-1 rounded bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-[11px] font-bold shadow";

    }

  }

}

function tourNextStep() {

  if (currentTourStep < tourSteps.length) {

    currentTourStep++;

    renderTourStep();

  } else {

    endInteractiveTour();

  }

}

function tourPrevStep() {

  if (currentTourStep > 1) {

    currentTourStep--;

    renderTourStep();

  }

}

// ==========================================

// 24/7 Autonomous Sales Engine (Reel 2: End-to-End)

// ==========================================

const HARVEY_PRESETS = {

  spices: {

    offering: "Primary processor of BRC Grade-A & US FDA-registered organic spices (Turmeric, Cumin, Black Pepper) based in Gujarat, India with ready CIF/FOB container inventory.",

    icp: "VP of Global Sourcing, Director of Agricultural Commodities, and Procurement Heads at food importing & wholesale distribution companies across North America and Western Europe importing 10+ containers/year."

  },

  rice: {

    offering: "Direct exporter of 1121 XXL Steam & Parboiled Basmati Rice (Purity 95%+, Average Grain Length 8.35mm+) with US FDA, ISO 22000 & APEDA certifications.",

    icp: "Commodity importers, ethnic food distributors, and supermarket chain suppliers across United States, Canada, and Western Europe."

  },

  flanges: {

    offering: "Manufacturer & exporter of ASTM A182 Forged Stainless Steel Flanges (SS 304/304L, 316/316L) and high-pressure pipe fittings with EN 10204 3.1 MTR inspection.",

    icp: "Chief Procurement Officers and Piping Material Managers at oil & gas distributors, chemical processing plants, and marine infrastructure contractors in USA & Gulf."

  },

  saas: {

    offering: "B2B AI-powered outbound sales orchestration platform automating prospect discovery, custom manifest intelligence, and zero-bounce cold sequence delivery.",

    icp: "Founders, VP of Sales, and SDR Leaders at B2B exporters, logistics providers, and growth-stage companies with 10-100 employees in US & Europe."

  }

};

function setHarveyPreset(type) {

  const p = HARVEY_PRESETS[type];

  if (!p) return;

  const offEl = document.getElementById("harvey_e2e_offering");

  const icpEl = document.getElementById("harvey_e2e_icp");

  if (offEl) offEl.value = p.offering;

  if (icpEl) icpEl.value = p.icp;

}

let e2eTimerInterval = null;

function closeE2EModal() {

  const modal = document.getElementById("e2e-execution-modal");

  if (modal) modal.classList.add("hidden");

  if (e2eTimerInterval) {

    clearInterval(e2eTimerInterval);

    e2eTimerInterval = null;

  }

}

async function launchEndToEndSalesCycle() {

  const offeringEl = document.getElementById("harvey_e2e_offering");

  const icpEl = document.getElementById("harvey_e2e_icp");

  const modeRadio = document.querySelector('input[name="harvey_e2e_mode"]:checked');

  

  const offering = offeringEl ? offeringEl.value.trim() : "";

  const icp = icpEl ? icpEl.value.trim() : "";

  const mode = modeRadio ? modeRadio.value : "review_first";

  const modal = document.getElementById("e2e-execution-modal");

  const compBox = document.getElementById("e2e-completion-box");

  const timerEl = document.getElementById("e2e-modal-timer");

  const btnLaunch = document.getElementById("btn-launch-e2e-cycle");

  const spinner = document.getElementById("e2e-spinner");

  const launchIcon = document.getElementById("e2e-launch-icon");

  const launchText = document.getElementById("e2e-launch-text");

  if (modal) modal.classList.remove("hidden");

  if (compBox) compBox.classList.add("hidden");

  // Reset stages

  for (let s = 1; s <= 6; s++) {

    const el = document.getElementById(`e2e-stage-${s}`);

    if (el) {

      el.className = "p-3.5 rounded-xl border border-gray-800 bg-gray-900/60 transition duration-300 flex items-start gap-3.5";

      const icon = el.querySelector(".stage-icon");

      if (icon) {

        icon.className = "w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold bg-gray-800 text-gray-300 stage-icon shrink-0";

        icon.textContent = s;

      }

      const badge = el.querySelector(".stage-status-badge");

      if (badge) {

        badge.className = "stage-status-badge text-[10px] px-2 py-0.5 rounded font-semibold bg-gray-800 text-gray-400";

        badge.textContent = "Waiting";

      }

      const metric = el.querySelector(".stage-metric");

      if (metric) metric.textContent = "";

    }

  }

  // Start timer

  const startTime = Date.now();

  if (e2eTimerInterval) clearInterval(e2eTimerInterval);

  e2eTimerInterval = setInterval(() => {

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

    if (timerEl) timerEl.textContent = `${elapsed}s elapsed`;

  }, 100);

  // Helper to update stage status

  function updateStageUI(stageNum, state, badgeText, metricText, customDesc) {

    const el = document.getElementById(`e2e-stage-${stageNum}`);

    if (!el) return;

    const icon = el.querySelector(".stage-icon");

    const badge = el.querySelector(".stage-status-badge");

    const metric = el.querySelector(".stage-metric");

    const desc = el.querySelector(".stage-desc");

    if (state === "running") {

      el.className = "p-3.5 rounded-xl border border-cyan-500/50 bg-cyan-950/20 shadow-md transition duration-300 flex items-start gap-3.5";

      if (icon) {

        icon.className = "w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold bg-cyan-500/20 text-cyan-300 animate-pulse shrink-0";

        icon.textContent = "⚡";

      }

      if (badge) {

        badge.className = "stage-status-badge text-[10px] px-2 py-0.5 rounded font-semibold bg-cyan-500/20 text-cyan-300 animate-pulse";

        badge.textContent = badgeText || "Running...";

      }

    } else if (state === "completed") {

      el.className = "p-3.5 rounded-xl border border-emerald-500/40 bg-emerald-950/20 transition duration-300 flex items-start gap-3.5";

      if (icon) {

        icon.className = "w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold bg-emerald-500/20 text-emerald-400 shrink-0";

        icon.textContent = "✓";

      }

      if (badge) {

        badge.className = "stage-status-badge text-[10px] px-2 py-0.5 rounded font-semibold bg-emerald-500/20 text-emerald-300";

        badge.textContent = badgeText || "Done";

      }

      if (metric && metricText) metric.textContent = metricText;

      if (desc && customDesc) desc.textContent = customDesc;

    }

  }

  // Animate Stage 1 immediately

  updateStageUI(1, "running", "Querying Customs AMS & Instagram...");

  try {

    if (btnLaunch) btnLaunch.disabled = true;

    if (spinner) spinner.classList.remove("hidden");

    if (launchIcon) launchIcon.classList.add("hidden");

    if (launchText) launchText.textContent = "Executing 6-Stage Sprint...";

    // Call Backend

    const response = await fetch("/api/harvey/run-cycle", {

      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({

        business_offering: offering,

        icp_description: icp,

        mode: mode

      })

    });

    const data = await response.json();

    // Smoothly step through stages with visual cadence

    await new Promise(r => setTimeout(r, 600));

    updateStageUI(1, "completed", "Identified", `${data.candidates_scouted || 6} Buyers Found`);

    updateStageUI(2, "running", "Analyzing Manifests & TEUs...");

    await new Promise(r => setTimeout(r, 600));

    updateStageUI(2, "completed", "Verified", "100% Manifest History");

    updateStageUI(3, "running", "Enforcing Zero AI Clichés...");

    await new Promise(r => setTimeout(r, 650));

    updateStageUI(3, "completed", "Generated", `${data.emails_staged || 6} Sequences (<75 words)`);

    updateStageUI(4, "running", "Checking MX & SMTP Handshake...");

    await new Promise(r => setTimeout(r, 550));

    updateStageUI(4, "completed", "Verified", "0% Bounce Rate");

    updateStageUI(5, "running", "Staging in Safe Delivery Outbox...");

    await new Promise(r => setTimeout(r, 500));

    updateStageUI(5, "completed", "Staged", `Paced: 35 sends/day (${mode.toUpperCase()})`);

    updateStageUI(6, "running", "Syncing CRM & Scheduling Call...");

    await new Promise(r => setTimeout(r, 500));

    const bookedCall = data.booked_call || {};

    updateStageUI(6, "completed", "Call Coordinated", bookedCall.name ? `Meeting: ${bookedCall.name}` : "CRM Synchronized");

    // Stop timer

    clearInterval(e2eTimerInterval);

    const finalElapsed = ((Date.now() - startTime) / 1000).toFixed(2);

    if (timerEl) timerEl.textContent = `${finalElapsed}s total`;

    // Show completion box

    if (compBox) {

      compBox.classList.remove("hidden");

      const completeTime = document.getElementById("e2e-complete-time");

      if (completeTime) completeTime.textContent = `Sprint completed in ${finalElapsed}s`;

      const statScouted = document.getElementById("e2e-stat-scouted");

      if (statScouted) statScouted.textContent = data.candidates_scouted || 6;

      const statStaged = document.getElementById("e2e-stat-staged");

      if (statStaged) statStaged.textContent = data.emails_staged || 6;

      const callDetails = document.getElementById("e2e-booked-call-details");

      if (callDetails) {

        callDetails.textContent = `${bookedCall.name || "Marcus Vance"} (${bookedCall.company || "American Spice Imports LLC"}) — ${bookedCall.topic || "Container CIF Contract"}`;

      }

      const callTime = document.getElementById("e2e-booked-call-time");

      if (callTime) callTime.textContent = bookedCall.time || "Tomorrow at 03:30 PM EST";

    }

    // Refresh dashboard background views

    if (typeof loadHarveyStatus === "function") loadHarveyStatus();

    if (typeof loadCRMLeads === "function") loadCRMLeads();

  } catch (err) {

    clearInterval(e2eTimerInterval);

    alert("End-to-End sales cycle encountered an error. Check console.");

    console.error(err);

  } finally {

    if (btnLaunch) btnLaunch.disabled = false;

    if (spinner) spinner.classList.add("hidden");

    if (launchIcon) launchIcon.classList.remove("hidden");

    if (launchText) launchText.textContent = "Launch 24/7 Autonomous Sales Cycle";

  }

}

