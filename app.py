import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from PyPDF2 import PdfReader
from io import BytesIO

load_dotenv()

st.set_page_config(
    page_title="KonspektAI",
    page_icon="K",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body { margin: 0; padding: 0; }

/* ── BASE ── */
.stApp {
    background: #EDEAE3 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Force readable text everywhere in main area */
.stApp p, .stApp span, .stApp div,
.stApp label, .stApp li,
.stApp h1, .stApp h2, .stApp h3 {
    color: #1C1917;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 2.5rem !important;
}
header[data-testid="stHeader"] button {
    background: #FFFFFF !important;
    border: 1px solid #D4CFC9 !important;
    border-radius: 8px !important;
}
header[data-testid="stHeader"] button svg {
    fill: #1C1917 !important;
    stroke: #1C1917 !important;
}

/* ── LAYOUT ── */
.block-container {
    max-width: 900px !important;
    padding: 0.5rem 2.5rem 3rem !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #1C1917 !important;
    border-right: none !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small {
    color: #D6D3D1 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #292524 !important;
    border: 1.5px dashed #44403C !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: #B8B3AD !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #292524 !important;
    border: 1px solid #3C3835 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] span {
    color: #D6D3D1 !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
    fill: #B8B3AD !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: #FFFFFF !important;
    border: 1.5px solid #D4CFC9 !important;
    border-radius: 16px !important;
    margin-bottom: 10px !important;
    padding: 1.1rem 1.4rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatMessage"] p {
    color: #1C1917 !important;
    font-size: 0.95rem !important;
    line-height: 1.78 !important;
    margin: 0 !important;
}
[data-testid="stChatMessage"] .stMarkdown p,
[data-testid="stChatMessage"] .stMarkdown span,
[data-testid="stChatMessage"] .stMarkdown div,
[data-testid="stChatMessage"] .stMarkdown li,
[data-testid="stChatMessage"] .stMarkdown strong,
[data-testid="stChatMessage"] .stMarkdown em {
    color: #1C1917 !important;
}
[data-testid="stChatMessage"] .stMarkdown h1,
[data-testid="stChatMessage"] .stMarkdown h2,
[data-testid="stChatMessage"] .stMarkdown h3 {
    color: #1C1917 !important;
    font-weight: 800 !important;
}
[data-testid="stChatMessage"] .stMarkdown code {
    background: #F5F2EE !important;
    border: 1px solid #D4CFC9 !important;
    color: #FF5C35 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82em !important;
}
[data-testid="stChatMessage"] .stMarkdown pre {
    background: #1C1917 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="stChatMessage"] .stMarkdown pre code {
    background: transparent !important;
    border: none !important;
    color: #E7E5E4 !important;
    padding: 0 !important;
}

/* User message — dark bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #1C1917 !important;
    border-color: #1C1917 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown span,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown div,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown li,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown strong {
    color: #FFFFFF !important;
}

[data-testid="chatAvatarIcon-user"] {
    background: #FF5C35 !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: #FFFFFF !important;
    color: #1C1917 !important;
    border: 2px solid #D4CFC9 !important;
    border-radius: 10px !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 2px solid #D4CFC9 !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #FF5C35 !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #1C1917 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important;
    padding: 0.9rem 1.1rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #8B8580 !important;
}
[data-testid="stChatInput"] button {
    background: #1C1917 !important;
    border: none !important;
    border-radius: 10px !important;
    margin: 7px !important;
}
[data-testid="stChatInput"] button svg { fill: #FFFFFF !important; }
[data-testid="stChatInput"] button:hover { background: #FF5C35 !important; }

/* ── BUTTONS — main area ── */
.stButton > button {
    background: #1C1917 !important;
    color: #FFFFFF !important;
    border: 2px solid #1C1917 !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    padding: 0.55rem 1.1rem !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #FF5C35 !important;
    border-color: #FF5C35 !important;
    transform: translateY(-1px) !important;
}
.btn-accent .stButton > button {
    background: #FF5C35 !important;
    border-color: #FF5C35 !important;
    color: #FFFFFF !important;
}
.btn-accent .stButton > button:hover {
    background: #e04a26 !important;
    border-color: #e04a26 !important;
    transform: none !important;
}
.btn-outline .stButton > button {
    background: transparent !important;
    color: #1C1917 !important;
    border: 1.5px solid #1C1917 !important;
}
.btn-outline .stButton > button:hover {
    background: #FFF7ED !important;
    border-color: #FF5C35 !important;
    color: #FF5C35 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .nav-btn .stButton > button {
    background: transparent !important;
    color: #B8B3AD !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 0.75rem !important;
    text-align: left !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .nav-btn .stButton > button:hover {
    background: #292524 !important;
    color: #FFFFFF !important;
    transform: none !important;
}
[data-testid="stSidebar"] .nav-btn-active .stButton > button {
    background: #FF5C35 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
}
[data-testid="stSidebar"] .nav-btn-active .stButton > button:hover {
    background: #e04a26 !important;
}
[data-testid="stSidebar"] .action-btn .stButton > button {
    background: transparent !important;
    color: #B8B3AD !important;
    border: 1px solid #3C3835 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    padding: 0.45rem 0.75rem !important;
}
[data-testid="stSidebar"] .action-btn .stButton > button:hover {
    background: #292524 !important;
    color: #FFFFFF !important;
    border-color: #57534E !important;
    transform: none !important;
}

/* ── TEXT INPUT / TEXT AREA (main) ── */
.stTextInput input {
    background: #FFFFFF !important;
    border: 1.5px solid #D4CFC9 !important;
    border-radius: 10px !important;
    color: #1C1917 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 0.9rem !important;
}
.stTextInput input:focus {
    border-color: #FF5C35 !important;
    box-shadow: 0 0 0 3px rgba(255,92,53,0.08) !important;
}
.stTextInput input::placeholder { color: #8B8580 !important; }

[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important;
    border: 1.5px solid #D4CFC9 !important;
    border-radius: 12px !important;
    color: #1C1917 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    line-height: 1.65 !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #FF5C35 !important;
}

/* ── SLIDER ── */
[data-testid="stSlider"] {
    color: #1C1917 !important;
}
[data-testid="stSlider"] p,
[data-testid="stSlider"] span,
[data-testid="stSlider"] div {
    color: #1C1917 !important;
}
[data-testid="stSlider"] [data-testid="stTickBar"],
[data-testid="stSlider"] .stSlider {
    color: #1C1917 !important;
}

/* ── SELECTBOX (main) ── */
[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    border: 1.5px solid #D4CFC9 !important;
    border-radius: 10px !important;
    color: #1C1917 !important;
}
[data-testid="stSelectbox"] span { color: #1C1917 !important; }

/* ── MISC ── */
.stSpinner > div { border-top-color: #FF5C35 !important; }
hr { border: none; border-top: 2px solid #D4CFC9 !important; margin: 1.25rem 0 !important; }

/* ── ALERTS ── */
.alert {
    padding: 0.8rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    line-height: 1.6;
    border: 1.5px solid;
    margin: 0.5rem 0;
    font-weight: 600;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.alert b { font-weight: 700; }
.alert-ok   { background:#F0FDF4; border-color:#BBF7D0; color:#15803D; }
.alert-err  { background:#FEE2E2; border-color:#FECACA; color:#991B1B; }
.alert-nfo  { background:#EEF2FF; border-color:#C7D2FE; color:#1E40AF; }
.alert-warn { background:#FFFBEB; border-color:#FDE68A; color:#92400E; }

/* ── PAGE HEADER ── */
.page-header {
    padding: 1.5rem 0 1.25rem;
    border-bottom: 2px solid #1C1917;
    margin-bottom: 2rem;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
}
.page-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 2.1rem;
    color: #1C1917;
    letter-spacing: -1px;
    line-height: 1;
}
.page-title-accent { color: #FF5C35; }
.page-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #5A5652;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 6px;
    font-weight: 700;
}
.mode-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 999px;
    font-weight: 700;
    border: 1.5px solid;
}
.mode-pill-pdf  { background:#FFF7ED; border-color:#FDBA74; color:#92400E; }
.mode-pill-free { background:#EEF2FF; border-color:#A5B4FC; color:#1E40AF; }

/* ── CARDS ── */
.card {
    background: #FFFFFF;
    border: 1.5px solid #D4CFC9;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-accent { border-left: 4px solid #FF5C35; }
.card-title {
    font-weight: 700;
    font-size: 1rem;
    color: #1C1917;
    margin-bottom: 0.4rem;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.card-sub {
    font-size: 0.85rem;
    color: #2A2622;
    line-height: 1.65;
    font-weight: 500;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── PDF BAR ── */
.pdf-bar {
    background: #FFFFFF;
    border: 1.5px solid #D4CFC9;
    border-left: 4px solid #FF5C35;
    border-radius: 12px;
    padding: 0.85rem 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
.pdf-bar-title {
    font-weight: 700;
    font-size: 0.88rem;
    color: #1C1917;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.pdf-bar-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #5A5652;
    margin-top: 2px;
    font-weight: 500;
}

/* ── EMPTY STATE ── */
.empty-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
}
.empty-icon {
    width: 72px; height: 72px;
    background: #FFFFFF;
    border: 2px solid #D4CFC9;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin-bottom: 1.25rem;
}
.empty-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 1.35rem;
    color: #1C1917;
    letter-spacing: -0.5px;
    margin-bottom: 0.6rem;
}
.empty-body {
    font-size: 0.88rem;
    color: #2A2622;
    line-height: 1.85;
    max-width: 360px;
    font-weight: 500;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.empty-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 1.5rem;
}
.chip {
    background: #FFFFFF;
    border: 1.5px solid #D4CFC9;
    border-radius: 999px;
    padding: 0.4rem 0.9rem;
    font-size: 0.78rem;
    color: #2A2622;
    font-weight: 600;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── QUIZ ── */
.quiz-question {
    background: #FFFFFF;
    border: 1.5px solid #D4CFC9;
    border-radius: 14px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 0.75rem;
}
.quiz-q-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #FF5C35;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    font-weight: 700;
}
.quiz-q-text {
    font-weight: 700;
    font-size: 0.95rem;
    color: #1C1917;
    line-height: 1.5;
    margin-bottom: 0.9rem;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.quiz-answer-box {
    background: #F5F2EE;
    border: 1.5px solid #D4CFC9;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.88rem;
    color: #2A2622;
    line-height: 1.65;
    margin-top: 0.5rem;
    font-weight: 500;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.quiz-answer-correct {
    background: #F0FDF4;
    border-color: #BBF7D0;
    color: #15803D;
}
.quiz-score {
    background: #FFFFFF;
    border: 2px solid #1C1917;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
}
.quiz-score-num {
    font-size: 3.5rem;
    font-weight: 800;
    color: #FF5C35;
    letter-spacing: -2px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.quiz-score-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #5A5652;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
    font-weight: 700;
}

/* ── TAGS ── */
.tag {
    display: inline-block;
    border-radius: 4px;
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 1px;
    font-weight: 700;
}
.tag-orange { background:#FFF7ED; border:1px solid #FDBA74; color:#92400E; }
.tag-green  { background:#F0FDF4; border:1px solid #BBF7D0; color:#15803D; }
.tag-blue   { background:#EEF2FF; border:1px solid #C7D2FE; color:#1E40AF; }

/* ── SIDEBAR COMPONENTS ── */
.sb-logo { padding: 0 1rem 1.25rem; border-bottom: 1px solid #292524; margin-bottom: 1.25rem; }
.sb-logo-text { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 1.4rem; color: #FFFFFF; letter-spacing: -0.5px; }
.sb-logo-dot { color: #FF5C35; }
.sb-logo-sub { font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #897D77; letter-spacing: 2px; text-transform: uppercase; margin-top: 3px; }

.sb-section { padding: 0 1rem; margin-bottom: 1.25rem; }
.sb-section-title { font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #6B6B6B; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.6rem; display: block; font-weight: 700; }

.sb-file-card { background: #292524; border: 1px solid #3C3835; border-radius: 10px; padding: 0.7rem 0.9rem; margin-top: 0.5rem; }
.sb-file-name { font-weight: 600; font-size: 0.82rem; color: #FFFFFF; margin-bottom: 4px; font-family: 'Plus Jakarta Sans', sans-serif; }
.sb-file-meta { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #A39F9B; }
.sb-file-badge { display: inline-block; background: #16A34A20; color: #22C55E; border: 1px solid #16A34A40; border-radius: 4px; padding: 2px 7px; font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; font-weight: 600; }

.sb-model-display { background: #292524; border: 1px solid #3C3835; border-radius: 8px; padding: 0.55rem 0.75rem; display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem; }
.sb-model-dot { width: 7px; height: 7px; background: #FF5C35; border-radius: 50%; flex-shrink: 0; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.sb-model-name { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #B8B3AD; font-weight: 500; }

.sb-stat-row { display: flex; justify-content: space-between; align-items: baseline; padding: 0.3rem 0; border-bottom: 1px solid #292524; }
.sb-stat-row:last-child { border-bottom: none; }
.sb-stat-label { font-size: 0.78rem; color: #A39F9B; font-weight: 500; font-family: 'Plus Jakarta Sans', sans-serif; }
.sb-stat-val { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #FFFFFF; font-weight: 600; }

/* ── SETTINGS PAGE SPECIFIC ── */
.settings-section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: #1C1917;
    margin-bottom: 0.2rem;
}
.settings-caption {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #5A5652;
    margin-bottom: 0.75rem;
    display: block;
}
.check-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #D4CFC9;
}
.check-row-label {
    font-size: 0.88rem;
    color: #1C1917;
    flex: 1;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 500;
}
.stat-mini {
    text-align: center;
    background: #FFFFFF;
    border: 1.5px solid #D4CFC9;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.stat-mini-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: #5A5652;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
    display: block;
}
.stat-mini-val {
    font-size: 1.8rem;
    font-weight: 800;
    color: #FF5C35;
    font-family: 'Plus Jakarta Sans', sans-serif;
    line-height: 1;
}

/* ── KONSPEKT PAGE SPECIFIC ── */
.konspekt-stat {
    background: #FFFFFF;
    border: 1.5px solid #D4CFC9;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 1rem;
}
.konspekt-stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: #5A5652;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
    display: block;
}
.konspekt-stat-val {
    font-weight: 700;
    font-size: 1.05rem;
    color: #1C1917;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── FOOTER ── */
.app-footer {
    text-align: center;
    padding: 2.5rem 0 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: #5A5652;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 700;
}

/* ── PROGRESS BAR ── */
.progress-wrap { margin-bottom: 1.5rem; }
.progress-top { display: flex; justify-content: space-between; margin-bottom: 6px; }
.progress-label { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #5A5652; text-transform: uppercase; letter-spacing: 1.5px; }
.progress-count { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #FF5C35; font-weight: 600; }
.progress-track { background: #D4CFC9; border-radius: 999px; height: 6px; overflow: hidden; }
.progress-fill { background: #FF5C35; height: 100%; border-radius: 999px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── API ──
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.markdown('<div class="alert alert-err"><b>GROQ_API_KEY не знайдено</b> — додай у файл .env</div>', unsafe_allow_html=True)
    st.stop()

client = Groq(api_key=api_key)

# ── SESSION STATE ──
defaults = {
    "messages": [],
    "knowledge_base": "",
    "file_name": "",
    "page_count": 0,
    "page": "chat",
    "quiz_questions": [],
    "quiz_answers": [],
    "quiz_revealed": [],
    "quiz_ai_answers": [],
    "temperature": 0.35,
    "max_tokens": 1800,
    "system_prompt": "",
    "chunk_size": 14000,
    "model": "llama-3.3-70b-versatile",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="sb-logo-text">Konspekt<span class="sb-logo-dot">AI</span></div>
      <div class="sb-logo-sub">RAG навчальний асистент</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:0 0.5rem;margin-bottom:1.25rem;">', unsafe_allow_html=True)
    st.markdown('<span class="sb-section-title" style="padding:0 0.25rem">Навігація</span>', unsafe_allow_html=True)
    for key, icon, label in [
        ("chat",      "–", "Чат з асистентом"),
        ("konspekt",  "–", "Мій конспект"),
        ("quiz",      "–", "Квіз-режим"),
        ("settings",  "–", "Налаштування"),
    ]:
        is_active = st.session_state.page == key
        css = "nav-btn-active nav-btn" if is_active else "nav-btn"
        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{key}"):
            st.session_state.page = key
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#292524 !important;margin:0 0 1.25rem !important;">', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">', unsafe_allow_html=True)
    st.markdown('<span class="sb-section-title">Конспект (PDF)</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("PDF", type="pdf", label_visibility="collapsed")
    if uploaded_file:
        raw = uploaded_file.read()
        if len(raw) > 50 * 1024 * 1024:
            st.markdown('<div class="alert alert-err">Файл перевищує 50 МБ</div>', unsafe_allow_html=True)
        elif st.session_state.file_name != uploaded_file.name:
            with st.spinner("Читаю PDF..."):
                try:
                    reader = PdfReader(BytesIO(raw))
                    text = ""
                    for i, page in enumerate(reader.pages):
                        extracted = page.extract_text()
                        if extracted:
                            text += f"\n--- Стор. {i+1} ---\n{extracted}"
                    if text.strip():
                        st.session_state.knowledge_base = text
                        st.session_state.file_name = uploaded_file.name
                        st.session_state.page_count = len(reader.pages)
                        st.session_state.messages = []
                        st.session_state.quiz_questions = []
                        st.session_state.quiz_answers = []
                        st.session_state.quiz_revealed = []
                        st.session_state.quiz_ai_answers = []
                        st.rerun()
                    else:
                        st.markdown('<div class="alert alert-err">PDF не містить тексту</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="alert alert-err">{str(e)[:100]}</div>', unsafe_allow_html=True)
        else:
            name = st.session_state.file_name
            st.markdown(f"""
            <div class="sb-file-card">
              <div class="sb-file-badge">завантажено</div>
              <div class="sb-file-name">{name[:28]}{"..." if len(name)>28 else ""}</div>
              <div class="sb-file-meta">{st.session_state.page_count} стор. · {len(st.session_state.knowledge_base):,} симв.</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#292524 !important;margin:0.25rem 0 1.25rem !important;">', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">', unsafe_allow_html=True)
    st.markdown('<span class="sb-section-title">Модель</span>', unsafe_allow_html=True)
    model_list = ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"]
    idx = model_list.index(st.session_state.model) if st.session_state.model in model_list else 0
    model_choice = st.selectbox("Модель", model_list, index=idx, label_visibility="collapsed")
    st.session_state.model = model_choice
    st.markdown(f'<div class="sb-model-display"><div class="sb-model-dot"></div><div class="sb-model-name">online · {model_choice[:22]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.knowledge_base:
        st.markdown('<hr style="border-color:#292524 !important;margin:1rem 0 1.25rem !important;">', unsafe_allow_html=True)
        st.markdown('<div class="sb-section">', unsafe_allow_html=True)
        st.markdown('<span class="sb-section-title">Статистика</span>', unsafe_allow_html=True)
        msgs_u = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.markdown(f"""
        <div>
          <div class="sb-stat-row"><span class="sb-stat-label">Повідомлень</span><span class="sb-stat-val">{len(st.session_state.messages)}</span></div>
          <div class="sb-stat-row"><span class="sb-stat-label">Запитань</span><span class="sb-stat-val">{msgs_u}</span></div>
          <div class="sb-stat-row"><span class="sb-stat-label">Сторінок PDF</span><span class="sb-stat-val">{st.session_state.page_count}</span></div>
          <div class="sb-stat-row"><span class="sb-stat-label">Символів</span><span class="sb-stat-val">{len(st.session_state.knowledge_base):,}</span></div>
          <div class="sb-stat-row"><span class="sb-stat-label">Питань квізу</span><span class="sb-stat-val">{len(st.session_state.quiz_questions)}</span></div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#292524 !important;margin:1rem 0 1rem !important;">', unsafe_allow_html=True)
    st.markdown('<div class="sb-section">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="action-btn">', unsafe_allow_html=True)
        if st.button("Скинути", use_container_width=True, key="reset_all"):
            for k in ["messages","knowledge_base","file_name","page_count","quiz_questions","quiz_answers","quiz_revealed","quiz_ai_answers"]:
                st.session_state[k] = defaults[k]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="action-btn">', unsafe_allow_html=True)
        if st.button("Новий чат", use_container_width=True, key="new_chat"):
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── HELPER ──
def render_header(title, accent, subtitle, badge=""):
    st.markdown(f"""
    <div class="page-header">
      <div>
        <div class="page-title">{title}<span class="page-title-accent">{accent}</span></div>
        <div class="page-subtitle">{subtitle}</div>
      </div>
      {badge}
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════
#  PAGE: CHAT
# ══════════════════════════════════════
def page_chat():
    has_pdf = bool(st.session_state.knowledge_base)
    badge = '<span class="mode-pill mode-pill-pdf">PDF режим</span>' if has_pdf else '<span class="mode-pill mode-pill-free">Вільний чат</span>'
    sub = "ВІДПОВІДІ НА ОСНОВІ КОНСПЕКТУ" if has_pdf else "AI-АСИСТЕНТ ДЛЯ НАВЧАННЯ"
    render_header("Konspekt", "AI", sub, badge)

    if has_pdf:
        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(f"""
            <div class="pdf-bar">
              <div>
                <div class="pdf-bar-title">{st.session_state.file_name}</div>
                <div class="pdf-bar-sub">{st.session_state.page_count} стор. · {len(st.session_state.knowledge_base):,} символів · готово до роботи</div>
              </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="btn-accent" style="margin-top:4px">', unsafe_allow_html=True)
            if st.button("Квіз", use_container_width=True, key="go_quiz"):
                st.session_state.page = "quiz"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        if has_pdf:
            st.markdown("""
            <div class="empty-wrap">
              <div class="empty-icon">K</div>
              <div class="empty-title">Матеріал готовий</div>
              <div class="empty-body">Задавай питання нижче — відповіді будуть виключно на основі твого конспекту.</div>
              <div class="empty-chips">
                <span class="chip">Поясни цю тему</span>
                <span class="chip">Що таке...?</span>
                <span class="chip">Порівняй...</span>
                <span class="chip">Підсумуй</span>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-wrap">
              <div class="empty-icon">K</div>
              <div class="empty-title">Привіт, я KonspektAI</div>
              <div class="empty-body">Твій персональний асистент для навчання. Завантаж PDF ліворуч — і я відповідатиму виключно по твоєму матеріалу.</div>
              <div class="empty-chips">
                <span class="chip">Що таке фотосинтез?</span>
                <span class="chip">Поясни теорему Піфагора</span>
                <span class="chip">Як готуватись до іспиту?</span>
              </div>
            </div>""", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input(
        "Задай питання по конспекту..." if has_pdf else "Напиши питання або тему для пояснення..."
    )

    if user_input and user_input.strip():
        question = user_input.strip()
        if len(question) > 50000:
            st.markdown('<div class="alert alert-err">Запит занадто довгий (макс. 50 000 символів)</div>', unsafe_allow_html=True)
            return

        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})

        custom_sys = st.session_state.system_prompt.strip()
        if has_pdf:
            ctx = st.session_state.knowledge_base[:st.session_state.chunk_size]
            system = (custom_sys + f"\n\nМАТЕРІАЛ:\n===\n{ctx}\n===") if custom_sys else \
                f"""Ти — навчальний асистент KonspektAI. Відповідай ТІЛЬКИ на основі матеріалу нижче.
Якщо інформації немає в матеріалі — скажи: «Цієї інформації немає в матеріалі.»
Не вигадуй. Пояснюй зрозуміло. Структуруй відповідь якщо потрібно.
Відповідай тією ж мовою, якою поставлено питання.

МАТЕРІАЛ:
===
{ctx}
==="""
        else:
            system = custom_sys or "Ти — KonspektAI, навчальний асистент для студентів. Відповідай українською. Будь чітким і структурованим."

        api_messages = [{"role": "system", "content": system}]
        for m in st.session_state.messages[-20:]:
            if m["role"] in ("user", "assistant"):
                api_messages.append({"role": m["role"], "content": m["content"]})

        with st.chat_message("assistant"):
            with st.spinner("Думаю..."):
                try:
                    resp = client.chat.completions.create(
                        model=st.session_state.model,
                        messages=api_messages,
                        temperature=st.session_state.temperature,
                        max_tokens=st.session_state.max_tokens
                    )
                    answer = resp.choices[0].message.content
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    err = f"Сервер тимчасово недоступний. Спробуй за хвилину.\n\n_{str(e)[:120]}_"
                    st.markdown(err)
                    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                        st.session_state.messages.pop()


# ══════════════════════════════════════
#  PAGE: KONSPEKT
# ══════════════════════════════════════
def page_konspekt():
    render_header("Мій ", "Конспект", "ПЕРЕГЛЯД ЗАВАНТАЖЕНОГО МАТЕРІАЛУ")

    if not st.session_state.knowledge_base:
        st.markdown("""
        <div class="empty-wrap">
          <div class="empty-icon">K</div>
          <div class="empty-title">Конспект не завантажено</div>
          <div class="empty-body">Завантаж PDF у боковому меню — і тут з'явиться його зміст для перегляду і пошуку.</div>
        </div>""", unsafe_allow_html=True)
        return

    kb = st.session_state.knowledge_base
    c1, c2, c3, c4 = st.columns(4)
    cols_data = [
        ("Файл", st.session_state.file_name[:16] + ("..." if len(st.session_state.file_name) > 16 else "")),
        ("Сторінок", str(st.session_state.page_count)),
        ("Символів", f"{len(kb):,}"),
        ("Слів", f"{len(kb.split()):,}"),
    ]
    for col, (lbl, val) in zip([c1, c2, c3, c4], cols_data):
        col.markdown(f"""
        <div class="konspekt-stat">
          <span class="konspekt-stat-label">{lbl}</span>
          <div class="konspekt-stat-val">{val}</div>
        </div>""", unsafe_allow_html=True)

    search_query = st.text_input("Пошук у конспекті", placeholder="Введи слово або фразу...", label_visibility="collapsed")

    if search_query.strip():
        count = kb.lower().count(search_query.lower())
        if count > 0:
            st.markdown(f'<div class="alert alert-nfo">Знайдено <b>{count}</b> збігів для «{search_query}»</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert alert-warn">«{search_query}» не знайдено в конспекті</div>', unsafe_allow_html=True)

    st.text_area("Конспект", value=kb, height=500, label_visibility="collapsed")

    st.markdown('<br><div class="btn-accent">', unsafe_allow_html=True)
    if st.button("Згенерувати квіз по цьому матеріалу", use_container_width=True):
        st.session_state.page = "quiz"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════
#  PAGE: QUIZ
# ══════════════════════════════════════
def page_quiz():
    render_header("Квіз-", "Режим", "САМОПЕРЕВІРКА ЗНАНЬ")

    if not st.session_state.knowledge_base:
        st.markdown("""
        <div class="empty-wrap">
          <div class="empty-icon">K</div>
          <div class="empty-title">Спочатку завантаж конспект</div>
          <div class="empty-body">Квіз генерується на основі твого PDF. Завантаж файл у боковому меню ліворуч.</div>
        </div>""", unsafe_allow_html=True)
        return

    if not st.session_state.quiz_questions:
        st.markdown("""
        <div class="card card-accent" style="margin-bottom:1.5rem;">
          <div class="card-title">Генератор квізу</div>
          <div class="card-sub">AI створить питання на основі твого конспекту. Вибери кількість і натисни «Генерувати».</div>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns([2, 1])
        with c1:
            num_q = st.slider("Кількість питань", 3, 10, 5)
        with c2:
            diff = st.selectbox("Складність", ["Легка", "Середня", "Важка"], index=1)

        st.markdown('<div class="btn-accent" style="margin-top:0.5rem">', unsafe_allow_html=True)
        gen_btn = st.button("Генерувати квіз", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if gen_btn:
            ctx = st.session_state.knowledge_base[:6000]
            diff_map = {
                "Легка":   "прості, на запам'ятовування фактів",
                "Середня": "на розуміння та застосування",
                "Важка":   "аналітичні, вимагають глибокого розуміння"
            }
            with st.spinner(f"Генерую {num_q} питань..."):
                try:
                    r = client.chat.completions.create(
                        model=st.session_state.model,
                        messages=[{"role": "user", "content":
                            f"""Створи рівно {num_q} навчальних питань ({diff_map[diff]}) на основі матеріалу.
Правила: питання різноманітні, кожне з нового рядка, без нумерації, без пояснень.
МАТЕРІАЛ:\n===\n{ctx}\n===\nВиведи ТІЛЬКИ {num_q} питань:"""}],
                        max_tokens=800, temperature=0.6
                    )
                    raw = r.choices[0].message.content.strip()
                    qs = [q.strip().lstrip("0123456789.-) ") for q in raw.split("\n") if q.strip() and "?" in q]
                    qs = qs[:num_q]
                    if not qs:
                        st.markdown('<div class="alert alert-err">Не вдалося згенерувати питання. Спробуй ще раз.</div>', unsafe_allow_html=True)
                        return
                    st.session_state.quiz_questions = qs
                    st.session_state.quiz_answers   = [""] * len(qs)
                    st.session_state.quiz_revealed   = [False] * len(qs)
                    st.session_state.quiz_ai_answers = [""] * len(qs)
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="alert alert-err">Помилка: {str(e)[:120]}</div>', unsafe_allow_html=True)
        return

    questions = st.session_state.quiz_questions
    answered  = sum(1 for a in st.session_state.quiz_answers if a.strip())
    pct_done  = int(answered / len(questions) * 100)

    st.markdown(f"""
    <div class="progress-wrap">
      <div class="progress-top">
        <span class="progress-label">Прогрес</span>
        <span class="progress-count">{answered}/{len(questions)} відповіли</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width:{pct_done}%"></div>
      </div>
    </div>""", unsafe_allow_html=True)

    for i, q in enumerate(questions):
        revealed_i = st.session_state.quiz_revealed[i]
        ai_ans     = st.session_state.quiz_ai_answers[i]

        st.markdown(f"""
        <div class="quiz-question">
          <div class="quiz-q-num">Питання {i+1} / {len(questions)}</div>
          <div class="quiz-q-text">{q}</div>
        </div>""", unsafe_allow_html=True)

        user_ans = st.text_area(
            f"Відповідь {i+1}",
            value=st.session_state.quiz_answers[i],
            placeholder="Введи свою відповідь тут...",
            height=90,
            label_visibility="collapsed",
            key=f"qa_{i}",
            disabled=revealed_i
        )
        st.session_state.quiz_answers[i] = user_ans

        if not revealed_i:
            st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
            if st.button(f"Перевірити відповідь {i+1}", key=f"check_{i}", use_container_width=True):
                if not user_ans.strip():
                    st.markdown('<div class="alert alert-warn">Спочатку введи відповідь</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Перевіряю..."):
                        try:
                            ctx = st.session_state.knowledge_base[:5000]
                            r = client.chat.completions.create(
                                model=st.session_state.model,
                                messages=[{"role": "user", "content":
                                    f"""На основі матеріалу оціни відповідь студента в 1-2 речення.
Якщо правильно — почни з "Правильно!" і коротко поясни. Якщо ні — почни з "Не зовсім." і дай правильну відповідь.
МАТЕРІАЛ:\n===\n{ctx}\n===\nПитання: {q}\nВідповідь студента: {user_ans.strip()}\nОцінка:"""}],
                                max_tokens=250, temperature=0.2
                            )
                            st.session_state.quiz_ai_answers[i] = r.choices[0].message.content
                            st.session_state.quiz_revealed[i]   = True
                            st.rerun()
                        except Exception as e:
                            st.markdown(f'<div class="alert alert-err">Помилка: {str(e)[:80]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if revealed_i and ai_ans:
            css_extra = "quiz-answer-correct" if "Правильно" in ai_ans else ""
            st.markdown(f'<div class="quiz-answer-box {css_extra}">{ai_ans}</div>', unsafe_allow_html=True)

        st.markdown('<div style="margin-bottom:1rem"></div>', unsafe_allow_html=True)

    if all(st.session_state.quiz_revealed):
        correct = sum(1 for a in st.session_state.quiz_ai_answers if "Правильно" in a)
        total   = len(questions)
        score   = int(correct / total * 100)
        comment = "Чудово! Матеріал засвоєно відмінно!" if score >= 80 else \
                  "Непогано! Ще трохи повторення." if score >= 50 else \
                  "Варто ще раз перечитати матеріал."
        st.markdown(f"""
        <div class="quiz-score">
          <div class="quiz-score-num">{score}%</div>
          <div class="quiz-score-label">Правильних: {correct} / {total}</div>
          <div style="margin-top:0.75rem;font-size:0.9rem;color:#2A2622;font-family:'Plus Jakarta Sans',sans-serif;">{comment}</div>
        </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="btn-accent">', unsafe_allow_html=True)
        if st.button("Новий квіз", use_container_width=True, key="new_quiz"):
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers   = []
            st.session_state.quiz_revealed   = []
            st.session_state.quiz_ai_answers = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("До чату", use_container_width=True, key="quiz_to_chat"):
            st.session_state.page = "chat"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════
#  PAGE: SETTINGS
# ══════════════════════════════════════
def page_settings():
    render_header("Нала-", "штування", "КОНФІГУРАЦІЯ СИСТЕМИ")

    st.markdown("""
    <div class="card card-accent" style="margin-bottom:1.5rem;">
      <div class="card-title">Що тут можна змінити?</div>
      <div class="card-sub">Temperature — творчість відповідей. Max Tokens — довжина відповіді. Chunk Size — скільки символів PDF передається моделі. Системний промпт — додаткові інструкції для бота.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="settings-section-title">Temperature</div>', unsafe_allow_html=True)
    st.markdown('<span class="settings-caption">0.0 = суворі факти · 1.0 = дуже творчо · Рекомендується 0.2–0.4 для навчання</span>', unsafe_allow_html=True)
    temp = st.slider("Temperature", 0.0, 1.0, float(st.session_state.temperature), 0.05,
                     label_visibility="collapsed", format="%.2f")
    st.session_state.temperature = temp

    c1, c2, c3 = st.columns(3)
    for col, lbl, val in zip([c1, c2, c3],
        ["Фактичний (0.2)", "Збалансований (0.4)", "Творчий (0.7)"],
        [0.2, 0.4, 0.7]):
        col.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if col.button(lbl, use_container_width=True, key=f"t{val}"):
            st.session_state.temperature = val
            st.rerun()
        col.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<br><div class="settings-section-title">Max Tokens</div>', unsafe_allow_html=True)
    st.markdown('<span class="settings-caption">500 = короткі відповіді · 3000 = детальні</span>', unsafe_allow_html=True)
    st.session_state.max_tokens = st.slider("Max Tokens", 200, 3000, int(st.session_state.max_tokens), 100,
                                             label_visibility="collapsed")

    st.markdown('<br><div class="settings-section-title">Chunk Size (символів PDF)</div>', unsafe_allow_html=True)
    st.markdown('<span class="settings-caption">Скільки символів PDF передавати моделі. Більше = точніше, але повільніше.</span>', unsafe_allow_html=True)
    st.session_state.chunk_size = st.slider("Chunk Size", 2000, 30000, int(st.session_state.chunk_size), 1000,
                                             label_visibility="collapsed", format="%d симв.")

    st.markdown('<br><div class="settings-section-title">Кастомний системний промпт</div>', unsafe_allow_html=True)
    st.markdown('<span class="settings-caption">Порожньо = стандартний промпт KonspektAI</span>', unsafe_allow_html=True)
    st.session_state.system_prompt = st.text_area(
        "System prompt",
        value=st.session_state.system_prompt,
        placeholder="Наприклад: Ти суворий викладач. Відповідай коротко...",
        height=120, label_visibility="collapsed"
    )

    st.markdown("<br>")
    st.markdown("---")

    st.markdown('<div class="settings-section-title" style="margin-bottom:0.75rem">Поточна конфігурація</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, lbl, val in zip([c1, c2, c3],
        ["Temperature", "Max Tokens", "Chunk Size"],
        [st.session_state.temperature, st.session_state.max_tokens, f"{st.session_state.chunk_size:,}"]):
        col.markdown(f"""
        <div class="stat-mini">
          <span class="stat-mini-label">{lbl}</span>
          <div class="stat-mini-val">{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    st.markdown("---")

    st.markdown('<div class="settings-section-title" style="margin-bottom:0.75rem">Відповідність вимогам проєкту</div>', unsafe_allow_html=True)
    checks = [
        "RAG-паттерн (база знань з PDF)",
        "Groq API інтеграція (LLM)",
        "Графічний інтерфейс (Streamlit)",
        "Валідація вхідних даних (довжина, тип файлу)",
        "Обробка помилок (try-except + повідомлення)",
        "Захист API ключів (.env, не в коді)",
        "Очищення контексту (Новий чат / Скинути)",
        "Ізоляція інструкцій від даних (=== роздільники)",
        "Квіз-режим з AI-перевіркою відповідей",
        "Мультисторінковий інтерфейс (4 розділи)",
        "Налаштування моделі (temperature, max_tokens, chunk)",
        "Кастомний системний промпт",
        "Статистика сесії (повідомлення, сторінки, символи)",
    ]
    for label in checks:
        st.markdown(f"""
        <div class="check-row">
          <span style="color:#15803D;font-weight:700;font-size:0.9rem;">+</span>
          <span class="check-row-label">{label}</span>
          <span class="tag tag-green">реалізовано</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
    if st.button("Скинути до стандартних налаштувань", use_container_width=True):
        st.session_state.temperature  = 0.35
        st.session_state.max_tokens   = 1800
        st.session_state.chunk_size   = 14000
        st.session_state.system_prompt = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════
page_map = {
    "chat":      page_chat,
    "konspekt":  page_konspekt,
    "quiz":      page_quiz,
    "settings":  page_settings,
}
page_map.get(st.session_state.page, page_chat)()

st.markdown('<div class="app-footer">KonspektAI · RAG асистент · 2026 · @FEDORONKO</div>', unsafe_allow_html=True)