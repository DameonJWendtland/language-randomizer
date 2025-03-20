from ttkthemes import ThemedTk
from gui import create_main_gui

def main():
    root = ThemedTk(theme="classic")
    root.title("Language Randomizer")
    create_main_gui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
