// School Management frontend (plain JS). Talks to the FastAPI backend.
const API = location.port === "8000" ? "" : "http://127.0.0.1:8000";
const LIMIT = 20;
const METHODS = ["cash", "upi", "card", "cheque", "bank transfer"];
const $ = (s) => document.querySelector(s);
// Escape everything that comes from the database before putting it in HTML (stops XSS)
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const money = (v) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(Number(v));

const ico = (p) => `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;
const ICON = {
  classes: ico('<path d="M3 8l9-4 9 4-9 4-9-4z"/><path d="M7 10.5v4.5c0 1.4 2.2 3 5 3s5-1.6 5-3v-4.5"/>'),
  students: ico('<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.6-3.6 3.2-5.5 6.5-5.5s5.9 1.9 6.5 5.5"/><path d="M16 4.6a3.5 3.5 0 010 6.8M18 14.8c2 .6 3.2 2.2 3.5 4.7"/>'),
  fees: ico('<path d="M6 4h12M6 9h12M9 4c4 0 6 2 6 5s-2 5-6 5l7 6"/>'),
  payments: ico('<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19M6.5 15h4"/>'),
};
const toast = (m) => { const t = $("#toast"); t.textContent = m; t.classList.add("on"); setTimeout(() => t.classList.remove("on"), 2200); };

let token = sessionStorage.getItem("token");
let expAt = Number(sessionStorage.getItem("expAt")) || 0;
let classes = [], current = "classes", page = 0, rows = {};

// What each page shows and which fields its form has
const R = {
  classes: { title: "Classes", path: "/classes", id: "class_id",
    cols: ["class_id", "class_name"],
    fields: [{ n: "class_name" }] },
  students: { title: "Students", path: "/students", id: "student_id", summary: true,
    cols: ["student_id", "first_name", "last_name", "parent_name", "phone", "class_id", "section"],
    fields: [{ n: "first_name" }, { n: "last_name" }, { n: "parent_name" }, { n: "phone" },
      { n: "class_id", t: "class" }, { n: "section", opt: 1 }, { n: "date_of_birth", t: "date", opt: 1 },
      { n: "enrollment_date", t: "date", opt: 1 }, { n: "address", t: "textarea", opt: 1 }] },
  fees: { title: "Fees", path: "/fees", id: "fee_id",
    cols: ["fee_id", "class_id", "total_amount", "due_date"],
    fields: [{ n: "class_id", t: "class", once: 1 }, { n: "total_amount", t: "money" }, { n: "due_date", t: "date" }] },
  payments: { title: "Payments", path: "/payments", id: "payment_id",
    cols: ["payment_id", "student_id", "amount_paid", "payment_method", "payment_date"],
    fields: [{ n: "student_id", t: "int", once: 1 }, { n: "amount_paid", t: "money" },
      { n: "payment_method", t: "method" }, { n: "payment_date", t: "datetime-local", opt: 1 }] },
};

async function api(path, method = "GET", body) {
  const res = await fetch(API + path, {
    method,
    headers: { Authorization: "Bearer " + token, ...(body ? { "Content-Type": "application/json" } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401) { logout("Session expired. Please log in again."); throw new Error("Not logged in"); }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const d = data.detail;
    throw new Error(typeof d === "string" ? d : Array.isArray(d) ? d.map((x) => `${x.loc.slice(1).join(".")}: ${x.msg}`).join("; ") : "Request failed");
  }
  return data;
}

// ---------- login / logout ----------
$("#login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const res = await fetch(API + "/auth/login", {
      method: "POST",
      body: new URLSearchParams({ username: $("#u").value, password: $("#p").value }),
    });
    const d = await res.json().catch(() => ({}));
    if (!res.ok) { $("#login-err").textContent = d.detail || "Login failed"; return; }
    token = d.access_token;
    expAt = Date.now() + d.expires_in * 1000;
    sessionStorage.setItem("token", token);   // cleared when the tab closes
    sessionStorage.setItem("expAt", expAt);
    $("#p").value = "";
    start();
  } catch { $("#login-err").textContent = "Cannot reach the server."; }
});

function logout(msg = "") {
  sessionStorage.clear();
  token = null;
  $("#app").hidden = true;
  $("#login").hidden = false;
  $("#login-err").textContent = msg;
}
$("#logout").onclick = () => logout();

setInterval(() => {
  if (!token) return;
  const min = Math.ceil((expAt - Date.now()) / 60000);
  if (min <= 0) return logout("Session expired. Please log in again.");
  $("#timer").textContent = `Session ends in ${min} min`;
}, 15000);

async function start() {
  $("#login").hidden = true;
  $("#app").hidden = false;
  $("#nav").innerHTML = Object.keys(R).map((k) => `<button data-nav="${k}">${ICON[k]}<span>${R[k].title}</span></button>`).join("");
  $("#timer").textContent = `Session ends in ${Math.ceil((expAt - Date.now()) / 60000)} min`;
  try { classes = await api("/classes?limit=100"); show("classes"); } catch {}
}
$("#nav").addEventListener("click", (e) => { const b = e.target.closest("[data-nav]"); if (b) show(b.dataset.nav); });

// ---------- list page ----------
const cell = (c, v) =>
  c === "class_id" ? `<span class="chip">${esc(classes.find((x) => x.class_id === v)?.class_name ?? v)}</span>`
  : c === "payment_method" ? `<span class="badge">${esc(v)}</span>`
  : /amount/.test(c) ? esc(money(v))
  : c === "payment_date" && v ? esc(new Date(v).toLocaleString())
  : esc(v);

async function show(name, p = 0) {
  current = name; page = p;
  const r = R[name];
  $("#title").textContent = r.title;
  document.querySelectorAll("#nav button").forEach((b) => b.classList.toggle("on", b.dataset.nav === name));
  let list;
  try { list = await api(`${r.path}?skip=${p * LIMIT}&limit=${LIMIT}`); }
  catch (e) { $("#content").innerHTML = `<p class="err">${esc(e.message)}</p>`; return; }
  rows = Object.fromEntries(list.map((x) => [x[r.id], x]));
  const head = r.cols.map((c) => `<th>${esc(c.replace(/_/g, " "))}</th>`).join("");
  const body = list.map((x) => `<tr>${r.cols.map((c) => `<td>${cell(c, x[c])}</td>`).join("")}
    <td class="act">${r.summary ? `<button class="ghost" data-a="sum" data-i="${x[r.id]}">Fees</button>` : ""}
    <button class="ghost" data-a="edit" data-i="${x[r.id]}">Edit</button>
    <button class="danger" data-a="del" data-i="${x[r.id]}">Delete</button></td></tr>`).join("");
  $("#content").innerHTML = `<div class="bar"><span class="count">${list.length} shown</span><button data-a="add">+ Add ${esc(r.title.slice(0, -1))}</button></div>
    <div class="card"><table><thead><tr>${head}<th></th></tr></thead><tbody>${body || `<tr><td colspan="9">Nothing here yet.</td></tr>`}</tbody></table></div>
    <div class="pager"><button class="ghost" data-a="prev" ${p ? "" : "disabled"}>Prev</button>
    <span>Page ${p + 1}</span><button class="ghost" data-a="next" ${list.length < LIMIT ? "disabled" : ""}>Next</button></div>`;
}

$("#content").addEventListener("click", async (e) => {
  const a = e.target.dataset.a, r = R[current], item = rows[e.target.dataset.i];
  if (a === "add") form();
  else if (a === "edit") form(item);
  else if (a === "prev") show(current, page - 1);
  else if (a === "next") show(current, page + 1);
  else if (a === "sum") summary(item);
  else if (a === "del") {
    const warn = current === "students" ? "\n\nThis also deletes ALL payment records of this student." : "";
    if (!confirm(`Delete this record?${warn}`)) return;
    try { await api(`${r.path}/${item[r.id]}`, "DELETE"); await refresh(); toast("Deleted"); } catch (err) { alert(err.message); }
  }
});

async function refresh() {
  if (current === "classes") classes = await api("/classes?limit=100");
  show(current, page);
}

// ---------- add / edit form ----------
function field(f, item) {
  const v = item?.[f.n] ?? "";
  const label = `<label>${esc(f.n.replace(/_/g, " "))}`;
  const req = f.opt ? "" : "required";
  if (f.t === "class")
    return `${label}<select name="${f.n}" ${req}><option value="">Select class</option>${classes.map((c) =>
      `<option value="${c.class_id}" ${c.class_id === v ? "selected" : ""}>${esc(c.class_name)}</option>`).join("")}</select></label>`;
  if (f.t === "method")
    return `${label}<select name="${f.n}" required>${METHODS.map((m) => `<option ${m === v ? "selected" : ""}>${m}</option>`).join("")}</select></label>`;
  if (f.t === "textarea") return `${label}<textarea name="${f.n}">${esc(v)}</textarea></label>`;
  const type = f.t === "money" ? 'type="number" step="0.01" min="0.01"' : f.t === "int" ? 'type="number" min="1"' : `type="${f.t || "text"}"`;
  const val = f.t === "datetime-local" ? String(v).slice(0, 16) : v;
  return `${label}<input name="${f.n}" ${type} value="${esc(val)}" ${req}></label>`;
}

function form(item) {
  const r = R[current];
  const fs = r.fields.filter((f) => !(item && f.once));
  $("#dlg-body").innerHTML = `<h3>${item ? "Edit" : "Add"} ${esc(r.title.slice(0, -1))}</h3>
    ${fs.map((f) => field(f, item)).join("")}<p id="err" class="err"></p>
    <div class="row"><button type="button" class="ghost" data-close>Cancel</button><button>Save</button></div>`;
  $("#dlg-body").onsubmit = async (e) => {
    e.preventDefault();
    const body = {};
    fs.forEach((f) => {
      const v = e.target.elements[f.n].value.trim();
      if (v !== "") body[f.n] = f.t === "class" || f.t === "int" ? parseInt(v, 10) : v;
    });
    try {
      await api(item ? `${r.path}/${item[r.id]}` : r.path, item ? "PUT" : "POST", body);
      $("#dlg").close();
      await refresh();
      toast("Saved");
    } catch (err) { $("#err").textContent = err.message; }
  };
  $("#dlg").showModal();
}

// ---------- student fee summary ----------
async function summary(s) {
  let html;
  try {
    const d = await api(`/payments/student/${s.student_id}/summary`);
    html = `<dl><dt>Total fee</dt><dd>${esc(money(d.total_fee))}</dd><dt>Paid</dt><dd>${esc(money(d.total_paid))}</dd>
      <dt>Balance due</dt><dd><b>${esc(money(d.balance_due))}</b></dd><dt>Due date</dt><dd>${esc(d.due_date)}</dd></dl>`;
  } catch (e) { html = `<p class="err">${esc(e.message)}</p>`; }
  $("#dlg-body").onsubmit = null;
  $("#dlg-body").innerHTML = `<h3>Fees: ${esc(s.first_name)} ${esc(s.last_name)}</h3>${html}
    <div class="row"><button type="button" data-close>Close</button></div>`;
  $("#dlg").showModal();
}
$("#dlg").addEventListener("click", (e) => { if (e.target.hasAttribute("data-close")) $("#dlg").close(); });

if (token && expAt > Date.now()) start(); else logout();