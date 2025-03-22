import tkinter as tk
from tkinter import ttk, filedialog
import translator


def show_translation_steps():
    steps_win = tk.Toplevel()
    steps_win.title("Translation Steps")
    steps_win.geometry("760x400")

    top_frame = ttk.Frame(steps_win)
    top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    export_btn = ttk.Button(top_frame, text="Export", command=lambda: export_steps())
    export_btn.pack(side="right")

    canvas = tk.Canvas(steps_win)
    canvas.grid(row=1, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(steps_win, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=1, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _on_mousewheel(event):
        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass

    canvas.bind("<MouseWheel>", _on_mousewheel)

    steps = translator.get_translation_steps()
    if not steps:
        no_label = ttk.Label(scrollable_frame, text="No steps recorded.", font=("Helvetica", 12))
        no_label.pack(padx=10, pady=10)
    else:
        for idx, (lang, step_text) in enumerate(steps, 1):
            lang_label = ttk.Label(scrollable_frame, text=f"Step {idx} ({lang}):")
            lang_label.pack(anchor="w", padx=10, pady=(10, 2))

            translation_text = tk.Text(scrollable_frame, wrap="word", font=("Helvetica", 12), height=4)
            translation_text.pack(fill="x", padx=10, pady=(0, 10))
            translation_text.insert("1.0", step_text)
            translation_text.configure(state="disabled")

    steps_win.grid_rowconfigure(1, weight=1)
    steps_win.grid_columnconfigure(0, weight=1)


def export_steps():
    steps = translator.get_translation_steps()
    export_text = ""
    if not steps:
        export_text = "No steps recorded."
    else:
        for idx, (lang, step_text) in enumerate(steps, 1):
            export_text += f"Step {idx} ({lang}):\n{step_text}\n\n"

    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        title="Save translation steps as..."
    )

    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(export_text)
        print("Steps exported to", filename)
