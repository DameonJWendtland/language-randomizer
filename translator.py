import time
import re
import random as rdm
from googletrans import Translator, LANGUAGES

translator = Translator()
language_name_to_code = {value: key for key, value in LANGUAGES.items()}
supported_languages = list(LANGUAGES.values())
target_languages = list(LANGUAGES.keys())

timeOutCounter = 0
usedLanguages = []
detectedLanguage = ""
forcedLanguages = [] #options.py
setLoopTimes = 1


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
    global timeOutCounter, usedLanguages
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
                timeOutCounter += 1
                retries += 1
                time.sleep(1)
        return text
    else:
        return text


def randomizer(text, language_selector, right_frame, progress_queue):
    """
    Executes the translation chain.
    Expects:
        - text: Input text
        - language_selector: tk.StringVar of the dropdown (target language)
        - right_frame: Frame where the output is displayed
        - progress_queue: Queue for updating the progress display
    Returns:
        - result_text: Translated final text
        - lang_chain: String indicating the languages used
        - selected_language_name: The originally selected target language
    """
    global detectedLanguage, usedLanguages, forcedLanguages, setLoopTimes

    detected_lang_code = translator.detect(text).lang
    detectedLanguage = LANGUAGES.get(detected_lang_code, "Unknown")

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
                candidate_indices = [i for i in range(1, len(supported_languages) + 1) if
                                     supported_languages[i - 1] != last_language]
                random_value = rdm.choice(candidate_indices)
            else:
                random_value = rdm.randint(1, len(supported_languages))
            text = language(text, random_value)
        print(text)
        progress_queue.put(100 * (i + 1) / num_steps if num_steps > 0 else 100)

    text = safe_translate(text, selected_language_code)

    lang_chain = "Detected language: [" + detectedLanguage + "]"
    for lang in usedLanguages:
        lang_chain += " -> " + lang

    usedLanguages = []
    detectedLanguage = ""

    return text, lang_chain, selected_language_name
