import time
import re
from googletrans import Translator, LANGUAGES
import tkinter as tk
from tkinter import ttk
import random as rdm
import threading
import queue

# Erstellen einer Mapping-Dictionary, um Sprachname -> Sprachcode zu erhalten
language_name_to_code = {value: key for key, value in LANGUAGES.items()}

supported_languages = list(LANGUAGES.values())
target_languages = list(LANGUAGES.keys())

timeOutCounter = 0
setLoopTimes = 1
translator = Translator()

progress_queue = queue.Queue()

usedLanguages = []
detectedLanguage = ""

def safe_translate(text, dest_language_code, max_retries=3):
    """
    Tranlates sentence wise. If an error occurs, the translation will be retried {{max_retries}} times.
    If translation fails the original sentence is being used.
    """
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
                        raise ValueError("Keine Übersetzung erhalten")
                except Exception as e:
                    print(f"Fehler bei der Übersetzung des Satzes '{sentence}': {e}")
                    retries += 1
                    time.sleep(1)  # kurze Pause vor erneutem Versuch
                    if retries == max_retries:
                        print(f"Übersetzung von Satz '{sentence}' fehlgeschlagen. Ursprünglicher Satz wird verwendet.")
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
                print(f"Fehler aufgetreten: {e}, versuche es erneut...")
                global timeOutCounter
                timeOutCounter += 1
                retry_label = tk.Label(root, text=("Total Time Outs: " + str(timeOutCounter)))
                retry_label.grid(row=count, column=0, sticky="ew")
                retries += 1
                time.sleep(1)
        return text
    else:
        return text

def randomizer(text, queue):
    global detectedLanguage

    detectedLanguage = translator.detect(text).lang
    detectedLanguage = LANGUAGES.get(detectedLanguage, "Unbekannt")

    selected_language_name = language_selector.get()
    selected_language_index = supported_languages.index(selected_language_name)
    selected_language_code = target_languages[selected_language_index]

    for i in range(setLoopTimes - 1):
        random_value = rdm.randint(1, len(supported_languages))
        text = language(text, random_value)
        print(text)
        queue.put(100 * (i + 1) / (setLoopTimes - 1) if setLoopTimes > 1 else 100)

    text = safe_translate(text, selected_language_code)

    out_label = tk.Label(root, text="Output:")
    out_label.grid(row=0, column=1, sticky="ew")

    output_text = tk.Text(root, wrap=tk.WORD)
    output_text.grid(row=1, column=1, sticky="nsew")
    output_text.insert("1.0", text)
    output_text.config(state="disabled")
    print(text)
    queue.put(100)

    lang_chain = "Detected language: ("+detectedLanguage+")"
    for lang in usedLanguages:
        lang_chain += " -> " + lang

    lang_used_label = tk.Label(root, text="Used Languages: \n")
    lang_used_label.grid(row=2, column=1, sticky="ew")

    detectedLanguagesDisplay = tk.Text(root, wrap=tk.WORD, height=3, width=30)
    detectedLanguagesDisplay.insert("1.0", lang_chain + " -> " + selected_language_name)
    detectedLanguagesDisplay.grid(row=3, column=1, sticky="ew")
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

count = 0
root = tk.Tk()
root.title("Language Randomizer by D. J. Wendtland")

label = tk.Label(root, text="Input:")
label.grid(row=count, column=0, sticky="ew")
count += 1

text_field = tk.Text(root, wrap=tk.WORD)
text_field.grid(row=count, column=0, sticky="nsew")

text_field.insert("1.0", "Insert your Text here...")
count += 1

label = tk.Label(root, text="Select target language:")
label.grid(row=count, column=0, sticky="ew")
count += 1

language_selector = tk.StringVar(root)
language_selector.set(supported_languages[0])
language_dropdown = tk.OptionMenu(root, language_selector, *supported_languages)
language_dropdown.grid(row=count, column=0, sticky="ew")
count += 1

label = tk.Label(root, text="How many times it shall be translated:")
label.grid(row=count, column=0, sticky="ew")
count += 1

validate_command = (root.register(validate_input), '%P')
number_entry = tk.Entry(root, validate="key", validatecommand=validate_command)
number_entry.grid(row=count, column=0, sticky="ew")
count += 1

progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress_bar.grid(row=count, column=0, sticky="ew")
count += 1

button = tk.Button(root, text="Translate Text", command=on_button_click)
button.grid(row=count, column=0, sticky="ew")
count += 1

label = tk.Label(root, text="")
label.grid(row=count, column=0, sticky="ew")
count += 1

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=0)
root.grid_rowconfigure(3, weight=0)
root.grid_rowconfigure(4, weight=0)
root.grid_rowconfigure(5, weight=0)

root.mainloop()
