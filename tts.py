import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GNANI_API_KEY")
TTS_URL = "https://api.vachana.ai/api/v1/tts/inference"

# If timbre-v3.0 gives an error, switch to: MODEL = "timbre-v2.5" and VOICE = "Nalini"
MODEL = "timbre-v3.0"
VOICE = "Shivani"


def speak(text, language="auto", voice=VOICE, model=MODEL):
    """Turns text into speech. Returns WAV audio as bytes."""
    response = requests.post(
        TTS_URL,
        headers={"Content-Type": "application/json", "X-API-Key-ID": API_KEY},
        json={
            "text": text,
            "voice": voice,
            "model": model,
            "language": language,
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 24000,
                "num_channels": 1,
                "sample_width": 2,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        },
        timeout=60,
    )
    if response.status_code != 200:
        raise RuntimeError(f"TTS error {response.status_code}: {response.text}")
    return response.content


if __name__ == "__main__":
    audio = speak("నమస్కారం, మీరు ఎలా ఉన్నారు? నేను మీ మాట వినడానికి ఇక్కడ ఉన్నాను.", language="te-IN")
    with open("hello.wav", "wb") as f:
        f.write(audio)
    print("Saved hello.wav")