
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GNANI_API_KEY")
TTS_URL = "https://api.vachana.ai/api/v1/tts/inference"

MODEL = "timbre-v3.0"
VOICE = "Shivani"


def speak(text, language="auto", voice=VOICE, model=MODEL):
    """Convert text into speech using the Gnani TTS API."""

    if not API_KEY:
        raise RuntimeError(
            "GNANI_API_KEY is missing. Please check your .env file."
        )

    response = requests.post(
        TTS_URL,
        headers={
            "Content-Type": "application/json",
            "X-API-Key-ID": API_KEY,
        },
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
        raise RuntimeError(
            f"TTS error {response.status_code}: {response.text}"
        )

    return response.content


if __name__ == "__main__":
    text = "నమస్కారం, మీరు ఎలా ఉన్నారు? నేను మీ మాట వినడానికి ఇక్కడ ఉన్నాను."

    try:
        audio = speak(text, language="te-IN")

        output_file = "tts_test.wav"

        with open(output_file, "wb") as file:
            file.write(audio)

        print(f"Speech generated successfully: {output_file}")
        print(f"Audio size: {len(audio)} bytes")

    except Exception as error:
        print(f"Speech generation failed: {error}")
