Open-source software used in pdf-word-finder
============================================

pdf-word-finder is © Nicolás Vaughan 2026 and is licensed under the GNU
General Public License, version 3 or later (GPL-3.0-or-later); the full
text is in `LICENSE`. It is built on the open-source software listed
here. Every license below is compatible with the GPL-3.0-or-later, so the
program and the packages made from it can be distributed under the GPL.

The versions are those of version 1.6, built on Linux (Fedora) with
Python 3.15. Licenses are given as SPDX identifiers.

Contact: nicolasvaughan@proton.me


1. What the program needs to run
--------------------------------

| Software | Version | License | Use |
|---|---|---|---|
| [Python](https://www.python.org/) | 3.15.2 | PSF-2.0 | the language and its standard library (`argparse`, `csv`, `re`, `unicodedata`, `threading`…) |
| [pypdf](https://github.com/py-pdf/pypdf) | 7.1.1 | BSD-3-Clause | reads the PDF: the pages, their text and the `/PageLabels` tree |
| [Tcl/Tk](https://www.tcl-lang.org/) (through `tkinter`) | 9.0.4 | TCL | the window of the graphical interface |

Optional, only if it is installed:

| Software | License | Use |
|---|---|---|
| [PyMuPDF](https://github.com/pymupdf/PyMuPDF) (with MuPDF) | AGPL-3.0-or-later (or a commercial license from Artifex) | extracts the text better than pypdf. It is never included in the packages; the program loads it only if the user installed it. |


2. What is used to build and test it
------------------------------------

These programs make the executables and run the tests, but only a small
part of them (the PyInstaller bootloader) goes inside the packages.

| Software | Version | License |
|---|---|---|
| [PyInstaller](https://pyinstaller.org/) | 6.22.3 | GPL-2.0-or-later, with an exception that allows its bootloader in programs under any license |
| [pyinstaller-hooks-contrib](https://github.com/pyinstaller/pyinstaller-hooks-contrib) | 2026.10 | GPL-2.0-or-later OR Apache-2.0 |
| [altgraph](https://github.com/ronaldoussoren/altgraph) | 0.17.5 | MIT |
| [packaging](https://github.com/pypa/packaging) | 26.3 | Apache-2.0 OR BSD-2-Clause |
| [setuptools](https://github.com/pypa/setuptools) | 84.2.1 | MIT |
| [uv](https://github.com/astral-sh/uv) (to make the build environment) | 0.13.7 | Apache-2.0 OR MIT |
| [pytest](https://pytest.org/) (to run the tests) | 9.2.0 | MIT |
| [pluggy](https://github.com/pytest-dev/pluggy) and [iniconfig](https://github.com/pytest-dev/iniconfig) | 1.7.0, 2.3.1 | MIT |
| [Pygments](https://pygments.org/) (needed by pytest) | 2.21.0 | BSD-2-Clause |


3. What goes inside the packages
--------------------------------

A package (`pdf-word-finder-linux-1.6.zip`) carries its own Python
interpreter and the libraries it needs, in the folder `_internal/`. Besides
Python, pypdf and Tcl/Tk (section 1), it contains:

| Software | Version | License | Why it is there |
|---|---|---|---|
| [cryptography](https://github.com/pyca/cryptography) | 50.0.2 | Apache-2.0 OR BSD-3-Clause | pypdf uses it to open encrypted PDFs |
| [cffi](https://github.com/python-cffi/cffi) | 2.1.1 | MIT-0 | needed by cryptography |
| [OpenSSL](https://www.openssl.org/) (`libssl`, `libcrypto`) | 4.0.3 | Apache-2.0 | Python's `ssl` and `hashlib` modules |
| [mpdecimal](https://www.bytereef.org/mpdecimal/) | 4.0.1 | BSD-2-Clause | Python's `decimal` module |
| [libffi](https://sourceware.org/libffi/) | 3.5.2 | MIT | Python's `ctypes` module |
| [Expat](https://libexpat.github.io/) | 2.9.0 | MIT | Python's XML modules |
| [zlib-ng](https://github.com/zlib-ng/zlib-ng) (`libz`) | 2.3.3 | Zlib | compression (`zlib`) |
| [bzip2](https://sourceware.org/bzip2/) | 1.0.8 | bzip2-1.0.6 | compression (`bz2`) |
| [XZ Utils](https://tukaani.org/xz/) (`liblzma`) | 5.8.3 | 0BSD | compression (`lzma`) |
| [Zstandard](https://facebook.github.io/zstd/) | 1.5.7 | BSD-3-Clause OR GPL-2.0-only | compression (`zstd`) |
| [libuuid](https://github.com/util-linux/util-linux) (util-linux) | 2.42.4 | BSD-3-Clause | Python's `uuid` module |
| [libtommath](https://www.libtom.net/LibTomMath/) | 1.3.1 | Unlicense | needed by Tcl |
| [FreeType](https://freetype.org/) | 2.14.3 | FTL OR GPL-2.0-or-later | fonts of the window (Tk) |
| [Fontconfig](https://www.freedesktop.org/wiki/Software/fontconfig/) | 2.18.3 | HPND | fonts of the window (Tk) |
| [HarfBuzz](https://harfbuzz.github.io/) | 15.0.0 | MIT-Modern-Variant | text shaping, needed by FreeType |
| [Graphite2](https://github.com/silnrsi/graphite) | 1.3.14 | LGPL-2.1-or-later OR MPL-2.0 OR GPL-2.0-or-later | needed by HarfBuzz |
| [GLib](https://gitlab.gnome.org/GNOME/glib) | 2.90.1 | LGPL-2.1-or-later | needed by HarfBuzz |
| [PCRE2](https://github.com/PCRE2Project/pcre2) | 10.49 | BSD-3-Clause WITH PCRE2-exception | needed by GLib |
| [libpng](http://www.libpng.org/pub/png/libpng.html) | 1.6.59 | libpng-2.0 | needed by FreeType |
| [Brotli](https://github.com/google/brotli) | 1.2.1 | MIT | needed by FreeType |
| [libxml2](https://gitlab.gnome.org/GNOME/libxml2) | 2.15.4 | MIT | needed by Fontconfig |
| [libX11](https://gitlab.freedesktop.org/xorg/lib/libx11) | 1.8.13 | X11 | the window (X Window System) |
| [libXft](https://gitlab.freedesktop.org/xorg/lib/libxft) | 2.3.8 | HPND-sell-variant | fonts in X |
| [libXrender](https://gitlab.freedesktop.org/xorg/lib/libxrender) | 0.9.12 | HPND-sell-variant | needed by libXft |
| [libXau](https://gitlab.freedesktop.org/xorg/lib/libxau) | 1.0.12 | MIT-open-group | needed by libX11 |
| [libgcc](https://gcc.gnu.org/) (`libgcc_s`) | 16.2.1 | GPL-3.0-or-later WITH GCC-exception-3.1 | runtime support of the compiler |

The libraries in this table are those of the Fedora system where the
package was built, and the exact list changes a little with the system and
the version of PyInstaller. A Windows package, built on Windows, carries
the Windows builds of the same pieces (Python, Tcl/Tk, OpenSSL, libffi,
zlib, libtommath…) and also the Microsoft Visual C++ runtime
(`VCRUNTIME140.dll`), which is not open-source software: Microsoft allows
it to be redistributed with programs, and Python itself is distributed
with it.

The source code of all these pieces is at the address given in each row,
and the full text of each license is in that source code (for
cryptography, also in `_internal/cryptography-*.dist-info/licenses/`). The
packages carry this list in `docs/`, next to the program's own `LICENSE`.
