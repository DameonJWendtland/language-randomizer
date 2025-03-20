import tkinter as tk
from tkinter import ttk


def open_help():
    help_win = tk.Toplevel()
    help_win.title("Help")

    label_above = tk.Label(help_win, text=(
        "This program should not be used as a serious translator since the precision is not that good. "
        "Rather use DeepL or something else :)"
    ), justify="left", wraplength=400)
    label_above.pack(padx=10, pady=(10, 5))

    separator_1 = ttk.Separator(help_win, orient='horizontal')
    separator_1.pack(fill='x', padx=10, pady=5)

    label_mid = tk.Label(help_win, text=(
        "↓ How to use ↓"
    ), justify="left", wraplength=400)
    label_mid.pack(padx=10, pady=(5, 10))

    separator_2 = ttk.Separator(help_win, orient='horizontal')
    separator_2.pack(fill='x', padx=10)

    label_below = tk.Label(help_win, text=(
        "1. Write something into the text field below the \"Input:\" label you want to be translated.\n\n"
        "2. Select a language you want the result is in.\n\n"
        "\t2.1. (optional) You may now click on the \"Options\" button.\n"
        "\t2.2. (optional) Now you can select languages which must be used during the random translation process. (Forced languages)\n"
        "\t2.3. (optional) Press \"Apply\".\n\n"
        "3. Type a positive integer into the field below the \"Randomized iterations:\" label. It sets how many iterations you want of language randomization.\n(Default is 1)*\n\n"
        "4. Click \"Translate Text\" to start the random translation process.\n\n\n"
        "* NOTE: if you selected forced languages (fl) and the interation value (3rd point) is lower than the total of selected languages (fl + target lang) the forced languages are still being used!"

    ), justify="left", wraplength=400)
    label_below.pack(padx=10, pady=(5, 10))


    separator_3 = ttk.Separator(help_win, orient='horizontal')
    separator_3.pack(fill='x', padx=10)


    label_additional = tk.Label(help_win, text=(
        "Since it's a randomizer all languages will be chosen randomly. Languages may be used more than once, but not in a row (e.g. maltese -> maltese won't happen, but maybe maltese -> urdu -> maltese).\n"
        "Also, if you selected forced languages they will be used at random once. If they occur twice it's not because you selected them, it is because the randomizer used one of them again."
    ), justify="left", wraplength=400)

    label_additional.pack(padx=10, pady=(10, 5))


