#!/usr/bin/env python3
"""
Mobile Usage Analytics Dashboard
Mobile Usage Analytics System
Team: Big Data Analysis Project

Two layers:
  Layer 1 - LIVE: reads directly from Firebase Realtime Database
  Layer 2 - HISTORICAL: reads from HDFS batch export (summary.json)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import time

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Mobile Usage Analytics",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── THEME STATE ───────────────────────────────────────────────────────────────

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode


# ── THEME VARIABLES ───────────────────────────────────────────────────────────

if st.session_state.dark_mode:
    # Dark mode colors
    BG_COLOR         = "#0e1117"
    CARD_BG          = "#1a1d24"
    TEXT_PRIMARY     = "#ffffff"
    TEXT_SECONDARY   = "#aaaaaa"
    ACCENT_BLUE      = "#4DA6FF"
    ACCENT_BLUE2     = "#2E75B6"
    ACTIVE_BG        = "#1a472a"
    ACTIVE_BORDER    = "#28a745"
    ACTIVE_TEXT      = "#90EE90"
    IDLE_BG          = "#2a2a2a"
    IDLE_BORDER      = "#6c757d"
    IDLE_TEXT        = "#aaaaaa"
    EVENT_BG         = "#2a2200"
    EVENT_BORDER     = "#ffc107"
    EVENT_TEXT       = "#FFD966"
    SECTION_COLOR    = "#4DA6FF"
    FOOTER_COLOR     = "#666666"
    PLOTLY_TEMPLATE  = "plotly_dark"
    TOGGLE_LABEL     = "☀️ Switch to Light Mode"
    TOGGLE_BG        = "#FFD700"
    TOGGLE_COLOR     = "#000000"
else:
    # Light mode colors
    BG_COLOR         = "#ffffff"
    CARD_BG          = "#f8f9fa"
    TEXT_PRIMARY     = "#000000"
    TEXT_SECONDARY   = "#555555"
    ACCENT_BLUE      = "#1F5C99"
    ACCENT_BLUE2     = "#2E75B6"
    ACTIVE_BG        = "#d4edda"
    ACTIVE_BORDER    = "#28a745"
    ACTIVE_TEXT      = "#155724"
    IDLE_BG          = "#f8f9fa"
    IDLE_BORDER      = "#6c757d"
    IDLE_TEXT        = "#555555"
    EVENT_BG         = "#fff3cd"
    EVENT_BORDER     = "#ffc107"
    EVENT_TEXT       = "#856404"
    SECTION_COLOR    = "#1F5C99"
    FOOTER_COLOR     = "#888888"
    PLOTLY_TEMPLATE  = "plotly_white"
    TOGGLE_LABEL     = "🌙 Switch to Dark Mode"
    TOGGLE_BG        = "#1F5C99"
    TOGGLE_COLOR     = "#ffffff"

# ── DYNAMIC CSS ───────────────────────────────────────────────────────────────

st.markdown(f"""
<style>
    /* Force background color */
    .stApp {{
        background-color: {BG_COLOR};
    }}

    /* Main content area */
    .main .block-container {{
        background-color: {BG_COLOR};
        color: {TEXT_PRIMARY};
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {CARD_BG};
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT_PRIMARY} !important;
    }}

    /* All text */
    p, span, label, div {{
        color: {TEXT_PRIMARY};
    }}

    .main-header {{
        font-size: 2.5rem;
        font-weight: bold;
        color: {ACCENT_BLUE};
        text-align: center;
        padding: 1rem 0;
    }}

    .sub-header {{
        font-size: 1rem;
        color: {TEXT_SECONDARY};
        text-align: center;
        margin-bottom: 2rem;
    }}

    .active-user {{
        background-color: {ACTIVE_BG};
        border-left: 4px solid {ACTIVE_BORDER};
        padding: 0.5rem 0.8rem;
        border-radius: 4px;
        margin: 0.3rem 0;
        color: {ACTIVE_TEXT};
        font-weight: bold;
    }}

    .idle-user {{
        background-color: {IDLE_BG};
        border-left: 4px solid {IDLE_BORDER};
        padding: 0.5rem 0.8rem;
        border-radius: 4px;
        margin: 0.3rem 0;
        color: {IDLE_TEXT};
    }}

    .live-event {{
        background-color: {EVENT_BG};
        border-left: 4px solid {EVENT_BORDER};
        padding: 0.4rem 0.8rem;
        border-radius: 4px;
        margin: 0.2rem 0;
        font-size: 0.9rem;
        color: {EVENT_TEXT};
    }}

    .section-header {{
        font-size: 1.3rem;
        font-weight: bold;
        color: {SECTION_COLOR};
        border-bottom: 2px solid {ACCENT_BLUE2};
        padding-bottom: 0.3rem;
        margin: 1rem 0 0.8rem 0;
    }}

    .theme-toggle {{
        display: inline-block;
        background-color: {TOGGLE_BG};
        color: {TOGGLE_COLOR};
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        cursor: pointer;
        border: none;
        margin-bottom: 1rem;
    }}

    /* Metric labels */
    [data-testid="stMetricLabel"] {{
        color: {TEXT_SECONDARY} !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {TEXT_PRIMARY} !important;
    }}

    /* Dataframe */
    [data-testid="stDataFrame"] {{
        background-color: {CARD_BG};
        color: {TEXT_PRIMARY};
    }}
</style>
""", unsafe_allow_html=True)

# ── FIREBASE CONNECTION ───────────────────────────────────────────────────────

@st.cache_resource
def init_firebase():
    import firebase_admin
    from firebase_admin import credentials, db

    if firebase_admin._apps:
        return db

    try:
        if "firebase" in st.secrets:
            cred_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(cred_dict)
        else:
            cred_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "credentials", "firebase-credentials.json"
            )
            cred = credentials.Certificate(cred_path)

        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://learning-for-project-e4909-default-rtdb.europe-west1.firebasedatabase.app/"
        })
        return db

    except Exception as e:
        st.error(f"Firebase connection failed: {e}")
        return None


def fetch_live_events(db, minutes=60):
    try:
        from firebase_admin import db as firebase_db
        events_ref = firebase_db.reference("events")
        raw = events_ref.get()

        if not raw:
            return []

        events = []
        cutoff = datetime.now() - timedelta(minutes=minutes)

        for key, event in raw.items():
            try:
                ts_str = event.get("timestamp", "")
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                if ts >= cutoff:
                    event["_key"] = key
                    event["_datetime"] = ts
                    events.append(event)
            except Exception:
                continue

        events.sort(key=lambda x: x["_datetime"], reverse=True)
        return events

    except Exception as e:
        st.warning(f"Could not fetch live events: {e}")
        return []


def get_active_users(events, idle_minutes=5):
    now = datetime.now()
    user_last_seen = {}

    for event in events:
        user = event.get("user_name", "unknown").lower()
        ts = event.get("_datetime", now)
        if user not in user_last_seen or ts > user_last_seen[user]:
            user_last_seen[user] = ts

    result = {}
    for user, last_seen in user_last_seen.items():
        seconds_ago = (now - last_seen).total_seconds()
        result[user] = {
            "last_seen":  last_seen,
            "seconds_ago": int(seconds_ago),
            "is_active":  seconds_ago <= (idle_minutes * 60)
        }
    return result

# ── HISTORICAL DATA ───────────────────────────────────────────────────────────

def load_summary_json():
    local_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "exports", "summary.json"
    )
    if os.path.exists(local_path):
        with open(local_path, "r") as f:
            return json.load(f)

    local_path2 = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "summary.json"
    )
    if os.path.exists(local_path2):
        with open(local_path2, "r") as f:
            return json.load(f)

    return None

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Hadoop_logo.svg/320px-Hadoop_logo.svg.png",
        width=150
    )
    st.markdown("### 📱 Mobile Analytics")
    st.markdown("---")

    # ── THEME TOGGLE ──────────────────────────────────────────────
    st.markdown("**Display Theme**")
    st.button(
        TOGGLE_LABEL,
        on_click=toggle_theme,
        use_container_width=True,
        key="theme_btn"
    )
    st.markdown("---")

    # Time filter
    st.markdown("**Time Filter**")
    time_filter = st.selectbox(
        "Show events from:",
        ["Last 5 minutes", "Last hour", "Last 24 hours"],
        index=1
    )

    time_map = {
        "Last 5 minutes": 5,
        "Last hour":       60,
        "Last 24 hours":   1440
    }
    selected_minutes = time_map[time_filter]

    # User filter
    st.markdown("**User Filter**")
    user_filter = st.selectbox(
        "Show data for:",
        ["All users", "kevin", "kintu", "travor", "olivia", "razal"]
    )

    st.markdown("---")

    # Auto refresh
    st.markdown("**Auto Refresh**")
    auto_refresh = st.toggle("Enable auto-refresh", value=True)
    refresh_interval = st.slider("Refresh every (seconds)", 5, 60, 10)

    st.markdown("---")
    st.markdown("**Hadoop Cluster**")
    st.markdown("🟢 HDFS: `hdfs://ssali:9000`")
    st.markdown("🟢 YARN: `:8088`")
    st.markdown("🟢 Pipeline: Automated")
    st.markdown("---")
    st.caption(f"Last loaded: {datetime.now().strftime('%H:%M:%S')}")

# ── MAIN HEADER ───────────────────────────────────────────────────────────────

st.markdown(
    '<div class="main-header">📱 Mobile Usage Analytics System</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-header">Real-time phone activity monitoring + '
    'Hadoop batch analytics | Big Data Analysis Project</div>',
    unsafe_allow_html=True
)

# ── FETCH DATA ────────────────────────────────────────────────────────────────

db           = init_firebase()
live_events  = fetch_live_events(db, minutes=selected_minutes) if db else []
summary_data = load_summary_json()

if user_filter != "All users":
    live_events = [
        e for e in live_events
        if e.get("user_name", "").lower() == user_filter.lower()
    ]

# ── TOP METRICS ───────────────────────────────────────────────────────────────

col1, col2, col3, col4, col5 = st.columns(5)

user_status  = get_active_users(live_events)
active_count = sum(1 for u in user_status.values() if u["is_active"])

total_screen_seconds = 0
total_apps           = 0
if summary_data:
    total_screen_seconds = sum(
        u.get("total_seconds", 0)
        for u in summary_data.get("screen_time", [])
    )
    total_apps = len(summary_data.get("top_apps", []))

with col1:
    st.metric("👥 Active Users", f"{active_count} / 5")
with col2:
    st.metric("📊 Live Events", len(live_events))
with col3:
    st.metric("⏱️ Total Screen Time",
              f"{round(total_screen_seconds/60, 1)} min")
with col4:
    st.metric("📱 Apps Tracked", total_apps)
with col5:
    st.metric("🕐 Last Updated", datetime.now().strftime("%H:%M:%S"))

st.markdown("---")

# ── LIVE SECTION ──────────────────────────────────────────────────────────────

st.markdown(
    '<div class="section-header">🔴 Live Activity</div>',
    unsafe_allow_html=True
)

live_col1, live_col2 = st.columns([1, 2])

with live_col1:
    st.markdown(f"<p style='color:{TEXT_PRIMARY}; font-weight:bold;'>👤 User Status</p>",
                unsafe_allow_html=True)

    all_users = ["kevin", "kintu", "travor", "olivia", "razal"]

    for user in all_users:
        if user_filter != "All users" and user != user_filter:
            continue

        if user in user_status:
            info = user_status[user]
            if info["is_active"]:
                seconds = info["seconds_ago"]
                st.markdown(
                    f'<div class="active-user">'
                    f'🟢 <b>{user.capitalize()}</b> — active {seconds}s ago'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                mins = info["seconds_ago"] // 60
                st.markdown(
                    f'<div class="idle-user">'
                    f'⚫ <b>{user.capitalize()}</b> — idle {mins}m ago'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                f'<div class="idle-user">'
                f'⚫ <b>{user.capitalize()}</b> — no data yet'
                f'</div>',
                unsafe_allow_html=True
            )

with live_col2:
    st.markdown(
        f"<p style='color:{TEXT_PRIMARY}; font-weight:bold;'>📋 Live Activity Feed</p>",
        unsafe_allow_html=True
    )

    if not live_events:
        st.info("No events found for selected time range. "
                "Make sure phones are running the logger app.")
    else:
        for event in live_events[:15]:
            ts       = event.get("_datetime", datetime.now())
            user     = event.get("user_name", "unknown").capitalize()
            pkg      = event.get("app_name", "unknown")
            app      = pkg.split(".")[-2] if "." in pkg else pkg
            etype    = event.get("event_type", "")
            duration = event.get("duration_seconds", 0)

            if etype == "OPEN":
                action = f"opened <b>{app}</b>"
            elif etype == "CLOSE":
                action = f"closed <b>{app}</b> after {duration}s"
            else:
                action = f"used <b>{app}</b>"

            st.markdown(
                f'<div class="live-event">'
                f'🕐 {ts.strftime("%H:%M:%S")} &nbsp;|&nbsp; '
                f'👤 {user} &nbsp;|&nbsp; {action}'
                f'</div>',
                unsafe_allow_html=True
            )

st.markdown("---")

# ── HISTORICAL SECTION ────────────────────────────────────────────────────────

st.markdown(
    '<div class="section-header">'
    '📊 Historical Analytics (Powered by Hadoop MapReduce)'
    '</div>',
    unsafe_allow_html=True
)

if not summary_data:
    st.warning(
        "No historical data found. Make sure the ingestion and export "
        "scripts have run at least once."
    )
else:
    generated_at = summary_data.get("generated_at", "Unknown")
    st.caption(
        f"Data generated at: {generated_at} | "
        f"Source: HDFS batch results via MapReduce"
    )

    hist_col1, hist_col2, hist_col3 = st.columns(3)

    # Chart 1 — Screen Time Per User
    with hist_col1:
        st.markdown(
            f"<p style='color:{TEXT_PRIMARY}; font-weight:bold;'>"
            f"⏱️ Screen Time Per User</p>",
            unsafe_allow_html=True
        )
        screen_data = summary_data.get("screen_time", [])

        if screen_data:
            df_screen           = pd.DataFrame(screen_data)
            df_screen["minutes"] = df_screen["total_seconds"] / 60

            fig1 = px.bar(
                df_screen,
                x="user_id",
                y="minutes",
                color="minutes",
                color_continuous_scale="Blues",
                labels={"user_id": "User", "minutes": "Minutes"},
                title="Total Screen Time (minutes)",
                template=PLOTLY_TEMPLATE
            )
            fig1.update_layout(
                showlegend=False,
                height=300,
                margin=dict(t=40, b=20, l=20, r=20),
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No screen time data yet.")

    # Chart 2 — Top Apps
    with hist_col2:
        st.markdown(
            f"<p style='color:{TEXT_PRIMARY}; font-weight:bold;'>"
            f"📱 Top Apps by Usage</p>",
            unsafe_allow_html=True
        )
        apps_data = summary_data.get("top_apps", [])

        if apps_data:
            df_apps           = pd.DataFrame(apps_data)
            df_apps["minutes"] = df_apps["total_seconds"] / 60

            fig2 = px.bar(
                df_apps,
                x="total_seconds",
                y="app_name",
                orientation="h",
                color="total_seconds",
                color_continuous_scale="Oranges",
                labels={"app_name": "App", "total_seconds": "Seconds"},
                title="Top Apps (seconds)",
                template=PLOTLY_TEMPLATE
            )
            fig2.update_layout(
                showlegend=False,
                height=300,
                margin=dict(t=40, b=20, l=20, r=20),
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No app usage data yet.")

    # Chart 3 — Hourly Patterns
    with hist_col3:
        st.markdown(
            f"<p style='color:{TEXT_PRIMARY}; font-weight:bold;'>"
            f"🕐 Usage by Hour of Day</p>",
            unsafe_allow_html=True
        )
        hourly_data = summary_data.get("hourly_patterns", [])

        if hourly_data:
            df_hourly            = pd.DataFrame(hourly_data)
            df_hourly["minutes"] = df_hourly["total_seconds"] / 60

            fig3 = px.line(
                df_hourly,
                x="label",
                y="minutes",
                markers=True,
                labels={"label": "Hour", "minutes": "Minutes"},
                title="Phone Usage Pattern by Hour",
                color_discrete_sequence=["#4DA6FF"],
                template=PLOTLY_TEMPLATE
            )
            fig3.update_layout(
                height=300,
                margin=dict(t=40, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No hourly pattern data yet.")

    # Summary Table
    st.markdown(
        f"<p style='color:{TEXT_PRIMARY}; font-weight:bold;'>"
        f"📋 Summary Table — All Users</p>",
        unsafe_allow_html=True
    )
    screen_data = summary_data.get("screen_time", [])

    if screen_data:
        df_summary = pd.DataFrame(screen_data)
        df_summary = df_summary.rename(columns={
            "user_id":       "User ID",
            "total_seconds": "Total Seconds",
            "total_minutes": "Total Minutes"
        })
        df_summary["Total Hours"] = (
            df_summary["Total Seconds"] / 3600
        ).round(3)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)

st.markdown("---")

# ── FOOTER ────────────────────────────────────────────────────────────────────

st.markdown(
    f"""
    <div style='text-align:center; color:{FOOTER_COLOR};
                font-size:0.85rem; padding:1rem'>
    Mobile Usage Analytics System &nbsp;|&nbsp;
    Big Data Analysis Project &nbsp;|&nbsp;
    Powered by Apache Hadoop + Firebase &nbsp;|&nbsp;
    Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)

# ── AUTO REFRESH ──────────────────────────────────────────────────────────────

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()