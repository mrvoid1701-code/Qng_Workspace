const els = {
  workspacePath: document.getElementById("workspacePath"),
  statusText: document.getElementById("statusText"),
  systemOutput: document.getElementById("systemOutput"),
  clearConsoleBtn: document.getElementById("clearConsoleBtn"),

  tabNav: document.getElementById("tabNav"),

  lintBtn: document.getElementById("lintBtn"),
  syncBtn: document.getElementById("syncBtn"),
  exportBtn: document.getElementById("exportBtn"),
  themeSelect: document.getElementById("themeSelect"),

  treeRoot: document.getElementById("treeRoot"),
  treeFilter: document.getElementById("treeFilter"),
  refreshBtn: document.getElementById("refreshBtn"),
  newFileBtn: document.getElementById("newFileBtn"),
  saveBtn: document.getElementById("saveBtn"),
  activeFileTitle: document.getElementById("activeFileTitle"),
  dirtyBadge: document.getElementById("dirtyBadge"),
  editor: document.getElementById("editor"),
  preview: document.getElementById("preview"),

  missionCards: document.getElementById("missionCards"),
  runJournal: document.getElementById("runJournal"),
  p1TableBody: document.getElementById("p1TableBody"),
  missionRefreshBtn: document.getElementById("missionRefreshBtn"),

  wbPriority: document.getElementById("wbPriority"),
  wbStatus: document.getElementById("wbStatus"),
  wbSearch: document.getElementById("wbSearch"),
  wbApplyBtn: document.getElementById("wbApplyBtn"),
  wbResetBtn: document.getElementById("wbResetBtn"),
  wbRefreshBtn: document.getElementById("wbRefreshBtn"),
  wbTableBody: document.getElementById("wbTableBody"),
  wbDetail: document.getElementById("wbDetail"),
  wbForm: document.getElementById("wbForm"),
  wbFormTestId: document.getElementById("wbFormTestId"),
  wbFormStatus: document.getElementById("wbFormStatus"),
  wbFormAuthenticity: document.getElementById("wbFormAuthenticity"),
  wbFormLeakageRisk: document.getElementById("wbFormLeakageRisk"),
  wbFormNegativeControl: document.getElementById("wbFormNegativeControl"),
  wbFormLastRun: document.getElementById("wbFormLastRun"),
  wbFormMetric: document.getElementById("wbFormMetric"),
  wbFormDecision: document.getElementById("wbFormDecision"),
  wbFormNext: document.getElementById("wbFormNext"),
  wbOpenEvidenceBtn: document.getElementById("wbOpenEvidenceBtn"),
  wbOpenDerivationBtn: document.getElementById("wbOpenDerivationBtn"),
  wbOpenClaimBtn: document.getElementById("wbOpenClaimBtn"),

  resultsPriority: document.getElementById("resultsPriority"),
  resultsStatus: document.getElementById("resultsStatus"),
  resultsSearch: document.getElementById("resultsSearch"),
  resultsApplyBtn: document.getElementById("resultsApplyBtn"),
  resultsResetBtn: document.getElementById("resultsResetBtn"),
  resultsRefreshBtn: document.getElementById("resultsRefreshBtn"),
  resultsExportPackageBtn: document.getElementById("resultsExportPackageBtn"),
  resultsDetailToggleBtn: document.getElementById("resultsDetailToggleBtn"),
  resultsTableBody: document.getElementById("resultsTableBody"),
  resultsDetail: document.getElementById("resultsDetail"),
  resultsMetricsBody: document.getElementById("resultsMetricsBody"),
  resultsSlider: document.getElementById("resultsSlider"),
  resultsSliderImage: document.getElementById("resultsSliderImage"),
  resultsSliderCaption: document.getElementById("resultsSliderCaption"),
  resultsSliderCounter: document.getElementById("resultsSliderCounter"),
  resultsSliderPrevBtn: document.getElementById("resultsSliderPrevBtn"),
  resultsSliderNextBtn: document.getElementById("resultsSliderNextBtn"),
  resultsArtifacts: document.getElementById("resultsArtifacts"),

  exportsRefreshBtn: document.getElementById("exportsRefreshBtn"),
  exportsGate: document.getElementById("exportsGate"),
  exportsValidatedBtn: document.getElementById("exportsValidatedBtn"),
  exportsDossierBtn: document.getElementById("exportsDossierBtn"),
  exportsDossierMdOnly: document.getElementById("exportsDossierMdOnly"),
  exportsPackageMode: document.getElementById("exportsPackageMode"),
  exportsPackageTest: document.getElementById("exportsPackageTest"),
  exportsPackageMdOnly: document.getElementById("exportsPackageMdOnly"),
  exportsPackageBtn: document.getElementById("exportsPackageBtn"),
  exportsPackageHint: document.getElementById("exportsPackageHint"),
  exportsFiles: document.getElementById("exportsFiles"),
  exportsOutput: document.getElementById("exportsOutput"),

  graphPriority: document.getElementById("graphPriority"),
  graphResetBtn: document.getElementById("graphResetBtn"),
  graphOpenSelectedBtn: document.getElementById("graphOpenSelectedBtn"),
  graphRefreshBtn: document.getElementById("graphRefreshBtn"),
  graphCounts: document.getElementById("graphCounts"),
  graphSvg: document.getElementById("graphSvg"),
  graphDetail: document.getElementById("graphDetail"),
};

const state = {
  workspace: "",
  tree: [],
  activePath: "",
  selectedDir: "",
  savedContent: "",
  collapsedDirs: new Set(),
  filter: "",

  activeTab: "explorer",

  mission: null,
  workbench: null,
  selectedTestId: "",
  results: null,
  selectedResultTestId: "",
  resultDetail: null,
  resultsDetailCollapsed: false,
  resultImageArtifacts: [],
  resultImageIndex: 0,
  exports: null,
  theme: "light",
  graph: null,
  activeGraphNodeId: "",
};

const EXEC_STATUSES = [
  "queued-p1",
  "queued-p2",
  "queued-p3",
  "in-progress",
  "pass",
  "fail",
  "blocked",
];
const AUTHENTICITY_LEVELS = ["gold", "silver", "bronze"];
const LEAKAGE_RISK_LEVELS = ["low", "med", "high"];
const NEGATIVE_CONTROL_STATES = ["none", "planned", "done"];

const TAB_ORDER = ["explorer", "mission", "workbench", "results", "exports", "graph"];
const THEME_STORAGE_KEY = "qng-workbench-theme";
const THEMES = ["light", "dark", "green-dark", "green-deep"];
const GRAPH_PRIORITY_STORAGE_KEY = "qng-workbench-graph-priority";
const GRAPH_SELECTED_NODE_STORAGE_KEY = "qng-workbench-graph-selected-node";

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function statusClass(status) {
  const value = String(status || "").toLowerCase();
  if (value === "pass") return "status-pass";
  if (value === "fail" || value === "blocked") return "status-fail";
  if (value === "in-progress") return "status-in-progress";
  return "";
}

function normalizeChoice(value, allowed, fallback) {
  const raw = String(value || "").trim().toLowerCase();
  return allowed.includes(raw) ? raw : fallback;
}

function applyTheme(theme, persist = true) {
  const normalized = normalizeChoice(theme, THEMES, "light");
  state.theme = normalized;
  document.body.dataset.theme = normalized;
  if (els.themeSelect && els.themeSelect.value !== normalized) {
    els.themeSelect.value = normalized;
  }
  if (persist) {
    localStorage.setItem(THEME_STORAGE_KEY, normalized);
  }
}

function initTheme() {
  const saved = localStorage.getItem(THEME_STORAGE_KEY) || "light";
  applyTheme(saved, false);
}

function setGraphSelectedNode(nodeId) {
  state.activeGraphNodeId = String(nodeId || "");
  if (state.activeGraphNodeId) {
    localStorage.setItem(GRAPH_SELECTED_NODE_STORAGE_KEY, state.activeGraphNodeId);
  } else {
    localStorage.removeItem(GRAPH_SELECTED_NODE_STORAGE_KEY);
  }
  updateGraphOpenSelectedButton();
}

function initGraphPreferences() {
  if (els.graphPriority) {
    const savedPriority = (localStorage.getItem(GRAPH_PRIORITY_STORAGE_KEY) || "").toUpperCase();
    if (["P1", "P2", "P3", "ALL"].includes(savedPriority)) {
      els.graphPriority.value = savedPriority;
    }
  }
  const savedNode = localStorage.getItem(GRAPH_SELECTED_NODE_STORAGE_KEY) || "";
  state.activeGraphNodeId = savedNode;
}

function formatBytes(bytes) {
  const value = Number(bytes || 0);
  if (!Number.isFinite(value) || value <= 0) {
    return "0 B";
  }
  const units = ["B", "KB", "MB", "GB"];
  let size = value;
  let idx = 0;
  while (size >= 1024 && idx < units.length - 1) {
    size /= 1024;
    idx += 1;
  }
  return `${size.toFixed(size >= 10 || idx === 0 ? 0 : 1)} ${units[idx]}`;
}

function artifactUrl(path) {
  return `/api/artifact?path=${encodeURIComponent(path)}`;
}

function exportFileUrl(path) {
  return `/api/export-file?path=${encodeURIComponent(path)}`;
}

function setStatus(message, isError = false) {
  const safe = escapeHtml(message);
  els.statusText.innerHTML = isError ? `<strong>${safe}</strong>` : safe;
}

function appendConsole(message) {
  const stamp = new Date().toLocaleTimeString();
  els.systemOutput.textContent += `[${stamp}] ${message}\n`;
  els.systemOutput.scrollTop = els.systemOutput.scrollHeight;
}

async function apiGet(path) {
  const response = await fetch(path);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Request failed (${response.status})`);
  }
  return data;
}

async function apiPost(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Request failed (${response.status})`);
  }
  return data;
}

function switchTab(tab) {
  if (!TAB_ORDER.includes(tab)) {
    return;
  }
  state.activeTab = tab;
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tab);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `tab-${tab}`);
  });
}

function isDirty() {
  return Boolean(state.activePath) && els.editor.value !== state.savedContent;
}

function updateDirtyUi() {
  const dirty = isDirty();
  els.dirtyBadge.classList.toggle("hidden", !dirty);
  if (dirty) {
    setStatus(`Unsaved changes in ${state.activePath}`);
  }
}

function updateTitle() {
  els.activeFileTitle.textContent = state.activePath || "No file selected";
  els.saveBtn.disabled = !state.activePath;
}

function normalizePath(path) {
  return path.replace(/\\/g, "/").replace(/^\/+/, "");
}

function getParentDir(path) {
  const normalized = normalizePath(path);
  const idx = normalized.lastIndexOf("/");
  return idx >= 0 ? normalized.slice(0, idx) : "";
}

function filterTree(nodes, query) {
  if (!query) {
    return nodes;
  }
  const q = query.toLowerCase();
  const out = [];
  for (const node of nodes) {
    const selfMatch = node.name.toLowerCase().includes(q);
    if (node.type === "file") {
      if (selfMatch) {
        out.push(node);
      }
      continue;
    }
    const children = filterTree(node.children || [], query);
    if (selfMatch || children.length > 0) {
      out.push({ ...node, children });
    }
  }
  return out;
}

function pickFirstEditableFile(nodes) {
  for (const node of nodes) {
    if (node.type === "file" && node.editable) {
      return node.path;
    }
    if (node.type === "dir") {
      const candidate = pickFirstEditableFile(node.children || []);
      if (candidate) {
        return candidate;
      }
    }
  }
  return "";
}

function iconForFile(name) {
  const lower = name.toLowerCase();
  if (lower.endsWith(".md")) return "[MD]";
  if (lower.endsWith(".py")) return "[PY]";
  if (lower.endsWith(".json")) return "[JS]";
  if (lower.endsWith(".txt")) return "[TX]";
  if (lower.endsWith(".ps1")) return "[PS]";
  return "[F]";
}

function createTreeRow(node, depth) {
  const row = document.createElement("button");
  row.type = "button";
  row.className = "tree-row";
  row.style.paddingLeft = `${8 + depth * 14}px`;

  const icon = document.createElement("span");
  icon.className = "tree-icon";
  row.append(icon);

  const label = document.createElement("span");
  label.textContent = node.name;
  row.append(label);

  if (node.type === "dir") {
    const collapsed = state.collapsedDirs.has(node.path);
    icon.textContent = collapsed ? "[+]" : "[-]";
    row.addEventListener("click", () => {
      state.selectedDir = node.path;
      if (collapsed) {
        state.collapsedDirs.delete(node.path);
      } else {
        state.collapsedDirs.add(node.path);
      }
      renderTree();
      setStatus(`Selected folder: ${node.path}`);
    });
    if (state.selectedDir === node.path) {
      row.classList.add("active");
    }
    return row;
  }

  icon.textContent = iconForFile(node.name);
  row.addEventListener("click", () => {
    openFile(node.path, node.editable);
  });
  if (state.activePath === node.path) {
    row.classList.add("active");
  }
  return row;
}

function renderTreeNodes(nodes, root, depth = 0) {
  for (const node of nodes) {
    const wrapper = document.createElement("div");
    wrapper.className = "tree-node";
    wrapper.append(createTreeRow(node, depth));
    root.append(wrapper);

    if (node.type === "dir" && !state.collapsedDirs.has(node.path)) {
      const children = node.children || [];
      if (children.length > 0) {
        const childContainer = document.createElement("div");
        childContainer.className = "tree-children";
        wrapper.append(childContainer);
        renderTreeNodes(children, childContainer, depth + 1);
      }
    }
  }
}

function renderTree() {
  els.treeRoot.innerHTML = "";
  const filtered = filterTree(state.tree, state.filter);
  if (filtered.length === 0) {
    const msg = document.createElement("div");
    msg.className = "tree-muted";
    msg.textContent = "No matching files.";
    els.treeRoot.append(msg);
    return;
  }
  renderTreeNodes(filtered, els.treeRoot, 0);
}

function formatInline(line) {
  let out = escapeHtml(line);
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  out = out.replace(/\$([^$\n]+)\$/g, '<span class="formula-inline">$1</span>');
  out = out.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    '<a href="$2" target="_blank" rel="noreferrer noopener">$1</a>'
  );
  return out;
}

function markdownToHtml(text) {
  const lines = text.split(/\r?\n/);
  const html = [];
  let inUl = false;
  let inOl = false;
  let inCode = false;
  let inMath = false;
  let mathBuffer = [];

  const closeLists = () => {
    if (inUl) {
      html.push("</ul>");
      inUl = false;
    }
    if (inOl) {
      html.push("</ol>");
      inOl = false;
    }
  };

  const closeMath = () => {
    if (!inMath) return;
    html.push(`<pre class="formula-block">${escapeHtml(mathBuffer.join("\n"))}</pre>`);
    mathBuffer = [];
    inMath = false;
  };

  for (const raw of lines) {
    const line = raw || "";

    if (line.trim().startsWith("$$")) {
      closeLists();
      if (inMath) {
        closeMath();
      } else {
        inMath = true;
        mathBuffer = [];
      }
      continue;
    }

    if (inMath) {
      mathBuffer.push(line);
      continue;
    }

    if (line.startsWith("```")) {
      closeLists();
      if (!inCode) {
        inCode = true;
        html.push("<pre><code>");
      } else {
        inCode = false;
        html.push("</code></pre>");
      }
      continue;
    }

    if (inCode) {
      html.push(`${escapeHtml(line)}\n`);
      continue;
    }

    if (/^\s*$/.test(line)) {
      closeLists();
      continue;
    }

    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      closeLists();
      const level = heading[1].length;
      html.push(`<h${level}>${formatInline(heading[2])}</h${level}>`);
      continue;
    }

    if (/^---+$/.test(line.trim())) {
      closeLists();
      html.push("<hr />");
      continue;
    }

    const ul = line.match(/^\s*[-*+]\s+(.*)$/);
    if (ul) {
      if (inOl) {
        html.push("</ol>");
        inOl = false;
      }
      if (!inUl) {
        html.push("<ul>");
        inUl = true;
      }
      html.push(`<li>${formatInline(ul[1])}</li>`);
      continue;
    }

    const ol = line.match(/^\s*\d+\.\s+(.*)$/);
    if (ol) {
      if (inUl) {
        html.push("</ul>");
        inUl = false;
      }
      if (!inOl) {
        html.push("<ol>");
        inOl = true;
      }
      html.push(`<li>${formatInline(ol[1])}</li>`);
      continue;
    }

    const quote = line.match(/^\s*>\s?(.*)$/);
    if (quote) {
      closeLists();
      html.push(`<blockquote>${formatInline(quote[1])}</blockquote>`);
      continue;
    }

    closeLists();
    html.push(`<p>${formatInline(line)}</p>`);
  }

  closeLists();
  closeMath();
  if (inCode) {
    html.push("</code></pre>");
  }

  return html.join("\n");
}

function updatePreview() {
  if (!state.activePath) {
    els.preview.innerHTML = '<p class="tree-muted">No file selected.</p>';
    return;
  }

  const content = els.editor.value;
  const lower = state.activePath.toLowerCase();
  if (lower.endsWith(".md")) {
    els.preview.innerHTML = markdownToHtml(content);
    return;
  }
  if (lower.endsWith(".tex")) {
    els.preview.innerHTML = `<pre class="formula-block">${escapeHtml(content)}</pre>`;
    return;
  }
  els.preview.innerHTML = `<pre>${escapeHtml(content)}</pre>`;
}

async function openFile(path, editable) {
  if (!editable) {
    setStatus("File is not editable text.", true);
    return;
  }

  if (isDirty() && path !== state.activePath) {
    const ok = window.confirm("You have unsaved changes. Continue without saving?");
    if (!ok) return;
  }

  try {
    setStatus(`Opening ${path} ...`);
    const data = await apiGet(`/api/file?path=${encodeURIComponent(path)}`);
    state.activePath = data.path;
    state.savedContent = data.content || "";
    els.editor.value = state.savedContent;
    state.selectedDir = getParentDir(state.activePath);
    updateTitle();
    updateDirtyUi();
    updatePreview();
    renderTree();
    setStatus(`Opened ${state.activePath}`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function saveCurrentFile() {
  if (!state.activePath) return;
  try {
    const content = els.editor.value;
    await apiPost("/api/file", { path: state.activePath, content });
    state.savedContent = content;
    updateDirtyUi();
    setStatus(`Saved ${state.activePath}`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function createNewFile() {
  const baseDir = state.selectedDir || getParentDir(state.activePath) || "01_notes";
  const suggestion = `${baseDir}/new-note.md`.replace(/^\/+/, "");
  const requested = window.prompt("Relative path for new file", suggestion);
  if (!requested) return;

  const normalized = normalizePath(requested);
  if (!normalized.includes(".")) {
    setStatus("Please include a file extension.", true);
    return;
  }

  const idx = normalized.lastIndexOf("/");
  const dir = idx >= 0 ? normalized.slice(0, idx) : "";
  const name = idx >= 0 ? normalized.slice(idx + 1) : normalized;

  try {
    await apiPost("/api/new", { dir, name });
    await loadTree();
    await openFile(normalized, true);
    setStatus(`Created ${normalized}`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function loadTree() {
  try {
    const data = await apiGet("/api/tree");
    state.workspace = data.workspace;
    state.tree = data.items || [];
    els.workspacePath.textContent = state.workspace;
    renderTree();

    if (!state.activePath) {
      const first = pickFirstEditableFile(state.tree);
      if (first) {
        await openFile(first, true);
      }
    }
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function openWorkspacePath(path) {
  const normalized = normalizePath(path || "");
  if (!normalized || normalized.toLowerCase() === "n/a") {
    return;
  }
  switchTab("explorer");
  await openFile(normalized, true);
}

function statValue(counter, key) {
  return Number((counter && counter[key]) || 0);
}

function renderMissionCards(summary) {
  const queued =
    statValue(summary.tests_by_exec_status, "queued-p1") +
    statValue(summary.tests_by_exec_status, "queued-p2") +
    statValue(summary.tests_by_exec_status, "queued-p3");
  const release = summary.export_release || {};
  const releaseLabel = release.ready ? "ready" : "blocked";

  const cards = [
    { key: "Claims", value: summary.claims_total || 0 },
    { key: "Tests", value: summary.tests_total || 0 },
    { key: "Queued", value: queued },
    { key: "In Progress", value: statValue(summary.tests_by_exec_status, "in-progress") },
    { key: "Pass", value: statValue(summary.tests_by_exec_status, "pass") },
    { key: "Gold Pass", value: statValue(summary.pass_by_authenticity, "gold") },
    { key: "Fail", value: statValue(summary.tests_by_exec_status, "fail") },
    { key: "Blocked", value: statValue(summary.tests_by_exec_status, "blocked") },
    { key: "Release", value: releaseLabel },
    { key: "Runs", value: summary.runs_total || 0 },
  ];

  els.missionCards.innerHTML = cards
    .map((card) => `<div class="card"><div class="k">${escapeHtml(card.key)}</div><div class="v">${card.value}</div></div>`)
    .join("");
}

function renderRunJournal(runs) {
  if (!runs || runs.length === 0) {
    els.runJournal.innerHTML = '<div class="tree-muted">No runs logged yet.</div>';
    return;
  }

  els.runJournal.innerHTML = runs
    .map(
      (run) =>
        `<div class="run-item"><div class="run-id">${escapeHtml(run.run_id)}</div><div>${escapeHtml(
          run.date
        )} | ${escapeHtml(run.scope)}</div><div>${escapeHtml(run.result_summary)}</div></div>`
    )
    .join("");
}

function buildStatusSelect(value) {
  const select = document.createElement("select");
  EXEC_STATUSES.forEach((status) => {
    const option = document.createElement("option");
    option.value = status;
    option.textContent = status;
    if (status === value) {
      option.selected = true;
    }
    select.append(option);
  });
  return select;
}

async function quickUpdateTest(testId, execStatus, note = "") {
  try {
    const payload = {
      test_id: testId,
      exec_status: execStatus,
      last_run: todayIso(),
      decision_note: note || `Mission update: ${execStatus}`,
    };
    await apiPost("/api/test/update", payload);
    await Promise.all([loadMission(false), loadWorkbench(false), loadResults(false), loadExports(false), loadGraph(false)]);
    setStatus(`Updated ${testId} to ${execStatus}`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

function renderP1Queue(rows) {
  els.p1TableBody.innerHTML = "";
  if (!rows || rows.length === 0) {
    const tr = document.createElement("tr");
    tr.innerHTML = '<td colspan="5" class="tree-muted">No P1 tests available.</td>';
    els.p1TableBody.append(tr);
    return;
  }

  rows.forEach((row) => {
    const tr = document.createElement("tr");

    const testTd = document.createElement("td");
    testTd.textContent = row.test_id;
    tr.append(testTd);

    const claimTd = document.createElement("td");
    claimTd.textContent = row.claim_id;
    tr.append(claimTd);

    const statusTd = document.createElement("td");
    const select = buildStatusSelect(row.exec_status || "queued-p1");
    statusTd.append(select);
    tr.append(statusTd);

    const actionTd = document.createElement("td");
    actionTd.textContent = row.next_action || "";
    tr.append(actionTd);

    const toolsTd = document.createElement("td");
    toolsTd.className = "inline-actions";

    const saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.className = "btn tiny primary";
    saveBtn.textContent = "Save";
    saveBtn.addEventListener("click", () => {
      quickUpdateTest(row.test_id, select.value, `P1 queue update: ${select.value}`);
    });

    const openBtn = document.createElement("button");
    openBtn.type = "button";
    openBtn.className = "btn tiny ghost";
    openBtn.textContent = "Evidence";
    openBtn.disabled = !row.evidence_path;
    openBtn.addEventListener("click", () => {
      openWorkspacePath(row.evidence_path);
    });

    toolsTd.append(saveBtn, openBtn);
    tr.append(toolsTd);

    els.p1TableBody.append(tr);
  });
}

function renderMission() {
  if (!state.mission) {
    els.missionCards.innerHTML = '<div class="tree-muted">Mission data unavailable.</div>';
    els.runJournal.innerHTML = "";
    els.p1TableBody.innerHTML = "";
    return;
  }

  renderMissionCards(state.mission.summary || {});
  renderRunJournal(state.mission.runs || []);
  renderP1Queue(state.mission.p1_focus || []);
}

async function loadMission(showStatus = true) {
  try {
    const data = await apiGet("/api/mission");
    state.mission = data;
    renderMission();
    if (showStatus) {
      setStatus("Mission refreshed");
    }
  } catch (error) {
    setStatus(error.message, true);
  }
}

function workbenchFilters() {
  return {
    priority: els.wbPriority.value.trim(),
    status: els.wbStatus.value.trim(),
    q: els.wbSearch.value.trim(),
  };
}

function queryStringFromFilters(filters) {
  const params = new URLSearchParams();
  if (filters.priority) params.set("priority", filters.priority);
  if (filters.status) params.set("status", filters.status);
  if (filters.q) params.set("q", filters.q);
  return params.toString();
}

function getClaimById(claimId) {
  if (!state.workbench || !state.workbench.claims) return null;
  return state.workbench.claims.find((claim) => claim.claim_id === claimId) || null;
}

function getSelectedTest() {
  if (!state.workbench || !state.workbench.tests) return null;
  return state.workbench.tests.find((test) => test.test_id === state.selectedTestId) || null;
}

function renderWorkbenchTable() {
  const tests = (state.workbench && state.workbench.tests) || [];
  els.wbTableBody.innerHTML = "";

  if (tests.length === 0) {
    const tr = document.createElement("tr");
    tr.innerHTML = '<td colspan="8" class="tree-muted">No tests match current filters.</td>';
    els.wbTableBody.append(tr);
    return;
  }

  tests.forEach((test) => {
    const tr = document.createElement("tr");
    tr.classList.toggle("active", test.test_id === state.selectedTestId);

    tr.innerHTML = `
      <td>${escapeHtml(test.test_id)}</td>
      <td>${escapeHtml(test.claim_id)}</td>
      <td>${escapeHtml(test.priority)}</td>
      <td class="${statusClass(test.exec_status)}">${escapeHtml(test.exec_status)}</td>
      <td>${escapeHtml(test.authenticity || "")}</td>
      <td>${escapeHtml(test.leakage_risk || "")}</td>
      <td>${escapeHtml(test.negative_control || "")}</td>
      <td>${escapeHtml(test.last_run || "")}</td>
    `;

    tr.addEventListener("click", () => {
      state.selectedTestId = test.test_id;
      renderWorkbenchTable();
      renderWorkbenchDetail();
    });

    els.wbTableBody.append(tr);
  });
}

function renderWorkbenchDetail() {
  const test = getSelectedTest();
  if (!test) {
    els.wbDetail.textContent = "Select a test row to inspect and update.";
    els.wbForm.classList.add("hidden");
    return;
  }

  const claim = getClaimById(test.claim_id);
  const claimStatement = claim ? claim.statement : test.claim_statement;

  els.wbDetail.innerHTML = `
    <p><strong>${escapeHtml(test.test_id)}</strong> linked to <code>${escapeHtml(test.claim_id)}</code></p>
    <p>${escapeHtml(claimStatement || "")}</p>
    <p><strong>Formula:</strong> <code>${escapeHtml(test.formula_anchor || "")}</code></p>
    <p><strong>Dataset:</strong> ${escapeHtml(test.dataset_environment || "")}</p>
    <p><strong>Method:</strong> ${escapeHtml(test.method || "")}</p>
    <p><strong>Review meta:</strong> authenticity=<code>${escapeHtml(
      test.authenticity || ""
    )}</code>, leakage_risk=<code>${escapeHtml(test.leakage_risk || "")}</code>, negative_control=<code>${escapeHtml(
      test.negative_control || ""
    )}</code></p>
    <p><strong>Evidence:</strong> <code>${escapeHtml(test.evidence_path || "")}</code></p>
    <p><strong>Derivation:</strong> <code>${escapeHtml(test.derivation || "")}</code></p>
  `;

  els.wbForm.classList.remove("hidden");
  els.wbFormTestId.value = test.test_id;
  els.wbFormStatus.value = EXEC_STATUSES.includes(test.exec_status) ? test.exec_status : "queued-p3";
  els.wbFormAuthenticity.value = normalizeChoice(test.authenticity, AUTHENTICITY_LEVELS, "bronze");
  els.wbFormLeakageRisk.value = normalizeChoice(test.leakage_risk, LEAKAGE_RISK_LEVELS, "high");
  els.wbFormNegativeControl.value = normalizeChoice(test.negative_control, NEGATIVE_CONTROL_STATES, "none");
  els.wbFormLastRun.value = /^\d{4}-\d{2}-\d{2}$/.test(test.last_run || "") ? test.last_run : todayIso();
  els.wbFormMetric.value = test.metric_value === "TODO" ? "" : test.metric_value || "";
  els.wbFormDecision.value = test.decision_note === "TODO" ? "" : test.decision_note || "";
  els.wbFormNext.value = test.next_action || "";

  els.wbOpenEvidenceBtn.disabled = !test.evidence_path;
  els.wbOpenDerivationBtn.disabled = !test.derivation || test.derivation.toLowerCase() === "n/a";
  els.wbOpenClaimBtn.disabled = !claim || !claim.claim_file;

  els.wbOpenEvidenceBtn.onclick = () => openWorkspacePath(test.evidence_path);
  els.wbOpenDerivationBtn.onclick = () => openWorkspacePath(test.derivation);
  els.wbOpenClaimBtn.onclick = () => openWorkspacePath(claim ? claim.claim_file : "");
}

async function loadWorkbench(showStatus = true) {
  try {
    const query = queryStringFromFilters(workbenchFilters());
    const data = await apiGet(`/api/workbench${query ? `?${query}` : ""}`);
    state.workbench = data;

    if (state.selectedTestId) {
      const stillExists = (data.tests || []).some((test) => test.test_id === state.selectedTestId);
      if (!stillExists) {
        state.selectedTestId = "";
      }
    }

    renderWorkbenchTable();
    renderWorkbenchDetail();

    if (showStatus) {
      setStatus("Workbench refreshed");
    }
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function saveWorkbenchUpdate(event) {
  event.preventDefault();
  const testId = els.wbFormTestId.value.trim();
  if (!testId) return;

  try {
    const execStatus = els.wbFormStatus.value;
    const authenticity = els.wbFormAuthenticity.value;
    const leakageRisk = els.wbFormLeakageRisk.value;
    const negativeControl = els.wbFormNegativeControl.value;
    if (execStatus === "pass") {
      if (!AUTHENTICITY_LEVELS.includes(authenticity)) {
        throw new Error("Pass rows require authenticity: gold|silver|bronze.");
      }
      if (!LEAKAGE_RISK_LEVELS.includes(leakageRisk)) {
        throw new Error("Pass rows require leakage_risk: low|med|high.");
      }
      if (!NEGATIVE_CONTROL_STATES.includes(negativeControl)) {
        throw new Error("Pass rows require negative_control: none|planned|done.");
      }
    }

    await apiPost("/api/test/update", {
      test_id: testId,
      exec_status: execStatus,
      last_run: els.wbFormLastRun.value || todayIso(),
      metric_value: els.wbFormMetric.value,
      decision_note: els.wbFormDecision.value,
      next_action: els.wbFormNext.value,
      rationale: els.wbFormDecision.value,
      authenticity: authenticity,
      leakage_risk: leakageRisk,
      negative_control: negativeControl,
    });

    await Promise.all([loadMission(false), loadWorkbench(false), loadResults(false), loadExports(false), loadGraph(false)]);
    setStatus(`Saved update for ${testId}`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

function resultsFilters() {
  return {
    priority: els.resultsPriority.value.trim(),
    status: els.resultsStatus.value.trim(),
    q: els.resultsSearch.value.trim(),
  };
}

function getSelectedResultRow() {
  if (!state.results || !state.results.tests) return null;
  return state.results.tests.find((test) => test.test_id === state.selectedResultTestId) || null;
}

function applyResultsDetailCollapse() {
  const stack = document.querySelector(".result-detail-stack");
  if (!stack || !els.resultsDetailToggleBtn) return;

  const collapsed = Boolean(state.resultsDetailCollapsed);
  stack.classList.toggle("results-detail-collapsed", collapsed);
  els.resultsDetailToggleBtn.textContent = collapsed ? "Show Detail" : "Hide Detail";
  els.resultsDetailToggleBtn.setAttribute("aria-pressed", collapsed ? "true" : "false");
}

function renderResultsMetrics(metrics) {
  els.resultsMetricsBody.innerHTML = "";
  if (!metrics || metrics.length === 0) {
    const tr = document.createElement("tr");
    tr.innerHTML = '<td colspan="2" class="tree-muted">No fit summary metrics available.</td>';
    els.resultsMetricsBody.append(tr);
    return;
  }

  metrics.forEach((entry) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><code>${escapeHtml(entry.metric || "")}</code></td>
      <td>${escapeHtml(entry.value || "")}</td>
    `;
    els.resultsMetricsBody.append(tr);
  });
}

function clampResultImageIndex() {
  const total = state.resultImageArtifacts.length;
  if (total <= 0) {
    state.resultImageIndex = 0;
    return;
  }
  if (state.resultImageIndex < 0) {
    state.resultImageIndex = total - 1;
  }
  if (state.resultImageIndex >= total) {
    state.resultImageIndex = 0;
  }
}

function renderArtifactSlider() {
  const images = state.resultImageArtifacts || [];
  const total = images.length;

  if (total === 0) {
    els.resultsSlider.classList.add("hidden");
    els.resultsSliderImage.removeAttribute("src");
    els.resultsSliderCaption.textContent = "Select an artifact image.";
    els.resultsSliderCounter.textContent = "0 / 0";
    els.resultsSliderPrevBtn.disabled = true;
    els.resultsSliderNextBtn.disabled = true;
    return;
  }

  clampResultImageIndex();
  const current = images[state.resultImageIndex];
  els.resultsSlider.classList.remove("hidden");
  els.resultsSliderImage.src = artifactUrl(current.path);
  els.resultsSliderImage.alt = current.name || "Artifact image";
  els.resultsSliderCounter.textContent = `${state.resultImageIndex + 1} / ${total}`;
  els.resultsSliderCaption.textContent = `${current.name || "image"} | ${formatBytes(current.size)}`;
  const disableNav = total <= 1;
  els.resultsSliderPrevBtn.disabled = disableNav;
  els.resultsSliderNextBtn.disabled = disableNav;
}

function setResultSliderImages(artifacts) {
  const previous = state.resultImageArtifacts[state.resultImageIndex];
  const previousPath = previous ? previous.path : "";
  state.resultImageArtifacts = (artifacts || []).filter((artifact) => artifact.is_image);

  if (!state.resultImageArtifacts.length) {
    state.resultImageIndex = 0;
    renderArtifactSlider();
    return;
  }

  if (previousPath) {
    const matched = state.resultImageArtifacts.findIndex((artifact) => artifact.path === previousPath);
    state.resultImageIndex = matched >= 0 ? matched : 0;
  } else {
    state.resultImageIndex = 0;
  }
  renderArtifactSlider();
}

function selectResultSliderImage(path) {
  const idx = state.resultImageArtifacts.findIndex((artifact) => artifact.path === path);
  if (idx < 0) return;
  state.resultImageIndex = idx;
  renderArtifactSlider();
}

function stepResultSlider(delta) {
  if (!state.resultImageArtifacts.length) return;
  state.resultImageIndex += delta;
  clampResultImageIndex();
  renderArtifactSlider();
}

function renderResultsArtifacts(artifacts) {
  els.resultsArtifacts.innerHTML = "";
  setResultSliderImages(artifacts);
  if (!artifacts || artifacts.length === 0) {
    els.resultsArtifacts.innerHTML = '<div class="tree-muted">No artifacts found for this test.</div>';
    return;
  }

  artifacts.forEach((artifact) => {
    const card = document.createElement("article");
    card.className = "artifact-card";

    if (artifact.is_image) {
      card.classList.add("artifact-card-image");
      const image = document.createElement("img");
      image.className = "artifact-thumb";
      image.loading = "lazy";
      image.alt = artifact.name || "artifact image";
      image.src = artifactUrl(artifact.path);
      image.addEventListener("click", () => {
        selectResultSliderImage(artifact.path);
      });
      card.append(image);
    } else {
      const placeholder = document.createElement("div");
      placeholder.className = "artifact-placeholder";
      placeholder.textContent = (artifact.content_type || "file").toUpperCase();
      card.append(placeholder);
    }

    const meta = document.createElement("div");
    meta.className = "artifact-meta";
    meta.innerHTML = `
      <div class="artifact-name">${escapeHtml(artifact.name || "")}</div>
      <div>${escapeHtml(formatBytes(artifact.size))}</div>
      <div><code>${escapeHtml(artifact.path || "")}</code></div>
    `;
    card.append(meta);

    const actions = document.createElement("div");
    actions.className = "artifact-actions";

    const openBtn = document.createElement("button");
    openBtn.type = "button";
    openBtn.className = "btn tiny ghost";
    openBtn.textContent = "Open";
    openBtn.addEventListener("click", () => {
      window.open(artifactUrl(artifact.path), "_blank", "noopener,noreferrer");
    });
    actions.append(openBtn);

    if (artifact.is_text) {
      const openInExplorerBtn = document.createElement("button");
      openInExplorerBtn.type = "button";
      openInExplorerBtn.className = "btn tiny ghost";
      openInExplorerBtn.textContent = "Open in Explorer";
      openInExplorerBtn.addEventListener("click", () => {
        openWorkspacePath(artifact.path);
      });
      actions.append(openInExplorerBtn);
    }

    card.append(actions);
    els.resultsArtifacts.append(card);
  });
}

function buildResultInterpretation(detail) {
  if (!detail || !detail.metric_map) return "";
  const metric = detail.metric_map || {};
  const notes = [];
  const rec = metric.pass_recommendation;
  if (rec) {
    notes.push(`Runner recommendation: ${rec}.`);
  }

  const deltaChi2 = Number(metric.delta_chi2);
  const deltaAic = Number(metric.delta_aic);
  if (Number.isFinite(deltaChi2)) {
    notes.push(`Delta chi2 is ${deltaChi2.toExponential(3)} (negative supports memory model).`);
  }
  if (Number.isFinite(deltaAic)) {
    notes.push(`Delta AIC is ${deltaAic.toExponential(3)} (<= -10 is usually strong support).`);
  }

  if (!notes.length) return "";
  return notes.join(" ");
}

function renderResultsTable() {
  const tests = (state.results && state.results.tests) || [];
  els.resultsTableBody.innerHTML = "";

  if (tests.length === 0) {
    const tr = document.createElement("tr");
    tr.innerHTML = '<td colspan="8" class="tree-muted">No test results match current filters.</td>';
    els.resultsTableBody.append(tr);
    return;
  }

  tests.forEach((test) => {
    const tr = document.createElement("tr");
    tr.classList.toggle("active", test.test_id === state.selectedResultTestId);
    tr.innerHTML = `
      <td>${escapeHtml(test.test_id)}</td>
      <td class="${statusClass(test.exec_status)}">${escapeHtml(test.exec_status || "")}</td>
      <td>${escapeHtml(test.authenticity || "")}</td>
      <td>${escapeHtml(test.leakage_risk || "")}</td>
      <td>${escapeHtml(test.negative_control || "")}</td>
      <td>${escapeHtml(test.last_run || "")}</td>
      <td>${escapeHtml(String(test.artifact_count || 0))} files / ${escapeHtml(
        String(test.image_count || 0)
      )} images</td>
      <td>${escapeHtml(test.metric_value || "")}</td>
    `;

    tr.addEventListener("click", async () => {
      state.selectedResultTestId = test.test_id;
      state.resultDetail = null;
      renderResultsTable();
      renderResultsDetail();
      await loadResultDetail(test.test_id, false);
    });
    els.resultsTableBody.append(tr);
  });
}

function renderResultsDetail() {
  const summary = getSelectedResultRow();
  if (!summary) {
    els.resultsDetail.textContent = "Select a test result to inspect artifacts and metrics.";
    renderResultsMetrics([]);
    renderResultsArtifacts([]);
    if (els.resultsExportPackageBtn) {
      els.resultsExportPackageBtn.disabled = true;
      els.resultsExportPackageBtn.onclick = null;
    }
    return;
  }

  if (els.resultsExportPackageBtn) {
    els.resultsExportPackageBtn.disabled = false;
    els.resultsExportPackageBtn.onclick = () =>
      runExportAction(
        "/api/system/export/package",
        { test_id: summary.test_id, md_only: false },
        `claim-package export (${summary.test_id})`
      );
  }

  if (!state.resultDetail || !state.resultDetail.test || state.resultDetail.test.test_id !== summary.test_id) {
    els.resultsDetail.innerHTML = `<p><strong>${escapeHtml(
      summary.test_id
    )}</strong> selected. Loading detailed artifacts and metrics...</p>`;
    renderResultsMetrics([]);
    renderResultsArtifacts([]);
    return;
  }

  const detail = state.resultDetail;
  const test = detail.test || {};
  const evidence = detail.evidence || {};
  const interpretation = buildResultInterpretation(detail);

  els.resultsDetail.innerHTML = `
    <p><strong>${escapeHtml(test.test_id || "")}</strong> linked to <code>${escapeHtml(test.claim_id || "")}</code></p>
    <p>${escapeHtml(test.claim_statement || "")}</p>
    <p><strong>Status:</strong> <span class="${statusClass(test.exec_status)}">${escapeHtml(test.exec_status || "")}</span></p>
    <p><strong>Review meta:</strong> authenticity=<code>${escapeHtml(
      test.authenticity || ""
    )}</code>, leakage_risk=<code>${escapeHtml(test.leakage_risk || "")}</code>, negative_control=<code>${escapeHtml(
      test.negative_control || ""
    )}</code></p>
    <p><strong>Last run:</strong> ${escapeHtml(test.last_run || "")}</p>
    <p><strong>Evidence:</strong> <code>${escapeHtml(test.evidence_path || "")}</code></p>
    <p><strong>Derivation:</strong> <code>${escapeHtml(test.derivation || "")}</code></p>
    <p><strong>Decision note:</strong> ${escapeHtml(test.decision_note || "")}</p>
    <p><strong>Objective:</strong> ${escapeHtml(evidence.objective || "")}</p>
    <p><strong>Method:</strong> ${escapeHtml(evidence.method || test.method || "")}</p>
    <p><strong>Rationale:</strong> ${escapeHtml(evidence.rationale || "")}</p>
    <p><strong>Interpretation:</strong> ${escapeHtml(interpretation || "No automated interpretation available yet.")}</p>
    <p><strong>Run manifest:</strong> <code>${escapeHtml(detail.run_manifest ? detail.run_manifest.path : "")}</code></p>
  `;

  renderResultsMetrics(detail.metrics || []);
  renderResultsArtifacts(detail.artifacts || []);
}

async function loadResultDetail(testId, showStatus = true) {
  if (!testId) {
    state.resultDetail = null;
    renderResultsDetail();
    return;
  }

  try {
    const data = await apiGet(`/api/results/detail?test_id=${encodeURIComponent(testId)}`);
    if (state.selectedResultTestId !== testId) {
      return;
    }
    state.resultDetail = data;
    renderResultsDetail();
    if (showStatus) {
      setStatus(`Loaded result detail: ${testId}`);
    }
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function loadResults(showStatus = true) {
  try {
    const query = queryStringFromFilters(resultsFilters());
    const data = await apiGet(`/api/results${query ? `?${query}` : ""}`);
    state.results = data;

    if (state.selectedResultTestId) {
      const exists = (data.tests || []).some((test) => test.test_id === state.selectedResultTestId);
      if (!exists) {
        state.selectedResultTestId = "";
      }
    }
    if (!state.selectedResultTestId && data.tests && data.tests.length > 0) {
      state.selectedResultTestId = data.tests[0].test_id;
    }

    state.resultDetail = null;
    renderResultsTable();
    renderResultsDetail();

    if (state.selectedResultTestId) {
      await loadResultDetail(state.selectedResultTestId, false);
    }

    if (showStatus) {
      const count = (data.stats && data.stats.tests_returned) || 0;
      setStatus(`Results refreshed (${count} tests)`);
    }
  } catch (error) {
    setStatus(error.message, true);
  }
}

function formatDateTimeFromUnix(seconds) {
  const value = Number(seconds);
  if (!Number.isFinite(value) || value <= 0) return "n/a";
  return new Date(value * 1000).toLocaleString();
}

function isLikelyTextPath(path) {
  return /\.(md|txt|json|ya?ml|py|ps1|csv|xml|html?|css|js)$/i.test(String(path || ""));
}

function renderExportsFiles(files) {
  if (!els.exportsFiles) return;
  els.exportsFiles.innerHTML = "";
  if (!files || files.length === 0) {
    els.exportsFiles.innerHTML = '<div class="tree-muted">No exports generated yet.</div>';
    return;
  }

  files.forEach((file) => {
    const card = document.createElement("article");
    card.className = "export-file";
    card.innerHTML = `
      <div><strong>${escapeHtml(file.name || "")}</strong></div>
      <div>${escapeHtml(formatBytes(file.size || 0))} | ${escapeHtml(formatDateTimeFromUnix(file.mtime))}</div>
      <div><code>${escapeHtml(file.path || "")}</code></div>
    `;

    const actions = document.createElement("div");
    actions.className = "inline-actions";

    const openBtn = document.createElement("button");
    openBtn.type = "button";
    openBtn.className = "btn tiny ghost";
    openBtn.textContent = "Open";
    openBtn.addEventListener("click", () => {
      window.open(exportFileUrl(file.path), "_blank", "noopener,noreferrer");
    });
    actions.append(openBtn);

    if (isLikelyTextPath(file.path)) {
      const openInExplorerBtn = document.createElement("button");
      openInExplorerBtn.type = "button";
      openInExplorerBtn.className = "btn tiny ghost";
      openInExplorerBtn.textContent = "Open in Explorer";
      openInExplorerBtn.addEventListener("click", () => {
        openWorkspacePath(file.path);
      });
      actions.append(openInExplorerBtn);
    }

    card.append(actions);
    els.exportsFiles.append(card);
  });
}

function renderExportsOutput(result, label) {
  if (!els.exportsOutput) return;
  if (!result) {
    els.exportsOutput.textContent = "";
    return;
  }

  const cmd = Array.isArray(result.command) ? result.command.join(" ") : String(result.command || "");
  const chunks = [
    `Action: ${label}`,
    `Exit: ${result.exit_code}`,
    `Duration: ${result.duration_seconds}s`,
    cmd ? `$ ${cmd}` : "",
    "",
    result.stdout || "",
    result.stderr ? `\n[stderr]\n${result.stderr}` : "",
  ].filter(Boolean);
  els.exportsOutput.textContent = chunks.join("\n");
}

function syncExportPackageMode() {
  if (!els.exportsPackageMode || !els.exportsPackageTest) return;
  const mode = els.exportsPackageMode.value;
  const single = mode === "single";
  els.exportsPackageTest.disabled = !single;
  const selected = els.exportsPackageTest.value;
  const label = single
    ? `Export package for ${selected || "selected Gold test"}.`
    : "Export packages for all pass+gold tests.";
  if (els.exportsPackageHint) {
    els.exportsPackageHint.textContent = label;
  }
}

function renderExports() {
  if (!els.exportsGate) return;
  if (!state.exports) {
    els.exportsGate.innerHTML = '<p class="tree-muted">Export data unavailable.</p>';
    renderExportsFiles([]);
    return;
  }

  const release = state.exports.release_gate || {};
  const ready = Boolean(release.ready);
  const blocked = release.blocked_tests || [];
  const goldTests = state.exports.gold_tests || [];
  const blockedText = blocked.length ? blocked.join(", ") : "none";
  const releaseNote = state.exports.release_note || "";

  els.exportsGate.innerHTML = `
    <p><span class="release-pill ${ready ? "ok" : "blocked"}">${ready ? "ready" : "blocked"}</span></p>
    <p><strong>Pass tests:</strong> ${escapeHtml(String(release.pass_total || 0))} | <strong>Gold pass:</strong> ${escapeHtml(
      String(release.gold_total || 0)
    )}</p>
    <p><strong>Blocked tests:</strong> ${escapeHtml(blockedText || "none")}</p>
    <p><strong>Gold package candidates:</strong> ${escapeHtml(String(goldTests.length))}</p>
    <p>${escapeHtml(releaseNote || (ready ? "Validated release export is currently allowed." : ""))}</p>
  `;

  if (els.exportsValidatedBtn) {
    els.exportsValidatedBtn.disabled = !ready;
  }
  if (els.exportsPackageBtn) {
    els.exportsPackageBtn.disabled = goldTests.length === 0;
  }

  if (els.exportsPackageTest) {
    const previous = els.exportsPackageTest.value;
    els.exportsPackageTest.innerHTML = "";
    if (goldTests.length === 0) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "No Gold tests";
      els.exportsPackageTest.append(option);
    } else {
      goldTests.forEach((row) => {
        const option = document.createElement("option");
        option.value = row.test_id;
        option.textContent = `${row.test_id} | ${row.claim_id} | ${row.last_run || "n/a"}`;
        els.exportsPackageTest.append(option);
      });
      if (previous && goldTests.some((row) => row.test_id === previous)) {
        els.exportsPackageTest.value = previous;
      }
    }
  }

  syncExportPackageMode();
  renderExportsFiles(state.exports.recent_exports || []);
}

function setExportActionsDisabled(disabled) {
  [
    els.exportsRefreshBtn,
    els.exportsValidatedBtn,
    els.exportsDossierBtn,
    els.exportsPackageBtn,
    els.exportsPackageMode,
    els.exportsPackageTest,
    els.exportsDossierMdOnly,
    els.exportsPackageMdOnly,
    els.resultsExportPackageBtn,
  ].forEach((node) => {
    if (node) node.disabled = disabled;
  });
}

async function runExportAction(endpoint, payload, label) {
  setGlobalActionDisabled(true);
  setExportActionsDisabled(true);
  setStatus(`Running ${label} ...`);
  try {
    const result = await apiPost(endpoint, payload || {});
    const cmd = Array.isArray(result.command) ? result.command.join(" ") : String(result.command || "");
    if (cmd) appendConsole(`$ ${cmd}`);
    appendConsole(`action=${result.action || label} exit=${result.exit_code} duration=${result.duration_seconds}s`);

    if (result.stdout && result.stdout.trim()) appendConsole(result.stdout.trim());
    if (result.stderr && result.stderr.trim()) appendConsole(result.stderr.trim());

    renderExportsOutput(result, label);
    if (result.ok) {
      setStatus(`${label} completed`);
    } else {
      setStatus(`${label} failed (exit ${result.exit_code})`, true);
    }

    await Promise.all([loadMission(false), loadResults(false), loadExports(false)]);
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    setExportActionsDisabled(false);
    setGlobalActionDisabled(false);
    syncExportPackageMode();
  }
}

async function exportClaimPackage() {
  const mode = els.exportsPackageMode ? els.exportsPackageMode.value : "single";
  const mdOnly = Boolean(els.exportsPackageMdOnly && els.exportsPackageMdOnly.checked);
  const testId = els.exportsPackageTest ? els.exportsPackageTest.value.trim() : "";
  const payload =
    mode === "all-gold" ? { all_gold: true, md_only: mdOnly } : { test_id: testId, md_only: mdOnly };
  await runExportAction("/api/system/export/package", payload, "claim-package export");
}

async function loadExports(showStatus = true) {
  try {
    const data = await apiGet("/api/exports");
    state.exports = data;
    renderExports();
    if (showStatus) {
      const n = (data.gold_tests && data.gold_tests.length) || 0;
      setStatus(`Exports refreshed (${n} gold tests)`);
    }
  } catch (error) {
    setStatus(error.message, true);
  }
}

function graphTypeOrder() {
  return ["parameter", "claim", "derivation", "test", "evidence"];
}

function renderGraphCounts(counts) {
  const order = graphTypeOrder();
  els.graphCounts.innerHTML = order
    .map((type) => `<span class="chip">${escapeHtml(type)}: ${Number((counts && counts[type]) || 0)}</span>`)
    .join("");
}

function getActiveGraphNode() {
  const graph = state.graph;
  if (!graph || !graph.nodes) return null;
  return graph.nodes.find((node) => node.id === state.activeGraphNodeId) || null;
}

function updateGraphOpenSelectedButton() {
  if (!els.graphOpenSelectedBtn) return;
  const node = getActiveGraphNode();
  const canOpen = Boolean(node && node.path);
  els.graphOpenSelectedBtn.disabled = !canOpen;
}

function renderGraphGuide() {
  return `
    <p><strong>How to use Graph</strong></p>
    <ol>
      <li>Choose scope from <code>P1/P2/P3/All</code>.</li>
      <li>Click one node to focus dependencies.</li>
      <li>Use <code>Reset Focus</code> to clear highlight.</li>
      <li>Use <code>Open Selected</code> to jump to file-backed nodes.</li>
    </ol>
  `;
}

function renderGraphDetail(node, linkedNodeCount = 0, linkedEdgeCount = 0) {
  if (!node) {
    const hasStoredSelection = Boolean(state.activeGraphNodeId);
    const extra = hasStoredSelection
      ? `<p class="tree-muted">Saved focus <code>${escapeHtml(
          state.activeGraphNodeId
        )}</code> is outside current graph scope. Keep current filter or switch scope.</p>`
      : "";
    els.graphDetail.innerHTML = `${renderGraphGuide()}${extra}<p class="tree-muted">Click a node for metadata.</p>`;
    updateGraphOpenSelectedButton();
    return;
  }

  const lines = Object.entries(node)
    .filter(([key]) => key !== "id" && key !== "type" && key !== "label")
    .map(([key, value]) => `<p><strong>${escapeHtml(key)}:</strong> ${escapeHtml(String(value))}</p>`)
    .join("");

  els.graphDetail.innerHTML = `
    ${renderGraphGuide()}
    <hr />
    <p><strong>ID:</strong> <code>${escapeHtml(node.id)}</code></p>
    <p><strong>Type:</strong> ${escapeHtml(node.type)}</p>
    <p><strong>Label:</strong> ${escapeHtml(node.label)}</p>
    <p><strong>Linked nodes:</strong> ${escapeHtml(String(linkedNodeCount))} | <strong>Linked edges:</strong> ${escapeHtml(
      String(linkedEdgeCount)
    )}</p>
    ${lines}
    ${node.path ? '<p><button id="graphOpenPathBtn" class="btn tiny ghost" type="button">Open Path</button></p>' : ""}
  `;

  if (node.path) {
    const btn = document.getElementById("graphOpenPathBtn");
    if (btn) {
      btn.addEventListener("click", () => {
        openWorkspacePath(node.path);
      });
    }
  }
  updateGraphOpenSelectedButton();
}

function renderGraph() {
  const graph = state.graph;
  const svg = els.graphSvg;
  while (svg.firstChild) {
    svg.removeChild(svg.firstChild);
  }

  if (!graph || !graph.nodes || graph.nodes.length === 0) {
    renderGraphCounts({});
    renderGraphDetail(null);
    setStatus("Graph is empty", true);
    return;
  }

  renderGraphCounts(graph.counts || {});

  const selectedNode = graph.nodes.find((node) => node.id === state.activeGraphNodeId) || null;
  const selectedId = selectedNode ? selectedNode.id : "";
  const focusActive = Boolean(selectedId);
  const focusNodes = new Set();
  let focusEdgeCount = 0;
  if (focusActive) {
    focusNodes.add(selectedId);
    (graph.edges || []).forEach((edge) => {
      const touches = edge.source === selectedId || edge.target === selectedId;
      if (!touches) return;
      focusEdgeCount += 1;
      focusNodes.add(edge.source);
      focusNodes.add(edge.target);
    });
  }

  const typeOrder = graphTypeOrder();
  const groups = Object.fromEntries(typeOrder.map((type) => [type, []]));
  graph.nodes.forEach((node) => {
    if (!groups[node.type]) {
      groups[node.type] = [];
    }
    groups[node.type].push(node);
  });

  Object.keys(groups).forEach((type) => {
    groups[type].sort((a, b) => a.id.localeCompare(b.id));
  });

  const maxGroupSize = Math.max(...Object.values(groups).map((items) => items.length), 1);
  const width = 1200;
  const height = Math.max(420, maxGroupSize * 26 + 90);
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  const stepX = width / (typeOrder.length + 1);
  const positions = {};

  typeOrder.forEach((type, index) => {
    const items = groups[type] || [];
    const x = stepX * (index + 1);
    const usableHeight = height - 90;
    items.forEach((node, i) => {
      const y = 45 + (usableHeight * (i + 1)) / (items.length + 1);
      positions[node.id] = { x, y, node };
    });
  });

  const ns = "http://www.w3.org/2000/svg";

  (graph.edges || []).forEach((edge) => {
    const source = positions[edge.source];
    const target = positions[edge.target];
    if (!source || !target) return;

    const line = document.createElementNS(ns, "line");
    line.setAttribute("x1", String(source.x));
    line.setAttribute("y1", String(source.y));
    line.setAttribute("x2", String(target.x));
    line.setAttribute("y2", String(target.y));
    const classes = ["graph-edge"];
    if (focusActive) {
      if (edge.source === selectedId || edge.target === selectedId) {
        classes.push("active");
      } else {
        classes.push("muted");
      }
    }
    line.setAttribute("class", classes.join(" "));
    svg.append(line);
  });

  Object.values(positions).forEach(({ x, y, node }) => {
    const group = document.createElementNS(ns, "g");
    const classes = ["graph-node", `node-${node.type}`];
    if (node.id === selectedId) {
      classes.push("active");
    }
    if (focusActive) {
      if (focusNodes.has(node.id)) {
        if (node.id !== selectedId) {
          classes.push("linked");
        }
      } else {
        classes.push("muted");
      }
    }
    group.setAttribute("class", classes.join(" "));

    const circle = document.createElementNS(ns, "circle");
    circle.setAttribute("cx", String(x));
    circle.setAttribute("cy", String(y));
    circle.setAttribute("r", node.type === "claim" ? "5" : "6");
    group.append(circle);

    const label = document.createElementNS(ns, "text");
    label.setAttribute("x", String(x + 9));
    label.setAttribute("y", String(y + 3));
    const rawLabel = node.label || node.id;
    label.textContent = rawLabel.length > 40 ? `${rawLabel.slice(0, 40)}...` : rawLabel;
    group.append(label);

    group.addEventListener("click", () => {
      setGraphSelectedNode(node.id);
      renderGraph();
    });

    group.addEventListener("dblclick", () => {
      if (node.path) {
        openWorkspacePath(node.path);
      }
    });

    svg.append(group);
  });

  renderGraphDetail(selectedNode, focusActive ? focusNodes.size : 0, focusEdgeCount);
}

async function loadGraph(showStatus = true) {
  try {
    const priority = els.graphPriority.value;
    const query = priority && priority !== "ALL" ? `?priority=${encodeURIComponent(priority)}` : "";
    const data = await apiGet(`/api/graph${query}`);
    state.graph = data;
    renderGraph();
    if (showStatus) {
      setStatus(`Graph refreshed (${data.scope})`);
    }
  } catch (error) {
    setStatus(error.message, true);
  }
}

function setGlobalActionDisabled(disabled) {
  [els.lintBtn, els.syncBtn, els.exportBtn].forEach((btn) => {
    btn.disabled = disabled;
  });
}

async function runSystemAction(action) {
  setGlobalActionDisabled(true);
  setExportActionsDisabled(true);
  setStatus(`Running ${action} ...`);
  try {
    const result = await apiPost(`/api/system/${action}`, {});
    const cmd = Array.isArray(result.command) ? result.command.join(" ") : String(result.command || "");
    appendConsole(`$ ${cmd}`);
    appendConsole(`action=${action} exit=${result.exit_code} duration=${result.duration_seconds}s`);

    if (result.stdout && result.stdout.trim()) {
      appendConsole(result.stdout.trim());
    }
    if (result.stderr && result.stderr.trim()) {
      appendConsole(result.stderr.trim());
    }

    if (result.ok) {
      setStatus(`${action} completed`);
    } else {
      setStatus(`${action} failed (exit ${result.exit_code})`, true);
    }

    if (action === "sync" && result.ok) {
      await Promise.all([
        loadTree(),
        loadMission(false),
        loadWorkbench(false),
        loadResults(false),
        loadExports(false),
        loadGraph(false),
      ]);
      setStatus("Sync completed and UI refreshed");
    }

    if (action === "export" && result.ok) {
      await Promise.all([loadMission(false), loadResults(false), loadExports(false)]);
    }
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    setGlobalActionDisabled(false);
    setExportActionsDisabled(false);
    syncExportPackageMode();
  }
}

function bindEvents() {
  els.tabNav.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const tab = target.dataset.tab;
    if (!tab) return;
    switchTab(tab);
  });

  if (els.themeSelect) {
    els.themeSelect.addEventListener("change", () => {
      applyTheme(els.themeSelect.value);
      setStatus(`Theme switched to ${els.themeSelect.value}`);
    });
  }

  els.treeFilter.addEventListener("input", () => {
    state.filter = els.treeFilter.value.trim();
    renderTree();
  });

  els.refreshBtn.addEventListener("click", async () => {
    if (isDirty()) {
      const ok = window.confirm("You have unsaved changes. Refresh file tree anyway?");
      if (!ok) return;
    }
    await loadTree();
    setStatus("Tree refreshed");
  });

  els.newFileBtn.addEventListener("click", createNewFile);
  els.saveBtn.addEventListener("click", saveCurrentFile);

  els.editor.addEventListener("input", () => {
    updateDirtyUi();
    updatePreview();
  });

  els.missionRefreshBtn.addEventListener("click", () => loadMission());

  els.wbApplyBtn.addEventListener("click", () => loadWorkbench());
  els.wbResetBtn.addEventListener("click", async () => {
    els.wbPriority.value = "";
    els.wbStatus.value = "";
    els.wbSearch.value = "";
    state.selectedTestId = "";
    await loadWorkbench();
  });
  els.wbRefreshBtn.addEventListener("click", () => loadWorkbench());

  els.wbSearch.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      loadWorkbench();
    }
  });

  els.wbForm.addEventListener("submit", saveWorkbenchUpdate);

  els.resultsApplyBtn.addEventListener("click", () => loadResults());
  els.resultsResetBtn.addEventListener("click", async () => {
    els.resultsPriority.value = "";
    els.resultsStatus.value = "";
    els.resultsSearch.value = "";
    state.selectedResultTestId = "";
    state.resultDetail = null;
    await loadResults();
  });
  els.resultsRefreshBtn.addEventListener("click", () => loadResults());
  els.resultsSearch.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      loadResults();
    }
  });
  els.resultsDetailToggleBtn.addEventListener("click", () => {
    state.resultsDetailCollapsed = !state.resultsDetailCollapsed;
    applyResultsDetailCollapse();
  });
  els.resultsSliderPrevBtn.addEventListener("click", () => stepResultSlider(-1));
  els.resultsSliderNextBtn.addEventListener("click", () => stepResultSlider(1));
  els.resultsSliderImage.addEventListener("click", () => {
    const current = state.resultImageArtifacts[state.resultImageIndex];
    if (!current) return;
    window.open(artifactUrl(current.path), "_blank", "noopener,noreferrer");
  });

  els.graphRefreshBtn.addEventListener("click", () => loadGraph());
  els.graphPriority.addEventListener("change", () => {
    localStorage.setItem(GRAPH_PRIORITY_STORAGE_KEY, els.graphPriority.value);
    loadGraph();
  });
  if (els.graphResetBtn) {
    els.graphResetBtn.addEventListener("click", () => {
      setGraphSelectedNode("");
      renderGraph();
      setStatus("Graph focus reset");
    });
  }
  if (els.graphOpenSelectedBtn) {
    els.graphOpenSelectedBtn.addEventListener("click", () => {
      const node = getActiveGraphNode();
      if (!node || !node.path) {
        setStatus("Selected node has no openable file path.", true);
        return;
      }
      openWorkspacePath(node.path);
    });
  }

  if (els.exportsRefreshBtn) {
    els.exportsRefreshBtn.addEventListener("click", () => loadExports());
  }
  if (els.exportsValidatedBtn) {
    els.exportsValidatedBtn.addEventListener("click", () => runSystemAction("export"));
  }
  if (els.exportsDossierBtn) {
    els.exportsDossierBtn.addEventListener("click", () =>
      runExportAction(
        "/api/system/export/dossier",
        { md_only: Boolean(els.exportsDossierMdOnly && els.exportsDossierMdOnly.checked) },
        "full-dossier export"
      )
    );
  }
  if (els.exportsPackageBtn) {
    els.exportsPackageBtn.addEventListener("click", exportClaimPackage);
  }
  if (els.exportsPackageMode) {
    els.exportsPackageMode.addEventListener("change", syncExportPackageMode);
  }

  els.lintBtn.addEventListener("click", () => runSystemAction("lint"));
  els.syncBtn.addEventListener("click", () => runSystemAction("sync"));
  els.exportBtn.addEventListener("click", () => runSystemAction("export"));

  els.clearConsoleBtn.addEventListener("click", () => {
    els.systemOutput.textContent = "";
  });

  window.addEventListener("keydown", (event) => {
    const key = event.key.toLowerCase();
    const savePressed = (event.ctrlKey || event.metaKey) && key === "s";
    if (savePressed) {
      event.preventDefault();
      saveCurrentFile();
      return;
    }

    if (!event.ctrlKey && !event.metaKey && state.activeTab === "results") {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        stepResultSlider(-1);
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        stepResultSlider(1);
      }
    }

    if ((event.ctrlKey || event.metaKey) && /^\d$/.test(key)) {
      const idx = Number(key) - 1;
      if (idx >= 0 && idx < TAB_ORDER.length) {
        event.preventDefault();
        switchTab(TAB_ORDER[idx]);
      }
    }
  });

  window.addEventListener("beforeunload", (event) => {
    if (!isDirty()) return;
    event.preventDefault();
    event.returnValue = "";
  });
}

async function init() {
  initTheme();
  initGraphPreferences();
  bindEvents();
  switchTab("explorer");
  applyResultsDetailCollapse();
  updateTitle();
  updatePreview();
  appendConsole("QNG Mission Workbench initialized.");

  await loadTree();
  await Promise.all([loadMission(false), loadWorkbench(false), loadResults(false), loadExports(false), loadGraph(false)]);

  setStatus("Ready");
}

init();
