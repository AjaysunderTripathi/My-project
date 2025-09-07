from langdetect import detect
from transformers import pipeline

def safe_pipeline(task, model):
    """Safely load a pipeline, fallback to None if unavailable."""
    try:
        return pipeline(task, model=model)
    except Exception as e:
        print(f"⚠️ Warning: Could not load model {model}. Error: {e}")
        return None

# Input translation pipelines (to English)
IN_PIPELINES = {
    'hi': safe_pipeline("translation", "Helsinki-NLP/opus-mt-hi-en"),
    'bn': safe_pipeline("translation", "Helsinki-NLP/opus-mt-bn-en"),
    'mr': safe_pipeline("translation", "Helsinki-NLP/opus-mt-mr-en"),
    'en': None
}

# Output translation pipelines (from English)
OUT_PIPELINES = {
    'hi': safe_pipeline("translation", "Helsinki-NLP/opus-mt-en-hi"),
    'bn': safe_pipeline("translation", "Helsinki-NLP/opus-mt-en-bn"),
    'mr': safe_pipeline("translation", "Helsinki-NLP/opus-mt-en-mr"),
}

def detect_and_translate_in(text):
    """Detect language and translate input to English if needed."""
    try:
        lang = detect(text)
    except Exception:
        lang = 'en'
    if lang != 'en' and lang in IN_PIPELINES and IN_PIPELINES[lang]:
        translated = IN_PIPELINES[lang](text)[0]['translation_text']
        return lang, translated
    return lang, text

def translate_out(text, lang):
    """Translate English output to target language if needed."""
    if lang != 'en' and lang in OUT_PIPELINES and OUT_PIPELINES[lang]:
        return OUT_PIPELINES[lang](text)[0]['translation_text']
    return text
# Fallback to original text if translation fails or model unavailable