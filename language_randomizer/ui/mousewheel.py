import sys


def _scroll_canvas(canvas, event):
    event_num = getattr(event, "num", None)
    if event_num == 4:
        canvas.yview_scroll(-1, "units")
        return
    if event_num == 5:
        canvas.yview_scroll(1, "units")
        return

    delta = getattr(event, "delta", 0)
    if not delta:
        return

    if sys.platform == "darwin":
        step = -1 * int(delta)
    else:
        step = -1 * int(delta / 120)
    if step:
        canvas.yview_scroll(step, "units")


def enable_vertical_mousewheel(canvas):
    def _on_mousewheel(event):
        _scroll_canvas(canvas, event)

    def _bind_all(_event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

    def _unbind_all(_event):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    canvas.bind("<Enter>", _bind_all)
    canvas.bind("<Leave>", _unbind_all)
