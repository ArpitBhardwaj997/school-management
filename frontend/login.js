// Login page: log in, or (first run only) create the first admin.
const API = location.hostname.includes("onrender.com") ? "" : "http://127.0.0.1:8000";
const $ = (s) => document.querySelector(s);
const detail = (d) => (typeof d === "string" ? d : Array.isArray(d) ? d.map((x) => x.msg).join("; ") : "Request failed");

$("#login-err").textContent = sessionStorage.getItem("flash") || "";
sessionStorage.removeItem("flash");
if (sessionStorage.getItem("token") && Number(sessionStorage.getItem("expAt")) > Date.now()) location.replace("index.html");

// Show the "create admin" link only while no admin exists (and SETUP_KEY is set on the server)
fetch(API + "/auth/setup-status").then((r) => r.json()).then((d) => { $("#setup-link").hidden = !d.needs_setup; }).catch(() => {});
const swap = (setup) => { $("#login-form").hidden = setup; $("#setup-form").hidden = !setup; };
$("#setup-link").onclick = (e) => { e.preventDefault(); swap(true); };
$("#back").onclick = (e) => { e.preventDefault(); swap(false); };

$("#login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const res = await fetch(API + "/auth/login", {
      method: "POST",
      body: new URLSearchParams({ username: $("#u").value.trim(), password: $("#p").value }),
    });
    const d = await res.json().catch(() => ({}));
    if (!res.ok) { $("#login-err").textContent = detail(d.detail) || "Login failed"; return; }
    sessionStorage.setItem("token", d.access_token);   // cleared when the tab closes
    sessionStorage.setItem("expAt", Date.now() + d.expires_in * 1000);
    location.href = "index.html";
  } catch { $("#login-err").textContent = "Cannot reach the server."; }
});

$("#setup-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = Object.fromEntries(new FormData(e.target));
  const err = (m) => ($("#setup-err").textContent = m);
  if (f.password !== f.again) return err("Passwords do not match.");
  delete f.again;
  try {
    const res = await fetch(API + "/auth/setup", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(f) });
    const d = await res.json().catch(() => ({}));
    if (!res.ok) return err(detail(d.detail));
    $("#setup-form").reset();
    $("#u").value = d.username;
    swap(false);
    $("#login-err").textContent = "Admin created. Please log in.";
  } catch { err("Cannot reach the server."); }
});