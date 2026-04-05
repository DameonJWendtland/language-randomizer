import tkinter as tk
import tkinter.font as tk_font
import webbrowser
from tkinter import ttk

from .window_icon import apply_window_icon


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
    theme_entry = ttk.Entry(main_frame)
    theme_entry.pack(pady=5, fill="x")

    apply_btn = ttk.Button(main_frame, text="Apply", command=lambda: apply_settings(font_dropdown, theme_entry))
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


def apply_settings(font_dropdown, theme_entry):
    selected_font = font_dropdown.get()
    root = tk._default_root
    if root is not None:
        root.option_add("*Font", f"{selected_font} 12")
    print("Applied font:", selected_font)


def open_menu():
    menu_win = tk.Toplevel()
    menu_win.title("Menu")
    menu_win.geometry("400x300")
    apply_window_icon(menu_win)

    main_frame = ttk.Frame(menu_win, padding=10)
    main_frame.pack(fill="both", expand=True)

    show_main_menu(menu_win, main_frame)
