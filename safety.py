
# Safety layer: simple keyword checks for possible self-harm signals.
# Keyword matching is only a fallback, not a reliable risk detector.

import unicodedata

CRISIS_WORDS = [
    # English
    "kill myself", "suicide", "end my life", "want to die",
    "wanna die", "don't want to live", "dont want to live",
    "hurt myself", "self harm", "no reason to live",
    "better off dead", "going to kill myself",

    # Hindi: Devanagari
    "आत्महत्या", "मरना चाहता", "मरना चाहती",
    "मर जाना चाहता", "मर जाना चाहती",
    "जीना नहीं चाहता", "जीना नहीं चाहती", "खुदकुशी",

    # Telugu
    "ఆత్మహత్య", "చనిపోవాలని", "చనిపోవాలనిపిస్తుంది",
    "బతకాలని లేదు", "చనిపోవాలి", "జీవించాలని లేదు",

    # Romanized Telugu/Hindi
    "chanipovalani", "chanipovali", "brathakalani ledu",
    "marna chahta", "marna chahti", "jeena nahi chahta",
    "jeena nahi chahti", "khudkhushi",
]

CRISIS_MESSAGES = {
    "te": (
        "మీరు ఈ బాధను ఒంటరిగా ఎదుర్కోవాల్సిన అవసరం లేదు. "
        "మీకు నమ్మకం ఉన్న వ్యక్తితో ఇప్పుడే మాట్లాడండి. "
        "టెలి మానస్ సహాయం కోసం 14416కు కాల్ చేయండి. "
        "మీకు వెంటనే ప్రమాదం ఉంటే 112కు కాల్ చేయండి."
    ),
    "hi": (
        "आपको इस दर्द का सामना अकेले नहीं करना है। "
        "कृपया अभी किसी भरोसेमंद व्यक्ति से बात करें। "
        "टेली मानस हेल्पलाइन 14416 पर कॉल करें। "
        "अगर तुरंत खतरा है, तो 112 पर कॉल करें।"
    ),
    "en": (
        "I'm glad you told me. You deserve support right now. "
        "Please contact someone you trust and ask them to stay with you. "
        "In India, call Tele-MANAS at 14416 for mental health support. "
        "If you are in immediate danger, call 112."
    ),
}


def is_crisis(text):
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = " ".join(normalized.split())
    return any(word.casefold() in normalized for word in CRISIS_WORDS)


def crisis_message(lang="en"):
    return CRISIS_MESSAGES.get(lang, CRISIS_MESSAGES["en"])


if __name__ == "__main__":
    tests = [
        ("I want to die", True),
        ("I am stressed about my exam", False),
        ("ఆత్మహత్య", True),
        ("చనిపోవాలని", True),
        ("खुदकुशी", True),
        ("chanipovalani", True),
    ]

    for phrase, expected in tests:
        actual = is_crisis(phrase)
        print(
            f"{'PASS' if actual == expected else 'FAIL'}: "
            f"{phrase!r} -> {actual}"
        )
