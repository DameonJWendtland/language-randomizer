from ..paths import ICON_PATH


def apply_window_icon(window):
    if not ICON_PATH.exists():
        return
    try:
        window.iconbitmap(str(ICON_PATH))
    except Exception:
        pass
