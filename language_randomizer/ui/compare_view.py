import difflib
import importlib
import importlib.util
import re
import threading
import tkinter as tk
from tkinter import ttk

from ..font_utils import apply_saved_font
from ..i18n import t
from ..paths import SEMANTIC_MODEL_DIR
from .context_menu import bind_context_menu
from .window_icon import apply_window_icon

_SEMANTIC_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_semantic_model = None
_semantic_model_failed = False
_semantic_model_lock = threading.Lock()


def _tokenize(text):
    return re.findall(r"\S+|\s+", text or "")


def _get_semantic_model_source():
    modules_file = SEMANTIC_MODEL_DIR / "modules.json"
    config_file = SEMANTIC_MODEL_DIR / "config_sentence_transformers.json"
    if modules_file.exists() or config_file.exists():
        return str(SEMANTIC_MODEL_DIR)
    return _SEMANTIC_MODEL_NAME


def _bundled_semantic_model_exists():
    modules_file = SEMANTIC_MODEL_DIR / "modules.json"
    config_file = SEMANTIC_MODEL_DIR / "config_sentence_transformers.json"
    return modules_file.exists() or config_file.exists()


def _semantic_support_available():
    return _bundled_semantic_model_exists() or importlib.util.find_spec("sentence_transformers") is not None


def _load_semantic_model():
    global _semantic_model, _semantic_model_failed
    if _semantic_model is not None:
        return _semantic_model

    if _semantic_model_failed:
        return None

    with _semantic_model_lock:
        if _semantic_model is not None:
            return _semantic_model
        if _semantic_model_failed:
            return None

        try:
            sentence_transformers_module = importlib.import_module("sentence_transformers")
            sentence_transformer_cls = getattr(sentence_transformers_module, "SentenceTransformer", None)
            if sentence_transformer_cls is None:
                _semantic_model_failed = True
                return None

            _semantic_model = sentence_transformer_cls(_get_semantic_model_source())
        except Exception:
            _semantic_model_failed = True
            _semantic_model = None
            return None
    return _semantic_model


def _compute_semantic_similarity(original_text, final_text):
    if not original_text.strip() and not final_text.strip():
        return 1.0
    if not original_text.strip() or not final_text.strip():
        return 0.0

    model = _load_semantic_model()
    if model is None:
        return None

    embeddings = model.encode(
        [original_text, final_text],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    score = float(embeddings[0] @ embeddings[1])
    return max(0.0, min(1.0, score))


def _compute_text_similarity(original_text, final_text):
    return difflib.SequenceMatcher(
        None,
        (original_text or "").strip(),
        (final_text or "").strip(),
        autojunk=False,
    ).ratio()


def _insert_diff(left_widget, right_widget, original_text, final_text):
    left_tokens = _tokenize(original_text)
    right_tokens = _tokenize(final_text)

    matcher = difflib.SequenceMatcher(a=left_tokens, b=right_tokens, autojunk=False)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        left_segment = "".join(left_tokens[i1:i2])
        right_segment = "".join(right_tokens[j1:j2])

        if tag == "equal":
            if left_segment:
                left_widget.insert("end", left_segment)
            if right_segment:
                right_widget.insert("end", right_segment)
            continue

        if tag in {"replace", "delete"} and left_segment:
            left_widget.insert("end", left_segment, "removed")
        if tag in {"replace", "insert"} and right_segment:
            right_widget.insert("end", right_segment, "added")


def open_compare_view(root, original_text, final_text):
    original_text = original_text or ""
    final_text = final_text or ""

    compare_win = tk.Toplevel(root)
    compare_win.title(t("compare_window_title"))
    compare_win.geometry("1020x620")
    apply_window_icon(compare_win)

    container = ttk.Frame(compare_win, padding=10)
    container.pack(fill="both", expand=True)
    container.columnconfigure(0, weight=1)
    container.columnconfigure(1, weight=1)
    container.rowconfigure(1, weight=1)

    textual_ratio = _compute_text_similarity(original_text, final_text)
    textual_similarity_text = t("compare_similarity_textual", value=f"{textual_ratio * 100:.1f}%")
    semantic_available = _semantic_support_available()
    semantic_similarity_var = tk.StringVar(value="")
    # Keep a strong reference on the window to prevent Tk variable GC from clearing the label.
    compare_win._semantic_similarity_var = semantic_similarity_var
    length_text = t("compare_length", original=len(original_text), final=len(final_text))

    info_frame = ttk.Frame(container)
    info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
    info_frame.columnconfigure(0, weight=1)
    info_frame.columnconfigure(1, weight=1)
    ttk.Label(info_frame, text=textual_similarity_text).grid(row=0, column=0, sticky="w")
    ttk.Label(info_frame, text=length_text).grid(row=0, column=1, sticky="e")
    semantic_label = ttk.Label(info_frame, textvariable=semantic_similarity_var, foreground="#8a5a00")
    if semantic_available:
        semantic_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

    if not original_text and not final_text:
        if semantic_available:
            semantic_similarity_var.set(t("compare_semantic_unavailable"))
        empty_label = ttk.Label(container, text=t("compare_no_data"), justify="left")
        empty_label.grid(row=1, column=0, columnspan=2, sticky="nsew")
        return

    if semantic_available and original_text.strip() and final_text.strip():
        semantic_similarity_var.set(t("compare_semantic_loading"))

        def _semantic_worker():
            semantic_ratio = _compute_semantic_similarity(original_text, final_text)

            def _apply_result():
                if not compare_win.winfo_exists():
                    return
                if semantic_ratio is None:
                    semantic_similarity_var.set(t("compare_semantic_unavailable"))
                    return

                semantic_similarity_var.set(
                    t("compare_similarity_semantic", value=f"{semantic_ratio * 100:.1f}%")
                )

            compare_win.after(0, _apply_result)

        threading.Thread(target=_semantic_worker, daemon=True).start()
    elif semantic_available:
        semantic_similarity_var.set(t("compare_semantic_unavailable"))

    left_frame = ttk.Frame(container)
    left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
    left_frame.columnconfigure(0, weight=1)
    left_frame.rowconfigure(1, weight=1)

    right_frame = ttk.Frame(container)
    right_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 0))
    right_frame.columnconfigure(0, weight=1)
    right_frame.rowconfigure(1, weight=1)

    ttk.Label(left_frame, text=t("compare_left_label")).grid(row=0, column=0, sticky="w", pady=(0, 4))
    ttk.Label(right_frame, text=t("compare_right_label")).grid(row=0, column=0, sticky="w", pady=(0, 4))

    left_text = tk.Text(left_frame, wrap="word", padx=6, pady=6)
    left_text.grid(row=1, column=0, sticky="nsew")
    left_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=left_text.yview)
    left_scroll.grid(row=1, column=1, sticky="ns")
    left_text.configure(yscrollcommand=left_scroll.set)
    bind_context_menu(left_text)

    right_text = tk.Text(right_frame, wrap="word", padx=6, pady=6)
    right_text.grid(row=1, column=0, sticky="nsew")
    right_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=right_text.yview)
    right_scroll.grid(row=1, column=1, sticky="ns")
    right_text.configure(yscrollcommand=right_scroll.set)
    bind_context_menu(right_text)

    # Removed tokens are highlighted red, inserted/replaced tokens green.
    left_text.tag_configure("removed", background="#FDE2E1", foreground="#8A1C1C")
    right_text.tag_configure("added", background="#DEF7E0", foreground="#1C6E2A")

    _insert_diff(left_text, right_text, original_text, final_text)

    left_text.config(state="disabled")
    right_text.config(state="disabled")
    apply_saved_font(compare_win)
