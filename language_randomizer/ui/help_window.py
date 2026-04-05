import tkinter as tk
from tkinter import ttk

from ..i18n import t
from .mousewheel import enable_vertical_mousewheel
from .window_icon import apply_window_icon


def _add_centered_heading(parent, text):
    heading_row = ttk.Frame(parent)
    heading_row.pack(fill="x", padx=10, pady=(10, 6))

    left_line = ttk.Separator(heading_row, orient="horizontal")
    left_line.pack(side="left", fill="x", expand=True, padx=(0, 8))

    heading_label = ttk.Label(heading_row, text=text, justify="center")
    heading_label.pack(side="left")

    right_line = ttk.Separator(heading_row, orient="horizontal")
    right_line.pack(side="left", fill="x", expand=True, padx=(8, 0))


def _add_section_text(parent, text):
    section_label = ttk.Label(
        parent,
        text=text,
        justify="left",
        wraplength=400,
    )
    section_label.pack(padx=10, pady=(0, 6), anchor="w")


def open_help():
    help_win = tk.Toplevel()
    help_win.title(t("help_window_title"))
    help_win.minsize(450, 500)
    apply_window_icon(help_win)

    canvas = tk.Canvas(help_win)
    scrollbar = tk.Scrollbar(help_win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    enable_vertical_mousewheel(canvas)

    _add_centered_heading(scrollable_frame, t("help_section_overview"))
    _add_section_text(scrollable_frame, t("help_intro"))

    _add_centered_heading(scrollable_frame, t("help_section_guide"))
    _add_section_text(scrollable_frame, t("help_steps"))

    _add_centered_heading(scrollable_frame, t("help_section_seed"))
    _add_section_text(scrollable_frame, t("help_seed"))

    _add_centered_heading(scrollable_frame, t("help_section_modes"))
    _add_section_text(scrollable_frame, t("help_modes"))

    _add_centered_heading(scrollable_frame, t("help_section_notes"))
    _add_section_text(scrollable_frame, t("help_additional"))
