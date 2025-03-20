import tkinter as tk
from tkinter import ttk
import threading, queue
import translator
from translator import randomizer, supported_languages
from options import open_options
from help_window import open_help

def create_main_gui(root):
    progress_queue = queue.Queue()
    top_frame = tk.Frame(root)
    top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    top_frame.grid_columnconfigure(0, weight=1)
    help_button = tk.Button(top_frame, text="❓", command=open_help, font=("Helvetica", 14, "bold"), width=3, height=1)
    help_button.pack(side="right", padx=5, pady=5)
    left_frame = tk.Frame(root)
    left_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    right_frame = tk.Frame(root)
    right_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)
    count = 0
    label = tk.Label(left_frame, text="Input:")
    label.grid(row=count, column=0, columnspan=2, sticky="ew")
    count += 1
    text_field = tk.Text(left_frame, wrap=tk.WORD)
    text_field.grid(row=count, column=0, columnspan=2, sticky="nsew")
    text_field.insert("1.0", "Insert your Text here...")
    count += 1
    label = tk.Label(left_frame, text="Select target language:")
    label.grid(row=count, column=0, columnspan=2, sticky="ew")
    count += 1
    language_selector = tk.StringVar(left_frame)
    language_selector.set(supported_languages[0])
    language_dropdown = ttk.Combobox(left_frame, textvariable=language_selector, values=supported_languages, state="readonly")
    language_dropdown.grid(row=count, column=0, sticky="ew")
    options_button = tk.Button(left_frame, text="Options", command=open_options)
    options_button.grid(row=count, column=1, sticky="ew")
    count += 1
    label = tk.Label(left_frame, text="Randomized iterations:")
    label.grid(row=count, column=0, columnspan=2, sticky="ew")
    count += 1
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
    number_entry = tk.Entry(left_frame, validate="key", validatecommand=validate_command)
    number_entry.grid(row=count, column=0, columnspan=2, sticky="ew")
    count += 1
    progress_bar = ttk.Progressbar(left_frame, orient="horizontal", length=200, mode="determinate")
    progress_bar.grid(row=count, column=0, columnspan=2, sticky="ew")
    count += 1
    translate_button = tk.Button(left_frame, text="Translate Text", command=lambda: on_button_click())
    translate_button.grid(row=count, column=0, columnspan=2, sticky="ew")
    count += 1
    left_frame.grid_columnconfigure(0, weight=1)
    left_frame.grid_columnconfigure(1, weight=1)
    left_frame.grid_rowconfigure(1, weight=1)
    right_frame.grid_columnconfigure(0, weight=1)
    right_frame.grid_rowconfigure(1, weight=1)
    right_frame.grid_rowconfigure(3, weight=1)
    def update_progress_bar(value):
        progress_bar['value'] = value
        root.update_idletasks()
    def check_queue():
        try:
            while True:
                progress = progress_queue.get_nowait()
                update_progress_bar(progress)
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
        for widget in right_frame.winfo_children():
            widget.destroy()
        out_label = tk.Label(right_frame, text="Output:")
        out_label.grid(row=0, column=0, sticky="ew")
        output_text = tk.Text(right_frame, wrap=tk.WORD)
        output_text.grid(row=1, column=0, sticky="nsew")
        output_text.insert("1.0", result_text)
        output_text.config(state="disabled")
        lang_used_label = tk.Label(right_frame, text="Used Languages: \n")
        lang_used_label.grid(row=2, column=0, sticky="ew")
        lang_frame = tk.Frame(right_frame)
        lang_frame.grid(row=3, column=0, sticky="nsew")
        detectedLanguagesDisplay = tk.Text(lang_frame, wrap=tk.WORD, height=3, width=30)
        detectedLanguagesDisplay.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(lang_frame, command=detectedLanguagesDisplay.yview)
        scrollbar.pack(side="right", fill="y")
        detectedLanguagesDisplay.config(yscrollcommand=scrollbar.set)
        detectedLanguagesDisplay.insert("1.0", lang_chain + " -> " + selected_language_name)
        detectedLanguagesDisplay.config(state="disabled")
        root.after(0, lambda: translate_button.config(state="normal"))
    check_queue()
    bottom_frame = tk.Frame(root)
    bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    credit_label = tk.Label(bottom_frame, text="by D. J. Wendtland", font=("Helvetica", 8), fg="grey")
    credit_label.pack(side="left", padx=5, pady=5)
