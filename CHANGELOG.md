# Changelog

All notable changes to pdf-word-finder. The releases are on
[GitHub](https://github.com/nivaca/pdf-word-finder/releases) (1.1, 1.4, 1.5
and 1.6 have release pages; 1.2 to 1.23 are only tags). The program and its
README are in Spanish; an English README is in `README_en.md`.

## Unreleased

- `scripts/construir.py` leaves everything in `build/`, and nothing in
  `dist/`: the program folder and the ZIP in `build/release/`
  (`build/release/pdf-word-finder-SYSTEM-VERSION.zip`), PyInstaller's work
  files in `build/pyinstaller/`. The READMEs (§11) and the recipe say so.
- `scripts/test.py` runs the tests at once, each file in a pytest process
  of its own, as many as there are processors (`-j N` changes it), and
  exits with 1 if any fails, with the output of the files that failed.

## 1.6 — 2026-11-21

- **Python 3.14 or later is required**: in `pyproject.toml`, in the
  READMEs, in the Windows launchers (an older Python counts as no Python,
  and they offer to install a new one), and in the program itself, which
  says so in one line instead of failing with a syntax error.
- **The project is reorganized in directories.** The program is the
  package `src/pdf_word_finder/`, split into modules: `extraction`,
  `text`, `patterns`, `search`, `report`, `cli` and `gui`. A
  `pyproject.toml` makes it installable (`pip install .`, `pipx install .`)
  with two commands, `pdf-word-finder` and `pdf-word-finder-gui`. The
  PyInstaller recipe and its two launchers are in `packaging/`,
  `subir_version.py` is in `scripts/`, and the two `.bat` files are in
  `windows/`.
- The recipe `pdf_word_finder.spec` is now in the repository; before, the
  `.gitignore` left it out.
- The functions of the package raise exceptions (`PdfError`,
  `PatternError`) instead of ending the program, and the command line and
  the window share the search (`search()`), the report and the export to
  TXT and CSV. The window no longer has its own copy of the search loop and
  of the CSV export.
- `scripts/construir.py` builds the executables and packs them, with the
  license, the READMEs, the changelogs and `docs/`, in
  `dist/pdf-word-finder-SYSTEM-VERSION.zip`.
- Tests: 43, with pytest, in `tests/`. They make their own small PDFs.
- The dependency is `pypdf[crypto]`, which also opens PDFs encrypted with
  AES.
- In the window, a context width that is not a number no longer stops the
  search; it uses 60.
- The README no longer describes the GitHub workflow, which was taken out
  in 1.4; §11 explains how to build on each system and publish by hand.
- Two description documents in `docs/`: `DESCRIPTION.md`, how the program
  was made, and `DESCRIPCIÓN_es.md`, a description in Spanish.
- The Linux package is built with Python 3.15. There is no Windows package
  for this version.

## 1.5 — 2026-11-21

- A list of the open-source software used in the program, with versions
  and licenses: `docs/THIRD_PARTY_LICENSES.md` and, in Spanish,
  `docs/LICENCIAS_DE_TERCEROS_es.md`. The README points to it, and the
  package carries it, with `LICENSE` and the READMEs.
- The Linux package is built with Python 3.15. There is no Windows package
  for this version.
- **The license is now the GNU GPL, version 3 or later** (it was MIT):
  `LICENSE`, the README, the headers of the scripts and `__license__`.
- An English translation of the README, `README_en.md`.
- `crear-acceso-directo.bat` makes a shortcut in the Windows Start menu
  (and, if wanted, on the desktop), which runs `pythonw.exe` with the
  window directly, so no console window stays behind and Windows does not
  block it as a downloaded `.bat`.
- `subir_version.py` changes the version in every place of the READMEs
  (`subir_version.py 1.5`), shows it (`--mostrar`), and checks that the
  READMEs agree with `__version__` (`--revisar`).

## 1.4 — 2026-08-20

- The version lives in one place, `__version__` in `pdf_word_finder.py`;
  the window and the PyInstaller recipe take it from there, and the
  headers of the scripts no longer repeat it. The README has a section on
  the version.
- The build workflow `build.yml` is no longer in the repository.

## 1.23 — 2026-08-20

- The Windows launcher, `pdf-word-finder.bat`, goes on to open the program
  right after it installs Python, without starting again. As the new
  Python is not yet on the PATH of that window, it looks for it in the
  folders where it is usually installed, from the newest version down.

## 1.22 — 2026-08-20

- The Windows launcher installs the newest Python that winget offers
  (it tries `Python.Python.3.19` down to `3.12`), instead of always 3.12.
- The README is rewritten in parts.

## 1.21 — 2026-08-20

- The Windows launcher tests Python by running it, not with `where`:
  Windows 11 has a fake `python` that only opens the Store. If installing
  Python with winget for the user fails, it tries again in the normal
  way, and checks that Python works before going on.
- The build workflow also runs for tags without a `v` (`1.2` as well as
  `v1.2`).

## 1.2 — 2026-08-20

- `--sort` orders the list alphabetically, and `--txt FILE` exports it to
  a text file; the window can save the list as text or as CSV.
- The text of a PDF is extracted once and kept, for the next searches.
- PyMuPDF is imported as `pymupdf`, not with the old name `fitz`.
- The window has an About box, with the version and the technical data
  (Python, Tcl/Tk, pypdf, PyMuPDF and the system), and does the search in
  the background.
- The scripts are renamed `pdf_word_finder.py` and
  `pdf_word_finder_gui.py`, so that one can be imported by the other.
- `pdf-word-finder.bat`, a launcher for Windows that installs Python
  (with winget, or else from the Store) and pypdf when they are missing,
  and opens the window.
- Executables made with PyInstaller (a folder, or one file with
  `PWF_ONEFILE=1`), and a GitHub workflow, `build.yml`, that builds them
  for Windows, macOS and Linux and attaches them to a release. The README
  explains how to open them when Windows or macOS refuse to.

## 1.1 — 2026-08-18

- First version: a command line program that searches a list of words,
  phrases or regular expressions in a PDF and tells on which pages each
  one appears. It gives the labelled page numbers of the `/PageLabels`
  tree (the numbers printed on the pages), says so when the PDF has none,
  and with `--show-logical` adds the sequential page in brackets. It
  joins words hyphenated at the end of a line, and has the options
  `--words-file`, `--regex`, `--regex-word`, `--substring`,
  `--case-sensitive`, `--ignore-accents`, `--context` and `--csv`.
- The report is one line for each term, with the pages separated by
  commas, as in an index; `--detailed` gives the long report, with the
  count of each term. Terms not found and warnings go to the error
  output, so a redirected result is a clean index.
- A simple window (Tkinter), `pdf-word-finder-gui.py`, which uses the
  functions of the command line program and offers the same options.
