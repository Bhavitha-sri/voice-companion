
import hashlib
import time
import streamlit as st
import streamlit.components.v1 as components

from stt import transcribe
from tts import speak
from llm import chat
from safety import is_crisis, crisis_message


# --------------------------------------------------
# Streamlit browser component
# --------------------------------------------------

wake_listener = components.declare_component(
    "bhavi_wake_listener",
    path="wake_component",
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Bhavi Voice Companion",
    page_icon="🎙️",
    layout="centered",
)


# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            160deg, #f4f1ff 0%, #eaf6ff 55%, #fff6ee 100%
        );
    }

    .hero {
        padding: 28px 26px;
        border-radius: 22px;
        color: white;
        background: linear-gradient(
            135deg, #6a4cff 0%, #3b82f6 60%, #14b8a6 100%
        );
        box-shadow: 0 10px 30px rgba(80, 70, 200, 0.25);
        margin-bottom: 18px;
    }

    .hero h1 {
        margin: 0;
        font-size: 2rem;
        color: white;
    }

    .hero p {
        margin: 8px 0 0 0;
        font-size: 1.05rem;
    }

    .hint {
        font-size: 0.92rem;
        color: #5b5b7a;
        margin: 4px 0 10px 0;
    }

    .footer {
        text-align: center;
        color: #7a7a99;
        font-size: 0.85rem;
        margin-top: 28px;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.75);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Modes
# --------------------------------------------------

MODE_INFO = {
    "auto": (
        "✨",
        "Automatic",
        "Talk naturally. Your companion will adapt to your needs.",
    ),
    "listener": (
        "💬",
        "Listener",
        "Talk about your feelings. Your companion will listen.",
    ),
    "study": (
        "📚",
        "Study buddy",
        "Learn topics and prepare for exams.",
    ),
    "farmer": (
        "🌾",
        "Farm helper",
        "Ask farming and crop-related questions.",
    ),
    "helper": (
        "🤝",
        "Everyday helper",
        "Get help with everyday questions and tasks.",
    ),
}

SUPPORTED_LANGUAGES = [
    "te-IN",
    "en-IN",
    "hi-IN",
    "ta-IN",
    "kn-IN",
    "ml-IN",
    "mr-IN",
    "bn-IN",
    "gu-IN",
    "pa-IN",
]

LANG_SHORT = {
    "te-IN": "te",
    "hi-IN": "hi",
    "en-IN": "en",
    "te": "te",
    "hi": "hi",
    "en": "en",
}


# --------------------------------------------------
# Session state
# --------------------------------------------------

defaults = {
    "history": [],
    "last_hash": None,
    "last_wake_id": None,
    "reply_audio": None,
    "selected_mode": "auto",
    "processing": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# Shared request-processing function
# --------------------------------------------------

def process_user_text(text, detected_lang="en-IN"):
    """Process text from either the microphone or wake listener."""

    text = (text or "").strip()

    if not text:
        st.warning("I could not understand that request. Please try again.")
        return

    detected_lang = detected_lang or "en-IN"
    short_lang = LANG_SHORT.get(detected_lang, "en")

    # Avoid overlapping processing during a rerun.
    if st.session_state.processing:
        return

    st.session_state.processing = True

    try:
        with st.spinner("Bhavi is thinking..."):
            if is_crisis(text):
                reply = crisis_message(short_lang)
                crisis = True

            else:
                mode = st.session_state.selected_mode

                # Automatic currently uses the adaptive helper prompt.
                # Dedicated automatic role classification is a future step.
                selected_mode = "helper" if mode == "auto" else mode

                reply, flagged = chat(
                    selected_mode,
                    [
                        {
                            "role": item["role"],
                            "text": item["text"],
                        }
                        for item in st.session_state.history[-12:]
                    ],
                    text,
                )

                crisis = bool(flagged)

                if crisis:
                    reply = (
                        reply.rstrip()
                        + " "
                        + crisis_message(short_lang)
                    )

        st.session_state.history.append(
            {
                "role": "user",
                "text": text,
                "lang": detected_lang,
            }
        )

        st.session_state.history.append(
            {
                "role": "model",
                "text": reply,
                "crisis": crisis,
            }
        )

        with st.spinner("Bhavi is preparing a spoken reply..."):
            try:
                st.session_state.reply_audio = speak(
                    reply,
                    language="auto",
                )
            except Exception as error:
                st.session_state.reply_audio = None
                st.warning(
                    "The text reply is ready, but speech generation "
                    f"failed: {type(error).__name__}: {error}"
                )

    except Exception as error:
        st.error(
            "Bhavi could not process the request. "
            f"Technical detail: {type(error).__name__}: {error}"
        )

    finally:
        st.session_state.processing = False


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.header("Settings")

    langs = st.multiselect(
        "Languages you may speak",
        SUPPORTED_LANGUAGES,
        default=["te-IN", "en-IN", "hi-IN"],
        max_selections=4,
    )

    if st.button("🔄 Start a new conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.last_hash = None
        st.session_state.last_wake_id = None
        st.session_state.reply_audio = None
        st.rerun()

    st.divider()

    st.info(
        "If you may harm yourself or are in immediate danger, "
        "contact someone you trust. In India, call Tele-MANAS "
        "at 14416 for mental health support or 112 for emergencies."
    )

    st.caption(
        "Conversation history stays in the current Streamlit session. "
        "This app does not intentionally save it to a database."
    )


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🎙️ Bhavi Voice Companion</h1>
        <p>
            Your voice-first AI companion for learning,
            listening, farming questions, and everyday help.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Mode selection
# --------------------------------------------------

mode = st.radio(
    "What do you need right now?",
    list(MODE_INFO.keys()),
    index=list(MODE_INFO.keys()).index(
        st.session_state.selected_mode
    ),
    format_func=lambda key: (
        f"{MODE_INFO[key][0]} {MODE_INFO[key][1]}"
    ),
    horizontal=True,
)

st.session_state.selected_mode = mode

st.markdown(
    f'<div class="hint">{MODE_INFO[mode][2]}</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Wake-word listener
# --------------------------------------------------

st.subheader("🎧 Hands-free voice activation")

st.write(
    'Allow microphone access, press "Start voice activation" '
    "inside the listener, then say “Bhavi” or “Hey Bhavi”."
)

wake_result = wake_listener(
    key="bhavi_wake_listener",
    default=None,
)

# The HTML component returns a dictionary when it hears a request.
if isinstance(wake_result, dict):
    if wake_result.get("type") == "BHAVI_COMMAND":
        wake_id = wake_result.get("time")
        wake_text = str(wake_result.get("text", "")).strip()

        if (
            wake_text
            and wake_id is not None
            and wake_id != st.session_state.last_wake_id
        ):
            st.session_state.last_wake_id = wake_id

            # Browser speech recognition is configured for English.
            # Telugu and other languages still use the recording/STT path.
            process_user_text(
                wake_text,
                detected_lang="en-IN",
            )


# --------------------------------------------------
# Existing microphone-button option
# --------------------------------------------------

with st.container(border=True):
    st.markdown("**🎤 Or tap the microphone to record a request.**")

    audio = st.audio_input(
        "Your voice",
        label_visibility="collapsed",
    )

if audio is not None:
    audio_data = audio.getvalue()
    digest = hashlib.sha256(audio_data).hexdigest()

    if digest != st.session_state.last_hash:
        st.session_state.last_hash = digest

        try:
            with st.spinner("Listening to your recording..."):
                text, detected_lang = transcribe(
                    audio_data,
                    language_code="indic-auto",
                )

            if not text or not text.strip():
                st.warning(
                    "I could not understand the recording. "
                    "Please speak clearly and try again."
                )
                st.session_state.last_hash = None

            else:
                process_user_text(
                    text,
                    detected_lang or "en-IN",
                )

        except Exception as error:
            st.session_state.last_hash = None
            st.error(
                "The recording could not be processed. "
                f"Technical detail: {type(error).__name__}: {error}"
            )


# --------------------------------------------------
# Conversation history
# --------------------------------------------------

st.divider()
st.subheader("Conversation")

if not st.session_state.history:
    st.markdown(
        '<div class="hint">Your conversation will appear here.</div>',
        unsafe_allow_html=True,
    )

for turn in st.session_state.history:
    if turn["role"] == "user":
        with st.chat_message("user"):
            st.write(turn["text"])

            if turn.get("lang"):
                st.caption(
                    f"Detected language: {turn['lang']}"
                )

    else:
        with st.chat_message("assistant", avatar="🎙️"):
            if turn.get("crisis"):
                st.warning(turn["text"])
            else:
                st.write(turn["text"])


# --------------------------------------------------
# Spoken response
# --------------------------------------------------

reply_audio = st.session_state.get("reply_audio")

if reply_audio:
    st.markdown("**🔊 Listen to Bhavi's response**")
    st.audio(
        reply_audio,
        format="audio/wav",
        autoplay=True,
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        Bhavi Voice Companion is an AI assistant, not a replacement
        for emergency services, doctors, or counsellors.
        Built with Gnani speech APIs and Gemini.
    </div>
    """,
    unsafe_allow_html=True,
)
