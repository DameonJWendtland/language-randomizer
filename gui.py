import tkinter as tk
from tkinter import ttk
import threading
import queue
import translator
from translator import randomizer, supported_languages, get_translation_steps
from options import open_options
from help_window import open_help
from show_steps import show_translation_steps
from menu import open_menu  


class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = completion_list
        self['values'] = self._completion_list

    def autocomplete(self, event=None):
        if event.keysym in ("BackSpace", "Left", "Right", "Return", "Escape"):
            return
        typed = self.get()
        if typed == "":
            filtered = self._completion_list
        else:
            filtered = [item for item in self._completion_list if item.lower().startswith(typed.lower())]
        self['values'] = filtered
        self.set(typed)
        self.icursor(tk.END)
        self.selection_clear()
        if filtered:
            try:
                self.current(-1)
            except tk.TclError:
                pass
        self.after(10, self.open_dropdown)

    def open_dropdown(self):
        try:
            self.tk.call('ttk::combobox::popdown', self)
        except tk.TclError:
            pass

def create_main_gui(root):
    style = ttk.Style()
    style.configure("Valid.TCombobox", fieldbackground="white")
    style.configure("Invalid.TCombobox", fieldbackground="lightcoral")
    style.map("Invalid.TCombobox",
              fieldbackground=[("!disabled", "lightcoral"), ("active", "lightcoral")])

    progress_queue = queue.Queue()
    
    top_frame = ttk.Frame(root)
    top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    top_frame.columnconfigure(0, weight=1)

    menu_button = ttk.Button(top_frame, text="Menu", command=open_menu, width=5)
    menu_button.pack(side="right", padx=(0, 5), pady=5)

    help_button = ttk.Button(top_frame, text="?", command=open_help, width=3)
    help_button.pack(side="right", padx=(0, 5), pady=5)
    
    left_frame = ttk.Frame(root)
    left_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    
    right_frame = ttk.Frame(root)
    right_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)

    input_label = ttk.Label(left_frame, text="Input:")
    input_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
    text_field = tk.Text(left_frame, wrap=tk.WORD)
    text_field.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    text_field.insert("1.0", "Insert your Text here...")
    
    lang_label = ttk.Label(left_frame, text="Select target language:")
    lang_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 2))
    
    language_selector = tk.StringVar(left_frame)
    language_selector.set(supported_languages[0])
    language_dropdown = AutocompleteCombobox(left_frame, textvariable=language_selector, state="normal")
    language_dropdown.set_completion_list(supported_languages)
    language_dropdown.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
    language_dropdown.bind('<KeyRelease>', language_dropdown.autocomplete)

    options_button = ttk.Button(left_frame, text="Options", command=open_options)
    options_button.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
    
    iter_label = ttk.Label(left_frame, text="Randomized iterations:")
    iter_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 2))
    
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

    validate_command = (left_frame.register(validate_input), '%P')
    number_entry = tk.Entry(left_frame, textvariable=iteration_var, validate="key", validatecommand=validate_command)
    number_entry.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

    progress_bar = ttk.Progressbar(left_frame, orient="horizontal", length=200, mode="determinate")
    progress_bar.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=(10,2))
    
    translate_button = ttk.Button(left_frame, text="Translate Text")
    translate_button.grid(row=7, column=0, columnspan=2, sticky="ew", padx=5, pady=(2,5))
    
    for i in range(8):
        left_frame.rowconfigure(i, weight=0)
    left_frame.rowconfigure(1, weight=1)  

    def check_validity(*args):
        current_language = language_selector.get()
        iter_text = iteration_var.get().strip()
        if current_language == "":
            language_dropdown.configure(style="Invalid.TCombobox")
            language_dropdown['values'] = supported_languages
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
    
    output_label = ttk.Label(right_frame, text="Output:")
    output_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
    output_text = tk.Text(right_frame, wrap=tk.WORD)
    output_text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    output_text.insert("1.0", "")
    output_text.config(state="disabled")
    
    used_lang_label = ttk.Label(right_frame, text="Used Languages:")
    used_lang_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

    show_steps_btn = ttk.Button(right_frame, text="Show Steps", command=lambda: show_translation_steps())
    show_steps_btn.grid(row=2, column=1, sticky="e", padx=5, pady=5)
    
    used_lang_text = tk.Text(right_frame, wrap=tk.WORD, height=3)
    used_lang_text.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    used_lang_text.config(state="disabled")

    for i in range(4):
        right_frame.rowconfigure(i, weight=0)
    right_frame.rowconfigure(1, weight=1)  

    def update_progress_bar(value):
        progress_bar['value'] = value
        root.update_idletasks()

    def check_queue():
        try:
            while True:
                val = progress_queue.get_nowait()
                update_progress_bar(val)
        except queue.Empty:
            pass
        root.after(100, check_queue)

    def on_button_click():
        entered_text = text_field.get("1.0", tk.END).strip()
        if entered_text:
            translate_button.config(state="disabled")
            threading.Thread(target=run_randomizer, args=(entered_text,)).start()

    def run_randomizer(text):
        result_text, lang_chain, selected_language_name = randomizer(text, language_selector, right_frame, progress_queue)
        
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.insert("1.0", result_text)
        output_text.config(state="disabled")

        
        used_lang_text.config(state="normal")
        used_lang_text.delete("1.0", tk.END)
        used_lang_text.insert("1.0", lang_chain + f"\nTarget language: [{selected_language_name}]")
        used_lang_text.config(state="disabled")

        root.after(0, lambda: translate_button.config(state="normal"))

    translate_button.config(command=on_button_click)
    check_queue()

    bottom_frame = ttk.Frame(root)
    bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    credit_label = ttk.Label(bottom_frame, text="by D. J. Wendtland", font=("Helvetica", 8), foreground="grey")
    credit_label.pack(side="left", padx=5, pady=5)
