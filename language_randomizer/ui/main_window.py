import queue
import threading
import tkinter as tk
from tkinter import ttk

from .. import translator
from ..i18n import t
from ..translator import randomizer, supported_languages
from .compare_view import open_compare_view
from .context_menu import bind_context_menu
from .help_window import open_help
from .menu import open_menu
from .options import open_options
from .show_steps import show_translation_steps
from .text_direction import set_text_widget_content


class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._completion_list = []
        self._popup = None
        self._listbox = None
        self._filtered = []
        self._click_binding_id = None

    def set_completion_list(self, completion_list):
        self._completion_list = completion_list
        self["values"] = self._completion_list

    def autocomplete(self, event=None):
        if event and event.keysym in ("Up", "Down", "Return", "Escape", "Tab"):
            return

        typed = self.get()
        if typed == "":
            filtered = self._completion_list
        else:
            filtered = [item for item in self._completion_list if typed.lower() in item.lower()]

        self._filtered = filtered
        self["values"] = filtered if filtered else self._completion_list
        if filtered:
            if typed.strip():
                self.show_suggestions(filtered)
            else:
                self.hide_suggestions()
        else:
            self.hide_suggestions()

    def show_suggestions(self, suggestions):
        if self._popup is None or not self._popup.winfo_exists():
            self._popup = tk.Toplevel(self)
            self._popup.overrideredirect(True)
            self._popup.transient(self.winfo_toplevel())

            self._listbox = tk.Listbox(self._popup, height=6, activestyle="dotbox", takefocus=0)
            self._listbox.pack(fill="both", expand=True)
            self._listbox.bind("<Button-1>", self.on_listbox_click)
            self._listbox.bind("<Escape>", self.on_escape)
            self._click_binding_id = self.winfo_toplevel().bind("<Button-1>", self.on_global_click, add="+")

        self._popup.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        width = self.winfo_width()
        height = min(max(len(suggestions), 1), 8)
        self._popup.geometry(f"{width}x{(height * 22)}+{x}+{y}")
        self._popup.lift()

        self._listbox.delete(0, tk.END)
        for item in suggestions[:50]:
            self._listbox.insert(tk.END, item)

        if self._listbox.size() > 0:
            self._listbox.selection_clear(0, tk.END)
            self._listbox.selection_set(0)
            self._listbox.activate(0)

    def hide_suggestions(self):
        if self._popup is not None and self._popup.winfo_exists():
            self._popup.destroy()
        if self._click_binding_id is not None:
            try:
                self.winfo_toplevel().unbind("<Button-1>", self._click_binding_id)
            except tk.TclError:
                pass
            self._click_binding_id = None
        self._popup = None
        self._listbox = None

    def on_listbox_click(self, event=None):
        if self._listbox is None:
            return "break"

        if event is not None:
            index = self._listbox.nearest(event.y)
            if index < 0:
                return "break"
            value = self._listbox.get(index)
        else:
            selection = self._listbox.curselection()
            if not selection:
                return "break"
            value = self._listbox.get(selection[0])

        self.set(value)
        self.icursor(tk.END)
        self.event_generate("<<ComboboxSelected>>")
        self.hide_suggestions()
        return "break"

    def on_down(self, event=None):
        if self._listbox is None or self._listbox.size() == 0:
            if self._completion_list:
                self.show_suggestions(self._completion_list)
            return "break"
        self.move_selection(1)
        return "break"

    def on_up(self, event=None):
        if self._listbox is None or self._listbox.size() == 0:
            return "break"
        self.move_selection(-1)
        return "break"

    def on_return(self, event=None):
        if self._listbox is None or self._listbox.size() == 0:
            return None
        self.on_listbox_click()
        return "break"

    def on_escape(self, event=None):
        self.hide_suggestions()
        return "break"

    def on_global_click(self, event=None):
        if self._popup is None or self._listbox is None:
            return None

        clicked_widget = event.widget
        if clicked_widget in (self, self._listbox):
            return None

        widget_name = str(clicked_widget)
        popup_name = str(self._popup)
        if widget_name.startswith(popup_name):
            return None

        self.hide_suggestions()
        return None

    def move_selection(self, delta):
        if self._listbox is None or self._listbox.size() == 0:
            return
        current = self._listbox.curselection()
        index = current[0] if current else 0
        next_index = max(0, min(self._listbox.size() - 1, index + delta))
        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(next_index)
        self._listbox.activate(next_index)
        self._listbox.see(next_index)


def create_main_gui(root):
    style = ttk.Style()
    style.configure("Valid.TCombobox", fieldbackground="white")
    style.configure("Invalid.TCombobox", fieldbackground="lightcoral")
    style.map(
        "Invalid.TCombobox",
        fieldbackground=[("!disabled", "lightcoral"), ("active", "lightcoral")],
    )

    progress_queue = queue.Queue()
    last_run_data = {"original": "", "final": ""}

    def refresh_ui(force_rebuild=False):
        root.title(t("app_title"))
        if force_rebuild:
            for widget in root.winfo_children():
                widget.destroy()
            create_main_gui(root)

    top_frame = ttk.Frame(root)
    top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    top_frame.columnconfigure(0, weight=1)

    menu_button = ttk.Button(
        top_frame,
        text=t("menu_button"),
        command=lambda: open_menu(on_ui_refresh=refresh_ui),
        width=7,
    )
    menu_button.pack(side="left", padx=(5, 0), pady=5)

    help_button = ttk.Button(top_frame, text="?", command=open_help, width=3)
    help_button.pack(side="right", padx=(0, 5), pady=5)

    left_frame = ttk.Frame(root)
    left_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    right_frame = ttk.Frame(root)
    right_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)

    input_label = ttk.Label(left_frame, text=t("input_label"))
    input_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    text_field = tk.Text(left_frame, wrap=tk.WORD)
    text_field.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    text_field.insert("1.0", t("input_placeholder"))
    bind_context_menu(text_field)

    lang_label = ttk.Label(left_frame, text=t("target_language_label"))
    lang_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 2))

    language_selector = tk.StringVar(left_frame)
    language_selector.set(supported_languages[0])

    language_dropdown = AutocompleteCombobox(left_frame, textvariable=language_selector, state="normal")
    language_dropdown.set_completion_list(supported_languages)
    language_dropdown.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
    bind_context_menu(language_dropdown)
    language_dropdown.bind("<KeyRelease>", language_dropdown.autocomplete)
    language_dropdown.bind("<Down>", language_dropdown.on_down)
    language_dropdown.bind("<Up>", language_dropdown.on_up)
    language_dropdown.bind("<Return>", language_dropdown.on_return)
    language_dropdown.bind("<Escape>", language_dropdown.on_escape)

    max_forced_languages = len(supported_languages)
    forced_lang_status_var = tk.StringVar(left_frame)

    def refresh_forced_languages_label(forced_list=None):
        forced_count = len(forced_list) if forced_list is not None else len(translator.forcedLanguages)
        forced_lang_status_var.set(
            t("forced_languages_status", count=forced_count, maximum=max_forced_languages)
        )

    refresh_forced_languages_label()

    options_button = ttk.Button(
        left_frame,
        text=t("options_button"),
        command=lambda: open_options(on_apply=refresh_forced_languages_label),
    )
    options_button.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

    forced_lang_status_label = ttk.Label(left_frame, textvariable=forced_lang_status_var, foreground="grey")
    forced_lang_status_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=(2, 8))

    iter_label = ttk.Label(left_frame, text=t("iterations_label"))
    iter_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 2))

    iteration_var = tk.StringVar(left_frame)
    iteration_var.set("")

    def validate_input(new_value):
        if new_value == "":
            return True
        try:
            value = int(new_value)
            translator.setLoopTimes = value
            return value > 0
        except ValueError:
            return False

    validate_command = (left_frame.register(validate_input), "%P")
    number_entry = tk.Entry(left_frame, textvariable=iteration_var, validate="key", validatecommand=validate_command)
    number_entry.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
    bind_context_menu(number_entry)

    progress_status_var = tk.StringVar(left_frame)
    progress_status_var.set(t("progress_initial"))
    progress_status_label = ttk.Label(left_frame, textvariable=progress_status_var, foreground="grey")
    progress_status_label.grid(row=7, column=0, columnspan=2, sticky="w", padx=5, pady=(8, 2))

    progress_bar = ttk.Progressbar(left_frame, orient="horizontal", length=200, mode="determinate")
    progress_bar.grid(row=8, column=0, columnspan=2, sticky="ew", padx=5, pady=(2, 2))

    translate_button = ttk.Button(left_frame, text=t("translate_button"))
    translate_button.grid(row=9, column=0, columnspan=2, sticky="ew", padx=5, pady=(2, 5))

    for i in range(10):
        left_frame.rowconfigure(i, weight=0)
    left_frame.rowconfigure(1, weight=1)

    def check_validity(*args):
        current_language = language_selector.get()
        iter_text = iteration_var.get().strip()

        if current_language == "":
            language_dropdown.configure(style="Invalid.TCombobox")
            language_dropdown["values"] = supported_languages
        elif current_language not in supported_languages:
            language_dropdown.configure(style="Invalid.TCombobox")
        else:
            language_dropdown.configure(style="Valid.TCombobox")

        if iter_text == "":
            number_entry.config(bg="lightcoral")
        else:
            number_entry.config(bg="white")

        if current_language == "" or current_language not in supported_languages or iter_text == "":
            translate_button.config(state="disabled")
        else:
            translate_button.config(state="normal")

    language_selector.trace("w", check_validity)
    iteration_var.trace("w", check_validity)
    check_validity()

    output_label = ttk.Label(right_frame, text=t("output_label"))
    output_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    output_text = tk.Text(right_frame, wrap=tk.WORD)
    output_text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    set_text_widget_content(output_text, "")
    bind_context_menu(output_text)

    used_lang_label = ttk.Label(right_frame, text=t("used_languages_label"))
    used_lang_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

    actions_frame = ttk.Frame(right_frame)
    actions_frame.grid(row=2, column=1, sticky="e", padx=5, pady=5)

    compare_btn = ttk.Button(
        actions_frame,
        text=t("compare_button"),
        command=lambda: open_compare_view(
            root,
            last_run_data.get("original", ""),
            last_run_data.get("final", ""),
        ),
    )
    compare_btn.pack(side="right")

    show_steps_btn = ttk.Button(actions_frame, text=t("show_steps_button"), command=show_translation_steps)
    show_steps_btn.pack(side="right", padx=(0, 6))

    used_lang_text = tk.Text(right_frame, wrap=tk.WORD, height=3)
    used_lang_text.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    used_lang_text.config(state="disabled")
    bind_context_menu(used_lang_text)

    for i in range(4):
        right_frame.rowconfigure(i, weight=0)
    right_frame.rowconfigure(1, weight=1)

    def update_progress_bar(value=None, status_text=None):
        if value is not None:
            progress_bar["value"] = value
        if status_text:
            progress_status_var.set(status_text)
        root.update_idletasks()

    def check_queue():
        try:
            while True:
                payload = progress_queue.get_nowait()
                if isinstance(payload, dict):
                    update_progress_bar(
                        payload.get("progress"),
                        payload.get("status"),
                    )
                elif isinstance(payload, tuple) and len(payload) >= 2:
                    update_progress_bar(payload[0], payload[1])
                else:
                    update_progress_bar(payload)
        except queue.Empty:
            pass
        root.after(100, check_queue)

    def on_button_click():
        entered_text = text_field.get("1.0", tk.END).strip()
        if entered_text:
            last_run_data["original"] = entered_text
            progress_bar["value"] = 0
            progress_status_var.set(t("progress_preparing"))
            translate_button.config(state="disabled")
            threading.Thread(target=run_randomizer, args=(entered_text,), daemon=True).start()

    def run_randomizer(text):
        result_text, lang_chain, selected_language_name = randomizer(text, language_selector, progress_queue)
        last_run_data["final"] = result_text

        set_text_widget_content(output_text, result_text)

        used_lang_text.config(state="normal")
        used_lang_text.delete("1.0", tk.END)
        used_lang_text.insert(
            "1.0",
            lang_chain + "\n" + t("target_language_line", language=selected_language_name),
        )
        used_lang_text.config(state="disabled")

        root.after(0, lambda: translate_button.config(state="normal"))

    translate_button.config(command=on_button_click)
    check_queue()

    bottom_frame = ttk.Frame(root)
    bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    credit_label = ttk.Label(bottom_frame, text="by D. J. Wendtland", font=("Helvetica", 8), foreground="grey")
    credit_label.pack(side="left", padx=5, pady=5)
