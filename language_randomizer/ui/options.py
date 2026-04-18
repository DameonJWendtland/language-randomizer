import tkinter as tk
from tkinter import ttk

from .. import translator
from ..font_utils import apply_saved_font
from ..i18n import t
from ..settings_store import update_settings
from .context_menu import bind_context_menu
from .mousewheel import enable_vertical_mousewheel


def open_options(on_apply=None):
    options_win = tk.Toplevel()
    options_win.title(t("options_window_title"))
    options_win.geometry("700x400")

    canvas = tk.Canvas(options_win)
    scrollbar = tk.Scrollbar(options_win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    window_item = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def resize_canvas(event):
        canvas.itemconfig(window_item, width=event.width)

    canvas.bind("<Configure>", resize_canvas)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    enable_vertical_mousewheel(canvas)

    info_text = tk.Text(scrollable_frame, wrap=tk.WORD, height=4)
    info_text.insert("1.0", t("options_info_text"))
    info_text.config(state="disabled")
    info_text.pack(padx=10, pady=(10, 10), fill="x")
    bind_context_menu(info_text)

    info_label = ttk.Label(scrollable_frame, text=t("options_select_forced"))
    info_label.pack(padx=10, pady=(0, 10), fill="x")

    forced_vars = {}
    frame = ttk.Frame(scrollable_frame)
    frame.pack(padx=10, pady=10, fill="x")

    for i, lang in enumerate(translator.supported_languages):
        var = tk.BooleanVar(value=(lang in translator.forcedLanguages))
        forced_vars[lang] = var
        chk = ttk.Checkbutton(frame, text=lang, variable=var)
        chk.grid(row=i // 5, column=i % 5, sticky="w", padx=5, pady=5)

    def apply_options():
        translator.forcedLanguages.clear()
        for lang, var in forced_vars.items():
            if var.get():
                translator.forcedLanguages.append(lang)
        update_settings(forced_languages=translator.forcedLanguages)
        if callable(on_apply):
            on_apply(list(translator.forcedLanguages))
        options_win.destroy()
        print("Forced languages:", translator.forcedLanguages)

    def reset_options():
        for var in forced_vars.values():
            var.set(False)

    def select_all_options():
        for var in forced_vars.values():
            var.set(True)

    btn_frame = ttk.Frame(scrollable_frame)
    btn_frame.pack(pady=10)

    select_all_btn = ttk.Button(btn_frame, text=t("select_all_button"), command=select_all_options)
    select_all_btn.pack(side="left", padx=(0, 10))

    reset_btn = ttk.Button(btn_frame, text=t("reset_button"), command=reset_options)
    reset_btn.pack(side="left", padx=(0, 10))

    apply_btn = ttk.Button(btn_frame, text=t("apply_button"), command=apply_options)
    apply_btn.pack(side="left")
    apply_saved_font(options_win)
