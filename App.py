from ttkthemes import ThemedTk
from gui import create_main_gui

def main():
    root = ThemedTk(theme="default")
    root.title("Language Randomizer")
    root.iconbitmap("C:/Users/micro/PycharmProjects/language-randomizer/translating.ico")
    create_main_gui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
