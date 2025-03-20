import tkinter as tk
from gui import create_main_gui

def main():
    root = tk.Tk()
    root.title("Language Randomizer")
    create_main_gui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
