"""Validated synthesis, independent of the browser interface."""
from pathlib import Path
import tempfile
from gtts import gTTS
from gtts.lang import tts_langs

MAX_CHARACTERS = 10_000
ACCENTS = {"Default": "com", "United Kingdom": "co.uk", "United States": "us", "Australia": "com.au", "India": "co.in"}


def normalize_text(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Enter some text before generating speech.")
    text = text.strip()
    if len(text) > MAX_CHARACTERS:
        raise ValueError("Use at most 10,000 characters per conversion.")
    return text


def text_stats(text):
    text = text or ""
    words = len(text.split())
    return f"{len(text):,} / 10,000 characters | {words:,} words | ~{round(words / 150 * 60)} seconds at normal pace"


def read_document(filepath):
    if not filepath:
        return ""
    path = Path(filepath)
    if path.suffix.lower() not in {".txt", ".md"}:
        raise ValueError("Upload a UTF-8 .txt or .md document.")
    if path.stat().st_size > 100_000:
        raise ValueError("The document must be smaller than 100 KB.")
    try:
        return normalize_text(path.read_text(encoding="utf-8-sig"))
    except UnicodeError as exc:
        raise ValueError("Save your document with UTF-8 encoding.") from exc


def synthesize(text, language="en", slow=False, accent="Default"):
    text = normalize_text(text)
    if language not in tts_langs():
        raise ValueError("Choose a supported language.")
    if accent not in ACCENTS:
        raise ValueError("Choose a supported accent.")
    with tempfile.NamedTemporaryFile(prefix="voice-studio-", suffix=".mp3", delete=False) as output:
        path = Path(output.name)
    try:
        gTTS(text=text, lang=language, slow=bool(slow), tld=ACCENTS[accent], timeout=(10, 60)).save(str(path))
        if not path.stat().st_size:
            raise RuntimeError("Empty audio")
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise RuntimeError("Speech generation failed. Check your connection or try again later.") from exc
    return str(path)
