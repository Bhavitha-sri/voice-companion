import os
import time
import requests
from dotenv import load_dotenv
from modes import MODES

load_dotenv()
API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL", "gemini-3.1-flash-lite")
FALLBACKS = [m.strip() for m in os.getenv("LLM_FALLBACK", "").split(",") if m.strip()]
BASE = "https://generativelanguage.googleapis.com/v1beta"
TIMEOUT = 20  # seconds to wait for each try


def _call(model, system_prompt, contents):
    return requests.post(
        f"{BASE}/models/{model}:generateContent",
        headers={"x-goog-api-key": API_KEY, "Content-Type": "application/json"},
        json={
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
        },
        timeout=TIMEOUT,
    )


def chat(mode, history, user_text):
    """history = list of {"role": "user" or "model", "text": "..."}.
    Returns (reply_text, crisis_flag)."""
    contents = [{"role": h["role"], "parts": [{"text": h["text"]}]} for h in history]
    contents.append({"role": "user", "parts": [{"text": user_text}]})
    system_prompt = MODES[mode]["prompt"]

    last_error = "unknown error"
    for model in [MODEL] + FALLBACKS:
        for attempt in range(2):
            try:
                response = _call(model, system_prompt, contents)
            except requests.exceptions.RequestException as e:
                last_error = f"{model}: {type(e).__name__}"
                print(f"[LLM] {last_error}, trying again or switching model...")
                break  # slow or unreachable model: move to the next one

            if response.status_code == 200:
                reply = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                crisis = reply.startswith("[CRISIS]")
                return reply.replace("[CRISIS]", "").strip(), crisis

            last_error = f"{model}: {response.status_code} {response.text[:200]}"
            print(f"[LLM] {last_error}")
            if response.status_code in (429, 500, 503):
                time.sleep(2)
                continue
            break  # 400, 404 etc. will not fix themselves

    raise RuntimeError(f"All models failed. Last error: {last_error}")


def list_models():
    r = requests.get(f"{BASE}/models", headers={"x-goog-api-key": API_KEY}, timeout=30)
    for m in r.json().get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            print(m["name"].replace("models/", ""))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "models":
        list_models()
    else:
        text, crisis = chat("listener", [], "నాకు పరీక్షల గురించి చాలా భయంగా ఉంది")
        print(text)
        print("Crisis flag:", crisis)