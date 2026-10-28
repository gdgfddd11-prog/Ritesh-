"""
AllPrintHub API Website - PREMIUM EDITION
Brand: RITESH | EXPLOITS
- Admin Panel (unlimited searches)
- User System (login with number & password, 5 Rs per search balance)
- 3 APIs integrated: num_info, ultra_vehicle, addhaar2num
"""

import os
import json
import sqlite3
import hashlib
import secrets
import requests
from datetime import datetime
from functools import wraps
from flask import (
    Flask, request, session, redirect, url_for,
    render_template_string, flash, jsonify
)

app = Flask(__name__)
app.secret_key = "change-this-secret-key-to-random-string-xyz123"

DB_FILE = "database.db"
API_BASE = "https://api.allprinthub.in/api"

# ---------- Admin credentials ----------
ADMIN_USERNAME = "@AURABHAI"
ADMIN_PASSWORD = "ritesh111"
ADMIN_SEARCH_KEY = "30day"

# ---------- Default API keys ----------
NUM_INFO_KEY = "30day"
ULTRA_VEHICLE_KEY = "demo"

COST_PER_SEARCH = 5.0


# ============================================================
# DATABASE
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            balance REAL DEFAULT 0,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT,
            api_name TEXT,
            query TEXT,
            cost REAL,
            status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# AUTH
# ============================================================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_mobile") and not session.get("admin"):
            flash("Please login first", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            flash("Admin access required", "error")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper


# ============================================================
# PREMIUM GLOWING BLUE CSS
# ============================================================
BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Rajdhani:wght@500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Rajdhani', 'Segoe UI', sans-serif;
  background: radial-gradient(circle at 20% 10%, #0a1a3f 0%, #050b1e 45%, #000308 100%);
  min-height: 100vh;
  padding: 20px;
  color: #d6ecff;
  overflow-x: hidden;
  position: relative;
}
body::before {
  content: '';
  position: fixed; inset: 0;
  background:
    radial-gradient(circle at 15% 25%, rgba(0,140,255,0.18), transparent 45%),
    radial-gradient(circle at 85% 75%, rgba(0,200,255,0.14), transparent 45%),
    radial-gradient(circle at 50% 50%, rgba(80,0,255,0.08), transparent 55%);
  pointer-events: none;
  z-index: 0;
}
.container { max-width: 940px; margin: 0 auto; position: relative; z-index: 1; }

/* === PREMIUM CARD === */
.card {
  background: linear-gradient(145deg, rgba(10,25,60,0.92), rgba(4,10,30,0.96));
  border: 1px solid rgba(0,180,255,0.35);
  border-radius: 18px;
  padding: 26px;
  margin-bottom: 22px;
  box-shadow:
    0 0 0 1px rgba(0,180,255,0.08),
    0 8px 40px rgba(0,120,255,0.25),
    inset 0 0 60px rgba(0,120,255,0.05);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(12px);
}
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, #0084ff, #00d4ff, transparent);
  animation: borderRun 4s linear infinite;
  background-size: 200% 100%;
}
@keyframes borderRun {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* === LOGO === */
.logo {
  text-align: center;
  margin-bottom: 22px;
  padding: 8px 0;
}
.logo-text {
  font-family: 'Orbitron', sans-serif;
  font-weight: 800;
  font-size: 26px;
  letter-spacing: 3px;
  background: linear-gradient(90deg, #00e0ff, #00a2ff, #7b5cff, #00e0ff);
  background-size: 300% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: logoShine 5s linear infinite;
  filter: drop-shadow(0 0 12px rgba(0,180,255,0.6));
}
.logo-sub {
  font-family: 'Orbitron', sans-serif;
  font-size: 10px;
  letter-spacing: 6px;
  color: #4fa8ff;
  margin-top: 6px;
  opacity: 0.8;
  text-shadow: 0 0 8px rgba(0,150,255,0.6);
}
@keyframes logoShine {
  0% { background-position: 0% 50%; }
  100% { background-position: 300% 50%; }
}

h1, h2, h3 {
  font-family: 'Orbitron', sans-serif;
  color: #c9e6ff;
  margin-bottom: 16px;
  letter-spacing: 1px;
  text-shadow: 0 0 12px rgba(0,150,255,0.4);
}
h1 { font-size: 22px; }
h2 { font-size: 18px; }
h3 { font-size: 15px; }

/* === INPUTS === */
input, select {
  width: 100%;
  padding: 13px 15px;
  margin: 9px 0;
  background: rgba(5,15,40,0.85);
  border: 1px solid rgba(0,160,255,0.35);
  border-radius: 10px;
  font-size: 15px;
  color: #d6ecff;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 600;
  transition: all 0.25s;
  outline: none;
}
input::placeholder { color: #4a6c99; font-weight: 500; }
input:focus, select:focus {
  border-color: #00d4ff;
  box-shadow: 0 0 0 3px rgba(0,180,255,0.18), 0 0 20px rgba(0,180,255,0.35);
  background: rgba(8,22,55,0.95);
}

/* === BUTTONS === */
button {
  width: 100%;
  padding: 13px;
  margin: 9px 0;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  font-size: 15px;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 1px;
  transition: all 0.25s;
  background: linear-gradient(135deg, #0084ff, #00d4ff);
  color: #001428;
  box-shadow: 0 0 20px rgba(0,180,255,0.45);
}
button:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(0,200,255,0.7), 0 0 50px rgba(0,150,255,0.35);
  filter: brightness(1.12);
}
button.green {
  background: linear-gradient(135deg, #00ffa3, #00d4ff);
  color: #001f1a;
  box-shadow: 0 0 20px rgba(0,255,180,0.4);
}
button.green:hover {
  box-shadow: 0 0 32px rgba(0,255,190,0.75);
}
button.red {
  background: linear-gradient(135deg, #ff2e63, #ff6b9d);
  color: #fff;
  box-shadow: 0 0 20px rgba(255,50,100,0.45);
}
button.red:hover { box-shadow: 0 0 32px rgba(255,50,120,0.75); }

/* === FLASH === */
.flash {
  padding: 13px 16px;
  border-radius: 10px;
  margin-bottom: 14px;
  font-weight: 700;
  letter-spacing: 0.5px;
  animation: slideIn 0.4s;
}
.flash.error {
  background: rgba(255,40,80,0.15);
  border: 1px solid rgba(255,60,100,0.5);
  color: #ff9bb3;
  box-shadow: 0 0 20px rgba(255,40,80,0.25);
}
.flash.success {
  background: rgba(0,255,160,0.12);
  border: 1px solid rgba(0,255,180,0.45);
  color: #6dffce;
  box-shadow: 0 0 20px rgba(0,255,180,0.22);
}
@keyframes slideIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* === NAV === */
.nav {
  background: linear-gradient(145deg, rgba(8,20,50,0.95), rgba(3,8,25,0.98));
  border: 1px solid rgba(0,180,255,0.3);
  border-radius: 14px;
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 22px;
  box-shadow: 0 0 24px rgba(0,140,255,0.25);
  flex-wrap: wrap;
  gap: 8px;
}
.nav strong {
  font-family: 'Orbitron', sans-serif;
  color: #00d4ff;
  font-size: 13px;
  letter-spacing: 1px;
  text-shadow: 0 0 10px rgba(0,180,255,0.6);
}
.nav a {
  color: #7ec4ff;
  text-decoration: none;
  font-weight: 700;
  margin-left: 15px;
  font-size: 14px;
  letter-spacing: 0.5px;
  transition: 0.2s;
}
.nav a:hover { color: #00e0ff; text-shadow: 0 0 10px rgba(0,220,255,0.7); }

/* === BALANCE BADGE === */
.balance {
  background: linear-gradient(135deg, rgba(0,255,160,0.12), rgba(0,180,255,0.1));
  border: 1px solid rgba(0,255,180,0.4);
  padding: 12px 18px;
  border-radius: 10px;
  color: #6dffce;
  font-weight: 700;
  margin-bottom: 16px;
  font-family: 'Orbitron', sans-serif;
  font-size: 13px;
  letter-spacing: 0.5px;
  box-shadow: 0 0 20px rgba(0,255,180,0.2);
  text-align: center;
}

/* === PREMIUM RESULT BOX === */
.result-card {
  margin-top: 20px;
  background: linear-gradient(145deg, rgba(6,18,45,0.95), rgba(2,8,22,0.98));
  border: 1px solid rgba(0,200,255,0.4);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 0 30px rgba(0,150,255,0.3), inset 0 0 40px rgba(0,120,255,0.06);
  animation: popIn 0.4s ease;
}
@keyframes popIn {
  from { opacity: 0; transform: scale(0.97); }
  to { opacity: 1; transform: scale(1); }
}
.result-header {
  background: linear-gradient(90deg, rgba(0,180,255,0.18), rgba(0,100,255,0.12));
  padding: 14px 18px;
  border-bottom: 1px solid rgba(0,180,255,0.3);
  font-family: 'Orbitron', sans-serif;
  font-weight: 800;
  letter-spacing: 2px;
  font-size: 13px;
  color: #00e0ff;
  text-shadow: 0 0 12px rgba(0,220,255,0.5);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.result-status {
  font-size: 11px;
  padding: 4px 12px;
  border-radius: 20px;
  letter-spacing: 1px;
}
.result-status.ok {
  background: rgba(0,255,160,0.18);
  color: #6dffce;
  border: 1px solid rgba(0,255,180,0.4);
}
.result-status.fail {
  background: rgba(255,60,100,0.18);
  color: #ff9bb3;
  border: 1px solid rgba(255,60,100,0.4);
}
.result-body {
  padding: 8px 4px;
}
.result-row {
  display: flex;
  padding: 10px 18px;
  border-bottom: 1px dashed rgba(0,150,255,0.15);
  transition: background 0.2s;
}
.result-row:hover {
  background: rgba(0,140,255,0.06);
}
.result-row:last-child { border-bottom: none; }
.result-key {
  flex: 0 0 42%;
  color: #5fa8ff;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
.result-val {
  flex: 1;
  color: #d6ecff;
  font-weight: 600;
  font-size: 14px;
  word-break: break-word;
}
.result-val.highlight {
  color: #00ffcc;
  text-shadow: 0 0 8px rgba(0,255,200,0.4);
}
.result-nested {
  background: rgba(0,100,255,0.05);
  margin: 4px 14px;
  border-radius: 8px;
  border-left: 2px solid rgba(0,200,255,0.5);
  padding: 4px 8px;
}

/* === TABLE === */
table { width: 100%; border-collapse: collapse; margin-top: 12px; }
th, td {
  padding: 11px 10px;
  text-align: left;
  border-bottom: 1px solid rgba(0,140,255,0.15);
  font-size: 13px;
}
th {
  background: rgba(0,140,255,0.12);
  color: #7ec4ff;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 1px;
  font-size: 11px;
  text-transform: uppercase;
}
td { color: #b8d6f5; font-weight: 600; }

/* === MISC === */
a { color: #00d4ff; text-decoration: none; font-weight: 700; }
a:hover { text-shadow: 0 0 10px rgba(0,200,255,0.6); }

.tab-buttons { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.tab-buttons button { flex: 1; min-width: 140px; }
.tab-buttons button.active { background: linear-gradient(135deg, #00ffa3, #00d4ff); }

/* Scrollbar */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: rgba(0,20,50,0.6); }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #0084ff, #00d4ff);
  border-radius: 10px;
}

@media (max-width: 600px) {
  .logo-text { font-size: 19px; letter-spacing: 1.5px; }
  .logo-sub { font-size: 8px; letter-spacing: 4px; }
  .card { padding: 18px; }
  .nav { font-size: 12px; padding: 12px; }
  .nav a { margin-left: 10px; font-size: 12px; }
  .result-key { flex: 0 0 45%; font-size: 11px; }
  .result-val { font-size: 12px; }
}
</style>
"""


# ============================================================
# PREMIUM RESULT RENDERER (JSON -> styled cards)
# ============================================================
def render_premium_result(data):
    """Convert API JSON response into a premium formatted card."""
    if not isinstance(data, dict):
        return f'<div class="result-card"><div class="result-body"><div class="result-row"><div class="result-val">{str(data)}</div></div></div></div>'

    is_ok = str(data.get("status", "")).lower() in ("success", "true", "ok", "1")
    status_label = "SUCCESS" if is_ok else "FAILED"
    status_cls = "ok" if is_ok else "fail"

    def render_value(v, depth=0):
        if isinstance(v, dict):
            inner = "".join(
                f'<div class="result-row"><div class="result-key">{escape_key(k)}</div>'
                f'<div class="result-val">{render_value(val, depth+1)}</div></div>'
                for k, val in v.items()
            )
            return f'<div class="result-nested">{inner}</div>'
        if isinstance(v, list):
            if not v:
                return '<span style="color:#4a6c99;">[empty]</span>'
            return "".join(
                f'<div class="result-nested">{render_value(item, depth+1)}</div>'
                for item in v
            )
        if v is None or v == "":
            return '<span style="color:#4a6c99;">—</span>'
        # Highlight phone/aadhaar-like values
        s = str(v)
        cls = "result-val highlight" if (s.isdigit() and 6 <= len(s) <= 14) else "result-val"
        return f'<span class="{cls}">{s}</span>'

    def escape_key(k):
        return str(k).replace("_", " ").replace("-", " ").title()

    rows = ""
    for k, v in data.items():
        if k.lower() in ("status", "success"):
            continue
        rows += (
            f'<div class="result-row">'
            f'<div class="result-key">{escape_key(k)}</div>'
            f'<div class="result-val">{render_value(v)}</div>'
            f'</div>'
        )

    if not rows:
        rows = '<div class="result-row"><div class="result-val">No data</div></div>'

    return f"""
    <div class="result-card">
      <div class="result-header">
        <span>📋 RESULT DATA</span>
        <span class="result-status {status_cls}">{status_label}</span>
      </div>
      <div class="result-body">{rows}</div>
    </div>
    """


# ============================================================
# LAYOUTS
# ============================================================
def logo_html():
    return """
    <div class="logo">
      <div class="logo-text">⏤͟͟͞͞RITESH | EXPLOITS</div>
      <div class="logo-sub">PREMIUM API HUB</div>
    </div>
    """


def user_layout(content, mobile=""):
    nav = ""
    if mobile:
        nav = f"""
        <div class="nav">
          <strong>📱 {mobile}</strong>
          <div>
            <a href="/dashboard">Dashboard</a>
            <a href="/logout" style="color:#ff6b9d;">Logout</a>
          </div>
        </div>"""
    flashes = "".join(
        f'<div class="flash {cat}">{msg}</div>'
        for cat, msg in session.pop("_flashes", [])
    )
    return f"""
    <!DOCTYPE html>
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>RITESH | EXPLOITS</title>{BASE_CSS}</head>
    <body><div class="container">{logo_html()}{nav}{flashes}{content}</div></body></html>
    """


def admin_layout(content):
    nav = """
    <div class="nav">
      <strong>👑 ADMIN PANEL</strong>
      <div>
        <a href="/admin">Dashboard</a>
        <a href="/admin/users">Users</a>
        <a href="/admin/searches">Searches</a>
        <a href="/admin/logout" style="color:#ff6b9d;">Logout</a>
      </div>
    </div>"""
    flashes = "".join(
        f'<div class="flash {cat}">{msg}</div>'
        for cat, msg in session.pop("_flashes", [])
    )
    return f"""
    <!DOCTYPE html>
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Admin - RITESH | EXPLOITS</title>{BASE_CSS}</head>
    <body><div class="container">{logo_html()}{nav}{flashes}{content}</div></body></html>
    """


# ============================================================
# PUBLIC ROUTES
# ============================================================
@app.route("/")
def index():
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    if session.get("user_mobile"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form.get("mobile", "").strip()
        password = request.form.get("password", "")
        conn = get_conn()
        user = conn.execute("SELECT * FROM users WHERE mobile=?", (mobile,)).fetchone()
        conn.close()
        if user and user["password_hash"] == hash_password(password):
            session["user_mobile"] = mobile
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid mobile or password", "error")
    content = """
    <div class="card" style="max-width:440px;margin:20px auto;">
      <h1 style="text-align:center;">🔐 USER LOGIN</h1>
      <form method="post">
        <input name="mobile" placeholder="Mobile Number" required>
        <input name="password" type="password" placeholder="Password" required>
        <button type="submit" class="green">LOGIN</button>
      </form>
      <p style="margin-top:18px;text-align:center;color:#7ec4ff;">
        New user? <a href="/register">Register</a>
      </p>
      <p style="text-align:center;margin-top:10px;">
        <a href="/admin/login" style="color:#4a6c99;font-size:12px;">Admin Login</a>
      </p>
    </div>"""
    return user_layout(content)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        mobile = request.form.get("mobile", "").strip()
        password = request.form.get("password", "")
        if not mobile or not password:
            flash("All fields required", "error")
        elif len(password) < 4:
            flash("Password must be at least 4 characters", "error")
        else:
            conn = get_conn()
            try:
                conn.execute(
                    "INSERT INTO users (mobile, password_hash, balance, created_at) VALUES (?, ?, 0, ?)",
                    (mobile, hash_password(password), datetime.now().isoformat())
                )
                conn.commit()
                flash("Registered! Please login.", "success")
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Mobile already registered", "error")
            conn.close()
    content = """
    <div class="card" style="max-width:440px;margin:20px auto;">
      <h1 style="text-align:center;">📝 REGISTER</h1>
      <form method="post">
        <input name="mobile" placeholder="Mobile Number" required>
        <input name="password" type="password" placeholder="Password (min 4)" required>
        <button type="submit" class="green">CREATE ACCOUNT</button>
      </form>
      <p style="margin-top:18px;text-align:center;color:#7ec4ff;">
        Already registered? <a href="/login">Login</a>
      </p>
    </div>"""
    return user_layout(content)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ============================================================
# API CALLS
# ============================================================
def call_num_info(number, key):
    try:
        r = requests.get(API_BASE, params={"": "num_info", "key": key, "num": number}, timeout=20)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {e}"}


def call_ultra_vehicle(vehicle_no, key):
    try:
        r = requests.get(API_BASE, params={"": "ultra_vehicle", "key": key, "xr": vehicle_no}, timeout=20)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {e}"}


def call_aadhaar(aadhaar, key):
    try:
        r = requests.get(API_BASE, params={"": "addhaar2num", "key": key, "q": aadhaar}, timeout=20)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {e}"}


# ============================================================
# USER DASHBOARD
# ============================================================
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    mobile = session["user_mobile"]
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE mobile=?", (mobile,)).fetchone()

    if not user:
        conn.close()
        session.clear()
        return redirect(url_for("login"))

    result = None
    api_type = request.form.get("api_type", "num_info")
    query = request.form.get("query", "").strip()

    if request.method == "POST" and query:
        if user["balance"] < COST_PER_SEARCH:
            flash(f"Insufficient balance. You need ₹{COST_PER_SEARCH}.", "error")
        else:
            new_balance = user["balance"] - COST_PER_SEARCH
            conn.execute("UPDATE users SET balance=? WHERE mobile=?", (new_balance, mobile))

            if api_type == "num_info":
                result = call_num_info(query, NUM_INFO_KEY)
            elif api_type == "ultra_vehicle":
                result = call_ultra_vehicle(query, ULTRA_VEHICLE_KEY)
            elif api_type == "addhaar2num":
                result = call_aadhaar(query, NUM_INFO_KEY)
            else:
                result = {"status": "error", "message": "Unknown API"}

            status = "success" if result.get("status") == "success" else "failed"
            conn.execute(
                "INSERT INTO searches (mobile, api_name, query, cost, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (mobile, api_type, query, COST_PER_SEARCH, status, datetime.now().isoformat())
            )
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE mobile=?", (mobile,)).fetchone()

    conn.close()

    result_html = render_premium_result(result) if result is not None else ""

    content = f"""
    <div class="card">
      <h1>🔎 API SEARCH</h1>
      <div class="balance">💰 BALANCE: ₹{user['balance']:.2f} &nbsp;|&nbsp; COST PER SEARCH: ₹{COST_PER_SEARCH}</div>
      <form action="/dashboard" method="post">
        <select name="api_type" id="api_type" onchange="updatePlaceholder()">
          <option value="num_info" {'selected' if api_type=='num_info' else ''}>📞 Mobile Number Info</option>
          <option value="ultra_vehicle" {'selected' if api_type=='ultra_vehicle' else ''}>🚗 Vehicle Info</option>
          <option value="addhaar2num" {'selected' if api_type=='addhaar2num' else ''}>🆔 Aadhaar → Mobile</option>
        </select>
        <input name="query" id="query" placeholder="Enter Mobile Number" value="{query}" required>
        <button type="submit" class="green">🔍 SEARCH (₹{COST_PER_SEARCH})</button>
      </form>
      {result_html}
    </div>
    <script>
    function updatePlaceholder() {{
      var t = document.getElementById('api_type').value;
      var q = document.getElementById('query');
      if (t === 'num_info') q.placeholder = 'Enter Mobile Number (10 digit)';
      else if (t === 'ultra_vehicle') q.placeholder = 'Enter Vehicle Number (e.g. HR55AL0051)';
      else q.placeholder = 'Enter Aadhaar Number';
    }}
    updatePlaceholder();
    </script>
    """
    return user_layout(content, mobile)


# ============================================================
# ADMIN ROUTES
# ============================================================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session["admin"] = True
            flash("Admin login successful", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials", "error")
    content = """
    <div class="card" style="max-width:440px;margin:20px auto;">
      <h1 style="text-align:center;">👑 ADMIN LOGIN</h1>
      <form method="post">
        <input name="username" placeholder="Admin Username" required>
        <input name="password" type="password" placeholder="Password" required>
        <button type="submit">LOGIN</button>
      </form>
    </div>"""
    return admin_layout(content)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin", methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    result = None
    api_type = request.form.get("api_type", "num_info") if request.method == "POST" else "num_info"
    query = request.form.get("query", "").strip()

    if request.method == "POST" and query:
        if api_type == "num_info":
            result = call_num_info(query, ADMIN_SEARCH_KEY)
        elif api_type == "ultra_vehicle":
            result = call_ultra_vehicle(query, ADMIN_SEARCH_KEY)
        elif api_type == "addhaar2num":
            result = call_aadhaar(query, ADMIN_SEARCH_KEY)

        conn = get_conn()
        status = "success" if (result or {}).get("status") == "success" else "failed"
        conn.execute(
            "INSERT INTO searches (mobile, api_name, query, cost, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("ADMIN", api_type, query, 0, status, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    result_html = render_premium_result(result) if result is not None else ""

    conn = get_conn()
    total_users = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
    total_searches = conn.execute("SELECT COUNT(*) c FROM searches").fetchone()["c"]
    conn.close()

    content = f"""
    <div class="card">
      <h1>📊 ADMIN DASHBOARD</h1>
      <p style="color:#7ec4ff;font-weight:700;">
        👥 Total Users: <b style="color:#00e0ff;">{total_users}</b> &nbsp;|&nbsp;
        🔎 Total Searches: <b style="color:#00e0ff;">{total_searches}</b> &nbsp;|&nbsp;
        👑 Unlimited
      </p>
    </div>
    <div class="card">
      <h2>🔎 UNLIMITED SEARCH</h2>
      <form method="post">
        <select name="api_type">
          <option value="num_info" {'selected' if api_type=='num_info' else ''}>📞 Mobile Number Info</option>
          <option value="ultra_vehicle" {'selected' if api_type=='ultra_vehicle' else ''}>🚗 Vehicle Info</option>
          <option value="addhaar2num" {'selected' if api_type=='addhaar2num' else ''}>🆔 Aadhaar → Mobile</option>
        </select>
        <input name="query" placeholder="Enter value" value="{query}" required>
        <button type="submit" class="green">🔍 SEARCH (UNLIMITED)</button>
      </form>
      {result_html}
    </div>"""
    return admin_layout(content)


@app.route("/admin/users", methods=["GET", "POST"])
@admin_required
def admin_users():
    conn = get_conn()
    if request.method == "POST":
        action = request.form.get("action")
        mobile = request.form.get("mobile", "").strip()
        if action == "add_balance":
            amt = float(request.form.get("amount", 0))
            conn.execute("UPDATE users SET balance = balance + ? WHERE mobile=?", (amt, mobile))
            flash(f"Added ₹{amt} to {mobile}", "success")
        elif action == "delete":
            conn.execute("DELETE FROM users WHERE mobile=?", (mobile,))
            flash(f"Deleted user {mobile}", "success")
        conn.commit()

    users = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    conn.close()

    rows = "".join(
        f"<tr><td>{u['mobile']}</td><td style='color:#6dffce;'>₹{u['balance']:.2f}</td>"
        f"<td>{u['created_at'][:10] if u['created_at'] else ''}</td>"
        f"<td>"
        f"<form method='post' style='display:inline;' onsubmit='return confirm(\"Add balance?\")'>"
        f"<input type='hidden' name='action' value='add_balance'>"
        f"<input type='hidden' name='mobile' value='{u['mobile']}'>"
        f"<input name='amount' type='number' step='0.01' placeholder='₹' style='width:80px;display:inline;margin:0;' required>"
        f"<button type='submit' class='green' style='width:auto;padding:6px 12px;margin:0;font-size:12px;'>+ADD</button>"
        f"</form> "
        f"<form method='post' style='display:inline;' onsubmit='return confirm(\"Delete user?\")'>"
        f"<input type='hidden' name='action' value='delete'>"
        f"<input type='hidden' name='mobile' value='{u['mobile']}'>"
        f"<button type='submit' class='red' style='width:auto;padding:6px 12px;margin:0;font-size:12px;'>DEL</button>"
        f"</form>"
        f"</td></tr>"
        for u in users
    )

    content = f"""
    <div class="card">
      <h1>👥 USERS</h1>
      <table>
        <tr><th>Mobile</th><th>Balance</th><th>Created</th><th>Actions</th></tr>
        {rows if users else '<tr><td colspan=4 style="text-align:center;color:#4a6c99;">No users yet</td></tr>'}
      </table>
    </div>"""
    return admin_layout(content)


@app.route("/admin/searches")
@admin_required
def admin_searches():
    conn = get_conn()
    searches = conn.execute("SELECT * FROM searches ORDER BY id DESC LIMIT 500").fetchall()
    conn.close()

    rows = "".join(
        f"<tr><td>{s['mobile']}</td><td>{s['api_name']}</td>"
        f"<td>{s['query']}</td><td>₹{s['cost']}</td>"
        f"<td style='color:{'#6dffce' if s['status']=='success' else '#ff9bb3'};'>{s['status']}</td>"
        f"<td>{s['created_at'][:19] if s['created_at'] else ''}</td></tr>"
        for s in searches
    )

    content = f"""
    <div class="card">
      <h1>📋 SEARCH HISTORY (LAST 500)</h1>
      <table>
        <tr><th>User</th><th>API</th><th>Query</th><th>Cost</th><th>Status</th><th>Time</th></tr>
        {rows if searches else '<tr><td colspan=6 style="text-align:center;color:#4a6c99;">No searches yet</td></tr>'}
      </table>
    </div>"""
    return admin_layout(content)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print("  ⏤͟͟͞͞RITESH | EXPLOITS  —  PREMIUM API HUB")
    print("=" * 60)
    print(f"  Admin URL:      http://127.0.0.1:5000/admin/login")
    print(f"  Admin User:     {ADMIN_USERNAME}")
    print(f"  Admin Password: {ADMIN_PASSWORD}")
    print(f"  User Login:     http://127.0.0.1:5000/login")
    print(f"  Cost/Search:    ₹{COST_PER_SEARCH}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)