import json
import os
import sys
from pathlib import Path


DEFAULT_SETTINGS = {
    "font_family": "",
    "theme": "",
    "ui_language": "en",
    "activate_transliteration": False,
    "forced_languages": [],
}


def _settings_path():
    if sys.platform.startswith("win"):
        base = Path(os.getenv("APPDATA") or (Path.home() / "AppData" / "Roaming"))
        return base / "LanguageRandomizer" / "settings.json"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "LanguageRandomizer" / "settings.json"

    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    base = Path(xdg_config_home) if xdg_config_home else (Path.home() / ".config")
    return base / "language-randomizer" / "settings.json"


def _sanitize_settings(raw_settings):
    sanitized = dict(DEFAULT_SETTINGS)
    if not isinstance(raw_settings, dict):
        return sanitized

    font_family = raw_settings.get("font_family", "")
    theme = raw_settings.get("theme", "")
    ui_language = raw_settings.get("ui_language", "en")
    activate_transliteration = raw_settings.get("activate_transliteration", False)
    forced_languages = raw_settings.get("forced_languages", [])

    sanitized["font_family"] = str(font_family) if font_family else ""
    sanitized["theme"] = str(theme) if theme else ""
    sanitized["ui_language"] = str(ui_language).strip().lower() if ui_language else "en"
    sanitized["activate_transliteration"] = bool(activate_transliteration)

    if isinstance(forced_languages, list):
        sanitized["forced_languages"] = [str(lang) for lang in forced_languages if isinstance(lang, str)]
    else:
        sanitized["forced_languages"] = []

    return sanitized


def load_settings():
    path = _settings_path()
    if not path.exists():
        return dict(DEFAULT_SETTINGS)

    try:
        with path.open("r", encoding="utf-8") as settings_file:
            loaded = json.load(settings_file)
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_SETTINGS)

    return _sanitize_settings(loaded)


def save_settings(settings):
    path = _settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    sanitized = _sanitize_settings(settings)
    with path.open("w", encoding="utf-8") as settings_file:
        json.dump(sanitized, settings_file, ensure_ascii=False, indent=2)


def update_settings(**updates):
    settings = load_settings()
    settings.update(updates)
    save_settings(settings)
    return load_settings()
