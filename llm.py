
import os
import time
import requests
from dotenv import load_dotenv
from modes import MODES

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL", "gemini-3.1-flash-lite")
FALLBACKS = [
    m.strip()
    for m in os.getenv("LLM_FALLBACK", "").split(",")
    if m.strip()
]

BASE = "https://generativelanguage.googleapis.com/v1beta"
TIMEOUT = 20


def _call(model, system_prompt, contents):
    """Send a request to the Gemini API."""

    if not API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is missing. Check your .env file."
        )

    return requests.post(
        f"{BASE}/models/{model}:generateContent",
        headers={
            "x-goog-api-key": API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": contents,
        },
        timeout=TIMEOUT,
    )


def chat(mode, history, user_text):
    """
    Generate an AI response.

    history: list of {"role": "user" or "model", "text": "..."}
    Returns: (reply_text, crisis_flag)
    """

    if mode not in MODES:
        raise ValueError(f"Unknown mode: {mode}")

    contents = [
        {
            "role": item["role"],
            "parts": [{"text": item["text"]}],
        }
        for item in history
    ]

    contents.append({
        "role": "user",
        "parts": [{"text": user_text}],
    })

    system_prompt = MODES[mode]["prompt"]
    last_error = "unknown error"

    for model in [MODEL] + FALLBACKS:
        for attempt in range(2):
            try:
                response = _call(
                    model,
                    system_prompt,
                    contents,
                )

            except requests.exceptions.RequestException as error:
                last_error = (
                    f"{model}: {type(error).__name__}"
                )
                print(f"[LLM] {last_error}")
                break

            if response.status_code == 200:
                try:
                    data = response.json()
                    candidates = data.get("candidates", [])

                    if not candidates:
                        last_error = (
                            f"{model}: API returned no candidates"
                        )
                        print(f"[LLM] {last_error}")
                        break

                    parts = candidates[0]["content"]["parts"]
                    reply = " ".join(
                        part["text"]
                        for part in parts
                        if "text" in part
                    ).strip()

                    if not reply:
                        last_error = (
                            f"{model}: API returned an empty response"
                        )
                        print(f"[LLM] {last_error}")
                        break

                    crisis = reply.startswith("[CRISIS]")
                    reply = reply.replace("[CRISIS]", "").strip()

                    return reply, crisis

                except (KeyError, IndexError, TypeError, ValueError) as error:
                    last_error = (
                        f"{model}: Invalid API response "
                        f"({type(error).__name__})"
                    )
                    print(f"[LLM] {last_error}")
                    break

            last_error = (
                f"{model}: HTTP {response.status_code} "
                f"{response.text[:200]}"
            )
            print(f"[LLM] {last_error}")

            if response.status_code in (429, 500, 503):
                if attempt == 0:
                    time.sleep(2)
                    continue

            break

    raise RuntimeError(
        f"All configured models failed. Last error: {last_error}"
    )


def list_models():
    """List Gemini models available to this API key."""

    if not API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is missing. Check your .env file."
        )

    response = requests.get(
        f"{BASE}/models",
        headers={"x-goog-api-key": API_KEY},
        timeout=30,
    )
    response.raise_for_status()

    for model_info in response.json().get("models", []):
        if "generateContent" in model_info.get(
            "supportedGenerationMethods", []
        ):
            print(model_info["name"].replace("models/", ""))


if __name__ == "__main__":
    try:
        text, crisis = chat(
            "listener",
            [],
            "I feel very scared about my exams. Can you help me?",
        )

        print("AI response:", text)
        print("Crisis flag:", crisis)

    except Exception as error:
        print("LLM test failed:", error)
