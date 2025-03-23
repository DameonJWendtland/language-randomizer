import tkinter as tk
from tkinter import ttk


def open_menu():
    menu_win = tk.Toplevel()
    menu_win.title("Menu")
    menu_win.geometry("400x300")
    menu_win.iconbitmap("C:/Users/micro/PycharmProjects/language-randomizer/translating.ico")

    label = ttk.Label(menu_win, text="This is the menu window!", font=("Helvetica", 14))
    label.pack(padx=20, pady=20)

    example_button = ttk.Button(menu_win, text="Close", command=menu_win.destroy)
    example_button.pack(pady=10)