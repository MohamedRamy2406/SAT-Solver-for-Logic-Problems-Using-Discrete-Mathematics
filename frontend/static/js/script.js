// SAT Solver frontend logic. Vanilla JS — no frameworks. Brute-force only.

const $ = (s) => document.querySelector(s);
const formulaEl = $("#formula");
const solveBtn = $("#solve-btn");
const clearBtn = $("#clear-btn");
const errorEl = $("#error");
const resultSection = $("#result-section");
const verdictEl = $("#verdict");
const modelEl = $("#model");
const traceEl = $("#trace");
const historyEl = $("#history");

const HIST_KEY = "sat:history";

// ---------- helpers ----------
function showError(msg) {
  errorEl.textContent = msg;
  errorEl.hidden = false;
}
function clearError() { errorEl.hidden = true; errorEl.textContent = ""; }

function spinner(on) {
  solveBtn.querySelector(".btn-label").textContent = on ? "Solving" : "Solve";
  solveBtn.querySelector(".spinner").hidden = !on;
  solveBtn.disabled = on;
}

async function api(path, body) {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await r.json();
  if (!r.ok) throw new Error(data.message || data.error || "Request failed");
  return data;
}

// ---------- operator insertion ----------
$("#op-bar").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-insert]");
  if (!b) return;
  const ins = b.dataset.insert;
  const start = formulaEl.selectionStart, end = formulaEl.selectionEnd;
  const v = formulaEl.value;
  formulaEl.value = v.slice(0, start) + ins + v.slice(end);
  formulaEl.focus();
  formulaEl.selectionStart = formulaEl.selectionEnd = start + ins.length;
});

document.querySelectorAll(".example").forEach((b) =>
  b.addEventListener("click", () => {
    formulaEl.value = b.dataset.formula;
    formulaEl.focus();
  })
);

clearBtn.addEventListener("click", () => {
  formulaEl.value = "";
  clearError();
  resultSection.hidden = true;
  $("#table").hidden = true;
  formulaEl.focus();
});

// Keyboard shortcut: Ctrl/Cmd + Enter
formulaEl.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") solve();
});

// ---------- solve ----------
solveBtn.addEventListener("click", solve);

async function solve() {
  const formula = formulaEl.value.trim();
  clearError();
  if (!formula) return showError("Enter a formula first.");
  spinner(true);
  try {
    const data = await api("/api/solve", { formula });
    renderResult(data, formula);
    addHistory(formula, data.satisfiable);
    // Automatically build the truth table on every solve.
    await buildTable(formula);
  } catch (e) {
    showError(e.message);
    resultSection.hidden = true;
  } finally {
    spinner(false);
  }
}

function renderResult(data, formula) {
  resultSection.hidden = false;
  verdictEl.className = "verdict " + (data.satisfiable ? "sat" : "unsat");
  verdictEl.textContent = data.satisfiable ? "SATISFIABLE" : "UNSATISFIABLE";

  $("#meta-method").textContent = "BRUTE-FORCE";
  $("#meta-time").textContent = `${data.elapsed_ms} ms`;
  $("#meta-checked").textContent = `${data.combinations_checked}/${data.combinations_total} checked · ${data.models_count} model(s)`;

  modelEl.innerHTML = "";
  if (data.satisfiable && data.model) {
    Object.entries(data.model).forEach(([k, v], i) => {
      const d = document.createElement("div");
      d.className = "var-chip";
      d.style.animationDelay = (i * 60) + "ms";
      d.innerHTML = `<span class="v">${k}</span> = <span class="val ${v ? "true" : "false"}">${v ? "True" : "False"}</span>`;
      modelEl.appendChild(d);
    });
  } else {
    modelEl.innerHTML = `<p class="muted">No assignment satisfies the formula. The formula is a contradiction over its variables.</p>`;
  }

  traceEl.innerHTML = "";
  const trace = data.trace || [];
  trace.forEach((row) => {
    const asg = Object.entries(row.assignment).map(([k, v]) => `${k}=${v ? "T" : "F"}`).join(" ");
    const d = document.createElement("div");
    d.className = "trace-row " + (row.result ? "t" : "");
    d.innerHTML = `<span>${asg}</span><span class="res ${row.result ? "true" : "false"}">${row.result ? "✓" : "✗"}</span>`;
    traceEl.appendChild(d);
  });

  resultSection.dataset.formula = formula;
}

// ---------- result actions ----------
$("#copy-result").addEventListener("click", async () => {
  const text = verdictEl.textContent + "\n" + Array.from(modelEl.querySelectorAll(".var-chip"))
    .map((c) => c.textContent).join("\n");
  await navigator.clipboard.writeText(text);
  flash($("#copy-result"), "Copied!");
});

function flash(btn, text) {
  const old = btn.textContent;
  btn.textContent = text;
  setTimeout(() => btn.textContent = old, 1200);
}

// ---------- truth table ----------
async function buildTable(formula) {
  if (!formula) return;
  try {
    const data = await api("/api/truth-table", { formula });
    const sec = $("#table");
    sec.hidden = false;
    const wrap = $("#truth-table");
    if (data.variables.length > 10) {
      wrap.innerHTML = `<p class="muted" style="padding:14px">Too many variables (${data.variables.length}) — truth table would have ${2**data.variables.length} rows.</p>`;
      return;
    }
    const head = `<tr>${data.variables.map((v) => `<th>${v}</th>`).join("")}<th>Φ</th></tr>`;
    const rows = data.rows.map((r) => {
      const cells = data.variables.map((v) =>
        `<td class="${r.assignment[v] ? "t" : "f"}">${r.assignment[v] ? "T" : "F"}</td>`
      ).join("");
      return `<tr class="${r.result ? "sat" : ""}">${cells}<td class="${r.result ? "t" : "f"}"><b>${r.result ? "T" : "F"}</b></td></tr>`;
    }).join("");
    wrap.innerHTML = `<table class="tt"><thead>${head}</thead><tbody>${rows}</tbody></table>`;
    wrap._data = data;
  } catch (e) { showError(e.message); }
}

$("#export-table").addEventListener("click", () => {
  const data = $("#truth-table")._data;
  if (!data) return;
  const header = [...data.variables, "result"].join(",");
  const lines = data.rows.map((r) =>
    [...data.variables.map((v) => r.assignment[v] ? "T" : "F"), r.result ? "T" : "F"].join(",")
  );
  const blob = new Blob([header + "\n" + lines.join("\n")], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "truth-table.csv";
  a.click();
});

// ---------- history ----------
function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HIST_KEY) || "[]"); }
  catch { return []; }
}
function saveHistory(h) { localStorage.setItem(HIST_KEY, JSON.stringify(h.slice(0, 20))); }

function addHistory(formula, sat) {
  const h = loadHistory();
  const idx = h.findIndex((x) => x.formula === formula);
  if (idx >= 0) h.splice(idx, 1);
  h.unshift({ formula, sat, ts: Date.now() });
  saveHistory(h);
  renderHistory();
}

function renderHistory() {
  const h = loadHistory();
  historyEl.innerHTML = "";
  if (!h.length) {
    historyEl.innerHTML = `<li style="cursor:default"><span class="muted">No formulas yet — solve one to populate history.</span></li>`;
    return;
  }
  h.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>${escapeHtml(item.formula)}</span><span class="tag ${item.sat ? "sat" : "unsat"}">${item.sat ? "SAT" : "UNSAT"}</span>`;
    li.addEventListener("click", () => { formulaEl.value = item.formula; solve(); });
    historyEl.appendChild(li);
  });
}

$("#clear-history").addEventListener("click", () => { localStorage.removeItem(HIST_KEY); renderHistory(); });

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

renderHistory();
formulaEl.focus();
