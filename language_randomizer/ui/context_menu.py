import tkinter as tk

from ..i18n import t

_RIGHT_CLICK_EVENTS = ("<Button-3>", "<Button-2>", "<Control-Button-1>")


def _get_selected_text(widget):
    try:
        if isinstance(widget, tk.Text):
            return widget.get("sel.first", "sel.last")
        return widget.selection_get()
    except (tk.TclError, AttributeError):
        return ""


def _is_editable(widget):
    try:
        state = str(widget.cget("state"))
    except tk.TclError:
        state = "normal"
    return state not in {"disabled", "readonly"}


def _clipboard_has_text(widget):
    try:
        return bool(widget.clipboard_get())
    except tk.TclError:
        return False


def _copy(widget):
    selected_text = _get_selected_text(widget)
    if not selected_text:
        return
    widget.clipboard_clear()
    widget.clipboard_append(selected_text)


def _cut(widget):
    if not _is_editable(widget):
        return
    if isinstance(widget, tk.Text):
        selected_text = _get_selected_text(widget)
        if not selected_text:
            return
        widget.clipboard_clear()
        widget.clipboard_append(selected_text)
        widget.delete("sel.first", "sel.last")
        return
    try:
        widget.event_generate("<<Cut>>")
    except tk.TclError:
        pass


def _paste(widget):
    if not _is_editable(widget):
        return
    try:
        widget.event_generate("<<Paste>>")
    except tk.TclError:
        pass


def _select_all(widget):
    if isinstance(widget, tk.Text):
        widget.tag_add("sel", "1.0", "end-1c")
        widget.mark_set("insert", "1.0")
    else:
        try:
            widget.selection_range(0, tk.END)
            widget.icursor(tk.END)
        except tk.TclError:
            pass


def bind_context_menu(widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label=t("context_cut"), command=lambda: _cut(widget))
    menu.add_command(label=t("context_copy"), command=lambda: _copy(widget))
    menu.add_command(label=t("context_paste"), command=lambda: _paste(widget))
    menu.add_separator()
    menu.add_command(label=t("context_select_all"), command=lambda: _select_all(widget))

    def show_menu(event):
        try:
            widget.focus_set()
        except tk.TclError:
            return "break"

        has_selection = bool(_get_selected_text(widget))
        editable = _is_editable(widget)
        has_clipboard = _clipboard_has_text(widget)

        menu.entryconfigure(0, state="normal" if has_selection and editable else "disabled")
        menu.entryconfigure(1, state="normal" if has_selection else "disabled")
        menu.entryconfigure(2, state="normal" if has_clipboard and editable else "disabled")
        menu.entryconfigure(4, state="normal")

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
        return "break"

    for click_event in _RIGHT_CLICK_EVENTS:
        widget.bind(click_event, show_menu, add="+")
