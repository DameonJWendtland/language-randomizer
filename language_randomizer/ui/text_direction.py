import unicodedata

RTL_BIDI_CLASSES = {"R", "AL", "AN"}


def has_rtl_text(text):
    for char in text:
        if not char.strip():
            continue
        if unicodedata.bidirectional(char) in RTL_BIDI_CLASSES:
            return True
    return False


def set_text_widget_content(text_widget, text):
    text_widget.config(state="normal")
    text_widget.delete("1.0", "end")
    text_widget.tag_configure("dir_ltr", justify="left")
    text_widget.tag_configure("dir_rtl", justify="right")

    if has_rtl_text(text):
        # Prefix with RLM to improve mixed punctuation/number rendering.
        text_widget.insert("1.0", "\u200f" + text, ("dir_rtl",))
    else:
        text_widget.insert("1.0", text, ("dir_ltr",))

    text_widget.config(state="disabled")
