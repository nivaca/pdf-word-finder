"""
El programa de línea de órdenes: busca palabras o frases en un PDF e informa
dónde aparecen.

© Nicolás Vaughan 2026. Distribuido bajo la licencia GNU GPL, versión 3 o
posterior (véase LICENSE).

Informa la página *rotulada* de cada aparición: el número realmente impreso
en la página, tomado del árbol /PageLabels del PDF (numeración romana del
principio, desfases, prefijos, reinicios, láminas sin numerar, etc.). Es
decir, el número que le sirve al lector para abrir el libro, no el índice
interno del archivo.

Con --show-logical se añade entre corchetes la página *secuencial* (lógica):
el índice de la página dentro del archivo, empezando en 1, que es lo que
cuenta la barra de desplazamiento del visor.

Cada término se informa en un renglón, seguido de las páginas en que
aparece, listo para copiarse a un índice:

    Sharahzad 3, 5, 23, 34
    Nombre de Dios 5, 23

Con --detailed se obtiene en cambio el recuento por término y una página
por renglón, que es donde caben los fragmentos de contexto.

Uso
---
    pdf-word-finder libro.pdf amor virtus "de rerum natura"
    pdf-word-finder libro.pdf --words-file terminos.txt --csv hits.csv
    pdf-word-finder libro.pdf --regex "Marcolph\\w*" --context
    pdf-word-finder libro.pdf amor "re:virtu(s|tem|tis)"
    pdf-word-finder libro.pdf --words-file onomastico.txt --txt indice.txt

Sin instalar el paquete: `python -m pdf_word_finder` desde la carpeta src/.
"""

import argparse
import sys

from . import __copyright__, __license__, __version__, _argparse_es  # noqa: F401
from .extraction import PdfError, extract_pages
from .patterns import PatternError
from .report import build_report, write_csv, write_txt
from .search import Options, read_terms, search
from .text import plural


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="pdf-word-finder",
        description="Busca palabras en un PDF e informa, en un renglón por "
                    "término, las páginas rotuladas (impresas) en que "
                    "aparece cada una.",
        epilog="Ejemplo: pdf-word-finder libro.pdf amor "
               "\"re:virtu(s|tem|tis)\" --ignore-accents --context")
    ap.add_argument("--version", action="version",
                    version=f"%(prog)s {__version__} — {__copyright__} — "
                            f"licencia {__license__}")
    ap.add_argument("pdf", help="ruta del archivo PDF")
    ap.add_argument("words", nargs="*", metavar="TÉRMINO",
                    help="palabras o frases que se han de buscar; si un "
                         "término empieza por «re:» se interpreta como "
                         "expresión regular")
    ap.add_argument("--words-file", metavar="ARCHIVO",
                    help="archivo con un término por renglón "
                         "(«#» inicia un comentario)")
    ap.add_argument("--regex", action="store_true",
                    help="trata TODOS los términos como expresiones regulares "
                         "(también puede prefijarse «re:» a cada término)")
    ap.add_argument("--regex-word", action="store_true",
                    help="exige límites de palabra también en las expresiones "
                         "regulares")
    ap.add_argument("--substring", action="store_true",
                    help="busca también dentro de las palabras (por omisión "
                         "solo se buscan palabras completas)")
    ap.add_argument("--case-sensitive", action="store_true",
                    help="distingue mayúsculas de minúsculas")
    ap.add_argument("--ignore-accents", action="store_true",
                    help="ignora los signos diacríticos")
    ap.add_argument("--no-dehyphenate", action="store_true",
                    help="no vuelve a unir las palabras partidas por un guion "
                         "al final del renglón")
    ap.add_argument("--show-logical", action="store_true",
                    help="muestra además la página secuencial, entre "
                         "corchetes, cuando difiere de la rotulada")
    ap.add_argument("--detailed", action="store_true",
                    help="informe detallado: recuento por término y una "
                         "página por renglón (por omisión, lista compacta)")
    ap.add_argument("--context", action="store_true",
                    help="muestra un fragmento de cada aparición (implica "
                         "--detailed)")
    ap.add_argument("--context-width", type=int, default=60, metavar="N",
                    help="caracteres de contexto a cada lado (por omisión: 60)")
    ap.add_argument("--sort", action="store_true",
                    help="ordena la lista alfabéticamente (por omisión sigue "
                         "el orden en que se dieron los términos)")
    ap.add_argument("--txt", metavar="ARCHIVO",
                    help="escribe la lista, siempre alfabetizada, en un "
                         "archivo de texto")
    ap.add_argument("--csv", metavar="ARCHIVO",
                    help="además, escribe los resultados en un archivo CSV")
    return ap


def main(argv: list[str] | None = None) -> None:
    ap = build_parser()
    args = ap.parse_args(argv)

    terms: list[str] = list(args.words)
    if args.words_file:
        try:
            with open(args.words_file, encoding="utf-8") as fh:
                terms += read_terms(fh)
        except OSError as exc:
            sys.exit(f"error: no se pudo leer «{args.words_file}»: {exc}")
    if not terms:
        ap.error("no se indicó ningún término de búsqueda")

    opts = Options(regex=args.regex, regex_word=args.regex_word,
                   substring=args.substring,
                   case_sensitive=args.case_sensitive,
                   ignore_accents=args.ignore_accents,
                   dehyphenate=not args.no_dehyphenate,
                   context_width=args.context_width if args.context else None)
    try:
        result = search(extract_pages(args.pdf), terms, opts)
    except (PdfError, PatternError) as exc:
        sys.exit(f"error: {exc}")

    report, notes = build_report(result, show_logical=args.show_logical,
                                 detailed=args.detailed or args.context,
                                 alphabetical=args.sort)

    # Las notas y los avisos van al canal de error para que la salida
    # ordinaria quede limpia y pueda redirigirse a un archivo o encauzarse
    # a otro programa.
    if notes:
        print(notes, file=sys.stderr)
    if report:
        print(report)

    if args.txt:
        try:
            n = write_txt(args.txt, result, args.show_logical)
        except OSError as exc:
            sys.exit(f"error: no se pudo escribir «{args.txt}»: {exc}")
        print(f"lista de {n} {plural(n, 'entrada', 'entradas')} escrita "
              f"en {args.txt}", file=sys.stderr)

    if args.csv:
        try:
            write_csv(args.csv, result)
        except OSError as exc:
            sys.exit(f"error: no se pudo escribir «{args.csv}»: {exc}")
        print(f"CSV escrito en {args.csv}", file=sys.stderr)


if __name__ == "__main__":
    main()
