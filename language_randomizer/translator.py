import asyncio
import random as rdm
import re

from googletrans import LANGUAGES, Translator

from .i18n import t

language_name_to_code = {value: key for key, value in LANGUAGES.items()}
supported_languages = list(LANGUAGES.values())
target_languages = list(LANGUAGES.keys())

timeOutCounter = 0
forcedLanguages = []
activateTransliteration = False
setLoopTimes = 1
translation_steps = []
randomSeed = None
lastUsedSeed = None

MAX_PARALLEL_SENTENCE_REQUESTS = 4
RETRY_DELAY_SECONDS = 0.6

TRANSLATION_MODES = ("normal", "chaos", "safe")
translationMode = "normal"

_HIGH_QUALITY_LANGUAGE_CODES = {
    "ar",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "fi",
    "fr",
    "he",
    "hi",
    "hu",
    "id",
    "it",
    "ja",
    "ko",
    "nl",
    "no",
    "pl",
    "pt",
    "ro",
    "ru",
    "sv",
    "th",
    "tr",
    "uk",
    "vi",
    "zh-cn",
    "zh-tw",
}

_LOW_QUALITY_LANGUAGE_CODES = {
    "ay",
    "bho",
    "co",
    "eo",
    "fy",
    "gd",
    "haw",
    "hmn",
    "ht",
    "ig",
    "ilo",
    "jv",
    "jw",
    "la",
    "lb",
    "ln",
    "lus",
    "mi",
    "mn",
    "mni-mtei",
    "my",
    "ny",
    "om",
    "qu",
    "sm",
    "sn",
    "so",
    "st",
    "su",
    "tg",
    "ti",
    "tk",
    "to",
    "ts",
    "tt",
    "ug",
    "yi",
    "yo",
    "zu",
}


def _sanitize_translation_mode(mode):
    candidate = str(mode).strip().lower() if mode else "normal"
    if candidate in TRANSLATION_MODES:
        return candidate
    return "normal"


def _get_language_quality_score(language_code):
    code = str(language_code).strip().lower() if language_code else ""
    if code in _HIGH_QUALITY_LANGUAGE_CODES:
        return 0.92
    if code in _LOW_QUALITY_LANGUAGE_CODES:
        return 0.16
    return 0.55


def _get_mode_weight_for_score(score, mode):
    normalized_score = max(0.0, min(1.0, float(score)))
    if mode == "safe":
        return (normalized_score ** 3) + 0.01
    if mode == "chaos":
        return ((1.0 - normalized_score) ** 3) + 0.01
    return 1.0


def _sanitize_seed(seed_value):
    if seed_value is None:
        return None

    if isinstance(seed_value, bool):
        return None

    if isinstance(seed_value, int):
        return seed_value

    text = str(seed_value).strip()
    if not text:
        return None

    try:
        return int(text)
    except ValueError:
        return None


def set_random_seed(seed_value):
    global randomSeed, lastUsedSeed
    randomSeed = _sanitize_seed(seed_value)
    if randomSeed is not None:
        lastUsedSeed = randomSeed
    return randomSeed


def _create_rng(seed_value):
    normalized = _sanitize_seed(seed_value)
    return rdm.Random(normalized)


def _generate_runtime_seed():
    return rdm.SystemRandom().randint(0, 2_147_483_647)


def get_copyable_seed():
    global lastUsedSeed
    configured = _sanitize_seed(randomSeed)
    if configured is not None:
        lastUsedSeed = configured
        return configured

    if lastUsedSeed is not None:
        return lastUsedSeed

    lastUsedSeed = _generate_runtime_seed()
    return lastUsedSeed


def _choose_random_language_index(candidate_indices, rng):
    if not candidate_indices:
        return rng.randint(1, len(supported_languages))

    mode = _sanitize_translation_mode(translationMode)
    if mode == "normal":
        return rng.choice(candidate_indices)

    weights = []
    for index in candidate_indices:
        language_code = target_languages[index - 1]
        quality_score = _get_language_quality_score(language_code)
        weights.append(_get_mode_weight_for_score(quality_score, mode))

    try:
        return rng.choices(candidate_indices, weights=weights, k=1)[0]
    except Exception:
        return rng.choice(candidate_indices)


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


def _coerce_to_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple, set)):
        parts = [_coerce_to_text(part) for part in value]
        parts = [part for part in parts if part]
        return " ".join(parts).strip()
    return str(value)


def _normalize_text_for_compare(text):
    normalized_text = _coerce_to_text(text)
    return re.sub(r"\s+", " ", normalized_text.strip()).casefold()


def _is_effectively_same_text(left_text, right_text):
    return _normalize_text_for_compare(left_text) == _normalize_text_for_compare(right_text)


async def _translate_sentence_with_retries(
    translator_client,
    sentence,
    dest_language_code,
    source_language_code=None,
    max_retries=3,
):
    sentence_text = _coerce_to_text(sentence)
    if not sentence_text.strip():
        return sentence_text, ""

    retries = 0
    while retries < max_retries:
        try:
            translate_kwargs = {"dest": dest_language_code}
            if source_language_code and source_language_code != "auto":
                translate_kwargs["src"] = source_language_code

            result = await translator_client.translate(sentence_text, **translate_kwargs)
            result_text = _coerce_to_text(getattr(result, "text", ""))
            if result is not None and result_text:
                pronunciation = _coerce_to_text(getattr(result, "pronunciation", "") or "")
                return result_text, pronunciation
            raise ValueError("No translation received")
        except Exception as exc:
            _console_log(f"Error translating sentence '{sentence_text}': {exc}")
            retries += 1
            if retries < max_retries:
                await asyncio.sleep(RETRY_DELAY_SECONDS)

    _console_log(f"Translation for sentence '{sentence_text}' failed. Using original sentence.")
    return sentence_text, ""


async def _safe_translate(
    translator_client,
    text,
    dest_language_code,
    source_language_code=None,
    max_retries=3,
):
    source_text = _coerce_to_text(text)
    sentences = re.split(r"(?<=[.!?])\s+", source_text)
    non_empty_sentences = [sentence for sentence in sentences if sentence.strip()]

    if len(non_empty_sentences) <= 1:
        translated_sentences = []
        pronunciation_sentences = []
        for sentence in sentences:
            translated_sentence, pronunciation = await _translate_sentence_with_retries(
                translator_client,
                sentence,
                dest_language_code,
                source_language_code=source_language_code,
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
                    source_language_code=source_language_code,
                    max_retries=max_retries,
                )

        translated_pairs = await asyncio.gather(*[_translate_with_limit(sentence) for sentence in sentences])
        translated_sentences = [pair[0] for pair in translated_pairs]
        pronunciation_sentences = [pair[1] for pair in translated_pairs]

    translated_text = " ".join(translated_sentences)
    pronunciation_text = " ".join(pronunciation_sentences).strip()
    return translated_text, pronunciation_text


async def _translate_final_with_fallbacks(
    translator_client,
    current_text,
    selected_language_code,
    current_source_code,
    original_text,
    original_source_code,
):
    current_text = _coerce_to_text(current_text)
    original_text = _coerce_to_text(original_text)

    attempts = [
        (current_text, current_source_code),
        (current_text, None),
    ]

    if original_text and not _is_effectively_same_text(original_text, current_text):
        attempts.append((original_text, original_source_code))
        attempts.append((original_text, None))

    seen = set()
    ordered_attempts = []
    for source_text, source_code in attempts:
        normalized_key = (
            _normalize_text_for_compare(source_text),
            source_code or "auto",
        )
        if normalized_key in seen:
            continue
        seen.add(normalized_key)
        ordered_attempts.append((source_text, source_code))

    last_translation = current_text
    last_pronunciation = ""
    last_source_text = current_text
    last_source_code = current_source_code or "auto"

    for source_text, source_code in ordered_attempts:
        translated_text, pronunciation = await _safe_translate(
            translator_client,
            source_text,
            selected_language_code,
            source_language_code=source_code,
        )

        last_translation = translated_text
        last_pronunciation = pronunciation
        last_source_text = source_text
        last_source_code = source_code or "auto"

        if translated_text.strip() and not _is_effectively_same_text(translated_text, source_text):
            return translated_text, pronunciation, source_text, (source_code or "auto")

    _console_log("Final translation remained unchanged after fallbacks.")
    return last_translation, last_pronunciation, last_source_text, last_source_code


async def _detect_language_code(translator_client, text, max_retries=3):
    text = _coerce_to_text(text)
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


async def _language_step(
    translator_client,
    text,
    value,
    used_languages,
    steps,
    source_language_name="",
    source_language_code="",
):
    global timeOutCounter
    text = _coerce_to_text(text)

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
                    source_language_code=source_language_code,
                )
                steps.append(
                    {
                        "source_language_name": source_language_name or "auto",
                        "source_language_code": source_language_code or "auto",
                        "target_language_name": dest_language_name,
                        "target_language_code": dest_language_code or "",
                        "input_text": _coerce_to_text(text),
                        "output_text": _coerce_to_text(translated_text),
                        "transliteration": pronunciation,
                    }
                )
                return _coerce_to_text(translated_text), dest_language_name, dest_language_code
            except Exception as exc:
                _console_log(f"Error occurred: {exc}, trying again...")
                timeOutCounter += 1
                retries += 1
                await asyncio.sleep(RETRY_DELAY_SECONDS)

        return _coerce_to_text(text), dest_language_name, dest_language_code

    return _coerce_to_text(text), source_language_name, source_language_code


async def _randomizer_async(text, selected_language_name, progress_queue):
    global translation_steps, forcedLanguages, setLoopTimes, translationMode, randomSeed, lastUsedSeed

    steps = []
    used_languages = []
    translationMode = _sanitize_translation_mode(translationMode)
    randomSeed = _sanitize_seed(randomSeed)
    effective_seed = randomSeed if randomSeed is not None else _generate_runtime_seed()
    lastUsedSeed = effective_seed
    rng = _create_rng(effective_seed)

    async with Translator() as translator_client:
        original_input_text = _coerce_to_text(text)
        text = original_input_text
        detected_lang_code = await _detect_language_code(translator_client, text)
        detected_language = LANGUAGES.get(detected_lang_code, "Unknown")
        current_language_name = detected_language
        current_language_code = detected_lang_code or "auto"

        selected_language_index = supported_languages.index(selected_language_name)
        selected_language_code = target_languages[selected_language_index]

        _console_log("\nTarget language: " + selected_language_name)
        if forcedLanguages:
            _console_log("Forced languages: " + ", ".join(forcedLanguages))
        else:
            _console_log("Forced languages: none")
        _console_log("Translation mode: " + translationMode)
        _console_log("Seed: " + str(effective_seed))

        num_steps = setLoopTimes - 1
        if forcedLanguages:
            num_steps = max(num_steps, len(forcedLanguages))
        total_steps = num_steps + 2
        total_iteration_display = num_steps + 1
        _queue_progress(
            progress_queue,
            progress_value=100 * 1 / total_steps,
            status_text=t(
                "progress_translating",
                language=selected_language_name,
                current=0,
                total=total_iteration_display,
            ),
        )

        forced_count = len(forcedLanguages)
        forced_positions = []
        forced_order = []

        if forced_count > 0:
            forced_positions = rng.sample(range(num_steps), forced_count)
            forced_positions.sort()
            forced_order = list(forcedLanguages)
            rng.shuffle(forced_order)

        for i in range(num_steps):
            if forced_count > 0 and i in forced_positions:
                forced_lang = forced_order[forced_positions.index(i)]
                forced_index = supported_languages.index(forced_lang) + 1
                step_language = forced_lang
                _queue_progress(
                    progress_queue,
                    status_text=t(
                        "progress_translating",
                        language=step_language,
                        current=(i + 1),
                        total=total_iteration_display,
                    ),
                )
                text, current_language_name, current_language_code = await _language_step(
                    translator_client,
                    text,
                    forced_index,
                    used_languages,
                    steps,
                    source_language_name=current_language_name,
                    source_language_code=current_language_code,
                )
            else:
                if used_languages:
                    last_language = used_languages[-1]
                    candidate_indices = [
                        j
                        for j in range(1, len(supported_languages) + 1)
                        if supported_languages[j - 1] != last_language
                    ]
                    random_value = _choose_random_language_index(candidate_indices, rng)
                else:
                    random_value = _choose_random_language_index(
                        list(range(1, len(supported_languages) + 1)),
                        rng,
                    )

                step_language = supported_languages[random_value - 1]
                _queue_progress(
                    progress_queue,
                    status_text=t(
                        "progress_translating",
                        language=step_language,
                        current=(i + 1),
                        total=total_iteration_display,
                    ),
                )
                text, current_language_name, current_language_code = await _language_step(
                    translator_client,
                    text,
                    random_value,
                    used_languages,
                    steps,
                    source_language_name=current_language_name,
                    source_language_code=current_language_code,
                )

            if used_languages:
                _console_log("RDM (" + used_languages[-1] + "): " + text)

            _queue_progress(progress_queue, progress_value=100 * (1 + (i + 1)) / total_steps)

        _queue_progress(
            progress_queue,
            status_text=t(
                "progress_translating",
                language=selected_language_name,
                current=total_iteration_display,
                total=total_iteration_display,
            ),
        )
        text, final_pronunciation, final_source_text, final_source_code = await _translate_final_with_fallbacks(
            translator_client,
            current_text=text,
            selected_language_code=selected_language_code,
            current_source_code=current_language_code,
            original_text=original_input_text,
            original_source_code=detected_lang_code or "auto",
        )
        _queue_progress(progress_queue, progress_value=100)

    lang_chain = f"{t('detected_language_prefix')}: [{detected_language}]\n"
    if used_languages:
        lang_chain += " -> ".join(used_languages)

    steps.append(
        {
            "source_language_name": LANGUAGES.get(final_source_code, current_language_name or "Unknown"),
            "source_language_code": final_source_code or "auto",
            "target_language_name": selected_language_name,
            "target_language_code": selected_language_code or "",
            "input_text": final_source_text,
            "output_text": _coerce_to_text(text),
            "transliteration": final_pronunciation,
        }
    )
    translation_steps = steps

    _console_log("END (" + selected_language_name + "): " + text)

    return text, lang_chain, selected_language_name


def randomizer(text, language_selector, progress_queue):
    selected_language_name = language_selector.get()
    return asyncio.run(_randomizer_async(text, selected_language_name, progress_queue))


def get_translation_steps():
    return translation_steps
