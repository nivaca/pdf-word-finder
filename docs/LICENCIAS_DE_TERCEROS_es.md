Software libre usado en pdf-word-finder
=======================================

pdf-word-finder es © Nicolás Vaughan 2026 y se distribuye bajo la Licencia
Pública General de GNU, versión 3 o posterior (GPL-3.0-or-later); el texto
completo está en `LICENSE`. Está construido sobre el software libre que se
enumera aquí. Todas las licencias de la lista son compatibles con la
GPL-3.0-or-later, de modo que el programa y los paquetes hechos a partir de
él pueden distribuirse bajo la GPL.

Las versiones son las de la versión 1.6, construida en Linux (Fedora) con
Python 3.15. Las licencias van con su identificador SPDX.

Contacto: nicolasvaughan@proton.me


1. Lo que el programa necesita para funcionar
---------------------------------------------

| Software | Versión | Licencia | Para qué |
|---|---|---|---|
| [Python](https://www.python.org/) | 3.15.2 | PSF-2.0 | el lenguaje y su biblioteca estándar (`argparse`, `csv`, `re`, `unicodedata`, `threading`…) |
| [pypdf](https://github.com/py-pdf/pypdf) | 7.1.1 | BSD-3-Clause | lee el PDF: las páginas, su texto y el árbol `/PageLabels` |
| [Tcl/Tk](https://www.tcl-lang.org/) (mediante `tkinter`) | 9.0.4 | TCL | la ventana de la interfaz gráfica |

Opcional, solo si está instalado:

| Software | Licencia | Para qué |
|---|---|---|
| [PyMuPDF](https://github.com/pymupdf/PyMuPDF) (con MuPDF) | AGPL-3.0-or-later (o una licencia comercial de Artifex) | extrae el texto mejor que pypdf. Nunca va en los paquetes; el programa lo carga solo si quien lo usa lo instaló. |


2. Lo que se usa para construirlo y probarlo
--------------------------------------------

Estos programas hacen los ejecutables y ejecutan las pruebas, pero de ellos
solo entra en los paquetes una parte pequeña (el cargador de PyInstaller).

| Software | Versión | Licencia |
|---|---|---|
| [PyInstaller](https://pyinstaller.org/) | 6.22.3 | GPL-2.0-or-later, con una excepción que permite incluir su cargador en programas de cualquier licencia |
| [pyinstaller-hooks-contrib](https://github.com/pyinstaller/pyinstaller-hooks-contrib) | 2026.10 | GPL-2.0-or-later OR Apache-2.0 |
| [altgraph](https://github.com/ronaldoussoren/altgraph) | 0.17.5 | MIT |
| [packaging](https://github.com/pypa/packaging) | 26.3 | Apache-2.0 OR BSD-2-Clause |
| [setuptools](https://github.com/pypa/setuptools) | 84.2.1 | MIT |
| [uv](https://github.com/astral-sh/uv) (para crear el entorno de construcción) | 0.13.7 | Apache-2.0 OR MIT |
| [pytest](https://pytest.org/) (para ejecutar las pruebas) | 9.2.0 | MIT |
| [pluggy](https://github.com/pytest-dev/pluggy) e [iniconfig](https://github.com/pytest-dev/iniconfig) | 1.7.0, 2.3.1 | MIT |
| [Pygments](https://pygments.org/) (lo necesita pytest) | 2.21.0 | BSD-2-Clause |


3. Lo que va dentro de los paquetes
-----------------------------------

Un paquete (`pdf-word-finder-linux-1.6.zip`) lleva su propio intérprete de
Python y las bibliotecas que necesita, en la carpeta `_internal/`. Además de
Python, pypdf y Tcl/Tk (sección 1), contiene:

| Software | Versión | Licencia | Por qué está |
|---|---|---|---|
| [cryptography](https://github.com/pyca/cryptography) | 50.0.2 | Apache-2.0 OR BSD-3-Clause | pypdf la usa para abrir PDF cifrados |
| [cffi](https://github.com/python-cffi/cffi) | 2.1.1 | MIT-0 | la necesita cryptography |
| [OpenSSL](https://www.openssl.org/) (`libssl`, `libcrypto`) | 4.0.3 | Apache-2.0 | los módulos `ssl` y `hashlib` de Python |
| [mpdecimal](https://www.bytereef.org/mpdecimal/) | 4.0.1 | BSD-2-Clause | el módulo `decimal` de Python |
| [libffi](https://sourceware.org/libffi/) | 3.5.2 | MIT | el módulo `ctypes` de Python |
| [Expat](https://libexpat.github.io/) | 2.9.0 | MIT | los módulos de XML de Python |
| [zlib-ng](https://github.com/zlib-ng/zlib-ng) (`libz`) | 2.3.3 | Zlib | compresión (`zlib`) |
| [bzip2](https://sourceware.org/bzip2/) | 1.0.8 | bzip2-1.0.6 | compresión (`bz2`) |
| [XZ Utils](https://tukaani.org/xz/) (`liblzma`) | 5.8.3 | 0BSD | compresión (`lzma`) |
| [Zstandard](https://facebook.github.io/zstd/) | 1.5.7 | BSD-3-Clause OR GPL-2.0-only | compresión (`zstd`) |
| [libuuid](https://github.com/util-linux/util-linux) (util-linux) | 2.42.4 | BSD-3-Clause | el módulo `uuid` de Python |
| [libtommath](https://www.libtom.net/LibTomMath/) | 1.3.1 | Unlicense | la necesita Tcl |
| [FreeType](https://freetype.org/) | 2.14.3 | FTL OR GPL-2.0-or-later | las fuentes de la ventana (Tk) |
| [Fontconfig](https://www.freedesktop.org/wiki/Software/fontconfig/) | 2.18.3 | HPND | las fuentes de la ventana (Tk) |
| [HarfBuzz](https://harfbuzz.github.io/) | 15.0.0 | MIT-Modern-Variant | composición del texto; la necesita FreeType |
| [Graphite2](https://github.com/silnrsi/graphite) | 1.3.14 | LGPL-2.1-or-later OR MPL-2.0 OR GPL-2.0-or-later | la necesita HarfBuzz |
| [GLib](https://gitlab.gnome.org/GNOME/glib) | 2.90.1 | LGPL-2.1-or-later | la necesita HarfBuzz |
| [PCRE2](https://github.com/PCRE2Project/pcre2) | 10.49 | BSD-3-Clause WITH PCRE2-exception | la necesita GLib |
| [libpng](http://www.libpng.org/pub/png/libpng.html) | 1.6.59 | libpng-2.0 | la necesita FreeType |
| [Brotli](https://github.com/google/brotli) | 1.2.1 | MIT | la necesita FreeType |
| [libxml2](https://gitlab.gnome.org/GNOME/libxml2) | 2.15.4 | MIT | la necesita Fontconfig |
| [libX11](https://gitlab.freedesktop.org/xorg/lib/libx11) | 1.8.13 | X11 | la ventana (sistema X Window) |
| [libXft](https://gitlab.freedesktop.org/xorg/lib/libxft) | 2.3.8 | HPND-sell-variant | las fuentes en X |
| [libXrender](https://gitlab.freedesktop.org/xorg/lib/libxrender) | 0.9.12 | HPND-sell-variant | la necesita libXft |
| [libXau](https://gitlab.freedesktop.org/xorg/lib/libxau) | 1.0.12 | MIT-open-group | la necesita libX11 |
| [libgcc](https://gcc.gnu.org/) (`libgcc_s`) | 16.2.1 | GPL-3.0-or-later WITH GCC-exception-3.1 | soporte de ejecución del compilador |

Las bibliotecas de esta tabla son las del sistema Fedora donde se construyó
el paquete, y la lista exacta cambia un poco con el sistema y con la
versión de PyInstaller. Un paquete para Windows, construido en Windows,
lleva las versiones para Windows de las mismas piezas (Python, Tcl/Tk,
OpenSSL, libffi, zlib, libtommath…) y además el entorno de ejecución de
Microsoft Visual C++ (`VCRUNTIME140.dll`), que no es software libre:
Microsoft permite redistribuirlo con los programas, y el propio Python se
distribuye con él.

El código fuente de cada pieza está en la dirección de su fila, y el texto
completo de cada licencia está en ese código fuente (en el caso de
cryptography, también en `_internal/cryptography-*.dist-info/licenses/`).
Los paquetes llevan esta lista en `docs/`, junto al `LICENSE` del programa.
