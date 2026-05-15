from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="MoodBot", page_icon="🎭", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { max-width: 680px; padding-top: 2rem !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Mode cards ── */
.mode-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 1.5rem 0;
}
.mode-card {
    border-radius: 16px;
    padding: 1.4rem 1rem;
    text-align: center;
    cursor: pointer;
    border: 2px solid transparent;
    transition: transform .15s, box-shadow .15s;
    font-family: 'Syne', sans-serif;
}
.mode-card:hover { transform: translateY(-3px); }
.card-funny  { background: #fff9e6; border-color: #fcd34d; }
.card-sad    { background: #eff6ff; border-color: #93c5fd; }
.card-angry  { background: #fff1f2; border-color: #fca5a5; }
.card-funny.selected  { background: #fef08a; border-color: #eab308; box-shadow: 0 0 0 3px rgba(234,179,8,.25); }
.card-sad.selected    { background: #bfdbfe; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,.25); }
.card-angry.selected  { background: #fecaca; border-color: #ef4444; box-shadow: 0 0 0 3px rgba(239,68,68,.25); }
.card-emoji { font-size: 2.2rem; display: block; margin-bottom: .4rem; }
.card-label { font-size: .95rem; font-weight: 700; letter-spacing: -.3px; }
.card-funny  .card-label { color: #92400e; }
.card-sad    .card-label { color: #1e3a8a; }
.card-angry  .card-label { color: #991b1b; }
.card-desc { font-size: .72rem; color: #888; margin-top: .2rem; font-family: 'Inter', sans-serif; font-weight: 300; }

/* ── Start button ── */
.stButton > button {
    width: 100%;
    padding: .75rem !important;
    border-radius: 12px !important;
    border: none !important;
    font-family: 'Syne', sans-serif !important;
    font-size: .95rem !important;
    font-weight: 700 !important;
    letter-spacing: .3px;
    cursor: pointer;
    transition: opacity .2s, transform .1s !important;
}
.stButton > button:hover { opacity: .88 !important; transform: translateY(-1px) !important; }
.btn-funny > button  { background: linear-gradient(135deg,#f59e0b,#d97706) !important; color:#fff !important; }
.btn-sad   > button  { background: linear-gradient(135deg,#3b82f6,#2563eb) !important; color:#fff !important; }
.btn-angry > button  { background: linear-gradient(135deg,#ef4444,#dc2626) !important; color:#fff !important; }
.btn-default > button { background: linear-gradient(135deg,#6366f1,#4f46e5) !important; color:#fff !important; }

/* ── Badge ── */
.mode-badge {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .35rem .85rem;
    border-radius: 999px;
    font-size: .78rem;
    font-weight: 600;
    margin-bottom: 1rem;
    font-family: 'Syne', sans-serif;
}
.badge-funny { background:#fef9c3; color:#92400e; border:1px solid #fde68a; }
.badge-sad   { background:#dbeafe; color:#1e3a8a; border:1px solid #bfdbfe; }
.badge-angry { background:#fee2e2; color:#991b1b; border:1px solid #fecaca; }

/* ── Chat input accent per mode ── */
.stChatInput textarea { border-radius: 12px !important; }

/* ── Title ── */
.app-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -1.5px;
    text-align: center;
    margin-bottom: .2rem;
}
.app-sub { text-align: center; color: #999; font-size: .82rem; margin-bottom: .2rem; }
.divider { height:1px; background: linear-gradient(90deg,transparent,#e5e7eb,transparent); margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Initialize model (unchanged) ────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.9
    )

model = get_model()

# ── Mode config ──────────────────────────────────────────────────────────────────
MODES = {
    1: {
        "label": "Funny Mode",
        "emoji": "😂",
        "desc": "Laughs at everything",
        "system": "you are a funny AI assistant and reply every message in funny way .",
        "card": "funny",
        "badge": "badge-funny",
        "btn": "btn-funny",
    },
    2: {
        "label": "Sad Mode",
        "emoji": "😢",
        "desc": "Cries about everything",
        "system": "you are a sad AI assistant and reply every message in sad way .",
        "card": "sad",
        "badge": "badge-sad",
        "btn": "btn-sad",
    },
    3: {
        "label": "Angry Mode",
        "emoji": "😡",
        "desc": "Mad about everything",
        "system": "you are an angry AI assistant and reply every message in angry way .",
        "card": "angry",
        "badge": "badge-angry",
        "btn": "btn-angry",
    },
}

# ── Session state ────────────────────────────────────────────────────────────────
if "choice" not in st.session_state:
    st.session_state.choice = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected" not in st.session_state:
    st.session_state.selected = None

# ════════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — Mode selection (replaces the print + input() block)
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state.choice is None:

    st.markdown('<div class="app-title">🎭 MoodBot</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Choose a personality before we begin</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Render the 3 clickable cards
    cols = st.columns(3)
    for idx, (num, cfg) in enumerate(MODES.items()):
        with cols[idx]:
            selected_class = "selected" if st.session_state.selected == num else ""
            st.markdown(f"""
            <div class="mode-card card-{cfg['card']} {selected_class}">
                <span class="card-emoji">{cfg['emoji']}</span>
                <div class="card-label">{cfg['label']}</div>
                <div class="card-desc">{cfg['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select", key=f"pick_{num}", use_container_width=True):
                st.session_state.selected = num
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.selected:
        cfg = MODES[st.session_state.selected]
        st.markdown(f"""
        <div style="text-align:center; color:#555; font-size:.88rem; margin-bottom:.8rem;">
            {cfg['emoji']} <b>{cfg['label']}</b> selected — ready to chat!
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="{cfg["btn"]}">', unsafe_allow_html=True)
        if st.button("Start Chatting →", use_container_width=True):
            choice = st.session_state.selected

            # ── Same logic as your original if/elif block ──
            if choice == 1:
                mode = "you are a funny AI assistant and reply every message in funny way ."
            elif choice == 2:
                mode = "you are a sad AI assistant and reply every message in sad way ."
            elif choice == 3:
                mode = "you are an angry AI assistant and reply every message in angry way ."

            # ── Initialize messages (same as your original) ──
            st.session_state.messages = [
                SystemMessage(content=mode)
            ]
            st.session_state.choice = choice
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="btn-default">', unsafe_allow_html=True)
        st.button("Start Chatting →", disabled=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — Chat UI (replaces the while True loop)
# ════════════════════════════════════════════════════════════════════════════════
else:
    cfg = MODES[st.session_state.choice]

    # Header
    st.markdown('<div class="app-title">🎭 MoodBot</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:.5rem;">
        <span class="mode-badge {cfg['badge']}">{cfg['emoji']} {cfg['label']}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Display chat history (replaces print("Bot :", response.content))
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.write(msg.content)

    # Chat input (replaces prompt = input("You : "))
    prompt = st.chat_input("You : ")

    if prompt:
        st.session_state.messages.append(HumanMessage(content=prompt))

        with st.chat_message("user"):
            st.write(prompt)

        response = model.invoke(st.session_state.messages)

        st.session_state.messages.append(AIMessage(content=response.content))

        with st.chat_message("assistant"):
            st.write(response.content)

    # Change mode button (replaces TYPE 0 TO EXIT)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Change Mode"):
        st.session_state.choice = None
        st.session_state.selected = None
        st.session_state.messages = []
        st.rerun()