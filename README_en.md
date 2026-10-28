# pdf-word-finder

**Version 1.4** · © Nicolás Vaughan 2026 · License GNU GPL v3 or later

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

You need Python 3.9 or newer.

```bash
pip install pypdf
```

Optionally:

```bash
pip install pymupdf
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

The file has the line `#!/usr/bin/env python3`, so on macOS and Linux you
can run it directly if you give it execute permission:

```bash
chmod +x pdf_word_finder.py
./pdf_word_finder.py libro.pdf amor
```

To have it available from any directory, you can copy it to some place in
your `PATH` (for example `~/.local/bin/`), or put there a symbolic link with
the short name of the command:

```bash
ln -s ~/proyectos/pdf-word-finder/pdf_word_finder.py ~/.local/bin/pdf-word-finder
```

Then you just write `pdf-word-finder libro.pdf amor`.

> **About the names.** The source files have underscores
> (`pdf_word_finder.py`) because the hyphen is not a valid character in a
> Python identifier, and a file named `pdf-word-finder.py` could not be
> imported with `import`. The executables and the console commands, on the
> other hand, have hyphens: `pdf-word-finder`. This is not an inconsistency,
> it is the normal convention in Python. And it has a practical advantage:
> because the core is a real importable module, the graphical interface uses
> it with a normal `import`, and the packaging for distribution does not need
> any trick (§11).

---

## 3. Basic use

```bash
python pdf_word_finder.py libro.pdf amor virtus "de rerum natura"
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
python pdf_word_finder.py libro.pdf --words-file onomastico.txt > indice.txt
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
python pdf_word_finder.py libro.pdf --words-file terminos.txt
```

The terms in the file are added to the terms you write in the command line,
so you can combine both.

---

## 5. Regular expressions

There are two ways to use them.

**Per term**, with the prefix `re:`. This lets you mix patterns and literal
words in the same search:

```bash
python pdf_word_finder.py libro.pdf amor "re:virtu(s|tem|tis)" "de rerum natura"
```

**All together**, with `--regex`, when *all* the terms are patterns:

```bash
python pdf_word_finder.py libro.pdf --regex "Marcolph\w*" "am(or|oris|orem)"
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
python pdf_word_finder.py libro.pdf "re:amor|virtus" --regex-word
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
python pdf_word_finder.py libro.pdf amor --substring
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
python pdf_word_finder.py libro.pdf amor --context --context-width 80
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
python pdf_word_finder.py libro.pdf --words-file onomastico.txt --txt indice.txt
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
python pdf_word_finder.py libro.pdf --words-file terminos.txt --context --csv indice.csv
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
python pdf_word_finder.py dialogus.pdf \
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

The file `pdf_word_finder_gui.py` opens a simple window, for people who
prefer not to use the console, or for occasional searches where it is not
worth to remember the options.

```bash
python pdf_word_finder_gui.py
```

It does not duplicate a single line of the search logic: **it loads the
command line program and calls its functions**. Any correction you make in
`pdf_word_finder.py` (in the text extraction, in the normalization, in the
construction of patterns) appears in the interface without touching it. The
two pieces cannot get out of sync.

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
sudo apt install python3-tk
```

Three internal decisions that are good to know, in case one day you modify
the file:

**How the core is loaded.** With a normal `import pdf_word_finder`, which
works because the two files are in the same folder. This is why they must
travel together. If the interface does not find it, it shows a dialog box
instead of failing in silence. That it is a normal import and not a loading
by path is important also for packaging (§11).

**Errors don't close the window.** The functions of the core stop the
program with `sys.exit()` when the PDF is encrypted or a regular expression
is malformed. This is correct in the console, but in the window it would
close everything without explanation. The interface catches this
`SystemExit` and turns it into a dialog box with the same message.

**The search runs in a separate thread.** Extracting the text of a whole
book takes some seconds, and doing it in the main thread would freeze the
window. The result comes back through a queue, which the main thread checks
every tenth of a second, because tkinter does not allow another thread to
touch the widgets. Also, the format of the report is made by the core and
not by the interface, so here too there cannot be two versions that
diverge. The only difference is that in the window the warnings are shown
together with the results, while in the console they go to the error
channel. Also, the extracted text stays in memory: if you change a checkbox
and search again, the PDF is not read again.

---

## 11. Distribution

For people who have Python installed, the `.py` files are enough. To give it
to somebody who does not have it (a research assistant, a colleague from
another department) you must package it as a standalone executable.

### PyInstaller

The file `pdf_word_finder.spec` that comes with the project has the recipe.
In the project folder:

```bash
pip install pyinstaller pypdf
pyinstaller --clean --noconfirm pdf_word_finder.spec
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
PWF_ONEFILE=1 pyinstaller pdf_word_finder.spec          # macOS and Linux
$env:PWF_ONEFILE=1; pyinstaller pdf_word_finder.spec    # Windows, PowerShell
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
There is no cross-compilation option, and emulators don't help. The two
ways out are to have access to the three machines, or to let GitHub do it
(see below).

Two particularities of this recipe that you should not forget if one day you
modify it:

The recipe needs neither `datas` nor `hiddenimports`, and it is good to
understand why, because this is exactly what would break if one day you
renamed the files with hyphens. PyInstaller finds out what to package **by
analyzing the code to look for imports**. Because the interface imports the
core with a normal `import` (§10), it finds it, and with it it finds `pypdf`
and its dependencies. Everything goes in by itself.

If the core had hyphens in the name it could not be imported like this. You
would have to load it by path with importlib, package it as an extra file in
`datas`, declare `hiddenimports=["pypdf"]` by hand (because a file treated as
data is not analyzed, so its imports are invisible), and add code to find it
inside the executable, where the extra files are not next to the program but
in a temporary folder whose path is in `sys._MEIPASS`. The underscores save
you all four things.

**The name of the executable is independent from the name of the file.** It
is declared in `name`, inside each `EXE` block, and this is why the
executables are called `pdf-word-finder` and `pdf-word-finder-gui` even if
the sources have underscores.

### Automatic build and publishing on GitHub

The file `.github/workflows/build.yml` builds the four versions (Windows,
macOS Intel, macOS Apple Silicon and Linux) on the GitHub machines, so you
don't need to have a Windows and a Mac at hand, and it attaches them to a
*release*. All the procedure is reduced to making a tag:

```bash
git tag -a v1.4 -m "Versión 1.4"
git push origin v1.4
```

Some minutes later, in the "Releases" tab of the repository, you will see a
draft with the four packages attached. You check it and press "Publish
release". From that moment anybody can download them, with a permanent link
and without needing a GitHub account.

It comes out as a **draft** on purpose: you should download at least one
package and open it before the link is public. If you prefer that it is
published automatically, change `draft: true` to `draft: false` in the
workflow.

If you start it by hand from the "Actions" tab ("Run workflow" button), it
builds the same but publishes nothing: the packages stay as temporary
artifacts. This is the way to test the build before committing to a tag.

#### Artifacts and releases are not the same

It is good to have the difference clear, because GitHub uses both words and
they are different things:

| | Artifact | Release |
|---|---|---|
| Where | "Actions" tab, inside each run | "Releases" tab |
| How long it stays | deleted after 90 days | permanent |
| Who can download | only with a GitHub session | anybody |
| Format | always a `.zip` imposed by GitHub | the files as they were uploaded |
| What for | testing a build | distributing |

To give the program to a colleague, it must be a release. An artifact is
internal working material.

#### Details of the workflow

Four decisions that you should not undo without knowing why:

* **Ubuntu 22.04** and not the newest version: a Linux binary needs a glibc
  equal or older than the one of the machine where it was built. Compiling
  on the oldest one you want to support makes compatibility wider; the other
  way around does not work.

* **Two macOS entries.** `macos-latest` produces a binary for Apple Silicon;
  Macs with Intel processor need the one from `macos-13`.

* **On macOS the packaging is done with `ditto`, not with `zip`.** The
  `.app` bundle contains symbolic links that `zip` turns into copies, and
  the resulting application does not open on the target machine. It is a
  classic error and difficult to diagnose, because the build does not
  complain.

* **The workflow checks that the tag and `__version__` match**, and it fails
  if they don't. A tag `v1.3` on code that says it is 1.2 produces downloads
  that lie about themselves, and this cannot be fixed later: published
  releases cannot be edited without breaking the links of people who
  already downloaded. When you raise the version you must change
  `__version__` in `pdf_word_finder.py` **and** the two version lines of the
  `.spec`.

### Publish a release by hand

If you prefer not to depend on the automatic workflow, or you want to
publish a build made on your own computer, there are two ways.

On the web: "Releases" tab → "Draft a new release" → "Choose a tag" (you can
create it right there) → drag the files from `dist/` to the attachments
area → "Publish release".

On the console, with the official tool `gh`:

```bash
gh release create v1.4 \
    pdf-word-finder-linux-x64.tar.gz \
    pdf-word-finder-windows-x64.zip \
    --title "pdf-word-finder 1.4" \
    --notes "Versión 1.4."
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
  is to give them the `.py` files and let them install Python.

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
> none of these two things happen. This is why the GitHub workflow packages
> before publishing.

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
`pdf-word-finder.bat`. You distribute a `.zip` with three files:

```
pdf_word_finder.py
pdf_word_finder_gui.py
pdf-word-finder.bat
```

and the instruction is: extract it and double-click the `.bat`.

The launcher takes care of everything else. If `pypdf` is missing, it
installs it without asking (it takes some seconds and has no downside). If
Python is missing, on the other hand, **it asks for permission first**:
installing a 100 MB program on the computer of another person is not
something that should happen by surprise. Once accepted, it tries first with
`winget`, which comes with Windows 11 and does not force the user to choose
anything. If `winget` is not available or fails, it opens the Microsoft
Store on the Python page and explains the three steps to do there.

After installing Python you must close the window and double-click again.
This is not carelessness: a console window inherits the list of programs of
the system when it opens and does not update it, so it cannot see a Python
that just appeared. The launcher says it with these words, so nobody
concludes that something went wrong.

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
installs the newest available one without any maintenance. The list goes up
to 3.19; if one day it is needed, you just add numbers at the beginning.

#### A shortcut in the Start menu

The Windows equivalent of the Linux `.desktop` file is a `.lnk` shortcut
saved in the Start menu folder of the user:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs
```

You create it with `crear-acceso-directo.bat`, which you run only once, and
which also offers to put a shortcut on the desktop. After that, the program
opens from the Start menu like any other application.

The shortcut **does not point to the `.bat`**, but directly to
`pythonw.exe`, giving it the path of the interface. This solves two things
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

* **The loose files.** Four files and `pip install pypdf`. For colleagues
  with some technical skill this is the simplest.

* **A `.pyz` file.** `zipapp` packages everything in one single file that
  Python can run, of only a few KB. It needs Python on the target machine,
  but it is distributed as one unit.

* **An installable package.** With a minimal `pyproject.toml` and a console
  entry point, `pipx install` makes the command `pdf-word-finder` available
  in the whole system. This is the right way if one day you publish the
  program on PyPI, and the current names already work as they are.

---

## 12. Version

Version **1.4**. You can check the number from the program itself:

```bash
python pdf_word_finder.py --version
```

```
pdf-word-finder 1.4 — © Nicolás Vaughan 2026 — licencia GPL-3.0-or-later
```

### Changing the version number

The number lives in only one place: `__version__`, in `pdf_word_finder.py`.
The graphical interface shows `núcleo.__version__`, and the PyInstaller
recipe reads it from the file when it builds, so none of them can stay
behind. The READMEs (`README.md` and this translation, `README_en.md`) are
the exception: they mention the number in several places and cannot deduce
it. For this there is `subir_version.py` ("raise version"):

```bash
python subir_version.py 1.3        # changes the version everywhere
python subir_version.py --mostrar  # says which one is the current
python subir_version.py --revisar  # checks that everything matches
```

The `--revisar` mode is a safety net before making a tag: it returns an
error code if one of the READMEs mentions a version different from the one
of the program, so you can call it from a git hook or from the workflow.

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

When you distribute it, include the files `pdf_word_finder.py`,
`pdf_word_finder_gui.py`, `README.md`, `README_en.md` and `LICENSE`, and
also `pdf_word_finder.spec` if you want that others can build the
executables. The reason is that the copyright notice inside the two programs
points to `LICENSE`, and the graphical interface does not work without the
command line program in the same folder.
