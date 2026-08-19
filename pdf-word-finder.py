#!/usr/bin/env python3
"""
pdf-word-finder.py — busca palabras o frases en un PDF e informa dónde
aparecen.

Versión 1.0
© Nicolás Vaughan 2026. Distribuido bajo licencia MIT (véase LICENSE).

Informa la página *rotulada* de cada aparición: el número realmente impreso
en la página, tomado del árbol /PageLabels del PDF (numeración romana del
principio, desfases, prefijos, reinicios, láminas sin numerar, etc.). Es
decir, el número que le sirve al lector para abrir el libro, no el índice
interno del archivo.

Con --show-logical se añade entre corchetes la página *secuencial* (lógica):
el índice de la página dentro del archivo, empezando en 1, que es lo que
cuenta la barra de desplazamiento del visor.

Cada página se imprime en un renglón aparte.

Uso
---
    python pdf-word-finder.py libro.pdf amor virtus "de rerum natura"
    python pdf-word-finder.py libro.pdf --words-file terminos.txt --csv hits.csv
    python pdf-word-finder.py libro.pdf --regex "Marcolph\\w*" --context
    python pdf-word-finder.py libro.pdf amor "re:virtu(s|tem|tis)"

Opciones destacadas
-------------------
    --ignore-accents   ignora los diacríticos (búsqueda ≈ busqueda)
    --case-sensitive   distingue mayúsculas y minúsculas (por omisión, no)
    --substring        busca también dentro de las palabras
                       (por omisión solo se buscan palabras completas)
    --regex            trata todos los términos como expresiones regulares
    --regex-word       exige límites de palabra también en las expresiones
    --no-dehyphenate   conserva la división silábica de fin de renglón
    --show-logical     añade la página secuencial entre corchetes
    --context          muestra un fragmento de cada aparición

Requiere:  pip install pypdf
Opcional:  pip install pymupdf   (mejor extracción de texto; se usa si está)
"""

from __future__ import annotations

__version__ = "1.0"
__author__ = "Nicolás Vaughan"
__copyright__ = "© Nicolás Vaughan 2026"
__license__ = "MIT"

import argparse
import csv
import re
import sys
import unicodedata
from collections import defaultdict

# --------------------------------------------------------------------------
# Castellanización de los mensajes propios de argparse
# --------------------------------------------------------------------------
# argparse toma sus cadenas de `gettext`, importadas en el módulo como `_` y
# `ngettext`. Al sustituir esos nombres por una tabla propia, los rótulos
# «usage:», «options:», «error:» etc. salen en español sin necesidad de
# instalar catálogos .mo.

_ES = {
    "usage: ": "uso: ",
    "positional arguments": "argumentos posicionales",
    "options": "opciones",
    "optional arguments": "argumentos opcionales",
    "show this help message and exit": "muestra esta ayuda y termina",
    "show program's version number and exit":
        "muestra la versión del programa y termina",
    "%(prog)s: error: %(message)s\n": "%(prog)s: error: %(message)s\n",
    "the following arguments are required: %s":
        "faltan los siguientes argumentos: %s",
    "unrecognized arguments: %s": "argumentos no reconocidos: %s",
    "argument %(argument_name)s: %(message)s":
        "argumento %(argument_name)s: %(message)s",
    "invalid %(type)s value: %(value)r":
        "valor de tipo %(type)s no válido: %(value)r",
    "expected one argument": "se esperaba un argumento",
    "expected at most one argument": "se esperaba a lo sumo un argumento",
    "expected at least one argument": "se esperaba al menos un argumento",
    "ignored explicit argument %r": "se ignoró el argumento explícito %r",
    "not allowed with argument %s": "no se permite junto con el argumento %s",
    "one of the arguments %s is required":
        "se requiere alguno de los argumentos %s",
    "ambiguous option: %(option)s could match %(matches)s":
        "opción ambigua: %(option)s puede corresponder a %(matches)s",
    "unexpected option string: %s": "opción inesperada: %s",
    "cannot have multiple subparser arguments":
        "no puede haber varios argumentos de subanalizador",
    "no such option: %s": "no existe la opción: %s",
}

argparse._ = lambda s: _ES.get(s, s)  # type: ignore[attr-defined]
argparse.ngettext = (  # type: ignore[attr-defined]
    lambda sing, plur, n: _ES.get(sing if n == 1 else plur,
                                  sing if n == 1 else plur))

# --------------------------------------------------------------------------
# Extracción del texto
# --------------------------------------------------------------------------


def extract_pages(path: str) -> tuple[list[str], list[str], bool]:
    """Devuelve (textos, rótulos, tiene_rótulos_reales).

    textos[i] y rótulos[i] corresponden ambos a la página secuencial i+1.
    """
    from pypdf import PdfReader

    try:
        reader = PdfReader(path)
    except FileNotFoundError:
        sys.exit(f"error: no se encontró el archivo «{path}».")
    except Exception as exc:
        sys.exit(f"error: no se pudo abrir «{path}»: {exc}")

    if reader.is_encrypted:
        try:
            reader.decrypt("")  # la contraseña de usuario vacía es frecuente
        except Exception:
            sys.exit(f"error: «{path}» está cifrado y no se puede abrir.")

    n = len(reader.pages)

    # --- rótulos ---------------------------------------------------------
    # pypdf inventa "1", "2", ... cuando el archivo no tiene árbol
    # /PageLabels, así que se consulta el catálogo para saber si los
    # rótulos son reales.
    has_labels = "/PageLabels" in reader.trailer["/Root"]
    try:
        labels = [str(x) for x in reader.page_labels]
    except Exception:
        labels = []
    if len(labels) != n:  # árbol defectuoso -> numeración secuencial
        labels = [str(i + 1) for i in range(n)]
        has_labels = False

    # --- texto -----------------------------------------------------------
    texts = None
    try:  # PyMuPDF extrae bastante mejor, si está instalado
        import fitz  # type: ignore

        with fitz.open(path) as doc:
            texts = [p.get_text("text") for p in doc]
        if len(texts) != n:
            texts = None
    except ImportError:
        pass

    if texts is None:
        texts = [(p.extract_text() or "") for p in reader.pages]

    return texts, labels, has_labels


# --------------------------------------------------------------------------
# Normalización
# --------------------------------------------------------------------------

# u+2010..2015 son los distintos guiones unicode.
_HYPHENS = "\u002d\u00ad\u2010\u2011\u2012\u2013\u2014"
_DEHYPH_RE = re.compile(rf"(\w)[{_HYPHENS}][ \t]*\n[ \t]*(\w)")
_WS_RE = re.compile(r"[ \t\r\f\v\u00a0]+")


def strip_accents(s: str) -> str:
    """Elimina los signos diacríticos: 'philología' -> 'philologia'."""
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if not unicodedata.combining(c))


def normalise(text: str, dehyphenate: bool, ignore_accents: bool) -> str:
    # NFKC deshace ligaduras (ﬁ -> fi) y otras formas de compatibilidad.
    text = unicodedata.normalize("NFKC", text)
    if dehyphenate:
        text = _DEHYPH_RE.sub(r"\1\2", text)
    text = text.replace("\n", " ")
    text = _WS_RE.sub(" ", text)
    if ignore_accents:
        text = strip_accents(text)
    return text


# --------------------------------------------------------------------------
# Construcción de los patrones
# --------------------------------------------------------------------------

RE_PREFIX = "re:"


def is_regex_term(term: str, as_regex: bool) -> bool:
    """Un término es patrón si se pasó --regex o si empieza por 're:'."""
    return as_regex or term.startswith(RE_PREFIX)


def build_pattern(term: str, *, as_regex: bool, substring: bool,
                  case_sensitive: bool, ignore_accents: bool,
                  regex_word: bool = False) -> re.Pattern:
    pattern_mode = is_regex_term(term, as_regex)
    if term.startswith(RE_PREFIX):
        term = term[len(RE_PREFIX):]

    if ignore_accents:
        # Al texto de las páginas ya se le quitaron los diacríticos, así que
        # hay que quitárselos también al patrón. Solo se ven afectados los
        # caracteres literales acentuados; secuencias como \w quedan igual.
        term = strip_accents(unicodedata.normalize("NFKC", term))

    if pattern_mode:
        body = term
        # Por omisión las expresiones regulares no se tocan: delimitarlas es
        # tarea de quien las escribe. --regex-word les aplica los mismos
        # límites de palabra que a los términos literales.
        if regex_word and not substring:
            body = rf"(?<!\w)(?:{body})(?!\w)"
    else:
        # una frase puede partirse al final del renglón -> espacios flexibles
        body = r"\s+".join(re.escape(w) for w in term.split())
        if not substring:
            # \b falla junto a caracteres no alfanuméricos; con lookarounds
            # funcionan también los términos con apóstrofo, guion o puntuación.
            body = rf"(?<!\w){body}(?!\w)"

    flags = 0 if case_sensitive else re.IGNORECASE | re.UNICODE
    try:
        return re.compile(body, flags)
    except re.error as exc:
        sys.exit(f"error: expresión regular mal formada «{term}»: {exc}")


# --------------------------------------------------------------------------
# Informe
# --------------------------------------------------------------------------


def plural(n: int, singular: str, plural_: str) -> str:
    return singular if n == 1 else plural_


def fmt_page(logical: int, label: str, show_logical: bool) -> str:
    """Devuelve el número rotulado; con --show-logical añade el secuencial.

    Se informa el rótulo impreso, que es el que le sirve al lector. El
    número secuencial solo aparece si se pide, y solo cuando difiere.
    """
    if show_logical and label != str(logical):
        return f"{label} [sec. {logical}]"
    return label


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="pdf-word-finder.py",
        description="Busca palabras en un PDF e informa, una por renglón, la "
                    "página rotulada (impresa) en que aparece cada una.",
        epilog="Ejemplo: python pdf-word-finder.py libro.pdf amor "
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
    ap.add_argument("--context", action="store_true",
                    help="muestra un fragmento de cada aparición")
    ap.add_argument("--context-width", type=int, default=60, metavar="N",
                    help="caracteres de contexto a cada lado (por omisión: 60)")
    ap.add_argument("--csv", metavar="ARCHIVO",
                    help="además, escribe los resultados en un archivo CSV")
    args = ap.parse_args()

    terms: list[str] = list(args.words)
    if args.words_file:
        try:
            with open(args.words_file, encoding="utf-8") as fh:
                for line in fh:
                    line = line.split("#", 1)[0].strip()
                    if line:
                        terms.append(line)
        except OSError as exc:
            sys.exit(f"error: no se pudo leer «{args.words_file}»: {exc}")
    if not terms:
        ap.error("no se indicó ningún término de búsqueda")

    texts, labels, has_labels = extract_pages(args.pdf)
    pages = [normalise(t, not args.no_dehyphenate, args.ignore_accents)
             for t in texts]

    patterns = {t: build_pattern(t, as_regex=args.regex,
                                 substring=args.substring,
                                 case_sensitive=args.case_sensitive,
                                 ignore_accents=args.ignore_accents,
                                 regex_word=args.regex_word)
                for t in terms}

    # término -> lista de (página_secuencial, rótulo, nº apariciones, frags.)
    results: dict[str, list[tuple[int, str, int, list[str]]]] = defaultdict(list)

    for idx, page in enumerate(pages):
        logical = idx + 1
        label = labels[idx]
        for term, pat in patterns.items():
            hits = list(pat.finditer(page))
            if not hits:
                continue
            snippets = []
            if args.context:
                w = args.context_width
                for m in hits:
                    a, b = max(0, m.start() - w), min(len(page), m.end() + w)
                    snippets.append(
                        ("…" if a else "") + page[a:b].strip() +
                        ("…" if b < len(page) else ""))
            results[term].append((logical, label, len(hits), snippets))

    # --- informe por pantalla --------------------------------------------
    if not has_labels:
        print("nota: este PDF no tiene árbol /PageLabels; se supone que los "
              "números rotulados coinciden con los secuenciales.\n")

    empty = sum(1 for p in pages if not p.strip())
    if empty:
        print(f"nota: {empty} de {len(pages)} "
              f"{plural(len(pages), 'página', 'páginas')} no arrojaron texto "
              f"(¿digitalización sin OCR?).\n")

    for term in terms:
        rows = results.get(term, [])
        total = sum(r[2] for r in rows)
        if not rows:
            print(f"«{term}»: sin apariciones")
            continue
        print(f"«{term}»: {total} {plural(total, 'aparición', 'apariciones')} "
              f"en {len(rows)} {plural(len(rows), 'página', 'páginas')}")
        for lg, lb, c, snips in rows:
            print(f"    {fmt_page(lg, lb, args.show_logical)}"
                  f"{f' ×{c}' if c > 1 else ''}")
            for s in snips:
                print(f"        {s}")
        print()

    if has_labels and args.show_logical:
        print("Convención: página rotulada [sec. página secuencial]")

    # --- CSV -------------------------------------------------------------
    if args.csv:
        try:
            with open(args.csv, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["termino", "pagina_secuencial", "pagina_rotulada",
                            "apariciones", "contexto"])
                for term in terms:
                    for lg, lb, c, snips in results.get(term, []):
                        w.writerow([term, lg, lb, c, " | ".join(snips)])
        except OSError as exc:
            sys.exit(f"error: no se pudo escribir «{args.csv}»: {exc}")
        print(f"\nCSV escrito en {args.csv}")


if __name__ == "__main__":
    main()
