import tkinter as tk
import tkinter.font as tk_font
from tkinter import ttk

from .settings_store import load_settings

_NAMED_FONTS = (
    "TkDefaultFont",
    "TkTextFont",
    "TkFixedFont",
    "TkMenuFont",
    "TkHeadingFont",
    "TkCaptionFont",
    "TkSmallCaptionFont",
    "TkIconFont",
    "TkTooltipFont",
)

_CONTENT_NAMED_FONTS = (
    "TkTextFont",
    "TkFixedFont",
)

_TTK_STYLE_NAMES = (
    ".",
    "TLabel",
    "TButton",
    "TCheckbutton",
    "TRadiobutton",
    "TMenubutton",
    "TLabelframe",
    "TLabelframe.Label",
    "TNotebook.Tab",
    "Treeview",
    "Treeview.Heading",
    "TScale",
    "TEntry",
    "TCombobox",
    "TSpinbox",
)

_CONTENT_WIDGET_TYPES = (
    tk.Text,
    tk.Entry,
    tk.Listbox,
    tk.Spinbox,
    ttk.Entry,
    ttk.Combobox,
    ttk.Spinbox,
)

_DEFAULT_NAMED_FONT_CONFIGS = {}
_DEFAULT_TTK_STYLE_FONTS = {}


def _remember_default_named_fonts():
    if _DEFAULT_NAMED_FONT_CONFIGS:
        return

    for font_name in _NAMED_FONTS:
        try:
            actual = tk_font.nametofont(font_name).actual()
        except tk.TclError:
            continue

        _DEFAULT_NAMED_FONT_CONFIGS[font_name] = {
            key: actual.get(key)
            for key in ("family", "size", "weight", "slant", "underline", "overstrike")
        }


def _should_update_widget(widget, apply_to_all):
    if apply_to_all:
        return True
    return isinstance(widget, _CONTENT_WIDGET_TYPES)


def _remember_default_ttk_style_fonts(root):
    if _DEFAULT_TTK_STYLE_FONTS:
        return

    style = ttk.Style(root)
    for style_name in _TTK_STYLE_NAMES:
        try:
            _DEFAULT_TTK_STYLE_FONTS[style_name] = style.lookup(style_name, "font")
        except tk.TclError:
            _DEFAULT_TTK_STYLE_FONTS[style_name] = ""


def _build_font_spec_from_descriptor(font_descriptor, font_family):
    if isinstance(font_descriptor, tk_font.Font):
        actual = font_descriptor.actual()
    else:
        actual = tk_font.Font(font=font_descriptor).actual()

    font_parts = [font_family, actual.get("size", 10)]
    if actual.get("weight") == "bold":
        font_parts.append("bold")
    if actual.get("slant") == "italic":
        font_parts.append("italic")
    if actual.get("underline"):
        font_parts.append("underline")
    if actual.get("overstrike"):
        font_parts.append("overstrike")
    return tuple(font_parts)


def _apply_ttk_style_fonts(root, font_family):
    _remember_default_ttk_style_fonts(root)
    style = ttk.Style(root)

    for style_name, default_font in _DEFAULT_TTK_STYLE_FONTS.items():
        try:
            font_source = default_font or tk_font.nametofont("TkDefaultFont")
            style.configure(style_name, font=_build_font_spec_from_descriptor(font_source, font_family))
        except tk.TclError:
            continue


def _configure_widget_font(widget, current_font, font_family, apply_to_all):
    try:
        named_font = tk_font.nametofont(current_font)
    except tk.TclError:
        named_font = None

    if named_font is not None:
        named_font_name = str(current_font)
        if apply_to_all or named_font_name in _CONTENT_NAMED_FONTS:
            named_font.configure(family=font_family)
            return

        widget_font = tk_font.Font(font=named_font)
        widget_font.configure(family=font_family)
        widget.configure(font=widget_font)
        return

    resolved_font = tk_font.Font(font=current_font)
    resolved_font.configure(family=font_family)
    widget.configure(font=resolved_font)


def apply_font_family(root, font_family, apply_to_all=True):
    if root is None or not font_family:
        return

    _remember_default_named_fonts()
    if apply_to_all:
        _apply_ttk_style_fonts(root, font_family)

    named_fonts = _NAMED_FONTS if apply_to_all else _CONTENT_NAMED_FONTS
    for font_name in named_fonts:
        try:
            tk_font.nametofont(font_name).configure(family=font_family)
        except tk.TclError:
            pass

    def _update_widget_fonts(widget):
        if not _should_update_widget(widget, apply_to_all):
            for child in widget.winfo_children():
                _update_widget_fonts(child)
            return

        try:
            current_font = widget.cget("font")
        except tk.TclError:
            current_font = ""

        if current_font:
            try:
                _configure_widget_font(widget, current_font, font_family, apply_to_all)
            except tk.TclError:
                pass

        for child in widget.winfo_children():
            _update_widget_fonts(child)

    _update_widget_fonts(root)
    root.update_idletasks()


def reset_named_fonts(root=None):
    _remember_default_named_fonts()
    for font_name, font_config in _DEFAULT_NAMED_FONT_CONFIGS.items():
        try:
            tk_font.nametofont(font_name).configure(**font_config)
        except tk.TclError:
            pass

    if root is None:
        root = tk._default_root
    if root is None:
        return

    _remember_default_ttk_style_fonts(root)
    style = ttk.Style(root)
    for style_name, font_value in _DEFAULT_TTK_STYLE_FONTS.items():
        try:
            style.configure(style_name, font=font_value)
        except tk.TclError:
            continue


def apply_saved_font(root):
    settings = load_settings()
    font_family = settings.get("font_family", "")
    if not font_family:
        return

    apply_to_all = bool(settings.get("font_apply_globally", True))
    apply_font_family(root, font_family, apply_to_all=apply_to_all)
