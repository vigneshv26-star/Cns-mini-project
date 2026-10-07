import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import os
from datetime import datetime

import database
import checker

# 1. Page Configuration
st.set_page_config(
    page_title="NetSage AI Troubleshooter",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize database
database.init_db()

# 2. Theme Toggle State
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# Define Palette colors
bg = "#09090b" if IS_DARK else "#ffffff"
bg_subtle = "#0c0c0f" if IS_DARK else "#f9fafb"
card = "#0c0c0f" if IS_DARK else "#ffffff"
card_hover = "#131316" if IS_DARK else "#f4f4f5"
border = "#1e1e24" if IS_DARK else "#e4e4e7"
border_subtle = "#16161a" if IS_DARK else "#f0f0f2"
text = "#fafafa" if IS_DARK else "#09090b"
text_muted = "#a1a1aa" if IS_DARK else "#71717a"
text_dim = "#52525b" if IS_DARK else "#a1a1aa"
accent = "#2563eb"
accent_hover = "#1d4ed8"
green = "#22c55e" if IS_DARK else "#16a34a"
green_muted = "rgba(34,197,94,0.12)" if IS_DARK else "rgba(22,163,74,0.08)"
red = "#ef4444" if IS_DARK else "#dc2626"
red_muted = "rgba(239,68,68,0.12)" if IS_DARK else "rgba(220,38,38,0.08)"
amber = "#f59e0b" if IS_DARK else "#d97706"
amber_muted = "rgba(245,158,11,0.12)" if IS_DARK else "rgba(217,119,6,0.08)"
shadow = "none" if IS_DARK else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"
radius = "10px"

# 3. Inject CSS Design System
css = f"""
<style>
:root {{
    --bg: {bg};
    --bg-subtle: {bg_subtle};
    --card: {card};
    --card-hover: {card_hover};
    --border: {border};
    --border-subtle: {border_subtle};
    --text: {text};
    --text-muted: {text_muted};
    --text-dim: {text_dim};
    --accent: {accent};
    --accent-muted: {accent_hover};
    --green: {green};
    --green-muted: {green_muted};
    --red: {red};
    --red-muted: {red_muted};
    --amber: {amber};
    --amber-muted: {amber_muted};
    --shadow: {shadow};
    --radius: {radius};
}}

/* Hide Streamlit chrome */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
div[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}}

.block-container {{
    padding: 1.5rem 2.5rem 3rem !important;
    max-width: 1360px !important;
}}

/* Brand Styling */
.brand {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.03em;
    margin-bottom: 0.5rem;
}}
.brand-accent {{
    color: var(--accent);
}}

/* Tabs Styling */
button[data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 1.25rem !important;
    border: 1px solid transparent !important;
    border-radius: 7px !important;
    transition: all 0.2s ease !important;
}}
button[data-baseweb="tab"]:hover {{
    color: var(--text) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--text) !important;
    background: var(--card) !important;
    border-color: var(--border) !important;
}}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
    display: none !important;
}}
[data-baseweb="tab-list"] {{
    gap: 4px !important;
    background: var(--bg-subtle) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    margin-bottom: 1.5rem !important;
}}

/* Column Gap */
[data-testid="stHorizontalBlock"] {{
    gap: 1.5rem !important;
}}

/* Metric Card */
.metric-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.3rem;
    box-shadow: var(--shadow);
    transition: all 0.2s ease;
}}
.metric-card:hover {{
    border-color: var(--text-dim);
}}
.metric-label {{
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
.metric-value {{
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.03em;
    margin-top: 0.2rem;
}}
.metric-delta {{
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 0.3rem;
    padding: 2px 8px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 3px;
}}
.delta-up {{ color: var(--green); background: var(--green-muted); }}
.delta-down {{ color: var(--red); background: var(--red-muted); }}
.delta-warn {{ color: var(--amber); background: var(--amber-muted); }}

/* Card Wrapping */
.card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
}}
.card-header {{
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 0.5rem;
    color: var(--text);
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}

/* Diagnostic Checks */
.check-item {{
    display: flex;
    align-items: center;
    padding: 0.65rem 0.8rem;
    border-radius: 6px;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    font-weight: 500;
    border: 1px solid var(--border-subtle);
}}
.check-passed {{
    color: var(--green);
    background: var(--green-muted);
    border-color: rgba(34, 197, 94, 0.2);
}}
.check-failed {{
    color: var(--red);
    background: var(--red-muted);
    border-color: rgba(239, 68, 68, 0.2);
}}

/* Plotly wrap */
.chart-wrap {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.25rem 0.75rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.5rem;
}}
.chart-title {{
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text);
}}
.chart-subtitle {{
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 0.8rem;
}}

/* Custom HTML Table */
.data-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.825rem;
}}
.data-table th {{
    text-align: left;
    padding: 0.75rem 0.9rem;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--border);
    background: var(--bg-subtle);
}}
.data-table td {{
    padding: 0.75rem 0.9rem;
    color: var(--text);
    border-bottom: 1px solid var(--border-subtle);
    vertical-align: top;
}}
.data-table tr:hover td {{
    background: var(--bg-subtle);
}}
.data-table tr:last-child td {{
    border-bottom: none;
}}

/* Badges */
.badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.725rem;
    font-weight: 600;
}}
.badge-Accepted {{ color: var(--green); background: var(--green-muted); border: 1px solid rgba(34,197,94,0.2); }}
.badge-Edited {{ color: var(--amber); background: var(--amber-muted); border: 1px solid rgba(245,158,11,0.2); }}
.badge-Rejected {{ color: var(--red); background: var(--red-muted); border: 1px solid rgba(239,68,68,0.2); }}
.badge-blue {{ color: var(--accent); background: rgba(37,99,235,0.1); border: 1px solid rgba(37,99,235,0.2); }}

/* Code display */
.cisco-code {{
    font-family: 'JetBrains Mono', monospace !important;
    background: var(--bg-subtle) !important;
    color: var(--text) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    border: 1px solid var(--border) !important;
    font-size: 0.8rem;
}}

.show-output-box {{
    background: #020617;
    color: #cbd5e1;
    font-family: 'JetBrains Mono', monospace;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid var(--border);
    font-size: 0.85rem;
    white-space: pre-wrap;
    overflow-x: auto;
    margin-bottom: 1rem;
    line-height: 1.4;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 4. Plotly Chart Theming Layout
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#a1a1aa" if IS_DARK else "#71717a", size=11),
    margin=dict(l=10, r=10, t=20, b=10),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.05)",
        zerolinecolor="rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.05)",
        tickfont=dict(size=10, color="#a1a1aa" if IS_DARK else "#71717a"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.05)",
        zerolinecolor="rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.05)",
        tickfont=dict(size=10, color="#a1a1aa" if IS_DARK else "#71717a"),
    ),
)

# 5. Header Component
head_left, head_right = st.columns([8, 1])
with head_left:
    st.markdown("""
    <div class="brand">
        ⚡ Net<span class="brand-name brand-accent">Sage</span> AI Troubleshooter
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True, key="theme_toggle_btn")

# 6. Tab Navigation
tab_troubleshoot, tab_dashboard = st.tabs(["Case Troubleshooting", "Responsible AI Dashboard"])

@st.cache_data
def load_cases():
    return pd.read_csv("cases.csv")

cases_df = load_cases()

# ----------------------------------------------------
# TAB 1: Case Troubleshooting
# ----------------------------------------------------
with tab_troubleshoot:
    st.markdown("<p style='font-size: 0.875rem; color:var(--text-muted); margin-bottom: 1.5rem;'>Diagnose complex Cisco network configuration anomalies and log human review actions.</p>", unsafe_allow_html=True)
    
    col_select, col_empty = st.columns([4, 5])
    with col_select:
        # Create case list for dropdown
        case_options = [f"{row['case_id']}: {row['title']}" for _, row in cases_df.iterrows()]
        selected_case_str = st.selectbox("Select Troubleshooting Case", case_options, key="case_selector")
        selected_case_id = selected_case_str.split(":")[0].strip()
        case_row = cases_df[cases_df["case_id"] == selected_case_id].iloc[0]
        
    c_left, c_right = st.columns([5, 4])
    
    with c_left:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">📋 Case Details: {case_row['case_id']}</div>
            <div style="font-size:0.875rem; margin-bottom:1rem;">
                <strong>Symptom:</strong> {case_row['symptom']}
            </div>
            <div style="font-size:0.8rem; font-weight:600; color:var(--text-muted); margin-bottom:0.4rem;">SHOW RUNNING-CONFIG OUTPUT</div>
            <div class="show-output-box">{case_row['show_output']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c_right:
        # Run Deterministic Rule Checker
        check_results = checker.run_rule_checker(case_row["show_output"], case_row["expected_gateway"])
        
        st.markdown(f"""
        <div class="card">
            <div class="card-header">⚙️ Deterministic Rule Checks</div>
            <div style="margin-bottom:0.5rem;">
                <div class="check-item check-{"passed" if check_results["interface"]["status"] == "PASS" else "failed"}">
                    {check_results["interface"]["badge"]}
                </div>
                <div class="check-item check-{"passed" if check_results["mask"]["status"] == "PASS" else "failed"}">
                    {check_results["mask"]["badge"]}
                </div>
                <div class="check-item check-{"passed" if check_results["gateway"]["status"] == "PASS" else "failed"}">
                    {check_results["gateway"]["badge"]}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # AI Integration
        st.markdown("<div class='card'><div class='card-header'>🧠 NetSage AI Diagnosis</div>", unsafe_allow_html=True)
        
        # State to store AI output
        ai_state_key = f"ai_res_{selected_case_id}"
        run_ai_clicked = st.button("Run NetSage AI Diagnosis", use_container_width=True, key=f"run_ai_btn_{selected_case_id}")
        
        if run_ai_clicked:
            with st.spinner("Invoking NetSage AI model..."):
                # Call AI with fallback
                fallback_str = case_row["ai_fallback"]
                ai_output, source = checker.run_deterministic_checks(case_row["show_output"]), None # dummy placeholders
                
                # Fetch AI diagnosis
                api_key = os.environ.get("ANTHROPIC_API_KEY", "dummy-key")
                base_url = os.environ.get("ANTHROPIC_BASE_URL", "http://127.0.0.1:4000")
                
                try:
                    import anthropic
                    # Read prompt
                    with open("diagnose_prompt.md", "r", encoding="utf-8") as f:
                        prompt_tmpl = f.read()
                    prompt = prompt_tmpl.replace("{symptom}", case_row["symptom"]).replace("{show_output}", case_row["show_output"])
                    
                    client = anthropic.Anthropic(api_key=api_key, base_url=base_url, timeout=3.0)
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1000,
                        temperature=0.0,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    content = response.content[0].text.strip()
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    parsed = json.loads(content)
                    st.session_state[ai_state_key] = {"data": parsed, "source": "NetSage AI Live API"}
                except Exception as e:
                    # Fallback to pre-seeded response
                    try:
                        parsed = json.loads(fallback_str)
                        st.session_state[ai_state_key] = {"data": parsed, "source": "Simulation Fallback (Offline Proxy)"}
                    except Exception as ex:
                        st.session_state[ai_state_key] = None
                        st.error(f"Error parsing fallback: {ex}")
                        
        if st.session_state.get(ai_state_key):
            ai_data = st.session_state[ai_state_key]["data"]
            ai_source = st.session_state[ai_state_key]["source"]
            
            # Display source tag
            st.markdown(f"<p style='font-size:0.75rem; color:var(--text-muted); margin-bottom:0.5rem;'>Source: <strong>{ai_source}</strong></p>", unsafe_allow_html=True)
            
            # Custom card displaying parsed AI JSON response
            st.markdown(f"""
            <div style="background:var(--bg-subtle); border: 1px solid var(--border); border-radius:6px; padding:1rem; margin-bottom:1rem;">
                <table style="width:100%; border-spacing:0.4rem; border-collapse:separate; font-size:0.85rem;">
                    <tr>
                        <td style="font-weight:600; width:100px; color:var(--text-muted); vertical-align:top;">Root Cause:</td>
                        <td>{ai_data.get("root_cause", "")}</td>
                    </tr>
                    <tr>
                        <td style="font-weight:600; color:var(--text-muted);">OSI Layer:</td>
                        <td><span class="badge badge-blue">{ai_data.get("osi_layer", "")}</span></td>
                    </tr>
                    <tr>
                        <td style="font-weight:600; color:var(--text-muted);">Confidence:</td>
                        <td><span class="badge badge-{"green" if ai_data.get("confidence", "").lower() == "high" else ("amber" if ai_data.get("confidence", "").lower() == "medium" else "red")}">{ai_data.get("confidence", "").upper()}</span></td>
                    </tr>
                    <tr>
                        <td style="font-weight:600; color:var(--text-muted); vertical-align:top;">Evidence:</td>
                        <td><code class="cisco-code">{ai_data.get("evidence", "")}</code></td>
                    </tr>
                    <tr>
                        <td style="font-weight:600; color:var(--text-muted); vertical-align:top;">Next Command:</td>
                        <td><code class="cisco-code" style="color:#2563eb;">{ai_data.get("next_command", "")}</code></td>
                    </tr>
                    <tr>
                        <td style="font-weight:600; color:var(--text-muted); vertical-align:top;">Fix Steps:</td>
                        <td>
                            <ol style="margin:0; padding-left:1.1rem; font-size:0.825rem;">
                                {"".join(f"<li>{step}</li>" for step in ai_data.get("fix_steps", []))}
                            </ol>
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # Formatted JSON Raw output toggle
            with st.expander("Show Raw JSON Output"):
                st.json(ai_data)
                
            st.markdown("</div>", unsafe_allow_html=True) # End of NetSage AI Diagnosis Card
            
            # Human Oversight Form
            st.markdown("<div class='card'><div class='card-header'>✍️ Human Reviewer Oversight</div>", unsafe_allow_html=True)
            with st.form(key=f"review_form_{selected_case_id}"):
                status_choice = st.selectbox("Status Decision", ["Accepted", "Edited", "Rejected"], key=f"status_{selected_case_id}")
                
                reviewer_notes = st.text_area(
                    "Reviewer Corrected Notes & Verification", 
                    value="", 
                    placeholder="Enter review notes and manual corrections here...", 
                    height=80, 
                    key=f"notes_{selected_case_id}"
                )
                
                submit_review = st.form_submit_button("Submit Review Logs")
                if submit_review:
                    database.save_review(
                        case_id=case_row["case_id"],
                        case_title=case_row["title"],
                        status=status_choice,
                        ai_response_str=json.dumps(ai_data),
                        corrected_notes=reviewer_notes
                    )
                    st.success(f"Successfully recorded review for {case_row['case_id']}!")
                    # Clear session state for AI so user can rerun if wanted
                    st.toast("Dashboard logs updated!")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Click 'Run NetSage AI Diagnosis' to view AI structured diagnosis.")
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# TAB 2: Responsible AI Dashboard
# ----------------------------------------------------
with tab_dashboard:
    st.markdown("<p style='font-size: 0.875rem; color:var(--text-muted); margin-bottom: 1.5rem;'>Real-time AI performance monitoring, human feedback analytics, and compliance review logs.</p>", unsafe_allow_html=True)
    
    # Retrieve metrics
    metrics = database.get_metrics()
    
    # Render KPI Cards in a row
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Human Reviews</div>
            <div class="metric-value">{metrics['total']}</div>
            <div class="metric-delta delta-up">📊 Active Monitoring</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        # Agreement rate badge color
        rate_cls = "delta-up" if metrics['agreement_rate'] >= 70.0 else ("delta-warn" if metrics['agreement_rate'] >= 50.0 else "delta-down")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">AI Agreement Rate</div>
            <div class="metric-value">{metrics['agreement_rate']:.1f}%</div>
            <div class="metric-delta {rate_cls}">🎯 Target > 80%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Accepted Reviews</div>
            <div class="metric-value">{metrics['accepted']}</div>
            <div class="metric-delta delta-up">✅ Match</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Edited / Rejected</div>
            <div class="metric-value">{metrics['edited'] + metrics['rejected']}</div>
            <div class="metric-delta delta-warn">⚠️ Intervention Needed</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Visualizations
    reviews_all = database.get_all_reviews()
    if reviews_all:
        df_revs = pd.DataFrame(reviews_all)
        
        chart_col1, chart_col2 = st.columns([4, 5])
        
        with chart_col1:
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">Oversight Status Distribution</div>
                <div class="chart-subtitle">Proportion of Accepted vs Corrected AI results</div>
            """, unsafe_allow_html=True)
            
            # Pie / Donut Chart
            status_counts = df_revs['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig_pie = px.pie(
                status_counts,
                values='Count',
                names='Status',
                hole=0.45,
                color='Status',
                color_discrete_map={
                    'Accepted': '#16a34a' if not IS_DARK else '#22c55e',
                    'Edited': '#d97706' if not IS_DARK else '#f59e0b',
                    'Rejected': '#dc2626' if not IS_DARK else '#ef4444'
                },
                height=260
            )
            fig_pie.update_layout(**PLOT_LAYOUT)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            
        with chart_col2:
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">Review Volume & Status Timeline</div>
                <div class="chart-subtitle">Distribution of human feedback submissions over time</div>
            """, unsafe_allow_html=True)
            
            # Chronological stack bar
            df_revs['dt'] = pd.to_datetime(df_revs['timestamp'])
            df_revs_sorted = df_revs.sort_values('dt')
            df_revs_sorted['time_label'] = df_revs_sorted['dt'].dt.strftime('%b %d, %H:%M')
            
            timeline_df = df_revs_sorted.groupby(['time_label', 'status']).size().reset_index(name='count')
            
            fig_bar = px.bar(
                timeline_df,
                x='time_label',
                y='count',
                color='status',
                color_discrete_map={
                    'Accepted': '#16a34a' if not IS_DARK else '#22c55e',
                    'Edited': '#d97706' if not IS_DARK else '#f59e0b',
                    'Rejected': '#dc2626' if not IS_DARK else '#ef4444'
                },
                barmode='stack',
                height=260
            )
            fig_bar.update_layout(**PLOT_LAYOUT)
            fig_bar.update_layout(xaxis_title=None, yaxis_title="Review Count")
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Responsible AI Log Table
        st.markdown("<div class='card'><div class='card-header'>📜 Responsible AI Audit Log</div>", unsafe_allow_html=True)
        
        table_rows = ""
        for _, r in df_revs.iterrows():
            ai_data_parsed = json.loads(r["ai_response"])
            cause = ai_data_parsed.get("root_cause", "N/A")
            
            table_rows += f"<tr><td><strong>{r['case_id']}</strong><br><span style='font-size:0.75rem; color:var(--text-muted);'>{r['case_title']}</span></td><td><span class='badge badge-{r['status']}'>{r['status']}</span></td><td><span style='font-size:0.8rem; font-family:monospace;'>{cause}</span></td><td>{r['corrected_notes']}</td><td style='color:var(--text-muted); font-size:0.75rem;'>{r['timestamp']}</td></tr>"
            
        st.markdown(f"""<table class="data-table">
<thead>
<tr>
<th style="width: 15%;">Case</th>
<th style="width: 12%;">Oversight Status</th>
<th style="width: 30%;">AI Suggested Cause</th>
<th style="width: 28%;">Human Reviewer Notes</th>
<th style="width: 15%;">Timestamp</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>""", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Reset DB option at the bottom
        reset_col, _ = st.columns([2, 7])
        with reset_col:
            if st.button("Reset Review logs", key="reset_db_btn"):
                database.clear_db()
                st.rerun()
    else:
        st.info("No human review logs available yet. Submit a review in the Case Troubleshooting tab.")
