# pdf-word-finder

**Version 1.6** · © Nicolás Vaughan 2026 · License GNU GPL v3 or later

*Versión en español: [README.md](README.md).*

This program searches a list of words, phrases or regular expressions inside
a PDF file, and it tells you **on which pages each one appears**. It always
makes a difference between the two page numbering systems that live
together inside a PDF.

A note before starting: the program itself speaks Spanish. All the help
text, the messages and the graphical interface are in Spanish. The option
names (`--context`, `--sort`...) are in English, so the commands in this
document work the same. When an example shows a message from the program, I
leave it in Spanish (as you will see it) and I give the meaning next to it.

---

## 1. The two numberings

Every PDF file has a **sequential** (or logical) numbering: the position of
each page inside the file, counting from 1. This is the number you see in
the scroll bar of the viewer, and the one you use when you print a range of
pages.

Besides this, the file *can* declare a **labelled** numbering: the number
that is really printed on the page. It is stored in the `/PageLabels` tree
in the catalog of the document. With this tree it is possible to express
everything that the typographic tradition asks for:

| Situation | Sequential | Labelled |
|---|---|---|
| Cover and title page without number | 1, 2 | *(no label, or "C-1")* |
| Front matter in small roman numerals | 3–14 | i–xii |
| Main body of the work | 15– | 1– |
| Restart in the second volume | 320– | 1– |
| Inserted plates | 88 | "Lám. IV" |

So in a normal edition the **sequential page 15** is the **labelled page
1**. That is a difference of fourteen, and any search that gives you the
wrong number is useless.

The program reports **the labelled one**, because this is the number the
reader needs to open the book. It gives one line for each term:

```
amor i, 1, 4
Sharahzad 3, 5, 23, 34
Nombre de Dios 5, 23
```

If sometimes you need also the internal index of the file (for example to
jump to the page in the viewer), the option `--show-logical` adds it in
square brackets, but only when it is different from the label:

```
amor i [sec. 1], 1 [sec. 3], 4 [sec. 6]
```

("sec." means *secuencial*, sequential.)

If the PDF has no `/PageLabels` tree, the program tells you this clearly. It
does not pretend that there is a labelled numbering when there is none. (Be
careful here: `pypdf` by itself returns "1, 2, 3..." when there are no
labels, and this silence is exactly what I wanted to avoid.) In this case,
the printed numbers are necessarily the sequential ones.

Keep in mind also that a `/PageLabels` tree can lie, or be incomplete. It is
made by the typesetting program, and not always with care. If the labels you
get do not match what is printed in the book, with `--show-logical` you can
check the difference very fast.

---

## 2. Installation

You need Python 3.14 or newer.

The program is a Python package, which you install with `pip` from the
project folder. The installation brings the only dependency, `pypdf`, and
gives two commands: `pdf-word-finder`, the command line program, and
`pdf-word-finder-gui`, the window (§10).

```bash
pip install .
```

To keep it apart from the Python of the system, it is better to install it
in its own environment, which is what `pipx` and `uv` do:

```bash
pipx install .
uv tool install .
```

Optionally:

```bash
pip install pymupdf        # or, from the project folder: pip install ".[mupdf]"
```

If `pymupdf` is installed, the program uses it automatically to extract the
text, because it respects better the reading order in pages with two
columns, footnotes or critical apparatus. If it is not installed, the
program uses `pypdf`, which is enough for texts with a simple layout. You
don't need to say anything: the choice is automatic, and the "Acerca de..."
(About) button of the graphical interface tells you which one is in use
(§10).

> **Note.** PyMuPDF is imported as `pymupdf`, not with the old name `fitz`.
> The old name still works, but it prints a deprecation warning **in the
> standard output**, so the warning would go inside your list when you
> redirect it to a file. Also, its removal is already announced. I keep it
> only as a fallback for old versions of the library.

Without installing anything, you only need `pypdf`, and you work from the
folder `src/`:

```bash
pip install "pypdf[crypto]"
cd src
python -m pdf_word_finder libro.pdf amor     # command line
python -m pdf_word_finder.gui                # window
```

With a Python older than 3.14 the program does not start: it says so, in
one line, instead of failing with a syntax error.

> **About the names.** The package has underscores (`pdf_word_finder`)
> because the hyphen is not a valid character in a Python identifier. The
> console commands and the executables, on the other hand, have hyphens:
> `pdf-word-finder`. This is not an inconsistency, it is the normal
> convention in Python.

### Layout of the project

```
src/pdf_word_finder/     the program
    __init__.py          version and metadata; checks the Python version
    extraction.py        opens the PDF: the text and the label of each page
    text.py              normalization of the text, Spanish alphabetical order
    patterns.py          from a term to a regular expression
    search.py            the search, shared by the console and the window
    report.py            the report and the export to TXT and CSV
    cli.py               the command line program
    gui.py               the graphical interface (tkinter)
    _argparse_es.py      the messages of argparse, in Spanish
tests/                   the tests (pytest)
packaging/               the PyInstaller recipe and its two launchers
scripts/                 construir.py and subir_version.py
windows/                 the launcher and the shortcut for Windows
docs/                    the open-source software used, and its licenses
pyproject.toml           the data of the package and its dependencies
```

The tests use small PDFs that they make themselves, with and without a
`/PageLabels` tree, so the repository does not keep any PDF:

```bash
pip install -e ".[dev]"
pytest
```

---

## 3. Basic use

```bash
pdf-word-finder libro.pdf amor virtus "de rerum natura"
```

Output:

```
amor i, 1, 4
virtus 4
```

One line for each term, with the pages separated by commas. This is the
shape of an index, so you can paste it as it is in the manuscript of the
edition, or import it into a word processor without changes.

The terms that do not appear don't make the list dirty. They are reported
apart:

```
sin apariciones: de rerum natura
```

("sin apariciones" means "no occurrences".)

This note, like all the other warnings, goes to the **error channel**
(stderr) and not to the standard output. In practice this means that if you
redirect the result to a file you get a clean index, and you still see the
warnings on the screen:

```bash
pdf-word-finder libro.pdf --words-file onomastico.txt > indice.txt
```

With `--detailed` you get instead the long report, with the count for each
term and one page per line:

```
«amor»: 7 apariciones en 3 páginas
    i
    1 ×4
    4 ×2
```

(That is: "amor": 7 occurrences in 3 pages.) Here the `×` shows how many
times the term appears on each page, and this is also the only format where
the context fragments fit (§7).

Phrases with several words are written between quotes. Internally the
spaces become `\s+`, so the phrase is found even if it is broken by a line
break or by a page break of the typesetter.

---

## 4. Lists of terms in a file

For a long vocabulary it is better to put it in a text file, one term per
line. The sign `#` starts a comment:

```text
# terminos.txt — vocabulario del Dialogus
Marcolphus
Salomon
rusticus          # cf. la nota de la p. 44
"scientia divina"
re:sapient(ia|em|iae)
```

```bash
pdf-word-finder libro.pdf --words-file terminos.txt
```

The terms in the file are added to the terms you write in the command line,
so you can combine both.

---

## 5. Regular expressions

There are two ways to use them.

**Per term**, with the prefix `re:`. This lets you mix patterns and literal
words in the same search:

```bash
pdf-word-finder libro.pdf amor "re:virtu(s|tem|tis)" "de rerum natura"
```

**All together**, with `--regex`, when *all* the terms are patterns:

```bash
pdf-word-finder libro.pdf --regex "Marcolph\w*" "am(or|oris|orem)"
```

Some useful patterns for philological work:

| Pattern | Finds |
|---|---|
| `re:\bMarcolph\w*` | all the inflected forms of a proper name |
| `re:(?:im)?possibil\w+` | a word family with an optional prefix |
| `re:\d{1,2}[.,]\s*\d+` | references like "12, 34" |
| `re:[A-Z]{2,}` | small caps and acronyms transcribed in capitals |
| `re:qu[oa]d\s+\w+` | a syntactic collocation |

By default the patterns are **not** delimited: the person who writes the
expression decides where it starts and where it ends. If you prefer that
they get the same word boundaries as the literal terms, add `--regex-word`:

```bash
pdf-word-finder libro.pdf "re:amor|virtus" --regex-word
```

The alternation is grouped before the boundaries are applied, so in
`amor|virtus` both branches are delimited, not only one of them.

If an expression is malformed, the program stops with a clear message
instead of a stack trace:

```
error: expresión regular mal formada «amor(»: missing ), unterminated subpattern at position 4
```

("expresión regular mal formada" means "malformed regular expression".) The
second half of this message comes from the `re` module of Python and is
always in English.

---

## 6. Options

| Option | Effect |
|---|---|
| `--words-file FILE` | reads more terms from a file |
| `--regex` | treats all the terms as regular expressions |
| `--regex-word` | applies word boundaries also to the expressions |
| `--substring` | searches also inside words |
| `--case-sensitive` | makes a difference between upper and lower case |
| `--ignore-accents` | ignores diacritical marks |
| `--no-dehyphenate` | keeps the hyphenation at the end of the line |
| `--show-logical` | adds the sequential page in square brackets |
| `--detailed` | long report instead of the compact list |
| `--context` | shows a fragment of each occurrence (implies `--detailed`) |
| `--context-width N` | width of the fragment (60 characters by default) |
| `--sort` | sorts the list alphabetically |
| `--txt FILE` | exports the alphabetized list to a text file |
| `--csv FILE` | also writes the results to a CSV |

The option names are in English on purpose, because this is the convention
for command line tools, and because then you can copy them from the
documentation of other utilities without surprises. But all the help and
all the messages are in Spanish.

### Whole words or fragments

By default the program searches **whole words**: `amor` does not find
`amoroso` or `desamor`. The boundaries are not done with `\b`, but with
lookbehind and lookahead `(?<!\w)…(?!\w)`. This is important when the term
has an apostrophe, a hyphen or punctuation, because in those cases `\b`
gives results that are against intuition.

With `--substring` the program searches in any position:

```bash
pdf-word-finder libro.pdf amor --substring
```

### Diacritics

`--ignore-accents` removes the diacritical marks both from the text and from
the terms, so `busqueda` finds `búsqueda`, and `philologia` finds
`philología`. This is very useful with OCR of old printed books, where
accents are often lost or invented.

**Warning for texts with metrical or critical notation:** the option also
folds the search terms. So a pattern that you wrote on purpose to make a
difference between macrons (`ā`) or diaereses (`ë`) silently stops making
that difference. Use one thing or the other, not both.

### Hyphenation

By default, `philo-\nlogia` is joined again into `philologia` before the
search, so the words broken at the end of a line are not lost. All the
Unicode hyphens are considered, including the soft hyphen (`U+00AD`) that
some PDF generators insert.

There is one case where this is bad: compounds with a real hyphen that by
chance are broken exactly there. If your text has many of them,
`--no-dehyphenate` turns this behaviour off.

---

## 7. Context, export and alphabetical order

```bash
pdf-word-finder libro.pdf amor --context --context-width 80
```

```
«amor»: 2 apariciones en 2 páginas
    i
        …Prefacio: el amor cortés y la philología medieval…
    1
        …Capítulo I. Marcolphus responde al rey. El AMOR vence todo…
```

The fragment is indented under the page number, so you can still read the
column of numbers at a glance. `--context` turns on the detailed report by
itself, because in the compact list there is no place for the fragments.
You don't need to add `--detailed`.

### Export the list to a text file

```bash
pdf-word-finder libro.pdf --words-file onomastico.txt --txt indice.txt
```

`--txt` writes the list **always in alphabetical order**, one term per line,
without headers or notes: only the entries, ready to paste in the manuscript
of the edition.

```
amor i, 1, 4
Marcolphus 1, 4
philologia i, 4
virtus 4
```

The order follows the Spanish alphabet. It ignores accents and capital
letters ("ámbito", "Ámbito" and "ambito" go to the same place), but it
**keeps the ñ as its own letter**, after n. So "leña" goes after "lengua",
and it is not mixed with the n's. *Ch* and *ll* are sorted as c+h and l+l,
following the reform of the Spanish Academy of 1994. It does not depend on
the locale settings of the system, so the result is the same on any
computer.

The file is written in UTF-8 and with a final line break, so it behaves well
in any editor.

If you also want to see the list sorted on the screen, `--sort` does the
same for the standard output. By default the output keeps the order in
which you gave the terms, which is sometimes the one you want (the order of
a working script, for example).

### Send it to a spreadsheet

To send the results to a spreadsheet:

```bash
pdf-word-finder libro.pdf --words-file terminos.txt --context --csv indice.csv
```

The CSV has the columns `termino` (term), `pagina_secuencial` (sequential
page), `pagina_rotulada` (labelled page), `apariciones` (occurrences) and
`contexto` (context), with one row for each term and page. There **both**
numberings are kept on purpose, even if on the screen you see only the
labelled one. A data file is filtered and sorted later, and having the
sequential page at hand saves you from repeating the search if one day you
need to check a page in the viewer. You can just hide the column. The file
is encoded in UTF-8. If you open it in Excel and the accents look wrong, you
have to import it and choose this encoding, instead of opening it with a
double click. The rows come out in alphabetical order by term, like in the
TXT.

The messages saying that one file or the other was written go to the error
channel, not to the standard output. So you can still redirect the list to a
file and export at the same time, and they don't get mixed.

---

## 8. Diagnosis

The program warns you when some pages gave no text:

```
nota: 12 de 340 páginas no arrojaron texto (¿digitalización sin OCR?).
```

(That is: "note: 12 of 340 pages gave no text (scan without OCR?)".)

Almost always this means one of three things: those pages are scanned images
without a text layer; they are really blank; or they are plates. If the
warning covers *all* the pages, the whole PDF is a scan, and no text search
will give results until you apply OCR to it (for example with `ocrmypdf`,
which keeps the page labels).

Remember also that text extraction from a PDF is never perfect. Fonts that
are not embedded, old encodings and character sets for medieval Latin
sometimes produce silent substitutions. When a term that you know is there
appears as "sin apariciones", it is worth to search a shorter fragment with
`--substring` before you accept that it is absent.

---

## 9. A complete example

Index of proper names for a critical edition: the alphabetized list for the
manuscript, the CSV to verify, and the context on the screen to check
during the work, ignoring accents because the OCR is irregular:

```bash
pdf-word-finder dialogus.pdf \
    --words-file onomastico.txt \
    --ignore-accents \
    --context --context-width 90 \
    --txt indice_onomastico.txt \
    --csv indice_onomastico.csv
```

The TXT is ready to paste into the manuscript. The CSV, sorted by term, is
for checking: the column `pagina_rotulada` is the one that is printed, and
`pagina_secuencial` stays in reserve, to find each passage in the viewer if
you need to compare it.

---

## 10. Graphical interface

The command `pdf-word-finder-gui` opens a simple window, for people who
prefer not to use the console, or for occasional searches where it is not
worth to remember the options.

```bash
pdf-word-finder-gui
python -m pdf_word_finder.gui      # without installing, from the folder src/
```

It does not duplicate a single line of the search logic: **the window and
the command line are two modules of the same package** (`gui.py` and
`cli.py`), and they call the same functions: `search()` to search,
`build_report()` to make the report, `write_txt()` and `write_csv()` to
export. Any correction you make in the text extraction, in the
normalization or in the construction of patterns appears in both without
touching them. They cannot get out of sync.

The window offers the same as the command line: a file selector, a box to
write the terms (one per line, with `re:` and `#` like in a list file),
checkboxes for all the options, results in a monospaced font, a checkbox to
change from the list report to the detailed one, and buttons to save the
alphabetized list as TXT, export the CSV or copy the report to the
clipboard. The button "Cargar lista..." (Load list) lets you load a file of
terms that you already prepared.

On the right side, the button **"Acerca de..."** (About) opens a window with
the version, the author, a summary of the license and a section of technical
data: the version of Python and of Tcl/Tk, the version of pypdf, if PyMuPDF
is installed (and so which of the two is extracting the text), if the
program runs from the source code or as a standalone executable, and the
operating system. A button copies all of this to the clipboard. This is not
decoration: when somebody reports that "it does not find a word that is
there", the first thing you need to know is which extractor read the PDF.

It only needs **tkinter**, which comes with Python. If it is missing on
Linux:

```bash
sudo apt install python3-tk          # Debian, Ubuntu
sudo dnf install python3-tkinter     # Fedora
```

Three internal decisions that are good to know, in case one day you modify
the code:

**Errors don't close the window.** The functions of the package do not stop
the program when the PDF cannot be opened or a regular expression is
malformed: they raise an exception (`PdfError`, `PatternError`). The command
line turns it into an error message and an exit code; the window, into a
dialog box with the same message.

**The search runs in a separate thread.** Extracting the text of a whole
book takes some seconds, and doing it in the main thread would freeze the
window. The result comes back through a queue, which the main thread checks
every tenth of a second, because tkinter does not allow another thread to
touch the widgets. Also, the format of the report is made by `report.py` and
not by the interface, so here too there cannot be two versions that
diverge. The only difference is that in the window the warnings are shown
together with the results, while in the console they go to the error
channel. Also, the extracted text stays in memory: if you change a checkbox
and search again, the PDF is not read again.

---

## 11. Distribution

For people who have Python installed, the source code is enough (§2). To give it
to somebody who does not have it (a research assistant, a colleague from
another department) you must package it as a standalone executable.

### PyInstaller

The recipe is in `packaging/pdf_word_finder.spec`, and
`scripts/construir.py` ("build") runs it and packages the result. In the
project folder:

```bash
pip install pyinstaller "pypdf[crypto]"
python scripts/construir.py
```

The result is `dist/pdf-word-finder-SYSTEM-VERSION.zip` (SYSTEM is
`linux`, `win` or `macos`), which has inside the folder `pdf-word-finder/`
with the executables, the license, the READMEs, the changelogs and
`docs/`. You can also use the recipe alone:

```bash
pyinstaller --clean --noconfirm packaging/pdf_word_finder.spec
```

In `dist/pdf-word-finder/` you get the two programs (the graphical
interface and the console one) together with the subfolder `_internal/`,
with the interpreter and the libraries that both share. None of this needs
Python on the target computer. The whole folder is about 50 MB, and **you
distribute it complete, compressed**: the executables don't work if you take
them out of it.

#### Folder or single file

This is the default mode, and it is better that it stays like this. The
alternative is a single executable for each program:

```bash
PWF_ONEFILE=1 pyinstaller packaging/pdf_word_finder.spec          # macOS and Linux
$env:PWF_ONEFILE=1; pyinstaller packaging/pdf_word_finder.spec    # Windows, PowerShell
```

A single file is more comfortable to send, but you pay two prices. The first
is speed: the single executable is decompressed into a temporary folder **on
every run**. Measured on this same computer, starting and showing the
version:

| | Folder mode | Single file |
|---|---|---|
| startup | 79 ms | 264 ms |

The second price is worse: to decompress itself in a temporary folder and
run code from there is, structurally, what some malware does, and some
antivirus programs treat it like that. The folder mode does nothing of this
and is much less suspicious. If a colleague says that Windows "cannot access
the file" (a misleading message that Defender often uses to say that it
blocked something), the folder mode is the first answer.

Strictly speaking the folder mode takes more disk space (about 50 MB against
33 MB for the two single executables together), but when compressed for
distribution the difference is smaller, and anyway this is not what is
important here.

**You cannot compile for other systems.** PyInstaller packages the
interpreter of the machine where it runs, so the Windows `.exe` must be
built on Windows, the macOS `.app` on a Mac, and the Linux binary on Linux.
There is no cross-compilation option, and emulators don't help. You need
access to the three machines (see below).

Two particularities of this recipe that you should not forget if one day you
modify it:

The recipe needs neither `datas` nor `hiddenimports`, and it is good to
understand why. PyInstaller finds out what to package **by analyzing the
code to look for imports**. The executables start from two minimal files,
`packaging/lanzador_cli.py` and `packaging/lanzador_gui.py`, which import
the package with a normal `import`; the recipe tells PyInstaller where the
package is (`pathex`, the folder `src/`), and from there it finds `pypdf` and
its dependencies. Everything goes in by itself.

The launchers exist because a module of a package cannot run alone: its
relative imports (`from .search import ...`) fail outside the package.
PyMuPDF, on the other hand, stays out even if it is installed, because the
program loads it with `importlib` and PyInstaller does not see it. This is
what we want: it would add some 40 MB, and its license is the AGPL.

**The name of the executable is independent from the name of the file.** It
is declared in `name`, inside each `EXE` block, and this is why the
executables are called `pdf-word-finder` and `pdf-word-finder-gui` even if
the sources have underscores.

### Building on each system and publishing

Since version 1.4 there is no automatic build: the project no longer has a
GitHub workflow. Each package is built on its own system with
`scripts/construir.py` and attached by hand to the release. The order is
this:

```bash
python scripts/subir_version.py 1.6        # the new version, everywhere
python scripts/subir_version.py --revisar
git commit -am "Versión 1.6"
git tag -a 1.6 -m "Versión 1.6"
git push origin main 1.6
python scripts/construir.py                # on each system
```

Three things to keep in mind:

* **On Linux, build on the oldest system you want to support.** A Linux
  binary needs a glibc equal to or older than the one of the machine where
  it was built. Built on a recent distribution, it does not open on an
  older one; the other way round there is no problem.

* **On macOS the package is made with `ditto`, not with `zip`.** The `.app`
  bundle contains symbolic links that `zip` turns into copies, and the
  resulting application does not open on the target machine.
  `scripts/construir.py` already does it this way. It is a classic mistake,
  and hard to diagnose, because the build does not complain.

* **The tag and `__version__` must match.** A tag `1.3` on code that says
  it is 1.2 produces downloads that lie about themselves, and this cannot be
  fixed later: published releases cannot be edited without breaking the
  links of people who already downloaded. You change the version with
  `scripts/subir_version.py` (§12), and the package takes its name from
  `__version__`.

### Publish a release by hand

There are two ways.

On the web: "Releases" tab → "Draft a new release" → "Choose a tag" (you can
create it right there) → drag the files from `dist/` to the attachments
area → "Publish release".

On the console, with the official tool `gh`:

```bash
gh release create v1.6 \
    dist/pdf-word-finder-linux-1.5.zip \
    dist/pdf-word-finder-win-1.5.zip \
    --title "pdf-word-finder 1.6" \
    --notes "Versión 1.6."
```

In both cases remember that the packages must be built on each operating
system, so by hand you can only attach the one of the machine in front of
you.

### If Windows or macOS refuse to open it

The executables have no digital signature, and both systems notice it. On
macOS, Gatekeeper will refuse to open the application: the way out is to
right-click on it and choose "Open", which offers a one-time exception. On
Linux there is no obstacle; `chmod +x` is enough. Windows needs its own
section.

#### On Windows 11

This is what you have to explain to the person who receives the program. It
is a good idea to paste it as it is in the email, because people who don't
know this often conclude that the file is damaged and delete it.

**1. Unblock the file.** Windows marks everything that comes from the
internet with an invisible flag, and it is this flag (not the program) that
causes the warning. Right-click → Properties → at the very bottom, checkbox
**"Unblock"** → OK.

If what you received is a `.zip`, it is better to unblock it **before**
extracting it: this way all its content is cleaned at once, and you don't
have to repeat the operation with every extracted file. If it is a single
`.exe`, you do it directly on it.

After this, normally the warning of the next point does not appear anymore:
unblocking is exactly to take away from Windows the reason to be
suspicious. Point 2 is there just in case.

**2. When you run it, a blue screen will appear** saying "Windows protected
your PC". It is not an error and not a virus: it is the unknown publisher
warning. Press **"More info"** (only then the button appears) and then
**"Run anyway"**.

This is enough the first time; after that it opens without asking.

If you prefer to do it from PowerShell, one command replaces the first
step:

```powershell
Unblock-File .\pdf-word-finder-gui.exe        # a single file
Get-ChildItem -Recurse .\pdf-word-finder | Unblock-File   # a folder
```

Two situations where this does not work, both specific to Windows 11:

* **Smart App Control.** This is a protection that is active in some clean
  installations of Windows 11, and it blocks every unsigned program with no
  appeal: there is no "run anyway". You can check it in Windows Security →
  App & browser control. Turning it off is **irreversible** (you cannot turn
  it on again without reinstalling the system), so it is not something you
  should ask anybody to do. If the person has it active, the sensible thing
  is to give them the source code and let them install Python (see below).

* **S mode.** It only allows programs from the Microsoft Store. Leaving S
  mode is free, but also irreversible.

If in addition the antivirus puts the file in quarantine (this is different
from the warning above), you have to restore it from Windows Security →
Virus & threat protection → Protection history, or exclude the folder.
Exclusions lower the guard of the system in that folder, so use them only on
a folder you control, and not on Downloads.

Note that none of this happens with the executables that you build yourself
on your machine: the flag is put by the download, not by the program. Only
people who receive it through the internet will see it.

> **Distribute it inside a `.zip`, not as a single `.exe`.** This is not for
> comfort: a naked `.exe` also hits obstacles before Windows. Chrome and
> Edge mark it in the downloads bar and ask for an extra "Keep anyway", and
> most email services (Outlook and Gmail among them) reject executable
> attachments directly, sometimes without telling the sender. Compressed,
> none of these two things happen. This is why `scripts/construir.py`
> packages before publishing.

#### The other problem: antivirus programs

Different from the warning above, and more annoying, is that the
executables made with PyInstaller trigger **false positives** in some
antivirus programs. The reason is structural: a single-file executable
decompresses itself in a temporary folder and runs code from there, which is
exactly what some malware does.

Two free remedies:

* **Build in folder mode**, which is what the recipe does by default exactly
  for this reason. See "Folder or single file", above.

* **Report the false positive.** Microsoft and the other vendors have forms
  for this, and they usually fix it in a few days.

### For colleagues on Windows: the way without executable

Windows Defender quite often blocks the executables made with PyInstaller,
and the message it uses ("Windows cannot access the specified file") looks
like a permission problem, but it is not. Reporting the false positive to
Microsoft fixes it for everybody in some days, but meanwhile your colleagues
cannot open the program, and on computers managed by the university maybe
it is never fixed.

The way that does not depend on any of this is to not distribute an
executable. Python is free, it installs from the Microsoft Store without
administrator permissions, and no antivirus complains about a `.py` file.

So that a colleague only needs a double click, the project includes
`windows/pdf-word-finder.bat`. You distribute a `.zip` with the source code
(the one that GitHub offers for each version works as it is), in which two
folders matter:

```
src/pdf_word_finder/       the program
windows/pdf-word-finder.bat
```

and the instruction is: extract it and double-click
`windows\pdf-word-finder.bat`. The launcher looks for the program in the
folder `src`, next to its own, and opens it from there with
`pythonw -m pdf_word_finder.gui`.

The launcher takes care of everything else. If `pypdf` is missing, it
installs it without asking (it takes some seconds and has no downside). If
Python 3.14 or newer is missing, on the other hand, **it asks for permission
first** (an older Python counts as if there were none):
installing a 100 MB program on the computer of another person is not
something that should happen by surprise. Once accepted, it tries first with
`winget`, which comes with Windows 11 and does not force the user to choose
anything. If `winget` is not available or fails, it opens the Microsoft
Store on the Python page and explains the three steps to do there.

After installing Python, the launcher goes on and opens the program. A
console window inherits the list of programs of the system when it opens and
does not update it, so it cannot see a Python that just appeared; this is
why the launcher looks for it in the folders where it is usually installed.
If it still does not find it, it asks to close the window and double-click
again, and it says it with these words, so nobody concludes that something
went wrong.

If something fails (`tkinter` is missing, or pip cannot reach the network
because of the proxy) it says so in Spanish and explains what to do,
instead of just closing.

Three details of this file that you should not "fix":

* **It is written without accents.** The Windows console does not use UTF-8
  by default, and the accents would come out unreadable. It is ugly on
  purpose.

* **It has CRLF line endings**, which is what the `.bat` format requires. If
  you edit it in a Linux or macOS editor, keep this detail.

* **It opens the window with `pythonw`** and not with `python`, so that no
  black console window stays behind.

About the version of Python it installs: `winget` identifies each series
separately (`Python.Python.3.14`, `Python.Python.3.15`...) and there is no
generic identifier that means "the newest". The launcher tries them from
higher to lower and keeps the first one it finds in the catalog, so it
installs the newest available one without any maintenance. The list goes
from 3.19 down to 3.14, the oldest that the program accepts; if one day it
is needed, you just add numbers at the beginning.

#### A shortcut in the Start menu

The Windows equivalent of the Linux `.desktop` file is a `.lnk` shortcut
saved in the Start menu folder of the user:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs
```

You create it with `windows\crear-acceso-directo.bat`, which you run only once, and
which also offers to put a shortcut on the desktop. After that, the program
opens from the Start menu like any other application.

The shortcut **does not point to the `.bat`**, but directly to
`pythonw.exe`, with `-m pdf_word_finder.gui` and the folder `src` as the
working folder. This solves two things
at the same time: no black console window stays behind, and Windows does not
apply to shortcuts the filter that it applies to command files downloaded
from the internet. (This filter is the reason why a freshly downloaded
`.bat` is blocked when you double-click it in the Explorer, even if it works
perfectly from the terminal.)

> If you prefer not to run anything: right-click on `pdf-word-finder.bat` →
> "Show more options" → "Create shortcut", and drag the result to the folder
> above. The effect is the same, except that the shortcut will point to the
> `.bat` and will inherit its block, if it has one.

About this block: you remove it once and for all with

```powershell
Unblock-File .\pdf-word-finder.bat
```

or by unchecking it in Properties, as explained above.

### Lighter alternatives

If the person has Python, there are simpler ways than a 20 MB executable:

* **The source code.** The folder `src/` and `pip install "pypdf[crypto]"`
  (§2). For colleagues with some technical skill this is the simplest.

* **A `.pyz` file.** `zipapp` packages everything in one single file that
  Python can run, of only a few KB. It needs Python on the target machine,
  but it is distributed as one unit.

* **The installable package.** The project already is one: `pipx install .`
  makes the commands `pdf-word-finder` and `pdf-word-finder-gui` available
  in the whole system (§2). It is also the way if one day the program is
  published on PyPI.

---

## 12. Version

Version **1.6**. You can check the number from the program itself:

```bash
pdf-word-finder --version
```

```
pdf-word-finder 1.6 — © Nicolás Vaughan 2026 — licencia GPL-3.0-or-later
```

### Changing the version number

The number lives in only one place: `__version__`, in
`src/pdf_word_finder/__init__.py`. The program and the window take it from
there, and so do `pyproject.toml` (as a dynamic version) and the PyInstaller
recipe, which reads it from the file when it builds, so none of them can
stay behind. The READMEs (`README.md` and this translation, `README_en.md`) are
the exception: they mention the number in several places and cannot deduce
it. For this there is `scripts/subir_version.py` ("raise version"):

```bash
python scripts/subir_version.py 1.6        # changes the version everywhere
python scripts/subir_version.py --mostrar  # says which one is the current
python scripts/subir_version.py --revisar  # checks that everything matches
```

The `--revisar` mode is a safety net before making a tag: it returns an
error code if one of the READMEs mentions a version different from the one
of the program, so you can call it from a git hook.

The patterns of the script are anchored to their context (`**Versión X**`,
`**Version X**`, `git tag -a X`, `pdf-word-finder X — ©`...) and they don't
replace loose numbers. This is on purpose: a "1.2" lost in any line could be
something else, and breaking it would be difficult to notice. If you add to
a README a new mention of the version with a different shape, you should add
also its pattern to the script.

In the code it is declared only once, in `__version__`, and from there it is
taken both by `--version` and by the header. When you modify the program it
is enough to change it in this single place.

---

## 13. License and authorship

© Nicolás Vaughan 2026.

Distributed under the **GNU General Public License (GPL), version 3 or (at
your option) any later version**. The full text is in the file `LICENSE`
that comes with this README. In short: anybody can use, study, copy, modify
and distribute the program, also for money, with the condition that what
they distribute (the program as it is, or a modified version) goes under the
same license, keeps the copyright and license notices, and comes together
with its source code (or with an offer to get it). The program is given "as
is", without any kind of warranty.

When you distribute the code, distribute the whole project, or at least
`src/`, `pyproject.toml`, `README.md`, `README_en.md`, `LICENSE` and `docs/`,
and also `packaging/` and `scripts/` if you want that others can build the
executables. The reason is that the copyright notice inside the program
points to `LICENSE`. The packages made by `scripts/construir.py` already
carry the license and `docs/` inside.

The open-source software the program is made with (Python, pypdf, Tcl/Tk,
PyInstaller and the libraries that go inside the packages) is listed, with
its version and its license, in
[`docs/THIRD_PARTY_LICENSES.md`](docs/THIRD_PARTY_LICENSES.md) (in Spanish,
[`docs/LICENCIAS_DE_TERCEROS_es.md`](docs/LICENCIAS_DE_TERCEROS_es.md)).
All these licenses are compatible with the GPL.
