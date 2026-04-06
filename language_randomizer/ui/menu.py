import tkinter as tk
import tkinter.font as tk_font
import webbrowser
from tkinter import ttk

from .. import translator
from ..i18n import (
    get_ui_language,
    get_ui_language_code_from_label,
    get_ui_language_label,
    get_ui_language_options,
    set_ui_language,
    t,
)
from ..settings_store import load_settings, update_settings
from .context_menu import bind_context_menu
from .window_icon import apply_window_icon

_TRANSLATION_MODE_OPTIONS = ("normal", "chaos", "safe")


def _get_translation_mode_pairs():
    return [(mode, t(f"translation_mode_{mode}")) for mode in _TRANSLATION_MODE_OPTIONS]


def _get_translation_mode_label(mode_code):
    options = dict(_get_translation_mode_pairs())
    return options.get(mode_code, options["normal"])


def _get_translation_mode_code_from_label(mode_label):
    for code, label in _get_translation_mode_pairs():
        if label == mode_label:
            return code
    return "normal"


def _fit_window_to_content(window, min_width=360, min_height=260, max_screen_ratio=0.9):
    if window is None or not window.winfo_exists():
        return

    window.update_idletasks()
    requested_width = window.winfo_reqwidth() + 12
    requested_height = window.winfo_reqheight() + 12

    max_width = int(window.winfo_screenwidth() * max_screen_ratio)
    max_height = int(window.winfo_screenheight() * max_screen_ratio)

    final_width = min(max(requested_width, min_width), max_width)
    final_height = min(max(requested_height, min_height), max_height)

    try:
        pos_x = window.winfo_x()
        pos_y = window.winfo_y()
        if pos_x >= 0 and pos_y >= 0:
            window.geometry(f"{final_width}x{final_height}+{pos_x}+{pos_y}")
            return
    except Exception:
        pass

    window.geometry(f"{final_width}x{final_height}")


def _get_available_themes(root):
    themes = []
    if root is not None and hasattr(root, "get_themes"):
        try:
            themes = list(root.get_themes())
        except Exception:
            themes = []
    if not themes:
        style = ttk.Style(root)
        themes = list(style.theme_names())
    themes = sorted(set(themes))
    return themes


def _get_current_theme(root):
    try:
        return ttk.Style(root).theme_use()
    except Exception:
        return ""


def _apply_font_family_now(root, font_family):
    named_fonts = (
        "TkDefaultFont",
        "TkTextFont",
        "TkFixedFont",
        "TkMenuFont",
        "TkHeadingFont",
        "TkCaptionFont",
        "TkSmallCaptionFont",
        "TkIconFont",
        "TkTooltipFont",
    )

    for font_name in named_fonts:
        try:
            tk_font.nametofont(font_name).configure(family=font_family)
        except tk.TclError:
            pass

    def _update_widget_fonts(widget):
        try:
            current_font = widget.cget("font")
        except tk.TclError:
            current_font = ""

        if current_font:
            try:
                named_font = tk_font.nametofont(current_font)
                named_font.configure(family=font_family)
            except tk.TclError:
                try:
                    resolved_font = tk_font.Font(font=current_font)
                    resolved_font.configure(family=font_family)
                    widget.configure(font=resolved_font)
                except tk.TclError:
                    pass

        for child in widget.winfo_children():
            _update_widget_fonts(child)

    _update_widget_fonts(root)
    root.update_idletasks()


def show_settings(menu_win, main_frame, on_ui_refresh=None):
    for widget in main_frame.winfo_children():
        widget.destroy()

    header_font = tk_font.Font(family="Helvetica", size=16, weight="bold")
    header_label = ttk.Label(main_frame, text=t("settings_header"), font=header_font)
    header_label.pack(pady=(0, 20))

    font_label = ttk.Label(main_frame, text=t("font_label"))
    font_label.pack(pady=5)

    fonts = sorted(tk_font.families())
    font_dropdown = ttk.Combobox(main_frame, values=fonts, state="readonly")
    saved_settings = load_settings()
    saved_font = saved_settings.get("font_family", "")
    if saved_font in fonts:
        font_dropdown.set(saved_font)
    elif fonts:
        font_dropdown.set(fonts[0])
    font_dropdown.pack(pady=5, fill="x")
    bind_context_menu(font_dropdown)

    theme_label = ttk.Label(main_frame, text=t("theme_label"))
    theme_label.pack(pady=5)
    root = tk._default_root
    available_themes = _get_available_themes(root)
    current_theme = _get_current_theme(root)
    saved_theme = saved_settings.get("theme", "")

    theme_dropdown = ttk.Combobox(main_frame, values=available_themes, state="readonly")
    if saved_theme in available_themes:
        theme_dropdown.set(saved_theme)
    elif current_theme in available_themes:
        theme_dropdown.set(current_theme)
    elif available_themes:
        theme_dropdown.set(available_themes[0])
    theme_dropdown.pack(pady=5, fill="x")
    bind_context_menu(theme_dropdown)

    ui_language_label = ttk.Label(main_frame, text=t("ui_language_label"))
    ui_language_label.pack(pady=5)

    language_options = get_ui_language_options()
    language_labels = [label for _, label in language_options]
    language_dropdown = ttk.Combobox(main_frame, values=language_labels, state="readonly")

    saved_ui_language = saved_settings.get("ui_language", get_ui_language())
    language_dropdown.set(get_ui_language_label(saved_ui_language))
    language_dropdown.pack(pady=5, fill="x")
    bind_context_menu(language_dropdown)

    transliteration_var = tk.BooleanVar(value=translator.activateTransliteration)
    transliteration_chk = ttk.Checkbutton(
        main_frame,
        text=t("activate_transliteration"),
        variable=transliteration_var,
    )
    transliteration_chk.pack(pady=(8, 4), anchor="w")

    translation_mode_label = ttk.Label(main_frame, text=t("translation_mode_label"))
    translation_mode_label.pack(pady=(8, 5), anchor="w")

    translation_mode_dropdown = ttk.Combobox(
        main_frame,
        values=[label for _, label in _get_translation_mode_pairs()],
        state="readonly",
    )
    saved_mode = saved_settings.get("translation_mode", getattr(translator, "translationMode", "normal"))
    translation_mode_dropdown.set(_get_translation_mode_label(saved_mode))
    translation_mode_dropdown.pack(pady=2, fill="x")
    bind_context_menu(translation_mode_dropdown)

    apply_btn = ttk.Button(
        main_frame,
        text=t("apply_button"),
        command=lambda: apply_settings(
            menu_win,
            font_dropdown,
            theme_dropdown,
            language_dropdown,
            transliteration_var,
            translation_mode_dropdown,
            on_ui_refresh=on_ui_refresh,
        ),
    )
    apply_btn.pack(pady=5)

    back_btn = ttk.Button(
        main_frame,
        text=t("back_button"),
        command=lambda: show_main_menu(menu_win, main_frame, on_ui_refresh=on_ui_refresh),
    )
    back_btn.pack(pady=10)

    _fit_window_to_content(menu_win, min_width=400, min_height=430)


def show_main_menu(menu_win, main_frame, on_ui_refresh=None):
    for widget in main_frame.winfo_children():
        widget.destroy()

    header_font = tk_font.Font(family="Helvetica", size=16, weight="bold")
    header_label = ttk.Label(main_frame, text=t("menu_header"), font=header_font)
    header_label.pack(pady=(0, 20))

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill="x", pady=10)

    settings_btn = ttk.Button(
        btn_frame,
        text=t("settings_button"),
        command=lambda: show_settings(menu_win, main_frame, on_ui_refresh=on_ui_refresh),
    )
    settings_btn.pack(fill="x", pady=5)

    report_btn = ttk.Button(
        btn_frame,
        text=t("report_bugs_button"),
        command=lambda: webbrowser.open("https://github.com/DameonJWendtland/language-randomizer/"),
    )
    report_btn.pack(fill="x", pady=5)

    close_btn = ttk.Button(main_frame, text=t("close_button"), command=menu_win.destroy)
    close_btn.pack(pady=10)

    _fit_window_to_content(menu_win, min_width=360, min_height=260)


def apply_settings(
    menu_win,
    font_dropdown,
    theme_dropdown,
    language_dropdown,
    transliteration_var,
    translation_mode_dropdown,
    on_ui_refresh=None,
):
    selected_font = font_dropdown.get()
    selected_theme = theme_dropdown.get()
    selected_ui_language = get_ui_language_code_from_label(language_dropdown.get())
    selected_translation_mode = _get_translation_mode_code_from_label(translation_mode_dropdown.get())
    previous_ui_language = get_ui_language()
    set_ui_language(selected_ui_language)

    root = tk._default_root
    if root is not None:
        if selected_theme:
            try:
                if hasattr(root, "set_theme"):
                    root.set_theme(selected_theme)
                else:
                    ttk.Style(root).theme_use(selected_theme)
            except tk.TclError as exc:
                print("Failed to apply theme:", selected_theme, "-", exc)
        if selected_font:
            _apply_font_family_now(root, selected_font)
            root.option_add("*Font", f"{selected_font} 12")

    translator.activateTransliteration = transliteration_var.get()
    translator.translationMode = selected_translation_mode
    update_settings(
        font_family=selected_font,
        theme=selected_theme,
        ui_language=selected_ui_language,
        activate_transliteration=translator.activateTransliteration,
        translation_mode=translator.translationMode,
    )

    print("Applied font:", selected_font)
    print("Applied theme:", selected_theme)
    print("App language:", selected_ui_language)
    print("Activate transliteration:", translator.activateTransliteration)
    print("Translation mode:", translator.translationMode)

    if menu_win is not None and menu_win.winfo_exists():
        menu_win.destroy()

    if callable(on_ui_refresh):
        try:
            on_ui_refresh(force_rebuild=(selected_ui_language != previous_ui_language))
        except TypeError:
            on_ui_refresh()


def open_menu(on_ui_refresh=None):
    menu_win = tk.Toplevel()
    menu_win.title(t("menu_window_title"))
    menu_win.resizable(True, True)
    apply_window_icon(menu_win)

    main_frame = ttk.Frame(menu_win, padding=10)
    main_frame.pack(fill="both", expand=True)

    show_main_menu(menu_win, main_frame, on_ui_refresh=on_ui_refresh)
