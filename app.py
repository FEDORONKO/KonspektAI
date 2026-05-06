import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from PyPDF2 import PdfReader
from io import BytesIO

load_dotenv(override=True)

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

.stApp {
    background: #EDEAE3 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; height: 2.5rem !important; }

/* ── HIDE DEPLOY BUTTON ── */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton,
button[kind="header"],
[data-testid="stAppViewBlockContainer"] > div:first-child > div:first-child > div > div > div > div > div[data-testid="stToolbar"] {
    display: none !important;
    visibility: hidden !important;
}

/* ── STATIC SIDEBAR (never collapses) ── */
[data-testid="stSidebar"] {
    background: #1C1917 !important;
    border-right: none !important;
    min-width: 270px !important;
    max-width: 270px !important;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    height: 100vh !important;
    overflow-y: auto !important;
    z-index: 999 !important;
    transform: none !important;
    transition: none !important;
}

/* Hide the sidebar collapse arrow button */
[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"],
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* Push main content to account for fixed sidebar */
.stMain, section.main {
    margin-left: 270px !important;
}

.block-container { 
    max-width: 760px !important; 
    width: 100% !important;
    padding: 0.5rem 2.5rem 3rem !important;
    margin-left: auto !important;
    margin-right: auto !important;
    position: relative !important;
    left: -135px !important;
}

[data-testid="stSidebar"] section[data-testid="stSidebarContent"] { padding: 0 !important; }
[data-testid="stSidebar"] * { box-sizing: border-box !important; }

[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #292524 !important;
    border: 1.5px dashed #44403C !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] * { color: #A39F9B !important; font-size: 0.78rem !important; }

[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #292524 !important; border: 1px solid #3C3835 !important;
    border-radius: 8px !important; color: #D6D3D1 !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] span,
[data-testid="stSidebar"] [data-testid="stSelectbox"] p { color: #D6D3D1 !important; font-size: 0.82rem !important; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg { fill: #A39F9B !important; }

[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; color: #A39F9B !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 500 !important; font-size: 0.85rem !important;
    padding: 0.6rem 0.75rem !important; width: 100% !important;
    text-align: left !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #292524 !important; color: #FFFFFF !important;
    transform: none !important; box-shadow: none !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: #FFFFFF !important; border: 1.5px solid #E2DED8 !important;
    border-radius: 16px !important; margin-bottom: 10px !important;
    padding: 1.1rem 1.4rem !important; box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] .stMarkdown p,
[data-testid="stChatMessage"] .stMarkdown span,
[data-testid="stChatMessage"] .stMarkdown li,
[data-testid="stChatMessage"] .stMarkdown strong,
[data-testid="stChatMessage"] .stMarkdown em {
    color: #1C1917 !important; font-size: 0.94rem !important; line-height: 1.75 !important;
}
[data-testid="stChatMessage"] .stMarkdown h1,
[data-testid="stChatMessage"] .stMarkdown h2,
[data-testid="stChatMessage"] .stMarkdown h3 { color: #1C1917 !important; font-weight: 800 !important; }
[data-testid="stChatMessage"] .stMarkdown code {
    background: #F5F2EE !important; border: 1px solid #D4CFC9 !important;
    color: #FF5C35 !important; padding: 2px 6px !important; border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 0.82em !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #1C1917 !important; border-color: #1C1917 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown span,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown li,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown strong {
    color: #FFFFFF !important;
}
[data-testid="chatAvatarIcon-user"] { background: #FF5C35 !important; border-radius: 10px !important; }
[data-testid="chatAvatarIcon-assistant"] { background: #FFFFFF !important; border: 2px solid #D4CFC9 !important; border-radius: 10px !important; }

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    background: #FFFFFF !important; border: 2px solid #D4CFC9 !important;
    border-radius: 14px !important; box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    max-width: calc(100vw - 270px) !important;
    box-sizing: border-box !important;
}
[data-testid="stBottomBlockContainer"] {
    box-sizing: border-box !important;
    position: fixed !important;
    bottom: 0 !important;
    left: 270px !important;
    width: calc(100vw - 270px) !important;
    padding: 1rem 2.5rem 1.5rem !important;
    display: flex !important;
    justify-content: center !important;
}
[data-testid="stBottomBlockContainer"] > div {
    width: 100% !important;
    max-width: 760px !important;
}
[data-testid="stChatInput"]:focus-within { border-color: #FF5C35 !important; }
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important; border: none !important; outline: none !important;
    box-shadow: none !important; color: #1C1917 !important; caret-color: #1C1917 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 0.92rem !important;
    padding: 0.9rem 1.1rem !important;
    max-height: 120px !important;
    overflow-y: auto !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #8B8580 !important; }
[data-testid="stChatInput"] button { background: #1C1917 !important; border: none !important; border-radius: 10px !important; margin: 7px !important; }
[data-testid="stChatInput"] button svg { fill: #FFFFFF !important; }
[data-testid="stChatInput"] button:hover { background: #FF5C35 !important; }

/* ── MAIN BUTTONS ── */
.stButton > button {
    background: #1C1917 !important; color: #FFFFFF !important;
    border: 2px solid #1C1917 !important; border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important;
    font-size: 0.85rem !important; padding: 0.6rem 1.2rem !important;
    transition: all 0.15s !important; width: 100% !important;
}
.stButton > button:hover {
    background: #FF5C35 !important; border-color: #FF5C35 !important;
    color: #FFFFFF !important; transform: translateY(-1px) !important;
}

/* ── TEXT INPUTS ── */
[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important; border: 1.5px solid #D4CFC9 !important;
    border-radius: 12px !important; color: #1C1917 !important; caret-color: #1C1917 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 0.88rem !important; line-height: 1.65 !important;
}
[data-testid="stTextArea"] textarea:focus { border-color: #FF5C35 !important; outline: none !important; box-shadow: none !important; }
[data-testid="stTextArea"] textarea::placeholder { color: #8B8580 !important; }

[data-testid="stSelectbox"] > div > div { background: #FFFFFF !important; border: 1.5px solid #D4CFC9 !important; border-radius: 10px !important; color: #1C1917 !important; }
[data-testid="stSelectbox"] span { color: #1C1917 !important; }
[data-testid="stSlider"] p, [data-testid="stSlider"] span, [data-testid="stSlider"] div { color: #1C1917 !important; }
.stSpinner > div { border-top-color: #FF5C35 !important; }

/* ── PAGE COMPONENTS ── */
.page-header { padding: 1.75rem 0 1.25rem; border-bottom: 2px solid #1C1917; margin-bottom: 2rem; display: flex; align-items: flex-end; justify-content: space-between; }
.page-title { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 2rem; color: #1C1917; letter-spacing: -1px; line-height: 1; }
.page-title-accent { color: #FF5C35; }
.page-subtitle { font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; color: #5A5652; letter-spacing: 2px; text-transform: uppercase; margin-top: 6px; font-weight: 700; }
.mode-pill { display: inline-flex; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; letter-spacing: 1.5px; text-transform: uppercase; padding: 4px 12px; border-radius: 999px; font-weight: 700; border: 1.5px solid; }
.pill-pdf  { background:#FFF7ED; border-color:#FDBA74; color:#92400E; }
.pill-free { background:#EEF2FF; border-color:#A5B4FC; color:#1E40AF; }

.pdf-bar { background: #FFFFFF; border: 1.5px solid #D4CFC9; border-left: 4px solid #FF5C35; border-radius: 12px; padding: 0.85rem 1.1rem; margin-bottom: 1.25rem; }
.pdf-bar-title { font-weight: 700; font-size: 0.88rem; color: #1C1917; font-family: 'Plus Jakarta Sans', sans-serif; }
.pdf-bar-sub { font-family: 'JetBrains Mono', monospace; font-size: 0.63rem; color: #5A5652; margin-top: 3px; }

.empty-wrap { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; text-align: center; }
.empty-icon { width: 64px; height: 64px; background: #FFFFFF; border: 2px solid #D4CFC9; border-radius: 18px; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; margin-bottom: 1.25rem; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; color: #1C1917; }
.empty-title { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 1.3rem; color: #1C1917; letter-spacing: -0.5px; margin-bottom: 0.5rem; }
.empty-body { font-size: 0.86rem; color: #5A5652; line-height: 1.85; max-width: 340px; font-family: 'Plus Jakarta Sans', sans-serif; }
.empty-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin-top: 1.25rem; }

/* ── CLICKABLE CHIPS ── */
.chip-btn {
    background: #FFFFFF;
    border: 1.5px solid #D4CFC9;
    border-radius: 999px;
    padding: 0.35rem 0.85rem;
    font-size: 0.76rem;
    color: #5A5652;
    font-weight: 600;
    font-family: 'Plus Jakarta Sans', sans-serif;
    cursor: pointer;
    transition: all 0.15s ease;
    display: inline-block;
    text-decoration: none;
}
.chip-btn:hover {
    background: #1C1917;
    border-color: #1C1917;
    color: #FFFFFF;
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(0,0,0,0.15);
}

.card { background: #FFFFFF; border: 1.5px solid #D4CFC9; border-left: 4px solid #FF5C35; border-radius: 14px; padding: 1.25rem 1.4rem; margin-bottom: 1.25rem; }
.card-title { font-weight: 700; font-size: 0.95rem; color: #1C1917; margin-bottom: 0.35rem; font-family: 'Plus Jakarta Sans', sans-serif; }
.card-sub { font-size: 0.84rem; color: #5A5652; line-height: 1.65; font-family: 'Plus Jakarta Sans', sans-serif; }

.quiz-q { background: #FFFFFF; border: 1.5px solid #D4CFC9; border-radius: 14px; padding: 1.25rem 1.4rem; margin-bottom: 0.75rem; }
.quiz-q-num { font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #FF5C35; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.4rem; font-weight: 700; }
.quiz-q-text { font-weight: 700; font-size: 0.94rem; color: #1C1917; line-height: 1.5; font-family: 'Plus Jakarta Sans', sans-serif; }

.quiz-feedback { border-radius: 10px; padding: 0.75rem 1rem; font-size: 0.86rem; line-height: 1.65; margin-top: 0.5rem; font-weight: 500; font-family: 'Plus Jakarta Sans', sans-serif; border: 1.5px solid; }
.quiz-ok  { background:#F0FDF4; border-color:#BBF7D0; color:#15803D; }
.quiz-err { background:#FEF2F2; border-color:#FECACA; color:#991B1B; }

.quiz-score { background: #FFFFFF; border: 2px solid #1C1917; border-radius: 16px; padding: 2rem; text-align: center; margin-bottom: 1.5rem; }
.quiz-score-num { font-size: 3.5rem; font-weight: 800; color: #FF5C35; letter-spacing: -2px; font-family: 'Plus Jakarta Sans', sans-serif; line-height: 1; }
.quiz-score-lbl { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #5A5652; letter-spacing: 2px; text-transform: uppercase; margin-top: 6px; font-weight: 700; }
.quiz-score-comment { margin-top: 0.75rem; font-size: 0.9rem; color: #1C1917; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 600; }

.alert { padding: 0.75rem 1rem; border-radius: 10px; font-size: 0.84rem; line-height: 1.6; border: 1.5px solid; margin: 0.5rem 0; font-weight: 600; font-family: 'Plus Jakarta Sans', sans-serif; }
.alert-err  { background:#FEE2E2; border-color:#FECACA; color:#991B1B; }
.alert-warn { background:#FFFBEB; border-color:#FDE68A; color:#92400E; }

.progress-wrap { margin-bottom: 1.5rem; }
.progress-top { display: flex; justify-content: space-between; margin-bottom: 6px; }
.progress-label { font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #5A5652; text-transform: uppercase; letter-spacing: 1.5px; }
.progress-count { font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #FF5C35; font-weight: 700; }
.progress-track { background: #D4CFC9; border-radius: 999px; height: 5px; overflow: hidden; }
.progress-fill  { background: #FF5C35; height: 100%; border-radius: 999px; }

.app-footer { text-align: center; padding: 2.5rem 0 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #A39F9B; letter-spacing: 2px; text-transform: uppercase; font-weight: 700; }

/* Sidebar HTML */
.sb-logo-text { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 1.35rem; color: #FFFFFF; letter-spacing: -0.5px; line-height: 1; }
.sb-logo-dot  { color: #FF5C35; }
.sb-logo-sub  { font-family: 'JetBrains Mono', monospace; font-size: 0.52rem; color: #6B6460; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px; font-weight: 700; }
.sb-divider   { border: none; border-top: 1px solid #292524; margin: 0.75rem 0; }
.sb-label     { font-family: 'JetBrains Mono', monospace; font-size: 0.52rem; color: #6B6460; letter-spacing: 2px; text-transform: uppercase; font-weight: 700; margin-bottom: 0.6rem; display: block; }
.sb-nav-active { background: #FF5C35; color: #FFFFFF !important; font-weight: 700; border-radius: 8px; padding: 0.6rem 0.75rem; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.85rem; display: block; margin-bottom: 2px; }
.sb-file-card { background: #292524; border: 1px solid #3C3835; border-radius: 10px; padding: 0.7rem 0.9rem; margin-top: 0.5rem; }
.sb-file-badge { display: inline-block; background: rgba(22,163,74,0.12); color: #22C55E; border: 1px solid rgba(22,163,74,0.25); border-radius: 4px; padding: 2px 7px; font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; font-weight: 600; }
.sb-file-name { font-weight: 600; font-size: 0.82rem; color: #FFFFFF; margin-bottom: 3px; font-family: 'Plus Jakarta Sans', sans-serif; }
.sb-file-meta { font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #6B6460; }
.sb-model-row { background: #292524; border: 1px solid #3C3835; border-radius: 8px; padding: 0.5rem 0.75rem; display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem; }
.sb-model-dot { width: 6px; height: 6px; background: #FF5C35; border-radius: 50%; flex-shrink: 0; animation: pulse 2s infinite; }
.sb-model-name { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #6B6460; font-weight: 500; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.35} }
.sb-stat-row { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #252220; }
.sb-stat-row:last-child { border-bottom: none; }
.sb-stat-lbl { font-size: 0.76rem; color: #6B6460; font-family: 'Plus Jakarta Sans', sans-serif; }
.sb-stat-val { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #D6D3D1; font-weight: 600; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── API ──
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY не знайдено — додай у файл .env")
    st.stop()

client = Groq(api_key=api_key)

# ── CONSTANTS ──
TEMPERATURE = 0.35
MAX_TOKENS  = 1800
CHUNK_SIZE  = 14000

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
    "model": "llama-3.3-70b-versatile",
    "chip_prompt": "",   # NEW: stores chip text to auto-send
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:1.5rem 1rem 1rem">
      <div class="sb-logo-text">Konspekt<span class="sb-logo-dot">AI</span></div>
      <div class="sb-logo-sub">RAG навчальний асистент</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider" style="margin:0 1rem 0.75rem">', unsafe_allow_html=True)

    # Navigation
    st.markdown('<div style="padding:0 1rem">', unsafe_allow_html=True)
    st.markdown('<span class="sb-label">Навігація</span>', unsafe_allow_html=True)
    for key, label in [("chat", "Чат з асистентом"), ("quiz", "Квіз-режим")]:
        if st.session_state.page == key:
            st.markdown(f'<span class="sb-nav-active">{label}</span>', unsafe_allow_html=True)
        else:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider" style="margin:0.75rem 1rem">', unsafe_allow_html=True)

    # PDF
    st.markdown('<div style="padding:0 1rem">', unsafe_allow_html=True)
    st.markdown('<span class="sb-label">Конспект (PDF)</span>', unsafe_allow_html=True)
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
              <div class="sb-file-name">{name[:26]}{"..." if len(name)>26 else ""}</div>
              <div class="sb-file-meta">{st.session_state.page_count} стор. · {len(st.session_state.knowledge_base):,} симв.</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider" style="margin:0.75rem 1rem">', unsafe_allow_html=True)

    # Model
    st.markdown('<div style="padding:0 1rem">', unsafe_allow_html=True)
    st.markdown('<span class="sb-label">Модель</span>', unsafe_allow_html=True)
    model_list = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-groq-70b-8192-tool-use-preview"]
    idx = model_list.index(st.session_state.model) if st.session_state.model in model_list else 0
    st.session_state.model = st.selectbox("Модель", model_list, index=idx, label_visibility="collapsed")
    st.markdown(f'<div class="sb-model-row"><div class="sb-model-dot"></div><span class="sb-model-name">{st.session_state.model[:26]}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Stats
    if st.session_state.knowledge_base:
        st.markdown('<hr class="sb-divider" style="margin:0.75rem 1rem">', unsafe_allow_html=True)
        st.markdown('<div style="padding:0 1rem">', unsafe_allow_html=True)
        st.markdown('<span class="sb-label">Статистика</span>', unsafe_allow_html=True)
        msgs_u = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.markdown(f"""
        <div>
          <div class="sb-stat-row"><span class="sb-stat-lbl">Сторінок PDF</span><span class="sb-stat-val">{st.session_state.page_count}</span></div>
          <div class="sb-stat-row"><span class="sb-stat-lbl">Запитань</span><span class="sb-stat-val">{msgs_u}</span></div>
          <div class="sb-stat-row"><span class="sb-stat-lbl">Питань квізу</span><span class="sb-stat-val">{len(st.session_state.quiz_questions)}</span></div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider" style="margin:0.75rem 1rem">', unsafe_allow_html=True)

    # Actions
    st.markdown('<div style="padding:0 1rem 1rem">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Скинути все", use_container_width=True, key="reset_all"):
            for k in defaults:
                st.session_state[k] = defaults[k]
            st.rerun()
    with c2:
        if st.button("Новий чат", use_container_width=True, key="new_chat"):
            st.session_state.messages = []
            st.rerun()
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


# ── CHIP HELPER ──
# Renders clickable chips using Streamlit buttons styled as chips
def render_chips(chips: list[str], prefix: str = "chip"):
    """Render chips as real Streamlit buttons that trigger a rerun with the chip text."""
    cols = st.columns(len(chips))
    for i, (col, chip_text) in enumerate(zip(cols, chips)):
        with col:
            # Use a small styled button; CSS will be overridden per-chip via a wrapper trick
            if st.button(chip_text, key=f"{prefix}_{i}", use_container_width=False):
                st.session_state.chip_prompt = chip_text
                st.rerun()


# ══════════════════════════════════════
#  AI CALL HELPER
# ══════════════════════════════════════
def call_ai_and_render(question: str):
    """Add question to history, call Groq, stream answer, update history."""
    has_pdf = bool(st.session_state.knowledge_base)

    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    if has_pdf:
        ctx = st.session_state.knowledge_base[:CHUNK_SIZE]
        system = f"""Ти — навчальний асистент KonspektAI. Відповідай ТІЛЬКИ на основі матеріалу нижче.
Якщо інформації немає в матеріалі — скажи: «Цієї інформації немає в конспекті.»
Не вигадуй. Пояснюй зрозуміло. Структуруй відповідь якщо потрібно.
Відповідай тією ж мовою, якою поставлено питання.

МАТЕРІАЛ:
===
{ctx}
==="""
    else:
        system = "Ти — KonspektAI, навчальний асистент для студентів. Відповідай чітко і структуровано."

    api_messages = [{"role": "system", "content": system}]
    for m in st.session_state.messages[-20:]:
        if m["role"] in ("user", "assistant"):
            api_messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            import time
            answer = None
            last_err = None
            for attempt in range(3):
                try:
                    resp = client.chat.completions.create(
                        model=st.session_state.model,
                        messages=api_messages,
                        temperature=TEMPERATURE,
                        max_tokens=MAX_TOKENS
                    )
                    answer = resp.choices[0].message.content
                    break
                except Exception as e:
                    last_err = e
                    if "429" in str(e):
                        wait = 10 * (attempt + 1)
                        st.toast(f"\u23f3 Ліміт запитів. Чекаю {wait}с...", icon="\u26a0\ufe0f")
                        time.sleep(wait)
                    else:
                        break
            if answer:
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                is_429 = "429" in str(last_err)
                if is_429:
                    err = "\u26a0\ufe0f **Ліміт Groq вичерпано.** Безкоштовний план має ~30 запитів/хв. Зачекай хвилину або зміни модель на `llama3-8b-8192` — вона має вищий ліміт."
                else:
                    err = f"Сервер тимчасово недоступний.\n\n_{str(last_err)[:120]}_"
                st.markdown(err)
                if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                    st.session_state.messages.pop()


# ══════════════════════════════════════
#  PAGE: CHAT
# ══════════════════════════════════════
def page_chat():
    has_pdf = bool(st.session_state.knowledge_base)
    badge = '<span class="mode-pill pill-pdf">PDF режим</span>' if has_pdf \
            else '<span class="mode-pill pill-free">Вільний чат</span>'
    render_header("Konspekt", "AI",
                  "ВІДПОВІДІ НА ОСНОВІ КОНСПЕКТУ" if has_pdf else "AI-АСИСТЕНТ ДЛЯ НАВЧАННЯ",
                  badge)

    if has_pdf:
        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(f"""
            <div class="pdf-bar">
              <div class="pdf-bar-title">{st.session_state.file_name}</div>
              <div class="pdf-bar-sub">{st.session_state.page_count} стор. · {len(st.session_state.knowledge_base):,} символів · готово</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            if st.button("Квіз", use_container_width=True, key="go_quiz"):
                st.session_state.page = "quiz"
                st.rerun()

    # ── Check if a chip was clicked (chip_prompt set) ──
    pending_question = ""
    if st.session_state.chip_prompt:
        pending_question = st.session_state.chip_prompt
        st.session_state.chip_prompt = ""

    if not st.session_state.messages and not pending_question:
        if has_pdf:
            st.markdown("""
            <div class="empty-wrap">
              <div class="empty-icon">K</div>
              <div class="empty-title">Матеріал завантажено</div>
              <div class="empty-body">Задавай питання — відповіді виключно на основі твого конспекту. Або обери підказку нижче.</div>
            </div>""", unsafe_allow_html=True)
            render_chips(["Поясни цю тему", "Що таке...?", "Порівняй...", "Підсумуй розділ"], prefix="chip_pdf")
        else:
            st.markdown("""
            <div class="empty-wrap">
              <div class="empty-icon">K</div>
              <div class="empty-title">Привіт, я KonspektAI</div>
              <div class="empty-body">Завантаж PDF у боковому меню — і я відповідатиму виключно по твоєму матеріалу. Або обери приклад нижче.</div>
            </div>""", unsafe_allow_html=True)
            render_chips(
                ["Що таке фотосинтез?", "Поясни теорему Піфагора", "Як готуватись до іспиту?"],
                prefix="chip_free"
            )

    # Render existing messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input (always rendered so it never disappears)
    user_input = st.chat_input(
        "Задай питання по конспекту..." if has_pdf else "Напиши питання або тему..."
    )

    # Handle chip click OR manual input
    question = pending_question or (user_input.strip() if user_input and user_input.strip() else "")
    if question:
        if len(question) > 50000:
            st.markdown('<div class="alert alert-err">Запит занадто довгий (макс. 50 000 символів)</div>', unsafe_allow_html=True)
            return
        call_ai_and_render(question)


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
          <div class="empty-body">Квіз генерується автоматично на основі твого PDF. Завантаж файл у боковому меню.</div>
        </div>""", unsafe_allow_html=True)
        return

    if not st.session_state.quiz_questions:
        st.markdown("""
        <div class="card">
          <div class="card-title">Генератор квізу</div>
          <div class="card-sub">AI створить питання на основі твого конспекту. Обери кількість і складність.</div>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns([2, 1])
        with c1:
            num_q = st.slider("Кількість питань", 3, 10, 5)
        with c2:
            diff = st.selectbox("Складність", ["Легка", "Середня", "Важка"], index=1)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Генерувати квіз", use_container_width=True):
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
Кожне питання з нового рядка. Без нумерації. Без пояснень. Тільки питання.
МАТЕРІАЛ:\n===\n{ctx}\n===\nВиведи ТІЛЬКИ {num_q} питань:"""}],
                        max_tokens=600, temperature=0.6
                    )
                    raw = r.choices[0].message.content.strip()
                    qs = [q.strip().lstrip("0123456789.-) ") for q in raw.split("\n") if q.strip() and "?" in q]
                    qs = qs[:num_q]
                    if not qs:
                        st.markdown('<div class="alert alert-err">Не вдалося згенерувати питання. Спробуй ще раз.</div>', unsafe_allow_html=True)
                        return
                    st.session_state.quiz_questions  = qs
                    st.session_state.quiz_answers    = [""] * len(qs)
                    st.session_state.quiz_revealed   = [False] * len(qs)
                    st.session_state.quiz_ai_answers = [""] * len(qs)
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="alert alert-err">Помилка: {str(e)[:120]}</div>', unsafe_allow_html=True)
        return

    questions = st.session_state.quiz_questions
    answered  = sum(1 for a in st.session_state.quiz_answers if a.strip())
    pct       = int(answered / len(questions) * 100)

    st.markdown(f"""
    <div class="progress-wrap">
      <div class="progress-top">
        <span class="progress-label">Прогрес</span>
        <span class="progress-count">{answered} / {len(questions)}</span>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>
    </div>""", unsafe_allow_html=True)

    for i, q in enumerate(questions):
        revealed = st.session_state.quiz_revealed[i]
        ai_ans   = st.session_state.quiz_ai_answers[i]

        st.markdown(f"""
        <div class="quiz-q">
          <div class="quiz-q-num">Питання {i+1} / {len(questions)}</div>
          <div class="quiz-q-text">{q}</div>
        </div>""", unsafe_allow_html=True)

        user_ans = st.text_area(
            f"answer_{i}",
            value=st.session_state.quiz_answers[i],
            placeholder="Твоя відповідь...",
            height=88,
            label_visibility="collapsed",
            key=f"qa_{i}",
            disabled=revealed,
        )
        st.session_state.quiz_answers[i] = user_ans

        if not revealed:
            if st.button(f"Перевірити {i+1}", key=f"check_{i}", use_container_width=True):
                if not user_ans.strip():
                    st.markdown('<div class="alert alert-warn">Спочатку введи відповідь</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Перевіряю..."):
                        try:
                            ctx = st.session_state.knowledge_base[:5000]
                            r = client.chat.completions.create(
                                model=st.session_state.model,
                                messages=[{"role": "user", "content":
                                    f"""На основі матеріалу оціни відповідь студента (1-2 речення).
Якщо правильно — почни з "Правильно!" і поясни. Якщо ні — почни з "Не зовсім." і дай правильну відповідь.
МАТЕРІАЛ:\n===\n{ctx}\n===\nПитання: {q}\nВідповідь: {user_ans.strip()}\nОцінка:"""}],
                                max_tokens=220, temperature=0.2
                            )
                            st.session_state.quiz_ai_answers[i] = r.choices[0].message.content
                            st.session_state.quiz_revealed[i]   = True
                            st.rerun()
                        except Exception as e:
                            st.markdown(f'<div class="alert alert-err">Помилка: {str(e)[:80]}</div>', unsafe_allow_html=True)

        if revealed and ai_ans:
            css = "quiz-ok" if "Правильно" in ai_ans else "quiz-err"
            st.markdown(f'<div class="quiz-feedback {css}">{ai_ans}</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

    if all(st.session_state.quiz_revealed):
        correct = sum(1 for a in st.session_state.quiz_ai_answers if "Правильно" in a)
        total   = len(questions)
        score   = int(correct / total * 100)
        comment = "Відмінно! Матеріал засвоєно." if score >= 80 else \
                  "Непогано, ще трохи повторення." if score >= 50 else \
                  "Варто ще раз перечитати конспект."
        st.markdown(f"""
        <div class="quiz-score">
          <div class="quiz-score-num">{score}%</div>
          <div class="quiz-score-lbl">Правильних: {correct} / {total}</div>
          <div class="quiz-score-comment">{comment}</div>
        </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Новий квіз", use_container_width=True, key="new_quiz"):
            st.session_state.quiz_questions  = []
            st.session_state.quiz_answers    = []
            st.session_state.quiz_revealed   = []
            st.session_state.quiz_ai_answers = []
            st.rerun()
    with c2:
        if st.button("До чату", use_container_width=True, key="to_chat"):
            st.session_state.page = "chat"
            st.rerun()


# ══════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════
{"chat": page_chat, "quiz": page_quiz}.get(st.session_state.page, page_chat)()

st.markdown('<div class="app-footer">KonspektAI · RAG асистент · 2026 · @FEDORONKO</div>', unsafe_allow_html=True)
