import tkinter as tk
import unicodedata
from tkinter import filedialog, ttk

from .. import translator
from .context_menu import bind_context_menu
from .mousewheel import enable_vertical_mousewheel
from .text_direction import set_text_widget_content
from .window_icon import apply_window_icon


def _contains_non_latin_letters(text):
    for char in text:
        if not char.isalpha():
            continue
        if "LATIN" not in unicodedata.name(char, ""):
            return True
    return False


def _normalize_step(step):
    if isinstance(step, (list, tuple)):
        if len(step) >= 3:
            return step[0], step[1], step[2] or ""
        if len(step) == 2:
            return step[0], step[1], ""
    return "Unknown", str(step), ""


def _should_show_transliteration(step_text, transliteration_text):
    if not translator.activateTransliteration:
        return False
    if not transliteration_text.strip():
        return False
    if transliteration_text.strip() == step_text.strip():
        return False
    return _contains_non_latin_letters(step_text)


def _build_transliteration_widget(parent, transliteration_text):
    badge_frame = tk.Frame(parent, bg="#F2D35C", bd=0, highlightthickness=0)
    badge_frame.pack(fill="x", padx=10, pady=(0, 10))

    title = tk.Label(
        badge_frame,
        text="Transliteration:",
        bg="#F2D35C",
        fg="#202020",
        font=("TkDefaultFont", 10, "bold"),
        anchor="w",
    )
    title.pack(side="left", padx=(8, 6), pady=6)

    value = tk.Label(
        badge_frame,
        text=transliteration_text,
        bg="#F2D35C",
        fg="#202020",
        font=("TkDefaultFont", 10),
        justify="left",
        wraplength=560,
        anchor="w",
    )
    value.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=6)


def show_translation_steps():
    steps_win = tk.Toplevel()
    steps_win.title("Translation Steps")
    steps_win.geometry("760x430")
    apply_window_icon(steps_win)

    top_frame = ttk.Frame(steps_win)
    top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    export_btn = ttk.Button(top_frame, text="Export", command=export_steps)
    export_btn.pack(side="right")

    canvas = tk.Canvas(steps_win)
    canvas.grid(row=1, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(steps_win, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=1, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    enable_vertical_mousewheel(canvas)

    steps = translator.get_translation_steps()
    if not steps:
        no_label = ttk.Label(scrollable_frame, text="No steps recorded.", font=("TkDefaultFont", 20))
        no_label.pack(padx=10, pady=10)
    else:
        for idx, step in enumerate(steps, 1):
            lang, step_text, transliteration_text = _normalize_step(step)

            lang_label = ttk.Label(scrollable_frame, text=f"Step {idx} ({lang}):")
            lang_label.pack(anchor="w", padx=10, pady=(10, 2))

            translation_text = tk.Text(scrollable_frame, wrap="word", font=("TkDefaultFont", 15), height=4)
            translation_text.pack(fill="x", padx=10, pady=(0, 8))
            set_text_widget_content(translation_text, step_text)
            bind_context_menu(translation_text)

            if _should_show_transliteration(step_text, transliteration_text):
                _build_transliteration_widget(scrollable_frame, transliteration_text)

    steps_win.grid_rowconfigure(1, weight=1)
    steps_win.grid_columnconfigure(0, weight=1)


def export_steps():
    steps = translator.get_translation_steps()
    export_text = ""

    if not steps:
        export_text = "No steps recorded."
    else:
        for idx, step in enumerate(steps, 1):
            lang, step_text, transliteration_text = _normalize_step(step)
            export_text += f"Step {idx} ({lang}):\n{step_text}\n"
            if _should_show_transliteration(step_text, transliteration_text):
                export_text += f"Transliteration: {transliteration_text}\n"
            export_text += "\n"

    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        title="Save translation steps as...",
    )

    if filename:
        with open(filename, "w", encoding="utf-8") as export_file:
            export_file.write(export_text)
        print("Steps exported to", filename)
