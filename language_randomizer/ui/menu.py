import tkinter as tk
import tkinter.font as tk_font
import webbrowser
from tkinter import ttk

from .. import translator
from .window_icon import apply_window_icon


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


def show_settings(menu_win, main_frame):
    for widget in main_frame.winfo_children():
        widget.destroy()

    header_font = tk_font.Font(family="Helvetica", size=16, weight="bold")
    header_label = ttk.Label(main_frame, text="Settings", font=header_font)
    header_label.pack(pady=(0, 20))

    font_label = ttk.Label(main_frame, text="Select font:")
    font_label.pack(pady=5)

    fonts = sorted(tk_font.families())
    font_dropdown = ttk.Combobox(main_frame, values=fonts, state="readonly")
    font_dropdown.set(fonts[0])
    font_dropdown.pack(pady=5, fill="x")

    theme_label = ttk.Label(main_frame, text="Select theme:")
    theme_label.pack(pady=5)
    root = tk._default_root
    available_themes = _get_available_themes(root)
    current_theme = _get_current_theme(root)

    theme_dropdown = ttk.Combobox(main_frame, values=available_themes, state="readonly")
    if current_theme in available_themes:
        theme_dropdown.set(current_theme)
    elif available_themes:
        theme_dropdown.set(available_themes[0])
    theme_dropdown.pack(pady=5, fill="x")

    transliteration_var = tk.BooleanVar(value=translator.activateTransliteration)
    transliteration_chk = ttk.Checkbutton(
        main_frame,
        text="Activate Transliteration",
        variable=transliteration_var,
    )
    transliteration_chk.pack(pady=(8, 4), anchor="w")

    apply_btn = ttk.Button(
        main_frame,
        text="Apply",
        command=lambda: apply_settings(font_dropdown, theme_dropdown, transliteration_var),
    )
    apply_btn.pack(pady=5)

    back_btn = ttk.Button(main_frame, text="Back", command=lambda: show_main_menu(menu_win, main_frame))
    back_btn.pack(pady=10)


def show_main_menu(menu_win, main_frame):
    for widget in main_frame.winfo_children():
        widget.destroy()

    header_font = tk_font.Font(family="Helvetica", size=16, weight="bold")
    header_label = ttk.Label(main_frame, text="Language Randomizer Menu", font=header_font)
    header_label.pack(pady=(0, 20))

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill="x", pady=10)

    settings_btn = ttk.Button(btn_frame, text="Settings", command=lambda: show_settings(menu_win, main_frame))
    settings_btn.pack(fill="x", pady=5)

    report_btn = ttk.Button(
        btn_frame,
        text="Report Bugs",
        command=lambda: webbrowser.open("https://github.com/DameonJWendtland/language-randomizer/"),
    )
    report_btn.pack(fill="x", pady=5)

    close_btn = ttk.Button(main_frame, text="Close", command=menu_win.destroy)
    close_btn.pack(pady=10)


def apply_settings(font_dropdown, theme_dropdown, transliteration_var):
    selected_font = font_dropdown.get()
    selected_theme = theme_dropdown.get()
    root = tk._default_root
    if root is not None:
        root.option_add("*Font", f"{selected_font} 12")
        if selected_theme:
            try:
                if hasattr(root, "set_theme"):
                    root.set_theme(selected_theme)
                else:
                    ttk.Style(root).theme_use(selected_theme)
            except tk.TclError as exc:
                print("Failed to apply theme:", selected_theme, "-", exc)
    translator.activateTransliteration = transliteration_var.get()
    print("Applied font:", selected_font)
    print("Applied theme:", selected_theme)
    print("Activate transliteration:", translator.activateTransliteration)


def open_menu():
    menu_win = tk.Toplevel()
    menu_win.title("Menu")
    menu_win.geometry("400x300")
    apply_window_icon(menu_win)

    main_frame = ttk.Frame(menu_win, padding=10)
    main_frame.pack(fill="both", expand=True)

    show_main_menu(menu_win, main_frame)
