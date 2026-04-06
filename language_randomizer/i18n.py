import json
from functools import lru_cache

from .paths import PACKAGE_DIR

DEFAULT_UI_LANGUAGE = "en"

UI_LANGUAGE_OPTIONS = [
    ("en", "English"),
    ("de", "Deutsch"),
    ("da", "Dansk"),
    ("sv", "Svenska"),
    ("es", "Español"),
    ("fr", "Français"),
    ("ru", "Русский"),
]

_LANGUAGE_LABELS = {code: label for code, label in UI_LANGUAGE_OPTIONS}
_LABEL_TO_LANGUAGE = {label: code for code, label in UI_LANGUAGE_OPTIONS}
_current_ui_language = DEFAULT_UI_LANGUAGE

_LOCALES_DIR = PACKAGE_DIR / "locales"


def _sanitize_locale_payload(payload):
    if not isinstance(payload, dict):
        return {}

    sanitized = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            continue
        sanitized[key] = value if isinstance(value, str) else str(value)
    return sanitized


@lru_cache(maxsize=None)
def _load_locale(language_code):
    locale_path = _LOCALES_DIR / f"{language_code}.json"
    try:
        with locale_path.open("r", encoding="utf-8") as locale_file:
            payload = json.load(locale_file)
    except (OSError, json.JSONDecodeError):
        return {}

    return _sanitize_locale_payload(payload)


def set_ui_language(language_code):
    global _current_ui_language
    candidate = str(language_code).strip().lower() if language_code else ""
    if candidate in _LANGUAGE_LABELS:
        _current_ui_language = candidate
    else:
        _current_ui_language = DEFAULT_UI_LANGUAGE


def get_ui_language():
    return _current_ui_language


def get_ui_language_options():
    return list(UI_LANGUAGE_OPTIONS)


def get_ui_language_label(language_code):
    return _LANGUAGE_LABELS.get(language_code, _LANGUAGE_LABELS[DEFAULT_UI_LANGUAGE])


def get_ui_language_code_from_label(language_label):
    return _LABEL_TO_LANGUAGE.get(language_label, DEFAULT_UI_LANGUAGE)


def t(key, **kwargs):
    text_key = str(key)
    language_bucket = _load_locale(_current_ui_language)
    default_bucket = _load_locale(DEFAULT_UI_LANGUAGE)
    template = language_bucket.get(text_key, default_bucket.get(text_key, text_key))

    try:
        return template.format(**kwargs)
    except Exception:
        return template
