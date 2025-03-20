import tkinter as tk
from tkinter import ttk

def open_help():
    help_win = tk.Toplevel()
    help_win.title("Help")
    help_win.minsize(450, 500)
    canvas = tk.Canvas(help_win)
    scrollbar = tk.Scrollbar(help_win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    label_above = ttk.Label(scrollable_frame, text=(
        "This program should not be used as a serious translator since the precision is not that good. "
        "Rather use DeepL or something else :)"
    ), justify="left", wraplength=400)
    label_above.pack(padx=10, pady=(10, 5))
    separator_1 = ttk.Separator(scrollable_frame, orient='horizontal')
    separator_1.pack(fill='x', padx=10, pady=5)
    label_mid = ttk.Label(scrollable_frame, text="↓ How to use ↓", justify="left", wraplength=400)
    label_mid.pack(padx=10, pady=(5, 10))
    separator_2 = ttk.Separator(scrollable_frame, orient='horizontal')
    separator_2.pack(fill='x', padx=10)
    label_below = ttk.Label(scrollable_frame, text=(
        "1. Write something into the text field below the \"Input:\" label you want to be translated.\n\n"
        "2. Select a language you want the result is in.\n\n"
        "\t2.1. (optional) You may now click on the \"Options\" button.\n"
        "\t2.2. (optional) Now you can select languages which must be used during the random translation process. (Forced languages)\n"
        "\t2.3. (optional) Press \"Apply\".\n\n"
        "3. Type a positive integer into the field below the \"Randomized iterations:\" label. It sets how many iterations you want of language randomization.\n(Default is 1)*\n\n"
        "4. Click \"Translate Text\" to start the random translation process.\n\n\n"
        "* NOTE: if you selected forced languages (fl) and the iteration value (3rd point) is lower than the total of selected languages (fl + target lang) the forced languages are still being used!"
    ), justify="left", wraplength=400)
    label_below.pack(padx=10, pady=(5, 10))
    separator_3 = ttk.Separator(scrollable_frame, orient='horizontal')
    separator_3.pack(fill='x', padx=10)
    label_additional = ttk.Label(scrollable_frame, text=(
        "Since it's a randomizer all languages will be chosen randomly. Languages may be used more than once, but not in a row "
        "(e.g. Maltese -> Maltese won't happen, but maybe Maltese -> Urdu -> Maltese).\n"
        "Also, if you selected forced languages they will be used at random once. If they occur twice it's not because you selected them, "
        "it is because the randomizer used one of them again."
    ), justify="left", wraplength=400)
    label_additional.pack(padx=10, pady=(10, 5))
