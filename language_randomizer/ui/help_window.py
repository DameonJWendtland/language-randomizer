import tkinter as tk
from tkinter import ttk

from .mousewheel import enable_vertical_mousewheel
from .window_icon import apply_window_icon


def open_help():
    help_win = tk.Toplevel()
    help_win.title("Help")
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
        text=(
            "This program is not intended for serious translation because the accuracy is limited. "
            "Use DeepL or another translator instead :)"
        ),
        justify="left",
        wraplength=400,
    )
    label_above.pack(padx=10, pady=(10, 5))

    separator_1 = ttk.Separator(scrollable_frame, orient="horizontal")
    separator_1.pack(fill="x", padx=10, pady=5)

    label_mid = ttk.Label(scrollable_frame, text="How to use", justify="left", wraplength=400)
    label_mid.pack(padx=10, pady=(5, 10))

    separator_2 = ttk.Separator(scrollable_frame, orient="horizontal")
    separator_2.pack(fill="x", padx=10)

    label_below = ttk.Label(
        scrollable_frame,
        text=(
            "1. Write the text you want to translate in the field below the \"Input:\" label.\n\n"
            "2. Select the language you want the result in.\n\n"
            "2.1. (optional) Click on the \"Options\" button.\n"
            "2.2. (optional) Select languages that must be used during the random translation process.\n"
            "2.3. (optional) Press \"Apply\".\n\n"
            "3. Enter a positive integer in the field below the \"Randomized iterations:\" label. "
            "This sets how many randomization iterations are used.\n(Default is 1)*\n\n"
            "4. Click \"Translate Text\" to start the random translation process.\n\n"
            "* NOTE: If you selected forced languages and the iteration value is lower than the total number "
            "of selected languages (forced + target), the forced languages are still used."
        ),
        justify="left",
        wraplength=400,
    )
    label_below.pack(padx=10, pady=(5, 10))

    separator_3 = ttk.Separator(scrollable_frame, orient="horizontal")
    separator_3.pack(fill="x", padx=10)

    label_additional = ttk.Label(
        scrollable_frame,
        text=(
            "Because this is a randomizer, languages are selected at random. A language may be used "
            "more than once, but not twice in a row (e.g. Maltese -> Maltese will not happen, but "
            "Maltese -> Urdu -> Maltese may happen).\n"
            "If you selected forced languages, each one is inserted once at a random position. If they appear more often, "
            "it is because the randomizer picked them again."
        ),
        justify="left",
        wraplength=400,
    )
    label_additional.pack(padx=10, pady=(10, 5))
