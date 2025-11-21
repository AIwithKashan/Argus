# dashboard.py
# FINAL V4: UI shows exact terminated process details.

import streamlit as st
import sqlite3
import pandas as pd
import time
import altair as alt

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="ARGUS // MISSION CONTROL", page_icon="👁️‍🗨️", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono:wght@400;700&display=swap');
    .stApp { background-color: #05050f; background-image: radial-gradient(circle at 50% 50%, #111122 0%, #05050f 100%); }
    ::-webkit-scrollbar { width: 10px; background: #05050f; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 5px; }
    h1, h2, h3, .big-font { font-family: 'Orbitron', sans-serif !important; letter-spacing: 2px; }
    p, .stMetricLabel, .stText, .stTextArea { font-family: 'Roboto Mono', monospace !important; }
    .metric-card { background: rgba(20, 20, 35, 0.8); border: 1px solid #333; border-radius: 12px; padding: 20px; text-align: center; transition: all 0.3s ease-in-out; box-shadow: 0 4px 15px rgba(0,0,0,0.5); backdrop-filter: blur(5px); }
    .metric-title { color: #888; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-family: 'Orbitron', sans-serif; font-size: 2.5rem; font-weight: 700; margin: 10px 0; }
    .metric-unit { font-size: 1rem; color: #aaa; }
    .glow-green { border-bottom: 4px solid #0f0; box-shadow: 0 0 15px rgba(0, 255, 0, 0.2); color: #0f0; }
    .glow-orange { border-bottom: 4px solid #fa0; box-shadow: 0 0 15px rgba(255, 170, 0, 0.2); color: #fa0; }
    .glow-red { border-bottom: 4px solid #f00; box-shadow: 0 0 25px rgba(255, 0, 0, 0.4); color: #f00; animation: pulse-red 1.5s infinite; }
    @keyframes pulse-red { 0% { box-shadow: 0 0 15px rgba(255, 0, 0, 0.4); } 50% { box-shadow: 0 0 30px rgba(255, 0, 0, 0.7); } 100% { box-shadow: 0 0 15px rgba(255, 0, 0, 0.4); } }
    .ai-brain { display: inline-block; font-size: 2rem; animation: brain-pulse 2s infinite alternate; }
    @keyframes brain-pulse { from { text-shadow: 0 0 10px #d0f, 0 0 20px #d0f; } to { text-shadow: 0 0 20px #0ff, 0 0 40px #0ff; } }
    .stTextArea textarea { background-color: #0a0a12 !important; color: #00ff41 !important; border: 1px solid #333; font-family: 'Roboto Mono', monospace !important; font-size: 0.9rem; }
    footer {visibility: hidden;} #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def make_card(title, value, unit, status_val, threshold_warn, threshold_crit):
    theme = "glow-green"
    if status_val > threshold_crit: theme = "glow-red"
    elif status_val > threshold_warn: theme = "glow-orange"
    html = f"""<div class="metric-card {theme}"><div class="metric-title">{title}</div><div class="metric-value">{value}</div><div class="metric-unit">{unit}</div></div>"""
    st.markdown(html, unsafe_allow_html=True)

# --- DATA LOADING (UPDATED to fetch 'details') ---
def load_data():
    try:
        conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
        df_metrics = pd.read_sql("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 60", conn)
        df_alerts = pd.read_sql("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10", conn)
        # Fetch 'details' column here
        df_cmds = pd.read_sql("SELECT * FROM commands WHERE executed=1 ORDER BY id DESC LIMIT 5", conn)
        conn.close()
        if not df_alerts.empty: df_alerts['timestamp'] = pd.to_datetime(df_alerts['timestamp'])
        if not df_metrics.empty: df_metrics['timestamp'] = pd.to_datetime(df_metrics['timestamp'])
        return df_metrics, df_alerts, df_cmds
    except: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def create_cyber_chart(data, y_col, title, threshold=None, current_val=0):
    if data.empty: return st.info("Initializing Data Stream...")
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    chart_color = '#00FFAA'
    if threshold and current_val > threshold: chart_color = '#FF0055'
    base = alt.Chart(data).encode(x=alt.X('timestamp:T', axis=alt.Axis(labels=False, grid=False, title=None)), y=alt.Y(f'{y_col}:Q', axis=alt.Axis(gridColor='#333', title=None), scale=alt.Scale(domain=[0, 100])), tooltip=['timestamp', y_col])
    area = base.mark_area(line={'color': chart_color, 'strokeWidth': 3}, color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(offset=0, color=chart_color), alt.GradientStop(offset=1, color='transparent')], x1=1, x2=1, y1=1, y2=0), opacity=0.6)
    final_chart = area
    if threshold: rule = alt.Chart(pd.DataFrame({'y': [threshold]})).mark_rule(color='#ff0000', strokeDash=[5, 5], strokeWidth=2).encode(y='y'); final_chart = area + rule
    st.altair_chart(final_chart, width="stretch", theme=None)

# --- MAIN APP LOOP ---
time.sleep(0.5)
df, df_alerts, df_cmds = load_data()
if df.empty: st.warning("📡 WAITING FOR TELEMETRY STREAM..."); time.sleep(2); st.rerun()
latest = df.iloc[0]
cpu_crit = latest['cpu'] > 90; ram_crit = latest['ram'] > 95; temp_crit = latest['temp'] > 85
cpu_warn = latest['cpu'] > 70; ram_warn = latest['ram'] > 85; temp_warn = latest['temp'] > 75
header_status = "🟢 SYSTEM STABLE"; header_color = "#0f0"; threat_reason = ""
if cpu_crit or ram_crit or temp_crit: header_status = "🔴 CRITICAL THREAT DETECTED"; header_color = "#f00"; threat_reason = "[HIGH LOAD/TEMP]"
elif cpu_warn or ram_warn or temp_warn: header_status = "🟠 ANOMALY DETECTED"; header_color = "#fa0"
st.markdown(f"""<div style='text-align: center; border-bottom: 2px solid {header_color}; padding-bottom: 10px; margin-bottom: 20px;'><h1 style='color: {header_color}; margin:0; text-shadow: 0 0 15px {header_color};'>👁‍🗨 ARGUS // MISSION CONTROL</h1><h3 style='color: #aaa; margin:0;'>STATUS: {header_status} <span style='color:{header_color}'>{threat_reason}</span></h3></div>""", unsafe_allow_html=True)

col_main, col_logs = st.columns([2, 1])
with col_main:
    st.markdown("### 📊 LIVE TELEMETRY")
    c1, c2, c3, c4 = st.columns(4)
    with c1: make_card("CPU LOAD", f"{latest['cpu']:.1f}", "%", latest['cpu'], 70, 90)
    with c2: make_card("RAM USAGE", f"{latest['ram']:.1f}", "%", latest['ram'], 85, 95)
    with c3: make_card("TEMP (EST)", f"{latest['temp']:.1f}", "°C", latest['temp'], 75, 85)
    with c4: make_card("NET I/O", f"{latest['network']:.1f}", "MB/s", 0, 9999, 9999)
    st.divider(); st.markdown("### 📉 CRITICAL METRICS VIEW")
    cc1, cc2 = st.columns(2)
    with cc1: st.markdown("**🔥 CPU Load (Danger Line: 90%)**"); create_cyber_chart(df, 'cpu', 'CPU', threshold=90, current_val=latest['cpu'])
    with cc2: st.markdown("**💾 RAM Usage (Danger Line: 95%)**"); create_cyber_chart(df, 'ram', 'RAM', threshold=95, current_val=latest['ram'])
    cc3, cc4 = st.columns(2)
    with cc3: st.markdown("**🌡️ Temperature (Danger Line: 85°C)**"); create_cyber_chart(df, 'temp', 'TEMP', threshold=85, current_val=latest['temp'])
    with cc4: st.markdown("**🌐 Network Activity**"); create_cyber_chart(df, 'network', 'NET', current_val=latest['network'])

with col_logs:
    st.markdown("""<h3><span class="ai-brain">🧠</span> GEMINI NEURAL NET</h3>""", unsafe_allow_html=True)
    
    # --- UPDATED INTERVENTIONS SECTION ---
    with st.expander("🛠️ AUTONOMOUS INTERVENTIONS", expanded=True):
        if not df_cmds.empty:
            for i, row in df_cmds.iterrows():
                # Display the details from the database
                details_text = row.get('details', 'Execution complete.')
                st.markdown(f"""
                <div style='border-left: 4px solid #f00; background: #221111; padding: 10px; margin-bottom: 5px; border-radius: 5px;'>
                    <strong style='color:#f00'>⚡ ACTION REPORT (ID: {row['id']})</strong><br>
                    <span style='font-size: 0.9em; color:#fff; font-family: Roboto Mono;'>{details_text}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#666; padding:10px;'>No recent interventions.</div>", unsafe_allow_html=True)

    with st.expander("📟 LIVE REASONING LOGS", expanded=True):
        if not df_alerts.empty:
            for i, row in df_alerts.iterrows():
                ts = row['timestamp'].strftime('%H:%M:%S'); clean_analysis = row['analysis'].replace("STATUS:", ">> STATUS:").replace("ACTION:", ">> ACTION:")
                st.text_area(f"[{ts}] EVENT ID: {row['id']}", clean_analysis, height=120, key=f"log_{row['id']}")
        else: st.markdown("<div style='color:#666; padding:10px;'>Awaiting anomaly data...</div>", unsafe_allow_html=True)
st.rerun()
