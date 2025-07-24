from langdetect import detect

def detect_lang(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "unknown"