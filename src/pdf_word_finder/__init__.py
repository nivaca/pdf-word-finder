"""
pdf-word-finder: busca palabras o frases en un PDF e informa en qué páginas
aparecen, con el número impreso en la página (el rótulo) y no el índice
interno del archivo.

© Nicolás Vaughan 2026. Distribuido bajo la licencia GNU GPL, versión 3 o
posterior (véase LICENSE).

El paquete se divide así:

    extraction   abre el PDF y extrae el texto y los rótulos de las páginas
    text         normalización del texto y orden alfabético español
    patterns     de un término a una expresión regular compilada
    search       la búsqueda: términos × páginas -> apariciones
    report       el informe (lista o detallado) y la exportación TXT y CSV
    cli          el programa de línea de órdenes
    gui          la interfaz gráfica (tkinter)
"""

import sys

# La comprobación va antes que cualquier otra importación del paquete, y con
# una sintaxis que cualquier Python 3 entienda, para que un intérprete viejo
# dé este aviso en vez de un error de sintaxis incomprensible.
if sys.version_info < (3, 14):
    sys.exit("pdf-word-finder necesita Python 3.14 o posterior; este es "
             "Python %d.%d." % sys.version_info[:2])

__version__ = "1.6"
__author__ = "Nicolás Vaughan"
__email__ = "nicolasvaughan@proton.me"
__copyright__ = "© Nicolás Vaughan 2026"
__license__ = "GPL-3.0-or-later"

from .extraction import Document, PdfError, extract_pages, load_pymupdf
from .patterns import PatternError, build_pattern, display_term
from .report import build_report, index_lines, write_csv, write_txt
from .search import Hit, Options, Result, read_terms, search

__all__ = [
    "Document", "Hit", "Options", "PatternError", "PdfError", "Result",
    "build_pattern", "build_report", "display_term", "extract_pages",
    "index_lines", "load_pymupdf", "read_terms", "search", "write_csv",
    "write_txt",
]
