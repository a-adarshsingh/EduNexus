"""Lightweight automatic language detection (no heavy dependencies).
detect() returns (language code, confident?)."""
import re

NAMES = {"en": "English", "hi": "Hindi", "hinglish": "Hinglish (Hindi written in Roman script mixed with English)",
         "bn": "Bengali", "ta": "Tamil", "te": "Telugu", "mr": "Marathi", "gu": "Gujarati",
         "pa": "Punjabi", "ur": "Urdu", "es": "Spanish", "fr": "French"}

SCRIPTS = {"bn": (0x0980, 0x09FF), "pa": (0x0A00, 0x0A7F), "gu": (0x0A80, 0x0AFF),
           "ta": (0x0B80, 0x0BFF), "te": (0x0C00, 0x0C7F), "ur": (0x0600, 0x06FF),
           "deva": (0x0900, 0x097F)}
MARATHI = {"आहे", "काय", "आणि", "नाही", "मला", "तुम्ही", "होते", "कसे", "म्हणजे"}
ROMAN_HINDI = set("hai hain kya kaise kyun kyu nahi nahin mujhe mera meri tum aap ko ka ki ke se me mein "
                  "samjhao samjha batao bata karo kar kaun kab kitna toh bhi aur ya yeh ye woh wo accha "
                  "theek hota hoti chahiye padhai samajh sikhna".split())
ES = set("el la los las es qué que cómo como por para una un del y en con pero explica".split())
FR = set("le la les est une un des et en pour que qui dans avec mais pourquoi comment expliquez".split())

OVERRIDES = [(r"\b(in|into)\s+english\b", "en"), (r"\b(in|into)\s+hindi\b|hindi\s+(me|mein)", "hi"),
             (r"\bin\s+hinglish\b", "hinglish"), (r"\bin\s+spanish\b", "es"), (r"\bin\s+french\b", "fr"),
             (r"\bin\s+(bengali|tamil|telugu|marathi|gujarati|punjabi|urdu)\b", None)]
NAME2CODE = {"bengali": "bn", "tamil": "ta", "telugu": "te", "marathi": "mr",
             "gujarati": "gu", "punjabi": "pa", "urdu": "ur"}

def explicit_override(text: str) -> str | None:
    t = text.lower()
    for pat, code in OVERRIDES:
        m = re.search(pat, t)
        if m:
            return code or NAME2CODE[m.group(1)]
    return None

def detect(text: str) -> tuple[str, bool]:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "en", False
    counts: dict[str, int] = {}
    latin = 0
    for c in letters:
        o = ord(c)
        if o < 0x250:
            latin += 1
            continue
        for k, (lo, hi) in SCRIPTS.items():
            if lo <= o <= hi:
                counts[k] = counts.get(k, 0) + 1
    if counts:
        top = max(counts, key=counts.get)
        if latin / len(letters) >= 0.25:
            return ("hinglish" if top == "deva" else top), True
        if top == "deva":
            return ("mr" if set(text.split()) & MARATHI else "hi"), True
        return top, True
    words = re.findall(r"[a-zA-Zà-ÿ']+", text.lower())
    hits = sum(w in ROMAN_HINDI for w in words)
    if hits >= 2 or (hits == 1 and len(words) <= 3):
        return "hinglish", True
    es, fr = sum(w in ES for w in words), sum(w in FR for w in words)
    if max(es, fr) >= 2 or re.search(r"[¿¡ñ]", text):
        return ("es" if es >= fr else "fr"), True
    if fr and re.search(r"[àâçéèêëîïôûùœ]", text.lower()):
        return "fr", True
    return "en", len(words) >= 4

def resolve(text: str, user_pref: str = "auto", previous: str | None = None) -> str:
    """Priority: explicit request > manual setting > detected > previous turn > English."""
    forced = explicit_override(text)
    if forced: return forced
    if user_pref and user_pref != "auto": return user_pref
    code, confident = detect(text)
    return code if confident or not previous else previous

def instruction(code: str) -> str:
    name = NAMES.get(code, "English")
    extra = (" Write Hindi in Roman script mixed naturally with English, the way the user does."
             if code == "hinglish" else "")
    return f"Reply entirely in {name}, matching the user's conversational style.{extra}"
