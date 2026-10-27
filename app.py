import csv
import io

from charts import (
    bill_amount_chart,
    unit_chart,
    consumption_pie
)
import streamlit as st
from report import generate_report
from ocr import extract_text, POPPLER_PATH, TESSERACT_PATH
from parser import parse_bill
from llm import analyze_bill
from database import create_database, save_bill, update_bill_analysis, get_all_bills, save_sample, export_samples_csv
from charts import bill_amount_chart, unit_chart
from score import energy_score
from analytics import summarize_bill_history

# ======================================================
# Database
# ======================================================
create_database()

# ======================================================
# Page Configuration
# ======================================================
st.set_page_config(
    page_title="⚡ VOLTWise AI",
    page_icon="⚡",
    layout="wide"
)

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

theme = st.sidebar.radio(
    "Theme",
    ["Dark", "Light"],
    index=0 if st.session_state.theme == "Dark" else 1,
    key="theme",
    label_visibility="collapsed"
)

if theme == "Light":
    primary = "#7C3AED"
    secondary = "#F59E0B"
    tertiary = "#0EA5E9"
    bg = "#F8FAFC"
    card = "#FFFFFF"
    card_border = "rgba(148,163,184,0.25)"
    surface = "rgba(255,255,255,0.92)"
    surface_soft = "rgba(255,255,255,0.78)"
    surface_strong = "rgba(248,250,252,0.96)"
    input_bg = "rgba(255,255,255,0.98)"
    sidebar_bg = "linear-gradient(180deg, #EEF2FF 0%, #E2E8F0 100%)"
    text_main = "#0F172A"
    text_muted = "#475569"
    body_bg = "radial-gradient(circle at top left, #E0E7FF 0%, #F8FAFC 45%, #EFF6FF 100%)"
    hero_bg = "linear-gradient(120deg, rgba(124,58,237,0.14), rgba(245,158,11,0.10))"
    card_transparent = "rgba(255,255,255,0.78)"
else:
    primary = "#8B5CF6"
    secondary = "#FBBF24"
    tertiary = "#22D3EE"
    bg = "#0A0A0F"
    card = "#14141F"
    card_border = "rgba(255, 255, 255, 0.09)"
    surface = "rgba(20, 20, 31, 0.9)"
    surface_soft = "rgba(30, 41, 59, 0.65)"
    surface_strong = "rgba(15, 23, 42, 0.85)"
    input_bg = "rgba(15,23,42,0.6)"
    sidebar_bg = "linear-gradient(180deg, #17102B 0%, #08080C 100%)"
    text_main = "#F8FAFC"
    text_muted = "#B4B9C9"
    body_bg = "radial-gradient(circle at top left, #1B1230 0%, #0A0A0F 45%, #050507 100%)"
    hero_bg = "linear-gradient(120deg, rgba(139,92,246,0.18), rgba(251,191,36,0.14))"
    card_transparent = "rgba(30, 41, 59, 0.65)"

# ======================================================
# Global Theme / Custom CSS
# ======================================================
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

:root {
    --primary: __PRIMARY__;
    --secondary: __SECONDARY__;
    --tertiary: __TERTIARY__;
    --bg: __BG__;
    --card: __CARD__;
    --card-border: __CARD_BORDER__;
    --surface: __SURFACE__;
    --surface-soft: __SURFACE_SOFT__;
    --surface-strong: __SURFACE_STRONG__;
    --input-bg: __INPUT_BG__;
    --sidebar-bg: __SIDEBAR_BG__;
    --text-main: __TEXT_MAIN__;
    --text-muted: __TEXT_MUTED__;
}

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    color: var(--text-main);
}

.stApp {
    background: __BODY_BG__;
}

/* Force high-contrast text everywhere Streamlit renders its own defaults */
p, span, label, li, div, h1, h2, h3, h4, h5, h6 {
    color: var(--text-main);
}
.stMarkdown, .stText, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    color: var(--text-main) !important;
}

#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

/* ---------------- Sidebar ---------------- */
section[data-testid="stSidebar"] {
    background: var(--sidebar-bg);
    border-right: 1px solid var(--card-border);
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}
.sidebar-logo {
    text-align: center;
    padding: 14px 0 8px 0;
}
.sidebar-logo h1 {
    font-family: 'Sora', 'Poppins', sans-serif !important;
    font-size: 52px;
    font-weight: 800;
    letter-spacing: .5px;
    line-height: 1.1;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--tertiary));
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
    filter: drop-shadow(0 0 22px rgba(139,92,246,0.6)) drop-shadow(0 0 36px rgba(251,191,36,0.3));
    animation: shine 4s linear infinite;
}
@keyframes shine {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}
.sidebar-logo p {
    color: var(--text-muted);
    font-size: 13px;
    font-weight: 500;
    margin-top: 2px;
    letter-spacing: .4px;
}
section[data-testid="stSidebar"] hr {
    border-color: var(--card-border);
    margin: 14px 0;
}

/* Radio nav styled like a menu */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: transparent;
    border-radius: 12px;
    padding: 10px 14px !important;
    margin-bottom: 4px;
    transition: all .2s ease;
    width: 100%;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(139, 92, 246, 0.12);
    transform: translateX(3px);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label span {
    font-size: 15px !important;
    font-weight: 500;
}

.sidebar-footer {
    position: fixed;
    bottom: 18px;
    width: 260px;
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
    border-top: 1px solid var(--card-border);
    padding-top: 10px;
}
.sidebar-footer b {
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ---------------- Hero ---------------- */
.hero {
    position: relative;
    padding: 42px 40px;
    border-radius: 22px;
    margin-bottom: 28px;
    overflow: hidden;
    background: __HERO_BG__;
    border: 1px solid var(--card-border);
    animation: fadeIn .8s ease;
}
.hero-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 14px;
}
.pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    color: var(--text-main);
    font-size: 13px;
    font-weight: 600;
}
.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
}
.info-card {
    background: var(--surface);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 16px;
}
.info-card .title {
    font-weight: 700;
    margin-bottom: 6px;
}
.info-card .meta {
    color: var(--text-muted);
    font-size: 13px;
    line-height: 1.5;
}
.step-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-top: 10px;
}
.step-card {
    background: var(--surface-soft);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 14px;
}
.step-card .step-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    color: #0A0A0F;
    font-weight: 800;
    margin-bottom: 8px;
}
.step-card .step-title {
    font-weight: 700;
    margin-bottom: 4px;
}
.step-card .step-text {
    color: var(--text-muted);
    font-size: 13px;
    line-height: 1.5;
}
.empty-state {
    text-align: center;
    padding: 24px;
    border: 1px dashed rgba(139,92,246,0.16);
    border-radius: 18px;
    background: var(--surface);
    margin: 18px 0;
}
.empty-icon {
    font-size: 34px;
    margin-bottom: 8px;
}
.empty-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 6px;
}
.empty-body {
    color: var(--text-muted);
    font-size: 14px;
    line-height: 1.6;
}
.inline-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(139,92,246,0.16);
    border: 1px solid rgba(139,92,246,0.28);
    color: #D8B4FE;
    font-size: 12px;
    margin-top: 8px;
}
.hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(139,92,246,0.35), transparent 70%);
    filter: blur(10px);
}
.hero::after {
    content: "";
    position: absolute;
    bottom: -80px; left: -40px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(251,191,36,0.3), transparent 70%);
    filter: blur(10px);
}
.hero h1 {
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 6px;
    position: relative;
}
.hero p {
    color: var(--text-muted);
    font-size: 15.5px;
    max-width: 640px;
    position: relative;
}

/* ---------------- Generic Cards ---------------- */
.glass-card {
    background: __CARD_TRANSPARENT__;
    backdrop-filter: blur(10px);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    padding: 22px 22px;
    margin-bottom: 18px;
    animation: fadeIn .6s ease;
}
.section-title {
    font-size: 19px;
    font-weight: 700;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title .bar {
    width: 5px;
    height: 20px;
    border-radius: 4px;
    background: linear-gradient(180deg, var(--primary), var(--secondary));
    display: inline-block;
}

/* ---------------- Metric Cards ---------------- */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 8px;
}
.metric-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    padding: 18px 18px 16px 18px;
    position: relative;
    overflow: hidden;
    transition: transform .25s ease, box-shadow .25s ease;
    animation: fadeIn .6s ease;
}
.metric-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.18);
    border-color: rgba(139,92,246,0.4);
}
.metric-card .icon {
    font-size: 22px;
    margin-bottom: 6px;
}
.metric-card .label {
    color: var(--text-muted);
    font-size: 12.5px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: .4px;
}
.metric-card .value {
    font-size: 24px;
    font-weight: 700;
    margin-top: 2px;
}
.metric-card .indicator {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
}
.ind-green { background: linear-gradient(90deg, #22C55E, #16A34A); }
.ind-cyan { background: linear-gradient(90deg, #06B6D4, #0891B2); }
.ind-amber { background: linear-gradient(90deg, #F59E0B, #D97706); }
.ind-red { background: linear-gradient(90deg, #EF4444, #DC2626); }
.ind-blue { background: linear-gradient(90deg, #3B82F6, #2563EB); }
.ind-purple { background: linear-gradient(90deg, #A855F7, #7E22CE); }

/* ---------------- Buttons ---------------- */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
    color: #0A0A0F !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 22px !important;
    transition: all .25s ease !important;
    box-shadow: 0 4px 18px rgba(139,92,246,0.25);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 8px 24px rgba(139,92,246,0.4);
}
.hero-cta {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    color: #0A0A0F;
    font-weight: 700;
    background: linear-gradient(90deg, var(--secondary), var(--primary));
    border-radius: 999px;
    padding: 12px 24px;
    text-decoration: none;
    margin-top: 18px;
    box-shadow: 0 18px 60px rgba(139,92,246,0.18);
}
.hero-cta:hover {
    transform: translateY(-1px);
}
.upload-hint {
    display: grid;
    gap: 6px;
    background: var(--surface-soft);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 16px 18px;
    margin-top: 18px;
}
.upload-hint strong {
    color: var(--text-main);
}
.upload-hint li {
    color: var(--text-muted);
    margin-left: 18px;
    line-height: 1.5;
}
.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    color: var(--text-main);
    font-size: 13px;
    font-weight: 600;
    margin-right: 10px;
}
.status-chip span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    background: var(--secondary);
}

/* ---------------- Uploader ---------------- */
[data-testid="stFileUploaderDropzone"] {
    background: linear-gradient(135deg, rgba(139,92,246,0.16), rgba(251,191,36,0.10)) !important;
    border: 2px dashed rgba(139,92,246,0.65) !important;
    border-radius: 18px !important;
    transition: all .25s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: rgba(251,191,36,0.75) !important;
    background: linear-gradient(135deg, rgba(139,92,246,0.22), rgba(251,191,36,0.14)) !important;
}
[data-testid="stFileUploaderDropzone"] * {
    color: var(--text-main) !important;
}
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span {
    color: var(--text-muted) !important;
}
[data-testid="stFileUploaderDropzone"] svg {
    fill: var(--secondary) !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
    color: #0A0A0F !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] button p {
    color: #0A0A0F !important;
}

/* ---------------- Expander ---------------- */
details {
    background: var(--card) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 14px !important;
    margin-bottom: 12px !important;
}
summary {
    font-weight: 600 !important;
    font-size: 15px !important;
}

/* Newer Streamlit builds render expanders as [data-testid="stExpander"]
   instead of a plain <details>/<summary> pair, so the rules above miss
   them and the header falls back to the browser's white default. */
[data-testid="stExpander"] {
    background: var(--card) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 14px !important;
    overflow: hidden;
    margin-bottom: 12px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] > details > summary,
[data-testid="stExpander"] div[role="button"] {
    background: var(--card) !important;
    color: var(--text-main) !important;
}
[data-testid="stExpander"] summary:hover {
    background: rgba(139, 92, 246, 0.10) !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {
    color: var(--text-main) !important;
    fill: var(--text-main) !important;
}
[data-testid="stExpanderDetails"] {
    background: var(--card) !important;
    color: var(--text-main) !important;
}

/* ---------------- st.write(dict) / st.json ---------------- */
[data-testid="stJson"] {
    background: var(--card) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
}
[data-testid="stJson"],
[data-testid="stJson"] * {
    color: var(--text-main) !important;
    background-color: transparent !important;
}
[data-testid="stJson"] > div {
    background: var(--card) !important;
}
/* react-json-view-lite assigns its own inline colors per token type;
   this keeps punctuation/keys/strings readable on the dark card. */
[data-testid="stJson"] span {
    color: #E9D5FF !important;
}

/* ---------------- Uploaded file chip ---------------- */
[data-testid="stFileUploaderFile"] {
    background: var(--card) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
    padding: 8px 10px !important;
}
/* The icon swatch, name/size wrapper, and every other nested <div>/<span>
   inside the chip carry their own light background by default — knock
   all of them transparent so only the dark chip background shows. */
[data-testid="stFileUploaderFile"] div,
[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] small {
    background: transparent !important;
    background-color: transparent !important;
}
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] * {
    color: var(--text-main) !important;
}
[data-testid="stFileUploaderFileName"] {
    color: var(--text-main) !important;
    font-weight: 500;
}
[data-testid="stFileUploaderFileErrorMessage"] {
    color: #F87171 !important;
}
/* File-type icon glyph (the little document icon) — force it to an
   accent color so it reads clearly against the dark chip. */
[data-testid="stFileUploaderFile"] svg {
    fill: var(--secondary) !important;
    color: var(--secondary) !important;
}
[data-testid="stFileUploaderDeleteBtn"] svg {
    fill: var(--text-muted) !important;
    color: var(--text-muted) !important;
}
[data-testid="stFileUploaderDeleteBtn"]:hover svg {
    fill: #F87171 !important;
    color: #F87171 !important;
}

/* ---------------- Tabs ---------------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(30,41,59,0.5);
    padding: 6px;
    border-radius: 14px;
    border: 1px solid var(--card-border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: var(--text-muted);
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, rgba(139,92,246,0.25), rgba(251,191,36,0.2)) !important;
    color: var(--text-main) !important;
}

/* ---------------- Text inputs / number inputs ---------------- */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: var(--input-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 10px !important;
    color: var(--text-main) !important;
}

/* ---------------- Chat / AI box ---------------- */
.ai-box {
    background: var(--surface-soft);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    padding: 20px 22px;
    animation: fadeIn .6s ease;
}
.ai-box .ai-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 16px;
    margin-bottom: 10px;
    color: var(--primary);
}

/* ---------------- Badges ---------------- */
.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(139,92,246,0.14);
    border: 1px solid rgba(139,92,246,0.35);
    color: #D8B4FE;
    font-size: 12.5px;
    font-weight: 600;
    margin: 4px 6px 4px 0;
}
.badge-cyan {
    background: rgba(251,191,36,0.14);
    border: 1px solid rgba(251,191,36,0.35);
    color: #FDE68A;
}

/* ---------------- Score Gauge ---------------- */
.score-wrap {
    text-align: center;
    padding: 10px 0;
}
.score-track {
    width: 100%;
    height: 14px;
    border-radius: 999px;
    background: rgba(148,163,184,0.15);
    overflow: hidden;
    margin: 12px 0;
}
.score-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--secondary), var(--primary));
    transition: width 1s ease;
}
.status-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: .3px;
}

/* ---------------- History Table ---------------- */
.history-table {
    width: 100%;
    border-collapse: collapse;
    overflow: hidden;
    border-radius: 14px;
}
.history-table th {
    background: rgba(139,92,246,0.12);
    color: var(--text-main);
    text-align: left;
    padding: 12px 14px;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: .4px;
}
.history-table td {
    padding: 12px 14px;
    font-size: 14px;
    border-bottom: 1px solid var(--card-border);
}
.history-table tr:nth-child(even) {
    background: rgba(30,41,59,0.5);
}
.history-table tr:nth-child(odd) {
    background: rgba(15,23,42,0.35);
}
.history-table tr:hover {
    background: rgba(139,92,246,0.10);
}

/* ---------------- Footer ---------------- */
.app-footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 13px;
    margin-top: 50px;
    padding: 18px 0;
    border-top: 1px solid var(--card-border);
}
.app-footer b {
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
"""

css = css.replace("__PRIMARY__", primary)
css = css.replace("__SECONDARY__", secondary)
css = css.replace("__TERTIARY__", tertiary)
css = css.replace("__BG__", bg)
css = css.replace("__CARD__", card)
css = css.replace("__CARD_BORDER__", card_border)
css = css.replace("__TEXT_MAIN__", text_main)
css = css.replace("__TEXT_MUTED__", text_muted)
css = css.replace("__BODY_BG__", body_bg)
css = css.replace("__HERO_BG__", hero_bg)
css = css.replace("__CARD_TRANSPARENT__", card_transparent)
css = css.replace("__SURFACE__", surface)
css = css.replace("__SURFACE_SOFT__", surface_soft)
css = css.replace("__SURFACE_STRONG__", surface_strong)
css = css.replace("__INPUT_BG__", input_bg)
css = css.replace("__SIDEBAR_BG__", sidebar_bg)

st.markdown(css, unsafe_allow_html=True)


def metric_card(col, icon, label, value, indicator="ind-green"):
    col.markdown(f"""
    <div class="metric-card">
        <div class="indicator {indicator}"></div>
        <div class="icon">{icon}</div>
        <div class="label">{label}</div>
        <div class="value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(title, body, icon="⚡"):
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def style_chart(fig):
    """Re-skins a Plotly figure returned by charts.py to match the app's
    color theme. Does not touch chart data/logic — purely visual restyling."""
    if fig is None:
        return fig
    try:
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC", family="Poppins"),
            colorway=["#8B5CF6", "#FBBF24", "#22D3EE", "#F472B6", "#34D399", "#F87171"],
            legend=dict(font=dict(color="#F8FAFC")),
            margin=dict(t=30, l=10, r=10, b=10),
        )
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", color="#B4B9C9", zerolinecolor="rgba(255,255,255,0.08)")
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", color="#B4B9C9", zerolinecolor="rgba(255,255,255,0.08)")
        fig.update_traces(marker=dict(line=dict(color="#0A0A0F", width=1)))
    except Exception:
        pass
    return fig


def section_title(icon, text):
    st.markdown(f"""
    <div class="section-title"><span class="bar"></span> {icon} {text}</div>
    """, unsafe_allow_html=True)


def energy_score_gauge(score, status):
    status_colors = {
        "Excellent": ("#34D399", "rgba(52,211,153,0.16)"),
        "Good": ("#A78BFA", "rgba(139,92,246,0.16)"),
        "Average": ("#FBBF24", "rgba(251,191,36,0.16)"),
        "Poor": ("#F87171", "rgba(248,113,113,0.16)"),
    }
    color, bg = status_colors.get(status, ("#94A3B8", "rgba(148,163,184,0.18)"))
    pct = max(0, min(100, score))
    st.markdown(f"""
    <div class="score-wrap">
        <div style="font-size:34px; font-weight:800;">{score}<span style="font-size:16px; color:var(--text-muted);">/100</span></div>
        <div class="score-track"><div class="score-fill" style="width:{pct}%;"></div></div>
        <span class="status-badge" style="background:{bg}; color:{color}; border:1px solid {color};">{status}</span>
    </div>
    """, unsafe_allow_html=True)


def build_history_csv(rows):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Bill ID", "Consumer Number", "Bill Date", "Units", "Amount", "AI Recommendation"])
    for row in rows:
        writer.writerow(row)
    return output.getvalue()


# ======================================================
# Sidebar
# ======================================================
st.sidebar.markdown("""
<div class="sidebar-logo">
    <h1>⚡ VOLTWise AI</h1>
    <p>Smarter energy decisions in seconds</p>
</div>
<hr>
""", unsafe_allow_html=True)

if "page_target" not in st.session_state:
    st.session_state.page_target = None

if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

if "uploaded_bill_saved" not in st.session_state:
    st.session_state.uploaded_bill_saved = False
    st.session_state.current_bill_id = None

if st.session_state.page_target:
    st.session_state.page = st.session_state.page_target
    st.session_state.page_target = None

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📤 Upload Bill",
        "📊 Analytics",
        "📜 Bill History",
        "📄 Reports",
        "🤖 AI Insights",
        "ℹ️ About"
    ],
    index=["🏠 Dashboard","📤 Upload Bill","📊 Analytics","📜 Bill History","📄 Reports","🤖 AI Insights","ℹ️ About"].index(st.session_state.page),
    key="page",
    label_visibility="collapsed"
)

# ======================================================
# Dashboard
# ======================================================

if page == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>⚡ VOLTWise AI</h1>
        <p>Turn every electricity bill into a clear action plan with OCR, AI insights, and smarter energy recommendations.</p>
        <div class="hero-actions">
            <span class="pill">📄 OCR-powered bill reading</span>
            <span class="pill">🤖 Local AI analysis</span>
            <span class="pill">⚡ Savings guidance</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Upload your first bill", key="dashboard_cta"):
            st.session_state.page_target = "📤 Upload Bill"

    st.markdown('<div class="info-grid">', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><div class="title">🚀 Quick start</div><div class="meta">Upload a bill, review the extracted text, and get a tailored recommendation in seconds.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><div class="title">📊 Track progress</div><div class="meta">Compare bills over time and spot rising usage before it hurts your budget.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><div class="title">💡 Save smarter</div><div class="meta">See which appliances likely drive your bill and where small changes can make a big difference.</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    rows = get_all_bills()

    if rows:
        summary = summarize_bill_history(rows)

        section_title("📈", "Overview")

        m1, m2, m3 = st.columns(3)
        metric_card(m1, "📂", "Bills Uploaded", summary["total_bills"], "ind-green")
        metric_card(m2, "⚡", "Total Units", f"{summary['total_units']:.2f}", "ind-cyan")
        metric_card(m3, "💰", "Total Amount", f"₹{summary['total_amount']:.2f}", "ind-blue")

        m4, m5, m6 = st.columns(3)
        metric_card(m4, "📊", "Average Bill", f"₹{summary['average_bill']:.2f}", "ind-purple")
        metric_card(m5, "🔥", "Highest Bill", f"₹{summary['highest_bill']:.2f}", "ind-red")
        metric_card(m6, "❄️", "Lowest Bill", f"₹{summary['lowest_bill']:.2f}", "ind-amber")

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_title("🔎", "Trend Snapshot")
        if summary["trend"] == "up":
            st.info("Bills are trending upward compared with your earliest saved entry.")
        elif summary["trend"] == "down":
            st.success("Bills are trending downward compared with your earliest saved entry.")
        else:
            st.info("Bills are staying fairly consistent across your saved history.")
        st.caption(f"Average monthly usage: {summary['average_units']:.2f} units")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---------------- Charts ----------------

        fig1 = bill_amount_chart(rows)

        if fig1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            section_title("💰", "Bill Amount Trend")
            st.plotly_chart(style_chart(fig1), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        fig2 = unit_chart(rows)

        if fig2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            section_title("⚡", "Units Trend")
            st.plotly_chart(style_chart(fig2), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            pie = consumption_pie(rows)
            if pie:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                section_title("🥧", "Consumption Distribution")
                st.plotly_chart(
                    style_chart(pie),
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        render_empty_state(
            "Ready when you are",
            "Upload your first bill to unlock summaries, charts, and smart recommendations.",
            icon="📄"
        )

# ======================================================
# Upload Bill
# ======================================================

elif page == "📤 Upload Bill":

    st.markdown("""
    <div class="hero">
        <h1>📄 Upload Electricity Bill</h1>
        <p>Drop a PDF or image of your bill and let OCR + AI do the rest.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_title("📦", "Smart Bill Upload")
    st.write("Upload a PDF or a clear photo of your electricity bill. We’ll extract the key fields automatically.")

    uploaded_file = st.file_uploader(
        "Upload your bill",
        type=["pdf", "png", "jpg", "jpeg"]
    )
    st.markdown(
        '<div class="upload-hint"><strong>Best practices:</strong><ul>'
        '<li>Use a high-resolution scan or photo.</li>'
        '<li>Keep the bill centered, well-lit, and readable.</li>'
        '<li>PDF files usually give the most accurate OCR results.</li>'
        '</ul></div>',
        unsafe_allow_html=True,
    )

    if uploaded_file:
        st.markdown('<span class="status-chip"><span></span>File received</span>', unsafe_allow_html=True)
        if uploaded_file.name.lower().endswith(".pdf") and not POPPLER_PATH:
            st.warning(
                "PDF OCR requires Poppler. Install it and either add it to PATH or provide the Poppler bin folder here."
            )
        if not TESSERACT_PATH:
            st.warning(
                "Tesseract OCR is required. Install Tesseract and add it to PATH or provide the executable path above."
            )
    else:
        st.markdown('<span class="status-chip"><span></span>Ready to upload</span>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("🧭 How VOLTWise AI works", expanded=False):
        st.write("Upload a bill, review extracted data, then get a guided recommendation.")

    if uploaded_file:
        st.success("✅ Bill uploaded successfully")
        st.info("Tip: use a clear PDF or a sharp image with good contrast for the best OCR results.")

        with st.status("Processing your bill…", expanded=True) as status:
            try:
                st.write("Extracting text with OCR…")
                text = extract_text(
                    uploaded_file,
                    poppler_path=POPPLER_PATH,
                    tesseract_path=TESSERACT_PATH,
                )
                st.write("Parsing bill details…")
                bill_data = parse_bill(text)
                if not bill_data:
                    st.warning("The bill could not be parsed automatically. You can still review the raw OCR text below and edit the fields manually.")
                else:
                    if not st.session_state.uploaded_bill_saved:
                        analysis_placeholder = "Pending analysis"
                        bill_id = save_bill(bill_data, analysis_placeholder)
                        st.session_state.uploaded_bill_saved = True
                        st.session_state.current_bill_id = bill_id
                status.update(label="Processing complete", state="complete")
            except Exception as exc:
                status.update(label="Processing failed", state="error")
                st.error(f"OCR processing failed: {exc}")
                st.stop()

        with st.expander("📄 OCR Extracted Text", expanded=False):
            st.text_area(
                "OCR Output",
                text,
                height=250
            )

        if bill_data:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            section_title("🧾", "Parsed Bill Summary")
            for key, value in bill_data.items():
                st.markdown(f"**{key}:** {value}")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.uploaded_bill_saved:
                st.success("✅ Bill saved successfully. You can analyze it or view analytics now.")

            # ---------------- Bulk sample uploader ----------------
            with st.expander("📚 Upload sample bills for labeling (bulk)", expanded=False):
                sample_files = st.file_uploader(
                    "Upload sample bills",
                    accept_multiple_files=True,
                    type=["pdf", "png", "jpg", "jpeg"],
                    key="bulk_samples"
                )

                if st.button("Export saved samples CSV"):
                    csv_data = export_samples_csv()
                    st.download_button("⬇️ Download samples CSV", csv_data, file_name="samples.csv", mime="text/csv")

                if sample_files:
                    if st.button("Save all samples", key="save_all_samples"):
                        saved_count = 0
                        for sf in sample_files:
                            try:
                                sf_text = extract_text(sf, poppler_path=POPPLER_PATH, tesseract_path=TESSERACT_PATH)
                            except Exception:
                                continue

                            parsed_sf = parse_bill(sf_text) or {}
                            consumer = st.session_state.get(f"sample_consumer_{sf.name}", parsed_sf.get("Consumer Number", ""))
                            billdate = st.session_state.get(f"sample_date_{sf.name}", parsed_sf.get("Bill Date", ""))
                            units_s = st.session_state.get(f"sample_units_{sf.name}", parsed_sf.get("Units", ""))
                            amount_s = st.session_state.get(f"sample_amount_{sf.name}", parsed_sf.get("Amount", ""))

                            corrected = {
                                "Consumer Number": consumer,
                                "Bill Date": billdate,
                                "Units": units_s,
                                "Amount": amount_s,
                            }

                            save_sample(sf.name, sf_text, parsed_sf, corrected)
                            saved_count += 1

                        st.success(f"Saved {saved_count} samples")

                    for sf in sample_files:
                        st.markdown(f"**{sf.name}**")
                        try:
                            sf_text = extract_text(sf, poppler_path=POPPLER_PATH, tesseract_path=TESSERACT_PATH)
                        except Exception as exc:
                            st.error(f"OCR failed for {sf.name}: {exc}")
                            continue

                        parsed_sf = parse_bill(sf_text) or {}
                        st.text_area("OCR Output", sf_text, height=180)

                        c1, c2, c3, c4 = st.columns(4)
                        consumer = c1.text_input("Consumer Number", value=parsed_sf.get("Consumer Number", ""), key=f"sample_consumer_{sf.name}")
                        billdate = c2.text_input("Bill Date", value=parsed_sf.get("Bill Date", ""), key=f"sample_date_{sf.name}")
                        units_s = c3.text_input("Units", value=parsed_sf.get("Units", ""), key=f"sample_units_{sf.name}")
                        amount_s = c4.text_input("Amount", value=parsed_sf.get("Amount", ""), key=f"sample_amount_{sf.name}")

                        corrected = {
                            "Consumer Number": consumer,
                            "Bill Date": billdate,
                            "Units": units_s,
                            "Amount": amount_s,
                        }

                        if st.button(f"Save sample {sf.name}", key=f"save_sample_{sf.name}"):
                            save_sample(sf.name, sf_text, parsed_sf, corrected)
                            st.success(f"Saved sample: {sf.name}")

# =====================================================
# Energy Score
# =====================================================

            score = 0
            status = "Unknown"

            if "Units" in bill_data:

                score, status = energy_score(
                    bill_data["Units"]
                    )

                with st.expander("⭐ Energy Score", expanded=True):
                    energy_score_gauge(score, status)

            # AI Analysis
            if st.button("🤖 Analyze Bill"):

                with st.spinner("Gemma 3 is analyzing your bill..."):
                    result = analyze_bill(
                        bill_data
                    )

                st.markdown('<div class="ai-box">', unsafe_allow_html=True)
                st.markdown('<div class="ai-header">🤖 AI Assistant — Recommendation</div>', unsafe_allow_html=True)
                st.write(result)
                st.markdown('</div>', unsafe_allow_html=True)

                pdf = generate_report(
                    bill_data,
                    result,
                    score,
                    status
                )

                with open(pdf, "rb") as file:
                    st.download_button(
                        "📄 Download Report",
                        file,
                        file_name="VOLTWise_Report.pdf"
                    )

                if st.session_state.current_bill_id:
                    update_bill_analysis(st.session_state.current_bill_id, result)
                else:
                    save_bill(
                        bill_data,
                        result
                    )

                st.success("Bill analysis and report generation complete.")

        else:

            st.warning(
                "Unable to detect bill information."
            )

# ======================================================
# Analytics
# ======================================================

elif page == "📊 Analytics":

    st.markdown("""
    <div class="hero">
        <h1>📊 Analytics</h1>
        <p>Deeper look at your electricity consumption trends over time.</p>
    </div>
    """, unsafe_allow_html=True)

    rows = get_all_bills()

    if rows:
        summary = summarize_bill_history(rows)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_title("📌", "Key Insights")
        st.write(f"- Total bills saved: {summary['total_bills']}")
        st.write(f"- Total units consumed: {summary['total_units']:.2f}")
        st.write(f"- Average bill amount: ₹{summary['average_bill']:.2f}")
        st.write(f"- Trend: {summary['trend'].capitalize()}")
        st.markdown('</div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["💰 Bill Amount Trend", "⚡ Units Trend", "🥧 Consumption Distribution"])

        with tab1:
            fig1 = bill_amount_chart(rows)
            if fig1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.plotly_chart(style_chart(fig1), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            fig2 = unit_chart(rows)
            if fig2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.plotly_chart(style_chart(fig2), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            pie = consumption_pie(rows)
            if pie:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.plotly_chart(style_chart(pie), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        render_empty_state(
            "No analytics yet",
            "Upload a few bills to unlock trend charts and useful energy insights.",
            icon="📈"
        )

# ======================================================
# Bill History
# ======================================================

elif page == "📜 Bill History":

    st.markdown("""
    <div class="hero">
        <h1>📑 Bill History</h1>
        <p>All your previously analyzed electricity bills in one place.</p>
    </div>
    """, unsafe_allow_html=True)

    rows = get_all_bills()

    if rows:

        table_rows = ""
        for row in rows:
            table_rows += (
                "<tr>"
                f"<td>#{row[0]}</td>"
                f"<td>{row[1]}</td>"
                f"<td>{row[2]}</td>"
                f"<td>{row[3]}</td>"
                f"<td>₹{row[4]}</td>"
                "</tr>"
            )

        table_html = (
            '<div class="glass-card">'
            '<table class="history-table">'
            "<tr>"
            "<th>Bill ID</th>"
            "<th>Consumer No.</th>"
            "<th>Bill Date</th>"
            "<th>Units</th>"
            "<th>Amount</th>"
            "</tr>"
            f"{table_rows}"
            "</table>"
            "</div>"
        )

        st.markdown(table_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for row in rows:
            with st.expander(f"🤖 AI Recommendation — Bill #{row[0]}"):
                if row[5] and row[5] != "Pending analysis":
                    st.write(row[5])
                else:
                    st.info("This bill has been saved, but AI analysis is still pending. Click Analyze Bill on the Upload page to generate recommendations.")

    else:
        render_empty_state(
            "Your bill history is empty",
            "Analyze a bill to start building a history of savings and trends.",
            icon="🧾"
        )

# ======================================================
# Reports
# ======================================================

elif page == "📄 Reports":

    st.markdown("""
    <div class="hero">
        <h1>📄 Reports</h1>
        <p>Download professionally generated PDF reports for your analyzed bills.</p>
    </div>
    """, unsafe_allow_html=True)

    rows = get_all_bills()

    if rows:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_title("📑", "Saved Bills")
        st.write("Your saved bills are listed below. Generate a PDF report after analyzing a bill on the Upload page.")
        st.write(f"**{len(rows)} saved bills** in your history.")
        st.info("Download your bill history as CSV or go to Upload to analyze a bill and create a report.")
        csv_data = build_history_csv(rows)
        st.download_button(
            "⬇️ Download bill history CSV",
            csv_data,
            file_name="bill_history.csv",
            mime="text/csv"
        )
        for row in rows:
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"Bill #{row[0]} — {row[2]}")
            c2.write(f"₹{row[4]} · {row[3]} units")
            c3.markdown('<span class="badge">Saved</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        render_empty_state(
            "No reports yet",
            "Analyze a bill to generate and download your first PDF report.",
            icon="📄"
        )

# ======================================================
# AI Insights
# ======================================================

elif page == "🤖 AI Insights":

    st.markdown("""
    <div class="hero">
        <h1>🤖 AI Insights</h1>
        <p>Your latest personalized, AI-generated energy-saving recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

    rows = get_all_bills()

    if rows:
        latest = rows[-1]
        if latest[5] and latest[5] != "Pending analysis":
            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            st.markdown('<div class="ai-header">🤖 AI Assistant</div>', unsafe_allow_html=True)
            st.write(latest[5])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            render_empty_state(
                "AI insights will appear here",
                "Analyze a bill on the Upload page to generate personalized recommendations.",
                icon="🤖"
            )
    else:
        render_empty_state(
            "AI insights will appear here",
            "Upload and analyze one bill to get personalized recommendations.",
            icon="🤖"
        )

# ======================================================
# About
# ======================================================

elif page == "ℹ️ About":

    st.markdown("""
    <div class="hero">
        <h1>⚡ About VOLTWise AI</h1>
        <p>LLM-Based Smart Energy Consumption Advisor</p>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.markdown("""
        <div class="metric-card">
            <div class="indicator ind-green"></div>
            <div class="icon">📄</div>
            <div class="label">OCR</div>
            <div style="font-size:13px; color:var(--text-muted); margin-top:6px;">
            Extracts text from bill PDFs and images using Tesseract OCR.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="metric-card">
            <div class="indicator ind-cyan"></div>
            <div class="icon">🤖</div>
            <div class="label">LLM</div>
            <div style="font-size:13px; color:var(--text-muted); margin-top:6px;">
            Gemma 3, run locally via Ollama, powers bill analysis and tips.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="metric-card">
            <div class="indicator ind-purple"></div>
            <div class="icon">⭐</div>
            <div class="label">Energy Score</div>
            <div style="font-size:13px; color:var(--text-muted); margin-top:6px;">
            Scores your consumption and flags where you stand.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f4:
        st.markdown("""
        <div class="metric-card">
            <div class="indicator ind-amber"></div>
            <div class="icon">📊</div>
            <div class="label">Analytics</div>
            <div style="font-size:13px; color:var(--text-muted); margin-top:6px;">
            Interactive charts track spend and usage over time.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_title("🛠️", "Technology Stack")
    st.markdown("""
    <span class="badge">Python</span>
    <span class="badge badge-cyan">Streamlit</span>
    <span class="badge">Tesseract OCR</span>
    <span class="badge badge-cyan">Poppler</span>
    <span class="badge">SQLite</span>
    <span class="badge badge-cyan">Plotly</span>
    <span class="badge">Ollama</span>
    <span class="badge badge-cyan">Gemma 3</span>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_title("🎯", "Project Objective")
    st.write(
        "Help users understand their electricity bill, reduce unnecessary "
        "energy consumption, and receive AI-powered recommendations."
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# Footer
# ======================================================

st.markdown("""
<div class="app-footer">
    <b>⚡ VOLTWise AI</b><br>
    Built with ❤️ using Streamlit + AI
</div>
""", unsafe_allow_html=True)                                                                            