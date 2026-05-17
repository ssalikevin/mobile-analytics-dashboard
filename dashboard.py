#!/usr/bin/env python3
"""
Mobile Usage Analytics Dashboard
Clean, professional design — perfect in both light and dark mode.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import time

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Mobile Usage Analytics",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Mobile Usage Analytics System — Big Data Analysis Project"
    }
)

# ── THEME STATE ────────────────────────────────────────────────────────────────

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

D = st.session_state.dark_mode

# ── COLOUR TOKENS ─────────────────────────────────────────────────────────────
# Every single colour in the UI comes from here.
# Nothing is hardcoded inside components.

if D:
    # ── DARK PALETTE ──
    ROOT_BG          = "#0D1117"
    SURFACE          = "#161B22"
    SURFACE2         = "#1C2128"
    BORDER           = "#30363D"
    BORDER_SOFT      = "#21262D"

    TXT_HEAD         = "#E6EDF3"
    TXT_BODY         = "#C9D1D9"
    TXT_MUTED        = "#8B949E"
    TXT_FAINT        = "#484F58"

    ACCENT           = "#58A6FF"
    ACCENT_DIM       = "#1F6FEB"
    ACCENT_GLOW      = "rgba(88,166,255,0.15)"

    OK               = "#3FB950"
    OK_BG            = "rgba(63,185,80,0.12)"
    OK_BORDER        = "rgba(63,185,80,0.35)"

    WARN             = "#D29922"
    WARN_BG          = "rgba(210,153,34,0.12)"
    WARN_BORDER      = "rgba(210,153,34,0.35)"

    PILL_OPEN_BG     = "rgba(63,185,80,0.15)"
    PILL_OPEN_TXT    = "#3FB950"
    PILL_CLOSE_BG   = "rgba(210,153,34,0.15)"
    PILL_CLOSE_TXT  = "#D29922"

    METRIC_BG        = "#161B22"
    METRIC_BORDER    = "#30363D"
    CHART_BG         = "rgba(0,0,0,0)"
    GRID             = "#21262D"
    PLOTLY_T         = "plotly_dark"

    BTN_BG           = "#FFD700"
    BTN_FG           = "#0D1117"
    BTN_ICON         = "☀️"
    BTN_LABEL        = "Light Mode"

else:
    # ── LIGHT PALETTE ──
    ROOT_BG          = "#F6F8FA"
    SURFACE          = "#FFFFFF"
    SURFACE2         = "#F6F8FA"
    BORDER           = "#D0D7DE"
    BORDER_SOFT      = "#EAEEF2"

    TXT_HEAD         = "#1F2328"
    TXT_BODY         = "#36393D"
    TXT_MUTED        = "#57606A"
    TXT_FAINT        = "#B0B7BF"

    ACCENT           = "#0969DA"
    ACCENT_DIM       = "#0550AE"
    ACCENT_GLOW      = "rgba(9,105,218,0.08)"

    OK               = "#1A7F37"
    OK_BG            = "rgba(26,127,55,0.08)"
    OK_BORDER        = "rgba(26,127,55,0.25)"

    WARN             = "#9A6700"
    WARN_BG          = "rgba(154,103,0,0.08)"
    WARN_BORDER      = "rgba(154,103,0,0.25)"

    PILL_OPEN_BG     = "rgba(26,127,55,0.1)"
    PILL_OPEN_TXT    = "#1A7F37"
    PILL_CLOSE_BG   = "rgba(154,103,0,0.1)"
    PILL_CLOSE_TXT  = "#9A6700"

    METRIC_BG        = "#FFFFFF"
    METRIC_BORDER    = "#D0D7DE"
    CHART_BG         = "rgba(0,0,0,0)"
    GRID             = "#EAEEF2"
    PLOTLY_T         = "plotly_white"

    BTN_BG           = "#1F2328"
    BTN_FG           = "#FFFFFF"
    BTN_ICON         = "🌙"
    BTN_LABEL        = "Dark Mode"

# ── HIDE STREAMLIT CHROME ──────────────────────────────────────────────────────
# Hides: running man, stop button, deploy button,
#        top-right toolbar, manage app footer, made-with-streamlit

HIDE_CHROME = """
<style>
/* Top toolbar (running man, stop, deploy, 3-dot menu) */
header[data-testid="stHeader"] {
    display: none !important;
}

/* The fixed top bar gap that header leaves behind */
.stApp > header { display: none !important; }
.stApp { margin-top: 0 !important; }
.block-container { padding-top: 1.5rem !important; }

/* "Manage app" bottom-right button */
[data-testid="manage-app-button"],
.st-emotion-cache-h4xjwg,
.streamlit-wide ._profileContainer_gzau3_53,
button[kind="borderlessIcon"][aria-label*="Manage"],
div[data-testid="stToolbar"],
div.stToolbar,
#stToolbar,
.viewerBadge_container__r5tak,
.viewerBadge_link__qRIco,
footer,
footer a,
.footer {
    display: none !important;
    visibility: hidden !important;
}

/* "Made with Streamlit" & hosted badge */
#MainMenu { visibility: hidden !important; }
</style>
"""
st.markdown(HIDE_CHROME, unsafe_allow_html=True)

# ── FULL THEME CSS ─────────────────────────────────────────────────────────────

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

/* ── Root ── */
.stApp {{
    background-color: {ROOT_BG} !important;
    font-family: 'Inter', sans-serif !important;
    color: {TXT_BODY} !important;
}}
.main .block-container {{
    background: {ROOT_BG} !important;
    max-width: 1380px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 3rem !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {SURFACE} !important;
    border-right: 1px solid {BORDER} !important;
    min-width: 240px !important;
    max-width: 260px !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 1.4rem 1.2rem !important;
}}
[data-testid="stSidebar"] * {{
    color: {TXT_BODY} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {{
    background: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TXT_BODY} !important;
}}
[data-testid="stSelectbox"] svg {{
    fill: {TXT_MUTED} !important;
}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
    background: {METRIC_BG} !important;
    border: 1px solid {METRIC_BORDER} !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    transition: border-color 0.2s;
}}
[data-testid="stMetric"]:hover {{
    border-color: {ACCENT} !important;
}}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] div {{
    color: {TXT_MUTED} !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}}
[data-testid="stMetricValue"] div {{
    color: {TXT_HEAD} !important;
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    line-height: 1.15 !important;
}}

/* ── Toggle ── */
[data-testid="stToggle"] p {{
    color: {TXT_BODY} !important;
    font-size: 0.82rem !important;
}}

/* ── Slider ── */
[data-testid="stSlider"] p {{
    color: {TXT_MUTED} !important;
    font-size: 0.8rem !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {{
    background: {ACCENT} !important;
}}

/* ── Divider ── */
hr {{
    border: none !important;
    border-top: 1px solid {BORDER} !important;
    margin: 1.25rem 0 !important;
}}

/* ── Caption ── */
[data-testid="stCaptionContainer"] p {{
    color: {TXT_MUTED} !important;
    font-size: 0.76rem !important;
}}

/* ── Info box ── */
[data-testid="stAlert"] {{
    background: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TXT_BODY} !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] iframe {{
    border-radius: 10px !important;
}}

/* ── Button (theme toggle) ── */
[data-testid="stButton"] button {{
    background: {BTN_BG} !important;
    color: {BTN_FG} !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.45rem 1rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}}
[data-testid="stButton"] button:hover {{
    opacity: 0.85 !important;
}}

/* ── Headings ── */
h1, h2, h3, h4, h5 {{
    color: {TXT_HEAD} !important;
    font-family: 'Inter', sans-serif !important;
}}
p, span, label, div {{
    font-family: 'Inter', sans-serif !important;
}}

/* ── CUSTOM COMPONENTS ── */

/* Page header */
.ph-wrap {{
    padding-bottom: 1rem;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 1.5rem;
}}
.ph-title {{
    font-size: 1.65rem;
    font-weight: 800;
    color: {TXT_HEAD};
    letter-spacing: -0.03em;
    line-height: 1.2;
}}
.ph-sub {{
    font-size: 0.82rem;
    color: {TXT_MUTED};
    margin-top: 0.3rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}}
.ph-badge {{
    background: {ACCENT_GLOW};
    color: {ACCENT};
    border: 1px solid {ACCENT_DIM};
    border-radius: 20px;
    padding: 0.1rem 0.6rem;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}}

/* Section label */
.slabel {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.5rem 0 0.9rem 0;
}}
.slabel-text {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {TXT_MUTED};
    white-space: nowrap;
}}
.slabel-line {{
    flex: 1;
    height: 1px;
    background: {BORDER};
}}
.live-pulse {{
    width: 8px;
    height: 8px;
    background: #F85149;
    border-radius: 50%;
    flex-shrink: 0;
    animation: livepulse 1.8s ease-in-out infinite;
}}
@keyframes livepulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(248,81,73,0.4); }}
    50% {{ opacity: 0.7; transform: scale(1.2); box-shadow: 0 0 0 5px rgba(248,81,73,0); }}
}}

/* User cards */
.ucard {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.65rem 0.85rem;
    border-radius: 10px;
    margin-bottom: 0.45rem;
    border: 1px solid {BORDER};
    background: {SURFACE};
    transition: border-color 0.2s, background 0.2s;
}}
.ucard.active {{
    background: {OK_BG};
    border: 1px solid {OK_BORDER};
}}
.ucard.idle {{
    background: {SURFACE2};
    border: 1px solid {BORDER_SOFT};
}}
.udot {{
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
}}
.udot.active {{
    background: {OK};
    box-shadow: 0 0 0 3px {OK_BG};
}}
.udot.idle {{
    background: {TXT_FAINT};
}}
.uname {{
    font-size: 0.88rem;
    font-weight: 600;
    color: {TXT_HEAD};
    flex: 1;
}}
.utime {{
    font-size: 0.72rem;
    color: {TXT_MUTED};
    font-family: 'JetBrains Mono', monospace;
}}
.ubadge {{
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    padding: 0.13rem 0.5rem;
    border-radius: 20px;
    border: 1px solid transparent;
}}
.ubadge.active {{
    background: {OK_BG};
    color: {OK};
    border-color: {OK_BORDER};
}}
.ubadge.idle {{
    background: {SURFACE2};
    color: {TXT_MUTED};
    border-color: {BORDER};
}}
.ubadge.offline {{
    background: transparent;
    color: {TXT_FAINT};
    border-color: {BORDER_SOFT};
}}

/* Event feed container */
.feed-wrap {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    overflow: hidden;
}}
.feed-head {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid {BORDER};
    background: {SURFACE2};
}}
.feed-head-label {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {TXT_MUTED};
    flex: 1;
}}
.feed-count {{
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    color: {TXT_MUTED};
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 0.1rem 0.5rem;
}}
.feed-scroll {{
    max-height: 330px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: {BORDER} transparent;
}}
.feed-scroll::-webkit-scrollbar {{ width: 4px; }}
.feed-scroll::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 4px; }}
.feed-scroll::-webkit-scrollbar-track {{ background: transparent; }}

/* Event row */
.ev-row {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.6rem 1rem;
    border-bottom: 1px solid {BORDER_SOFT};
    transition: background 0.15s;
}}
.ev-row:last-child {{ border-bottom: none; }}
.ev-row:hover {{ background: {SURFACE2}; }}
.ev-time {{
    font-size: 0.71rem;
    color: {TXT_MUTED};
    font-family: 'JetBrains Mono', monospace;
    min-width: 58px;
    flex-shrink: 0;
}}
.ev-avatar {{
    width: 27px;
    height: 27px;
    border-radius: 50%;
    background: linear-gradient(135deg, {ACCENT_DIM}, {ACCENT});
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.62rem;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
    letter-spacing: 0.02em;
}}
.ev-text {{
    font-size: 0.82rem;
    color: {TXT_BODY};
    flex: 1;
    line-height: 1.35;
}}
.ev-text b {{
    color: {ACCENT};
    font-weight: 600;
}}
.ev-pill {{
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.13rem 0.5rem;
    border-radius: 20px;
    border: 1px solid transparent;
    flex-shrink: 0;
}}
.ev-pill.open {{
    background: {PILL_OPEN_BG};
    color: {PILL_OPEN_TXT};
    border-color: {OK_BORDER};
}}
.ev-pill.close {{
    background: {PILL_CLOSE_BG};
    color: {PILL_CLOSE_TXT};
    border-color: {WARN_BORDER};
}}

/* Chart card */
.ccrd {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 1rem 1.1rem 0.4rem 1.1rem;
    height: 100%;
}}
.ccrd-title {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: {TXT_MUTED};
    margin-bottom: 0.6rem;
}}

/* Empty state */
.empty {{
    text-align: center;
    padding: 2rem 1rem;
    color: {TXT_MUTED};
    font-size: 0.85rem;
    line-height: 1.6;
}}
.empty-icon {{ font-size: 1.8rem; margin-bottom: 0.5rem; }}

/* Sidebar labels */
.sb-label {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {TXT_MUTED};
    margin: 1rem 0 0.4rem 0;
}}

/* Status rows */
.st-row {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0;
}}
.st-dot {{
    width: 7px; height: 7px;
    border-radius: 50%;
    background: {OK};
    box-shadow: 0 0 0 2px {OK_BG};
    flex-shrink: 0;
}}
.st-key {{
    font-size: 0.78rem;
    color: {TXT_MUTED};
    flex: 1;
}}
.st-val {{
    font-size: 0.71rem;
    color: {TXT_BODY};
    font-family: 'JetBrains Mono', monospace;
}}

/* Footer */
.dash-footer {{
    margin-top: 2rem;
    padding-top: 1.25rem;
    border-top: 1px solid {BORDER};
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1.25rem;
    flex-wrap: wrap;
}}
.df-item {{
    font-size: 0.74rem;
    color: {TXT_MUTED};
}}
.df-sep {{
    width: 3px; height: 3px;
    border-radius: 50%;
    background: {BORDER};
    flex-shrink: 0;
}}
.df-accent {{
    color: {ACCENT};
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.71rem;
}}

</style>
""", unsafe_allow_html=True)


# ── FIREBASE ───────────────────────────────────────────────────────────────────

@st.cache_resource
def init_firebase():
    import firebase_admin
    from firebase_admin import credentials, db
    if firebase_admin._apps:
        return db
    try:
        if "firebase" in st.secrets:
            cred = credentials.Certificate(dict(st.secrets["firebase"]))
        else:
            p = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "credentials", "firebase-credentials.json"
            )
            cred = credentials.Certificate(p)
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://learning-for-project-e4909-default-rtdb.europe-west1.firebasedatabase.app/"
        })
        return db
    except Exception as e:
        st.error(f"Firebase: {e}")
        return None


def fetch_events(db, minutes=60):
    try:
        from firebase_admin import db as fdb
        raw = fdb.reference("events").get()
        if not raw:
            return []
        events, cutoff = [], datetime.now() - timedelta(minutes=minutes)
        for k, ev in raw.items():
            try:
                ts = datetime.strptime(ev.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
                if ts >= cutoff:
                    ev["_dt"] = ts
                    events.append(ev)
            except Exception:
                continue
        events.sort(key=lambda x: x["_dt"], reverse=True)
        return events
    except Exception:
        return []


def user_status(events, idle_min=5):
    now, seen = datetime.now(), {}
    for ev in events:
        u = ev.get("user_name", "?").lower()
        t = ev.get("_dt", now)
        if u not in seen or t > seen[u]:
            seen[u] = t
    return {
        u: {
            "secs": int((now - t).total_seconds()),
            "active": (now - t).total_seconds() <= idle_min * 60
        }
        for u, t in seen.items()
    }


def load_summary():
    for p in [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "exports", "summary.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary.json"),
    ]:
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)
    return None


# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:

    # Branding
    st.markdown(f"""
    <div style="padding-bottom:1rem; border-bottom:1px solid {BORDER}; margin-bottom:0.5rem">
        <div style="font-size:1.05rem;font-weight:800;color:{TXT_HEAD};
                    letter-spacing:-0.02em;line-height:1.2">
            📱 Mobile Analytics
        </div>
        <div style="font-size:0.74rem;color:{TXT_MUTED};margin-top:0.2rem">
            Big Data Analysis Project
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Theme toggle
    st.markdown(f'<div class="sb-label">Display</div>', unsafe_allow_html=True)
    st.button(f"{BTN_ICON}  {BTN_LABEL}", on_click=toggle_theme,
              use_container_width=True, key="theme_btn")

    # Filters
    st.markdown(f'<div class="sb-label">Time Range</div>', unsafe_allow_html=True)
    time_filter = st.selectbox("", ["Last 5 minutes", "Last hour", "Last 24 hours"],
                               index=1, label_visibility="collapsed")
    selected_min = {"Last 5 minutes": 5, "Last hour": 60, "Last 24 hours": 1440}[time_filter]

    st.markdown(f'<div class="sb-label">User</div>', unsafe_allow_html=True)
    # Use cached user list from previous refresh cycle.
    # On first load it shows only "All users".
    # After first data fetch, session_state["known_users"] is populated
    # and the dropdown shows all real users dynamically.
    _known = st.session_state.get("known_users", [])
    user_filter = st.selectbox("", ["All users"] + _known,
                               label_visibility="collapsed")

    # Refresh
    st.markdown(f'<div class="sb-label">Auto Refresh</div>', unsafe_allow_html=True)
    auto_refresh = st.toggle("Enabled", value=True)
    refresh_sec  = st.slider("Interval (s)", 5, 60, 10)

    # Cluster status
    st.markdown(f'<div class="sb-label">Cluster</div>', unsafe_allow_html=True)
    for label, val in [("HDFS", "ssali:9000"), ("YARN", "ssali:8088"), ("Pipeline", "Automated")]:
        st.markdown(f"""
        <div class="st-row">
            <div class="st-dot"></div>
            <span class="st-key">{label}</span>
            <span class="st-val">{val}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:1rem;font-size:0.7rem;
                font-family:'JetBrains Mono',monospace;color:{TXT_FAINT}">
        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)


# ── DATA ───────────────────────────────────────────────────────────────────────

firebase_db  = init_firebase()
all_evs      = fetch_events(firebase_db, minutes=selected_min) if firebase_db else []
summary      = load_summary()

# Build user_id → name map from live events (e.g. U001 → kevin)
uid_to_name = {}
for _e in all_evs:
    _uname = _e.get("user_name", "").strip().lower()
    _uid   = _e.get("user_id",   "").strip().upper()
    if _uname and _uid and _uid not in uid_to_name:
        uid_to_name[_uid] = _uname

# Update known_users in session_state so sidebar dropdown stays dynamic
_live_names_fresh = sorted(set(
    e.get("user_name", "").strip().lower()
    for e in all_evs
    if e.get("user_name", "").strip()
))
_summary_names_fresh = sorted(set(
    uid_to_name.get(u.get("user_id","").upper(), u.get("user_id","").lower())
    for u in (summary or {}).get("screen_time", [])
    if u.get("user_id", "")
))
_combined = sorted(set(_live_names_fresh + _summary_names_fresh))
if _combined:
    st.session_state["known_users"] = _combined

live_evs = all_evs if user_filter == "All users" else [
    e for e in all_evs if e.get("user_name", "").lower() == user_filter.lower()
]

ustatus      = user_status(live_evs)
active_count = sum(1 for u in ustatus.values() if u["active"])
total_secs   = sum(u.get("total_seconds", 0) for u in (summary or {}).get("screen_time", []))
total_apps   = len((summary or {}).get("top_apps", []))


# ── HEADER ─────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="ph-wrap">
    <div class="ph-title">📱 Mobile Usage Analytics</div>
    <div class="ph-sub">
        Real-time monitoring &nbsp;·&nbsp; Hadoop MapReduce batch layer
        &nbsp;·&nbsp; Big Data Analysis Project
        <span class="ph-badge">mobile-analytics-cs-class.streamlit.app</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── METRICS ────────────────────────────────────────────────────────────────────

m1, m2, m3, m4, m5 = st.columns(5)
with m1: st.metric("Active Users",    f"{active_count} / 5")
with m2: st.metric("Live Events",     f"{len(live_evs):,}")
with m3: st.metric("Screen Time",     f"{round(total_secs/60,1)} min")
with m4: st.metric("Apps Tracked",    str(total_apps))
with m5: st.metric("Updated",         datetime.now().strftime("%H:%M:%S"))

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)


# ── LIVE SECTION ───────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="slabel">
    <div class="live-pulse"></div>
    <span class="slabel-text">Live Activity</span>
    <div class="slabel-line"></div>
</div>
""", unsafe_allow_html=True)

col_users, col_feed = st.columns([5, 7], gap="large")

# User status cards
with col_users:
    # ALL users = everyone seen in live events OR in HDFS summary
    _seen_live = sorted(set(
        e.get("user_name", "").strip().lower()
        for e in all_evs
        if e.get("user_name", "").strip()
    ))
    _seen_summary = sorted(set(
        u.get("user_id", "").lower()
        for u in (summary or {}).get("screen_time", [])
        if u.get("user_id", "")
    ))
    ALL = sorted(set(_seen_live + _seen_summary))
    if not ALL:
        ALL = ["no users yet"]
    show = [user_filter.lower()] if user_filter != "All users" else ALL

    cards = ""
    for u in show:
        if u in ustatus:
            s   = ustatus[u]["secs"]
            act = ustatus[u]["active"]
            cls = "active" if act else "idle"
            dot = "active" if act else "idle"
            badge_cls = "active" if act else "idle"
            badge_txt = "Live" if act else "Idle"
            t_str = (f"{s}s ago" if s < 60 else f"{s//60}m {s%60}s ago") if s < 3600 else f"{s//3600}h ago"
        else:
            cls, dot, badge_cls, badge_txt, t_str = "idle", "idle", "offline", "Offline", "No data"

        cards += f"""
        <div class="ucard {cls}">
            <div class="udot {dot}"></div>
            <span class="uname">{u.capitalize()}</span>
            <span class="utime">{t_str}</span>
            <span class="ubadge {badge_cls}">{badge_txt}</span>
        </div>"""

    st.markdown(cards, unsafe_allow_html=True)

# Event feed
with col_feed:
    if not live_evs:
        st.markdown(f"""
        <div class="feed-wrap">
            <div class="feed-head">
                <div class="live-pulse"></div>
                <span class="feed-head-label">Activity Feed</span>
            </div>
            <div class="empty">
                <div class="empty-icon">📭</div>
                No events in the selected time range.<br>
                <span style="font-size:0.78rem;color:{TXT_FAINT}">
                Make sure phones are running the logger app.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        rows = ""
        for ev in live_evs[:20]:
            ts       = ev.get("_dt", datetime.now())
            uname    = ev.get("user_name", "?").capitalize()
            initials = uname[:2].upper()
            pkg      = ev.get("app_name", "unknown")
            app      = pkg.split(".")[-2].capitalize() if "." in pkg else pkg.capitalize()
            etype    = ev.get("event_type", "").upper()
            dur      = ev.get("duration_seconds", 0)
            pill_cls = "open" if etype == "OPEN" else "close"

            if etype == "OPEN":
                desc = f"opened <b>{app}</b>"
            elif etype == "CLOSE":
                desc = f"used <b>{app}</b> for {dur}s"
            else:
                desc = f"<b>{app}</b>"

            rows += f"""
            <div class="ev-row">
                <span class="ev-time">{ts.strftime('%H:%M:%S')}</span>
                <div class="ev-avatar">{initials}</div>
                <span class="ev-text">{uname} {desc}</span>
                <span class="ev-pill {pill_cls}">{etype}</span>
            </div>"""

        st.markdown(f"""
        <div class="feed-wrap">
            <div class="feed-head">
                <div class="live-pulse"></div>
                <span class="feed-head-label">Activity Feed</span>
                <span class="feed-count">{len(live_evs)} events</span>
            </div>
            <div class="feed-scroll">{rows}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)


# ── HISTORICAL SECTION ─────────────────────────────────────────────────────────

st.markdown(f"""
<div class="slabel">
    <span class="slabel-text">Hadoop Batch Analytics — MapReduce Results</span>
    <div class="slabel-line"></div>
</div>
""", unsafe_allow_html=True)

if not summary:
    st.markdown(f"""
    <div class="ccrd">
        <div class="empty">
            <div class="empty-icon">🗄️</div>
            No historical data yet. Ingestion runs hourly via cron.<br>
            <span style="font-size:0.78rem;color:{TXT_FAINT}">
            Check: /home/kevin/bigdata-project/exports/summary.json</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    gen = summary.get("generated_at", "")
    st.markdown(f"""
    <div style="font-size:0.74rem;color:{TXT_MUTED};margin-bottom:1rem">
        Generated <span style="font-family:'JetBrains Mono',monospace;color:{ACCENT}">{gen}</span>
        &nbsp;·&nbsp; Source: HDFS MapReduce output &nbsp;·&nbsp; Updates every hour
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    BLAYOUT = dict(
        template=PLOTLY_T, height=270,
        margin=dict(t=15, b=35, l=10, r=10),
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(family="Inter", size=11, color=TXT_MUTED),
        showlegend=False,
    )

    # Chart 1 — Screen Time
    with c1:
        st.markdown(f'<div class="ccrd"><div class="ccrd-title">Screen Time per User</div>',
                    unsafe_allow_html=True)
        sd = summary.get("screen_time", [])
        if sd:
            df = pd.DataFrame(sd)
            df["min"] = (df["total_seconds"] / 60).round(1)
            # Map user_id to name for display
            df["display"] = df["user_id"].apply(
                lambda uid: f'{uid_to_name.get(uid.upper(), uid)}\n({uid})'
                if uid_to_name.get(uid.upper()) else uid
            )
            fig = go.Figure(go.Bar(
                x=df["display"], y=df["min"],
                marker=dict(color=df["min"],
                            colorscale=[[0, ACCENT_DIM], [1, ACCENT]],
                            line=dict(width=0)),
                text=df["min"].astype(str) + "m",
                textposition="outside",
                textfont=dict(size=10, color=TXT_BODY, family="JetBrains Mono"),
                hovertemplate="<b>%{x}</b><br>%{y} min<extra></extra>"
            ))
            fig.update_layout(
                template=PLOTLY_T, height=270,
                margin=dict(t=15, b=35, l=10, r=10),
                paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(family="Inter", size=11, color=TXT_MUTED),
                showlegend=False,
                xaxis=dict(showgrid=False, color=TXT_MUTED,
                           tickfont=dict(size=10, color=TXT_MUTED)),
                yaxis=dict(showgrid=True, gridcolor=GRID, color=TXT_MUTED,
                           title=dict(text="minutes", font=dict(size=10))),
            )
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
        else:
            st.markdown('<div class="empty">No data yet</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Chart 2 — Top Apps
    with c2:
        st.markdown(f'<div class="ccrd"><div class="ccrd-title">Top Apps by Usage</div>',
                    unsafe_allow_html=True)
        ad = summary.get("top_apps", [])
        if ad:
            df2 = pd.DataFrame(ad)
            df2["min"] = (df2["total_seconds"] / 60).round(1)
            clrs = [ACCENT if i == 0 else ACCENT_DIM for i in range(len(df2))]
            fig2 = go.Figure(go.Bar(
                y=df2["app_name"], x=df2["total_seconds"],
                orientation="h",
                marker=dict(color=clrs, line=dict(width=0)),
                text=df2["min"].astype(str) + "m",
                textposition="outside",
                textfont=dict(size=10, color=TXT_BODY, family="JetBrains Mono"),
                hovertemplate="<b>%{y}</b><br>%{x}s<extra></extra>"
            ))
            fig2.update_layout(
                template=PLOTLY_T, height=270,
                margin=dict(t=15, b=35, l=10, r=10),
                paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(family="Inter", size=11, color=TXT_MUTED),
                showlegend=False,
                xaxis=dict(showgrid=True, gridcolor=GRID, color=TXT_MUTED,
                           title=dict(text="seconds", font=dict(size=10))),
                yaxis=dict(showgrid=False, color=TXT_HEAD,
                           categoryorder="total ascending",
                           tickfont=dict(size=11, color=TXT_HEAD)),
            )
            st.plotly_chart(fig2, use_container_width=True,
                            config={"displayModeBar": False})
        else:
            st.markdown('<div class="empty">No data yet</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Chart 3 — Hourly
    with c3:
        st.markdown(f'<div class="ccrd"><div class="ccrd-title">Usage by Hour</div>',
                    unsafe_allow_html=True)
        hd = summary.get("hourly_patterns", [])
        if hd:
            df3 = pd.DataFrame(hd)
            df3["min"] = (df3["total_seconds"] / 60).round(1)
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df3["label"], y=df3["min"],
                mode="lines+markers",
                line=dict(color=ACCENT, width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=7, color=ACCENT,
                            line=dict(width=2, color=ROOT_BG)),
                fill="tozeroy",
                fillcolor=ACCENT_GLOW,
                hovertemplate="<b>%{x}</b><br>%{y} min<extra></extra>"
            ))
            fig3.update_layout(
                template=PLOTLY_T, height=270,
                margin=dict(t=15, b=35, l=10, r=10),
                paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(family="Inter", size=11, color=TXT_MUTED),
                showlegend=False,
                xaxis=dict(showgrid=False, color=TXT_MUTED,
                           tickfont=dict(size=9, color=TXT_MUTED), tickangle=-35),
                yaxis=dict(showgrid=True, gridcolor=GRID, color=TXT_MUTED,
                           title=dict(text="minutes", font=dict(size=10))),
            )
            st.plotly_chart(fig3, use_container_width=True,
                            config={"displayModeBar": False})
        else:
            st.markdown('<div class="empty">No data yet</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Summary table
    st.markdown(f"""
    <div class="slabel" style="margin-top:0.5rem">
        <span class="slabel-text">All Users Summary</span>
        <div class="slabel-line"></div>
    </div>
    """, unsafe_allow_html=True)

    raw_sd = summary.get("screen_time", [])
    if raw_sd:
        dft = pd.DataFrame(raw_sd)
        dft["Name"] = dft["user_id"].apply(
            lambda uid: uid_to_name.get(uid.upper(), "Unknown")
        )
        dft = dft.rename(columns={
            "user_id": "User ID", "total_seconds": "Seconds", "total_minutes": "Minutes"
        })
        dft["Hours"] = (dft["Seconds"] / 3600).round(3)
        dft = dft[["User ID", "Name", "Seconds", "Minutes", "Hours"]]
        st.dataframe(dft, use_container_width=True, hide_index=True)


# ── FOOTER ─────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="dash-footer">
    <span class="df-item">📱 Mobile Usage Analytics</span>
    <div class="df-sep"></div>
    <span class="df-item">Big Data Analysis Project</span>
    <div class="df-sep"></div>
    <span class="df-item">Apache Hadoop 3.3.6</span>
    <div class="df-sep"></div>
    <span class="df-item">Firebase Realtime DB</span>
    <div class="df-sep"></div>
    <span class="df-accent">{datetime.now().strftime('%Y-%m-%d')}</span>
</div>
""", unsafe_allow_html=True)


# ── AUTO REFRESH ───────────────────────────────────────────────────────────────

if auto_refresh:
    time.sleep(refresh_sec)
    st.rerun()