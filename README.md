# Language Randomizer

A fun Tkinter desktop app that translates text through random language hops using `googletrans`.
It is intentionally experimental and not meant for production-grade translation quality.

## Features

- Random translation chain
- Optional forced languages
- Configurable iteration count
- Translation progress indicator
- Step-by-step output with export

## Project Structure

```text
language-randomizer/
|-- main.py
|-- language_randomizer/
|   |-- __init__.py
|   |-- __main__.py
|   |-- app.py
|   |-- paths.py
|   |-- translator.py
|   |-- assets/
|   |   `-- translating.ico
|   `-- ui/
|       |-- __init__.py
|       |-- main_window.py
|       |-- help_window.py
|       |-- menu.py
|       |-- options.py
|       |-- show_steps.py
|       `-- window_icon.py
```

## Requirements

- Python 3.10+
- `googletrans==4.0.2`
- `ttkthemes`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Choose one of these commands:

```bash
python main.py
```

python -m language_randomizer
```

## Notes

- The icon path is now relative and portable.
- IDE/build/cache artifacts are intentionally not part of the source layout.
- If you previously installed `googletrans==4.0.0rc1`, upgrade with:

```bash
python -m pip install --upgrade googletrans==4.0.2
```

## Attribution

<a href="https://www.flaticon.com/free-icons/translate" title="translate icons">Translate icons created by photo3idea_studio - Flaticon</a>
