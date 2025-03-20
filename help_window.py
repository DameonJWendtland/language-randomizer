import tkinter as tk

def open_help():
    help_win = tk.Toplevel()
    help_win.title("Help")
    help_label = tk.Label(help_win, text=(
        "This is helpful!"
    ), justify="left", wraplength=400)
    help_label.pack(padx=10, pady=10)
