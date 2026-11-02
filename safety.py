# First safety layer: checks every user message for self-harm signals.
# The AI model also watches for this (see modes.py), so there are two layers.

CRISIS_WORDS = [
    # English
    "kill myself", "suicide", "end my life", "want to die", "wanna die",
    "don't want to live", "dont want to live", "hurt myself", "self harm",
    "no reason to live",
    # Hindi
    "आत्महत्या", "मरना चाहता", "मरना चाहती", "मर जाना चाहता", "मर जाना चाहती",
    "जीना नहीं चाहता", "जीना नहीं चाहती", "ख़ुदकुशी", "खुदकुशी",
    # Telugu
    "ఆత్మహత్య", "చనిపోవాలని", "చనిపోవాలనిపిస్తుంది", "బతకాలని లేదు",
    # Romanised (typed or transliterated)
    "chanipovalani", "marna chahta", "marna chahti", "jeena nahi chahta",
]

CRISIS_MESSAGES = {
    "te": "మీరు ఒంటరి కాదు. మీ బాధ నాకు అర్థమవుతోంది. దయచేసి ఇప్పుడే మీకు నమ్మకమైన ఒకరితో మాట్లాడండి, లేదా టెలి మానస్ హెల్ప్‌లైన్ 1 4 4 1 6 కి కాల్ చేయండి. మీ ప్రాణం చాలా విలువైనది.",
    "hi": "आप अकेले नहीं हैं। मैं आपका दर्द समझ सकता हूँ। कृपया अभी किसी भरोसेमंद व्यक्ति से बात करें, या टेली मानस हेल्पलाइन 1 4 4 1 6 पर कॉल करें। आपकी जान बहुत कीमती है।",
    "en": "You are not alone, and I am really glad you told me. Please talk to someone you trust right now, or call the Tele MANAS helpline at 1 4 4 1 6. If you are in immediate danger, call 1 1 2. Your life matters.",
}


def is_crisis(text):
    t = text.lower()
    return any(word in t for word in CRISIS_WORDS)


def crisis_message(lang="en"):
    return CRISIS_MESSAGES.get(lang, CRISIS_MESSAGES["en"])


if __name__ == "__main__":
    print(is_crisis("I want to die"))          # True
    print(is_crisis("I am stressed about my exam"))  # False