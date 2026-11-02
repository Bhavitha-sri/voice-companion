# Voice Companion

A voice-first companion for people who cannot type or find the words to explain what they feel or need. Speak in Telugu, Hindi, English or a mix, and get a spoken reply.

## Modes
- **Listener**: for stress and overthinking. Validates feelings first, then gently guides.
- **Study buddy**: explains topics simply and checks understanding.
- **Farm helper**: asks simple follow-up questions, then gives practical advice.
- **All-time helper**: finds out what the person needs and helps.

## How it works
Voice in, Gnani speech-to-text, Gemini (with a mode-specific prompt), safety check, Gnani text-to-speech, voice out.

## Safety
- Every message is checked for self-harm signals; if found, the app shows a caring message with a helpline instead of a normal reply.
- It is a supportive companion, not a replacement for doctors, therapists or counsellors.
- Conversations are not stored by this app.

## Run it
```
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Create a `.env` file with GNANI_API_KEY, LLM_API_KEY, LLM_MODEL and LLM_FALLBACK (your own keys), then:
```
streamlit run app.py
```

## Built with
Gnani Prisma (speech-to-text), Gnani Timbre (text-to-speech), Google Gemini, Streamlit.
