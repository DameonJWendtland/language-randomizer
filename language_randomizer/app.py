from ttkthemes import ThemedTk

from .ui.main_window import create_main_gui
from .ui.window_icon import apply_window_icon


def main():
    root = ThemedTk(theme="default")
    root.title("Language Randomizer")
    apply_window_icon(root)
    create_main_gui(root)
    root.mainloop()
