import hashlib
import streamlit as st

from stt import transcribe
from tts import speak
from llm import chat
from safety import is_crisis, crisis_message
from modes import MODES

st.set_page_config(page_title="Voice Companion", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
.stApp { background: linear-gradient(160deg, #f4f1ff 0%, #eaf6ff 55%, #fff6ee 100%); }
.hero { padding: 28px 26px; border-radius: 22px; color: #ffffff;
        background: linear-gradient(135deg, #6a4cff 0%, #3b82f6 60%, #14b8a6 100%);
        box-shadow: 0 10px 30px rgba(80, 70, 200, 0.25); margin-bottom: 18px; }
.hero h1 { margin: 0; font-size: 2.1rem; color: #ffffff; }
.hero p { margin: 8px 0 0 0; font-size: 1.05rem; opacity: 0.95; }
.hint { font-size: 0.92rem; color: #5b5b7a; margin: 4px 0 10px 0; }
.footer { text-align: center; color: #7a7a99; font-size: 0.85rem; margin-top: 28px; }
div[data-testid="stChatMessage"] { border-radius: 16px; background: rgba(255,255,255,0.75);
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
section[data-testid="stSidebar"] { background: #ffffffcc; }
</style>
""", unsafe_allow_html=True)

MODE_INFO = {
    "listener": ("💬", "Listener", "Feeling stressed or overthinking? Just talk. I will listen first."),
    "study":    ("📚", "Study buddy", "Ask any topic. I explain it simply and check your understanding."),
    "farmer":   ("🌾", "Farm helper", "Tell me about your crop. I ask simple questions, then help."),
    "helper":   ("🤝", "All-time helper", "Not sure what you need? Start talking and we will find out."),
}
LANG_SHORT = {"te-IN": "te", "hi-IN": "hi"}

if "history" not in st.session_state:
    st.session_state.history = []
if "last_hash" not in st.session_state:
    st.session_state.last_hash = None

# ---------- sidebar ----------
with st.sidebar:
    st.header("Settings")
    langs = st.multiselect(
        "Languages you may speak (max 4)",
        ["te-IN", "en-IN", "hi-IN", "ta-IN", "kn-IN", "ml-IN", "mr-IN", "bn-IN", "gu-IN", "pa-IN"],
        default=["te-IN", "en-IN", "hi-IN"],
        max_selections=4,
    )
    if st.button("🔄 Start a new conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.last_hash = None
        st.rerun()
    st.divider()
    st.info("If you are in danger or thinking of harming yourself, call Tele MANAS "
            "14416 or 112 right now.")
    st.caption("Your conversation stays only in this browser session. Nothing is saved by this app.")

# ---------- header ----------
st.markdown("""
<div class="hero">
  <h1>🎙️ Voice Companion</h1>
  <p>No typing needed. Speak in your own language and get a caring, spoken reply.</p>
</div>
""", unsafe_allow_html=True)

# ---------- mode ----------
mode = st.radio(
    "What do you need right now?",
    list(MODE_INFO.keys()),
    format_func=lambda k: f"{MODE_INFO[k][0]} {MODE_INFO[k][1]}",
    horizontal=True,
)
st.markdown(f'<div class="hint">{MODE_INFO[mode][2]}</div>', unsafe_allow_html=True)

# ---------- microphone ----------
with st.container(border=True):
    st.markdown("**🎤 Tap the mic, speak for a few seconds, then tap again to stop**")
    audio = st.audio_input("Your voice", label_visibility="collapsed")

if audio is not None:
    data = audio.getvalue()
    digest = hashlib.md5(data).hexdigest()
    if digest != st.session_state.last_hash:   # process each recording only once
        st.session_state.last_hash = digest
        try:
            with st.spinner("👂 Listening..."):
                text, lang = transcribe(data, language_code=",".join(langs) or "indic-auto")

            if not text.strip():
                st.warning("I could not hear anything. Please try again, a little closer to the mic.")
            else:
                short = LANG_SHORT.get(lang, "en")
                crisis = False
                with st.spinner("💭 Thinking..."):
                    if is_crisis(text):                          # safety layer 1
                        reply, crisis = crisis_message(short), True
                    else:
                        reply, flagged = chat(mode, st.session_state.history[-12:], text)
                        if flagged:                              # safety layer 2 (the AI)
                            reply, crisis = reply + " " + crisis_message(short), True

                st.session_state.history.append({"role": "user", "text": text, "lang": lang})
                st.session_state.history.append({"role": "model", "text": reply, "crisis": crisis})

                with st.spinner("🔊 Speaking..."):
                    st.session_state.reply_audio = speak(reply, "auto")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# ---------- conversation ----------
if not st.session_state.history:
    st.markdown('<div class="hint">Your conversation will appear here.</div>', unsafe_allow_html=True)

for turn in st.session_state.history:
    if turn["role"] == "user":
        with st.chat_message("user", avatar="🧑"):
            st.write(turn["text"])
            if turn.get("lang"):
                st.caption(f"Detected language: {turn['lang']}")
    else:
        with st.chat_message("assistant", avatar="🎙️"):
            if turn.get("crisis"):
                st.warning(turn["text"])
            else:
                st.write(turn["text"])

reply_audio = st.session_state.pop("reply_audio", None)
if reply_audio:
    st.audio(reply_audio, format="audio/wav", autoplay=True)

st.markdown('<div class="footer">A supportive companion, not a replacement for doctors or '
            'counsellors. Built with Gnani speech APIs and Gemini.</div>', unsafe_allow_html=True)