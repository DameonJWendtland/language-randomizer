# Language Randomizer

A fun and experimental tool that randomly translates text through multiple languages. This project uses Python's tkinter for the GUI and the [googletrans](https://py-googletrans.readthedocs.io/en/latest/) API for translations. While it's entertaining and educational, please note that it's not meant to be a serious translation solution.

## Overview

The Language Randomizer demonstrates how meaning can shift when text is passed through multiple languages in a "telephone game" style translation chain. You can force specific languages into the chain and control the number of translation iterations.


## Features

- **Randomized Translation Chain:** Translates input text through a series of random languages.
- **Forced Languages:** Option to force specific languages into the translation chain.
- **Customizable Iterations:** Adjust the number of translation iterations.
- **Graphical User Interface:** User-friendly interface built with tkinter.
- **Help & Options Dialogs:** Easy access to instructions and language options.
- **Progress Tracking:** Visual progress bar indicating the translation process.

### In v1.1

- **Themes:** Use your own `ThemedTK` theme in the code in [App.py](https://github.com/DameonJWendtland/language-randomizer/blob/v1.1/App.py)
```py
root = ThemedTk(theme="custom_theme")
```
You may look up [List of ttk Themes](https://wiki.tcl-lang.org/page/List+of+ttk+Themes)
  
- **Secure entry:** Now it is requied to select a *valid* target language and to type in a positive integer into the `randomizer iterations` field.
- **Visuals:** The `translate text` button is now disabled until all requirements are fulfilled of the secure entry. Fields, which are invalid are changing their `background-color` to `lightcoral`.
- **Filter languages:** Type into the selector field of the target language to filter for languages. To unselect the filter: clear the text and open the dropdown.
- **Review Languages:** You can now see all languages that have been used during the iterations with each output they gave.
- **Export:** The steps for each language with their coresponding translation can be exported as `.txt`.
## Folder Structure

```
language_randomizer/
├── App.py           # Entry point of the application
├── translator.py    # Contains functions for translation logic and language randomization
├── gui.py           # Manages the graphical user interface
├── options.py       # Implements the options dialog for forced languages
├── show_steps.py    # Implements the translation steps dialogue with each language which was iterated through
└── help_window.py   # Implements the help dialog window
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/DameonJWendtland/language_randomizer.git
   cd language_randomizer
   ```

2. **Install Dependencies:**

   Ensure you have Python 3 installed. Install the required package using pip:

   ```bash
   pip install googletrans==4.0.0rc1
   ```

   *Note:* The `tkinter` module is bundled with Python on most platforms.

## Usage

Run the application by executing:

```bash
python App.py
```

Once the GUI appears:
- Enter your text in the "Input:" field.
- Select the target language from the dropdown.
- Adjust the number of iterations for translation.
- Optionally, open the Options dialog to force specific languages.
- Click on "Translate Text" to start the translation chain.
- Use the Help button ( ? ) for more detailed instructions.


---

Enjoy experimenting with translations and have fun with your Language Randomizer! 😊


---

### Attribution
<a href="https://www.flaticon.com/free-icons/translate" title="translate icons">App icon created by photo3idea_studio - Flaticon</a>
