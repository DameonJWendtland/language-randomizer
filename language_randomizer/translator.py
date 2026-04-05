import asyncio
import random as rdm
import re

from googletrans import LANGUAGES, Translator

language_name_to_code = {value: key for key, value in LANGUAGES.items()}
supported_languages = list(LANGUAGES.values())
target_languages = list(LANGUAGES.keys())

timeOutCounter = 0
forcedLanguages = []
activateTransliteration = False
setLoopTimes = 1
translation_steps = []

MAX_PARALLEL_SENTENCE_REQUESTS = 4
RETRY_DELAY_SECONDS = 0.6


def _console_log(message):
    try:
        print(message)
    except UnicodeEncodeError:
        fallback = str(message).encode("ascii", errors="replace").decode("ascii")
        print(fallback)


def _queue_progress(progress_queue, progress_value=None, status_text=None):
    if progress_queue is None:
        return

    payload = {}
    if progress_value is not None:
        payload["progress"] = max(0, min(100, progress_value))
    if status_text is not None:
        payload["status"] = status_text

    if payload:
        progress_queue.put(payload)


async def _translate_sentence_with_retries(translator_client, sentence, dest_language_code, max_retries=3):
    if not sentence.strip():
        return sentence, ""

    retries = 0
    while retries < max_retries:
        try:
            result = await translator_client.translate(sentence, dest=dest_language_code)
            if result is not None and getattr(result, "text", None):
                pronunciation = getattr(result, "pronunciation", "") or ""
                return result.text, pronunciation
            raise ValueError("No translation received")
        except Exception as exc:
            _console_log(f"Error translating sentence '{sentence}': {exc}")
            retries += 1
            if retries < max_retries:
                await asyncio.sleep(RETRY_DELAY_SECONDS)

    _console_log(f"Translation for sentence '{sentence}' failed. Using original sentence.")
    return sentence, ""


async def _safe_translate(translator_client, text, dest_language_code, max_retries=3):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    non_empty_sentences = [sentence for sentence in sentences if sentence.strip()]

    if len(non_empty_sentences) <= 1:
        translated_sentences = []
        pronunciation_sentences = []
        for sentence in sentences:
            translated_sentence, pronunciation = await _translate_sentence_with_retries(
                translator_client,
                sentence,
                dest_language_code,
                max_retries=max_retries,
            )
            translated_sentences.append(translated_sentence)
            pronunciation_sentences.append(pronunciation)
    else:
        concurrency = min(MAX_PARALLEL_SENTENCE_REQUESTS, max(1, len(non_empty_sentences)))
        semaphore = asyncio.Semaphore(concurrency)

        async def _translate_with_limit(sentence):
            if not sentence.strip():
                return sentence, ""
            async with semaphore:
                return await _translate_sentence_with_retries(
                    translator_client,
                    sentence,
                    dest_language_code,
                    max_retries=max_retries,
                )

        translated_pairs = await asyncio.gather(*[_translate_with_limit(sentence) for sentence in sentences])
        translated_sentences = [pair[0] for pair in translated_pairs]
        pronunciation_sentences = [pair[1] for pair in translated_pairs]

    translated_text = " ".join(translated_sentences)
    pronunciation_text = " ".join(pronunciation_sentences).strip()
    return translated_text, pronunciation_text


async def _detect_language_code(translator_client, text, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            detected = await translator_client.detect(text)
            detected_lang_code = getattr(detected, "lang", "")
            if detected_lang_code:
                return detected_lang_code
            raise ValueError("No language detected")
        except Exception as exc:
            _console_log(f"Error detecting language: {exc}")
            retries += 1
            await asyncio.sleep(RETRY_DELAY_SECONDS)

    return ""


async def _language_step(translator_client, text, value, used_languages, steps):
    global timeOutCounter

    max_retries = 3
    retries = 0

    if 0 < value <= len(supported_languages):
        dest_language_name = supported_languages[value - 1]
        used_languages.append(dest_language_name)
        dest_language_code = language_name_to_code.get(dest_language_name)

        while retries < max_retries:
            try:
                translated_text, pronunciation = await _safe_translate(
                    translator_client,
                    text,
                    dest_language_code,
                )
                steps.append((dest_language_name, translated_text, pronunciation))
                return translated_text
            except Exception as exc:
                _console_log(f"Error occurred: {exc}, trying again...")
                timeOutCounter += 1
                retries += 1
                await asyncio.sleep(RETRY_DELAY_SECONDS)

        return text

    return text


async def _randomizer_async(text, selected_language_name, progress_queue):
    global translation_steps, forcedLanguages, setLoopTimes

    steps = []
    used_languages = []

    async with Translator() as translator_client:
        detected_lang_code = await _detect_language_code(translator_client, text)
        detected_language = LANGUAGES.get(detected_lang_code, "Unknown")

        selected_language_index = supported_languages.index(selected_language_name)
        selected_language_code = target_languages[selected_language_index]

        _console_log("\nTarget language: " + selected_language_name)
        if forcedLanguages:
            _console_log("Forced languages: " + ", ".join(forcedLanguages))
        else:
            _console_log("Forced languages: none")

        num_steps = setLoopTimes - 1
        if forcedLanguages:
            num_steps = max(num_steps, len(forcedLanguages))
        total_steps = num_steps + 2
        total_iteration_display = num_steps + 1
        _queue_progress(
            progress_queue,
            progress_value=100 * 1 / total_steps,
            status_text=f"Translating to {selected_language_name} (0/{total_iteration_display})",
        )

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
                step_language = forced_lang
                _queue_progress(
                    progress_queue,
                    status_text=f"Translating to {step_language} ({i + 1}/{total_iteration_display})",
                )
                text = await _language_step(translator_client, text, forced_index, used_languages, steps)
            else:
                if used_languages:
                    last_language = used_languages[-1]
                    candidate_indices = [
                        j
                        for j in range(1, len(supported_languages) + 1)
                        if supported_languages[j - 1] != last_language
                        ]
                    random_value = rdm.choice(candidate_indices)
                else:
                    random_value = rdm.randint(1, len(supported_languages))

                step_language = supported_languages[random_value - 1]
                _queue_progress(
                    progress_queue,
                    status_text=f"Translating to {step_language} ({i + 1}/{total_iteration_display})",
                )
                text = await _language_step(translator_client, text, random_value, used_languages, steps)

            if used_languages:
                _console_log("RDM (" + used_languages[-1] + "): " + text)

            _queue_progress(progress_queue, progress_value=100 * (1 + (i + 1)) / total_steps)

        _queue_progress(
            progress_queue,
            status_text=(
                f"Translating to {selected_language_name} "
                f"({total_iteration_display}/{total_iteration_display})"
            ),
        )
        text, final_pronunciation = await _safe_translate(translator_client, text, selected_language_code)
        _queue_progress(progress_queue, progress_value=100)

    lang_chain = "Detected language: [" + detected_language + "]\n"
    if used_languages:
        lang_chain += " -> ".join(used_languages)

    steps.append((selected_language_name, text, final_pronunciation))
    translation_steps = steps

    _console_log("END (" + selected_language_name + "): " + text)

    return text, lang_chain, selected_language_name


def randomizer(text, language_selector, progress_queue):
    selected_language_name = language_selector.get()
    return asyncio.run(_randomizer_async(text, selected_language_name, progress_queue))


def get_translation_steps():
    return translation_steps
