from . import language, ollama

GROUND = ("Use ONLY the document text provided. Do not invent information. "
          "If the document does not contain enough information, say so clearly.")

def run(task: str, content: str, lang: str, model: str | None = None) -> str:
    system = f"{ollama.TUTOR} {language.instruction(lang)}"
    return ollama.chat(model, [{"role": "system", "content": system},
                               {"role": "user", "content": f"{task}\n\n{content}"}])

def out_lang(user, requested: str | None, text: str = "") -> str:
    """Output language: explicit choice > request wording > user's manual setting > interface language."""
    if requested and requested != "auto": return requested
    forced = language.explicit_override(text) if text else None
    if forced: return forced
    if user.response_language != "auto": return user.response_language
    if text: return language.resolve(text, "auto")
    return user.interface_language if user.interface_language in language.NAMES else "en"
