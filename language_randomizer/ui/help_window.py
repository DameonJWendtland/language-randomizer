import tkinter as tk
from tkinter import ttk

from ..i18n import t
from .mousewheel import enable_vertical_mousewheel
from .window_icon import apply_window_icon


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

    label_above = ttk.Label(
        scrollable_frame,
        text=t("help_intro"),
        justify="left",
        wraplength=400,
    )
    label_above.pack(padx=10, pady=(10, 5))

    separator_1 = ttk.Separator(scrollable_frame, orient="horizontal")
    separator_1.pack(fill="x", padx=10, pady=5)

    label_mid = ttk.Label(scrollable_frame, text=t("help_how_to"), justify="left", wraplength=400)
    label_mid.pack(padx=10, pady=(5, 10))

    separator_2 = ttk.Separator(scrollable_frame, orient="horizontal")
    separator_2.pack(fill="x", padx=10)

    label_below = ttk.Label(
        scrollable_frame,
        text=t("help_steps"),
        justify="left",
        wraplength=400,
    )
    label_below.pack(padx=10, pady=(5, 10))

    separator_3 = ttk.Separator(scrollable_frame, orient="horizontal")
    separator_3.pack(fill="x", padx=10)

    label_additional = ttk.Label(
        scrollable_frame,
        text=t("help_additional"),
        justify="left",
        wraplength=400,
    )
    label_additional.pack(padx=10, pady=(10, 5))
