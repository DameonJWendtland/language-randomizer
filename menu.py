import tkinter as tk
from tkinter import ttk
import webbrowser

def open_menu():
    menu_win = tk.Toplevel()
    menu_win.title("Menu")
    menu_win.geometry("400x200")
    menu_win.iconbitmap("C:/Users/micro/PycharmProjects/language-randomizer/translating.ico")

    main_frame = ttk.Frame(menu_win, padding=10)
    main_frame.pack(fill="both", expand=True)

    header_label = ttk.Label(main_frame, text="Language Randomizer Menu", font=("Helvetica", 16, "bold"))
    header_label.pack(pady=(0, 20))

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill="x", pady=10)

    settings_btn = ttk.Button(btn_frame, text="Settings", command=lambda: print("Settings clicked"))
    settings_btn.pack(fill="x", pady=5)

    report_btn = ttk.Button(btn_frame, text="Report Bugs",
                            command=lambda: webbrowser.open("https://github.com/DameonJWendtland/language-randomizer/"))
    report_btn.pack(fill="x", pady=5)

    close_btn = ttk.Button(main_frame, text="Close", command=menu_win.destroy)
    close_btn.pack(pady=10)
