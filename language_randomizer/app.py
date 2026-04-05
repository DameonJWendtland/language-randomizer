from tkinter import ttk

from .i18n import set_ui_language, t
from . import translator
from .settings_store import load_settings
from ttkthemes import ThemedTk

from .ui.main_window import create_main_gui
from .ui.window_icon import apply_window_icon


def _apply_saved_settings(root):
    settings = load_settings()
    set_ui_language(settings.get("ui_language", "en"))

    saved_font = settings.get("font_family", "")
    if saved_font:
        root.option_add("*Font", f"{saved_font} 12")

    saved_theme = settings.get("theme", "")
    if saved_theme:
        try:
            if hasattr(root, "set_theme"):
                available = root.get_themes()
                if saved_theme in available:
                    root.set_theme(saved_theme)
                else:
                    ttk.Style(root).theme_use(saved_theme)
            else:
                ttk.Style(root).theme_use(saved_theme)
        except Exception:
            pass

    translator.activateTransliteration = bool(settings.get("activate_transliteration", False))

    saved_forced = settings.get("forced_languages", [])
    if isinstance(saved_forced, list):
        valid_forced = [lang for lang in saved_forced if lang in translator.supported_languages]
        translator.forcedLanguages = valid_forced
    else:
        translator.forcedLanguages = []


def main():
    root = ThemedTk(theme="default")
    _apply_saved_settings(root)
    root.title(t("app_title"))
    apply_window_icon(root)
    create_main_gui(root)
    root.mainloop()
