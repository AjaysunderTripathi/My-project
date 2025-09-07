from langdetect import detect
from transformers import pipeline

# ✅ Verified models that exist on Hugging Face
MODEL_IDS = {
    'hi-en': "Helsinki-NLP/opus-mt-hi-en",
    'bn-en': "Helsinki-NLP/opus-mt-bn-en",
    'mr-en': "Helsinki-NLP/opus-mt-mr-en",
    'en-hi': "Helsinki-NLP/opus-mt-en-hi",
    'en-bn': "Helsinki-NLP/opus-mt-en-bn",
    'en-mr': "Helsinki-NLP/opus-mt-en-mr",
}

# ✅ Lazy-loaded pipelines (avoid warnings + faster startup)
_loaded_pipelines = {}

def get_pipeline(direction):
    """Load pipeline on first use, return None if unavailable."""
    if direction not in _loaded_pipelines:
        model_id = MODEL_IDS.get(direction)
        if model_id:
            try:
                _loaded_pipelines[direction] = pipeline("translation", model=model_id)
            except Exception as e:
                # Fail silently — no error spam in console
                _loaded_pipelines[direction] = None
        else:
            _loaded_pipelines[direction] = None
    return _loaded_pipelines[direction]

def detect_and_translate_in(text):
    """Detect language and translate input to English if needed."""
    try:
        lang = detect(text)
    except Exception:
        lang = 'en'

    direction = f"{lang}-en"
    pipe = get_pipeline(direction)
    if lang != 'en' and pipe:
        translated = pipe(text)[0]['translation_text']
        return lang, translated
    return lang, text

def translate_out(text, lang):
    """Translate English output to target language if needed."""
    direction = f"en-{lang}"
    pipe = get_pipeline(direction)
    if lang != 'en' and pipe:
        return pipe(text)[0]['translation_text']
    return text
