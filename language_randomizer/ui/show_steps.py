import tkinter as tk
import unicodedata
import urllib.parse
import webbrowser
from tkinter import filedialog, ttk

from .. import translator
from ..font_utils import apply_saved_font
from ..i18n import t
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
    if isinstance(step, dict):
        target_language_name = step.get("target_language_name", "Unknown")
        step_text = str(step.get("output_text", ""))
        transliteration_text = step.get("transliteration", "") or ""
        source_text = str(step.get("input_text", step_text))
        source_language_code = step.get("source_language_code", "") or "auto"
        target_language_lookup = str(target_language_name).lower()
        target_language_code = step.get("target_language_code", "") or translator.language_name_to_code.get(
            target_language_lookup, ""
        )
        return (
            target_language_name,
            step_text,
            transliteration_text,
            source_text,
            source_language_code,
            target_language_code,
        )

    if isinstance(step, (list, tuple)):
        if len(step) >= 3:
            target_language_name = step[0]
            step_text = str(step[1])
            transliteration_text = step[2] or ""
            target_language_lookup = str(target_language_name).lower()
            target_language_code = translator.language_name_to_code.get(target_language_lookup, "")
            return target_language_name, step_text, transliteration_text, step_text, "auto", target_language_code
        if len(step) == 2:
            target_language_name = step[0]
            step_text = str(step[1])
            target_language_lookup = str(target_language_name).lower()
            target_language_code = translator.language_name_to_code.get(target_language_lookup, "")
            return target_language_name, step_text, "", step_text, "auto", target_language_code

    text = str(step)
    return "Unknown", text, "", text, "auto", ""


def _open_in_google_translate(source_text, source_language_code, target_language_code):
    if not target_language_code or not source_text.strip():
        return

    query = urllib.parse.urlencode(
        {
            "sl": source_language_code or "auto",
            "tl": target_language_code,
            "text": source_text,
            "op": "translate",
        }
    )
    webbrowser.open(f"https://translate.google.com/?{query}")


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
        text=t("transliteration_label"),
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
    steps_win.title(t("translation_steps_title"))
    steps_win.geometry("760x430")
    apply_window_icon(steps_win)

    top_frame = ttk.Frame(steps_win)
    top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    export_btn = ttk.Button(top_frame, text=t("export_button"), command=export_steps)
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
        no_label = ttk.Label(scrollable_frame, text=t("no_steps_recorded"), font=("TkDefaultFont", 20))
        no_label.pack(padx=10, pady=10)
    else:
        _, _, _, _, _, final_target_lang_code = _normalize_step(steps[-1])
        for idx, step in enumerate(steps, 1):
            lang, step_text, transliteration_text, _, _, target_lang_code = _normalize_step(step)

            lang_label = ttk.Label(scrollable_frame, text=t("step_label", index=idx, language=lang))
            lang_label.pack(anchor="w", padx=10, pady=(10, 2))

            translation_text = tk.Text(scrollable_frame, wrap="word", font=("TkDefaultFont", 15), height=4)
            translation_text.pack(fill="x", padx=10, pady=(0, 8))
            set_text_widget_content(translation_text, step_text)
            bind_context_menu(translation_text)

            if _should_show_transliteration(step_text, transliteration_text):
                _build_transliteration_widget(scrollable_frame, transliteration_text)

            open_google_button = ttk.Button(
                scrollable_frame,
                text=t("see_on_google_translate_button"),
                command=lambda s=step_text, sl=target_lang_code, tl=final_target_lang_code: _open_in_google_translate(
                    s, sl, tl
                ),
            )
            if not step_text.strip() or not target_lang_code or not final_target_lang_code:
                open_google_button.configure(state="disabled")
            open_google_button.pack(anchor="w", padx=10, pady=(0, 10))

    steps_win.grid_rowconfigure(1, weight=1)
    steps_win.grid_columnconfigure(0, weight=1)
    apply_saved_font(steps_win)


def export_steps():
    steps = translator.get_translation_steps()
    export_text = ""
    separator_line = "-" * 72

    if not steps:
        export_text = t("no_steps_recorded")
    else:
        for idx, step in enumerate(steps, 1):
            if idx > 1:
                export_text += f"{separator_line}\n"
            lang, step_text, transliteration_text, _, _, _ = _normalize_step(step)
            export_text += f"{t('step_label', index=idx, language=lang)}\n{step_text}\n"
            if _should_show_transliteration(step_text, transliteration_text):
                export_text += f"{t('transliteration_label')} {transliteration_text}\n"
            export_text += "\n"

    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        title=t("save_steps_title"),
    )

    if filename:
        with open(filename, "w", encoding="utf-8") as export_file:
            export_file.write(export_text)
        print(t("steps_exported_log"), filename)
