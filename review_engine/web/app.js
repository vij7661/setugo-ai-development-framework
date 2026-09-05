"use strict";

const $ = (id) => document.getElementById(id);

function escapeText(value) {
  return value == null ? "" : String(value);
}

function isoFromSqliteUtc(value) {
  if (!value) return null;
  const text = String(value);
  return text.includes("T") ? text + (/[zZ]|[+-]\d\d:\d\d$/.test(text) ? "" : "Z") : text.replace(" ", "T") + "Z";
}

function formatIst(value) {
  const iso = isoFromSqliteUtc(value);
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return escapeText(value);
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit",
    hour12: false,
  }).formatToParts(d).reduce((acc, p) => { acc[p.type] = p.value; return acc; }, {});
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {"Content-Type": "application/json", ...(options.headers || {})},
    cache: "no-store",
  });
  let payload;
  try { payload = await response.json(); } catch (_) { payload = {error: `HTTP ${response.status}`}; }
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

function badgeClass(state) {
  if (state === "CONVERGED_PASS") return "state-pass";
  if (state === "HUMAN_REQUIRED") return "state-human";
  return "state-neutral";
}

async function loadHealth() {
  try {
    const health = await api("/health");
    $("healthBadge").textContent = health.status === "ok" ? "SYSTEM READY" : "SYSTEM DEGRADED";
    $("healthBadge").classList.add(health.status === "ok" ? "ok" : "warn");
    $("assurance").textContent = `${health.assurance_mode} · action execution disabled`;
    const container = $("reviewers");
    container.replaceChildren();
    for (const role of ["R1", "R2", "R3"]) {
      const cfg = health.reviewers[role];
      const card = document.createElement("article");
      card.className = "reviewer-card";
      const title = document.createElement("strong");
      title.textContent = role;
      const detail = document.createElement("span");
      detail.textContent = cfg ? `${cfg.provider} · ${cfg.model}` : "Not configured";
      const meta = document.createElement("small");
      meta.textContent = cfg ? `${cfg.sku}/${cfg.deployment_path} · ${cfg.qualification_ref || "no qualification"}` : "Review unavailable";
      card.append(title, detail, meta);
      container.append(card);
    }
  } catch (err) {
    $("healthBadge").textContent = "UNAVAILABLE";
    $("healthBadge").classList.add("warn");
    $("assurance").textContent = err.message;
  }
}

function makeRequestId() {
  if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") return globalThis.crypto.randomUUID();
  return `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function renderDecision(result) {
  $("resultPanel").classList.remove("hidden");
  const state = $("decisionState");
  state.textContent = result.state;
  state.className = badgeClass(result.state);

  const meta = $("decisionMeta");
  meta.replaceChildren();
  const entries = [
    ["Request", result.request_id],
    ["Assurance", result.assurance_mode],
    ["Evidence chain", result.session_chain_valid ? "VALID" : "INVALID"],
    ["Action authorized", result.action_authorized ? "YES" : "NO"],
    ["Human action approval", result.human_action_approval_required ? "REQUIRED" : "NOT REQUIRED"],
    ["Artifact hash", result.artifact_hash || "—"],
  ];
  for (const [key, value] of entries) {
    const item = document.createElement("div");
    const k = document.createElement("small"); k.textContent = key;
    const v = document.createElement("strong"); v.textContent = escapeText(value);
    item.append(k, v); meta.append(item);
  }

  const reasons = $("decisionReasons"); reasons.replaceChildren();
  for (const reason of (result.reasons || [])) {
    const li = document.createElement("li"); li.textContent = reason; reasons.append(li);
  }
  $("finalOutput").textContent = result.final_output || "No final output. Review requires external/human resolution.";
}

async function runReview(event) {
  event.preventDefault();
  const button = $("runButton");
  button.disabled = true; button.textContent = "Running review…";
  try {
    const target = $("targetEnvironment").value;
    const payload = {
      request_id: makeRequestId(),
      user_input: $("userInput").value,
      operation_class: $("operationClass").value,
      task_type: $("taskType").value.trim() || "GENERAL",
      connected_tool_capabilities: [],
      evidence_complete: true,
    };
    if (target) payload.target_environment = target;
    const result = await api("/review", {method: "POST", body: JSON.stringify(payload)});
    renderDecision(result);
    await loadHistory();
  } catch (err) {
    $("resultPanel").classList.remove("hidden");
    $("decisionState").textContent = "EXECUTION ERROR";
    $("decisionState").className = "state-human";
    $("decisionReasons").replaceChildren();
    const li = document.createElement("li"); li.textContent = err.message; $("decisionReasons").append(li);
    $("finalOutput").textContent = "The backend did not produce a governed decision.";
  } finally {
    button.disabled = false; button.textContent = "Run governed review";
  }
}

async function loadHistory() {
  const body = $("sessions");
  try {
    const data = await api("/sessions?limit=100");
    body.replaceChildren();
    for (const session of data.sessions || []) {
      const tr = document.createElement("tr");
      const id = document.createElement("td");
      const link = document.createElement("button");
      link.type = "button"; link.className = "link-button"; link.textContent = session.session_id;
      link.addEventListener("click", () => loadEvents(session.session_id)); id.append(link);
      const status = document.createElement("td");
      const pill = document.createElement("span"); pill.className = badgeClass(session.final_state); pill.textContent = session.final_state || "IN PROGRESS"; status.append(pill);
      const started = document.createElement("td"); started.textContent = formatIst(session.started_at_utc);
      const updated = document.createElement("td"); updated.textContent = formatIst(session.updated_at_utc);
      const evidence = document.createElement("td"); evidence.textContent = session.chain_valid ? `VALID · ${session.event_count} events` : "INVALID";
      tr.append(id, status, started, updated, evidence); body.append(tr);
    }
    if (!body.children.length) {
      const tr = document.createElement("tr"); const td = document.createElement("td"); td.colSpan = 5; td.textContent = "No review sessions yet."; tr.append(td); body.append(tr);
    }
  } catch (err) {
    body.replaceChildren();
    const tr = document.createElement("tr"); const td = document.createElement("td"); td.colSpan = 5; td.textContent = `History unavailable: ${err.message}`; tr.append(td); body.append(tr);
  }
}

async function loadEvents(sessionId) {
  const panel = $("eventPanel"); const timeline = $("events");
  panel.classList.remove("hidden"); $("eventSession").textContent = sessionId;
  timeline.replaceChildren();
  try {
    const data = await api(`/sessions/${encodeURIComponent(sessionId)}/events`);
    for (const event of data.events || []) {
      const item = document.createElement("article"); item.className = "event";
      const head = document.createElement("div"); head.className = "event-head";
      const type = document.createElement("strong"); type.textContent = `${event.seq}. ${event.event_type}`;
      const time = document.createElement("span"); time.textContent = `${formatIst(event.created_at)} IST`;
      head.append(type, time);
      const payload = document.createElement("pre"); payload.textContent = JSON.stringify(event.payload, null, 2);
      const hash = document.createElement("small"); hash.textContent = `hash ${event.event_hash}`;
      item.append(head, payload, hash); timeline.append(item);
    }
    panel.scrollIntoView({behavior: "smooth", block: "start"});
  } catch (err) {
    const p = document.createElement("p"); p.textContent = `Evidence unavailable: ${err.message}`; timeline.append(p);
  }
}

$("reviewForm").addEventListener("submit", runReview);
$("refreshHistory").addEventListener("click", loadHistory);

Promise.all([loadHealth(), loadHistory()]);
