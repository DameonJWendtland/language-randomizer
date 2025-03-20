import time
import re
from googletrans import Translator, LANGUAGES
import tkinter as tk
from tkinter import ttk
import random as rdm
import threading
import queue

language_name_to_code = {value: key for key, value in LANGUAGES.items()}
supported_languages = list(LANGUAGES.values())
target_languages = list(LANGUAGES.keys())

timeOutCounter = 0
setLoopTimes = 1
translator = Translator()
progress_queue = queue.Queue()

usedLanguages = []
detectedLanguage = ""
forcedLanguages = []
forced_vars = {}

def safe_translate(text, dest_language_code, max_retries=3):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    translated_sentences = []
    for sentence in sentences:
        if sentence.strip():
            retries = 0
            while retries < max_retries:
                try:
                    result = translator.translate(sentence, dest=dest_language_code)
                    if result is not None and result.text:
                        translated_sentences.append(result.text)
                        break
                    else:
                        raise ValueError("No translation received")
                except Exception as e:
                    print(f"Error translating sentence '{sentence}': {e}")
                    retries += 1
                    time.sleep(1)
                    if retries == max_retries:
                        print(f"Translation for sentence '{sentence}' failed. Using original sentence.")
                        translated_sentences.append(sentence)
        else:
            translated_sentences.append(sentence)
    return " ".join(translated_sentences)

def language(text, value):
    max_retries = 3
    retries = 0
    if 0 < value <= len(supported_languages):
        dest_language_name = supported_languages[value - 1]
        usedLanguages.append(dest_language_name)
        dest_language_code = language_name_to_code.get(dest_language_name)
        while retries < max_retries:
            try:
                translated_text = safe_translate(text, dest_language_code)
                return translated_text
            except Exception as e:
                print(f"Error occurred: {e}, trying again...")
                global timeOutCounter
                timeOutCounter += 1
                retry_label = tk.Label(root, text=("Total Time Outs: " + str(timeOutCounter)))
                retry_label.grid(row=99, column=0, sticky="ew")
                retries += 1
                time.sleep(1)
        return text
    else:
        return text

def randomizer(text, queue):
    global detectedLanguage
    detectedLanguage = translator.detect(text).lang
    detectedLanguage = LANGUAGES.get(detectedLanguage, "Unknown")
    selected_language_name = language_selector.get()
    selected_language_index = supported_languages.index(selected_language_name)
    selected_language_code = target_languages[selected_language_index]
    num_steps = setLoopTimes - 1
    if forcedLanguages:
        num_steps = max(num_steps, len(forcedLanguages))
    forced_count = len(forcedLanguages)
    forced_positions = []
    forced_order = []
    if forced_count > 0:
        forced_positions = rdm.sample(range(num_steps), forced_count)
        forced_positions.sort()
        forced_order = list(forcedLanguages)
        rdm.shuffle(forced_order)
    for i in range(num_steps):
        if forced_count > 0 and i in forced_positions:
            forced_lang = forced_order[forced_positions.index(i)]
            forced_index = supported_languages.index(forced_lang) + 1
            text = language(text, forced_index)
        else:
            if usedLanguages:
                last_language = usedLanguages[-1]
                candidate_indices = [i for i in range(1, len(supported_languages) + 1) if supported_languages[i - 1] != last_language]
                random_value = rdm.choice(candidate_indices)
            else:
                random_value = rdm.randint(1, len(supported_languages))
            text = language(text, random_value)
        print(text)
        queue.put(100 * (i + 1) / num_steps if num_steps > 0 else 100)
    text = safe_translate(text, selected_language_code)
    for widget in right_frame.winfo_children():
        widget.destroy()
    out_label = tk.Label(right_frame, text="Output:")
    out_label.grid(row=0, column=0, sticky="ew")
    output_text = tk.Text(right_frame, wrap=tk.WORD)
    output_text.grid(row=1, column=0, sticky="nsew")
    output_text.insert("1.0", text)
    output_text.config(state="disabled")
    print(text)
    queue.put(100)
    lang_chain = "Detected language: (" + detectedLanguage + ")"
    for lang in usedLanguages:
        lang_chain += " -> " + lang
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
    usedLanguages.clear()
    detectedLanguage = ""

def update_progress_bar(value):
    progress_bar['value'] = value
    root.update_idletasks()

def check_queue():
    while not progress_queue.empty():
        progress = progress_queue.get()
        update_progress_bar(progress)
    root.after(100, check_queue)

def start_randomizer_thread(text):
    randomizer_thread = threading.Thread(target=randomizer, args=(text, progress_queue))
    randomizer_thread.start()
    root.after(100, check_queue)

def on_button_click():
    entered_text = text_field.get("1.0", tk.END).strip()
    if entered_text:
        start_randomizer_thread(entered_text)

def validate_input(new_value):
    global setLoopTimes
    if new_value == "":
        return True
    try:
        setLoopTimes = int(new_value)
        return setLoopTimes > 0
    except ValueError:
        return False

def open_options():
    options_win = tk.Toplevel(root)
    options_win.title("Options - Force Languages")
    global forced_vars
    forced_vars = {}
    frame = tk.Frame(options_win)
    frame.pack(padx=10, pady=10)
    for i, lang in enumerate(supported_languages):
        var = tk.BooleanVar()
        forced_vars[lang] = var
        chk = tk.Checkbutton(frame, text=lang, variable=var)
        chk.grid(row=i // 5, column=i % 5, sticky="w", padx=5, pady=5)
    def apply_options():
        global forcedLanguages
        forcedLanguages = [lang for lang, var in forced_vars.items() if var.get()]
        options_win.destroy()
        print("Forced languages:", forcedLanguages)
    apply_btn = tk.Button(options_win, text="Apply", command=apply_options)
    apply_btn.pack(pady=10)

root = tk.Tk()
root.title("Language Randomizer by D. J. Wendtland")
left_frame = tk.Frame(root)
left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
right_frame = tk.Frame(root)
right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
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
label = tk.Label(left_frame, text="How many times it shall be translated:")
label.grid(row=count, column=0, columnspan=2, sticky="ew")
count += 1
validate_command = (left_frame.register(validate_input), '%P')
number_entry = tk.Entry(left_frame, validate="key", validatecommand=validate_command)
number_entry.grid(row=count, column=0, columnspan=2, sticky="ew")
count += 1
progress_bar = ttk.Progressbar(left_frame, orient="horizontal", length=200, mode="determinate")
progress_bar.grid(row=count, column=0, columnspan=2, sticky="ew")
count += 1
button = tk.Button(left_frame, text="Translate Text", command=on_button_click)
button.grid(row=count, column=0, columnspan=2, sticky="ew")
count += 1
left_frame.grid_columnconfigure(0, weight=1)
left_frame.grid_columnconfigure(1, weight=1)
left_frame.grid_rowconfigure(1, weight=1)
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_rowconfigure(1, weight=1)
right_frame.grid_rowconfigure(3, weight=1)
root.mainloop()
