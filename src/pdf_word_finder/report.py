"""El informe de la búsqueda y su exportación a TXT y CSV.

Lo componen aquí tanto el programa de línea de órdenes como la interfaz
gráfica, de modo que no hay dos versiones del informe que puedan divergir.
"""

import csv

from .patterns import display_term
from .search import Result
from .text import plural, sort_key

CSV_HEADER = ["termino", "pagina_secuencial", "pagina_rotulada",
              "apariciones", "contexto"]


def fmt_page(logical: int, label: str, show_logical: bool) -> str:
    """Devuelve el número rotulado; con show_logical añade el secuencial.

    Se informa el rótulo impreso, que es el que le sirve al lector. El
    número secuencial solo aparece si se pide, y solo cuando difiere.
    """
    if show_logical and label != str(logical):
        return f"{label} [sec. {logical}]"
    return label


def alphabetical_terms(terms: list[str]) -> list[str]:
    return sorted(terms, key=lambda t: sort_key(display_term(t)))


def index_lines(result: Result, show_logical: bool = False,
                alphabetical: bool = False) -> list[str]:
    """Renglones del formato de lista: «término pág., pág., pág.»."""
    terms = alphabetical_terms(result.terms) if alphabetical else result.terms
    lines = []
    for term in terms:
        hits = result.hits.get(term)
        if not hits:
            continue
        pages = ", ".join(fmt_page(h.logical, h.label, show_logical)
                          for h in hits)
        lines.append(f"{display_term(term)} {pages}")
    return lines


def detailed_lines(result: Result, show_logical: bool = False) -> list[str]:
    """Recuento por término y una página por renglón, con los fragmentos
    de contexto debajo de cada página."""
    lines: list[str] = []
    for term in result.terms:
        hits = result.hits.get(term, [])
        shown = display_term(term)
        if not hits:
            lines.append(f"«{shown}»: sin apariciones")
            continue
        total = sum(h.count for h in hits)
        lines.append(
            f"«{shown}»: {total} "
            f"{plural(total, 'aparición', 'apariciones')} en {len(hits)} "
            f"{plural(len(hits), 'página', 'páginas')}")
        for h in hits:
            lines.append(f"    {fmt_page(h.logical, h.label, show_logical)}"
                         f"{f' ×{h.count}' if h.count > 1 else ''}")
            lines.extend(f"        {s}" for s in h.snippets)
        lines.append("")
    if result.has_labels and show_logical:
        lines.append("Convención: página rotulada [sec. página secuencial]")
    return lines


def build_report(result: Result, *, show_logical: bool = False,
                 detailed: bool = False,
                 alphabetical: bool = False) -> tuple[str, str]:
    """Arma el informe. Devuelve (informe, notas).

    Formato de lista (por omisión), pensado para copiarse a un índice:

        Sharahzad 3, 5, 23, 34
        Nombre de Dios 5, 23

    Formato detallado, con el recuento por término y una página por
    renglón, que es donde caben los fragmentos de contexto.

    Las notas (falta de rótulos, páginas sin texto, términos sin
    apariciones) van aparte: el programa de línea de órdenes las manda al
    canal de error, y la interfaz las muestra encima del informe.
    """
    notes: list[str] = []
    if not result.has_labels:
        notes.append("nota: este PDF no tiene árbol /PageLabels; se supone "
                     "que los números rotulados coinciden con los "
                     "secuenciales.")
    if result.empty_pages:
        notes.append(f"nota: {result.empty_pages} de {result.total_pages} "
                     f"{plural(result.total_pages, 'página', 'páginas')} no "
                     f"arrojaron texto (¿digitalización sin OCR?).")

    if detailed:
        lines = detailed_lines(result, show_logical)
    else:
        lines = index_lines(result, show_logical, alphabetical)
        # Los términos sin apariciones no ensucian la lista: se avisan aparte.
        missing = [display_term(t) for t in result.terms
                   if not result.hits.get(t)]
        if missing:
            notes.append("sin apariciones: " + ", ".join(missing))

    return "\n".join(lines).rstrip("\n"), "\n".join(notes)


def write_txt(path: str, result: Result, show_logical: bool = False) -> int:
    """Escribe la lista alfabetizada en un archivo de texto. Devuelve el
    número de renglones escritos. Lanza OSError si no puede."""
    lines = index_lines(result, show_logical, alphabetical=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + ("\n" if lines else ""))
    return len(lines)


def write_csv(path: str, result: Result) -> None:
    """Escribe una fila por término y página, en orden alfabético. Lanza
    OSError si no puede."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_HEADER)
        for term in alphabetical_terms(result.terms):
            for h in result.hits.get(term, []):
                w.writerow([display_term(term), h.logical, h.label, h.count,
                            " | ".join(h.snippets)])
