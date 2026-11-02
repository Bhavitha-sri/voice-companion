import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GNANI_API_KEY")
STT_URL = "https://api.vachana.ai/stt/v3"


def transcribe(audio, language_code="indic-auto", fmt="codemix"):
    """audio = path to a file (str) or raw bytes. Returns (text, detected_language)."""
    if isinstance(audio, str):
        with open(audio, "rb") as f:
            audio = f.read()

    response = requests.post(
        STT_URL,
        headers={"X-API-Key-ID": API_KEY},
        files={"audio_file": ("audio.wav", audio, "audio/wav")},
        data={"model": "prisma-v3.0", "language_code": language_code, "format": fmt},
        timeout=60,
    )
    body = response.json()
    if response.status_code != 200:
        raise RuntimeError(f"STT error {response.status_code}: {body}")
    return body.get("transcript", ""), body.get("detected_language_code")


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "hello.wav"
    text, lang = transcribe(path)
    print("Transcript:", text)
    print("Detected language:", lang)