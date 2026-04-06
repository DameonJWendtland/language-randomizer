# Language Randomizer

Language Randomizer is a Tkinter desktop app that sends text through random language hops with `googletrans`.
The result is intentionally experimental and designed for fun, not for production-grade translation quality.

## Features

- Random translation chains with configurable iterations
- Forced languages and three translation modes: `Normal`, `Chaos`, `Safe`
- Optional transliteration for non-Latin scripts
- Step-by-step view with export and Google Translate links
- Comparison view with text similarity and optional semantic similarity
- Saved settings for theme, font, UI language, seed, and more

## Requirements

- Windows, Linux, or macOS for source execution
- Python 3.10+
- `googletrans==4.0.2`
- `ttkthemes`

Install the runtime dependencies:

```bash
pip install -r requirements.txt
```

## Run From Source

Use either of these commands:

```bash
python main.py
python -m language_randomizer
```

## Build Windows Packages

The project now includes reproducible scripts for both a portable EXE bundle and an MSI installer:

```powershell
python -m pip install pyinstaller
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows_exe.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows_msi.ps1
```

This creates:

- `dist\LanguageRandomizer\LanguageRandomizer.exe`
- `dist\LanguageRandomizer-windows.zip`
- `dist\LanguageRandomizer-2.0.0-x64.msi`

Important:

- Share the whole `dist\LanguageRandomizer` folder or the generated ZIP, not only the `.exe`.
- The MSI is a per-machine installer and requires administrator rights during installation.
- Windows builds should be created on Windows.
- macOS and Linux need to be built on their own operating systems.
- Semantic similarity in the compare view stays optional and may show as unavailable if the extra NLP stack is not bundled.

## Project Structure

```text
language-randomizer/
|-- main.py
|-- scripts/
|   `-- build_windows_exe.ps1
|   `-- build_windows_msi.ps1
|-- installer/
|   `-- windows/
|       |-- LanguageRandomizer.wxs
|       `-- installer-notice.rtf
|-- language_randomizer/
|   |-- __init__.py
|   |-- __main__.py
|   |-- app.py
|   |-- i18n.py
|   |-- paths.py
|   |-- settings_store.py
|   |-- translator.py
|   |-- assets/
|   |   `-- translating.ico
|   |-- locales/
|   `-- ui/
```

## Notes

- The icon and locale files are bundled into the executable build.
- If you previously installed `googletrans==4.0.0rc1`, upgrade with:

```bash
python -m pip install --upgrade googletrans==4.0.2
```

## Attribution

<a href="https://www.flaticon.com/free-icons/translate" title="translate icons">Translate icons created by photo3idea_studio - Flaticon</a>
