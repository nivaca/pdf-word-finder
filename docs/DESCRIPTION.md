How pdf-word-finder was made
============================

pdf-word-finder searches a PDF for a list of words, phrases or regular
expressions and tells on which pages each one appears. What makes it
different from the search of a PDF viewer is the page number it gives: the
number printed on the page, taken from the `/PageLabels` tree of the file,
and not the position of the page inside the file. In an ordinary book the
two numbers differ (the front matter in Roman numerals, the body starting
again at 1), and only the printed one is useful to make an index or to find
a passage in the paper book. Nicolas Vaughan made it in August 2026, for
this kind of work: the indexes of names and terms of an edition. It has a
command line program and a small window. Here I explain how it was made,
in six stages.

pdf-word-finder is free software, under the GNU General Public License,
version 3 or later. It reads the PDF with pypdf (BSD-3-Clause), which uses
cryptography (Apache-2.0 or BSD-3-Clause) for encrypted files; it runs on
Python (PSF License), and the window uses Tcl/Tk (TCL License). If PyMuPDF
(AGPL-3.0) is installed, the program uses it to extract the text, but it
never goes inside the packages. The executables are made with PyInstaller
(GPL-2.0-or-later, with an exception for its bootloader).
[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) lists all the software
it uses, with versions and licenses.

Nicolas Vaughan is Associate Professor of Literature at the School of Arts
and Humanities of the Universidad de los Andes, Bogotá, Colombia.

1. A first version
------------------

The first version (1.1, 18 August 2026) was one script for the command
line and a second one for the window. The main problem was the page
numbers. pypdf gives the labels of the pages, but when the file has no
`/PageLabels` tree it invents "1, 2, 3...", and these look exactly like
real labels. So the program looks in the catalogue of the PDF to know if
the tree exists, and when it does not, it says so in a note, instead of
pretending. With `--show-logical` it adds the position in the file, in
brackets, which is useful to check a label that seems wrong.

The text of a PDF needs some cleaning before searching. Ligatures are
undone (NFKC normalization), words divided by a hyphen at the end of a
line are joined again, and a phrase can be split between two lines. Whole
words are found with lookarounds and not with `\b`, which fails next to an
apostrophe or a hyphen. Terms can be regular expressions, all of them with
`--regex` or one by one with the prefix `re:`.

The output has the form of an index: one line for each term, with its
pages separated by commas. Notes and terms not found go to the error
output, so that the standard output, redirected to a file, is a clean
index. `--detailed` gives instead the count of each term and one page for
each line, where the fragments of context fit. The messages of `argparse`
were translated to Spanish by replacing its `gettext` functions with a
small table, so no catalogue files are needed.

2. A better window, and executables
-----------------------------------

Version 1.2 added the alphabetical order (`--sort`), with the Spanish
alphabet: accents and capitals do not count, but ñ goes after n. The list
can be saved as a text file (`--txt`). The window got an About box, with
the versions of Python, Tcl/Tk, pypdf and PyMuPDF. This is not decoration:
when somebody says that the program does not find a word that is there,
the first question is which library extracted the text. The search runs in
a separate thread, so the window does not freeze with a long book, and the
extracted text stays in memory for the next search. PyMuPDF is imported as
`pymupdf`, because the old name `fitz` prints a warning in the standard
output, which would go inside a redirected index.

To give the program to people without Python I made executables with
PyInstaller. This needed one change of names: the scripts had hyphens,
and a file with a hyphen in its name cannot be imported. With underscores
the window imports the command line program in the normal way, and
PyInstaller finds it, and pypdf with it, without any declaration by hand.
The executables are a folder and not one single file. One file unpacks
itself in a temporary folder every time it runs (on my machine it started
in 264 ms, against 79 ms for the folder), and some antivirus programs
treat this as suspicious. A GitHub workflow built the packages for
Windows, macOS and Linux.

3. Colleagues on Windows
------------------------

The executables had a problem on Windows: Defender blocked them often,
with a message ("Windows cannot access the specified file") that looks
like a problem of permissions. The answer was not to send an executable.
`pdf-word-finder.bat` (versions 1.2 to 1.23) is a launcher that installs
Python with winget, or from the Store, if it is missing, installs pypdf,
and opens the window. It asks before installing Python, but not before
installing pypdf.

Windows gave some surprises. Windows 11 has a fake `python`, an empty file
that only opens the Store, so `where python` finds it; the launcher tests
Python by running it. winget has one identifier for each series of Python
(`Python.Python.3.14`, `3.15`...) and none for "the newest", so the
launcher tries them from the highest down. A console window does not see a
Python installed after it opened, so the launcher looks for it in the
folders where it is usually installed, and goes on. The file has no
accents, because the console does not use UTF-8, and it has CRLF line
endings.

4. One version number
---------------------

Up to 1.23 the version was written in several places, and they did not
always agree. In 1.4 it has only one place, `__version__`, and the window
and the PyInstaller recipe read it from there. The GitHub workflow was
taken out of the repository; since then each package is built on its own
system.

5. License and documentation
----------------------------

In October and November 2026 (version 1.5) the license changed from MIT
to the GNU GPL, version 3 or later. The README, which is in Spanish, got an
English translation, and the project got changelogs in both languages.
`crear-acceso-directo.bat` puts a shortcut in the Windows Start menu, which
runs `pythonw.exe` directly: no console window stays behind, and Windows
does not block it as a downloaded `.bat`. `subir_version.py` changes the
version in all the places of the READMEs and checks that they agree with
the program. The list of the open-source software in the packages, with
their licenses, was taken from the package actually built, not from
memory, because the libraries inside depend on the system where it is
built.

6. A package
------------

Version 1.6 (21 November 2026) reorganized the code. The two scripts
became the package `src/pdf_word_finder/`, with one module for each task:
`extraction` opens the PDF, `text` normalizes the text and gives the
alphabetical order, `patterns` makes the regular expressions, `search`
does the search, `report` makes the report and the exports, and `cli` and
`gui` are the two interfaces. Before, the window had its own copy of the
search loop and of the CSV export; now both interfaces call the same
functions. The functions raised `SystemExit` when a PDF could not be
opened, and the window had to catch it so as not to close; now they raise
their own exceptions, and each interface shows them in its own way.

A `pyproject.toml` makes it installable, with the commands
`pdf-word-finder` and `pdf-word-finder-gui`. The program needs Python 3.14
or later, and with an older one it says so in one line, instead of failing
with a syntax error. The Windows launchers moved to `windows/`, and treat
an older Python as no Python. The PyInstaller recipe moved to
`packaging/`, with two small files to start the executables, because a
module of a package cannot run alone. The recipe had never been in the
repository: the `.gitignore` excluded all `.spec` files. A new script,
`scripts/construir.py`, builds the executables and packs them with the
license and the documentation.

Testing
-------

There are 43 tests (`tests/`, with pytest), which run with Python 3.14,
the oldest supported, and with Python 3.15. They make their own small
PDFs, with and without a `/PageLabels` tree, so the repository keeps no
PDF. They check the normalization of the text and the Spanish order, the
patterns (whole words, phrases, regular expressions, accents), the
extraction of labels and the errors of a missing or broken file, the
search, both reports, the TXT and CSV exports, the command line with its
errors and its Spanish help, and the search of the window.

Before the reorganization of 1.6, I saved the output of the old program
for 18 cases (options, formats, exports and errors) and compared it with
the new one: they differ only in the example of the help. The window was
checked with a script that makes a search, saves both exports, opens the
About box and gives a malformed expression. The Linux package was built
and run. The Windows launchers were not tested on Windows for this
version. The program now has 25 files of code, around 2,400 lines: 1,185
in the package and 382 in the tests.
