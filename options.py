import tkinter as tk
from tkinter import ttk
from translator import supported_languages, forcedLanguages

def open_options():
    options_win = tk.Toplevel()
    options_win.title("Options - Force Languages")
    options_win.geometry("700x400")
    canvas = tk.Canvas(options_win)
    scrollbar = tk.Scrollbar(options_win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    window_item = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    def resize_canvas(event):
        canvas.itemconfig(window_item, width=event.width)
    canvas.bind("<Configure>", resize_canvas)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    def _on_mousewheel(event):
        try:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except tk.TclError:
            pass
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    info_text = tk.Text(scrollable_frame, wrap=tk.WORD, height=5)
    info_text.insert("1.0", "You may select the language you want to be definitely included in the randomizer. To undo selection, just reopen the options window and apply changes without anything selected.\n\nEverything will be unselected after reopening!")
    info_text.config(state="disabled")
    info_text.pack(padx=10, pady=(10, 10), fill="x")
    info_label = ttk.Label(scrollable_frame, text="Select forced languages:")
    info_label.pack(padx=10, pady=(0, 10), fill="x")
    forced_vars = {}
    frame = ttk.Frame(scrollable_frame)
    frame.pack(padx=10, pady=10, fill="x")
    for i, lang in enumerate(supported_languages):
        var = tk.BooleanVar(value=(lang in forcedLanguages))
        forced_vars[lang] = var
        chk = ttk.Checkbutton(frame, text=lang, variable=var)
        chk.grid(row=i // 5, column=i % 5, sticky="w", padx=5, pady=5)
    def apply_options():
        global forcedLanguages
        forcedLanguages.clear()
        for lang, var in forced_vars.items():
            if var.get():
                forcedLanguages.append(lang)
        options_win.destroy()
        print("Forced languages:", forcedLanguages)
    def reset_options():
        for var in forced_vars.values():
            var.set(False)
    def select_all_options():
        for var in forced_vars.values():
            var.set(True)
    btn_frame = ttk.Frame(scrollable_frame)
    btn_frame.pack(pady=10)
    select_all_btn = ttk.Button(btn_frame, text="Select All", command=select_all_options)
    select_all_btn.pack(side="left", padx=(0, 10))
    reset_btn = ttk.Button(btn_frame, text="Reset", command=reset_options)
    reset_btn.pack(side="left", padx=(0, 10))
    apply_btn = ttk.Button(btn_frame, text="Apply", command=apply_options)
    apply_btn.pack(side="left")
